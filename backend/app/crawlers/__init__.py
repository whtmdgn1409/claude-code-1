"""
Crawlers package for deal aggregation.
"""
from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.ppomppu import PpomppuCrawler, run_ppomppu_crawler
from app.crawlers.ruliweb import RuliwebCrawler, run_ruliweb_crawler
from app.crawlers.quasarzone import QuasarzoneCrawler, run_quasarzone_crawler
from app.crawlers.fmkorea import FmkoreaCrawler, run_fmkorea_crawler

__all__ = [
    "BaseCrawler",
    "PpomppuCrawler",
    "run_ppomppu_crawler",
    "RuliwebCrawler",
    "run_ruliweb_crawler",
    "QuasarzoneCrawler",
    "run_quasarzone_crawler",
    "FmkoreaCrawler",
    "run_fmkorea_crawler",
]
