import os
from flask import Flask, jsonify

app = Flask(__name__)

APP_MESSAGE = os.environ.get("APP_MESSAGE", "Hello from the Incident Lab app!")

# Required at startup as of v2 - no default, will raise KeyError if missing
REQUIRED_CONFIG = os.environ["REQUIRED_CONFIG"]


@app.route("/")
def index():
    return jsonify(message=APP_MESSAGE, status="ok")


@app.route("/health")
def health():
    return jsonify(status="healthy"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
