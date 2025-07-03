from dask.distributed import Client
from knn.load_data import cargar_rating_matrix
from knn.recomendador import obtener_usuarios, knn, recomendar_peliculas
from knn.distancias import (
    distancia_euclidiana,
    distancia_manhattan,
    similitud_coseno,
    correlacion_pearson,
)
from knn.visualizacion import graficar_red

# === 1. Conectarse a Dask Scheduler remoto
client = Client("tcp://10.7.135.127:8786")
print("✅ Conectado a Dask scheduler remoto")
print(client)

# === 2. Cargar matriz de utilidad con filtros para evitar saturar RAM
data = cargar_rating_matrix(
    path='/mnt/datasets/ml-32m/ratings.csv',
    min_ratings_usuario=1000,
    min_ratings_pelicula=1000,
    frac_sample=0.05  # Reduce el tamaño para evitar MemoryError
)

# === 3. (Opcional) Distribuir entre los workers
future = client.scatter(data)
data = future.result()
print(f"✅ Matriz de utilidad cargada: {data.shape}")

# === 4. Configuración de usuario y parámetros
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

# === 5. Mapeo de función de distancia
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

# === 6. Calcular vecinos
vecinos = knn(usuario_x, data, k, f)
if not vecinos:
    print("❌ No se encontraron vecinos.")
    exit()

print(f"\n👥 Vecinos más cercanos usando {tipo}:")
for i, (vecino, puntaje) in enumerate(vecinos, 1):
    print(f"{i}. Vecino: {vecino} → Puntaje: {round(puntaje, 4)}")

# === 7. Visualización con NetworkX
graficar_red(usuario_x, vecinos, tipo)

# === 8. Generar recomendaciones
recomendaciones = recomendar_peliculas(data, usuario_x, vecinos, umbral)

if recomendaciones:
    print("\n🎬 Películas recomendadas:")
    for pelicula, promedio in recomendaciones[:10]:
        print(f"Película ID {pelicula} → Predicción promedio: {round(promedio, 2)}")
    print(f"\n⭐ Recomendación destacada: Película ID {recomendaciones[0][0]} con {round(recomendaciones[0][1], 2)}")
else:
    print("❌ No se encontraron recomendaciones que superen el umbral.")
