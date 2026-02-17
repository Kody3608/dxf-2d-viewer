const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// キャンバス初期化
canvas.width = 800;
canvas.height = 600;

// DXF描画
function drawDXF(entities) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!entities || entities.length === 0) {
    console.warn("No entities to draw");
    return;
  }

  // 全点収集
  let points = [];
  entities.forEach(e => {
    if (e.points) {
      e.points.forEach(p => points.push(p));
    }
  });

  if (points.length === 0) {
    console.warn("No points found");
    return;
  }

  // bounding box
  const xs = points.map(p => p[0]);
  const ys = points.map(p => p[1]);

  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const w = maxX - minX;
  const h = maxY - minY;

  const scale = Math.min(
    canvas.width / w,
    canvas.height / h
  ) * 0.9;

  const offsetX = (canvas.width - w * scale) / 2;
  const offsetY = (canvas.height - h * scale) / 2;

  ctx.strokeStyle = "#000";
  ctx.lineWidth = 1;

  // 描画
  entities.forEach(e => {
    if (!e.points || e.points.length < 2) return;

    ctx.beginPath();
    e.points.forEach((p, i) => {
      const x = (p[0] - minX) * scale + offsetX;
      const y = canvas.height - ((p[1] - minY) * scale + offsetY);

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  });
}

// アップロード処理
document.getElementById("fileInput").addEventListener("change", async e => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/upload", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  console.log("DXF data:", data); // ← 必ず確認

  drawDXF(data);
});
