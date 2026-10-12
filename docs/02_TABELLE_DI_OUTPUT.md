# Specifica delle tabelle di output

**Camera di Commercio di Varese – Ufficio Statistica** · stato al **12 ottobre 2026**

Questo documento descrive **ogni tabella** prodotta dal sistema e caricata su Osserva:
- da quali **dati di input** parte (fonte, tavola, filtri);
- quali **trasformazioni** fa;
- che **forma** ha il file Excel (foglio, righe, colonne).

Il funzionamento generale è in `01_DOCUMENTAZIONE_TECNICA.md`.

## Convenzioni

- **N** = anno scelto nella pagina; **T** = trimestre scelto (1–4).
- **Varese / Lombardia / Italia**: i tre territori di quasi tutte le tabelle. Le «12 province» sono quelle lombarde.
- **ROUND(x; d)** = arrotondamento come ARROTONDA di Excel (metà lontano da zero).
- **var(a, b)** = `ROUND(a / b × 100 − 100; 2)`: variazione % di *a* rispetto a *b*. Se *b* è 0 o manca, la cella resta vuota, salvo diversa indicazione.
- **peso(a, tot)** = `ROUND(a / tot × 100; 2)`.
- **cum(N, T)** = somma da gennaio (o dal I trimestre) fino alla fine del trimestre T dell'anno N. Si usa solo per i flussi.
- Tutti i file sono `.xlsx` con i numeri salvati come numeri. Ogni report è una cartella `Report_<tema>_<periodo>`, da scaricare anche come ZIP.
- «**Come Osserva**» = stesso nome del file, stesso foglio, stesse intestazioni ed etichette della tabella già pubblicata. Le **differenze volute** sono indicate tabella per tabella.

## Indice

- **A. Commercio estero**: 10 tabelle
- **B. Imprese**: B1 Registrate e attive (10) · B2 Iscrizioni e cessazioni (8 + 1 di controllo) · B3 Procedure concorsuali e scioglimenti (11)
- **C. Credito**: C1 Depositi (4) · C2 Impieghi (4) · C3 Sofferenze (4) · C4 Sportelli (2)
- **D. Lavoro**: D1 Disoccupazione (6) · D2 Occupazione (8) · D3 Attività (6) · D4 Inattività (6) · D5 Cassa integrazione (11)
- **E. Popolazione**: 6 tabelle
- **F. Conti economici – Valore aggiunto**: 6 tabelle
- **G. Trasporti – Strade**: 6 tabelle

---

# A. Commercio estero (Import/Export)

Sito `codice/2_Versione_Web_GitHub/index.html`, identico al programma Python `codice/1_Estrattore_Python/report_import_export.py`. Cartella del report: `Report_import_export_{N}_T{T}`.

## A.0 Dati di input

Fonte: **ISTAT Coeweb**, chiamato dalla pagina nel momento in cui si preme «Genera». Valori in **euro**, dati grezzi (`ADJUSTMENT = N`).

| # | Dataset | Filtri | Anni | Serve a |
|---|---|---|---|---|
| 1 | `IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0` (annuale e trimestrale, dal 2020) | FREQ A+Q; Italia `ITTOT`, Lombardia `ITC4`, 12 province; `EV` (export) e `IV` (import); CPA `ALL`; partner `WORLD` | N−6 … N | Sintesi, Territori, Tempo trimestrale |
| 2 | `IT1,DF_CPA_AT2007_COE_OPT_A_REG_ALL,1.0` (solo annuale, dal 1991) | FREQ A; Varese `ITC41`; EV, IV; ALL; WORLD | N−14 … N | Tempo annuale (anni prima del 2020). **Si chiede solo se T = 4** e se esiste già il dato annuale |
| 3 | come 1 | FREQ A+Q; Varese; EV, IV; CPA `ALL`, `C` (manifatturiero) e sottosezioni `CA`…`CM`; WORLD | N−1, N | Settori |
| 4 | come 1 | FREQ A+Q; Varese; EV, IV; ALL; **tutti i partner** (filtro omesso: paesi a 2 lettere e continenti) | N−1, N | Paesi, grafico dei paesi |

**Regola del cumulato**: cum(N, T) = somma dei trimestri 1…T. Con T = 4 si usa il **dato annuale ISTAT**, se c'è. La variazione tendenziale confronta sempre cumulato con cumulato (N contro N−1). La variazione usa `|vecchio|` al denominatore, così ha senso anche per i saldi negativi.

Se ISTAT non ha ancora il trimestre scelto per Varese, nessun file viene prodotto e la pagina mostra: «ISTAT non ha ancora pubblicato i dati del … (ultimo disponibile: …)».

## A.1 `Import_export_Sintesi.xlsx` (foglio **Foglio2**)
- **Colonne**: Ordine | Territorio | Bilancia commerciale | Stesso periodo precedente | Periodo recente | Variazione %
- **Righe (9)**: Varese, Lombardia, Italia, ciascuno con Export, Import, Saldo.
- **Calcoli**:
  - Stesso periodo precedente = cum(N−1, T); Periodo recente = cum(N, T);
  - Saldo = Export − Import;
  - Variazione = var(recente, precedente), vuota per il Saldo.
- **Formati**: valori `#,##0`, variazione `0.00`.

## A.2 `Import_export_Territori.xlsx`
- **Colonne**: Ordine | Territori | Export | T.var % tend export | Import | T.var % tend import | Saldo | Peso % export su Lombardia | Peso % import su Lombardia
- **Righe (13)**: Varese, Como, Sondrio, Milano, Bergamo, Brescia, Pavia, Cremona, Mantova, Lecco, Lodi, Monza e della Brianza, Lombardia.
- **Calcoli**:
  - Export e Import = cum(N, T);
  - T.var = var(cum N, cum N−1);
  - Saldo = E − I;
  - Peso = valore / Lombardia × 100 (la Lombardia vale 100).

## A.3 `Import_export_Tempo_Trimestrale.xlsx`
- **Colonne**: Anno | Trimestre | Export | T.var% cong. export | T.var% tend. export | Import | (idem) | Saldo | T.var% cong. saldo | T.var% tend. saldo
- **Righe**: i **trimestri singoli, non cumulati**, di Varese dal I trim N−5 al trimestre scelto (21 righe con T = 1, 24 con T = 4). Etichette `I trim '21`…
- **Calcoli**:
  - congiunturale = sul trimestre precedente (per la prima riga si usa il IV trim N−6);
  - tendenziale = sullo stesso trimestre dell'anno prima.

## A.4 `Import_export_Tempo_Annuale.xlsx` (solo con T = 4 e dato annuale pubblicato)
- **Colonne**: Anno | Export | T.var % su export anno precedente | Import | T.var % su import anno precedente | Saldo | T.var% sull'anno precedente
- **Righe (13)**: N−12 … N, dato annuale ISTAT di Varese. Dal 2020 si usa il dataset 1, per gli anni prima il dataset 2.

## A.5 `Import_export_Settori_Export.xlsx` e `Import_export_Settori_Import.xlsx`
- **Colonne**: Ordine | Dettaglio manifatturiero | Valori in euro | % export sul totale manifatturiero (o «% import…») | T.var% tend.
- **Righe (15)**:
  - 1–13: sottosezioni CA…CM, con le etichette dei modelli dell'ufficio (diverse da quelle ISTAT);
  - 14: Totale manifatturiero (`C`);
  - 15: «% manifatturiero sul totale dell'export» (o «…dell'import»).
- **Calcoli**:
  - righe 1–14: valore = cum(N, T) di Varese per la voce; % = valore / C × 100; T.var = var(cum N, cum N−1);
  - riga 15: valore = totale di tutte le merci (`ALL`); % = C / ALL × 100; T.var = variazione del totale.

## A.6 `Import_export_Paesi_Export.xlsx` e `Import_export_Paesi_Import.xlsx`
- **Colonne**: Ordine | Aree geografiche | Export (o Import) | Composizione % | T.var% tend.
- **Righe (27)**:
  - 1–5: i continenti (Europa, Asia, America, Africa, Oceania ed altri territori), **ordinati per valore decrescente**;
  - 6: MONDO;
  - 7: «Primi 20 paesi partner» (riga titolo);
  - 8–27: i primi 20 paesi per valore cumulato decrescente. Si considerano solo i codici a 2 lettere; sono esclusi gli aggregati e i codici che non sono paesi (`QP QZ QW QS QY QV QR QU QX QQ QO XC XL`).
- **Calcoli**: Composizione = valore / MONDO × 100; T.var = var(cum N, cum N−1).

## A.7 `Export_paesi_xgrafico.xlsx` e `Import_paesi_xgrafico.xlsx`
- Le stesse colonne di A.6, **solo le righe 1–5** (continenti).

