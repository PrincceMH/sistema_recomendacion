import pandas as pd
from collections import Counter
def obtener_usuarios(data):
    """Devuelve una lista ordenada de userId únicos, compatible con Pandas y Dask."""
    try:
        usuarios = data['userId'].unique()
        if hasattr(usuarios, 'compute'):  # Es Dask
            usuarios = usuarios.compute()
        return sorted(usuarios.tolist())
    except Exception as e:
        print(f"❌ Error al obtener usuarios: {e}")
        return []
    
def preparar_datos(data, movies, usuario_x):
    # PASO 1: Obtener las películas vistas por el usuario
    user_x_data = data[data['userId'] == usuario_x]
    peliculas_vistas = set(user_x_data['movieId'])

    # PASO 2: Identificar TODAS las películas NO vistas
    todas_peliculas = set(movies['movieId'])
    peliculas_no_vistas = list(todas_peliculas - peliculas_vistas)

    # PASO 3: Crear DataFrame con todas las no vistas
    peliculas_no_vistas_df = movies[movies['movieId'].isin(peliculas_no_vistas)]

    # PASO 4: Mostrar SOLO las primeras 20 películas NO vistas
    print(f"\nMostrando las primeras 20 películas NO vistas por el usuario {usuario_x}:")
    print(peliculas_no_vistas_df.iloc[:20][['movieId', 'title', 'genres']].to_string(index=False))

    # PASO 5: Procesar todas las películas vistas sin umbral
    peliculas_vistas_info = user_x_data.merge(movies, how='left', on='movieId')

    # PASO 6: Mostrar info final
    print(f"\nPelículas VISTAS por el usuario {usuario_x} con título y género:")
    print(peliculas_vistas_info[['movieId', 'title', 'genres', 'rating']].to_string(index=False))

    # PASO 7: Crear vector final de géneros por frecuencia
    conteo = Counter()
    for genres in peliculas_vistas_info['genres']:
        for g in genres.split('|'):
            g = g.strip()
            conteo[g] += 1

    # Vector final de géneros con su frecuencia, manteniendo la estructura de 3 elementos
    vector_generos_priorizado = [(None, genero, frecuencia) for genero, frecuencia in conteo.most_common()]

    # Mostrar vector final
    print("\n=== Vector final de géneros ordenado por frecuencia ===")
    for _, genero, frecuencia in vector_generos_priorizado:
        print(f"{genero}: {frecuencia}")

    return peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado