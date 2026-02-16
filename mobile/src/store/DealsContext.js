/**
 * Deals Context
 * Manages deals data and operations
 */
import React, { createContext, useState, useContext, useCallback } from 'react';
import { dealsAPI, bookmarksAPI } from '../services/api';
import { UI_TEXT, resolveRequestError } from '../utils/copy';

const DealsContext = createContext();

export const useDeals = () => {
  const context = useContext(DealsContext);
  if (!context) {
    throw new Error('useDeals must be used within DealsProvider');
  }
  return context;
};

export const DealsProvider = ({ children }) => {
  const [deals, setDeals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  });
  const [filters, setFilters] = useState({
    sourceId: null,
    categoryId: null,
    sortBy: 'hot_score',
    order: 'desc',
  });

  const resolveError = (error, fallback) =>
    resolveRequestError(error, fallback, {
      byType: {
        network: UI_TEXT.errors.network.unreachable,
        validation: fallback,
        server: UI_TEXT.errors.server.unavailable,
      },
    });

  /**
   * Fetch deals with current filters
   */
  const fetchDeals = useCallback(async (page = 1, append = false, activeFilters = filters) => {
    try {
      setIsLoading(true);
      setError(null);

      const apiFilters = {
        source_id: activeFilters.sourceId,
        category_id: activeFilters.categoryId,
        sort_by: activeFilters.sortBy || 'hot_score',
        order: activeFilters.order || 'desc',
      };

      const response = await dealsAPI.getDeals({
        page,
        page_size: pagination.pageSize,
        ...apiFilters,
      });

      if (append) {
        setDeals((prev) => [...prev, ...response.deals]);
      } else {
        setDeals(response.deals);
      }

      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages,
      });

      return { success: true };
      } catch (err) {
      const errorMessage = resolveError(err, UI_TEXT.errors.deals.loadFail);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [filters, pagination.pageSize]);

  /**
   * Refresh deals (pull to refresh)
   */
  const refreshDeals = useCallback(async () => {
    return await fetchDeals(1, false);
  }, [fetchDeals, filters]);

  /**
   * Load more deals (pagination)
   */
  const loadMoreDeals = useCallback(async () => {
    if (pagination.page < pagination.totalPages && !isLoading) {
      return await fetchDeals(pagination.page + 1, true);
    }
  }, [pagination, isLoading, fetchDeals]);

  /**
   * Update filters and refetch
   */
  const updateFilters = useCallback(async (newFilters) => {
    const updatedFilters = {
      ...filters,
      ...newFilters,
    };
    setFilters(updatedFilters);
    // Reset to page 1 when filters change
    return await fetchDeals(1, false, updatedFilters);
  }, [fetchDeals, filters]);

  /**
   * Search deals by keyword
   */
  const searchDeals = useCallback(async (keyword, page = 1) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await dealsAPI.searchDeals(keyword, page, pagination.pageSize);

      setDeals(response.deals);
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages,
      });

      return { success: true };
      } catch (err) {
      const errorMessage = resolveError(err, UI_TEXT.errors.search.fail);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [pagination.pageSize]);

  /**
   * Find bookmark ID for a deal from the user's bookmark list.
   */
  const findBookmarkIdByDealId = useCallback(
    async (dealId) => {
      let page = 1;

      while (true) {
        const response = await bookmarksAPI.getBookmarks(
          page,
          Math.min(pagination.pageSize, 100),
        );
        const pageSize = response.page_size || Math.min(pagination.pageSize, 100);
        const totalPages = response.total_pages || Math.max(Math.ceil((response.total || 0) / pageSize), 1);

        const matched = response.bookmarks?.find((bookmark) => bookmark.deal_id === dealId);
        if (matched?.id) {
          return matched.id;
        }

        if (page >= totalPages) {
          return null;
        }
        page += 1;
      }
    },
    [pagination.pageSize],
  );

  /**
   * Toggle bookmark for a deal
   */
  const toggleBookmark = useCallback(
    async (dealId, isBookmarked, sourceBookmarkId = null) => {
      let bookmarkId = null;

      try {
        if (!dealId) {
          const errorMessage = UI_TEXT.errors.deals.invalid;
          setError(errorMessage);
          return {
            success: false,
            error: errorMessage,
          };
        }

        if (isBookmarked) {
          bookmarkId = sourceBookmarkId || (await findBookmarkIdByDealId(dealId));
          if (!bookmarkId) {
            return {
              success: false,
              error: UI_TEXT.errors.bookmark.missingId,
            };
          }
          await bookmarksAPI.removeBookmark(bookmarkId);
        } else {
          // Add bookmark
          const created = await bookmarksAPI.addBookmark(dealId);
          bookmarkId = created?.id || null;
        }

        // Update local state
        setDeals((prev) =>
          prev.map((deal) =>
            deal.id === dealId
              ? {
                  ...deal,
                  is_bookmarked: !isBookmarked,
                  bookmark_count: Math.max(
                    (deal.bookmark_count || 0) + (isBookmarked ? -1 : 1),
                    0,
                  ),
                }
              : deal,
          ),
        );

        return {
          success: true,
          action: isBookmarked ? 'removed' : 'added',
          bookmarkId,
        };
      } catch (err) {
      const errorMessage = resolveError(err, UI_TEXT.errors.bookmark.actionFail);
      setError(errorMessage);
      return { success: false, error: errorMessage };
      }
    },
    [deals, findBookmarkIdByDealId],
  );

  const clearError = () => setError(null);

  const value = {
    deals,
    isLoading,
    error,
    pagination,
    filters,
    fetchDeals,
    refreshDeals,
    loadMoreDeals,
    updateFilters,
    searchDeals,
    toggleBookmark,
    clearError,
  };

  return <DealsContext.Provider value={value}>{children}</DealsContext.Provider>;
};
