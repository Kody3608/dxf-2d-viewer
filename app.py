from flask import Flask, render_template, request, jsonify
import ezdxf
import tempfile
import os

from ezdxf.entities.hatch import PolylinePath, EdgePath

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        entities = []

        for e in msp:
            etype = e.dxftype()

            # LINE
            if etype == "LINE":
                entities.append({
                    "type": "LINE",
                    "start": [e.dxf.start.x, e.dxf.start.y],
                    "end": [e.dxf.end.x, e.dxf.end.y],
                })

            # CIRCLE
            elif etype == "CIRCLE":
                entities.append({
                    "type": "CIRCLE",
                    "center": [e.dxf.center.x, e.dxf.center.y],
                    "radius": e.dxf.radius,
                })

            # LWPOLYLINE
            elif etype == "LWPOLYLINE":
                points = [[p[0], p[1]] for p in e.get_points()]
                if len(points) >= 2:
                    entities.append({
                        "type": "POLYLINE",
                        "points": points,
                        "closed": e.closed,
                    })

            # TEXT
            elif etype == "TEXT":
                entities.append({
                    "type": "TEXT",
                    "text": e.dxf.text,
                    "position": [e.dxf.insert.x, e.dxf.insert.y],
                    "height": e.dxf.height,
                })

            # MTEXT（簡易）
            elif etype == "MTEXT":
                entities.append({
                    "type": "TEXT",
                    "text": e.text,
                    "position": [e.dxf.insert.x, e.dxf.insert.y],
                    "height": e.dxf.char_height if e.dxf.char_height else 10,
                })

            # HATCH（簡易：PolylinePathのみ）
            elif etype == "HATCH":
                for path in e.paths:
                    if isinstance(path, PolylinePath):
                        points = [[v[0], v[1]] for v in path.vertices]
                        if len(points) >= 2:
                            entities.append({
                                "type": "POLYLINE",
                                "points": points,
                                "closed": True,
                            })
                    elif isinstance(path, EdgePath):
                        # EdgePath は今回は簡易対応のため無視
                        continue

        return jsonify({
            "entities": entities
        })

    except Exception as ex:
        return jsonify({
            "error": str(ex)
        }), 500

    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    app.run(debug=True)
