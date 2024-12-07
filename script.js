document.getElementById('recommendation-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Get user input values
    const ingredients = document.getElementById('ingredients').value;
    const maxCalories = document.getElementById('max-calories').value || null;

    // Send AJAX request to Flask backend
    fetch('http://127.0.0.1:5000/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ingredients: ingredients,
            max_calories: maxCalories
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Recommendations:', data); // Log the response data for debugging
        
        // Display recommendations
        const recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = ''; // Clear previous recommendations
        
        if (data.length === 0) {
            recommendationsDiv.innerHTML = '<p>No recipes found with the given criteria.</p>';
        } else {
            data.forEach(recipe => {
                const recipeDiv = document.createElement('div');
                recipeDiv.classList.add('recipe');
                recipeDiv.innerHTML = `
                    <h2>${recipe.recipe_name}</h2>
                    <p><strong>Average Rating:</strong> ${recipe.aver_rate}</p>
                    <p><strong>Ingredients:</strong> ${recipe.ingredients_list}</p>
                    <p><strong>Calories:</strong> ${recipe.calories}</p>
                `;
                recommendationsDiv.appendChild(recipeDiv);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching recommendations:', error);
        const recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = '<p>There was an error processing your request. Please try again later.</p>';
    });
});
