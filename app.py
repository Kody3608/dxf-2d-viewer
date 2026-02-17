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

        # バイト列を BytesIO に渡す前に文字コードを自動判定
        try:
            # まず UTF-8 として読み込む
            stream = BytesIO(data)
            doc = ezdxf.read(stream)
        except UnicodeDecodeError:
            # UTF-8 で失敗した場合、latin-1 としてデコードして再度バイト列に変換
            text = data.decode("latin-1")
            data_bytes = text.encode("utf-8")
            stream = BytesIO(data_bytes)
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
    port = int(os.environ.get("PORT", 10000))  # Render の PORT 環境変数対応
    app.run(host="0.0.0.0", port=port, debug=True)
