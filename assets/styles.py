import tkinter as tk

# ─── Color Palette ────────────────────────────────────────────────────────────
BG_MAIN        = "#FFF8F0"   # warm white – app background
BG_CARD        = "#FFFFFF"   # card / frame background
BG_SIDEBAR     = "#2D2D2D"   # dark sidebar
ACCENT         = "#FF6B35"   # orange – primary action color
ACCENT_HOVER   = "#E55A27"   # darker orange on hover
ACCENT_LIGHT   = "#FFE8DC"   # pale orange – highlights
TEXT_DARK      = "#1A1A1A"   # primary text
TEXT_MID       = "#555555"   # secondary text
TEXT_LIGHT     = "#AAAAAA"   # placeholder / disabled text
TEXT_WHITE     = "#FFFFFF"
SUCCESS        = "#4CAF50"
DANGER         = "#E53935"
BORDER         = "#E0D6CC"

# ─── Font Definitions ─────────────────────────────────────────────────────────
FONT_H1        = ("Segoe UI", 24, "bold")
FONT_H2        = ("Segoe UI", 18, "bold")
FONT_H3        = ("Segoe UI", 14, "bold")
FONT_BODY      = ("Segoe UI", 11)
FONT_SMALL     = ("Segoe UI", 9)
FONT_BTN       = ("Segoe UI", 11, "bold")
FONT_LABEL     = ("Segoe UI", 10)

# ─── Dimensions ───────────────────────────────────────────────────────────────
ENTRY_HEIGHT   = 38
BTN_HEIGHT     = 40
CORNER_RADIUS  = 8
PAD            = 20


# ─── Reusable Widget Helpers ──────────────────────────────────────────────────

def styled_button(parent, text, command, bg=ACCENT, fg=TEXT_WHITE,
                  width=20, font=FONT_BTN, pady=8):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, font=font,
        width=width, pady=pady,
        relief="flat", cursor="hand2",
        activebackground=ACCENT_HOVER, activeforeground=TEXT_WHITE,
        bd=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER if bg == ACCENT else bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def styled_entry(parent, show=None, width=30):
    import tkinter as tk
    frame = tk.Frame(parent, bg=BORDER, bd=1)
    entry = tk.Entry(
        frame, show=show, width=width,
        font=FONT_BODY, bg=BG_CARD, fg=TEXT_DARK,
        relief="flat", bd=6,
        insertbackground=TEXT_DARK
    )
    entry.pack(fill="x")
    return frame, entry


def card_frame(parent, **kwargs):
    defaults = dict(bg=BG_CARD, relief="flat", bd=0, padx=PAD, pady=PAD)
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def section_label(parent, text, font=FONT_H3, fg=TEXT_DARK):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=parent.cget("bg"))


def link_label(parent, text, command, fg=ACCENT, font=FONT_LABEL):
    lbl = tk.Label(parent, text=text, font=font, fg=fg,
                   bg=parent.cget("bg"), cursor="hand2")
    lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>", lambda e: lbl.config(font=(font[0], font[1], "underline")))
    lbl.bind("<Leave>", lambda e: lbl.config(font=font))
    return lbl

# ─── Compatibility dictionaries ─────────────────────────────────────────────

COLORS = {
    "bg_dark": BG_MAIN,
    "bg_card": BG_CARD,
    "sidebar": BG_SIDEBAR,
    "accent": ACCENT,
    "accent_hover": ACCENT_HOVER,
    "white": TEXT_WHITE,
    "text_primary": TEXT_DARK,
    "text_muted": TEXT_MID,
    "danger": DANGER,
    "success": SUCCESS,
    "warning": ACCENT,
    "border": BORDER
}

FONTS = {
    "brand": FONT_H1,
    "heading": FONT_H2,
    "subheading": FONT_H3,
    "body": FONT_BODY,
    "body_bold": FONT_BTN,
    "caption": FONT_SMALL,
    "stat_number": ("Segoe UI", 22, "bold")
}

def apply_button_style(button):
    button.config(
        relief="flat",
        cursor="hand2",
        bd=0
    )
