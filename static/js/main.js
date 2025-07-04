document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formulario");
    const loader = document.querySelector(".loader");
    const resultadosDiv = document.getElementById("resultados");
    const peliculasDiv = document.getElementById("peliculas");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const userId = document.getElementById("user_id").value;
        const k = document.getElementById("k_value").value;

        // Mostrar loader
        loader.style.display = "block";

        try {
            const response = await fetch("/recomendar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: parseInt(userId), k: parseInt(k) })
            });

            const data = await response.json();

            // Limpiar resultados anteriores
            resultadosDiv.innerHTML = "";
            peliculasDiv.innerHTML = "";

            // Mostrar vecinos
            const vecinosHTML = data.vecinos.map(v => 
                `<li>Vecino: ${v.vecino_id} - Similitud: ${v.similitud.toFixed(4)}</li>`
            ).join("");
            resultadosDiv.innerHTML = `<h2>Vecinos más cercanos</h2><ul>${vecinosHTML}</ul>`;

            // Mostrar películas no vistas
            const peliculasHTML = data.peliculas_no_vistas.map(p => 
                `<li>${p.movieId} - ${p.title} (${p.genres})</li>`
            ).join("");
            peliculasDiv.innerHTML = `<h2>Películas no vistas</h2><ul>${peliculasHTML}</ul>`;

        } catch (err) {
            console.error("Error:", err);
            resultadosDiv.innerHTML = "<p style='color:red;'>Hubo un error al procesar la solicitud.</p>";
        } finally {
            loader.style.display = "none";
        }
    });
});
