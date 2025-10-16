from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import random

# Import your existing modules
<<<<<<< HEAD
# Add the Python_part directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
python_part_dir = os.path.join(parent_dir, "Python_part")
sys.path.append(python_part_dir)

=======
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
from tsunami_detector import fetch_recent_earthquakes, calculate_indian_tsunami_risk
from blog_gen2 import (
    get_detailed_weather, get_monthly_weather_data, 
    create_weather_crew, run_crew_with_retry,
    generate_image, create_pdf_blog
)
from podcast import generate_climate_podcast, generate_weather_script_with_llama, generate_tts

<<<<<<< HEAD
# Import Twitter functionality
import tweepy
import requests

=======
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
app = Flask(__name__)
CORS(app)  # Enable CORS for React Native

# Configuration
CITIES = ["Chennai", "Delhi", "Bengaluru", "Mumbai", "Kolkata", "Hyderabad"]
BASE_URL = "http://172.17.132.1:5000"

<<<<<<< HEAD
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# API Configuration from environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "f4ed27622e29484a8c342846251210")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Twitter API Configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "cMJIivsDEpvv8sbvvm5jSUAIZ")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET", "N3brDG386I7xyYJSLptwmm4bYBFJcZcNEvZJ5XHXmkOC6iyllq")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "1845850146107703297-8YkAu3JZmw9JrzH0gBGSTo7sOnXikQ")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "FBeUdPC5NDBZIDPaZcNDM7GZI8Dh83gXE8OKQfgINUhwx")

