#!/usr/bin/env python3
"""
Configuration module for the Chuck Norris Joke Fetcher.

Contains API constants, terminal styling helpers, and the category
listing function used by the main application.
"""

import json
import sys
import urllib.request
import urllib.error


API_BASE_URL = "https://api.chucknorris.io"
USER_AGENT = "ChuckNorrisJokeFetcher/2.0"


# ── ANSI color codes ──────────────────────────────────────────────────────

class Style:
    """Terminal styling helpers. Disables colors if output is not a TTY."""
    _enabled = sys.stdout.isatty()

    @classmethod
    def _code(cls, code: str) -> str:
        return f"\033[{code}m" if cls._enabled else ""

    # Foreground colors
    RED     = property(lambda self: self._code("91"))
    GREEN   = property(lambda self: self._code("92"))
    YELLOW  = property(lambda self: self._code("93"))
    BLUE    = property(lambda self: self._code("94"))
    MAGENTA = property(lambda self: self._code("95"))
    CYAN    = property(lambda self: self._code("96"))
    WHITE   = property(lambda self: self._code("97"))

    # Styles
    BOLD      = property(lambda self: self._code("1"))
    DIM       = property(lambda self: self._code("2"))
    ITALIC    = property(lambda self: self._code("3"))
    UNDERLINE = property(lambda self: self._code("4"))
    RESET     = property(lambda self: self._code("0"))

    # Emoji helpers (always visible)
    @staticmethod
    def thumbs_up() -> str:
        return "\U0001f44d"  # 👍

    @staticmethod
    def thumbs_down() -> str:
        return "\U0001f44e"  # 👎

    @staticmethod
    def fire() -> str:
        return "\U0001f525"  # 🔥

    @staticmethod
    def star() -> str:
        return "\u2b50"      # ⭐

    @staticmethod
    def thinking() -> str:
        return "\U0001f914"  # 🤔

    @staticmethod
    def party() -> str:
        return "\U0001f389"  # 🎉

    @staticmethod
    def chuck() -> str:
        return "\U0001f9d1\u200d\u2696\ufe0f"  # 🧑‍⚖️ (person with scales — close enough to Chuck!)


s = Style()


# ── API helpers ───────────────────────────────────────────────────────────

def fetch_json(url: str) -> dict | list:
    """Fetch JSON data from a URL and return the parsed result."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                print(f"{s.RED}Error: HTTP {response.status} - {response.reason}{s.RESET}",
                      file=sys.stderr)
                sys.exit(1)
            data = response.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"{s.RED}Network error: {e.reason}{s.RESET}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{s.RED}Failed to parse response: {e}{s.RESET}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"{s.RED}Error: Request timed out after 10 seconds{s.RESET}", file=sys.stderr)
        sys.exit(1)


def list_categories() -> list[str]:
    """Fetch and return the list of available joke categories."""
    url = f"{API_BASE_URL}/jokes/categories"
    data = fetch_json(url)
    if isinstance(data, list):
        return sorted(data)
    print(f"{s.RED}Unexpected response format for categories.{s.RESET}", file=sys.stderr)
    sys.exit(1)
