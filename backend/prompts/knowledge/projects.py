"""
Engineering projects and screen navigation targets metadata.
"""

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
    "sec-abstract": "Case study abstract, institutional problem thesis, and summary of findings",
    "sec-intro": "Introduction, motivation, and engineered multi-agent solution",
    "subsec-intro-problem": "Problem statement: fire-sale contagion and covariance matrix degeneration",
    "subsec-intro-solution": "Engineered solution: convex conic optimization with CLARABEL",
    "sec-math": "Mathematical formulation: G-CVaR, Ledoit-Wolf shrinkage (alpha=0.42), and CLARABEL SOCP cones",
    "subsec-math-cvar": "Equation (1): Rockafellar-Uryasev CVaR tail-loss convex formulation",
    "subsec-math-graph": "Equation (2): Graph Laplacian quadratic regularizer over SEC 13-F bipartite network",
    "sec-arch": "System architecture: multi-agent blackboard / DAG pipeline dataflow",
    "subsec-arch-fig1": "Figure 1: Modular pipeline architecture schematic diagram",
    "sec-eval": "Empirical evaluation: 20-year backtests, +38.6% Sharpe ratio, -42.1% crisis drawdown reduction",
    "sec-references": "Academic peer-reviewed literature citations and BibTeX records",
}
