#!/usr/bin/env python3
"""Costruisce il SITO UNICO (cartella sito/) partendo dalle pagine dei 7 siti originali.

I siti originali NON vengono toccati: questo programma li legge soltanto.
Da ogni pagina originale prende, IDENTICI, i due script (motore dei calcoli e interfaccia)
e il contenuto di <main>; li mette dentro la grafica comune (testata, menu laterale,
intestazione del tema, piè di pagina) e scrive sito/<tema>/index.html.

Uniche modifiche al contenuto copiato (controllate da test_sito_unico.py):
  1. negli script delle pagine con dati automatici i dati vengono letti SEMPRE dal sito
     originale (URL_DATI_ONLINE): ["dati/", URL_DATI_ONLINE] -> [URL_DATI_ONLINE].
     Così il sito unico usa gli stessi dati aggiornati dai bot dei siti originali,
     senza un secondo bot e senza una seconda e-mail di avviso;
  2. il titolo «1 · Sezione e periodo/anno» diventa «1 · Periodo» (la sezione si sceglie
     con le schede in alto, che comandano gli stessi pulsanti di prima, nascosti);
  3. <main class="wrap"> riceve id="contenuto" (link «Vai al contenuto»);
  4. il vecchio <footer> diventa <footer class="versione">;
  5. nelle scritte dello script dell'interfaccia «Ultimo controllo automatico: <data>» e
     «ultimo controllo il <data>» diventano «Dati aggiornati al <data>» e «dati aggiornati
     al <data>» (la data è quella dell'ultimo salvataggio del bot, non dell'ultimo controllo:
     il bot non salva se i dati sono invariati).

Uso:  python3 costruisci_sito.py      (riscrive tutta la cartella sito/ tranne .git)
Solo libreria standard di Python.
"""
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
FINALE = QUI.parent
SORGENTI = QUI / "sorgenti"
SITO = QUI / "sito"
VERSIONE = "1.0"
VERSIONE_AREE = ""

