export const UI_TEXT = {
  actions: {
    retry: '다시 시도',
    search: '검색',
    add: '추가',
    addProgress: '처리 중...',
    allRead: '전체 읽음',
    allReadProgress: '처리 중...',
    signup: '회원가입',
    login: '로그인',
    delete: '삭제',
    deleteProgress: '삭제 중...',
    logout: '로그아웃',
    appSummary: '요약을 생성 중...',
    openProduct: '🛒 상품 보러가기',
    openSource: '🔗 원문 보기',
  },
  app: {
    brand: 'DealMoa',
    tagline: '핫딜 모아보기',
  },
  loading: {
    default: '로딩 중...',
    deals: '딜을 불러오는 중...',
    search: '검색 중...',
    bookmarks: '북마크를 불러오는 중...',
    notifications: '알림을 불러오는 중...',
    keywords: '키워드를 불러오는 중...',
    deal: '딜 정보를 불러오는 중...',
    appInit: '앱 상태를 확인하는 중...',
    summary: '요약 생성 중...',
  },
  empty: {
    deals: '딜이 없습니다',
    search: '검색 결과가 없습니다',
    bookmarks: '북마크한 딜이 없습니다',
    bookmarksHint: '마음에 드는 딜을 저장해보세요',
    notifications: '새 알림이 없습니다',
    notificationHint: '딜 알림이 오면 여기에 표시됩니다',
    keywords: '아직 등록된 키워드가 없습니다',
    keywordHint: '포함/제외 키워드를 하나씩 추가하면 알림을 더 정확하게 받을 수 있어요.',
    keywordCta: '키워드 추가하기',
    keywordInputPlaceholder: '키워드 입력 (예: 맥북)',
    searchPlaceholder: '딜 검색 (예: RTX4090)',
  },
  errors: {
    unexpected: '요청을 처리하지 못했습니다.',
    network: {
      timeout: '요청이 너무 오래 걸립니다. 다시 시도해 주세요.',
      offline: '네트워크 상태를 확인해 주세요.',
      unreachable: '네트워크에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.',
    },
    validation: {
      request: '요청 형식이 올바르지 않습니다.',
      input: '입력값을 확인해 주세요.',
      conflict: '이미 처리된 요청입니다.',
      exists: '이미 등록된 항목입니다.',
    },
    server: {
      unavailable: '현재 서버에 일시적인 문제가 있습니다. 잠시 후 다시 시도해 주세요.',
      timeout: '요청 처리 중 서버 응답이 지연되었습니다.',
    },
    deals: {
      loadFail: '딜 목록을 불러오지 못했습니다.',
      invalid: '딜 정보를 확인할 수 없습니다.',
      notFound: '딜 정보를 불러오지 못했습니다.',
      unavailable: '딜을 불러올 수 없습니다.',
    },
    search: {
      required: '검색어를 입력해 주세요.',
      minLength: '검색어는 2자 이상 입력해 주세요.',
      fail: '검색에 실패했습니다.',
    },
    bookmark: {
      actionFail: '북마크 처리에 실패했습니다.',
      deleteFail: '북마크 삭제 실패',
      invalidTarget: '북마크 정보를 확인할 수 없습니다.',
      missingId: '북마크 ID를 찾지 못했습니다. 새로고침 후 다시 시도해 주세요.',
      fetchFail: '북마크를 불러오지 못했습니다.',
    },
    keyword: {
      loadFail: '키워드를 불러오지 못했습니다.',
      required: '키워드를 입력해 주세요.',
      duplicate: '이미 등록된 키워드입니다.',
      maxCount: '키워드는 최대 20개까지만 등록할 수 있습니다.',
      addFail: '키워드 추가에 실패했습니다.',
      deleteFail: '키워드 삭제에 실패했습니다.',
      statusFail: '상태 변경에 실패했습니다.',
      addFailWithReason: '키워드 추가 실패',
      deleteFailWithReason: '키워드 삭제 실패',
      statusFailWithReason: '키워드 상태 변경 실패',
    },
    notification: {
      loadFail: '알림을 불러오지 못했습니다.',
      markReadFail: '읽음 처리 실패',
      markAllFail: '전체 읽음 처리 실패',
    },
    auth: {
      loginFail: '로그인에 실패했습니다.',
      signupFail: '회원가입에 실패했습니다.',
      inputErrorTitle: '입력 오류',
      inputErrorMessage: '이메일과 비밀번호를 입력해 주세요.',
      inputPasswordErrorMessage: '비밀번호는 6자 이상 입력해 주세요.',
      logoutTitle: '로그아웃',
      logoutMessage: '정말 로그아웃 하시겠습니까?',
      cancel: '취소',
    },
  },
  auth: {
    title: 'DealMoa',
    subtitle: '핫딜 알림과 북마크를 시작하세요',
    emailPlaceholder: '이메일',
    passwordPlaceholder: '비밀번호 (최소 6자)',
    passwordMinLength: 6,
    usernamePlaceholder: '사용자명 (선택)',
    switchToLoginText: '이미 계정이 있나요? 로그인',
    switchToSignupText: '계정이 없나요? 회원가입',
  },
  settings: {
    title: '⚙️ 설정',
    sectionTitleUser: '사용자 정보',
    sectionTitleNotifications: '알림 설정',
    sectionTitleApp: '앱 정보',
    keywordMenu: '🔔 키워드 관리',
    notificationMenu: '📬 알림 내역',
    versionLabel: '버전',
    termsMenu: '이용약관',
    privacyMenu: '개인정보 처리방침',
    openSourceLicenseMenu: '오픈소스 라이선스',
    footerText: 'DealMoa - 핫딜 모아보기',
    footerCopyright: '© 2026 DealMoa',
  },
  dealDetail: {
    sectionTitleSource: '🏪 판매처',
    sectionTitleSummary: '🤖 AI 요약',
    sectionTitleDescription: '📝 상세 내용',
    sectionTitleStats: '📊 통계',
    aiSummaryBadge: '🤖 AI 요약',
    newBadge: 'NEW',
    statUpvotes: '추천',
    statComments: '댓글',
    statViews: '조회',
    statBookmarks: '북마크',
  },
  a11y: {
    retryError: '오류 다시 시도',
    retryHint: '실패한 작업을 다시 시도합니다',
    keyword: {
      item: '키워드 항목',
      typeInclusion: '포함',
      typeExclusion: '제외',
      typeValueOn: '켜짐',
      typeValueOff: '꺼짐',
      inactiveLabel: '비활성',
      badgeInclusion: '포함',
      badgeExclusion: '제외',
      inputLabel: '키워드 입력',
      inputHint: '등록할 키워드를 입력한 다음 추가 버튼을 눌러주세요.',
      inputEmptyHint: '새 키워드 입력창으로 이동합니다.',
      typeInclusionLabel: '포함 키워드',
      typeExclusionLabel: '제외 키워드',
      typeButtonHint: '해당 타입으로 새 키워드를 등록할 수 있습니다.',
      addButtonLabel: '키워드 추가',
      addButtonHint: '현재 선택한 타입으로 키워드를 추가합니다.',
      toggleLabel: '키워드 상태 토글',
      toggleOnHint: '현재 키워드가 비활성 상태입니다. 탭하면 키워드 알림이 다시 적용됩니다.',
      toggleOffHint: '현재 키워드가 활성 상태입니다. 탭하면 키워드 알림이 일시중지됩니다.',
      deleteLabel: '키워드 삭제',
      deleteHint: '키워드를 목록에서 제거합니다.',
      processingHint: '작업이 처리 중입니다.',
      emptyActionLabel: '키워드 입력하기',
      emptyActionHint: '키워드 입력창으로 이동해 바로 등록할 수 있습니다.',
    },
    notification: {
      itemLabel: '알림 항목',
      unreadItemLabel: '미확인 알림',
      readItemLabel: '읽은 알림',
      itemUnreadHint: '탭하면 읽음 처리 후 상세 화면으로 이동할 수 있습니다.',
      itemReadHint: '탭해도 이미 읽은 알림입니다.',
      markAllLabel: '전체 읽음 처리',
      markAllHint: '목록의 미확인 알림을 모두 읽음 처리합니다.',
      markAllDisabledHint: '현재 처리 가능한 미확인 알림이 없습니다.',
      markInProgress: '알림 처리 중입니다.',
    },
  },
};

