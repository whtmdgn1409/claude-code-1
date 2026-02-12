# 딜모아 (DealMoa) - 프로젝트 개요

**연관 문서**:
- [개발 현황](backend/STATUS.md)
- [데이터베이스](backend/DATABASE.md)
- [크롤러 가이드](backend/CRAWLERS.md)

---

## 📝 프로젝트 소개

**딜모아 (DealMoa)** - 한국 주요 커뮤니티의 핫딜 정보를 실시간으로 수집하고 키워드 기반 푸시 알림을 제공하는 서비스

### 핵심 기능

딜모아는 다음과 같은 핵심 기능을 제공합니다:

- ⚡ **실시간 핫딜 수집**: 주요 커뮤니티(뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다)에서 자동 크롤링
- 🎯 **키워드 기반 알림**: 사용자가 등록한 키워드에 맞는 딜을 1분 내 푸시 알림
- 📊 **가격 신호 시스템**: 역대가/평균가 비교를 통한 🟢🟡🔴 가격 신호 제공
- 💡 **통합 피드**: 여러 사이트의 딜을 한 곳에서 확인
- 📱 **개인화**: 최대 20개 키워드, 제외 키워드, 북마크 기능

### 타겟 사용자

- **연령대**: 20-40대 가성비를 추구하는 스마트 소비자
- **니즈**: 특정 제품/브랜드의 할인 정보를 빠르게 받고 싶은 사람
- **문제 해결**: 여러 커뮤니티를 일일이 확인하는 번거로움 제거

### 핵심 가치 제안

- ⚡ **실시간성**: 딜 등록 후 1분 내 알림
- 🎯 **개인화**: 최대 20개 키워드 기반 맞춤 알림
- 📱 **편리함**: 여러 사이트를 한 곳에서 확인
- 💡 **인사이트**: 역대가/평균가 가격 신호 제공

---

## 🏗 시스템 아키텍처

### 시스템 구성 요소

#### 1. Multi-Source Crawler (다중 소스 크롤러)

**대상 사이트**:
- 뽐뿌 (Ppomppu) ✅ 구현 완료
- 루리웹 (Ruliweb) ⏳ 예정
- 펨코 (Fmkorea) ⏳ 예정
- 퀘이사존 (Quasarzone) ⏳ 예정
- 딜바다 (Dealbada) ⏳ 예정

**기능**:
- 실시간 스크래핑 및 데이터 정규화
- 쇼핑몰 링크 파싱 및 썸네일 추출
- 중복 방지 및 증분 크롤링
- 자동 키워드 추출

#### 2. Data Processing Layer (데이터 처리 계층)

**가격 분석**:
- 가격 추출 및 히스토리 비교
- 가격 신호등: 🟢 역대가 (5% 이내) / 🟡 평균가 (10% 이내) / 🔴 비쌈

**Hot Level 계산**:
```python
hot_score = (upvotes - downvotes) * 10 + comment_count * 5 + (view_count / 100) - (age_hours * 0.5)
```

**추가 기능** (Phase 2):
- AI 기반 3줄 요약 (게시글 + 댓글)
- 자동 카테고리 분류
- 블랙리스트 필터링 (스팸, 광고)

#### 3. User Personalization (사용자 개인화)

**인증**:
- 소셜 로그인: Kakao, Google, Apple
- JWT 기반 토큰 인증 ✅ 구현 완료

**키워드 관리**:
- 관심 키워드 (최대 20개)
- 제외 키워드 (NOT 조건)

**기타**:
- 북마크 시스템
- DND (방해 금지) 모드 (23:00-07:00)

#### 4. Notification Engine (알림 엔진)

**실시간 푸시**:
- 키워드 매칭 후 1분 내 알림 전송
- Firebase Cloud Messaging (FCM) - Android
- Apple Push Notification Service (APNS) - iOS

**알림 제어**:
- DND 모드 지원
- 읽음/미읽음 상태 추적
- 인구통계 기반 추천 (선택 사항)

---

## 💻 기술 스택

### Backend

| 구분 | 기술 | 버전 | 상태 |
|------|------|------|------|
| Language | Python | 3.13 | ✅ |
| Framework | FastAPI | 0.109.0 | ✅ |
| Database | PostgreSQL | 15 | ✅ |
| ORM | SQLAlchemy | 2.0.46 | ✅ |
| Cache/Queue | Redis | 7 | ✅ |
| Migration | Alembic | 1.13.1 | ✅ |
| Validation | Pydantic | 2.12.5 | ✅ |
| Web Scraping | BeautifulSoup4 | - | ✅ |
| Task Queue | Celery | - | ⏳ |
| Push Notification | Firebase Admin SDK | - | ⏳ |

### Mobile

| 구분 | 기술 | 버전 | 상태 |
|------|------|------|------|
| Framework | React Native | 0.73 | ⏳ |
| Language | TypeScript | - | ⏳ |
| Navigation | React Navigation | - | ⏳ |
| HTTP Client | Axios | - | ⏳ |
| Push | react-native-push-notification | - | ⏳ |

### DevOps

| 구분 | 기술 | 상태 |
|------|------|------|
| Containerization | Docker & Docker Compose | ✅ |
| Version Control | Git & GitHub | ✅ |
| CI/CD | GitHub Actions | ⏳ |
| Deployment | AWS/GCP | ⏳ |

---

## 📦 프로젝트 구조

### Backend 구조

