import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator, FlatList } from "react-native";

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔥 Replace YOUR_IP_HERE with your laptop's local IP (step 1)
  const API_URL = "http://172.17.132.1:5000/api/tsunami";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        const json = await response.json();
        setData(json);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text>Fetching Tsunami Alerts...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>🌊 Indian Tsunami Alerts</Text>
      <FlatList
        data={data}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.place}>{item.place}</Text>
            <Text>Magnitude: {item.magnitude}</Text>
            <Text>Depth: {item.depth_km} km</Text>
            <Text>Risk: {item.risk}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 16,
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 12,
  },
  card: {
    backgroundColor: "#E8F0FE",
    padding: 15,
    marginVertical: 8,
    borderRadius: 10,
    width: "100%",
  },
  place: {
    fontWeight: "bold",
    fontSize: 16,
  },
});
