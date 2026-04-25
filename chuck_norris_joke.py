#!/usr/bin/env python3
"""
Chuck Norris Joke Fetcher

Fetches random Chuck Norris jokes from api.chucknorris.io using only
the Python standard library (no third-party packages required).

Usage:
    python chuck_norris_joke.py                    # Fetch a random joke
    python chuck_norris_joke.py --category animal  # Fetch a joke from a specific category
    python chuck_norris_joke.py --categories       # List available categories
    python chuck_norris_joke.py --help             # Show this help message
"""

import json
import sys
import urllib.request
import urllib.error


API_BASE_URL = "https://api.chucknorris.io"
USER_AGENT = "ChuckNorrisJokeFetcher/1.0"


def fetch_json(url: str) -> dict:
    """Fetch JSON data from a URL and return the parsed dictionary."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                print(f"Error: HTTP {response.status} - {response.reason}", file=sys.stderr)
                sys.exit(1)
            data = response.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Failed to parse response: {e}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print("Error: Request timed out after 10 seconds", file=sys.stderr)
        sys.exit(1)


def fetch_random_joke(category: str | None = None) -> str:
    """Fetch a random Chuck Norris joke, optionally from a specific category."""
    url = f"{API_BASE_URL}/jokes/random"
    if category:
        url += f"?category={category}"
    data = fetch_json(url)
    return data.get("value", "No joke found in response.")


def list_categories() -> list[str]:
    """Fetch and return the list of available joke categories."""
    url = f"{API_BASE_URL}/jokes/categories"
    data = fetch_json(url)
    if isinstance(data, list):
        return data
    print("Unexpected response format for categories.", file=sys.stderr)
    sys.exit(1)


def print_help() -> None:
    """Display usage information."""
    print(__doc__)


def main() -> None:
    """Main entry point."""
    # Handle command-line arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_help()
        sys.exit(0)

    if "--categories" in args:
        categories = list_categories()
        print("Available Chuck Norris joke categories:")
        for cat in categories:
            print(f"  - {cat}")
        sys.exit(0)

    # Extract category if provided
    category = None
    if "--category" in args:
        idx = args.index("--category")
        if idx + 1 < len(args):
            category = args[idx + 1]
        else:
            print("Error: --category requires a value.", file=sys.stderr)
            sys.exit(1)

    joke = fetch_random_joke(category)
    print("Chuck Norris Joke:")
    print(f"  {joke}")


if __name__ == "__main__":
    main()
