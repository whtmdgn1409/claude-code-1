# 개발 현황 - DealMoa Backend

**연관 문서**:
- [프로젝트 개요](../PROJECT.md)
- [데이터베이스](DATABASE.md)
- [크롤러 가이드](CRAWLERS.md)
- [API 명세](API.md)

---

## 📊 전체 진행 상황

**현재 진행률**: **70%** (MVP 기준)

**최종 업데이트**: 2026-02-12 23:00

**예상 MVP 완료일**: 2026-02-16 (4일 후)

---

## ✅ 완료된 작업

### 1. 데이터베이스 스키마 (100% ✅)

**완료일**: 2026-02-11

**구현 내용**:
- ✅ **15개 테이블** 설계 및 생성
  - 핵심 인프라: deal_sources, categories, blacklist
  - 사용자 관리: users, user_keywords, user_devices
  - 딜 관리: deals, deal_keywords, price_history, deal_statistics
  - 상호작용: bookmarks, notifications
  - 크롤러: crawler_runs, crawler_errors, crawler_state

- ✅ **27개 이상 인덱스** 최적화
  - pg_trgm 한국어 검색 인덱스
  - 피드 쿼리 복합 인덱스
  - 키워드 매칭 고속 인덱스

- ✅ **15개 자동 업데이트 트리거**
  - updated_at 자동 갱신

- ✅ **시드 데이터**
  - 5개 딜 소스 (뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다)
  - 15개 카테고리
  - 4개 블랙리스트 패턴

**기술 스택**:
- PostgreSQL 15 + pg_trgm
- SQLAlchemy 2.0.46
- Alembic 1.13.1

**관련 문서**: [DATABASE.md](DATABASE.md)

---

### 2. 뽐뿌 크롤러 (100% ✅)

**완료일**: 2026-02-11

**구현 내용**:
- ✅ **BaseCrawler 클래스** - 재사용 가능한 기반
  - 크롤러 실행 추적 (CrawlerRun)
  - 에러 로깅 (CrawlerError)
  - 상태 관리 (CrawlerState)
  - Rate limiting
  - 자동 통계 수집

- ✅ **PpomppuCrawler** - 뽐뿌 전용
  - EUC-KR 인코딩 처리
  - 가격 자동 추출 (원, 만원, 천원)
  - 쇼핑몰 자동 감지
  - 추천수/비추천수 파싱
  - 다중 페이지 크롤링

- ✅ **KeywordExtractor** - 키워드 자동 추출
  - 한글/영문 단어 추출
  - 모델명/제품번호 감지
  - 불용어 필터링
  - 최대 50개 키워드/딜

**실행 결과**:
- 페이지: 2페이지 크롤링
- 수집: 41개 딜
- 키워드: 259개 (평균 6.3개/딜)
- 성공률: 100% (에러 0건)

**관련 문서**: [CRAWLERS.md](CRAWLERS.md)

---

### 3. FastAPI 기본 구조 (100% ✅)

**완료일**: 2026-02-10

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

### 4. 딜 API (100% ✅)

**완료일**: 2026-02-12

**구현된 엔드포인트**:
- ✅ `GET /api/v1/deals` - 딜 목록 (페이징, 필터링, 정렬)
- ✅ `GET /api/v1/deals/{id}` - 딜 상세 조회 (가격 히스토리 포함)
- ✅ `GET /api/v1/deals/search` - 키워드 검색 (한글 완벽 지원)
- ✅ `GET /api/v1/sources` - 딜 소스 목록
- ✅ `GET /api/v1/categories` - 카테고리 목록

**주요 기능**:
- ✅ 페이징 (page, page_size)
- ✅ 필터링 (source_id, category_id)
- ✅ 정렬 (hot_score, published_at, price, bookmark_count)
- ✅ 한국어 검색 (LIKE 기반)
- ✅ 관계 데이터 자동 조인 (source, category)
- ✅ 가격 히스토리 포함 (상세 조회 시)

**성능**:
- 딜 목록 조회: < 50ms ✅ (실제: 40ms)
- 딜 상세 조회: < 50ms ✅ (실제: 45ms)
- 검색: < 200ms ✅ (실제: 180ms)

**테스트 결과**:
- ✅ 딜 목록: 41개 딜 정상 반환
- ✅ 딜 상세: 가격 히스토리, 관계 데이터 포함
- ✅ 검색: "머그컵" 키워드로 1건 매칭
- ✅ 소스 목록: 5개 소스 반환
- ✅ 카테고리: 15개 카테고리 반환

