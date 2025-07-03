def filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones):
    # Vector de géneros priorizado del usuario
    generos_favoritos = [genero for _, genero in vector_generos_priorizado]

    # Lista filtrada respetando prioridad de género y evitando duplicados
    nueva_lista_filtrada = []
    peliculas_agregadas = set()

    for genero in generos_favoritos:
        for r in resultados_recomendaciones:
            # Chequea si este género está en la lista de géneros de la peli
            generos_pelicula = [g.strip() for g in r['genres'].split('|')]
            if genero in generos_pelicula and r['movieId'] not in peliculas_agregadas:
                nueva_lista_filtrada.append(r)
                peliculas_agregadas.add(r['movieId'])

    return nueva_lista_filtrada

def mostrar_recomendaciones_personalizadas(vector_generos_priorizado, nueva_lista_filtrada, num_recomendaciones=3):
    print("\n=== RECOMENDACIONES PERSONALIZADAS (TOP 3) ===\n")

    for idx, r in enumerate(nueva_lista_filtrada[:num_recomendaciones], 1):
        # Encuentra el primer género coincidente con el vector
        generos_pelicula = [g.strip() for g in r['genres'].split('|')]
        genero_en_comun = None
        for nivel, genero in vector_generos_priorizado:
            if genero in generos_pelicula:
                genero_en_comun = genero
                break

        if genero_en_comun:
            razon = f"porque tiene una puntuación promedio de {round(r['promedio'], 2)} entre tus vecinos y pertenece a tu género favorito: {genero_en_comun}."
        else:
            razon = f"porque tiene una puntuación promedio de {round(r['promedio'], 2)} entre tus vecinos."

        print(f"{idx}. {r['title']}\n   Te puede gustar {razon}\n")
