"""API REST (Flask) del gestor de torneo eliminatorio."""
from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, render_template, request
from flask.typing import ResponseReturnValue

from tree import BinaryTree, TreeError

app = Flask(__name__)
tree = BinaryTree()

# Los 8 equipos de ejemplo se insertan en este orden para obtener un árbol balanceado.
SAMPLE_TEAMS: list[str] = [
    "Jaguares", "Dragones", "Pumas", "Albatros",
    "Estrellas", "Lobos", "Rayos", "Zorros",
]


def ok(payload: dict[str, Any], status: int = 200) -> ResponseReturnValue:
    return jsonify({"ok": True, **payload}), status


def fail(message: str, status: int = 400) -> ResponseReturnValue:
    return jsonify({"ok": False, "error": message}), status


def read_name() -> str:
    """Lee el campo 'value' del JSON recibido."""
    data = request.get_json(silent=True) or {}
    value = data.get("value", "")
    if not isinstance(value, str):
        raise TreeError("El nombre del equipo debe ser texto.")
    return value


@app.errorhandler(TreeError)
def handle_tree_error(err: TreeError) -> ResponseReturnValue:
    return fail(str(err))


@app.errorhandler(404)
def handle_404(_: Exception) -> ResponseReturnValue:
    return fail("Recurso no encontrado.", 404)


@app.errorhandler(405)
def handle_405(_: Exception) -> ResponseReturnValue:
    return fail("Método no permitido.", 405)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/tree")
def get_tree() -> ResponseReturnValue:
    return ok({"tree": tree.to_dict()})


@app.post("/api/insert")
def insert() -> ResponseReturnValue:
    path = tree.insert(read_name())
    return ok({"path": path, "tree": tree.to_dict(), "message": f"Equipo «{path[-1]}» insertado."}, 201)


@app.post("/api/search")
def search() -> ResponseReturnValue:
    result = tree.search(read_name())
    msg = "Equipo encontrado." if result["found"] else "El equipo no está en el árbol."
    return ok({**result, "message": msg})


@app.post("/api/delete")
def delete() -> ResponseReturnValue:
    name = tree.delete(read_name())
    return ok({"tree": tree.to_dict(), "message": f"Equipo «{name}» eliminado."})


@app.post("/api/reset")
def reset() -> ResponseReturnValue:
    tree.clear()
    return ok({"tree": None, "message": "Árbol reiniciado."})


@app.post("/api/sample")
def load_sample() -> ResponseReturnValue:
    tree.clear()
    for team in SAMPLE_TEAMS:
        tree.insert(team)
    return ok({"tree": tree.to_dict(), "message": "Ejemplo cargado: 8 equipos."})


@app.get("/api/metrics")
def get_metrics() -> ResponseReturnValue:
    return ok({"metrics": tree.metrics()})


@app.get("/api/traversal/<kind>")
def get_traversal(kind: str) -> ResponseReturnValue:
    return ok({"kind": kind, "order": tree.traversal(kind)})


@app.get("/api/rounds")
def get_rounds() -> ResponseReturnValue:
    """Rondas del torneo: cada nivel del árbol es una ronda."""
    tree_dict = tree.to_dict()
    if tree_dict is None:
        raise TreeError("El árbol está vacío. Inserta equipos primero.")
    rounds: list[list[str]] = []
    level = [tree_dict]
    while level:
        rounds.append([n["value"] for n in level])
        level = [c for n in level for c in (n["left"], n["right"]) if c]
    return ok({"rounds": rounds})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
