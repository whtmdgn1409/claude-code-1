/**
 * Login / Signup Screen
 * Basic authentication entry for demo and quick recovery.
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { useAuth } from '../store/AuthContext';
import { COLORS, SIZES } from '../utils/constants';
import { UI_TEXT } from '../utils/copy';

const LoginScreen = () => {
  const [mode, setMode] = useState('login'); // login | signup
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const { login, signup, error, isLoading, clearError } = useAuth();

  const isSignup = mode === 'signup';

  const handleSubmit = async () => {
    clearError?.();
    if (!email || !password) {
      Alert.alert(
        UI_TEXT.errors.auth.inputErrorTitle,
        UI_TEXT.errors.auth.inputErrorMessage,
      );
      return;
    }
    if (password.length < UI_TEXT.auth.passwordMinLength) {
      Alert.alert(
        UI_TEXT.errors.auth.inputErrorTitle,
        UI_TEXT.errors.auth.inputPasswordErrorMessage,
      );
      return;
    }

    const result = isSignup
      ? await signup(email, password, username || email.split('@')[0])
      : await login(email, password);

    if (result?.success) {
      // AppNavigator will automatically switch to authenticated flow
      // when user state is set.
      return;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>{UI_TEXT.auth.title}</Text>
        <Text style={styles.subtitle}>{UI_TEXT.auth.subtitle}</Text>

        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder={UI_TEXT.auth.emailPlaceholder}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder={UI_TEXT.auth.passwordPlaceholder}
          secureTextEntry
        />
        {isSignup && (
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            placeholder={UI_TEXT.auth.usernamePlaceholder}
            autoCapitalize="none"
          />
        )}

        {!!error && <Text style={styles.errorText}>{error}</Text>}

        <TouchableOpacity
          style={[styles.button, isLoading && styles.buttonDisabled]}
          onPress={handleSubmit}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            {isLoading ? UI_TEXT.actions.addProgress : (isSignup ? UI_TEXT.actions.signup : UI_TEXT.actions.login)}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setMode(isSignup ? 'login' : 'signup')}
          style={styles.switchButton}
        >
          <Text style={styles.switchText}>
            {isSignup
              ? UI_TEXT.auth.switchToLoginText
              : UI_TEXT.auth.switchToSignupText}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    flex: 1,
    padding: SIZES.lg,
    justifyContent: 'center',
  },
  title: {
    fontSize: 40,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: SIZES.xs,
    color: COLORS.textPrimary,
  },
  subtitle: {
    fontSize: SIZES.fontMd,
    textAlign: 'center',
    color: COLORS.textSecondary,
    marginBottom: SIZES.xl,
  },
  input: {
    borderWidth: 1,
    borderColor: COLORS.divider,
    backgroundColor: COLORS.white,
    borderRadius: SIZES.radiusMd,
    paddingHorizontal: SIZES.md,
    paddingVertical: 12,
    marginBottom: SIZES.md,
    fontSize: SIZES.fontMd,
  },
  button: {
    backgroundColor: COLORS.primary,
    borderRadius: SIZES.radiusMd,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: SIZES.sm,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: COLORS.white,
    fontWeight: 'bold',
    fontSize: SIZES.fontMd,
  },
  switchButton: {
    marginTop: SIZES.lg,
    alignSelf: 'center',
  },
  switchText: {
    color: COLORS.primary,
    fontSize: SIZES.fontMd,
  },
  errorText: {
    color: COLORS.error,
    marginBottom: SIZES.md,
  },
});

export default LoginScreen;
