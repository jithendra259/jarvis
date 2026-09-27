"""
Jithendra's Portfolio & Research Knowledge Base
Contains structured metadata, research papers, projects, and biography for the Voice AI assistant.
"""

BIOGRAPHY = {
    "name": "Kandula Jithendra Subramanyam",
    "preferred_name": "Jithendra",
    "roles": [
        "AI Systems Engineer",
        "Quantitative Financial Researcher",
        "Multi-Agent Systems Architect",
        "Full-Stack Developer",
    ],
    "mission": (
        "Bridging autonomous agentic swarms with convex mathematical optimization (CVXPY) "
        "and deterministic supervisory governance for verifiable, audit-compliant decision systems in high-stakes domains."
    ),
    "location": "Mumbai, Maharashtra, India (Open to global roles: remote or relocation)",
    "email": "kandulajithendrasubramanyam@gmail.com",
    "phone": "+91-9704400336",
    "portfolio_url": "https://jithendra-portfolio.vercel.app",
    "github": "https://github.com/jithendra259",
    "linkedin": "https://linkedin.com/in/kandulajithendra",
}

EDUCATION = [
    {
        "degree": "M.Tech in Artificial Intelligence & Data Science",
        "institution": "K J Somaiya College of Engineering, Somaiya Vidyavihar University, Mumbai",
        "period": "2024 - 2026",
        "cgpa": "8.06 / 10.0",
        "thesis": (
            "Multi-Agent Governance for Graph-Regularized Conditional Value-at-Risk "
            "Portfolio Optimization with Adaptive Contagion Penalization (supervised by Prof. Sunayana Jadhav)"
        ),
    },
    {
        "degree": "B.Tech in Electronics & Communication Engineering",
        "institution": "Presidency University, Bangalore",
        "period": "2019 - 2023",
        "cgpa": "7.77 / 10.0",
        "capstone": (
            "Autonomous Swarm Robotics for Precision Agriculture & Plant Pathology. "
            "Awarded Karnataka State Council for Science & Technology (KSCST) 46th Series Project Grant."
        ),
    },
]

COMPETITIVE_EXAMS = [
    "GATE 2024 Qualified (Data Science & Artificial Intelligence - DA)",
    "GATE 2024 Qualified (Computer Science & Information Technology - CS)",
]

PUBLICATIONS = [
    {
        "id": "paper_eaai",
        "title": "Multi-Agent Governance for Graph-Regularized Conditional Value-at-Risk Portfolio Optimization with Adaptive Contagion Penalization",
        "venue": "Elsevier Engineering Applications of Artificial Intelligence (EAAI)",
        "status": "Under Review (2026)",
        "manuscript_id": "EAAI-26-14280",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Jadhav",
        "summary": (
            "5-agent blackboard architecture for institutional portfolio optimization addressing fire-sale contagion "
            "via SEC 13-F bipartite co-holding graphs. Integrates graph-regularized CVaR (G-CVaR) with Ledoit-Wolf shrinkage. "
            "Delivers 25.9% reduction in CVaR-95% and 32.5 percentage point reduction in crisis drawdown over 552 rolling windows (2005-2025)."
        ),
        "target_nav": "case_study_adaptive_governance",
    },
    {
        "id": "paper_lncs",
        "title": "Regime-Adaptive Supervisory Governance for Instability-Aware Portfolio Stabilization",
        "venue": "5th International Joint Conference on Advances in Computational Intelligence (IJCACI 2026) / Springer Nature LNCS",
        "status": "Accepted & Presented (2026)",
        "location": "Washington University of Science and Technology (WUST), Alexandria, USA",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Vilas Jadhav, Ashwini Dalvi",
        "summary": (
            "Interpretable supervisory governance coupling covariance drift, rolling volatility, and correlation stress into a composite Instability Index. "
            "Dynamically adjusts concentration limits and Ledoit-Wolf shrinkage (alpha = 0.42) during stress periods across 218 US equities over 20 years."
        ),
        "target_nav": "case_study_regime_supervisory",
    },
    {
        "id": "paper_cor",
        "title": "A Supervisory Portfolio Governance Framework: Composite Instability Detection, Deterministic Regime Switching & Conversational Explainability",
        "venue": "Elsevier Computers & Operations Research (CAS Journal)",
        "status": "Prepared / Under Review (2026)",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Vilas Jadhav, Ashwini Dalvi",
        "summary": (
            "7-agent DAG architecture integrating CLARABEL interior-point convex solver with conversational Mistral-7B LLM. "
            "Guarantees 100% numerical grounding (0% hallucination) by strictly bounding LLM explanations to verified solver outputs. "
            "Compliant with MiFID II and the EU AI Act."
        ),
        "target_nav": "case_study_supervisory_xai",
    },
]

