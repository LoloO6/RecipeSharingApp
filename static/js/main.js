document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const recipesContainer = document.getElementById('recipes-container');
    const ingredientContainer = document.querySelector('.ingredient-checkboxes');
    const recipeModal = document.getElementById('recipeImageModal');
    const modalImg = document.getElementById('expandedRecipeImage');
    const closeModal = document.querySelector('.close-recipe-modal');

    // Common ingredients for filters
    const commonIngredients = [
        'egg', 'flour', 'sugar', 'salt', 'butter', 'oil',
        'garlic', 'onion', 'cheese', 'milk', 'chicken',
        'beef', 'tomato', 'pepper', 'pasta', 'rice'
    ];

    function init() {
        setupIngredientFilters();
        setupEventListeners();
        loadRecipes(); // Initial load
    }

    function setupIngredientFilters() {
        commonIngredients.forEach(ing => {
            const div = document.createElement('div');
            div.innerHTML = `
                <input type="checkbox" id="ing-${ing.replace(/\s+/g, '-')}" value="${ing}">
                <label for="ing-${ing.replace(/\s+/g, '-')}">${ing}</label>
            `;
            ingredientContainer.appendChild(div);
        });
    }

    function setupEventListeners() {

        searchBtn.addEventListener('click', loadRecipes);
        searchInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') loadRecipes();
        });

        closeModal.addEventListener('click', () => {
            recipeModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === recipeModal) {
                recipeModal.style.display = 'none';
            }
        });
    }

    function loadRecipes() {
        const searchText = searchInput.value;
        const selectedIngredients = Array.from(
            document.querySelectorAll('.ingredient-checkboxes input:checked')
        ).map(el => el.value);


        const params = new URLSearchParams();
        if (searchText) params.append('search', searchText);
        selectedIngredients.forEach(ing => params.append('ingredient', ing));

        fetch(`/api/recipes?${params.toString()}`)
            .then(res => res.json())
            .then(recipes => {
                renderRecipes(recipes);
                setupImageModals();
            })
            .catch(error => {
                console.error('Error loading recipes:', error);
                recipesContainer.innerHTML =
                    '<p>Error loading recipes. Please try again later.</p>';
            });
    }

    function renderRecipes(recipes) {
        recipesContainer.innerHTML = '';

        if (recipes.length === 0) {
            recipesContainer.innerHTML = '<p>No recipes found matching your criteria.</p>';
            return;
        }

        recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'recipe-card';
            card.innerHTML = `
                <a href="/recipe/${recipe.id}" class="recipe-link">
                    <div class="recipe-image-container">
                        <img src="${recipe.image_url}" alt="${recipe.name}" class="recipe-image">
                    </div>
                    <h2>${recipe.name}</h2>
                </a>
                <div class="recipe-meta">
                    <p><strong>Prep Time:</strong> ${recipe.prep_time} mins</p>
                    <p><strong>Cook Time:</strong> ${recipe.cook_time} mins</p>
                    <p><strong>Servings:</strong> ${recipe.servings}</p>
                </div>
            `;
            recipesContainer.appendChild(card);
        });
    }

    function setupImageModals() {
        document.querySelectorAll('.recipe-image').forEach(img => {
            img.addEventListener('click', function(e) {
                if (e.target === this) {
                    e.preventDefault();
                    recipeModal.style.display = 'flex';
                    modalImg.src = this.src;
                }
            });
        });
    }

    init();
});