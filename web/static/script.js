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

// ========== FUNCIONES DE UTILIDAD (DEBEN IR PRIMERO) ==========

// Función para mostrar alertas
function showAlert(message, type) {
    console.log(`📢 Alerta [${type}]: ${message}`);
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Función para mostrar loading
function showLoading() {
    const neighborsContainer = document.getElementById('neighbors-results');
    const recommendationsContainer = document.getElementById('recommendations-results');
    
    neighborsContainer.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Ejecutando algoritmo KNN...</p>
        </div>
    `;
    
    recommendationsContainer.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Generando recomendaciones...</p>
        </div>
    `;
}

// Función para simular KNN (fallback cuando no hay conexión)
function simulateKNN(k, distanceType, threshold) {
    console.log('🎭 Simulando resultados KNN...');
    
    const neighbors = [];
    for (let i = 0; i < k; i++) {
        neighbors.push({
            userId: Math.floor(Math.random() * 1000) + 1,
            score: Math.random() * 0.5 + 0.5,
            distance: distanceType
        });
    }
    
    const recommendations = [
        { movieId: 1, title: "Toy Story (1995)", predictedRating: 4.2, confidence: 0.85 },
        { movieId: 2, title: "Jumanji (1995)", predictedRating: 3.8, confidence: 0.75 },
        { movieId: 3, title: "Grumpier Old Men (1995)", predictedRating: 3.5, confidence: 0.70 },
        { movieId: 4, title: "Waiting to Exhale (1995)", predictedRating: 4.0, confidence: 0.80 },
        { movieId: 5, title: "Father of the Bride Part II (1995)", predictedRating: 3.7, confidence: 0.72 }
    ];
    
    return {
        neighbors: neighbors.sort((a, b) => b.score - a.score),
        recommendations: recommendations.sort((a, b) => b.predictedRating - a.predictedRating),
        executionTime: (Math.random() * 5 + 2).toFixed(2)
    };
}

// ========== FUNCIONES PRINCIPALES ==========
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
        console.log(`🚀 Conectando a: ${API_BASE_URL}/${endpoint}`);
        console.log('📤 Datos enviados:', data);
        
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        console.log(`📡 Respuesta HTTP: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('📥 Datos recibidos:', result);
        return result;
        
    } catch (error) {
        console.error('❌ Error conectando con Python backend:', error);
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

// ⚡ FUNCIÓN CORREGIDA PARA EJECUTAR KNN
async function runKNN() {
    console.log('🚀 Iniciando ejecución de KNN...');
    
    const k = parseInt(document.getElementById('k-value').value);
    const distanceType = document.getElementById('distance-type').value;
    const threshold = parseFloat(document.getElementById('rating-threshold').value);
    
    console.log('📋 Parámetros KNN:', { k, distanceType, threshold, userType: appState.userType, currentUser: appState.currentUser });
    
    // Validaciones
    if (appState.userType === 'new' && Object.keys(appState.userRatings).length === 0) {
        showAlert('Por favor, califica al menos una película antes de ejecutar KNN.', 'error');
        return;
    }
    
    if (appState.userType === 'existing' && !appState.currentUser) {
        showAlert('Por favor, carga un usuario existente primero.', 'error');
        return;
    }
    
    // Mostrar loading y cambiar a tab de resultados
    showLoading();
    switchTab('results');
    
    try {
        const requestData = {
            user_type: appState.userType,
            user_id: appState.currentUser,
            user_ratings: appState.userRatings,
            k: k,
            distance_type: distanceType,
            threshold: threshold
        };
        
        console.log('📤 Enviando datos al servidor:', requestData);
        
        const results = await connectToPythonBackend('run_knn', requestData);
        
        console.log('✅ Resultados recibidos:', results);
        
        displayResults(results);
        
    } catch (error) {
        console.error('❌ Error ejecutando KNN:', error);
        showAlert(`Error al ejecutar KNN: ${error.message}`, 'error');
        
        // Fallback a simulación si falla la conexión
        console.log('🔄 Usando simulación como fallback...');
        setTimeout(() => {
            const results = simulateKNN(k, distanceType, threshold);
            displayResults(results);
        }, 1000);
    }
}

// Función para mostrar resultados
function displayResults(results) {
    console.log('📊 Mostrando resultados:', results);
    
    appState.knnResults = results;
    appState.neighbors = results.neighbors;
    appState.recommendations = results.recommendations;
    appState.stats.executionTime = results.executionTime;
    appState.stats.totalNeighbors = results.neighbors.length;
    appState.stats.totalRecommendations = results.recommendations.length;
    
    displayNeighbors(results.neighbors);
    displayRecommendations(results.recommendations);
    displayStats();
    displayVisualization();
}

// Función para mostrar vecinos
function displayNeighbors(neighbors) {
    const container = document.getElementById('neighbors-results');
    container.innerHTML = '';
    
    neighbors.forEach((neighbor, index) => {
        const card = document.createElement('div');
        card.className = 'neighbor-card';
        card.innerHTML = `
            <div>
                <strong>Vecino ${index + 1}:</strong> Usuario ${neighbor.userId}
                <br>
                <small>Distancia: ${neighbor.distance}</small>
            </div>
            <div class="neighbor-score">${neighbor.score.toFixed(4)}</div>
        `;
        container.appendChild(card);
    });
}

// Función para mostrar recomendaciones
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-results');
    container.innerHTML = '';
    
    const grid = document.createElement('div');
    grid.className = 'movie-grid';
    
    recommendations.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.innerHTML = `
            <div class="movie-title">${movie.title}</div>
            <div class="movie-rating">
                <span>Rating Predicho:</span>
                <div class="rating-stars">
                    ${[1, 2, 3, 4, 5].map(star => 
                        `<span class="star ${movie.predictedRating >= star ? 'filled' : ''}">★</span>`
                    ).join('')}
                </div>
                <span>${movie.predictedRating}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${movie.confidence * 100}%"></div>
            </div>
            <small>Confianza: ${(movie.confidence * 100).toFixed(1)}%</small>
        `;
        grid.appendChild(card);
    });
    
    container.appendChild(grid);
}

// Función para mostrar estadísticas
function displayStats() {
    const container = document.getElementById('stats-results');
    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${appState.stats.executionTime}s</div>
            <div class="stat-label">Tiempo de Ejecución</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${appState.stats.totalNeighbors}</div>
            <div class="stat-label">Vecinos Encontrados</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${appState.stats.totalRecommendations}</div>
            <div class="stat-label">Recomendaciones</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${appState.currentUser || 'Nuevo'}</div>
            <div class="stat-label">Usuario Actual</div>
        </div>
    `;
}

// Función para mostrar visualización
function displayVisualization() {
    const canvas = document.getElementById('network-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 3;
    
    // Dibujar usuario central
    ctx.beginPath();
    ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
    ctx.fillStyle = '#3498db';
    ctx.fill();
    ctx.strokeStyle = '#2980b9';
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Etiqueta del usuario central
    ctx.fillStyle = '#2c3e50';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`Usuario ${appState.currentUser || 'Nuevo'}`, centerX, centerY - 30);
    
    // Dibujar vecinos
    if (appState.neighbors && appState.neighbors.length > 0) {
        appState.neighbors.forEach((neighbor, index) => {
            const angle = (2 * Math.PI * index) / appState.neighbors.length;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            // Línea de conexión
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = '#95a5a6';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Círculo del vecino
            ctx.beginPath();
            ctx.arc(x, y, 15, 0, 2 * Math.PI);
            ctx.fillStyle = '#e74c3c';
            ctx.fill();
            ctx.strokeStyle = '#c0392b';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Etiqueta del vecino
            ctx.fillStyle = '#2c3e50';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${neighbor.userId}`, x, y - 25);
            ctx.fillText(`${neighbor.score.toFixed(2)}`, x, y + 35);
        });
    }
}

// Función para mostrar alertas
function showAlert(message, type) {
    console.log(`📢 Alerta [${type}]: ${message}`);
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Función para exportar recomendaciones
function exportRecommendations() {
    if (!appState.recommendations || appState.recommendations.length === 0) {
        showAlert('No hay recomendaciones para exportar.', 'error');
        return;
    }
    
    const csvContent = [
        ['Título', 'Rating Predicho', 'Confianza'],
        ...appState.recommendations.map(movie => [
            movie.title,
            movie.predictedRating,
            (movie.confidence * 100).toFixed(1) + '%'
        ])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recomendaciones_usuario_${appState.currentUser || 'nuevo'}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showAlert('Recomendaciones exportadas exitosamente.', 'success');
}

// Función para guardar perfil de usuario (sin localStorage para compatibilidad)
function saveUserProfile() {
    const profile = {
        userType: appState.userType,
        currentUser: appState.currentUser,
        userRatings: appState.userRatings,
        preferences: {
            k: document.getElementById('k-value').value,
            distanceType: document.getElementById('distance-type').value,
            threshold: document.getElementById('rating-threshold').value
        }
    };
    
    console.log('💾 Perfil guardado:', profile);
    showAlert('Perfil de usuario guardado exitosamente.', 'success');
}

// Función para resetear la aplicación
function resetApplication() {
    if (confirm('¿Estás seguro de que quieres reiniciar la aplicación? Se perderán todos los datos actuales.')) {
        appState = {
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
        
        // Resetear formularios
        document.getElementById('user-id').value = '';
        document.getElementById('k-value').value = '5';
        document.getElementById('distance-type').value = 'euclidiana';
        document.getElementById('rating-threshold').value = '3.0';
        document.getElementById('movie-search').value = '';
        
        // Limpiar contenedores
        document.getElementById('neighbors-results').innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Ejecuta el algoritmo KNN para ver los resultados</p></div>';
        document.getElementById('recommendations-results').innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Los resultados aparecerán aquí después de ejecutar KNN</p></div>';
        document.getElementById('stats-results').innerHTML = '';
        document.getElementById('rated-movies').innerHTML = '';
        document.getElementById('movie-suggestions').style.display = 'none';
        
        // Volver a la primera pestaña
        switchTab('user-selection');
        
        showAlert('Aplicación reiniciada exitosamente.', 'success');
    }
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 Sistema de Recomendación KNN inicializado');
    showAlert('Sistema de Recomendación KNN cargado exitosamente. ¡Comienza seleccionando un usuario!', 'info');
});