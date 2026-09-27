"""
Dynamic Prompt Builder for Jithendra's Portfolio Voice AI.
Loads only relevant section knowledge based on active screen/context to minimize token usage.
"""

from typing import Optional, Dict, Any, List
from .knowledge import (
    BIOGRAPHY,
    EDUCATION,
    COMPETITIVE_EXAMS,
    PUBLICATIONS,
    PROJECTS,
    TECHNICAL_SKILLS,
    WORK_EXPERIENCE,
    NAVIGATION_TARGETS,
    PAGE_KNOWLEDGE,
    SECTION_KNOWLEDGE,
    get_section_knowledge,
)
from .response_policy import COMMON_RESPONSE_POLICY


# Base identity - always included (compact)
BASE_IDENTITY = (
    "You are the Voice AI Assistant for Kandula Jithendra Subramanyam "
    "(M.Tech AI & Data Science, Somaiya Vidyavihar Univ; B.Tech ECE, Presidency Univ; GATE 2024 DA & CS). "
    "AI Systems Engineer & Quantitative Researcher with 3 peer-reviewed publications "
    "(Elsevier EAAI, Springer Nature LNCS, Elsevier COR). "
    "Contact: kandulajithendrasubramanyam@gmail.com."
)

# Navigation targets - always available
NAV_TARGETS_LIST = ", ".join([f"'{k}'" for k in NAVIGATION_TARGETS.keys()])


def build_base_system_instructions() -> str:
    """Ultra-compact base system prompt under 500 chars for minimal TTFT."""
    return (
        f"{BASE_IDENTITY}\n"
        f"RESPONSE RULES:\n"
        f"1. Short Mode: <20 words. Long Mode: 45-70 words, key result first.\n"
        f"2. Speak naturally: short sentences, no markdown, no bullet lists.\n"
        f"3. Match listener: plain words for visitors, technical precision for engineers.\n"
        f"4. Call navigate_portfolio(target) immediately when asked to view any section or case study.\n"
        f"5. Valid targets: {NAV_TARGETS_LIST}\n"
        f"6. Transfers: transfer_to_research (math/proofs), transfer_to_engineering (robotics/code), transfer_to_booking (meetings).\n"
        f"7. Only use verified portfolio facts. Never fabricate.\n"
        f"{COMMON_RESPONSE_POLICY}"
    )


def build_section_context_prompt(active_screen: str, active_title: str = "") -> str:
    """
    Builds context-specific prompt addition based on the currently active screen/section.
    Only loads knowledge relevant to what the user is currently viewing.
    """
    # Normalize the active screen
    clean_screen = active_screen.strip().lower().replace("#", "").replace("/", "")
    
    # Get relevant knowledge
    knowledge = get_section_knowledge(clean_screen)
    
    if not knowledge:
        # Try route-based lookup
        route_key = "/" + clean_screen if not clean_screen.startswith("/") else clean_screen
        knowledge = PAGE_KNOWLEDGE.get(route_key)
    
    if not knowledge:
        return ""
    
    # Build focused context
    title = knowledge.get("title", "")
    what_it_tells = knowledge.get("what_it_tells") or knowledge.get("summary", "")
    key_elements = knowledge.get("key_elements", [])
    
    # Extract mathematical rigor if present
    math_rigor = knowledge.get("mathematical_rigor", "")
    empirical_results = knowledge.get("empirical_results", [])
    architecture_agents = knowledge.get("architecture_agents", [])
    technical_highlights = knowledge.get("technical_highlights", [])
    
    context_lines = [f"\n### ACTIVE SCREEN CONTEXT: {title}"]
    
    if what_it_tells:
        context_lines.append(f"Content: {what_it_tells}")
    
    if key_elements:
        context_lines.append(f"Key elements: {', '.join(key_elements[:5])}.")
    
    if math_rigor:
        context_lines.append(f"Mathematical formulation: {math_rigor}")
    
    if empirical_results:
        results_str = "; ".join(empirical_results[:3])
        context_lines.append(f"Key results: {results_str}.")
    
    if architecture_agents:
        agents_str = "; ".join([f"{a.split(':')[0].strip()}: {':'.join(a.split(':')[1:]).strip()}" for a in architecture_agents[:3]])
        context_lines.append(f"Architecture agents: {agents_str}.")
    
    if technical_highlights:
        highlights_str = "; ".join(technical_highlights[:3])
        context_lines.append(f"Technical highlights: {highlights_str}.")
    
    return "\n".join(context_lines)


def build_publication_context_prompt(target_publication: str) -> str:
    """Builds focused context for a specific publication when discussed."""
    pub_map = {p["target_nav"]: p for p in PUBLICATIONS}
    pub = pub_map.get(target_publication)
    
    if not pub:
        return ""
    
    lines = [f"\n### PUBLICATION CONTEXT: {pub['title']}"]
    lines.append(f"Venue: {pub['venue']} ({pub['status']})")
    lines.append(f"Authors: {pub['authors']}")
    lines.append(f"Summary: {pub['summary']}")
    return "\n".join(lines)


def build_project_context_prompt(target_project: str) -> str:
    """Builds focused context for a specific project when discussed."""
    proj_map = {p["target_nav"]: p for p in PROJECTS}
    proj = proj_map.get(target_project)
    
    if not proj:
        return ""
    
    lines = [f"\n### PROJECT CONTEXT: {proj['name']}"]
    lines.append(f"Description: {proj['description']}")
    return "\n".join(lines)


