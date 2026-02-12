# 딜모아 개발 진행 상황 및 다음 단계

**작성일**: 2026-02-12
**현재 진행률**: 60% (MVP 기준)
**최종 업데이트**: 2026-02-12 22:30

---

## ✅ 오늘 완료한 작업 (2026-02-12)

### 1. 딜 API 엔드포인트 구현 ✅ (100% 완료)
- 5개 엔드포인트 구현 및 테스트 완료
- 한글 검색 기능 정상 동작
- 성능 목표 달성 (< 50ms ~ 200ms)
- Swagger UI 문서 자동 생성

### 2. **사용자 인증 시스템 구현** ✅ (100% 완료) 🎉
**소요 시간**: 약 3시간 (디버깅 포함)

#### 구현된 기능
- ✅ **JWT 인증 유틸리티** (`backend/app/utils/auth.py`)
  - bcrypt 비밀번호 해싱/검증
  - JWT 토큰 생성/검증 (HS256, 7일 만료)
  - `get_current_user()` FastAPI Dependency
  - JWT "sub" claim 문자열 변환 처리

- ✅ **사용자 서비스 레이어** (`backend/app/services/user.py`)
  - 이메일 중복 체크 기반 회원가입
  - 이메일/비밀번호 인증 (last_login_at 자동 업데이트)
  - 프로필 수정 (username, display_name, age, gender)
  - 알림 설정 수정 (push_enabled, DND 시간)
  - 소프트 삭제 (is_active=False, deleted_at 기록)

- ✅ **사용자 API 엔드포인트** (`backend/app/api/users.py`)
  - `POST /api/v1/users/register` - 회원가입 (201 Created)
  - `POST /api/v1/users/login` - 로그인 (200 OK)
  - `GET /api/v1/users/me` - 내 정보 조회
  - `PUT /api/v1/users/me` - 프로필 수정
  - `PUT /api/v1/users/me/settings` - 알림 설정
  - `DELETE /api/v1/users/me` - 회원 탈퇴 (204 No Content)

#### 검증 완료
```bash
✅ 회원가입 성공 (JWT 토큰 반환)
✅ 로그인 성공 (last_login_at 업데이트)
✅ 인증된 요청 (Bearer 토큰)
✅ 프로필 수정 (display_name: "Updated Name", age: 30)
✅ 알림 설정 (dnd_enabled: false)
✅ 회원 탈퇴 (소프트 삭제, 토큰 무효화)
✅ 에러 처리 (잘못된 비밀번호: 401, 무효 토큰: 401)
```

#### 데이터베이스 확인
```sql
 id |        email        | auth_provider | is_active | deleted_at
----+---------------------+---------------+-----------+------------
  1 | test@dealmoa.com    | EMAIL         | f         | 2026-02-12
  2 | newuser@dealmoa.com | EMAIL         | t         | NULL

✅ 비밀번호 bcrypt 해싱 확인 ($2b$12$...)
✅ 소프트 삭제 작동 확인
```

#### 해결한 이슈
1. ✅ bcrypt 버전 호환성 문제 → bcrypt 직접 사용으로 해결
2. ✅ PostgreSQL enum 'EMAIL' 추가 → ALTER TYPE 실행
3. ✅ JWT "sub" claim 타입 오류 → str(user.id) 변환

---

## 🎯 다음 작업 우선순위

### 🔴 우선순위 1: 키워드 관리 API (다음 작업!)
**예상 소요 시간**: 2-3시간
**난이도**: 하
**의존성**: ✅ 사용자 인증 완료 (바로 시작 가능)

#### 구현 범위
**파일 생성**:
- `backend/app/services/keyword.py` - 키워드 비즈니스 로직
- `backend/app/api/keywords.py` - 키워드 API 엔드포인트

**엔드포인트**:
```
POST   /api/v1/keywords              # 키워드 추가
GET    /api/v1/keywords              # 내 키워드 목록 (inclusion/exclusion 분리)
PUT    /api/v1/keywords/{id}         # 키워드 활성화/비활성화
DELETE /api/v1/keywords/{id}         # 키워드 삭제
POST   /api/v1/keywords/batch        # 키워드 일괄 추가 (최대 20개)
```

**주요 기능**:
- ✅ UserKeyword 모델 재사용 (이미 존재)
- ✅ UserKeywordCreate/Response 스키마 재사용
- 최대 20개 키워드 제한 (DB 쿼리로 체크)
- Inclusion (관심) / Exclusion (제외) 키워드 구분
- 키워드 정규화 (소문자 변환, 공백 제거)
- 중복 키워드 체크 (대소문자 무시)

