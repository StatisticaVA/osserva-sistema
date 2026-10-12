#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sdmx_gui.py - Interfaccia grafica per le query SDMX salvate (edizione premium).
Mostra l'elenco delle query definite in 'query_salvate.py' con caselle da
spuntare; premi "Aggiorna" e crea gli Excel con i dati piu' recenti.
Richiede 'sdmx_estrai.py' e 'query_salvate.py' nella stessa cartella.

Solo libreria standard (tkinter): nessuna dipendenza grafica aggiuntiva.
"""
import datetime as _dt, os, queue, sys, threading, webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sdmx_estrai as core
import report_import_export as report

# ============================================================================
#  DESIGN SYSTEM
# ============================================================================
# Sfondi e superfici
BG        = "#EEF1F8"   # sfondo finestra (azzurro-grigio freddo)
SURFACE   = "#FFFFFF"   # card / superfici
SURFACE_2 = "#F7F9FD"   # superficie tenue (campi, log)
ROW_HOVER = "#F1F5FD"   # riga in hover
ROW_SEL   = "#EAF1FE"   # riga selezionata
LINE      = "#E3E8F2"   # bordi sottili
LINE_2    = "#D5DCEA"   # bordi piu' marcati

# Brand / accenti
PRIMARY   = "#2C6BED"   # blu principale
PRIMARY_D = "#1E54C8"   # blu hover/active
PRIMARY_SOFT = "#E7EEFE"
NAVY_1    = "#16315E"   # gradiente header (scuro)
NAVY_2    = "#2C6BED"   # gradiente header (chiaro)

# Testo
TEXT      = "#1A2334"   # testo principale
MUTED     = "#69748A"   # testo secondario
ON_DARK   = "#FFFFFF"
ON_DARK_2 = "#C5D6F2"

# Stati
OK_GREEN  = "#1B8A4B"
OK_SOFT   = "#E4F4EA"
ERR_RED   = "#C0392B"
WARN_AMBER= "#B5651D"
WARN_SOFT = "#FBEDDD"

# Font adatti alla piattaforma (Windows: Segoe UI/Consolas, Mac: Helvetica/Menlo)
if sys.platform == "darwin":
    FONT, MONO = "Helvetica", "Menlo"
elif os.name == "nt":
    FONT, MONO = "Segoe UI", "Consolas"
else:
    FONT, MONO = "Helvetica", "DejaVu Sans Mono"


# ============================================================================
#  UTILITÀ COLORE / GRADIENTI
# ============================================================================
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _rgb_to_hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in c)

def _mix(c1, c2, t):
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


# ============================================================================
#  WIDGET: pulsante con angoli arrotondati + hover (Canvas)
# ============================================================================
class RoundButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, kind="primary",
                 width=200, height=44, radius=12, font=None, parent_bg=None):
        self._bg = parent_bg or parent.cget("bg")
        super().__init__(parent, width=width, height=height, bg=self._bg,
                         highlightthickness=0, bd=0, takefocus=0)
        self.command = command
        self.kind = kind
        self.radius = radius
        self.text = text
        self.w, self.h = width, height
        self.font = font or (FONT, 11, "bold")
        self._enabled = True
        self._state = "normal"
        self._palette()
        self.bind("<Enter>", lambda e: self._set("hover"))
        self.bind("<Leave>", lambda e: self._set("normal"))
        self.bind("<ButtonPress-1>", lambda e: self._set("active"))
        self.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _palette(self):
        if self.kind == "primary":
            self.col = {"normal": (PRIMARY, ON_DARK, None),
                        "hover":  (PRIMARY_D, ON_DARK, None),
                        "active": (PRIMARY_D, ON_DARK, None),
                        "disabled": ("#A9BEE8", "#EEF3FC", None)}
        else:  # ghost
            self.col = {"normal": (SURFACE, PRIMARY, LINE_2),
                        "hover":  (PRIMARY_SOFT, PRIMARY_D, PRIMARY),
                        "active": (PRIMARY_SOFT, PRIMARY_D, PRIMARY),
                        "disabled": (SURFACE, "#AEB7C6", LINE)}

    def _rounded(self, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def _set(self, state):
        if not self._enabled:
            return
        self._state = state
        self._draw()

    def _release(self, _e):
        inside = (0 <= self.winfo_pointerx() - self.winfo_rootx() <= self.w and
                  0 <= self.winfo_pointery() - self.winfo_rooty() <= self.h)
        self._set("hover" if inside else "normal")
        if self._enabled and inside and self.command:
            self.command()

    def set_enabled(self, on):
        self._enabled = on
        self.configure(cursor="hand2" if on else "arrow")
        self._state = "normal" if on else "disabled"
        self._draw()

    def _draw(self):
        self.delete("all")
        state = self._state if self._enabled else "disabled"
        fill, fg, border = self.col[state]
        pad = 1
        if border:
            self._rounded(pad, pad, self.w - pad, self.h - pad, self.radius,
                          fill=fill, outline=border, width=1)
        else:
            self._rounded(pad, pad, self.w - pad, self.h - pad, self.radius,
                          fill=fill, outline=fill)
        self.create_text(self.w / 2, self.h / 2 + 1, text=self.text,
                         fill=fg, font=self.font)


# ============================================================================
#  WIDGET: segmented control (scelta formato)
# ============================================================================
class Segmented(tk.Frame):
    def __init__(self, parent, options, variable, bg=SURFACE, command=None):
        super().__init__(parent, bg="#E6ECF7", bd=0,
                         highlightbackground=LINE, highlightthickness=1)
        self.var = variable
        self.command = command
        self.options = options
        self.cells = {}
        for label, value in options:
            cell = tk.Label(self, text=label, bg="#E6ECF7", fg=MUTED,
                            font=(FONT, 10, "bold"), padx=16, pady=7, cursor="hand2")
            cell.pack(side="left", padx=3, pady=3)
            cell.bind("<Button-1>", lambda e, v=value: self._select(v))
            cell.bind("<Enter>", lambda e, c=cell, v=value: self._hover(c, v, True))
            cell.bind("<Leave>", lambda e, c=cell, v=value: self._hover(c, v, False))
            self.cells[value] = cell
        self._restyle()

    def _hover(self, cell, value, on):
        if self.var.get() == value:
            return
        cell.configure(fg=PRIMARY if on else MUTED)

    def _select(self, value):
        self.var.set(value)
        self._restyle()
        if self.command:
            self.command(value)

    def _restyle(self):
        for value, cell in self.cells.items():
            if self.var.get() == value:
                cell.configure(bg=SURFACE, fg=PRIMARY)
            else:
                cell.configure(bg="#E6ECF7", fg=MUTED)


# ============================================================================
#  WIDGET: riga query (checkbox custom + pill)
# ============================================================================
class QueryRow(tk.Frame):
    def __init__(self, parent, query, index):
        self.bg = SURFACE
        super().__init__(parent, bg=self.bg, cursor="hand2")
        self.var = tk.BooleanVar(value=False)
        self.query = query
        self._widgets = []

        # barra accento (sinistra) visibile solo se selezionata
        self.accent = tk.Frame(self, bg=self.bg, width=3)
        self.accent.pack(side="left", fill="y")

        # checkbox disegnata
        self.box = tk.Canvas(self, width=22, height=22, bg=self.bg,
                             highlightthickness=0, bd=0)
        self.box.pack(side="left", padx=(14, 10), pady=12)

        # nome
        nome = query.get("nome", "(senza nome)")
        self.name = tk.Label(self, text=nome, bg=self.bg, fg=TEXT,
                             font=(FONT, 12), anchor="w", justify="left")
        self.name.pack(side="left", fill="x", expand=True, pady=12)
        self._widgets.append(self.name)

        # pill tipo (COEWEB / SDMX)
        is_post = bool(query.get("filtri"))
        tipo = "COEWEB" if is_post else "SDMX"
        p_bg = WARN_SOFT if is_post else PRIMARY_SOFT
        p_fg = WARN_AMBER if is_post else PRIMARY
        pill = tk.Label(self, text=f"  {tipo}  ", bg=p_bg, fg=p_fg,
                        font=(FONT, 8, "bold"), padx=2, pady=3)
        pill.pack(side="right", padx=(0, 14))

        # layout label
        lay = query.get("layout", "long")
        self.lay = tk.Label(self, text=lay, bg=self.bg, fg=MUTED,
                            font=(FONT, 9))
        self.lay.pack(side="right", padx=(0, 12))
        self._widgets.append(self.lay)

        # binding su tutta la riga
        for w in (self, self.name, self.lay, self.box):
            w.bind("<Button-1>", self._toggle)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

        self._draw_box()

    def _draw_box(self):
        self.box.delete("all")
        checked = self.var.get()
        x1, y1, x2, y2, r = 2, 2, 20, 20, 6
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        if checked:
            self.box.create_polygon(pts, smooth=True, fill=PRIMARY, outline=PRIMARY)
            self.box.create_line(6, 11, 10, 15, 16, 7, fill="white", width=2,
                                 capstyle="round", joinstyle="round")
        else:
            self.box.create_polygon(pts, smooth=True, fill=SURFACE, outline=LINE_2,
                                    width=1.5)

    def _recolor(self, bg):
        self.bg = bg
        self.configure(bg=bg)
        self.box.configure(bg=bg)
        for w in self._widgets:
            w.configure(bg=bg)

    def _toggle(self, _e=None):
        self.var.set(not self.var.get())
        self._draw_box()
        self._apply_state()

    def _apply_state(self):
        if self.var.get():
            self._recolor(ROW_SEL)
            self.accent.configure(bg=PRIMARY)
            self.name.configure(fg=TEXT, font=(FONT, 12, "bold"))
        else:
            self._recolor(SURFACE)
            self.accent.configure(bg=SURFACE)
            self.name.configure(fg=TEXT, font=(FONT, 12))

    def _enter(self, _e=None):
        if not self.var.get():
            self._recolor(ROW_HOVER)

    def _leave(self, _e=None):
        if not self.var.get():
            self._recolor(SURFACE)

    def set(self, value):
        self.var.set(value)
        self._draw_box()
        self._apply_state()


# ============================================================================
#  APPLICAZIONE
# ============================================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Estrattore SDMX ISTAT")
        root.geometry("880x790")
        root.minsize(780, 660)
        root.configure(bg=BG)
        self.queries = []
        self.rows = []          # istanze QueryRow
        self.msgq = queue.Queue()
        self.layout = tk.StringVar(value="config")
        anno = _dt.date.today().year
        self.period_mode = tk.StringVar(value="auto")
        self.da_anno = tk.StringVar(value=str(anno - 1))
        self.da_trim = tk.StringVar(value="T1")
        self.a_anno = tk.StringVar(value=str(anno))
        self.a_trim = tk.StringVar(value="T4")
        # report import/export: di default l'ultimo trimestre concluso
        oggi = _dt.date.today()
        ult = (oggi.month - 1) // 3
        self.rep_anno = tk.StringVar(value=str(anno if ult else anno - 1))
        self.rep_trim = tk.StringVar(value=f"T{ult or 4}")
        self.outdir = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads", "SDMX_ISTAT"))
        self._setup_style()
        self._build()
        # messaggi di attesa/avanzamento dal modulo core (thread-safe via coda)
        core.PROGRESSO = lambda t: self.msgq.put(("log", (f"      ⏳ {t}", "muted")))
        self.root.after(120, self._poll)
        self._load_queries()

    # ------------------------------------------------------------------ stile
    def _setup_style(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except Exception:
            pass
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=SURFACE)
        st.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 11))
        st.configure("Section.TLabel", background=BG, foreground=MUTED,
                     font=(FONT, 10, "bold"))
        st.configure("Vertical.TScrollbar", background="#C4CEDF", troughcolor=BG,
                     borderwidth=0, arrowsize=12, relief="flat")
        st.map("Vertical.TScrollbar", background=[("active", "#A9B6CC")])
        st.configure("Periodo.TCombobox", fieldbackground=SURFACE_2,
                     background=SURFACE, bordercolor=LINE_2, lightcolor=SURFACE_2,
                     darkcolor=SURFACE_2, arrowcolor=MUTED, padding=4)
        st.map("Periodo.TCombobox",
               fieldbackground=[("readonly", SURFACE_2)],
               foreground=[("readonly", TEXT)],
               selectbackground=[("readonly", SURFACE_2)],
               selectforeground=[("readonly", TEXT)])

    # --------------------------------------------------------------- gradiente
    def _draw_header(self, _e=None):
        c = self.header
        w = c.winfo_width() or 880
        h = int(c["height"])
        c.delete("grad")
        r1, r2 = _hex_to_rgb(NAVY_1), _hex_to_rgb(NAVY_2)
        steps = max(1, w)
        for x in range(steps):
            t = x / steps
            col = _rgb_to_hex(_mix(r1, r2, t))
            c.create_line(x, 0, x, h, fill=col, tags="grad")
        c.tag_lower("grad")

    # ------------------------------------------------------------------ layout
    def _build(self):
        # ===== HEADER (gradiente disegnato) =====
        self.header = tk.Canvas(self.root, height=84, highlightthickness=0, bd=0)
        self.header.pack(fill="x", side="top")
        self.header.bind("<Configure>", self._draw_header)

        # badge logo
        self.header.create_oval(22, 22, 62, 62, fill="#FFFFFF", outline="")
        self.header.create_text(42, 43, text="\U0001F4CA", font=(FONT, 20))
        # titolo + sottotitolo
        self.header.create_text(78, 32, anchor="w", text="Estrattore SDMX ISTAT",
                                fill=ON_DARK, font=(FONT, 19, "bold"))
        self.header.create_text(80, 58, anchor="w",
                                text="Scarica i dati ISTAT sempre aggiornati e salvali in Excel",
                                fill=ON_DARK_2, font=(FONT, 10))
        # status (a destra, aggiornato dinamicamente)
        self.status_id = self.header.create_text(0, 43, anchor="e", text="",
                                                  fill=ON_DARK_2, font=(FONT, 10))
        self.header.bind("<Configure>", self._reposition_status, add="+")

        # ===== CORPO =====
        body = ttk.Frame(self.root, style="TFrame")
        body.pack(fill="both", expand=True, padx=22, pady=(16, 8))

        # --- intestazione sezione lista ---
        head = tk.Frame(body, bg=BG)
        head.pack(fill="x", pady=(0, 6))
        tk.Label(head, text="LE TUE QUERY", bg=BG, fg=MUTED,
                 font=(FONT, 10, "bold")).pack(side="left")
        self.count_pill = tk.Label(head, text="", bg=PRIMARY_SOFT, fg=PRIMARY,
                                   font=(FONT, 9, "bold"), padx=8, pady=1)
        self.count_pill.pack(side="left", padx=8)
        # azioni selezione a destra
        RoundButton(head, text="↻  Ricarica", command=self._load_queries,
                    kind="ghost", width=110, height=32, radius=9,
                    font=(FONT, 10, "bold"), parent_bg=BG).pack(side="right")
        RoundButton(head, text="Deseleziona", command=lambda: self._set_all(False),
                    kind="ghost", width=104, height=32, radius=9,
                    font=(FONT, 10, "bold"), parent_bg=BG).pack(side="right", padx=8)
        RoundButton(head, text="Seleziona tutte", command=lambda: self._set_all(True),
                    kind="ghost", width=126, height=32, radius=9,
                    font=(FONT, 10, "bold"), parent_bg=BG).pack(side="right")

        # --- card lista scrollabile ---
        listcard = tk.Frame(body, bg=SURFACE, highlightbackground=LINE,
                            highlightthickness=1, bd=0)
        listcard.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(listcard, bg=SURFACE, highlightthickness=0)
        sb = ttk.Scrollbar(listcard, orient="vertical", command=self.canvas.yview,
                          style="Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.inner = tk.Frame(self.canvas, bg=SURFACE)
        self.iid = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.iid, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        # ===== CARD OPZIONI =====
        opt = tk.Frame(body, bg=SURFACE, highlightbackground=LINE, highlightthickness=1)
        opt.pack(fill="x", pady=(14, 0))

        r1 = tk.Frame(opt, bg=SURFACE)
        r1.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(r1, text="FORMATO", bg=SURFACE, fg=MUTED, font=(FONT, 9, "bold"),
                 width=9, anchor="w").pack(side="left")
        Segmented(r1, [("Come da query", "config"), ("Matrice (ISTAT)", "istat"),
                       ("Tabella lunga", "long")], self.layout).pack(side="left")

        tk.Frame(opt, bg=LINE, height=1).pack(fill="x", padx=16)

        # --- riga PERIODO: anno/trimestre di inizio e fine download ---
        rp = tk.Frame(opt, bg=SURFACE)
        rp.pack(fill="x", padx=16, pady=(8, 0))
        tk.Label(rp, text="PERIODO", bg=SURFACE, fg=MUTED, font=(FONT, 9, "bold"),
                 width=9, anchor="w").pack(side="left")
        Segmented(rp, [("Più recenti", "auto"), ("Personalizzato", "custom"),
                       ("Come da query", "query")], self.period_mode,
                  command=lambda _v: self._period_ui()).pack(side="left")

        detail = tk.Frame(opt, bg=SURFACE)
        detail.pack(fill="x", padx=16, pady=(4, 8))
        tk.Label(detail, text="", bg=SURFACE, width=9, font=(FONT, 9, "bold"),
                 anchor="w").pack(side="left")           # rientro sotto l'etichetta
        self.period_hint = tk.Label(detail, text="", bg=SURFACE, fg=MUTED,
                                    font=(FONT, 9), anchor="w", justify="left")
        self.period_pick = tk.Frame(detail, bg=SURFACE)
        anni = [str(v) for v in range(_dt.date.today().year + 1, 1998, -1)]
        trims = ["T1", "T2", "T3", "T4"]

        def _combo(var, values, w):
            return ttk.Combobox(self.period_pick, textvariable=var, values=values,
                                width=w, state="readonly", font=(FONT, 10),
                                style="Periodo.TCombobox")

        tk.Label(self.period_pick, text="Da", bg=SURFACE, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left")
        _combo(self.da_anno, anni, 6).pack(side="left", padx=(8, 4))
        _combo(self.da_trim, trims, 4).pack(side="left")
        tk.Label(self.period_pick, text="a", bg=SURFACE, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left", padx=(14, 0))
        _combo(self.a_anno, anni, 6).pack(side="left", padx=(8, 4))
        _combo(self.a_trim, trims, 4).pack(side="left")
        tk.Label(self.period_pick, text="(anno e trimestre di inizio e fine)",
                 bg=SURFACE, fg=MUTED, font=(FONT, 9)).pack(side="left", padx=(12, 0))
        self._period_ui()

        # --- riga REPORT: tabelle import/export per anno e trimestre (cumulati) ---
        tk.Frame(opt, bg=LINE, height=1).pack(fill="x", padx=16)
        rr = tk.Frame(opt, bg=SURFACE)
        rr.pack(fill="x", padx=16, pady=(8, 8))
        tk.Label(rr, text="REPORT", bg=SURFACE, fg=MUTED, font=(FONT, 9, "bold"),
                 width=9, anchor="w").pack(side="left")
        tk.Label(rr, text="Import/Export", bg=SURFACE, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left")
        ttk.Combobox(rr, textvariable=self.rep_anno, values=anni, width=6, state="readonly",
                     font=(FONT, 10), style="Periodo.TCombobox").pack(side="left", padx=(8, 4))
        ttk.Combobox(rr, textvariable=self.rep_trim, values=trims, width=4, state="readonly",
                     font=(FONT, 10), style="Periodo.TCombobox").pack(side="left")
        tk.Label(rr, text="(valori cumulati da T1)", bg=SURFACE, fg=MUTED,
                 font=(FONT, 9)).pack(side="left", padx=(12, 0))
        self.btn_report = RoundButton(rr, text="📑  Genera report", command=self._start_report,
                                      kind="ghost", width=160, height=36, radius=10,
                                      font=(FONT, 10, "bold"), parent_bg=SURFACE)
        self.btn_report.pack(side="right")

        sep = tk.Frame(opt, bg=LINE, height=1)
        sep.pack(fill="x", padx=16)

        r2 = tk.Frame(opt, bg=SURFACE)
        r2.pack(fill="x", padx=16, pady=(8, 14))
        tk.Label(r2, text="CARTELLA", bg=SURFACE, fg=MUTED, font=(FONT, 9, "bold"),
                 width=9, anchor="w").pack(side="left")
        entwrap = tk.Frame(r2, bg=SURFACE_2, highlightbackground=LINE_2,
                          highlightthickness=1)
        entwrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ent = tk.Entry(entwrap, textvariable=self.outdir, font=(FONT, 10),
                       relief="flat", bg=SURFACE_2, fg=TEXT, bd=0,
                       highlightthickness=0, insertbackground=TEXT)
        ent.pack(side="left", fill="x", expand=True, padx=10, ipady=7)
        RoundButton(r2, text="Sfoglia…", command=self._choose, kind="ghost",
                    width=96, height=36, radius=10, font=(FONT, 10, "bold"),
                    parent_bg=SURFACE).pack(side="left")

        # ===== BARRA AZIONE =====
        action = tk.Frame(body, bg=BG)
        action.pack(fill="x", pady=(14, 2))
        self.hint = tk.Label(action, text="Spunta le query e premi Aggiorna",
                             bg=BG, fg=MUTED, font=(FONT, 10))
        self.hint.pack(side="left")
        self.btn = RoundButton(action, text="⬇  Aggiorna selezionate",
                               command=self._start, kind="primary",
                               width=232, height=46, radius=13,
                               font=(FONT, 12, "bold"), parent_bg=BG)
        self.btn.pack(side="right")
        self.btn_cancel = RoundButton(action, text="✕  Annulla",
                                      command=self._annulla, kind="ghost",
                                      width=110, height=46, radius=13,
                                      font=(FONT, 11, "bold"), parent_bg=BG)
        self.btn_cancel.pack(side="right", padx=(0, 10))
        self.btn_cancel.set_enabled(False)

        # ===== LOG =====
        loghead = tk.Frame(body, bg=BG)
        loghead.pack(fill="x", pady=(14, 4))
        tk.Label(loghead, text="STATO", bg=BG, fg=MUTED,
                 font=(FONT, 10, "bold")).pack(side="left")
        logcard = tk.Frame(body, bg=SURFACE, highlightbackground=LINE, highlightthickness=1)
        logcard.pack(fill="x")
        self.log = tk.Text(logcard, height=7, wrap="word", state="disabled",
                           relief="flat", bg=SURFACE_2, fg=TEXT, font=(MONO, 10),
                           padx=12, pady=10, highlightthickness=0,
                           selectbackground=PRIMARY_SOFT)
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("ok", foreground=OK_GREEN)
        self.log.tag_configure("err", foreground=ERR_RED)
        self.log.tag_configure("muted", foreground=MUTED)
        self._log("Pronto.  Le tue query salvate sono elencate qui sopra.", "muted")

    # ------------------------------------------------------------------ helpers
    def _reposition_status(self, _e=None):
        w = self.header.winfo_width() or 880
        self.header.coords(self.status_id, w - 22, 43)

    def _set_status(self, text):
        self.header.itemconfigure(self.status_id, text=text)

    def _log(self, t, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", t + "\n", (tag,) if tag else ())
        self.log.see("end")
        self.log.configure(state="disabled")

    def _busy(self, b):
        self.btn.set_enabled(not b)
        self.btn.text = "⏳  Aggiornamento…" if b else "⬇  Aggiorna selezionate"
        self.btn._draw()
        self.btn_report.set_enabled(not b)
        self.btn_cancel.set_enabled(b)

    def _annulla(self):
        core.CANCELLA.set()
        self.btn_cancel.set_enabled(False)
        self._log("⏹  Annullamento richiesto: mi fermo appena possibile…", "muted")

    def _on_wheel(self, e):
        # macOS: delta gia' in "righe" (±1..3); Windows: multipli di ±120
        step = -int(e.delta) if sys.platform == "darwin" else -int(e.delta / 120)
        if step:
            self.canvas.yview_scroll(step, "units")

    def _choose(self):
        d = filedialog.askdirectory(initialdir=self.outdir.get() or os.path.expanduser("~"))
        if d:
            self.outdir.set(d)

    def _set_all(self, v):
        for row in self.rows:
            row.set(v)

    # ------------------------------------------------------------------ periodo
    def _period_ui(self):
        """Mostra i selettori Da/A solo in modalita' Personalizzato."""
        m = self.period_mode.get()
        self.period_hint.pack_forget()
        self.period_pick.pack_forget()
        if m == "custom":
            self.period_pick.pack(side="left")
        else:
            self.period_hint.configure(
                text="Scarica i dati più recenti disponibili e tutti i trimestri "
                     "dell'anno precedente." if m == "auto"
                else "Usa il periodo salvato dentro ogni query.")
            self.period_hint.pack(side="left")

    def _periodo_scelto(self):
        """Legge la scelta periodo dalla GUI. None = scelta non valida."""
        m = self.period_mode.get()
        if m in ("auto", "query"):
            return {"mode": m}
        da = (int(self.da_anno.get()), int(self.da_trim.get()[1]))
        a = (int(self.a_anno.get()), int(self.a_trim.get()[1]))
        if da > a:
            messagebox.showwarning(
                "Periodo non valido",
                "L'inizio del periodo viene dopo la fine: correggi anni/trimestri.")
            return None
        return {"mode": "custom", "da": da, "a": a}

    # ------------------------------------------------------------------ lista query
    def _load_queries(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.rows = []
        try:
            import importlib, query_salvate
            importlib.reload(query_salvate)
            self.queries = list(getattr(query_salvate, "QUERY", []))
        except Exception as exc:
            self.queries = []
            self._log(f"ERRORE leggendo query_salvate.py: {exc}", "err")
        for i, q in enumerate(self.queries):
            row = QueryRow(self.inner, q, i)
            row.pack(fill="x")
            self.rows.append(row)
            sep = tk.Frame(self.inner, bg=LINE, height=1)
            sep.pack(fill="x", padx=14)
        n = len(self.queries)
        self.count_pill.configure(text=f"{n}")
        self._set_status(f"{n} query salvate" if n else "nessuna query")
        if not n:
            empty = tk.Label(self.inner, bg=SURFACE, fg=MUTED, justify="center",
                             font=(FONT, 11),
                             text="\n\U0001F4ED  Nessuna query in query_salvate.py.\n\n"
                                  "Apri il file e incolla le tue query, poi premi ↻ Ricarica.\n")
            empty.pack(anchor="center", padx=16, pady=30)

    # ------------------------------------------------------------------ esecuzione
    def _start(self):
        sel = [row.query for row in self.rows if row.var.get()]
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Spunta almeno una query.")
            return
        outdir = self.outdir.get().strip() or os.path.join(
            os.path.expanduser("~"), "Downloads", "SDMX_ISTAT")
        lay = None if self.layout.get() == "config" else self.layout.get()
        periodo = self._periodo_scelto()
        if periodo is None:
            return
        if periodo["mode"] == "auto":
            descr = "periodo: più recenti + tutto l'anno precedente"
        elif periodo["mode"] == "custom":
            descr = (f"periodo: {periodo['da'][0]}-T{periodo['da'][1]}"
                     f" → {periodo['a'][0]}-T{periodo['a'][1]}")
        else:
            descr = "periodo: come da query"
        self._busy(True)
        core.CANCELLA.clear()
        self._log(f"▶  Aggiorno {len(sel)} query…  ({descr})", "muted")
        threading.Thread(target=self._worker, args=(sel, outdir, lay, periodo),
                         daemon=True).start()

    def _worker(self, sel, outdir, lay, periodo):
        created, interrotto = [], False
        for n, q in enumerate(sel, start=1):
            if core.CANCELLA.is_set():
                interrotto = True
                break
            self.msgq.put(("log", (f"[{n}/{len(sel)}] {q.get('nome')} …", None)))
            try:
                path = core.esegui_query(q, layout=lay, outdir=outdir, periodo=periodo)
                created.append(path)
                self.msgq.put(("log", (f"      ✓ {os.path.basename(path)}", "ok")))
            except core.SdmxError as exc:
                if core.CANCELLA.is_set():
                    self.msgq.put(("log", ("      ⏹ annullata", "muted")))
                    interrotto = True
                    break
                self.msgq.put(("log", (f"      ✗ {exc}", "err")))
            except Exception as exc:
                self.msgq.put(("log", (f"      ✗ errore: {exc}", "err")))
        self.msgq.put(("done", (outdir, created, interrotto)))

    def _start_report(self):
        outdir = self.outdir.get().strip() or os.path.join(
            os.path.expanduser("~"), "Downloads", "SDMX_ISTAT")
        anno, trim = int(self.rep_anno.get()), int(self.rep_trim.get()[1])
        self._busy(True)
        core.CANCELLA.clear()
        self._log(f"▶  Report Import/Export {anno} T{trim} (cumulato T1-T{trim})…", "muted")
        threading.Thread(target=self._worker_report, args=(anno, trim, outdir),
                         daemon=True).start()

    def _worker_report(self, anno, trim, outdir):
        cartella, created, interrotto = outdir, [], False
        simboli = {"ok": ("✓", "ok"), "info": ("ℹ", "muted")}
        log = lambda t, tag=None: self.msgq.put(
            ("log", (f"      {simboli.get(tag, ('✗', 'err'))[0]} {t}", simboli.get(tag, ('✗', 'err'))[1])))
        try:
            cartella, created = report.genera_report(anno, trim, outdir, log=log)
        except core.SdmxError as exc:
            if core.CANCELLA.is_set():
                self.msgq.put(("log", ("      ⏹ annullato", "muted")))
                interrotto = True
            else:
                self.msgq.put(("log", (f"      ✗ {exc}", "err")))
        except Exception as exc:
            self.msgq.put(("log", (f"      ✗ errore: {exc}", "err")))
        self.msgq.put(("done", (cartella, created, interrotto)))

    def _poll(self):
        try:
            while True:
                k, p = self.msgq.get_nowait()
                if k == "log":
                    self._log(p[0], p[1])
                elif k == "done":
                    outdir, created, interrotto = p
                    self._busy(False)
                    if interrotto:
                        self._set_status(f"Interrotto: {len(created)} file")
                        self._log(f"⏹  Interrotto dall'utente: {len(created)} file creati in {outdir}",
                                  "muted")
                    else:
                        self._set_status(f"Fatto: {len(created)} file")
                        self._log(f"✔  Completato: {len(created)} file in {outdir}",
                                  "ok" if created else "err")
                        if created and messagebox.askyesno(
                                "Completato",
                                f"Creati {len(created)} file in:\n{outdir}\n\nAprire la cartella?"):
                            self._open(outdir)
        except queue.Empty:
            pass
        self.root.after(120, self._poll)

    @staticmethod
    def _open(path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception:
            webbrowser.open("file://" + path)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
