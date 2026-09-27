"""
Peer-reviewed publications and conference presentations metadata.
"""

PUBLICATIONS = [
    {
        "id": "paper_eaai",
        "title": "Multi-Agent Governance for Graph-Regularized Conditional Value-at-Risk Portfolio Optimization with Adaptive Contagion Penalization",
        "venue": "Elsevier Engineering Applications of Artificial Intelligence (EAAI)",
        "status": "Under Review (2026)",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Jadhav",
        "summary": (
            "Five-agent blackboard architecture integrating SEC 13-F bipartite institutional networks, "
            "eigenvector centrality penalty, and CLARABEL conic solver. Reduces CVaR-95% by 25.9% and "
            "crisis-regime drawdown by 32.5 pp with Wilcoxon p = 0.0065."
        ),
        "target_nav": "case_study_adaptive_governance",
    },
    {
        "id": "paper_lncs",
        "title": "Regime-Adaptive Supervisory Governance for Instability-Aware Portfolio Stabilization",
        "venue": "Springer Nature LNCS (IJCACI 2026, Alexandria, USA)",
        "status": "Accepted & Presented (2026)",
        "authors": "K. J. Subramanyam (First & Corresponding Author), Sunayana Vilas Jadhav, Ashwini Dalvi",
        "summary": (
            "Composite Instability Index (I_t) coupling Frobenius norm covariance drift, rolling volatility, "
            "and pairwise correlation. Dynamically controls Ledoit-Wolf shrinkage intensity (alpha = 0.42) "
            "across 3 market regimes, containing maximum drawdown to 32.5% over 20 years."
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
