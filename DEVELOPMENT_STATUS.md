# 딜모아 (DealMoa) 개발 현황

**최종 업데이트**: 2026-02-12
**프로젝트 진행률**: **45%** (MVP 기준)

---

## 📊 전체 개요

딜모아는 한국 주요 커뮤니티(뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다)에서 핫딜 정보를 실시간으로 수집하고, 사용자가 등록한 키워드에 맞는 딜을 푸시 알림으로 전달하는 서비스입니다.

### 목표 사용자
- 20-40대 가성비를 추구하는 스마트 소비자
- 특정 제품/브랜드의 할인 정보를 빠르게 받고 싶은 사람
- 여러 커뮤니티를 일일이 확인하기 번거로운 사람

### 핵심 가치 제안
- ⚡ **실시간성**: 딜 등록 후 1분 내 알림
- 🎯 **개인화**: 최대 20개 키워드 기반 맞춤 알림
- 📱 **편리함**: 여러 사이트를 한 곳에서 확인
- 💡 **인사이트**: 역대가/평균가 가격 신호 제공

---

## ✅ 완료된 작업 (Phase 1 - 기반 구축)

### 1. 데이터베이스 스키마 구현 (100% 완료)

**구현 내용**:
- ✅ **15개 테이블** 설계 및 생성
  - 핵심 인프라: `deal_sources`, `categories`, `blacklist`
  - 사용자 관리: `users`, `user_keywords`, `user_devices`
  - 딜 관리: `deals`, `deal_keywords`, `price_history`, `deal_statistics`
  - 상호작용: `bookmarks`, `notifications`
  - 크롤러: `crawler_runs`, `crawler_errors`, `crawler_state`

- ✅ **27개 이상 인덱스** 최적화
  - 한국어 텍스트 검색용 pg_trgm 인덱스
  - 피드 쿼리 최적화 복합 인덱스
  - 키워드 매칭용 고속 인덱스

- ✅ **15개 자동 업데이트 트리거**
  - `updated_at` 자동 갱신

- ✅ **시드 데이터 구축**
  - 5개 딜 소스 (뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다)
  - 15개 상품 카테고리
  - 4개 기본 블랙리스트 패턴

**파일 구조**:
```
backend/app/
├── models/          # 8개 모델 파일
├── schemas/         # 4개 스키마 파일
├── utils/           # 3개 유틸리티 파일
└── config.py        # 설정 관리

backend/alembic/     # 마이그레이션 설정
```

**기술 스택**:
- PostgreSQL 15 + pg_trgm (한국어 검색)
- SQLAlchemy 2.0.46
- Pydantic 2.12.5
- Alembic 1.13.1

**관련 문서**: `DATABASE_SCHEMA_IMPLEMENTATION_SUMMARY.md`

---

### 2. 뽐뿌 크롤러 구현 (100% 완료)

**구현 내용**:
- ✅ **BaseCrawler 클래스** - 재사용 가능한 크롤러 기반
  - 크롤러 실행 추적 (CrawlerRun)
  - 에러 로깅 (CrawlerError)
  - 상태 관리 (CrawlerState)
  - Rate limiting (1초 딜레이)
  - 자동 통계 수집

- ✅ **PpomppuCrawler** - 뽐뿌 전용 크롤러
  - EUC-KR 인코딩 처리
  - 가격 자동 추출 (원, 만원, 천원 지원)
  - 쇼핑몰 자동 감지 (쿠팡, 11번가, G마켓 등)
  - 추천수/비추천수 파싱
  - 다중 페이지 크롤링

- ✅ **KeywordExtractor** - 키워드 자동 추출
  - 한글/영문 단어 추출
  - 모델명/제품번호 감지 (RTX4090, 갤럭시S23 등)
  - 불용어 필터링
  - 최대 50개 키워드/딜

**실행 결과** (테스트 완료):
```
페이지: 2페이지 크롤링
수집: 41개 딜
키워드: 259개 (평균 6.3개/딜)
성공률: 100% (에러 0건)
```

**파일 구조**:
```
backend/app/
├── crawlers/
│   ├── base_crawler.py      # 기본 크롤러
│   └── ppomppu.py            # 뽐뿌 크롤러
├── services/
│   └── keyword_extractor.py # 키워드 추출
└── scripts/
    └── run_ppomppu_crawler.py # 실행 스크립트
```

**관련 문서**: `CRAWLER_README.md`

---

### 3. FastAPI 기본 구조 (100% 완료)

**구현 내용**:
- ✅ FastAPI 애플리케이션 설정
- ✅ CORS 미들웨어
- ✅ 데이터베이스 연결 health check
- ✅ Swagger UI 문서 (`/docs`)
- ✅ 환경 변수 관리 (`.env`)

