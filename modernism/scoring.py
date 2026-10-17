"""Word-list scoring: counts modernist terms and turns them into 0-100 scores."""

import re
from dataclasses import dataclass, field

from modernism.lexicon import CATEGORIES

# Hits per 1000 words. At or below LOW -> score 0. At or above HIGH -> score 100.
# Measured on Project Gutenberg books: Austen, Bronte, Dickens, Melville sit near LOW;
# Joyce, Woolf, Eliot, Lawrence, Kafka, Conrad range from LOW up to about HIGH.
CALIBRATION = {
    "vocabulary": (0.1, 1.0),
    "ideas": (0.1, 0.6),
    "politics": (0.02, 1.5),
}

WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class CategoryResult:
    score: int
    hits: int
    hits_per_1000_words: float
    theme_counts: dict
    top_terms: list
    example_sentences: list = field(default_factory=list)


def _term_to_regex(term):
    term = term.lower().replace("’", "'")
    is_prefix = term.endswith("*")
    if is_prefix:
        term = term[:-1]
    parts = [re.escape(p) for p in term.split()]
    pattern = r"\s+".join(parts)
    pattern = r"\b" + pattern + (r"[a-z'-]*" if is_prefix else r"\b")
    return re.compile(pattern)


_COMPILED = {
    category: {
        theme: [(term, _term_to_regex(term)) for term in terms]
        for theme, terms in themes.items()
    }
    for category, themes in CATEGORIES.items()
}


_ANY_TERM = {
    category: re.compile("|".join(r.pattern for terms in themes.values() for _, r in terms))
    for category, themes in _COMPILED.items()
}


def count_words(text):
    return len(WORD_RE.findall(text))


def _scale(rate, low, high):
    if rate <= low:
        return 0
    if rate >= high:
        return 100
    return round(100 * (rate - low) / (high - low))


def _normalize(text):
    return text.lower().replace("’", "'")


def score_category(text, category, word_count=None, max_examples=3):
    lowered = _normalize(text)
    if word_count is None:
        word_count = count_words(text)
    theme_counts = {}
    term_counts = {}
    for theme, terms in _COMPILED[category].items():
        theme_total = 0
        for term, regex in terms:
            n = len(regex.findall(lowered))
            if n:
                term_counts[term] = term_counts.get(term, 0) + n
                theme_total += n
        theme_counts[theme] = theme_total
    hits = sum(theme_counts.values())
    rate = 1000 * hits / word_count if word_count else 0.0
    low, high = CALIBRATION[category]
    top_terms = sorted(term_counts.items(), key=lambda kv: -kv[1])[:10]
    return CategoryResult(
        score=_scale(rate, low, high),
        hits=hits,
        hits_per_1000_words=round(rate, 2),
        theme_counts=theme_counts,
        top_terms=top_terms,
        example_sentences=find_example_sentences(text, category, max_examples),
    )


def find_example_sentences(text, category, max_examples=3):
    """Return the sentences with the most distinct modernist terms in them."""
    scored = []
    if max_examples <= 0:
        return []
    for sentence in SENTENCE_RE.split(text):
        sentence = " ".join(sentence.split())
        if not (20 <= len(sentence) <= 400):
            continue
        lowered = _normalize(sentence)
        if not _ANY_TERM[category].search(lowered):
            continue
        matched = [
            term
            for terms in _COMPILED[category].values()
            for term, regex in terms
            if regex.search(lowered)
        ]
        if matched:
            scored.append((len(set(matched)), sentence, sorted(set(matched))))
    scored.sort(key=lambda item: -item[0])
    return [{"sentence": s, "terms": t} for _, s, t in scored[:max_examples]]


def analyze_text(text):
    word_count = count_words(text)
    results = {
        category: score_category(text, category, word_count)
        for category in CATEGORIES
    }
    overall = round(sum(r.score for r in results.values()) / len(results))
    return {"word_count": word_count, "overall": overall, "categories": results}
