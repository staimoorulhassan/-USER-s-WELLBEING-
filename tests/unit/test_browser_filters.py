"""Unit tests for browser filter utility.

Tests that:
- Suffix removal patterns work correctly
- Empty titles are handled
- Special characters are preserved
"""

import pytest
from utils.browser_filters import BrowserFilter


class TestBrowserFilter:
    """Test browser suffix filtering behavior."""

    def test_filters_google_chrome_suffix(self):
        """Test that ' - Google Chrome' suffix is removed."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("GitHub - python/requests - Google Chrome")

        assert result == "GitHub - python/requests"
        assert "Google Chrome" not in result

    def test_filters_mozilla_firefox_suffix(self):
        """Test that ' - Mozilla Firefox' suffix is removed."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("Stack Overflow - Mozilla Firefox")

        assert result == "Stack Overflow"
        assert "Mozilla Firefox" not in result

    def test_filters_microsoft_edge_suffix(self):
        """Test that ' - Microsoft Edge' suffix is removed."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("Documentation - Microsoft Edge")

        assert result == "Documentation"
        assert "Microsoft Edge" not in result

    def test_handles_empty_title(self):
        """Test that empty title returns empty string."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("")

        assert result == ""

    def test_handles_title_without_browser_suffix(self):
        """Test that title without browser suffix is unchanged."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("Visual Studio Code")

        assert result == "Visual Studio Code"

    def test_preserves_special_characters(self):
        """Test that special characters in title are preserved."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("GitHub - python/requests: Pull Request #123 - Google Chrome")

        assert result == "GitHub - python/requests: Pull Request #123"

    def test_trims_whitespace(self):
        """Test that leading/trailing whitespace is trimmed."""
        browser_filter = BrowserFilter()

        result = browser_filter.filter("  GitHub - Google Chrome  ")

        assert result == "GitHub"

    def test_custom_suffix_can_be_added(self):
        """Test that custom suffix patterns can be added."""
        browser_filter = BrowserFilter()
        browser_filter.add_custom_suffix(r" - CustomBrowser$")

        result = browser_filter.filter("Example - CustomBrowser")

        assert result == "Example"

    def test_get_current_patterns(self):
        """Test that current patterns can be retrieved."""
        browser_filter = BrowserFilter()

        patterns = browser_filter.get_current_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert any("Chrome" in p for p in patterns)

    def test_multiple_suffixes_not_double_filtered(self):
        """Test that filtering doesn't remove multiple suffixes incorrectly."""
        browser_filter = BrowserFilter()

        # Title with just one suffix
        result = browser_filter.filter("Site - Google Chrome")

        # Should only filter once
        assert result == "Site"
