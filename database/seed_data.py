def seed(db):
    conn = db._connect()
    existing = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    conn.close()

    if existing > 0:
        return  

    _seed_categories(db)
    _seed_admin(db)
    _seed_recipes(db)
    print("[DB] Database seeded successfully.")


# ─── Categories ────────────────────────────────────────────────────────────────
def _seed_categories(db):
    categories = [
        ("Breakfast", "🍳"),
        ("Lunch",     "🥗"),
        ("Dinner",    "🥪"),
        ("Desserts",  "🍰"),
        ("Vegetarian","🥦"),
        ("Snacks",    "🥪"),
        ("Drinks",    "🥤"),
    ]
    conn = db._connect()
    conn.executemany("INSERT INTO categories (name, icon) VALUES (?,?)", categories)
    conn.commit()
    conn.close()


# ─── Admin Account ─────────────────────────────────────────────────────────────
def _seed_admin(db):
    conn = db._connect()
    conn.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
        ("Admin", "admin@recipe.com", db.hash_password("admin123"), "admin")
    )
    conn.commit()
    conn.close()


# ─── Sample Recipes ────────────────────────────────────────────────────────────
def _seed_recipes(db):
    conn = db._connect()

    # Fetch category IDs
    cats = {row["name"]: row["id"]
            for row in conn.execute("SELECT id, name FROM categories")}
    conn.close()

    recipes = [
        # Breakfast
        (
            "Classic Pancakes", cats["Breakfast"],
            "1 cup flour\n1 tbsp sugar\n1 tsp baking powder\n1/2 tsp salt\n"
            "1 cup milk\n1 egg\n2 tbsp butter",
            "1. Mix dry ingredients.\n2. Whisk wet ingredients separately.\n"
            "3. Combine until smooth.\n4. Cook on greased pan 2 min per side.",
            ""
        ),
        (
            "Avocado Toast", cats["Breakfast"],
            "2 slices bread\n1 avocado\nSalt & pepper\nChili flakes\nLemon juice",
            "1. Toast the bread.\n2. Mash avocado with lemon, salt & pepper.\n"
            "3. Spread on toast and top with chili flakes.",
            ""
        ),
        # Lunch
        (
            "Caesar Salad", cats["Lunch"],
            "Romaine lettuce\nCaesar dressing\nCroutons\nParmesan cheese\nBlack pepper",
            "1. Chop lettuce.\n2. Toss with dressing.\n3. Add croutons and parmesan.",
            ""
        ),
        (
            "Chicken Wrap", cats["Lunch"],
            "Tortilla wrap\n150g grilled chicken\nLettuce\nTomato\nYogurt sauce",
            "1. Grill chicken and slice.\n2. Layer ingredients on wrap.\n3. Roll tightly and serve.",
            ""
        ),
        # Dinner
        (
            "Spaghetti Bolognese", cats["Dinner"],
            "300g spaghetti\n250g minced beef\n1 can tomatoes\n1 onion\n2 garlic cloves\nOlive oil",
            "1. Sauté onion and garlic.\n2. Brown the meat.\n3. Add tomatoes and simmer 20 min.\n"
            "4. Cook pasta and combine.",
            ""
        ),
        (
            "Grilled Salmon", cats["Dinner"],
            "2 salmon fillets\nOlive oil\nLemon\nGarlic\nDill\nSalt & pepper",
            "1. Season salmon with oil, lemon and spices.\n2. Grill 4 min each side.\n"
            "3. Serve with vegetables.",
            ""
        ),
        # Desserts
        (
            "Chocolate Brownie", cats["Desserts"],
            "100g dark chocolate\n80g butter\n2 eggs\n150g sugar\n70g flour\n1 tsp vanilla",
            "1. Melt chocolate and butter.\n2. Whisk eggs and sugar.\n3. Fold in chocolate mixture and flour.\n"
            "4. Bake at 180°C for 25 min.",
            ""
        ),
        (
            "Fruit Salad", cats["Desserts"],
            "Strawberries\nMango\nKiwi\nGrapes\nOrange juice\nMint",
            "1. Chop all fruits.\n2. Mix with orange juice.\n3. Garnish with mint and chill.",
            ""
        ),
        # Vegetarian
        (
            "Veggie Stir-Fry", cats["Vegetarian"],
            "Broccoli\nBell peppers\nCarrots\nSoy sauce\nGarlic\nSesame oil\nRice",
            "1. Heat oil in wok.\n2. Stir-fry garlic then add vegetables.\n"
            "3. Add soy sauce and cook 5 min.\n4. Serve over rice.",
            ""
        ),
        # Snacks
        (
            "Hummus & Pita", cats["Snacks"],
            "1 can chickpeas\n2 tbsp tahini\nLemon juice\nGarlic\nOlive oil\nPita bread",
            "1. Blend chickpeas, tahini, lemon and garlic.\n2. Drizzle with olive oil.\n"
            "3. Serve with warm pita.",
            ""
        ),
        # Drinks
        (
            "Mango Smoothie", cats["Drinks"],
            "1 mango\n1 cup milk\n2 tbsp yogurt\n1 tbsp honey\nIce cubes",
            "1. Peel and chop mango.\n2. Blend all ingredients until smooth.\n3. Pour and serve cold.",
            ""
        ),
    ]

    db_conn = db._connect()
    db_conn.executemany(
        "INSERT INTO recipes (title, category_id, ingredients, instructions, image_url) "
        "VALUES (?,?,?,?,?)",
        recipes
    )
    db_conn.commit()
    db_conn.close()