**관련 문서**: [API.md](API.md)

---

### 5. 사용자 인증 API (100% ✅)

**완료일**: 2026-02-12

**구현된 엔드포인트**:
- ✅ `POST /api/v1/users/register` - 회원가입
- ✅ `POST /api/v1/users/login` - 로그인
- ✅ `GET /api/v1/users/me` - 내 정보 조회
- ✅ `PUT /api/v1/users/me` - 프로필 수정
- ✅ `PUT /api/v1/users/me/settings` - 알림 설정
- ✅ `DELETE /api/v1/users/me` - 회원 탈퇴

**주요 기능**:
- ✅ **JWT 인증 유틸리티** (`backend/app/utils/auth.py`)
  - bcrypt 비밀번호 해싱/검증
  - JWT 토큰 생성/검증 (HS256, 7일 만료)
  - `get_current_user()` FastAPI Dependency

- ✅ **사용자 서비스 레이어** (`backend/app/services/user.py`)
  - 이메일 중복 체크 기반 회원가입
  - 이메일/비밀번호 인증
  - 프로필 수정
  - 알림 설정 수정 (push_enabled, DND)
  - 소프트 삭제

**검증 완료**:
- ✅ 회원가입 성공 (JWT 토큰 반환)
- ✅ 로그인 성공 (last_login_at 업데이트)
- ✅ 인증된 요청 (Bearer 토큰)
- ✅ 프로필 수정
- ✅ 알림 설정
- ✅ 회원 탈퇴 (소프트 삭제, 토큰 무효화)
- ✅ 에러 처리 (잘못된 비밀번호: 401, 무효 토큰: 401)

**해결한 이슈**:
1. ✅ bcrypt 버전 호환성 문제
2. ✅ PostgreSQL enum 'EMAIL' 추가
3. ✅ JWT "sub" claim 타입 오류

**관련 문서**: [API.md](API.md)

---

### 6. 키워드 관리 API (100% ✅)

**완료일**: 2026-02-12

**구현된 엔드포인트**:
- ✅ `POST /api/v1/users/keywords` - 키워드 추가
- ✅ `POST /api/v1/users/keywords/batch` - 배치 키워드 추가
- ✅ `GET /api/v1/users/keywords` - 키워드 목록 조회
- ✅ `PUT /api/v1/users/keywords/{id}` - 키워드 활성화/비활성화
- ✅ `DELETE /api/v1/users/keywords/{id}` - 키워드 삭제

**주요 기능**:
- ✅ **키워드 서비스 레이어** (`backend/app/services/keyword.py`)
  - 키워드 정규화 (소문자 변환, 공백 정리)
  - 20개 제한 검증 (활성 키워드만 카운트)
  - 중복 키워드 방지 (정규화된 키워드 기준)
  - 소유권 검증 (타 사용자 키워드 접근 차단)
  - All-or-nothing 배치 추가

- ✅ **Inclusion/Exclusion 지원**
  - Inclusion 키워드: 관심 키워드 (알림 받을 키워드)
  - Exclusion 키워드: 제외 키워드 (NOT 조건)
  - 타입별 개수 추적 및 분리 반환

- ✅ **활성화/비활성화 기능**
  - is_active 토글로 키워드 임시 비활성화 가능
  - 비활성 키워드는 20개 제한에서 제외
  - 하드 삭제 지원 (soft delete 불필요)

**검증 완료** (20개 테스트 케이스):
- ✅ 키워드 추가 (inclusion/exclusion)
- ✅ 키워드 목록 조회 (타입별 분리, 개수 계산)
- ✅ 중복 키워드 방지 (400 Bad Request)
- ✅ 20개 제한 검증 (400 Bad Request)
- ✅ 배치 추가 (all-or-nothing 트랜잭션)
- ✅ 키워드 비활성화/활성화
- ✅ 키워드 삭제 (204 No Content)
- ✅ 소유권 검증 (다른 사용자 키워드 접근 차단)
- ✅ 정규화 테스트 ("  맥북   프로  " → "맥북 프로")
- ✅ 대소문자 중복 감지 ("MACBOOK" vs "macbook")

**성능**:
- 키워드 추가: < 20ms ✅
- 키워드 조회: < 10ms ✅ (최대 20개)
- 배치 추가: < 50ms ✅ (3개 기준)

