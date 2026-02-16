/**
 * MainTabNavigator
 * Bottom tab navigation for main screens
 */
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, StyleSheet } from 'react-native';
import { SCREEN_NAMES, COLORS, SIZES } from '../utils/constants';

// Import screens
import HomeScreen from '../screens/HomeScreen';
import BookmarksScreen from '../screens/BookmarksScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const MainTabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textSecondary,
        tabBarLabelStyle: { fontSize: SIZES.fontXs },
        tabBarStyle: styles.tabBar,
      }}
    >
      <Tab.Screen
        name={SCREEN_NAMES.HOME}
        component={HomeScreen}
        options={{
          tabBarLabel: '홈',
          tabBarIcon: ({ color }) => <Text style={[styles.tabIcon, { color }]}>🏠</Text>,
        }}
      />
      <Tab.Screen
        name={SCREEN_NAMES.BOOKMARKS}
        component={BookmarksScreen}
        options={{
          tabBarLabel: '북마크',
          tabBarIcon: ({ color }) => <Text style={[styles.tabIcon, { color }]}>⭐️</Text>,
        }}
      />
      <Tab.Screen
        name={SCREEN_NAMES.SETTINGS}
        component={SettingsScreen}
        options={{
          tabBarLabel: '설정',
          tabBarIcon: ({ color }) => <Text style={[styles.tabIcon, { color }]}>⚙️</Text>,
        }}
      />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: COLORS.white,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
    paddingBottom: 4,
    paddingTop: 4,
    minHeight: 56,
  },
  tabIcon: {
    fontSize: 24,
    marginBottom: -2,
  },
});

export default MainTabNavigator;
