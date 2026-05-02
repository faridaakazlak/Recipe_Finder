import tkinter as tk
from database.db_manager import DatabaseManager
from auth.login_screen import LoginScreen


def main():
    root = tk.Tk()
    root.title("Recipe Finder")
    root.geometry("1200x750")
    root.minsize(1100, 680)
    root.resizable(True, True)
    root.configure(bg="#FFF8F0")

    db = DatabaseManager()
    db.initialize()

    app = LoginScreen(root, db)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()