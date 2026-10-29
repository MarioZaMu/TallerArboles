"use strict";

// Estado de la interfaz -----------------------------------------------------
const NS = "http://www.w3.org/2000/svg";
const STEP_MS = 650;
let currentTree = null;
let busy = false;       // evita lanzar dos animaciones a la vez
let runId = 0;          // cancela animaciones anteriores

const $ = (id) => document.getElementById(id);
const input = $("team-input");

// API -----------------------------------------------------------------------
async function api(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(path, opts);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Error desconocido.");
    return data;
  } catch (err) {
    if (err instanceof TypeError) throw new Error("No se pudo conectar con el servidor.");
    throw err;
  }
}

function say(text, kind = "") {
  const box = $("message");
  box.textContent = text;
  box.className = "message " + kind;
}

// Render del árbol en SVG ---------------------------------------------------
const X_GAP = 88, Y_GAP = 90, R = 35, PAD_X = 60, PAD_TOP = 50;

function layout(tree) {
  // x = posición inorden, y = nivel -> sin cruces de aristas
  const nodes = [];
  let idx = 0;
  (function walk(n, parent) {
    if (!n) return;
    walk(n.left, n);
    const item = { ...n, x: PAD_X + idx++ * X_GAP, y: PAD_TOP + (n.level - 1) * Y_GAP, parent };
    n._pos = item;
    nodes.push(item);
    walk(n.right, n);
  })(tree, null);
  return nodes;
}

function el(name, attrs = {}, text) {
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text !== undefined) e.textContent = text;
  return e;
}

function render(tree, popValue = null) {
  currentTree = tree;
  const canvas = $("canvas");
  canvas.innerHTML = "";
  if (!tree) {
    canvas.innerHTML = '<div class="empty">El árbol está vacío.<br>Inserta un equipo o pulsa «Cargar ejemplo».</div>';
    return;
  }
  const nodes = layout(tree);
  const maxLevel = Math.max(...nodes.map((n) => n.level));
  const width = PAD_X * 2 + (nodes.length - 1) * X_GAP + 70;
  const height = PAD_TOP + (maxLevel - 1) * Y_GAP + 60;
  const svg = el("svg", { width, height, viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "Árbol binario del torneo" });

  for (let l = 1; l <= maxLevel; l++) {
    const y = PAD_TOP + (l - 1) * Y_GAP;
    svg.appendChild(el("line", { x1: 0, x2: width, y1: y + 44, y2: y + 44, class: "level-line" }));
    svg.appendChild(el("text", { x: 8, y: y - 34, class: "level-label" }, `Ronda ${l}`));
  }
  const edges = el("g");
  const circles = el("g");
  for (const n of nodes) {
    if (n.parent) {
      const p = n.parent._pos;
      const e = el("line", { x1: p.x, y1: p.y, x2: n.x, y2: n.y, class: "edge", "data-edge": n.value });
      edges.appendChild(e);
    }
  }
  const typeName = { root: "Raíz", branch: "Rama", leaf: "Hoja" };
  for (const n of nodes) {
    const g = el("g", { class: `node ${n.type}` + (n.value === popValue ? " pop" : ""), "data-value": n.value, tabindex: 0 });
    g.appendChild(el("title", {}, `${n.value} · ${typeName[n.type]} · Nivel ${n.level} · Grado ${n.degree}`));
    g.appendChild(el("circle", { cx: n.x, cy: n.y, r: R }));
    const label = n.value.length > 9 ? n.value.slice(0, 8) + "…" : n.value;
    g.appendChild(el("text", { x: n.x, y: n.y + 4 }, label));
    g.addEventListener("click", () => { input.value = n.value; showNodeInfo(n.value); });
    g.addEventListener("keydown", (ev) => { if (ev.key === "Enter") { input.value = n.value; showNodeInfo(n.value); } });
    circles.appendChild(g);
  }
  svg.appendChild(edges);
  svg.appendChild(circles);
  canvas.appendChild(svg);
}

// Animaciones ---------------------------------------------------------------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const nodeEl = (v) => [...document.querySelectorAll(".node")].find((n) => n.dataset.value === v);
const edgeEl = (v) => [...document.querySelectorAll(".edge")].find((n) => n.dataset.edge === v);

function clearHighlights() {
  document.querySelectorAll(".node").forEach((n) => n.classList.remove("visit", "visited", "found"));
  document.querySelectorAll(".edge").forEach((e) => e.classList.remove("hot", "found"));
}

/** Resalta nodo por nodo; devuelve false si otra animación la canceló. */
async function animate(values, { onStep, finalClass } = {}) {
  const myRun = ++runId;
  clearHighlights();
  for (let i = 0; i < values.length; i++) {
    if (myRun !== runId) return false;
    const n = nodeEl(values[i]);
    document.querySelectorAll(".node.visit").forEach((x) => x.classList.replace("visit", "visited"));
    if (n) n.classList.add("visit");
    const e = edgeEl(values[i]);
    if (e && finalClass !== "none") e.classList.add("hot");
    if (onStep) onStep(i);
    await sleep(STEP_MS);
  }
  if (myRun !== runId) return false;
  document.querySelectorAll(".node.visit").forEach((x) => x.classList.replace("visit", "visited"));
  return true;
}