PROJECTS = [
    {
        "id": "voice_portfolio_architecture",
        "name": "Real-Time Voice AI Portfolio & Agentic Web Architecture",
        "description": (
            "Interactive voice-driven engineering portfolio. Built with Next.js 15 App Router, LiveKit WebRTC, "
            "Groq LPU (sub-90ms TTFT primary LLM), Cartesia Sonic-3 neural TTS, Deepgram Nova-3 STT, "
            "and Google Gemini 2.5 Flash fallback. Uses bi-directional WebRTC data channels for real-time UI auto-navigation "
            "and is cloud-optimized for zero event-loop blocking on Render's 0.1 vCPU."
        ),
        "target_nav": "case_study_voice_architecture",
    },
    {
        "id": "voice_assistant",
        "name": "Agentic AI Portfolio Governance Chatbot",
        "description": (
            "Interactive voice AI assistant with real-time UI navigation. Decoupled into 10+ agent roles delivering "
            "sub-200ms TTFT via Groq LPU LLM, LiveKit WebRTC, Deepgram Nova-3 STT, and Cartesia Sonic-3 TTS."
        ),
        "target_nav": "projects",
    },
    {
        "id": "portfolio_governance_platform",
        "name": "Multi-Agent Adaptive Portfolio Governance System",
        "description": (
            "Full-stack quantitative investment intelligence platform built on Next.js 15, TypeScript, TailwindCSS, and Python backend. "
            "Provides institutional-grade risk visualization, backtesting, and supervisory telemetry."
        ),
        "target_nav": "case_study_adaptive_governance",
    },
    {
        "id": "aqi_forecasting",
        "name": "Personalised AQI Global Air Quality Forecasting",
        "description": (
            "Machine learning system using Next.js 15, Flask, and CPCB sensor data across 10 Delhi stations. "
            "Evaluated XGBoost, Markov Chains, and ARIMA. XGBoost achieved R2 = 0.912 and RMSE of 18.4 ug/m3 for 48-hour PM2.5 forecasting."
        ),
        "target_nav": "case_study_aqi",
    },
    {
        "id": "swarm_robotics",
        "name": "Autonomous Swarm Robots for Precision Agriculture",
        "description": (
            "Distributed IoT hardware-software swarm using ESP32, ESP-NOW mesh, edge CNNs, and DenseNet121. "
            "Achieved 98.4% field coverage and 96.8% disease classification accuracy. Funded by KSCST 46th Series grant."
        ),
        "target_nav": "case_study_swarm_robotics",
    },
]

TECHNICAL_SKILLS = {
    "AI, ML & Research": [
        "Artificial Intelligence", "Machine Learning", "Deep Learning", "Agentic AI",
        "Multi-Agent Systems", "Explainable AI", "Retrieval-Augmented Generation", "Prompt Engineering",
    ],
    "Finance & Optimization": [
        "Quantitative Finance", "Portfolio Optimization", "CVaR", "Drawdown", "Volatility",
        "RSI", "MACD", "Bollinger Bands", "Market Regime Detection", "Compliance-Aware AI",
    ],
    "Agentic AI & LLM Tools": [
        "LangChain", "LangGraph", "Groq", "Ollama", "Mistral-7B",
        "Agent Memory", "Verification Frameworks", "Audit Logging", "Source Grounding",
    ],
    "Voice AI & Real-Time Systems": [
        "LiveKit", "WebRTC", "Deepgram (STT)", "ElevenLabs (TTS)",
        "Real-Time Data Channels", "Sub-500ms Conversational Pipelines",
    ],
    "Optimization & Graph Tools": [
        "CVXPY", "CLARABEL", "NetworkX", "Risk-Aware Portfolio Construction", "Graph-Based Reasoning",
    ],
    "Programming & Data": [
        "Python", "NumPy", "Pandas", "SciPy", "Scikit-learn", "SQL", "MongoDB", "Supabase", "Git", "GitHub",
    ],
    "Full-Stack Development": [
        "React", "Next.js", "TypeScript", "JavaScript", "Flask", "REST APIs", "HTML", "CSS", "Gradio", "AQICN API",
    ],
}

WORK_EXPERIENCE = [
    {
        "role": "Thesis Researcher",
        "organization": "K J Somaiya College of Engineering",
        "period": "Oct 2025 - Apr 2026",
        "details": "Led research on multi-agent financial systems, convex portfolio optimization, and authored 3 research papers.",
    },
    {
        "role": "Full-Stack Developer Intern",
        "organization": "ScholarRankAI",
        "period": "May 2025 - Aug 2025",
        "details": "Developed AI ranking algorithms, scalable Next.js UI, optimized REST APIs with sub-200ms latency.",
    },
    {
        "role": "UI/UX Developer Intern",
        "organization": "MNJ Software",
        "period": "Mar 2024 - May 2024",
        "details": "Designed and built modern responsive web dashboards, component design systems, and client interfaces.",
    },
]

