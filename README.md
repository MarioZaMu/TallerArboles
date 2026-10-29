# Gestor de torneo eliminatorio — Árbol Binario de Búsqueda

Taller de **Árboles** · Estructuras de Datos · Cuarto semestre.

## Descripción del caso

En un torneo eliminatorio los equipos se organizan en un **árbol binario de búsqueda (ABB) ordenado por nombre**.
Cada nivel del árbol se muestra como una **ronda** del torneo. Se pueden registrar equipos, buscarlos, retirarlos
(eliminarlos) y recorrer el árbol de cuatro formas. La estructura está implementada **a mano** en Python
(sin librerías de árboles) y se visualiza en SVG.

## Estructura

```
TallerArboles/
├── app.py              # API REST con Flask
├── tree.py             # Node y BinaryTree (el árbol implementado a mano)
├── requirements.txt
├── templates/index.html
├── static/css/style.css
├── static/js/app.js    # Visualización SVG y animaciones
└── tests/test_tree.py  # Pruebas con pytest
```

## Instalación y ejecución

```bash
pip install -r requirements.txt
python app.py
```

Abre <http://localhost:5000>. Para las pruebas:

```bash
python -m pytest
```

## Uso

1. Pulsa **Cargar ejemplo** para precargar 8 equipos.
2. Escribe un nombre y usa **Insertar**, **Buscar** o **Eliminar**. La búsqueda anima el camino recorrido desde la raíz.
3. Los botones de **Recorridos** animan el orden de visita nodo por nodo.
4. El panel de **Métricas en vivo** se actualiza tras cada cambio. Al hacer clic en un nodo se ven su nivel, grado y hermanos.
5. Colores: **raíz** amarillo, **rama** azul, **hoja** verde.

## API REST

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/tree` | Árbol completo en JSON |
| POST | `/api/insert` | Inserta `{"value": "..."}` |
| POST | `/api/search` | Busca y devuelve el camino |
| POST | `/api/delete` | Elimina un equipo |
| POST | `/api/reset` | Vacía el árbol |
| POST | `/api/sample` | Carga los 8 equipos de ejemplo |
| GET | `/api/metrics` | Métricas del árbol |
| GET | `/api/traversal/<inorder\|preorder\|postorder\|levelorder>` | Recorrido |
| GET | `/api/rounds` | Equipos agrupados por ronda (nivel) |

Los errores devuelven `{"ok": false, "error": "mensaje en español"}` (duplicados, entrada vacía, árbol vacío, equipo inexistente).

## Conceptos de árboles aplicados

| Concepto | Dónde se aplica |
|---|---|
| Nodo, raíz, hijo, padre | `Node` y `BinaryTree.root` en `tree.py` |
| Árbol binario / orden 2 | `BinaryTree.ORDER`; cada nodo tiene máximo 2 hijos |
| Propiedad del ABB | `insert` / `search`: menor a la izquierda, mayor a la derecha |
| Eliminación (hoja, un hijo, dos hijos) | `delete`: el caso de dos hijos usa el sucesor inorden |
| Recorridos en profundidad | `inorder`, `preorder`, `postorder` (recursivos) |
| Recorrido por niveles | `levelorder` con una cola; equivale a las rondas |
| Altura (raíz = nivel 1) | `height()` |
| Nivel de un nodo | `level_of()` |
| Peso | `weight()` = cantidad de nodos |
| Grado de un nodo | `degree_of()` = cantidad de hijos |
| Nodos hoja / rama / hermanos | `leaves()`, `branches()`, `siblings_of()` |
| Serialización | `to_dict()` → JSON para el frontend |
| Visualización | `static/js/app.js`: x = posición inorden, y = nivel |

Definiciones usadas: rama = nodo que no es la raíz y tiene al menos un hijo; hoja = nodo sin hijos.
