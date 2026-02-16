/**
 * SettingsScreen
 * User settings and keyword management
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useAuth } from '../store/AuthContext';
import { COLORS, SIZES, SCREEN_NAMES } from '../utils/constants';
import { UI_TEXT } from '../utils/copy';

const SettingsScreen = ({ navigation }) => {
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      UI_TEXT.errors.auth.logoutTitle,
      UI_TEXT.errors.auth.logoutMessage,
      [
        { text: UI_TEXT.errors.auth.cancel, style: 'cancel' },
        {
          text: UI_TEXT.errors.auth.logoutTitle,
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{UI_TEXT.settings.title}</Text>
      </View>

      {/* User Info Section */}
      {isAuthenticated && user && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{UI_TEXT.settings.sectionTitleUser}</Text>
          <View style={styles.userCard}>
            <Text style={styles.userName}>{user.username || user.email}</Text>
            <Text style={styles.userEmail}>{user.email}</Text>
          </View>
        </View>
      )}

      {/* Keywords Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{UI_TEXT.settings.sectionTitleNotifications}</Text>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate(SCREEN_NAMES.KEYWORDS)}
        >
          <Text style={styles.menuItemText}>{UI_TEXT.settings.keywordMenu}</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate(SCREEN_NAMES.NOTIFICATIONS)}
        >
          <Text style={styles.menuItemText}>{UI_TEXT.settings.notificationMenu}</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
      </View>

      {/* App Info Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{UI_TEXT.settings.sectionTitleApp}</Text>

        <View style={styles.menuItem}>
          <Text style={styles.menuItemText}>{UI_TEXT.settings.versionLabel}</Text>
          <Text style={styles.menuItemValue}>0.1.0</Text>
        </View>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>{UI_TEXT.settings.termsMenu}</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>{UI_TEXT.settings.privacyMenu}</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>{UI_TEXT.settings.openSourceLicenseMenu}</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
      </View>

      {/* Account Section */}
      {isAuthenticated && (
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
          >
            <Text style={styles.logoutButtonText}>{UI_TEXT.errors.auth.logoutTitle}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>{UI_TEXT.settings.footerText}</Text>
        <Text style={styles.footerCopyright}>{UI_TEXT.settings.footerCopyright}</Text>
      </View>
    </ScrollView>
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
  section: {
    marginTop: SIZES.lg,
    backgroundColor: COLORS.white,
    paddingHorizontal: SIZES.md,
  },
  sectionTitle: {
    fontSize: SIZES.fontSm,
    fontWeight: 'bold',
    color: COLORS.textSecondary,
    paddingTop: SIZES.md,
    paddingBottom: SIZES.sm,
    textTransform: 'uppercase',
  },
  userCard: {
    paddingVertical: SIZES.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  userName: {
    fontSize: SIZES.fontLg,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SIZES.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  menuItemText: {
    fontSize: SIZES.fontMd,
    color: COLORS.textPrimary,
  },
  menuItemValue: {
    fontSize: SIZES.fontMd,
    color: COLORS.textSecondary,
  },
  menuItemArrow: {
    fontSize: 24,
    color: COLORS.textSecondary,
  },
  logoutButton: {
    paddingVertical: SIZES.md,
    alignItems: 'center',
  },
  logoutButtonText: {
    fontSize: SIZES.fontMd,
    color: COLORS.error,
    fontWeight: '600',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: SIZES.xl,
  },
  footerText: {
    fontSize: SIZES.fontSm,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  footerCopyright: {
    fontSize: SIZES.fontXs,
    color: COLORS.textDisabled,
  },
});

export default SettingsScreen;
