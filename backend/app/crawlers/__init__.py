"""
Crawlers package for deal aggregation.
"""
from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.ppomppu import PpomppuCrawler, run_ppomppu_crawler

__all__ = [
    "BaseCrawler",
    "PpomppuCrawler",
    "run_ppomppu_crawler",
]
