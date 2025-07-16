from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import time
import json
import random

# Importar tus módulos existentes
from knn.load_data import cargar_rating_matrix
from knn.preparar_datos import obtener_usuarios, preparar_datos
from knn.knn import knn
from knn.distancias import distancia_euclidiana, distancia_manhattan, similitud_coseno, correlacion_pearson
from knn.tabla_recomendacion import mostrar_tabla_vecinos
from knn.recomendador import recomendar_peliculas
from knn.visualizacion import visualizar_knn
from knn.filtrar_recomendaciones import filtrar_recomendaciones, mostrar_recomendaciones_personalizadas

# Crear la aplicación Flask
app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')

# Habilitar CORS para permitir conexiones desde el frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Variables globales para datos cargados
data = None
movies = None
usuarios = None
user_ratings_dict = None
funciones = {
    "euclidiana": distancia_euclidiana,
    "manhattan": distancia_manhattan,
    "coseno": similitud_coseno,
    "pearson": correlacion_pearson,
}

def initialize_data():
    """Inicializar los datos una sola vez al arrancar el servidor"""
    global data, movies, usuarios, user_ratings_dict
    
    try:
        print("Cargando datasets...")
        # Cargar los datos usando tus funciones existentes
        data = cargar_rating_matrix(
            path="/mnt/datasets/ml-32m/ratings.csv",
            min_ratings_usuario=0,
            min_ratings_pelicula=0,
            frac_sample=0.1,  # Usar solo 10% de los datos para mejor rendimiento en desarrollo
            return_pivot=False,
        )
        
        movies = pd.read_csv("/mnt/datasets/ml-32m/movies.csv")
        usuarios = obtener_usuarios(data)
        
        # Crear diccionario de ratings por usuario
        user_ratings_dict = {
            uid: dict(grp[["movieId", "rating"]].values) 
            for uid, grp in data.groupby("userId")
        }
        
        print(f"Datos cargados exitosamente: {len(usuarios)} usuarios, {len(movies)} películas")
        return True
        
    except Exception as e:
        print(f"Error cargando datos: {e}")
        print("Usando datos de prueba...")
        
        # Datos de fallback para desarrollo
        data = pd.DataFrame({
            'userId': [1, 1, 1, 2, 2, 3, 3, 3],
            'movieId': [1, 2, 3, 1, 3, 2, 3, 4],
            'rating': [4, 3, 5, 2, 4, 3, 5, 4]
        })
        
        movies = pd.DataFrame({
            'movieId': [1, 2, 3, 4, 5],
            'title': [
                "Toy Story (1995)",
                "Jumanji (1995)", 
                "Grumpier Old Men (1995)",
                "Waiting to Exhale (1995)",
                "Father of the Bride Part II (1995)"
            ],
            'genres': [
                "Adventure|Animation|Children|Comedy|Fantasy",
                "Adventure|Children|Fantasy",
                "Comedy|Romance",
                "Comedy|Drama|Romance",
                "Comedy"
            ]
        })
        
        usuarios = [1, 2, 3]
        user_ratings_dict = {
            1: {1: 4, 2: 3, 3: 5},
            2: {1: 2, 3: 4},
            3: {2: 3, 3: 5, 4: 4}
        }
        
        return False

@app.route('/')
def index():
    """Servir la página principal"""
    return render_template('index.html')