# ---------------------------------------------------------------------------
# Le aree (temi) del sito, nell'ordine del menu
# ---------------------------------------------------------------------------
AREE = [
    {
        "slug": "imprese", "nome": "Imprese", "cartella": "6_Web_Imprese_Stockview",
        "colore": "#006ba0", "chiaro": "#e3f2fa", "icona": "imprese",
        "lead": "Imprese registrate e attive, iscrizioni e cessazioni, procedure concorsuali e scioglimenti "
                "in provincia di Varese, dai file scaricati da Stockview (InfoCamere).",
        "fonte": "InfoCamere – Stockview", "modo": "file",
        "modo_testo": "Carichi tu i file di Stockview e la serie storica",
        "stato_fisso": "Nessun dato automatico: si caricano i file di Stockview",
        "sezioni": [("registrate_attive", "Registrate e attive"), ("iscrizioni_cessazioni", "Iscrizioni e cessazioni"),
                    ("procedure", "Procedure concorsuali e scioglimenti")],
    },
    {
        "slug": "lavoro", "nome": "Lavoro", "cartella": "8_Web_Lavoro",
        "colore": "#c2410c", "chiaro": "#fdede4", "icona": "lavoro",
        "lead": "Disoccupazione, occupazione, attività e inattività dalla Rilevazione sulle forze di lavoro dell'ISTAT; "
                "cassa integrazione dall'Osservatorio dell'INPS.",
        "fonte": "ISTAT · INPS", "modo": "auto",
        "modo_testo": "Dati automatici: ISTAT ogni lunedì, INPS dal 2 al 12 del mese",
        "sezioni": [("disoccupazione", "Disoccupazione"), ("occupazione", "Occupazione"), ("attivita", "Attività"),
                    ("inattivita", "Inattività"), ("cig", "Cassa integrazione")],
    },
    {
        "slug": "commercio-estero", "nome": "Commercio estero", "cartella": "2_Versione_Web_GitHub",
        "colore": "#0f766e", "chiaro": "#e0f3f0", "icona": "commercio",
        "lead": "Export e import di Varese, Lombardia e Italia per territori, settori e paesi, "
                "con i dati ISTAT Coeweb scaricati al momento.",
        "fonte": "ISTAT – Coeweb", "modo": "diretta",
        "modo_testo": "Dati scaricati da ISTAT quando premi «Genera report»",
        "stato_fisso": "Dati scaricati in diretta da ISTAT a ogni report",
        "sezioni": [("", "Import / Export")],
    },
    {
        "slug": "credito", "nome": "Credito", "cartella": "7_Web_Credito_BancaItalia",
        "colore": "#4338ca", "chiaro": "#ebeafd", "icona": "credito",
        "lead": "Depositi, impieghi, sofferenze e sportelli bancari di Varese, Lombardia e Italia "
                "dalla Base Dati Statistica della Banca d'Italia.",
        "fonte": "Banca d'Italia", "modo": "auto",
        "modo_testo": "Dati automatici: controllo i giorni 28–31 e il 2 di ogni mese",
        "sezioni": [("depositi", "Depositi"), ("impieghi", "Impieghi"), ("sofferenze", "Sofferenze"), ("sportelli", "Sportelli")],
    },
    {
        "slug": "conti-economici", "nome": "Conti economici", "cartella": "10_Web_ContiEconomici",
        "colore": "#7e22ce", "chiaro": "#f3e7fc", "icona": "conti",
        "lead": "Valore aggiunto totale, pro capite e per settore di Varese, Lombardia e Italia, "
                "dal Centro Studi Tagliacarne e dall'ISTAT.",
        "fonte": "Centro Studi Tagliacarne · ISTAT", "modo": "auto",
        "modo_testo": "Dati automatici: controllo ogni giorno",
        "sezioni": [("", "Valore aggiunto")],
    },
    {
        "slug": "popolazione", "nome": "Popolazione", "cartella": "9_Web_Popolazione",
        "colore": "#13733a", "chiaro": "#e3f4e8", "icona": "popolazione",
        "lead": "Popolazione residente e straniera, territori, serie storica, saldi demografici e indicatori "
                "(vecchiaia, dipendenza, speranza di vita) dai dati ISTAT.",
        "fonte": "ISTAT", "modo": "auto",
        "modo_testo": "Dati automatici: controllo ogni lunedì",
        "sezioni": [("", "Popolazione residente")],
    },
    {
        "slug": "trasporti", "nome": "Trasporti", "cartella": "11_Web_Trasporti",
        "colore": "#be123c", "chiaro": "#fce7eb", "icona": "trasporti",
        "lead": "Autovetture circolanti in provincia di Varese per classe Euro, alimentazione e cilindrata, "
                "dall'Autoritratto dell'ACI e dalla popolazione ISTAT.",
        "fonte": "ACI · ISTAT", "modo": "auto",
        "modo_testo": "Dati automatici: controllo ogni giorno",
        "sezioni": [("", "Strade – autovetture")],
    },
]
AC = ' aria-current="page"'
NOME_REPO = "report-osserva"   # nome del repository su GitHub (serve solo alla pagina 404)
MODI = {"auto": "Dati automatici", "diretta": "Dati in diretta", "file": "File da caricare"}

# Icone in stile «Lucide» (licenza ISC), disegnate a tratto
ICONE = {
    "imprese": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "lavoro": '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "commercio": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "credito": '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M12 2 20 7H4z"/>',
    "conti": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "popolazione": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "trasporti": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    "freccia": '<path d="m9 18 6-6-6-6"/>',
    "freccia-dx": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "attivita": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "fonte": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "orologio": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "scegli": '<path d="M9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "scarica": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "scudo": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "tabella": '<path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/>',
}


def impronta(nome):
    """?v=… con l'impronta del file: il browser riprende il file nuovo appena cambia"""
    return "?v=" + hashlib.sha256((SORGENTI / "assets" / nome).read_bytes()).hexdigest()[:10]


def icona(nome, classe="icona-svg"):
    return (f'<svg class="{classe}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONE[nome]}</svg>')


def e(t):
    return html.escape(t, quote=True)