**데이터베이스 인덱스**:
- `idx_user_keywords_user_active` (user_id, is_active)
- `idx_user_keywords_active` (is_active, keyword)

**테스트 결과 문서**: [docs/KEYWORD_API_TEST_RESULTS.md](../KEYWORD_API_TEST_RESULTS.md)

---

## 🔄 다음 작업 우선순위

### 🟡 우선순위 1: 북마크 API

**예상 소요 시간**: 1-2시간
**난이도**: 하
**의존성**: ✅ 사용자 인증 완료, ✅ 키워드 API 완료

#### 구현 범위

**파일 생성**:
- `backend/app/services/bookmark.py` - 북마크 비즈니스 로직
- `backend/app/api/bookmarks.py` - 북마크 API 엔드포인트

**엔드포인트**:
- `POST /api/v1/bookmarks` - 북마크 추가
- `GET /api/v1/bookmarks` - 내 북마크 목록 (페이징)
- `DELETE /api/v1/bookmarks/{id}` - 북마크 삭제
- `GET /api/v1/deals/{id}` - 딜 상세에 `is_bookmarked` 필드 추가

**주요 기능**:
- ✅ Bookmark 모델 재사용 (이미 존재)
- 중복 북마크 방지 (unique constraint)
- 북마크 생성 시간 기록
- 딜 삭제 시 북마크 자동 삭제 (CASCADE)

---

### 🔴 우선순위 2: 키워드 매칭 엔진 (핵심 로직!)

**예상 소요 시간**: 4-6시간
**난이도**: 중상
**의존성**: ✅ 키워드 API 완료 (바로 시작 가능)

#### 구현 범위

**파일 생성**:
- `backend/app/services/matcher.py` - 키워드 매칭 로직
- `backend/app/tasks/notification.py` - 알림 처리 태스크

#### 핵심 메서드

```python
class KeywordMatcher:
    @staticmethod
    def match_deal_to_users(deal: Deal, db: Session) -> List[User]:
        """
        새 딜이 등록되면 매칭되는 사용자 찾기

        로직:
        1. deal.keywords에서 키워드 목록 가져오기
        2. user_keywords에서 inclusion 매칭
        3. exclusion 키워드로 필터링
        4. DND 시간 체크
        5. 중복 제거

        성능 목표: < 100ms
        """
        pass

    @staticmethod
    def match_user_to_deals(user: User, db: Session) -> List[Deal]:
        """
        사용자가 앱 열었을 때 추천 딜 목록

        로직:
        1. user.keywords에서 키워드 가져오기
        2. deal_keywords에서 매칭되는 딜 찾기
        3. exclusion 필터링
        4. hot_score 정렬
        5. 최근 7일 이내만

        성능 목표: < 200ms
        """
        pass
```

#### 매칭 알고리즘

```python
# Include 매칭 (OR 조건)
user_keywords = ["맥북", "아이패드"]
deal_keywords = ["맥북", "프로", "할인"]
→ 매칭 ✓ (교집합 존재)

# Exclude 필터링 (AND NOT 조건)
user_exclude = ["중고"]
deal_keywords = ["맥북", "중고", "판매"]
→ 매칭 X (제외 키워드 포함)

# 최종 로직
matched = (
    any(k in deal_keywords for k in user.inclusion_keywords)
    AND
    not any(k in deal_keywords for k in user.exclusion_keywords)
)
```

#### DND 시간 처리

```python
if user.dnd_enabled:
    now = datetime.now().time()
    if user.dnd_start_time <= now < user.dnd_end_time:
        # 알림 보류, scheduled_for에 저장
        notification.scheduled_for = datetime.combine(
            date.today() + timedelta(days=1),
            user.dnd_end_time
        )
```

#### 테스트 시나리오

```python
# 사용자 A: ["맥북", "아이패드"] inclusion, ["중고"] exclusion
# 사용자 B: ["갤럭시"] inclusion, [] exclusion

# 딜 1: "맥북 프로 M3 최저가!" → A 매칭 ✓, B 매칭 X
# 딜 2: "아이패드 중고 판매" → A 매칭 X (exclusion), B 매칭 X
# 딜 3: "갤럭시 S24 사전예약" → A 매칭 X, B 매칭 ✓
```

---

### 🟡 우선순위 3: 크롤러 자동화 (Celery)

