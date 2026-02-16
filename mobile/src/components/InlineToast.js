import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text, View } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';

const toastTypeStyles = {
  error: {
    backgroundColor: '#FFF1F2',
    borderColor: COLORS.error,
    textColor: COLORS.error,
  },
  success: {
    backgroundColor: '#E8F5E9',
    borderColor: COLORS.success,
    textColor: COLORS.success,
  },
};

const InlineToast = ({
  visible,
  message,
  type = 'error',
  duration = 1800,
  onHide,
  trigger = 0,
}) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const translateAnim = useRef(new Animated.Value(-10)).current;
  const hideTimer = useRef(null);
  const theme = toastTypeStyles[type] || toastTypeStyles.error;

  useEffect(() => {
    if (!visible || !message) {
      return undefined;
    }

    fadeAnim.setValue(0);
    translateAnim.setValue(-10);
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 180,
        useNativeDriver: true,
      }),
      Animated.timing(translateAnim, {
        toValue: 0,
        duration: 180,
        useNativeDriver: true,
      }),
    ]).start();

    hideTimer.current = setTimeout(() => {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 180,
          useNativeDriver: true,
        }),
        Animated.timing(translateAnim, {
          toValue: -10,
          duration: 180,
          useNativeDriver: true,
        }),
      ]).start(() => {
        onHide?.();
      });
    }, duration);

    return () => {
      if (hideTimer.current) {
        clearTimeout(hideTimer.current);
      }
    };
  }, [duration, fadeAnim, message, onHide, trigger, translateAnim, visible]);

  if (!visible) {
    return null;
  }

  return (
    <View style={styles.container} pointerEvents="none">
      <Animated.View
        style={[
          styles.toast,
          {
            backgroundColor: theme.backgroundColor,
            borderColor: theme.borderColor,
            opacity: fadeAnim,
            transform: [{ translateY: translateAnim }],
          },
        ]}
      >
        <Text style={[styles.message, { color: theme.textColor }]}>{message}</Text>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 12,
    left: SIZES.md,
    right: SIZES.md,
    alignItems: 'center',
    zIndex: 999,
  },
  toast: {
    paddingHorizontal: SIZES.md,
    paddingVertical: SIZES.sm,
    borderRadius: SIZES.radiusMd,
    borderWidth: 1,
    borderLeftWidth: 4,
    minHeight: 40,
    justifyContent: 'center',
  },
  message: {
    fontSize: SIZES.fontSm,
    fontWeight: '500',
  },
});

export default InlineToast;
