import requests
import random
from datetime import datetime, timedelta
import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- API Keys from environment variables ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "f4ed27622e29484a8c342846251210")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# --- Twitter API Keys from environment variables ---
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "cMJIivsDEpvv8sbvvm5jSUAIZ")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET", "N3brDG386I7xyYJSLptwmm4bYBFJcZcNEvZJ5XHXmkOC6iyllq")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "1845850146107703297-8YkAu3JZmw9JrzH0gBGSTo7sOnXikQ")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "FBeUdPC5NDBZIDPaZcNDM7GZI8Dh83gXE8OKQfgINUhwx")


CITIES = ["Chennai", "Delhi", "Bengaluru", "Mumbai", "Kolkata", "Hyderabad"]

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
        "max_tokens": 300 # Keep this relatively high to allow for a good story, Tweepy will truncate if too long
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    return result['choices'][0]['message']['content']

def generate_image(prompt):
    """Generate an AI image from Pollinations API and return the filename"""
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    filename = "weather_image.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def main():
    # --- Twitter API Authentication ---
    # Create an OAuthHandler instance
    try:
        # Authenticate to Twitter using OAuth 1.0a (User Context)
        # This is the authentication handler that uses your keys and tokens
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
        
        print("✅ Twitter authentication successful!")

    except tweepy.errors.TweepyException as e:
        print(f"❌ Error during Twitter authentication: {e}")
        print("Please check your Twitter API keys and tokens.")
        return # Exit if authentication fails
    except Exception as e:
        print(f"❌ An unexpected error occurred during Twitter authentication: {e}")
        return


    # --- Weather Data & Story Generation ---
    city = random.choice(CITIES)
    print(f"\n📍 Selected City: {city}")
    
    print("🔄 Fetching current weather data...")
    current = get_detailed_weather(city)
    
    print(f"\n📊 Weather Data for {city}:")
    print(f"🌡 Temp: {current['temp_c']}°C (Feels like {current['feels_like_c']}°C)")
    print(f"💨 Wind: {current['wind_kph']} km/h")
    print(f"💧 Humidity: {current['humidity']}%")
    print(f"☀ UV Index: {current['uv']}")
    print(f"🏭 AQI (US EPA): {current['aqi_us']} | PM2.5: {current['pm2_5']} | PM10: {current['pm10']}")
    
    print("\n✍ Generating story-like tweet with Groq AI...")
    story_tweet_text = generate_story_tweet_with_groq(current)
    
    print("\n" + "="*70)
    print("📝 GENERATED WEATHER STORY TWEET")
    print("="*70)
    print(story_tweet_text)
    print("="*70)

    # --- Image Generation ---
    print(f"\n🎨 Generating AI image...")
    image_prompt = f"{current['condition']} weather in {city}, India, realistic photo"
    image_path = generate_image(image_prompt)
    print(f"🖼 Image saved as: {image_path}")
    
    # Display image in Colab (optional, for local viewing)
    try:
        from IPython.display import Image, display
        print("\n📷 Displaying image:")
        display(Image(filename=image_path))
    except ImportError:
        print("(Image display requires IPython environment)")


    # --- Post to Twitter ---
    print("\n🚀 Attempting to post to Twitter with image...")
    try:
        # 1. Upload the image to Twitter
        # The API v1.1 is typically used for media uploads
        media = api_v1.media_upload(image_path)
        media_id = media.media_id
        print(f"🖼 Image uploaded to Twitter. Media ID: {media_id}")

        # Ensure the tweet text is within Twitter's 280 character limit
        if len(story_tweet_text) > 280:
            print("⚠️ Warning: Tweet text exceeds 280 characters. Truncating for Twitter.")
            # Find a natural break if possible, otherwise hard truncate
            story_tweet_text = story_tweet_text[:277] + "..." 

        # 2. Post the tweet with the uploaded media
        response = client.create_tweet(text=story_tweet_text, media_ids=[media_id])
        
        print(f"\n✅ Tweet posted successfully!")
        print(f"Tweet ID: {response.data['id']}")
        print(f"Tweet Text: {response.data['text']}")
        print(f"View it here: https://twitter.com/{client.get_me().data['username']}/status/{response.data['id']}") # Dynamically get username
        
        # Clean up the generated image file
        # os.remove(image_path) 
        # print(f"Deleted local image file: {image_path}")

    except tweepy.errors.TweepyException as e:
        print(f"❌ Error during Twitter posting: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred during Twitter posting: {e}")

# Run the system
if __name__ == "__main__":
    main()