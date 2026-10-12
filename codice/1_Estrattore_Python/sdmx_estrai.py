#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sdmx_estrai.py - Estrattore GENERICO SDMX ISTAT -> Excel (robusto/multi-formato).
=================================================================================
Le query si definiscono in 'query_salvate.py'. Due tipi (rilevati in automatico):
  TIPO A "normale": ha "url" (GET su .../SDMXWS/rest/data/...).
  TIPO B "coeweb" : ha "filtri" (POST sul databrowserhub, niente URL semplice).

In ENTRAMBI i casi lo script chiede i dati al sito e li legge in modo ROBUSTO:
riconosce da solo il formato della risposta (XML / JSON / CSV) tramite il
modulo sdmx_file_to_excel, provando piu' formati finche' uno funziona.

USO:
  python sdmx_estrai.py --list
  python sdmx_estrai.py --run "Nome query"
  python sdmx_estrai.py --all
Opzioni: --layout istat|long   --outdir CARTELLA   --lang it|en

Dipendenze: requests, pandas, openpyxl, lxml ; e il file sdmx_file_to_excel.py
"""
from __future__ import annotations
import argparse, copy, json as _json, os, re, sys, threading, time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
import sdmx_file_to_excel as fc   # lettore/scrittore robusto

SdmxError = fc.SdmxError
DEFAULT_LANG, DEFAULT_OUTDIR, DEFAULT_LAYOUT, HTTP_TIMEOUT = "it", "output", "long", 180

# --- Anti rate-limit ISTAT (~5 richieste/minuto) ---------------------------
MIN_INTERVAL = 13.0   # secondi minimi tra una richiesta HTTP e la successiva
MAX_RETRY = 4         # tentativi in caso di errori temporanei (429/5xx/rete)
_last_request_ts = 0.0

# Collegamenti verso l'esterno (GUI o CLI):
CANCELLA = threading.Event()   # se impostato, il lavoro si interrompe appena possibile
PROGRESSO = None               # callable(str) opzionale: messaggi di attesa/avanzamento


def _notifica(msg):
    cb = PROGRESSO
    if cb:
        try:
            cb(msg)
        except Exception:
            pass


def _pausa(sec):
    """Attesa interrompibile dal pulsante Annulla."""
    if CANCELLA.wait(timeout=sec):
        raise SdmxError("Operazione annullata.")


def _throttle():
    """Distanzia le richieste per non superare il limite ISTAT (~5/min)."""
    global _last_request_ts
    wait = MIN_INTERVAL - (time.monotonic() - _last_request_ts)
    if wait > 0:
        if wait > 3:
            _notifica(f"pausa di {wait:.0f}s per il limite ISTAT (~5 richieste/min)…")
        _pausa(wait)
    _last_request_ts = time.monotonic()


def _send(method, url, **kwargs):
    """Richiesta con pausa anti-flood e retry su 429, errori server e rete."""
    delay = 30.0
    last = None
    for attempt in range(MAX_RETRY):
        if CANCELLA.is_set():
            raise SdmxError("Operazione annullata.")
        _throttle()
        try:
            last = requests.request(method, url, timeout=HTTP_TIMEOUT, **kwargs)
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRY - 1:
                _notifica("il server non risponde (timeout): riprovo…")
                continue
            raise SdmxError(f"Timeout ({HTTP_TIMEOUT}s).")
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRY - 1:
                _notifica("connessione persa: riprovo tra 10s…")
                _pausa(10)
                continue
            raise SdmxError("Connessione assente o server irraggiungibile.")
        except requests.exceptions.RequestException as exc:
            raise SdmxError(f"Errore di rete: {exc}")
        if last.status_code == 429 and attempt < MAX_RETRY - 1:
            ra = last.headers.get("Retry-After")
            try:
                pausa = float(ra) if ra else delay
            except ValueError:
                pausa = delay
            pausa = min(pausa, 120)        # rispetta Retry-After, max 2 min
            _notifica(f"ISTAT chiede una pausa ({pausa:.0f}s), poi riprovo…")
            _pausa(pausa)
            delay *= 2                     # backoff esponenziale
            continue
        if last.status_code in (500, 502, 503, 504) and attempt < MAX_RETRY - 1:
            _notifica(f"errore temporaneo del server (HTTP {last.status_code}): riprovo tra 15s…")
            _pausa(15)
            continue
        return last
    return last

# Formati richiesti in ordine: prima JSON (etichette incluse), poi XML, poi CSV.
_ACCEPTS = [
    "application/vnd.sdmx.data+json;version=1.0.0, application/json",
    "application/vnd.sdmx.data.structurespecific+xml;version=2.1, application/xml",
    "application/vnd.sdmx.data+csv;version=1.0.0, text/csv",
]


def _headers(accept, lang, origin=None, post=False):
    # "UserLang" e' l'header proprietario del Data Browser ISTAT (coeweb):
    # e' l'unico modo per avere le etichette in italiano da quell'API.
    h = {"Accept": accept, "Accept-Language": f"{lang}, en;q=0.5",
         "UserLang": lang,
         "User-Agent": "Mozilla/5.0 (sdmx-estrai/1.2)"}
    if post:
        h["Content-Type"] = "application/json"
    if origin:
        h["Origin"] = origin; h["Referer"] = origin + "/"
    return h


def _check(r):
    if r.status_code == 200:
        if not r.content or len(r.content) < 30:
            raise SdmxError("risposta vuota.")
        return r.content
    if r.status_code == 404:
        raise SdmxError("404: nessun dato per questa query (URL/filtri errati?).")
    if r.status_code == 413:
        raise SdmxError("413: selezione troppo ampia (restringi i filtri).")
    if r.status_code == 429:
        raise SdmxError("429: troppe richieste (limite ISTAT ~5/min): attendi 1-2 min.")
    if r.status_code in (406, 415):
        raise SdmxError(f"formato non accettato (HTTP {r.status_code}).")
    if r.status_code >= 400:
        raise SdmxError(f"HTTP {r.status_code}. {r.text[:160]}")
    return r.content


def _get(url, accept, lang):
    p = urlparse(url)
    q = {k: (v[0] if isinstance(v, list) else v) for k, v in parse_qs(p.query).items()}
    q.setdefault("dimensionAtObservation", "TIME_PERIOD")
    full = urlunparse(p._replace(query=urlencode(q)))
    r = _send("GET", full, headers=_headers(accept, lang))
    return _check(r)


def _post(url, filtri, accept, lang):
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    # prova a chiedere le etichette nella lingua scelta (parametro ignorato se non supportato)
    p = urlparse(url)
    q = {k: (v[0] if isinstance(v, list) else v) for k, v in parse_qs(p.query).items()}
    q.setdefault("lang", lang)
    url = urlunparse(p._replace(query=urlencode(q)))
    body = filtri if isinstance(filtri, (list, dict)) else _json.loads(filtri)
    r = _send("POST", url, headers=_headers(accept, lang, origin, post=True), json=body)
    return _check(r)


# ===========================================================================
#  SELEZIONE PERIODO (anno/trimestre di inizio e fine download)
# ===========================================================================
def _trim_date(da, a):
    """(anno, trim) -> date ISO per il payload coeweb.
    from = primo giorno del trimestre iniziale, to = ultimo giorno del finale."""
    f = t = None
    if da:
        y, q = da
        f = f"{y}-{(q - 1) * 3 + 1:02d}-01T00:00:00"
    if a:
        y, q = a
        m = q * 3
        giorno = {3: 31, 6: 30, 9: 30, 12: 31}[m]
        t = f"{y}-{m:02d}-{giorno}T00:00:00"
    return f, t


def _periodo_param(p, end=False):
    """(anno, trim) -> valore per startPeriod/endPeriod SDMX REST.
    Trimestre 'pieno' (T1 inizio / T4 fine) -> solo anno, cosi' vale anche
    per i dataflow annuali."""
    y, q = p
    if (q == 1 and not end) or (q == 4 and end):
        return str(y)
    return f"{y}-Q{q}"


def _url_con_periodo(url, da, a):
    p = urlparse(url)
    q = {k: (v[0] if isinstance(v, list) else v) for k, v in parse_qs(p.query).items()}
    if da:
        q["startPeriod"] = _periodo_param(da)
    if a:
        q["endPeriod"] = _periodo_param(a, end=True)
    return urlunparse(p._replace(query=urlencode(q)))


def _filtri_con_periodo(filtri, da, a):
    """Sostituisce (o aggiunge) il filtro TIME_PERIOD nel payload coeweb."""
    filtri = copy.deepcopy(filtri if isinstance(filtri, (list, dict)) else _json.loads(filtri))
    if not isinstance(filtri, list):
        return filtri            # payload non standard: lascio invariato
    f_iso, t_iso = _trim_date(da, a)
    tp = next((f for f in filtri if isinstance(f, dict) and f.get("id") == "TIME_PERIOD"), None)
    if tp is None:
        tp = {"id": "TIME_PERIOD", "filterValues": [], "type": "TimeRange", "period": 0}
        filtri.append(tp)
    tp["type"] = "TimeRange"
    tp["filterValues"] = []
    if f_iso:
        tp["from"] = f_iso
    if t_iso:
        tp["to"] = t_iso
    return filtri


def _fetch_parse(url, filtri, is_post, lang, struttura, nome, outdir):
    """Scarica provando i formati e ritorna (df, time_label)."""
    errors, last = [], None
    for accept in _ACCEPTS:
        try:
            content = _post(url, filtri, accept, lang) if is_post else _get(url, accept, lang)
        except SdmxError as exc:
            if "annullata" in str(exc):
                raise
            errors.append(f"[{accept.split(';')[0]}] {exc}")
            if str(exc).startswith("413"):
                break              # selezione troppo ampia: cambiare formato non aiuta
            continue
        last = content
        try:
            return fc.sniff_e_parse(content, struttura, lang)
        except Exception as exc:
            errors.append(f"[{accept.split(';')[0]}] lettura: {exc}")
            continue
    # nessun formato ha funzionato: salva la risposta grezza per diagnosi
    if last is not None:
        os.makedirs(outdir, exist_ok=True)
        dbg = os.path.join(outdir, ("_risposta_grezza_" + nome[:30] + ".txt").replace(" ", "_"))
        try:
            open(dbg, "wb").write(last[:300000])
        except OSError:
            dbg = "(non salvata)"
        raise SdmxError("Nessun formato leggibile. Tentativi:\n  " + "\n  ".join(errors) +
                        f"\n  Risposta grezza salvata in: {dbg}")
    raise SdmxError("Download non riuscito. Tentativi:\n  " + "\n  ".join(errors))


def _anni_per_split(da, a, filtri):
    """Anni su cui spezzare il download quando il server risponde 413.
    Usa il periodo richiesto oppure, se assente, il TIME_PERIOD della query."""
    y1 = da[0] if da else None
    y2 = a[0] if a else None
    if (y1 is None or y2 is None) and isinstance(filtri, list):
        tp = next((f for f in filtri if isinstance(f, dict) and f.get("id") == "TIME_PERIOD"), None)
        if tp:
            m1 = re.match(r"(\d{4})", str(tp.get("from", "")))
            m2 = re.match(r"(\d{4})", str(tp.get("to", "")))
            y1 = y1 or (int(m1.group(1)) if m1 else None)
            y2 = y2 or (int(m2.group(1)) if m2 else None)
    if y1 is None or y2 is None or y2 <= y1 or y2 - y1 > 30:
        return []
    return list(range(y1, y2 + 1))


def esegui_query(q, lang=None, layout=None, outdir=DEFAULT_OUTDIR, periodo=None):
    """periodo: None o {'mode':'query'} = come salvato nella query;
    {'mode':'auto'} = ultimo anno con dati + tutto l'anno precedente;
    {'mode':'custom','da':(anno,trim),'a':(anno,trim)} = intervallo scelto."""
    if CANCELLA.is_set():
        raise SdmxError("Operazione annullata.")
    nome = q.get("nome") or "query"
    lang = lang or q.get("lingua", DEFAULT_LANG)
    layout = (layout or q.get("layout", DEFAULT_LAYOUT))
    layout = layout if layout in ("long", "istat") else "long"
    struttura = q.get("struttura") or None
    url = (q.get("url") or "").strip()
    filtri = q.get("filtri")
    is_post = bool(filtri)
    if not url:
        raise SdmxError(f"La query '{nome}' non ha una URL.")

    # --- applica il periodo richiesto ------------------------------------
    mode = (periodo or {}).get("mode", "query")
    da = a = None
    if mode == "custom":
        da, a = periodo.get("da"), periodo.get("a")
    elif mode == "auto":
        anno = time.localtime().tm_year
        # Finestra larga (il taglio esatto avviene dopo il parse). Per le query
        # GET (spesso annuali, pubblicate con ritardo) serve piu' margine;
        # per le coeweb POST (congiunturali trimestrali) 3 anni bastano.
        indietro = 3 if is_post else 6
        da, a = (anno - indietro, 1), (anno + 1, 4)
    if da or a:
        if is_post:
            filtri = _filtri_con_periodo(filtri, da, a)
        else:
            url = _url_con_periodo(url, da, a)

    # --- scarica (con spezzamento per anno se la selezione e' troppo ampia)
    try:
        df, time_label = _fetch_parse(url, filtri, is_post, lang, struttura, nome, outdir)
    except SdmxError as exc:
        anni = _anni_per_split(da, a, filtri if is_post else None)
        if "413" not in str(exc) or not anni:
            raise
        _notifica(f"selezione troppo ampia: la scarico anno per anno ({anni[0]}-{anni[-1]})…")
        pezzi, time_label = [], None
        for anno_i in anni:
            u2, f2 = url, filtri
            if is_post:
                f2 = _filtri_con_periodo(filtri, (anno_i, 1), (anno_i, 4))
            else:
                u2 = _url_con_periodo(url, (anno_i, 1), (anno_i, 4))
            try:
                d2, time_label = _fetch_parse(u2, f2, is_post, lang, struttura, nome, outdir)
            except SdmxError as e2:
                if "annullata" in str(e2):
                    raise
                if "404" in str(e2) or "vuota" in str(e2):
                    continue                    # anno senza dati: va bene, salto
                raise
            pezzi.append(d2)
        if not pezzi:
            raise SdmxError("Selezione troppo ampia anche per singolo anno: restringi i filtri.")
        df = fc.pd.concat(pezzi, ignore_index=True).drop_duplicates()

    # --- taglio esatto sul periodo (vale anche se il server ignora i parametri)
    if mode == "auto":
        df = fc.filtra_periodo(df, time_label, auto=True)
    elif mode == "custom":
        df = fc.filtra_periodo(df, time_label, da=da, a=a)
    return fc.esporta(df, time_label, nome, layout, q.get("righe"), outdir)


def _parse_periodo_cli(s, end=False):
    """'2024' o '2024-T1'/'2024Q1' -> (anno, trimestre)."""
    m = re.fullmatch(r"\s*(\d{4})(?:[-/]?[TtQq]0?([1-4]))?\s*", s or "")
    if not m:
        raise SdmxError(f"Periodo non valido: '{s}' (usa 2024 oppure 2024-T1).")
    return int(m.group(1)), int(m.group(2)) if m.group(2) else (4 if end else 1)


def _load_queries():
    try:
        import importlib, query_salvate
        importlib.reload(query_salvate)
    except ImportError:
        raise SdmxError("File 'query_salvate.py' non trovato accanto allo script.")
    qs = getattr(query_salvate, "QUERY", None)
    if not qs:
        raise SdmxError("In 'query_salvate.py' manca la lista QUERY (o e' vuota).")
    return qs


def main(argv=None):
    p = argparse.ArgumentParser(description="Estrattore SDMX ISTAT -> Excel (query in query_salvate.py).",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--run", nargs="+", metavar="NOME")
    g.add_argument("--all", action="store_true")
    p.add_argument("--layout", choices=["istat", "long"])
    p.add_argument("--outdir", default=DEFAULT_OUTDIR)
    p.add_argument("--lang", default=None, choices=["it", "en"])
    p.add_argument("--periodo", choices=["query", "auto"], default="query",
                   help="auto = ultimo anno con dati + tutto l'anno precedente")
    p.add_argument("--inizio", metavar="ANNO[-Tn]", help="inizio periodo, es. 2024 o 2024-T1")
    p.add_argument("--fine", metavar="ANNO[-Tn]", help="fine periodo, es. 2025 o 2025-T4")
    a = p.parse_args(argv)
    global PROGRESSO
    PROGRESSO = lambda t: print(f"  … {t}")
    periodo = None
    try:
        if a.inizio or a.fine:
            periodo = {"mode": "custom",
                       "da": _parse_periodo_cli(a.inizio) if a.inizio else None,
                       "a": _parse_periodo_cli(a.fine, end=True) if a.fine else None}
        elif a.periodo == "auto":
            periodo = {"mode": "auto"}
    except SdmxError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr); return 1
    try:
        queries = _load_queries()
    except SdmxError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr); return 1
    by_name = {q.get("nome"): q for q in queries}
    if a.list:
        print(f"\nQuery salvate ({len(queries)}):\n" + "-" * 60)
        for q in queries:
            tipo = "coeweb/POST" if q.get("filtri") else "normale/GET"
            print(f"  - {q.get('nome')}   [{tipo}, layout {q.get('layout', DEFAULT_LAYOUT)}]")
        print("\nEsegui:  python sdmx_estrai.py --run \"Nome query\"")
        return 0
    target = list(queries) if a.all else []
    if a.run:
        unknown = [n for n in a.run if n not in by_name]
        if unknown:
            print(f"ERRORE: query non trovate: {unknown}. Usa --list.", file=sys.stderr); return 1
        target = [by_name[n] for n in a.run]
    done, failed = [], []
    for n, q in enumerate(target, start=1):
        print(f"\n--- ({n}/{len(target)}) {q.get('nome')} ---")
        try:
            path = esegui_query(q, a.lang, a.layout, a.outdir, periodo)
            print(f"  OK -> {path}"); done.append(path)
        except SdmxError as exc:
            print(f"  SALTATA: {exc}", file=sys.stderr); failed.append(q.get("nome"))
    print("\n" + "=" * 60)
    print(f"Completato. File: {len(done)}. Falliti: {len(failed)}.")
    for d in done:
        print("  -", d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
