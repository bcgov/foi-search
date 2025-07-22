from typing import Any, Dict, List, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

def classify_sentence(
    sentence: Any,
    index: int,
    max_chars: int,
    max_words: int
) -> Tuple[Optional[str], Optional[Dict]]:
    """Validate a sentence and return either the cleaned sentence or a rejection reason."""
    if not isinstance(sentence, str):
        return None, {"index": index, "reason": "not a string"}

    stripped = sentence.strip()
    if not stripped:
        return None, {"index": index, "reason": "empty after stripping"}

    if len(stripped) > max_chars:
        return None, {"index": index, "reason": f"exceeds max char length ({len(stripped)} > {max_chars})"}

    if len(stripped.split()) > max_words:
        return None, {"index": index, "reason": f"exceeds max word count ({len(stripped.split())} > {max_words})"}

    return stripped, None


def validate_sentences(
    sentences: List[str],
    max_chars: int,
    max_words: int
) -> Tuple[List[str], List[int], List[Dict], Dict[str, int]]:
    """Validate a list of sentences.

    Args:
        sentences: Input sentences
        max_chars: Max char length allowed
        max_words: Max word count allowed

    Returns:
        valid_sentences, valid_indices, rejected_info, rejection_summary
    """
    valid = []
    indices = []
    rejected = []

    for i, s in enumerate(sentences):
        cleaned, error = classify_sentence(s, i, max_chars, max_words)
        if error:
            rejected.append(error)
            logger.debug(f"Skipping sentence at index {i}: {error['reason']}")
        else:
            valid.append(cleaned)
            indices.append(i)

    summary = Counter([r["reason"] for r in rejected])
    if rejected:
        logger.warning(
            f"{len(rejected)} sentences rejected. Summary: " +
            ", ".join(f"{k}: {v}" for k, v in summary.items())
        )

    return valid, indices, rejected, dict(summary)
