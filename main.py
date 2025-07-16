from dask.distributed import Client
import dask.dataframe as dd

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
    mostrar_recomendaciones_personalizadas,
)
import pandas as pd
import sys

# ===== 1. Conexión a Dask (solo una vez) =====
try:
    client = Client("tcp://10.147.17.195:8786")
    print("✅ Conectado a Dask scheduler remoto")
    print(client)
except Exception as e:
    print(f"❌ No se pudo conectar al scheduler: {e}")
    sys.exit(1)

# ===== 2. Cargar datasets (solo una vez) =====
data = cargar_rating_matrix(
    path="/mnt/datasets/ml-32m/ratings.csv",
    min_ratings_usuario=0,
    min_ratings_pelicula=0,
    frac_sample=1.0,
    return_pivot=False,
)
print("✅ Columnas del DataFrame:", data.columns.tolist())
movies = pd.read_csv("/mnt/datasets/ml-32m/movies.csv")
usuarios = obtener_usuarios(data)

# ===== 3. Tabla de funciones de distancia =====
funciones = {
    "euclidiana": distancia_euclidiana,
    "manhattan": distancia_manhattan,
    "coseno": similitud_coseno,
    "pearson": correlacion_pearson,
}

# ===== 4. Diccionario de ratings por usuario (solo una vez) =====
user_ratings_dict = {
    uid: dict(grp[["movieId", "rating"]].values) for uid, grp in data.groupby("userId")
}

# ===== 5. Bucle principal =====
while True:
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Realizar nueva consulta KNN")
    print("2. Salir del sistema")
    opcion_menu = input("Selecciona 1 o 2: ").strip()

    if opcion_menu == "2":
        print("👋 Cerrando sesión… ¡Hasta luego!")
        client.close()  # cerrar conexión Dask ordenadamente
        break

    if opcion_menu != "1":
        print("⚠️ Opción no válida. Intenta de nuevo.")
        continue

    # ---------- Solicitar parámetros al usuario ----------
    try:
        print("\nUsuarios disponibles:")
        for usuario in usuarios:
            print(usuario)
        usuario_x = int(input("🔎 Usuario para KNN (userId): "))
        if usuario_x not in usuarios:
            raise ValueError("El usuario no está en la matriz.")
        k = int(input("🔢 Número de vecinos K: "))
        tipo = (
            input("📐 Tipo de distancia (euclidiana, manhattan, coseno, pearson): ")
            .lower()
            .strip()
        )
        umbral = float(input("⭐ Umbral mínimo de calificación: "))
    except Exception as e:
        print(f"❌ Entrada inválida: {e}")
        continue  # volver al menú principal

    f = funciones.get(tipo)
    if not f:
        print("❌ Tipo de distancia no reconocida.")
        continue

    # ---------- Ejecutar KNN ----------
    vecinos = knn(usuario_x, k, f, user_ratings_dict, usuarios)
    if not vecinos:
        print("❌ No se encontraron vecinos para ese usuario/parámetro.")
        continue
    print(f"\n👥 Vecinos más cercanos de {usuario_x} usando {tipo}:")
    for i, (vecino, puntaje) in enumerate(vecinos, 1):
        print(f"{i}. Vecino: {vecino} → Puntaje: {round(puntaje, 4)}")

    # ---------- Mostrar tabla de calificaciones ----------
    tabla = mostrar_tabla_vecinos(vecinos, data)
    if tabla is None:
        print("❌ No hay datos suficientes para mostrar tabla de vecinos.")
        continue

    # ---------- Preparar datos y generar recomendaciones ----------
    (
        peliculas_no_vistas_df,
        peliculas_vistas_info,
        vector_generos_priorizado,
    ) = preparar_datos(data, movies, usuario_x)
    resultados_recomendaciones = recomendar_peliculas(
        vecinos, peliculas_no_vistas_df, tabla, umbral
    )
    nueva_lista_filtrada = filtrar_recomendaciones(
        vector_generos_priorizado, resultados_recomendaciones
    )
    mostrar_recomendaciones_personalizadas(
        vector_generos_priorizado, nueva_lista_filtrada
    )

    # ---------- Visualizar red de vecinos ----------
    visualizar_knn(usuario_x, vecinos, tipo)
    print("\n✅ Consulta finalizada.\n")