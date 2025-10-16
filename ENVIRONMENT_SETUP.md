# Environment Setup Guide

This guide explains how to set up environment variables for the Weather Services Backend.

## 🔐 API Keys Required

The application requires several API keys to function properly:

### 1. Weather API
- **Service**: WeatherAPI.com
- **Purpose**: Fetch weather data for cities
- **Key**: `WEATHER_API_KEY`

### 2. Groq API
- **Service**: Groq AI
- **Purpose**: Generate AI content for blogs, tweets, and podcasts
- **Key**: `GROQ_API_KEY`

### 3. Twitter API
- **Service**: Twitter Developer Platform
- **Purpose**: Post weather tweets automatically
- **Keys**: 
  - `TWITTER_API_KEY`
  - `TWITTER_API_KEY_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`

## 📝 Setup Instructions

### Step 1: Create .env File
1. Copy the example file:
   ```bash
   cp env.example .env
   ```

2. Edit the `.env` file with your actual API keys:
   ```env
   # Weather API Configuration
   WEATHER_API_KEY=your_actual_weather_api_key_here
   
   # Groq API Configuration
   GROQ_API_KEY=your_actual_groq_api_key_here
   
   # Twitter API Configuration
   TWITTER_API_KEY=your_actual_twitter_api_key_here
   TWITTER_API_KEY_SECRET=your_actual_twitter_api_key_secret_here
   TWITTER_ACCESS_TOKEN=your_actual_twitter_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_actual_twitter_access_token_secret_here
   ```

### Step 2: Get API Keys

#### Weather API Key
1. Go to [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file

#### Groq API Key
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Create an API key
4. Add it to your `.env` file

#### Twitter API Keys
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Generate API keys and tokens
4. Add all four keys to your `.env` file

### Step 3: Install Dependencies
```bash
pip install python-dotenv
```

### Step 4: Test the Setup
```bash
python Python_part/start_backend.py
```

## 🔒 Security Notes

- **Never commit your `.env` file to version control**
- The `.env` file is already added to `.gitignore`
- Use the `env.example` file as a template
- Keep your API keys secure and don't share them

## 🚨 Troubleshooting

### Common Issues:

1. **ModuleNotFoundError: No module named 'dotenv'**
   ```bash
   pip install python-dotenv
   ```

2. **API Key Errors**
   - Check that your `.env` file exists
   - Verify API keys are correct
   - Ensure no extra spaces in the `.env` file

3. **Twitter Authentication Failed**
   - Verify all four Twitter API keys
   - Check that your Twitter app has the correct permissions

## 📁 File Structure

```
MyApp/
├── .env                    # Your actual API keys (DO NOT COMMIT)
├── env.example            # Template for API keys
├── .gitignore             # Includes .env for security
├── Python_part/
│   ├── unified_backend.py # Uses environment variables
│   ├── blog_gen2.py       # Uses environment variables
│   ├── podcast.py         # Uses environment variables
│   └── twitter.py         # Uses environment variables
└── ENVIRONMENT_SETUP.md   # This guide
```

## ✅ Verification

To verify your setup is working:

1. **Check Environment Loading**:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv("WEATHER_API_KEY"))
   ```

2. **Test API Connections**:
   - Weather: Visit `/api/weather` endpoint
   - Twitter: Visit `/api/twitter` endpoint
   - Blog: Visit `/api/weather_blog` endpoint

## 🆘 Support

If you encounter issues:

1. Check that all API keys are correctly set
2. Verify the `.env` file is in the project root
3. Ensure all dependencies are installed
4. Check API service status pages

---

**Remember**: Keep your API keys secure and never share them publicly!
