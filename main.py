import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dask.distributed import Client
from knn.load_data import cargar_rating_matrix
from knn.preparar_datos import obtener_usuarios, preparar_datos
from knn.knn import knn
from knn.distancias import distancia_euclidiana, distancia_manhattan, similitud_coseno, correlacion_pearson
from knn.tabla_recomendacion import mostrar_tabla_vecinos
from knn.recomendador import recomendar_peliculas
from knn.visualizacion import visualizar_knn
from knn.filtrar_recomendaciones import filtrar_recomendaciones, mostrar_recomendaciones_personalizadas
import pandas as pd

# Conectarse a Dask Scheduler remoto
client = Client("tcp://192.168.0.195:8786")

# Cargar matriz de utilidad
data = cargar_rating_matrix(
    path='/mnt/datasets/ml-32m/ratings.csv',
    min_ratings_usuario=1000,
    min_ratings_pelicula=1000,
    frac_sample=0.05,
    return_pivot=False
)

# Cargar metadata de películas
movies = pd.read_csv('/mnt/datasets/ml-32m/movies.csv')

# Función para actualizar la interfaz
def actualizar_interfaz():
    usuario_x = int(entry_usuario.get())
    k = int(entry_k.get())
    tipo = entry_tipo.get().lower().strip()
    umbral = float(entry_umbral.get())

    # Selección de función de distancia
    funciones = {
        "euclidiana": distancia_euclidiana,
        "manhattan": distancia_manhattan,
        "coseno": similitud_coseno,
        "pearson": correlacion_pearson,
    }
    f = funciones.get(tipo)
    if not f:
        text_area.insert(tk.END, "Tipo de distancia no reconocida.\n")
        return

    # Crear diccionario de ratings por usuario para KNN
    user_ratings_dict = {
        user: dict(grupo[['movieId', 'rating']].values)
        for user, grupo in data.groupby('userId')
    }

    # Ejecutar KNN
    vecinos = knn(usuario_x, k, f, user_ratings_dict, obtener_usuarios(data))
    if not vecinos:
        text_area.insert(tk.END, "No se encontraron vecinos.\n")
        return

    text_area.insert(tk.END, f"Vecinos más cercanos de {usuario_x} usando {tipo}:\n")
    for i, (vecino, puntaje) in enumerate(vecinos, 1):
        text_area.insert(tk.END, f"{i}. Vecino: {vecino} → Puntaje: {round(puntaje, 4)}\n")

    # Visualización de la red de vecinos
    fig = visualizar_knn(usuario_x, vecinos, tipo)
    canvas.figure = fig
    canvas.draw()

    # Mostrar tabla de calificaciones de vecinos
    tabla = mostrar_tabla_vecinos(vecinos, data)
    if tabla is not None:
        text_area.insert(tk.END, "\nTabla de calificaciones de vecinos:\n")
        text_area.insert(tk.END, tabla.to_string())

    # Preparar info de películas vistas/no vistas y géneros del usuario
    peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizados = preparar_datos(data, movies, usuario_x)

    # Generar recomendaciones usando vecinos
    resultados_recomendaciones = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral)

    # Aplicar filtro por géneros favoritos y mostrar final
    nueva_lista_filtrada = filtrar_recomendaciones(vector_generos_priorizados, resultados_recomendaciones)
    recomendaciones = mostrar_recomendaciones_personalizadas(vector_generos_priorizados, nueva_lista_filtrada)
    text_area.insert(tk.END, "\nRecomendaciones personalizadas:\n")
    text_area.insert(tk.END, recomendaciones.to_string())

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Recomendación")

# Entradas para los parámetros
tk.Label(root, text="Usuario para KNN (userId):").pack()
entry_usuario = tk.Entry(root)
entry_usuario.pack()

tk.Label(root, text="Número de vecinos K:").pack()
entry_k = tk.Entry(root)
entry_k.pack()

tk.Label(root, text="Tipo de distancia:").pack()
entry_tipo = tk.Entry(root)
entry_tipo.pack()

tk.Label(root, text="Umbral mínimo de calificación:").pack()
entry_umbral = tk.Entry(root)
entry_umbral.pack()

# Botón para ejecutar la actualización
btn_actualizar = tk.Button(root, text="Actualizar", command=actualizar_interfaz)
btn_actualizar.pack()

# Área de texto para mostrar los resultados
text_area = tk.Text(root, height=20, width=80)
text_area.pack()

# Área para la visualización del grafo
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Iniciar la aplicación
root.mainloop()
