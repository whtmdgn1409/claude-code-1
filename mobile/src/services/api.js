/**
 * API Client for DealMoa Backend
 * Base URL: http://localhost:8000/api/v1
 */
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Base configuration
const DEV_HOST = Platform.OS === 'android' ? '10.0.2.2' : 'localhost';
const API_BASE_URL = __DEV__
  ? `http://${DEV_HOST}:8000/api/v1`  // Development
  : 'https://api.dealmoa.app/api/v1';  // Production

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      await AsyncStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Auth API
// ============================================================================

export const authAPI = {
  /**
   * Sign up a new user
   */
  signup: async (email, password, username, displayName = null) => {
    return apiClient.post('/users/register', {
      email,
      password,
      username,
      display_name: displayName,
    });
  },

  /**
   * Login user
   */
  login: async (email, password) => {
    const response = await apiClient.post('/users/login', {
      email,
      password,
    });

    // Save token
    if (response.access_token) {
      await AsyncStorage.setItem('auth_token', response.access_token);
    }

    return response;
  },

  /**
   * Logout user
   */
  logout: async () => {
    await AsyncStorage.removeItem('auth_token');
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    return apiClient.get('/users/me');
  },
};

// ============================================================================
// Deals API
// ============================================================================

export const dealsAPI = {
  /**
   * Get paginated list of deals
   */
  getDeals: async (params = {}) => {
    const {
      page = 1,
      page_size = 20,
      source_id,
      category_id,
      sort_by = 'hot_score',
      order = 'desc',
    } = params;

    return apiClient.get('/deals', {
      params: {
        page,
        page_size,
        source_id,
        category_id,
        sort_by,
        order,
      },
    });
  },

  /**
   * Get deal detail by ID
   */
  getDealDetail: async (dealId) => {
    return apiClient.get(`/deals/${dealId}`);
  },

  /**
   * Search deals by keyword
   */
  searchDeals: async (keyword, page = 1, pageSize = 20) => {
    return apiClient.get('/deals/search', {
      params: {
        keyword,
        page,
        page_size: pageSize,
      },
    });
  },

  /**
   * Get AI summary for a deal
   */
  getDealSummary: async (dealId, forceRegenerate = false) => {
    return apiClient.get(`/deals/${dealId}/summary`, {
      params: { force_regenerate: forceRegenerate },
    });
  },

  /**
   * Get price history for a deal
   */
  getPriceHistory: async (dealId, days = 30) => {
    return apiClient.get(`/deals/${dealId}/price-history`, {
      params: { days },
    });
  },
};

// ============================================================================
// Sources API
// ============================================================================

export const sourcesAPI = {
  /**
   * Get all deal sources
   */
  getSources: async () => {
    return apiClient.get('/sources');
  },
};

// ============================================================================
// Categories API
// ============================================================================

export const categoriesAPI = {
  /**
   * Get all categories
   */
  getCategories: async () => {
    return apiClient.get('/categories');
  },
};

// ============================================================================
// Bookmarks API
// ============================================================================

export const bookmarksAPI = {
  /**
   * Get user's bookmarks
   */
  getBookmarks: async (page = 1, pageSize = 20) => {
    return apiClient.get('/bookmarks', {
      params: { page, page_size: pageSize },
    });
  },

  /**
   * Add bookmark
   */
  addBookmark: async (dealId) => {
    return apiClient.post('/bookmarks', { deal_id: dealId });
  },

  /**
   * Remove bookmark
   */
  removeBookmark: async (bookmarkId) => {
    return apiClient.delete(`/bookmarks/${bookmarkId}`);
  },

  /**
   * Check if deal is bookmarked
   * (Deprecated endpoint removed in backend)
   */
  isBookmarked: async (dealId) => {
    const response = await apiClient.get('/bookmarks');
    return {
      bookmarked: response.bookmarks?.some((item) => item.deal_id === dealId),
      bookmarks: response.bookmarks,
    };
  },
};

// ============================================================================
// Keywords API
// ============================================================================

export const keywordsAPI = {
  /**
   * Get user's keywords
   */
  getKeywords: async () => {
    return apiClient.get('/users/keywords');
  },

  /**
   * Add keyword
   */
  addKeyword: async (keyword, isInclusion = true) => {
    return apiClient.post('/users/keywords', {
      keyword,
      is_inclusion: isInclusion,
    });
  },

  /**
   * Add keywords in batch
   */
  addKeywordsBatch: async (keywords) => {
    return apiClient.post('/users/keywords/batch', keywords);
  },

  /**
   * Update keyword
   */
  updateKeyword: async (keywordId, data) => {
    return apiClient.put(`/users/keywords/${keywordId}`, data);
  },

  /**
   * Delete keyword
   */
  deleteKeyword: async (keywordId) => {
    return apiClient.delete(`/users/keywords/${keywordId}`);
  },
};

// ============================================================================
// Devices API (for push notifications)
// ============================================================================

export const devicesAPI = {
  /**
   * Register device token
   */
  registerDevice: async (token, platform) => {
    return apiClient.post('/devices', {
      device_type: platform,
      device_token: token,
    });
  },

  /**
   * Unregister device
   */
  unregisterDevice: async (token) => {
    return apiClient.delete('/devices', {
      data: {
        device_token: token,
      },
    });
  },

  /**
   * List active devices
   */
  getDevices: async () => {
    return apiClient.get('/devices');
  },
};

// ============================================================================
// Notifications API
// ============================================================================

export const notificationsAPI = {
  /**
   * Get user's notifications
   */
  getNotifications: async (page = 1, pageSize = 20) => {
    return apiClient.get('/notifications', {
      params: { page, page_size: pageSize },
    });
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (notificationIds) => {
    const ids = Array.isArray(notificationIds)
      ? notificationIds
      : [notificationIds];
    return apiClient.post('/notifications/read', {
      notification_ids: ids,
    });
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async () => {
    return apiClient.post('/notifications/read-all');
  },

  /**
   * Mark notification as clicked (read + clicked_at)
   */
  markAsClicked: async (notificationId) => {
    return apiClient.post(`/notifications/${notificationId}/click`);
  },

  /**
   * Get unread count only
   */
  getUnreadCount: async () => {
    return apiClient.get('/notifications/unread-count');
  },
};

export default apiClient;
