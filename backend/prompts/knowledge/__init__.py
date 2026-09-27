"""
Jithendra's Portfolio & Research Knowledge Base Package.
Divided into modular subfiles:
- profile.py: Biographical details, education, competitive exams, skills, and experience
- publications.py: Peer-reviewed research papers (Elsevier EAAI, Elsevier COR, Springer LNCS)
- projects.py: Engineering projects and UI navigation targets
- pages.py: Structured screen knowledge and empirical results for all portfolio routes
"""

from .pages import (
    PAGE_KNOWLEDGE,
    SECTION_KNOWLEDGE,
    get_formatted_section_explanation,
    get_section_knowledge,
)
from .profile import (
    BIOGRAPHY,
    COMPETITIVE_EXAMS,
    EDUCATION,
    TECHNICAL_SKILLS,
    WORK_EXPERIENCE,
)
from .projects import NAVIGATION_TARGETS, PROJECTS
from .publications import PUBLICATIONS

__all__ = [
    "BIOGRAPHY",
    "EDUCATION",
    "COMPETITIVE_EXAMS",
    "TECHNICAL_SKILLS",
    "WORK_EXPERIENCE",
    "PUBLICATIONS",
    "PROJECTS",
    "NAVIGATION_TARGETS",
    "PAGE_KNOWLEDGE",
    "SECTION_KNOWLEDGE",
    "get_section_knowledge",
    "get_formatted_section_explanation",
]
