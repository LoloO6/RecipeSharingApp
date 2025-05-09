document.addEventListener('DOMContentLoaded', () => {
    const recipeId = window.location.pathname.split('/').pop();
    fetch(`/api/recipe/${recipeId}`)
        .then(res => res.json())
        .then(recipe => {
            const container = document.getElementById('recipe-details');
            container.innerHTML = `
                <h1>${recipe.name}</h1>
                <img src="${recipe.image_url}" width="300">
                <h2>Ingredients</h2>
                <ul>${recipe.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>
                <h2>Instructions</h2>
                <ol>${recipe.instructions.map(i => `<li>${i}</li>`).join('')}</ol>
            `;
        });
});