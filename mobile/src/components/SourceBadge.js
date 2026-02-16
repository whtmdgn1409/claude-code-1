/**
 * SourceBadge Component
 * Displays colored badge for deal source
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SIZES, SOURCE_NAMES } from '../utils/constants';
import { getSourceColor } from '../utils/helpers';

const SourceBadge = ({ source }) => {
  if (!source) return null;

  const backgroundColor = source.color_code || getSourceColor(source.name);
  const displayName = source.display_name || SOURCE_NAMES[source.name] || source.name;

  return (
    <View style={[styles.badge, { backgroundColor }]}>
      <Text style={styles.text}>{displayName}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: SIZES.sm,
    paddingVertical: 4,
    borderRadius: SIZES.radiusSm,
  },
  text: {
    fontSize: SIZES.fontXs,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});

export default SourceBadge;
