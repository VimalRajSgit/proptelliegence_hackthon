# 🌐 Weather Services Integration Guide

This guide explains how to connect and use all your Python services with the React Native app.

## 📁 Project Structure

```
MyApp/
├── App.js                          # React Native app with 4 tabs
├── Python part/
│   ├── unified_backend.py          # 🆕 Main Flask backend (ALL SERVICES)
│   ├── start_backend.py            # 🆕 Easy startup script
│   ├── blog_gen2.py               # Weather blog generator
│   ├── podcast.py                 # Climate podcast generator  
│   ├── tsunami_detector.py        # Earthquake/tsunami detection
│   ├── app1.py                    # Tsunami Flask app
│   └── requirements.txt           # Updated dependencies
└── INTEGRATION_GUIDE.md           # This file
```

## 🚀 Quick Start

### 1. Start the Backend (Python)

```bash
cd "Python part"
python start_backend.py
```

This will:
- Install all required packages
- Start the unified Flask server on `http://172.17.132.1:5000`

### 2. Start the React Native App

```bash
# In the main MyApp directory
npm start
# or
expo start
```

## 📱 App Features

Your React Native app now has **4 tabs**:

### 📝 Blog Tab
- **Endpoint**: `/api/weather_blog`
- **Features**: 
  - AI-generated weather blogs using CrewAI
  - Generated images via Pollinations API
  - PDF creation with ReportLab
  - City selection (Chennai, Delhi, Mumbai, etc.)

### 🌡️ Weather Tab  
- **Endpoint**: `/api/weather`
- **Features**:
  - Current weather conditions
  - Air quality data (AQI, PM2.5, PM10)
  - Historical weather data (past 30 days)
  - Detailed weather cards

### 🌊 Tsunami Tab
- **Endpoint**: `/api/tsunami`
- **Features**:
  - Real-time earthquake monitoring
  - Tsunami risk assessment for Indian Ocean
  - Risk level indicators (Low/Moderate/High)
  - Last 24 hours monitoring (configurable)

### 🎙️ Podcast Tab
- **Endpoint**: `/api/podcast`
- **Features**:
  - AI-generated podcast scripts using LLaMA
  - Weather context for podcast content
  - Audio generation capability (separate endpoint)
  - Natural, conversational weather reports

## 🔗 API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Service status | None |
| `/api/weather_blog` | GET | Generate weather blog | `city` (optional) |
| `/api/weather` | GET | Get weather data | `city` (optional) |
| `/api/tsunami` | GET | Tsunami detection | `hours` (optional, default: 24) |
| `/api/podcast` | GET | Generate podcast script | `city` (optional) |
| `/api/podcast/audio` | GET | Generate podcast with audio | `city` (optional) |
| `/api/cities` | GET | List available cities | None |
| `/static/<filename>` | GET | Serve generated files | filename |

## 🎯 Available Cities

- Chennai
- Delhi  
- Bengaluru
- Mumbai
- Kolkata
- Hyderabad

## 🔧 Configuration

### Backend Configuration
- **Host**: `0.0.0.0` (accessible from network)
- **Port**: `5000`
- **CORS**: Enabled for React Native
- **Debug**: Enabled

### API Keys Required
Make sure these are set in your Python files:
- **WeatherAPI**: `WEATHER_API_KEY`
- **Groq**: `GROQ_API_KEY` (for AI features)

## 📱 React Native Features

- **Tab Navigation**: Easy switching between services
- **Pull-to-Refresh**: Refresh data in each tab
- **Loading States**: Proper loading indicators
- **Error Handling**: User-friendly error messages
- **Modern UI**: Clean, card-based design
- **Responsive**: Works on different screen sizes

## 🛠️ Development

### Running Individual Services

If you want to run services separately:

```bash
# Weather Blog only
python blog_gen2.py

# Tsunami Detection only  
python app1.py

# Podcast Generator only
python podcast.py
```

### Adding New Cities

Edit the `CITIES` list in:
- `unified_backend.py`
- `blog_gen2.py` 
- `podcast.py`

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure the Python backend is running
   - Check if port 5000 is available
   - Verify IP address `172.17.132.1`

2. **API Key Errors**
   - Ensure WeatherAPI and Groq keys are valid
   - Check rate limits

3. **Image/PDF Generation Fails**
   - Check internet connection for Pollinations API
   - Verify ReportLab installation

4. **React Native Network Error**
   - Ensure both devices are on same network
   - Check firewall settings
   - Try using `localhost` instead of IP

### Debug Mode

The backend runs in debug mode, so you'll see detailed logs in the terminal.

## 📊 Performance Notes

- **Blog Generation**: Takes 30-60 seconds (AI processing)
- **Podcast Generation**: Takes 10-30 seconds
- **Weather Data**: Near-instant
- **Tsunami Detection**: 2-5 seconds

## 🔄 Updates

To add new features:

1. Add new endpoints to `unified_backend.py`
2. Create corresponding tab in `App.js`
3. Update the tab navigation
4. Test thoroughly

## 🎉 Success!

You now have a fully integrated weather services app that combines:
- ✅ AI-powered weather blogging
- ✅ Real-time weather monitoring  
- ✅ Tsunami risk assessment
- ✅ AI-generated climate podcasts
- ✅ Beautiful React Native interface

Enjoy your multi-service weather app! 🌤️

