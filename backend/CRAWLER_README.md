# DealMoa 크롤러 (Crawler) 문서

## 개요

뽐뿌(Ppomppu)를 시작으로 한국 주요 딜 커뮤니티에서 핫딜 정보를 수집하는 크롤러 시스템입니다.

---

## 구현된 크롤러

### ✅ 뽐뿌 (Ppomppu) 크롤러

**대상 사이트**: https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu

**수집 정보**:
- 딜 제목 (title)
- 가격 (price) - 자동 추출
- 작성자 (author)
- 조회수 (view_count)
- 추천수 (upvotes/downvotes)
- 댓글 수 (comment_count)
- 게시일 (published_at)
- 쇼핑몰 정보 (mall_name, mall_url)

**주요 기능**:
- ✅ 다중 페이지 크롤링
- ✅ 중복 방지 (external_id 기반)
- ✅ 자동 키워드 추출
- ✅ 가격 정보 파싱
- ✅ Rate limiting (1초 딜레이)
- ✅ 에러 처리 및 로깅
- ✅ 크롤러 실행 이력 추적

---

## 사용 방법

### 기본 실행

```bash
cd backend
source venv/bin/activate

# 기본 실행 (5 페이지)
python -m scripts.run_ppomppu_crawler

# 페이지 수 지정
python -m scripts.run_ppomppu_crawler --pages 10

# 해외딜 포함
python -m scripts.run_ppomppu_crawler --overseas
```

### 프로그래밍 방식 사용

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
finally:
    db.close()
```

---

## 크롤러 아키텍처

### 1. BaseCrawler (기본 크롤러 클래스)

모든 크롤러의 부모 클래스로 공통 기능 제공:

```python
from app.crawlers.base_crawler import BaseCrawler

class MyCrawler(BaseCrawler):
    def __init__(self, db):
        super().__init__(db, source_name="mysite")

    def fetch_deals(self, max_pages):
        # 딜 수집 로직
        pass

    def parse_deal(self, raw_data):
        # 파싱 로직
        pass
```

**제공 기능**:
- ✅ 크롤러 실행 추적 (CrawlerRun)
- ✅ 에러 로깅 (CrawlerError)
- ✅ 상태 관리 (CrawlerState)
- ✅ Rate limiting
- ✅ 통계 수집
- ✅ 자동 commit/rollback

### 2. PpomppuCrawler (뽐뿌 크롤러)

```python
from app.crawlers import PpomppuCrawler

crawler = PpomppuCrawler(db, include_overseas=False)
stats = crawler.run(max_pages=5)
```

**특징**:
- EUC-KR 인코딩 처리
- 한국어 가격 파싱 (원, 만원, 천원)
- 쇼핑몰 자동 감지 (쿠팡, 11번가, G마켓 등)
- 추천수/비추천수 분리
- 시간 형식 파싱 (HH:MM:SS, YY/MM/DD)

### 3. KeywordExtractor (키워드 추출기)

딜 제목/내용에서 자동으로 키워드 추출:

```python
from app.services import KeywordExtractor

# 단일 딜 키워드 추출
keywords_count = KeywordExtractor.extract_and_save(db, deal)

# 여러 딜 일괄 처리
total = KeywordExtractor.batch_extract_and_save(db, deals)
```

**추출 규칙**:
- 한글 단어 (2자 이상)
- 영문 단어 (2자 이상)
- 모델명/제품번호 (RTX4090, 갤럭시S23 등)
- 불용어 제외 (입니다, 있습니다 등)
- 최대 50개 키워드/딜

---

## 크롤러 실행 결과

### 성공적인 실행 예시

```bash
============================================================
🚀 Ppomppu (뽐뿌) Crawler
============================================================
Pages to crawl: 2
Include overseas: False
Extract keywords: True
============================================================

🚀 Starting crawler for 뽐뿌...
📄 Crawling board: https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu
   Page 1/2... ✓ Found 21 deals
   Page 2/2... ✓ Found 20 deals