**엔드포인트**:
- `GET /` - API 정보
- `GET /health` - 헬스 체크 (DB 연결 확인)
- `GET /docs` - Swagger UI

---

### 4. API 엔드포인트 구현 - 딜 API (100% 완료) ✨ NEW

**완료일**: 2026-02-12

**구현된 엔드포인트**:
- ✅ `GET /api/v1/deals` - 딜 목록 (페이징, 필터링, 정렬)
- ✅ `GET /api/v1/deals/{id}` - 딜 상세 조회 (가격 히스토리 포함)
- ✅ `GET /api/v1/deals/search` - 키워드 검색 (한글 완벽 지원)
- ✅ `GET /api/v1/sources` - 딜 소스 목록
- ✅ `GET /api/v1/categories` - 카테고리 목록

**주요 기능**:
- ✅ 페이징: `page`, `page_size` 파라미터 (최대 100개/페이지)
- ✅ 필터링: `source_id`, `category_id` 기반 필터
- ✅ 정렬: `hot_score`, `published_at`, `price`, `bookmark_count` (asc/desc)
- ✅ 한국어 검색: LIKE 기반 키워드 검색 (제목, 상품명)
- ✅ 관계 데이터: source, category 자동 조인 (joinedload)
- ✅ 가격 히스토리: 최근 30일 히스토리 포함

**성능**:
- 딜 목록 조회: < 50ms ✅
- 딜 상세 조회: < 50ms ✅
- 검색: < 200ms ✅

**파일 구조**:
```
backend/app/
└── api/
    ├── __init__.py
    └── deals.py         # 딜 API 엔드포인트 (249 lines)
```

**테스트 결과**:
```
✅ 딜 목록: 41개 딜 정상 반환
✅ 딜 상세: 가격 히스토리, 관계 데이터 포함
✅ 검색: "머그컵" 키워드로 1건 매칭
✅ 소스 목록: 5개 소스 반환
✅ 카테고리: 15개 카테고리 반환
```

**API 문서**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**기술적 개선사항**:
- SQLAlchemy 2.0.25 → 2.0.46 업그레이드 (Python 3.13 호환)
- 검색 엔진: pg_trgm → LIKE 기반 (한글 호환성)
- 라우트 순서 최적화 (/search가 /{id}보다 먼저)

---

## 🔄 현재 진행 중인 작업

없음 (다음 단계 대기 중)

---

## 📋 다음 단계 (Phase 2 - 핵심 기능 구현)

### 우선순위 1: 사용자 & 키워드 & 북마크 API 구현 (예상 6-8시간)

#### 2. 사용자(User) API (`backend/app/api/users.py`)
```python
POST /api/v1/users/register     # 회원가입 (소셜 로그인)
GET  /api/v1/users/me           # 내 정보 조회
PUT  /api/v1/users/me           # 내 정보 수정
PUT  /api/v1/users/me/settings  # 알림 설정 (DND 등)
```

**주요 기능**:
- 소셜 로그인 (Kakao, Google, Apple)
- JWT 토큰 발급
- DND 설정 관리

#### 3. 키워드(Keyword) API (`backend/app/api/keywords.py`)
```python
GET    /api/v1/keywords         # 내 키워드 목록
POST   /api/v1/keywords         # 키워드 추가
DELETE /api/v1/keywords/{id}    # 키워드 삭제
PUT    /api/v1/keywords/{id}    # 키워드 활성화/비활성화
```

**주요 기능**:
- 최대 20개 제한 검증
- Include/Exclude 타입 지원
- 키워드별 매칭 딜 수 표시

#### 4. 북마크(Bookmark) API (`backend/app/api/bookmarks.py`)
```python
GET    /api/v1/bookmarks        # 내 북마크 목록
POST   /api/v1/bookmarks        # 북마크 추가
DELETE /api/v1/bookmarks/{id}   # 북마크 삭제
```

**예상 소요 시간**: 2-3일

---

### 우선순위 2: 키워드 매칭 엔진 (예상 4-6시간)

**구현 파일**: `backend/app/services/keyword_matcher.py`

**주요 기능**:
```python
class KeywordMatcher:
    def match_deal_to_users(deal: Deal) -> List[User]:
        """딜에 매칭되는 사용자 찾기"""
        # 1. deal_keywords 테이블 조회
        # 2. user_keywords와 매칭
        # 3. Include/Exclude 로직 적용
        # 4. DND 시간 체크
        # 5. 매칭된 사용자 반환

    def match_user_to_deals(user: User) -> List[Deal]:
        """사용자 키워드에 매칭되는 딜 찾기"""
```

