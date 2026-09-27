"""
Structured page and section knowledge for Kandula Jithendra Subramanyam's portfolio.
Provides granular descriptions of every page route, homepage section, and case study subsection.
"""

from typing import Any, Optional

PAGE_KNOWLEDGE = {
    "/": {
        "title": "Portfolio Homepage & Overview",
        "route": "/",
        "type": "overview",
        "summary": (
            "Kandula Jithendra Subramanyam's master portfolio overview. Showcases interactive 3D Mascot Robot, "
            "academic credentials (M.Tech AI Somaiya, B.Tech ECE Presidency, GATE DA & CS), three 2026 research publications "
            "(Elsevier EAAI, Springer LNCS, Elsevier COR), engineering projects bento grid, skills matrix, career timeline, "
            "verified certificates, and 30-minute Google Calendar appointment booking."
        ),
        "key_sections": [
            "Hero: 3D Mascot Robot, Biometric Handshake & Voice Agent Trigger",
            "About Me: Quantitative finance, multi-agent swarms, and convex optimization mission",
            "Research Bento: Elsevier EAAI-26-14280, Springer LNCS (IJCACI 2026), Elsevier COR",
            "Featured Projects: AQI Forecasting, Swarm Robotics, Agentic Portfolio Governance",
            "Technical Skills: PyTorch, CVXPY, CLARABEL, LangGraph, Next.js 15, LiveKit WebRTC",
            "Career & Education: Somaiya M.Tech (CGPA 8.06), Presidency B.Tech (CGPA 7.77)",
            "Certificates: GATE 2024 (DA & CS qualified), Deep Learning, Cloud Architecture",
            "Contact & Booking: Interactive appointment calendar with Google Meet integration",
        ],
    },
    "/projects/adaptive-portfolio-governance": {
        "title": "Multi-Agent Adaptive Portfolio Governance System",
        "route": "/projects/adaptive-portfolio-governance",
        "type": "research_case_study",
        "venue": "Elsevier Engineering Applications of Artificial Intelligence (EAAI-26-14280) & Springer Nature LNCS",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Jadhav",
        "summary": (
            "Pioneering five-agent blackboard governance architecture for institutional portfolio optimization addressing "
            "fire-sale contagion via SEC 13-F bipartite co-holding networks. Integrates graph-regularized CVaR (G-CVaR) with "
            "adaptive sigmoid-gated Laplacian penalties and Ledoit-Wolf optimal shrinkage."
        ),
        "architecture_agents": [
            "Agent 0 (Ingestion): 218 US equities, 11 GICS sectors, 552 rolling windows (2005-2025), SEC 13-F holdings",
            "Agent 1 (Instability Analysis): Composite volatility, correlation stress, and covariance drift tracking",
            "Agent 2 (Contagion Graph): Bipartite institutional co-ownership network with normalized Laplacian L",
            "Agent 3 (G-CVaR Optimization): Graph-regularized CVaR solved via CLARABEL interior-point SOCP solver",
            "Agent 4 (XAI & Governance): Mistral-7B explanation generation and MiFID II / EU AI Act audit logging",
        ],
        "mathematical_rigor": (
            "G-CVaR formulation: min_{w, gamma, u} gamma + (1 / ((1 - beta) * T)) * sum(u_t) + lambda_G * (w^T * L * w) "
            "subject to sum(w) = 1, w >= 0, where L = I - D^{-1/2} * A * D^{-1/2} is the normalized graph Laplacian, "
            "and lambda_G is dynamically gated by a sigmoid function of market instability."
        ),
        "empirical_results": [
            "25.9% reduction in CVaR-95% across 11 sector universes vs equal-weight benchmark",
            "32.5 percentage point reduction in crisis period drawdown during GFC 2008",
            "100% trigger accuracy and 96.9% narrative accuracy across 160 governance evaluation scenarios",
            "552 rolling windows evaluated over 20 years of real US equity market data (2005-2025)",
        ],
    },
    "/projects/regime-adaptive-supervisory-governance": {
        "title": "Regime-Adaptive Supervisory Governance for Instability-Aware Portfolio Stabilization",
        "route": "/projects/regime-adaptive-supervisory-governance",
        "type": "research_case_study",
        "venue": "Springer Nature LNCS / 5th International Joint Conference on Advances in Computational Intelligence (IJCACI 2026)",
        "location": "Washington University of Science and Technology (WUST), Alexandria, USA",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Vilas Jadhav, Ashwini Dalvi",
        "summary": (
            "Interpretable supervisory governance coupling covariance drift, rolling volatility, and correlation stress into "
            "a composite Instability Index I_t. Dynamically switches concentration limits and Ledoit-Wolf shrinkage intensity (alpha = 0.42) "
            "across Calm, Turbulent, and Crisis regimes."
        ),
        "mathematical_rigor": (
            "Composite Instability Index: I_t = w_1 * delta_t + w_2 * sigma_t + w_3 * rho_t, where delta_t is Frobenius norm covariance drift, "
            "sigma_t is cross-sectional volatility, and rho_t is average pairwise correlation. Controls deterministic transition between "
            "three market regimes with tailored constraint bounds."
        ),
        "empirical_results": [
            "Maximum drawdown contained to 32.5% across 218 US equities over 20 years",
            "38% reduction in tail-loss variance under high-stress regimes",
            "Average turnover per rebalance optimized to 0.0045, drastically lowering transaction drag",
        ],
    },
    "/projects/supervisory-portfolio-xai-governance": {
        "title": "A Supervisory Portfolio Governance Framework: Instability Detection, Regime Switching & Conversational Explainability",
        "route": "/projects/supervisory-portfolio-xai-governance",
        "type": "research_case_study",
        "venue": "Elsevier Computers & Operations Research (CAS Journal, Under Review 2026)",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Vilas Jadhav, Ashwini Dalvi",
        "summary": (
            "7-agent Directed Acyclic Graph (DAG) pipeline integrating CLARABEL conic interior-point solver with conversational Mistral-7B LLM. "
            "Achieves 100% numerical grounding (0% hallucination) by strictly validating solver inputs and outputs against immutable constraints, "
            "complying with MiFID II and EU AI Act Article 14 standards."
        ),
        "mathematical_rigor": (
            "Second-Order Cone Programming (SOCP) solved via CLARABEL. Guarantees convex optimality and bounds conversational explanations "
            "to verified solver dual variables and slack vectors, preventing quantitative hallucination."
        ),
        "empirical_results": [
            "0% hallucination rate across 500+ simulated regulatory audit inquiries",
            "Full MiFID II and EU AI Act Article 14 decision-trail logging with cryptographic timestamping",
            "Sub-50ms SOCP rebalancing convergence time",
        ],
    },
    "/projects/voice-agent-portfolio-architecture": {
        "title": "Real-Time Voice AI Portfolio & Agentic Web Architecture",
        "route": "/projects/voice-agent-portfolio-architecture",
        "type": "engineering_case_study",
        "summary": (
            "Production real-time conversational voice assistant running live on this portfolio. Combines Next.js 15 App Router, "
            "LiveKit WebRTC Cloud, Groq LPU (sub-90ms TTFT primary LLM), Cartesia Sonic-3 neural TTS, Deepgram Nova-3 STT, "
            "and a custom WebGL Aura shader visualizer. Features bi-directional data channels for real-time screen auto-navigation."
        ),
        "technical_highlights": [
            "End-to-end voice roundtrip latency under 500ms using Groq LPU and Cartesia Sonic-3",
            "Bi-directional WebRTC data channel ('navigation', 'client_context') for real-time UI synchronization",
            "WebGL 3D Aura shader reacting to LiveKit audio tracks and agent conversational states",
            "Cloud-optimized Python worker architecture eliminating event-loop blocking on 0.1 vCPU container environments",
        ],
    },
    "/projects/agentic-portfolio-chatbot": {
        "title": "Agentic AI Portfolio Governance Chatbot",
        "route": "/projects/agentic-portfolio-chatbot",
        "type": "engineering_case_study",
        "summary": (
            "Interactive voice and conversational AI agent decoupled into 10+ agentic roles. Integrates LangGraph supervisor, "
            "LiveKit WebRTC, and CLARABEL convex solver for real-time financial portfolio queries and UI control."
        ),
    },
    "/projects/personalised-aqi-system": {
        "title": "Personalised AQI Global Air Quality Forecasting",
        "route": "/projects/personalised-aqi-system",
        "type": "machine_learning_case_study",
        "summary": (
            "Air quality forecasting engine using XGBoost, Markov Chains, and ARIMA trained on 10 Central Pollution Control Board (CPCB) "
            "monitoring stations across Delhi. XGBoost achieved test R² = 0.912 and RMSE of 18.4 ug/m3 for 48-hour PM2.5 prediction."
        ),
        "technical_highlights": [
            "Trained on multi-year hourly CPCB sensor telemetry (PM2.5, PM10, NO2, SO2, CO, Ozone)",
            "Engineered rolling temporal lags, planetary boundary layer dynamics, and wind vector transformations",
            "Interactive Next.js 15 frontend with geospatial pollutant heatmaps and health recommendations",
        ],
    },
    "/projects/swarm-robots-agriculture": {
        "title": "Autonomous Swarm Robots for Precision Agriculture",
        "route": "/projects/swarm-robots-agriculture",
        "type": "robotics_case_study",
        "summary": (
            "Decentralized IoT hardware-software swarm using ESP32 microcontrollers, ESP-NOW peer-to-peer mesh networking, "
            "and edge DenseNet121 vision for precision plant pathology. Awarded KSCST 46th Series Project Grant."
        ),
        "technical_highlights": [
            "98.4% autonomous field coverage without cellular or GPS infrastructure via localized mesh discovery",
            "96.8% edge disease classification accuracy using quantized convolutional neural networks",
            "Dynamic peer election and distributed fault-tolerant routing among robotic nodes",
        ],
    },
    "/book-appointment": {
        "title": "Interactive Meeting & Interview Booking",
        "route": "/book-appointment",
        "type": "service",
        "summary": (
            "Dedicated appointment scheduling interface for recruiters, collaborators, and engineering leads. "
            "Allows selecting 30-minute meeting slots with real-time Google Calendar synchronization and automatic Google Meet link generation."
        ),
    },
}


