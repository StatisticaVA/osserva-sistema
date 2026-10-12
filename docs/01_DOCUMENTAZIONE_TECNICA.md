# Documentazione tecnica del sistema dei report per Osserva

**Camera di Commercio di Varese – Ufficio Statistica**
Stato del sistema al **12 ottobre 2026**.

Questo documento spiega come funziona oggi il sistema che prepara le tabelle statistiche da caricare su **Osserva** (l'osservatorio economico della Camera, https://www.osserva-varese.it). Si legge dall'inizio alla fine.

Gli altri documenti della cartella `docs/`:

| Documento | Contenuto |
|---|---|
| `02_TABELLE_DI_OUTPUT.md` | Ogni tabella di output: da quali dati parte, quali calcoli fa, che forma ha. |
| `HANDOVER.md` | Registro tecnico dettagliato, scritto durante lo sviluppo in ordine cronologico: decisioni, verifiche, pubblicazioni. Serve per i dettagli; cita anche test e file di prova che non sono nel repository. |
| `LEGGIMI.txt` di ogni cartella | Istruzioni per chi usa i siti (l'ufficio). |

---

## 1. Quadro generale

### 1.1 Cosa fa il sistema

Ogni trimestre o anno l'Ufficio Statistica pubblica su Osserva delle tabelle Excel per ogni tema: commercio estero, imprese, credito, lavoro, popolazione, valore aggiunto, trasporti. Prima queste tabelle si facevano a mano: si scaricavano i dati dai siti delle fonti, si incollavano in fogli di lavoro con formule e si copiavano i risultati nei modelli.

Il sistema automatizza questo lavoro. Per ogni tema c'è una **pagina web** che:

1. ha i dati della fonte, in uno di tre modi: li scarica da sola, li prende già pronti da un aggiornamento automatico, oppure li riceve dall'utente con un trascinamento (§3.3);
2. controlla che ci sia tutto per il periodo scelto e dice cosa manca;
3. calcola le tabelle con le **stesse regole dei fogli di lavoro dell'ufficio**, verificate cella per cella sulle tabelle già pubblicate;
4. produce i file **Excel (.xlsx)** con gli stessi nomi, fogli e intestazioni delle tabelle di Osserva, più uno **ZIP** con tutto.

**Il caricamento su Osserva resta manuale**: lo fa l'ufficio con i file prodotti. Il sistema non scrive su Osserva.

### 1.2 Le aree (sette siti più un sito unico)

| Area | Sezioni | Fonte dei dati | Come arrivano i dati | Tabelle | Sito pubblicato |
|---|---|---|---|---|---|
| **Commercio estero** | Import/Export | ISTAT – Coeweb | La pagina li scarica da ISTAT quando si preme «Genera» | 9–10 | statisticava.github.io/report-import-export |
| **Imprese** | Registrate e attive · Iscrizioni e cessazioni · Procedure concorsuali e scioglimenti | InfoCamere – Stockview | File scaricati a mano da Stockview e trascinati nella pagina, più una serie storica in Excel tenuta dall'ufficio | 9–10 · 7–8 (+1 di controllo) · 10–11 | statisticava.github.io/report-imprese-stockview |
| **Credito** | Depositi · Impieghi · Sofferenze · Sportelli | Banca d'Italia (BDS, servizio A2A) | Automatici (GitHub Actions), con il file ZIP come riserva | 3–4 · 3–4 · 3–4 · 2 | statisticava.github.io/report-credito |
| **Lavoro** | Disoccupazione · Occupazione · Attività · Inattività · Cassa integrazione | ISTAT (Forze di lavoro, SDMX) · INPS (Osservatorio CIG) | Automatici (GitHub Actions) | 6 · 8 · 6 · 6 · 10–11 | statisticava.github.io/report-lavoro |
| **Popolazione** | Popolazione | ISTAT (SDMX) | Automatici (GitHub Actions) | 6 | statisticava.github.io/report-popolazione |
| **Conti economici** | Valore aggiunto | Centro Studi Tagliacarne (file Excel) + ISTAT | Automatici (GitHub Actions) | 6 | statisticava.github.io/report-conti-economici |
| **Trasporti** | Strade (autovetture) | ACI (file «Autoritratto») + ISTAT (popolazione) | Automatici (GitHub Actions) | 6 | statisticava.github.io/report-trasporti |
| **Sito unico** | Tutte le precedenti | (legge i dati dei siti sopra) | — | — | statisticava.github.io/report-osserva |

Quando il numero di tabelle ha due valori (es. «9–10»), le tabelle annuali si producono solo con il IV trimestre.

Tutti i siti stanno sull'account GitHub dell'ufficio **`StatisticaVA`** (GitHub Pages, repository pubblici `StatisticaVA/report-*`). Il **sito unico** (`report-osserva`) riunisce le sette pagine in un solo sito con una grafica comune. È il punto d'ingresso consigliato per l'ufficio. Le pagine originali restano attive e funzionanti (§3.6).

Oltre ai siti c'è un **programma Python** con interfaccia grafica: un estrattore generico di dati ISTAT, che contiene anche il report Import/Export. È descritto al §3.7.

### 1.3 Schema del funzionamento

```
            FONTI                          AGGIORNAMENTO                       PAGINE WEB (GitHub Pages)              USCITA
 ┌──────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
 │ ISTAT Coeweb (CORS ok)   │──────────────────────────────────────────▶│ Commercio estero (scarica in     │
 │                          │   (nessun bot: la pagina chiama ISTAT)    │ diretta quando si preme Genera)  │
 ├──────────────────────────┤   ┌──────────────────────────────────┐   ├──────────────────────────────────┤
 │ Banca d'Italia A2A       │──▶│ GitHub Actions (cron)            │   │ Credito, Lavoro, Popolazione,    │   File .xlsx
 │ ISTAT SDMXWS             │──▶│  aggiorna_dati.py: scarica,      │──▶│ Conti economici, Trasporti       │──▶ + ZIP ──▶ caricamento
 │ INPS Osservatorio CIG    │──▶│  controlla, salva CSV in dati/   │   │ (leggono dati/*.csv dal proprio  │           manuale su
 │ Tagliacarne (Excel)      │──▶│  segnala_problemi.py: e-mail     │   │  sito)                           │           Osserva
 │ ACI (archivio .zip/.rar) │──▶│  solo se qualcosa si rompe       │   │                                  │
 ├──────────────────────────┤   └──────────────────────────────────┘   ├──────────────────────────────────┤
 │ InfoCamere Stockview     │── scaricati a mano dall'ufficio ─────────▶│ Imprese (file trascinati +       │
 │ (nessuna API)            │                                           │ serie storica Excel in/out)      │
 └──────────────────────────┘                                           └──────────────────────────────────┘
                                                                         Sito unico (report-osserva): stesse pagine,
                                                                         legge i dati automatici dai siti sopra
```

---

## 2. Contenuto del repository

```
osserva-sistema/
├── README.md                      da dove partire
├── docs/                          01_DOCUMENTAZIONE_TECNICA, 02_TABELLE_DI_OUTPUT, HANDOVER (.md e .docx)
└── codice/
    ├── 1_Estrattore_Python/       estrattore SDMX generico + report Import/Export (Python)
    ├── 2_Versione_Web_GitHub/     sito Commercio estero           = repo StatisticaVA/report-import-export
    ├── 6_Web_Imprese_Stockview/   sito Imprese                    = repo StatisticaVA/report-imprese-stockview
    ├── 7_Web_Credito_BancaItalia/ sito Credito                    = repo StatisticaVA/report-credito
    ├── 8_Web_Lavoro/              sito Lavoro                     = repo StatisticaVA/report-lavoro
    ├── 9_Web_Popolazione/         sito Popolazione                = repo StatisticaVA/report-popolazione
    ├── 10_Web_ContiEconomici/     sito Conti economici            = repo StatisticaVA/report-conti-economici
    ├── 11_Web_Trasporti/          sito Trasporti                  = repo StatisticaVA/report-trasporti
    └── 12_Web_Sito_Unico/         costruisci_sito.py + sorgenti/ → sito/ = repo StatisticaVA/report-osserva
```

I numeri delle cartelle sono quelli originali: le cartelle 3, 4 e 5 erano versioni precedenti o strumenti secondari e non fanno parte del repository.

**File di ogni sito**

| File | Presente in | Ruolo |
|---|---|---|
| `index.html` | tutti i siti | La pagina: motore (`<script id="motore">`) e interfaccia (§3.2). |
| `LEGGIMI.txt` | tutti i siti | Istruzioni per l'ufficio. |
| `aggiorna_dati.py` (+ `aggiorna_cig.py` nel Lavoro) | 7, 8, 9, 10, 11 | **Estrazione ed elaborazione**: scarica, filtra, controlla e salva i dati in `dati/` (§3.4). |
| `segnala_problemi.py` | 7, 8, 9, 10, 11 | Avviso per e-mail quando l'aggiornamento non riesce (§3.4, §8.1). |
| `.github/workflows/*.yml` | 7, 8, 9, 10, 11 | Calendario e passi dell'aggiornamento automatico (§3.5). |
| `dati/*.csv`, `dati/aggiornamento.json` | 7, 8, 9, 10, 11 | Dati letti dalla pagina e stato dell'ultimo aggiornamento. Il contenuto dei CSV è descritto in `02_TABELLE_DI_OUTPUT.md`, nei paragrafi «Dati di input». |

Il sito Commercio estero (`2_…`) ha solo `index.html` e `LEGGIMI.txt`, perché scarica i dati da ISTAT Coeweb al momento. Anche il sito Imprese (`6_…`) ha solo questi due file, perché lavora sui file caricati dall'ufficio. Il sito unico (`12_…`) contiene:
- `costruisci_sito.py`;
- `sorgenti/` (grafica, logo, font);
- `sito/`, il risultato pubblicato (§3.6).

L'estrattore Python (`1_…`) è descritto al §3.7.

**Provare in locale**: `python3 -m http.server 8000` dentro `codice/`, poi aprire ad esempio `http://localhost:8000/7_Web_Credito_BancaItalia/` e premere «Genera». Le pagine funzionano anche aperte con doppio clic su `index.html`: in quel caso leggono i dati automatici dai siti online.

**Rapporto con i siti online.** Al 12/10/2026 queste cartelle sono identiche, file per file, ai repository pubblicati. Da qui in poi **i dati vivi stanno nei repository dei siti**: i bot salvano ogni settimana o ogni mese i CSV aggiornati nella loro cartella `dati/`. Le cartelle `dati/` di questo repository sono una fotografia al 12/10/2026.

I workflow GitHub dentro `codice/*/.github/workflows/` funzionano solo alla radice del loro repository. Qui sono quindi **inattivi**, ed è voluto: non partono bot doppi.

La serie storica delle imprese (`Storico_imprese_Varese.xlsx`) è un file dell'ufficio e non è in questo repository: l'ufficio la carica nella pagina ogni trimestre (§3.3).

---

## 3. Architettura

### 3.1 Principi comuni a tutte le pagine (decisi con l'ufficio)

- **Un solo file `index.html` per sito, nessuna dipendenza esterna**: niente librerie, CDN, framework né server. I file Excel e ZIP sono scritti dal codice della pagina, che genera direttamente l'XML di Office Open XML e il formato ZIP. Le pagine così restano «integre nel tempo» e non si rompono se una libreria cambia.
- **Funzionano sia pubblicate (GitHub Pages) sia aperte con doppio clic** dal disco (`file://`). Aperta da disco, una pagina con dati automatici li legge dal sito online (`URL_DATI_ONLINE`). GitHub Pages risponde con `Access-Control-Allow-Origin: *`, quindi la lettura funziona.
- **I file dell'utente non escono dal computer**: i file trascinati (Stockview, ZIP della Banca d'Italia…) si leggono solo nel browser.
- **Excel di output**:
  - numeri salvati come numeri veri, non come testo con la virgola;
  - intestazione in grassetto o blu come nei modelli;
  - nomi di file, fogli, intestazioni ed etichette **uguali alle tabelle già pubblicate su Osserva**, comprese alcune stranezze dei modelli, conservate apposta. Le differenze volute sono elencate in `02_TABELLE_DI_OUTPUT.md`.
- **Controllo prima di generare**: la pagina dice quale tabella è pronta, quale sarebbe incompleta (con celle vuote) e quale file o dato manca. Un periodo non ancora pubblicato dalla fonte viene rifiutato con un messaggio chiaro, ad esempio «ISTAT non ha ancora pubblicato i dati annuali 2026 … (ultimo anno disponibile: 2025)».
- **I calcoli si rifanno sempre sui dati più recenti della fonte.** Se la fonte rivede i dati passati, rigenerare un periodo vecchio può dare numeri leggermente diversi dalla tabella pubblicata allora. È voluto: le vecchie tabelle di Osserva avevano spesso righe copiate prima delle revisioni.

### 3.2 Com'è fatta una pagina

Ogni `index.html` ha:
- `<style>` e l'HTML dell'interfaccia (passi numerati: periodo → dati → controllo → genera → file pronti);
- **`<script id="motore">`**: tutta la logica di lettura, controllo e calcolo, più la scrittura di Excel e ZIP. Non tocca il DOM. In fondo esporta le funzioni con `module.exports` quando gira in Node: così i test eseguono **lo stesso codice** della pagina (lo caricano con il modulo `vm` di Node);
- un secondo `<script>`: l'**interfaccia** (eventi, trascinamento dei file, lettura dei dati automatici, download).

Funzioni ricorrenti nei motori, spesso copiate identiche da una pagina all'altra:

| Funzione | Cosa fa |
|---|---|
| `round2`, `arrotonda`, `R1`/`R2` | Arrotondamento **come ARROTONDA/ROUND di Excel** (metà lontano da zero, su 15 cifre significative). Con `toFixed` di JavaScript alcune celle verrebbero diverse dai fogli dell'ufficio. |
| `creaXlsx` / `foglioXml` | Scrivono il file .xlsx a mano: `[Content_Types].xml`, `workbook.xml`, `styles.xml` con un registro degli stili (formati numerici, grassetto, allineamento), `sheet1.xml` con stringhe inline, larghezze delle colonne, altezza della riga 1, riquadro bloccato quando il modello lo ha. |
| `creaZip` | ZIP senza compressione (CRC32, nomi in UTF-8): serve sia dentro ogni .xlsx sia per lo ZIP finale. |
| `indiceZip`, `inflateRaw` (`DecompressionStream`), `apriXlsx`, `leggiFoglioXml` | Lettura nel browser di ZIP ed Excel caricati dall'utente: file Stockview in .xlsx, ZIP della Banca d'Italia, Excel di Tagliacarne. |
| `parseCsv` / `leggiCsv…` | Lettura dei CSV, tollerante a separatori `,`/`;`/tab, virgolette, BOM, CRLF e colonne in ordine diverso. Le colonne si riconoscono per nome. |
| `controllaAnno` / `controllaPeriodo` / `ultimoAnno` / `ultimoTrimestre` | Ultimo periodo disponibile e messaggi su cosa manca. |
| `generaReport…` | Restituisce `{cartella, file: [{nome, dati}]}`, cioè i file della cartella `Report_<tema>_<periodo>`. |

### 3.3 I tre modi in cui arrivano i dati

1. **In diretta dal browser: solo Commercio estero.** Il servizio ISTAT **Coeweb** (`esploradati.istat.it/Coeweb/databrowserhub`) accetta richieste da qualunque origine (CORS), anche da una pagina aperta con doppio clic. La pagina fa 3–4 richieste POST al momento, rispettando il limite ISTAT di circa 5 richieste al minuto (pausa di 13 secondi tra una richiesta e l'altra).
2. **Automatici, scaricati da un bot: Credito, Lavoro, Popolazione, Conti economici, Trasporti.** Le altre fonti (ISTAT SDMXWS, Banca d'Italia, INPS, Tagliacarne, ACI) **non permettono** chiamate dal browser (niente CORS) oppure non hanno un'API. Un workflow **GitHub Actions** del repository di ogni sito scarica i dati a orari fissi, li controlla e li salva come CSV nella cartella `dati/` del repository. La pagina li legge da lì. Come riserva la pagina mostra i link per scaricare a mano i file della fonte e permette di trascinarli: i file caricati prevalgono sui dati automatici.
3. **File caricati a mano: Imprese.** InfoCamere/Stockview non ha un'API: l'ufficio scarica ogni trimestre alcuni file da Stockview e li trascina nella pagina insieme alla **serie storica** `Storico_imprese_Varese.xlsx`. La pagina aggiorna la serie storica e ne restituisce una copia nuova, che l'ufficio conserva per il trimestre dopo. La serie storica è un file dell'ufficio, volutamente **non** pubblicato su GitHub.

### 3.4 L'aggiornamento automatico (GitHub Actions)

Ogni sito con dati automatici ha nel proprio repository:

| File | Ruolo |
|---|---|
| `aggiorna_dati.py` (per il Lavoro anche `aggiorna_cig.py`) | Scarica, controlla e scrive i CSV in `dati/` e il file `dati/aggiornamento.json`. Usa **solo la libreria standard di Python**: niente `pip install`. |
| `segnala_problemi.py` | Se qualcosa non ha funzionato apre una **issue** nel repository. GitHub la manda per e-mail all'account `StatisticaVA` perché la issue lo cita con `@StatisticaVA`. |
| `.github/workflows/aggiorna-*.yml` | Quando lanciare lo script (cron), il salvataggio dei dati e l'avviso. |
| `dati/*.csv` | I dati filtrati: solo i territori e le serie che servono. |
| `dati/aggiornamento.json` | Per ogni tavola: data dello scaricamento, ultimo periodo, numero di righe, data di aggiornamento della fonte (es. `LAST_UPDATE` di ISTAT, `DateAgg` di INPS), avvisi. La pagina lo mostra («Dati aggiornati al …»). |

**Come lavora `aggiorna_dati.py`** (stesso schema in tutti i siti):
1. Per ogni tavola chiede i dati alla fonte. Ripete i tentativi con pause crescenti (es. 1, 3, 5 minuti); dopo un guasto di rete, le tavole successive fanno un solo tentativo.
2. **Controlla** quello che arriva:
   - colonne e codici attesi;
   - territori presenti (Varese, Lombardia, Italia, province);
   - valori numerici;
   - l'ultimo periodo non deve essere più vecchio di quello salvato;
   - le righe devono essere almeno il 90% di prima;
   - le somme devono tornare (es. le 12 province = Lombardia);
   - le variazioni non devono essere anomale (soglie di avviso e di blocco: Tagliacarne e ACI).

   Se un controllo fallisce, **i dati salvati non vengono toccati**.
3. Ogni problema ha un tipo:
   - `rete`: la fonte non risponde;
   - `risposta`: arriva una pagina di manutenzione invece dei dati;
   - `formato`: la tavola è cambiata (colonne o codici diversi);
   - `anomalia`: dati più vecchi, meno righe o valori fuori soglia;
   - `riservato`: solo INPS, una tavola rifiutata per riservatezza;
   - `prova` e `imprevisto`.
4. Con `--esito FILE` lo script scrive l'esito in JSON e **termina sempre con 0**: le tavole senza problemi vengono salvate lo stesso. Lanciato a mano senza `--esito`, esce con 1 se ci sono problemi.
5. Il CSV si riscrive solo se il contenuto cambia.

**Il workflow** ha tre passi:
1. «Scarica»;
2. «Salva i dati nel repository»: `git commit` e `git push` solo se è cambiato qualcosa, con un `git pull --rebase` prima del push;
3. «Avvisa per e-mail se qualcosa non ha funzionato» (`if: always()`).

Regole del salvataggio:
- se cambia solo `aggiornamento.json`, il bot salva soltanto **una volta al mese**. GitHub disattiva i cron dei repository pubblici dopo 60 giorni senza attività: questo commit mensile li tiene attivi;
- ogni workflow ha `concurrency: group: aggiorna-dati`, così due esecuzioni non scrivono insieme;
- il pulsante manuale «Run workflow» ha alcune caselle:
  - **«Prova»**: simula un errore per controllare che l'e-mail arrivi. La prova non è più stata rifatta per scelta dell'ufficio: ogni prova manda un'e-mail;
  - **«Forza»**: riscarica anche se la fonte non ha novità;
  - **«Accetta»**: solo Conti economici e Trasporti; accetta una revisione grande che altrimenti verrebbe bloccata.

**L'e-mail di avviso** arriva **solo quando qualcosa si rompe**, non quando la fonte non ha pubblicato dati nuovi: quello è normale.
- Se il problema si ripete, nella stessa issue compare un commento «si è ripresentato».
- Alla prima esecuzione riuscita la issue si **chiude da sola** con il commento «✅ Risolto».
- Gli avvisi di INPS hanno un'etichetta separata da quelli di ISTAT.
- Se non riesce nemmeno ad aprire la issue, il passo fallisce e GitHub manda la sua e-mail generica di workflow fallito.

### 3.5 Calendario dei controlli automatici

Gli orari sono in UTC: in Italia sono 2 ore in più con l'ora legale, 1 con l'ora solare.

| Repository | Workflow | Quando (cron) | Cosa scarica | Quando la fonte pubblica |
|---|---|---|---|---|
| `report-credito` | Aggiorna dati Banca d'Italia | `0 18 28-31 * *` e `0 6 2 * *` (giorni 28–31 alle 18 e giorno 2 alle 6) | 7 tavole: TDB10290, TDB10295, TRI30401, TDB20207, TDB20220, TDB10227, TSDPT140 | Tavole mensili tra il 27 e la fine del mese, con circa 2 mesi di ritardo; sofferenze trimestrali; sportelli a fine marzo; ATM a maggio |
| `report-lavoro` | Aggiorna dati ISTAT | `0 6 * * 1` (ogni lunedì) | 8 tavole delle Forze di lavoro (disoccupazione, occupazione, attività, inattività) | Annuali: uscita tra marzo e aprile, revisioni in autunno (ultima: 11/09/2026) |
| `report-lavoro` | Aggiorna dati INPS (cassa integrazione) | `0 6 2-12 * *` (giorni 2–12 di ogni mese) | Ore autorizzate CIG: territori, classi di attività, serie mensile di Varese | Mensile, con circa 3 mesi di ritardo; scarica solo se `DateAgg` di INPS cambia |
| `report-popolazione` | Aggiorna dati ISTAT | `0 6 * * 1` (ogni lunedì) | 6 tavole della popolazione al 1° gennaio | Fine marzo (bilancio rivisto in autunno) |
| `report-conti-economici` | Aggiorna dati valore aggiunto | `0 6 * * *` (ogni giorno) | Pagina e file Excel di Tagliacarne (28 KB) e valore aggiunto e popolazione ISTAT. ISTAT si riscarica solo se `LAST_UPDATE` cambia o dopo 28 giorni | Tagliacarne tra fine ottobre e novembre (prossimo: il 2025, atteso tra ottobre e novembre 2026); ISTAT a dicembre |
| `report-trasporti` | Aggiorna dati trasporti | `0 6 * * *` (ogni giorno) | Pagina Open data ACI: richiesta HEAD al file; scarica l'archivio solo se è cambiato. Più la popolazione ISTAT | ACI «Autoritratto» entro luglio (a volte novembre) |

### 3.6 Il sito unico (`12_Web_Sito_Unico`)

`costruisci_sito.py` (solo libreria standard) legge le 7 pagine originali e ne prende **identici** il motore, lo script dell'interfaccia e il `<main>`. Li inserisce in una grafica comune:
- testata con il logo;
- menu dei temi;
- schede delle sezioni con link diretti, nella forma `tema/index.html#sezione=<valore>`;
- home con lo «Stato dei dati», letto in diretta da `aggiornamento.json` di ogni sito.

Il risultato va nella cartella `sito/`, che è il repository `StatisticaVA/report-osserva`.

Il sito unico **non ha un bot**: legge i dati automatici dai siti originali (`URL_DATI_ONLINE = https://statisticava.github.io/report-*/dati/`). **I repository dei siti originali devono quindi restare attivi.**

Le uniche modifiche al codice copiato sono cinque:
1. non si prova la cartella `dati/` locale;
2. i titoli dei passi sono diversi;
3. `id="contenuto"` sul `<main>`;
4. la classe del piè di pagina;
5. «Ultimo controllo» diventa «Dati aggiornati al».

Dopo ogni modifica a un sito originale bisogna:
1. lanciare `python3 costruisci_sito.py`;
2. provare `sito/` in locale;
3. pubblicare `sito/` nel repository `StatisticaVA/report-osserva`.

### 3.7 I programmi Python

| Cartella | Programma | Note |
|---|---|---|
| `1_Estrattore_Python` | **Estrattore SDMX generico** (`sdmx_gui.py`, interfaccia tkinter) | Scarica le «query salvate» ISTAT (`query_salvate.py`) in Excel. Serve Python 3 con `requests pandas openpyxl lxml`; si avvia con i file `Avvia … (Mac).command` / `(Windows).bat`. Contiene anche `report_import_export.py`, che produce **gli stessi Excel** del sito Commercio estero (verificato cella per cella). |

Oggi l'uso quotidiano passa dai siti. Il programma Python resta come alternativa per il commercio estero e come strumento per estrarre altre tavole ISTAT.

---

## 4. Le fonti dei dati e le loro API

| Fonte | Accesso | Formato | CORS (pagina nel browser) | Particolarità |
|---|---|---|---|---|
| **ISTAT Coeweb** (commercio estero) | `POST https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/{IT1,DATASET,1.0}/data`, corpo JSON con i filtri, header `UserLang: it` | JSON-stat 2.0 | **Sì**, anche da `file://` | Circa 5 richieste al minuto per indirizzo IP. Il dataset `DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ` parte dal 2020; per la serie annuale più vecchia si usa `DF_CPA_AT2007_COE_OPT_A_REG_ALL`. ISTAT rivede i trimestri precedenti a ogni uscita. |
| **ISTAT SDMXWS** (forze di lavoro, popolazione, valore aggiunto) | `GET https://esploradati.istat.it/SDMXWS/rest/data/{flow}/{chiave}?startPeriod=…&format=csvfile`; data di aggiornamento: `…/dataflow/IT1/{id}/1.0` (annotazione `LAST_UPDATE`) | CSV SDMX | **No** → bot | Limite di circa 5 richieste al minuto: con troppe richieste l'indirizzo viene **bloccato per ore**. Il Mac dell'ufficio a volte non riusciva a collegarsi; i server di GitHub sì. Codici dei territori: Italia `IT`, Lombardia `ITC4`, Varese `ITC41`, Milano `ITC45`, Monza `IT108` (diversi da quelli della Banca d'Italia). |
| **Banca d'Italia – A2A** | `GET https://a2a.bancaditalia.it/infostat/dataservices/export/IT/CSV/{DATA\|ALL}/CUBE/BANKITALIA/DIFF/{TAVOLA}` | ZIP con CSV (circa 5 MB, 600.000 righe) | **No** → bot | Nessun filtro lato server: lo script filtra Varese, Lombardia e Italia. Valori in **migliaia** di euro (`SCALA=3` in `_STRUCTURE.csv`). Le colonne cambiano da tavola a tavola: `LOC_CTP`, `SEDELEG_SOGG`, `LOC_SPORT`; TSDPT140 è a serie storiche. Rivede l'anno precedente a ogni uscita. |
| **INPS – Osservatorio Cassa integrazione** | `POST https://servizi2.inps.it/servizi/osservatoristatistici/api/getDatiOsservatorio/` e `getStrutturaOsservatorio/` | JSON | **No** → bot | Il corpo JSON va mandato **compatto**, senza spazi, altrimenti risponde «not a valid Base-64 string»; la risposta è gzip. Osservatori 512 (mensile dal 2023) e 304 (mensile 2009–2022). Rifiuta alcune tavole di dettaglio per **riservatezza** («Anonimizzazione»): per questo si scaricano i periodi cumulati. Data di aggiornamento: `DateAgg`. |
| **Centro Studi Tagliacarne** (valore aggiunto) | Pagina «Statistiche territoriali», link al file Excel «Valore aggiunto per provincia e branca… Anno AAAA (versione …)» | Excel (.xlsx, 28 KB) | **No** → bot | **Nessuna API.** L'indirizzo del file contiene la data di caricamento e cambia: lo script lo ritrova nella pagina dal testo del link. Rivede gli anni passati. C.Stat (piattaforma SDMX delle Camere di commercio) potrebbe dare un accesso programmatico: è da chiedere (§9). |
| **ACI – Open data** (autovetture) | Pagina https://aci.gov.it/attivita-e-progetti/studi-e-ricerche/open-data/, archivio «Autoritratto» dell'anno | .zip o .rar (RAR5) con fogli ODS | **No** → bot | **Nessuna API**, un archivio all'anno con un indirizzo che cambia. Per i .rar sul runner viene installato `bsdtar` (`libarchive-tools`). Il layout dei fogli è cambiato tra le edizioni 2019–2023 e quelle 2024–2025; lo script legge quello 2024–2025. |
| **InfoCamere – Stockview** (imprese) | Download a mano dall'ufficio | CSV o testo a colonne | — | **Nessuna API**: l'elenco dei file da scaricare è in §7. |

---

## 5. Regole di calcolo comuni

Valgono per tutte le tabelle salvo diversa indicazione in `02_TABELLE_DI_OUTPUT.md`:

- **Arrotondamento** come ARROTONDA di Excel (metà lontano da zero). Le variazioni si arrotondano a 2 decimali.
- **Variazione %**: `ARROTONDA(nuovo / vecchio × 100 − 100; 2)`.
  - Per Import/Export si usa `|vecchio|` al denominatore, così la variazione dei saldi negativi ha senso.
  - Alcune sezioni (Lavoro: disoccupati, forze di lavoro, inattivi, occupati) calcolano la variazione **sui valori già arrotondati**, come facevano i fogli dell'ufficio.
  - Se il valore di confronto è 0 o manca, la cella resta vuota; per la Cassa integrazione si scrive `n.d.`.
- **Peso / quota %**: `valore / totale × 100`, arrotondato a 2 decimali dove il modello lo fa.
- **Variazione tendenziale** = sullo stesso periodo dell'anno prima. **Congiunturale** = sul periodo immediatamente precedente.
- **Cumulati** da inizio anno per i **flussi**: import/export, iscrizioni e cessazioni, aperture di procedure, ore di cassa integrazione. Il II trimestre vale gennaio–giugno, confrontato con gennaio–giugno dell'anno prima. Gli **stock** (imprese registrate, depositi, popolazione…) sono a fine periodo e non si cumulano. Le tabelle «tempo trimestrale» usano i trimestri singoli.
- **Tabelle annuali solo con il IV trimestre** (e, per Import/Export, solo se ISTAT ha già pubblicato il dato annuale).
- **Righe «ITALIA\*»** delle tabelle territori: il peso è quello della **Lombardia sull'Italia**, non dell'Italia su sé stessa (come i modelli di Osserva).
- **Celle vuote volute**: righe titolo, prima variazione di una serie… Non vengono contate come dati mancanti.

---

## 6. Account, hosting e accessi

- **Account GitHub dell'ufficio: `StatisticaVA`.** Ospita tutti i siti, con un repository pubblico per sito e GitHub Pages dal ramo `main`, cartella `/`. Le e-mail di avviso dei bot arrivano all'indirizzo di questo account: nelle impostazioni di GitHub le notifiche e-mail devono restare attive (lo sono di default). Le credenziali sono dell'ufficio.
- I repository sono **pubblici**: le pagine non contengono dati riservati, e la serie storica delle imprese non è pubblicata. GitHub Pages e GitHub Actions sono gratuiti per i repository pubblici.
- **Pubblicare** = fare un commit sul ramo `main` del repository del sito: GitHub Pages si aggiorna in circa un minuto. Autore dei commit usato finora: «Ufficio Statistica Varese» (`335452230+StatisticaVA@users.noreply.github.com`).
- Per far lavorare altre persone sui siti si possono aggiungere come **collaboratori** dei repository (Settings → Collaborators) senza condividere la password dell'account.
- **Attenzione alle credenziali git** sul Mac: se git usa un altro account salvato nel portachiavi, il push su `StatisticaVA` dà 403. Nei cloni conviene usare come credential helper solo `gh auth git-credential`.

---

## 7. Cosa fa l'ufficio, e quando

| Tema | Periodicità del report | Cosa fare |
|---|---|---|
| Commercio estero | Trimestrale | Aprire il sito, scegliere anno e trimestre, premere «Genera». I dati arrivano da ISTAT in 1–2 minuti. ISTAT pubblica il trimestre provinciale circa 2,5 mesi dopo la fine del trimestre (il II trim 2026 era disponibile il 14/09/2026). |
| Imprese – registrate e attive, iscrizioni e cessazioni | Trimestrale | Scaricare da Stockview: dati grezzi «sedi d'impresa» di Varese `TAAAAVAS.csv` (es. `22026VAS.csv` = II trim 2026); i tre mesi `AAAAMM_m.csv` (il terzo è facoltativo); le province lombarde `AAAAT_sa.csv`; l'Italia `AAAAT_sa (1).csv`. Trascinarli nella pagina con `Storico_imprese_Varese.xlsx`, generare e **salvare la nuova serie storica** restituita. |
| Imprese – procedure concorsuali | Trimestrale | Scaricare i tre file mensili di Varese `AAAAMM_me.csv` (Classe Evento, Settore, Classe di Natura Giuridica), i tre delle province `AAAAMM_me (1).csv` e lo stock per status d'impresa `AAAAT_sa.csv`. Per i report del III e IV trim 2026 il controllo chiederà una volta sola anche lo stock del III e IV trim 2025. |
| Credito | Trimestrale (sportelli annuale) | Aprire il sito: i dati sono già lì. Se il riquadro è arancione (dati automatici non disponibili), scaricare lo ZIP dal link e trascinarlo. |
| Lavoro – ISTAT | Annuale (marzo–aprile) | Aprire il sito, scegliere sezione e anno, «Genera». |
| Lavoro – Cassa integrazione | Trimestrale | Come sopra (anno e trimestre). INPS pubblica con circa 3 mesi di ritardo. |
| Popolazione | Annuale (fine marzo) | Come sopra. L'ultimo 1° gennaio è provvisorio, e la pagina lo segnala. |
| Conti economici | Annuale (Tagliacarne tra ottobre e novembre) | Come sopra. Quando esce il file Tagliacarne nuovo, controllare gli avvisi in `aggiornamento.json` (§9). |
| Trasporti | Annuale (ACI a luglio) | Come sopra. |

---

## 8. Manutenzione

### 8.1 Quando arriva un'e-mail di avviso

L'e-mail apre una issue nel repository del sito con il testo in italiano: cosa è successo per ogni tavola, fino a quando arrivano i dati rimasti sul sito (che **non** vengono cancellati), cosa fare e il link all'esecuzione.

| Tipo | Significato | Cosa fare |
|---|---|---|
| `rete` | La fonte non risponde | Di solito niente: il controllo successivo riprova. Se dura giorni, verificare che il sito della fonte funzioni. |
| `risposta` | La fonte ha risposto con una pagina che non contiene dati (manutenzione) | Come sopra. |
| `formato` | La tavola è cambiata: colonne, codici, classi, province, layout dei fogli | **Serve un intervento sul codice**: confrontare la nuova struttura con i controlli di `aggiorna_dati.py` e con la lettura nella pagina, poi adattare e testare. |
| `anomalia` | Dati più vecchi di quelli salvati, molte righe in meno, variazioni oltre soglia | Verificare sul sito della fonte. Se è una revisione vera: rilanciare il workflow con «Accetta» (Conti e Trasporti) o adattare la soglia. |
| `riservato` (INPS) | INPS ha rifiutato una tavola per riservatezza | Gli altri dati sono aggiornati: mancano solo le tabelle che usano quella tavola. |
| `imprevisto` | Errore non previsto o passo del workflow interrotto | Leggere il log dell'esecuzione (link nell'issue). |

La issue si chiude da sola quando un'esecuzione successiva va a buon fine. Per far ripartire subito il controllo: scheda **Actions** → workflow → **Run workflow**.

### 8.2 Modificare un sito e pubblicarlo

1. Modificare `codice/<cartella>/index.html` (o lo script). **Nel motore non usare librerie esterne** e **non inserire caratteri di controllo**: un byte NUL nel file fa scartare l'intero script al browser.
2. Provare nel browser: `python3 -m http.server` sulla cartella del sito, «Genera», e confrontare i file prodotti con quelli di prima. I motori espongono le funzioni con `module.exports`, quindi si possono anche eseguire in Node per test automatici (§8.4).
3. Pubblicare:
   1. clonare `StatisticaVA/<repo>`;
   2. fare **`git pull` prima**: i bot salvano i dati da soli e non bisogna sovrascrivere `dati/` con dati vecchi;
   3. copiare solo i file modificati;
   4. fare commit e push;
   5. controllare il sito online.

   Prima di cambiare un repository conviene creare un tag di backup (sono già stati usati `v1.3-prima-cig`, `v-prima-logo`…).
4. Rigenerare e ripubblicare il **sito unico** (§3.6).
5. Aggiornare `LEGGIMI.txt` della cartella e la documentazione.

### 8.3 Aggiungere una sezione o un tema

Il metodo usato per tutte le sezioni, che ha funzionato bene:
1. Farsi dare dall'ufficio **il foglio di lavoro fatto a mano** (dati incollati e formule) e **le tabelle di Osserva** di un periodo.
2. Da lì ricavare fonte, tavola, filtri e regole; verificare che i dati della fonte coincidano con quelli del foglio **prima** di scrivere codice.
3. Implementare nel motore le funzioni `tab…` e, se servono dati nuovi, una voce in `TAVOLE` di `aggiorna_dati.py`.
4. Confrontare **cella per cella** le tabelle prodotte con quelle di Osserva e spiegare ogni differenza: revisione della fonte, errore del modello o scelta voluta.
5. Verificare con test automatici (§8.4).
6. Pubblicare (§8.2).

Dove intervenire nel codice:
- **Credito**: `SEZIONI` nel motore (tavola, fenomeno, ente, settori, forma delle tabelle) e `TAVOLE` in `aggiorna_dati.py`;
- **Lavoro**: `TAVOLE`, `SEZIONI`, `DIMENSIONI_TIPO` e le funzioni `tab…` di ogni sezione nel motore, `TAVOLE` in `aggiorna_dati.py`;
- **Commercio estero**: le funzioni `tab…` e `generaReport` nel motore di `index.html` e, se lo si usa ancora, `report_import_export.py`.

### 8.4 I test

Durante lo sviluppo ogni sezione è stata verificata in tre modi:
- **test in Node** che eseguono il motore vero della pagina, caricato con il modulo `vm`, su dati reali e simulati;
- **verifiche in Python** che ricalcolano ogni cella in modo indipendente e la confrontano con le tabelle già pubblicate su Osserva;
- **prove di sensibilità**: errori inseriti apposta nel codice, che i test devono trovare.

Per gli script di aggiornamento ci sono test con le fonti simulate, senza internet, che provano anche gli avvisi via e-mail.

Questi test e i file di prova non sono in questo repository: li conserva l'Ufficio Statistica, che può fornirli.

---

## 9. Rischi noti e punti aperti

1. **Tagliacarne rivede gli anni passati.** Per il valore aggiunto, l'anno N viene dal file Tagliacarne nuovo e l'anno N−1 dal file Tagliacarne dell'anno prima, archiviato. Se Tagliacarne rivede molto l'anno N−1, la variazione N/N−1 è falsata. Lo script avvisa se la crescita di un territorio si discosta da quella dell'Italia. **Da controllare quando esce il file 2025** (atteso tra ottobre e novembre 2026). Il 2023 nell'archivio è un valore «congelato» di Osserva: non esiste una fonte aperta per quel dato. Un accesso SDMX a **C.Stat** (`cstat@tagliacarne.it`) risolverebbe tutti e due i problemi.
2. **Fonti senza API** (Stockview, Tagliacarne, ACI): se cambiano il formato dei file o della pagina, gli script si fermano con un avviso `formato` e serve un intervento sul codice.
3. **GitHub Actions.** `actions/checkout@v4` gira su Node 20, deprecato; `ubuntu-latest` passa a Ubuntu 26 dal 19/10/2026. Oggi non c'è da fare nulla. Se un workflow si rompe per questo motivo, aggiornare a `actions/checkout@v5`. I cron si fermano se un repository resta 60 giorni senza commit: lo evitano i salvataggi mensili dei bot.
4. **Limiti ISTAT**: con troppe richieste di fila l'indirizzo IP viene bloccato per ore. Rispettare la pausa di 13 secondi; per le prove usare il workflow su GitHub.
5. **Revisioni delle fonti**: ISTAT, Banca d'Italia e INPS rivedono i dati passati. Rifare un periodo vecchio può dare numeri leggermente diversi dalla tabella pubblicata allora. È voluto (§3.1).
6. **Punti da decidere o segnalare**:
   - Trasporti: «Gasolio e gas» (2 auto nel 2025) è conteggiato tra i Gasolio, mentre Osserva 2025 lo metteva tra gli ibridi gasolio. Da confermare: è una riga, `MAPPA_ALIM` in `11_Web_Trasporti/index.html`.
   - Errori nelle tabelle già pubblicate su Osserva, da segnalare a chi gestisce il sito: le variazioni CIGO/CIGS del I trim '26 sono calcolate sul trimestre sbagliato; nella pagina dei settori dell'occupazione alcuni numeri sono troncati.
7. **Imprese**: la serie storica è un file tenuto dall'ufficio. Se va perso, si ricostruisce solo ricaricando i vecchi download di Stockview: conservarne copie.
8. Nel repository `report-lavoro` sono rimasti registrati due workflow temporanei di esplorazione, «Prova INPS (temporaneo)» ed «Esplora tavole ISTAT (Attività)». Il loro ramo è stato cancellato e sono innocui.

---

## 10. Glossario

| Termine | Significato |
|---|---|
| Osserva | Osservatorio economico della Camera di Commercio di Varese: il sito dove l'ufficio pubblica le tabelle. |
| Modello | Tabella Excel già pubblicata su Osserva. Il sistema ne riproduce nomi, fogli, intestazioni e righe. |
| Foglio di lavoro | File Excel dell'ufficio con i dati incollati e le formule, da cui sono state ricavate le regole di calcolo. |
| Motore | Lo `<script id="motore">` di una pagina: tutta la logica di calcolo. |
| Bot | Il workflow GitHub Actions che aggiorna i dati di un sito. |
| SDMX / SDMXWS | Standard per lo scambio di dati statistici / il servizio SDMX di ISTAT. |
| Coeweb | Banca dati ISTAT del commercio estero. |
| A2A | Servizio di scarico dei dati della Banca d'Italia. |
| CORS | Regola dei browser: una pagina può leggere dati da un altro sito solo se quel sito lo permette. Da qui la necessità dei bot. |
| Cumulato | Somma da inizio anno fino al periodo scelto. |
| T.var% tend. / cong. | Variazione tendenziale (sullo stesso periodo dell'anno prima) / congiunturale (sul periodo precedente). |
| CIGO / CIGS / CIGD | Cassa integrazione ordinaria / straordinaria / in deroga. |
| CESNUF | Cessazioni non d'ufficio (Stockview): sono le «cessate» dei report. |