NAVIGATION_TARGETS = {
    "projects": "Overview of engineering and AI projects",
    "research": "Three peer-reviewed publications (EAAI, Springer LNCS, Computers & Operations Research)",
    "about": "Personal journey, philosophy, and biography",
    "resume": "Interactive resume and downloadable CV",
    "contact": "Direct contact options and meeting booking calendar",
    "book_appointment": "Dedicated full-screen interactive calendar appointment booking page (/book-appointment)",
    "skills": "Comprehensive technical skill matrix and proficiencies",
    "certificates": "Verified academic, competitive exam (GATE), and professional credentials",
    "experience": "Research and software engineering industry roles",
    "home": "Hero section and high-level introduction",
    "case_study_voice_architecture": "Deep-dive case study on this Portfolio's Real-Time Voice AI & Agentic Web Architecture (Groq LPU, LiveKit WebRTC, Next.js 15)",
    "case_study_adaptive_governance": "Deep-dive case study on G-CVaR portfolio optimization (EAAI Paper)",
    "case_study_regime_supervisory": "Deep-dive case study on Regime-Adaptive Supervisory Governance (Springer LNCS Paper)",
    "case_study_supervisory_xai": "Deep-dive case study on 100% Numerically Grounded Explainable AI (COR Paper)",
    "case_study_aqi": "Deep-dive case study on Global Air Quality Forecasting with XGBoost",
    "case_study_swarm_robotics": "Deep-dive case study on Autonomous Precision Agriculture Swarm Robots",
}


# ── Detailed Factual Metrics & Structured Knowledge for RAG Retrieval ─────────────
# These facts are indexed for precise metric queries via semantic_knowledge_search
# and get_research_metric tools.

