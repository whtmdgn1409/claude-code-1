/**
 * PriceTag Component
 * Displays price with discount and signal indicator
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import { formatPrice, calculateDiscount, getPriceSignal } from '../utils/helpers';

const PriceTag = ({ price, originalPrice, signal }) => {
  const discount = calculateDiscount(originalPrice, price);
  const priceSignal = getPriceSignal(signal);

  return (
    <View style={styles.container}>
      {/* Current Price */}
      <View style={styles.priceRow}>
        {signal && (
          <Text style={styles.signal}>{priceSignal.emoji}</Text>
        )}
        <Text style={styles.currentPrice}>{formatPrice(price)}</Text>
        {discount > 0 && (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>{discount}%</Text>
          </View>
        )}
      </View>

      {/* Original Price (if discounted) */}
      {originalPrice && originalPrice > price && (
        <Text style={styles.originalPrice}>
          {formatPrice(originalPrice)}
        </Text>
      )}

      {/* Price Signal Label */}
      {signal && (
        <Text style={[styles.signalLabel, { color: priceSignal.color }]}>
          {priceSignal.label}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'column',
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  signal: {
    fontSize: SIZES.fontLg,
    marginRight: SIZES.xs,
  },
  currentPrice: {
    fontSize: SIZES.fontXl,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  discountBadge: {
    backgroundColor: COLORS.error,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 2,
    borderRadius: SIZES.radiusSm,
    marginLeft: SIZES.sm,
  },
  discountText: {
    fontSize: SIZES.fontSm,
    fontWeight: 'bold',
    color: COLORS.white,
  },
  originalPrice: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    textDecorationLine: 'line-through',
  },
  signalLabel: {
    fontSize: SIZES.fontXs,
    fontWeight: 'bold',
    marginTop: 2,
  },
});

export default PriceTag;
