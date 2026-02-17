from flask import Flask, render_template, request, jsonify
import ezdxf
import tempfile
import os
import math

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        file.save(tmp.name)
        path = tmp.name

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    data = {
        "lines": [],
        "circles": [],
        "arcs": [],
        "texts": [],
        "hatches": [],
        "bbox": {
            "minx": math.inf,
            "miny": math.inf,
            "maxx": -math.inf,
            "maxy": -math.inf
        }
    }

    def update_bbox(x, y):
        data["bbox"]["minx"] = min(data["bbox"]["minx"], x)
        data["bbox"]["miny"] = min(data["bbox"]["miny"], y)
        data["bbox"]["maxx"] = max(data["bbox"]["maxx"], x)
        data["bbox"]["maxy"] = max(data["bbox"]["maxy"], y)

    for e in msp:
        t = e.dxftype()

        if t == "LINE":
            x1, y1 = e.dxf.start.x, -e.dxf.start.y
            x2, y2 = e.dxf.end.x, -e.dxf.end.y
            data["lines"].append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
            update_bbox(x1, y1)
            update_bbox(x2, y2)

        elif t == "LWPOLYLINE":
            pts = []
            for p in e.get_points():
                x, y = p[0], -p[1]
                pts.append([x, y])
                update_bbox(x, y)
            data["lines"].append({"poly": pts})

        elif t == "CIRCLE":
            cx, cy, r = e.dxf.center.x, -e.dxf.center.y, e.dxf.radius
            data["circles"].append({"cx": cx, "cy": cy, "r": r})
            update_bbox(cx - r, cy - r)
            update_bbox(cx + r, cy + r)

        elif t == "ARC":
            cx, cy, r = e.dxf.center.x, -e.dxf.center.y, e.dxf.radius
            data["arcs"].append({
                "cx": cx,
                "cy": cy,
                "r": r,
                "start": e.dxf.start_angle,
                "end": e.dxf.end_angle
            })
            update_bbox(cx - r, cy - r)
            update_bbox(cx + r, cy + r)

        elif t in ("TEXT", "MTEXT"):
            try:
                text = e.plain_text()
            except Exception:
                text = "<?>"
            x, y = e.dxf.insert.x, -e.dxf.insert.y
            data["texts"].append({"x": x, "y": y, "text": text})
            update_bbox(x, y)

        elif t == "HATCH":
            for path in e.paths:
                if path.PATH_TYPE == "PolylinePath":
                    pts = []
                    for v in path.vertices:
                        x, y = v[0], -v[1]
                        pts.append([x, y])
                        update_bbox(x, y)
                    if len(pts) >= 3:
                        data["hatches"].append({"boundary": pts})

    os.remove(path)
    return jsonify(data)

if __name__ == "__main__":
    app.run()
