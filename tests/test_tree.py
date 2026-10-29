"""Pruebas básicas del árbol binario de búsqueda y de la API."""
import pytest

from app import app
from tree import BinaryTree, TreeError


def build(values: list[str]) -> BinaryTree:
    t = BinaryTree()
    for v in values:
        t.insert(v)
    return t


# Árbol de ejemplo:
#            Jaguares
#         /            \
#     Dragones          Pumas
#     /     \          /     \
# Albatros Estrellas Lobos Rayos
#                                  \
#                                  Zorros
SAMPLE = ["Jaguares", "Dragones", "Pumas", "Albatros", "Estrellas", "Lobos", "Rayos", "Zorros"]


def test_insert_and_duplicates():
    t = build(SAMPLE)
    assert t.weight() == 8
    with pytest.raises(TreeError):
        t.insert("jaguares")
    with pytest.raises(TreeError):
        t.insert("   ")


def test_insert_returns_path():
    t = build(["B", "A"])
    assert t.insert("C") == ["B", "C"]


def test_search():
    t = build(SAMPLE)
    assert t.search("Lobos") == {"found": True, "path": ["Jaguares", "Pumas", "Lobos"]}
    assert t.search("Nadie")["found"] is False
    with pytest.raises(TreeError):
        BinaryTree().search("A")


def test_delete_leaf_one_child_two_children():
    t = build(SAMPLE)
    t.delete("Albatros")                      # hoja
    assert "Albatros" not in t.inorder()
    t.delete("Rayos")                         # un hijo (Zorros sube)
    assert t.search("Zorros")["path"] == ["Jaguares", "Pumas", "Zorros"]
    t.delete("Jaguares")                      # dos hijos (raíz)
    assert t.root.value == "Lobos"
    assert t.inorder() == sorted(t.inorder(), key=str.casefold)
    assert t.weight() == 5
    with pytest.raises(TreeError):
        t.delete("Inexistente")
    with pytest.raises(TreeError):
        BinaryTree().delete("A")


def test_traversals():
    t = build(SAMPLE)
    assert t.inorder() == sorted(SAMPLE)
    assert t.preorder() == ["Jaguares", "Dragones", "Albatros", "Estrellas", "Pumas", "Lobos", "Rayos", "Zorros"]
    assert t.postorder() == ["Albatros", "Estrellas", "Dragones", "Lobos", "Zorros", "Rayos", "Pumas", "Jaguares"]
    assert t.levelorder() == ["Jaguares", "Dragones", "Pumas", "Albatros", "Estrellas", "Lobos", "Rayos", "Zorros"]
    with pytest.raises(TreeError):
        BinaryTree().traversal("inorder")


def test_metrics():
    t = build(SAMPLE)
    assert t.height() == 4
    assert t.weight() == 8
    assert t.order() == 2
    assert t.level_of("Jaguares") == 1
    assert t.level_of("Zorros") == 4
    assert t.degree_of("Jaguares") == 2
    assert t.degree_of("Rayos") == 1
    assert t.leaves() == ["Albatros", "Estrellas", "Lobos", "Zorros"]
    assert t.branches() == ["Dragones", "Pumas", "Rayos"]
    assert t.siblings_of("Dragones") == ["Pumas"]
    assert t.siblings_of("Jaguares") == []
    assert t.to_dict()["type"] == "root"
    assert BinaryTree().height() == 0


def test_api():
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/api/reset")
    r = c.post("/api/insert", json={"value": ""})
    assert r.status_code == 400 and "vacío" in r.get_json()["error"]
    assert c.get("/api/metrics").get_json()["metrics"]["weight"] == 0
    assert c.post("/api/sample").status_code == 200
    assert c.post("/api/insert", json={"value": "Pumas"}).status_code == 400
    assert c.get("/api/traversal/inorder").get_json()["order"][0] == "Albatros"
    assert c.get("/api/traversal/xyz").status_code == 400
    assert len(c.get("/api/rounds").get_json()["rounds"]) == 4
    c.post("/api/reset")
    assert c.get("/api/traversal/inorder").status_code == 400
