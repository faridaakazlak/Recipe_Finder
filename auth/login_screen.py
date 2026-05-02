import tkinter as tk
from tkinter import messagebox
from assets.styles import *


class LoginScreen(tk.Frame):

    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_MAIN)
        self.db = db
        self.current_user = None
        self.current_admin_screen = None
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Left decorative panel ──────────────────────────────────────────────
        left = tk.Frame(self, bg=ACCENT)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.bind("<Configure>", lambda e: left.config(width=int(e.width * 0.35)))

        left_inner = tk.Frame(left, bg=ACCENT)
        left_inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            left_inner,
            text="🍴",
            font=("Segoe UI", 72),
            bg=ACCENT,
            fg=TEXT_WHITE
        ).pack(pady=(0, 16))

        tk.Label(
            left_inner,
            text="Recipe Finder",
            font=("Segoe UI", 28, "bold"),
            bg=ACCENT,
            fg=TEXT_WHITE
        ).pack()

        tk.Label(
            left_inner,
            text="Discover & cook amazing\nrecipes every day!",
            font=("Segoe UI", 13),
            bg=ACCENT,
            fg=ACCENT_LIGHT,
            justify="center"
        ).pack(pady=14)

        tk.Frame(left_inner, bg=ACCENT_LIGHT, height=2, width=120).pack(pady=(8, 0))

        # ── Right form panel ───────────────────────────────────────────────────
        right = tk.Frame(self, bg=BG_MAIN)
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=BG_MAIN)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form,
            text="Welcome Back! 👋",
            font=("Segoe UI", 26, "bold"),
            fg=TEXT_DARK,
            bg=BG_MAIN
        ).pack(pady=(0, 6))

        tk.Label(
            form,
            text="Enter your details to sign in",
            font=("Segoe UI", 12),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(pady=(0, 30))

        # Email
        tk.Label(
            form,
            text="Email Address",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(anchor="w")

        email_wrap, self.email_entry = styled_entry(form, width=42)
        email_wrap.pack(fill="x", pady=(6, 18), ipady=4)

        # Password
        tk.Label(
            form,
            text="Password",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(anchor="w")

        pw_wrap, self.pw_entry = styled_entry(form, show="•", width=42)
        pw_wrap.pack(fill="x", pady=(6, 30), ipady=4)

        # Login button
        styled_button(
            form,
            "Sign In",
            self._handle_login,
            width=42
        ).pack(fill="x", ipady=6)

        # Separator
        sep = tk.Frame(form, bg=BORDER, height=1)
        sep.pack(fill="x", pady=24)

        # Sign up link
        row = tk.Frame(form, bg=BG_MAIN)
        row.pack()

        tk.Label(
            row,
            text="Don't have an account? ",
            font=("Segoe UI", 12),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(side="left")

        link_label(
            row,
            "Create one",
            self._go_signup
        ).pack(side="left")

    # ── Logic ──────────────────────────────────────────────────────────────────
    def _handle_login(self):
        email = self.email_entry.get().strip()
        password = self.pw_entry.get().strip()

        if not email or not password:
            messagebox.showwarning(
                "Missing Fields",
                "Please fill in all fields."
            )
            return

        success, result = self.db.login_user(email, password)

        if not success:
            messagebox.showerror("Login Failed", result)
            return

        self.current_user = result
        self._navigate(result)

    def _navigate(self, user):
        self.pack_forget()
        root = self.master

        if user["role"] == "admin":
            from admin.dashboard_screen import DashboardScreen

            screen = DashboardScreen(
                root,
                self.db,
                user,
                self._admin_navigate
            )
            self.current_admin_screen = screen
            screen.show()

        else:
            from user.categories_screen import CategoriesScreen

            screen = CategoriesScreen(
                root,
                self.db,
                user
            )
            screen.pack(fill="both", expand=True)

    def _admin_navigate(self, screen_name):
        root = self.master

        if self.current_admin_screen is not None:
            try:
                self.current_admin_screen.hide()
            except Exception:
                pass
            self.current_admin_screen = None

        if screen_name == "login":
            self.current_user = None
            login = LoginScreen(root, self.db)
            login.pack(fill="both", expand=True)
            return

        if screen_name == "dashboard":
            from admin.dashboard_screen import DashboardScreen
            screen = DashboardScreen(
                root, self.db, self.current_user, self._admin_navigate
            )

        elif screen_name == "manage_recipes":
            from admin.manage_recipes_screen import ManageRecipesScreen
            screen = ManageRecipesScreen(
                root, self.db, self.current_user, self._admin_navigate
            )

        elif screen_name == "manage_users":
            from admin.manage_users_screen import ManageUsersScreen
            screen = ManageUsersScreen(
                root, self.db, self.current_user, self._admin_navigate
            )

        else:
            return

        self.current_admin_screen = screen
        screen.show()

    def _go_signup(self):
        self.pack_forget()

        from auth.signup_screen import SignupScreen

        SignupScreen(
            self.master,
            self.db
        ).pack(fill="both", expand=True)