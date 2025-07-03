from .distancias import distancia_euclidiana, distancia_manhattan, similitud_coseno, correlacion_pearson

def knn(usuario_x, k, distancia_funcion, user_ratings_dict, usuarios):
    resultados = []
    user_x_ratings = user_ratings_dict[usuario_x]

    for usuario in usuarios:
        if usuario == usuario_x:
            continue

        user_y_ratings = user_ratings_dict[usuario]
        peliculas_comunes = set(user_x_ratings.keys()) & set(user_y_ratings.keys())

        if not peliculas_comunes:
            continue

        v1 = [user_x_ratings[movieId] for movieId in peliculas_comunes]
        v2 = [user_y_ratings[movieId] for movieId in peliculas_comunes]

        valor = distancia_funcion(v1, v2)

        if distancia_funcion in [similitud_coseno, correlacion_pearson]:
            if valor is None:
                valor = -1
        else:
            if valor is None:
                valor = float('inf')

        resultados.append((usuario, valor))

    if distancia_funcion in [similitud_coseno, correlacion_pearson]:
        resultados.sort(key=lambda x: x[1], reverse=True)
    else:
        resultados.sort(key=lambda x: x[1])

    print(f"\nLos {k} vecinos más cercanos a {usuario_x} usando {distancia_funcion.__name__}:")
    vecinos = resultados[:k]
    for idx, (vecino, valor) in enumerate(vecinos, 1):
        print(f"{idx}. {vecino} - ({valor})")
    return vecinos
