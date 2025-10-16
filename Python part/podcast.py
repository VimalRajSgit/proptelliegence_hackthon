import requests
import random
from datetime import datetime, timedelta

# --- API Keys and Endpoints ---
WEATHER_API_KEY = "f4ed27622e29484a8c342846251210"
GROQ_API_KEY = ""
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

# --- WEATHER FETCHERS ---

def get_detailed_weather(city):
    """Fetch detailed weather + air quality data for a city"""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city},India&aqi=yes"
    response = requests.get(url)
    data = response.json()

    weather = {
        'city': data['location']['name'],
        'region': data['location']['region'],
        'country': data['location']['country'],
        'local_time': data['location']['localtime'],
        'temp_c': data['current']['temp_c'],
        'feels_like_c': data['current']['feelslike_c'],
        'condition': data['current']['condition']['text'],
        'wind_kph': data['current']['wind_kph'],
        'humidity': data['current']['humidity'],
        'uv': data['current']['uv'],
        'aqi_us': data['current']['air_quality']['us-epa-index'],
        'pm2_5': data['current']['air_quality']['pm2_5'],
        'pm10': data['current']['air_quality']['pm10']
    }
    return weather


def get_monthly_weather_data(city):
    """Fetch weather data for the past 30 days"""
    weather_records = []

    for days_ago in [7, 14, 21, 30]:
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city},India&dt={past_date}"

        try:
            response = requests.get(url)
            data = response.json()

            day_data = data['forecast']['forecastday'][0]['day']
            weather_records.append({
                'date': past_date,
                'avg_temp_c': day_data['avgtemp_c'],
                'max_temp_c': day_data['maxtemp_c'],
                'min_temp_c': day_data['mintemp_c'],
                'avg_humidity': day_data['avghumidity'],
                'condition': day_data['condition']['text'],
                'max_wind_kph': day_data['maxwind_kph'],
                'total_precip_mm': day_data['totalprecip_mm']
            })
        except Exception as e:
            print(f"⚠️ Failed to fetch data for {past_date}: {e}")
            continue

    return weather_records


# --- LLAMA SCRIPT GENERATOR ---

def generate_weather_script_with_llama(city):
    """Generate a dynamic, varied podcast script using LLaMA via Groq"""
    current = get_detailed_weather(city)
    history = get_monthly_weather_data(city)

    # Create historical insights
    avg_temps = [d['avg_temp_c'] for d in history]
    if avg_temps:
        avg_temp = sum(avg_temps) / len(avg_temps)
        max_temp = max([d['max_temp_c'] for d in history])
        min_temp = min([d['min_temp_c'] for d in history])
        temp_trend = "rising" if current['temp_c'] > avg_temp else "falling"
    else:
        avg_temp, max_temp, min_temp, temp_trend = current['temp_c'], current['temp_c'], current['temp_c'], "stable"

    # Map AQI to interpretation
    aqi_map = {
        1: "Good", 2: "Moderate", 3: "Unhealthy for sensitive groups",
        4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"
    }
    aqi_label = aqi_map.get(current['aqi_us'], "Unknown")

    # Recent weather events
    recent_conditions = [d['condition'] for d in history]
    had_rain = any('rain' in c.lower() for c in recent_conditions)
    
    # Construct data summary for LLaMA
    data_summary = f"""
Weather Data for {city}:
- Current Time: {current['local_time']}
- Temperature: {current['temp_c']}°C (feels like {current['feels_like_c']}°C)
- Condition: {current['condition']}
- Humidity: {current['humidity']}%
- Wind Speed: {current['wind_kph']} km/h
- UV Index: {current['uv']}
- Air Quality: {aqi_label} (AQI Level {current['aqi_us']})
- PM2.5: {current['pm2_5']:.1f} µg/m³
- PM10: {current['pm10']:.1f} µg/m³

Historical Trends (Past Month):
- Average Temperature: {avg_temp:.1f}°C
- Temperature Range: {min_temp:.1f}°C to {max_temp:.1f}°C
- Current Trend: {temp_trend}
- Recent Rainfall: {"Yes" if had_rain else "No significant rain"}
"""

    # Prompt LLaMA to generate varied script
    prompt = f"""You are a friendly, engaging climate podcast host for GaiaNet Climate Update. 
Create a natural, conversational weather report script using the data below. 
The day you are generating script is on friday
IMPORTANT: Make each script unique by:
- Varying your opening greeting (e.g., "Hello everyone", "Good day listeners", "Welcome back")
- Using different transitions and phrases
- Adding varied climate tips or observations
- Changing the order of information presentation
- Using different adjectives and descriptive words
- Adding personality and warmth

Keep it concise (150-200 words), informative, and engaging. Speak naturally like a real podcast host would.

{data_summary}

Generate the podcast script now:"""

    # Call Groq LLaMA API
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",  # You can also use llama-3.1-70b-versatile or llama3-70b-8192
        "messages": [
            {
                "role": "system",
                "content": "You are a professional weather podcast host. Create engaging, natural-sounding weather reports. Never repeat the same phrases or structure. Be conversational and warm."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.9,  # Higher temperature for more variety
        "max_tokens": 400,
        "top_p": 0.95
    }

    response = requests.post(GROQ_CHAT_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print("⚠️ LLaMA Error:", response.text)
        raise RuntimeError("Groq LLaMA request failed")

    script = response.json()['choices'][0]['message']['content'].strip()
    return script


# --- GROQ PLAYAI-TTS ---

def generate_tts(script_text, city):
    """Convert text to speech using Groq's playai-tts model"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    voices = [
        "Briggs-PlayAI"
    ]
    voice = random.choice(voices)

    payload = {
        "model": "playai-tts",
        "voice": voice,
        "input": script_text
    }

    response = requests.post(GROQ_TTS_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("⚠️ TTS Error:", response.text)
        raise RuntimeError("Groq TTS request failed")

    filename = f"podcast_{city}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"✅ Podcast generated using voice '{voice}': {filename}")
    return filename


# --- MAIN PODCAST GENERATOR ---

def generate_climate_podcast(city):
    print(f"🎙️ Generating climate podcast for {city}...")
    print(f"🤖 Using LLaMA to create unique script...")
    
    script = generate_weather_script_with_llama(city)
    
    print("\n" + "="*60)
    print("🗣️ GENERATED SCRIPT:")
    print("="*60)
    print(script)
    print("="*60 + "\n")
    
    print(f"🎵 Converting to audio...")
    return generate_tts(script, city)


# --- RUN ---
if __name__ == "__main__":
    city_choice = random.choice(["Chennai", "Bengaluru", "Delhi", "Mumbai", "Kolkata"])
    generate_climate_podcast(city_choice)
