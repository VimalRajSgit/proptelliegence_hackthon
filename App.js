// App.js (React Native) - Multi-Service Weather App
import React, {useEffect, useState} from "react";
import { 
  View, 
  Text, 
  ScrollView, 
  ActivityIndicator, 
  Image, 
  Linking, 
  TouchableOpacity, 
  StyleSheet,
  Alert,
  RefreshControl
} from "react-native";

const BASE_URL = "http://172.17.132.1:5000";

export default function App() {
  const [activeTab, setActiveTab] = useState("blog");
  const [data, setData] = useState({});
  const [loading, setLoading] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  const tabs = [
    { id: "blog", title: "📝 Blog", icon: "📝" },
    { id: "weather", title: "🌡️ Weather", icon: "🌡️" },
    { id: "tsunami", title: "🌊 Tsunami", icon: "🌊" },
    { id: "podcast", title: "🎙️ Podcast", icon: "🎙️" },
    { id: "twitter", title: "🐦 Twitter", icon: "🐦" }
  ];

  const getEndpointForTab = (tabId) => {
    const endpointMap = {
      'blog': '/api/weather_blog',
      'weather': '/api/weather',
      'tsunami': '/api/tsunami',
      'podcast': '/api/podcast',
      'twitter': '/api/twitter'
    };
    return endpointMap[tabId] || '/api/weather_blog';
  };

  const fetchData = async (endpoint, tabId) => {
    setLoading(prev => ({ ...prev, [tabId]: true }));
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`);
      const json = await response.json();
      setData(prev => ({ ...prev, [tabId]: json }));
    } catch (err) {
      setData(prev => ({ ...prev, [tabId]: { error: err.message } }));
    } finally {
      setLoading(prev => ({ ...prev, [tabId]: false }));
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData(getEndpointForTab(activeTab), activeTab);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchData(getEndpointForTab(activeTab), activeTab);
  }, [activeTab]);

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      {tabs.map(tab => (
        <TouchableOpacity
          key={tab.id}
          style={[styles.tab, activeTab === tab.id && styles.activeTab]}
          onPress={() => setActiveTab(tab.id)}
        >
          <Text style={[styles.tabIcon, activeTab === tab.id && styles.activeTabText]}>
            {tab.icon}
          </Text>
          <Text style={[styles.tabText, activeTab === tab.id && styles.activeTabText]}>
            {tab.title.split(' ')[1]}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderBlogTab = () => {
    const blogData = data.blog;
    if (loading.blog) return <ActivityIndicator size="large" style={styles.center} />;
    if (blogData?.error) return <Text style={styles.error}>Error: {blogData.error}</Text>;

    return (
      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>🌦️ Weather Blog - {blogData?.city}</Text>
        <Text style={styles.blog}>{blogData?.blog}</Text>

        {blogData?.image_url && (
          <>
            <Text style={styles.subtitle}>📸 Generated Image</Text>
            <Image
              source={{ uri: `${BASE_URL}${blogData.image_url}` }}
              style={styles.image}
            />
          </>
        )}

        {blogData?.pdf_url && (
          <TouchableOpacity 
            style={styles.button}
            onPress={() => Linking.openURL(`${BASE_URL}${blogData.pdf_url}`)}
          >
            <Text style={styles.buttonText}>📄 Open PDF Blog</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    );
  };

  const renderWeatherTab = () => {
    const weatherData = data.weather;
    if (loading.weather) return <ActivityIndicator size="large" style={styles.center} />;
    if (weatherData?.error) return <Text style={styles.error}>Error: {weatherData.error}</Text>;

    const current = weatherData?.current;
    const history = weatherData?.monthly_history;

    return (
      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>🌡️ Weather Data - {current?.city}</Text>
        
        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Current Conditions</Text>
          <Text style={styles.temp}>{current?.temp_c}°C</Text>
          <Text style={styles.condition}>{current?.condition}</Text>
          <Text style={styles.details}>Feels like: {current?.feels_like_c}°C</Text>
          <Text style={styles.details}>Humidity: {current?.humidity}%</Text>
          <Text style={styles.details}>Wind: {current?.wind_kph} km/h</Text>
          <Text style={styles.details}>UV Index: {current?.uv}</Text>
        </View>

        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Air Quality</Text>
          <Text style={styles.details}>AQI (US EPA): {current?.aqi_us}</Text>
          <Text style={styles.details}>PM2.5: {current?.pm2_5}</Text>
          <Text style={styles.details}>PM10: {current?.pm10}</Text>
        </View>

        {history && history.length > 0 && (
          <View style={styles.weatherCard}>
            <Text style={styles.cardTitle}>Recent History</Text>
            {history.map((record, index) => (
              <View key={index} style={styles.historyItem}>
                <Text style={styles.date}>{record.date}</Text>
                <Text style={styles.historyTemp}>{record.avg_temp_c}°C</Text>
                <Text style={styles.historyCondition}>{record.condition}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    );
  };

  const renderTsunamiTab = () => {
    const tsunamiData = data.tsunami;
    if (loading.tsunami) return <ActivityIndicator size="large" style={styles.center} />;
    if (tsunamiData?.error) return <Text style={styles.error}>Error: {tsunamiData.error}</Text>;

    const earthquakes = tsunamiData?.earthquakes || [];

    return (
      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>🌊 Tsunami Detection</Text>
        <Text style={styles.subtitle}>Monitoring last {tsunamiData?.hours_checked || 24} hours</Text>
        
        {earthquakes.length === 0 ? (
          <View style={styles.weatherCard}>
            <Text style={styles.cardTitle}>✅ No Significant Activity</Text>
            <Text style={styles.details}>No earthquakes detected that could trigger tsunamis in the Indian Ocean region.</Text>
          </View>
        ) : (
          earthquakes.map((eq, index) => (
            <View key={index} style={[
              styles.weatherCard, 
              eq.risk === 'High' && styles.highRiskCard,
              eq.risk === 'Moderate' && styles.moderateRiskCard
            ]}>
              <Text style={styles.cardTitle}>📍 {eq.place}</Text>
              <Text style={styles.riskLevel}>Risk Level: {eq.risk}</Text>
              <Text style={styles.details}>Magnitude: {eq.magnitude}</Text>
              <Text style={styles.details}>Depth: {eq.depth_km} km</Text>
              <Text style={styles.details}>
                Location: {eq.coordinates.lat.toFixed(2)}°N, {eq.coordinates.lon.toFixed(2)}°E
              </Text>
            </View>
          ))
        )}

        <TouchableOpacity 
          style={styles.button}
          onPress={() => fetchData('/api/tsunami?hours=1', 'tsunami')}
        >
          <Text style={styles.buttonText}>🔄 Check Last Hour</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  };

  const renderPodcastTab = () => {
    const podcastData = data.podcast;
    if (loading.podcast) return <ActivityIndicator size="large" style={styles.center} />;
    if (podcastData?.error) return <Text style={styles.error}>Error: {podcastData.error}</Text>;

    return (
      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>🎙️ Climate Podcast - {podcastData?.city}</Text>
        
        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Podcast Script</Text>
          <Text style={styles.podcastScript}>{podcastData?.script}</Text>
        </View>

        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Current Weather Context</Text>
          <Text style={styles.details}>Temperature: {podcastData?.weather?.temp_c}°C</Text>
          <Text style={styles.details}>Condition: {podcastData?.weather?.condition}</Text>
          <Text style={styles.details}>Humidity: {podcastData?.weather?.humidity}%</Text>
        </View>

        <TouchableOpacity 
          style={styles.button}
          onPress={() => fetchData('/api/podcast/audio', 'podcast')}
        >
          <Text style={styles.buttonText}>🎵 Generate Audio Version</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  };

  const renderTwitterTab = () => {
    const twitterData = data.twitter;
    if (loading.twitter) return <ActivityIndicator size="large" style={styles.center} />;
    if (twitterData?.error) return <Text style={styles.error}>Error: {twitterData.error}</Text>;

    return (
      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.title}>🐦 Twitter Weather Post - {twitterData?.city}</Text>
        
        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Generated Tweet</Text>
          <Text style={styles.tweetText}>{twitterData?.tweet_text}</Text>
        </View>

        <View style={styles.weatherCard}>
          <Text style={styles.cardTitle}>Weather Context</Text>
          <Text style={styles.details}>Temperature: {twitterData?.weather?.temp_c}°C</Text>
          <Text style={styles.details}>Feels Like: {twitterData?.weather?.feels_like_c}°C</Text>
          <Text style={styles.details}>Condition: {twitterData?.weather?.condition}</Text>
          <Text style={styles.details}>Humidity: {twitterData?.weather?.humidity}%</Text>
          <Text style={styles.details}>Wind: {twitterData?.weather?.wind_kph} km/h</Text>
          <Text style={styles.details}>AQI: {twitterData?.weather?.aqi_us}</Text>
        </View>

        {twitterData?.tweet_url && (
          <TouchableOpacity 
            style={[styles.button, styles.successButton]}
            onPress={() => Linking.openURL(twitterData.tweet_url)}
          >
            <Text style={styles.buttonText}>🐦 View Tweet on Twitter</Text>
          </TouchableOpacity>
        )}

        {twitterData?.status === 'generated_but_not_posted' && (
          <View style={styles.weatherCard}>
            <Text style={styles.cardTitle}>⚠️ Tweet Generated but Not Posted</Text>
            <Text style={styles.details}>The tweet was generated but couldn't be posted to Twitter.</Text>
            <Text style={styles.details}>Error: {twitterData?.error}</Text>
          </View>
        )}

        <TouchableOpacity 
          style={styles.button}
          onPress={() => fetchData('/api/twitter', 'twitter')}
        >
          <Text style={styles.buttonText}>🔄 Generate New Tweet</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case "blog": return renderBlogTab();
      case "weather": return renderWeatherTab();
      case "tsunami": return renderTsunamiTab();
      case "podcast": return renderPodcastTab();
      case "twitter": return renderTwitterTab();
      default: return renderBlogTab();
    }
  };

  return (
    <View style={styles.container}>
      {renderTabBar()}
      {renderContent()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: "#f8f9fa" 
  },
  center: { 
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center" 
  },
  tabBar: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e1e5e9",
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  tab: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
    marginHorizontal: 2,
  },
  activeTab: {
    backgroundColor: "#007AFF",
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  tabText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#6c757d",
  },
  activeTabText: {
    color: "#fff",
  },
  content: {
    flex: 1,
    padding: 16,
  },
  title: { 
    fontSize: 24, 
    fontWeight: "bold", 
    marginBottom: 16,
    color: "#2c3e50",
    textAlign: "center"
  },
  subtitle: { 
    fontSize: 16, 
    marginTop: 16, 
    marginBottom: 8,
    color: "#6c757d",
    fontWeight: "600"
  },
  blog: { 
    fontSize: 16, 
    lineHeight: 24,
    color: "#2c3e50",
    marginBottom: 16
  },
  weatherCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#2c3e50",
    marginBottom: 12,
  },
  temp: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#007AFF",
    textAlign: "center",
    marginBottom: 8,
  },
  condition: {
    fontSize: 18,
    color: "#6c757d",
    textAlign: "center",
    marginBottom: 12,
  },
  details: {
    fontSize: 14,
    color: "#6c757d",
    marginBottom: 4,
  },
  historyItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#f1f3f4",
  },
  date: {
    fontSize: 12,
    color: "#6c757d",
    flex: 1,
  },
  historyTemp: {
    fontSize: 14,
    fontWeight: "600",
    color: "#007AFF",
    marginHorizontal: 8,
  },
  historyCondition: {
    fontSize: 12,
    color: "#6c757d",
    flex: 1,
    textAlign: "right",
  },
  highRiskCard: {
    borderLeftWidth: 4,
    borderLeftColor: "#dc3545",
    backgroundColor: "#fff5f5",
  },
  moderateRiskCard: {
    borderLeftWidth: 4,
    borderLeftColor: "#ffc107",
    backgroundColor: "#fffbf0",
  },
  riskLevel: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#dc3545",
    marginBottom: 8,
  },
  podcastScript: {
    fontSize: 15,
    lineHeight: 22,
    color: "#2c3e50",
    fontStyle: "italic",
  },
  image: {
    width: "100%",
    height: 220,
    resizeMode: "cover",
    marginBottom: 16,
    borderRadius: 8,
  },
  button: {
    backgroundColor: "#007AFF",
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 16,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  error: {
    color: "#dc3545",
    fontSize: 16,
    textAlign: "center",
    margin: 20,
  },
  tweetText: {
    fontSize: 16,
    lineHeight: 24,
    color: "#2c3e50",
    fontStyle: "italic",
    backgroundColor: "#f8f9fa",
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: "#1DA1F2",
  },
  successButton: {
    backgroundColor: "#28a745",
  }
});
