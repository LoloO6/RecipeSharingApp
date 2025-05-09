from flask import Flask, render_template, request, redirect, url_for, g, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__,
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# Database Configuration
DATABASE = 'recipes.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            prep_time INTEGER NOT NULL,
            cook_time INTEGER NOT NULL,
            servings INTEGER NOT NULL,
            image_url TEXT,
            instructions TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
            PRIMARY KEY (recipe_id, ingredient_id)
        )
        ''')

        # Insert initial data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM recipes")
        if cursor.fetchone()[0] == 0:
            initial_recipes = [
                {
                    "name": "Spaghetti Carbonara",
                    "ingredients": ["spaghetti", "pancetta", "eggs", "pecorino", "parmesan", "black pepper", "salt"],
                    "instructions": "Boil pasta\nFry pancetta\nMix eggs and cheese\nCombine everything\nSeason with pepper",
                    "prep_time": 10,
                    "cook_time": 15,
                    "servings": 4,
                    "image_url": "/static/images/carbonara.jpg"
                },
                {
                    "name": "Chocolate Chip Cookies",
                    "ingredients": ["flour", "butter", "brown sugar", "white sugar", "vanilla", "egg",
                                    "chocolate chips"],
                    "instructions": "Preheat oven to 350°F\nMix dry ingredients\nCream butter and sugars\nAdd egg and vanilla\nCombine all ingredients\nBake for 10-12 minutes",
                    "prep_time": 15,
                    "cook_time": 12,
                    "servings": 24,
                    "image_url": "/static/images/cookies.jpg"
                }
            ]

            for recipe in initial_recipes:
                cursor.execute('''
                INSERT INTO recipes (name, prep_time, cook_time, servings, image_url, instructions)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    recipe['name'],
                    recipe['prep_time'],
                    recipe['cook_time'],
                    recipe['servings'],
                    recipe['image_url'],
                    recipe['instructions']
                ))
                recipe_id = cursor.lastrowid

                for ingredient_name in recipe['ingredients']:
                    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient_name,))
                    ingredient = cursor.fetchone()

                    if not ingredient:
                        cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (ingredient_name,))
                        ingredient_id = cursor.lastrowid
                    else:
                        ingredient_id = ingredient['id']

                    cursor.execute('''
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
                    VALUES (?, ?)
                    ''', (recipe_id, ingredient_id))

            db.commit()

init_db()


# Routes
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, prep_time, cook_time, servings, image_url FROM recipes')
    recipes = cursor.fetchall()
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    db = get_db()
    cursor = db.cursor()

    # Get recipe details
    cursor.execute('''
    SELECT id, name, prep_time, cook_time, servings, image_url, instructions
    FROM recipes
    WHERE id = ?
    ''', (recipe_id,))
    recipe = cursor.fetchone()

    if not recipe:
        return "Recipe not found", 404

    # Get ingredients
    cursor.execute('''
    SELECT i.name
    FROM ingredients i
    JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
    WHERE ri.recipe_id = ?
    ''', (recipe_id,))
    ingredients = [row['name'] for row in cursor.fetchall()]

    # Convert instructions to list
    instructions = recipe['instructions'].split('\n')

    return render_template('recipe.html',
                           recipe=dict(recipe),
                           ingredients=ingredients,
                           instructions=instructions)
@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('''
            INSERT INTO recipes (name, prep_time, cook_time, servings, image_url, instructions)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form['name'],
                int(request.form['prep_time']),
                int(request.form['cook_time']),
                int(request.form['servings']),
                request.form['image_url'] or "/static/images/default.gif",
                request.form['instructions']
            ))
            recipe_id = cursor.lastrowid

            ingredients = [ing.strip() for ing in request.form['ingredients'].split('\n') if ing.strip()]
            for ingredient_name in ingredients:
                cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient_name,))
                ingredient = cursor.fetchone()

                if not ingredient:
                    cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (ingredient_name,))
                    ingredient_id = cursor.lastrowid
                else:
                    ingredient_id = ingredient['id']

                cursor.execute('''
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
                VALUES (?, ?)
                ''', (recipe_id, ingredient_id))

            db.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            return f"An error occurred: {str(e)}", 500

    return render_template('add_recipe.html')


# API Endpoints
@app.route('/api/recipes')
def api_recipes():
    search = request.args.get('search', '').lower()
    ingredients = request.args.getlist('ingredient')

    db = get_db()
    cursor = db.cursor()

    query = '''
    SELECT r.id, r.name, r.prep_time, r.cook_time, r.servings, r.image_url
    FROM recipes r
    '''

    params = []

    if ingredients:
        query += '''
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE i.name IN ({})
        '''.format(','.join(['?'] * len(ingredients)))
        params.extend(ingredients)

        if search:
            query += ' AND r.name LIKE ?'
            params.append(f'%{search}%')
    elif search:
        query += ' WHERE r.name LIKE ?'
        params.append(f'%{search}%')

    query += ' GROUP BY r.id'

    if ingredients:
        query += ' HAVING COUNT(DISTINCT i.name) = ?'
        params.append(len(ingredients))

    cursor.execute(query, params)
    recipes = cursor.fetchall()

    return jsonify([dict(recipe) for recipe in recipes])

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    app.run(debug=True)