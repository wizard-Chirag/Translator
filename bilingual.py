"""
Bilingual Translator — English → Kannada / Hindi  (GUI Edition)
=================================================================
Dependencies:
    pip install deep-translator

Run:
    python bilingual_translator_gui.py
"""

import threading
import tkinter as tk
from tkinter import font as tkfont
from deep_translator import GoogleTranslator


# ── Palette ──────────────────────────────────────────────────────────────────
BG         = "#0F1117"
PANEL      = "#1A1D27"
BORDER     = "#2A2D3A"
TEXT_MAIN  = "#F0EDE6"
TEXT_DIM   = "#7A7D8E"
SUCCESS    = "#4CAF82"
ERROR_COL  = "#E8734A"

# Per-language accent colours
LANG_META = {
    "Kannada": {
        "code":    "kn",
        "accent":  "#F4A435",   # warm amber
        "accent2": "#E8734A",   # saffron
        "out_fg":  "#FFD580",   # golden output text
        "badge":   "ಕ",
        "label":   "ಕನ್ನಡ  (Kannada)",
        "hint":    "English  →  ಕನ್ನಡ",
    },
    "Hindi": {
        "code":    "hi",
        "accent":  "#2196F3",   # saffron-blue (tricolour nod)
        "accent2": "#1565C0",
        "out_fg":  "#90CAF9",   # light-blue output text
        "badge":   "ह",
        "label":   "हिन्दी  (Hindi)",
        "hint":    "English  →  हिन्दी",
    },
}

LANGUAGES = list(LANG_META.keys())


