// Example: How a React Native mobile app would use this API
// This shows what the mobile developer needs to build

import React, { useState, useEffect } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import * as Location from 'expo-location';

const TourGuideApp = () => {
  const [location, setLocation] = useState(null);
  const [nearbyMonuments, setNearbyMonuments] = useState([]);
  const [guideResponse, setGuideResponse] = useState('');

  // 1. REQUEST GPS PERMISSION
  const requestLocationPermission = async () => {
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission denied', 'GPS access is required for tour guide features');
      return false;
    }
    return true;
  };

  // 2. GET CURRENT GPS LOCATION
  const getCurrentLocation = async () => {
    try {
      const hasPermission = await requestLocationPermission();
      if (!hasPermission) return;

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      setLocation({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude
      });

      // 3. SEND GPS TO YOUR BACKEND API
      await checkNearbyMonuments(location.coords.latitude, location.coords.longitude);
      
    } catch (error) {
      Alert.alert('Error', 'Could not get your location');
    }
  };

  // 4. CALL YOUR BACKEND API WITH GPS COORDINATES
  const checkNearbyMonuments = async (lat, lon) => {
    try {
      // This calls YOUR backend API we just built
      const response = await fetch('http://your-api.onrender.com/api/check-location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: lat,
          longitude: lon,
          radius_km: 1.0
        })
      });

      const data = await response.json();
      setNearbyMonuments(data.monuments);

    } catch (error) {
      Alert.alert('Error', 'Could not fetch monument data');
    }
  };

  // 5. CHAT WITH AI TOUR GUIDE
  const askTourGuide = async (message) => {
    if (!location) {
      Alert.alert('Error', 'Location not available');
      return;
    }

    try {
      const response = await fetch('http://your-api.onrender.com/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: message,
          user_latitude: location.latitude,
          user_longitude: location.longitude
        })
      });

      const data = await response.json();
      setGuideResponse(data.response);

    } catch (error) {
      Alert.alert('Error', 'Could not reach tour guide');
    }
  };

  // 6. AUTO-UPDATE LOCATION (Real-time tracking)
  useEffect(() => {
    const watchLocation = async () => {
      const hasPermission = await requestLocationPermission();
      if (!hasPermission) return;

      // Update location every 30 seconds
      const locationSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 30000, // 30 seconds
          distanceInterval: 50, // 50 meters
        },
        (newLocation) => {
          setLocation({
            latitude: newLocation.coords.latitude,
            longitude: newLocation.coords.longitude
          });
          
          // Auto-check for new monuments as user moves
          checkNearbyMonuments(
            newLocation.coords.latitude, 
            newLocation.coords.longitude
          );
        }
      );

      return () => locationSubscription.remove();
    };

    watchLocation();
  }, []);

  return (
    <View style={{ padding: 20 }}>
      <Text>Delhi Tour Guide</Text>
      
      <Button 
        title="Get My Location" 
        onPress={getCurrentLocation} 
      />
      
      {location && (
        <Text>
          📍 You are at: {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
        </Text>
      )}
      
      {nearbyMonuments.length > 0 && (
        <View>
          <Text>🏛️ Nearby Monuments:</Text>
          {nearbyMonuments.map((monument, index) => (
            <Text key={index}>
              • {monument.name} ({monument.distance_km} km)
            </Text>
          ))}
        </View>
      )}
      
      <Button 
        title="Ask: What should I see here?" 
        onPress={() => askTourGuide("What should I see here?")} 
      />
      
      {guideResponse && (
        <Text>🤖 Tour Guide: {guideResponse}</Text>
      )}
    </View>
  );
};

export default TourGuideApp;