function setBusy(v) {
  busy = v;
  document.querySelectorAll(".btn").forEach((b) => (b.disabled = v));
}

async function guarded(fn) {
  if (busy) return;
  try { await fn(); }
  catch (err) { say(err.message, "error"); }
  finally { setBusy(false); }
}

// Métricas ------------------------------------------------------------------
async function refreshMetrics() {
  const { metrics: m } = await api("/api/metrics");
  $("m-height").textContent = m.height;
  $("m-weight").textContent = m.weight;
  $("m-order").textContent = m.order;
  $("m-degree").textContent = m.max_degree;
  $("m-leaves").textContent = m.leaf_count;
  $("m-branches").textContent = m.branch_count;
  window.__metrics = m;
}

function showNodeInfo(value) {
  const m = window.__metrics;
  const info = m && m.nodes.find((n) => n.value === value);
  if (!info) return;
  const sib = info.siblings.length ? info.siblings.join(", ") : "ninguno";
  $("node-info").textContent = `${info.value}: nivel ${info.level}, grado ${info.degree}, hermanos: ${sib}.`;
}

// Acciones ------------------------------------------------------------------
$("team-form").addEventListener("submit", (ev) => {
  ev.preventDefault();
  guarded(async () => {
    setBusy(true);
    const data = await api("/api/insert", "POST", { value: input.value });
    // Primero se muestra el árbol anterior con el camino de inserción, luego el nuevo.
    const previous = data.path.slice(0, -1);
    if (previous.length) await animate(previous, { finalClass: "none" });
    render(data.tree, data.path[data.path.length - 1]);
    await refreshMetrics();
    say(data.message, "success");
    input.value = "";
    input.focus();
  });
});

$("btn-search").addEventListener("click", () =>
  guarded(async () => {
    setBusy(true);
    const data = await api("/api/search", "POST", { value: input.value });
    const ok = await animate(data.path);
    if (ok && data.found) {
      const last = nodeEl(data.path[data.path.length - 1]);
      if (last) last.classList.add("found");
      document.querySelectorAll(".edge.hot").forEach((e) => e.classList.replace("hot", "found"));
    }
    say(`${data.message} Camino: ${data.path.join(" → ")}.`,
      data.found ? "success" : "error");
  }));

$("btn-delete").addEventListener("click", () =>
  guarded(async () => {
    setBusy(true);
    const found = await api("/api/search", "POST", { value: input.value });
    if (!found.found) throw new Error(`El equipo «${input.value.trim()}» no existe en el árbol.`);
    await animate(found.path);
    const data = await api("/api/delete", "POST", { value: input.value });
    render(data.tree);
    await refreshMetrics();
    say(data.message, "success");
    input.value = "";
  }));

$("btn-sample").addEventListener("click", () =>
  guarded(async () => {
    setBusy(true);
    const data = await api("/api/sample", "POST");
    render(data.tree);
    await refreshMetrics();
    $("trav-result").innerHTML = "";
    say(data.message, "success");
  }));

$("btn-reset").addEventListener("click", () =>
  guarded(async () => {
    setBusy(true);
    const data = await api("/api/reset", "POST");
    runId++;
    render(data.tree);
    await refreshMetrics();
    $("trav-result").innerHTML = "";
    $("node-info").textContent = "Haz clic en un nodo para ver su nivel, grado y hermanos.";
    say(data.message, "success");
  }));

const TRAV_NAMES = { inorder: "Inorden", preorder: "Preorden", postorder: "Postorden", levelorder: "Por niveles" };
document.querySelectorAll(".trav").forEach((btn) =>
  btn.addEventListener("click", () =>
    guarded(async () => {
      setBusy(true);
      const kind = btn.dataset.kind;
      const data = await api(`/api/traversal/${kind}`);
      const list = $("trav-result");
      list.innerHTML = "";
      data.order.forEach((v) => { const li = document.createElement("li"); li.textContent = v; list.appendChild(li); });
      $("trav-title").textContent = `Recorrido ${TRAV_NAMES[kind]}`;
      const items = list.querySelectorAll("li");
      await animate(data.order, { finalClass: "none", onStep: (i) => items[i].classList.add("on") });
      say(`Recorrido ${TRAV_NAMES[kind].toLowerCase()} completado.`, "success");
    })));

// Inicio --------------------------------------------------------------------
(async () => {
  try {
    const data = await api("/api/tree");
    render(data.tree);
    await refreshMetrics();
  } catch (err) { say(err.message, "error"); }
})();