const normalizeErrorStatus = (error) => {
  const status = error?.response?.status;
  if (!status || typeof status !== 'number') {
    return null;
  }
  return status;
};

const getErrorKind = (error) => {
  const code = error?.code;
  if (!error?.response) {
    if (code === 'ECONNABORTED' || code === 'ETIMEDOUT') {
      return 'network';
    }
    return 'network';
  }

  const status = normalizeErrorStatus(error);
  if (status >= 500) {
    return 'server';
  }
  if (status === 400 || status === 401 || status === 403 || status === 404 || status === 409 || status === 422) {
    return 'validation';
  }

  return 'unknown';
};

const getErrorMessageByKind = (error, fallback = UI_TEXT.errors.unexpected, overrideByKind = {}) => {
  if (error?.code === 'ECONNABORTED' || error?.code === 'ETIMEDOUT') {
    return UI_TEXT.errors.network.timeout;
  }

  const kind = getErrorKind(error);
  if (kind === 'network') {
    return overrideByKind.network || UI_TEXT.errors.network.unreachable;
  }
  if (kind === 'validation') {
    return overrideByKind.validation || UI_TEXT.errors.validation.request;
  }
  if (kind === 'server') {
    return overrideByKind.server || UI_TEXT.errors.server.unavailable;
  }

  return fallback;
};

