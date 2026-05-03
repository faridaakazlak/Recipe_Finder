import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assets.styles import COLORS, FONTS


class ManageUsersScreen:
    def __init__(self, root, db_manager, user_data, navigate_callback):
        self.root = root
        self.db = db_manager
        self.user_data = user_data
        self.navigate = navigate_callback
        self.frame = tk.Frame(root, bg=COLORS["bg_dark"])
        self.selected_user_id = None

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self._build_ui()

    def hide(self):
        self.frame.pack_forget()
        for widget in self.frame.winfo_children():
            widget.destroy()

    def _build_ui(self):
        # ── Sidebar ───────────────────────────────────────────────
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
            ("📊  Dashboard", "dashboard", False),
            ("📋  Manage Recipes", "manage_recipes", False),
            ("👥  Manage Users", "manage_users", True),
        ]
        for label, screen, active in nav_items:
            tk.Button(
                sidebar, text=label, font=FONTS["body"],
                bg=COLORS["accent"] if active else COLORS["sidebar"],
                fg=COLORS["white"] if active else COLORS["text_muted"],
                activebackground=COLORS["accent_hover"], activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=20, pady=10, cursor="hand2",
                command=lambda s=screen: self.navigate(s),
            ).pack(fill="x", pady=2)

        tk.Button(
            sidebar, text="🚪  Logout", font=FONTS["body"],
            bg=COLORS["sidebar"], fg=COLORS["danger"],
            activebackground=COLORS["danger"], activeforeground=COLORS["white"],
            relief="flat", anchor="w", padx=20, pady=10, cursor="hand2",
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
            header, text="Manage Users",
            font=FONTS["heading"], bg=COLORS["bg_card"], fg=COLORS["text_primary"],
        ).pack(side="left", padx=30, pady=20)

        # Content
        content = tk.Frame(main, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=30, pady=30)

        # Summary cards
        stats_row = tk.Frame(content, bg=COLORS["bg_dark"])
        stats_row.pack(fill="x", pady=(0, 25))

        total_users = self.db.get_user_count()
        admin_count = self.db.get_admin_count() if hasattr(self.db, "get_admin_count") else "N/A"

        for icon, label, val, color in [
            ("👥", "Total Users", total_users, COLORS["accent"]),
            ("🛡️", "Admins", admin_count, COLORS["warning"]),
        ]:
            card = tk.Frame(stats_row, bg=COLORS["bg_card"], padx=20, pady=15)
            card.pack(side="left", padx=(0, 15))
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 20),
                     bg=COLORS["bg_card"], fg=color).pack(anchor="w")
            tk.Label(card, text=str(val), font=FONTS["stat_number"],
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(3, 1))
            tk.Label(card, text=label, font=FONTS["caption"],
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")

        # Search bar
        top_bar = tk.Frame(content, bg=COLORS["bg_dark"])
        top_bar.pack(fill="x", pady=(0, 15))

        search_frame = tk.Frame(top_bar, bg=COLORS["bg_card"], padx=10, pady=6)
        search_frame.pack(side="left")
        tk.Label(search_frame, text="🔍", bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], font=FONTS["body"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._filter_users())
        tk.Entry(
            search_frame, textvariable=self.search_var,
            font=FONTS["body"], bg=COLORS["bg_card"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief="flat", width=30,
        ).pack(side="left", padx=5)

        btn_bar = tk.Frame(content, bg=COLORS["bg_dark"])
        btn_bar.pack(fill="x", pady=(0, 12))

        tk.Button(
            btn_bar, text="🗑️  Delete User",
            font=FONTS["body"], bg=COLORS["danger"], fg=COLORS["white"],
            activebackground="#8b0000", activeforeground=COLORS["white"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._delete_user,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_bar, text="ℹ️  View Details",
            font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            activebackground=COLORS["bg_dark"], activeforeground=COLORS["text_primary"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._view_user_details,
        ).pack(side="left")

        # Table
        table_frame = tk.Frame(content, bg=COLORS["bg_card"])
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Username", "Email", "Role")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=38, font=FONTS["body"])
        style.configure("Treeview.Heading",
                         background=COLORS["bg_dark"],
                         foreground=COLORS["text_muted"],
                         font=FONTS["caption"], relief="flat")
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        widths = [50, 200, 280, 120]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=w)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self._load_users()

    # ── Helpers ───────────────────────────────────────────────────

    def _load_users(self, filter_text=""):
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = self.db.get_all_users()

        for u in users:
            username = u.get("username") or u.get("name", "")
            email = u.get("email", "")

            if (filter_text.lower() in username.lower() or
                    filter_text.lower() in email.lower()):

                is_admin = u.get("is_admin") or u.get("role") == "admin"
                role_label = "🛡️ Admin" if is_admin else "👤 User"
                joined = u.get("created_at", "N/A")

                self.tree.insert(
                    "", "end",
                    iid=str(u.get("id", "")),
                    values=(
                        u.get("id", ""),
                        username,
                        email,
                        role_label
                    )
                )

    def _filter_users(self):
        self._load_users(self.search_var.get())

    def _on_select(self, event):
        sel = self.tree.selection()
        self.selected_user_id = int(sel[0]) if sel else None

    def _delete_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return

        if self.selected_user_id == self.user_data.get("id"):
            messagebox.showerror("Error", "You cannot delete your own account.")
            return

        user = self.db.get_user_by_id(self.selected_user_id)
        is_admin = user.get("is_admin") or user.get("role") == "admin" if user else False
        if user and is_admin:
            messagebox.showerror("Error", "Cannot delete an admin account.")
            return

        username = user.get("username") or user.get("name", "this user") if user else "this user"
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?\n"
            "All their favorites will also be removed. This cannot be undone."
        )
        if confirm:
            self.db.delete_user(self.selected_user_id)
            self.selected_user_id = None
            self._load_users()
            messagebox.showinfo("Deleted", "User deleted successfully.")

    def _view_user_details(self):
        if not self.selected_user_id:
            messagebox.showwarning("No Selection", "Please select a user to view.")
            return

        user = self.db.get_user_by_id(self.selected_user_id)
        if not user:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("User Details")
        dialog.geometry("380x320")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="👤 User Details", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(25, 15))

        username = user.get("username") or user.get("name", "")
        is_admin = user.get("is_admin") or user.get("role") == "admin"

        details = [
            ("ID", user["id"]),
            ("Username", username),
            ("Email", user["email"]),
            ("Role", "Admin" if is_admin else "User"),
            ("Joined", user.get("created_at", "N/A")),
        ]

        for label, value in details:
            row = tk.Frame(dialog, bg=COLORS["bg_card"])
            row.pack(fill="x", padx=30, pady=4)
            tk.Label(row, text=f"{label}:", font=FONTS["caption"],
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"], width=12,
                     anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     anchor="w").pack(side="left")

        favorites_count = self.db.get_user_favorites_count(self.selected_user_id)
        row = tk.Frame(dialog, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=30, pady=4)
        tk.Label(row, text="Favorites:", font=FONTS["caption"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"], width=12, anchor="w").pack(side="left")
        tk.Label(row, text=str(favorites_count), font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"], anchor="w").pack(side="left")

        tk.Button(
            dialog, text="Close",
            font=FONTS["body"], bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
            relief="flat", padx=30, pady=8, cursor="hand2",
            command=dialog.destroy,
        ).pack(pady=20)