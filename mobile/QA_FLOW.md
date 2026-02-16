# 모바일 QA 핵심 플로우 & 실패 시나리오 체크리스트 (실기기 1회 Smoke)

목표: Android/iOS 실제 기기에서 핵심 화면을 한 번 통과하면서, 실패 시나리오별 복원 동선을 로그로 남긴다.

## 0-1) 필수 도구/환경 검증 체크

### 공통

```bash
node -v
npm -v
yarn -v                        # 설치되어 있으면 선택
npx react-native --version
npx react-native doctor
```

### Android

```bash
echo $JAVA_HOME
java -version
adb --version
adb devices
echo $ANDROID_HOME
ls "$ANDROID_HOME"
```

`npx react-native doctor`에서 확인해야 할 핵심 항목:

- JDK >=17 <=20
- Android Studio
- Gradle/SDK manager
- adb 연결 상태

### iOS (macOS only)

```bash
xcodebuild -version
xcrun --find xcodebuild
xcodebuild -showsdks
which pod && pod --version
ios-deploy -V
```

### 실패 시 바로 점검할 항목(기기 실행 전)

- Android: `adb devices`에서 기기 상태가 `device`인지
- iOS: `xcodebuild -showsdks`에서 iOS SDK 보임 + Xcode 기기 신뢰
- Metro: `npx react-native start --reset-cache` 실행 가능 여부

## 0) 실행 준비 및 공통 로그 수집

- 프로젝트 기준: `cd mobile && npm install`
- 환경 변수:
  - 백엔드 기본 주소: `http://localhost:8000`
  - Android 실기기 접근 주소: `http://<PC_LAN_IP>:8000` (예: `http://192.168.0.10:8000`)
  - `mobile/src/services/api.js`의 `DEV_HOST`가 위 주소와 일치하는지 확인
- 로그 저장 디렉터리:
  - `mkdir -p mobile/qa-logs`
  - 로그 이름 예시: `mobile/qa-logs/<platform>-smoke-YYYYMMDD-HHMMSS.log`
- 앱 실행 전 공통 실행 로그
  ```bash
  cd mobile
  npm run start -- --reset-cache --host 0.0.0.0 > qa-logs/metro-YYYYMMDD-HHMMSS.log 2>&1 &
  ```

## 1) Android 1회 Smoke

1. 기기 준비: USB 디버깅 ON, 화면 잠금 해제
2. 기기 확인:
   - `adb devices`
3. 네트워크 경유 포트 포워딩(권장):
   - `adb -s <android_device_id> reverse tcp:8000 tcp:8000`
4. 로그 캐치 시작:
   ```bash
   LOG_FILE=mobile/qa-logs/android-smoke-$(date +%Y%m%d-%H%M%S).log
   adb -s <android_device_id> logcat -v time ReactNativeJS:V ReactNative:V JS:V NativeModules:V *:S \
     | tee "${LOG_FILE}"
   ```
5. 앱 실행:
   - `npm run android -- --deviceId <android_device_id>`
6. 아래 시나리오를 순차 진행

## 2) iOS 1회 Smoke

1. 기기/개발자 계정 등록, 앱 빌드 허용
2. Xcode에서 기기 연결 확인
3. iOS 로그 수집:
   - `idevicesyslog > mobile/qa-logs/ios-smoke-YYYYMMDD-HHMMSS.log` (libimobiledevice 설치 시)
   - 또는 Xcode `Devices and Simulators > Open Console` → 로그 캡처/내보내기
4. 앱 실행:
   - `npm run ios -- --device "<iOS 디바이스명>"`
5. 아래 시나리오를 순차 진행

## 3) 실패 분기별 시나리오

### A. 인증 (`LoginScreen`)

1. 네트워크 OFF 상태에서 로그인/회원가입 시도
   - 기대: 실패 토스트/에러 라벨이 공통 copy로 표시  
     (`로그인에 실패했습니다.` / `회원가입에 실패했습니다.`)
2. 입력 누락(이메일/비밀번호 미입력)
   - 기대: 입력 오류 Alert 노출 (`이메일과 비밀번호를 입력해 주세요.`)
3. 정상 로그인
   - 기대: 인증 성공 시 홈 탭 진입

### B. 홈 (`HomeScreen`)

1. 초기 진입/로딩 실패(백엔드 중단 또는 네트워크 OFF)
   - 기대: 공통 에러 메시지 + `다시 시도`