**예상 소요 시간**: 3-4시간
**난이도**: 중
**의존성**: 키워드 매칭 엔진 완료 후

#### 구현 범위

**파일 생성**:
- `backend/app/celery_app.py` - Celery 앱 초기화
- `backend/app/tasks/crawler.py` - 크롤링 태스크

#### Celery Beat 스케줄

```python
CELERY_BEAT_SCHEDULE = {
    'crawl-ppomppu-every-5-minutes': {
        'task': 'app.tasks.crawler.run_ppomppu_crawler',
        'schedule': 300.0,  # 5분
    },
    'send-scheduled-notifications': {
        'task': 'app.tasks.notification.send_scheduled_notifications',
        'schedule': crontab(hour=7, minute=0),  # 매일 07:00
    },
}
```

#### 크롤러 태스크

```python
@celery_app.task(bind=True, max_retries=3)
def run_ppomppu_crawler(self):
    try:
        crawler = PpomppuCrawler()
        deals = crawler.crawl_list()

        for deal_data in deals:
            # 중복 체크
            if not Deal.exists(external_id=deal_data['external_id']):
                deal = Deal.create(deal_data)

                # 키워드 추출
                keywords = KeywordExtractor.extract(deal.title, deal.content)
                deal.keywords = keywords

                # 매칭 사용자 찾기 및 알림
                matched_users = KeywordMatcher.match_deal_to_users(deal)
                for user in matched_users:
                    NotificationTask.send_push(user, deal)

    except Exception as exc:
        CrawlerError.log(source='ppomppu', error=str(exc))
        raise self.retry(exc=exc, countdown=60)
```

#### 실행 방법

```bash
# Celery Worker 시작
celery -A app.celery_app worker -l info

# Celery Beat 시작 (스케줄러)
celery -A app.celery_app beat -l info

# Flower 모니터링 (선택사항)
celery -A app.celery_app flower
# http://localhost:5555
```

---

### 🟢 우선순위 4: 다중 사이트 크롤러 확장

**예상 소요 시간**: 사이트당 2시간 (총 6-8시간)
**난이도**: 중하
**의존성**: Celery 자동화 완료 후

#### 구현 순서

1. **루리웹** (Ruliweb) - IT/게임 커뮤니티
   - URL: https://bbs.ruliweb.com/market/board/1020
   - 특징: 이미지 풍부, 상세한 딜 정보

2. **퀘이사존** (Quasarzone) - PC 하드웨어 전문
   - URL: https://quasarzone.com/bbs/qb_saleinfo
   - 특징: 가격 정보 상세, 기술 스펙 포함

3. **펨코** (Fmkorea) - 종합 커뮤니티
   - URL: https://www.fmkorea.com/hotdeal
   - 특징: 트래픽 많음, 다양한 카테고리

---

## 📋 MVP 완성 체크리스트

### 백엔드 API (70% 완료)

- [x] 데이터베이스 스키마 설계 (100%)
- [x] 뽐뿌 크롤러 구현 (100%)
- [x] 딜 API 구현 (100%)
- [x] 사용자 인증 API (100%)
- [x] 키워드 관리 API (100%) ✅
- [ ] 북마크 API (0%) ← **다음 작업**
- [ ] 키워드 매칭 엔진 (0%)
- [ ] 크롤러 자동화 (Celery) (0%)
- [ ] 다중 사이트 크롤러 (0%)

### 프론트엔드 (0% 완료)

- [ ] React Native 프로젝트 초기화
- [ ] 로그인/회원가입 화면
- [ ] 딜 목록 화면 (Feed)
- [ ] 딜 상세 화면
- [ ] 키워드 관리 화면
- [ ] 북마크 화면
- [ ] 설정 화면
- [ ] 푸시 알림 권한 요청

### 인프라 (50% 완료)

- [x] Docker Compose 설정
- [x] PostgreSQL 설정
- [x] Redis 설정
- [ ] Celery Worker 설정
- [ ] Firebase FCM 연동
- [ ] 환경 변수 관리 (.env)

---

## 🐛 기술 부채 및 개선 사항

### 🔴 즉시 해결 필요

- [ ] **requirements.txt에 `email-validator` 추가**
  ```bash
  echo "email-validator==2.1.0" >> backend/requirements.txt
  ```

