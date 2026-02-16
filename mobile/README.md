# DealMoa Mobile App

딜모아 모바일 앱 - React Native로 구현된 핫딜 모음 서비스

## 📱 기능

### ✅ 구현 완료
- **홈 피드**: 핫딜 카드 스타일 피드 (무한 스크롤, Pull-to-Refresh)
- **딜 상세**: AI 요약, 가격 정보, 통계 표시
- **검색**: 키워드 기반 딜 검색
- **북마크**: 즐겨찾는 딜 저장 및 관리
- **키워드 관리**: 포함/제외 키워드 CRUD
- **알림 내역**: 알림 조회 및 읽음 처리
- **설정**: 사용자 정보, 앱 정보
- **상태 관리**: Context API (Auth, Deals)
- **API 연동**: Backend REST API 완전 지원

### 🚧 향후 추가 예정
- FCM 디바이스 등록 및 실제 푸시 알림 수신
- 성능 최적화 (이미지 캐싱, 스켈레톤, 오프라인 캐시)

## 🏗️ 프로젝트 구조

```
mobile/
├── App.js                      # 앱 진입점
├── index.js                    # AppRegistry 진입점
├── app.json                    # 앱 이름/등록명
├── package.json                # 의존성 설정
├── android/                    # Android 네이티브 프로젝트
├── ios/                        # iOS 네이티브 프로젝트
├── babel.config.js             # Babel 설정
├── metro.config.js             # Metro 설정
├── .eslintrc.js                # ESLint 설정
├── .watchmanconfig             # Watchman 설정
├── .gitignore                  # Git 무시 목록
│
├── src/
│   ├── components/             # 재사용 가능한 컴포넌트
│   │   ├── DealCard.js         # 딜 카드 (Instagram 스타일)
│   │   ├── SourceBadge.js      # 출처 뱃지
│   │   ├── PriceTag.js         # 가격 태그 (할인율, 신호)
│   │   ├── LoadingSpinner.js   # 로딩 인디케이터
│   │   └── ErrorMessage.js     # 에러 메시지
│   │
│   ├── screens/                # 화면 컴포넌트
│   │   ├── HomeScreen.js       # 홈 피드
│   │   ├── DealDetailScreen.js # 딜 상세
│   │   ├── BookmarksScreen.js  # 북마크 목록
│   │   ├── SettingsScreen.js   # 설정
│   │   ├── SearchScreen.js     # 검색
│   │   ├── KeywordsScreen.js   # 키워드 관리
│   │   ├── NotificationsScreen.js # 알림 내역
│   │   └── LoginScreen.js      # 로그인/회원가입
│   │
│   ├── navigation/             # 네비게이션 설정
│   │   ├── AppNavigator.js     # 메인 네비게이터
│   │   └── MainTabNavigator.js # 탭 네비게이터
│   │
│   ├── store/                  # 상태 관리 (Context API)
│   │   ├── AuthContext.js      # 인증 상태
│   │   └── DealsContext.js     # 딜 데이터 상태
│   │
│   ├── services/               # 외부 서비스
│   │   └── api.js              # Backend API 클라이언트
│   │
│   └── utils/                  # 유틸리티 함수
│       ├── constants.js        # 상수 (색상, 크기, 화면명)
│       └── helpers.js          # 헬퍼 함수 (포맷, 변환)
```

## 🧩 네이티브 폴더 복구 가이드

`mobile` 실행 기준 네이티브 경로는 다음과 같습니다.

- `mobile/android`
- `mobile/ios`
- `mobile/index.js`
- `mobile/app.json`
- `mobile/babel.config.js`
- `mobile/metro.config.js`
- `mobile/.eslintrc.js`
- `mobile/.watchmanconfig`
- `mobile/.gitignore`

### 네이티브 파일 복구(템플릿 기반)

네이티브 폴더가 손상/삭제된 경우 아래 순서로 로컬 템플릿에서 복구할 수 있습니다.

```bash
cd /path/to/claude-code-1/mobile

# 1) 커스텀 변경 보호(선택)
mkdir -p .restore-backup/$(date +%Y%m%d_%H%M%S)
[ -d android ] && mv android .restore-backup/$(date +%Y%m%d_%H%M%S)/
[ -d ios ] && mv ios .restore-backup/$(date +%Y%m%d_%H%M%S)/

# 2) 템플릿 기반 복구
cp -R node_modules/react-native/template/android .
cp -R node_modules/react-native/template/ios .
cp node_modules/react-native/template/index.js .
cp node_modules/react-native/template/app.json .
cp node_modules/react-native/template/babel.config.js .
cp node_modules/react-native/template/metro.config.js .
cp node_modules/react-native/template/_eslintrc.js .eslintrc.js
cp node_modules/react-native/template/_watchmanconfig .watchmanconfig
cp node_modules/react-native/template/_gitignore .gitignore

# 3) RN 0.73+ 권장 파일
cp node_modules/react-native/template/ios/_xcode.env ios/.xcode.env
```

※ 앱명/패키지명은 프로젝트 정책과 맞게 후속 네이티브 파일(`android/app/src/main/java/...`, `android/app/build.gradle`, `ios/HelloWorld.xcodeproj`, `ios/HelloWorld/AppDelegate.mm`, `mobile/app.json`)을 정리해야 합니다.

