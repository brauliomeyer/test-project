#!/usr/bin/env python3
"""
Chuck Norris Joke Fetcher — Interactive Edition
================================================

Fetches random Chuck Norris jokes from api.chucknorris.io using only
the Python standard library (no third-party packages required).

Features:
  - Random jokes (optionally filtered by category)
  - Interactive category browser
  - Keyword search
  - Joke rating with session stats
  - Joke history
  - Dramatic typewriter animation
  - Colorful terminal output

Usage:
    python chuck_norris_joke.py                        # Interactive mode
    python chuck_norris_joke.py --random               # Fetch a single random joke
    python chuck_norris_joke.py --category animal      # Fetch a joke from a specific category
    python chuck_norris_joke.py --categories           # List available categories
    python chuck_norris_joke.py --search roundhouse    # Search jokes by keyword
    python chuck_norris_joke.py --help                 # Show this help message
"""

import json
import sys
import urllib.request
import urllib.error
import time
import random
import shutil
from dataclasses import dataclass, field


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


# ── Session data ──────────────────────────────────────────────────────────

@dataclass
class Session:
    """Tracks the user's joke session."""
    jokes_seen: list[dict] = field(default_factory=list)
    likes: int = 0
    dislikes: int = 0
    favorites: list[dict] = field(default_factory=list)

    def add_joke(self, joke_data: dict) -> None:
        self.jokes_seen.append(joke_data)

    def rate(self, liked: bool) -> None:
        if liked:
            self.likes += 1
        else:
            self.dislikes += 1

    def toggle_favorite(self, joke_data: dict) -> bool:
        """Toggle favorite status. Returns True if added, False if removed."""
        url = joke_data.get("url", joke_data.get("value", ""))
        for i, fav in enumerate(self.favorites):
            if fav.get("url", fav.get("value", "")) == url:
                self.favorites.pop(i)
                return False
        self.favorites.append(joke_data)
        return True

    @property
    def total(self) -> int:
        return len(self.jokes_seen)

    @property
    def score(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.likes / self.total) * 100)


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


def fetch_random_joke(category: str | None = None) -> dict:
    """Fetch a random Chuck Norris joke, optionally from a specific category."""
    url = f"{API_BASE_URL}/jokes/random"
    if category:
        url += f"?category={category}"
    data = fetch_json(url)
    if isinstance(data, dict):
        return data
    print(f"{s.RED}Unexpected response format.{s.RESET}", file=sys.stderr)
    sys.exit(1)


def list_categories() -> list[str]:
    """Fetch and return the list of available joke categories."""
    url = f"{API_BASE_URL}/jokes/categories"
    data = fetch_json(url)
    if isinstance(data, list):
        return sorted(data)
    print(f"{s.RED}Unexpected response format for categories.{s.RESET}", file=sys.stderr)
    sys.exit(1)


def search_jokes(query: str) -> list[dict]:
    """Search jokes by keyword."""
    import urllib.parse
    url = f"{API_BASE_URL}/jokes/search?query={urllib.parse.quote(query)}"
    data = fetch_json(url)
    if isinstance(data, dict) and "result" in data:
        return data["result"]
    print(f"{s.RED}Unexpected response format for search.{s.RESET}", file=sys.stderr)
    sys.exit(1)


# ── Display helpers ───────────────────────────────────────────────────────

