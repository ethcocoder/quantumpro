"""
Paradox v2 — Wikipedia Ingestion
==================================
Fetches full Wikipedia articles and prepares them for chunking + embedding.
"""

import warnings
from typing import List, Tuple, Optional

warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')
warnings.filterwarnings("ignore", message="No parser was explicitly specified")


def fetch_wikipedia(topic: str, auto_suggest: bool = True) -> Optional[Tuple[str, str]]:
    """
    Fetch a full Wikipedia article.

    Args:
        topic: article title or search query
        auto_suggest: allow Wikipedia to suggest closest match

    Returns:
        (title, content) tuple or None on failure
    """
    try:
        import wikipedia
    except ImportError:
        raise ImportError(
            "wikipedia package is required for Wikipedia ingestion.\n"
            "Install: pip install wikipedia"
        )

    try:
        page = wikipedia.page(topic, auto_suggest=auto_suggest)
        content = page.content

        # Clean structural Wikipedia noise
        content = _clean_wikipedia(content)

        if len(content) < 100:
            print(f"[WIKI] Warning: '{topic}' returned very short content ({len(content)} chars)")
            return None

        print(f"[WIKI] Fetched: '{page.title}' ({len(content):,} chars)")
        return page.title, content

    except Exception as e:
        print(f"[WIKI] Failed to fetch '{topic}': {e}")
        return None


def fetch_wikipedia_batch(
    topics: List[str],
    auto_suggest: bool = True,
) -> List[Tuple[str, str]]:
    """
    Fetch multiple Wikipedia articles.

    Returns:
        List of (title, content) tuples for successful fetches.
    """
    results = []
    for topic in topics:
        result = fetch_wikipedia(topic, auto_suggest)
        if result:
            results.append(result)
    print(f"[WIKI] Batch complete: {len(results)}/{len(topics)} articles fetched")
    return results


def _clean_wikipedia(text: str) -> str:
    """Remove Wikipedia structural artifacts."""
    import re

    # Remove "== Section ==" headers but keep content
    text = re.sub(r'={2,}\s*[^=]+\s*={2,}', '. ', text)

    # Remove reference markers like [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)

    # Remove empty parentheses
    text = re.sub(r'\(\s*\)', '', text)

    # Collapse excessive whitespace
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()
