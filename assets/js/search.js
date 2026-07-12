let searchIndex = [];

// Fetch the search index
fetch('/searchIndex.json')
    .then(response => response.json())
    .then(data => {
        searchIndex = data;
    })
    .catch(err => console.error("Could not load search index", err));

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchResults) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }
            
            const results = searchIndex.filter(article => {
                return (article.title && article.title.toLowerCase().includes(query)) ||
                       (article.description && article.description.toLowerCase().includes(query));
            }).slice(0, 5); // top 5 results
            
            if (results.length > 0) {
                searchResults.innerHTML = results.map(r => `
                    <div class="search-result-item">
                        <a href="${r.url}"><strong>${r.title}</strong></a>
                        <p style="font-size:0.8rem; margin:0;">${r.description}</p>
                    </div>
                `).join('');
                searchResults.classList.add('active');
            } else {
                searchResults.innerHTML = '<div class="search-result-item">No results found.</div>';
                searchResults.classList.add('active');
            }
        });

        // Hide search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });
    }
});
