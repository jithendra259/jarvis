"""
Prompts and Knowledge package for Jithendra's Portfolio AI.
"""

from .knowledge import (
    BIOGRAPHY,
    COMPETITIVE_EXAMS,
    EDUCATION,
    PUBLICATIONS,
    PROJECTS,
    TECHNICAL_SKILLS,
    WORK_EXPERIENCE,
    NAVIGATION_TARGETS,
    PAGE_KNOWLEDGE,
    SECTION_KNOWLEDGE,
    get_section_knowledge,
    get_formatted_section_explanation,
)
from .pronunciations import PRONUNCIATION_REPLACEMENTS
from .system_prompt import (
    SYSTEM_INSTRUCTIONS,
    build_system_instructions,
    build_section_context_prompt,
    build_publication_context_prompt,
    build_project_context_prompt,
    build_research_detail_prompt,
    get_full_system_prompt,
    get_specialist_instructions,
)
from .response_policy import COMMON_RESPONSE_POLICY

__all__ = [
    "BIOGRAPHY",
    "COMPETITIVE_EXAMS",
    "EDUCATION",
    "PUBLICATIONS",
    "PROJECTS",
    "TECHNICAL_SKILLS",
    "WORK_EXPERIENCE",
    "NAVIGATION_TARGETS",
    "PAGE_KNOWLEDGE",
    "SECTION_KNOWLEDGE",
    "PRONUNCIATION_REPLACEMENTS",
    "SYSTEM_INSTRUCTIONS",
    "build_system_instructions",
    "build_section_context_prompt",
    "build_publication_context_prompt",
    "build_project_context_prompt",
    "build_research_detail_prompt",
    "get_full_system_prompt",
    "get_specialist_instructions",
    "COMMON_RESPONSE_POLICY",
    "get_section_knowledge",
    "get_formatted_section_explanation",
]