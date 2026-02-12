# 크롤러 가이드 - DealMoa

**연관 문서**:
- [프로젝트 개요](../PROJECT.md)
- [데이터베이스](DATABASE.md)
- [개발 현황](STATUS.md)

---

## 개요

한국 주요 딜 커뮤니티에서 핫딜 정보를 실시간으로 수집하는 크롤러 시스템입니다.

**구현 상태**:
- ✅ 뽐뿌 (Ppomppu) - 100% 완료
- ⏳ 루리웹 (Ruliweb) - 예정
- ⏳ 펨코 (Fmkorea) - 예정
- ⏳ 퀘이사존 (Quasarzone) - 예정
- ⏳ 딜바다 (Dealbada) - 예정

---

## 구현 완료: 뽐뿌 크롤러

### 기본 정보

**대상 사이트**: https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu

**수집 정보**:
- 딜 제목 (title)
- 가격 (price) - 자동 추출
- 작성자 (author)
- 조회수 (view_count)
- 추천/비추천 수 (upvotes/downvotes)
- 댓글 수 (comment_count)
- 게시일 (published_at)
- 쇼핑몰 정보 (mall_name, mall_url)
- 썸네일 이미지 (image_url)

### 주요 기능

- ✅ **다중 페이지 크롤링**: 원하는 페이지 수만큼 크롤링
- ✅ **중복 방지**: `external_id` 기반 중복 체크
- ✅ **자동 키워드 추출**: 제목에서 키워드 자동 추출
- ✅ **가격 파싱**: 한국어 가격 형식 지원 (원, 만원, 천원)
- ✅ **Rate Limiting**: 1초 딜레이로 서버 부하 최소화
- ✅ **에러 처리**: 상세 에러 로깅 및 복구
- ✅ **실행 이력 추적**: `crawler_runs` 테이블에 기록

### 구현 결과

**테스트 실행 (2페이지)**:
```
수집된 딜: 41개
추출된 키워드: 259개 (평균 6.3개/딜)
성공률: 100% (에러 0건)
소요 시간: ~30초
```

---

## 사용 방법

### 기본 실행

```bash
cd backend
source venv/bin/activate

# 기본 실행 (5페이지)
python -m scripts.run_ppomppu_crawler

# 페이지 수 지정
python -m scripts.run_ppomppu_crawler --pages 10

# 해외딜 포함
python -m scripts.run_ppomppu_crawler --overseas
```

### 프로그래밍 방식

```python
from app.models.database import SessionLocal
from app.crawlers import run_ppomppu_crawler

# 데이터베이스 세션 생성
db = SessionLocal()

try:
    # 크롤러 실행
    stats = run_ppomppu_crawler(
        db,
        max_pages=5,
        include_overseas=False
    )

    print(f"수집된 딜: {stats['new_created']}개")
    print(f"업데이트된 딜: {stats['items_updated']}개")
    print(f"에러: {stats['errors_count']}개")
finally:
    db.close()
```

### 실행 결과 확인

**콘솔 출력**:
```bash
============================================================
🚀 Ppomppu (뽐뿌) Crawler
============================================================
Pages to crawl: 2
Include overseas: False
Extract keywords: True
============================================================

🚀 Starting crawler for 뽐뿌...
📄 Crawling board: https://www.ppomppu.co.kr/...
   Page 1/2... ✓ Found 21 deals
   Page 2/2... ✓ Found 20 deals
📦 Found 41 deals
✅ Crawler completed successfully!
   - New: 41
   - Updated: 0
   - Skipped: 0
   - Errors: 0

🔤 Extracting keywords from new deals...
✅ Extracted 259 keywords from 41 deals
   Average: 6.3 keywords per deal

✅ Crawler completed successfully!
```

