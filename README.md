# 딜모아 (DealMoa)

[기능 명세서] 핫딜 모음 및 알림 서비스

## 1. 개요

**목적**: 국내 주요 커뮤니티의 핫딜 정보를 실시간으로 수집하여 통합 제공하고, 사용자 맞춤형 키워드 알림을 제공함.

**타겟 유저**: 최저가 정보를 빠르게 얻고 싶은 20-40대 스마트 컨슈머.

**플랫폼**: 모바일 앱 (Android/iOS) 및 모바일 웹.

## 2. 상세 기능 명세

### A. 회원 및 개인화 (User)

| ID | 기능명 | 상세 설명 | 우선순위 |
|----|--------|-----------|----------|
| U-01 | 소셜 로그인 | 카카오, 구글, 애플 로그인 연동 (복잡한 가입 절차 제거) | High |
| U-02 | 프로필 설정 | 닉네임, 성별, 연령대 (10대~60대) 선택 (선택 정보) | Mid |
| U-03 | 관심 키워드 설정 | 알림 받을 키워드 등록/수정/삭제 (최대 20개)<br>예: 아이패드, 햇반, 특가 | High |
| U-04 | 제외 키워드 설정 | 알림에서 제외할 키워드 등록 (NOT 조건)<br>예: 아이패드 등록 시 케이스, 필름 제외 | High |
| U-05 | 찜(북마크) | 나중에 볼 상품 저장 및 모아보기 | Mid |

### B. 핫딜 리스트 및 상세 (View)

| ID | 기능명 | 상세 설명 | 우선순위 |
|----|--------|-----------|----------|
| V-01 | 통합 리스트 | 전체 커뮤니티 핫딜을 최신순/인기순(Hot Level)으로 정렬하여 노출 | High |
| V-02 | Hot Level 표시 | 추천수, 댓글수, 조회수 급상승 데이터를 기반으로 🔥, 🌡️ 아이콘 및 온도 표시 | High |
| V-03 | 카테고리 필터 | 디지털/가전, 식품, 의류, 생활용품 등 카테고리별 필터링 | High |
| V-04 | 상세 정보 카드 | 원본 사이트 이동 없이 핵심 정보(썸네일, 쇼핑몰명, 가격, 배송비) 요약 표시 | High |
| V-05 | 가격 신호등 | 해당 상품의 과거 핫딜 가격 DB와 비교하여 판별<br>🟢역대가 / 🟡평균가 / 🔴비쌈 표시 | High |
| V-06 | AI 3줄 요약 | 해당 게시글의 댓글 분위기 및 핵심 내용을 3줄로 요약하여 노출<br>("배송 느림", "역대가 아님", "쿠폰 적용 필수" 등) | Mid |
| V-07 | 원본 이동 (Deep Link) | '구매하러 가기' 버튼 클릭 시, 해당 쇼핑몰 앱/웹으로 즉시 연결 | High |

### C. 알림 시스템 (Notification)

| ID | 기능명 | 상세 설명 | 우선순위 |
|----|--------|-----------|----------|
| N-01 | 키워드 푸시 알림 | 사용자가 등록한 키워드가 포함된 핫딜 수집 시 1분 이내 푸시 발송 | High |
| N-02 | 방해 금지 모드 | 야간 시간대(23:00 ~ 07:00) 알림 미수신 설정 | Mid |
| N-03 | 추천 알림 | (U-02 정보 기반) 내 연령/성별 대에서 클릭률 높은 상품 일일 베스트 푸시 (On/Off 가능) | Low |

### D. 관리자 및 시스템 (Admin/System)

| ID | 기능명 | 상세 설명 | 우선순위 |
|----|--------|-----------|----------|
| S-01 | 멀티 크롤러 | 뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다 등 주요 5개 사이트 실시간 크롤링 | High |
| S-02 | 데이터 정제 | 쇼핑몰 링크 파싱 (수익화 링크 변환 고려), 썸네일 추출, 가격 텍스트 추출 | High |
| S-03 | 블랙리스트 관리 | 광고성 게시글, 업자, 특정 키워드 자동 필터링 및 수동 차단 기능 | High |

