/**
 * DealDetailScreen
 * Displays detailed information about a deal including AI summary
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Image,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import {
  formatRelativeTime,
} from '../utils/helpers';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import { dealsAPI } from '../services/api';
import SourceBadge from '../components/SourceBadge';
import PriceTag from '../components/PriceTag';
import LoadingSpinner from '../components/LoadingSpinner';

const DealDetailScreen = ({ route }) => {
  const initialDeal = route.params?.deal || null;
  const routeDealId = route.params?.dealId || route.params?.id;

  const [deal, setDeal] = useState(initialDeal);
  const [isLoading, setIsLoading] = useState(!initialDeal);
  const [error, setError] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    const fetchDeal = async () => {
      const targetId = routeDealId || initialDeal?.id;
      if (!targetId) {
        setError(UI_TEXT.errors.deals.unavailable);
        setIsLoading(false);
        return;
      }
      if (initialDeal && initialDeal.id === targetId) {
        setIsLoading(false);
        return;
      }

      try {
        setError(null);
        setIsLoading(true);
        const response = await dealsAPI.getDealDetail(targetId);
        setDeal(response);
      } catch (err) {
        setError(resolveRequestError(err, UI_TEXT.errors.deals.notFound));
      } finally {
        setIsLoading(false);
      }
    };

    fetchDeal();
  }, [initialDeal, routeDealId]);

  useEffect(() => {
    if (!deal?.id) return;

    const fetchAISummary = async () => {
      try {
        setLoadingSummary(true);
        const response = await dealsAPI.getDealSummary(deal.id);
        setAiSummary(response);
      } catch (err) {
        console.error('Failed to fetch AI summary:', err);
      } finally {
        setLoadingSummary(false);
      }
    };

    fetchAISummary();
  }, [deal?.id]);

  const handleRetryDeal = () => {
    if (!deal?.id && route.params) {
      setError(null);
      setIsLoading(true);
      const targetId = routeDealId || null;
      if (!targetId) {
        setError(UI_TEXT.errors.deals.unavailable);
        setIsLoading(false);
        return;
      }

      dealsAPI
        .getDealDetail(targetId)
        .then((response) => {
          setDeal(response);
          setError(null);
        })
        .catch((err) => {
          setError(resolveRequestError(err, UI_TEXT.errors.deals.notFound));
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };

  const handleOpenURL = async () => {
    if (!deal) return;

    const url = deal.mall_product_url || deal.url;
    if (!url) return;

    const supported = await Linking.canOpenURL(url);
    if (supported) {
      await Linking.openURL(url);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner message={UI_TEXT.loading.deal} />
      </View>
    );
  }

  if (error || !deal) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>{error || UI_TEXT.errors.deals.unavailable}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={handleRetryDeal}>
          <Text style={styles.retryText}>{UI_TEXT.actions.retry}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {deal.thumbnail_url && (
        <Image
          source={{ uri: deal.thumbnail_url }}
          style={styles.thumbnail}
          resizeMode="cover"
        />
      )}

      <View style={styles.content}>
        <View style={styles.header}>
          <SourceBadge source={deal.source} />
          <Text style={styles.time}>{formatRelativeTime(deal.published_at)}</Text>
        </View>

        <Text style={styles.title}>{deal.title}</Text>

        {deal.price && (
          <View style={styles.priceSection}>
            <PriceTag
              price={deal.price}
              originalPrice={deal.original_price}
              signal={deal.price_signal}
            />
          </View>
        )}

        {deal.mall_name && (
          <View style={styles.mallSection}>
            <Text style={styles.sectionTitle}>{UI_TEXT.dealDetail.sectionTitleSource}</Text>
            <Text style={styles.mallName}>{deal.mall_name}</Text>
          </View>
        )}

        {(aiSummary || loadingSummary) && (
          <View style={styles.summarySection}>
            <Text style={styles.sectionTitle}>{UI_TEXT.dealDetail.sectionTitleSummary}</Text>
            {loadingSummary ? (
              <LoadingSpinner size="small" message={UI_TEXT.loading.summary} />
            ) : aiSummary?.status === 'available' && aiSummary?.summary ? (
              <View style={styles.summaryBox}>
                <Text style={styles.summaryText}>{aiSummary.summary}</Text>
              </View>
            ) : aiSummary?.status === 'generating' ? (
              <Text style={styles.summaryPending}>{UI_TEXT.errors.dealDetail.summaryGenerating}</Text>
            ) : (
              <Text style={styles.summaryUnavailable}>{UI_TEXT.errors.dealDetail.summaryUnavailable}</Text>
            )}
          </View>
        )}

        {deal.content && (
          <View style={styles.descriptionSection}>
            <Text style={styles.sectionTitle}>{UI_TEXT.dealDetail.sectionTitleDescription}</Text>
            <Text style={styles.description}>{deal.content}</Text>
          </View>
        )}

        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>{UI_TEXT.dealDetail.sectionTitleStats}</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>{UI_TEXT.dealDetail.statUpvotes}</Text>
              <Text style={styles.statValue}>👍 {deal.upvotes}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>{UI_TEXT.dealDetail.statComments}</Text>
              <Text style={styles.statValue}>💬 {deal.comment_count}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>{UI_TEXT.dealDetail.statViews}</Text>
              <Text style={styles.statValue}>👁 {deal.view_count}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>{UI_TEXT.dealDetail.statBookmarks}</Text>
              <Text style={styles.statValue}>⭐️ {deal.bookmark_count}</Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.actionButton} onPress={handleOpenURL}>
          <Text style={styles.actionButtonText}>
            {deal.mall_product_url ? UI_TEXT.actions.openProduct : UI_TEXT.actions.openSource}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  thumbnail: {
    width: '100%',
    height: 300,
  },
  content: {
    padding: SIZES.md,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    padding: SIZES.md,
  },
  errorText: {
    color: COLORS.textSecondary,
    marginBottom: SIZES.md,
    textAlign: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SIZES.md,
  },
  time: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    marginLeft: SIZES.sm,
  },
  title: {
    fontSize: SIZES.fontXxl,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: SIZES.md,
    lineHeight: 32,
  },
  priceSection: {
    marginBottom: SIZES.lg,
    paddingBottom: SIZES.lg,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  mallSection: {
    marginBottom: SIZES.lg,
  },
  sectionTitle: {
    fontSize: SIZES.fontMd,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: SIZES.sm,
  },
  mallName: {
    fontSize: SIZES.fontLg,
    color: COLORS.textSecondary,
  },
  summarySection: {
    marginBottom: SIZES.lg,
  },
  summaryBox: {
    backgroundColor: COLORS.gray100,
    padding: SIZES.md,
    borderRadius: SIZES.radiusMd,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
  },
  summaryText: {
    fontSize: SIZES.fontMd,
    color: COLORS.textPrimary,
    lineHeight: 22,
  },
  summaryPending: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
    fontStyle: 'italic',
  },
  summaryUnavailable: {
    fontSize: SIZES.fontSm,
    color: COLORS.textDisabled,
  },
  descriptionSection: {
    marginBottom: SIZES.lg,
  },
  description: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
    lineHeight: 22,
  },
  statsSection: {
    marginBottom: SIZES.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  statValue: {
    fontSize: SIZES.fontMd,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  actionButton: {
    backgroundColor: COLORS.primary,
    padding: SIZES.md,
    borderRadius: SIZES.radiusMd,
    alignItems: 'center',
    marginTop: SIZES.md,
  },
  actionButtonText: {
    fontSize: SIZES.fontLg,
    fontWeight: 'bold',
    color: COLORS.white,
  },
  retryButton: {
    marginTop: SIZES.md,
    backgroundColor: COLORS.primary,
    paddingHorizontal: SIZES.md,
    paddingVertical: SIZES.sm,
    borderRadius: SIZES.radiusMd,
  },
  retryText: {
    color: COLORS.white,
    fontWeight: 'bold',
  },
});

export default DealDetailScreen;
