import pandas as pd

def mostrar_tabla_vecinos(vecinos, data):
    """
    Crea una tabla (pivot) de calificaciones solo de los usuarios vecinos.

    Parámetros:
    - vecinos: lista de tuplas (userId, valor_distancia) retornada por knn
    - data: DataFrame plano con columnas ['userId', 'movieId', 'rating']

    Retorna:
    - tabla: DataFrame pivote con movieId como índice y userId como columnas
    """
    if vecinos:
        vecinos_ids = [v for v, _ in vecinos]

        # Filtrar el DataFrame para obtener solo los ratings de los vecinos
        vecinos_data = data[data['userId'].isin(vecinos_ids)]

        # Crear matriz usuario-item solo con vecinos
        tabla = vecinos_data.pivot(index='movieId', columns='userId', values='rating')

        print(f"\n✅ Tabla de calificaciones para los {len(vecinos)} vecinos más cercanos:")
        print(tabla.head(10))  # Mostrar primeras filas como ejemplo

        return tabla
    else:
        print("⚠️ No hay vecinos calculados.")
        return None