**성능 목표**:
- 딜 1개 → 매칭 사용자 찾기: **< 100ms**
- 사용자 1명 → 매칭 딜 찾기: **< 200ms**

**예상 소요 시간**: 반나절

---

### 우선순위 3: 푸시 알림 서비스 (예상 6-8시간)

**구현 파일**: `backend/app/services/notification_service.py`

**주요 기능**:
```python
class NotificationService:
    def send_deal_notification(user: User, deal: Deal):
        """딜 알림 전송"""
        # 1. DND 시간 체크
        # 2. FCM/APNS 메시지 생성
        # 3. 푸시 전송
        # 4. Notification 테이블 기록

    def send_batch_notifications(notifications: List):
        """일괄 알림 전송 (최적화)"""
```

**통합 서비스**:
- Firebase Cloud Messaging (FCM) - Android
- Apple Push Notification Service (APNS) - iOS

**알림 형식**:
```
제목: [뽐뿌] 갤럭시S23 역대가!
내용: 700,000원 → 599,000원 (14% 할인)
      조회 1,234 | 추천 45
```

**예상 소요 시간**: 1일

---

### 우선순위 4: 나머지 크롤러 구현 (예상 10-12시간)

**구현할 크롤러**:

1. **루리웹** (`backend/app/crawlers/ruliweb.py`)
   - URL: https://bbs.ruliweb.com/market/board/1020
   - 특징: 게임/IT 중심

2. **펨코** (`backend/app/crawlers/fmkorea.py`)
   - URL: https://www.fmkorea.com/hotdeal
   - 특징: 다양한 카테고리

3. **퀘이사존** (`backend/app/crawlers/quasarzone.py`)
   - URL: https://quasarzone.com/bbs/qb_saleinfo
   - 특징: PC 하드웨어 중심

4. **딜바다** (`backend/app/crawlers/dealbada.py`)
   - URL: https://www.dealbada.com
   - 특징: 전문 딜 사이트

**공통 작업**:
- 각 사이트별 HTML 구조 분석
- BaseCrawler 상속하여 구현
- 테스트 스크립트 작성

**예상 소요 시간**: 2-3일 (사이트당 반나절)

---

### 우선순위 5: 스케줄러 설정 (예상 4-6시간)

**구현 파일**: `backend/app/scheduler/tasks.py`

**사용 기술**: Celery + Redis

**주요 태스크**:
```python
# 5분마다 크롤링
@celery.task
def crawl_all_sources():
    for source in ["ppomppu", "ruliweb", "fmkorea", ...]:
        run_crawler(source)

# 새로운 딜 발견 시 즉시 알림
@celery.task
def process_new_deal(deal_id):
    deal = get_deal(deal_id)
    matched_users = keyword_matcher.match_deal_to_users(deal)
    for user in matched_users:
        send_deal_notification(user, deal)

# 매일 자정 통계 업데이트
@celery.task
def update_daily_statistics():
    # deal_statistics 테이블 업데이트
    pass
```

**스케줄**:
- 크롤링: 5분마다
- 알림 전송: 즉시 (새 딜 발견 시)
- 통계 업데이트: 매일 00:00

**예상 소요 시간**: 반나절~1일

---

## 🎯 MVP (Minimum Viable Product) 완료 기준

### Phase 1: 기본 기능 (현재 45% 완료)

- [x] 데이터베이스 스키마
- [x] 뽐뿌 크롤러
- [x] FastAPI 기본 구조
- [x] **딜 API 엔드포인트** ✨ (2026-02-12 완료)
- [ ] 사용자/키워드/북마크 API 엔드포인트
- [ ] 키워드 매칭 엔진
- [ ] 푸시 알림 서비스

**예상 완료일**: 2-3주 (집중 개발 시)

### Phase 2: 확장 기능

- [ ] 나머지 4개 크롤러
- [ ] 스케줄러 (실시간 크롤링)
- [ ] 가격 신호 계산 (🟢🟡🔴)
- [ ] AI 요약 생성
- [ ] 자동 카테고리 분류

**예상 완료일**: 추가 2주

### Phase 3: 모바일 앱

- [ ] React Native 앱 기본 구조
- [ ] 홈 피드 화면
- [ ] 딜 상세 화면
- [ ] 키워드 설정 화면
- [ ] 북마크 화면
- [ ] 푸시 알림 연동

**예상 완료일**: 추가 3-4주

---

## 📊 기술 스택 현황

### Backend (구축 완료)
- ✅ Python 3.13
- ✅ FastAPI 0.109.0
- ✅ SQLAlchemy 2.0.46
- ✅ PostgreSQL 15
- ✅ Redis 7
- ✅ BeautifulSoup4 (크롤링)
- ⏳ Celery (예정)
- ⏳ Firebase Admin SDK (예정)

