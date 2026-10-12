# -*- coding: utf-8 -*-
# ============================================================================
#  QUERY SALVATE  -  incolla qui le tue query ISTAT (una sola volta).
#  Vale sia per la riga di comando sia per l'interfaccia grafica.
# ============================================================================
#
#  DUE TIPI (il programma sceglie da solo):
#   TIPO A "normale": ha "url" dei dati (.../SDMXWS/rest/data/...).
#       Campi: "nome", "url", "layout", "righe", "lingua".
#   TIPO B "coeweb" : ha "filtri" (POST databrowserhub; niente URL semplice).
#       In DevTools -> Network -> richiesta POST a .../datasets/.../data ->
#       scheda "Payload" -> Copy value -> incolla in "filtri". Copia anche la
#       "Request URL" in "url".
#       Campi: "nome", "url", "filtri", "layout", "righe", "struttura".
#
#  REGOLA: ogni query DENTRO QUERY = [ ... ] e SENZA '#' davanti.
#  layout: "long" (consigliato, qualunque dataflow) o "istat" (matrice).
#  Lo script riconosce da solo il formato della risposta (XML/JSON/CSV):
#  le etichette in italiano arrivano via JSON o CSV; per l'XML a codici
#  puoi indicare "struttura": "percorso_del_file_SDMX_struttura.xml".
# ============================================================================

QUERY = [

    # ----- TIPO A: BES - Speranza di vita alla nascita -----
    {
        "nome": "BES - Speranza di vita alla nascita",
        "url": "https://esploradati.istat.it/SDMXWS/rest/data/IT1,DF_BES_TERRIT_1,1.0/...01SAL001../ALL/",
        "layout": "istat",
        "righe": "REF_AREA",
    },

    # ----- TIPO B: COEWEB commercio estero (usa "filtri", non una URL semplice) -----
    {
        "nome": "Coeweb CPA Ateco2007 - Export valore (MONDO)",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "DATA_TYPE", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "filterValues": [], "type": "TimeRange",
             "period": 0, "from": "2020-01-01T00:00:00", "to": "2026-12-31T00:00:00"},
        ],
        "layout": "long",
    },

    # ----- TIPO B: COEWEB - Export valore, provincia Monza e Brianza (IT108) -----
    # NOTA: nel payload originale i filtri CPA e TIME_PERIOD erano troncati ("...").
    # Qui assumo CPA = ALL (tutte le voci). Se avevi scelto CPA specifiche,
    # sostituisci "filterValues": ["ALL"] con i codici copiati (Copy value completo).

 

