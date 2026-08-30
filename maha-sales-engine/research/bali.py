from __future__ import annotations

from typing import Any

# Curated from publicly discoverable Bali business listings retrieved on 2026-08-30.
# This is a research seed, not a claim of ownership/contact authority.
REAL_BALI_LEADS: list[dict[str, Any]] = [
    {
        "company": "IJEN BALI Transport", "name": "", "phone": "+62 811-366-936",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Wego Bali Tour", "name": "", "phone": "+62 819-9935-3723",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Bali Dilang Tour", "name": "", "phone": "+62 819-3307-7529",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Bali Rahayu Tour", "name": "", "phone": "+62 812-3791-1797",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "NANA BALI TOUR", "name": "", "phone": "+62 853-3778-1008",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Bali Private Experience", "name": "", "phone": "+62 812-3615-7587",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Bali Flamboyan Tour and Travel", "name": "", "phone": "+62 878-6193-6668",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Semara Bali Tours", "name": "", "phone": "+62 812-3675-4119",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "Indo Trip", "name": "", "phone": "+62 361 726571",
        "industry": "tour operator", "country": "Indonesia", "source": "business_directory",
        "source_url": "web:business-search-bali", "website": ""
    },
    {
        "company": "BALI ROA MANDIRI TOURS & TRAVEL", "name": "", "phone": "+62 361 723419",
        "industry": "tour operator", "country": "Indonesia", "source": "ASITA Bali",
        "source_url": "https://www.asitabali.org/id/keanggotaan/full-member?alpha=k&f_akt=&f_mrk=&f_mrk_g=&key=&search_type=",
        "website": "https://www.kalokatour.com"
    },
]


def get_bali_research_leads(limit: int = 10) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    return REAL_BALI_LEADS[: min(limit, len(REAL_BALI_LEADS))]
