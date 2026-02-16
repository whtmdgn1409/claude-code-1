/**
 * Keywords Screen
 * Manage inclusion/exclusion keywords for push matching.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Switch,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  StyleSheet,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES } from '../utils/constants';
import { keywordsAPI } from '../services/api';
import { UI_TEXT, resolveRequestError } from '../utils/copy';
import InlineErrorBanner from '../components/InlineErrorBanner';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const getErrorMessage = (error, fallback) => {
  const fallbackMessage = resolveRequestError(error, fallback, {
    byType: {
      network: UI_TEXT.errors.network.unreachable,
      validation: fallback,
      server: UI_TEXT.errors.server.unavailable,
    },
  });
      const detail = error?.response?.data?.detail;
  const normalized = typeof detail === 'string' ? detail.toLowerCase() : '';

  if (
    normalized.includes('already exists') ||
    normalized.includes('already added') ||
    normalized.includes('duplicate')
  ) {
    return UI_TEXT.errors.keyword.duplicate;
  }

  if (normalized.includes('maximum') && normalized.includes('keyword')) {
    return UI_TEXT.errors.keyword.maxCount;
  }

  return fallbackMessage;
};

const KeywordsScreen = () => {
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [isInclusion, setIsInclusion] = useState(true);
  const [loading, setLoading] = useState(false);
  const [pendingActions, setPendingActions] = useState({});
  const [errorState, setErrorState] = useState(null);
  const [isAdding, setIsAdding] = useState(false);

  const keywordInputRef = useRef(null);
  const hasKeywordsRef = useRef(false);

  useEffect(() => {
    hasKeywordsRef.current = keywords.length > 0;
  }, [keywords.length]);

  const isItemPending = (itemId) => Boolean(pendingActions[itemId]);

  const setPending = (itemId, action) => {
    setPendingActions((prev) => ({
      ...prev,
      [itemId]: action,
    }));
  };

  const clearPending = (itemId) => {
    setPendingActions((prev) => {
      const next = { ...prev };
      delete next[itemId];
      return next;
    });
  };

  const isKeywordDuplicate = (candidate) => {
    const normalized = candidate.trim().toLowerCase();
    return keywords.some(
      (item) => item.keyword?.trim().toLowerCase() === normalized,
    );
  };

  const fetchKeywords = useCallback(async () => {
    try {
      setLoading(true);
      const response = await keywordsAPI.getKeywords();
      setKeywords(response.keywords || []);
      hasKeywordsRef.current = Boolean((response.keywords || []).length);
      setErrorState(null);
    } catch (err) {
      setErrorState({
        message: getErrorMessage(err, UI_TEXT.errors.keyword.loadFail),
        onRetry: fetchKeywords,
        inline: hasKeywordsRef.current,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchKeywords();
    }, [fetchKeywords]),
  );

  const handleAdd = async (keywordOverride, inclusionOverride) => {
    const keyword = (keywordOverride ?? newKeyword).trim();
    const targetType = inclusionOverride ?? isInclusion;

    if (!keyword) {
      setErrorState({
        message: UI_TEXT.errors.keyword.required,
        onRetry: null,
        inline: true,
      });
      return;
    }

    if (isKeywordDuplicate(keyword)) {
      setErrorState({
        message: UI_TEXT.errors.keyword.duplicate,
        onRetry: null,
        inline: true,
      });
      return;
    }

    const tempId = `pending-${Date.now()}`;
    const optimisticKeyword = {
      id: tempId,
      keyword,
      is_inclusion: targetType,
      is_active: true,
    };

    setErrorState(null);
    setNewKeyword('');
    setIsAdding(true);
    setPending(tempId, 'add');
    setKeywords((prev) => [optimisticKeyword, ...prev]);

    try {
      const response = await keywordsAPI.addKeyword(keyword, targetType);
      setKeywords((prev) =>
        prev.map((item) => (item.id === tempId ? response : item)),
      );
    } catch (err) {
      const message = getErrorMessage(err, UI_TEXT.errors.keyword.addFail);
      setErrorState({
        message: `${UI_TEXT.errors.keyword.addFailWithReason}: ${message}`,
        onRetry: () => handleAdd(keyword, targetType),
        inline: true,
      });
      setKeywords((prev) => prev.filter((item) => item.id !== tempId));
    } finally {
      setIsAdding(false);
      clearPending(tempId);
    }
  };

  const handleDelete = async (itemId) => {
    const target = keywords.find((item) => item.id === itemId);
    if (!target || isItemPending(itemId)) {
      return;
    }

    const restoreIndex = keywords.findIndex((item) => item.id === itemId);

    setErrorState(null);
    setPending(itemId, 'delete');
    setKeywords((prev) => prev.filter((item) => item.id !== itemId));

    try {
      await keywordsAPI.deleteKeyword(itemId);
    } catch (err) {
      const message = getErrorMessage(err, UI_TEXT.errors.keyword.deleteFail);
      setErrorState({
        message: `${UI_TEXT.errors.keyword.deleteFailWithReason}: ${message}`,
        onRetry: () => handleDelete(itemId),
        inline: true,
      });
      setKeywords((prev) => {
        const next = [...prev];
        const safeIndex = Math.min(Math.max(restoreIndex, 0), next.length);
        next.splice(safeIndex, 0, target);
        return next;
      });
    } finally {
      clearPending(itemId);
    }
  };

  const handleToggleActive = async (item) => {
    if (isItemPending(item.id)) {
      return;
    }

    const nextActive = !item.is_active;
    const rollback = { ...item };

    setPending(item.id, 'toggle');
    setErrorState(null);
    setKeywords((prev) =>
      prev.map((value) =>
        value.id === item.id ? { ...value, is_active: nextActive } : value,
      ),
    );

    try {
      const response = await keywordsAPI.updateKeyword(item.id, {
        is_active: nextActive,
      });
      if (response) {
        setKeywords((prev) =>
          prev.map((value) =>
            value.id === item.id
              ? {
                  ...value,
                  is_active: response.is_active,
                  is_inclusion: response.is_inclusion,
                }
              : value,
          ),
        );
      }
    } catch (err) {
      const message = getErrorMessage(err, UI_TEXT.errors.keyword.statusFail);
      setErrorState({
        message: `${UI_TEXT.errors.keyword.statusFailWithReason}: ${message}`,
        onRetry: () => handleToggleActive(rollback),
        inline: true,
      });
      setKeywords((prev) =>
        prev.map((value) =>
          value.id === item.id
            ? { ...value, is_active: rollback.is_active }
            : value,
        ),
      );
    } finally {
      clearPending(item.id);
    }
  };

  const renderKeywordItem = ({ item }) => {
    const pending = isItemPending(item.id);
    const isTogglePending = pending && pendingActions[item.id] === 'toggle';
    const isDeletePending = pending && pendingActions[item.id] === 'delete';
    const keywordType = item.is_inclusion
      ? UI_TEXT.a11y.keyword.typeInclusion
      : UI_TEXT.a11y.keyword.typeExclusion;

    return (
      <View
        style={[
          styles.row,
          !item.is_active && styles.rowInactive,
          pending && styles.rowPending,
        ]}
        accessibilityRole="summary"
        accessibilityLabel={`${item.keyword} ${keywordType} ${UI_TEXT.a11y.keyword.item}`}
      >
        <View style={styles.keywordRowLeft}>
          <Text
            style={[styles.keywordText, !item.is_active && styles.keywordTextInactive]}
            numberOfLines={1}
          >
            {item.keyword}
          </Text>
        <View style={styles.badgeRow}>
            <Text
              style={[
                styles.badge,
                item.is_inclusion ? styles.badgeInclude : styles.badgeExclude,
              ]}
            >
              {keywordType}
            </Text>
            {!item.is_active && (
              <Text style={styles.badgeInactive}>
                {UI_TEXT.a11y.keyword.inactiveLabel}
              </Text>
            )}
          </View>
        </View>

        <View style={styles.actions}>
          <Switch
            value={item.is_active}
            onValueChange={() => handleToggleActive(item)}
            disabled={pending}
            trackColor={{ false: COLORS.gray300, true: COLORS.primary }}
            thumbColor={COLORS.white}
            ios_backgroundColor={COLORS.gray300}
            accessibilityRole="switch"
            accessibilityLabel={`${item.keyword} ${keywordType} ${UI_TEXT.a11y.keyword.toggleLabel}`}
            accessibilityHint={item.is_active ? UI_TEXT.a11y.keyword.toggleOffHint : UI_TEXT.a11y.keyword.toggleOnHint}
            accessibilityValue={{
              text: item.is_active ? UI_TEXT.a11y.keyword.typeValueOn : UI_TEXT.a11y.keyword.typeValueOff,
              checked: item.is_active,
            }}
            accessibilityState={{
              checked: item.is_active,
              disabled: pending,
            }}
          />
          <TouchableOpacity
            onPress={() => handleDelete(item.id)}
            disabled={pending}
            style={styles.deleteBtn}
            accessibilityRole="button"
            accessibilityLabel={`${item.keyword} ${keywordType} ${UI_TEXT.a11y.keyword.deleteLabel}`}
            accessibilityHint={UI_TEXT.a11y.keyword.deleteHint}
            accessibilityState={{ disabled: pending }}
          >
            <Text
              style={[
                styles.deleteText,
                pending && styles.deleteTextDisabled,
              ]}
            >
              {isDeletePending ? UI_TEXT.actions.deleteProgress : UI_TEXT.actions.delete}
            </Text>
          </TouchableOpacity>
          {isTogglePending && (
            <ActivityIndicator
              size="small"
              color={COLORS.primary}
              style={styles.pendingIndicator}
              accessibilityLabel={`${item.keyword} ${UI_TEXT.a11y.keyword.processingHint}`}
            />
          )}
        </View>
      </View>
    );
  };

  const focusKeywordInput = () => {
    keywordInputRef.current?.focus();
  };

  const renderEmptyState = () => {
    if (loading) {
      return null;
    }

    if (errorState && !errorState.inline) {
      return (
        <ErrorMessage
          message={errorState.message}
          onRetry={errorState.onRetry}
        />
      );
    }

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyTitle}>{UI_TEXT.empty.keywords}</Text>
        <Text style={styles.emptyHint}>
          {UI_TEXT.empty.keywordHint}
        </Text>
        <TouchableOpacity
          style={styles.emptyAction}
          onPress={focusKeywordInput}
          accessibilityRole="button"
          accessibilityLabel={UI_TEXT.a11y.keyword.emptyActionLabel}
          accessibilityHint={UI_TEXT.a11y.keyword.emptyActionHint}
        >
          <Text style={styles.emptyActionText}>{UI_TEXT.empty.keywordCta}</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>키워드 관리</Text>

      <View style={styles.form}>
        <TextInput
          ref={keywordInputRef}
          style={styles.input}
          value={newKeyword}
          onChangeText={setNewKeyword}
          placeholder={UI_TEXT.empty.keywordInputPlaceholder}
          editable={!isAdding}
          autoCorrect={false}
          autoCapitalize="none"
          returnKeyType="done"
          onSubmitEditing={() => handleAdd()}
          accessibilityLabel={UI_TEXT.a11y.keyword.inputLabel}
          accessibilityHint={UI_TEXT.a11y.keyword.inputHint}
        />
        <TouchableOpacity
          onPress={() => handleAdd()}
          disabled={isAdding}
          style={[styles.addBtn, isAdding && styles.addBtnDisabled]}
          accessibilityRole="button"
          accessibilityLabel={UI_TEXT.a11y.keyword.addButtonLabel}
          accessibilityHint={UI_TEXT.a11y.keyword.addButtonHint}
        >
          {isAdding ? (
            <ActivityIndicator size="small" color={COLORS.white} />
          ) : (
            <Text style={styles.addBtnText}>{UI_TEXT.actions.add}</Text>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.typeRow}>
        <TouchableOpacity
          style={[
            styles.typeBtn,
            isInclusion && styles.typeBtnActive,
          ]}
          onPress={() => setIsInclusion(true)}
          accessibilityRole="button"
          accessibilityState={{ selected: isInclusion }}
          accessibilityLabel={UI_TEXT.a11y.keyword.typeInclusionLabel}
          accessibilityHint={UI_TEXT.a11y.keyword.typeButtonHint}
        >
          <Text
            style={[
              styles.typeBtnText,
              isInclusion && styles.typeBtnTextActive,
            ]}
          >
            {UI_TEXT.a11y.keyword.typeInclusionLabel}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.typeBtn,
            !isInclusion && styles.typeBtnActive,
          ]}
          onPress={() => setIsInclusion(false)}
          accessibilityRole="button"
          accessibilityState={{ selected: !isInclusion }}
          accessibilityLabel={UI_TEXT.a11y.keyword.typeExclusionLabel}
          accessibilityHint={UI_TEXT.a11y.keyword.typeButtonHint}
        >
          <Text
            style={[
              styles.typeBtnText,
              !isInclusion && styles.typeBtnTextActive,
            ]}
          >
            {UI_TEXT.a11y.keyword.typeExclusionLabel}
          </Text>
        </TouchableOpacity>
      </View>

      {errorState && errorState.inline && (
        <InlineErrorBanner
          message={errorState.message}
          onRetry={errorState.onRetry}
        />
      )}

      {loading ? (
        <LoadingSpinner message={UI_TEXT.loading.keywords} />
      ) : (
        <FlatList
          data={keywords}
          renderItem={renderKeywordItem}
          keyExtractor={(item) => `${item.id}`}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={renderEmptyState}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: SIZES.md,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: SIZES.md,
    color: COLORS.textPrimary,
  },
  form: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SIZES.md,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: COLORS.divider,
    backgroundColor: COLORS.white,
    borderRadius: SIZES.radiusMd,
    padding: SIZES.md,
    marginRight: SIZES.sm,
  },
  addBtn: {
    backgroundColor: COLORS.primary,
    borderRadius: SIZES.radiusMd,
    paddingHorizontal: SIZES.md,
    paddingVertical: 12,
    minWidth: 72,
    alignItems: 'center',
  },
  addBtnDisabled: {
    backgroundColor: COLORS.gray400,
  },
  addBtnText: {
    color: COLORS.white,
    fontWeight: 'bold',
  },
  typeRow: {
    flexDirection: 'row',
    marginBottom: SIZES.md,
  },
  typeBtn: {
    flex: 1,
    borderWidth: 1,
    borderColor: COLORS.divider,
    backgroundColor: COLORS.white,
    paddingVertical: 10,
    alignItems: 'center',
    marginRight: SIZES.xs,
    borderRadius: SIZES.radiusMd,
  },
  typeBtnActive: {
    borderColor: COLORS.primary,
    backgroundColor: `${COLORS.primary}15`,
  },
  typeBtnText: {
    color: COLORS.textSecondary,
  },
  typeBtnTextActive: {
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  listContent: {
    paddingBottom: SIZES.xl,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SIZES.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  rowInactive: {
    backgroundColor: `${COLORS.gray200}40`,
    opacity: 0.85,
  },
  rowPending: {
    opacity: 0.65,
  },
  keywordRowLeft: {
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
    marginRight: SIZES.sm,
  },
  keywordText: {
    color: COLORS.textPrimary,
    fontSize: SIZES.fontMd,
    marginBottom: 4,
  },
  keywordTextInactive: {
    color: COLORS.textDisabled,
    textDecorationLine: 'line-through',
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badge: {
    marginRight: SIZES.sm,
    fontSize: SIZES.fontXs,
    color: COLORS.primary,
    fontWeight: 'bold',
    backgroundColor: `${COLORS.primary}15`,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 2,
    borderRadius: SIZES.radiusSm,
    overflow: 'hidden',
  },
  badgeInclude: {
    color: COLORS.primary,
    backgroundColor: `${COLORS.primary}20`,
  },
  badgeExclude: {
    color: COLORS.info,
    backgroundColor: `${COLORS.info}20`,
  },
  badgeInactive: {
    color: COLORS.textSecondary,
    fontSize: SIZES.fontXs,
    fontWeight: 'bold',
    backgroundColor: `${COLORS.gray300}80`,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 2,
    borderRadius: SIZES.radiusSm,
    overflow: 'hidden',
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  deleteBtn: {
    marginLeft: SIZES.md,
    marginRight: SIZES.xs,
    paddingHorizontal: SIZES.sm,
    paddingVertical: 4,
  },
  deleteText: {
    color: COLORS.error,
    fontSize: SIZES.fontSm,
  },
  deleteTextDisabled: {
    color: COLORS.textDisabled,
  },
  pendingIndicator: {
    marginLeft: SIZES.sm,
  },
  emptyContainer: {
    flex: 1,
    paddingTop: SIZES.xl,
    alignItems: 'center',
  },
  emptyTitle: {
    color: COLORS.textPrimary,
    fontSize: SIZES.fontLg,
    fontWeight: '700',
    marginBottom: SIZES.sm,
  },
  emptyHint: {
    color: COLORS.textSecondary,
    fontSize: SIZES.fontMd,
    textAlign: 'center',
    marginBottom: SIZES.md,
    paddingHorizontal: SIZES.md,
  },
  emptyAction: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: SIZES.lg,
    paddingVertical: SIZES.sm,
    borderRadius: SIZES.radiusMd,
  },
  emptyActionText: {
    color: COLORS.white,
    fontWeight: '700',
  },
});

export default KeywordsScreen;