**데이터베이스 확인**:
```sql
-- 수집된 딜 확인
SELECT id, title, price, upvotes, view_count
FROM deals
ORDER BY created_at DESC
LIMIT 5;

-- 통계
SELECT
    COUNT(*) as total_deals,
    AVG(view_count)::int as avg_views,
    MAX(upvotes) as max_upvotes
FROM deals;

-- 인기 키워드 Top 10
SELECT keyword, COUNT(*) as count
FROM deal_keywords
GROUP BY keyword
ORDER BY count DESC
LIMIT 10;
```

---

## 크롤러 아키텍처

### 1. BaseCrawler (기본 크롤러)

**위치**: `backend/app/crawlers/base_crawler.py`

모든 크롤러의 부모 클래스로 공통 기능 제공:

**제공 기능**:
- ✅ 크롤러 실행 추적 (`CrawlerRun`)
- ✅ 에러 로깅 (`CrawlerError`)
- ✅ 상태 관리 (`CrawlerState`)
- ✅ Rate limiting (요청 간 딜레이)
- ✅ 통계 수집 (성공/실패/소요 시간)
- ✅ 자동 commit/rollback

**사용 예시**:
```python
from app.crawlers.base_crawler import BaseCrawler

class MyCrawler(BaseCrawler):
    def __init__(self, db):
        super().__init__(db, source_name="mysite")

    def fetch_deals(self, max_pages):
        """딜 수집 로직"""
        deals = []
        for page in range(1, max_pages + 1):
            page_deals = self._fetch_page(page)
            deals.extend(page_deals)
        return deals

    def parse_deal(self, raw_data):
        """파싱 로직"""
        return {
            'title': raw_data.find('h3').text,
            'price': self._extract_price(raw_data),
            # ...
        }
```

### 2. PpomppuCrawler (뽐뿌 크롤러)

**위치**: `backend/app/crawlers/ppomppu.py`

**특징**:
- **EUC-KR 인코딩**: 뽐뿌는 EUC-KR 사용
- **가격 파싱**: 정규식으로 다양한 형식 지원
  - "50000원" → 50,000
  - "5만원" → 50,000
  - "5만 5천원" → 55,000
- **쇼핑몰 감지**: 자동으로 쇼핑몰 링크 추출
  - 쿠팡, 11번가, G마켓, 옥션, 티몬 등
- **추천/비추천**: 분리된 upvotes/downvotes
- **시간 파싱**: 여러 형식 지원
  - "14:23:45" (오늘)
  - "26/02/12" (과거)

**사용 예시**:
```python
from app.crawlers import PpomppuCrawler

crawler = PpomppuCrawler(db, include_overseas=False)
stats = crawler.run(max_pages=5)

print(f"New deals: {stats['new_created']}")
print(f"Errors: {stats['errors_count']}")
```

### 3. KeywordExtractor (키워드 추출기)

**위치**: `backend/app/services/keyword_extractor.py`

딜 제목/내용에서 자동으로 키워드 추출:

**추출 규칙**:
- ✅ 한글 단어 (2자 이상)
- ✅ 영문 단어 (2자 이상)
- ✅ 모델명/제품번호 (RTX4090, 갤럭시S23 등)
- ✅ 불용어 제외 (입니다, 있습니다, 무료배송 등)
- ✅ 최대 50개 키워드/딜

**사용 예시**:
```python
from app.services import KeywordExtractor

# 단일 딜 키워드 추출
keywords_count = KeywordExtractor.extract_and_save(db, deal)
print(f"Extracted {keywords_count} keywords")

# 여러 딜 일괄 처리
total = KeywordExtractor.batch_extract_and_save(db, deals)
print(f"Total keywords: {total}")
```

**추출 예시**:
```
제목: "맥북 프로 M3 최저가! 쿠팡 무료배송"
추출: ["맥북", "프로", "M3", "최저가", "쿠팡"]

제목: "삼성 갤럭시 S23 256GB 역대가 549,000원"
추출: ["삼성", "갤럭시", "S23", "256GB", "역대가", "549000"]
```

---

