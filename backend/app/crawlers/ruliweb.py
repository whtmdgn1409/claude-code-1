"""
Ruliweb (루리웹) crawler implementation.
Crawls hot deals from bbs.ruliweb.com/market/board/1020
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app.crawlers.base_crawler import BaseCrawler
from app.config import settings


class RuliwebCrawler(BaseCrawler):
    """
    Crawler for Ruliweb (루리웹) hot deals.
    Target: https://bbs.ruliweb.com/market/board/1020
    """

    BASE_URL = "https://bbs.ruliweb.com"
    DEAL_BOARD_URL = f"{BASE_URL}/market/board/1020"

    def __init__(self, db):
        super().__init__(db, source_name="ruliweb")
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
            response = self.session.get(url, params=params, timeout=10)
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
            "에픽게임즈", "스팀", "GOG", "험블번들",
        ]
        for mall in mall_keywords:
            if mall.lower() in title.lower():
                mall_info["mall_name"] = mall
                break
        return mall_info

    def _parse_date(self, date_text: str) -> datetime:
        """
        Parse date from Ruliweb format.
        Formats: 'HH:MM', 'YYYY.MM.DD'
        """
        try:
            date_text = date_text.strip()
            # Time only format (today's post)
            if re.match(r'^\d{2}:\d{2}$', date_text):
                return datetime.utcnow()
            # YYYY.MM.DD format
            if '.' in date_text:
                return datetime.strptime(date_text, '%Y.%m.%d')
        except Exception:
            pass
        return datetime.utcnow()

    def parse_deal(self, row) -> Optional[Dict[str, Any]]:
        """Parse a deal row from Ruliweb board."""
        try:
            cells = row.find_all("td")
            if len(cells) < 5:
                return None

            # Find external_id from the row's id attribute or the number cell
            num_cell = cells[0]
            num_text = num_cell.get_text(strip=True)

            # Skip notices
            if not num_text.isdigit():
                return None

            external_id = num_text

            # Title cell - look for subject class or the main link
            title_cell = row.find("td", class_="subject") or row.find("td", class_="title")
            if not title_cell:
                # Fallback: find the cell with a subject_link
                for cell in cells:
                    link = cell.find("a", class_="subject_link") or cell.find("a", class_="title_wrapper")
                    if link:
                        title_cell = cell
                        break

            if not title_cell:
                return None

            title_link = (
                title_cell.find("a", class_="subject_link")
                or title_cell.find("a", class_="title_wrapper")
                or title_cell.find("a", href=True)
            )
            if not title_link:
                return None

            title = title_link.get_text(strip=True)
            if not title:
                return None

            href = title_link.get("href", "")
            if href.startswith("/"):
                full_url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                full_url = f"{self.DEAL_BOARD_URL}/read/{external_id}"

            # Extract post ID from URL if possible
            id_match = re.search(r'/read/(\d+)', full_url)
            if id_match:
                external_id = id_match.group(1)

            # Category
            divsn_cell = row.find("td", class_="divsn")

            # Extract comment count from title area
            comment_el = title_cell.find("span", class_="num_reply") or title_cell.find("a", class_="num_reply")
            comment_count = 0
            if comment_el:
                comment_count = self._extract_number(comment_el.get_text())

            # Clean title - remove comment count markers
            title = re.sub(r'\s*\[\d+\]\s*$', '', title).strip()
            title = re.sub(r'\s*\(\d+\)\s*$', '', title).strip()

            # Author, recommendation, views, date - iterate remaining cells
            author = "Unknown"
            upvotes = 0
            view_count = 0
            published_at = datetime.utcnow()

            # Ruliweb typical column order: num, category, title, author, date, recommend, views
            # But layouts vary. Parse by known class names or position.
            for cell in cells:
                classes = cell.get("class", [])
                text = cell.get_text(strip=True)

                if "writer" in classes or "name" in classes:
                    author = text or "Unknown"
                elif "recomd" in classes or "recommend" in classes:
                    upvotes = self._extract_number(text)
                elif "hit" in classes or "count" in classes:
                    view_count = self._extract_number(text)
                elif "time" in classes or "date" in classes:
                    published_at = self._parse_date(text)

            # If class-based extraction didn't work, use positional fallback
            if author == "Unknown" and len(cells) >= 6:
                # Typical: [num, divsn, subject, writer, recomd, hit, date]
                # or: [num, subject, writer, recomd, hit, date]
                try:
                    if len(cells) >= 7:
                        author = cells[3].get_text(strip=True) or "Unknown"
                        upvotes = self._extract_number(cells[4].get_text(strip=True))
                        view_count = self._extract_number(cells[5].get_text(strip=True))
                        published_at = self._parse_date(cells[6].get_text(strip=True))
                    elif len(cells) >= 6:
                        author = cells[2].get_text(strip=True) or "Unknown"
                        upvotes = self._extract_number(cells[3].get_text(strip=True))
                        view_count = self._extract_number(cells[4].get_text(strip=True))
                        published_at = self._parse_date(cells[5].get_text(strip=True))
                except (IndexError, ValueError):
                    pass

            # Extract price and mall info from title
            price = self._extract_price(title)
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
        """Fetch deals from Ruliweb."""
        all_deals = []

        print(f"📄 Crawling board: {self.DEAL_BOARD_URL}")

        for page in range(1, max_pages + 1):
            print(f"   Page {page}/{max_pages}...", end=" ")

            soup = self._fetch_page(self.DEAL_BOARD_URL, page)
            if not soup:
                print("❌ Failed")
                continue

            # Ruliweb uses table.table_body or table.board_list_table
            table = (
                soup.find("table", class_="table_body")
                or soup.find("table", class_="board_list_table")
                or soup.find("table", {"id": "board_list"})
            )
            if not table:
                # Try finding any table with deal-like rows
                tables = soup.find_all("table")
                for t in tables:
                    if t.find("a", class_="subject_link") or t.find("a", class_="title_wrapper"):
                        table = t
                        break

            if not table:
                print("❌ No table found")
                continue

            rows = table.find_all("tr")
            page_deals = []

            for row in rows:
                if row.find("th"):
                    continue
                deal_data = self.parse_deal(row)
                if deal_data:
                    page_deals.append(deal_data)

            print(f"✓ Found {len(page_deals)} deals")
            all_deals.extend(page_deals)

            self._respect_rate_limit()

        return all_deals


def run_ruliweb_crawler(db, max_pages: int = 5):
    """Convenience function to run Ruliweb crawler."""
    crawler = RuliwebCrawler(db)
    return crawler.run(max_pages=max_pages)
