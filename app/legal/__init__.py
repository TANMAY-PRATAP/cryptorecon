"""Module 7: Closed-Loop Asset Recovery & Statutory Legal Dispatch."""

from app.legal.p2p_restitcher import P2PRestitcher
from app.legal.pdf_generator import LegalNoticeGenerator, get_legal_generator

__all__ = [
    "P2PRestitcher",
    "LegalNoticeGenerator",
    "get_legal_generator",
]
