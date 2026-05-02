import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assets.styles import COLORS, FONTS


class RecipesActions:
    
    def __init__(self, screen):
        self.screen = screen   # reference to ManageRecipesScreen

    # ── Convenience shorthands ─────────────────────────────────────────────────

    @property
    def db(self):
        return self.screen.db

    @property
    def root(self):
        return self.screen.root

    @property
    def tree(self):
        return self.screen.tree

    @property
    def recipes_data(self):
        return self.screen._recipes_data

    # ── Search UI + Logic ──────────────────────────────────────────────────────

    def build_search(self, parent):
        search_frame = tk.Frame(parent, bg=COLORS["bg_card"], padx=10, pady=6)
        search_frame.pack(side="left")

        tk.Label(
            search_frame, text="🔍",
            bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body"],
        ).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._filter_recipes())

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", width=30,
        ).pack(side="left", padx=5)

    def _filter_recipes(self):
        self.screen.load_recipes(self.search_var.get())

    # ── Detail Panel UI ────────────────────────────────────────────────────────

    def build_detail_panel(self, parent):
        ing_panel = tk.Frame(parent, bg=COLORS["bg_card"], width=240)
        ing_panel.pack(side="right", fill="y", padx=(8, 0))
        ing_panel.pack_propagate(False)

        # Ingredients
        tk.Label(
            ing_panel, text="🥗 Ingredients",
            font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["accent"],
        ).pack(pady=(14, 4), padx=16, anchor="w")
        tk.Frame(ing_panel, bg=COLORS["bg_dark"], height=1).pack(fill="x", padx=16, pady=(0, 6))

        self.ing_listbox = tk.Listbox(
            ing_panel, font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            selectbackground=COLORS["bg_card"], selectforeground=COLORS["text_primary"],
            relief="flat", bd=0, highlightthickness=0, activestyle="none", height=7,
        )
        self.ing_listbox.pack(fill="x", padx=12)

        # Instructions
        tk.Label(
            ing_panel, text="📋 Instructions",
            font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["accent"],
        ).pack(pady=(12, 4), padx=16, anchor="w")
        tk.Frame(ing_panel, bg=COLORS["bg_dark"], height=1).pack(fill="x", padx=16, pady=(0, 6))

        self.inst_text = tk.Text(
            ing_panel, font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            relief="flat", bd=0, highlightthickness=0,
            wrap="word", state="disabled", cursor="arrow",
        )
        self.inst_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.show_placeholder()

    def show_placeholder(self):
        self.ing_listbox.delete(0, "end")
        self.ing_listbox.insert("end", "  Select a recipe...")
        self.ing_listbox.itemconfig(0, fg=COLORS["text_muted"])
        self.inst_text.config(state="normal")
        self.inst_text.delete("1.0", "end")
        self.inst_text.insert("end", "Select a recipe to see instructions.")
        self.inst_text.config(state="disabled", fg=COLORS["text_muted"])

    def on_select(self, event):
        sel = self.tree.selection()
        iid = sel[0] if sel else None
        self.screen.selected_recipe_id = int(iid) if iid else None
        self._show_ingredients(iid)

    def _show_ingredients(self, iid):
        self.ing_listbox.delete(0, "end")
        self.inst_text.config(state="normal")
        self.inst_text.delete("1.0", "end")

        if not iid:
            self.show_placeholder()
            return

        recipe  = self.recipes_data.get(str(iid), {})
        raw_ing = recipe.get("ingredients", "") or ""
        items   = [i.strip() for i in re.split(r"[,;\n\r]+", raw_ing) if i.strip()]

        if not items:
            self.ing_listbox.insert("end", "  No ingredients found")
        else:
            for ing in items:
                self.ing_listbox.insert("end", f"  • {ing}")

        raw_inst = recipe.get("instructions", "") or ""
        if raw_inst.strip():
            self.inst_text.insert("end", raw_inst.strip())
            self.inst_text.config(fg=COLORS["text_primary"])
        else:
            self.inst_text.insert("end", "No instructions available.")
            self.inst_text.config(fg=COLORS["text_muted"])
        self.inst_text.config(state="disabled")

    # ── Button Bar UI ──────────────────────────────────────────────────────────

    def build_btn_bar(self, parent):
        btn_bar = tk.Frame(parent, bg=COLORS["bg_dark"])
        btn_bar.pack(fill="x", pady=(15, 0))

        tk.Button(
            btn_bar, text="✏️  Edit Recipe",
            font=FONTS["body"],
            bg=COLORS["warning"], fg=COLORS["white"],
            activebackground="#b8860b", activeforeground=COLORS["white"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._open_edit_dialog,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_bar, text="🗑️  Delete Recipe",
            font=FONTS["body"],
            bg=COLORS["danger"], fg=COLORS["white"],
            activebackground="#8b0000", activeforeground=COLORS["white"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._delete_recipe,
        ).pack(side="left")

    # ── Edit Logic + UI ────────────────────────────────────────────────────────

    def _open_edit_dialog(self):
        sel = self.tree.selection()
        if sel:
            self.screen.selected_recipe_id = int(sel[0])
        if not self.screen.selected_recipe_id:
            messagebox.showwarning("No Selection", "Please select a recipe to edit.")
            return

        recipe = self.recipes_data.get(str(self.screen.selected_recipe_id))
        if not recipe:
            recipe = self.db.get_recipe_by_id(self.screen.selected_recipe_id)
        if not recipe:
            return

        categories     = self.db.get_all_categories()
        cat_name_to_id = {c["name"]: c["id"] for c in categories}
        cat_names      = list(cat_name_to_id.keys())

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Recipe")
        dialog.geometry("520x500")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(
            dialog, text="Edit Recipe",
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

        name_entry = labeled_entry("Recipe Name")
        name_entry.insert(0, recipe.get("title") or recipe.get("name", ""))
        fields["name"] = name_entry

        tk.Label(
            dialog, text="Category", font=FONTS["caption"],
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        ).pack(fill="x", padx=30, pady=(8, 0))
        cat_var = tk.StringVar()
        ttk.Combobox(
            dialog, textvariable=cat_var, values=cat_names,
            state="readonly", font=FONTS["body"],
        ).pack(fill="x", padx=30, ipady=6)
        current_cat = recipe.get("category_name") or recipe.get("category", "")
        cat_var.set(current_cat if current_cat in cat_names else (cat_names[0] if cat_names else ""))
        fields["category"] = cat_var

        ing_entry = labeled_entry("Ingredients (comma-separated)")
        ing_entry.insert(0, recipe.get("ingredients", ""))
        fields["ingredients"] = ing_entry

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
        inst.insert("1.0", recipe.get("instructions", ""))
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
                self.db.update_recipe(
                    recipe["id"], name, cat_name_to_id[category], ingredients, instructions
                )
                messagebox.showinfo("Success", "Recipe updated successfully!", parent=dialog)
                dialog.destroy()
                self.screen.load_recipes()
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

    # ── Delete Logic ───────────────────────────────────────────────────────────

    def _delete_recipe(self):
        sel = self.tree.selection()
        if sel:
            self.screen.selected_recipe_id = int(sel[0])
        if not self.screen.selected_recipe_id:
            messagebox.showwarning("No Selection", "Please select a recipe to delete.")
            return
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this recipe?\nThis action cannot be undone."
        ):
            self.db.delete_recipe(self.screen.selected_recipe_id)
            self.screen.selected_recipe_id = None
            self.screen.load_recipes()
            messagebox.showinfo("Deleted", "Recipe deleted successfully.")
