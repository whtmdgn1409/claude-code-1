'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  createBookmark,
  deleteBookmark,
  getMe,
  listBookmarks,
  loginUser,
  registerUser,
} from '@/lib/client-api';

const TOKEN_KEY = 'dealmoa_access_token';

const AuthContext = createContext({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  isReady: false,
  authError: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  bookmarkedDeals: new Map(),
  isBookmarked: () => false,
  toggleBookmark: async () => {},
  reloadBookmarks: async () => {},
});

const normalizeBookmarks = (bookmarks = []) => {
  const next = new Map();
  bookmarks.forEach((bookmark) => {
    if (!bookmark?.deal_id || !bookmark?.id) return;
    next.set(Number(bookmark.deal_id), Number(bookmark.id));
  });
  return next;
};

const getStoredToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const [bookmarkedDeals, setBookmarkedDeals] = useState(new Map());

  const isAuthenticated = Boolean(token && user);
  const isReady = !isLoading;

  const reloadBookmarks = useCallback(
    async (activeToken = token) => {
      if (!activeToken) {
        setBookmarkedDeals(new Map());
        return;
      }

      try {
        const first = await listBookmarks({ page: 1, page_size: 200, token: activeToken });
        const pageTotal = Math.max(1, Number(first?.total_pages || 1));
        const merged = [...(first?.bookmarks || [])];

        if (pageTotal > 1) {
          for (let page = 2; page <= Math.min(pageTotal, 3); page += 1) {
            const next = await listBookmarks({ page, page_size: 200, token: activeToken });
            merged.push(...(next?.bookmarks || []));
          }
        }

        setBookmarkedDeals(normalizeBookmarks(merged));
      } catch {
        // Bookmark state will be retried on next interaction.
        setBookmarkedDeals(new Map());
      }
    },
    [token],
  );

  const loadUser = useCallback(
    async (activeToken) => {
      const bearerToken = activeToken || token;
      if (!bearerToken) {
        setUser(null);
        setBookmarkedDeals(new Map());
        setToken(null);
        return null;
      }

      try {
        const data = await getMe(bearerToken);
        setUser(data);
        await reloadBookmarks(bearerToken);
        setAuthError(null);
        return data;
      } catch (error) {
        setUser(null);
        setBookmarkedDeals(new Map());
        if (bearerToken === getStoredToken()) {
          localStorage.removeItem(TOKEN_KEY);
        }
        setToken(null);
        setAuthError(error?.message || '인증 정보를 확인할 수 없습니다.');
        throw error;
      }
    },
    [reloadBookmarks, token],
  );

  useEffect(() => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setToken(null);
      setUser(null);
      setIsLoading(false);
      return;
    }

    setToken(storedToken);
    setIsLoading(true);
    loadUser(storedToken).finally(() => {
      setIsLoading(false);
    });
  }, [loadUser]);

  const login = async (email, password) => {
    setAuthError(null);
    setIsLoading(true);
    try {
      const data = await loginUser(email, password);
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setUser(data.user || null);
      await reloadBookmarks(data.access_token);
      return data;
    } catch (error) {
      setAuthError(error?.message || '로그인에 실패했습니다.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email, password, username, displayName) => {
    setAuthError(null);
    setIsLoading(true);
    try {
      const data = await registerUser({ email, password, username, displayName });
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setUser(data.user || null);
      await reloadBookmarks(data.access_token);
      return data;
    } catch (error) {
      setAuthError(error?.message || '회원가입에 실패했습니다.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = useCallback(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
    }
    setToken(null);
    setUser(null);
    setBookmarkedDeals(new Map());
    setAuthError(null);
  }, []);

  const isBookmarked = useCallback((dealId) => bookmarkedDeals.has(Number(dealId)), [bookmarkedDeals]);

  const bookmarkIdByDeal = useCallback((dealId) => bookmarkedDeals.get(Number(dealId)), [bookmarkedDeals]);

  const toggleBookmark = useCallback(async (dealId) => {
    if (!token) {
      throw new Error('로그인이 필요합니다. 먼저 로그인해 주세요.');
    }

    const id = Number(dealId);
    const bookmarkId = bookmarkedDeals.get(id);

    if (bookmarkId) {
      await deleteBookmark(bookmarkId, token);
      setBookmarkedDeals((prev) => {
        const next = new Map(prev);
        next.delete(id);
        return next;
      });
      return { isBookmarked: false };
    }

    const created = await createBookmark(id, token);
    setBookmarkedDeals((prev) => {
      const next = new Map(prev);
      next.set(id, Number(created?.id));
      return next;
    });
    return { isBookmarked: true };
  }, [bookmarkedDeals, token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated,
      isLoading,
      isReady,
      authError,
      login,
      register,
      logout,
      bookmarkedDeals,
      isBookmarked,
      bookmarkIdByDeal,
      toggleBookmark,
      reloadBookmarks,
    }),
    [user, token, isAuthenticated, isLoading, isReady, authError, login, register, logout, bookmarkedDeals, isBookmarked, bookmarkIdByDeal, toggleBookmark, reloadBookmarks],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