# ==============================================================================
# DETAILED SECTION & SUBSECTION KNOWLEDGE
# ==============================================================================

SECTION_KNOWLEDGE = {
    # ── Homepage Sections ─────────────────────────────────────────────────────
    "home": {
        "title": "Hero & Overview Section",
        "anchor": "#home",
        "route": "/",
        "what_it_tells": (
            "The top hero section introduces Kandula Jithendra Subramanyam as an AI & Quantitative Systems Researcher. "
            "It features an interactive 3D Mascot robot that tracks cursor gestures, a biometric handshake animation, "
            "a floating 'Ask Voice Agent' button that connects to this LiveKit conversational assistant, and quick metric chips "
            "highlighting 3 research publications, 2 research grants, and an 8.52 CGPA."
        ),
        "key_elements": [
            "Interactive 3D Mascot Robot",
            "Candidate Title & Value Proposition",
            "Biometric Handshake UI",
            "LiveKit Real-Time Voice Agent Trigger",
            "Direct Navigation Action Buttons",
        ],
    },
    "about": {
        "title": "About & Credentials Section",
        "anchor": "#about",
        "route": "/",
        "what_it_tells": (
            "This section details Jithendra's background, research philosophy, and academic foundation. "
            "It explains his focus on convex risk optimization, graph-regularized loss formulations, and multi-agent systems. "
            "It highlights his M.Tech degree in AI & Data Science at Somaiya Vidyavihar (CGPA 8.06) / Amrita, his B.Tech in ECE at "
            "Presidency University (CGPA 7.77, KSCST Grant recipient), and his double GATE 2024 qualification in Data Science & AI and CS."
        ),
        "key_elements": [
            "Research Mission & Quantitative Philosophy",
            "Core Specializations: Convex Optimization & Multi-Agent Swarms",
            "Academic Degrees & Honors",
            "GATE 2024 Dual-Discipline Qualification",
        ],
    },
    "research": {
        "title": "Research Bento & Peer-Reviewed Publications",
        "anchor": "#research",
        "route": "/",
        "what_it_tells": (
            "The Research Bento grid presents Jithendra's 3 peer-reviewed quantitative finance and AI papers: "
            "1. Elsevier EAAI (2025/2026): Multi-Agent Governance via Graph-CVaR (G-CVaR) and SEC 13-F Network (+38.6% Sharpe, -42.1% drawdown). "
            "2. Springer Nature LNCS (IJCACI 2026): Regime-Adaptive Supervisory Governance with Instability Index I_t and Ledoit-Wolf shrinkage (alpha=0.42). "
            "3. Elsevier Computers & Operations Research (COR 2026): 7-Agent DAG with CLARABEL conic solver and Mistral-7B MiFID II audit trails. "
            "Each paper card includes direct PDF download links, venue badges, and deep-dive case study route buttons."
        ),
        "key_elements": [
            "Elsevier EAAI Paper Card & Case Study Link",
            "Springer Nature LNCS Paper Card & Case Study Link",
            "Elsevier COR Paper Card & Case Study Link",
            "One-Click Direct Research PDF Downloads",
            "Mathematical Formulation Callouts",
        ],
    },
    "projects": {
        "title": "Featured Engineering Projects Bento",
        "anchor": "#projects",
        "route": "/",
        "what_it_tells": (
            "The Projects section showcases 4 flagship engineering implementations: "
            "1. Personalised AQI System: XGBoost regressor trained on 10 CPCB Delhi stations predicting PM2.5 and PM10 with R²=0.912. "
            "2. Autonomous Swarm Robotics: Decentralized ESP32 wireless mesh with ESP-NOW protocol and DenseNet121 plant disease vision (KSCST Grant). "
            "3. Real-Time Voice AI Architecture: LiveKit WebRTC, Groq LPU, Cartesia Sonic-3 neural TTS, Deepgram Nova-3 STT, and Supabase. "
            "4. Agentic Portfolio Chatbot: Multimodal financial governance assistant with LangGraph supervisor. "
            "Each project features interactive case study modals and links to technical architectures."
        ),
        "key_elements": [
            "Personalised AQI System (Delhi CPCB Sensor Telemetry)",
            "Autonomous Swarm Robotics (ESP32 Mesh & ESP-NOW)",
            "LiveKit Real-Time WebRTC Voice AI Architecture",
            "Agentic Portfolio Chatbot with LangGraph",
        ],
    },
    "skills": {
        "title": "Skills Cards Stack & Technology Matrix",
        "anchor": "#skills",
        "route": "/",
        "what_it_tells": (
            "The Skills section features an interactive 4-card stack categorizing Jithendra's technical proficiencies: "
            "1. Languages: Python, TypeScript, JavaScript, C/C++, SQL, LaTeX, HTML5/CSS3. "
            "2. Machine Learning & AI: PyTorch, Scikit-learn, XGBoost, HuggingFace Transformers, LangGraph, OpenCV, NumPy. "
            "3. Quant & Optimization: CVXPY, CLARABEL (conic interior-point SOCP solver), G-CVaR, Ledoit-Wolf shrinkage, SEC 13-F bipartite graphs. "
            "4. Full-Stack & Systems: Next.js 15, LiveKit WebRTC, Cartesia Sonic-3, Deepgram Nova-3, Supabase, Tailwind CSS, Docker, Linux."
        ),
        "key_elements": [
            "Card 1: Programming Languages",
            "Card 2: Deep Learning & AI Frameworks",
            "Card 3: Quantitative Finance & Conic Optimization",
            "Card 4: Distributed Systems, WebRTC & Edge Hardware",
        ],
    },
    "experience": {
        "title": "Career & Education Timeline",
        "anchor": "#experience",
        "route": "/",
        "what_it_tells": (
            "The Experience & Education Timeline displays Jithendra's chronological academic and professional trajectory: "
            "1. M.Tech in Artificial Intelligence & Data Science at Somaiya Vidyavihar University / Amrita (2024–2026, CGPA 8.06/10). "
            "2. B.Tech in Electronics & Communication at Presidency University (2019–2023, CGPA 7.77/10). "
            "3. KSCST 46th Series Government Research Grant Awardee (Autonomous Swarm Robotics). "
            "4. Technical developer internships and quantitative research roles."
        ),
        "key_elements": [
            "Somaiya M.Tech AI & Data Science Degree",
            "Presidency University B.Tech ECE Degree",
            "Karnataka State Council for Science & Technology (KSCST) Grant",
            "Technical Internships & Lab Research Assistantships",
        ],
    },
    "certificates": {
        "title": "Certificates & Conference Awards",
        "anchor": "#certificates",
        "route": "/",
        "what_it_tells": (
            "The Certificates section highlights verified academic achievements and conference presentations: "
            "1. GATE 2024 double qualification in Data Science & AI (DA) and Computer Science & Information Technology (CS). "
            "2. IJCACI 2026 Conference Presentation Certificate at Washington University of Science and Technology (WUST), Alexandria, USA. "
            "3. Specialized certifications in Deep Learning, Convolutional Neural Networks, Cloud Computing, and Algorithmic Design."
        ),
        "key_elements": [
            "GATE 2024 Scorecards (DA & CS)",
            "Springer Nature IJCACI 2026 Conference Presentation Certificate",
            "Deep Learning & AI Specializations",
        ],
    },
    "resume": {
        "title": "Resume Preview & Download Section",
        "anchor": "#resume",
        "route": "/",
        "what_it_tells": (
            "The Resume section provides an interactive visual preview of Kandula Jithendra Subramanyam's professional resume. "
            "It summarizes education, research publications, awards, technical skills, and project metrics. "
            "It includes a direct 'Download Resume' action button that downloads Kandula_Jithendra_Subramanyam_Resume.pdf."
        ),
        "key_elements": [
            "Resume Interactive Viewer",
            "Direct Download Action Button",
            "One-Page Executive Summary",
        ],
    },
    "contact": {
        "title": "Contact & Collaboration Section",
        "anchor": "#contact",
        "route": "/",
        "what_it_tells": (
            "The Contact section, titled 'Let's Build Intelligent Systems Together', serves as the primary connection hub. "
            "It informs visitors that Jithendra is actively open for AI Engineering & Quantitative Research roles, thesis collaborations, "
            "and technical discussions. It features: "
            "1. Floating Interactive Contact Icons for GitHub (github.com/jithendra259), LinkedIn, Google Scholar, Email, and Twitter/X. "
            "2. The Pearl Button labeled 'Book Appointment' which navigates directly to the dedicated /book-appointment Google Meet scheduler. "
            "3. The Email Reveal Button with one-click copy for kandulajithendrasubramanyam@gmail.com."
        ),
        "key_elements": [
            "Title: 'Let's Build Intelligent Systems Together'",
            "Collaboration Scope: AI Roles, Quant Research, Speaking, Swarms",
            "Floating Icons: GitHub, LinkedIn, Google Scholar, Email, Twitter",
            "Pearl Button: Instant redirect to /book-appointment calendar",
            "Email Reveal Button: One-click copy for kandulajithendrasubramanyam@gmail.com",
        ],
    },
    "book_appointment": {
        "title": "Dedicated Meeting & Interview Scheduler",
        "anchor": "/book-appointment",
        "route": "/book-appointment",
        "what_it_tells": (
            "This dedicated booking page allows recruiters, hiring managers, and researchers to reserve a 1-on-1 meeting with Jithendra. "
            "It includes an interactive calendar date picker, time slot selection (IST/UTC), meeting purpose selector (Interview, Technical Chat, Research Collaboration), "
            "notes field, and document attachment upload. Submitting the form triggers automatic Google Calendar event creation, Google Meet link generation, "
            "and instant lead persistence into Supabase."
        ),
        "key_elements": [
            "Interactive Date & Time Slot Picker",
            "Meeting Purpose & Recruiter Intake",
            "Document / Resume Attachment Upload",
            "Automatic Google Meet Conference Link Generation",
            "Direct Sync with Jithendra's Google Calendar",
            "Supabase Non-Blocking Lead Logging",
        ],
    },

    # ── Case Study Subsections (Academic Layout) ──────────────────────────────
    "sec-abstract": {
        "title": "Abstract & Keywords Subsection",
        "anchor": "#sec-abstract",
        "what_it_tells": (
            "The Abstract subsection introduces the paper's central thesis, research context, and core mathematical contribution. "
            "It outlines the institutional portfolio problem, systemic fire-sale contagion risk under SEC 13-F bipartite holding graphs, "
            "and key results (e.g. 25.9% CVaR reduction, 38.6% Sharpe boost, and 42.1% drawdown reduction)."
        ),
    },
    "sec-intro": {
        "title": "Introduction & Motivation Subsection",
        "anchor": "#sec-intro",
        "what_it_tells": (
            "The Introduction section details the empirical breakdown of standard Markowitz mean-variance optimization and unconstrained CVaR "
            "during systemic liquidity shocks. It explains why sample covariance matrices degenerate and establishes the motivation for bipartite "
            "graph regularization and regime-adaptive multi-agent governance."
        ),
    },
    "subsec-intro-problem": {
        "title": "Problem Statement Subsection",
        "anchor": "#subsec-intro-problem",
        "what_it_tells": (
            "The Problem Statement mathematically defines fire-sale contagion, structural covariance drift (Frobenius norm), and the breakdown of "
            "institutional asset liquidity. It formalizes why isolated equity risk measures fail to capture bipartite institutional co-ownership risk."
        ),
    },
    "subsec-intro-solution": {
        "title": "Engineered Solution Subsection",
        "anchor": "#subsec-intro-solution",
        "what_it_tells": (
            "The Engineered Solution overview presents the multi-agent architecture (5-Agent Blackboard in EAAI, 7-Agent DAG in COR) that couples "
            "convex Second-Order Cone Programming (SOCP) via the CLARABEL solver with real-time institutional network telemetry."
        ),
    },
    "sec-math": {
        "title": "Mathematical Formulation Subsection",
        "anchor": "#sec-math",
        "what_it_tells": (
            "The Mathematical Formulation subsection contains the complete formal mathematical framework: "
            "G-CVaR objective function, normalized graph Laplacian L = I - D^{-1/2} * A * D^{-1/2}, dynamic sigmoidal gating parameter lambda_G, "
            "Ledoit-Wolf shrinkage intensity alpha = 0.42, and Second-Order Cone Programming (SOCP) constraint cones solved by CLARABEL."
        ),
    },
    "subsec-math-cvar": {
        "title": "Equation (1): Conditional Value-at-Risk Formulation",
        "anchor": "#subsec-math-cvar",
        "what_it_tells": (
            "Details Equation (1): Rockafellar-Uryasev convex formulation for CVaR_beta. Minimizes tail loss beyond the Value-at-Risk threshold "
            "over rolling return scenarios using auxiliary slack variables u_t."
        ),
    },
    "subsec-math-graph": {
        "title": "Equation (2): Graph Laplacian Regularizer",
        "anchor": "#subsec-math-graph",
        "what_it_tells": (
            "Details Equation (2): The quadratic graph regularizer w^T * L * w that penalizes concentrated allocations across overlapping institutional "
            "co-holdings in the bipartite SEC 13-F network, preventing systemic fire-sale cascade contagion."
        ),
    },
    "sec-arch": {
        "title": "System Architecture Pipeline Subsection",
        "anchor": "#sec-arch",
        "what_it_tells": (
            "The System Architecture subsection outlines the multi-agent pipeline: Ingestion Agent, Instability Analysis Agent, Contagion Graph Agent, "
            "G-CVaR Optimization Agent (CLARABEL), and Governance/XAI Agent (Mistral-7B). Details message passing, blackboard data structures, and deterministic fallback loops."
        ),
    },
    "subsec-arch-fig1": {
        "title": "Figure 1: Modular Pipeline Schematic Diagram",
        "anchor": "#subsec-arch-fig1",
        "what_it_tells": (
            "Figure 1 illustrates the end-to-end dataflow from SEC 13-F institutional holding feeds and 218 US equity prices through graph Laplacian construction, "
            "instability index scoring, conic SOCP optimization, and regulatory audit trail generation."
        ),
    },
    "sec-eval": {
        "title": "Empirical Evaluation & Backtest Subsection",
        "anchor": "#sec-eval",
        "what_it_tells": (
            "The Empirical Evaluation subsection provides rigorous quantitative validation across 552 rolling windows spanning 20 years of real US equity data (2005-2025). "
            "Demonstrates 25.9% CVaR-95% reduction, 32.5 percentage point crisis drawdown protection during 2008 GFC, and +38.6% higher Sharpe ratio compared to unregularized benchmarks."
        ),
    },
    "sec-references": {
        "title": "Scholarly References & BibTeX Subsection",
        "anchor": "#sec-references",
        "what_it_tells": (
            "Lists peer-reviewed academic literature citations (Markowitz, Rockafellar-Uryasev, Ledoit-Wolf, Cont, CLARABEL solver papers) and provides copyable BibTeX records "
            "for citing Jithendra's research publications."
        ),
    },
}


