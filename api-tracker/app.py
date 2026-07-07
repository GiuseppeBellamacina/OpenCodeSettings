import argparse
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

from providers import check_all, check_github_copilot

# Load .env from parent directory
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)
app.config["COPILOT_ONLY"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check")
def api_check():
    if app.config["COPILOT_ONLY"]:
        results = [check_github_copilot()]
    else:
        results = check_all()
    return jsonify(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--copilot", action="store_true", help="Controlla solo GitHub Copilot"
    )
    args = parser.parse_args()
    app.config["COPILOT_ONLY"] = args.copilot
    app.run(debug=True, port=5050)
