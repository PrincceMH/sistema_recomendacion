from dask.distributed import Client
from knn.load_data import cargar_rating_matrix
from knn.preparar_datos import obtener_usuarios, preparar_datos
from knn.knn import knn

from knn.distancias import (
    distancia_euclidiana,
    distancia_manhattan,
    similitud_coseno,
    correlacion_pearson,
)
from knn.tabla_recomendacion import mostrar_tabla_vecinos
from knn.recomendador import recomendar_peliculas
from knn.visualizacion import visualizar_knn
from knn.filtrar_recomendaciones import (
    filtrar_recomendaciones,
    mostrar_recomendaciones_personalizadas
)

import pandas as pd

# === 1. Conectarse a Dask Scheduler remoto ===
client = Client("tcp://192.168.0.195:8786")
print("✅ Conectado a Dask scheduler remoto")
print(client)

# === 2. Cargar matriz de utilidad (reducida para eficiencia) ===
data = cargar_rating_matrix(
    path='/mnt/datasets/ml-32m/ratings.csv',
    min_ratings_usuario=1000,
    min_ratings_pelicula=1000,
    frac_sample=0.05,  # Puedes subir a 0.1 si tu RAM lo permite
    return_pivot=False
)
print("✅ Columnas del DataFrame:", data.columns.tolist())

# === 3. Cargar metadata de películas (completa) ===
movies = pd.read_csv('/mnt/datasets/ml-32m/movies.csv')

# === 4. Seleccionar usuario y parámetros ===
usuarios = obtener_usuarios(data)
print("\nUsuarios disponibles:", usuarios[:10], "...")

try:
    usuario_x = int(input("🔎 Usuario para KNN (userId): "))
    if usuario_x not in usuarios:
        raise ValueError("El usuario no está en la matriz.")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

try:
    k = int(input("🔢 Número de vecinos K: "))
    tipo = input("📐 Tipo de distancia (euclidiana, manhattan, coseno, pearson): ").lower().strip()
    umbral = float(input("⭐ Umbral mínimo de calificación: "))
except Exception as e:
    print(f"❌ Entrada inválida: {e}")
    exit()

# === 5. Selección de función de distancia ===
funciones = {
    "euclidiana": distancia_euclidiana,
    "manhattan": distancia_manhattan,
    "coseno": similitud_coseno,
    "pearson": correlacion_pearson,
}
f = funciones.get(tipo)
if not f:
    print("❌ Tipo de distancia no reconocida.")
    exit()

# === 6. Crear diccionario de ratings por usuario para KNN ===
user_ratings_dict = {
    user: dict(grupo[['movieId', 'rating']].values)
    for user, grupo in data.groupby('userId')
}

# === 7. Ejecutar KNN ===
vecinos = knn(usuario_x, k, f, user_ratings_dict, usuarios)
if not vecinos:
    print("❌ No se encontraron vecinos.")
    exit()

print(f"\n👥 Vecinos más cercanos de {usuario_x} usando {tipo}:")
for i, (vecino, puntaje) in enumerate(vecinos, 1):
    print(f"{i}. Vecino: {vecino} → Puntaje: {round(puntaje, 4)}")

# === 8. Visualización de la red de vecinos ===
visualizar_knn(usuario_x, vecinos, tipo)

# === 9. Mostrar tabla de calificaciones de vecinos ===
tabla = mostrar_tabla_vecinos(vecinos, data)
if tabla is None:
    print("❌ No hay datos suficientes para mostrar tabla de vecinos.")
    exit()

# === 10. Preparar info de películas vistas/no vistas y géneros del usuario ===
peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado = preparar_datos(data, movies, usuario_x)

# === 11. Generar recomendaciones usando vecinos ===
resultados_recomendaciones = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral)

# === 12. Aplicar filtro por géneros favoritos y mostrar final ===
nueva_lista_filtrada = filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones)
mostrar_recomendaciones_personalizadas(vector_generos_priorizado, nueva_lista_filtrada)