Differenze volute rispetto ai vecchi modelli: numeri come numeri (i modelli li avevano come testo); etichette senza spazi finali; la tabella Territori ha la colonna Saldo. La tabella degli indici non si produce più (scelta dell'ufficio).

---

# B. Imprese (InfoCamere – Stockview)

Sito `codice/6_Web_Imprese_Stockview/index.html`. Una pagina con tre sezioni e una sola **serie storica** (`Storico_imprese_Varese.xlsx`): la serie è sia input sia output della pagina. Il primo report possibile è il **II trim 2026**, perché l'ATECO 2025 è in vigore dal II trim 2025 e serve il confronto con l'anno prima.

## B.0 Dati di input

| File (nome tipico) | Contenuto | Colonne usate |
|---|---|---|
| `TAAAAVAS.csv` (es. `22026VAS.csv`) — **dati grezzi** «sedi d'impresa» di Varese, testo con colonne separate da tab o a larghezza fissa | Una riga per combinazione di sezione, divisione, forma giuridica e stato; i valori si sommano | `DIV` (sezione ATECO), `ATDIV` (divisione, es. `C 10`), `CNG` (forma giuridica: BC, CP, DI, EF), `REGIST`, `ATTIVE`, `ISCRIZ`, `CESSAZ`, `CESNUF` (cessazioni non d'ufficio), `AAISC`/`TRIM` (per riconoscere il periodo) |
| `AAAAMM_m.csv` | Varese a fine mese | Registrate, Attive |
| `AAAAT_sa.csv` | Province lombarde nel trimestre | Registrate, Attive, Iscrizioni, Cessazioni, Cessazioni non d'ufficio (righe per provincia + Grand Totale) |
| `AAAAT_sa (1).csv` | Italia nel trimestre | come sopra (una riga) |
| `AAAAMM_me.csv` | Procedure di Varese aperte nel mese | Classe Evento, Settore, Classe di Natura Giuridica, Aperture Eventi Procedure |
| `AAAAMM_me (1).csv` | Procedure delle province lombarde nel mese | Provincia, Classe Evento, Aperture |
| `AAAAT_sa.csv` (per status d'impresa) | Stock di Varese a fine trimestre | Registrate, per «con Procedure concorsuali» e «in Scioglimento o Liquidazione» |
| `Storico_imprese_Varese.xlsx` | Serie storica, input e output | Fogli: Mesi, Anni_fino_2008, Settori_ATECO2025, Settori_ATECO2007, Forma_giuridica, Territori, Flussi_settori, Procedure_trimestri, Procedure_anni, Procedure_mesi, Procedure_dettaglio_Varese (+ un LEGGIMI e due fogli calcolati di sola lettura) |

Il **tipo** di file si riconosce dal contenuto, il **periodo** dal contenuto o dal nome. Sono accettati anche nomi diversi, file in Excel e separatore `;`.

**Dai dati grezzi alle voci** (funzioni `aggregaGrezzo`, `gruppiDaGrezzo` e `flussiDaGrezzo`):
- Registrate e attive di Varese = somma di `REGIST` e di `ATTIVE`. Vanno nella serie storica come dato del mese di fine trimestre.
- **Settori** (somma delle **attive** per sezione `DIV`):
  - Agricoltura = A; Manifatturiero = C; Costruzioni = F; Commercio = G;
  - Servizi = H…T in ATECO 2025 (H…S in ATECO 2007);
  - **Altro** = attive totali − settori precedenti, cioè B, D, E, X…
- La **classificazione ATECO** (2007 o 2025) si riconosce dai codici di divisione e le due serie si tengono separate. Esempi: `M68`/`K62`/`T95` indicano l'ATECO 2025, `L68`/`J62`/`S95` l'ATECO 2007.
- **Manifatturiero** (somma delle attive per divisione `C xx`), 14 gruppi:

  | Gruppo | Divisioni |
  |---|---|
  | Alimentari, bevande, tabacco | 10–12 |
  | Tessile abbigliamento | 13–14 |
  | Cuoio, pelle | 15 |
  | Legno | 16 |
  | Carta, editoria | 17–18 |
  | Coke e prodotti derivanti dalla raffinazione | 19 |
  | Chimica farmaceutica | 20–21 |
  | Gomma e materie plastiche | 22 |
  | Minerali non metalliferi | 23 |
  | Prodotti in metallo | 24–25 |
  | Computer e apparecchi elettrici ed elettronici | 26–27 |
  | Macchinari ed apparecchiature | 28, 33 |
  | Mezzi di trasporto | 29–30 |
  | Altre industrie manifatturiere | 31–32 + divisioni non riconosciute |

- **Servizi**: una riga per sezione, con le etichette del modello. In ATECO 2025:

  | Sezione | Etichetta |
  |---|---|
  | H | Trasporto e magazzinaggio |
  | I | Alloggio e di ristorazione |
  | J | Attività editoriali trasmissioni radiofoniche |
  | K | Telecomunicazioni e consulenza informatica |
  | L | Attività finanziarie e assicurative |
  | M | Attività immobiliari |
  | N | Attività professionali, scientifiche e tecniche |
  | O | Attività amministrative e di servizi di supporto |
  | P | Amministrazione pubblica e difesa |
  | Q | Istruzione e formazione |
  | R | Sanità |
  | S | Attività artistiche, sportive e ludiche |
  | T | Altre attività di servizi |

- **Forma giuridica** (da `CNG`): BC = Società di capitale; CP = Società di persone; DI = Imprese individuali; EF = Altre forme (più le forme non riconosciute).
- **Flussi**: iscrizioni (`ISCRIZ`), cessazioni totali (`CESSAZ`) e **cessazioni non d'ufficio** (`CESNUF`), per le stesse voci. Il manifatturiero dei flussi ha **12 gruppi diversi** (vedi B2).
- **Territori**: Varese viene sempre dai dati grezzi o dalla serie storica; nel file delle province la riga di Varese serve solo come controllo. **Lombardia = somma delle 12 province**, confrontata con il Grand Totale del file.

## B1. Registrate e attive (cartella `Report_imprese_registrate_attive_{N}_T{T}`)

Sono dati di **stock** a fine periodo: non si sommano.

### B1.1 `REGISTRATE_ATTIVE_tempo_trimestre.xlsx` (Foglio1)
- **Colonne**: Ordinamento | ANNO | Trimestre | Registrate | Attive | T.var.% cong. attive | T.var% tend. attive
- **Righe**: dal I trim N−5 al trimestre scelto (`I trim '21`…).
- **Calcoli**: registrate e attive di Varese a fine trimestre (serie storica, foglio Mesi); cong. = var(attive, trimestre precedente); tend. = var(attive, stesso trimestre N−1).

### B1.2 `REGISTRATE_ATTIVE_tempo_mese.xlsx` (Foglio2)
- **Colonne**: ordinamento | anno | mese | Registrate | Attive | T.var% cong attive | T.var% tend attive
- **Righe (37)**: dal mese di fine trimestre di N−3 al mese di fine trimestre di N (etichette `giugno '23`…).
- **Calcoli**: come sopra, sui mesi (congiunturale = sul mese precedente).

### B1.3 `REGISTRATE_ATTIVE_tempo_anno.xlsx` (Foglio1, **solo con T = 4**)
- **Colonne**: anno | Registrate | Attive | T.var% tendenziale registrate | T.var% tendenziale attive
- **Righe**: dal 2005 a N. Il dato è quello di dicembre; per il 2005–2008 si usa il foglio Anni_fino_2008, che contiene le variazioni del 2005 fisse.

### B1.4 `REGISTRATE_ATTIVE_settore_totale.xlsx` (Foglio2)
- **Colonne**: ordinamento | Settore | periodo recente | periodo passato 1 | periodo passato 2 | T.var% tendenz. | Peso %
- **Righe (7)**: Agricoltura, pesca, silvicoltura; Manifatturiero; Costruzioni; Commercio; Servizi; Altro; TOTALE.
- **Calcoli**:
  - periodo recente = attive al trimestre T di N;
  - periodo passato 1 = trimestre precedente;
  - periodo passato 2 = stesso trimestre di N−1;
  - T.var = var(recente, passato 2);
  - Peso = peso(voce, TOTALE).
- La serie ATECO usata è quella del file dei dati grezzi.

### B1.5 `REGISTRATE_ATTIVE_settore_manifatturiero.xlsx` (Foglio1)
- **Colonne**: Ordine | Settore | periodo passato | periodo recente | T.var.% tend. | Peso % su tot. manifatt.
- **Righe (15)**: i 14 gruppi del manifatturiero + TOTALE.
- **Calcoli**: passato = attive al trimestre T di N−1; recente = al trimestre T di N; T.var = var(recente, passato); peso sul totale del manifatturiero.

### B1.6 `REGISTRATE_ATTIVE_settore_servizi.xlsx` (Foglio1)
- **Colonne**: Ordine | Settore | periodo passato | periodo recente | T.var.% tend. | Peso % su tot. servizi
- **Righe (14)**: le 13 sezioni dei servizi + Totale. Calcoli come B1.5.

### B1.7 `REGISTRATE_ATTIVE_tipo.xlsx` (Foglio1)
- **Colonne**: ORDINE | Forma giuridica | periodo passato | periodo recente | T.var.% tend.
- **Righe (5)**: le 4 forme giuridiche + TOTALE (attive di Varese).

### B1.8 `REGISTRATE_ATTIVE_sintesi_xgrafico.xlsx` (Foglio1)
- **Colonne**: Imprese | periodo passato | periodo recente
- **Righe**: Registrate e Attive di Varese, al trimestre T di N−1 e di N.

### B1.9 `REGISTRATE_ATTIVE_sintesi.xlsx` (Foglio1)
- **Colonne**: ordinamento | Territorio | Imprese | periodo passato | periodo recente | T.var% tend.
- **Righe (6)**: ITALIA, LOMBARDIA, VARESE × Registrate, Attive.
- **Input**: Italia dal file `AAAAT_sa (1).csv`; Lombardia = somma delle province; Varese dai dati grezzi o dalla serie storica.

### B1.10 `REGISTRATE_ATTIVE_territori.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | trimestre passato | trimestre recente | T.var% tend | Peso %
- **Righe (14)**: Varese, Bergamo, Brescia, Como, Cremona, Lecco, Lodi, Mantova, Milano, Monza e Brianza, Pavia, Sondrio, LOMBARDIA, ITALIA\*. La numerazione è 1–11, 13, 14, 15: **manca il 12**, come nel modello.
- **Calcoli**: imprese **attive**; peso = peso(provincia, Lombardia). Nella riga **ITALIA\*** il peso è quello della **Lombardia sull'Italia**.

Nota: una tabella con un dato di confronto mancante viene creata con le celle vuote e segnalata come «incompleta». Se manca un dato del trimestre scelto, la tabella non viene creata.

## B2. Iscrizioni e cessazioni (cartella `Report_iscritte_cessate_{N}_T{T}`)

Sono **flussi**, cumulati da inizio anno: il II trimestre vale I + II, confrontato con I + II dell'anno prima.
- Le **«Cessate» sono le cessazioni NON d'ufficio** (`CESNUF`). Prima del 2009 si usano le cessazioni totali: per questo l'etichetta dell'anno è «2009(\*)».
- Saldo = iscritte − cessate.
- I tassi sono `ROUND(valore / registrate a fine periodo precedente × 100; 2)`.
- Tutti i trimestri dell'anno in corso sono **obbligatori**.

### B2.1 `Iscritte_cessate_trimestre.xlsx` (Foglio1)
- **Colonne**: Anno | Trimestre | Iscritte | Cessate | Saldo | Tasso di sviluppo
- **Righe**: i **trimestri singoli** dal I trim N−5 (`I trim 2021`…).
- **Calcoli**: Tasso di sviluppo = ROUND(saldo / registrate a fine del trimestre precedente × 100; 2).

### B2.2 `Iscritte_cessate_anno.xlsx` (Foglio1, **solo con T = 4**)
- **Colonne**: Anno | Iscritte | Cessate | Saldo | Tasso di sviluppo
- **Righe**: dal 2005 a N (somma dei 4 trimestri; etichetta «2009(\*)»).
- **Calcoli**: tasso = saldo / registrate a dicembre dell'anno prima × 100.

### B2.3 `Iscritte_cessate_sintesi.xlsx` (Foglio1)
- **Colonne**: Ordine | Imprese e tassi | Periodo passato | Periodo recente
- **Righe (6)**: Iscritte, Cessate, Saldo, Tasso natalità, Tasso mortalità, Tasso sviluppo.
- **Calcoli**:
  - valori = cum(N−1, T) e cum(N, T);
  - tassi = valore / registrate a **dicembre dell'anno prima del periodo** × 100 (per il periodo passato: dicembre N−2). Formato `0.00` sulle righe dei tassi.

### B2.4 `Iscritte_cessate_settori_totale.xlsx` (Foglio1)
- **Colonne**: Ordine | Settore | Iscritte | Cessate | Saldo
- **Righe (7)**: i 6 settori di B1.4 + Totale.
- **Calcoli**: cum(N, T) per voce.

### B2.5 `Iscritte_cessate_settore_manifatturiero.xlsx` (Foglio1)
- **Colonne**: come B2.4.
- **Righe (13)**: 12 gruppi **specifici dei flussi** + TOTALE MANIFATTURIERO.

  | Gruppo | Divisioni |
  |---|---|
  | Alimentari, bevande, tabacco | 10–12 |
  | Tessile abbigliamento, pelle | 13–15 |
  | Legno e mobili | 16, 31 |
  | Carta, editoria | 17–18 |
  | Chimica farmaceutica | 20–21 |
  | Gomma e materie plastiche | 22 |
  | Minerali e metallurgia | 23–24 |
  | Meccanico e macchinari | 25, 28 |
  | Computer e app. elettrici ed elettronici | 26–27 |
  | Mezzi di trasporto | 29–30 |
  | Riparazione e manutenzione | 33 |
  | Altre industrie manifatturiere | 19, 32 + divisioni non riconosciute |

### B2.6 `Iscritte_cessate_settore_servizi.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Settori | Iscritte | Cessate | Saldo
- **Righe (14)**: sezioni H…T con le etichette del modello (Trasporti, Alberghi e ristorazione, Attività editoriali e contenuti multimediali, … Altre attivita' di servizi) + TOTALE SERVIZI.

### B2.7 `Iscritte_cessate_tipo.xlsx` (Foglio1)
- **Colonne**: Ordine | Forma giuridica | Iscritte | Cessate | Saldo
- **Righe (5)**: le 4 forme giuridiche + TOTALE.

### B2.8 `Iscritte_cessate_territori.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | Iscritte | Cessate | Saldo
- **Righe (14)**: le 12 province nell'ordine di B1.10 («Monza-Brianza»), LOMBARDIA (somma delle province), ITALIA. Numerazione 1–11, 13, 14, 15.
- **Input**: Varese dai dati grezzi; province da `AAAAT_sa.csv`; Italia da `AAAAT_sa (1).csv`. Servono le colonne Iscrizioni e Cessazioni non d'ufficio.

### B2.9 `Monitoraggio_cessazioni_d_ufficio_NON_PER_OSSERVA.xlsx` — **non va caricato su Osserva**
File di controllo voluto dall'ufficio, in una cartella ZIP a parte (`NON_DA_CARICARE_…`).
- **Fogli**:
  - LEGGIMI;
  - Varese_trimestri: trimestri singoli (al massimo 5 anni) più i cumulati di N−1 e N;
  - Territori e Settori_Varese: trimestre e cumulato.
- **Calcoli**: cessazioni d'ufficio = cessazioni totali − non d'ufficio; % d'ufficio = d'ufficio / totali × 100; saldi con le cessazioni totali e con quelle non d'ufficio.
- I dati mancanti lasciano celle vuote e non bloccano nulla.

## B3. Procedure concorsuali e scioglimenti (cartella `Report_procedure_scioglimenti_{N}_T{T}`)

- **Procedure concorsuali** = tutte le Classi Evento tranne «SCIOGLIMENTO E LIQUIDAZIONE»: crisi d'impresa, procedimenti crisi d'impresa, fallimento, concordato, liquidazione giudiziale, altre procedure concorsuali. **Scioglimenti** = «SCIOGLIMENTO E LIQUIDAZIONE».
- Le **aperture** sono flussi, **cumulati da gennaio**. Gli **stock** («con Procedure concorsuali», «in Scioglimento o Liquidazione») sono a fine trimestre.
- **Caso speciale del II trim 2022**: 1.830 scioglimenti, di cui 1.698 straordinari. Nelle **variazioni** il II trim 2022 vale **132** e l'anno 2022 vale **848**, come nelle tabelle pubblicate (colonne «… per i confronti» della serie storica).

### B3.1 `Procedure_e_scioglim_trimestre.xlsx` (Foglio1)
- **Colonne**: Anno | Trimestre | N° procedure concorsuali | T.var% tend. pr.conc. | N° procedure scioglimento liquidazione | T.var.% tend. pr. sciogl.
- **Righe**: i trimestri singoli dal I trim N−5 (`I trim '21`…).
- **Calcoli**: aperture del trimestre = somma dei 3 mesi; variazione sullo stesso trimestre di N−1, con il valore «per i confronti».

### B3.2 `Procedure_e_scioglim_anno.xlsx` (Foglio1, **solo con T = 4**)
- **Colonne**: Anno | n° procedure concorsuali | T.var% tend pr.conc. | N°procedure scioglimento liquidazione | T.var%tend pr.sciogl.
- **Righe**: dal 2007 a N. L'etichetta del 2022 è «2022\*». Prima del 2020 si usano i valori annuali salvati.

### B3.3 `Procedure_e_scioglim_sintesi.xlsx` (Foglio1)
- **Colonne**: ordinamento | Variabile | periodo passato | periodo recente | T.var%
- **Righe (4)**: Aperture procedure concorsuali; Aperture scioglimento e liquidazione (cum N−1 e cum N); Stock procedure concorsuali; Stock scioglimento e liquidazione (fine trimestre T di N−1 e di N, dal file dello stock).

### B3.4 `Procedure_settori.xlsx` e `Scioglimento_settori.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Settore | Procedure concorsuali (o «Scioglimento liquidazione»)
- **Righe (22)**: le sezioni A…T + X «Imprese non classificate» (le sezioni sconosciute finiscono qui) + TOTALE. Le etichette sono quelle dei due modelli, leggermente diverse tra loro.
- **Calcoli**: aperture di Varese cumulate da gennaio, contate per sezione ATECO (prima lettera dell'etichetta «Settore» del file mensile). **Sempre in ATECO 2025.**

### B3.5 `Procedure_settori_x_grafico.xlsx` e `Scioglimento_settori_x_grafico.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Settore | Procedure (o «Scioglimento liquidazione») | Peso % su tot.
- **Righe (6)**: Manifatturiero (C), Costruzioni (F), Commercio (G), Servizi (H–T), Altro (B, D, E, X…), Agricoltura (A).

### B3.6 `Procedure_tipo.xlsx` e `Scioglimento_tipo.xlsx` (Foglio1)
- **Colonne**: ordine (o Ordine) | Procedure concorsuali (per forma giuridica) | Valore assoluto | Percentuale %
- **Righe (5)**: le 4 forme giuridiche (dalla Classe di Natura Giuridica) + TOTALE (= 100). Ordine 1–5 (nel modello degli scioglimenti era 1, 2, 3, 6, 7).

### B3.7 `Procedure_territori.xlsx` e `Scioglimento_territori.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Territorio | Periodo di riferimento | Peso % sul totale Lombardia
- **Righe (13)**: Varese, Como, Sondrio, Milano, Monza-Brianza, Bergamo, Brescia, Pavia, Cremona, Mantova, Lecco, Lodi, LOMBARDIA (= somma, peso 100).
- **Calcoli**: aperture cumulate da gennaio dai file mensili delle province. Varese viene dal proprio file.

Differenze volute rispetto ai vecchi modelli:
- etichette `IV trim '25` invece di `IV trim 2025`;
- intestazione «Ordinamento» al posto di una cella vuota;
- tabelle sempre cumulate.

---

# C. Credito (Banca d'Italia)

Sito `codice/7_Web_Credito_BancaItalia/index.html`. Dati automatici in `dati/` (aggiornati da `aggiorna_dati.py`).

## C.0 Dati di input

CSV della Banca d'Italia (servizio A2A), filtrati su **Varese `ITC41`, Lombardia `ITC4`, Italia `IT`**. Attenzione: questi codici territoriali sono diversi da quelli ISTAT per Milano e Monza.

| File in `dati/` | Tavola | Serie usate | Unità / frequenza |
|---|---|---|---|
| `TDB10290.csv` | Depositi (esclusi PCT) per provincia e settore | `FENEC=1041810`, ente `1070001` (Banche e Cassa depositi e prestiti), settore `SBI59` (totale clientela al netto delle IFM), `600` (famiglie consumatrici), `S11BI32` (imprese private al netto delle captive); territorio in `LOC_CTP` | Migliaia di euro, mensile (fine mese) |
| `TDB10295.csv` | Prestiti (esclusi PCT) | `FENEC=1077778`, stesso ente e settori dei depositi | Migliaia di euro, mensile |
| `TRI30401.csv` | Sofferenze per provincia della clientela | ente `1100010` (Banche), settore `SBI42`, classe `CLASSE_NUMAFF=1101` (totale), `FENEC 55100033` (sofferenze nette: utilizzato), `55100041` (numero di affidati); territorio in `SEDELEG_SOGG` | Milioni di euro / numero, trimestrale |
| `TDB20207.csv` | Banche e sportelli per provincia | ente `1100010`, `30990009` (sportelli), `30990005` (comuni serviti); territorio in `LOC_SPORT` | Numero, annuale (31/12) |
| `TDB20220.csv` | Sportelli per 100.000 abitanti | `30990011` | Annuale |
| `TDB10227.csv` | Dipendenti per provincia | `1001503` | Annuale |
| `TSDPT140.csv` | ATM e POS per provincia (tavola a serie storiche) | colonna `SDP_LOCATM.A.1100010.1700802.ITC41` (numero di ATM, banche, Varese) | Annuale |

Il **trimestre** corrisponde al **mese di fine trimestre**: sono consistenze, quindi non si sommano. I depositi e gli impieghi in **milioni** = `ROUND(valore in migliaia / 1000; 0)`. Le **variazioni** si calcolano sui valori **non** arrotondati.

## C1. Depositi (cartella `Report_credito_depositi_{N}_T{T}`)

### C1.1 `Credito_Depositi_Sintesi.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Territorio | {T} trim {N} (milioni di euro) | {T} trim {N−1} (milioni di euro) | T.var% tend
- **Righe (3)**: Varese, Lombardia, Italia; totale `SBI59` a fine trimestre.
- **Differenze volute** (decise dall'ufficio): nelle intestazioni compare il trimestre vero al posto di «periodo recente / periodo passato», e «milioni» al posto di «migliaia»: il modello sbagliava l'unità.

### C1.2 `Credito_Depositi_Tempo-trimestrale.xlsx` (Foglio1)
- **Colonne**: Anno | Trimestre | Depositi | T var% tend
- **Righe**: Varese dal I trim N−5 al trimestre scelto (`I trim 2021`…). Variazione sullo stesso trimestre dell'anno prima.

### C1.3 `Credito_Depositi_Tempo-annuale.xlsx` (Foglio1, **solo con T = 4**)
- **Colonne**: Anno | Depositi | T var% tend
- **Righe**: Varese, dicembre 2011 … N. La prima variazione è «\_», come nel modello.

### C1.4 `Credito_Depositi_Tipo-clientela.xlsx` (Foglio1)
- **Colonne**: Anno | Periodo | Famiglie | Imprese private | Altro | Totale
- **Righe**: gli stessi trimestri di C1.2.
- **Calcoli**: Famiglie = `600`; Imprese private = `S11BI32`; Totale = `SBI59`, tutti in milioni arrotondati. **Altro = Totale − Famiglie − Imprese, calcolato sui valori già arrotondati** (regola del foglio di lavoro dell'ufficio).

## C2. Impieghi (cartella `Report_credito_impieghi_{N}_T{T}`)

Tavola TDB10295, **stesse regole dei depositi**. Nomi e intestazioni sono quelli del modello impieghi, scelto dall'ufficio:
- **C2.1 `Credito_Impieghi_Sintesi.xlsx`**: come C1.1.
- **C2.2 `Credito_Impieghi_Tempo-trimestrale.xlsx`**: Anno | Trimestre | Impieghi | T.var% tend (con il punto).
- **C2.3 `Credito_Impieghi_Tempo-annuale.xlsx`** (solo T = 4): Anno | Impieghi | T var% tend, dal 2011, con la **prima variazione vuota**.
- **C2.4 `Credito_Impieghi_tipoclientela.xlsx`** (minuscolo, senza trattino): come C1.4, ma con i periodi `I trim '21`.

## C3. Sofferenze (cartella `Report_credito_sofferenze_{N}_T{T}`)

Valori della tavola TRI30401 **così come sono**: le sofferenze sono già in milioni, gli affidati sono un numero.

### C3.1 `Credito_sofferenze_sintesi.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | Sofferenze {T} trim {N} (milioni di euro) | Sofferenze {T} trim {N−1} (milioni di euro) | T.var % tend sofferenze | Affidati {T} trim {N} | Affidati {T} trim {N−1} | T.var % tend affidati
- **Righe (3)**: Varese, Lombardia, Italia.

### C3.2 `Credito_sofferenze_tempo-trimestre.xlsx` (Foglio1)
- **Colonne**: Anno | Trimestre | Sofferenze nette | T.var % tend sofferenze | Affidati | T.var % tend affidati
- **Righe**: Varese **dal I trim N−6** al trimestre scelto (25 righe con T = 1, 28 con T = 4), periodi `I trim '20`.

### C3.3 `Credito_sofferenze_tempo-anno.xlsx` (Foglio1, **solo con T = 4**)
- **Colonne**: Ordinamento | Anno | Sofferenze nette | T. var% tend sofferenze | Affidati | T. var% tend affidati
- **Righe**: Varese, dicembre 2011 … N. Le variazioni del 2011 sono vuote, come nel modello.

### C3.4 `Credito_sofferenze_sui-impieghi.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Anno | Periodo | Varese % | Lombardia % | Italia %
- **Righe**: gli stessi trimestri di C3.2.
- **Calcoli**: `ROUND(sofferenze / (impieghi TDB10295 SBI59 / 1000) × 100; 2)`. Usa due tavole: le sofferenze sono riferite alle banche, gli impieghi a banche e CDP, **come nel foglio di lavoro dell'ufficio**.

## C4. Sportelli (cartella `Report_credito_sportelli_{N}`, dati **annuali**)

### C4.1 `Sportelli_sintesi.xlsx` (foglio **Foglio2**)
- **Colonne**: Ordinamento | Indicatore | N−6 | … | N (anni veri al posto di «Anno 1…7», scelta dell'ufficio)
- **Righe (5)**: Comuni serviti da banche (`30990005`); Sportelli (`30990009`); Sportelli ogni 100mila abitanti (`30990011`); Dipendenti banche a Varese (`1001503`); N° ATM (\*) (TSDPT140). Varese, valori così come sono.
- Se l'ATM dell'anno manca, la tabella si crea con la cella vuota e la pagina mostra un avviso evidente.

### C4.2 `Sportelli_tempo.xlsx` (Foglio1)
- **Colonne**: Ordine | Anno | Numero sportelli
- **Righe**: Varese dal 2001 a N. Gli anni **2001–2014 sono fissi nella pagina** (`STORICO_SPORTELLI`, ricavati dalla vecchia tavola TDB10207, ferma al 2016). Dal 2015 si usa TDB20207.

---

# D. Lavoro (ISTAT – Forze di lavoro; INPS – Cassa integrazione)

Sito `codice/8_Web_Lavoro/index.html` (5 sezioni). Dati automatici in `dati/`.

## D.0 Dati di input ISTAT (annuali, dal 2018)

Tutte le tavole ISTAT si filtrano sul totale delle dimensioni di contorno: titolo di studio `EDU_LEV_HIGHEST = 99`, cittadinanza `TOTAL` e così via. Le chiavi vanno lette su 14 aree: Italia `IT`, Lombardia `ITC4` e le 12 province, con Milano `ITC45` e Monza `IT108`. Sesso: 1 maschi, 2 femmine, 9 totale.

| File in `dati/` | Dataflow | Tipo di dato | Età | Contorno |
|---|---|---|---|---|
| `disoccupazione_tassi.csv` | `IT1,151_914,1.0` | `UNEM_R` (tasso di disoccupazione) | 8 fasce: Y15-24, Y25-34, Y15-34, Y35-49, Y20-64, Y15-64, Y15-74, Y50-74 | — |
| `disoccupazione_disoccupati.csv` | `IT1,151_929_DF_DCCV_DISOCCUPT1_7,1.0` | `UNEMP` (migliaia) | Y15-74 | — |
| `occupazione_tassi.csv` | `IT1,150_915,1.0` | `EMP_R` | 10 fasce: Y15-24, Y18-29, Y15-29, Y25-34, Y35-44, Y45-54, Y55-64, Y20-64, Y15-64, Y15-89 | — |
| `occupazione_occupati.csv` | `IT1,150_938,1.0` | occupati (migliaia), senza colonna DATA_TYPE | Y15-89 | Ateco 2007: `0010` totale, `A`, `0020`, `F`, `0026`, `0025`; posizione `9` totale, `1` dipendenti, `2` indipendenti; part-time e tempo determinato a 9 |
| `attivita_forze.csv` | `IT1,150_908,1.0` | `FOR` (forze di lavoro, migliaia) | Y15-89 | — |
| `attivita_tassi.csv` | `IT1,150_916,1.0` | `ACT_R` | 9 fasce: Y15-24, Y18-29, Y25-34, Y35-44, Y35-49, Y45-54, Y55-64, Y15-64, Y15-89 | — |
| `inattivita_inattivi.csv` | `IT1,152_928,1.0` | `INAC` (migliaia) | Y15-64 | `LABPROF_STATUS_A = IN`, `INACTIVITY_REASON = ALL`, `DECLARED_LAB_STATUS = 99` |
| `inattivita_tassi.csv` | `IT1,152_913,1.0` | `INAC_R` | 9 fasce: Y15-24, Y18-29, Y25-34, Y35-44, Y35-49, Y45-54, Y55-64, Y15-64, Y_GE15 («15 anni e più») | — |

**Etichette dei territori nelle tabelle**: Varese, Como, Sondrio, Milano, Bergamo, Brescia, Pavia, Cremona, Mantova, Lecco, Lodi, Monza e Brianza, Lombardia, Italia.

## D1. Disoccupazione (cartella `Report_disoccupazione_{N}`)

### D1.1 `Istat_disoccupazione_sintesi.xlsx` (Foglio1)
- **Colonne**: Territori | Genere | Disoccupati periodo passato | Tasso di disoccupazione periodo passato | Disoccupati periodo recente | Tasso di disoccupazione periodo recente
- **Righe (9)**: Varese, Lombardia, Italia × Maschi, Femmine, Totale.
- **Calcoli**: disoccupati 15-74 ROUND(·; 0); tasso 15-74 ROUND(·; 2); anni N−1 e N.
- **Formati**: `0` / `0.0`; righe Italia della colonna C in `#,##0`, come il modello.

### D1.2 `Istat_disoccupazione_tassi.xlsx` (Foglio2)
- **Colonne**: Ordine | Genere | Anno | Varese | Lombardia
- **Righe (24 con N = 2025)**: Maschi, Femmine, Totale × 2018…N. Tasso ROUND(·; 2), formato `0.0`.

### D1.3 `Istat_disoccupazione_disoccupati.xlsx` (Foglio1)
- **Colonne**: (A1 vuota) | Genere | Anno | Varese disoccupati (migliaia) | Varese t.var.% | Lombardia disoccupati (migliaia) | Lombardia t.var.%
- **Calcoli**: disoccupati ROUND 0; t.var = `ROUND(ROUND(rec;0) / ROUND(prec;0) × 100 − 100; 2)`, cioè **sui valori arrotondati** (scelta dell'ufficio); **2018 = 0**.

### D1.4 `Istat_disoccupazione_disoccupati_grafico.xlsx` (Foglio1)
- **Colonne**: Ordine | Anno | Disoccupati maschi (migliaia) | Disoccupati femmine (migliaia) | Totale (migliaia)
- Varese 2018…N, **con i decimali** ISTAT (formato `0.000`, scelta dell'ufficio).

### D1.5 `Istat_disoccupazione_territori.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | Maschi | Femmine | Totale
- **Righe (14)**: 12 province, Lombardia, Italia; tasso 15-74 dell'anno N, ROUND(·; 2), formato `0.0`.

### D1.6 `Istat_disoccupazione_eta.xlsx` (Foglio2)
- **Colonne**: Territorio | Territorio e fasce d'età | Maschi N | Femmine N | Totale N | Totale N−1
- **Righe (16)**: Lombardia, poi Varese, × 8 fasce (`15-24 anni`…). Valori ISTAT **non arrotondati**, formato `0.00`.

## D2. Occupazione (cartella `Report_occupazione_{N}`)

### D2.1 `Istat_occupazione_sintesi.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | Genere | Occupati periodo passato | Tasso di occupazione periodo passato | Occupati periodo recente | Tasso di occupazione periodo recente
- **Righe (9)**: Varese, Lombardia, Italia × genere.
- **Calcoli**: occupati 15-89 (totale Ateco `0010`, posizione 9) ROUND 0; tasso 15-64 ROUND 2.

### D2.2 `Istat_occupazione_tassi.xlsx` (Foglio1)
- **Colonne**: Ordine | Genere | Anno | Varese | Lombardia. Tasso 15-64 ROUND 2, 2018…N.

### D2.3 `Istat_occupazione_occupati_tabella.xlsx` (Foglio1)
- **Colonne**: Genere | Anno | Varese occupati (migliaia) | Varese t.var.% | Lombardia occupati (migliaia) | Lombardia t.var.%
- **Calcoli**: occupati ROUND 0; t.var sui valori arrotondati come in D1.3; **2018 = 0**.

### D2.4 `Istat_occupazione_occupati_grafico.xlsx` (Foglio2)
- **Colonne**: Anno | Maschi | Femmine | Totale. Varese 2018…N, **con i decimali** (`0.000`). Il modello aveva gli anni passati interi: la scelta dell'ufficio è avere i decimali per tutti gli anni.

### D2.5 `Istat_occupazione_territorio.xlsx` (foglio **Foglio3**, l'unico)
- **Colonne**: Ordine | Territorio | Tasso di occupazione maschi | … femmine | … totale
- **Righe (14)**: 12 province, Lombardia, Italia; tasso 15-64 ROUND 2. Il vecchio «Foglio1» del modello non si riproduce.

### D2.6 `Istat_occupazione_età.xlsx` (Foglio2)
- **Colonne**: Territorio | Territorio e fasce d'età | Maschi N | Femmine N | Totale N | Totale N−1
- **Righe (20)**: Lombardia, poi `  Varese` (con 2 spazi davanti, come il modello), × 10 fasce. Valori non arrotondati.

### D2.7 `Istat_occupazione_settori.xlsx` (Foglio2)
- **Colonne**: Ordine | Territorio | Settori | Occupati (migliaia) | Peso %  | T.var %
- **Righe (18)**: per Varese e per Lombardia:
  - TOTALE (`0010`), Agricoltura (`A`), Industria in senso stretto (`0020`), Costruzioni (`F`), Commercio, alberghi e ristoranti (`0026`), Altri servizi (`0025`);
  - la riga titolo «Tipologia d'impiego» (vuota);
  - Dipendenti (posizione 1; «Dipendenti » con lo spazio solo per Varese, come il modello), Indipendenti (posizione 2).
- **Calcoli**: occupati = valore ISTAT anno N non arrotondato; Peso = peso(voce, TOTALE); T.var = `ROUND(N / (N−1) × 100 − 100; 2)` su valori non arrotondati.
- **Differenze volute** (decise dall'ufficio):
  - si usano le voci provinciali ISTAT `0026` e `0025` al posto di «Commercio» e «Altri servizi» di Osserva, perché la fonte di quei due valori non è nota e ISTAT non li pubblica per provincia;
  - la variazione è sempre su **N−1**: il modello 2025 la calcolava per errore sul 2023.

### D2.8 `Istat_occupazione_settori x grafico.xlsx` (Foglio2)
- **Colonne**: Territorio | Settori | Totale occupati (migliaia) | % occupati totali per settore
- **Righe (6)**: Varese, TOTALE + 5 settori; % = peso(voce, TOTALE).

## D3. Attività (cartella `Report_attivita_{N}`)

| File | Foglio | Colonne | Righe e calcoli |
|---|---|---|---|
| `Istat_attività-sintesi.xlsx` (con il trattino) | Foglio2 | Ordine \| Territorio \| Genere \| Forze lavoro periodo passato (migliaia) \| Tasso di attività periodo passato \| Forze lavoro periodo recente (migliaia) \| Tasso di attività periodo recente | Varese, Lombardia, Italia × genere; forze di lavoro 15-89 ROUND 0; tasso di attività 15-64 ROUND 2 |
| `Istat_attività_tassi.xlsx` | Foglio1 | Genere \| Anno \| Varese \| Lombardia | Tasso 15-64 ROUND 2, 2018…N, formato `0.0` |
| `Istat_attività_forze lavoro.xlsx` | Foglio1 | Genere \| Genere e anno \| Varese forze di lavoro (in migliaia) \| Varese tasso di variazione % \| Lombardia … | ROUND 0; variazione sui valori arrotondati; **2018 = «nd»** |
| `Istat_attività_forze lavoro_grafico.xlsx` | Foglio1 | Anno \| Maschi \| Femmine \| Totale | Varese, **arrotondati a 0 decimali** per tutti gli anni (come il modello) |
| `Istat_attività_territori.xlsx` | Foglio1 | Ordine \| Territorio \| Maschi \| Femmine \| Totale | 12 province, Lombardia, Italia; tasso 15-64 ROUND 2 |
| `Istat_attività_età.xlsx` | Foglio1 | Ordine \| Territorio \| Territorio e fasce d'età \| Maschi N \| Femmine N \| Totale N \| Totale N−1 | **Varese prima, poi Lombardia**; 9 fasce, etichette `15-24 anni` con **due spazi finali**; valori non arrotondati |

Errore del modello 2025 corretto: nel grafico le femmine 2025 erano 117 (errore di battitura); il dato è 177.

## D4. Inattività (cartella `Report_inattivita_{N}`)

| File | Foglio | Colonne | Righe e calcoli |
|---|---|---|---|
| `Istat_inattività_sintesi.xlsx` | Foglio1 (solo questo) | Ordine \| Territorio \| Territorio e genere \| Inattivi periodo passato (migliaia) \| Tasso di inattività periodo passato \| Inattivi periodo recente (migliaia) \| Tasso di inattività periodo recente | Varese, Lombardia, Italia × genere; inattivi 15-64 ROUND 0; tasso 15-64 ROUND 2 |
| `Istat_inattività_tassi.xlsx` | **Foglio2** | Genere \| Anno \| Varese \| Lombardia | Tasso 15-64 ROUND 2, 2018…N |
| `Istat_inattività_inattivi.xlsx` | Foglio1 (riquadro bloccato su A2) | Genere \| Genere e anno \| Varese inattivi (migliaia) \| Varese t.var.% \| Lombardia … | ROUND 0; variazione sui valori arrotondati; **2018 = «nd»** |
| `Istat_inattività_inattivi_grafico.xlsx` | Foglio1 | Anno \| Maschi \| Femmine \| Totale | Varese **con i decimali per tutti gli anni** (`0.000`, scelta dell'ufficio) |
| `Istat_inattività_territorio.xlsx` | Foglio1 | Ordine \| Territorio \| Maschi \| Femmine \| Totale | 12 province, Lombardia, Italia; tasso 15-64 ROUND 2 |
| `Istat_inattività_età.xlsx` | Foglio1 | Territorio \| Territorio e fasce d'età \| Maschi N \| Femmine N \| Totale N \| Totale N−1 | Varese prima, poi Lombardia; 9 fasce (ultima: «15 anni e più»); non arrotondati |

## D.5bis Dati di input INPS (Cassa integrazione)

Osservatorio INPS «Cassa integrazione guadagni – ore autorizzate» per codice statistico contributivo:
- osservatorio **512**: mensile dal 2023;
- osservatorio **304**: mensile dal 2009 al 2022.

Lo scarico è fatto da `aggiorna_cig.py`. I tre tipi di intervento sono Ordinaria (CIGO), Straordinaria (CIGS) e Deroga (CIGD); il totale lo calcola la pagina.

| File in `dati/` | Colonne | Contenuto |
|---|---|---|
| `cig_territori.csv` | anno, periodo, tipo, territorio, ore | 12 province lombarde, Lombardia (= somma delle 12), Italia; `periodo` = trimestre 1–4; ore **cumulate da gennaio a fine trimestre** |
| `cig_classi.csv` | anno, periodo, tipo, classe, ore | Varese per classe di attività (28 classi INPS), cumulate come sopra |
| `cig_varese_mensile.csv` | anno, mese, tipo, ore | Varese mese per mese dal 2009 |

Si scaricano i periodi cumulati e non i mesi perché l'INPS rifiuta per riservatezza alcune tavole mensili di dettaglio.

Le ore sono **flussi**.

**Regole di calcolo**:
- **Variazione**: `ROUND(rec / prec × 100 − 100; 2)`. Se il confronto è 0, la cella vale `0` quando anche il valore attuale è 0, altrimenti `n.d.`.
- **Peso**: `ROUND(v / totale × 100; 2)`.
- Percentuali sempre a 2 decimali; ore come numeri interi.

## D5. Cassa integrazione (cartella `Report_cassa_integrazione_{N}_T{T}`)

Nelle intestazioni il periodo cumulato si chiama `gen-mar`, `gen-giu`, `gen-set` o `gen-dic`.

### D5.1 `CIG_sintesi.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Territori | Tipo variabili | gen-xxx N−1 | gen-xxx N | T.var.%
- **Righe (12)**: VARESE, LOMBARDIA, ITALIA × Ordinaria, Straordinaria, Deroga, TOTALE (somma dei tre). Ore cumulate.

### D5.2–D5.5 `CIG_territori_CIGO.xlsx`, `CIG_territori_CIGS.xlsx`, `CIG_territori_CIGD.xlsx`, `CIG_territori_CIG_TOTALE.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Territorio | CIGO (o CIGS, CIGD, CIG totale) | Peso % sul tot regionale | T.var% tendenziale
- **Righe (14)**: Milano, Bergamo, Brescia, Como, Cremona, Lecco, Lodi, Mantova, Monza e della Brianza, Pavia, Sondrio, Varese, LOMBARDIA, ITALIA\*.
- **Calcoli**: ore cumulate di N; peso = peso(provincia, Lombardia); nella riga **ITALIA\*** il peso è **Lombardia / Italia** (scelta dell'ufficio, come Osserva); T.var su cum(N−1).
- **Differenza voluta**: il nome `CIG_territori_CIGS` (su Osserva era `CIG_territori_CIGS_`).

### D5.6–D5.9 `CIG_settori_CIGO.xlsx`, `CIG_settori_CIGS.xlsx`, `CIG_settori_DEROGA.xlsx`, `CIG_settori_TOTALE.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Settore | CIGO periodo passato | CIGO periodo recente | Peso % sul totale | T.var% tendenziale. Per il TOTALE le intestazioni sono `gen-xxx N−1` e `gen-xxx N`; per la Deroga «Deroga periodo …».
- **Righe**: le classi di attività che l'INPS mostra per quel tipo (oggi 22 per la CIGO, 26 per la CIGS, 13 per la Deroga) + Totale. Per il TOTALE ci sono tutte e 28 le classi (somma dei tre tipi).
- **Calcoli**: ore cumulate di Varese per classe; peso sul Totale; T.var su N−1.
- **Differenze volute**: «Attività» con l'accento e la parentesi chiusa in «Attività varie (…)»; intestazioni corrette (il modello della Deroga diceva «CIGS»).

### D5.10 `CIG_tempo_TRIMESTRE.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Anno | Trimestre | CIGO | T.var% tend. CIGO | CIGS | T.var% tend. CIGS | Deroga | T.var% tend. DEROGA | Totale | T.var% tend. TOTALE
- **Righe**: dal **I trim 2021** (inizio fisso) al trimestre scelto, etichette `I trim '21`.
- **Calcoli**: **trimestre singolo** = somma dei 3 mesi (`cig_varese_mensile.csv`); variazione sullo stesso trimestre dell'anno prima.

### D5.11 `CIG_tempo_ANNO.xlsx` (Foglio1)
- **Colonne**: Ordinamento | Anno | CIGO | T.var% CIGO | CIGS | T.var% CIGS | Deroga | T.var% Deroga | Totale | T.var% Totale
- **Righe**: dal 2009 all'ultimo anno completo (N se T = 4, altrimenti N−1). Somma dei 12 mesi. **2009 = n.d.**, perché manca il 2008.
- Per le serie 2009–2015 si usano i dati INPS di oggi, che sono leggermente diversi da quelli vecchi di Osserva (scelta dell'ufficio).

---

# E. Popolazione (ISTAT)

Sito `codice/9_Web_Popolazione/index.html`. Cartella `Report_popolazione_{N}`, dove N è l'anno del 1° gennaio.

## E.0 Dati di input (ISTAT SDMX, popolazione al 1° gennaio)

| File in `dati/` | Dataflow | Chiave / contenuto |
|---|---|---|
| `popolazione_residenti.csv` | `IT1,22_289_DF_DCIS_POPRES1_1,1.0` | `A.<14 aree>.JAN.1+2+9.TOTAL.99` dal 2019: maschi, femmine, totale |
| `popolazione_eta.csv` | stesso | `A.ITC41.JAN.9..99`: Varese per singola età (Y0…Y99, Y_GE100) |
| `popolazione_stranieri.csv` | `IT1,29_7_DF_DCIS_POPSTRRES1_1,1.0` | `A.IT+ITC4+ITC41.JAN.9.`: stranieri, per età |
| `popolazione_serie_storica.csv` | `IT1,164_164_DF_DCIS_RICPOPRES2011_1,1.0` | Varese 2002–2019 (ricostruzione intercensuaria) |
| `popolazione_bilancio.csv` | `IT1,22_315_DF_DCIS_POPORESBIL1_1,1.0` | Varese: saldo naturale `NTGROW_REGOF`, migratorio estero `INTERTNMIG_REGOF`, totale |
| `popolazione_indici.csv` | `IT1,22_293_DF_DCIS_INDDEMOG1_1,1.0` | Varese, Lombardia, Italia: TFR, LIFEEXP0M, LIFEEXP0F, DEPENDRATE, OLDAGEDEPR, AGEINDEX, MEANAGEP dal 2018 |

Valori **non arrotondati** (formato `0.00`). Variazione = (recente / precedente − 1) × 100. L'ultimo 1° gennaio è **provvisorio** (stato `e`) e la pagina lo segnala.

## E.1 `Popolazione_sintesi.xlsx` (Foglio1)
- **Colonne**: Ordine | Territori | Popolazione | periodo passato | periodo recente | T.var.% | Peso%
- **Righe (15)**: Varese, Lombardia, Italia × Maschi, Femmine, Totale, Stranieri, Densità abitativa.
- **Calcoli**:
  - passato = 1/1/N−1; recente = 1/1/N;
  - Peso = valore / totale del territorio nell'anno recente × 100 (il Totale vale 100);
  - **Densità** = popolazione / km², con superfici fisse nella pagina (1.198, 23.844 e 301.338 km², `SUPERFICIE_KMQ`), senza variazione né peso.

## E.2 `Popolazione_caratteristiche.xlsx` (Foglio1)
- **Colonne**: Ordine | Caratteristiche | N−1 | N | T.var.% | Peso % (le intestazioni degli anni sono numeriche).
- **Righe (14)**, per Varese:
  - Maschi, Femmine, Totale genere;
  - Italiani (= totale − stranieri), Stranieri, Totale nazionalità;
  - 0-14, 15-64, 65 e oltre, Totale età (somma delle singole età);
  - Stranieri 0-14 / 15-64 / 65 e oltre, Totale stranieri età.
- **Calcoli**: peso sul totale del proprio blocco.

## E.3 `Popolazione_territori.xlsx` (Foglio1)
- **Colonne**: Ordine | Territorio | N−1 | N | T.var. % | Peso %
- **Righe (14)**: Varese, Como, Sondrio, Milano, Bergamo, Brescia, Pavia, Cremona, Mantova, Lecco, Lodi, Monza e Brianza, Lombardia, **Italia\***.
- **Calcoli**: peso sulla Lombardia; nella riga Italia\* è il peso della Lombardia sull'Italia.

## E.4 `Popolazione_tempo.xlsx` (Foglio1)
- **Colonne**: Anno | Popolazione | T.var %
- **Righe (15)**: Varese, N−14 … N. La variazione del primo anno usa l'anno N−15. La serie viene dalla ricostruzione fino al 2018 e dalla tavola attuale dal 2019.

## E.5 `Popolazione_saldi.xlsx` (Foglio1)
- **Colonne**: Anno | Saldo naturale | Saldo migratorio e per altri motivi | Di cui: saldo migratorio estero | Saldo Totale
- **Righe**: Varese, **dal 2019** (scelta dell'ufficio) all'anno N−1.
- **Calcoli**:
  - Saldo totale = popolazione al 1/1 dell'anno+1 − popolazione al 1/1 dell'anno;
  - saldo migratorio e per altri motivi = totale − naturale.
- Gli anni 2019–2021 differiscono da Osserva per una revisione ISTAT post-censimento.

## E.6 `Popolazione_indici.xlsx` (foglio **Foglio2**)
- **Colonne**: Ordine | Territorio | Indici | 2018 … N
- **Righe (21)**: Varese, Lombardia, Italia × 7 indici: Numero medio di figli per donna; Speranza vita dei maschi; Speranza di vita delle femmine; Indice di dipendenza strutturale; Indice di dipendenza anziani; Indice di vecchiaia; Eta' media.
- Le celle restano vuote dove ISTAT non ha ancora il dato (figli per donna e speranza di vita dell'ultimo anno). Il modello di Osserva era un `.xls`; qui si produce un `.xlsx`.

---

# F. Conti economici – Valore aggiunto

Sito `codice/10_Web_ContiEconomici/index.html`. Cartella `Report_valore_aggiunto_{N}`.

## F.0 Dati di input e regola degli anni

| File in `dati/` | Fonte | Contenuto |
|---|---|---|
| `tagliacarne_AAAA.csv` (uno per anno, **mai sovrascritto** da un anno più recente) | File Excel «Valore aggiunto per provincia e branca di attività economica. Anno AAAA» del Centro Studi Tagliacarne | Per circa 131 territori (province, regioni, ripartizioni, Italia): agricoltura, industria in senso stretto, costruzioni, commercio, attività finanziarie, altri servizi, totale (milioni di euro), valore aggiunto pro-capite (euro) |
| `tagliacarne_2023.csv` | Valore di Osserva salvato una volta (`fonte=osserva`) | Varese, Lombardia, Italia 2023: il dato non è disponibile in forma aperta |
| `istat_valore_aggiunto.csv` | ISTAT `IT1,93_498_DF_DCCN_PILT_1` (valore aggiunto ai prezzi base, edizione più recente) + popolazione al 1° gennaio | anno, area, valore_aggiunto, popolazione_media. **Lombardia = somma delle 12 province; Italia = somma di 107 province + «extra-regio» `ITZ`** (il dato nazionale diretto sbaglia l'ultima cifra) |

**Regola degli anni**, decisa dall'ufficio, per l'anno scelto N:
- **N** = file Tagliacarne di quell'anno;
- **N−1** = file Tagliacarne dell'anno prima, già in archivio;
- **N−2 e precedenti** = ISTAT.

Pro-capite ISTAT = ROUND(VA; 1) × 10⁶ / media della popolazione al 1/1 dell'anno e al 1/1 dell'anno+1. Per Tagliacarne il pro-capite è già nel file.

**Branche**: ogni voce Tagliacarne si arrotonda a **1 decimale prima** di sommare i 3 gruppi dei servizi e prima di calcolare le quote. Servizi = R1(commercio) + R1(attività finanziarie) + R1(altri servizi).

## F.1 `VA_SINTESI.xlsx` (foglio **Sheet3**)
- **Colonne**: Ordinamento | Valori | variabili | periodo passato | periodo recente | T.var % 
- **Righe (8)**:
  - «VALORE AGGIUNTO in milioni di euro» per Varese, Lombardia, Italia;
  - «Quota % Varese su Lombardia », «Quota % Varese su Italia »;
  - «VALORE AGGIUNTO PRO-CAPITE in euro» per Varese, Lombardia, Italia.
- **Calcoli**:
  - passato = N−1, recente = N;
  - T.var = ROUND(var; 2);
  - le quote sono ROUND(·; 2), ma la loro variazione si calcola sulle quote **non** arrotondate.

## F.2 `VA_TEMPO_tot.xlsx` (Foglio1)
- **Colonne**: Valore aggiunto (milioni di euro) | Varese | Lombardia | Italia
- **Righe (15)**: N−14 … N, con la regola degli anni. Formato `0.0`.

## F.3 `VA_TEMPO_procapite.xlsx` (Foglio2)
- **Colonne**: Ordinamento | Valore aggiunto | Varese | Lombardia | Italia
- **Righe (15)**: N−14 … N, pro-capite in euro, `0.00`.

## F.4 `VA_TERRITORI.xlsx` (foglio **Sheet2**)
- **Colonne**: Ordinamento | Territorio | Valore aggiunto (milioni di euro) | Quota % su Lombardia | Quota % su Italia | Valore aggiunto pro-capite (euro)(\*)
- **Righe (14)**: 12 province (etichetta «Monza e della Brianza (\*\*)»), LOMBARDIA, ITALIA; anno N, Tagliacarne.
- **Calcoli**: quota su Lombardia = ROUND(VA / Lombardia × 100; 2) (Lombardia = 100; per l'Italia la cella vale «..»); quota su Italia (Italia = 100).

## F.5 `VA_SETTORI.xlsx` (Foglio1)
- **Colonne**: Ordinamento 1 | Ordinamento 2 | Territori | Agricoltura, silvicoltura e pesca | Industria in senso stretto | Costruzioni | Servizi | Totale
- **Righe (30)**:
  - riga titolo «Valori assoluti» + 14 territori;
  - riga titolo «Quota % per settore» + 14 territori («Monza e Brianza» nelle quote).
- **Calcoli**: branche arrotondate (F.0); quote = ROUND(branca / totale × 100; 2), con Totale = 100. Anno N.

## F.6 `VA_SETTORI_grafico.xlsx` (Foglio1)
- **Colonne**: Settori | Quota % per settore
- **Righe (4)**: Agricoltura, Industria, Costruzioni, Servizi di Varese; quote come in F.5.

Differenza voluta: i formati mostrano i decimali (`0.0` e `0.00`); i modelli usavano `0`, che li nascondeva. I modelli in parte `.xls` diventano `.xlsx`.

---

# G. Trasporti – Strade (autovetture)

Sito `codice/11_Web_Trasporti/index.html`. Cartella `Report_trasporti_strade_{N}`.

## G.0 Dati di input

| File in `dati/` | Fonte | Contenuto |
|---|---|---|
| `aci_autovetture.csv` (anno, territorio, autovetture, fonte) | ACI «Autoritratto», foglio `1_Provincia_categoria` del file `Parco_veicolare_AAAA.ods` | Autovetture al 31/12 per le 12 province, Lombardia (= somma delle 12, verificata sul totale regionale) e Italia (= somma delle province, verificata sul «Totale NAZIONALE»). **Archivio iniziale** (`fonte=archivio`) dal foglio di lavoro dell'ufficio: Varese 2009–2023, Lombardia e Italia 2020–2023 (verificato con le edizioni ACI 2019–2023, salvo Varese 2009–2018). Dal 2024 `fonte=aci` |
| `aci_varese_dettaglio.csv` (anno, tavola, riga, colonna, valore) | `Circolante_Copert_AAAA.ods` foglio `3_AV_per_Provincia` (alimentazione × classe Euro) e `Parco_veicolare_AAAA.ods` foglio `27_AV_Provincia_cilindrata` | Solo Varese, solo valori diversi da 0 |
| `istat_popolazione.csv` | ISTAT, popolazione al 1° gennaio (come E.0, con la ricostruzione per gli anni prima del 2019) | Varese, Lombardia, Italia |

**Regola dell'ufficio** per «ogni 100 abitanti»: autovetture al 31/12 dell'anno Y / popolazione al **1° gennaio dello stesso anno Y** × 100, **non arrotondato**. Variazione = `nuovo / vecchio × 100 − 100`, non arrotondata. Peso = voce / totale × 100.

Formati: conteggi `#,##0`, percentuali e «ogni 100 abitanti» `0.00`.

## G.1 `Trasporto_su_strada_sintesi.xlsx` (Foglio2)
- **Colonne**: Ordine | Territori | Autovetture | Periodo precedente | Periodo successivo | T.var %
- **Righe (6)**: Varese, Lombardia, Italia × Totale, Ogni 100 abitanti; anni N−1 e N.

## G.2 `Trasporto_su_strada_sintesi_x_grafico.xlsx` (Foglio2)
- **Colonne**: Ordine | Territori | Periodo precedente | Periodo successivo
- **Riga (1)**: autovetture di Varese, N−1 e N.

## G.3 `Trasporto_su_strada_tempo.xlsx` (Foglio1)
- **Colonne**: Ordine | Anno | Autovetture | T.var % | Autovetture ogni 100 abitanti
- **Righe (15)**: Varese, N−14 … N.

## G.4 `Trasporto_su_strada_tipologia_euro.xlsx` (Foglio1)
- **Colonne**: Ordine | Tipologia | Autovetture | Peso %
- **Righe (10)**: Euro 0 … Euro 6, Alimentazione elettrica, Non definito, Totale (peso 100).
- **Calcoli**:
  - Euro 5 = 5 + 5B;
  - Euro 6 = 6, 6A … 6E (regola `^EURO ([0-6])[A-Z]?$`);
  - «Alimentazione elettrica» = colonna ACI «Non contemplato».
- Una classe Euro nuova blocca la tabella con un messaggio.

## G.5 `Trasporto_su_strada_tipologia_alimentazione.xlsx` (Foglio1)
- **Colonne**: Ordine | Alimentazione | Autovetture | Peso %
- **Righe (10)**: Benzina, Benzina e gas liquido, Benzina e metano, Elettricità, Gasolio, Ibrido benzina, Ibrido gasolio, Metano, Altre e non definito, Totale.
- **Raggruppamenti delle voci ACI** (`MAPPA_ALIM`):
  - Ibrido benzina = IBRIDO BENZINA + IBRIDO BENZINA GAS LIQUIDO + IBRIDO BENZINA METANO;
  - Ibrido gasolio = IBRIDO GASOLIO + IBRIDO GASOLIO GPL;
  - Altre e non definito = ALTRE + NON DEFINITO (le voci ACI nuove finiscono qui, con un avviso);
  - **GASOLIO E GAS → Gasolio**. Punto aperto: Osserva 2025 lo metteva tra gli Ibridi gasolio (2 auto).

## G.6 `Trasporto_su_strada_tipologia_cilindrata.xlsx` (Foglio1)
- **Colonne**: Ordine | Cilindrata | Autovetture | Peso %
- **Righe (6)** e fasce ACI raggruppate:

  | Riga | Fasce ACI |
  |---|---|
  | Fino a 1200 | fino a 800, 801–1200 |
  | 1201 - 2000 | 1201–1600, 1601–1800, 1801–2000 |
  | 2001-3000 | 2001–2500, 2501–3000 |
  | Oltre 3000 | oltre 3000 |
  | Non definito | non definito |
  | Totale | — |

Differenze volute rispetto a Osserva:
- numeri come numeri (Osserva li aveva come testo con la virgola);
- nessuno spazio finale nelle etichette;
- «ogni 100 abitanti» con 2 decimali visibili;
- stile uniforme.