# ---------------------------------------------------------------------------
# Lettura delle pagine originali
# ---------------------------------------------------------------------------
class ErroreCostruzione(Exception):
    pass


def leggi_originale(area):
    p = FINALE / area["cartella"] / "index.html"
    s = p.read_text(encoding="utf-8")
    i_main = s.find('<main class="wrap">')
    f_main = s.find("</main>")
    i_footer = s.find("<footer>", f_main)
    f_footer = s.find("</footer>", i_footer)
    i_script = s.find('<script id="motore">')
    f_body = s.rfind("</body>")
    if f_body < 0:          # la pagina Trasporti finisce con </script> senza </body></html> (il browser lo tollera)
        f_body = len(s)
    if min(i_main, f_main, i_footer, f_footer, i_script, f_body) < 0:
        raise ErroreCostruzione(f"{p}: struttura della pagina non riconosciuta")
    if not (i_main < f_main < i_footer < f_footer < i_script < f_body):
        raise ErroreCostruzione(f"{p}: ordine delle parti della pagina inatteso")
    script = s[i_script:f_body].rstrip()
    if script.count("<script") != 2 or script.count("</script>") != 2:
        raise ErroreCostruzione(f"{p}: attesi esattamente 2 script (motore e interfaccia)")
    m = re.search(r'const URL_DATI_ONLINE = "([^"]+)";', s)
    return {
        "percorso": p,
        "main": s[i_main:f_main + len("</main>")],
        "footer": s[i_footer + len("<footer>"):f_footer],
        "script": script,
        "url_dati": m.group(1) if m else None,
    }


VECCHIO_BASI = '["dati/", URL_DATI_ONLINE]'
NUOVO_BASI = "[URL_DATI_ONLINE]"
ETICHETTE_DATA = [("Ultimo controllo automatico: ", "Dati aggiornati al "),
                  (" · ultimo controllo il ", " · dati aggiornati al ")]
TITOLI_SEZIONE = ["<h2>1 · Sezione e periodo</h2>", "<h2>1 · Sezione e anno</h2>"]


def adatta(area, orig):
    script = orig["script"]
    if orig["url_dati"]:
        if script.count(VECCHIO_BASI) != 1:
            raise ErroreCostruzione(f"{area['nome']}: la riga dei dati automatici non è come atteso")
        script = script.replace(VECCHIO_BASI, NUOVO_BASI)
    for vecchia, nuova in ETICHETTE_DATA:
        script = script.replace(vecchia, nuova)
    main = orig["main"].replace('<main class="wrap">', '<main class="wrap" id="contenuto">', 1)
    if area["sezioni"][0][0]:
        trovati = [t for t in TITOLI_SEZIONE if t in main]
        if len(trovati) != 1:
            raise ErroreCostruzione(f"{area['nome']}: titolo della scelta della sezione non trovato")
        main = main.replace(trovati[0], "<h2>1 · Periodo</h2>", 1)
        for valore, _ in area["sezioni"]:
            if f'value="{valore}"' not in main:
                raise ErroreCostruzione(f"{area['nome']}: la sezione «{valore}» non c'è nella pagina originale")
    return main, script


# ---------------------------------------------------------------------------
# Pezzi comuni della grafica
# ---------------------------------------------------------------------------
def stile_area(a):
    return f"--c:{a['colore']};--c-soft:{a['chiaro']}"


def testata(radice, home=False):
    return f"""<header class="testata">
  <div class="testata-in">
    <a class="marchio" href="{radice}index.html" title="Torna alla pagina iniziale"><img src="{radice}assets/logo.png" alt="Camera di Commercio di Varese – Futuro Impresa Territorio" width="218" height="44"></a>
    <div class="testata-titolo"><a href="{radice}index.html">Report statistici</a><small>Tabelle per Osserva · Ufficio Statistica</small></div>
    <nav class="testata-link" aria-label="Collegamenti principali">
      <a href="{radice}index.html"{AC if home else ''}>{icona("home")}<span>Home</span></a>
      <a href="{radice}index.html#stato">{icona("attivita")}<span>Stato dei dati</span></a>
    </nav>
    <button class="bottone-menu" type="button" aria-controls="menu" aria-expanded="false">{icona("menu")}Temi</button>
  </div>
</header>"""


