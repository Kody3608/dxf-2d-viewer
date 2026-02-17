from flask import Flask, render_template, request, jsonify
import ezdxf
from io import BytesIO
import base64
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MBまで許可

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file_b64 = request.form.get("file")
        if not file_b64:
            return jsonify({"error": "No file received"}), 400

        data = base64.b64decode(file_b64)
        stream = BytesIO(data)

        doc = ezdxf.read(stream)
        msp = doc.modelspace()

        lines = []
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for e in msp:
            if e.dxftype() == "LINE":
                x1, y1 = e.dxf.start.x, e.dxf.start.y
                x2, y2 = e.dxf.end.x, e.dxf.end.y
                lines.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
                min_x = min(min_x, x1, x2)
                min_y = min(min_y, y1, y2)
                max_x = max(max_x, x1, x2)
                max_y = max(max_y, y1, y2)

        return jsonify({
            "lines": lines,
            "bbox": {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}
        })

    except Exception as e:
        print("DXF ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
