import sqlite3
import hashlib
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "recipe_finder.db")


class DatabaseManager:

    def __init__(self):
        self.db_path = DB_PATH

    # ── Connection ─────────────────────────────────────────────────────────────
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Setup ──────────────────────────────────────────────────────────────────
    def initialize(self):

        conn = self._connect()
        cur = conn.cursor()

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT      NOT NULL,
                email      TEXT      NOT NULL UNIQUE,
                password   TEXT      NOT NULL,
                role       TEXT      NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL UNIQUE,
                icon TEXT    DEFAULT '🍽️'
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT      NOT NULL,
                category_id  INTEGER   NOT NULL REFERENCES categories(id),
                ingredients  TEXT      NOT NULL,
                instructions TEXT      NOT NULL,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS favorites (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL REFERENCES users(id),
                recipe_id INTEGER NOT NULL REFERENCES recipes(id),
                UNIQUE(user_id, recipe_id)
            );
        """)

        try:
            existing_user_cols = {row[1] for row in cur.execute("PRAGMA table_info(users)")}
            if "created_at" not in existing_user_cols:
                cur.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except Exception:
            pass


        conn.commit()
        conn.close()

        from database.seed_data import seed
        seed(self)

    # ── Password ───────────────────────────────────────────────────────────────
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # ── Auth ───────────────────────────────────────────────────────────────────
    def register_user(self, name, email, password):
        try:
            conn = self._connect()
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
                (name, email, self.hash_password(password), "user")
            )
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            conn.close()
            return True, dict(user)
        except sqlite3.IntegrityError:
            return False, "Email already registered."

    def login_user(self, email, password):
        conn = self._connect()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not user:
            return False, "Email not found."
        if user["password"] != self.hash_password(password):
            return False, "Incorrect password."
        return True, dict(user)

    # ── Users ──────────────────────────────────────────────────────────────────
    def get_all_users(self):
        conn = self._connect()
        rows = conn.execute("SELECT * FROM users WHERE role='user'").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_user(self, user_id):
        conn = self._connect()
        conn.execute("DELETE FROM favorites WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    def count_users(self):
        conn = self._connect()
        count = conn.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
        conn.close()
        return count

    # ── Categories ─────────────────────────────────────────────────────────────
    def get_all_categories(self):
        conn = self._connect()
        rows = conn.execute("SELECT * FROM categories").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Recipes ────────────────────────────────────────────────────────────────
    def get_recipes_by_category(self, category_id, search=""):
        conn = self._connect()
        query = """
            SELECT r.*, c.name AS category_name
            FROM recipes r JOIN categories c ON r.category_id = c.id
            WHERE r.category_id=? AND r.title LIKE ?
        """
        rows = conn.execute(query, (category_id, f"%{search}%")).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_recipes(self, search=""):
        conn = self._connect()
        rows = conn.execute(
            "SELECT r.*, c.name AS category_name FROM recipes r "
            "JOIN categories c ON r.category_id=c.id WHERE r.title LIKE ?",
            (f"%{search}%",)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_recipe(self, title, category_id, ingredients, instructions):
        conn = self._connect()
        conn.execute(
            "INSERT INTO recipes (title, category_id, ingredients, instructions) "
            "VALUES (?,?,?,?)",
            (title, category_id, ingredients, instructions)
        )
        conn.commit()
        conn.close()

    def update_recipe(self, recipe_id, title, category_id, ingredients, instructions):
        conn = self._connect()
        conn.execute(
            "UPDATE recipes SET title=?, category_id=?, ingredients=?, "
            "instructions=? WHERE id=?",
            (title, category_id, ingredients, instructions, recipe_id)
        )
        conn.commit()
        conn.close()

    def delete_recipe(self, recipe_id):
        conn = self._connect()
        conn.execute("DELETE FROM favorites WHERE recipe_id=?", (recipe_id,))
        conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        conn.commit()
        conn.close()

    def count_recipes(self):
        conn = self._connect()
        count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        conn.close()
        return count

    # ── Favorites ──────────────────────────────────────────────────────────────
    def add_favorite(self, user_id, recipe_id):
        try:
            conn = self._connect()
            conn.execute("INSERT INTO favorites (user_id, recipe_id) VALUES (?,?)",
                         (user_id, recipe_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_favorite(self, user_id, recipe_id):
        conn = self._connect()
        conn.execute("DELETE FROM favorites WHERE user_id=? AND recipe_id=?",
                     (user_id, recipe_id))
        conn.commit()
        conn.close()

    def get_favorites(self, user_id):
        conn = self._connect()
        rows = conn.execute(
            "SELECT r.*, c.name AS category_name FROM recipes r "
            "JOIN categories c ON r.category_id=c.id "
            "JOIN favorites f ON f.recipe_id=r.id WHERE f.user_id=?",
            (user_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def is_favorite(self, user_id, recipe_id):
        conn = self._connect()
        row = conn.execute(
            "SELECT 1 FROM favorites WHERE user_id=? AND recipe_id=?",
            (user_id, recipe_id)
        ).fetchone()
        conn.close()
        return row is not None
    # ── Admin Compatibility Methods ─────────────────────────────────────────

    def get_recipe_count(self):
        return self.count_recipes()

    def get_user_count(self):
        return self.count_users()

    def get_favorites_count(self):
        conn = self._connect()
        count = conn.execute(
            "SELECT COUNT(*) FROM favorites"
        ).fetchone()[0]
        conn.close()
        return count

    def get_recipe_by_id(self, recipe_id):
        conn = self._connect()
        row = conn.execute(
            """
            SELECT r.*, c.name AS category_name
            FROM recipes r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id=?
            """,
            (recipe_id,)
        ).fetchone()
        conn.close()

        if not row:
            return None

        recipe = dict(row)

        recipe["name"] = recipe["title"]
        recipe["category"] = recipe["category_name"]

        return recipe

    def get_user_by_id(self, user_id):
        conn = self._connect()
        row = conn.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        ).fetchone()
        conn.close()

        if not row:
            return None

        user = dict(row)

        user["username"] = user["name"]
        user["is_admin"] = user["role"] == "admin"

        return user

    def get_admin_count(self):
        conn = self._connect()
        count = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role='admin'"
        ).fetchone()[0]
        conn.close()
        return count

    def get_user_favorites_count(self, user_id):
        conn = self._connect()
        count = conn.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id=?",
            (user_id,)
        ).fetchone()[0]
        conn.close()
        return count