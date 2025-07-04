from flask import Flask, render_template, request
from dask.distributed import Client
import pandas as pd
import os

# === Importaciones del sistema de recomendación ===
from knn.load_data import cargar_rating_matrix
from knn.preparar_datos import obtener_usuarios, preparar_datos
from knn.knn import knn
from knn.distancias import (
    distancia_euclidiana,
    distancia_manhattan,
    similitud_coseno,
    correlacion_pearson,
)
from knn.tabla_recomendacion import mostrar_tabla_vecinos
from knn.recomendador import recomendar_peliculas
from knn.filtrar_recomendaciones import filtrar_recomendaciones

# === Flask app ===
app = Flask(__name__)

# === Conectar a Dask ===
client = Client("tcp://10.7.135.127:8786")
print("✅ Conectado a Dask scheduler remoto")
print(client)

# === Cargar datos solo una vez ===
data = cargar_rating_matrix(
    path="/mnt/datasets/ml-32m/ratings.csv",
    min_ratings_usuario=1000,
    min_ratings_pelicula=1000,
    frac_sample=0.05,
    return_pivot=False
)
movies = pd.read_csv("/mnt/datasets/ml-32m/movies.csv")
usuarios = obtener_usuarios(data)

# === Diccionario global de ratings ===
user_ratings_dict = {
    uid: dict(grp[["movieId", "rating"]].values)
    for uid, grp in data.groupby("userId")
}

# === Distancias disponibles ===
distancias = {
    "euclidiana": distancia_euclidiana,
    "manhattan": distancia_manhattan,
    "coseno": similitud_coseno,
    "pearson": correlacion_pearson
}

@app.route("/", methods=["GET", "POST"])
def index():
    recomendaciones = []
    usuario_id = None
    k = 5
    error = None

    if request.method == "POST":
        try:
            usuario_id = int(request.form["usuario_id"])
            k = int(request.form["k"])

            vecinos = knn(usuario_id, k, distancia_euclidiana, user_ratings_dict, usuarios)
            if not vecinos:
                error = "No se encontraron vecinos."
                return render_template("index.html", usuarios=usuarios, error=error)

            tabla = mostrar_tabla_vecinos(vecinos, data)
            if tabla is None:
                error = "No hay datos suficientes para recomendaciones."
                return render_template("index.html", usuarios=usuarios, error=error)

            peliculas_no_vistas_df, peliculas_vistas_info, vector_generos_priorizado = preparar_datos(
                data, movies, usuario_id
            )

            resultados = recomendar_peliculas(vecinos, peliculas_no_vistas_df, tabla, umbral_vecinos=3.0)
            recomendaciones = filtrar_recomendaciones(vector_generos_priorizado, resultados)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        usuarios=usuarios,
        recomendaciones=recomendaciones,
        usuario_id=usuario_id,
        k=k,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)