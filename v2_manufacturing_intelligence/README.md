# Version 2 — Manufacturing Process Intelligence System

Version 2 preserves Version 1 as the auditable statistical core and adds session-based live production records, FPY, RTY, OEE trends, BM25 lessons retrieval, evidence-grounded engineering briefs, and integrated Word reporting.

## Run locally

```bash
streamlit run v2_manufacturing_intelligence/app.py
```

## Public-storage design

Streamlit Community Cloud local storage is not a production database. Version 2 therefore keeps records in the user session and provides CSV download/restore. The analytics and reports are database-ready, but the public demonstration does not claim permanent production-record retention.

## LLM boundary

The public version produces a deterministic engineering brief from traceable BM25 evidence. A credentialed LLM can later rewrite or summarize retrieved evidence, but it must not become the authority for specifications, safety decisions, process parameters, or product disposition.
