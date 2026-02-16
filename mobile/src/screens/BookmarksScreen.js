/**
 * BookmarksScreen
 * Displays user's bookmarked deals
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  FlatList,
  Text,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { COLORS, SIZES, SCREEN_NAMES } from '../utils/constants';
import { bookmarksAPI } from '../services/api';
import { useDeals } from '../store/DealsContext';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import DealCard from '../components/DealCard';
import InlineToast from '../components/InlineToast';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const BookmarksScreen = ({ navigation }) => {
  const [bookmarks, setBookmarks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const { toggleBookmark } = useDeals();
  const [toast, setToast] = useState({
    visible: false,
    message: '',
    type: 'error',
    trigger: 0,
  });

  const resolveBookmarkError = (error, fallback = UI_TEXT.errors.bookmark.deleteFail) =>
    resolveRequestError(error, fallback, {
      byType: {
        network: UI_TEXT.errors.network.unreachable,
        validation: fallback,
        server: UI_TEXT.errors.server.unavailable,
      },
    });

  const showBookmarkError = (errorOrMessage = UI_TEXT.errors.bookmark.deleteFail) => {
    const message =
      typeof errorOrMessage === 'string'
        ? errorOrMessage
        : resolveBookmarkError(errorOrMessage, UI_TEXT.errors.bookmark.deleteFail);

    setToast({
      visible: true,
      message,
      type: 'error',
      trigger: Date.now(),
    });
  };

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await bookmarksAPI.getBookmarks();
      setBookmarks(response.bookmarks || []);
    } catch (err) {
      setError(
        resolveRequestError(err, UI_TEXT.errors.bookmark.fetchFail, {
          byType: {
            network: UI_TEXT.errors.network.unreachable,
            validation: UI_TEXT.errors.bookmark.fetchFail,
            server: UI_TEXT.errors.server.unavailable,
          },
        }),
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchBookmarks();
    setRefreshing(false);
  };

  const handleDealPress = (deal) => {
    navigation.navigate(SCREEN_NAMES.DEAL_DETAIL, { deal });
  };

  const handleRemoveBookmark = async (item) => {
    if (!item?.deal?.id) {
      showBookmarkError(UI_TEXT.errors.bookmark.invalidTarget);
      return;
    }

    try {
      const result = await toggleBookmark(item.deal.id, true, item.id);
      if (result?.success) {
        setBookmarks((prev) => prev.filter((b) => b.id !== item.id));
        return;
      }

      throw new Error(result?.error || UI_TEXT.errors.bookmark.deleteFail);
    } catch (error) {
      showBookmarkError(error);
    }
  };

  const hideToast = () => {
    setToast((prev) => ({ ...prev, visible: false }));
  };

  const renderEmpty = () => {
    if (isLoading) return <LoadingSpinner message={UI_TEXT.loading.bookmarks} />;
    if (error) return <ErrorMessage message={error} onRetry={fetchBookmarks} />;
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>⭐️</Text>
        <Text style={styles.emptyMessage}>{UI_TEXT.empty.bookmarks}</Text>
        <Text style={styles.emptyHint}>{UI_TEXT.empty.bookmarksHint}</Text>
      </View>
    );
  };

  const renderDealCard = ({ item }) => {
    if (!item?.deal) return null;

    return (
      <DealCard
        deal={{ ...item.deal, is_bookmarked: true }}
        onPress={() => handleDealPress(item.deal)}
        onBookmark={() => handleRemoveBookmark(item)}
        onBookmarkError={(error) => showBookmarkError(error)}
      />
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

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>⭐️ 내 북마크</Text>
      </View>

      {/* Bookmarks List */}
      <FlatList
        data={bookmarks}
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
        ListEmptyComponent={renderEmpty}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    padding: SIZES.md,
    backgroundColor: COLORS.white,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  headerTitle: {
    fontSize: SIZES.fontXl,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  listContent: {
    paddingVertical: SIZES.sm,
    flexGrow: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SIZES.xxl,
  },
  emptyText: {
    fontSize: 64,
    marginBottom: SIZES.md,
  },
  emptyMessage: {
    fontSize: SIZES.fontLg,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: SIZES.sm,
  },
  emptyHint: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
  },
});

export default BookmarksScreen;
