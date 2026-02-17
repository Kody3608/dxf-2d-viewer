window.addEventListener("DOMContentLoaded", () => {

    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const fileInput = document.getElementById("fileInput");

    fileInput.addEventListener("change", async () => {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const lines = await res.json();
        console.log("DXF data:", lines);

        draw(lines);
    });

    function draw(lines) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.scale(1, -1); // DXF座標系対策

        ctx.beginPath();
        lines.forEach(l => {
            ctx.moveTo(l.x1, l.y1);
            ctx.lineTo(l.x2, l.y2);
        });
        ctx.strokeStyle = "black";
        ctx.stroke();

        ctx.restore();
    }

});
