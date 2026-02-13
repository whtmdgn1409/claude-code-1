"""
Quasarzone (퀘이사존) crawler implementation.
Crawls hot deals from quasarzone.com/bbs/qb_saleinfo
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app.crawlers.base_crawler import BaseCrawler
from app.config import settings


class QuasarzoneCrawler(BaseCrawler):
    """
    Crawler for Quasarzone (퀘이사존) sale info.
    Target: https://quasarzone.com/bbs/qb_saleinfo
    """

    BASE_URL = "https://quasarzone.com"
    DEAL_BOARD_URL = f"{BASE_URL}/bbs/qb_saleinfo"

    def __init__(self, db):
        super().__init__(db, source_name="quasarzone")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": self.BASE_URL,
        })

    def _fetch_page(self, url: str, page: int = 1) -> Optional[BeautifulSoup]:
        """Fetch a single page and return BeautifulSoup object."""
        try:
            params = {"page": page} if page > 1 else {}
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self._log_error(
                type(e).__name__,
                f"Failed to fetch page {page}: {str(e)}",
                url=url
            )
            return None

    def _extract_number(self, text: str) -> int:
        """Extract number from text."""
        if not text:
            return 0
        numbers = re.findall(r'\d+', text.replace(',', ''))
        return int(numbers[0]) if numbers else 0

    def _extract_price(self, title: str) -> Optional[int]:
        """Extract price from title."""
        krw_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)(?:만)?(?:천)?원'
        match = re.search(krw_pattern, title)
        if match:
            price_text = match.group(1).replace(',', '')
            price = int(price_text)
            if '만' in match.group(0):
                price *= 10000
            elif '천' in match.group(0):
                price *= 1000
            return price

        usd_pattern = r'\$(\d+\.?\d*)'
        match = re.search(usd_pattern, title)
        if match:
            return int(float(match.group(1)) * 1300)

        return None

    def _extract_mall_info(self, title: str) -> Dict[str, Optional[str]]:
        """Extract shopping mall information from title."""
        mall_info = {"mall_name": None, "mall_url": None}
        mall_keywords = [
            "쿠팡", "11번가", "G마켓", "옥션", "네이버", "위메프", "티몬",
            "SSG", "롯데온", "인터파크", "알리익스프레스", "아마존",
            "다나와", "컴퓨존", "조이젠",
        ]
        for mall in mall_keywords:
            if mall.lower() in title.lower():
                mall_info["mall_name"] = mall
                break
        return mall_info

    def _parse_date(self, date_text: str) -> datetime:
        """
        Parse date from Quasarzone format.
        Formats: 'HH:MM', 'MM-DD', 'YYYY-MM-DD', '2시간 전', '3분 전'
        """
        try:
            date_text = date_text.strip()

            # Relative time: "N분 전", "N시간 전"
            if '분 전' in date_text or '분전' in date_text:
                return datetime.utcnow()
            if '시간 전' in date_text or '시간전' in date_text:
                return datetime.utcnow()
            if '일 전' in date_text:
                return datetime.utcnow()

            # Time only (today)
            if re.match(r'^\d{2}:\d{2}$', date_text):
                return datetime.utcnow()

            # YYYY-MM-DD
            if re.match(r'^\d{4}-\d{2}-\d{2}$', date_text):
                return datetime.strptime(date_text, '%Y-%m-%d')

            # YY.MM.DD or YYYY.MM.DD
            if '.' in date_text:
                parts = date_text.split('.')
                if len(parts) == 3:
                    year = int(parts[0])
                    if year < 100:
                        year += 2000
                    return datetime(year, int(parts[1]), int(parts[2]))

            # MM-DD
            if re.match(r'^\d{2}-\d{2}$', date_text):
                parts = date_text.split('-')
                return datetime(datetime.utcnow().year, int(parts[0]), int(parts[1]))

        except Exception:
            pass
        return datetime.utcnow()

    def parse_deal(self, row) -> Optional[Dict[str, Any]]:
        """Parse a deal row/item from Quasarzone board."""
        try:
            # Quasarzone uses <tr> rows in a table, or <div> items
            # Try table row first
            cells = row.find_all("td")

            # Extract title link
            title_link = (
                row.select_one(".tit a")
                or row.select_one("a.subject-link")
                or row.select_one(".subject a")
            )

            if not title_link:
                # Fallback: find any link that looks like a deal post
                for link in row.find_all("a", href=True):
                    href = link.get("href", "")
                    if "/views/" in href or "/qb_saleinfo/" in href:
                        title_link = link
                        break

            if not title_link:
                return None

            title = title_link.get_text(strip=True)
            if not title or len(title) < 3:
                return None

            href = title_link.get("href", "")
            if href.startswith("/"):
                full_url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                full_url = f"{self.DEAL_BOARD_URL}/{href}"

            # Extract external_id from URL
            id_match = re.search(r'/views/(\d+)', full_url)
            if not id_match:
                id_match = re.search(r'no=(\d+)', full_url)
            if not id_match:
                # Generate from URL hash
                external_id = re.sub(r'[^\d]', '', href)[-10:] if href else None
                if not external_id:
                    return None
            else:
                external_id = id_match.group(1)

            # Thumbnail
            thumb_el = row.select_one(".thumb-wrap img") or row.select_one("img.thumb")
            thumbnail_url = None
            if thumb_el:
                thumbnail_url = thumb_el.get("src") or thumb_el.get("data-src")
                if thumbnail_url and thumbnail_url.startswith("/"):
                    thumbnail_url = f"{self.BASE_URL}{thumbnail_url}"
                # Skip placeholder images
                if thumbnail_url and "no_image" in thumbnail_url:
                    thumbnail_url = None

            # Price element
            price_el = row.select_one(".price")
            price = None
            if price_el:
                price = self._extract_price(price_el.get_text())
            if not price:
                price = self._extract_price(title)

            # Date
            date_el = row.select_one(".date") or row.select_one(".time")
            published_at = datetime.utcnow()
            if date_el:
                published_at = self._parse_date(date_el.get_text(strip=True))

            # Views
            views_el = row.select_one(".count") or row.select_one(".hit")
            view_count = 0
            if views_el:
                view_count = self._extract_number(views_el.get_text())

            # Comments
            comment_el = row.select_one(".cmt") or row.select_one(".comment-cnt")
            comment_count = 0
            if comment_el:
                comment_count = self._extract_number(comment_el.get_text())

            # Recommendations / upvotes
            rec_el = row.select_one(".ok") or row.select_one(".recommend")
            upvotes = 0
            if rec_el:
                upvotes = self._extract_number(rec_el.get_text())

            # Author
            author_el = row.select_one(".nick") or row.select_one(".author")
            author = "Unknown"
            if author_el:
                author = author_el.get_text(strip=True) or "Unknown"

            # If class-based extraction didn't get views/date, try cells
            if cells and len(cells) >= 4 and view_count == 0:
                for cell in cells:
                    text = cell.get_text(strip=True)
                    # Detect view count (pure number, typically > 10)
                    if text.isdigit() and int(text) > 10:
                        view_count = int(text)
                        break

            mall_info = self._extract_mall_info(title)

            return {
                "external_id": external_id,
                "url": full_url,
                "title": title,
                "author": author,
                "published_at": published_at,
                "view_count": view_count,
                "comment_count": comment_count,
                "price": price,
                "thumbnail_url": thumbnail_url,
                "mall_name": mall_info["mall_name"],
                "mall_product_url": mall_info["mall_url"],
                "upvotes": upvotes,
                "downvotes": 0,
            }

        except Exception as e:
            self._log_error(
                type(e).__name__,
                f"Failed to parse deal: {str(e)}",
            )
            return None

    def fetch_deals(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Fetch deals from Quasarzone."""
        all_deals = []

        print(f"📄 Crawling board: {self.DEAL_BOARD_URL}")

        for page in range(1, max_pages + 1):
            print(f"   Page {page}/{max_pages}...", end=" ")

            soup = self._fetch_page(self.DEAL_BOARD_URL, page)
            if not soup:
                print("❌ Failed")
                continue

            page_deals = []

            # Strategy 1: Table-based layout
            table = (
                soup.select_one(".market-type-list table tbody")
                or soup.select_one("table.table_body tbody")
                or soup.select_one("table tbody")
            )
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    if row.find("th"):
                        continue
                    deal_data = self.parse_deal(row)
                    if deal_data:
                        page_deals.append(deal_data)

            # Strategy 2: Div-based list layout (fallback)
            if not page_deals:
                items = (
                    soup.select(".market-info-list .market-info-sub")
                    or soup.select(".list-board .list-item")
                    or soup.select("[class*='market'] [class*='item']")
                )
                for item in items:
                    deal_data = self.parse_deal(item)
                    if deal_data:
                        page_deals.append(deal_data)

            print(f"✓ Found {len(page_deals)} deals")
            all_deals.extend(page_deals)

            self._respect_rate_limit()

        return all_deals


def run_quasarzone_crawler(db, max_pages: int = 5):
    """Convenience function to run Quasarzone crawler."""
    crawler = QuasarzoneCrawler(db)
    return crawler.run(max_pages=max_pages)
