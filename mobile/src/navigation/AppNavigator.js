/**
 * AppNavigator
 * Main navigation structure with bottom tabs and stack navigation
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { SCREEN_NAMES, COLORS } from '../utils/constants';
import { useAuth } from '../store/AuthContext';
import { UI_TEXT } from '../utils/copy';

import DealDetailScreen from '../screens/DealDetailScreen';
import LoginScreen from '../screens/LoginScreen';
import SearchScreen from '../screens/SearchScreen';
import KeywordsScreen from '../screens/KeywordsScreen';
import NotificationsScreen from '../screens/NotificationsScreen';

import MainTabNavigator from './MainTabNavigator';

const Stack = createStackNavigator();

const AppNavigator = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>{UI_TEXT.loading.appInit}</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: COLORS.white,
            elevation: 0,
            shadowOpacity: 0,
            borderBottomWidth: 1,
            borderBottomColor: COLORS.divider,
          },
          headerTintColor: COLORS.textPrimary,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {isAuthenticated ? (
          <>
            {/* Main Tabs */}
            <Stack.Screen
              name={SCREEN_NAMES.MAIN_TABS}
              component={MainTabNavigator}
              options={{ headerShown: false }}
            />

            {/* Auth and utility screens */}
            <Stack.Screen
              name={SCREEN_NAMES.SEARCH}
              component={SearchScreen}
              options={{ title: '검색' }}
            />
            <Stack.Screen
              name={SCREEN_NAMES.KEYWORDS}
              component={KeywordsScreen}
              options={{ title: '키워드 관리' }}
            />
            <Stack.Screen
              name={SCREEN_NAMES.NOTIFICATIONS}
              component={NotificationsScreen}
              options={{ title: '알림 내역' }}
            />

            {/* Stack Screens */}
            <Stack.Screen
              name={SCREEN_NAMES.DEAL_DETAIL}
              component={DealDetailScreen}
              options={{ title: '딜 상세' }}
            />
          </>
        ) : (
          <>
            {/* Auth flow */}
            <Stack.Screen
              name={SCREEN_NAMES.LOGIN}
              component={LoginScreen}
              options={{ headerShown: false }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 12,
    color: COLORS.textSecondary,
  },
});

export default AppNavigator;