def menu_laterale(radice, corrente=None):
    righe = [f'<aside class="menu-laterale" id="menu" aria-label="Temi">',
             '  <nav>',
             f'    <a class="menu-area menu-home" href="{radice}index.html"{AC if corrente is None else ""}>'
             f'<span class="tessera">{icona("home")}</span><span class="nome">Pagina iniziale</span></a>',
             '    <p class="titoletto">Temi</p>']
    for a in AREE:
        qui = a["slug"] == corrente
        pagina = f"{radice}{a['slug']}/index.html"
        if a["sezioni"][0][0]:
            classi = "menu-voce corrente" if qui else "menu-voce"
            righe.append(f'    <details class="{classi}" style="{stile_area(a)}"{" open" if qui else ""}>')
            righe.append(f'      <summary><span class="menu-area"{AC if qui else ""}><span class="tessera">{icona(a["icona"])}</span>'
                         f'<span class="nome">{e(a["nome"])}</span><span class="freccia">{icona("freccia")}</span></span></summary>')
            righe.append('      <ul class="menu-sezioni">')
            for valore, nome in a["sezioni"]:
                href = f"#sezione={valore}" if qui else f"{pagina}#sezione={valore}"
                righe.append(f'        <li><a href="{href}" data-sezione="{valore}">{e(nome)}</a></li>')
            righe.append('      </ul>')
            righe.append('    </details>')
        else:
            righe.append(f'    <div class="menu-voce{" corrente" if qui else ""}" style="{stile_area(a)}"><a class="menu-area" href="{pagina}"'
                         f'{AC if qui else ""}><span class="tessera">{icona(a["icona"])}</span>'
                         f'<span class="nome">{e(a["nome"])}</span></a></div>')
    righe.append('  </nav>')
    righe.append('  <div class="menu-nota"><b>Come si usa</b>Scegli un tema, controlla i dati e premi «Genera». '
                 'In fondo a ogni pagina, «Come funziona» spiega tabelle e regole di calcolo.</div>')
    righe.append('</aside>')
    return "\n".join(righe)


def pie(radice):
    return f"""<footer class="pie">
  <div class="pie-in">
    <div><img class="simbolo" src="{radice}assets/simbolo-bianco.png" alt=""><b>Camera di Commercio di Varese</b> · Ufficio Statistica</div>
    <div>Fonti: ISTAT, Banca d'Italia, INPS, InfoCamere, Centro Studi Tagliacarne, ACI · Le tabelle si creano nel browser: i file che carichi restano sul tuo computer · versione {VERSIONE}</div>
  </div>
</footer>"""


def testa_html(titolo, descrizione, radice):
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{e(descrizione)}">
<meta name="theme-color" content="#12104a">
<link rel="icon" type="image/png" href="{radice}assets/favicon.png">
<link rel="stylesheet" href="{radice}assets/portale.css{impronta("portale.css")}">
<script>document.documentElement.classList.add("js");</script>
</head>"""


def eroe_area(a):
    sezioni = a["sezioni"] if a["sezioni"][0][0] else []
    schede = ""
    if sezioni:
        voci = "\n".join(
            f'      <a class="scheda" role="tab" href="#sezione={v}" data-sezione="{v}" data-nome="{e(n)}" aria-selected="{"true" if i == 0 else "false"}">'
            f'{e(n)}</a>' for i, (v, n) in enumerate(sezioni))
        schede = f'\n    <nav class="schede" role="tablist" aria-label="Sezioni di {e(a["nome"])}">\n{voci}\n    </nav>'
    briciola = f'<span aria-hidden="true">/</span><span class="qui">{e(sezioni[0][1])}</span>' if sezioni else ""
    stato = (f'<li class="stato-dati" data-stato-area="{a["slug"]}"><span class="pallino"></span>'
             f'<span class="testo">Controllo lo stato dei dati…</span></li>') if a["modo"] == "auto" else ""
    return f"""<section class="eroe-area{'' if sezioni else ' senza-schede'}" aria-labelledby="titolo-tema">
    <div class="briciole"><a href="../index.html">Home</a><span aria-hidden="true">/</span><a href="index.html">{e(a["nome"])}</a>{briciola}</div>
    <div class="eroe-riga">
      <div class="tessera-grande">{icona(a["icona"])}</div>
      <div>
        <h1 id="titolo-tema">{e(a["nome"])}</h1>
        <p class="lead">{e(a["lead"])}</p>
        <ul class="meta">
          <li>{icona("fonte")}Fonte: {e(a["fonte"])}</li>
          <li>{icona("orologio")}{e(a["modo_testo"])}</li>
          {stato}
        </ul>
      </div>
    </div>{schede}
  </section>"""


def pagina_area(a, main, script, footer):
    radice = "../"
    return f"""{testa_html(f"{a['nome']} – Report statistici · Camera di Commercio di Varese", a["lead"], radice)}
