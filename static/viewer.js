const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

document.getElementById("fileInput").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    console.log("Selected file:", file);

    const reader = new FileReader();
    reader.onload = async () => {
        const arrayBuffer = reader.result;
        const bytes = new Uint8Array(arrayBuffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        const base64 = btoa(binary);

        const formData = new FormData();
        formData.append("file", base64);

        try {
            const res = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            console.log("DXF data:", data);

            if (!data.lines || !data.bbox) {
                alert("DXF読み込みエラー:\n" + (data.error || "不明なエラー"));
                return;
            }

            draw(data.lines, data.bbox);
        } catch (err) {
            console.error("Upload error:", err);
            alert("ファイルアップロードに失敗しました");
        }
    };

    reader.readAsArrayBuffer(file);
});

function draw(lines, bbox) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "black";

    const padding = 20; // canvas の端に余白
    const scaleX = (canvas.width - 2*padding) / (bbox.max_x - bbox.min_x || 1);
    const scaleY = (canvas.height - 2*padding) / (bbox.max_y - bbox.min_y || 1);
    const scale = Math.min(scaleX, scaleY);

    const offsetX = padding - bbox.min_x * scale + (canvas.width - (bbox.max_x - bbox.min_x) * scale)/2;
    const offsetY = padding - bbox.min_y * scale + (canvas.height - (bbox.max_y - bbox.min_y) * scale)/2;

    lines.forEach(l => {
        ctx.beginPath();
        ctx.moveTo(l.x1 * scale + offsetX, canvas.height - (l.y1 * scale + offsetY));
        ctx.lineTo(l.x2 * scale + offsetX, canvas.height - (l.y2 * scale + offsetY));
        ctx.stroke();
    });
}
