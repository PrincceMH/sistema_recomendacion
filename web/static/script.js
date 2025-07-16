// Estado global de la aplicación
let appState = {
    userType: 'existing',
    currentUser: null,
    userRatings: {},
    knnResults: null,
    recommendations: [],
    neighbors: [],
    movies: [],
    stats: {
        executionTime: 0,
        totalNeighbors: 0,
        totalRecommendations: 0
    }
};

// Configuración de la API
const API_BASE_URL = 'http://localhost:5000';

// Función para cambiar entre tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// Función para cambiar tipo de usuario
function toggleUserType() {
    const userType = document.querySelector('input[name="user-type"]:checked').value;
    appState.userType = userType;
    
    const existingSection = document.getElementById('existing-user-section');
    const newSection = document.getElementById('new-user-section');
    
    if (userType === 'existing') {
        existingSection.style.display = 'block';
        newSection.style.display = 'none';
    } else {
        existingSection.style.display = 'none';
        newSection.style.display = 'block';
        loadSampleMovies();
    }
}

// Función para conectar con el backend Python
async function connectToPythonBackend(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error conectando con Python backend:', error);
        throw error;
    }
}

// Función para cargar usuarios disponibles
async function loadAvailableUsers() {
    try {
        showAlert('Cargando usuarios disponibles...', 'info');
        const response = await connectToPythonBackend('get_users', {});
        
        if (response.users && response.users.length > 0) {
            const usersList = response.users.slice(0, 10); // Mostrar solo los primeros 10
            showAlert(`Usuarios disponibles: ${usersList.join(', ')}`, 'success');
        } else {
            showAlert('No se pudieron cargar los usuarios.', 'error');
        }
        
    } catch (error) {
        console.error('Error cargando usuarios:', error);
        showAlert('Error al conectar con el servidor. Intenta más tarde.', 'error');
    }
}

// Función para cargar películas de muestra
async function loadSampleMovies() {
    try {
        const response = await connectToPythonBackend('get_sample_movies', {});
        if (response.movies) {
            displayMovieSuggestions(response.movies);
        }
    } catch (error) {
        console.error('Error cargando películas:', error);
        // Usar datos de muestra como fallback
        const sampleMovies = [
            { movieId: 1, title: "Toy Story (1995)", genres: "Adventure|Animation|Children|Comedy|Fantasy" },
            { movieId: 2, title: "Jumanji (1995)", genres: "Adventure|Children|Fantasy" },
            { movieId: 3, title: "Grumpier Old Men (1995)", genres: "Comedy|Romance" },
            { movieId: 4, title: "Waiting to Exhale (1995)", genres: "Comedy|Drama|Romance" },
            { movieId: 5, title: "Father of the Bride Part II (1995)", genres: "Comedy" }
        ];
        displayMovieSuggestions(sampleMovies);
    }
}

// Función para mostrar sugerencias de películas
function displayMovieSuggestions(movies) {
    const container = document.getElementById('movie-suggestions');
    container.innerHTML = '';
    
    movies.forEach(movie => {
        const movieCard = createMovieCard(movie);
        container.appendChild(movieCard);
    });
    
    container.style.display = 'grid';
}

// Función para crear una tarjeta de película
function createMovieCard(movie, showRating = false) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    
    const rating = appState.userRatings[movie.movieId] || 0;
    
    card.innerHTML = `
        <div class="movie-title">${movie.title}</div>
        <div class="movie-rating">
            <span>Tu calificación:</span>
            <div class="rating-stars">
                ${[1, 2, 3, 4, 5].map(star => 
                    `<span class="star ${rating >= star ? 'filled' : ''}" 
                          onclick="rateMovie(${movie.movieId}, ${star})">★</span>`
                ).join('')}
            </div>
            <span>${rating > 0 ? rating : 'Sin calificar'}</span>
        </div>
        ${showRating ? `<div class="predicted-rating">Predicción: ${movie.predictedRating || 'N/A'}</div>` : ''}
    `;
    
    return card;
}

