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
    """
    DXF ファイルを受け取り、Vector Express API で SVG に変換して返す
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 一時ファイルに保存
    temp_dxf = tempfile.NamedTemporaryFile(delete=False, suffix=".dxf")
    file.save(temp_dxf.name)

    try:
        # -------------------------------
        # ステップ1：変換パスを取得しフルURLにする
        # -------------------------------
        paths_resp = requests.get(f"{VECTOR_EXPRESS_BASE}/convert/dxf/auto/svg/")
        paths_resp.raise_for_status()
        alternatives = paths_resp.json().get("alternatives")
        if not alternatives:
            return jsonify({"error": "No conversion alternatives found"}), 500

        program_path = alternatives[0]["path"]  # "/api/v2/public/convert/dxf/cad2svg/svg"
        convert_url = f"https://vector.express{program_path}"  # フル URL

        # -------------------------------
        # ステップ2：DXF を POST（Content-Type 指定）
        # -------------------------------
        with open(temp_dxf.name, "rb") as f:
            convert_resp = requests.post(
                convert_url,
                data=f.read(),
                headers={"Content-Type": "application/octet-stream"}
            )
        convert_resp.raise_for_status()
        result = convert_resp.json()

        # -------------------------------
        # ステップ3：resultUrl が返っていない場合の処理
        # -------------------------------
        svg_url = result.get("resultUrl")
        if not svg_url:
            return jsonify({"error": "No resultUrl returned. You may have hit API limits or file too large."}), 500

        svg_resp = requests.get(svg_url)
        svg_resp.raise_for_status()

        # SVG を返す
        return svg_resp.text, 200, {"Content-Type": "image/svg+xml"}

    except Exception as e:
        print("DXF → SVG conversion error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        os.unlink(temp_dxf.name)

# Render では PORT を環境変数で受け取る
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
