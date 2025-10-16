from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import random

# Import your existing modules
from tsunami_detector import fetch_recent_earthquakes, calculate_indian_tsunami_risk
from blog_gen2 import (
    get_detailed_weather, get_monthly_weather_data, 
    create_weather_crew, run_crew_with_retry,
    generate_image, create_pdf_blog
)
from podcast import generate_climate_podcast, generate_weather_script_with_llama, generate_tts

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native

# Configuration
CITIES = ["Chennai", "Delhi", "Bengaluru", "Mumbai", "Kolkata", "Hyderabad"]
BASE_URL = "http://172.17.132.1:5000"

@app.route("/")
def home():
    return jsonify({
        "message": "🌐 Unified Backend Running!",
        "services": [
            "Weather Blog Generator",
            "Tsunami Detection", 
            "Climate Podcast",
            "Weather Data"
        ],
        "endpoints": {
            "weather_blog": "/api/weather_blog",
            "tsunami": "/api/tsunami",
            "podcast": "/api/podcast",
            "weather": "/api/weather"
        }
    })

# ==================== WEATHER BLOG ENDPOINT ====================
@app.route("/api/weather_blog", methods=["GET"])
def weather_blog():
    try:
        # Get city from query params or random
        city = request.args.get('city', random.choice(CITIES))
        
        print(f"🌤️ Generating weather blog for {city}...")
        
        # Get weather data
        current = get_detailed_weather(city)
        monthly_data = get_monthly_weather_data(city)
        
        # Create CrewAI crew
        crew = create_weather_crew(city, current, monthly_data)
        blog_result = run_crew_with_retry(crew, max_retries=2, delay=3)
        
        if not blog_result:
            blog_result = f"Weather Update for {city}: {current['condition']}, {current['temp_c']}°C"
        
        # Generate image
        prompt = f"{current['condition']} weather in {city}, India, realistic photo"
        image_path = generate_image(prompt)
        
        # Create PDF
        pdf_filename = create_pdf_blog(str(blog_result), image_path, city, current, monthly_data)
        
        return jsonify({
            "city": city,
            "blog": str(blog_result),
            "image_url": f"/static/{os.path.basename(image_path)}",
            "pdf_url": f"/static/{pdf_filename}",
            "weather": current,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Weather blog error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== TSUNAMI DETECTION ENDPOINT ====================
@app.route("/api/tsunami", methods=["GET"])
def tsunami_data():
    try:
        hours = int(request.args.get('hours', 24))
        print(f"🌊 Fetching tsunami data for last {hours} hours...")
        
        earthquakes = fetch_recent_earthquakes(hours=hours)
        if not earthquakes:
            # Fallback demo data
            earthquakes = [{
                "properties": {
                    "place": "Andaman Sea", 
                    "mag": 7.2, 
                    "time": int(datetime.now().timestamp() * 1000)
                },
                "geometry": {"coordinates": [92.5, 10.1, 30]}
            }]
        
        results = []
        for eq in earthquakes[:5]:  # Limit to 5 most recent
            analysis = calculate_indian_tsunami_risk(eq)
            results.append(analysis)
        
        return jsonify({
            "earthquakes": results,
            "total_found": len(earthquakes),
            "hours_checked": hours,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Tsunami detection error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== PODCAST ENDPOINT ====================
@app.route("/api/podcast", methods=["GET"])
def podcast_generator():
    try:
        city = request.args.get('city', random.choice(CITIES))
        print(f"🎙️ Generating podcast for {city}...")
        
        # Generate script only (no audio file for now)
        script = generate_weather_script_with_llama(city)
        
        # Get current weather for context
        current = get_detailed_weather(city)
        
        return jsonify({
            "city": city,
            "script": script,
            "weather": current,
            "timestamp": datetime.now().isoformat(),
            "note": "Audio generation available via /api/podcast/audio endpoint"
        })
        
    except Exception as e:
        print(f"❌ Podcast generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/podcast/audio", methods=["GET"])
def podcast_with_audio():
    try:
        city = request.args.get('city', random.choice(CITIES))
        print(f"🎵 Generating podcast with audio for {city}...")
        
        # Generate full podcast with audio
        audio_filename = generate_climate_podcast(city)
        
        return jsonify({
            "city": city,
            "audio_url": f"/static/{audio_filename}",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Audio podcast error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== WEATHER DATA ENDPOINT ====================
@app.route("/api/weather", methods=["GET"])
def weather_data():
    try:
        city = request.args.get('city', random.choice(CITIES))
        print(f"🌡️ Fetching weather data for {city}...")
        
        current = get_detailed_weather(city)
        monthly_data = get_monthly_weather_data(city)
        
        return jsonify({
            "city": city,
            "current": current,
            "monthly_history": monthly_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Weather data error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== STATIC FILES ====================
@app.route("/static/<filename>")
def static_files(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== CITIES LIST ====================
@app.route("/api/cities", methods=["GET"])
def get_cities():
    return jsonify({
        "cities": CITIES,
        "count": len(CITIES)
    })

if __name__ == "__main__":
    print("🚀 Starting Unified Backend...")
    print("📱 Available endpoints:")
    print("   • Weather Blog: http://172.17.132.1:5000/api/weather_blog")
    print("   • Tsunami Detection: http://172.17.132.1:5000/api/tsunami")
    print("   • Podcast: http://172.17.132.1:5000/api/podcast")
    print("   • Weather Data: http://172.17.132.1:5000/api/weather")
    print("   • Cities List: http://172.17.132.1:5000/api/cities")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=True)