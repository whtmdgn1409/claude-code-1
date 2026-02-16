"""
Ppomppu (뽐뿌) crawler implementation.
Crawls hot deals from www.ppomppu.co.kr
"""
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app.crawlers.base_crawler import BaseCrawler
from app.config import settings


class PpomppuCrawler(BaseCrawler):
    """
    Crawler for Ppomppu (뽐뿌) hot deals.
    Target: https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu
    """

    # Ppomppu board URLs
    BASE_URL = "https://www.ppomppu.co.kr"
    DEAL_BOARD_URL = f"{BASE_URL}/zboard/zboard.php?id=ppomppu"
    OVERSEAS_BOARD_URL = f"{BASE_URL}/zboard/zboard.php?id=ppomppu4"

    def __init__(self, db, include_overseas: bool = False):
        """
        Initialize Ppomppu crawler.

        Args:
            db: Database session
            include_overseas: Whether to include overseas deals board
        """
        super().__init__(db, source_name="ppomppu")
        self.include_overseas = include_overseas
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def _fetch_page(self, url: str, page: int = 1) -> Optional[BeautifulSoup]:
        """Fetch a single page and return BeautifulSoup object."""
        try:
            params = {"page": page} if page > 1 else {}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            response.encoding = "euc-kr"  # Ppomppu uses EUC-KR encoding

            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self._log_error(
                type(e).__name__,
                f"Failed to fetch page {page}: {str(e)}",
                url=url
            )
            return None

    def _extract_number(self, text: str) -> int:
        """Extract number from text (e.g., '1,234' -> 1234)."""
        if not text:
            return 0
        # Remove commas and extract digits
        numbers = re.findall(r'\d+', text.replace(',', ''))
        return int(numbers[0]) if numbers else 0

    def _extract_price(self, title: str) -> Optional[int]:
        """
        Extract price from title.
        Common patterns:
        - 12,000원
        - 12000원
        - $12.99
        - 1만2천원
        """
        # Pattern for Korean Won (원)
        krw_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)(?:만)?(?:천)?원'
        match = re.search(krw_pattern, title)
        if match:
            price_text = match.group(1).replace(',', '')
            price = int(price_text)

            # Handle 만 (10,000) and 천 (1,000)
            if '만' in match.group(0):
                price *= 10000
            elif '천' in match.group(0):
                price *= 1000

            return price

        # Pattern for USD ($)
        usd_pattern = r'\$(\d+\.?\d*)'
        match = re.search(usd_pattern, title)
        if match:
            # Convert USD to KRW (approximate rate: 1 USD = 1300 KRW)
            usd = float(match.group(1))
            return int(usd * 1300)

        return None

    def _extract_mall_info(self, title: str, content: str = "") -> Dict[str, Optional[str]]:
        """
        Extract shopping mall information from title or content.
        Returns dict with mall_name and mall_url.
        """
        mall_info = {"mall_name": None, "mall_url": None}

        # Common Korean shopping malls
        mall_keywords = [
            "쿠팡", "11번가", "G마켓", "옥션", "네이버", "위메프", "티몬",
            "SSG", "롯데온", "인터파크", "알리익스프레스", "아마존"
        ]

        for mall in mall_keywords:
            if mall in title or mall in content:
                mall_info["mall_name"] = mall
                break

        # Try to extract URL from content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        if urls:
            mall_info["mall_url"] = urls[0]

        return mall_info

    def parse_deal(self, row) -> Optional[Dict[str, Any]]:
        """
        Parse a deal row from Ppomppu board.

        Args:
            row: BeautifulSoup tr element

        Returns:
            Parsed deal dictionary or None
        """
        try:
            # Extract cells - Ppomppu has 6 cells per data row
            cells = row.find_all("td")
            if len(cells) != 6:
                return None

            # Cell 0: 번호 (number)
            num_cell = cells[0]
            external_id = num_cell.get_text(strip=True)

            # Skip notices and alerts
            if external_id in ["공지", "알림", "HOT"] or not external_id.isdigit():
                return None

            # Cell 1: 제목 (title) with link
            title_cell = cells[1]
            title_link = title_cell.find("a", href=True)
            if not title_link:
                return None

            full_title = title_cell.get_text(strip=True)
            relative_url = title_link.get("href", "")

            # Build full URL
            if relative_url.startswith("http"):
                full_url = relative_url
            elif relative_url.startswith("view.php"):
                full_url = f"{self.BASE_URL}/zboard/{relative_url}"
            else:
                full_url = f"{self.BASE_URL}/zboard/view.php?id=ppomppu&no={external_id}"

            # Extract comment count from title (e.g., "32" at the end)
            # The number appears after the title, sometimes in square brackets
            comment_match = re.search(r'(\d+)\s*(?:\[.*?\])?\s*$', full_title)
            comment_count = int(comment_match.group(1)) if comment_match else 0

            # Extract category tag (e.g., "[식품/건강]")
            category_match = re.search(r'\[([^\]]+)\]\s*$', full_title)
            category = category_match.group(1) if category_match else None

            # Clean title - remove comment count and category
            clean_title = re.sub(r'\d+\s*(?:\[.*?\])?\s*$', '', full_title)
            clean_title = re.sub(r'\[([^\]]+)\]\s*$', '', clean_title).strip()

            # Cell 2: 글쓴이 (author)
            author_cell = cells[2]
            author = author_cell.get_text(strip=True) or "Unknown"

            # Cell 3: 등록일 (date) - format: "09:19:25" or "24/11/14"
            date_cell = cells[3]
            date_text = date_cell.get_text(strip=True)
            published_at = self._parse_date(date_text)

            # Cell 4: 추천 (recommendations) - format: "16 - 0" (upvotes - downvotes)
            rec_cell = cells[4]
            rec_text = rec_cell.get_text(strip=True)
            upvotes, downvotes = self._parse_votes(rec_text)

            # Cell 5: 조회 (views)
            view_cell = cells[5]
            view_count = self._extract_number(view_cell.get_text(strip=True))

            # Extract price from title
            price = self._extract_price(clean_title)

            # Extract mall info
            mall_info = self._extract_mall_info(clean_title)

            # Build deal data
            deal_data = {
                "external_id": external_id,
                "url": full_url,
                "title": clean_title,
                "author": author,
                "published_at": published_at,
                "view_count": view_count,
                "comment_count": comment_count,
                "price": price,
                "mall_name": mall_info["mall_name"],
                "mall_product_url": mall_info["mall_url"],
                "upvotes": upvotes,
                "downvotes": downvotes,
            }

            return deal_data

        except Exception as e:
            self._log_error(
                type(e).__name__,
                f"Failed to parse deal: {str(e)}",
            )
            return None

    def _parse_votes(self, text: str) -> tuple:
        """
        Parse votes from recommendation text.
        Format: "16 - 0" (upvotes - downvotes)
        """
        try:
            if '-' in text:
                parts = text.split('-')
                upvotes = self._extract_number(parts[0].strip())
                downvotes = self._extract_number(parts[1].strip())
                return upvotes, downvotes
            else:
                # Single number means upvotes only
                votes = self._extract_number(text)
                return votes, 0
        except Exception:
            return 0, 0

    def _parse_date(self, date_text: str) -> datetime:
        """
        Parse date from Ppomppu format.
        Formats: 'HH:MM:SS', 'YY/MM/DD', or 'YYYY-MM-DD'
        """
        try:
            # If time format (HH:MM:SS or HH:MM), assume today
            if ':' in date_text:
                return datetime.utcnow()

            # If YY/MM/DD format (e.g., "24/11/14")
            if '/' in date_text:
                parts = date_text.split('/')
                if len(parts) == 3:
                    year = int(parts[0])
                    # Convert 2-digit year to 4-digit (20XX)
                    if year < 100:
                        year = 2000 + year
                    month = int(parts[1])
                    day = int(parts[2])
                    return datetime(year, month, day)

            # If MM-DD format, assume current year
            if len(date_text.split('-')) == 2:
                month, day = date_text.split('-')
                return datetime(datetime.utcnow().year, int(month), int(day))

            # If YYYY-MM-DD format
            if len(date_text.split('-')) == 3:
                return datetime.strptime(date_text, '%Y-%m-%d')

        except Exception:
            pass

        # Default to now
        return datetime.utcnow()

    def fetch_deals(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch deals from Ppomppu.

        Args:
            max_pages: Maximum number of pages to crawl

        Returns:
            List of deal dictionaries
        """
        all_deals = []
        boards = [self.DEAL_BOARD_URL]

        if self.include_overseas:
            boards.append(self.OVERSEAS_BOARD_URL)

        for board_url in boards:
            print(f"📄 Crawling board: {board_url}")

            for page in range(1, max_pages + 1):
                print(f"   Page {page}/{max_pages}...", end=" ")

                soup = self._fetch_page(board_url, page)
                if not soup:
                    print("❌ Failed")
                    continue

                # Find deal table - Ppomppu uses id="revolution_main_table"
                table = soup.find("table", {"id": "revolution_main_table"})
                if not table:
                    print("❌ No table found")
                    continue

                # Find all deal rows
                rows = table.find_all("tr")
                page_deals = []

                for row in rows:
                    # Skip header rows
                    if row.find("th"):
                        continue

                    deal_data = self.parse_deal(row)
                    if deal_data:
                        page_deals.append(deal_data)

                print(f"✓ Found {len(page_deals)} deals")
                all_deals.extend(page_deals)

                # Respect rate limit
                self._respect_rate_limit()

        return all_deals

    def fetch_deal_comments(self, deal_url: str) -> List[Dict]:
        """
        Fetch comments from Ppomppu deal detail page.

        Args:
            deal_url: URL of the deal detail page

        Returns:
            List of comment dictionaries (max 20, sorted by upvotes)
            Each comment dict contains: author, content, upvotes, created_at

        Note:
            This implementation uses generic CSS selectors that may need
            adjustment based on Ppomppu's actual HTML structure.
        """
        try:
            # Fetch detail page
            response = self.session.get(deal_url, timeout=10)
            response.raise_for_status()
            response.encoding = "euc-kr"  # Ppomppu uses EUC-KR encoding

            soup = BeautifulSoup(response.text, "html.parser")

            comments = []

            # Try multiple possible selectors for comments
            # Ppomppu may use different structures for different boards
            comment_elements = (
                soup.select(".comment-list .comment-item") or
                soup.select(".cmt_list tr") or
                soup.select(".re_list tr") or
                soup.select("div[id*='comment'] tr")
            )

            for elem in comment_elements[:20]:  # Limit to 20
                try:
                    # Try to extract author
                    author_el = (
                        elem.select_one(".comment-author") or
                        elem.select_one(".writer") or
                        elem.select_one("td.user") or
                        elem.select_one("td:first-child")
                    )

                    # Try to extract content
                    content_el = (
                        elem.select_one(".comment-content") or
                        elem.select_one(".memo_content") or
                        elem.select_one(".comment_memo") or
                        elem.select_one("td.memo")
                    )

                    # Try to extract upvotes
                    upvote_el = (
                        elem.select_one(".comment-upvotes") or
                        elem.select_one(".up") or
                        elem.select_one(".rec")
                    )

                    if not (author_el and content_el):
                        continue

                    author = author_el.get_text(strip=True)
                    content = content_el.get_text(strip=True)

                    # Skip empty comments
                    if not content:
                        continue

                    # Extract upvotes (default 0 if not found)
                    upvotes = 0
                    if upvote_el:
                        upvotes = self._extract_number(upvote_el.get_text())

                    comments.append({
                        "author": author,
                        "content": content,
                        "upvotes": upvotes,
                        "created_at": datetime.utcnow().isoformat()
                    })

                except Exception as e:
                    # Skip individual comment parsing errors
                    continue

            # Sort by upvotes (descending)
            comments.sort(key=lambda x: x['upvotes'], reverse=True)

            # Rate limiting - 2 second delay for detail page fetch
            time.sleep(2.0)

            return comments[:20]

        except Exception as e:
            self._log_error(
                'CommentParsingError',
                str(e),
                url=deal_url
            )
            return []


def run_ppomppu_crawler(db, max_pages: int = 5, include_overseas: bool = False):
    """
    Convenience function to run Ppomppu crawler.

    Args:
        db: Database session
        max_pages: Maximum pages to crawl
        include_overseas: Include overseas deals board

    Returns:
        Crawler statistics
    """
    crawler = PpomppuCrawler(db, include_overseas=include_overseas)
    return crawler.run(max_pages=max_pages)