<body class="pagina-tema" data-area="{a['slug']}" style="--area:{a['colore']};--area-soft:{a['chiaro']}">
<a class="vai-contenuto" href="#contenuto">Vai al contenuto</a>
{testata(radice)}
<div class="velo"></div>
<div class="struttura">
{menu_laterale(radice, a["slug"])}
<div class="contenuto">
  {eroe_area(a)}

{main}
<footer class="versione">{footer}</footer>
</div>
</div>
{pie(radice)}
{script}
<script src="../assets/aree.js{VERSIONE_AREE}"></script>
<script src="../assets/portale.js{impronta("portale.js")}"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Pagina iniziale
# ---------------------------------------------------------------------------
def pagina_home():
    n_sezioni = sum(len(a["sezioni"]) for a in AREE)
    carte = []
    for a in AREE:
        pagina = f"{a['slug']}/index.html"
        if a["sezioni"][0][0]:
            chips = "".join(f'<li><a href="{pagina}#sezione={v}">{e(n)}</a></li>' for v, n in a["sezioni"])
        else:
            chips = f'<li><a href="{pagina}">{e(a["sezioni"][0][1])}</a></li>'
        stato_testo = "Controllo lo stato dei dati…" if a["modo"] == "auto" else e(a.get("stato_fisso", ""))
        carte.append(f"""      <article class="tema" data-modo="{a['modo']}" style="{stile_area(a)}">
        <div class="tema-testa">
          <span class="tessera">{icona(a["icona"])}</span>
          <div><h3><a href="{pagina}">{e(a["nome"])}</a></h3><span class="fonte-tema">{e(a["fonte"])}</span></div>
        </div>
        <span class="vai">{icona("freccia-dx")}</span>
        <p>{e(a["lead"])}</p>
        <ul class="etichette" aria-label="Sezioni">{chips}</ul>
        <div class="tema-piede">
          <span class="modo {a['modo']}">{e(MODI[a['modo']])}</span>
          <span class="stato-breve" data-stato-area="{a['slug']}"><span class="testo">{stato_testo}</span></span>
        </div>
      </article>""")
    righe_stato = []
    for a in AREE:
        auto = a["modo"] == "auto"
        righe_stato.append(f"""        <tr style="{stile_area(a)}" data-stato-area="{a['slug']}">
          <td><a href="{a['slug']}/index.html"><span class="tessera">{icona(a["icona"])}</span>{e(a["nome"])}</a></td>
          <td data-titolo="Fonte">{e(a["fonte"])}</td>
          <td data-titolo="Dati disponibili"><span class="pallino"></span><span class="testo">{"Controllo…" if auto else e(a.get("stato_fisso", ""))}</span></td>
          <td data-titolo="Dati aggiornati al"><span class="{'quando' if auto else 'piccolo'}">{"…" if auto else "—"}</span></td>
          <td data-titolo="Aggiornamento" class="piccolo">{e(a["modo_testo"])}</td>
        </tr>""")
    pannello = "\n".join(
        f'      <li data-stato-area="{a["slug"]}" data-breve><span class="tessera">{icona(a["icona"])}</span>'
        f'<div><a href="{a["slug"]}/index.html">{e(a["nome"])}</a><span class="testo">Controllo…</span></div><span class="pallino"></span></li>'
        for a in AREE if a["modo"] == "auto")
    return f"""{testa_html("Report statistici · Camera di Commercio di Varese",
                     "Le tabelle Excel per Osserva su imprese, lavoro, commercio estero, credito, conti economici, popolazione e trasporti della provincia di Varese.", "")}
<body class="home">
<a class="vai-contenuto" href="#temi">Vai ai temi</a>
{testata("", home=True)}
<div class="velo"></div>
<section class="eroe" aria-labelledby="titolo-home">
  <img class="simbolo-sfondo" src="assets/simbolo-bianco.png" alt="">
  <div class="eroe-in">
   <div class="eroe-testo">
    <span class="occhiello">{icona("tabella")} Ufficio Statistica · Osserva Varese</span>
    <h1 id="titolo-home">Le tabelle di Osserva, <span>tutte in un unico posto</span></h1>
    <p class="lead">Scegli un tema, controlla i dati e scarica le tabelle Excel pronte da caricare su Osserva.
      La maggior parte dei dati arriva da sola dalle fonti ufficiali: niente da scaricare a mano.</p>
    <div class="azioni">
      <a class="azione piena" href="#temi">Scegli un tema {icona("freccia-dx")}</a>
      <a class="azione vuota" href="#stato">{icona("attivita")} Stato dei dati</a>
    </div>
    <div class="numeri">
      <div><b>{len(AREE)}</b><span>temi</span></div>
      <div><b>{n_sezioni}</b><span>sezioni di Osserva</span></div>
      <div><b>6</b><span>fonti ufficiali</span></div>
    </div>
   </div>
   <aside class="pannello" aria-labelledby="titolo-pannello">
    <h2 id="titolo-pannello">{icona("attivita")} Dati automatici</h2>
    <p>Arrivano da soli dalle fonti ufficiali. Ultimi dati disponibili:</p>
    <ul>
{pannello}
    </ul>
   </aside>
  </div>
</section>
<div class="struttura">
{menu_laterale("", None)}
<div class="contenuto" id="contenuto">
  <section class="blocco" id="temi" aria-labelledby="titolo-temi">
    <div class="blocco-testa">
      <div><h2 id="titolo-temi">Scegli un tema</h2>
        <p>Ogni tema ha la sua pagina con i passi da seguire. Le etichette colorate portano direttamente alla sezione.</p></div>
      <div class="filtri" role="group" aria-label="Filtra i temi">
        <button class="filtro" type="button" data-filtro="tutti" aria-pressed="true">Tutti</button>
        <button class="filtro" type="button" data-filtro="auto" aria-pressed="false">Dati automatici</button>
        <button class="filtro" type="button" data-filtro="diretta" aria-pressed="false">Dati in diretta</button>
        <button class="filtro" type="button" data-filtro="file" aria-pressed="false">File da caricare</button>
      </div>
    </div>
    <div class="temi">
{chr(10).join(carte)}
    </div>
  </section>

  <section class="blocco" aria-labelledby="titolo-come">
    <div class="blocco-testa"><div><h2 id="titolo-come">Come funziona</h2><p>Tre passi, uguali per ogni tema.</p></div></div>
    <div class="come">
      <div><span class="tessera">{icona("scegli")}</span><h3>Scegli tema e periodo</h3>
        <p>Apri il tema dal menu o dalle schede qui sopra, poi la sezione (es. Depositi, Occupazione) e l'anno o il trimestre.</p></div>
      <div><span class="tessera">{icona("fonte")}</span><h3>Controlla i dati</h3>
        <p>Un riquadro verde dice che i dati automatici sono pronti. Per le imprese trascini i file di Stockview; la pagina controlla tutto e dice cosa manca.</p></div>
      <div><span class="tessera">{icona("scarica")}</span><h3>Scarica le tabelle</h3>
        <p>Premi «Genera»: ottieni i file Excel con i nomi e le intestazioni dei modelli di Osserva, uno per uno o tutti insieme in un file ZIP.</p></div>
    </div>
  </section>

  <section class="blocco" id="stato" aria-labelledby="titolo-stato">
    <div class="blocco-testa"><div><h2 id="titolo-stato">Stato dei dati</h2>
      <p>Letto in questo momento dai controlli automatici. Se una fonte non risponde, le pagine permettono sempre di caricare i file a mano.</p></div></div>
    <table class="tabella-stato">
      <thead><tr><th scope="col">Tema</th><th scope="col">Fonte</th><th scope="col">Dati disponibili</th><th scope="col">Dati aggiornati al</th><th scope="col">Aggiornamento</th></tr></thead>
      <tbody>
{chr(10).join(righe_stato)}
      </tbody>
    </table>
    <div class="riquadro-info">{icona("scudo")}<div><b>I tuoi file restano sul tuo computer.</b>
      Le tabelle vengono calcolate dal browser: i file che carichi (per esempio quelli di Stockview e la serie storica delle imprese) non vengono inviati a nessun server.</div></div>
  </section>
</div>
</div>
{pie("")}
<script src="assets/aree.js{VERSIONE_AREE}"></script>
<script src="assets/portale.js{impronta("portale.js")}"></script>
</body>
</html>
"""


