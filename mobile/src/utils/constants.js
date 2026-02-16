/**
 * App-wide constants
 */

export const COLORS = {
  // Primary colors
  primary: '#FF6B6B',
  primaryDark: '#E85555',
  primaryLight: '#FF8888',

  // Secondary colors
  secondary: '#4ECDC4',
  secondaryDark: '#3CB8AF',
  secondaryLight: '#6FD7CF',

  // Neutrals
  white: '#FFFFFF',
  black: '#000000',
  gray100: '#F5F5F5',
  gray200: '#EEEEEE',
  gray300: '#E0E0E0',
  gray400: '#BDBDBD',
  gray500: '#9E9E9E',
  gray600: '#757575',
  gray700: '#616161',
  gray800: '#424242',
  gray900: '#212121',

  // Semantic colors
  success: '#4CAF50',
  warning: '#FFC107',
  error: '#F44336',
  info: '#2196F3',

  // Background
  background: '#FAFAFA',
  surface: '#FFFFFF',

  // Text
  textPrimary: '#212121',
  textSecondary: '#757575',
  textDisabled: '#BDBDBD',

  // Borders
  border: '#E0E0E0',
  divider: '#EEEEEE',
};

export const SIZES = {
  // Spacing
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 40,

  // Font sizes
  fontXs: 11,
  fontSm: 13,
  fontMd: 15,
  fontLg: 17,
  fontXl: 20,
  fontXxl: 24,
  fontXxxl: 28,

  // Border radius
  radiusSm: 4,
  radiusMd: 8,
  radiusLg: 12,
  radiusXl: 16,
  radiusFull: 9999,

  // Icon sizes
  iconSm: 16,
  iconMd: 24,
  iconLg: 32,
  iconXl: 48,
};

export const SHADOWS = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
};

export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
};

export const SCREEN_NAMES = {
  // Root stacks
  MAIN_TABS: 'MainTabs',
  LOGIN: 'Login',

  // Main tabs
  HOME: 'Home',
  BOOKMARKS: 'Bookmarks',
  SETTINGS: 'Settings',

  // Stack screens
  DEAL_DETAIL: 'DealDetail',
  SEARCH: 'Search',
  KEYWORDS: 'Keywords',
  NOTIFICATIONS: 'Notifications',
  SIGNUP: 'Signup',
};

export const API_CONFIG = {
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  PAGE_SIZE: 20,
};

export const DEAL_SORT_OPTIONS = [
  { value: 'hot_score', label: '인기순' },
  { value: 'published_at', label: '최신순' },
  { value: 'price', label: '가격순' },
  { value: 'bookmark_count', label: '북마크순' },
];

export const SOURCE_NAMES = {
  ppomppu: '뽐뿌',
  ruliweb: '루리웹',
  fmkorea: '펨코',
  quasarzone: '퀘이사존',
  dealbada: '딜바다',
};
