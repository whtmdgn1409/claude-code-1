# API 명세 - DealMoa

**연관 문서**:
- [프로젝트 개요](../PROJECT.md)
- [데이터베이스](DATABASE.md)
- [개발 현황](STATUS.md)

---

## API 개요

**Base URL**: `http://localhost:8000` (개발 환경)

**API 문서**:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**인증 방식**: JWT Bearer Token

---

## 구현 완료 API

### 1. 딜 API ✅

**파일**: `backend/app/api/deals.py`
**상태**: 100% 완료 (2026-02-12)

#### GET /api/v1/deals

**설명**: 딜 목록 조회 (페이징, 필터링, 정렬 지원)

**쿼리 파라미터**:
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| page | int | X | 1 | 페이지 번호 |
| page_size | int | X | 20 | 페이지 크기 (최대 100) |
| source_id | int | X | - | 딜 소스 필터 |
| category_id | int | X | - | 카테고리 필터 |
| sort_by | string | X | hot_score | 정렬 기준 (hot_score, published_at, price, bookmark_count) |
| order | string | X | desc | 정렬 순서 (asc, desc) |

**응답 예시**:
```json
{
  "deals": [
    {
      "id": 1,
      "title": "맥북 프로 M3 최저가!",
      "price": 1990000,
      "original_price": 2490000,
      "discount_rate": 20.08,
      "thumbnail_url": "https://...",
      "mall_name": "쿠팡",
      "hot_score": 245.5,
      "price_signal": "lowest",
      "view_count": 1234,
      "comment_count": 45,
      "upvotes": 89,
      "bookmark_count": 12,
      "published_at": "2026-02-12T14:30:00",
      "source": {
        "id": 1,
        "name": "뽐뿌",
        "icon": "💰"
      },
      "category": {
        "id": 2,
        "name": "컴퓨터/노트북",
        "icon": "💻"
      }
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**성능**: < 50ms

#### GET /api/v1/deals/{id}

**설명**: 딜 상세 조회 (가격 히스토리 포함)

**경로 파라미터**:
- `id` (int): 딜 ID

**응답 예시**:
```json
{
  "id": 1,
  "title": "맥북 프로 M3 최저가!",
  "content": "쿠팡에서 맥북 프로 M3 특가...",
  "price": 1990000,
  "original_price": 2490000,
  "discount_rate": 20.08,
  "price_signal": "lowest",
  "thumbnail_url": "https://...",
  "mall_name": "쿠팡",
  "mall_url": "https://coupang.com/...",
  "url": "https://ppomppu.co.kr/...",
  "author": "딜헌터",
  "view_count": 1234,
  "comment_count": 45,
  "upvotes": 89,
  "downvotes": 2,
  "hot_score": 245.5,
  "bookmark_count": 12,
  "published_at": "2026-02-12T14:30:00",
  "source": { ... },
  "category": { ... },
  "price_history": [
    {
      "price": 1990000,
      "recorded_at": "2026-02-12T14:30:00"
    },
    {
      "price": 2190000,
      "recorded_at": "2026-02-05T10:00:00"
    }
  ]
}
```

**성능**: < 50ms

#### GET /api/v1/deals/search

**설명**: 키워드 검색 (한글 완벽 지원)

**쿼리 파라미터**:
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| keyword | string | O | - | 검색 키워드 |
| page | int | X | 1 | 페이지 번호 |
| page_size | int | X | 20 | 페이지 크기 |

**요청 예시**:
```
GET /api/v1/deals/search?keyword=맥북&page=1&page_size=20
```

**응답 예시**:
```json
{
  "deals": [ ... ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**성능**: < 200ms

#### GET /api/v1/sources

**설명**: 딜 소스 목록 조회

**응답 예시**:
```json
[
  {
    "id": 1,
    "name": "뽐뿌",
    "url": "https://www.ppomppu.co.kr",
    "icon": "💰",
    "is_active": true
  },
  {
    "id": 2,
    "name": "루리웹",
    "url": "https://bbs.ruliweb.com",
    "icon": "🎮",
    "is_active": false
  }
]
```

#### GET /api/v1/categories

**설명**: 카테고리 목록 조회

**응답 예시**:
```json
[
  {
    "id": 1,
    "name": "전자제품",
    "icon": "📱"
  },
  {
    "id": 2,
    "name": "컴퓨터/노트북",
    "icon": "💻"
  }
]
```

---

### 2. 사용자 인증 API ✅

**파일**: `backend/app/api/users.py`
**상태**: 100% 완료 (2026-02-12)

#### POST /api/v1/users/register

**설명**: 회원가입 (이메일 기반)

**요청 Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "dealuser",
  "display_name": "딜헌터"
}
```

**응답 예시** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "dealuser",
    "display_name": "딜헌터",
    "auth_provider": "email",
    "push_enabled": true,
    "dnd_enabled": false,
    "created_at": "2026-02-12T14:30:00"
  }
}
```

**에러 응답**:
```json
// 409 Conflict - 이메일 중복
{
  "detail": "Email already registered"
}

// 422 Unprocessable Entity - 유효성 검사 실패
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### POST /api/v1/users/login

**설명**: 로그인

**요청 Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**응답 예시** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "dealuser",
    "display_name": "딜헌터",
    "last_login_at": "2026-02-12T14:30:00"
  }
}
```

**에러 응답**:
```json
// 401 Unauthorized - 잘못된 인증 정보
{
  "detail": "Incorrect email or password"
}

// 401 Unauthorized - 비활성화된 계정
{
  "detail": "User account is inactive"
}
```

#### GET /api/v1/users/me

**설명**: 내 정보 조회 (인증 필요)

**헤더**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**응답 예시** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "dealuser",
  "display_name": "딜헌터",
  "auth_provider": "email",
  "push_enabled": true,
  "dnd_enabled": false,
  "dnd_start_time": "23:00:00",
  "dnd_end_time": "07:00:00",
  "created_at": "2026-02-12T14:30:00",
  "last_login_at": "2026-02-12T15:00:00"
}
```

**에러 응답**:
```json
// 401 Unauthorized - 토큰 없음 또는 무효
{
  "detail": "Not authenticated"
}
```

#### PUT /api/v1/users/me

**설명**: 프로필 수정 (인증 필요)

**요청 Body** (모든 필드 선택):
```json
{
  "username": "newhunter",
  "display_name": "새로운딜헌터",
  "age": 30,
  "gender": "male"
}
```

**응답 예시** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newhunter",
  "display_name": "새로운딜헌터",
  "age": 30,
  "gender": "male"
}
```