# ----- INCOLLA QUI ALTRE QUERY (copia un blocco qui sopra, SENZA '#') -----

    # ----- TIPO B: COEWEB - Solo Esportazioni (italia, lombardia e Varese) -----
    {
        "nome": "EXPORT sintesi",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "type": "CodeValues", "filterValues": ["ITC4", "ITC41", "ITTOT"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "long",
    },

    # ----- TIPO B: COEWEB - Solo Importazioni (italia, lombardia e Varese) -----
    {
        "nome": "IMPORT sintesi",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "type": "CodeValues", "filterValues": ["ITC4", "ITC41", "ITTOT"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["IV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "long",
    },

	

	

 

 # ----- INCOLLA QUI ALTRE QUERY (copia un blocco qui sopra, SENZA '#') -----

    # ----- TIPO B: COEWEB - Export Varese (Sottosettori Manifatturiero in un unico foglio) -----
    {
        "nome": "EXPORT varese manifatturiero",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "UNICA",
    },

    # ----- TIPO B: COEWEB - Import Varese (Sottosettori Manifatturiero in un unico foglio) -----
    {
        "nome": "IMPORT varese manifatturiero",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["IV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "UNICA",
    },

# ----- INCOLLA QUI ALTRE QUERY (copia un blocco qui sopra, SENZA '#') -----

    # ----- TIPO B: COEWEB - Export Varese (Solo Continenti e Singoli Paesi) -----
    {
        "nome": "export Varese - Paesi e Continenti (top20)",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": [
                "AD", "AE", "AF", "AFR", "AG", "AI", "AL", "AM", "AME", "AN", "AO", "AQ", "AR", "AS", "ASI", "AT", "AU", "AW", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CS", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "EL", "ER", "ES", "ET", "EUR", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IO", "IQ", "IR", "IS", "IT", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OCE", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SU", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YF", "YT", "YU", "ZA", "ZM", "ZR", "ZW"
            ]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "TOP20", 
    },

    # ----- TIPO B: COEWEB - Solo Importazioni (Varese - Solo Continenti e Singoli Paesi) -----
    {
        "nome": " Import Varese - Paesi e Continenti (top20)",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["IV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": [
                "AD", "AE", "AF", "AFR", "AG", "AI", "AL", "AM", "AME", "AN", "AO", "AQ", "AR", "AS", "ASI", "AT", "AU", "AW", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CS", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "EL", "ER", "ES", "ET", "EUR", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IO", "IQ", "IR", "IS", "IT", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OCE", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SU", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YF", "YT", "YU", "ZA", "ZM", "ZR", "ZW"
            ]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "TOP20", 
    },

# ----- INCOLLA QUI ALTRE QUERY (copia un blocco qui sopra, SENZA '#') -----

    # ----- TIPO B: COEWEB - Export Varese (Solo Paesi ordinati decrescenti) -----
    {
        "nome": "Coeweb - Export Varese - Solo Paesi Ordinati",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": [
                "AD", "AE", "AF", "AFR", "AG", "AI", "AL", "AM", "AME", "AN", "AO", "AQ", "AR", "AS", "ASI", "AT", "AU", "AW", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CS", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "EL", "ER", "ES", "ET", "EUR", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IO", "IQ", "IR", "IS", "IT", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OCE", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SU", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YF", "YT", "YU", "ZA", "ZM", "ZR", "ZW"
            ]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "SOLOPAESI",  
    },

    # ----- TIPO B: COEWEB - Solo Importazioni (Varese - Solo Paesi ordinati decrescenti) -----
    {
        "nome": "Coeweb - Import Varese - Solo Paesi Ordinati",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": ["ITC41"]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["IV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": [
                "AD", "AE", "AF", "AFR", "AG", "AI", "AL", "AM", "AME", "AN", "AO", "AQ", "AR", "AS", "ASI", "AT", "AU", "AW", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CS", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "EL", "ER", "ES", "ET", "EUR", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IO", "IQ", "IR", "IS", "IT", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OCE", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SU", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YF", "YT", "YU", "ZA", "ZM", "ZR", "ZW"
            ]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2026-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "SOLOPAESI", 
    },

# ----- INCOLLA QUI ALTRE QUERY (copia un blocco qui sopra, SENZA '#') -----

    # ----- TIPO B: COEWEB - Solo Esportazioni (Lombardia e Province) -----
    {
        "nome": " Export Lombardia e Province",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": [
                "IT108", "ITC4", "ITC41", "ITC42", "ITC43", "ITC44", "ITC45", "ITC46", "ITC47", "ITC48", "ITC49", "ITC4A", "ITC4B"
            ]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["EV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2030-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "Territorio",  
    },

    # ----- TIPO B: COEWEB - Solo Importazioni (Lombardia e Province) -----
    {
        "nome": " Import Lombardia e Province",
        "url": "https://esploradati.istat.it/Coeweb/databrowserhub/api/core/nodes/1/datasets/IT1,DF_DCSE_CPA_ATECO2007_COE_A_Q_CONJ,1.0/data",
        "filtri": [
            {"id": "FREQ", "filterValues": ["Q"]},
            {"id": "REF_AREA", "filterValues": [
                "IT108", "ITC4", "ITC41", "ITC42", "ITC43", "ITC44", "ITC45", "ITC46", "ITC47", "ITC48", "ITC49", "ITC4A", "ITC4B"
            ]},
            {"id": "DATA_TYPE", "type": "CodeValues", "filterValues": ["IV"]},
            {"id": "ADJUSTMENT", "filterValues": ["N"]},
            {"id": "CPA_ATECO2007_COE", "filterValues": ["ALL"]},
            {"id": "PARTNER_COUNTRY", "filterValues": ["WORLD"]},
            {"id": "TIME_PERIOD", "type": "TimeRange", "filterValues": [], "from": "2025-01-01T00:00:00", "to": "2030-12-31T00:00:00"}
        ],
        "layout": "istat",
        "righe": "Territorio",  
    },

]