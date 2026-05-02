import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assets.styles import COLORS, FONTS, apply_button_style


class DashboardScreen:
    def __init__(self, root, db_manager, user_data, navigate_callback):
        self.root = root
        self.db = db_manager
        self.user_data = user_data
        self.navigate = navigate_callback
        self.frame = tk.Frame(root, bg=COLORS["bg_dark"])

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self._build_ui()

    def hide(self):
        self.frame.pack_forget()
        for widget in self.frame.winfo_children():
            widget.destroy()

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────
        sidebar = tk.Frame(self.frame, bg=COLORS["sidebar"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="🍽️",
            font=("Segoe UI Emoji", 22),
            bg=COLORS["sidebar"],
            fg=COLORS["accent"],
        ).pack(pady=(30, 4), padx=20, anchor="w")

        tk.Label(
            sidebar,
            text="RecipeFinder",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["sidebar"],
            fg="#FFFFFF",
        ).pack(padx=20, anchor="w", pady=(0, 10))

        tk.Label(
            sidebar,
            text="ADMIN PANEL",
            font=FONTS["caption"],
            bg=COLORS["sidebar"],
            fg=COLORS["text_muted"],
        ).pack(padx=20, anchor="w")

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20, pady=15)

        nav_items = [
            ("📊  Dashboard", "dashboard", True),
            ("📋  Manage Recipes", "manage_recipes", False),
            ("👥  Manage Users", "manage_users", False),
        ]
        for label, screen, active in nav_items:
            btn = tk.Button(
                sidebar,
                text=label,
                font=FONTS["body"],
                bg=COLORS["accent"] if active else COLORS["sidebar"],
                fg=COLORS["white"] if active else COLORS["text_muted"],
                activebackground=COLORS["accent_hover"],
                activeforeground=COLORS["white"],
                relief="flat",
                anchor="w",
                padx=20,
                pady=10,
                cursor="hand2",
                command=lambda s=screen: self.navigate(s),
            )
            btn.pack(fill="x", pady=2)

        # Logout
        tk.Button(
            sidebar,
            text="🚪  Logout",
            font=FONTS["body"],
            bg=COLORS["sidebar"],
            fg=COLORS["danger"],
            activebackground=COLORS["danger"],
            activeforeground=COLORS["white"],
            relief="flat",
            anchor="w",
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self.navigate("login"),
        ).pack(side="bottom", fill="x", pady=20)

        # ── Main content ──────────────────────────────────────────
        main = tk.Frame(self.frame, bg=COLORS["bg_dark"])
        main.pack(side="left", fill="both", expand=True)

        # Header
        header = tk.Frame(main, bg=COLORS["bg_card"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Dashboard Overview",
            font=FONTS["heading"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack(side="left", padx=30, pady=20)

        tk.Label(
            header,
            text=f"👤  {self.user_data.get('username', self.user_data.get('name', 'Admin'))}",
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(side="right", padx=30)

        # Content area
        content = tk.Frame(main, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(
            content,
            text="Welcome back, Admin! 👋",
            font=FONTS["subheading"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 20))

        # Stats cards row
        stats_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        stats_frame.pack(fill="x", pady=(0, 30))

        stats = self._get_stats()
        card_data = [
            ("📋", "Total Recipes", stats["recipes"], COLORS["accent"]),
            ("👥", "Total Users", stats["users"], COLORS["success"]),
            ("⭐", "Favorites Saved", stats["favorites"], COLORS["warning"]),
        ]
        for icon, label, value, color in card_data:
            self._stat_card(stats_frame, icon, label, value, color)

        # Quick Actions
        tk.Label(
            content,
            text="Quick Actions",
            font=FONTS["subheading"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 15))

        actions_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        actions_frame.pack(fill="x")

        actions = [
            ("📋  Manage Recipes", "manage_recipes", COLORS["accent"]),
            ("👥  Manage Users", "manage_users", COLORS["success"]),
        ]
        for text, screen, color in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=FONTS["body_bold"],
                bg=color,
                fg=COLORS["white"],
                activebackground=COLORS["accent_hover"],
                activeforeground=COLORS["white"],
                relief="flat",
                padx=25,
                pady=12,
                cursor="hand2",
                command=lambda s=screen: self.navigate(s),
            )
            btn.pack(side="left", padx=(0, 15))


    def _stat_card(self, parent, icon, label, value, color):
        card = tk.Frame(parent, bg=COLORS["bg_card"], padx=25, pady=20)
        card.pack(side="left", padx=(0, 15), fill="y")

        tk.Label(card, text=icon, font=("Segoe UI Emoji", 24),
                 bg=COLORS["bg_card"], fg=color).pack(anchor="w")
        tk.Label(card, text=str(value), font=FONTS["stat_number"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(5, 2))
        tk.Label(card, text=label, font=FONTS["caption"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")

    def _recent_recipes_table(self, parent):
        table_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        table_frame.pack(fill="x")

        cols = ("ID", "Name", "Category")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=7)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=35,
                         font=FONTS["body"])
        style.configure("Treeview.Heading",
                         background=COLORS["bg_dark"],
                         foreground=COLORS["text_muted"],
                         font=FONTS["caption"],
                         relief="flat")

        widths = [60, 280, 200]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=w)

        recipes = self.db.get_all_recipes()
        for r in recipes[:10]:
            name = r.get("name") or r.get("title", "")
            category = r.get("category") or r.get("category_name", "")
            tree.insert("", "end", values=(
                r["id"],
                name,
                category
            ))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y")

    def _get_stats(self):
        return {
            "recipes": self.db.get_recipe_count(),
            "users": self.db.get_user_count(),
            "favorites": self.db.get_favorites_count(),
        }