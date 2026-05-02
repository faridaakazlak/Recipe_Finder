import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assets.styles import COLORS, FONTS
from .recipes_actions import RecipesActions


class ManageRecipesScreen:

    def __init__(self, root, db_manager, user_data, navigate_callback):
        self.root       = root
        self.db         = db_manager
        self.user_data  = user_data
        self.navigate   = navigate_callback
        self.frame      = tk.Frame(root, bg=COLORS["bg_dark"])

        self.selected_recipe_id = None
        self._recipes_data      = {}

        self.actions = RecipesActions(self)

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self._build_ui()

    def hide(self):
        self.frame.pack_forget()
        for widget in self.frame.winfo_children():
            widget.destroy()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_sidebar()
        self._build_main()
        self.load_recipes()

    def _build_sidebar(self):
        sidebar = tk.Frame(self.frame, bg=COLORS["sidebar"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="🍽️",
            font=("Segoe UI Emoji", 22),
            bg=COLORS["sidebar"], fg=COLORS["accent"],
        ).pack(pady=(30, 4), padx=20, anchor="w")

        tk.Label(
            sidebar, text="RecipeFinder",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["sidebar"], fg="#FFFFFF",
        ).pack(padx=20, anchor="w", pady=(0, 10))

        tk.Label(
            sidebar, text="ADMIN PANEL",
            font=FONTS["caption"],
            bg=COLORS["sidebar"], fg=COLORS["text_muted"],
        ).pack(padx=20, anchor="w")

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20, pady=15)

        nav_items = [
            ("📊  Dashboard",      "dashboard",      False),
            ("📋  Manage Recipes", "manage_recipes", True),
            ("👥  Manage Users",   "manage_users",   False),
        ]
        for label, screen, active in nav_items:
            tk.Button(
                sidebar, text=label,
                font=FONTS["body"],
                bg=COLORS["accent"] if active else COLORS["sidebar"],
                fg=COLORS["white"]  if active else COLORS["text_muted"],
                activebackground=COLORS["accent_hover"],
                activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=20, pady=10, cursor="hand2",
                command=lambda s=screen: self.navigate(s),
            ).pack(fill="x", pady=2)

        tk.Button(
            sidebar, text="🚪  Logout",
            font=FONTS["body"],
            bg=COLORS["sidebar"], fg=COLORS["danger"],
            activebackground=COLORS["danger"], activeforeground=COLORS["white"],
            relief="flat", anchor="w", padx=20, pady=10, cursor="hand2",
            command=lambda: self.navigate("login"),
        ).pack(side="bottom", fill="x", pady=20)

    def _build_main(self):
        main = tk.Frame(self.frame, bg=COLORS["bg_dark"])
        main.pack(side="left", fill="both", expand=True)

        # Header
        header = tk.Frame(main, bg=COLORS["bg_card"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Manage Recipes",
            font=FONTS["heading"],
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
        ).pack(side="left", padx=30, pady=20)

        # Content
        content = tk.Frame(main, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=30, pady=30)

        top_bar = tk.Frame(content, bg=COLORS["bg_dark"])
        top_bar.pack(fill="x", pady=(0, 20))

        self.actions.build_search(top_bar)       
        self._build_add_button(top_bar)          

        body_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        body_frame.pack(fill="both", expand=True)

        self._build_table(body_frame)            
        self.actions.build_detail_panel(body_frame)  

        self.actions.build_btn_bar(content)      

    # ── Table ──────────────────────────────────────────────────────────────────

    def _build_table(self, parent):
        table_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        table_frame.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Name", "Category")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["bg_card"], foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_card"], rowheight=38, font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["bg_dark"], foreground=COLORS["text_muted"],
            font=FONTS["caption"], relief="flat",
        )
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        for col, w in zip(cols, [60, 260, 160]):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=w)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.actions.on_select)

    def load_recipes(self, filter_text=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.actions.show_placeholder()

        recipes = self.db.get_all_recipes()
        self._recipes_data = {str(r.get("id", "")): r for r in recipes}

        for r in recipes:
            name     = r.get("name") or r.get("title", "")
            category = r.get("category") or r.get("category_name", "")
            if (
                filter_text.lower() in name.lower()
                or filter_text.lower() in category.lower()
            ):
                self.tree.insert(
                    "", "end", iid=str(r.get("id", "")),
                    values=(r.get("id", ""), name, category),
                )

    # ── Add Recipe ─────────────────────────────────────────────────────────────

    def _build_add_button(self, parent):
        tk.Button(
            parent, text="➕  Add Recipe",
            font=FONTS["body_bold"],
            bg=COLORS["accent"], fg=COLORS["white"],
            activebackground=COLORS["accent_hover"], activeforeground=COLORS["white"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._open_add_dialog,
        ).pack(side="right")

    def _open_add_dialog(self):
        categories      = self.db.get_all_categories()
        cat_name_to_id  = {c["name"]: c["id"] for c in categories}
        cat_names       = list(cat_name_to_id.keys())

        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Recipe")
        dialog.geometry("520x500")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(
            dialog, text="Add New Recipe",
            font=FONTS["heading"],
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
        ).pack(pady=(20, 15))

        fields = {}

        def labeled_entry(label_text):
            tk.Label(
                dialog, text=label_text, font=FONTS["caption"],
                bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            ).pack(fill="x", padx=30, pady=(8, 0))
            e = tk.Entry(
                dialog, font=FONTS["body"],
                bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                insertbackground=COLORS["text_primary"], relief="flat",
            )
            e.pack(fill="x", padx=30, ipady=8)
            return e

        fields["name"] = labeled_entry("Recipe Name")

        tk.Label(
            dialog, text="Category", font=FONTS["caption"],
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        ).pack(fill="x", padx=30, pady=(8, 0))
        cat_var = tk.StringVar(value=cat_names[0] if cat_names else "")
        ttk.Combobox(
            dialog, textvariable=cat_var, values=cat_names,
            state="readonly", font=FONTS["body"],
        ).pack(fill="x", padx=30, ipady=6)
        fields["category"] = cat_var

        fields["ingredients"] = labeled_entry("Ingredients (comma-separated)")

        tk.Label(
            dialog, text="Instructions", font=FONTS["caption"],
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        ).pack(fill="x", padx=30, pady=(8, 0))
        inst = tk.Text(
            dialog, height=5, font=FONTS["body"],
            bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"], relief="flat",
        )
        inst.pack(fill="x", padx=30)
        fields["instructions"] = inst

        def save():
            name         = fields["name"].get().strip()
            category     = fields["category"].get().strip()
            ingredients  = fields["ingredients"].get().strip()
            instructions = fields["instructions"].get("1.0", "end").strip()

            if not name:
                messagebox.showerror("Error", "Recipe Name is required.", parent=dialog)
                return
            if not category or category not in cat_name_to_id:
                messagebox.showerror("Error", "Please select a valid Category.", parent=dialog)
                return
            try:
                self.db.add_recipe(name, cat_name_to_id[category], ingredients, instructions)
                messagebox.showinfo("Success", "Recipe added successfully!", parent=dialog)
                dialog.destroy()
                self.load_recipes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}", parent=dialog)

        tk.Button(
            dialog, text="💾  Save Recipe",
            font=FONTS["body_bold"],
            bg=COLORS["accent"], fg=COLORS["white"],
            activebackground=COLORS["accent_hover"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=save,
        ).pack(pady=18)