## 🚀 시작하기

### 1. 의존성 설치

```bash
cd mobile
npm install
```

**iOS 추가 설정** (macOS만):
```bash
cd ios
pod install
cd ..
```

### 1-1. 실기기 실행 전 필수 체크리스트(필수 검증)

```bash
node -v
npm -v
cd /path/to/claude-code-1/mobile
npx react-native doctor
npx react-native run-android --no-packager --help >/dev/null
```

기대 결과:

- `node`, `npm`: 버전 출력
- `react-native doctor`: Android/iOS 진단 항목이 가능한 항목은 `✓`로 표시
- `run-android --help`: CLI 실행 에러 없이 종료 0

### 2. Backend 서버 시작

모바일 앱이 연결할 Backend API 서버를 먼저 시작해야 합니다:

```bash
cd ../backend
./venv/bin/uvicorn app.main:app --reload
```

서버 주소: http://localhost:8000

### 3. 앱 실행

**iOS** (macOS only):
```bash
npm run ios
```

**Android**:
```bash
npm run android
```

### 4. 실기기 실행 체크

실기기(Android/iOS)에서는 `mobile/src/services/api.js`의 `DEV_HOST`를 기기에서 접근 가능한 서버 주소로 맞춰야 합니다.

- Android 에뮬레이터: `10.0.2.2`
- Android 실기기: `10.0.2.2` + `adb reverse` 또는 백엔드 LAN IP(예: `192.168.0.10`)
- iOS 실기기: 백엔드 LAN IP(예: `192.168.0.10`)

> 실기기 실행 전 `mobile/QA_FLOW.md`의 “실행 전 체크”와 “실기기 초기화” 항목을 먼저 따라가면 더 안정적입니다.

## 📦 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| react-native | 0.73.2 | React Native 프레임워크 |
| @react-navigation/native | ^6.1.9 | 네비게이션 |
| @react-navigation/stack | ^6.3.20 | 스택 네비게이션 |
| @react-navigation/bottom-tabs | ^6.5.11 | 하단 탭 네비게이션 |
| axios | ^1.6.5 | HTTP 클라이언트 |
| @react-native-async-storage/async-storage | ^1.21.0 | 로컬 저장소 |
| react-native-safe-area-context | ^4.8.2 | Safe Area 지원 |
| react-native-screens | ^3.29.0 | 네이티브 화면 최적화 |
| react-native-push-notification | ^8.1.1 | 푸시 알림 |

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: #FF6B6B (빨강 계열)
- **Secondary**: #4ECDC4 (청록 계열)
- **Success**: #4CAF50 (초록)
- **Warning**: #FFC107 (노랑)
- **Error**: #F44336 (빨강)

### 타이포그래피
- **Title**: 24-28px, Bold
- **Heading**: 20px, Bold
- **Body**: 15px, Regular
- **Caption**: 11-13px, Regular

### 간격
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px

## 🔌 API 연동

### API 베이스 URL 설정

`src/services/api.js` 파일에서 설정:

```javascript
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'  // 개발 환경
  : 'https://api.dealmoa.app/api/v1';  // 프로덕션
```

### 주요 API 함수

```javascript
import { dealsAPI, authAPI, bookmarksAPI } from './services/api';

// 딜 목록 조회
const deals = await dealsAPI.getDeals({ page: 1, page_size: 20 });

// 딜 상세 조회
const deal = await dealsAPI.getDealDetail(dealId);

// AI 요약 조회
const summary = await dealsAPI.getDealSummary(dealId);

// 로그인
const response = await authAPI.login(email, password);

// 북마크 추가
await bookmarksAPI.addBookmark(dealId);
```

## 🧪 테스트

```bash
npm test
```

### 핵심 화면 QA

실제 기기(Android/iOS) 기준 플로우는 별도 체크리스트로 정리했습니다.

```bash
cd mobile
cat QA_FLOW.md
```

## 🐛 트러블슈팅

### "Unable to resolve module"
```bash
# Metro bundler 캐시 초기화
npm start -- --reset-cache
```

### iOS 빌드 실패
```bash
cd ios
pod deintegrate
pod install
cd ..
```

### Android 빌드 실패
```bash
cd android
./gradlew clean
cd ..
```

## 📝 다음 단계

1. **푸시 권한/토큰 연동**: 디바이스 토큰 등록/해지 흐름 완성
2. **알림 스크린 고도화**: 알림 내 딜 바로 열기/읽음 상태 UX 정교화
3. **이미지 캐싱**: react-native-fast-image 추가
4. **애니메이션**: react-native-reanimated 추가

## ✅ 정합성 체크

- 북마크 해제는 북마크 ID 기반 엔드포인트(`/bookmarks/{id}`)로 통일했습니다.
- 앱 진입 전환은 인증 상태 기준(AppNavigator)으로만 제어합니다.
- 검색 화면에서 북마크 토글과 상세 이동을 동일한 데이터 계약으로 통합했습니다.

## 📄 라이선스

Private - DealMoa Project