**KeywordService 메서드**:
```python
class KeywordService:
    @staticmethod
    def add_keyword(db, user, keyword: str, is_inclusion: bool) -> UserKeyword:
        # 1. 20개 제한 체크
        # 2. 중복 체크 (정규화 후)
        # 3. UserKeyword 생성
        pass

    @staticmethod
    def get_user_keywords(db, user) -> UserKeywordListResponse:
        # 1. 사용자의 모든 키워드 조회
        # 2. inclusion/exclusion 분리
        # 3. 개수 계산
        pass

    @staticmethod
    def delete_keyword(db, user, keyword_id: int):
        # 1. 키워드 소유권 확인
        # 2. 삭제
        pass
```

**검증 방법**:
```bash
# 1. 키워드 추가
curl -X POST http://localhost:8000/api/v1/keywords \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"keyword":"맥북","is_inclusion":true}'

# 2. 키워드 목록 조회
curl http://localhost:8000/api/v1/keywords \
  -H "Authorization: Bearer $TOKEN"

# 3. 20개 초과 시도 (400 에러 확인)
for i in {1..21}; do
  curl -X POST http://localhost:8000/api/v1/keywords \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"keyword\":\"키워드$i\"}"
done
```

---

### 🟡 우선순위 2: 북마크 API
**예상 소요 시간**: 1-2시간
**난이도**: 하
**의존성**: 사용자 인증 완료 ✅

#### 구현 범위
**파일 생성**:
- `backend/app/services/bookmark.py` - 북마크 비즈니스 로직
- `backend/app/api/bookmarks.py` - 북마크 API 엔드포인트

**엔드포인트**:
```
POST   /api/v1/bookmarks        # 북마크 추가 (deal_id)
GET    /api/v1/bookmarks        # 내 북마크 목록 (페이징)
DELETE /api/v1/bookmarks/{id}   # 북마크 삭제
GET    /api/v1/deals/{id}       # 딜 상세 (is_bookmarked 필드 추가)
```

**주요 기능**:
- ✅ Bookmark 모델 재사용 (이미 존재)
- 중복 북마크 방지 (unique constraint 활용)
- 북마크 생성 시간 기록
- 딜이 삭제되면 북마크도 자동 삭제 (CASCADE)

**BookmarkService 메서드**:
```python
class BookmarkService:
    @staticmethod
    def add_bookmark(db, user, deal_id: int) -> Bookmark:
        # 1. 딜 존재 여부 확인
        # 2. 중복 체크
        # 3. Bookmark 생성
        pass

    @staticmethod
    def get_user_bookmarks(db, user, page: int, limit: int) -> PaginatedResponse:
        # 1. 북마크 목록 조회 (최신순)
        # 2. 딜 정보 join
        # 3. 페이징
        pass

    @staticmethod
    def remove_bookmark(db, user, bookmark_id: int):
        # 1. 소유권 확인
        # 2. 삭제
        pass

    @staticmethod
    def is_bookmarked(db, user, deal_id: int) -> bool:
        # 북마크 여부 확인
        pass
```

---

### 🔴 우선순위 3: 키워드 매칭 엔진 (핵심 로직!)
**예상 소요 시간**: 4-6시간
**난이도**: 중상
**의존성**: 키워드 API 완료 후

#### 구현 범위
**파일 생성**:
- `backend/app/services/matcher.py` - 키워드 매칭 로직
- `backend/app/tasks/notification.py` - 알림 처리 태스크

**핵심 메서드**:
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

**매칭 알고리즘**:
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

**DND 시간 처리**:
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

**테스트 시나리오**:
```python
# 사용자 A: ["맥북", "아이패드"] inclusion, ["중고"] exclusion
# 사용자 B: ["갤럭시"] inclusion, [] exclusion

# 딜 1: "맥북 프로 M3 최저가!" → A 매칭 ✓, B 매칭 X
# 딜 2: "아이패드 중고 판매" → A 매칭 X (exclusion), B 매칭 X
# 딜 3: "갤럭시 S24 사전예약" → A 매칭 X, B 매칭 ✓
```

---

### 🟡 우선순위 4: 크롤러 자동화 (Celery)
**예상 소요 시간**: 3-4시간
**난이도**: 중
**의존성**: 키워드 매칭 엔진 완료 후

#### 구현 범위
**파일 생성**:
- `backend/app/celery_app.py` - Celery 앱 초기화
- `backend/app/tasks/crawler.py` - 크롤링 태스크

**Celery Beat 스케줄**:
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

