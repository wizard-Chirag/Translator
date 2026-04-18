"""
English → Kannada Translator — GUI Edition
============================================
Dependencies:
    pip install deep-translator

Run:
    python kannada_translator_gui.py
"""

import threading
import tkinter as tk
from tkinter import font as tkfont
from deep_translator import GoogleTranslator


# ── Colour palette ──────────────────────────────────────────────────────────
BG          = "#0F1117"   # near-black background
PANEL       = "#1A1D27"   # card surface
BORDER      = "#2A2D3A"   # subtle border
ACCENT      = "#F4A435"   # warm amber — Karnataka / Kannada cultural tone
ACCENT2     = "#E8734A"   # deep saffron secondary
TEXT_MAIN   = "#F0EDE6"   # warm off-white
TEXT_DIM    = "#7A7D8E"   # muted labels
TEXT_OUT    = "#FFD580"   # output text — golden
BTN_HOVER   = "#E8923A"
SUCCESS     = "#4CAF82"


class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ಕನ್ನಡ  ·  Kannada Translator")
        self.geometry("700x560")
        self.minsize(560, 480)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._build_fonts()
        self._build_ui()
        self._translating = False

    # ── Fonts ────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_title   = tkfont.Font(family="Georgia",        size=18, weight="bold")
        self.f_sub     = tkfont.Font(family="Georgia",        size=10, slant="italic")
        self.f_label   = tkfont.Font(family="Courier New",    size=9,  weight="bold")
        self.f_input   = tkfont.Font(family="Palatino Linotype", size=13)
        self.f_output  = tkfont.Font(family="Palatino Linotype", size=14)
        self.f_btn     = tkfont.Font(family="Courier New",    size=11, weight="bold")
        self.f_status  = tkfont.Font(family="Courier New",    size=9)

    # ── UI layout ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, pady=18)
        hdr.pack(fill="x", padx=30)

        badge = tk.Label(hdr, text="ಕ", bg=ACCENT, fg=BG,
                         font=tkfont.Font(family="Georgia", size=20, weight="bold"),
                         width=2, relief="flat", padx=6, pady=2)
        badge.pack(side="left")

        title_frame = tk.Frame(hdr, bg=BG)
        title_frame.pack(side="left", padx=12)
        tk.Label(title_frame, text="Kannada Translator",
                 bg=BG, fg=TEXT_MAIN, font=self.f_title).pack(anchor="w")
        tk.Label(title_frame, text="English  →  ಕನ್ನಡ",
                 bg=BG, fg=TEXT_DIM, font=self.f_sub).pack(anchor="w")

        # thin divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30)

        # ── Body ─────────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=20)

        # INPUT card
        self._make_label(body, "ENGLISH INPUT")
        in_card = self._make_card(body)
        self.input_text = tk.Text(
            in_card, height=5, wrap="word",
            bg=PANEL, fg=TEXT_MAIN,
            insertbackground=ACCENT,
            selectbackground=ACCENT2, selectforeground=BG,
            relief="flat", bd=0,
            font=self.f_input,
            padx=12, pady=10
        )
        self.input_text.pack(fill="both", expand=True)
        self.input_text.bind("<Control-Return>", lambda e: self._translate())

        # char counter
        counter_row = tk.Frame(body, bg=BG)
        counter_row.pack(fill="x", pady=(2, 0))
        self.char_count = tk.Label(counter_row, text="0 characters",
                                   bg=BG, fg=TEXT_DIM, font=self.f_status, anchor="e")
        self.char_count.pack(side="right")
        self.input_text.bind("<KeyRelease>", self._update_counter)

        # ── Translate button ─────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(pady=14)

        self.btn = tk.Button(
            btn_row,
            text="  ⟶  TRANSLATE  ⟶  ",
            command=self._translate,
            bg=ACCENT, fg=BG,
            activebackground=BTN_HOVER, activeforeground=BG,
            font=self.f_btn,
            relief="flat", bd=0,
            padx=20, pady=9,
            cursor="hand2"
        )
        self.btn.pack(side="left")

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

        # ── OUTPUT card ───────────────────────────────────────────────────────
        self._make_label(body, "KANNADA OUTPUT")
        out_card = self._make_card(body)
        self.output_text = tk.Text(
            out_card, height=5, wrap="word",
            bg="#111520",
            fg=TEXT_OUT,
            insertbackground=ACCENT,
            selectbackground=ACCENT2, selectforeground=BG,
            relief="flat", bd=0,
            font=self.f_output,
            padx=12, pady=10,
            state="disabled"
        )
        self.output_text.pack(fill="both", expand=True)

        # Copy button (bottom-right of output card)
        copy_row = tk.Frame(body, bg=BG)
        copy_row.pack(fill="x", pady=(2, 0))
        self.copy_btn = tk.Button(
            copy_row, text="⧉  COPY",
            command=self._copy_output,
            bg=PANEL, fg=TEXT_DIM,
            activebackground=BORDER, activeforeground=TEXT_MAIN,
            font=self.f_status,
            relief="flat", bd=0,
            padx=10, pady=4,
            cursor="hand2"
        )
        self.copy_btn.pack(side="right")

        # ── Status bar ────────────────────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self.status = tk.Label(
            self, text="Ready  ·  Press Ctrl+Enter or click Translate",
            bg=BG, fg=TEXT_DIM,
            font=self.f_status, anchor="w", padx=30, pady=6
        )
        self.status.pack(fill="x")

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _make_label(self, parent, text):
        tk.Label(parent, text=text,
                 bg=BG, fg=TEXT_DIM,
                 font=self.f_label, anchor="w",
                 pady=4).pack(fill="x")

    def _make_card(self, parent):
        outer = tk.Frame(parent, bg=ACCENT, padx=1, pady=1)
        outer.pack(fill="both", expand=True, pady=(0, 4))
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill="both", expand=True)
        return inner

    # ── Actions ───────────────────────────────────────────────────────────────
    def _update_counter(self, _=None):
        n = len(self.input_text.get("1.0", "end-1c"))
        self.char_count.config(text=f"{n} character{'s' if n != 1 else ''}")

    def _translate(self):
        if self._translating:
            return
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            self._set_status("⚠  Please enter some English text first.", error=True)
            return

        self._translating = True
        self.btn.config(text="  … TRANSLATING …  ", state="disabled", bg=BORDER)
        self._set_status("Translating …")
        threading.Thread(target=self._do_translate, args=(text,), daemon=True).start()

    def _do_translate(self, text):
        try:
            result = GoogleTranslator(source="en", target="kn").translate(text)
            self.after(0, self._show_result, result)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_result(self, result):
        self._write_output(result)
        self._set_status(f"✓  Translation complete  ·  {len(result)} characters", ok=True)
        self._reset_btn()
        self._translating = False

    def _show_error(self, msg):
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
        self.btn.config(text="  ⟶  TRANSLATE  ⟶  ", state="normal", bg=ACCENT)

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
        colour = ACCENT2 if error else (SUCCESS if ok else TEXT_DIM)
        self.status.config(text=f"  {msg}", fg=colour)


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()