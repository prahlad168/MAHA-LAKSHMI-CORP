"""MAHA research adapters."""

from .web_search import DuckDuckGoResearchProvider, WebResearchError, discover_bali_businesses
from .bali import REAL_BALI_LEADS, get_bali_research_leads

__all__ = [
    "DuckDuckGoResearchProvider", "WebResearchError", "discover_bali_businesses",
    "REAL_BALI_LEADS", "get_bali_research_leads",
]
