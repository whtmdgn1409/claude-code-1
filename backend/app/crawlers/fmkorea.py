"""
FMKorea (펨코) crawler implementation.
Crawls hot deals from www.fmkorea.com/hotdeal

Note: FMKorea has moderate anti-scraping protections.
This crawler uses requests with realistic headers. If it fails consistently,
consider switching to a headless browser (Playwright/Selenium).
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app.crawlers.base_crawler import BaseCrawler
from app.config import settings


class FmkoreaCrawler(BaseCrawler):
    """
    Crawler for FMKorea (펨코) hot deals.
    Target: https://www.fmkorea.com/hotdeal
    Uses list view (?listStyle=list) for easier parsing.
    """

    BASE_URL = "https://www.fmkorea.com"
    # Use list view instead of webzine for simpler parsing
    DEAL_BOARD_URL = f"{BASE_URL}/hotdeal"

    def __init__(self, db):
        super().__init__(db, source_name="fmkorea")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": self.BASE_URL,
        })

    def _fetch_page(self, url: str, page: int = 1) -> Optional[BeautifulSoup]:
        """
        Fetch a single page and return BeautifulSoup object.
        FMKorea has aggressive anti-bot protection (HTTP 430).
        If blocked, consider using Playwright or a proxy.
        """
        try:
            if page > 1:
                fetch_url = f"{url}?page={page}"
            else:
                fetch_url = url

            response = self.session.get(fetch_url, timeout=15, allow_redirects=True)

            # FMKorea returns 430 when anti-bot triggered
            if response.status_code == 430:
                self._log_error(
                    "AntiBot",
                    f"FMKorea anti-bot protection triggered (HTTP 430). "
                    f"Consider using Playwright or a proxy.",
                    url=url
                )
                return None

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

    def _extract_mall_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract shopping mall information from title or metadata."""
        mall_info = {"mall_name": None, "mall_url": None}
        mall_keywords = [
            "쿠팡", "11번가", "G마켓", "옥션", "네이버", "위메프", "티몬",
            "SSG", "롯데온", "인터파크", "알리익스프레스", "아마존",
            "텐바이텐", "무신사", "올리브영",
        ]
        for mall in mall_keywords:
            if mall.lower() in text.lower():
                mall_info["mall_name"] = mall
                break

        # Try to find explicit "쇼핑몰: XXX" pattern
        mall_match = re.search(r'쇼핑몰\s*:\s*([^\s/,]+)', text)
        if mall_match and not mall_info["mall_name"]:
            mall_info["mall_name"] = mall_match.group(1).strip()

        return mall_info

    def _parse_date(self, date_text: str) -> datetime:
        """
        Parse date from FMKorea format.
        Formats: 'HH:MM', 'YYYY.MM.DD HH:MM', relative times
        """
        try:
            date_text = date_text.strip()

            # Relative time formats
            if '분 전' in date_text or '분전' in date_text:
                return datetime.utcnow()
            if '시간 전' in date_text or '시간전' in date_text:
                return datetime.utcnow()
            if '일 전' in date_text:
                return datetime.utcnow()

            # Time only (today)
            if re.match(r'^\d{2}:\d{2}$', date_text):
                return datetime.utcnow()

            # YYYY.MM.DD HH:MM or YYYY.MM.DD
            if re.match(r'^\d{4}\.\d{2}\.\d{2}', date_text):
                return datetime.strptime(date_text[:10], '%Y.%m.%d')

            # MM.DD HH:MM
            if re.match(r'^\d{2}\.\d{2}', date_text):
                parts = date_text.split('.')
                return datetime(datetime.utcnow().year, int(parts[0]), int(parts[1][:2]))

        except Exception:
            pass
        return datetime.utcnow()

    def _parse_deal_from_table_row(self, row) -> Optional[Dict[str, Any]]:
        """Parse a deal from table-style (<tr>) row."""
        try:
            cells = row.find_all("td")
            if len(cells) < 4:
                return None

            # Find title link
            title_link = None
            title_cell = None
            for cell in cells:
                link = cell.find("a", class_="hx") or cell.find("a", href=True)
                if link:
                    href = link.get("href", "")
                    # Filter for actual deal links (numeric document_srl)
                    if re.search(r'/\d{5,}', href) or 'document_srl' in href:
                        title_link = link
                        title_cell = cell
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
                full_url = f"{self.BASE_URL}/{href}"

            # Extract external_id (document_srl)
            id_match = re.search(r'/(\d{5,})', full_url)
            if not id_match:
                id_match = re.search(r'document_srl=(\d+)', full_url)
            if not id_match:
                return None
            external_id = id_match.group(1)

            # Remove query params from URL for cleanliness
            full_url = re.sub(r'\?.*$', '', full_url)

            # Comment count
            comment_el = title_cell.find("span", class_="comment_count") if title_cell else None
            comment_count = 0
            if comment_el:
                comment_count = self._extract_number(comment_el.get_text())

            # Clean title
            title = re.sub(r'\s*\[\d+\]\s*$', '', title).strip()
            title = re.sub(r'\s*\(\d+\)\s*$', '', title).strip()

            # Parse other fields from remaining cells
            author = "Unknown"
            upvotes = 0
            view_count = 0
            published_at = datetime.utcnow()

            for cell in cells:
                classes = cell.get("class", [])
                class_str = " ".join(classes) if classes else ""
                text = cell.get_text(strip=True)

                if "author" in class_str or "user_name" in class_str:
                    author = text or "Unknown"
                elif "m_no" in class_str or "recom" in class_str or "vote" in class_str:
                    upvotes = self._extract_number(text)
                elif "m_cpt_hit" in class_str or "reading" in class_str:
                    view_count = self._extract_number(text)
                elif "time" in class_str or "date" in class_str or "regdate" in class_str:
                    published_at = self._parse_date(text)

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
                f"Failed to parse table row: {str(e)}",
            )
            return None

    def _parse_deal_from_card(self, item) -> Optional[Dict[str, Any]]:
        """
        Parse a deal from FMKorea card-style (div.li) item.
        Structure: div.li > h3.title > a.hotdeal_var8 (title)
                   div.li > div.hotdeal_info > span (mall, price, shipping)
                   div.li > span.regdate, span.author, span.count
        """
        try:
            # Find title link: a.hotdeal_var8 inside h3.title
            title_link = item.select_one("h3.title a.hotdeal_var8")
            if not title_link:
                title_link = item.select_one("h3 a")
            if not title_link:
                # Fallback: find any link with document ID
                for link in item.find_all("a", href=True):
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    if re.search(r'/\d{5,}', href) and len(text) > 3:
                        title_link = link
                        break

            if not title_link:
                return None

            # Get title from span.ellipsis-target (clean) or link text
            ellipsis = title_link.select_one("span.ellipsis-target")
            title = ellipsis.get_text(strip=True) if ellipsis else title_link.get_text(strip=True)
            if not title or len(title) < 3:
                return None

            # Clean title - remove comment count [N] suffix
            title = re.sub(r'\s*\[\d+\]\s*$', '', title).strip()

            href = title_link.get("href", "")
            if href.startswith("/"):
                full_url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                full_url = f"{self.BASE_URL}/{href}"

            # Extract external_id (document_srl)
            id_match = re.search(r'/(\d{5,})', full_url)
            if not id_match:
                id_match = re.search(r'document_srl=(\d+)', full_url)
            if not id_match:
                return None
            external_id = id_match.group(1)

            full_url = re.sub(r'\?.*$', '', full_url)

            # Thumbnail (img.thumb, skip lazy placeholders)
            thumb_el = item.select_one("img.thumb") or item.select_one("img")
            thumbnail_url = None
            if thumb_el:
                thumbnail_url = (
                    thumb_el.get("data-original")
                    or thumb_el.get("data-src")
                    or thumb_el.get("src")
                )
                if thumbnail_url and ("transparent" in thumbnail_url or "lazy" in thumbnail_url):
                    thumbnail_url = None
                if thumbnail_url and thumbnail_url.startswith("//"):
                    thumbnail_url = f"https:{thumbnail_url}"

            # Parse hotdeal_info metadata: mall, price, shipping
            mall_name = None
            price = None
            hotdeal_info = item.select_one("div.hotdeal_info")
            if hotdeal_info:
                info_text = hotdeal_info.get_text()
                # Extract mall from "쇼핑몰:XXX" pattern
                mall_match = re.search(r'쇼핑몰\s*:\s*([^\s/,]+)', info_text)
                if mall_match:
                    mall_name = mall_match.group(1).strip()
                # Extract price from "가격:N원" pattern
                price_match = re.search(r'가격\s*:\s*([\d,]+)\s*원', info_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))

            # Fallback: extract from title
            if not price:
                price = self._extract_price(title)
            if not mall_name:
                mall_info = self._extract_mall_info(title)
                mall_name = mall_info["mall_name"]

            # Date (span.regdate)
            date_el = item.select_one("span.regdate")
            published_at = datetime.utcnow()
            if date_el:
                published_at = self._parse_date(date_el.get_text(strip=True))

            # Upvotes (span.count inside a.pc_voted_count)
            upvotes = 0
            vote_el = item.select_one("a.pc_voted_count span.count")
            if vote_el:
                upvotes = self._extract_number(vote_el.get_text())

            # Comment count (span.comment_count)
            comment_count = 0
            comment_el = item.select_one("span.comment_count")
            if comment_el:
                comment_count = self._extract_number(comment_el.get_text())

            # Author (span.author)
            author = "Unknown"
            author_el = item.select_one("span.author")
            if author_el:
                author_text = author_el.get_text(strip=True)
                # Remove leading "/ " prefix
                author = re.sub(r'^/\s*', '', author_text) or "Unknown"

            return {
                "external_id": external_id,
                "url": full_url,
                "title": title,
                "author": author,
                "published_at": published_at,
                "view_count": 0,
                "comment_count": comment_count,
                "price": price,
                "thumbnail_url": thumbnail_url,
                "mall_name": mall_name,
                "mall_product_url": None,
                "upvotes": upvotes,
                "downvotes": 0,
            }

        except Exception as e:
            self._log_error(
                type(e).__name__,
                f"Failed to parse card item: {str(e)}",
            )
            return None

    def parse_deal(self, raw_data) -> Optional[Dict[str, Any]]:
        """Parse a deal from either table row or card layout."""
        # Check if it's a table row
        if raw_data.name == "tr":
            return self._parse_deal_from_table_row(raw_data)
        else:
            return self._parse_deal_from_card(raw_data)

    def fetch_deals(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Fetch deals from FMKorea."""
        all_deals = []

        print(f"📄 Crawling board: {self.DEAL_BOARD_URL}")

        for page in range(1, max_pages + 1):
            print(f"   Page {page}/{max_pages}...", end=" ")

            soup = self._fetch_page(self.DEAL_BOARD_URL, page)
            if not soup:
                print("❌ Failed")
                continue

            page_deals = []

            # Strategy 1: fm_best_widget card layout (default FMKorea hotdeal)
            # Structure: .fm_best_widget > div.li (each deal card)
            widget = soup.select_one(".fm_best_widget")
            if widget:
                items = widget.select("div.li")
                for item in items:
                    deal_data = self._parse_deal_from_card(item)
                    if deal_data:
                        page_deals.append(deal_data)

            # Strategy 2: Table-based layout (list view ?listStyle=list)
            if not page_deals:
                table_body = soup.select_one("table.bd_lst tbody")
                if table_body:
                    rows = table_body.find_all("tr")
                    for row in rows:
                        row_classes = " ".join(row.get("class", []))
                        if row.find("th") or "notice" in row_classes:
                            continue
                        deal_data = self._parse_deal_from_table_row(row)
                        if deal_data:
                            page_deals.append(deal_data)

            print(f"✓ Found {len(page_deals)} deals")
            all_deals.extend(page_deals)

            self._respect_rate_limit()

        return all_deals


def run_fmkorea_crawler(db, max_pages: int = 5):
    """Convenience function to run FMKorea crawler."""
    crawler = FmkoreaCrawler(db)
    return crawler.run(max_pages=max_pages)