📦 Found 41 deals
✅ Crawler completed successfully!
   - New: 41
   - Updated: 0
   - Skipped: 0
   - Errors: 0

============================================================
📊 Crawling Results
============================================================
Total found: 41
New deals: 41
Updated deals: 0
Skipped: 0
Errors: 0
============================================================

🔤 Extracting keywords from new deals...
✅ Extracted 259 keywords from 41 deals
   Average: 6.3 keywords per deal

✅ Crawler completed successfully!
```

### 데이터베이스 확인

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

-- 인기 키워드
SELECT keyword, COUNT(*) as count
FROM deal_keywords
GROUP BY keyword
ORDER BY count DESC
LIMIT 10;
```

**실제 결과**:
```
총 딜: 41개
평균 조회수: 2,641
최대 추천수: 10
인기 키워드: 무료(26), 무배(10), 네이버(10), 11번가(7), 지마켓(5)
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

---

## 추가 구현 예정 크롤러

### 🔲 루리웹 (Ruliweb)
- URL: https://bbs.ruliweb.com/market/board/1020
- 특징: 게임/IT 중심 딜

### 🔲 펨코 (Fmkorea)
- URL: https://www.fmkorea.com/hotdeal
- 특징: 다양한 카테고리

### 🔲 퀘이사존 (Quasarzone)
- URL: https://quasarzone.com/bbs/qb_saleinfo
- 특징: PC 하드웨어 중심

### 🔲 딜바다 (Dealbada)
- URL: https://www.dealbada.com
- 특징: 전문 딜 사이트

---

## 성능 최적화

### Rate Limiting
```python
# app/config.py
CRAWLER_REQUEST_DELAY = 1.0  # 초 단위
```

### 배치 처리
```python
# 키워드 일괄 추출 (DB 쿼리 최소화)
KeywordExtractor.batch_extract_and_save(db, deals)
```

### 중복 방지
- `source_id + external_id` unique constraint
- 기존 딜은 업데이트만 수행

---

## 문제 해결

### 크롤링이 실패하는 경우

1. **사이트 구조 변경**
   - `scripts/debug_ppomppu.py` 실행
   - HTML 구조 확인 후 파서 수정

2. **인코딩 오류**
   ```python
   response.encoding = "euc-kr"  # 뽐뿌는 EUC-KR
   ```

3. **Rate Limit 차단**
   - `CRAWLER_REQUEST_DELAY` 증가
   - User-Agent 변경

### 데이터 품질 문제

1. **가격 파싱 실패**
   - `_extract_price()` 메서드 정규식 확인
   - 새로운 가격 패턴 추가

2. **키워드 품질 낮음**
   - `STOP_WORDS` 불용어 추가
   - `MIN_KEYWORD_LENGTH` 조정

---

## 향후 개선 계획

### Phase 1 (현재)
- ✅ 뽐뿌 크롤러 구현
- ✅ 키워드 추출
- ✅ 에러 처리

### Phase 2
- [ ] 나머지 4개 사이트 크롤러
- [ ] 스케줄러 (Celery)
- [ ] 실시간 크롤링 (5분 간격)

### Phase 3
- [ ] 중복 딜 감지 (동일 상품 다른 사이트)
- [ ] 가격 비교 기능
- [ ] AI 요약 생성

### Phase 4
- [ ] 분산 크롤링 (여러 서버)
- [ ] 캐싱 전략
- [ ] 성능 모니터링 대시보드

---

## 라이선스 및 주의사항

⚠️ **중요**:
- 웹사이트 이용약관 준수 필수
- Rate limiting을 통한 서버 부하 최소화
- 개인정보 수집 금지
- 상업적 이용 시 사이트 운영자 승인 필요

---

## 기여

새로운 크롤러 추가 시:
1. `BaseCrawler` 상속
2. `fetch_deals()` 구현
3. `parse_deal()` 구현
4. 테스트 스크립트 작성
5. 문서 업데이트

---

**작성일**: 2026-02-11
**버전**: 1.0.0
**상태**: Production Ready (뽐뿌 크롤러)
