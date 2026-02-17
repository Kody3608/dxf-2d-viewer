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
        # まず request.files をチェック
        file = request.files.get("file")
        if file:
            # 通常の FileStorage ならそのまま読み込む
            data = file.read()
        else:
            # 日本語ファイル名などで文字列として送られた場合
            # request.form に Base64 文字列として送る方法に対応
            data_b64 = request.form.get("file")
            if not data_b64:
                return jsonify({"error": "No file received"}), 400
            import base64
            data = base64.b64decode(data_b64)

        stream = BytesIO(data)
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
