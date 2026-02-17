from flask import Flask, render_template, request, jsonify, send_file
import requests
import tempfile
import os

app = Flask(__name__)

# Vector Express public API base
BASE_URL = "https://vector.express/api/v2/public"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-svg", methods=["POST"])
def upload_svg():
    """
    1. 受け取った DXF を Vector Express に投げる
    2. 変換パスを取得
    3. SVG を取得して Flask で返す
    """
    dxf_file = request.files.get("file")
    if not dxf_file:
        return jsonify({"error": "No file uploaded"}), 400

    # Save temp file
    temp_dxf = tempfile.NamedTemporaryFile(delete=False, suffix=".dxf")
    dxf_file.save(temp_dxf.name)

    try:
        # ◆ ① 変換パスを取得
        paths_resp = requests.get(f"{BASE_URL}/convert/dxf/auto/svg/")
        paths_resp.raise_for_status()
        paths = paths_resp.json()

        # paths から最初の変換プログラムパスを使う
        # 例: "dxf/cadlib/svg/"
        program_path = paths[0]

        # ◆ ② DXF を POST
        with open(temp_dxf.name, "rb") as f:
            convert_resp = requests.post(
                f"{BASE_URL}/convert/{program_path}",
                data=f.read()
            )
        convert_resp.raise_for_status()
        result = convert_resp.json()

        # 変換結果から SVG を GET
        svg_url = result["resultUrl"]
        svg_resp = requests.get(svg_url)
        svg_resp.raise_for_status()

        # SVG を返す
        return svg_resp.text, 200, {"Content-Type": "image/svg+xml"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.unlink(temp_dxf.name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
