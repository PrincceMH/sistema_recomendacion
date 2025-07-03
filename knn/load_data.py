import dask.dataframe as dd
import pandas as pd

def cargar_rating_matrix(
    path='/mnt/datasets/ml-32m/ratings.csv',
    min_ratings_usuario=1000,
    min_ratings_pelicula=1000,
    frac_sample=None,
    return_pivot=True  # ✅ Nuevo parámetro opcional
):
    # ✅ Leer sólo columnas necesarias (más eficiente)
    columns = ['userId', 'movieId', 'rating']
    df = dd.read_csv(path, usecols=columns).compute()

    # ✅ Filtrar usuarios con suficientes calificaciones
    conteo_usuarios = df.groupby("userId").size()
    usuarios_filtrados = conteo_usuarios[conteo_usuarios >= min_ratings_usuario].index.tolist()
    df = df[df["userId"].isin(usuarios_filtrados)]

    # ✅ Filtrar películas con suficientes calificaciones
    conteo_peliculas = df.groupby("movieId").size()
    peliculas_filtradas = conteo_peliculas[conteo_peliculas >= min_ratings_pelicula].index.tolist()
    df = df[df["movieId"].isin(peliculas_filtradas)]

    # ✅ Muestra aleatoria (opcional)
    if frac_sample is not None:
        df = df.sample(frac=frac_sample, random_state=42)

    # ✅ Devolver matriz pivoteada o dataframe plano
    if return_pivot:
        matrix = df.pivot_table(index="movieId", columns="userId", values="rating")
        matrix.reset_index(inplace=True)
        matrix.rename(columns={"movieId": "pelicula"}, inplace=True)
        return matrix
    else:
        return df  # 👈 Devolver DataFrame plano si se desea trabajar con userId directamente

def cargar_peliculas(path):
    """Carga el archivo de películas completo."""
    return pd.read_csv(path)
