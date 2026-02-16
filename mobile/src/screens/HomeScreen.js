/**
 * HomeScreen
 * Main feed displaying hot deals in vertical scroll
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Text,
} from 'react-native';
import { useDeals } from '../store/DealsContext';
import { COLORS, SIZES, SCREEN_NAMES } from '../utils/constants';
import DealCard from '../components/DealCard';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import InlineToast from '../components/InlineToast';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const HomeScreen = ({ navigation }) => {
  const {
    deals,
    isLoading,
    error,
    pagination,
    fetchDeals,
    refreshDeals,
    loadMoreDeals,
    toggleBookmark,
  } = useDeals();

  const [refreshing, setRefreshing] = useState(false);
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

  // Initial load
  useEffect(() => {
    fetchDeals();
  }, []);

  // Pull to refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshDeals();
    setRefreshing(false);
  };

  // Load more (pagination)
  const handleLoadMore = () => {
    if (!isLoading && pagination.page < pagination.totalPages) {
      loadMoreDeals();
    }
  };

  // Navigate to deal detail
  const handleDealPress = (deal) => {
    navigation.navigate(SCREEN_NAMES.DEAL_DETAIL, { deal });
  };

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

  // Toggle bookmark
  const handleBookmark = async (deal) => {
    if (!deal?.id) {
      showBookmarkError(UI_TEXT.errors.deals.invalid);
      return;
    }

    try {
      const result = await toggleBookmark(deal.id, !!deal.is_bookmarked);
      if (!result?.success) {
        throw new Error(result?.error || UI_TEXT.errors.bookmark.actionFail);
      }
    } catch (error) {
      showBookmarkError(error);
    }
  };

  const hideToast = () => {
    setToast((prev) => ({ ...prev, visible: false }));
  };

  // Render deal card
  const renderDealCard = ({ item }) => (
    <DealCard
      deal={item}
      onPress={handleDealPress}
      onBookmark={handleBookmark}
      onBookmarkError={(error) => showBookmarkError(error)}
    />
  );

  // Render footer (loading more indicator)
  const renderFooter = () => {
    if (!isLoading || deals.length === 0) return null;
    return (
      <View style={styles.footer}>
        <LoadingSpinner size="small" message="" />
      </View>
    );
  };

  // Render empty state
  const renderEmpty = () => {
    if (isLoading) return <LoadingSpinner message={UI_TEXT.loading.deals} />;
    if (error) return <ErrorMessage message={error} onRetry={fetchDeals} />;
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>🔍</Text>
        <Text style={styles.emptyMessage}>{UI_TEXT.empty.deals}</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🔥 핫딜 피드</Text>
        <TouchableOpacity
          style={styles.searchButton}
          onPress={() => navigation.navigate(SCREEN_NAMES.SEARCH)}
        >
          <Text style={styles.searchIcon}>🔍</Text>
        </TouchableOpacity>
      </View>

        {/* Deals List */}
      <InlineToast
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        trigger={toast.trigger}
        onHide={hideToast}
      />

      <FlatList
        data={deals}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  searchButton: {
    padding: SIZES.sm,
  },
  searchIcon: {
    fontSize: 24,
  },
  listContent: {
    paddingVertical: SIZES.sm,
    flexGrow: 1,
  },
  footer: {
    paddingVertical: SIZES.lg,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SIZES.xxl,
  },
  emptyText: {
    fontSize: 48,
    marginBottom: SIZES.md,
  },
  emptyMessage: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
  },
});

export default HomeScreen;
