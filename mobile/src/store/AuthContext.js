/**
 * Authentication Context
 * Manages user authentication state and operations
 */
import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';
import { UI_TEXT, resolveRequestError } from '../utils/copy';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const resolveAuthError = (error, fallback) =>
    resolveRequestError(error, fallback, {
      byType: {
        network: UI_TEXT.errors.network.unreachable,
        validation: fallback,
        server: UI_TEXT.errors.server.unavailable,
      },
    });

  // Check for existing token on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        // Validate token by fetching user info
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      // Token invalid, clear it
      await AsyncStorage.removeItem('auth_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await authAPI.login(email, password);
      setUser(response.user);

      return { success: true };
    } catch (err) {
      const errorMessage = resolveAuthError(err, UI_TEXT.errors.auth.loginFail);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email, password, username) => {
    try {
      setError(null);
      setIsLoading(true);

      await authAPI.signup(email, password, username);

      // Auto login after signup
      return await login(email, password);
    } catch (err) {
      const errorMessage = resolveAuthError(err, UI_TEXT.errors.auth.signupFail);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const clearError = () => setError(null);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    signup,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
