// JavaScript for doctor search functionality

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('doctor-search-form');
    const specialtyField = document.getElementById('specialty');
    const locationField = document.getElementById('location');
    const nameField = document.getElementById('doctor-name');
    const resultsContainer = document.getElementById('search-results');
    
    // Function to fetch search results via AJAX
    function fetchSearchResults() {
        const specialty = specialtyField.value;
        const location = locationField.value;
        const name = nameField.value;
        
        // Don't perform search if all fields are empty
        if (!specialty && !location && !name) {
            return;
        }
        
        // Show loading state
        resultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Construct query parameters
        const params = new URLSearchParams();
        if (specialty) params.append('specialty', specialty);
        if (location) params.append('location', location);
        if (name) params.append('name', name);
        
        // Fetch results
        fetch(`/search/ajax/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                renderSearchResults(data);
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                resultsContainer.innerHTML = '<div class="alert alert-danger">Error fetching results. Please try again.</div>';
            });
    }
    
    // Function to render search results
    function renderSearchResults(doctors) {
        if (doctors.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No doctors found matching your criteria. Please try a different search.</div>';
            return;
        }
        
        let html = '';
        
        doctors.forEach(doctor => {
            html += `
                <div class="card search-result-item">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h5 class="card-title">${doctor.name}</h5>
                                <div class="specialty-badge mb-2">${doctor.specialty}</div>
                                <p><i class="fas fa-map-marker-alt"></i> ${doctor.location}</p>
                                <p><i class="fas fa-user-md"></i> ${doctor.years_experience} years of experience</p>
                            </div>
                            <div class="col-md-4 text-end">
                                <a href="${doctor.profile_url}" class="btn btn-outline-primary">View Profile</a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        resultsContainer.innerHTML = html;
    }
    
    // Event listeners for live search
    if (searchForm) {
        // Debounce function to limit how often search is performed
        function debounce(func, wait) {
            let timeout;
            return function() {
                const context = this;
                const args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    func.apply(context, args);
                }, wait);
            };
        }
        
        const debouncedSearch = debounce(fetchSearchResults, 500);
        
        specialtyField.addEventListener('change', debouncedSearch);
        locationField.addEventListener('input', debouncedSearch);
        nameField.addEventListener('input', debouncedSearch);
        
        // Initial search on page load
        if (specialtyField.value || locationField.value || nameField.value) {
            fetchSearchResults();
        }
        
        // Prevent form submission (we're using AJAX instead)
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            fetchSearchResults();
        });
    }
});
