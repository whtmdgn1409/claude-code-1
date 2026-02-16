/**
 * Notifications Screen
 * Show notification list and mark-as-read actions.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES, SCREEN_NAMES } from '../utils/constants';
import { formatRelativeTime } from '../utils/helpers';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import { notificationsAPI } from '../services/api';
import InlineErrorBanner from '../components/InlineErrorBanner';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const PAGE_SIZE = 30;

const NotificationsScreen = ({ navigation }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorState, setErrorState] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [pendingReads, setPendingReads] = useState(new Set());
  const [markAllInFlight, setMarkAllInFlight] = useState(false);
  const hasNotificationsRef = useRef(false);

  useEffect(() => {
    hasNotificationsRef.current = items.length > 0;
  }, [items.length]);

  const addPendingReadId = useCallback((id) => {
    setPendingReads((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  const removePendingReadId = useCallback((id) => {
    setPendingReads((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const syncUnreadCount = useCallback(async () => {
    try {
      const countResponse = await notificationsAPI.getUnreadCount();
      setUnreadCount(countResponse.unread_count || 0);
    } catch {
      // 동기화 실패가 앱 UX를 깨뜨리지 않도록 조용히 무시
    }
  }, []);

  const fetchNotifications = useCallback(
    async ({ showLoader = true, silent = false } = {}) => {
      try {
        if (showLoader) {
          setLoading(true);
        }
        const response = await notificationsAPI.getNotifications(1, PAGE_SIZE);
        setItems(response.notifications || []);
        setUnreadCount(response.unread_count || 0);
        if (!silent) {
          setErrorState(null);
        }
      } catch (error) {
        if (!silent) {
        setErrorState({
            message: resolveRequestError(
              error,
              UI_TEXT.errors.notification.loadFail,
              {
                byType: {
                  network: UI_TEXT.errors.network.unreachable,
                  validation: UI_TEXT.errors.notification.loadFail,
                  server: UI_TEXT.errors.server.unavailable,
                },
              },
            ),
            onRetry: () => fetchNotifications(),
            inline: hasNotificationsRef.current,
          });
        }
      } finally {
        if (showLoader) {
          setLoading(false);
        }
      }
    },
    [],
  );

  useFocusEffect(
    useCallback(() => {
      fetchNotifications();
    }, [fetchNotifications])
  );

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    setErrorState(null);
    await fetchNotifications({ showLoader: false });
    setRefreshing(false);
  }, [fetchNotifications]);

  const handleRead = useCallback(async (id, dealId) => {
    if (pendingReads.has(id)) {
      return;
    }

    const target = items.find((item) => item.id === id);
    if (!target) {
      return;
    }

    const shouldMarkRead = !target.read_at;
    const shouldMarkClicked = Boolean(dealId);
    const now = new Date().toISOString();
    const snapshot = {
      read_at: target.read_at,
      clicked_at: target.clicked_at,
    };

    setErrorState(null);
    addPendingReadId(id);

    if (shouldMarkRead || shouldMarkClicked) {
      setItems((prev) =>
        prev.map((item) =>
          item.id === id
            ? {
                ...item,
                read_at: shouldMarkRead ? now : item.read_at,
                clicked_at: shouldMarkClicked ? now : item.clicked_at,
              }
            : item,
        ),
      );
      if (shouldMarkRead) {
        setUnreadCount((prev) => Math.max(prev - 1, 0));
      }
    }

    try {
      if (dealId) {
        await notificationsAPI.markAsClicked(id);
      } else {
        const response = await notificationsAPI.markAsRead(id);
        if (typeof response?.updated === 'number' && response.updated > 0) {
          // 서버 기준으로 정확히 동기화 (이미 읽은 알림 재탭 이슈 완화)
          setUnreadCount((prev) => Math.max(prev - response.updated, 0));
        }
      }

      if (dealId) {
        navigation?.navigate(SCREEN_NAMES.DEAL_DETAIL, { dealId });
      }
      await syncUnreadCount();
    } catch (error) {
      setItems((prev) =>
        prev.map((item) =>
          item.id === id
            ? {
                ...item,
                read_at: snapshot.read_at,
                clicked_at: snapshot.clicked_at,
              }
            : item,
        ),
      );
      if (shouldMarkRead) {
        setUnreadCount((prev) => prev + 1);
      }
      setErrorState({
        message: resolveRequestError(
          error,
          UI_TEXT.errors.notification.markReadFail,
          {
            byType: {
              network: UI_TEXT.errors.network.unreachable,
              validation: UI_TEXT.errors.notification.markReadFail,
              server: UI_TEXT.errors.server.unavailable,
            },
          },
        ),
        onRetry: () => handleRead(id, dealId),
        inline: true,
      });
    } finally {
      removePendingReadId(id);
    }
  }, [
    addPendingReadId,
    items,
    pendingReads,
    removePendingReadId,
    navigation,
    syncUnreadCount,
  ]);

  const handleReadAll = useCallback(async () => {
    if (markAllInFlight || items.length === 0 || unreadCount === 0) {
      return;
    }

    const now = new Date().toISOString();
    const prevItems = items;
    const prevUnreadCount = unreadCount;

    setErrorState(null);
    setMarkAllInFlight(true);
    setItems((prev) =>
      prev.map((item) =>
        item.read_at ? item : { ...item, read_at: now },
      ),
    );
    setUnreadCount(0);

    try {
      const response = await notificationsAPI.markAllAsRead();
      if (typeof response?.updated === 'number') {
        setUnreadCount((prev) => Math.max(prev - response.updated, 0));
      }
      await syncUnreadCount();
    } catch (error) {
      setItems(prevItems);
      setUnreadCount(prevUnreadCount);
      setErrorState({
        message: resolveRequestError(
          error,
          UI_TEXT.errors.notification.markAllFail,
          {
            byType: {
              network: UI_TEXT.errors.network.unreachable,
              validation: UI_TEXT.errors.notification.markAllFail,
              server: UI_TEXT.errors.server.unavailable,
            },
          },
        ),
        onRetry: handleReadAll,
        inline: true,
      });
    } finally {
      setMarkAllInFlight(false);
    }
  }, [items, markAllInFlight, unreadCount, syncUnreadCount]);

  const renderItem = ({ item }) => {
    const isUnread = !item.read_at;
    const isUpdating = pendingReads.has(item.id);
    const readState = isUnread
      ? UI_TEXT.a11y.notification.unreadItemLabel
      : UI_TEXT.a11y.notification.readItemLabel;
    const stateHint = isUnread
      ? UI_TEXT.a11y.notification.itemUnreadHint
      : UI_TEXT.a11y.notification.itemReadHint;

    return (
      <TouchableOpacity
        onPress={() => handleRead(item.id, item.deal_id)}
        disabled={isUpdating}
        accessibilityRole="button"
        accessibilityLabel={`${UI_TEXT.a11y.notification.itemLabel} ${readState}`}
        accessibilityHint={`${item.title}. ${stateHint}`}
        accessibilityState={{ disabled: isUpdating, selected: isUnread }}
        style={[
          styles.item,
          isUnread && styles.unreadItem,
          isUpdating && styles.itemDisabled,
        ]}
      >
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.body}>{item.body}</Text>

        <View style={styles.metaRow}>
          {isUnread ? <Text style={styles.unreadBadge}>NEW</Text> : null}
          <Text style={styles.meta}>
            {formatRelativeTime(item.created_at)}
          </Text>
          {isUpdating ? (
            <ActivityIndicator
              style={styles.itemSpinner}
              size="small"
              color={COLORS.primary}
              accessibilityLabel={UI_TEXT.a11y.notification.markInProgress}
            />
          ) : null}
        </View>
      </TouchableOpacity>
    );
  };

  const renderEmpty = () => {
    if (loading || refreshing || (errorState && !errorState.inline)) return null;
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>🔔</Text>
        <Text style={styles.emptyMessage}>{UI_TEXT.empty.notifications}</Text>
        <Text style={styles.emptyHint}>{UI_TEXT.empty.notificationHint}</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>알림 내역</Text>
          {unreadCount > 0 ? (
            <Text style={styles.headerUnread}>미확인 {unreadCount}건</Text>
          ) : (
            <Text style={styles.headerUnreadDimmed}>모든 알림을 확인했습니다</Text>
          )}
        </View>

        <TouchableOpacity
          onPress={handleReadAll}
          disabled={items.length === 0 || unreadCount === 0 || markAllInFlight}
          accessibilityRole="button"
          accessibilityLabel={UI_TEXT.a11y.notification.markAllLabel}
          accessibilityHint={
            items.length === 0 || unreadCount === 0 || markAllInFlight
              ? UI_TEXT.a11y.notification.markAllDisabledHint
              : UI_TEXT.a11y.notification.markAllHint
          }
          accessibilityState={{
            disabled: items.length === 0 || unreadCount === 0 || markAllInFlight,
          }}
        >
          <Text
            style={[
              styles.headerAction,
              (items.length === 0 || unreadCount === 0 || markAllInFlight) &&
                styles.headerActionDisabled,
            ]}
          >
            {markAllInFlight
              ? UI_TEXT.actions.allReadProgress
              : UI_TEXT.actions.allRead}
          </Text>
        </TouchableOpacity>
      </View>

      {loading && <LoadingSpinner message={UI_TEXT.loading.notifications} />}
      {errorState && !errorState.inline && (
        <ErrorMessage
          message={errorState.message}
          onRetry={errorState.onRetry}
        />
      )}
      {errorState && errorState.inline && (
        <InlineErrorBanner
          message={errorState.message}
          onRetry={errorState.onRetry}
          style={styles.inlineError}
        />
      )}

      <FlatList
        data={items}
        renderItem={renderItem}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: SIZES.fontXl,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  headerUnread: {
    marginTop: 2,
    color: COLORS.error,
    fontSize: SIZES.fontXs,
  },
  headerUnreadDimmed: {
    marginTop: 2,
    color: COLORS.textDisabled,
    fontSize: SIZES.fontXs,
  },
  headerAction: {
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  headerActionDisabled: {
    color: COLORS.textDisabled,
  },
  item: {
    backgroundColor: COLORS.white,
    padding: SIZES.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
    minHeight: 88,
  },
  itemDisabled: {
    opacity: 0.65,
  },
  unreadItem: {
    backgroundColor: '#FFF8E1',
  },
  title: {
    fontSize: SIZES.fontMd,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 4,
  },
  body: {
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  metaRow: {
    marginTop: 2,
    flexDirection: 'row',
    alignItems: 'center',
  },
  meta: {
    color: COLORS.textDisabled,
    fontSize: SIZES.fontXs,
  },
  unreadBadge: {
    marginRight: 6,
    backgroundColor: COLORS.error,
    color: COLORS.white,
    fontSize: SIZES.fontXs,
    fontWeight: 'bold',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: SIZES.radiusSm,
    overflow: 'hidden',
  },
  itemSpinner: {
    marginLeft: 6,
  },
  listContent: {
    flexGrow: 1,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: SIZES.xl,
  },
  emptyIcon: {
    fontSize: 32,
    marginBottom: SIZES.md,
  },
  emptyMessage: {
    color: COLORS.textPrimary,
    fontSize: SIZES.fontMd,
    fontWeight: '600',
    marginBottom: SIZES.xs,
  },
  emptyHint: {
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  inlineError: {
    marginBottom: 0,
  },
});

export default NotificationsScreen;