# ==================== TWITTER FUNCTIONS ====================
def generate_story_tweet_with_groq(weather_data):
    """Generate a descriptive, story-like weather tweet using Groq API"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Write a descriptive, story-like weather update for {weather_data['city']}, India.

    Your task is to create a single, evocative paragraph of about 6 to 7 lines (max 280 characters for Twitter). Don't just list the facts; weave them into a narrative that paints a picture of the city's atmosphere.

    - Start by setting the scene based on the weather condition: '{weather_data['condition']}'.
    - Naturally mention the temperature ({weather_data['temp_c']}°C) and the "feels like" temperature ({weather_data['feels_like_c']}°C) as part of the story.
    - Subtly comment on the air quality (AQI is {weather_data['aqi_us']}) and what it means for being outdoors.
    - The tone should be personal and immersive, as if a local is describing their experience.
    - Conclude the paragraph with 3-4 fitting hashtags.

    CURRENT WEATHER DATA:
    - City: {weather_data['city']}
    - Temperature: {weather_data['temp_c']}°C
    - Feels Like: {weather_data['feels_like_c']}°C
    - Condition: {weather_data['condition']}
    - Air Quality Index (US EPA): {weather_data['aqi_us']}
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 300
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # Handle different response structures
    if 'choices' in result and len(result['choices']) > 0:
        return result['choices'][0]['message']['content']
    elif 'error' in result:
        print(f"❌ Groq API error: {result['error']}")
        return f"Weather update for {weather_data['city']}: {weather_data['condition']}, {weather_data['temp_c']}°C. Air quality: {weather_data['aqi_us']} #Weather #{weather_data['city']} #Climate"
    else:
        print(f"❌ Unexpected Groq API response: {result}")
        return f"Weather update for {weather_data['city']}: {weather_data['condition']}, {weather_data['temp_c']}°C. Air quality: {weather_data['aqi_us']} #Weather #{weather_data['city']} #Climate"

def generate_weather_image(city, condition):
    """Generate an AI image for weather tweet"""
    prompt = f"{condition} weather in {city}, India, realistic photo"
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    filename = f"weather_image_{city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def authenticate_twitter():
    """Authenticate with Twitter API"""
    try:
        # Create Twitter client
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_KEY_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

        # For media upload, you also need an API v1.1 compatible object
        auth_v1 = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_KEY_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        api_v1 = tweepy.API(auth_v1)
        
        return client, api_v1
    except Exception as e:
        print(f"❌ Twitter authentication error: {e}")
        return None, None

=======
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
@app.route("/")
def home():
    return jsonify({
        "message": "🌐 Unified Backend Running!",
        "services": [
            "Weather Blog Generator",
            "Tsunami Detection", 
            "Climate Podcast",
<<<<<<< HEAD
            "Weather Data",
            "Twitter Weather Posts"
=======
            "Weather Data"
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
        ],
        "endpoints": {
            "weather_blog": "/api/weather_blog",
            "tsunami": "/api/tsunami",
            "podcast": "/api/podcast",
<<<<<<< HEAD
            "weather": "/api/weather",
            "twitter": "/api/twitter"
=======
            "weather": "/api/weather"
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
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

<<<<<<< HEAD
# ==================== TWITTER ENDPOINT ====================
@app.route("/api/twitter", methods=["GET"])
def twitter_weather_post():
    try:
        # Get city from query params or random
        city = request.args.get('city', random.choice(CITIES))
        print(f"🐦 Generating Twitter weather post for {city}...")
        
        # Get weather data
        current = get_detailed_weather(city)
        
        # Generate story-like tweet with error handling
        try:
            story_tweet_text = generate_story_tweet_with_groq(current)
        except Exception as e:
            print(f"❌ Error generating tweet with Groq: {e}")
            # Fallback to simple tweet
            story_tweet_text = f"Weather update for {city}: {current['condition']}, {current['temp_c']}°C. Air quality: {current['aqi_us']} #Weather #{city} #Climate"
        
        # Generate weather image
        try:
            image_path = generate_weather_image(city, current['condition'])
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            image_path = None
        
        # Authenticate with Twitter
        client, api_v1 = authenticate_twitter()
        if not client or not api_v1:
            return jsonify({
                "city": city,
                "tweet_text": story_tweet_text,
                "image_path": image_path,
                "weather": current,
                "timestamp": datetime.now().isoformat(),
                "status": "generated_but_not_posted",
                "error": "Twitter authentication failed"
            })
        
        # Post to Twitter
        try:
            media_id = None
            if image_path:
                # Upload image to Twitter
                media = api_v1.media_upload(image_path)
                media_id = media.media_id
                print(f"🖼 Image uploaded to Twitter. Media ID: {media_id}")

            # Ensure tweet is within character limit
            if len(story_tweet_text) > 280:
                print("⚠️ Warning: Tweet text exceeds 280 characters. Truncating for Twitter.")
                story_tweet_text = story_tweet_text[:277] + "..."

            # Post the tweet with or without image
            if media_id:
                response = client.create_tweet(text=story_tweet_text, media_ids=[media_id])
            else:
                response = client.create_tweet(text=story_tweet_text)
            
            # Get tweet URL
            username = client.get_me().data['username']
            tweet_url = f"https://twitter.com/{username}/status/{response.data['id']}"
            
            return jsonify({
                "city": city,
                "tweet_text": story_tweet_text,
                "tweet_id": response.data['id'],
                "tweet_url": tweet_url,
                "image_path": image_path,
                "weather": current,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            
        except Exception as e:
            print(f"❌ Error posting to Twitter: {e}")
            return jsonify({
                "city": city,
                "tweet_text": story_tweet_text,
                "image_path": image_path,
                "weather": current,
                "timestamp": datetime.now().isoformat(),
                "status": "generated_but_not_posted",
                "error": str(e)
            })
        
    except Exception as e:
        print(f"❌ Twitter weather post error: {e}")
        return jsonify({"error": str(e)}), 500

=======
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
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
<<<<<<< HEAD
    print("   • Twitter Weather: http://172.17.132.1:5000/api/twitter")
=======
>>>>>>> 9289b80dd1379fcee5515fdd737f5ef9b0dd1ac5
    print("   • Cities List: http://172.17.132.1:5000/api/cities")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