**크롤러 태스크**:
```python
@celery_app.task(bind=True, max_retries=3)
def run_ppomppu_crawler(self):
    try:
        crawler = PpomppuCrawler()
        deals = crawler.crawl_list()

        for deal_data in deals:
            # 중복 체크 (external_id)
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
        # 에러 로깅
        CrawlerError.log(source='ppomppu', error=str(exc))
        raise self.retry(exc=exc, countdown=60)
```

**실행 방법**:
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

### 🟢 우선순위 5: 다중 사이트 크롤러 확장
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

#### BaseCrawler 추상화
```python
class BaseCrawler(ABC):
    @abstractmethod
    def fetch_list(self, page: int = 1) -> List[Dict]:
        """목록 페이지 크롤링"""
        pass

    @abstractmethod
    def fetch_detail(self, url: str) -> Dict:
        """상세 페이지 크롤링"""
        pass

    def extract_images(self, html: str) -> List[str]:
        """이미지 URL 추출 (공통)"""
        pass

    def extract_links(self, text: str) -> List[str]:
        """상품 링크 추출 (공통)"""
        pass
```

---

## 📊 MVP 완성 체크리스트

### 백엔드 API (60% 완료)
- [x] 데이터베이스 스키마 설계 (100%)
- [x] 뽐뿌 크롤러 구현 (100%)
- [x] 딜 API 구현 (100%)
- [x] 사용자 인증 API (100%) ✅
- [ ] 키워드 관리 API (0%) ← **다음 작업**
- [ ] 북마크 API (0%)
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
  - 현재: Python enum 값은 "email"이지만 DB에는 "EMAIL"도 추가됨
  - 문제: 대소문자 불일치로 혼란 가능
  - 해결: Alembic 마이그레이션으로 통일
  ```sql
  -- 'EMAIL' 제거하고 'email'만 사용
  ALTER TYPE authprovider DROP VALUE 'EMAIL';
  ```

- [ ] **Alembic 마이그레이션 설정**
  - 현재: development 모드에서 자동 테이블 생성
  - 문제: 프로덕션 배포 시 스키마 변경 관리 불가
  - 해결: Alembic 초기화 및 마이그레이션 파일 생성
  ```bash
  cd backend
  alembic init alembic
  alembic revision --autogenerate -m "Initial schema"
  ```

### 🟡 중요도 중간
- [ ] **환경 변수 검증**
  - SECRET_KEY가 기본값("your-secret-key-here-change-in-production")이면 경고
  - 프로덕션 환경에서 필수 환경 변수 체크 (ENVIRONMENT, DATABASE_URL 등)

- [ ] **API Rate Limiting**
  - DDoS/Brute-force 공격 방지
  - slowapi 라이브러리 사용
  ```python
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)

  @app.post("/api/v1/users/login")
  @limiter.limit("5/minute")
  def login(...):
      pass
  ```

- [ ] **CORS origins 프로덕션 설정**
  - 현재: `CORS_ORIGINS = ["*"]` (모든 도메인 허용)
  - 프로덕션: 실제 프론트엔드 도메인만 허용
  ```python
  CORS_ORIGINS = [
      "https://dealmoa.app",
      "https://www.dealmoa.app"
  ]
  ```

### 🟢 추후 개선
- [ ] **Refresh Token 구현**
  - Access Token: 1시간 (짧게)
  - Refresh Token: 30일 (Redis 저장)
  - `/api/v1/users/refresh` 엔드포인트

- [ ] **소셜 로그인**
  - Kakao OAuth 연동
  - Google OAuth 연동
  - Apple Sign In 연동

- [ ] **비밀번호 재설정**
  - `/api/v1/users/forgot-password` - 이메일 전송
  - `/api/v1/users/reset-password` - 새 비밀번호 설정
  - 이메일 발송 서비스 필요 (SendGrid, AWS SES)

- [ ] **프로필 이미지 업로드**
  - S3 버킷 연동
  - 이미지 리사이징 (Pillow)
  - CDN 연동

---

## 📅 예상 일정

### Day 1 (✅ 완료)
- ✅ 딜 API 엔드포인트
- ✅ 사용자 인증 시스템

### Day 2 (다음)
- 키워드 관리 API (2-3시간)
- 북마크 API (1-2시간)
- 키워드 매칭 엔진 시작 (2시간)

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

## 📚 참고 문서

- **CLAUDE.md**: 프로젝트 개요 및 기술 스택
- **DATABASE_SCHEMA_IMPLEMENTATION_SUMMARY.md**: DB 스키마 상세
- **CRAWLER_README.md**: 크롤러 사용법
- **DEAL_API_IMPLEMENTATION_SUMMARY.md**: 딜 API 구현 세부사항

---

**작성자**: Claude Sonnet 4.5
**최종 수정**: 2026-02-12 22:30
