import tkinter as tk
from tkinter import messagebox
from assets.styles import *


class CategoriesScreen(tk.Frame):

    def __init__(self, parent, db, user):
        super().__init__(parent, bg=BG_MAIN)
        self.db = db
        self.user = user
        self.selected_category = None
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_navbar()
        self._build_body()

    def _build_navbar(self):
        nav = tk.Frame(self, bg=ACCENT, height=56)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tk.Label(nav, text="🍴 Recipe Finder", font=FONT_H3,
                 bg=ACCENT, fg=TEXT_WHITE).pack(side="left", padx=20)

        # Right-side nav buttons
        btn_frame = tk.Frame(nav, bg=ACCENT)
        btn_frame.pack(side="right", padx=16)

        styled_button(btn_frame, "⭐ Favorites", self._go_favorites,
                      bg=ACCENT_HOVER, width=12, pady=4).pack(side="left", padx=4)
        styled_button(btn_frame, "Logout", self._logout,
                      bg=TEXT_DARK, width=8, pady=4).pack(side="left")

        # Greeting
        tk.Label(nav, text=f"Hello, {self.user['name']} 👋",
                 font=FONT_LABEL, bg=ACCENT, fg=ACCENT_LIGHT).pack(side="left", padx=10)

    def _build_body(self):
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True)

        # ── Sidebar: categories ────────────────────────────────────────────────
        sidebar = tk.Frame(body, bg=BG_CARD, width=200, relief="flat")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Categories", font=FONT_H3,
                 bg=BG_CARD, fg=TEXT_DARK).pack(pady=(20, 8), padx=16, anchor="w")

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12)

        self.cat_buttons = []
        for cat in self.db.get_all_categories():
            btn = tk.Button(
                sidebar,
                text=f"  {cat['icon']}  {cat['name']}",
                font=FONT_BODY, bg=BG_CARD, fg=TEXT_DARK,
                anchor="w", relief="flat", cursor="hand2", pady=8, padx=12,
                activebackground=ACCENT_LIGHT, activeforeground=ACCENT,
                command=lambda c=cat: self._select_category(c)
            )
            btn.pack(fill="x")
            self.cat_buttons.append((btn, cat["id"]))

        # ── Main content ───────────────────────────────────────────────────────
        self.main_area = tk.Frame(body, bg=BG_MAIN)
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self._show_welcome()

    def _show_welcome(self):
        for w in self.main_area.winfo_children():
            w.destroy()

        tk.Label(self.main_area, text="     🍽️", font=("Segoe UI", 70),
                 bg=BG_MAIN, fg=ACCENT).pack(pady=(180, 30))
        tk.Label(self.main_area, text="Select a category to explore recipes",
                 font=FONT_H2, bg=BG_MAIN, fg=TEXT_MID).pack()

    def _select_category(self, cat):
        self.selected_category = cat

        # Highlight active button
        for btn, cid in self.cat_buttons:
            if cid == cat["id"]:
                btn.config(bg=ACCENT_LIGHT, fg=ACCENT, font=(*FONT_BODY[:2], "bold"))
            else:
                btn.config(bg=BG_CARD, fg=TEXT_DARK, font=FONT_BODY)

        self._show_recipes(cat)

    def _show_recipes(self, cat):
        for w in self.main_area.winfo_children():
            w.destroy()

        # Header
        tk.Label(self.main_area,
                 text=f"{cat['icon']}  {cat['name']} Recipes",
                 font=FONT_H2, bg=BG_MAIN, fg=TEXT_DARK).pack(anchor="w")

        # Search bar
        search_frame = tk.Frame(self.main_area, bg=BG_MAIN)
        search_frame.pack(fill="x", pady=(10, 16))

        tk.Label(search_frame, text="🔍", font=FONT_BODY,
                 bg=BG_MAIN).pack(side="left")
        wrap, self.search_entry = styled_entry(search_frame, width=30)
        wrap.pack(side="left", padx=6)
        styled_button(search_frame, "Search", self._do_search,
                      width=8, pady=4).pack(side="left")

        # Recipe list container (scrollable)
        canvas_frame = tk.Frame(self.main_area, bg=BG_MAIN)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.recipe_container = tk.Frame(canvas, bg=BG_MAIN)

        self.recipe_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.recipe_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._load_recipe_cards()

    def _do_search(self):
        self._load_recipe_cards(self.search_entry.get().strip())

    def _load_recipe_cards(self, search=""):
        for w in self.recipe_container.winfo_children():
            w.destroy()

        recipes = self.db.get_recipes_by_category(
            self.selected_category["id"], search
        )

        if not recipes:
            tk.Label(self.recipe_container,
                     text="No recipes found.", font=FONT_BODY,
                     fg=TEXT_LIGHT, bg=BG_MAIN).pack(pady=30)
            return

        for recipe in recipes:
            self._recipe_card(self.recipe_container, recipe)

    def _recipe_card(self, parent, recipe):
        card = tk.Frame(parent, bg=BG_CARD, relief="flat",
                        bd=1, padx=14, pady=12, cursor="hand2")
        card.pack(fill="x", pady=6)
        card.bind("<Button-1>", lambda e, r=recipe: self._open_recipe(r))

        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x")

        tk.Label(top, text=recipe["title"], font=FONT_H3,
                 fg=TEXT_DARK, bg=BG_CARD).pack(side="left")

        is_fav = self.db.is_favorite(self.user["id"], recipe["id"])
        fav_text = "★ Remove" if is_fav else "☆ Favorite"
        fav_btn = styled_button(top, fav_text,
                                lambda r=recipe: self._toggle_favorite(r),
                                bg=ACCENT if is_fav else BORDER,
                                fg=TEXT_WHITE if is_fav else TEXT_DARK,
                                width=10, pady=2)
        fav_btn.pack(side="right")

        tk.Label(card, text=f"Category: {recipe['category_name']}",
                 font=FONT_SMALL, fg=TEXT_LIGHT, bg=BG_CARD).pack(anchor="w")

        preview = recipe["ingredients"].split("\n")[0]
        tk.Label(card, text=f"Ingredients: {preview}...",
                 font=FONT_LABEL, fg=TEXT_MID, bg=BG_CARD).pack(anchor="w", pady=(4, 0))

        tk.Button(card, text="View Recipe →", font=FONT_SMALL,
                  fg=ACCENT, bg=BG_CARD, relief="flat",
                  cursor="hand2", command=lambda r=recipe: self._open_recipe(r)).pack(anchor="e")

    def _open_recipe(self, recipe):
        win = tk.Toplevel(self.master)
        win.title(recipe["title"])
        win.geometry("520x580")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)

        # Header
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

        is_fav = self.db.is_favorite(self.user["id"], recipe["id"])
        fav_label = "★ Remove from Favorites" if is_fav else "☆ Add to Favorites"
        styled_button(body, fav_label,
                      lambda: [self._toggle_favorite(recipe), win.destroy()],
                      width=26).pack(pady=10)

    def _toggle_favorite(self, recipe):
        if self.db.is_favorite(self.user["id"], recipe["id"]):
            self.db.remove_favorite(self.user["id"], recipe["id"])
        else:
            self.db.add_favorite(self.user["id"], recipe["id"])
        self._load_recipe_cards(
            self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        )

    # ── Navigation ─────────────────────────────────────────────────────────────
    def _go_favorites(self):
        self.pack_forget()
        from user.favorites_screen import FavoritesScreen
        FavoritesScreen(self.master, self.db, self.user).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.pack_forget()
            from auth.login_screen import LoginScreen
            LoginScreen(self.master, self.db).pack(fill="both", expand=True)
