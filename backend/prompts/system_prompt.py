"""
System Instructions Builder for Jithendra's Voice AI Assistant.
Formats biography, research papers, projects, and voice policies into an ultra-low-latency prompt.
Supports dynamic context-aware prompt generation to minimize token usage.
"""

from .dynamic_prompts import (
    build_base_system_instructions,
    build_section_context_prompt,
    build_publication_context_prompt,
    build_project_context_prompt,
    build_research_detail_prompt,
    get_full_system_prompt,
    get_specialist_instructions,
)


def build_system_instructions() -> str:
    """Ultra-compact base system prompt under 500 chars to minimize TTFT and prevent token rate limits."""
    return build_base_system_instructions()


# Base system instructions (backward compatibility)
SYSTEM_INSTRUCTIONS = build_system_instructions()

# Dynamic prompt functions for context-aware generation
__all__ = [
    "SYSTEM_INSTRUCTIONS",
    "build_system_instructions",
    "build_section_context_prompt",
    "build_publication_context_prompt",
    "build_project_context_prompt",
    "build_research_detail_prompt",
    "get_full_system_prompt",
    "get_specialist_instructions",
]