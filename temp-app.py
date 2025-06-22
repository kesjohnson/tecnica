from flask import Flask, request, jsonify, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

DATA_FOLDER = "data"
CSV_FILENAME = "datos_tecnica.csv"
os.makedirs(DATA_FOLDER, exist_ok=True)
CSV_PATH = os.path.join(DATA_FOLDER, CSV_FILENAME)

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH, parse_dates=["Fecha"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    if "Rating" not in df.columns:
        df["Rating"] = 0
else:
    df = pd.DataFrame(columns=["Fecha", "Ejercicio", "Velocidad", "Rating"])

@app.route("/upload", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if file:
        file.save(CSV_PATH)
        return jsonify({"message": "Archivo subido correctamente."})
    return jsonify({"error": "No se envió ningún archivo."}), 400

@app.route("/add", methods=["POST"])
def add_data():
    data = request.json
    nueva_fila = {
        "Fecha": data.get("Fecha", datetime.now().strftime("%Y-%m-%d")),
        "Ejercicio": data.get("Ejercicio", "Desconocido"),
        "Velocidad": data.get("Velocidad", 0),
        "Rating": data.get("Rating", 0)
    }
    global df
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    return jsonify({"message": "Datos agregados correctamente."})

@app.route("/grafico", methods=["GET"])
def generar_grafico():
    ejercicio = request.args.get("ejercicio")
    if ejercicio:
        datos_filtrados = df[df["Ejercicio"] == ejercicio]
    else:
        datos_filtrados = df

    if datos_filtrados.empty:
        return jsonify({"error": "No hay datos para graficar."}), 404

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        datos_filtrados["Fecha"],
        datos_filtrados["Velocidad"],
        c=datos_filtrados["Rating"],
        cmap="coolwarm",
        s=100,
        edgecolors="k"
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    ax.set_title(f"Evolución técnica{' - ' + ejercicio if ejercicio else ''}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Velocidad")

    leyenda = [Patch(color=scatter.cmap(scatter.norm(rating)), label=f"Rating: {rating}")
               for rating in sorted(datos_filtrados["Rating"].unique())]
    ax.legend(handles=leyenda, loc="best")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
