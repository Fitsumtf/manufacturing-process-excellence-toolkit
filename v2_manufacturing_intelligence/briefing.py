"""Evidence-grounded engineering briefing from retrieved lessons and live KPIs."""

from __future__ import annotations

import pandas as pd


def build_engineering_brief(query: str, matches: pd.DataFrame, metrics: dict) -> str:
    if matches.empty:
        return (
            f"## Engineering brief\n\n**Problem:** {query}\n\n"
            "No sufficiently similar historical lesson was retrieved. Record containment, "
            "collect time-ordered evidence, verify the measurement system, and complete a "
            "structured root-cause investigation before changing the process."
        )
    causes = matches.root_cause.head(3).tolist()
    actions = matches.corrective_action.head(3).tolist()
    verification = matches.verification.head(3).tolist()
    evidence = "\n".join(
        f"- **{row.lesson_id} — {row.problem}** (BM25 {row.bm25_score:.2f})"
        for row in matches.itertuples()
    )
    return f"""## Evidence-grounded engineering brief

**Problem submitted:** {query}

**Current portfolio indicators:** FPY {metrics.get('fpy', 0):.1%}; OEE {metrics.get('weighted_oee', 0):.1%}; RTY {metrics.get('rty', 0):.1%}; scrap {metrics.get('scrapped', 0)} units.

### Retrieved evidence

{evidence}

### Causes to investigate

{chr(10).join(f'- {cause}' for cause in causes)}

### Containment and corrective-action candidates

{chr(10).join(f'- {action}' for action in actions)}

### Verification plan

{chr(10).join(f'- {item}' for item in verification)}

### Engineering control

This briefing is generated from retrieved synthetic lessons. A qualified engineer must confirm the actual failure mechanism, measurement-system adequacy, safety implications, specifications, and corrective-action effectiveness before production disposition.
"""
