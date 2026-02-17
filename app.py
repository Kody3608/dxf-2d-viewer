from flask import Flask, render_template, request, jsonify
import requests
import tempfile
import os

app = Flask(__name__)

VECTOR_EXPRESS_BASE = "https://vector.express/api/v2/public"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-svg", methods=["POST"])
def upload_svg():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 一時ファイルに保存
    temp_dxf = tempfile.NamedTemporaryFile(delete=False, suffix=".dxf")
    file.save(temp_dxf.name)

    try:
        # ① 変換パスを取得
        paths_resp = requests.get(f"{VECTOR_EXPRESS_BASE}/convert/dxf/auto/svg/")
        paths_resp.raise_for_status()
        alternatives = paths_resp.json().get("alternatives")
        if not alternatives:
            return jsonify({"error": "No conversion alternatives found"}), 500

        # ここで program_path をフル URL にするのがステップ1
        program_path = alternatives[0]["path"]  # "/api/v2/public/convert/dxf/cad2svg/svg"
        convert_url = f"https://vector.express{program_path}"  # フル URL に変換

        # ② DXF ファイルを POST
        with open(temp_dxf.name, "rb") as f:
            convert_resp = requests.post(
                convert_url,
                data=f.read()
            )
        convert_resp.raise_for_status()
        result = convert_resp.json()

        # ③ SVG を取得
        svg_url = result.get("resultUrl")
        if not svg_url:
            return jsonify({"error": "No resultUrl returned"}), 500

        svg_resp = requests.get(svg_url)
        svg_resp.raise_for_status()
        return svg_resp.text, 200, {"Content-Type": "image/svg+xml"}

    except Exception as e:
        print("DXF → SVG conversion error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        os.unlink(temp_dxf.name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
