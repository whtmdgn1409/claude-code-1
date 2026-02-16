/**
 * DealCard Component
 * Instagram/Karrot Market style card for displaying deal information
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
} from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../utils/constants';
import {
  formatRelativeTime,
  getPriceSignal,
  isNewDeal,
} from '../utils/helpers';
import SourceBadge from './SourceBadge';
import PriceTag from './PriceTag';
import { UI_TEXT } from '../utils/copy';

const DealCard = ({
  deal,
  onPress,
  onBookmark,
  onBookmarkError,
}) => {
  const priceSignal = getPriceSignal(deal.price_signal);
  const isNew = isNewDeal(deal.published_at);
  const [isBookmarking, setIsBookmarking] = useState(false);

  const handleBookmarkPress = async () => {
    if (!onBookmark || isBookmarking) return;

    try {
      setIsBookmarking(true);
      await onBookmark(deal);
    } catch (error) {
      if (onBookmarkError) {
        onBookmarkError(error);
      }
    } finally {
      setIsBookmarking(false);
    }
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={() => onPress(deal)}
      activeOpacity={0.7}
    >
      {/* Thumbnail Image */}
      {deal.thumbnail_url && (
        <Image
          source={{ uri: deal.thumbnail_url }}
          style={styles.thumbnail}
          resizeMode="cover"
        />
      )}

      {/* Content */}
      <View style={styles.content}>
        {/* Header: Source Badge + Time */}
        <View style={styles.header}>
          <SourceBadge source={deal.source} />
          <Text style={styles.time}>{formatRelativeTime(deal.published_at)}</Text>
          {isNew && <View style={styles.newBadge}><Text style={styles.newText}>{UI_TEXT.dealDetail.newBadge}</Text></View>}
        </View>

        {/* Title */}
        <Text style={styles.title} numberOfLines={2}>
          {deal.title}
        </Text>

        {/* Price Section */}
        {deal.price && (
          <View style={styles.priceSection}>
            <PriceTag
              price={deal.price}
              originalPrice={deal.original_price}
              signal={deal.price_signal}
            />
          </View>
        )}

        {/* Mall Info */}
        {deal.mall_name && (
          <Text style={styles.mall}>{deal.mall_name}</Text>
        )}

        {/* Footer: Engagement Metrics */}
        <View style={styles.footer}>
          <View style={styles.metrics}>
            <Text style={styles.metric}>👍 {deal.upvotes}</Text>
            <Text style={styles.metric}>💬 {deal.comment_count}</Text>
            <Text style={styles.metric}>👁 {deal.view_count}</Text>
          </View>

          {/* Bookmark Button */}
          <TouchableOpacity
            onPress={handleBookmarkPress}
            style={styles.bookmarkButton}
            disabled={isBookmarking}
          >
            <Text style={styles.bookmarkIcon}>
              {isBookmarking ? '⏳' : deal.is_bookmarked ? '⭐️' : '☆'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* AI Summary Badge (if available) */}
        {deal.ai_summary && (
          <View style={styles.aiSummaryBadge}>
            <Text style={styles.aiSummaryText}>{UI_TEXT.dealDetail.aiSummaryBadge}</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.white,
    borderRadius: SIZES.radiusLg,
    marginHorizontal: SIZES.md,
    marginVertical: SIZES.sm,
    ...SHADOWS.md,
  },
  thumbnail: {
    width: '100%',
    height: 200,
    borderTopLeftRadius: SIZES.radiusLg,
    borderTopRightRadius: SIZES.radiusLg,
  },
  content: {
    padding: SIZES.md,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SIZES.sm,
  },
  time: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    marginLeft: SIZES.sm,
  },
  newBadge: {
    backgroundColor: COLORS.error,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 2,
    borderRadius: SIZES.radiusSm,
    marginLeft: SIZES.sm,
  },
  newText: {
    fontSize: SIZES.fontXs,
    color: COLORS.white,
    fontWeight: 'bold',
  },
  title: {
    fontSize: SIZES.fontLg,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: SIZES.sm,
    lineHeight: 24,
  },
  priceSection: {
    marginBottom: SIZES.sm,
  },
  mall: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    marginBottom: SIZES.sm,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: SIZES.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
  },
  metrics: {
    flexDirection: 'row',
    gap: SIZES.md,
  },
  metric: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
  },
  bookmarkButton: {
    padding: SIZES.xs,
  },
  bookmarkIcon: {
    fontSize: 20,
  },
  aiSummaryBadge: {
    position: 'absolute',
    top: SIZES.sm,
    right: SIZES.sm,
    backgroundColor: COLORS.primary,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 4,
    borderRadius: SIZES.radiusSm,
  },
  aiSummaryText: {
    fontSize: SIZES.fontXs,
    color: COLORS.white,
    fontWeight: 'bold',
  },
});

export default DealCard;
