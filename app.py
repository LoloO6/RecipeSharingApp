from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__,
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Needed for form security
CORS(app)

# Initial recipes data
recipes = [
    {
        "id": 1,
        "name": "Spaghetti Carbonara",
        "ingredients": ["400g spaghetti", "200g pancetta", "4 eggs", "50g pecorino", "50g parmesan", "Black pepper", "Salt"],
        "instructions": ["Boil pasta", "Fry pancetta", "Mix eggs and cheese", "Combine everything", "Season with pepper"],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "image_url": "/static/images/carbonara.jpg"
    },
    {
        "id": 2,
        "name": "Chocolate Chip Cookies",
        "ingredients": ["250g flour", "170g butter", "150g brown sugar", "100g white sugar", "1 tsp vanilla", "1 egg", "200g chocolate chips"],
        "instructions": ["Preheat oven to 350°F", "Mix dry ingredients", "Cream butter and sugars", "Add egg and vanilla", "Combine all ingredients", "Bake for 10-12 minutes"],
        "prep_time": 15,
        "cook_time": 12,
        "servings": 24,
        "image_url": "/static/images/cookies.jpg"
    },
    {
        "id": 3,
        "name": "Vegetable Stir Fry",
        "ingredients": ["2 tbsp oil", "1 onion", "2 bell peppers", "2 carrots", "1 cup broccoli", "2 garlic cloves", "1 tbsp ginger", "3 tbsp soy sauce"],
        "instructions": ["Heat oil in wok", "Add vegetables", "Stir fry for 5 minutes", "Add garlic and ginger", "Mix in soy sauce"],
        "prep_time": 15,
        "cook_time": 10,
        "servings": 4,
        "image_url": "/static/images/stirfry.jpg"
    }
]

# Helper function to get next ID
def get_next_id():
    return max(recipe['id'] for recipe in recipes) + 1 if recipes else 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    return render_template('recipe.html')

@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        new_recipe = {
            "id": get_next_id(),
            "name": request.form['name'],
            "ingredients": [ing.strip() for ing in request.form['ingredients'].split('\n') if ing.strip()],
            "instructions": [inst.strip() for inst in request.form['instructions'].split('\n') if inst.strip()],
            "prep_time": int(request.form['prep_time']),
            "cook_time": int(request.form['cook_time']),
            "servings": int(request.form['servings']),
            "image_url": request.form['image_url'] or "/static/images/default.jpg"
        }
        recipes.append(new_recipe)
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

# API endpoints remain the same
@app.route('/api/recipes')
def get_recipes():
    search = request.args.get('search', '').lower()
    if search:
        filtered = [r for r in recipes if search in r['name'].lower()]
        return jsonify(filtered)
    return jsonify(recipes)

@app.route('/api/recipe/<int:recipe_id>')
def get_recipe(recipe_id):
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    return jsonify(recipe) if recipe else ('Not found', 404)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    app.run(debug=True)