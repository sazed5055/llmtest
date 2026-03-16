"""Text processing utilities."""

from typing import List


def contains_phrase(text: str, phrase: str, case_sensitive: bool = False) -> bool:
    """
    Check if text contains a phrase.

    Args:
        text: Text to search in
        phrase: Phrase to search for
        case_sensitive: Whether to perform case-sensitive search

    Returns:
        True if phrase is found in text
    """
    if not case_sensitive:
        text = text.lower()
        phrase = phrase.lower()
    return phrase in text


def contains_any_phrase(text: str, phrases: List[str], case_sensitive: bool = False) -> bool:
    """
    Check if text contains any of the given phrases.

    Args:
        text: Text to search in
        phrases: List of phrases to search for
        case_sensitive: Whether to perform case-sensitive search

    Returns:
        True if any phrase is found in text
    """
    return any(contains_phrase(text, phrase, case_sensitive) for phrase in phrases)


def contains_all_phrases(text: str, phrases: List[str], case_sensitive: bool = False) -> bool:
    """
    Check if text contains all of the given phrases.

    Args:
        text: Text to search in
        phrases: List of phrases that must all be present
        case_sensitive: Whether to perform case-sensitive search

    Returns:
        True if all phrases are found in text
    """
    return all(contains_phrase(text, phrase, case_sensitive) for phrase in phrases)


def find_matching_phrases(
    text: str, phrases: List[str], case_sensitive: bool = False
) -> List[str]:
    """
    Find which phrases from a list are present in text.

    Args:
        text: Text to search in
        phrases: List of phrases to check
        case_sensitive: Whether to perform case-sensitive search

    Returns:
        List of phrases that were found in text
    """
    return [phrase for phrase in phrases if contains_phrase(text, phrase, case_sensitive)]