## 3. UI/UX 핵심 가이드 (Wireframe Concept)

- **메인 홈 (Feed)**: 인스타그램이나 당근마켓처럼 세로 스크롤 카드형 UI. 이미지가 크고 가격이 잘 보여야 함.
- **색상 구분**: 커뮤니티 출처를 뱃지 색상으로 구분 (예: 뽐뿌-회색, 펨코-파랑, 루리웹-하늘색).
- **반응 속도**: 앱 진입 시 로딩 없이 데이터를 보여줄 수 있도록 캐싱(Caching) 적용 필수.

## 4. 개발 단계별 로드맵 (제안)

- **1단계 (MVP)**: 크롤링 + 통합 리스트 보기 + 키워드 푸시 알림 (핵심 기능 검증)
- **2단계 (고도화)**: 가격 비교(신호등) + AI 댓글 요약 + 카테고리 분류 자동화
- **3단계 (확장)**: 연령별/성별 추천 알고리즘 + 커뮤니티 기능(유저끼리 의견 공유)

---

## 기술 스택

### Backend
- **Framework**: Python 3.x + FastAPI
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **ORM**: SQLAlchemy
- **Task Queue**: Celery
- **Web Scraping**: BeautifulSoup4, aiohttp

### Mobile
- **Framework**: React Native 0.73
- **Navigation**: React Navigation
- **HTTP Client**: Axios
- **Push Notifications**: react-native-push-notification

### DevOps
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git & GitHub

## 프로젝트 구조

```
claude-code-1/
├── backend/                 # Python FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱 엔트리포인트
│   │   ├── api/            # API 라우터
│   │   ├── models/         # SQLAlchemy 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── services/       # 비즈니스 로직
│   │   ├── crawlers/       # 커뮤니티별 크롤러
│   │   └── utils/          # 유틸리티
│   ├── tests/
│   └── requirements.txt
├── mobile/                  # React Native 앱
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── navigation/
│   │   └── services/
│   ├── App.js
│   └── package.json
└── docker-compose.yml
```

## 로컬 개발 환경 설정

### 1. 사전 요구사항
- Python 3.10 이상
- Node.js 18 이상
- Docker & Docker Compose
- Git

### 2. 데이터베이스 실행 (Docker)

```bash
# PostgreSQL & Redis 컨테이너 시작
docker-compose up -d

# 컨테이너 상태 확인
docker ps
```

### 3. 백엔드 실행

```bash
cd backend

# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 개발 서버 실행
uvicorn app.main:app --reload
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 4. 모바일 앱 실행

```bash
cd mobile

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env

# iOS 실행 (macOS only)
npm run ios

# Android 실행
npm run android
```

**참고**: React Native 앱 실행을 위해 Xcode (iOS) 또는 Android Studio (Android) 설정이 필요합니다.

## 개발 명령어

### 백엔드
```bash
# 개발 서버 실행
uvicorn app.main:app --reload

# 테스트 실행
pytest

# 코드 포맷팅
black app/

# 린트 검사
flake8 app/
```

### 모바일
```bash
# 개발 서버 시작
npm start

# iOS 실행
npm run ios

# Android 실행
npm run android

# 테스트 실행
npm test

# 린트 검사
npm run lint
```

## 다음 단계

1. **데이터베이스 스키마 설계**: SQLAlchemy 모델 정의
2. **첫 크롤러 구현**: 뽐뿌 또는 루리웹 크롤러 작성
3. **API 엔드포인트 개발**: 핫딜 리스트 조회 API
4. **모바일 UI 구현**: 핫딜 리스트 화면 개발
5. **푸시 알림 시스템**: 키워드 매칭 및 푸시 발송 구현
