"""Árbol binario de búsqueda implementado a mano (sin librerías de árboles).

Cada equipo del torneo es un nodo; el orden se define por el nombre
(comparación sin distinguir mayúsculas/minúsculas).
"""
from __future__ import annotations

from collections import deque
from typing import Any, Optional


class TreeError(Exception):
    """Error de dominio del árbol; el mensaje ya está en español."""


class Node:
    """Nodo del árbol: guarda un valor y referencias a sus hijos."""

    def __init__(self, value: str) -> None:
        self.value: str = value
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def degree(self) -> int:
        """Grado del nodo: cantidad de hijos (0, 1 o 2)."""
        return (self.left is not None) + (self.right is not None)

    def is_leaf(self) -> bool:
        """Un nodo hoja no tiene hijos."""
        return self.left is None and self.right is None


def _key(value: str) -> str:
    """Clave de comparación: sin distinguir mayúsculas ni espacios extremos."""
    return value.strip().casefold()


class BinaryTree:
    """Árbol binario de búsqueda (ABB). Orden del árbol = 2."""

    ORDER: int = 2

    def __init__(self) -> None:
        self.root: Optional[Node] = None

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    @staticmethod
    def _clean(value: Any) -> str:
        """Valida que el valor sea un texto no vacío y lo normaliza."""
        if not isinstance(value, str) or not value.strip():
            raise TreeError("El nombre del equipo no puede estar vacío.")
        return " ".join(value.split())

    def _require_not_empty(self) -> None:
        if self.root is None:
            raise TreeError("El árbol está vacío. Inserta equipos primero.")

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def insert(self, value: str) -> list[str]:
        """Inserta un valor. Devuelve el camino recorrido hasta su posición.

        Lanza TreeError si está vacío o duplicado.
        """
        value = self._clean(value)
        new_node = Node(value)
        if self.root is None:
            self.root = new_node
            return [value]
        path: list[str] = []
        current = self.root
        while True:
            path.append(current.value)
            if _key(value) == _key(current.value):
                raise TreeError(f"El equipo «{value}» ya está registrado.")
            if _key(value) < _key(current.value):
                if current.left is None:
                    current.left = new_node
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right
        path.append(value)
        return path

    def search(self, value: str) -> dict[str, Any]:
        """Busca un valor. Devuelve {'found': bool, 'path': [...]}."""
        value = self._clean(value)
        self._require_not_empty()
        path: list[str] = []
        current = self.root
        while current is not None:
            path.append(current.value)
            if _key(value) == _key(current.value):
                return {"found": True, "path": path}
            current = current.left if _key(value) < _key(current.value) else current.right
        return {"found": False, "path": path}

    def delete(self, value: str) -> str:
        """Elimina un valor (hoja, un hijo o dos hijos). Devuelve el nombre borrado."""
        value = self._clean(value)
        self._require_not_empty()
        deleted: list[str] = []
        self.root = self._delete(self.root, value, deleted)
        if not deleted:
            raise TreeError(f"El equipo «{value}» no existe en el árbol.")
        return deleted[0]

    def _delete(self, node: Optional[Node], value: str, deleted: list[str]) -> Optional[Node]:
        if node is None:
            return None
        if _key(value) < _key(node.value):
            node.left = self._delete(node.left, value, deleted)
        elif _key(value) > _key(node.value):
            node.right = self._delete(node.right, value, deleted)
        else:
            if not deleted:
                deleted.append(node.value)
            # Caso 1: hoja
            if node.is_leaf():
                return None
            # Caso 2: un solo hijo -> lo sube
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Caso 3: dos hijos -> sucesor inorden (mínimo del subárbol derecho)
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.value = successor.value
            node.right = self._delete_min_replace(node.right, successor.value)
        return node

    def _delete_min_replace(self, node: Optional[Node], value: str) -> Optional[Node]:
        """Quita el nodo sucesor (que tiene a lo sumo hijo derecho)."""
        if node is None:
            return None
        if node.left is None:
            return node.right
        node.left = self._delete_min_replace(node.left, value)
        return node

    def clear(self) -> None:
        """Reinicia el árbol."""
        self.root = None

    def is_empty(self) -> bool:
        return self.root is None

    # ------------------------------------------------------------------
    # Recorridos (devuelven listas)
    # ------------------------------------------------------------------
    def inorder(self) -> list[str]:
        """Izquierda, raíz, derecha (resultado ordenado alfabéticamente)."""
        out: list[str] = []

        def visit(n: Optional[Node]) -> None:
            if n:
                visit(n.left)
                out.append(n.value)
                visit(n.right)

        visit(self.root)
        return out

    def preorder(self) -> list[str]:
        """Raíz, izquierda, derecha."""
        out: list[str] = []

        def visit(n: Optional[Node]) -> None:
            if n:
                out.append(n.value)
                visit(n.left)
                visit(n.right)

        visit(self.root)
        return out

    def postorder(self) -> list[str]:
        """Izquierda, derecha, raíz."""
        out: list[str] = []

        def visit(n: Optional[Node]) -> None:
            if n:
                visit(n.left)
                visit(n.right)
                out.append(n.value)

        visit(self.root)
        return out

    def levelorder(self) -> list[str]:
        """Por niveles (anchura), usando una cola."""
        out: list[str] = []
        queue: deque[Node] = deque([self.root] if self.root else [])
        while queue:
            n = queue.popleft()
            out.append(n.value)
            if n.left:
                queue.append(n.left)
            if n.right:
                queue.append(n.right)
        return out

    def traversal(self, kind: str) -> list[str]:
        """Selecciona el recorrido por nombre (inorder, preorder, postorder, levelorder)."""
        methods = {
            "inorder": self.inorder,
            "preorder": self.preorder,
            "postorder": self.postorder,
            "levelorder": self.levelorder,
        }
        if kind not in methods:
            raise TreeError("Recorrido no válido. Usa: inorder, preorder, postorder o levelorder.")
        self._require_not_empty()
        return methods[kind]()

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------
    def height(self) -> int:
        """Altura: niveles del camino más largo raíz-hoja (la raíz es nivel 1)."""

        def h(n: Optional[Node]) -> int:
            return 0 if n is None else 1 + max(h(n.left), h(n.right))

        return h(self.root)

    def weight(self) -> int:
        """Peso: cantidad total de nodos."""

        def w(n: Optional[Node]) -> int:
            return 0 if n is None else 1 + w(n.left) + w(n.right)

        return w(self.root)

    def _find(self, value: str) -> tuple[Optional[Node], Optional[Node], int]:
        """Devuelve (nodo, padre, nivel) del valor buscado."""
        value = self._clean(value)
        self._require_not_empty()
        parent: Optional[Node] = None
        current = self.root
        level = 1
        while current is not None:
            if _key(value) == _key(current.value):
                return current, parent, level
            parent = current
            current = current.left if _key(value) < _key(current.value) else current.right
            level += 1
        raise TreeError(f"El equipo «{value}» no existe en el árbol.")

    def level_of(self, value: str) -> int:
        """Nivel del nodo (raíz = 1)."""
        return self._find(value)[2]

    def degree_of(self, value: str) -> int:
        """Grado del nodo: cantidad de hijos."""
        return self._find(value)[0].degree()  # type: ignore[union-attr]

    def siblings_of(self, value: str) -> list[str]:
        """Hermanos del nodo: otros hijos de su mismo padre."""
        node, parent, _ = self._find(value)
        if parent is None:
            return []
        return [c.value for c in (parent.left, parent.right) if c is not None and c is not node]

    def order(self) -> int:
        """Orden del árbol: máximo de hijos por nodo (2 en un árbol binario)."""
        return self.ORDER

    def max_degree(self) -> int:
        """Mayor grado realmente presente en el árbol."""
        return max((d for _, d in self._walk_degrees()), default=0)

    def _walk_degrees(self) -> list[tuple[str, int]]:
        out: list[tuple[str, int]] = []
        queue: deque[Node] = deque([self.root] if self.root else [])
        while queue:
            n = queue.popleft()
            out.append((n.value, n.degree()))
            queue.extend(c for c in (n.left, n.right) if c)
        return out

    def leaves(self) -> list[str]:
        """Nodos hoja (sin hijos), en orden inorden."""
        out: list[str] = []

        def visit(n: Optional[Node]) -> None:
            if n:
                visit(n.left)
                if n.is_leaf():
                    out.append(n.value)
                visit(n.right)

        visit(self.root)
        return out

    def branches(self) -> list[str]:
        """Nodos rama: no son la raíz y tienen al menos un hijo."""
        out: list[str] = []

        def visit(n: Optional[Node]) -> None:
            if n:
                visit(n.left)
                if n is not self.root and not n.is_leaf():
                    out.append(n.value)
                visit(n.right)

        visit(self.root)
        return out

    def node_types(self) -> dict[str, str]:
        """Mapa nombre -> 'root' | 'branch' | 'leaf'."""
        types: dict[str, str] = {}
        for name in self.inorder():
            types[name] = "leaf"
        for name in self.branches():
            types[name] = "branch"
        if self.root:
            # Un árbol de un solo nodo: la raíz se muestra como raíz.
            types[self.root.value] = "root"
        return types

    def metrics(self) -> dict[str, Any]:
        """Todas las métricas del árbol en un diccionario."""
        leaves, branches = self.leaves(), self.branches()
        nodes = [
            {
                "value": v,
                "level": self.level_of(v),
                "degree": d,
                "siblings": self.siblings_of(v),
            }
            for v, d in self._walk_degrees()
        ]
        return {
            "height": self.height(),
            "weight": self.weight(),
            "order": self.order(),
            "max_degree": self.max_degree(),
            "root": self.root.value if self.root else None,
            "leaves": leaves,
            "leaf_count": len(leaves),
            "branches": branches,
            "branch_count": len(branches),
            "nodes": nodes,
        }

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------
    def to_dict(self) -> Optional[dict[str, Any]]:
        """Serializa el árbol a un diccionario listo para JSON (None si está vacío)."""
        types = self.node_types()

        def conv(n: Optional[Node], level: int) -> Optional[dict[str, Any]]:
            if n is None:
                return None
            return {
                "value": n.value,
                "type": types[n.value],
                "level": level,
                "degree": n.degree(),
                "left": conv(n.left, level + 1),
                "right": conv(n.right, level + 1),
            }

        return conv(self.root, 1)