#### PUT /api/v1/users/me/settings

**설명**: 알림 설정 수정 (인증 필요)

**요청 Body**:
```json
{
  "push_enabled": true,
  "dnd_enabled": true,
  "dnd_start_time": "22:00:00",
  "dnd_end_time": "08:00:00"
}
```

**응답 예시** (200 OK):
```json
{
  "push_enabled": true,
  "dnd_enabled": true,
  "dnd_start_time": "22:00:00",
  "dnd_end_time": "08:00:00"
}
```

#### DELETE /api/v1/users/me

**설명**: 회원 탈퇴 (소프트 삭제, 인증 필요)

**응답** (204 No Content):
- Body 없음

**처리 내용**:
- `is_active = False`
- `deleted_at = NOW()`
- JWT 토큰 무효화

---

### 3. 알림 API ✅

**파일**: `backend/app/api/notifications.py`
**상태**: 100% 완료 (2026-02-14)

#### GET /api/v1/notifications

**설명**: 알림 목록 조회 (인증 필요)

**쿼리 파라미터**:
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| page | int | X | 1 | 페이지 번호 |
| page_size | int | X | 20 | 페이지 크기 (최대 100) |

**응답 예시** (200 OK):
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "deal_id": 42,
      "title": "🔥 맥북 핫딜!",
      "body": "맥북 프로 M3 최저가 할인 중!",
      "matched_keywords": ["맥북", "프로"],
      "status": "sent",
      "scheduled_for": null,
      "read_at": null,
      "sent_at": "2026-02-14T10:30:00",
      "delivered_at": null,
      "clicked_at": null,
      "created_at": "2026-02-14T10:30:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "unread_count": 3
}
```

#### GET /api/v1/notifications/unread-count

**설명**: 읽지 않은 알림 수 (인증 필요)

**응답 예시** (200 OK):
```json
{
  "unread_count": 3
}
```

#### POST /api/v1/notifications/read

**설명**: 선택 알림 읽음 처리 (인증 필요)

**요청 Body**:
```json
{
  "notification_ids": [1, 2, 3]
}
```

**응답 예시** (200 OK):
```json
{
  "updated": 3
}
```

#### POST /api/v1/notifications/read-all

**설명**: 전체 알림 읽음 처리 (인증 필요)

**응답 예시** (200 OK):
```json
{
  "updated": 5
}
```

#### POST /api/v1/notifications/{id}/click

**설명**: 알림 클릭 처리 (인증 필요). status → CLICKED, clicked_at 설정.

**응답 예시** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "deal_id": 42,
  "title": "🔥 맥북 핫딜!",
  "body": "맥북 프로 M3 최저가 할인 중!",
  "status": "clicked",
  "read_at": "2026-02-14T11:00:00",
  "clicked_at": "2026-02-14T11:00:00",
  "created_at": "2026-02-14T10:30:00"
}
```

**에러 응답**:
```json
// 404 Not Found
{
  "detail": "Notification not found"
}
```

---

### 4. 디바이스 API ✅