DETAILED_METRICS = {
    # EAAI Paper (G-CVaR / Adaptive Governance)
    "cvar_reduction_eaai": {
        "value": "25.9%",
        "description": "CVaR-95% reduction achieved by G-CVaR portfolio vs. baseline",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "drawdown_reduction_eaai": {
        "value": "32.5 percentage points",
        "description": "Crisis drawdown reduction over 552 rolling windows (2005-2025)",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "ledoit_wolf_alpha_eaai": {
        "value": "0.42",
        "description": "Optimal shrinkage parameter for covariance estimation in G-CVaR",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "rolling_windows_eaai": {
        "value": "552",
        "description": "Number of rolling windows in backtest (2005-2025)",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "fire_sale_contagion_penalty": {
        "value": "Adaptive",
        "description": "Graph-regularized contagion penalty via SEC 13-F bipartite co-holding graphs",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "g_cvar_agents": {
        "value": "5",
        "description": "5-agent blackboard architecture for institutional portfolio optimization",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },
    "sec_13f_institutions": {
        "value": "Bipartite co-holding graph",
        "description": "Institutional ownership network from SEC 13-F filings",
        "source": "Elsevier EAAI Paper",
        "paper_id": "paper_eaai",
    },

    # LNCS Paper (Regime-Adaptive Supervisory Governance)
    "instability_index_components": {
        "value": "Covariance drift + Rolling volatility + Correlation stress",
        "description": "Composite Instability Index composition",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "ledoit_wolf_alpha_lncs": {
        "value": "0.42",
        "description": "Dynamic shrinkage parameter adjusted during stress periods",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "equities_universe_lncs": {
        "value": "218 US equities",
        "description": "Asset universe for regime-adaptive governance backtest",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "backtest_period_lncs": {
        "value": "20 years",
        "description": "Historical period for regime-adaptive backtesting",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "concentration_limits": {
        "value": "Dynamically adjusted",
        "description": "Concentration limits adjusted by Instability Index during stress",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "conference": {
        "value": "IJCACI 2026",
        "description": "5th International Joint Conference on Advances in Computational Intelligence",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },
    "location": {
        "value": "Washington University of Science and Technology, Alexandria, USA",
        "description": "Conference presentation location",
        "source": "Springer Nature LNCS Paper",
        "paper_id": "paper_lncs",
    },

    # COR Paper (Supervisory XAI Governance)
    "clarabel_solver": {
        "value": "Interior-point convex solver",
        "description": "CLARABEL used for SOCP formulation in 7-agent DAG",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },
    "mistral_7b_llm": {
        "value": "Mistral-7B",
        "description": "Conversational LLM for explainability in 7-agent DAG",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },
    "numerical_grounding": {
        "value": "100%",
        "description": "Zero hallucination - LLM explanations strictly bounded to solver outputs",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },
    "dag_agents": {
        "value": "7",
        "description": "7-agent Directed Acyclic Graph architecture",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },
    "compliance": {
        "value": "MiFID II + EU AI Act",
        "description": "Regulatory compliance for financial AI governance",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },
    "socp_formulation": {
        "value": "Second-Order Cone Programming",
        "description": "Convex optimization formulation solved by CLARABEL",
        "source": "Elsevier COR Paper",
        "paper_id": "paper_cor",
    },

    # AQI Project
    "aqi_r2_score": {
        "value": "0.912",
        "description": "R-squared score for 48-hour PM2.5 forecasting with XGBoost",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_rmse": {
        "value": "18.4 ug/m3",
        "description": "Root Mean Square Error for 48-hour PM2.5 forecast",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_stations": {
        "value": "10",
        "description": "Delhi CPCB monitoring stations used for training",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_pollutants": {
        "value": "PM2.5, PM10, NO2, CO, O3",
        "description": "Multi-pollutant time-series forecasting",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_horizon": {
        "value": "48-hour",
        "description": "Forecasting horizon for PM2.5 prediction",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_models_compared": {
        "value": "XGBoost, Markov Chains, ARIMA",
        "description": "Models evaluated; XGBoost selected as best performer",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },
    "aqi_personalized": {
        "value": "Respiratory risk classification",
        "description": "Personalized health risk classification based on forecast",
        "source": "AQI Forecasting Project",
        "paper_id": "aqi_forecasting",
    },

    # Swarm Robotics Project
    "swarm_coverage": {
        "value": "98.4%",
        "description": "Field coverage achieved by ESP32 swarm",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_classification_accuracy": {
        "value": "96.8%",
        "description": "Plant pathology classification accuracy (DenseNet121 edge CNN)",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_protocol": {
        "value": "ESP-NOW",
        "description": "Peer-to-peer wireless mesh protocol (no router dependency)",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_grant": {
        "value": "KSCST 46th Series",
        "description": "Karnataka State Council for Science & Technology project grant",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_microcontroller": {
        "value": "ESP32",
        "description": "Microcontroller used for decentralized swarm nodes",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_consensus": {
        "value": "Distributed consensus",
        "description": "Algorithm for spatial partitioning, telemetry, and obstacle avoidance",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },
    "swarm_edge_cnn": {
        "value": "DenseNet121",
        "description": "Edge CNN for plant pathology classification",
        "source": "Swarm Robotics Project",
        "paper_id": "swarm_robotics",
    },

    # Voice AI Portfolio Architecture
    "ttft_groq": {
        "value": "sub-90ms",
        "description": "Time-to-first-token with Groq LPU primary LLM",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "ttft_fallback": {
        "value": "Google Gemini 2.5 Flash",
        "description": "Fallback LLM when Groq unavailable",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "stt_model": {
        "value": "Deepgram Nova-3",
        "description": "Speech-to-Text model for real-time transcription",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "tts_model": {
        "value": "Cartesia Sonic-3 / Groq Orpheus",
        "description": "Neural Text-to-Speech models",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "livekit_webrtc": {
        "value": "LiveKit WebRTC",
        "description": "Real-time communication infrastructure",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "data_channels": {
        "value": "Bi-directional WebRTC",
        "description": "Real-time UI auto-navigation and page context sharing",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "render_cpu": {
        "value": "0.1 vCPU",
        "description": "Render Free tier CPU - zero event-loop blocking achieved",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },
    "turn_detection": {
        "value": "Deepgram Flux STT-based",
        "description": "No local VAD - STT handles end-of-turn detection",
        "source": "Voice AI Portfolio Architecture",
        "paper_id": "voice_portfolio_architecture",
    },

    # Education & Qualifications
    "mtech_cgpa": {
        "value": "8.06 / 10.0",
        "description": "M.Tech AI & Data Science CGPA at Somaiya Vidyavihar University",
        "source": "Education",
        "paper_id": "education",
    },
    "btech_cgpa": {
        "value": "7.77 / 10.0",
        "description": "B.Tech ECE CGPA at Presidency University, Bangalore",
        "source": "Education",
        "paper_id": "education",
    },
    "gate_da": {
        "value": "Qualified",
        "description": "GATE 2024 Data Science & Artificial Intelligence (DA)",
        "source": "Competitive Exams",
        "paper_id": "qualifications",
    },
    "gate_cs": {
        "value": "Qualified",
        "description": "GATE 2024 Computer Science & Information Technology (CS)",
        "source": "Competitive Exams",
        "paper_id": "qualifications",
    },
}
