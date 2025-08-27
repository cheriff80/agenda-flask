from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
EVENTOS_FILE = "eventos.json"

# ----------------------
# Funciones auxiliares
# ----------------------
def cargar_eventos():
    if not os.path.exists(EVENTOS_FILE):
        return []
    with open(EVENTOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_eventos(eventos):
    with open(EVENTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(eventos, f, indent=4, ensure_ascii=False)

# ----------------------
# Rutas principales
# ----------------------
@app.route("/")
def index():
    eventos = cargar_eventos()
    return render_template("index.html", eventos=eventos)

@app.route("/add", methods=["GET", "POST"])
def add_evento():
    if request.method == "POST":
        nuevo_evento = {
            "id": datetime.now().strftime("%Y%m%H%M%S"),
            "titulo": request.form["titulo"],
            "fecha": request.form["fecha"],
            "hora": request.form["hora"],
            "aviso_horas": int(request.form["aviso_horas"])
        }
        eventos = cargar_eventos()
        eventos.append(nuevo_evento)
        guardar_eventos(eventos)
        return redirect(url_for("index"))
    return render_template("add_evento.html")

@app.route("/edit/<evento_id>", methods=["GET", "POST"])
def edit_evento(evento_id):
    eventos = cargar_eventos()
    evento = next((e for e in eventos if e["id"] == evento_id), None)
    if not evento:
        return "Evento no encontrado", 404

    if request.method == "POST":
        evento["titulo"] = request.form["titulo"]
        evento["fecha"] = request.form["fecha"]
        evento["hora"] = request.form["hora"]
        evento["aviso_horas"] = int(request.form["aviso_horas"])
        guardar_eventos(eventos)
        return redirect(url_for("index"))

    return render_template("edit_evento.html", evento=evento)

@app.route("/delete/<evento_id>", methods=["POST"])
def delete_evento(evento_id):
    eventos = cargar_eventos()
    eventos = [e for e in eventos if e["id"] != evento_id]
    guardar_eventos(eventos)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)



