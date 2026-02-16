/**
 * Search Screen
 * Allows users to search deals by keyword.
 */
import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { dealsAPI } from '../services/api';
import { useDeals } from '../store/DealsContext';
import { API_CONFIG, COLORS, SIZES, SCREEN_NAMES } from '../utils/constants';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import DealCard from '../components/DealCard';
import InlineToast from '../components/InlineToast';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';

const SearchScreen = ({ navigation }) => {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const { toggleBookmark } = useDeals();
  const [toast, setToast] = useState({
    visible: false,
    message: '',
    type: 'error',
    trigger: 0,
  });

  const resolveBookmarkError = (error, fallback = UI_TEXT.errors.bookmark.actionFail) =>
    resolveRequestError(error, fallback, {
      byType: {
        network: UI_TEXT.errors.network.unreachable,
        validation: fallback,
        server: UI_TEXT.errors.server.unavailable,
      },
    });

  const showBookmarkError = (errorOrMessage = UI_TEXT.errors.bookmark.actionFail) => {
    const message =
      typeof errorOrMessage === 'string'
        ? errorOrMessage
        : resolveBookmarkError(errorOrMessage, UI_TEXT.errors.bookmark.actionFail);

    setToast({
      visible: true,
      message,
      type: 'error',
      trigger: Date.now(),
    });
  };

  const fetchSearchResults = useCallback(async (query, targetPage = 1, append = false) => {
    const trimmed = query.trim();

    try {
      setIsLoading(true);
      setError(null);
      if (!append) {
        setResults([]);
      }

      if (!trimmed) {
        setError(UI_TEXT.errors.search.required);
        setIsSubmitted(false);
        setTotalPages(0);
        setPage(1);
        return;
      }

      if (trimmed.length < 2) {
        setError(UI_TEXT.errors.search.minLength);
        setIsSubmitted(false);
        setTotalPages(0);
        setPage(1);
        return;
      }

      const response = await dealsAPI.searchDeals(
        trimmed,
        targetPage,
        API_CONFIG.PAGE_SIZE,
      );

      setResults((prev) => (append ? [...prev, ...response.deals] : response.deals));
      setPage(response.page);
      setTotalPages(response.total_pages);
      setIsSubmitted(true);
    } catch (err) {
      setError(
        resolveRequestError(err, UI_TEXT.errors.search.fail, {
          byType: {
            network: UI_TEXT.errors.network.unreachable,
            validation: UI_TEXT.errors.search.fail,
            server: UI_TEXT.errors.server.unavailable,
          },
        }),
      );
      if (!append) {
        setResults([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSearch = async () => {
    await fetchSearchResults(keyword, 1, false);
  };

  const handleLoadMore = () => {
    if (!isLoading && isSubmitted && page < totalPages) {
      fetchSearchResults(keyword, page + 1, true);
    }
  };

  const handleRefresh = async () => {
    if (!isSubmitted) return;
    setRefreshing(true);
    await fetchSearchResults(keyword, 1, false);
    setRefreshing(false);
  };

  const handleBookmark = async (deal) => {
    if (!deal?.id) {
      showBookmarkError(UI_TEXT.errors.deals.invalid);
      return;
    }

    try {
      const result = await toggleBookmark(
        deal.id,
        !!deal.is_bookmarked,
        deal.bookmark_id || null,
      );

      if (!result?.success) {
        throw new Error(result?.error || UI_TEXT.errors.bookmark.actionFail);
      }

      setResults((prev) =>
        prev.map((item) =>
          item.id === deal.id
            ? {
                ...item,
                is_bookmarked: !item.is_bookmarked,
                bookmark_id: !item.is_bookmarked
                  ? result?.bookmark_id || item.bookmark_id
                  : null,
              }
            : item,
        ),
      );
    } catch (error) {
      showBookmarkError(error);
    }
  };

  const hideToast = () => setToast((prev) => ({ ...prev, visible: false }));

  const renderDealCard = ({ item }) => (
      <DealCard
        deal={item}
        onPress={(deal) => navigation.navigate(SCREEN_NAMES.DEAL_DETAIL, { deal })}
        onBookmark={handleBookmark}
        onBookmarkError={(error) => showBookmarkError(error)}
      />
  );

  const renderFooter = () => {
    if (!isLoading || results.length === 0) return null;
    return (
      <View style={styles.footerLoader}>
        <LoadingSpinner size="small" message="" />
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <InlineToast
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        trigger={toast.trigger}
        onHide={hideToast}
      />

      <View style={styles.searchBox}>
          <TextInput
            value={keyword}
            onChangeText={setKeyword}
          placeholder={UI_TEXT.empty.searchPlaceholder}
            style={styles.input}
            returnKeyType="search"
            onSubmitEditing={handleSearch}
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>{UI_TEXT.actions.search}</Text>
          </TouchableOpacity>
        </View>

      {isLoading && results.length === 0 && (
        <LoadingSpinner message={UI_TEXT.loading.search} />
      )}
      {error && <ErrorMessage message={error} onRetry={handleSearch} />}

      <FlatList
        data={results}
        renderItem={renderDealCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={[COLORS.primary]}
            tintColor={COLORS.primary}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={
          !isLoading && isSubmitted ? (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>{UI_TEXT.empty.search}</Text>
            </View>
          ) : null
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: SIZES.md,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SIZES.md,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: COLORS.divider,
    borderRadius: SIZES.radiusMd,
    backgroundColor: COLORS.white,
    padding: SIZES.md,
    fontSize: SIZES.fontMd,
  },
  searchButton: {
    marginLeft: SIZES.sm,
    backgroundColor: COLORS.primary,
    borderRadius: SIZES.radiusMd,
    paddingHorizontal: SIZES.md,
    paddingVertical: 12,
  },
  searchButtonText: {
    color: COLORS.white,
    fontWeight: 'bold',
  },
  listContent: {
    paddingBottom: SIZES.xl,
  },
  emptyContainer: {
    alignItems: 'center',
    marginTop: SIZES.xl,
  },
  emptyText: {
    color: COLORS.textSecondary,
    fontSize: SIZES.fontMd,
  },
  footerLoader: {
    alignItems: 'center',
    paddingVertical: SIZES.md,
  },
});

export default SearchScreen;