// Función para calificar una película
function rateMovie(movieId, rating) {
    appState.userRatings[movieId] = rating;
    
    // Actualizar las estrellas
    const movieCard = event.target.closest('.movie-card');
    const stars = movieCard.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.classList.toggle('filled', index < rating);
    });
    
    // Actualizar el texto de calificación
    const ratingText = movieCard.querySelector('.movie-rating span:last-child');
    ratingText.textContent = rating;
    
    // Actualizar la sección de películas calificadas
    updateRatedMovies();
}

// Función para actualizar películas calificadas
function updateRatedMovies() {
    const container = document.getElementById('rated-movies');
    container.innerHTML = '';
    
    Object.keys(appState.userRatings).forEach(movieId => {
        const rating = appState.userRatings[movieId];
        if (rating > 0) {
            const card = document.createElement('div');
            card.className = 'movie-card';
            card.innerHTML = `
                <div class="movie-title">Película ${movieId}</div>
                <div class="movie-rating">
                    <span>Tu calificación:</span>
                    <div class="rating-stars">
                        ${[1, 2, 3, 4, 5].map(star => 
                            `<span class="star ${rating >= star ? 'filled' : ''}">★</span>`
                        ).join('')}
                    </div>
                    <span>${rating}</span>
                </div>
            `;
            container.appendChild(card);
        }
    });
}

// Función para buscar películas
async function searchMovies() {
    const searchTerm = document.getElementById('movie-search').value.toLowerCase();
    const container = document.getElementById('movie-suggestions');
    
    if (searchTerm.length < 2) {
        container.style.display = 'none';
        return;
    }
    
    try {
        const response = await connectToPythonBackend('search_movies', { query: searchTerm });
        if (response.movies && response.movies.length > 0) {
            displayMovieSuggestions(response.movies);
        } else {
            container.style.display = 'none';
        }
    } catch (error) {
        console.error('Error buscando películas:', error);
    }
}

// Función para cargar usuario existente
async function loadExistingUser() {
    const userId = document.getElementById('user-id').value;
    
    if (!userId) {
        showAlert('Por favor, ingresa un ID de usuario válido.', 'error');
        return;
    }
    
    try {
        const response = await connectToPythonBackend('validate_user', { user_id: parseInt(userId) });
        
        if (response.valid) {
            appState.currentUser = parseInt(userId);
            showAlert(`Usuario ${userId} cargado exitosamente.`, 'success');
            switchTab('knn-config');
        } else {
            showAlert('El usuario no existe en la base de datos.', 'error');
        }
    } catch (error) {
        console.error('Error validando usuario:', error);
        // Asumir que el usuario es válido si hay error de conexión
        appState.currentUser = parseInt(userId);
        showAlert(`Usuario ${userId} cargado (modo offline).`, 'info');
        switchTab('knn-config');
    }
}

// Función para ejecutar KNN
async function runKNN()
{
    const k = parseInt(document.getElementById('k-value').value);
    const distanceType = document.getElementById('distance-type').value;
    const threshold = parseFloat(document.getElementById('rating-threshold').value);
    
    if (appState.userType === 'new' && Object.keys(appState.userRatings).length === 0) {
        showAlert('Por favor, califica al menos una película antes de ejecutar KNN.', 'error');
        return;
    }
    
    if (appState.userType === 'existing' && !appState.currentUser) {
        showAlert('Por favor, carga un usuario existente primero.', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const requestData = {
            user_type: appState.userType,
            user_id: appState.currentUser,
            user_ratings: appState.userRatings,
            k: k,
            distance_type: distanceType,
            threshold: threshold
        };
        
        const results = await connectToPythonBackend('run_knn', requestData);
        displayResults(results);
        switchTab('results');
        
    } catch (error) {
        console.error('Error ejecutando KNN:', error);
        showAlert('Error al ejecutar KNN. Intenta nuevamente.', 'error');
    }

}
    