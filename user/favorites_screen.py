import tkinter as tk
from tkinter import messagebox
from assets.styles import *


class FavoritesScreen(tk.Frame):
    def __init__(self, parent, db, user):
        super().__init__(parent, bg=BG_MAIN)
        self.db = db
        self.user = user
        self._build_ui()

    def _build_ui(self):
        self._build_navbar()
        self._build_body()

    def _build_navbar(self):
        nav = tk.Frame(self, bg=ACCENT, height=56)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tk.Label(nav, text="⭐ My Favorite Recipes", font=FONT_H3,
                 bg=ACCENT, fg=TEXT_WHITE).pack(side="left", padx=20)

        btn_frame = tk.Frame(nav, bg=ACCENT)
        btn_frame.pack(side="right", padx=16)

        styled_button(btn_frame, "← Browse Recipes", self._go_back,
                      bg=ACCENT_HOVER, width=14, pady=4).pack(side="left", padx=4)
        styled_button(btn_frame, "Logout", self._logout,
                      bg=TEXT_DARK, width=8, pady=4).pack(side="left")

    def _build_body(self):
        self.body = tk.Frame(self, bg=BG_MAIN)
        self.body.pack(fill="both", expand=True, padx=24, pady=20)
        self._load_favorites()

    def _load_favorites(self):
        for w in self.body.winfo_children():
            w.destroy()

        favorites = self.db.get_favorites(self.user["id"])

        if not favorites:
            tk.Label(self.body, text="⭐", font=("Segoe UI", 56),
                     bg=BG_MAIN, fg=ACCENT).pack(pady=(60, 6))
            tk.Label(self.body, text="You haven't added any favorites yet.",
                     font=FONT_H3, fg=TEXT_LIGHT, bg=BG_MAIN).pack()
            tk.Label(self.body, text="Browse recipes and tap ☆ Favorite to save them here.",
                     font=FONT_LABEL, fg=TEXT_LIGHT, bg=BG_MAIN).pack(pady=4)
            return

        tk.Label(self.body, text=f"{len(favorites)} saved recipe(s)",
                 font=FONT_LABEL, fg=TEXT_MID, bg=BG_MAIN).pack(anchor="w", pady=(0, 12))

        canvas_frame = tk.Frame(self.body, bg=BG_MAIN)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        container = tk.Frame(canvas, bg=BG_MAIN)

        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        for recipe in favorites:
            self._favorite_card(container, recipe)

    def _favorite_card(self, parent, recipe):
        card = tk.Frame(parent, bg=BG_CARD, padx=14, pady=12, relief="flat")
        card.pack(fill="x", pady=6)

        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x")

        tk.Label(top, text="⭐", font=FONT_BODY, bg=BG_CARD).pack(side="left")
        tk.Label(top, text=recipe["title"], font=FONT_H3,
                 fg=TEXT_DARK, bg=BG_CARD).pack(side="left", padx=6)

        tk.Label(card, text=f"  {recipe['category_name']}  ",
                 font=FONT_SMALL, fg=ACCENT, bg=ACCENT_LIGHT).pack(anchor="w", pady=(4, 0))

        preview = "\n".join(recipe["ingredients"].split("\n")[:3])
        tk.Label(card, text=preview, font=FONT_LABEL,
                 fg=TEXT_MID, bg=BG_CARD, justify="left").pack(anchor="w", pady=(4, 8))

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(anchor="e")

        styled_button(btn_row, "View Recipe", lambda r=recipe: self._open_recipe(r),
                      width=12, pady=3).pack(side="left", padx=4)
        styled_button(btn_row, "Remove ✕", lambda r=recipe: self._remove_favorite(r),
                      bg=DANGER, width=10, pady=3).pack(side="left")

    def _open_recipe(self, recipe):
        win = tk.Toplevel(self.master)
        win.title(recipe["title"])
        win.geometry("520x580")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)

        hdr = tk.Frame(win, bg=ACCENT, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=recipe["title"], font=FONT_H2,
                 bg=ACCENT, fg=TEXT_WHITE).pack(side="left", padx=20, pady=10)

        body = tk.Frame(win, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(body, text="🥕 Ingredients", font=FONT_H3,
                 bg=BG_MAIN, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(body, text=recipe["ingredients"], font=FONT_BODY,
                 bg=BG_MAIN, fg=TEXT_MID, justify="left",
                 wraplength=460).pack(anchor="w", pady=(4, 14))

        tk.Label(body, text="📋 Instructions", font=FONT_H3,
                 bg=BG_MAIN, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(body, text=recipe["instructions"], font=FONT_BODY,
                 bg=BG_MAIN, fg=TEXT_MID, justify="left",
                 wraplength=460).pack(anchor="w", pady=(4, 14))

        styled_button(body, "Remove from Favorites",
                      lambda: [self._remove_favorite(recipe), win.destroy()],
                      bg=DANGER, width=22).pack(pady=10)

    def _remove_favorite(self, recipe):
        if messagebox.askyesno("Remove", f"Remove '{recipe['title']}' from favorites?"):
            self.db.remove_favorite(self.user["id"], recipe["id"])
            self._load_favorites()

    def _go_back(self):
        self.pack_forget()
        from user.categories_screen import CategoriesScreen
        CategoriesScreen(self.master, self.db, self.user).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.pack_forget()
            from auth.login_screen import LoginScreen
            LoginScreen(self.master, self.db).pack(fill="both", expand=True)