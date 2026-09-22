import os

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/dispatch")
def dispatch():
    routes = request.args.getlist("route")
    if not routes:
        return jsonify(error="missing route stamp"), 400

    gate_stamp = routes[0]
    sorter_stamp = routes[-1]

    if gate_stamp != "visitor":
        return jsonify(status="rejected", gate=gate_stamp, note="gate only accepts visitor stamp"), 403

    if sorter_stamp == "visitor":
        return jsonify(status="ok", gate=gate_stamp, sorter=sorter_stamp, platform="public lounge")
    if sorter_stamp == "conductor":
        return jsonify(
            status="ok",
            gate=gate_stamp,
            sorter=sorter_stamp,
            platform="sealed dispatch office",
            flag=os.environ.get("FLAG", "COMPFEST18{placeholder_flag}"),
        )
    return jsonify(status="lost", gate=gate_stamp, sorter=sorter_stamp), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
