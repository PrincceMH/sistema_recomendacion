import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def obtener_usuarios(data):
    """Devuelve una lista de usuarios, ignorando la primera columna que es 'pelicula'."""
    return list(data.columns[1:])  # 'pelicula' es la columna 0

def knn(usuario_x, data, k, distancia_funcion):
    resultados = []
    for usuario in data.columns[1:]:
        if usuario != usuario_x:
            pares = data[[usuario_x, usuario]].dropna()
            v1 = pares[usuario_x].values
            v2 = pares[usuario].values
            valor = distancia_funcion(v1, v2)

            # Manejo de valores nulos o indefinidos
            if distancia_funcion.__name__ in ['similitud_coseno', 'correlacion_pearson']:
                valor = -1 if valor is None else valor
            else:
                valor = float('inf') if valor is None else valor

            resultados.append((usuario, valor))

    # Ordenar según la distancia/similitud
    reverse = distancia_funcion.__name__ in ['similitud_coseno', 'correlacion_pearson']
    resultados.sort(key=lambda x: x[1], reverse=reverse)

    return resultados[:k]

def recomendar_peliculas(data, usuario_x, vecinos, umbral):
    vecinos_ids = [v for v, _ in vecinos]
    no_vistas = data[data[usuario_x].isna()]
    recomendaciones = []

    for _, fila in no_vistas.iterrows():
        pelicula = fila['pelicula']
        calificaciones = fila[vecinos_ids]
        validas = calificaciones[calificaciones >= umbral].dropna()
        if not validas.empty:
            promedio = validas.mean()
            recomendaciones.append((pelicula, promedio, validas))

    recomendaciones.sort(key=lambda x: x[1], reverse=True)
    return recomendaciones

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
