/**
 * Utility helper functions
 */

/**
 * Format price to Korean Won
 * @param {number} price - Price in KRW
 * @returns {string} Formatted price (e.g., "12,345원")
 */
export const formatPrice = (price) => {
  if (!price) return '가격 미정';
  return `${price.toLocaleString('ko-KR')}원`;
};

/**
 * Format large numbers to Korean units (만, 억)
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatKoreanNumber = (num) => {
  if (num >= 100000000) {
    // 억
    return `${(num / 100000000).toFixed(1)}억`;
  } else if (num >= 10000) {
    // 만
    return `${(num / 10000).toFixed(1)}만`;
  }
  return num.toLocaleString('ko-KR');
};

/**
 * Calculate discount percentage
 * @param {number} originalPrice - Original price
 * @param {number} currentPrice - Current price
 * @returns {number} Discount percentage
 */
export const calculateDiscount = (originalPrice, currentPrice) => {
  if (!originalPrice || !currentPrice) return 0;
  return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
};

/**
 * Format relative time in Korean
 * @param {string|Date} dateString - Date to format
 * @returns {string} Relative time (e.g., "5분 전", "2시간 전")
 */
export const formatRelativeTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return '방금 전';
  if (diffMin < 60) return `${diffMin}분 전`;
  if (diffHour < 24) return `${diffHour}시간 전`;
  if (diffDay < 7) return `${diffDay}일 전`;

  // More than 7 days - show date
  return date.toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Get price signal color and emoji
 * @param {string} signal - Price signal ('lowest', 'average', 'high')
 * @returns {object} Color and emoji
 */
export const getPriceSignal = (signal) => {
  const signals = {
    lowest: { emoji: '🟢', label: '역대가', color: '#4CAF50' },
    average: { emoji: '🟡', label: '평균가', color: '#FFC107' },
    high: { emoji: '🔴', label: '비쌈', color: '#F44336' },
  };
  return signals[signal] || { emoji: '', label: '', color: '#999' };
};

/**
 * Get source color by source name
 * @param {string} sourceName - Source name
 * @returns {string} Hex color code
 */
export const getSourceColor = (sourceName) => {
  const colors = {
    ppomppu: '#FF6B6B',
    ruliweb: '#4ECDC4',
    fmkorea: '#95E1D3',
    quasarzone: '#F38181',
    dealbada: '#AA96DA',
  };
  return colors[sourceName] || '#999999';
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Parse URL and extract domain
 * @param {string} url - URL to parse
 * @returns {string} Domain name
 */
export const getDomain = (url) => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace('www.', '');
  } catch {
    return '';
  }
};

/**
 * Check if deal is new (within 1 hour)
 * @param {string|Date} publishedAt - Published date
 * @returns {boolean} True if new
 */
export const isNewDeal = (publishedAt) => {
  const date = new Date(publishedAt);
  const now = new Date();
  const diffHours = (now - date) / (1000 * 60 * 60);
  return diffHours < 1;
};

/**
 * Format hot score for display
 * @param {number} score - Hot score
 * @returns {string} Formatted score
 */
export const formatHotScore = (score) => {
  if (score >= 1000) return `${(score / 1000).toFixed(1)}K`;
  return Math.round(score).toString();
};

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};
