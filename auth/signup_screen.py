import tkinter as tk
from tkinter import messagebox
from assets.styles import *


class SignupScreen(tk.Frame):

    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_MAIN)
        self.db = db
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
            text="👨‍🍳",
            font=("Segoe UI", 72),
            bg=ACCENT,
            fg=TEXT_WHITE
        ).pack(pady=(0, 16))

        tk.Label(
            left_inner,
            text="Join Us!",
            font=("Segoe UI", 28, "bold"),
            bg=ACCENT,
            fg=TEXT_WHITE
        ).pack()

        tk.Label(
            left_inner,
            text="Create an account and start\nexploring recipes today.",
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
            text="Create New Account",
            font=("Segoe UI", 26, "bold"),
            fg=TEXT_DARK,
            bg=BG_MAIN
        ).pack(pady=(0, 6))

        tk.Label(
            form,
            text="Fill in the details to get started",
            font=("Segoe UI", 12),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(pady=(0, 26))

        # Name
        tk.Label(form, text="Full Name", font=("Segoe UI", 12, "bold"),
                 fg=TEXT_MID, bg=BG_MAIN).pack(anchor="w")
        name_wrap, self.name_entry = styled_entry(form, width=42)
        name_wrap.pack(fill="x", pady=(6, 16), ipady=4)

        # Email
        tk.Label(form, text="Email Address", font=("Segoe UI", 12, "bold"),
                 fg=TEXT_MID, bg=BG_MAIN).pack(anchor="w")
        email_wrap, self.email_entry = styled_entry(form, width=42)
        email_wrap.pack(fill="x", pady=(6, 16), ipady=4)

        # Password
        tk.Label(form, text="Password", font=("Segoe UI", 12, "bold"),
                 fg=TEXT_MID, bg=BG_MAIN).pack(anchor="w")
        pw_wrap, self.pw_entry = styled_entry(form, show="•", width=42)
        pw_wrap.pack(fill="x", pady=(6, 16), ipady=4)

        # Confirm Password
        tk.Label(form, text="Confirm Password", font=("Segoe UI", 12, "bold"),
                 fg=TEXT_MID, bg=BG_MAIN).pack(anchor="w")
        cpw_wrap, self.cpw_entry = styled_entry(form, show="•", width=42)
        cpw_wrap.pack(fill="x", pady=(6, 28), ipady=4)

        # Submit button
        styled_button(form, "Create Account", self._handle_signup, width=42).pack(fill="x", ipady=6)

        sep = tk.Frame(form, bg=BORDER, height=1)
        sep.pack(fill="x", pady=20)

        row = tk.Frame(form, bg=BG_MAIN)
        row.pack()

        tk.Label(
            row,
            text="Already have an account? ",
            font=("Segoe UI", 12),
            fg=TEXT_MID,
            bg=BG_MAIN
        ).pack(side="left")

        link_label(row, "Sign In", self._go_login).pack(side="left")

    # ── Logic ──────────────────────────────────────────────────────────────────
    def _handle_signup(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.pw_entry.get().strip()
        confirm = self.cpw_entry.get().strip()

        if not all([name, email, password, confirm]):
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return

        if password != confirm:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        if len(password) < 6:
            messagebox.showwarning("Weak Password", "Password must be at least 6 characters.")
            return

        success, result = self.db.register_user(name, email, password)
        if not success:
            messagebox.showerror("Registration Failed", result)
            return

        messagebox.showinfo("Success", f"Welcome, {name}! Your account has been created.")
        self._go_login()

    def _go_login(self):
        self.pack_forget()
        from auth.login_screen import LoginScreen
        LoginScreen(self.master, self.db).pack(fill="both", expand=True)