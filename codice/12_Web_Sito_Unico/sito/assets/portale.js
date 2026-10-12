/* Report statistici per Osserva – comportamento comune del sito.
   Non tocca i calcoli: le pagine dei temi hanno i loro script (copiati identici dai siti originali).
   Qui ci sono solo: menu sul telefono, schede delle sezioni, titoli numerati e stato dei dati automatici.
   Le aree (nomi, colori, indirizzi dei dati) sono in aree.js, scritto da costruisci_sito.py. */
(function () {
  "use strict";
  const AREE = window.AREE_PORTALE || [];
  const corpo = document.body;
  const areaCorrente = corpo.dataset.area || "";

  /* ---------- menu laterale sul telefono ---------- */
  const bottone = document.querySelector(".bottone-menu");
  const velo = document.querySelector(".velo");
  function menu(apri) {
    corpo.classList.toggle("menu-aperto", apri);
    if (bottone) bottone.setAttribute("aria-expanded", apri ? "true" : "false");
  }
  if (bottone) bottone.addEventListener("click", () => menu(!corpo.classList.contains("menu-aperto")));
  if (velo) velo.addEventListener("click", () => menu(false));
  document.addEventListener("keydown", e => { if (e.key === "Escape") menu(false); });
  document.querySelectorAll(".menu-laterale a").forEach(a => a.addEventListener("click", () => menu(false)));

  /* ---------- titoli «1 · Periodo» → numero in un cerchio ---------- */
  const RE_PASSO = /^\s*(\d+)\s*·\s*(.+)$/;
  function decoraTitoli() {
    document.querySelectorAll(".card > h2").forEach(h => {
      if (h.querySelector(".passo")) return;
      const m = RE_PASSO.exec(h.textContent);
      if (!m) return;
      h.textContent = "";
      const n = document.createElement("span"); n.className = "passo"; n.textContent = m[1]; n.setAttribute("aria-hidden", "true");
      const t = document.createElement("span"); t.textContent = m[2];
      const nascosto = document.createElement("span"); nascosto.className = "solo-lettori"; nascosto.textContent = `Passo ${m[1]}: `;
      nascosto.style.cssText = "position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)";
      h.append(nascosto, n, t);
    });
  }
  decoraTitoli();
  // alcune pagine riscrivono il titolo (es. «2 · Dati INPS»): lo ridecoro
  const main = document.querySelector("main");
  if (main && "MutationObserver" in window) {
    new MutationObserver(() => decoraTitoli()).observe(main, { childList: true, subtree: true, characterData: true });
  }

  /* ---------- schede delle sezioni (Depositi, Impieghi, …) ---------- */
  const radio = () => [...document.querySelectorAll('input[name="sezione"]')];
  const schede = [...document.querySelectorAll(".scheda[data-sezione]")];
  const vociMenu = [...document.querySelectorAll(".menu-voce.corrente .menu-sezioni a[data-sezione]")];
  function sezioneScelta() { const r = radio().find(x => x.checked); return r ? r.value : ""; }
  function mostraSezione() {
    const v = sezioneScelta();
    schede.forEach(s => {
      const r = radio().find(x => x.value === s.dataset.sezione);
      s.setAttribute("aria-selected", s.dataset.sezione === v ? "true" : "false");
      s.setAttribute("tabindex", s.dataset.sezione === v ? "0" : "-1");
      if (r && r.disabled) s.setAttribute("aria-disabled", "true");
    });
    vociMenu.forEach(a => a.classList.toggle("attiva", a.dataset.sezione === v));
    // sul telefono la scheda scelta può essere fuori vista: scorro solo la barra delle schede
    const sel = schede.find(s => s.dataset.sezione === v);
    if (sel && sel.parentElement) {
      const barra = sel.parentElement;
      const sinistra = sel.offsetLeft - (barra.clientWidth - sel.offsetWidth) / 2;
      barra.scrollLeft = Math.max(0, sinistra);
    }
    const nome = schede.find(s => s.dataset.sezione === v);
    const dove = document.querySelector(".briciole .qui");
    if (dove && nome) dove.textContent = nome.dataset.nome;
  }
  function scegli(v, aggiornaIndirizzo) {
    const r = radio().find(x => x.value === v);
    if (!r || r.disabled) return false;
    if (!r.checked) {
      r.checked = true;
      r.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (aggiornaIndirizzo) history.replaceState(null, "", "#sezione=" + v);
    mostraSezione();
    return true;
  }
  function daIndirizzo() {
    const m = /(?:^#|&)sezione=([\w-]+)/.exec(location.hash);
    if (m) scegli(m[1], false);
  }
  if (radio().length) {
    radio().forEach(r => r.addEventListener("change", () => {
      if (r.checked) { history.replaceState(null, "", "#sezione=" + r.value); mostraSezione(); }
    }));
    schede.forEach((s, i) => {
      s.addEventListener("click", e => { e.preventDefault(); scegli(s.dataset.sezione, true); });
      s.addEventListener("keydown", e => {
        const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        const prossima = schede[(i + d + schede.length) % schede.length];
        prossima.focus(); scegli(prossima.dataset.sezione, true);
      });
    });
    window.addEventListener("hashchange", daIndirizzo);
    daIndirizzo();
    mostraSezione();
  }

  /* ---------- quando compaiono i «File pronti» li porto in vista ---------- */
  const risultati = document.getElementById("risultati");
  if (risultati && "MutationObserver" in window) {
    let nascosto = risultati.hidden;
    new MutationObserver(() => {
      if (nascosto && !risultati.hidden) {
        const ridotto = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
        setTimeout(() => risultati.scrollIntoView({ behavior: ridotto ? "auto" : "smooth", block: "start" }), 60);
      }
      nascosto = risultati.hidden;
    }).observe(risultati, { attributes: true, attributeFilter: ["hidden"] });
  }

  /* ---------- pagina Imprese: avviso se si esce con la serie storica aggiornata non salvata ---------- */
  if (areaCorrente === "imprese") {
    window.addEventListener("beforeunload", e => {
      const r = document.getElementById("risultati");
      if (r && !r.hidden) { e.preventDefault(); e.returnValue = ""; }
    });
  }

  /* ---------- stato dei dati automatici (letto da aggiornamento.json dei siti dei dati) ---------- */
  const MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"];
  const mese = iso => { const m = /^(\d{4})-(\d{2})/.exec(iso || ""); return m ? `${MESI[+m[2] - 1]} ${m[1]}` : ""; };
  const giorno = iso => {
    const d = new Date(iso); if (isNaN(d)) return "";
    return d.toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Rome" });
  };
  const piuRecente = (...v) => v.filter(Boolean).sort().pop();
  // per ogni area: cosa dire dei dati (testo breve) e la data dell'ultimo salvataggio dei dati
  const RIASSUNTI = {
    credito: j => ({
      dati: [j.TDB10290 && `depositi e impieghi fino a ${mese(j.TDB10290.ultimo_dato)}`,
             j.TRI30401 && `sofferenze fino a ${mese(j.TRI30401.ultimo_dato)}`,
             j.TDB20207 && `sportelli ${String(j.TDB20207.ultimo_dato || "").slice(0, 4)}`].filter(Boolean).join(" · "),
      controllo: j.controllato }),
    lavoro: j => ({
      dati: [j.disoccupazione_tassi && `forze di lavoro ISTAT fino al ${j.disoccupazione_tassi.ultimo_anno}`,
             j.cig_varese_mensile && `cassa integrazione fino a ${mese(j.cig_varese_mensile.ultimo_mese)}`].filter(Boolean).join(" · "),
      controllo: piuRecente(j.controllato, j.controllato_cig) }),
    popolazione: j => ({
      dati: j.popolazione_residenti ? `popolazione al 1° gennaio ${j.popolazione_residenti.ultimo_anno}` : "",
      controllo: j.controllato }),
    "conti-economici": j => ({
      dati: [j.tagliacarne && `valore aggiunto ${j.tagliacarne.anno} (Tagliacarne)`,
             j.istat_valore_aggiunto && `ISTAT fino al ${j.istat_valore_aggiunto.ultimo_anno}`].filter(Boolean).join(" · "),
      controllo: j.controllato }),
    trasporti: j => ({
      dati: [j.aci && `autovetture ${j.aci.anno} (ACI)`,
             j.istat_popolazione && `popolazione ISTAT fino al ${j.istat_popolazione.ultimo_anno}`].filter(Boolean).join(" · "),
      controllo: j.controllato }),
  };
  async function leggiStato(area) {
    if (!area.stato || !RIASSUNTI[area.slug]) return null;
    const r = await fetch(area.stato, { cache: "no-store" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return RIASSUNTI[area.slug](await r.json());
  }
  function scriviStato(el, esito, area) {
    el.classList.remove("stato-ok", "stato-ko");
    if (esito === null) { el.querySelector(".testo").textContent = area.statoFisso || ""; return; }
    if (esito instanceof Error) { el.classList.add("stato-ko"); el.querySelector(".testo").textContent = "Stato dei dati automatici non raggiungibile ora"; return; }
    el.classList.add("stato-ok");
    const testo = esito.dati ? esito.dati.charAt(0).toUpperCase() + esito.dati.slice(1) : "Dati automatici";
    const quando = el.querySelector(".quando");
    const controllo = esito.controllo ? giorno(esito.controllo) : "";
    if (quando) { el.querySelector(".testo").textContent = testo; quando.textContent = controllo || "—"; }
    else el.querySelector(".testo").textContent = testo + (controllo && !el.hasAttribute("data-breve") ? ` · dati aggiornati al ${controllo}` : "");
  }
  // una sola richiesta per area anche se lo stato compare in più punti della pagina
  const richieste = new Map();
  document.querySelectorAll("[data-stato-area]").forEach(el => {
    const area = AREE.find(a => a.slug === el.dataset.statoArea);
    if (!area) return;
    if (!richieste.has(area.slug)) richieste.set(area.slug, leggiStato(area).catch(e => e));
    richieste.get(area.slug).then(esito => scriviStato(el, esito, area));
  });

  /* ---------- home: filtro dei temi ---------- */
  const filtri = [...document.querySelectorAll(".filtro[data-filtro]")];
  filtri.forEach(f => f.addEventListener("click", () => {
    filtri.forEach(x => x.setAttribute("aria-pressed", x === f ? "true" : "false"));
    document.querySelectorAll(".tema[data-modo]").forEach(t => {
      t.hidden = f.dataset.filtro !== "tutti" && t.dataset.modo !== f.dataset.filtro;
    });
  }));
})();
