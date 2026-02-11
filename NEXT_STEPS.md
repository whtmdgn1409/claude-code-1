# 다음 작업 단계 (Next Steps)

**작성일**: 2026-02-12
**현재 진행률**: 45% (MVP 기준)

---

## 📌 오늘 완료한 작업 (2026-02-12)

✅ **딜 API 엔드포인트 구현** (100% 완료)
- 5개 엔드포인트 구현 및 테스트 완료
- 한글 검색 기능 정상 동작
- 성능 목표 달성 (< 50ms ~ 200ms)
- Swagger UI 문서 자동 생성

---

## 🎯 다음 작업 우선순위

### 우선순위 1: 사용자 인증 및 API (필수) ⭐⭐⭐

**예상 소요 시간**: 4-6시간
**난이도**: 중
**의존성**: 없음 (즉시 시작 가능)

#### 1.1 JWT 인증 시스템 구현
**파일**: `backend/app/utils/auth.py`

```python
# 구현 내용
- create_access_token(): JWT 토큰 생성
- verify_token(): 토큰 검증
- get_current_user(): 현재 로그인 사용자 가져오기
- hash_password(): 비밀번호 해싱
- verify_password(): 비밀번호 검증
```

**필요 라이브러리**:
- python-jose (이미 설치됨)
- passlib[bcrypt] (이미 설치됨)

#### 1.2 사용자 API 구현
**파일**: `backend/app/api/users.py`

**엔드포인트**:
```
POST   /api/v1/users/register      # 회원가입
POST   /api/v1/users/login          # 로그인 (JWT 토큰 반환)
GET    /api/v1/users/me             # 내 정보 조회
PUT    /api/v1/users/me             # 내 정보 수정
PUT    /api/v1/users/me/settings    # 알림 설정 (DND)
DELETE /api/v1/users/me             # 회원 탈퇴
```

**주요 기능**:
- 이메일/비밀번호 기반 회원가입
- JWT 토큰 발급 및 인증
- DND 시간 설정 (예: 23:00-07:00)
- 사용자 프로필 관리

**스키마**: `backend/app/schemas/user.py` (이미 존재)

---

### 우선순위 2: 키워드 API (필수) ⭐⭐⭐

**예상 소요 시간**: 2-3시간
**난이도**: 하
**의존성**: 사용자 인증 완료 후

**파일**: `backend/app/api/keywords.py`

**엔드포인트**:
```
GET    /api/v1/keywords              # 내 키워드 목록
POST   /api/v1/keywords              # 키워드 추가
PUT    /api/v1/keywords/{id}         # 키워드 수정 (활성화/비활성화)
DELETE /api/v1/keywords/{id}         # 키워드 삭제
GET    /api/v1/keywords/{id}/matches # 키워드 매칭 딜 목록
```

**주요 기능**:
- 최대 20개 키워드 제한
- Include/Exclude 타입 지원
- 키워드별 매칭 딜 수 표시
- 활성화/비활성화 토글

**비즈니스 로직**:
```python
# 키워드 추가 시
if user.keywords.count() >= 20:
    raise HTTPException(400, "최대 20개까지만 등록 가능합니다")

# 중복 체크
if keyword_text in [k.keyword for k in user.keywords]:
    raise HTTPException(400, "이미 등록된 키워드입니다")
```

---

### 우선순위 3: 북마크 API (필수) ⭐⭐

**예상 소요 시간**: 1-2시간
**난이도**: 하
**의존성**: 사용자 인증 완료 후

**파일**: `backend/app/api/bookmarks.py`

**엔드포인트**:
```
GET    /api/v1/bookmarks        # 내 북마크 목록
POST   /api/v1/bookmarks        # 북마크 추가 (deal_id)
DELETE /api/v1/bookmarks/{id}   # 북마크 삭제
```

**주요 기능**:
- 딜 북마크 저장
- 북마크 목록 조회 (페이징)
- 중복 북마크 방지

---

### 우선순위 4: 키워드 매칭 엔진 (핵심 로직) ⭐⭐⭐

**예상 소요 시간**: 4-6시간
**난이도**: 중상
**의존성**: 사용자 & 키워드 API 완료 후

**파일**: `backend/app/services/keyword_matcher.py`

**구현 함수**:

#### 4.1 딜 → 사용자 매칭
```python
def match_deal_to_users(deal: Deal, db: Session) -> List[User]:
    """
    새로운 딜이 등록되면, 어떤 사용자에게 알림을 보낼지 찾기

    로직:
    1. deal.keywords에서 키워드 목록 가져오기
    2. user_keywords 테이블에서 매칭되는 사용자 찾기
    3. Include/Exclude 로직 적용
    4. DND 시간 체크 (현재 시간이 DND 범위면 제외)
    5. 중복 제거 후 반환

    성능 목표: < 100ms
    """
```

#### 4.2 사용자 → 딜 매칭
```python
def match_user_to_deals(user: User, db: Session) -> List[Deal]:
    """
    사용자가 앱을 열었을 때, 추천할 딜 목록

    로직:
    1. user.keywords에서 키워드 목록 가져오기
    2. deal_keywords 테이블에서 매칭되는 딜 찾기
    3. Exclude 키워드가 포함된 딜은 제외
    4. hot_score 기준 정렬
    5. 최근 7일 이내 딜만 반환

    성능 목표: < 200ms
    """
```

