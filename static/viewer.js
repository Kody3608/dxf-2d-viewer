const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

function drawDXF(data) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 1️⃣ 全点を集める
  const points = [];
  data.forEach(ent => {
    ent.points.forEach(p => points.push(p));
  });

  if (points.length === 0) return;

  // 2️⃣ bounding box
  const xs = points.map(p => p[0]);
  const ys = points.map(p => p[1]);

  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const dxfWidth = maxX - minX;
  const dxfHeight = maxY - minY;

  // 3️⃣ scale
  const scale = Math.min(
    canvas.width / dxfWidth,
    canvas.height / dxfHeight
  ) * 0.9;

  const offsetX = (canvas.width - dxfWidth * scale) / 2;
  const offsetY = (canvas.height - dxfHeight * scale) / 2;

  // 4️⃣ 描画
  ctx.strokeStyle = "#000";
  ctx.lineWidth = 1;

  data.forEach(ent => {
    ctx.beginPath();
    ent.points.forEach((p, i) => {
      const x = (p[0] - minX) * scale + offsetX;
      const y = canvas.height - ((p[1] - minY) * scale + offsetY); // Y反転

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  });
}