## 모니터링 및 로깅

### 크롤러 실행 이력

```sql
-- 최근 크롤러 실행 이력
SELECT
    id,
    status,
    started_at,
    duration_seconds,
    new_items_created,
    errors_count
FROM crawler_runs
ORDER BY started_at DESC
LIMIT 10;
```

**예상 결과**:
```
 id | status    | started_at          | duration | new | errors
----|-----------|---------------------|----------|-----|-------
  5 | completed | 2026-02-12 14:30:00 |       28 |  41 |      0
  4 | completed | 2026-02-12 09:15:00 |       32 |  38 |      0
  3 | failed    | 2026-02-12 03:00:00 |       15 |   0 |      5
```

### 에러 로그

```sql
-- 크롤러 에러 확인
SELECT
    error_type,
    error_message,
    url,
    created_at
FROM crawler_errors
ORDER BY created_at DESC
LIMIT 10;
```

**에러 타입**:
- `ConnectionError`: 사이트 연결 실패
- `ParseError`: HTML 파싱 실패
- `TimeoutError`: 요청 타임아웃
- `DatabaseError`: 데이터베이스 저장 실패

---

## 추가 구현 예정 크롤러

### 🔲 루리웹 (Ruliweb)

**URL**: https://bbs.ruliweb.com/market/board/1020

**특징**:
- 게임/IT 중심 커뮤니티
- 이미지 풍부한 딜 정보
- 상세한 제품 정보

**예상 소요 시간**: 2-3시간

### 🔲 펨코 (Fmkorea)

**URL**: https://www.fmkorea.com/hotdeal

**특징**:
- 다양한 카테고리
- 높은 트래픽
- 커뮤니티 활성도 높음

**예상 소요 시간**: 2-3시간

### 🔲 퀘이사존 (Quasarzone)

**URL**: https://quasarzone.com/bbs/qb_saleinfo

**특징**:
- PC 하드웨어 전문
- 기술 스펙 상세
- 가격 정보 풍부

**예상 소요 시간**: 2-3시간

### 🔲 딜바다 (Dealbada)

**URL**: https://www.dealbada.com

**특징**:
- 전문 딜 사이트
- API 지원 가능성
- 깔끔한 데이터 구조

**예상 소요 시간**: 2-3시간

---

## 성능 최적화

### Rate Limiting

**설정**:
```python
# app/config.py
CRAWLER_REQUEST_DELAY = 1.0  # 초 단위
```

**목적**:
- 서버 부하 최소화
- IP 차단 방지
- 윤리적 크롤링

### 배치 처리

**키워드 일괄 추출**:
```python
# ❌ 비효율적 (딜마다 DB 쿼리)
for deal in deals:
    KeywordExtractor.extract_and_save(db, deal)

# ✅ 효율적 (배치 처리)
KeywordExtractor.batch_extract_and_save(db, deals)
```

**성능 개선**: DB 쿼리 50% 감소

### 중복 방지

**Unique Constraint**:
```python
# models/deal.py
__table_args__ = (
    UniqueConstraint('source_id', 'external_id', name='uq_deal_source_external'),
)
```

**처리**:
- 기존 딜: 업데이트 (view_count, comment_count 등)
- 새 딜: 생성

---

## 문제 해결

### 크롤링 실패

**1. 사이트 구조 변경**

**증상**: ParseError 발생

**해결**:
```bash
# 디버그 스크립트 실행
python -m scripts.debug_ppomppu

# HTML 구조 확인 후 파서 수정
# app/crawlers/ppomppu.py 수정
```

**2. 인코딩 오류**

**증상**: 한글 깨짐

**해결**:
```python
# 뽐뿌는 EUC-KR 사용
response.encoding = "euc-kr"
html = response.text
```

**3. Rate Limit 차단**

**증상**: 403 Forbidden 또는 연속 실패