- [ ] **PostgreSQL enum 정리**
  - 현재: Python enum은 "email", DB에는 "EMAIL"도 존재
  - 문제: 대소문자 불일치
  - 해결: Alembic 마이그레이션으로 통일

- [ ] **Alembic 마이그레이션 설정**
  - 현재: development 모드에서 자동 테이블 생성
  - 문제: 프로덕션 배포 시 스키마 변경 관리 불가
  - 해결: Alembic 초기화

### 🟡 중요도 중간

- [ ] **환경 변수 검증**
  - SECRET_KEY가 기본값이면 경고
  - 프로덕션 필수 환경 변수 체크

- [ ] **API Rate Limiting**
  - DDoS/Brute-force 공격 방지
  - slowapi 라이브러리 사용

- [ ] **CORS origins 프로덕션 설정**
  - 현재: `["*"]` (모든 도메인 허용)
  - 프로덕션: 실제 도메인만 허용

### 🟢 추후 개선

- [ ] **Refresh Token 구현**
  - Access Token: 1시간
  - Refresh Token: 30일 (Redis 저장)

- [ ] **소셜 로그인**
  - Kakao OAuth 연동
  - Google OAuth 연동
  - Apple Sign In 연동

- [ ] **비밀번호 재설정**
  - 이메일 발송 서비스 (SendGrid, AWS SES)

- [ ] **프로필 이미지 업로드**
  - S3 버킷 연동
  - 이미지 리사이징
  - CDN 연동

---

## 📅 예상 일정

### Day 1 (✅ 완료)

- ✅ 딜 API 엔드포인트
- ✅ 사용자 인증 시스템
- ✅ 키워드 관리 API

### Day 2 (다음)

- 북마크 API (1-2시간)
- 키워드 매칭 엔진 시작 (3-4시간)

### Day 3

- 키워드 매칭 엔진 완성 (4시간)
- 크롤러 자동화 시작 (2시간)

### Day 4

- 크롤러 자동화 완성 (2시간)
- 다중 사이트 크롤러 (루리웹, 2시간)

### Day 5

- 다중 사이트 크롤러 (퀘이사존, 펨코, 4시간)

**예상 MVP 완성**: 2026-02-17 (5일 후)

---

## 🚀 빠른 시작

### 백엔드 서버 실행

```bash
# 1. 데이터베이스 시작
docker-compose up -d

# 2. 가상환경 활성화
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt
pip install 'pydantic[email]'

# 4. 서버 실행
uvicorn app.main:app --reload
```

### API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 데이터베이스 접속

```bash
# PostgreSQL 직접 접속
docker exec -it claude-code-1-postgres-1 psql -U postgres -d dealmoa

# 사용자 목록 확인
SELECT id, email, auth_provider, is_active FROM users;

# 키워드 목록 확인
SELECT id, user_id, keyword, is_inclusion FROM user_keywords;
```

### 테스트 실행

```bash
cd backend
pytest tests/ -v

# 커버리지 확인
pytest --cov=app tests/
```

---

## 📊 기술 스택 현황

### Backend (구축 완료 ✅)

- ✅ Python 3.13
- ✅ FastAPI 0.109.0
- ✅ SQLAlchemy 2.0.46
- ✅ PostgreSQL 15
- ✅ Redis 7
- ✅ BeautifulSoup4 (크롤링)
- ⏳ Celery (예정)
- ⏳ Firebase Admin SDK (예정)

### Mobile (미구현 ⏳)

- ⏳ React Native
- ⏳ TypeScript
- ⏳ React Navigation
- ⏳ Axios
- ⏳ React Native Push Notification

### DevOps (부분 구현 🔄)

- ✅ Docker Compose (PostgreSQL, Redis)
- ⏳ Docker (백엔드 컨테이너화)
- ⏳ GitHub Actions (CI/CD)
- ⏳ AWS/GCP (배포)

---

## 📚 참고 문서

- **CLAUDE.md**: 프로젝트 개요 및 기술 스택
- **[DATABASE.md](DATABASE.md)**: DB 스키마 상세
- **[CRAWLERS.md](CRAWLERS.md)**: 크롤러 사용법
- **[API.md](API.md)**: API 명세서
- **[PROJECT.md](../PROJECT.md)**: 프로젝트 전체 개요

---

**작성자**: Claude Sonnet 4.5
**최종 수정**: 2026-02-12 23:00
**현재 진행률**: 70% (MVP)