const resolveErrorDetail = (detail) => {
  if (!detail) return null;

  if (typeof detail === 'string') {
    return detail.trim() || null;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item) return null;
        if (typeof item === 'string') return item.trim();
        if (typeof item === 'object') {
          return (
            item.detail ||
            item.message ||
            item.msg ||
            item.error ||
            null
          );
        }
        return null;
      })
      .filter(Boolean)
      .map((item) => (typeof item === 'string' ? item.trim() : ''))
      .filter(Boolean);

    return messages.length ? messages.join(', ') : null;
  }

  if (typeof detail === 'object') {
    return (
      detail.detail ||
      detail.message ||
      detail.error ||
      null
    );
  }

  return null;
};

const hasKoreanText = (value) =>
  typeof value === 'string' && /[가-힣]/.test(value);

export const resolveRequestError = (
  error,
  fallback = UI_TEXT.errors.unexpected,
  options = {},
) => {
  const detail = resolveErrorDetail(error?.response?.data?.detail);
  const overrideByKind = options.byType || {};

  if (detail && hasKoreanText(detail)) {
    return detail.trim();
  }
  if (typeof error?.message === 'string' && error.message.trim()) {
    const normalized = error.message.toLowerCase();
    if (hasKoreanText(error.message)) {
      return error.message.trim();
    }
    if (error?.code === 'ERR_BAD_RESPONSE' && normalized.includes('timeout')) {
      return UI_TEXT.errors.server.timeout;
    }
    if (normalized.includes('network')) {
      return UI_TEXT.errors.network.offline;
    }
  }

  if (!error?.response || (error?.code && !error.message)) {
    return getErrorMessageByKind(error, fallback, overrideByKind);
  }

  return getErrorMessageByKind(error, fallback, overrideByKind);
};

export const resolveRequestErrorInfo = (
  error,
  fallback = UI_TEXT.errors.unexpected,
  options = {},
) => ({
  kind: getErrorKind(error),
  message: resolveRequestError(error, fallback, options),
});
