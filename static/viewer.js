const fileInput = document.getElementById("file");
const svg = document.getElementById("svg");

let viewBox = { x: 0, y: 0, w: 100, h: 100 };
let isPanning = false;
let start = { x: 0, y: 0 };

function updateViewBox() {
  svg.setAttribute(
    "viewBox",
    `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`
  );
}

fileInput.addEventListener("change", async () => {
  const form = new FormData();
  form.append("file", fileInput.files[0]);

  const res = await fetch("/upload", { method: "POST", body: form });
  const data = await res.json();

  svg.innerHTML = "";

  // ===== 自動フィット =====
  const b = data.bbox;
  const w = b.maxx - b.minx || 100;
  const h = b.maxy - b.miny || 100;
  const margin = 0.1;

  viewBox = {
    x: b.minx - w * margin,
    y: b.miny - h * margin,
    w: w * (1 + margin * 2),
    h: h * (1 + margin * 2)
  };
  updateViewBox();

  // ===== HATCH =====
  data.hatches.forEach(h => {
    const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    poly.setAttribute("points", h.boundary.map(p => p.join(",")).join(" "));
    poly.setAttribute("fill", "rgba(0,0,0,0.1)");
    poly.setAttribute("stroke", "black");
    svg.appendChild(poly);
  });

  // ===== Lines =====
  data.lines.forEach(l => {
    if (l.poly) {
      const el = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
      el.setAttribute("points", l.poly.map(p => p.join(",")).join(" "));
      el.setAttribute("fill", "none");
      el.setAttribute("stroke", "black");
      svg.appendChild(el);
    } else {
      const el = document.createElementNS("http://www.w3.org/2000/svg", "line");
      Object.entries(l).forEach(([k,v]) => el.setAttribute(k, v));
      el.setAttribute("stroke", "black");
      svg.appendChild(el);
    }
  });

  // ===== Circles =====
  data.circles.forEach(c => {
    const el = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    Object.entries(c).forEach(([k,v]) => el.setAttribute(k, v));
    el.setAttribute("fill", "none");
    el.setAttribute("stroke", "black");
    svg.appendChild(el);
  });

  // ===== Texts =====
  data.texts.forEach(t => {
    const el = document.createElementNS("http://www.w3.org/2000/svg", "text");
    el.setAttribute("x", t.x);
    el.setAttribute("y", t.y);
    el.setAttribute("font-size", "10");
    el.textContent = t.text;
    svg.appendChild(el);
  });
});

// ===== ズーム・パン（前回と同じ） =====
svg.addEventListener("wheel", e => {
  e.preventDefault();
  const scale = e.deltaY < 0 ? 0.9 : 1.1;

  const rect = svg.getBoundingClientRect();
  const mx = (e.clientX - rect.left) / rect.width;
  const my = (e.clientY - rect.top) / rect.height;

  const nx = viewBox.x + viewBox.w * mx;
  const ny = viewBox.y + viewBox.h * my;

  viewBox.w *= scale;
  viewBox.h *= scale;
  viewBox.x = nx - viewBox.w * mx;
  viewBox.y = ny - viewBox.h * my;

  updateViewBox();
}, { passive: false });

svg.addEventListener("mousedown", e => {
  isPanning = true;
  start = { x: e.clientX, y: e.clientY };
});

window.addEventListener("mousemove", e => {
  if (!isPanning) return;
  const dx = (e.clientX - start.x) * (viewBox.w / svg.clientWidth);
  const dy = (e.clientY - start.y) * (viewBox.h / svg.clientHeight);
  viewBox.x -= dx;
  viewBox.y -= dy;
  start = { x: e.clientX, y: e.clientY };
  updateViewBox();
});

window.addEventListener("mouseup", () => {
  isPanning = false;
});