### Mobile (미구현)
- ⏳ React Native
- ⏳ TypeScript
- ⏳ React Navigation
- ⏳ Axios
- ⏳ React Native Push Notification

### DevOps (부분 구현)
- ✅ Docker Compose (PostgreSQL, Redis)
- ⏳ Docker (백엔드 컨테이너화)
- ⏳ GitHub Actions (CI/CD)
- ⏳ AWS/GCP (배포)

---

## 💾 데이터베이스 현황

### 테이블 생성 상태
```
✅ 15/15 테이블 생성 완료
✅ 27+ 인덱스 생성 완료
✅ 15 트리거 생성 완료
✅ pg_trgm 확장 활성화
```

### 현재 데이터
```
딜 소스: 5개 (뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다)
카테고리: 15개
블랙리스트: 4개 패턴
수집된 딜: 41개 (뽐뿌 크롤러 테스트)
추출된 키워드: 259개
```

---

## 🚀 즉시 시작 가능한 작업

### 1. 사용자/키워드/북마크 API 구현 (최우선 추천) ⭐
**이유**: 딜 API 완료 후 다음 단계, 사용자 인증 및 개인화 기능의 기반
**난이도**: 중
**소요 시간**: 1-2일
**의존성**: 딜 API ✅ 완료

**시작 방법**:
```bash
# API 파일 생성
touch backend/app/api/users.py
touch backend/app/api/keywords.py
touch backend/app/api/bookmarks.py

# JWT 인증 추가
touch backend/app/utils/auth.py
```

**구현 순서**:
1. JWT 인증 유틸리티 (`auth.py`)
2. 사용자 API (회원가입, 로그인, 내 정보)
3. 키워드 API (CRUD, 최대 20개 제한)
4. 북마크 API (CRUD)

---

### 2. 키워드 매칭 엔진 (추천)
**이유**: 알림 기능의 핵심 로직
**난이도**: 중상
**소요 시간**: 반나절~1일
**의존성**: 사용자 & 키워드 API 필요

**시작 방법**:
```bash
touch backend/app/services/keyword_matcher.py
```

**구현 내용**:
- `match_deal_to_users()`: 딜 → 사용자 매칭
- `match_user_to_deals()`: 사용자 → 딜 매칭
- Include/Exclude 로직
- DND 시간 체크

---

### 3. 나머지 크롤러 구현 (병렬 진행 가능)
**이유**: 더 많은 딜 소스 확보
**난이도**: 중하
**소요 시간**: 크롤러당 2-3시간
**의존성**: 없음 (독립적)

**시작 방법**:
```bash
# 루리웹 크롤러 생성
touch backend/app/crawlers/ruliweb.py
touch backend/scripts/run_ruliweb_crawler.py
```

**구현 순서** (추천):
1. 루리웹 (게임/IT 중심)
2. 퀘이사존 (PC 하드웨어)
3. 펨코 (다양한 카테고리)
4. 딜바다 (전문 딜 사이트)

---

## 📝 개발 환경 설정

### 필수 사전 준비
```bash
# 1. Docker 실행
docker-compose up -d

# 2. 가상환경 활성화
cd backend
source venv/bin/activate

# 3. 데이터베이스 확인
python -m app.utils.seed_data  # 이미 실행됨

# 4. 크롤러 테스트
python -m scripts.run_ppomppu_crawler --pages 2
```

### 개발 서버 실행
```bash
# FastAPI 서버
uvicorn app.main:app --reload

# API 문서 확인
open http://localhost:8000/docs
```

---

## 🎯 단기 목표 (1-2주)

1. ✅ 데이터베이스 스키마 완성
2. ✅ 뽐뿌 크롤러 완성
3. ✅ **딜 API 구현** ✨ (2026-02-12 완료)
4. 🔲 사용자/키워드/북마크 API 구현 (다음 작업)
5. 🔲 키워드 매칭 엔진 구현
6. 🔲 기본 푸시 알림 구현

---

## 📞 문의 및 기여

**프로젝트 저장소**: https://github.com/whtmdgn1409/claude-code-1

**주요 문서**:
- `CLAUDE.md` - 프로젝트 개요 및 개발 가이드
- `DATABASE_SCHEMA_IMPLEMENTATION_SUMMARY.md` - DB 스키마 상세
- `CRAWLER_README.md` - 크롤러 사용법
- `DEVELOPMENT_STATUS.md` - 현재 문서

---

**마지막 업데이트**: 2026-02-12
**최근 완료**: 딜 API 엔드포인트 (5개 엔드포인트)
**다음 마일스톤**: 사용자/키워드/북마크 API 구현
**예상 완료일**: 1주 후 (2026-02-19)