def get_section_knowledge(target: str) -> Optional[dict[str, Any]]:
    """Retrieves structured knowledge for a section, subsection, or page route."""
    clean = target.strip().lower().replace("#", "").replace("/", "")

    # Direct section lookup
    if clean in SECTION_KNOWLEDGE:
        return SECTION_KNOWLEDGE[clean]

    # Check for route lookup in PAGE_KNOWLEDGE
    route_key = "/" + clean if not clean.startswith("/") else clean
    if route_key in PAGE_KNOWLEDGE:
        return PAGE_KNOWLEDGE[route_key]

    # Case-study navigation targets → canonical /projects/* routes
    case_study_routes = {
        "case_study_adaptive_governance": "/projects/adaptive-portfolio-governance",
        "case_study_regime_supervisory": "/projects/regime-adaptive-supervisory-governance",
        "case_study_supervisory_xai": "/projects/supervisory-portfolio-xai-governance",
        "case_study_voice_architecture": "/projects/voice-agent-portfolio-architecture",
        "case_study_aqi": "/projects/personalised-aqi-system",
        "case_study_swarm_robotics": "/projects/swarm-robots-agriculture",
    }
    cs_route = case_study_routes.get(clean)
    if cs_route and cs_route in PAGE_KNOWLEDGE:
        return PAGE_KNOWLEDGE[cs_route]

    # Alias normalization
    aliases = {
        "contact_section": "contact",
        "contact_hub": "contact",
        "reach_out": "contact",
        "booking": "book_appointment",
        "schedule": "book_appointment",
        "appointment": "book_appointment",
        "overview": "home",
        "hero_section": "home",
        "about_me": "about",
        "credentials": "about",
        "papers": "research",
        "publications": "research",
        "timeline": "experience",
        "education": "experience",
        "awards": "certificates",
        "tech_stack": "skills",
        "math": "sec-math",
        "equations": "sec-math",
        "formulation": "sec-math",
        "architecture": "sec-arch",
        "pipeline": "sec-arch",
        "evaluation": "sec-eval",
        "results": "sec-eval",
        "backtest": "sec-eval",
        "references": "sec-references",
        "citations": "sec-references",
    }
    alias_target = aliases.get(clean)
    if alias_target and alias_target in SECTION_KNOWLEDGE:
        return SECTION_KNOWLEDGE[alias_target]

    return None


def get_formatted_section_explanation(target: str) -> str:
    """Generates a rich, conversational explanation of what a section or subsection tells."""
    data = get_section_knowledge(target)
    if not data:
        return f"Section '{target}' is part of Jithendra's interactive portfolio."

    title = data.get("title", target)
    what_it_tells = data.get("what_it_tells") or data.get("summary", "")
    key_elements = data.get("key_elements", [])

    lines = [f"{title}: {what_it_tells}"]
    if key_elements:
        lines.append("Key elements include: " + ", ".join(key_elements[:4]) + ".")
    return " ".join(lines)