def build_research_detail_prompt(query_topic: str) -> str:
    """
    Builds focused research context when user asks about specific mathematical concepts,
    theorems, or metrics from the papers.
    """
    knowledge = get_section_knowledge(query_topic)
    if not knowledge:
        return ""
    
    title = knowledge.get("title", "")
    what_it_tells = knowledge.get("what_it_tells", "")
    math_rigor = knowledge.get("mathematical_rigor", "")
    empirical_results = knowledge.get("empirical_results", [])
    
    lines = [f"\n### RESEARCH DETAIL: {title}"]
    if what_it_tells:
        lines.append(what_it_tells)
    if math_rigor:
        lines.append(f"Formulation: {math_rigor}")
    if empirical_results:
        lines.append(f"Results: {'; '.join(empirical_results[:3])}.")
    
    return "\n".join(lines)


def get_full_system_prompt(
    active_screen: str = "/",
    active_title: str = "",
    recent_topics: Optional[List[str]] = None
) -> str:
    """
    Composes the complete system prompt with base identity + active screen context + relevant detail.
    
    Args:
        active_screen: Current route/section (e.g., "/", "/projects/adaptive-portfolio-governance", "#skills")
        active_title: Page title from client context
        recent_topics: List of recently discussed topics for contextual relevance
        
    Returns:
        Complete system prompt optimized for token efficiency
    """
    base = build_base_system_instructions()
    
    # Add active screen context (always relevant)
    screen_context = build_section_context_prompt(active_screen, active_title)
    
    # Add publication context if on a case study page
    pub_context = ""
    case_study_targets = [
        "case_study_adaptive_governance",
        "case_study_regime_supervisory", 
        "case_study_supervisory_xai",
        "case_study_voice_architecture",
        "case_study_aqi",
        "case_study_swarm_robotics",
    ]
    
    clean_screen = active_screen.strip().lower().replace("#", "").replace("/", "")
    if clean_screen in case_study_targets:
        pub_context = build_publication_context_prompt(clean_screen)
    
    # Add project context if on project page
    project_context = ""
    if clean_screen.startswith("projects/") or clean_screen in case_study_targets:
        project_context = build_project_context_prompt(clean_screen)
    
    # Combine all context
    parts = [base]
    if screen_context:
        parts.append(screen_context)
    if pub_context:
        parts.append(pub_context)
    if project_context:
        parts.append(project_context)
    
    # Add recent topics context if available
    if recent_topics:
        topic_contexts = []
        for topic in recent_topics[-3:]:  # Last 3 topics
            if topic in case_study_targets:
                ctx = build_publication_context_prompt(topic)
            else:
                ctx = build_research_detail_prompt(topic)
            if ctx:
                topic_contexts.append(ctx)
        if topic_contexts:
            parts.append("\n### RECENT CONTEXT:")
            parts.extend(topic_contexts)
    
    return "\n".join(parts)


def get_specialist_instructions(specialist: str, active_screen: str = "/") -> str:
    """
    Returns specialist-specific instructions with minimal relevant context.
    Used when agent handoff occurs.
    """
    base = build_base_system_instructions()
    screen_context = build_section_context_prompt(active_screen)
    
    specialist_contexts = {
        "greeter": (
            f"\n### GREETER SPECIALIST ROLE:\n"
            f"1. Welcome callers warmly and use navigate_portfolio(target) to visually show what they ask about — IMMEDIATELY.\n"
            f"2. For deep math/proofs/citations: invoke transfer_to_research(reason).\n"
            f"3. For engineering/robotics/firmware/architecture: invoke transfer_to_engineering(reason).\n"
            f"4. For hiring/collab/meetings: invoke transfer_to_booking(reason).\n"
            f"5. If intent unclear, ask ONE targeted clarifying question."
        ),
        "research": (
            f"\n### RESEARCH SPECIALIST ROLE:\n"
            f"1. Mastery over 3 peer-reviewed publications (EAAI G-CVaR, LNCS Regime-Adaptive, COR 7-Agent XAI).\n"
            f"2. Lead with exact numbers and formulations. Verbal precision over prose.\n"
            f"3. Use semantic_knowledge_search for specific theorems, metrics, or citations.\n"
            f"4. Use navigate_portfolio to show corresponding case study pages.\n"
            f"5. Transfer: transfer_to_booking (hiring), transfer_to_greeter (overview).\n"
            f"6. Short mode: <20 words. Long mode: 45-70 words, key result first."
        ),
        "engineering": (
            f"\n### ENGINEERING SPECIALIST ROLE:\n"
            f"1. Expert in: Voice AI Architecture (LiveKit, Groq LPU, Cartesia, Deepgram), Swarm Robotics (ESP32, ESP-NOW), AQI Forecasting (XGBoost), Agentic Systems (LangGraph).\n"
            f"2. Explain architectures, dataflows, and implementation details with technical precision.\n"
            f"3. Use navigate_portfolio to show engineering case studies.\n"
            f"4. Transfer: transfer_to_research (math), transfer_to_greeter (overview), transfer_to_booking (collab)."
        ),
        "booking": (
            f"\n### BOOKING SPECIALIST ROLE:\n"
            f"1. Handle appointment scheduling via /book-appointment page.\n"
            f"2. Collect: name, email, date/time preference, meeting purpose, notes, resume attachment.\n"
            f"3. Confirm Google Calendar + Google Meet link generation.\n"
            f"4. Use navigate_portfolio('book_appointment') to show booking page.\n"
            f"5. Transfer: transfer_to_greeter for portfolio questions."
        ),
    }
    
    specialist_inst = specialist_contexts.get(specialist, "")
    parts = [base]
    if screen_context:
        parts.append(screen_context)
    if specialist_inst:
        parts.append(specialist_inst)
    
    return "\n".join(parts)


__all__ = [
    "build_base_system_instructions",
    "build_section_context_prompt",
    "build_publication_context_prompt",
    "build_project_context_prompt",
    "build_research_detail_prompt",
    "get_full_system_prompt",
    "get_specialist_instructions",
]