def typewriter(text: str, delay: float = 0.025, *, ending: str = "\n") -> None:
    """Print text with a dramatic typewriter animation."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print(end=ending)


def print_banner() -> None:
    """Print a fun welcome banner."""
    terminal_width = shutil.get_terminal_size().columns
    title = f" {s.chuck()} CHUCK NORRIS JOKE MACHINE {s.chuck()} "
    padding = max(0, (terminal_width - len(title) + 20) // 2)
    border = "=" * (len(title) + 4)
    print()
    print(" " * padding + s.BOLD + s.YELLOW + border + s.RESET)
    print(" " * padding + s.BOLD + s.YELLOW + "| " + s.RESET + s.BOLD + title + s.BOLD + s.YELLOW + " |" + s.RESET)
    print(" " * padding + s.BOLD + s.YELLOW + border + s.RESET)
    print()


def print_joke(joke_data: dict, *, animated: bool = True) -> None:
    """Print a joke with optional typewriter animation."""
    joke_text = joke_data.get("value", "No joke found.")
    category = joke_data.get("categories", [])
    cat_str = f" [{', '.join(category)}]" if category else ""

    print(f"\n{s.BOLD}{s.CYAN}Chuck Norris says:{s.RESET}{s.DIM}{cat_str}{s.RESET}\n")

    if animated:
        typewriter(f"  {s.YELLOW}\"{joke_text}\"{s.RESET}", delay=0.02)
    else:
        print(f"  {s.YELLOW}\"{joke_text}\"{s.RESET}")

    print()


def print_stats(session: Session) -> None:
    """Print session statistics."""
    print(f"\n{s.BOLD}{s.BLUE}── Session Stats ──{s.RESET}")
    print(f"  {s.star()} Jokes seen:  {s.BOLD}{session.total}{s.RESET}")
    print(f"  {s.thumbs_up()} Liked:      {s.GREEN}{session.likes}{s.RESET}")
    print(f"  {s.thumbs_down()} Disliked:   {s.RED}{session.dislikes}{s.RESET}")
    print(f"  {s.fire()} Approval:   {s.BOLD}{session.score}%{s.RESET}")
    if session.favorites:
        print(f"  {s.party()} Favorites:  {s.BOLD}{len(session.favorites)}{s.RESET}")
    print()


def print_favorites(session: Session) -> None:
    """Print the user's favorite jokes."""
    if not session.favorites:
        print(f"\n  {s.thinking()} No favorites saved yet. Use {s.BOLD}/fave{s.RESET} to save one!\n")
        return
    print(f"\n{s.BOLD}{s.MAGENTA}══ Your Favorite Jokes ══{s.RESET}\n")
    for i, fav in enumerate(session.favorites, 1):
        print(f"  {s.BOLD}#{i}{s.RESET} {s.YELLOW}\"{fav.get('value', '')}\"{s.RESET}")
        print()


def print_history(session: Session) -> None:
    """Print the joke history for the current session."""
    if not session.jokes_seen:
        print(f"\n  {s.thinking()} No jokes yet. Go fetch some!\n")
        return
    print(f"\n{s.BOLD}{s.CYAN}══ Joke History ({session.total}) ══{s.RESET}\n")
    for i, joke in enumerate(session.jokes_seen, 1):
        preview = joke.get("value", "")
        if len(preview) > 70:
            preview = preview[:67] + "..."
        print(f"  {s.DIM}[{i}]{s.RESET} {s.YELLOW}\"{preview}\"{s.RESET}")
    print()


def print_help() -> None:
    """Display usage information."""
    print(__doc__)


# ── Interactive commands ──────────────────────────────────────────────────

def handle_interactive_command(cmd: str, session: Session,
                                current_joke: dict | None) -> str | None:
    """
    Handle a slash command typed by the user during interactive mode.
    Returns a command result string or None.
    """
    cmd = cmd.lower().strip()

    if cmd == "/help":
        print(f"\n  {s.BOLD}Available commands:{s.RESET}")
        print(f"    {s.CYAN}/next{s.RESET}        — Show another random joke")
        print(f"    {s.CYAN}/category{s.RESET}    — Pick a joke by category")
        print(f"    {s.CYAN}/search{s.RESET}      — Search jokes by keyword")
        print(f"    {s.CYAN}/fave{s.RESET}        — Toggle favorite on current joke")
        print(f"    {s.CYAN}/history{s.RESET}     — Show all jokes this session")
        print(f"    {s.CYAN}/favorites{s.RESET}   — Show your saved favorites")
        print(f"    {s.CYAN}/stats{s.RESET}       — Show session statistics")
        print(f"    {s.CYAN}/banner{s.RESET}      — Show the welcome banner again")
        print(f"    {s.CYAN}/quit{s.RESET}        — Exit")
        print(f"    {s.CYAN}/help{s.RESET}        — Show this help")
        print()
        return None

    elif cmd == "/quit":
        return "quit"

    elif cmd == "/stats":
        print_stats(session)
        return None

    elif cmd == "/history":
        print_history(session)
        return None

    elif cmd == "/favorites":
        print_favorites(session)
        return None

    elif cmd == "/fave":
        if current_joke:
            added = session.toggle_favorite(current_joke)
            if added:
                print(f"\n  {s.party()} {s.GREEN}Added to favorites!{s.RESET}\n")
            else:
                print(f"\n  {s.thinking()} {s.YELLOW}Removed from favorites.{s.RESET}\n")
        else:
            print(f"\n  {s.thinking()} No joke to favorite yet.\n")
        return None

    elif cmd == "/banner":
        print_banner()
        return None

    elif cmd == "/next":
        return "next"

    elif cmd == "/category":
        return "category"

    elif cmd == "/search":
        return "search"

    else:
        print(f"\n  {s.thinking()} Unknown command '{cmd}'. Type {s.CYAN}/help{s.RESET} for options.\n")
        return None


# ── Interactive flows ─────────────────────────────────────────────────────