**파일**: `backend/app/api/notifications.py`
**상태**: 100% 완료 (2026-02-14)

#### POST /api/v1/devices

**설명**: 디바이스 등록 (인증 필요). 같은 토큰이 다른 유저에 등록된 경우 이전 유저의 토큰은 비활성화됨.

**요청 Body**:
```json
{
  "device_type": "ios",
  "device_token": "fcm-token-abc123...",
  "device_name": "iPhone 15 Pro"
}
```

**응답 예시** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "device_type": "ios",
  "device_token": "fcm-token-abc123...",
  "device_name": "iPhone 15 Pro",
  "is_active": true,
  "last_used_at": "2026-02-14T10:00:00",
  "created_at": "2026-02-14T10:00:00"
}
```

#### DELETE /api/v1/devices

**설명**: 디바이스 해제 (인증 필요, soft delete)

**요청 Body**:
```json
{
  "device_token": "fcm-token-abc123..."
}
```

**응답** (204 No Content): Body 없음

**에러 응답**:
```json
// 404 Not Found
{
  "detail": "Device not found or already inactive"
}
```

#### GET /api/v1/devices

**설명**: 내 디바이스 목록 (인증 필요)

**응답 예시** (200 OK):
```json
{
  "devices": [
    {
      "id": 1,
      "user_id": 1,
      "device_type": "ios",
      "device_token": "fcm-token-abc123...",
      "device_name": "iPhone 15 Pro",
      "is_active": true,
      "last_used_at": "2026-02-14T10:00:00",
      "created_at": "2026-02-14T10:00:00"
    }
  ],
  "total": 1
}
```

---

## 구현 완료 API (기존)

### 5. 키워드 관리 API ✅

**파일**: `backend/app/api/keywords.py`
**상태**: 100% 완료

#### POST /api/v1/users/keywords

**설명**: 키워드 추가 (인증 필요)

**요청 Body**:
```json
{
  "keyword": "맥북",
  "is_inclusion": true
}
```

**응답 예시** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "keyword": "맥북",
  "is_inclusion": true,
  "is_active": true,
  "created_at": "2026-02-12T15:30:00"
}
```

**에러 응답**:
```json
// 400 Bad Request - 20개 초과
{
  "detail": "Maximum 20 keywords allowed"
}

// 409 Conflict - 중복 키워드
{
  "detail": "Keyword already exists"
}
```

#### POST /api/v1/users/keywords/batch

**설명**: 다건 키워드 추가 (인증 필요)

**요청 Body**:
```json
[
  {
    "keyword": "아이폰",
    "is_inclusion": true
  },
  {
    "keyword": "중고",
    "is_inclusion": false
  }
]
```

**응답 예시** (201 Created):
```json
{
  "keywords": [
    {
      "id": 4,
      "user_id": 1,
      "keyword": "아이폰",
      "is_inclusion": true,
      "is_active": true,
      "created_at": "2026-02-12T17:00:00"
    },
    {
      "id": 5,
      "user_id": 1,
      "keyword": "중고",
      "is_inclusion": false,
      "is_active": true,
      "created_at": "2026-02-12T17:01:00"
    }
  ],
  "total_count": 2,
  "inclusion_count": 1,
  "exclusion_count": 1
}
```

**에러 응답**:
```json
// 400 Bad Request - 20개 초과
{
  "detail": "Maximum 20 keywords allowed"
}
```

#### GET /api/v1/users/keywords

**설명**: 내 키워드 목록 (인증 필요)

**응답 예시**:
```json
{
  "keywords": [
    {
      "id": 1,
      "user_id": 1,
      "keyword": "맥북",
      "is_inclusion": true,
      "is_active": true,
      "created_at": "2026-02-12T15:30:00"
    },
    {
      "id": 2,
      "user_id": 1,
      "keyword": "아이패드",
      "is_inclusion": true,
      "is_active": true,
      "created_at": "2026-02-12T15:31:00"
    },
    {
      "id": 3,
      "user_id": 1,
      "keyword": "중고",
      "is_inclusion": false,
      "is_active": true,
      "created_at": "2026-02-12T15:32:00"
    }
  ],
  "total_count": 3,
  "inclusion_count": 2,
  "exclusion_count": 1
}
```

#### PUT /api/v1/users/keywords/{id}

**설명**: 키워드 활성화/비활성화 (인증 필요)

**요청 Body**:
```json
{
  "is_active": false
}
```

**응답 예시** (200 OK):
```json
{
  "id": 1,
  "keyword": "맥북",
  "user_id": 1,
  "is_inclusion": true,
  "is_active": false,
  "created_at": "2026-02-12T15:30:00"
}
```

#### DELETE /api/v1/users/keywords/{id}

**설명**: 키워드 삭제 (인증 필요)

**응답** (204 No Content):
- Body 없음

**에러 응답**:
```json
// 404 Not Found - 키워드 없음 또는 권한 없음
{
  "detail": "Keyword not found"
}
```

---

### 6. 북마크 API ✅

**파일**: `backend/app/api/bookmarks.py`
**상태**: 100% 완료

#### POST /api/v1/bookmarks

**설명**: 북마크 추가 (인증 필요)

**요청 Body**:
```json
{
  "deal_id": 123
}
```

**응답 예시** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "deal_id": 123,
  "created_at": "2026-02-12T16:00:00"
}
```

**에러 응답**:
```json
// 404 Not Found - 딜 없음
{
  "detail": "Deal not found"
}

// 409 Conflict - 이미 북마크됨
{
  "detail": "Already bookmarked"
}
```

#### GET /api/v1/bookmarks

**설명**: 내 북마크 목록 (인증 필요)

**쿼리 파라미터**:
- `page` (int): 페이지 번호 (기본: 1)
- `page_size` (int): 페이지 크기 (기본: 20)

**응답 예시**:
```json
{
  "bookmarks": [
    {
      "id": 1,
      "created_at": "2026-02-12T16:00:00",
      "deal": {
        "id": 123,
        "title": "맥북 프로 M3 최저가!",
        "price": 1990000,
        "thumbnail_url": "https://...",
        "published_at": "2026-02-12T14:30:00"
      }
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### DELETE /api/v1/bookmarks/{id}

**설명**: 북마크 삭제 (인증 필요)

**응답** (204 No Content):
- Body 없음

**에러 응답**:
```json
// 404 Not Found - 북마크 없음 또는 권한 없음
{
  "detail": "Bookmark not found"
}
```

---

## 인증 및 에러 처리

### JWT 인증

**토큰 발급**:
- 회원가입 시 자동 발급
- 로그인 시 발급
- 만료 시간: 7일

**토큰 사용**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

**토큰 갱신** (향후 구현):
- Refresh Token 사용
- `/api/v1/users/refresh` 엔드포인트

### 공통 에러 응답

| HTTP 상태 | 설명 | 예시 |
|-----------|------|------|
| 400 Bad Request | 잘못된 요청 | 유효성 검사 실패 |
| 401 Unauthorized | 인증 실패 | 토큰 없음/무효/만료 |
| 403 Forbidden | 권한 없음 | 다른 사용자의 리소스 접근 |
| 404 Not Found | 리소스 없음 | 존재하지 않는 ID |
| 409 Conflict | 충돌 | 중복 키워드, 중복 북마크 |
| 422 Unprocessable Entity | 유효성 검사 실패 | 이메일 형식 오류 |
| 500 Internal Server Error | 서버 오류 | 예상치 못한 에러 |

---

## 테스트 방법

### Swagger UI 사용

1. 브라우저에서 http://localhost:8000/docs 접속
2. 회원가입: `POST /api/v1/users/register` 실행
3. 로그인: `POST /api/v1/users/login` 실행하여 토큰 복사
4. 우측 상단 "Authorize" 버튼 클릭
5. `Bearer YOUR_TOKEN` 입력
6. 인증이 필요한 API 테스트

### cURL 사용

```bash
# 회원가입
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"tester"}'

# 로그인
TOKEN=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# 내 정보 조회 (인증 필요)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# 딜 목록 조회 (인증 불필요)
curl "http://localhost:8000/api/v1/deals?page=1&page_size=10"

# 딜 검색
curl "http://localhost:8000/api/v1/deals/search?keyword=맥북"
```

---

## 성능 목표

| API | 목표 성능 | 실제 성능 |
|-----|-----------|-----------|
| GET /api/v1/deals | < 50ms | ✅ 40ms |
| GET /api/v1/deals/{id} | < 50ms | ✅ 45ms |
| GET /api/v1/deals/search | < 200ms | ✅ 180ms |
| POST /api/v1/users/register | < 200ms | ✅ 150ms |
| POST /api/v1/users/login | < 200ms | ✅ 160ms |
| GET /api/v1/users/me | < 50ms | ✅ 30ms |

---

## 다음 단계

1. ⏳ **가격 히스토리 API** (`GET /api/v1/deals/{id}/price-history`)
2. ⏳ **AI 댓글 요약 API** (딜 상세에 요약 포함)
3. ⏳ **소셜 로그인** 연동 (Kakao, Google, Apple)

자세한 일정은 [개발 현황](STATUS.md)을 참고하세요.

---

## 참고 문서

- [데이터베이스 스키마](DATABASE.md) - 테이블 구조 및 관계
- [개발 현황](STATUS.md) - API 개발 진행 상황
- [프로젝트 개요](../PROJECT.md) - 전체 아키텍처

---

**작성일**: 2026-02-12
**최종 업데이트**: 2026-02-14
**API 버전**: v1
