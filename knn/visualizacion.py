import matplotlib.pyplot as plt
import networkx as nx

def graficar_red(usuario_x, vecinos, tipo):
    G = nx.Graph()
    G.add_node(usuario_x)

    for vecino, valor in vecinos:
        G.add_node(vecino)
        G.add_edge(usuario_x, vecino, weight=round(valor, 2))

    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700, edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    plt.title(f"Grafo K-NN para Usuario {usuario_x} usando {tipo}")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