def interactive_category_picker() -> str | None:
    """Let the user browse and pick a category interactively. Returns category name or None."""
    print(f"\n{s.BOLD}{s.BLUE}Fetching categories...{s.RESET}")
    try:
        categories = list_categories()
    except SystemExit:
        return None

    # Paginate if there are many categories
    page_size = 10
    total = len(categories)
    page = 0

    while True:
        start = page * page_size
        end = min(start + page_size, total)
        print(f"\n{s.BOLD}{s.CYAN}Available Categories (page {page + 1}/{(total - 1) // page_size + 1}):{s.RESET}\n")
        for i, cat in enumerate(categories[start:end], start + 1):
            print(f"  {s.BOLD}{i:2}.{s.RESET} {cat}")

        print(f"\n  {s.DIM}─── Page {page + 1} of {(total - 1) // page_size + 1} ───{s.RESET}")
        print(f"  {s.CYAN}/next{s.RESET}  — Next page    {s.CYAN}/prev{s.RESET}  — Previous page")
        print(f"  {s.CYAN}/all{s.RESET}   — Random from any category")
        print(f"  {s.CYAN}/back{s.RESET}  — Go back")
        print(f"  {s.DIM}Or enter a number (1-{end}) to pick a category.{s.RESET}")

        try:
            choice = input(f"\n{s.BOLD}Pick a category >{s.RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if choice == "/back":
            return None
        elif choice == "/all":
            return None
        elif choice == "/next":
            if end < total:
                page += 1
            continue
        elif choice == "/prev":
            if page > 0:
                page -= 1
            continue
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < total:
                    return categories[idx]
                else:
                    print(f"\n  {s.RED}Please enter a number between 1 and {total}.{s.RESET}")
            except ValueError:
                print(f"\n  {s.RED}Invalid input. Enter a number or a /command.{s.RESET}")


def interactive_search() -> str | None:
    """Let the user search jokes by keyword. Returns 'next' or None."""
    try:
        query = input(f"\n{s.BOLD}Search for what?{s.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if not query:
        print(f"\n  {s.thinking()} Empty search. Try again!\n")
        return None

    print(f"\n{s.BOLD}{s.BLUE}Searching for \"{query}\"...{s.RESET}")
    try:
        results = search_jokes(query)
    except SystemExit:
        return None

    if not results:
        print(f"\n  {s.thinking()} No jokes found for \"{query}\". Chuck Norris doesn't approve.\n")
        return None

    print(f"\n{s.BOLD}{s.GREEN}Found {len(results)} joke{'s' if len(results) != 1 else ''}!{s.RESET}\n")

    # Show results with numbers
    for i, joke in enumerate(results[:10], 1):
        text = joke.get("value", "")
        if len(text) > 80:
            text = text[:77] + "..."
        print(f"  {s.BOLD}[{i}]{s.RESET} {s.YELLOW}\"{text}\"{s.RESET}")

    if len(results) > 10:
        print(f"\n  {s.DIM}... and {len(results) - 10} more.{s.RESET}")

    # Let user pick one to view in full
    print(f"\n  {s.DIM}Enter a number to view that joke in full, or press Enter to skip.{s.RESET}")
    try:
        pick = input(f"\n{s.BOLD}View joke >{s.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if pick.isdigit():
        idx = int(pick) - 1
        if 0 <= idx < len(results):
            joke_data = results[idx]
            print_joke(joke_data, animated=True)
            return joke_data

    return None


def rate_joke(session: Session, joke_data: dict) -> None:
    """Ask the user to rate the joke and update session stats."""
    print(f"  {s.DIM}Rate this joke:{s.RESET}")
    print(f"  {s.BOLD}[1]{s.RESET} {s.thumbs_up()} {s.GREEN}Funny!{s.RESET}")
    print(f"  {s.BOLD}[2]{s.RESET} {s.thumbs_down()} {s.RED}Meh...{s.RESET}")
    print(f"  {s.BOLD}[3]{s.RESET} {s.star()} {s.YELLOW}Favorite it!{s.RESET}")
    print(f"  {s.BOLD}[4]{s.RESET} {s.thinking()} Skip rating")

    try:
        choice = input(f"\n{s.BOLD}Your rating >{s.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice == "1":
        session.rate(liked=True)
        print(f"\n  {s.thumbs_up()} {s.GREEN}Ha! Chuck approves.{s.RESET}")
    elif choice == "2":
        session.rate(liked=False)
        print(f"\n  {s.thumbs_down()} {s.RED}Chuck is disappointed in you.{s.RESET}")
    elif choice == "3":
        session.toggle_favorite(joke_data)
        print(f"\n  {s.party()} {s.MAGENTA}Added to favorites!{s.RESET}")
    elif choice == "4":
        pass
    else:
        print(f"\n  {s.thinking()} No rating recorded.{s.RESET}")


# ── Main interactive loop ─────────────────────────────────────────────────

def interactive_mode() -> None:
    """Run the full interactive joke experience."""
    session = Session()
    current_joke = None

    print_banner()

    # Welcome message with typewriter effect
    typewriter(
        f"  {s.BOLD}Welcome to the Chuck Norris Joke Machine!{s.RESET}\n"
        f"  {s.DIM}Type {s.CYAN}/help{s.RESET}{s.DIM} at any time to see available commands.{s.RESET}\n"
        f"  {s.DIM}Or just press {s.CYAN}Enter{s.RESET}{s.DIM} to get a random joke!{s.RESET}\n",
        delay=0.015
    )

    while True:
        # Show prompt
        try:
            cmd = input(f"\n{s.BOLD}{s.GREEN}chuck>{s.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(f"\n  {s.chuck()} {s.BOLD}Chuck Norris never says goodbye. But you can go.{s.RESET}")
            print_stats(session)
            print(f"  {s.BOLD}Thanks for laughing!{s.RESET}\n")
            sys.exit(0)

        # Empty input → fetch a random joke
        if not cmd:
            joke_data = fetch_random_joke()
            session.add_joke(joke_data)
            current_joke = joke_data
            print_joke(joke_data, animated=True)
            rate_joke(session, joke_data)
            continue

        # Slash commands
        if cmd.startswith("/"):
            result = handle_interactive_command(cmd, session, current_joke)
            if result == "quit":
                break
            elif result == "next":
                joke_data = fetch_random_joke()
                session.add_joke(joke_data)
                current_joke = joke_data
                print_joke(joke_data, animated=True)
                rate_joke(session, joke_data)
                continue
            elif result == "category":
                cat = interactive_category_picker()
                if cat:
                    print(f"\n  {s.BOLD}Fetching a {s.MAGENTA}{cat}{s.RESET}{s.BOLD} joke...{s.RESET}")
                    joke_data = fetch_random_joke(cat)
                    session.add_joke(joke_data)
                    current_joke = joke_data
                    print_joke(joke_data, animated=True)
                    rate_joke(session, joke_data)
                continue
            elif result == "search":
                search_result = interactive_search()
                if isinstance(search_result, dict):
                    session.add_joke(search_result)
                    current_joke = search_result
                    rate_joke(session, search_result)
                continue
            else:
                continue

        # Anything else → treat as a search query (quick search)
        print(f"\n  {s.thinking()} Searching for \"{cmd}\"...")
        try:
            results = search_jokes(cmd)
        except SystemExit:
            continue

        if results:
            joke_data = random.choice(results)
            session.add_joke(joke_data)
            current_joke = joke_data
            print_joke(joke_data, animated=True)
            rate_joke(session, joke_data)
        else:
            print(f"\n  {s.thinking()} No jokes found for \"{cmd}\". Try something else!\n")

    # Farewell
    print(f"\n  {s.chuck()} {s.BOLD}Farewell, friend!{s.RESET}")
    print_stats(session)
    print(f"  {s.BOLD}Thanks for laughing!{s.RESET}\n")


# ── CLI entry point ───────────────────────────────────────────────────────

def main() -> None:
    """Main entry point."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_help()
        sys.exit(0)

    if "--categories" in args:
        categories = list_categories()
        print(f"\n{s.BOLD}{s.CYAN}Available Chuck Norris joke categories:{s.RESET}\n")
        for cat in categories:
            print(f"  {s.BOLD}•{s.RESET} {cat}")
        print()
        sys.exit(0)

    # Search mode
    if "--search" in args:
        idx = args.index("--search")
        if idx + 1 < len(args):
            query = args[idx + 1]
            print(f"\n{s.BOLD}{s.BLUE}Searching for \"{query}\"...{s.RESET}\n")
            results = search_jokes(query)
            if not results:
                print(f"  {s.thinking()} No jokes found for \"{query}\".\n")
                sys.exit(0)
            for joke in results:
                print(f"  {s.YELLOW}\"{joke.get('value', '')}\"{s.RESET}\n")
            sys.exit(0)
        else:
            print(f"{s.RED}Error: --search requires a query.{s.RESET}", file=sys.stderr)
            sys.exit(1)

    # Category mode (fetch a single joke from a category)
    category = None
    if "--category" in args:
        idx = args.index("--category")
        if idx + 1 < len(args):
            category = args[idx + 1]
        else:
            print(f"{s.RED}Error: --category requires a value.{s.RESET}", file=sys.stderr)
            sys.exit(1)
        joke_data = fetch_random_joke(category)
        print_joke(joke_data, animated=True)
        sys.exit(0)

    # Random single joke mode
    if "--random" in args:
        joke_data = fetch_random_joke()
        print_joke(joke_data, animated=True)
        sys.exit(0)

    # Default: interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
