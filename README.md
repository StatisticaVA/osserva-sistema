# Sistema dei report per Osserva – Camera di Commercio di Varese

Questo repository contiene il sistema che prepara le tabelle statistiche dell'Ufficio Statistica da caricare su **Osserva** (https://www.osserva-varese.it). I temi sono: commercio estero, imprese, credito, lavoro, popolazione, valore aggiunto e trasporti.

Contiene tre cose:
- il **codice dei siti** che producono le tabelle;
- gli **script che estraggono ed elaborano i dati** dalle fonti (ISTAT, Banca d'Italia, INPS, Tagliacarne, ACI);
- la **documentazione**.

Stato al **12 ottobre 2026**.

---

## 1. Come funziona, in breve

Per ogni tema c'è un **sito**: una pagina HTML statica, senza librerie esterne. La pagina:
- legge i dati;
- controlla che ci sia tutto per il periodo scelto;
- calcola le tabelle con le regole dell'ufficio;
- produce i file **Excel** da caricare su Osserva, più uno ZIP con tutto.

Il caricamento su Osserva lo fa l'ufficio, a mano.

I dati arrivano in tre modi:

| Modo | Siti | Come |
|---|---|---|
| **In diretta** | Commercio estero | La pagina chiama l'API **ISTAT Coeweb** quando si preme «Genera». Coeweb accetta richieste dal browser, quindi non serve altro. |
| **Automatici** | Credito, Lavoro, Popolazione, Conti economici, Trasporti | Uno script Python (`aggiorna_dati.py`), lanciato a orari fissi da **GitHub Actions**, scarica i dati dalle fonti, li controlla e li salva come CSV nella cartella `dati/` del sito. La pagina legge quei CSV. Se qualcosa si rompe, `segnala_problemi.py` manda un'e-mail. |
| **File caricati a mano** | Imprese | Stockview (InfoCamere) non ha un'API: l'ufficio scarica alcuni file ogni trimestre e li trascina nella pagina, insieme alla serie storica `Storico_imprese_Varese.xlsx` tenuta dall'ufficio. |

Il **sito unico** riunisce tutte le pagine in un solo sito con una grafica comune.

## 2. Contenuto del repository

```
osserva-sistema/
├── README.md                          questo file
├── docs/
│   ├── 01_DOCUMENTAZIONE_TECNICA      come funziona il sistema (.md e .docx)
│   ├── 02_TABELLE_DI_OUTPUT           come si crea ogni tabella (.md e .docx)
│   └── HANDOVER                       registro tecnico dettagliato dello sviluppo (.md e .docx)
└── codice/
    ├── 1_Estrattore_Python/           estrattore generico di dati ISTAT (interfaccia grafica) + report Import/Export in Python
    ├── 2_Versione_Web_GitHub/         sito COMMERCIO ESTERO (dati ISTAT Coeweb in diretta)
    ├── 6_Web_Imprese_Stockview/       sito IMPRESE (file Stockview caricati a mano)
    ├── 7_Web_Credito_BancaItalia/     sito CREDITO (dati Banca d'Italia automatici)
    ├── 8_Web_Lavoro/                  sito LAVORO (dati ISTAT e INPS automatici)
    ├── 9_Web_Popolazione/             sito POPOLAZIONE (dati ISTAT automatici)
    ├── 10_Web_ContiEconomici/         sito CONTI ECONOMICI – valore aggiunto (Tagliacarne + ISTAT automatici)
    ├── 11_Web_Trasporti/              sito TRASPORTI – strade (ACI + ISTAT automatici)
    └── 12_Web_Sito_Unico/             generatore del SITO UNICO che riunisce tutti i siti
```

I numeri delle cartelle sono quelli originali: le cartelle 3, 4 e 5 erano versioni precedenti o strumenti secondari e non fanno parte del repository.

### File di ogni sito

| File | Presente in | Ruolo |
|---|---|---|
| `index.html` | tutti i siti | La pagina. Dentro c'è il **motore** (`<script id="motore">`: lettura dei dati, controlli, calcolo delle tabelle, scrittura degli Excel e dello ZIP) e l'**interfaccia**. |
| `LEGGIMI.txt` | tutti i siti | Istruzioni per l'ufficio. |
| `aggiorna_dati.py` | 7, 8, 9, 10, 11 | **Estrazione ed elaborazione**: scarica le tavole dalle fonti, le filtra, le controlla e scrive i CSV in `dati/`. Usa solo la libreria standard di Python. Nel sito Lavoro c'è anche `aggiorna_cig.py` per i dati INPS. |
| `segnala_problemi.py` | 7, 8, 9, 10, 11 | Avviso per e-mail (tramite una issue di GitHub) solo quando l'aggiornamento non riesce. |
| `.github/workflows/*.yml` | 7, 8, 9, 10, 11 | Quando e come GitHub Actions lancia gli script. |
| `dati/*.csv`, `dati/aggiornamento.json` | 7, 8, 9, 10, 11 | I dati che la pagina legge, con la data e lo stato dell'ultimo aggiornamento. |

Il sito unico (`12_Web_Sito_Unico/`) contiene:
- `costruisci_sito.py`, che prende identici motore e interfaccia delle sette pagine;
- `sorgenti/` (grafica, logo, font);
- `sito/`, il risultato pubblicato.

## 3. Dove girano i siti

Ogni sito è pubblicato con **GitHub Pages** dal **proprio repository** sull'account dell'ufficio `StatisticaVA`. Lì girano anche gli aggiornamenti automatici.

| Sito | Indirizzo | Repository | Cartella qui |
|---|---|---|---|
| **Sito unico** | https://statisticava.github.io/report-osserva/ | `StatisticaVA/report-osserva` | `codice/12_Web_Sito_Unico/sito/` |
| Commercio estero | https://statisticava.github.io/report-import-export/ | `StatisticaVA/report-import-export` | `codice/2_Versione_Web_GitHub/` |
| Imprese | https://statisticava.github.io/report-imprese-stockview/ | `StatisticaVA/report-imprese-stockview` | `codice/6_Web_Imprese_Stockview/` |
| Credito | https://statisticava.github.io/report-credito/ | `StatisticaVA/report-credito` | `codice/7_Web_Credito_BancaItalia/` |
| Lavoro | https://statisticava.github.io/report-lavoro/ | `StatisticaVA/report-lavoro` | `codice/8_Web_Lavoro/` |
| Popolazione | https://statisticava.github.io/report-popolazione/ | `StatisticaVA/report-popolazione` | `codice/9_Web_Popolazione/` |
| Conti economici | https://statisticava.github.io/report-conti-economici/ | `StatisticaVA/report-conti-economici` | `codice/10_Web_ContiEconomici/` |
| Trasporti | https://statisticava.github.io/report-trasporti/ | `StatisticaVA/report-trasporti` | `codice/11_Web_Trasporti/` |

Al 12/10/2026 ogni cartella di `codice/` è **identica** al repository del sito corrispondente.

Da qui in poi i bot aggiornano i dati **nei repository dei siti**: le cartelle `dati/` di questo repository sono una fotografia a quella data. I workflow in `codice/*/.github/workflows/` qui **non partono**, perché GitHub esegue solo quelli alla radice del repository. È voluto.

## 4. Provare in locale

Servono solo un browser e, per gli script, Python 3.

```bash
cd codice
python3 -m http.server 8000
```

Poi aprire nel browser, ad esempio:
- http://localhost:8000/7_Web_Credito_BancaItalia/
- http://localhost:8000/2_Versione_Web_GitHub/

Scegliere il periodo e premere «Genera». Le pagine funzionano anche aperte con doppio clic su `index.html`: in quel caso leggono i dati automatici dal sito online.

Per lanciare a mano uno script di aggiornamento (scarica davvero dalle fonti):

```bash
cd codice/9_Web_Popolazione
python3 aggiorna_dati.py
```

L'estrattore Python (`codice/1_Estrattore_Python/`) richiede `requests pandas openpyxl lxml`; si avvia con `Avvia Estrattore SDMX (Mac).command` o `(Windows).bat`.

## 5. Documentazione

| Documento | Contenuto |
|---|---|
| `docs/01_DOCUMENTAZIONE_TECNICA` | Architettura, fonti e API, aggiornamenti automatici e calendario, account, cosa fa l'ufficio e quando, manutenzione (avvisi, modifiche, pubblicazione), rischi aperti. |
| `docs/02_TABELLE_DI_OUTPUT` | Per ognuna delle circa 110 tabelle: dati di input (fonte, tavola, filtri), trasformazioni e calcoli, forma del file Excel, differenze volute rispetto alle vecchie tabelle di Osserva. |
| `docs/HANDOVER` | Registro dettagliato dello sviluppo, in ordine cronologico: decisioni prese con l'ufficio, verifiche fatte, pubblicazioni. Cita anche test e file di prova che non sono in questo repository: li conserva l'Ufficio Statistica. |

## 6. Cosa non è in questo repository

Le cose seguenti restano all'Ufficio Statistica:
- i test automatici e i file di prova usati durante lo sviluppo;
- la serie storica delle imprese (`Storico_imprese_Varese.xlsx`), che è un file di lavoro dell'ufficio;
- i fogli di lavoro e le tabelle di Osserva usati per le verifiche;
- le versioni precedenti dei programmi.
