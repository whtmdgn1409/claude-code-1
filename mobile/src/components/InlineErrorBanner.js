import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import { UI_TEXT } from '../utils/copy';

const InlineErrorBanner = ({
  message,
  onRetry,
  retryLabel = UI_TEXT.actions.retry,
  retryLabelAccessibility = UI_TEXT.a11y.retryError,
  retryHint = UI_TEXT.a11y.retryHint,
  style,
  contentStyle,
}) => {
  if (!message) {
    return null;
  }

  return (
    <View
      style={[styles.container, style]}
      accessible
      accessibilityRole="alert"
      accessibilityLiveRegion="assertive"
    >
      <Text style={[styles.message, contentStyle]}>{message}</Text>
      {onRetry && (
        <TouchableOpacity
          style={styles.retryButton}
          onPress={onRetry}
          accessibilityLabel={`${retryLabelAccessibility}`}
          accessibilityHint={retryHint}
          accessibilityRole="button"
        >
          <Text style={styles.retryButtonText}>{retryLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderWidth: 1,
    borderColor: COLORS.error,
    backgroundColor: `${COLORS.error}15`,
    borderRadius: SIZES.radiusMd,
    padding: SIZES.md,
    margin: SIZES.md,
  },
  message: {
    color: COLORS.error,
    fontSize: SIZES.fontSm,
    marginBottom: SIZES.sm,
  },
  retryButton: {
    backgroundColor: COLORS.error,
    alignSelf: 'flex-start',
    paddingHorizontal: SIZES.md,
    paddingVertical: 6,
    borderRadius: SIZES.radiusSm,
  },
  retryButtonText: {
    color: COLORS.white,
    fontSize: SIZES.fontSm,
    fontWeight: '700',
  },
});

export default InlineErrorBanner;
