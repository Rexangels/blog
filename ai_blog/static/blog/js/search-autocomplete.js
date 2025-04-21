/**
 * Search Autocomplete Implementation
 * 
 * This script handles the autocomplete functionality for the search input field.
 * It sends AJAX requests to the server as the user types and displays matching results.
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = searchInput ? searchInput.closest('form') : null;
    
    if (!searchInput || !searchForm) return;
    
    // Create container for autocomplete results
    const autocompleteContainer = document.createElement('div');
    autocompleteContainer.classList.add('search-autocomplete-container');
    searchForm.appendChild(autocompleteContainer);
    
    let debounceTimer;
    const debounceDelay = 300; // ms delay between keystrokes before sending request
    
    // Handle input event on search field
    searchInput.addEventListener('input', function() {
        // Clear previous timeout
        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }
        
        const query = this.value.trim();
        
        // Hide autocomplete if query is empty
        if (!query) {
            autocompleteContainer.innerHTML = '';
            autocompleteContainer.style.display = 'none';
            return;
        }
        
        // Set timeout for debounce
        debounceTimer = setTimeout(function() {
            // Send AJAX request
            fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Clear previous results
                    autocompleteContainer.innerHTML = '';
                    
                    if (data.results && data.results.length > 0) {
                        // Create result items
                        data.results.forEach(result => {
                            const resultItem = document.createElement('div');
                            resultItem.classList.add('search-autocomplete-item');
                            
                            resultItem.innerHTML = `
                                <a href="${result.url}">
                                    <div class="search-result-title">${result.title}</div>
                                    <div class="search-result-snippet">${result.snippet}</div>
                                </a>
                            `;
                            
                            autocompleteContainer.appendChild(resultItem);
                        });
                        
                        autocompleteContainer.style.display = 'block';
                    } else {
                        autocompleteContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Search autocomplete error:', error);
                    autocompleteContainer.style.display = 'none';
                });
        }, debounceDelay);
    });
    
    // Close autocomplete when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchForm.contains(event.target)) {
            autocompleteContainer.style.display = 'none';
        }
    });
    
    // Close autocomplete when pressing Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            autocompleteContainer.style.display = 'none';
        }
    });
});