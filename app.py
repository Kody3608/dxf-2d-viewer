from flask import Flask, render_template, request, jsonify
import ezdxf

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    doc = ezdxf.readfile(file)
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

if __name__ == "__main__":
    # Renderでは gunicorn が起動するのでここはローカル用
    app.run(host="0.0.0.0", port=10000, debug=True)
