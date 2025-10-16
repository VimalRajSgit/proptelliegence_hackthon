import requests
from datetime import datetime, timedelta

# --------------- FETCH RECENT EARTHQUAKES -----------------
def fetch_recent_earthquakes(hours=1):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time.isoformat()}&endtime={end_time.isoformat()}&minmagnitude=5"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("features", [])


# --------------- RISK CALCULATION -----------------
def calculate_indian_tsunami_risk(event):
    mag = event["properties"]["mag"]
    coords = event["geometry"]["coordinates"]
    lon, lat, depth = coords[0], coords[1], coords[2]

    # Simplified rule-based logic
    risk_level = "Low"
    if mag >= 7.5 and depth < 70 and (40 < lon < 110) and (-10 < lat < 30):
        risk_level = "High"
    elif mag >= 6.5 and depth < 150:
        risk_level = "Moderate"

    return {
        "place": event["properties"]["place"],
        "magnitude": mag,
        "depth_km": depth,
        "coordinates": {"lat": lat, "lon": lon},
        "risk": risk_level,
        "time": event["properties"]["time"],
    }


# --------------- ALERT MESSAGE -----------------
def generate_indian_alert(analysis):
    return (
        f"🌊 Tsunami Alert for {analysis['place']}!\n"
        f"Magnitude: {analysis['magnitude']}\n"
        f"Depth: {analysis['depth_km']} km\n"
        f"Risk Level: {analysis['risk']}\n"
        f"Time: {analysis['time']}"
    )


# --------------- TEST MODE (optional) -----------------
if __name__ == "__main__":
    # Only runs if you run `python tsunami_detector.py` directly
    print("Running demo mode...\n")
    earthquakes = fetch_recent_earthquakes(hours=1)
    for e in earthquakes[:3]:
        analysis = calculate_indian_tsunami_risk(e)
        print(generate_indian_alert(analysis))
        print()
