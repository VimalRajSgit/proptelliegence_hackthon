// App.js (React Native)
import React, {useEffect, useState} from "react";
import { View, Text, ScrollView, ActivityIndicator, Image, Linking, TouchableOpacity, StyleSheet } from "react-native";

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const API = "http://172.17.132.1:5000/api/weather_blog";

  useEffect(() => {
    fetch(API)
      .then(r => r.json())
      .then(json => {
        setData(json);
      })
      .catch(err => {
        setData({ error: err.message });
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <View style={styles.center}>
      <ActivityIndicator size="large" />
      <Text>Generating blog…</Text>
    </View>
  );

  if (data && data.error) return (
    <View style={styles.container}>
      <Text style={{color: "red"}}>Error: {data.error}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🌦️ Weather Blog - {data.city}</Text>
      <Text style={styles.blog}>{data.blog}</Text>

      {data.image_url ? (
        <>
          <Text style={styles.subtitle}>Image</Text>
          <Image
            source={{ uri: `http://172.17.132.1:5000${data.image_url}` }}
            style={{ width: "100%", height: 220, resizeMode: "cover", marginBottom: 16 }}
          />
        </>
      ) : null}

      {data.pdf_url ? (
        <TouchableOpacity onPress={() => Linking.openURL(`http://172.17.132.1:5000${data.pdf_url}`)}>
          <Text style={styles.link}>Open PDF</Text>
        </TouchableOpacity>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  center: { flex:1, justifyContent:"center", alignItems:"center" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 12 },
  subtitle: { fontSize: 18, marginTop: 12, marginBottom: 6 },
  blog: { fontSize: 16, lineHeight: 24 },
  link: { color: "#007AFF", marginTop: 12 }
});