def pagina_404():
    return f"""{testa_html("Pagina non trovata · Report statistici", "Pagina non trovata", f"/{NOME_REPO}/")}
<body class="home">
{testata(f"/{NOME_REPO}/")}
<div class="struttura" style="grid-template-columns:minmax(0,1fr)"><div class="contenuto">
  <section class="eroe-area senza-schede" style="max-width:720px;margin:40px auto">
    <h1>Pagina non trovata</h1>
    <p class="lead">L'indirizzo non esiste (forse è cambiato). Torna alla <a href="/{NOME_REPO}/index.html">pagina iniziale</a> e scegli il tema.</p>
  </section>
</div></div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
def costruisci():
    if not SITO.exists():
        SITO.mkdir()
    # pulisco tutto tranne .git (il repository)
    for p in SITO.iterdir():
        if p.name == ".git":
            continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(SORGENTI / "assets", SITO / "assets")
    originali = {a["slug"]: leggi_originale(a) for a in AREE}
    info_aree = [{"slug": a["slug"], "nome": a["nome"], "originale": a["cartella"],
                  "stato": (originali[a["slug"]]["url_dati"] + "aggiornamento.json") if originali[a["slug"]]["url_dati"] else None,
                  "statoFisso": a.get("stato_fisso", "")} for a in AREE]
    testo_aree = ("/* scritto da costruisci_sito.py: non modificare a mano */\nwindow.AREE_PORTALE = "
                  + json.dumps(info_aree, ensure_ascii=False, indent=1) + ";\n")
    (SITO / "assets" / "aree.js").write_text(testo_aree, encoding="utf-8")
    global VERSIONE_AREE
    VERSIONE_AREE = "?v=" + hashlib.sha256(testo_aree.encode("utf-8")).hexdigest()[:10]
    for a in AREE:
        orig = originali[a["slug"]]
        main, script = adatta(a, orig)
        cartella = SITO / a["slug"]
        cartella.mkdir()
        (cartella / "index.html").write_text(pagina_area(a, main, script, orig["footer"]), encoding="utf-8")
        print(f"  ✓ {a['slug']}/index.html  (da {a['cartella']})")
    (SITO / "index.html").write_text(pagina_home(), encoding="utf-8")
    (SITO / "404.html").write_text(pagina_404(), encoding="utf-8")
    (SITO / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copy(SORGENTI / "LEGGIMI.txt", SITO / "LEGGIMI.txt")
    print(f"  ✓ index.html, 404.html, assets/ ({len(AREE)} temi) → {SITO}")


if __name__ == "__main__":
    try:
        costruisci()
    except ErroreCostruzione as ex:
        print("ERRORE:", ex)
        sys.exit(1)