class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bilingual Translator  ·  EN → KN / HI")
        self.geometry("720x620")
        self.minsize(580, 520)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._translating = False
        self._lang_var = tk.StringVar(value=LANGUAGES[0])

        self._build_fonts()
        self._build_ui()
        self._apply_lang()          # paint initial accent colours

    # ── Fonts ─────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_title  = tkfont.Font(family="Georgia",           size=17, weight="bold")
        self.f_sub    = tkfont.Font(family="Georgia",           size=10, slant="italic")
        self.f_label  = tkfont.Font(family="Courier New",       size=9,  weight="bold")
        self.f_input  = tkfont.Font(family="Palatino Linotype", size=13)
        self.f_output = tkfont.Font(family="Palatino Linotype", size=14)
        self.f_btn    = tkfont.Font(family="Courier New",       size=11, weight="bold")
        self.f_status = tkfont.Font(family="Courier New",       size=9)
        self.f_toggle = tkfont.Font(family="Courier New",       size=10, weight="bold")

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, pady=16)
        hdr.pack(fill="x", padx=30)

        self.badge_lbl = tk.Label(
            hdr, text="", bg=BG, fg=BG,
            font=tkfont.Font(family="Georgia", size=20, weight="bold"),
            width=2, relief="flat", padx=6, pady=2
        )
        self.badge_lbl.pack(side="left")

        title_frame = tk.Frame(hdr, bg=BG)
        title_frame.pack(side="left", padx=12)
        tk.Label(title_frame, text="Bilingual Translator",
                 bg=BG, fg=TEXT_MAIN, font=self.f_title).pack(anchor="w")
        self.hint_lbl = tk.Label(title_frame, text="",
                                 bg=BG, fg=TEXT_DIM, font=self.f_sub)
        self.hint_lbl.pack(anchor="w")

        # ── Language toggle ───────────────────────────────────────────────────
        toggle_frame = tk.Frame(self, bg=BG)
        toggle_frame.pack(pady=(0, 4))

        tk.Label(toggle_frame, text="TRANSLATE TO :",
                 bg=BG, fg=TEXT_DIM, font=self.f_label).pack(side="left", padx=(0, 10))

        self.toggle_btns = {}
        for lang in LANGUAGES:
            btn = tk.Button(
                toggle_frame,
                text=LANG_META[lang]["label"],
                command=lambda l=lang: self._switch_lang(l),
                relief="flat", bd=0,
                font=self.f_toggle,
                padx=16, pady=7,
                cursor="hand2"
            )
            btn.pack(side="left", padx=4)
            self.toggle_btns[lang] = btn

        # thin divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30)

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=16)

        # INPUT
        self._make_label(body, "ENGLISH INPUT")
        self.in_card_outer = tk.Frame(body, bg=BG, padx=1, pady=1)
        self.in_card_outer.pack(fill="both", expand=True, pady=(0, 4))
        in_inner = tk.Frame(self.in_card_outer, bg=PANEL)
        in_inner.pack(fill="both", expand=True)

        self.input_text = tk.Text(
            in_inner, height=5, wrap="word",
            bg=PANEL, fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            selectbackground=BORDER, selectforeground=TEXT_MAIN,
            relief="flat", bd=0,
            font=self.f_input, padx=12, pady=10
        )
        self.input_text.pack(fill="both", expand=True)
        self.input_text.bind("<Control-Return>", lambda e: self._translate())
        self.input_text.bind("<KeyRelease>", self._update_counter)

        counter_row = tk.Frame(body, bg=BG)
        counter_row.pack(fill="x", pady=(2, 0))
        self.char_count = tk.Label(counter_row, text="0 characters",
                                   bg=BG, fg=TEXT_DIM, font=self.f_status, anchor="e")
        self.char_count.pack(side="right")

        # ── Translate / Clear buttons ─────────────────────────────────────────
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(pady=12)

        self.translate_btn = tk.Button(
            btn_row,
            text="  ⟶  TRANSLATE  ⟶  ",
            command=self._translate,
            fg=BG, activeforeground=BG,
            font=self.f_btn,
            relief="flat", bd=0,
            padx=20, pady=9,
            cursor="hand2"
        )
        self.translate_btn.pack(side="left")

        self.clear_btn = tk.Button(
            btn_row,
            text="✕  CLEAR",
            command=self._clear,
            bg=PANEL, fg=TEXT_DIM,
            activebackground=BORDER, activeforeground=TEXT_MAIN,
            font=self.f_status,
            relief="flat", bd=0,
            padx=14, pady=9,
            cursor="hand2"
        )
        self.clear_btn.pack(side="left", padx=(10, 0))

        # OUTPUT
        self.out_label = tk.Label(body, text="",
                                  bg=BG, fg=TEXT_DIM,
                                  font=self.f_label, anchor="w", pady=4)
        self.out_label.pack(fill="x")

        self.out_card_outer = tk.Frame(body, bg=BG, padx=1, pady=1)
        self.out_card_outer.pack(fill="both", expand=True, pady=(0, 4))
        out_inner = tk.Frame(self.out_card_outer, bg="#111520")
        out_inner.pack(fill="both", expand=True)

        self.output_text = tk.Text(
            out_inner, height=5, wrap="word",
            bg="#111520", fg=TEXT_DIM,
            insertbackground=TEXT_MAIN,
            relief="flat", bd=0,
            font=self.f_output, padx=12, pady=10,
            state="disabled"
        )
        self.output_text.pack(fill="both", expand=True)

        copy_row = tk.Frame(body, bg=BG)
        copy_row.pack(fill="x", pady=(2, 0))
        self.copy_btn = tk.Button(
            copy_row, text="⧉  COPY",
            command=self._copy_output,
            bg=PANEL, fg=TEXT_DIM,
            activebackground=BORDER, activeforeground=TEXT_MAIN,
            font=self.f_status,
            relief="flat", bd=0,
            padx=10, pady=4, cursor="hand2"
        )
        self.copy_btn.pack(side="right")

        # ── Status bar ────────────────────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self.status = tk.Label(
            self,
            text="  Ready  ·  Press Ctrl+Enter or click Translate",
            bg=BG, fg=TEXT_DIM,
            font=self.f_status, anchor="w", padx=30, pady=6
        )
        self.status.pack(fill="x")

    # ── Language switching ────────────────────────────────────────────────────
    def _switch_lang(self, lang):
        self._lang_var.set(lang)
        self._apply_lang()
        self._write_output("")          # clear stale output on switch
        self._set_status(f"Mode switched to English → {lang}")

    def _apply_lang(self):
        lang  = self._lang_var.get()
        meta  = LANG_META[lang]
        acc   = meta["accent"]
        acc2  = meta["accent2"]
        out_c = meta["out_fg"]

        # badge
        self.badge_lbl.config(text=meta["badge"], bg=acc, fg=BG)
        # subtitle
        self.hint_lbl.config(text=meta["hint"])
        # output label
        self.out_label.config(text=f"{lang.upper()} OUTPUT")
        # card borders
        self.in_card_outer.config(bg=acc)
        self.out_card_outer.config(bg=acc)
        # output text colour
        self.output_text.config(fg=out_c)
        # translate button
        self.translate_btn.config(
            bg=acc, activebackground=acc2
        )
        # input cursor colour
        self.input_text.config(insertbackground=acc)
        # toggle buttons — highlight active, dim inactive
        for l, btn in self.toggle_btns.items():
            if l == lang:
                btn.config(bg=acc, fg=BG,
                           activebackground=acc2, activeforeground=BG)
            else:
                btn.config(bg=PANEL, fg=TEXT_DIM,
                           activebackground=BORDER, activeforeground=TEXT_MAIN)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _make_label(self, parent, text):
        tk.Label(parent, text=text,
                 bg=BG, fg=TEXT_DIM,
                 font=self.f_label, anchor="w", pady=4).pack(fill="x")

    def _update_counter(self, _=None):
        n = len(self.input_text.get("1.0", "end-1c"))
        self.char_count.config(text=f"{n} character{'s' if n != 1 else ''}")

    # ── Translation logic ─────────────────────────────────────────────────────
    def _translate(self):
        if self._translating:
            return
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            self._set_status("⚠  Please enter some English text first.", error=True)
            return

        lang = self._lang_var.get()
        code = LANG_META[lang]["code"]

        self._translating = True
        acc = LANG_META[lang]["accent"]
        self.translate_btn.config(text="  … TRANSLATING …  ",
                                  state="disabled", bg=BORDER)
        self._set_status(f"Translating to {lang} …")
        threading.Thread(
            target=self._do_translate,
            args=(text, code, lang),
            daemon=True
        ).start()

    def _do_translate(self, text, code, lang):
        try:
            result = GoogleTranslator(source="en", target=code).translate(text)
            self.after(0, self._show_result, result, lang)
        except Exception as e:
            self.after(0, self._show_error, str(e), lang)

    def _show_result(self, result, lang):
        self._write_output(result)
        self._set_status(
            f"✓  Translated to {lang}  ·  {len(result)} characters", ok=True)
        self._reset_btn()
        self._translating = False

    def _show_error(self, msg, lang):
        self._write_output(f"[Error] {msg}")
        self._set_status(f"✗  {msg}", error=True)
        self._reset_btn()
        self._translating = False

    def _write_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", text)
        self.output_text.config(state="disabled")

    def _reset_btn(self):
        lang = self._lang_var.get()
        acc  = LANG_META[lang]["accent"]
        self.translate_btn.config(
            text="  ⟶  TRANSLATE  ⟶  ", state="normal", bg=acc)

    def _clear(self):
        self.input_text.delete("1.0", "end")
        self._write_output("")
        self.char_count.config(text="0 characters")
        self._set_status("Cleared.")

    def _copy_output(self):
        out = self.output_text.get("1.0", "end-1c").strip()
        if out:
            self.clipboard_clear()
            self.clipboard_append(out)
            self._set_status("✓  Copied to clipboard!", ok=True)

    def _set_status(self, msg, error=False, ok=False):
        colour = ERROR_COL if error else (SUCCESS if ok else TEXT_DIM)
        self.status.config(text=f"  {msg}", fg=colour)


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()