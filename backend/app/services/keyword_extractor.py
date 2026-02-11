"""
Keyword extraction service for deals.
Extracts keywords from deal titles and content for fast matching.
"""
import re
from typing import List, Set
from sqlalchemy.orm import Session

from app.models import Deal, DealKeyword


class KeywordExtractor:
    """
    Extract keywords from deal text for indexing and matching.
    """

    # Common Korean stop words to exclude
    STOP_WORDS = {
        "입니다", "있습니다", "합니다", "됩니다", "하는", "있는", "되는",
        "이", "가", "을", "를", "은", "는", "의", "에", "에서", "으로", "로",
        "이다", "하다", "되다", "있다", "없다", "좋다", "나쁘다",
        "그", "저", "이것", "저것", "그것", "여기", "저기", "거기",
        "오늘", "어제", "내일", "지금", "현재", "최근",
        "및", "또한", "그리고", "하지만", "그러나", "등",
    }

    # Minimum keyword length
    MIN_KEYWORD_LENGTH = 2

    # Maximum keywords per deal
    MAX_KEYWORDS = 50

    @staticmethod
    def extract_keywords(text: str, source: str = "title") -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Text to extract keywords from
            source: Source of text ('title', 'content', 'product_name')

        Returns:
            List of extracted keywords
        """
        if not text:
            return []

        keywords = set()

        # 1. Extract Korean words (2+ characters)
        korean_words = re.findall(r'[가-힣]{2,}', text)
        for word in korean_words:
            if word not in KeywordExtractor.STOP_WORDS:
                if len(word) >= KeywordExtractor.MIN_KEYWORD_LENGTH:
                    keywords.add(word)

        # 2. Extract English words (2+ characters)
        english_words = re.findall(r'\b[A-Za-z]{2,}\b', text)
        for word in english_words:
            word_lower = word.lower()
            if len(word_lower) >= KeywordExtractor.MIN_KEYWORD_LENGTH:
                keywords.add(word_lower)

        # 3. Extract numbers (potential model numbers or prices)
        # e.g., "RTX4090", "256GB", "5600X"
        alphanumeric = re.findall(r'\b[A-Z0-9]{3,}\b', text.upper())
        keywords.update(alphanumeric)

        # 4. Extract brand names and model numbers
        # Common patterns: "갤럭시S23", "아이폰15", "RTX 4090"
        patterns = [
            r'갤럭시\s*[A-Z]?\d+',
            r'아이폰\s*\d+',
            r'RTX\s*\d+',
            r'GTX\s*\d+',
            r'[A-Z]+\d{3,}',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update([m.replace(' ', '').lower() for m in matches])

        # Limit number of keywords
        keywords_list = list(keywords)[:KeywordExtractor.MAX_KEYWORDS]

        return keywords_list

    @staticmethod
    def extract_and_save(db: Session, deal: Deal) -> int:
        """
        Extract keywords from a deal and save to database.

        Args:
            db: Database session
            deal: Deal object to extract keywords from

        Returns:
            Number of keywords extracted
        """
        all_keywords = []

        # Extract from title
        if deal.title:
            keywords = KeywordExtractor.extract_keywords(deal.title, source="title")
            all_keywords.extend([
                {"keyword": kw, "source": "title"} for kw in keywords
            ])

        # Extract from product name
        if deal.product_name:
            keywords = KeywordExtractor.extract_keywords(deal.product_name, source="product_name")
            all_keywords.extend([
                {"keyword": kw, "source": "product_name"} for kw in keywords
            ])

        # Extract from content (if available)
        if deal.content:
            # Limit content to first 500 characters to avoid too many keywords
            content_preview = deal.content[:500]
            keywords = KeywordExtractor.extract_keywords(content_preview, source="content")
            all_keywords.extend([
                {"keyword": kw, "source": "content"} for kw in keywords[:20]  # Limit content keywords
            ])

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw_dict in all_keywords:
            if kw_dict["keyword"] not in seen:
                seen.add(kw_dict["keyword"])
                unique_keywords.append(kw_dict)

        # Delete existing keywords for this deal
        db.query(DealKeyword).filter_by(deal_id=deal.id).delete()

        # Insert new keywords
        for kw_dict in unique_keywords:
            deal_keyword = DealKeyword(
                deal_id=deal.id,
                keyword=kw_dict["keyword"],
                source=kw_dict["source"]
            )
            db.add(deal_keyword)

        db.commit()

        return len(unique_keywords)

    @staticmethod
    def batch_extract_and_save(db: Session, deals: List[Deal]) -> int:
        """
        Extract keywords from multiple deals in batch.

        Args:
            db: Database session
            deals: List of Deal objects

        Returns:
            Total number of keywords extracted
        """
        total_keywords = 0

        for deal in deals:
            count = KeywordExtractor.extract_and_save(db, deal)
            total_keywords += count

        return total_keywords
