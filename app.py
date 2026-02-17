from flask import Flask, render_template, request, jsonify
import ezdxf
from io import BytesIO
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file received"}), 400

        data = file.read()

        # -------------------------------
        # ASCII かバイナリか自動判定
        # -------------------------------
        if data.startswith(b'0\nSECTION\n'):  # ASCII DXFの典型的な先頭
            try:
                # UTF-8で読み込めるか試す
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                # UTF-8で失敗したら latin-1 でデコードして再エンコード
                text = data.decode('latin-1')
            data_bytes = text.encode('utf-8')
            stream = BytesIO(data_bytes)
        else:
            # バイナリDXFはそのまま
            stream = BytesIO(data)

        # ezdxf で読み込み
        doc = ezdxf.read(stream)
        msp = doc.modelspace()

        lines = []
        for e in msp:
            if e.dxftype() == "LINE":
                lines.append({
                    "x1": e.dxf.start.x,
                    "y1": e.dxf.start.y,
                    "x2": e.dxf.end.x,
                    "y2": e.dxf.end.y,
                })

        return jsonify(lines)

    except Exception as e:
        print("DXF ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
