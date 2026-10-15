import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# "Base de datos" en memoria: catálogo básico de autos
autos = [
    {"id": 1, "marca": "Toyota",    "modelo": "Supra", "anio": 2022, "precio": 385000, "color": "Rojo"},
    {"id": 2, "marca": "Nissan",    "modelo": "370z",   "anio": 2018, "precio": 295000, "color": "Gris"},
    {"id": 3, "marca": "Volkswagen","modelo": "GTI",   "anio": 2023, "precio": 450000, "color": "Negro"},
    {"id": 4, "marca": "Mazda",     "modelo": "MX-5", "anio": 2022, "precio": 420000, "color": "Rojo"},
    {"id": 5, "marca": "Chevrolet", "modelo": "Camaro",    "anio": 2020, "precio": 210000, "color": "Azul"},
]

CAMPOS = ["marca", "modelo", "anio", "precio", "color"]


def buscar_auto(auto_id):
    return next((a for a in autos if a["id"] == auto_id), None)


def validar(data):
    """Valida que vengan todos los campos y con el tipo correcto."""
    if not data:
        return "El cuerpo debe ser JSON"
    faltantes = [c for c in CAMPOS if c not in data]
    if faltantes:
        return f"Faltan campos: {', '.join(faltantes)}"
    if not isinstance(data["anio"], int) or not isinstance(data["precio"], (int, float)):
        return "'anio' debe ser entero y 'precio' numerico"
    return None


@app.route("/")
def inicio():
    return jsonify({"servicio": "Catálogo de autos", "version": "1.0", "rutas": "/autos"})


# GET /autos  (opcional: ?marca=Toyota&color=Blanco)
@app.route("/autos", methods=["GET"])
def listar_autos():
    resultado = autos
    marca = request.args.get("marca")
    color = request.args.get("color")
    if marca:
        resultado = [a for a in resultado if a["marca"].lower() == marca.lower()]
    if color:
        resultado = [a for a in resultado if a["color"].lower() == color.lower()]
    return jsonify({"total": len(resultado), "autos": resultado})


# GET /autos/<id>
@app.route("/autos/<int:auto_id>", methods=["GET"])
def obtener_auto(auto_id):
    auto = buscar_auto(auto_id)
    if auto is None:
        abort(404, description="Auto no encontrado")
    return jsonify(auto)


# POST /autos
@app.route("/autos", methods=["POST"])
def crear_auto():
    data = request.get_json(silent=True)
    error = validar(data)
    if error:
        abort(400, description=error)
    nuevo = {
        "id": max((a["id"] for a in autos), default=0) + 1,
        **{c: data[c] for c in CAMPOS},
    }
    autos.append(nuevo)
    return jsonify(nuevo), 201


# PUT /autos/<id>
@app.route("/autos/<int:auto_id>", methods=["PUT"])
def actualizar_auto(auto_id):
    auto = buscar_auto(auto_id)
    if auto is None:
        abort(404, description="Auto no encontrado")
    data = request.get_json(silent=True)
    error = validar(data)
    if error:
        abort(400, description=error)
    auto.update({c: data[c] for c in CAMPOS})
    return jsonify(auto)


# DELETE /autos/<id>
@app.route("/autos/<int:auto_id>", methods=["DELETE"])
def eliminar_auto(auto_id):
    auto = buscar_auto(auto_id)
    if auto is None:
        abort(404, description="Auto no encontrado")
    autos.remove(auto)
    return jsonify({"mensaje": "Auto eliminado", "id": auto_id})


# Errores en formato JSON
@app.errorhandler(400)
@app.errorhandler(404)
def manejar_error(e):
    return jsonify({"error": e.description}), e.code


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)