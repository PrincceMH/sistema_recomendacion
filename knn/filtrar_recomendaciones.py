def filtrar_recomendaciones(vector_generos_priorizado, resultados_recomendaciones):
    # Crear un diccionario para mapear géneros a sus prioridades
    prioridad_generos = {genero: idx for idx, (_, genero, _) in enumerate(vector_generos_priorizado)}

    # Función para obtener la prioridad de una película
    def obtener_prioridad_pelicula(pelicula):
        generos_pelicula = [g.strip() for g in pelicula['genres'].split('|')]
        # Obtener la prioridad más alta (más baja en valor numérico) entre los géneros de la película
        prioridades = [prioridad_generos.get(genero, float('inf')) for genero in generos_pelicula]
        return min(prioridades) if prioridades else float('inf')

    # Ordenar las películas según la prioridad de sus géneros
    nueva_lista_filtrada = sorted(resultados_recomendaciones, key=obtener_prioridad_pelicula)

    return nueva_lista_filtrada


def mostrar_recomendaciones_personalizadas(vector_generos_priorizado, nueva_lista_filtrada, num_recomendaciones=3):
    print("\n=== RECOMENDACIONES PERSONALIZADAS (TOP 3) ===\n")
    for idx, r in enumerate(nueva_lista_filtrada[:num_recomendaciones], 1):
        # Encuentra el primer género coincidente con el vector
        generos_pelicula = [g.strip() for g in r['genres'].split('|')]
        genero_en_comun = None
        for nivel, genero, _ in vector_generos_priorizado:
            if genero in generos_pelicula:
                genero_en_comun = genero
                break
        if genero_en_comun:
            razon = f"porque tiene una puntuación promedio de {round(r['promedio'], 2)} entre tus vecinos y pertenece a tu género favorito: {genero_en_comun}."
        else:
            razon = f"porque tiene una puntuación promedio de {round(r['promedio'], 2)} entre tus vecinos."
        print(f"{idx}. {r['title']}\n   Te puede gustar {razon}\n")
