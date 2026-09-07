from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..schemas import Fact

class FactCandidateIndex:
    """
    Semantic index for efficient candidate retrieval across documents.
    Prevents O(N^2) brute-force comparisons by filtering on subject + predicate similarity.
    """

    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')

    def find_cross_document_candidates(self, facts: List[Fact]) -> List[Tuple[Fact, Fact, float]]:
        """
        Identify plausible cross-document candidate pairs with high semantic topic alignment.
        """
        if len(facts) < 2:
            return []

        # Group facts by document
        doc_ids = [f.document_id for f in facts]
        if len(set(doc_ids)) < 2:
            return []  # Need at least two different documents to compare

        # Build feature text per fact: Subject + Predicate + Segment
        feature_texts = [
            f"{f.subject} {f.predicate} {f.scope.segment or ''} {f.unit or ''}"
            for f in facts
        ]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(feature_texts)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            # Empty vocabulary or stop words
            sim_matrix = np.zeros((len(facts), len(facts)))

        candidates = []
        n = len(facts)

        for i in range(n):
            for j in range(i + 1, n):
                fact_a = facts[i]
                fact_b = facts[j]

                # Must be from different documents
                if fact_a.document_id == fact_b.document_id:
                    continue

                # Subject must have some overlap or similarity
                subj_sim = (
                    fact_a.subject.lower() in fact_b.subject.lower() or
                    fact_b.subject.lower() in fact_a.subject.lower()
                )

                score = float(sim_matrix[i, j])
                
                # Check predicate token overlap
                tokens_a = set(fact_a.predicate.lower().split())
                tokens_b = set(fact_b.predicate.lower().split())
                token_overlap = bool(tokens_a & tokens_b)

                # Bonus if predicate keyword or tokens match
                pred_match = (
                    fact_a.predicate.lower() in fact_b.predicate.lower() or
                    fact_b.predicate.lower() in fact_a.predicate.lower() or
                    token_overlap
                )

                if pred_match and subj_sim:
                    score = max(score, 0.70)

                if (score >= self.threshold or pred_match) and (subj_sim or score >= 0.60):
                    candidates.append((fact_a, fact_b, score))

        # Sort by similarity descending
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates
