import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral_vecinos):
    resultados_recomendaciones = []

    if vecinos:
        vecinos_ids = [v for v, _ in vecinos]

        print(f"\n=== Recomendaciones basadas en promedio de vecinos (umbral >= {umbral_vecinos}) ===\n")

        for _, pelicula in peliculas_no_vistas_df.iterrows():
            movie_id = pelicula['movieId']
            title = pelicula['title']
            genres = pelicula['genres']

            ratings_vecinos = []
            if movie_id in tabla.index:
                fila = tabla.loc[movie_id, vecinos_ids]
                for vecino_id in vecinos_ids:
                    rating = fila[vecino_id] if vecino_id in fila.index else None
                    ratings_vecinos.append((vecino_id, rating))
            else:
                ratings_vecinos = [(vecino_id, None) for vecino_id in vecinos_ids]

            ratings_validos = [r for _, r in ratings_vecinos if pd.notnull(r) and r >= umbral_vecinos]

            if not ratings_validos:
                continue

            promedio = sum(ratings_validos) / len(ratings_validos)

            print(f"Película: {title} (ID: {movie_id})")
            print(f"Géneros: {genres}")
            for vecino_id, rating in ratings_vecinos:
                if pd.isnull(rating):
                    estado = "Sin datos"
                elif rating >= umbral_vecinos:
                    estado = f"{rating} ✅"
                else:
                    estado = f"{rating} ❌"
                print(f"  Vecino {vecino_id}: {estado}")
            print(f"Promedio (solo ratings >= {umbral_vecinos}): {round(promedio, 2)}\n")

            resultados_recomendaciones.append({
                'movieId': movie_id,
                'title': title,
                'genres': genres,
                'promedio': promedio
            })

        resultados_recomendaciones.sort(key=lambda x: x['promedio'], reverse=True)

        print("\n=== Lista FINAL ordenada de mayor a menor promedio ===\n")
        for r in resultados_recomendaciones:
            print(f"{r['title']} | Géneros: {r['genres']} | Promedio: {round(r['promedio'], 2)}")

    else:
        print("No hay vecinos calculados.")

    return resultados_recomendaciones

def graficar_red(usuario_x, vecinos, tipo):
    G = nx.Graph()
    G.add_node(usuario_x)

    for vecino, valor in vecinos:
        G.add_node(vecino)
        G.add_edge(usuario_x, vecino, weight=valor)

    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    formatted_labels = {k: f"{v:.2f}" for k, v in edge_labels.items()}

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_labels)
    plt.title(f"Grafo K-NN para {usuario_x} ({tipo})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
