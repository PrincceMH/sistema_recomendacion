import pandas as pd
from collections import Counter

def obtener_usuarios(data):
    """
    Retorna la lista de usuarios desde la matriz de utilidad.
    Se omite la primera columna que debe ser 'pelicula' (movieId).
    """
    return list(data.columns)[1:]  # omitir columna 'pelicula'

def preparar_datos(data, movies, usuario_x):
    # === PASO 1: Obtener las películas vistas por el usuario ===
    user_x_data = data[data['userId'] == usuario_x]
    peliculas_vistas = set(user_x_data['movieId'])

    # === PASO 2: Identificar TODAS las películas NO vistas ===
    todas_peliculas = set(movies['movieId'])
    peliculas_no_vistas = list(todas_peliculas - peliculas_vistas)

    # === PASO 3: Crear DataFrame con todas las no vistas ===
    peliculas_no_vistas_df = movies[movies['movieId'].isin(peliculas_no_vistas)]

    # === PASO 4: Mostrar SOLO las primeras 20 películas NO vistas ===
    print(f"\nMostrando las primeras 20 películas NO vistas por el usuario {usuario_x}:")
    print(peliculas_no_vistas_df.iloc[:20][['movieId', 'title', 'genres']].to_string(index=False))

    # === PASO 5: Procesar todas las películas vistas sin umbral ===
    peliculas_vistas_info = user_x_data.merge(
        movies,
        how='left',
        on='movieId'
    )

    # === PASO 6: Mostrar info final ===
    print(f"\nPelículas VISTAS por el usuario {usuario_x} con título y género:")
    print(peliculas_vistas_info[['movieId', 'title', 'genres', 'rating']].to_string(index=False))

    # === PASO 7: Crear vector final de géneros priorizado por rating y frecuencia ===
    niveles_presentes = sorted(
        peliculas_vistas_info['rating'].unique(),
        reverse=True
    )

    vector_generos_priorizado = []  # Vector final
    generos_agregados = set()       # Para no repetir

    for nivel in niveles_presentes:
        filtrado = peliculas_vistas_info[peliculas_vistas_info['rating'] == nivel]
        conteo = Counter()
        for genres in filtrado['genres']:
            for g in genres.split('|'):
                g = g.strip()
                conteo[g] += 1
        generos_ordenados = [g for g, _ in conteo.most_common()]
        for genero in generos_ordenados:
            if genero not in generos_agregados:
                vector_generos_priorizado.append((nivel, genero))
                generos_agregados.add(genero)

    # === Mostrar vector final ===
    print("\n=== Vector final de géneros ordenado por nivel y frecuencia ===")
    for nivel, genero in vector_generos_priorizado:
        print(f"Rating {nivel}: {genero}")

    return peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado
