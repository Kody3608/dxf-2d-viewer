const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

document.getElementById("fileInput").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    console.log("Selected file:", file);

    const formData = new FormData();
    formData.append("file", file); // そのまま送るだけでOK

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        console.log("DXF data:", data);

        if (!Array.isArray(data)) {
            alert("DXF読み込みエラー:\n" + data.error);
            return;
        }

        draw(data);
    } catch (err) {
        console.error("Upload error:", err);
        alert("ファイルアップロードに失敗しました");
    }
});

function draw(lines) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "black";

    lines.forEach(l => {
        ctx.beginPath();
        ctx.moveTo(l.x1, canvas.height - l.y1);
        ctx.lineTo(l.x2, canvas.height - l.y2);
        ctx.stroke();
    });
}