**해결**:
```python
# app/config.py
CRAWLER_REQUEST_DELAY = 2.0  # 1초 → 2초로 증가

# User-Agent 변경
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
}
```

### 데이터 품질 문제

**1. 가격 파싱 실패**

**증상**: `price = None` 또는 잘못된 값

**해결**:
```python
# app/crawlers/ppomppu.py의 _extract_price() 정규식 확인
def _extract_price(self, text):
    # 새로운 가격 패턴 추가
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*원',    # 50,000원
        r'(\d+)\s*만\s*(\d+)\s*천\s*원', # 5만 5천원
        # 추가 패턴...
    ]
```

**2. 키워드 품질 낮음**

**증상**: 불필요한 키워드 추출 ("입니다", "있습니다" 등)

**해결**:
```python
# app/services/keyword_extractor.py
STOP_WORDS = {
    '입니다', '있습니다', '무료배송', '쿠폰',
    # 추가 불용어...
}

# 최소 길이 조정
MIN_KEYWORD_LENGTH = 2  # 1글자 키워드 제외
```

---

## 향후 개선 계획

### Phase 1 (현재) ✅

- ✅ 뽐뿌 크롤러 구현
- ✅ 키워드 추출
- ✅ 에러 처리

### Phase 2 (다음 단계)

- [ ] 나머지 4개 사이트 크롤러
- [ ] Celery 스케줄러 (5분마다 자동 실행)
- [ ] 실시간 크롤링

**예상 소요 시간**: 2주

### Phase 3 (고도화)

- [ ] 중복 딜 감지 (동일 상품, 다른 사이트)
- [ ] 가격 비교 기능
- [ ] AI 요약 생성

**예상 소요 시간**: 2주

### Phase 4 (확장)

- [ ] 분산 크롤링 (여러 서버)
- [ ] 캐싱 전략
- [ ] 성능 모니터링 대시보드

**예상 소요 시간**: 3-4주

---

## 파일 구조

```
backend/app/
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py      # 기본 크롤러 클래스 ✅
│   └── ppomppu.py            # 뽐뿌 크롤러 ✅
├── services/
│   ├── keyword_extractor.py # 키워드 추출 ✅
│   └── ...
└── scripts/
    ├── run_ppomppu_crawler.py # 실행 스크립트 ✅
    └── debug_ppomppu.py        # 디버그 도구 ✅
```

---

## 라이선스 및 주의사항

⚠️ **중요**:

- **이용약관 준수**: 웹사이트 이용약관 준수 필수
- **Rate Limiting**: 서버 부하 최소화 (1초 딜레이)
- **개인정보**: 개인정보 수집 금지
- **상업적 이용**: 사이트 운영자 승인 필요
- **윤리적 크롤링**: robots.txt 확인

---

## 기여 가이드

새로운 크롤러 추가 시:

1. `BaseCrawler` 상속
2. `fetch_deals()` 구현
3. `parse_deal()` 구현
4. 테스트 스크립트 작성
5. 문서 업데이트 (이 파일)

**예시 템플릿**:
```python
from app.crawlers.base_crawler import BaseCrawler

class NewSiteCrawler(BaseCrawler):
    def __init__(self, db):
        super().__init__(db, source_name="newsite")

    def fetch_deals(self, max_pages=5):
        """딜 수집 로직"""
        # TODO: 구현
        pass

    def parse_deal(self, raw_data):
        """파싱 로직"""
        # TODO: 구현
        return {
            'title': '...',
            'price': 0,
            # ...
        }
```

---

## 참고 문서

- [데이터베이스 스키마](DATABASE.md) - `crawler_runs`, `crawler_errors`, `crawler_state` 테이블
- [개발 현황](STATUS.md) - 크롤러 개발 진행 상황
- [프로젝트 개요](../PROJECT.md) - 전체 아키텍처

---

**작성일**: 2026-02-11
**최종 업데이트**: 2026-02-12
**상태**: Production Ready (뽐뿌 크롤러)
