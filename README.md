# Sistema dei report per Osserva – Camera di Commercio di Varese

Codice dei siti, script di estrazione ed elaborazione dei dati e documentazione tecnica del sistema che prepara le tabelle statistiche da caricare su **Osserva**:
- commercio estero;
- imprese;
- credito;
- lavoro;
- popolazione;
- valore aggiunto;
- trasporti.

Stato al **12 ottobre 2026**.

## Documentazione

1. **`docs/01_DOCUMENTAZIONE_TECNICA`**: come funziona il sistema: architettura, fonti e API, aggiornamenti automatici, account, manutenzione, rischi.
2. **`docs/02_TABELLE_DI_OUTPUT`**: come si crea ogni tabella: dati di input, trasformazioni e forma del file.

I documenti sono sia in Markdown (`.md`) sia in Word (`.docx`).

## Codice

| Cartella | Contenuto |
|---|---|
| `codice/1_Estrattore_Python/` | Estrattore generico di dati ISTAT con interfaccia grafica e report Import/Export in Python |
| `codice/2_Versione_Web_GitHub/` | Sito Commercio estero |
| `codice/6_Web_Imprese_Stockview/` | Sito Imprese |
| `codice/7_Web_Credito_BancaItalia/` | Sito Credito, con scarico automatico dei dati Banca d'Italia |
| `codice/8_Web_Lavoro/` | Sito Lavoro, con scarico automatico dei dati ISTAT e INPS |
| `codice/9_Web_Popolazione/` | Sito Popolazione, con scarico automatico dei dati ISTAT |
| `codice/10_Web_ContiEconomici/` | Sito Conti economici, con scarico automatico dei dati Tagliacarne e ISTAT |
| `codice/11_Web_Trasporti/` | Sito Trasporti, con scarico automatico dei dati ACI e ISTAT |
| `codice/12_Web_Sito_Unico/` | Generatore del sito unico che riunisce tutti i siti |

## Siti pubblicati (account GitHub dell'ufficio `StatisticaVA`)

| Sito | Indirizzo | Repository |
|---|---|---|
| **Sito unico (tutti i report)** | https://statisticava.github.io/report-osserva/ | `StatisticaVA/report-osserva` |
| Commercio estero | https://statisticava.github.io/report-import-export/ | `StatisticaVA/report-import-export` |
| Imprese | https://statisticava.github.io/report-imprese-stockview/ | `StatisticaVA/report-imprese-stockview` |
| Credito | https://statisticava.github.io/report-credito/ | `StatisticaVA/report-credito` |
| Lavoro | https://statisticava.github.io/report-lavoro/ | `StatisticaVA/report-lavoro` |
| Popolazione | https://statisticava.github.io/report-popolazione/ | `StatisticaVA/report-popolazione` |
| Conti economici | https://statisticava.github.io/report-conti-economici/ | `StatisticaVA/report-conti-economici` |
| Trasporti | https://statisticava.github.io/report-trasporti/ | `StatisticaVA/report-trasporti` |

I **dati aggiornati** stanno nei repository dei siti: i bot di GitHub Actions li aggiornano da soli. Questo repository è una **fotografia** al 12/10/2026, e i workflow dentro `codice/*/.github/` qui non partono.
