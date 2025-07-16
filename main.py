from dask.distributed import Client
import pandas as pd
import sys
import time
import random

# Importar funciones necesarias
from knn.load_data import cargar_rating_matrix
from knn.preparar_datos import obtener_usuarios, preparar_datos
from knn.knn import knn
from knn.distancias import distancia_euclidiana, distancia_manhattan, similitud_coseno, correlacion_pearson
from knn.tabla_recomendacion import mostrar_tabla_vecinos
from knn.recomendador import recomendar_peliculas
from knn.visualizacion import visualizar_knn
from knn.filtrar_recomendaciones import filtrar_recomendaciones, mostrar_recomendaciones_personalizadas

# ===== 1. Conexión a Dask (solo una vez) =====
try:
    client = Client("tcp://10.147.17.195:8786")
    print("Conectado a Dask scheduler remoto")
    print(client)
except Exception as e:
    print(f"No se pudo conectar al scheduler: {e}")
    sys.exit(1)

# ===== 2. Cargar datasets (solo una vez) =====
data = cargar_rating_matrix(
    path="/mnt/datasets/ml-32m/ratings.csv",
    min_ratings_usuario=0,
    min_ratings_pelicula=0,
    frac_sample=1.0,
    return_pivot=False,
)
print("Columnas del DataFrame:", data.columns.tolist())
movies = pd.read_csv("/mnt/datasets/ml-32m/movies.csv")
usuarios = obtener_usuarios(data)
print(usuarios)

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
    print("\n=== MENU PRINCIPAL ===")
    print("1. Realizar nueva consulta KNN")
    print("2. Salir del sistema")
    opcion_menu = input("Selecciona 1 o 2: ").strip()

    if opcion_menu == "2":
        print("Cerrando sesión... Hasta luego!")
        client.close()  # Cerrar conexión Dask ordenadamente
        break

    if opcion_menu != "1":
        print("Opción no válida. Intenta de nuevo.")
        continue

    # ===== Submenú para escoger usuario =====
    while True:
        print("\n=== SUBMENU USUARIO ===")
        print("1. Escoger usuario conocido")
        print("2. Escoger nuevo usuario")
        print("3. Volver al menú principal")
        opcion_usuario = input("Selecciona 1, 2 o 3: ").strip()

        if opcion_usuario == "3":
            break

        if opcion_usuario == "1":
            # Solicitar parámetros al usuario
            try:
                print("\nUsuarios disponibles:")
                for usuario in usuarios:
                    print(usuario)
                usuario_x = int(input("Usuario para KNN (userId): "))
                if usuario_x not in usuarios:
                    raise ValueError("El usuario no está en la matriz.")
                k = int(input("Número de vecinos K: "))
                tipo = input("Tipo de distancia (euclidiana, manhattan, coseno, pearson): ").lower().strip()
                umbral = float(input("Umbral mínimo de calificación: "))
            except Exception as e:
                print(f"Entrada inválida: {e}")
                continue

            f = funciones.get(tipo)
            if not f:
                print("Tipo de distancia no reconocida.")
                continue

            # Ejecutar KNN
            vecinos = knn(usuario_x, k, f, user_ratings_dict, usuarios)
            if not vecinos:
                print("No se encontraron vecinos para ese usuario/parámetro.")
                continue

            print(f"\nVecinos más cercanos de {usuario_x} usando {tipo}:")
            for i, (vecino, puntaje) in enumerate(vecinos, 1):
                print(f"{i}. Vecino: {vecino} -> Puntaje: {round(puntaje, 4)}")

            # Mostrar tabla de calificaciones
            tabla = mostrar_tabla_vecinos(vecinos, data)
            if tabla is None:
                print("No hay datos suficientes para mostrar tabla de vecinos.")
                continue

            # Preparar datos y generar recomendaciones
            start_time = time.time()  # Iniciar medición de tiempo
            peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado = preparar_datos(data, movies, usuario_x)
            print("----------------------------------------------------")
            print(vector_generos_priorizado)
            resultados_recomendaciones = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral)
            print("----------------------------------------------------")
            print(resultados_recomendaciones)
            nueva_lista_filtrada = filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones)
            print("----------------------------------------------------")
            print(nueva_lista_filtrada)
            mostrar_recomendaciones_personalizadas(vector_generos_priorizado, nueva_lista_filtrada)
            end_time = time.time()  # Finalizar medición de tiempo
            print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")

            # Visualizar red de vecinos
            visualizar_knn(usuario_x, vecinos, tipo)
            print("\nConsulta finalizada.\n")

        elif opcion_usuario == "2":
            # Mostrar una muestra aleatoria de películas
            muestra_peliculas = movies.sample(min(10, len(movies)))
            print("\n=== MUESTRA DE PELICULAS DISPONIBLES ===")
            print(muestra_peliculas[['movieId', 'title']])

            # Permitir al nuevo usuario calificar cualquier película
            nuevo_usuario_ratings = {}
            while True:
                movie_id = input("Introduce el ID de la película que deseas calificar (o 'terminar' para finalizar): ").strip()
                if movie_id.lower() == 'terminar':
                    break
                try:
                    movie_id = int(movie_id)
                    if movie_id not in movies['movieId'].values:
                        print("ID de película no válido.")
                        continue
                    rating = float(input(f"Calificación para la película {movie_id} (1-5): "))
                    if not 1 <= rating <= 5:
                        print("La calificación debe estar entre 1 y 5.")
                        continue
                    nuevo_usuario_ratings[movie_id] = rating
                except ValueError:
                    print("Entrada inválida.")

            if not nuevo_usuario_ratings:
                print("No se han introducido calificaciones para el nuevo usuario.")
                continue

            # Añadir el nuevo usuario al diccionario de ratings
            nuevo_usuario_id = max(usuarios) + 1
            user_ratings_dict[nuevo_usuario_id] = nuevo_usuario_ratings
            usuarios.append(nuevo_usuario_id)

            # Seguir el flujo principal con el nuevo usuario
            try:
                k = int(input("Número de vecinos K: "))
                tipo = input("Tipo de distancia (euclidiana, manhattan, coseno, pearson): ").lower().strip()
                umbral = float(input("Umbral mínimo de calificación: "))
            except Exception as e:
                print(f"Entrada inválida: {e}")
                continue

            f = funciones.get(tipo)
            if not f:
                print("Tipo de distancia no reconocida.")
                continue

            # Ejecutar KNN con el nuevo usuario
            vecinos = knn(nuevo_usuario_id, k, f, user_ratings_dict, usuarios)
            if not vecinos:
                print("No se encontraron vecinos para ese usuario/parámetro.")
                continue

            print(f"\nVecinos más cercanos de {nuevo_usuario_id} usando {tipo}:")
            for i, (vecino, puntaje) in enumerate(vecinos, 1):
                print(f"{i}. Vecino: {vecino} -> Puntaje: {round(puntaje, 4)}")

            # Mostrar tabla de calificaciones
            tabla = mostrar_tabla_vecinos(vecinos, data)
            if tabla is None:
                print("No hay datos suficientes para mostrar tabla de vecinos.")
                continue

            # Preparar datos y generar recomendaciones
            start_time = time.time()  # Iniciar medición de tiempo
            peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado = preparar_datos(data, movies, nuevo_usuario_id)
            resultados_recomendaciones = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral)
            nueva_lista_filtrada = filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones)
            mostrar_recomendaciones_personalizadas(vector_generos_priorizado, nueva_lista_filtrada)
            end_time = time.time()  # Finalizar medición de tiempo
            print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")

            # Visualizar red de vecinos
            visualizar_knn(nuevo_usuario_id, vecinos, tipo)
            print("\nConsulta finalizada.\n")

        else:
            print("Opción no válida. Intenta de nuevo.")