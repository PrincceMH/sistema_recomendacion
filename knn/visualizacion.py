import matplotlib.pyplot as plt
import networkx as nx

def visualizar_knn(usuario_x, vecinos, tipo):
    """
    Dibuja un grafo de vecinos K-NN para un usuario dado.

    Parámetros:
    - usuario_x: ID del usuario objetivo.
    - vecinos: lista de tuplas (usuario_id, valor de similitud o distancia).
    - tipo: nombre de la métrica (para el título del grafo).
    """
    G = nx.Graph()
    G.add_node(usuario_x)

    for vecino, valor in vecinos:
        G.add_node(vecino)
        G.add_edge(usuario_x, vecino, weight=valor)

    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    formatted_labels = {k: f"{v:.2f}" for k, v in edge_labels.items()}

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_labels, font_size=9)
    plt.title(f"Grafo K-NN para {usuario_x} ({tipo})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
