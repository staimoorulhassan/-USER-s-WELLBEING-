"""Browser suffix filter utility.

Removes browser-specific suffixes from window titles to normalize them.
Uses regex patterns for flexible matching.
"""

import re
from typing import List

from config.constants import BROWSER_SUFFIXES


class BrowserFilter:
    """Filters browser suffixes from window titles."""

    def __init__(self, custom_suffixes: Optional[List[str]] = None):
        """Initialize browser filter.

        Args:
            custom_suffixes: Additional suffix patterns to filter
        """
        self.patterns = BROWSER_SUFFIXES.copy()
        if custom_suffixes:
            self.patterns.extend(custom_suffixes)

        # Compile regex patterns for performance
        self._compiled_patterns = [re.compile(pattern) for pattern in self.patterns]

    def filter(self, window_title: str) -> str:
        """Remove browser suffix from window title.

        Args:
            window_title: Raw window title from OS

        Returns:
            Filtered window title with browser suffix removed

        Examples:
            >>> filter("GitHub - python/requests - Google Chrome")
            "GitHub - python/requests"
            >>> filter("Empty title")
            "Empty title"
        """
        if not window_title:
            return ""

        filtered_title = window_title
        for pattern in self._compiled_patterns:
            filtered_title = pattern.sub("", filtered_title)

        return filtered_title.strip()

    def add_custom_suffix(self, suffix: str) -> None:
        """Add a custom suffix pattern to filter.

        Args:
            suffix: Regex pattern to match and remove
        """
        self.patterns.append(suffix)
        self._compiled_patterns.append(re.compile(suffix))

    def get_current_patterns(self) -> List[str]:
        """Get list of current suffix patterns.

        Returns:
            List of regex patterns
        """
        return self.patterns.copy()
