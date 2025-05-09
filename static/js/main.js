document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/recipes')
        .then(res => res.json())
        .then(recipes => {
            const container = document.getElementById('recipes-container');

            if (recipes.length === 0) {
                container.innerHTML = '<p>No recipes found. Add one!</p>';
                return;
            }

            recipes.forEach(recipe => {
                const card = document.createElement('div');
                card.className = 'recipe-card';
                card.innerHTML = `
                    <h2><a href="/recipe/${recipe.id}">${recipe.name}</a></h2>
                    <img src="${recipe.image_url}" width="200">
                    <p><strong>Prep Time:</strong> ${recipe.prep_time} mins</p>
                    <p><strong>Cook Time:</strong> ${recipe.cook_time} mins</p>
                    <p><strong>Servings:</strong> ${recipe.servings}</p>
                `;
                container.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error loading recipes:', error);
            document.getElementById('recipes-container').innerHTML =
                '<p>Error loading recipes. Please try again later.</p>';
        });
});