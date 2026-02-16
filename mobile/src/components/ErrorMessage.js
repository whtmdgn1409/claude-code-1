/**
 * ErrorMessage Component
 * Displays error message with retry button
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import { UI_TEXT } from '../utils/copy';

const ErrorMessage = ({
  message = UI_TEXT.errors.unexpected,
  retryLabel = UI_TEXT.actions.retry,
  retryLabelAccessibility = UI_TEXT.a11y.retryError,
  retryHint = UI_TEXT.a11y.retryHint,
  onRetry,
}) => {
  return (
    <View
      style={styles.container}
      accessibilityRole="alert"
      accessibilityLiveRegion="assertive"
    >
      <Text style={styles.emoji}>😕</Text>
      <Text style={styles.message}>{message}</Text>
      {onRetry && (
        <TouchableOpacity
          style={styles.button}
          onPress={onRetry}
          accessibilityRole="button"
          accessibilityLabel={retryLabelAccessibility}
          accessibilityHint={retryHint}
        >
          <Text style={styles.buttonText}>{retryLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: SIZES.xl,
  },
  emoji: {
    fontSize: 48,
    marginBottom: SIZES.md,
  },
  message: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: SIZES.lg,
  },
  button: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: SIZES.lg,
    paddingVertical: SIZES.md,
    borderRadius: SIZES.radiusMd,
  },
  buttonText: {
    fontSize: SIZES.fontMd,
    fontWeight: 'bold',
    color: COLORS.white,
  },
});

export default ErrorMessage;
