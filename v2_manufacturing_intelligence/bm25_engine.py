"""Small, dependency-free BM25 retrieval engine for engineering lessons."""

from __future__ import annotations

import math
import re
from collections import Counter

import pandas as pd


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(text).lower())


class BM25LessonsIndex:
    def __init__(self, frame: pd.DataFrame, text_columns: list[str] | None = None):
        self.frame = frame.reset_index(drop=True).copy()
        self.text_columns = text_columns or [
            "problem", "symptoms", "root_cause", "containment",
            "corrective_action", "verification", "lesson",
        ]
        missing = set(self.text_columns) - set(frame.columns)
        if missing:
            raise ValueError(f"Lessons dataset is missing columns: {sorted(missing)}")
        self.documents = [
            tokenize(" ".join(str(row[c]) for c in self.text_columns))
            for _, row in self.frame.iterrows()
        ]
        self.lengths = [len(doc) for doc in self.documents]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        self.term_frequencies = [Counter(doc) for doc in self.documents]
        document_frequency = Counter()
        for doc in self.documents:
            document_frequency.update(set(doc))
        n = len(self.documents)
        self.idf = {
            term: math.log(1 + (n - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }

    def search(self, query: str, top_k: int = 5, k1: float = 1.5, b: float = 0.75) -> pd.DataFrame:
        terms = tokenize(query)
        if not terms:
            return self.frame.head(0).assign(bm25_score=[])
        scores = []
        for frequencies, length in zip(self.term_frequencies, self.lengths):
            score = 0.0
            for term in terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                denominator = frequency + k1 * (
                    1 - b + b * length / max(self.average_length, 1)
                )
                score += self.idf.get(term, 0) * frequency * (k1 + 1) / denominator
            scores.append(score)
        result = self.frame.copy()
        result["bm25_score"] = scores
        return result[result.bm25_score > 0].sort_values(
            "bm25_score", ascending=False
        ).head(top_k).reset_index(drop=True)
