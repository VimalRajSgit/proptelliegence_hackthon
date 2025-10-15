from flask import Flask, jsonify
from tsunami_detector import (
    fetch_recent_earthquakes,
    calculate_indian_tsunami_risk,
)

app = Flask(__name__)

@app.route("/")
def home():
    return "🌊 Tsunami Detection Backend Running!"


@app.route("/api/tsunami", methods=["GET"])
def tsunami_data():
    earthquakes = fetch_recent_earthquakes(hours=24)
    if not earthquakes:
        # fallback demo data
        earthquakes = [{
            "properties": {"place": "Andaman Sea", "mag": 7.2, "time": "Demo"},
            "geometry": {"coordinates": [92.5, 10.1, 30]}
        }]
    results = [calculate_indian_tsunami_risk(e) for e in earthquakes]
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