```
backend/app/
├── main.py              # FastAPI 엔트리포인트
├── config.py            # 설정 관리
├── api/                 # API 라우트 핸들러
│   ├── deals.py         # 딜 API ✅
│   ├── users.py         # 사용자 API ✅
│   ├── keywords.py      # 키워드 API ⏳
│   └── bookmarks.py     # 북마크 API ⏳
├── models/              # SQLAlchemy 모델 (15개 테이블) ✅
│   ├── deal.py
│   ├── user.py
│   ├── interaction.py
│   └── ...
├── schemas/             # Pydantic 스키마 ✅
│   ├── deal.py
│   ├── user.py
│   └── ...
├── services/            # 비즈니스 로직
│   ├── keyword_extractor.py  # 키워드 추출 ✅
│   ├── user.py               # 사용자 서비스 ✅
│   ├── matcher.py            # 키워드 매칭 ⏳
│   └── notification.py       # 알림 서비스 ⏳
├── crawlers/            # 사이트별 크롤러
│   ├── base_crawler.py  # 기본 크롤러 ✅
│   ├── ppomppu.py       # 뽐뿌 크롤러 ✅
│   └── ...              # 다른 사이트 ⏳
└── utils/               # 유틸리티
    ├── auth.py          # JWT 인증 ✅
    ├── seed_data.py     # 시드 데이터 ✅
    └── ...
```

### Mobile 구조

```
mobile/src/
├── screens/             # 화면 컴포넌트 ⏳
│   ├── Home.js          # 홈 피드
│   ├── Detail.js        # 딜 상세
│   └── Settings.js      # 설정
├── components/          # 재사용 컴포넌트 ⏳
│   ├── DealCard.js      # 딜 카드
│   └── ...
├── navigation/          # React Navigation ⏳
├── services/            # API 클라이언트 ⏳
└── store/               # 상태 관리 ⏳
```

---

## 🎯 기능 우선순위

### Phase 1: MVP (진행 중 - 60%)

**목표**: 핵심 기능 검증

- [x] 데이터베이스 스키마 설계
- [x] 뽐뿌 크롤러 구현
- [x] 딜 API 구현
- [x] 사용자 인증 API
- [ ] 키워드 관리 API
- [ ] 북마크 API
- [ ] 키워드 매칭 엔진
- [ ] 푸시 알림 서비스

**예상 완료**: 2026-02-17 (5일 후)

### Phase 2: Enhancement (예정)

**목표**: 고도화된 기능 추가

- [ ] 나머지 4개 사이트 크롤러
- [ ] 크롤러 자동화 (Celery)
- [ ] 가격 비교 (신호등 시스템)
- [ ] AI 댓글 요약
- [ ] 자동 카테고리 분류

**예상 소요**: 2주

### Phase 3: Expansion (예정)

**목표**: 확장 기능 및 커뮤니티

- [ ] 연령/성별 기반 추천 알고리즘
- [ ] 커뮤니티 기능 (유저 의견 공유)
- [ ] 고급 분석 대시보드

**예상 소요**: 3-4주

---

## 🎨 UI/UX 가이드라인

### 메인 화면 (Feed)

- **스타일**: 인스타그램/당근마켓 스타일 세로 스크롤 카드 UI
- **이미지**: 크고 눈에 잘 띄는 썸네일
- **가격**: 큰 폰트로 강조
- **배지**: 커뮤니티 출처를 색상으로 구분
  - 뽐뿌: 회색
  - 루리웹: 하늘색
  - 펨코: 파랑
  - 퀘이사존: 초록
  - 딜바다: 주황

### 성능 요구사항

- **로딩 속도**: 앱 진입 시 즉시 데이터 표시 (캐싱 필수)
- **피드 쿼리**: < 50ms
- **검색**: < 200ms
- **알림 전송**: < 1초

### 접근성

- 고대비 모드 지원
- 큰 터치 영역
- 명확한 라벨링

---

## 🌏 한국 시장 컨텍스트

### 언어

- **UI/UX**: 모든 인터페이스는 한국어
- **콘텐츠**: 한국 커뮤니티의 한국어 콘텐츠
- **검색**: 한국어 형태소 분석 (pg_trgm)

### 소셜 로그인

- **Kakao**: 가장 높은 우선순위 (한국 시장 점유율 1위)
- **Google**: 2순위
- **Apple**: iOS 사용자 대응

### 결제 연동 (향후)

- 네이버페이
- 카카오페이
- 토스페이

---

## 📊 현재 개발 상황

**전체 진행률**: 60% (MVP 기준)

상세 현황은 [backend/STATUS.md](backend/STATUS.md)를 참고하세요.

---

## 🚀 시작하기

### 로컬 환경 설정

자세한 설정 방법은 [루트 README.md](../README.md)를 참고하세요.

**간단 요약**:

```bash
# 1. Docker 시작
docker-compose up -d

# 2. 백엔드 실행
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 3. API 문서 확인
open http://localhost:8000/docs
```

---

## 📚 추가 문서

- [데이터베이스 스키마](backend/DATABASE.md) - 15개 테이블, 27+ 인덱스
- [크롤러 가이드](backend/CRAWLERS.md) - 크롤러 사용법 및 구현
- [API 명세](backend/API.md) - REST API 엔드포인트
- [개발 현황](backend/STATUS.md) - 진행 상황 및 다음 단계
- [CLAUDE.md](../CLAUDE.md) - Claude Code용 개발 가이드

---

**프로젝트 시작일**: 2026-02-10
**최종 업데이트**: 2026-02-12
**상태**: Active Development (MVP Phase)