**테스트 시나리오**:
```python
# 사용자 A: 키워드 "갤럭시", "삼성" (Include)
# 사용자 B: 키워드 "갤럭시" (Include), "버즈" (Exclude)

# 딜 1: "갤럭시S24 사전예약" → A, B 모두 매칭
# 딜 2: "갤럭시 버즈3 출시" → A만 매칭 (B는 Exclude)
```

---

### 우선순위 5: 나머지 크롤러 구현 (병렬 진행 가능) ⭐

**예상 소요 시간**: 크롤러당 2-3시간 (총 8-12시간)
**난이도**: 중하
**의존성**: 없음 (독립적으로 진행 가능)

#### 5.1 루리웹 크롤러
- URL: https://bbs.ruliweb.com/market/board/1020
- 특징: 게임/IT 중심, 이미지 썸네일 풍부

#### 5.2 퀘이사존 크롤러
- URL: https://quasarzone.com/bbs/qb_saleinfo
- 특징: PC 하드웨어 전문, 가격 정보 상세

#### 5.3 펨코 크롤러
- URL: https://www.fmkorea.com/hotdeal
- 특징: 다양한 카테고리, 트래픽 많음

#### 5.4 딜바다 크롤러
- URL: https://www.dealbada.com
- 특징: 전문 딜 사이트, 체계적인 구조

**구현 순서** (권장):
1. 루리웹 → 2. 퀘이사존 → 3. 펨코 → 4. 딜바다

---

### 우선순위 6: 푸시 알림 서비스 (핵심 기능) ⭐⭐⭐

**예상 소요 시간**: 6-8시간
**난이도**: 중상
**의존성**: 키워드 매칭 엔진 완료 후

**파일**: `backend/app/services/notification_service.py`

**구현 내용**:
```python
class NotificationService:
    def send_deal_notification(user: User, deal: Deal):
        """
        딜 알림 전송
        1. DND 시간 체크
        2. FCM/APNS 메시지 생성
        3. 푸시 전송
        4. notifications 테이블 기록
        """

    def send_batch_notifications(notifications: List):
        """일괄 알림 전송 (성능 최적화)"""
```

**필요 라이브러리**:
```bash
pip install firebase-admin
```

**Firebase 설정 필요**:
- Firebase 프로젝트 생성
- 서비스 계정 키 JSON 다운로드
- `.env`에 Firebase 설정 추가

---

### 우선순위 7: 스케줄러 설정 (자동화) ⭐⭐

**예상 소요 시간**: 4-6시간
**난이도**: 중
**의존성**: 크롤러 & 알림 서비스 완료 후

**파일**: `backend/app/scheduler/tasks.py`

**Celery 태스크**:
```python
# 5분마다 크롤링
@celery.task
def crawl_all_sources():
    for source in ["ppomppu", "ruliweb", "fmkorea", "quasarzone", "dealbada"]:
        run_crawler(source)

# 새 딜 발견 시 즉시 알림
@celery.task
def process_new_deal(deal_id):
    deal = get_deal(deal_id)
    matched_users = keyword_matcher.match_deal_to_users(deal)
    for user in matched_users:
        send_deal_notification(user, deal)
```

---

## 📅 권장 작업 일정

### Day 1 (오늘 완료 ✅)
- ✅ 딜 API 엔드포인트 구현
- ✅ 검색 기능 구현
- ✅ Swagger UI 문서

### Day 2-3 (다음 작업)
- 사용자 인증 시스템 (JWT)
- 사용자 API 구현
- 키워드 API 구현
- 북마크 API 구현

### Day 4-5
- 키워드 매칭 엔진 구현
- 매칭 알고리즘 테스트

### Day 6-7
- 푸시 알림 서비스 구현
- Firebase 연동

### Day 8-10
- 나머지 크롤러 구현 (4개)
- 크롤러 테스트

### Day 11-12
- 스케줄러 설정 (Celery)
- 전체 통합 테스트

---

## 🧪 테스트 체크리스트

### API 테스트
- [ ] 사용자 회원가입/로그인
- [ ] JWT 토큰 인증
- [ ] 키워드 CRUD (20개 제한 확인)
- [ ] 북마크 CRUD
- [ ] 키워드 매칭 정확도
- [ ] 딜 검색 성능 (< 200ms)

### 크롤러 테스트
- [ ] 루리웹 크롤링 성공률 > 95%
- [ ] 퀘이사존 크롤링 성공률 > 95%
- [ ] 펨코 크롤링 성공률 > 95%
- [ ] 딜바다 크롤링 성공률 > 95%
- [ ] 에러 로깅 동작

### 알림 테스트
- [ ] DND 시간 체크 동작
- [ ] FCM 푸시 전송 성공
- [ ] 알림 이력 저장
- [ ] Include/Exclude 로직 정확도

---

## 📝 참고 문서

- **DEVELOPMENT_STATUS.md**: 전체 프로젝트 진행 현황
- **CLAUDE.md**: 프로젝트 개요 및 기술 스택
- **DATABASE_SCHEMA_IMPLEMENTATION_SUMMARY.md**: DB 스키마 상세
- **CRAWLER_README.md**: 크롤러 사용법

---

## 🚀 빠른 시작 (Quick Start)

```bash
# 1. Docker 컨테이너 시작
docker-compose up -d

# 2. 가상환경 활성화
cd backend
source venv/bin/activate

# 3. 서버 실행
uvicorn app.main:app --reload

# 4. API 문서 확인
open http://localhost:8000/docs
```

---

**작성자**: Claude Sonnet 4.5
**최종 수정**: 2026-02-12