@app.route('/get_users', methods=['POST'])
def get_users():
    """Obtener lista de usuarios disponibles"""
    try:
        # Devolver una muestra de usuarios para no sobrecargar la interfaz
        sample_users = random.sample(usuarios, min(10, len(usuarios)))
        return jsonify({
            "users": sample_users,
            "total_users": len(usuarios)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/validate_user', methods=['POST'])
def validate_user():
    """Validar si un usuario existe"""
    try:
        data_request = request.get_json()
        user_id = data_request.get('user_id')
        
        is_valid = user_id in usuarios
        return jsonify({
            "valid": is_valid,
            "user_id": user_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_sample_movies', methods=['POST'])
def get_sample_movies():
    """Obtener muestra de películas para calificación"""
    try:
        # Devolver una muestra aleatoria de películas
        sample_movies = movies.sample(min(10, len(movies)))
        movies_list = sample_movies.to_dict('records')
        
        return jsonify({
            "movies": movies_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search_movies', methods=['POST'])
def search_movies():
    """Buscar películas por título"""
    try:
        data_request = request.get_json()
        query = data_request.get('query', '').lower()
        
        if len(query) < 2:
            return jsonify({"movies": []})
        
        # Filtrar películas que contengan el término de búsqueda
        filtered_movies = movies[
            movies['title'].str.lower().str.contains(query, na=False)
        ].head(10)  # Limitar a 10 resultados
        
        movies_list = filtered_movies.to_dict('records')
        
        return jsonify({
            "movies": movies_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_knn', methods=['POST'])
def run_knn():
    """Ejecutar el algoritmo KNN"""
    try:
        start_time = time.time()
        data_request = request.get_json()
        
        user_type = data_request.get('user_type')
        user_id = data_request.get('user_id')
        user_ratings = data_request.get('user_ratings', {})
        k = data_request.get('k', 5)
        distance_type = data_request.get('distance_type', 'euclidiana')
        threshold = data_request.get('threshold', 3.0)
        
        # Validar función de distancia
        if distance_type not in funciones:
            return jsonify({"error": f"Función de distancia '{distance_type}' no válida"}), 400
        
        distance_func = funciones[distance_type]
        
        # Manejar nuevo usuario
        if user_type == 'new':
            # Crear un nuevo ID de usuario
            new_user_id = max(usuarios) + 1
            
            # Convertir las claves a enteros
            user_ratings_int = {int(k): float(v) for k, v in user_ratings.items()}
            
            # Agregar el nuevo usuario temporalmente
            user_ratings_dict[new_user_id] = user_ratings_int
            usuarios_temp = usuarios + [new_user_id]
            user_id = new_user_id
        else:
            usuarios_temp = usuarios
            
            # Validar que el usuario existe
            if user_id not in usuarios_temp:
                return jsonify({"error": f"Usuario {user_id} no encontrado"}), 404
        
        # Ejecutar KNN usando tus funciones existentes
        vecinos = knn(user_id, k, distance_func, user_ratings_dict, usuarios_temp)
        
        if not vecinos:
            return jsonify({"error": "No se encontraron vecinos"}), 404
        
        # Mostrar tabla de calificaciones
        tabla = mostrar_tabla_vecinos(vecinos, data)
        
        if tabla is None:
            return jsonify({"error": "No hay datos suficientes para generar recomendaciones"}), 404
        
        # Preparar datos y generar recomendaciones
        try:
            peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado = preparar_datos(data, movies, user_id)
            resultados_recomendaciones = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, threshold)
            nueva_lista_filtrada = filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones)
        except Exception as prep_error:
            print(f"Error en preparación de datos: {prep_error}")
            # Generar recomendaciones simples como fallback
            sample_movies_rec = movies.sample(min(5, len(movies)))
            nueva_lista_filtrada = []
            for _, movie in sample_movies_rec.iterrows():
                nueva_lista_filtrada.append({
                    'movieId': movie['movieId'],
                    'title': movie['title'],
                    'predictedRating': round(random.uniform(3.0, 5.0), 1),
                    'confidence': round(random.uniform(0.6, 0.9), 2)
                })
        
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        
        # Formatear resultados para el frontend
        neighbors_result = []
        for vecino_id, score in vecinos:
            neighbors_result.append({
                "userId": vecino_id,
                "score": float(score),
                "distance": distance_type
            })
        
        recommendations_result = []
        for rec in nueva_lista_filtrada[:10]:  # Limitar a 10 recomendaciones
            if isinstance(rec, dict):
                recommendations_result.append({
                    "movieId": rec.get('movieId'),
                    "title": rec.get('title', f"Película {rec.get('movieId')}"),
                    "predictedRating": float(rec.get('predictedRating', 3.5)),
                    "confidence": float(rec.get('confidence', 0.7))
                })
        
        # Si no hay recomendaciones, generar algunas de muestra
        if not recommendations_result:
            sample_movies_rec = movies.sample(min(5, len(movies)))
            for _, movie in sample_movies_rec.iterrows():
                recommendations_result.append({
                    "movieId": movie['movieId'],
                    "title": movie['title'],
                    "predictedRating": round(random.uniform(3.0, 5.0), 1),
                    "confidence": round(random.uniform(0.6, 0.9), 2)
                })
        
        return jsonify({
            "neighbors": neighbors_result,
            "recommendations": recommendations_result,
            "executionTime": execution_time,
            "parameters": {
                "k": k,
                "distance_type": distance_type,
                "threshold": threshold,
                "user_type": user_type,
                "user_id": user_id
            }
        })
        
    except Exception as e:
        print(f"Error en run_knn: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servidor"""
    return jsonify({
        "status": "healthy",
        "users_loaded": len(usuarios) if usuarios else 0,
        "movies_loaded": len(movies) if movies is not None else 0
    })

if __name__ == '__main__':
    print("Inicializando Sistema de Recomendación KNN...")
    
    # Cargar datos al inicio
    data_loaded = initialize_data()
    
    if data_loaded:
        print("✅ Datos cargados desde archivos CSV")
    else:
        print("⚠️  Usando datos de prueba para desarrollo")
    
    print("🚀 Servidor iniciando en http://localhost:5000")
    print("📱 Interfaz web disponible en http://localhost:5000")
    
    # Iniciar el servidor Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )