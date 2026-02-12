# 딜모아 (DealMoa)

**한국 주요 커뮤니티의 핫딜 정보를 실시간으로 수집하고 키워드 기반 푸시 알림을 제공하는 서비스**

---

## 🚀 빠른 시작

### 1. Docker 시작

```bash
docker-compose up -d
```

### 2. 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**API 문서**: http://localhost:8000/docs

### 3. 모바일 앱 (예정)

```bash
cd mobile
npm install
npm run ios     # iOS (macOS only)
npm run android # Android
```

---

## 📚 문서

- **[전체 문서](docs/README.md)** - 문서 네비게이션
- **[프로젝트 개요](docs/PROJECT.md)** - 서비스 소개 및 아키텍처
- **[Backend 문서](docs/backend/)** - 데이터베이스, 크롤러, API, 개발 현황
- **[개발 가이드](CLAUDE.md)** - Claude Code용 가이드

---

## 💻 기술 스택

### Backend
- **Language**: Python 3.13
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **ORM**: SQLAlchemy 2.0.46

### Mobile (예정)
- **Framework**: React Native 0.73
- **Language**: TypeScript

### DevOps
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git & GitHub

---

## 📊 개발 상황

**현재 진행률**: **60%** (MVP 기준)

**완료된 작업**:
- ✅ 데이터베이스 스키마 (15개 테이블)
- ✅ 뽐뿌 크롤러 구현
- ✅ 딜 API 엔드포인트 (5개)
- ✅ 사용자 인증 API (6개)

**다음 작업**:
- ⏳ 키워드 관리 API
- ⏳ 북마크 API
- ⏳ 키워드 매칭 엔진
- ⏳ 푸시 알림 서비스

**상세 현황**: [docs/backend/STATUS.md](docs/backend/STATUS.md)

---

## 🎯 핵심 기능

### MVP (Phase 1) - 진행 중 (60%)
- ✅ 다중 사이트 크롤링 (뽐뿌 완료, 4개 예정)
- ✅ 통합 딜 목록 보기
- ⏳ 키워드 기반 푸시 알림

### Enhancement (Phase 2)
- 가격 비교 (🟢역대가 / 🟡평균가 / 🔴비쌈)
- AI 댓글 요약
- 자동 카테고리 분류

### Expansion (Phase 3)
- 인구통계 기반 추천 알고리즘
- 커뮤니티 기능

---

## 📝 프로젝트 구조

```
claude-code-1/
├── README.md              # 프로젝트 진입점 (현재 파일)
├── CLAUDE.md              # Claude Code용 개발 가이드
├── docs/                  # 전체 문서 폴더
│   ├── README.md          # 문서 네비게이션
│   ├── PROJECT.md         # 프로젝트 개요
│   └── backend/           # 백엔드 문서
│       ├── DATABASE.md    # 데이터베이스 스키마
│       ├── CRAWLERS.md    # 크롤러 가이드
│       ├── API.md         # API 명세
│       └── STATUS.md      # 개발 현황
├── backend/               # Python FastAPI 백엔드
│   ├── app/
│   │   ├── main.py        # FastAPI 엔트리포인트
│   │   ├── api/           # API 라우터
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   ├── crawlers/      # 사이트별 크롤러
│   │   └── utils/         # 유틸리티
│   └── requirements.txt
├── mobile/                # React Native 앱 (예정)
└── docker-compose.yml     # PostgreSQL, Redis 설정
```

---

## 🛠 개발 명령어

### Backend

```bash
cd backend

# 서버 실행
uvicorn app.main:app --reload

# 테스트 실행
pytest

# 코드 포맷팅
black app/

# 크롤러 실행
python -m scripts.run_ppomppu_crawler --pages 5
```

### Mobile (예정)

```bash
cd mobile

# 개발 서버 시작
npm start

# 테스트 실행
npm test

# 린트 검사
npm run lint
```

---

## 🌏 한국 시장 특화

- **타겟**: 20-40대 가성비 추구 소비자
- **언어**: 한국어 UI/콘텐츠
- **커뮤니티**: 뽐뿌, 루리웹, 펨코, 퀘이사존, 딜바다
- **소셜 로그인**: Kakao, Google, Apple

---

## 📞 문의 및 기여

**프로젝트 저장소**: https://github.com/whtmdgn1409/claude-code-1

**주요 문서**:
- [프로젝트 개요](docs/PROJECT.md)
- [데이터베이스](docs/backend/DATABASE.md)
- [크롤러 가이드](docs/backend/CRAWLERS.md)
- [API 명세](docs/backend/API.md)
- [개발 현황](docs/backend/STATUS.md)

---

**프로젝트 시작일**: 2026-02-10
**최종 업데이트**: 2026-02-12
**현재 상태**: Active Development (MVP Phase)