2. 딜 북마크 토글 실패
   - 기대: 즉시 토스트 노출, 북마크 상태 롤백/유지
3. 리스트 하단 추가 요청 실패
   - 기대: 로딩 정지 + 에러 상태 노출

### C. 검색 (`SearchScreen`)

1. 검색어 미입력/2자 미만
   - 기대: 공통 에러 문구: `검색어를 입력해 주세요.` / `검색어는 2자 이상 입력해 주세요.`
2. 검색 API 실패(네트워크 OFF)
   - 기대: `검색에 실패했습니다.` 계열의 ErrorMessage + `다시 시도`
3. 북마크 토글 실패(검색 결과 카드)
   - 기대: 즉시 토스트 + 카드 상태 동기화 실패 시 복원

### D. 북마크 (`BookmarksScreen`)

1. 북마크 목록 조회 실패
   - 기대: 목록 에러 화면 + 재시도 동작
2. 북마크 삭제 실패
   - 기대: 실패 토스트(`북마크 삭제 실패` 계열) + 삭제 목록 복원
3. 빈 상태
   - 기대: 빈 상태 문구 + 가이드 노출

### E. 키워드 (`KeywordsScreen`)

1. 키워드 목록 조회 실패
   - 기대: 기존 목록 있을 때 인라인 에러 배너, 없을 때 중앙 에러 화면
2. 중복 키워드 입력
   - 기대: `이미 등록된 키워드입니다.` 인라인 배너 + 즉시 재시도 버튼 비활성
3. 키워드 제한 초과 추가
   - 기대: `키워드는 최대 20개까지만 등록할 수 있습니다.`
4. 추가/삭제/토글 실패
   - 기대: 인라인 에러 + 재시도 + 현재 액션 상태 보존
5. 네트워크 복구 재시도
   - 기대: 재시도 후 실제 반영, 상태 일관성 유지

### F. 알림 (`NotificationsScreen`)

1. 알림 목록 조회 실패
   - 기대: 에러 배너/중앙 에러 + 재시도
2. 읽음 처리/클릭 처리 실패
   - 기대: 즉시 롤백(읽음 상태/클릭 상태 복구), 인라인 에러 + 재시도
3. 전체 읽음 실패
   - 기대: `전체 읽음 처리 실패` + 상태 롤백 및 재동기화
4. 빈 상태
   - 기대: 빈 메시지/힌트 노출

## 4) 실패 로그 기록 템플릿 (실행 즉시 작성)

### 기본 메모
- 실행 일시:
- 플랫폼/기기:
- 시나리오 빌드:
- 백엔드 상태:
- 네트워크 상태 전환 횟수:
- 실패 복구 횟수:

### 시나리오별 판정

| ID | 시나리오 | 기대 동작(Pass 기준) | 실제 결과 | Pass/Fail |
| --- | --- | --- | --- | --- |
| F01 | 로그인/회원가입 네트워크 오프라인 | 공통 에러 copy 표시 후 앱 안정 유지 |  |  |
| F02 | 홈 북마크 토글 실패 | 즉시 토스트 + 롤백 |  |  |
| F03 | 검색 API 실패 | 검색 실패 copy + 재시도 동작 |  |  |
| F04 | 북마크 삭제 실패 | 실패 토스트 + 삭제 목록 복원 |  |  |
| F05 | 키워드 중복/초과 | 하드 실패 문구 + 인라인 배너 |  |  |
| F06 | 키워드 추가/삭제/토글 실패 | 인라인 배너 + 재시도 + 상태 유지 |  |  |
| F07 | 알림 읽음 처리 실패 | 롤백 + 배너 + 재시도 |  |  |

### 로그 추출 체크
- Android: `grep -nE "(네트워크|오류|Error|failed|북마크|키워드|알림|ReactNativeJS)" <로그파일>`
- iOS: 저장한 Xcode/idevicesyslog 로그에서 동일 키워드 확인

## 5) 실패 복원/회귀 체크 (종합)

1. 실패/복구 동작 시 앱 크래시 없음
2. 토글/북마크/알림 상태는 실패 시 원복 후 재시도 성공 시 정상 복구
3. 화면별 에러 메시지 복합 케이스가 한글 공통 copy 정책을 유지
4. `읽음 카운트`는 0 미만으로 내려가지 않음
5. 앱 종료 후 토스트/배너 스택 누적 없음
