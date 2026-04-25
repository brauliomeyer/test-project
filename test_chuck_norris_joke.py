#!/usr/bin/env python3
"""
Tests for the Chuck Norris Joke Fetcher script.

Uses unittest.mock to patch network calls so no external API requests
are made during testing.
"""

import json
import sys
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from io import StringIO
from dataclasses import dataclass, field
from typing import Any

# ── Import the module under test ──────────────────────────────────────────

import chuck_norris_joke as cnj


# ── Test data ─────────────────────────────────────────────────────────────

MOCK_JOKE = {
    "categories": ["animal"],
    "created_at": "2020-01-05 13:42:19.576875",
    "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
    "id": "abc123",
    "updated_at": "2020-01-05 13:42:19.576875",
    "url": "https://api.chucknorris.io/jokes/abc123",
    "value": "Chuck Norris can divide by zero.",
}

MOCK_JOKE_2 = {
    "categories": [],
    "created_at": "2020-01-05 13:42:21.123456",
    "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
    "id": "def456",
    "updated_at": "2020-01-05 13:42:21.123456",
    "url": "https://api.chucknorris.io/jokes/def456",
    "value": "Chuck Norris counted to infinity. Twice.",
}

MOCK_CATEGORIES = ["animal", "career", "celebrity", "dev", "explicit", "fashion", "food", "history", "money", "movie", "music", "political", "religion", "science", "sport", "travel"]

MOCK_SEARCH_RESULTS = {
    "total": 2,
    "result": [MOCK_JOKE, MOCK_JOKE_2],
}


# ── Helper to build a mock HTTP response ──────────────────────────────────

def _mock_response(data: Any, status: int = 200) -> MagicMock:
    """Create a mock urllib.response object."""
    resp = MagicMock()
    resp.status = status
    resp.reason = "OK" if status == 200 else "Error"
    body = json.dumps(data).encode("utf-8")
    resp.read.return_value = body
    resp.__enter__.return_value = resp
    return resp


# ── Tests ─────────────────────────────────────────────────────────────────

class TestModuleImports(unittest.TestCase):
    """Verify the module can be imported and has expected attributes."""

    def test_module_imports(self):
        """The module should import without errors."""
        self.assertTrue(hasattr(cnj, "fetch_random_joke"))
        self.assertTrue(hasattr(cnj, "list_categories"))
        self.assertTrue(hasattr(cnj, "search_jokes"))
        self.assertTrue(hasattr(cnj, "fetch_json"))
        self.assertTrue(hasattr(cnj, "Session"))
        self.assertTrue(hasattr(cnj, "main"))

    def test_api_base_url(self):
        """API_BASE_URL should point to chucknorris.io."""
        self.assertEqual(cnj.API_BASE_URL, "https://api.chucknorris.io")


class TestFetchJson(unittest.TestCase):
    """Test the fetch_json helper function."""

    @patch("urllib.request.urlopen")
    def test_fetch_json_success(self, mock_urlopen):
        """fetch_json should return parsed JSON on success."""
        mock_urlopen.return_value = _mock_response(MOCK_JOKE)
        result = cnj.fetch_json("https://api.chucknorris.io/jokes/random")
        self.assertEqual(result, MOCK_JOKE)

    @patch("urllib.request.urlopen")
    def test_fetch_json_http_error(self, mock_urlopen):
        """fetch_json should exit on HTTP error."""
        mock_urlopen.return_value = _mock_response({}, status=404)
        mock_urlopen.return_value.reason = "Not Found"
        with self.assertRaises(SystemExit):
            cnj.fetch_json("https://api.chucknorris.io/jokes/random")

    @patch("urllib.request.urlopen")
    def test_fetch_json_network_error(self, mock_urlopen):
        """fetch_json should exit on network error."""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")
        with self.assertRaises(SystemExit):
            cnj.fetch_json("https://api.chucknorris.io/jokes/random")

    @patch("urllib.request.urlopen")
    def test_fetch_json_timeout(self, mock_urlopen):
        """fetch_json should exit on timeout."""
        mock_urlopen.side_effect = TimeoutError("timed out")
        with self.assertRaises(SystemExit):
            cnj.fetch_json("https://api.chucknorris.io/jokes/random")


class TestFetchRandomJoke(unittest.TestCase):
    """Test the fetch_random_joke function."""

    @patch("chuck_norris_joke.fetch_json")
    def test_random_joke_no_category(self, mock_fetch):
        """fetch_random_joke() should call the correct URL without category."""
        mock_fetch.return_value = MOCK_JOKE
        result = cnj.fetch_random_joke()
        mock_fetch.assert_called_once_with("https://api.chucknorris.io/jokes/random")
        self.assertEqual(result, MOCK_JOKE)

    @patch("chuck_norris_joke.fetch_json")
    def test_random_joke_with_category(self, mock_fetch):
        """fetch_random_joke('animal') should include the category parameter."""
        mock_fetch.return_value = MOCK_JOKE
        result = cnj.fetch_random_joke("animal")
        mock_fetch.assert_called_once_with("https://api.chucknorris.io/jokes/random?category=animal")
        self.assertEqual(result, MOCK_JOKE)

    @patch("chuck_norris_joke.fetch_json")
    def test_random_joke_unexpected_response(self, mock_fetch):
        """fetch_random_joke() should exit if response is not a dict."""
        mock_fetch.return_value = ["not", "a", "dict"]
        with self.assertRaises(SystemExit):
            cnj.fetch_random_joke()


class TestListCategories(unittest.TestCase):
    """Test the list_categories function."""

    @patch("chuck_norris_joke.fetch_json")
    def test_list_categories_success(self, mock_fetch):
        """list_categories() should return sorted categories."""
        mock_fetch.return_value = MOCK_CATEGORIES
        result = cnj.list_categories()
        mock_fetch.assert_called_once_with("https://api.chucknorris.io/jokes/categories")
        self.assertEqual(result, sorted(MOCK_CATEGORIES))

    @patch("chuck_norris_joke.fetch_json")
    def test_list_categories_unexpected_response(self, mock_fetch):
        """list_categories() should exit if response is not a list."""
        mock_fetch.return_value = {"not": "a list"}
        with self.assertRaises(SystemExit):
            cnj.list_categories()


class TestSearchJokes(unittest.TestCase):
    """Test the search_jokes function."""

    @patch("chuck_norris_joke.fetch_json")
    def test_search_jokes_success(self, mock_fetch):
        """search_jokes() should return the result list."""
        mock_fetch.return_value = MOCK_SEARCH_RESULTS
        result = cnj.search_jokes("roundhouse")
        # URL should include the encoded query
        called_url = mock_fetch.call_args[0][0]
        self.assertIn("query=roundhouse", called_url)
        self.assertEqual(result, MOCK_SEARCH_RESULTS["result"])

    @patch("chuck_norris_joke.fetch_json")
    def test_search_jokes_no_results(self, mock_fetch):
        """search_jokes() should return empty list when no results."""
        mock_fetch.return_value = {"total": 0, "result": []}
        result = cnj.search_jokes("nonexistent")
        self.assertEqual(result, [])

    @patch("chuck_norris_joke.fetch_json")
    def test_search_jokes_unexpected_response(self, mock_fetch):
        """search_jokes() should exit if response format is unexpected."""
        mock_fetch.return_value = ["not", "expected"]
        with self.assertRaises(SystemExit):
            cnj.search_jokes("test")


class TestSession(unittest.TestCase):
    """Test the Session dataclass."""

    def setUp(self):
        self.session = cnj.Session()

    def test_initial_state(self):
        """A new session should start empty."""
        self.assertEqual(self.session.total, 0)
        self.assertEqual(self.session.likes, 0)
        self.assertEqual(self.session.dislikes, 0)
        self.assertEqual(self.session.favorites, [])
        self.assertEqual(self.session.score, 0.0)

    def test_add_joke(self):
        """add_joke should append to jokes_seen."""
        self.session.add_joke(MOCK_JOKE)
        self.assertEqual(self.session.total, 1)
        self.assertEqual(self.session.jokes_seen[0], MOCK_JOKE)

    def test_rate_like(self):
        """rate(True) should increment likes."""
        self.session.add_joke(MOCK_JOKE)
        self.session.rate(liked=True)
        self.assertEqual(self.session.likes, 1)
        self.assertEqual(self.session.dislikes, 0)

    def test_rate_dislike(self):
        """rate(False) should increment dislikes."""
        self.session.add_joke(MOCK_JOKE)
        self.session.rate(liked=False)
        self.assertEqual(self.session.likes, 0)
        self.assertEqual(self.session.dislikes, 1)

    def test_score_calculation(self):
        """score should return correct percentage."""
        self.session.add_joke(MOCK_JOKE)
        self.session.add_joke(MOCK_JOKE_2)
        self.session.rate(liked=True)
        self.session.rate(liked=True)
        self.assertEqual(self.session.score, 100.0)

    def test_score_partial(self):
        """score should handle partial likes."""
        self.session.add_joke(MOCK_JOKE)
        self.session.add_joke(MOCK_JOKE_2)
        self.session.add_joke(MOCK_JOKE)
        self.session.add_joke(MOCK_JOKE_2)
        self.session.rate(liked=True)
        self.session.rate(liked=False)
        self.session.rate(liked=True)
        self.session.rate(liked=False)
        self.assertEqual(self.session.score, 50.0)

    def test_toggle_favorite_add(self):
        """toggle_favorite should add a joke to favorites."""
        added = self.session.toggle_favorite(MOCK_JOKE)
        self.assertTrue(added)
        self.assertEqual(len(self.session.favorites), 1)
        self.assertEqual(self.session.favorites[0], MOCK_JOKE)

    def test_toggle_favorite_remove(self):
        """toggle_favorite should remove a joke already in favorites."""
        self.session.toggle_favorite(MOCK_JOKE)
        added = self.session.toggle_favorite(MOCK_JOKE)
        self.assertFalse(added)
        self.assertEqual(len(self.session.favorites), 0)

    def test_toggle_favorite_multiple(self):
        """toggle_favorite should handle multiple distinct jokes."""
        self.session.toggle_favorite(MOCK_JOKE)
        self.session.toggle_favorite(MOCK_JOKE_2)
        self.assertEqual(len(self.session.favorites), 2)
        # Remove the first one
        self.session.toggle_favorite(MOCK_JOKE)
        self.assertEqual(len(self.session.favorites), 1)
        self.assertEqual(self.session.favorites[0], MOCK_JOKE_2)


class TestDisplayHelpers(unittest.TestCase):
    """Test display helper functions (capture stdout)."""

    def setUp(self):
        self.session = cnj.Session()
        self.session.add_joke(MOCK_JOKE)
        self.session.add_joke(MOCK_JOKE_2)

    def test_print_stats_empty(self):
        """print_stats should handle empty session."""
        empty_session = cnj.Session()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_stats(empty_session)
            output = mock_stdout.getvalue()
            self.assertIn("Jokes seen", output)
            self.assertIn("0", output)

    def test_print_stats_with_data(self):
        """print_stats should show session data."""
        self.session.rate(liked=True)
        self.session.rate(liked=False)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_stats(self.session)
            output = mock_stdout.getvalue()
            self.assertIn("2", output)  # jokes seen
            self.assertIn("1", output)  # likes
            self.assertIn("1", output)  # dislikes

    def test_print_favorites_empty(self):
        """print_favorites should show a message when no favorites."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_favorites(self.session)
            output = mock_stdout.getvalue()
            self.assertIn("No favorites", output)

    def test_print_favorites_with_data(self):
        """print_favorites should list favorites."""
        self.session.toggle_favorite(MOCK_JOKE)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_favorites(self.session)
            output = mock_stdout.getvalue()
            self.assertIn("Favorite Jokes", output)
            self.assertIn("Chuck Norris can divide by zero.", output)

    def test_print_history_empty(self):
        """print_history should show a message when no jokes seen."""
        empty_session = cnj.Session()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_history(empty_session)
            output = mock_stdout.getvalue()
            self.assertIn("No jokes yet", output)

    def test_print_history_with_data(self):
        """print_history should list jokes."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_history(self.session)
            output = mock_stdout.getvalue()
            self.assertIn("Joke History", output)
            self.assertIn("Chuck Norris", output)

    def test_print_banner(self):
        """print_banner should print the welcome banner."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_banner()
            output = mock_stdout.getvalue()
            self.assertIn("CHUCK NORRIS", output)

    def test_print_help(self):
        """print_help should display usage information."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_help()
            output = mock_stdout.getvalue()
            self.assertIn("Usage", output)
            self.assertIn("chuck_norris_joke.py", output)


class TestPrintJoke(unittest.TestCase):
    """Test the print_joke function."""

    def test_print_joke_animated(self):
        """print_joke should display joke text."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_joke(MOCK_JOKE, animated=False)
            output = mock_stdout.getvalue()
            self.assertIn("Chuck Norris can divide by zero.", output)
            self.assertIn("animal", output)

    def test_print_joke_no_category(self):
        """print_joke should handle jokes without categories."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.print_joke(MOCK_JOKE_2, animated=False)
            output = mock_stdout.getvalue()
            self.assertIn("Chuck Norris counted to infinity.", output)


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument parsing via main()."""

    @patch("sys.argv", ["chuck_norris_joke.py", "--help"])
    def test_help_flag(self):
        """--help should print help and exit with 0."""
        with self.assertRaises(SystemExit) as ctx:
            cnj.main()
        self.assertEqual(ctx.exception.code, 0)

    @patch("sys.argv", ["chuck_norris_joke.py", "-h"])
    def test_short_help_flag(self):
        """-h should print help and exit with 0."""
        with self.assertRaises(SystemExit) as ctx:
            cnj.main()
        self.assertEqual(ctx.exception.code, 0)

    @patch("chuck_norris_joke.list_categories")
    def test_categories_flag(self, mock_categories):
        """--categories should list categories and exit with 0."""
        mock_categories.return_value = MOCK_CATEGORIES
        test_args = ["chuck_norris_joke.py", "--categories"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 0)
        mock_categories.assert_called_once()

    @patch("chuck_norris_joke.fetch_random_joke")
    def test_random_flag(self, mock_fetch):
        """--random should fetch a random joke and exit with 0."""
        mock_fetch.return_value = MOCK_JOKE
        test_args = ["chuck_norris_joke.py", "--random"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 0)
        mock_fetch.assert_called_once_with()

    @patch("chuck_norris_joke.fetch_random_joke")
    def test_category_flag(self, mock_fetch):
        """--category animal should fetch a joke from that category."""
        mock_fetch.return_value = MOCK_JOKE
        test_args = ["chuck_norris_joke.py", "--category", "animal"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 0)
        mock_fetch.assert_called_once_with("animal")

    def test_category_flag_missing_value(self):
        """--category without a value should exit with 1."""
        test_args = ["chuck_norris_joke.py", "--category"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch("chuck_norris_joke.search_jokes")
    def test_search_flag(self, mock_search):
        """--search query should search and exit with 0."""
        mock_search.return_value = [MOCK_JOKE]
        test_args = ["chuck_norris_joke.py", "--search", "roundhouse"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 0)
        mock_search.assert_called_once_with("roundhouse")

    def test_search_flag_missing_query(self):
        """--search without a query should exit with 1."""
        test_args = ["chuck_norris_joke.py", "--search"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as ctx:
                cnj.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch("chuck_norris_joke.search_jokes")
    def test_search_flag_no_results(self, mock_search):
        """--search with no results should exit with 0."""
        mock_search.return_value = []
        test_args = ["chuck_norris_joke.py", "--search", "nonexistent"]
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", new_callable=lambda: StringIO(newline="")):
                with self.assertRaises(SystemExit) as ctx:
                    cnj.main()
        self.assertEqual(ctx.exception.code, 0)


class TestInteractiveCommands(unittest.TestCase):
    """Test the handle_interactive_command function."""

    def setUp(self):
        self.session = cnj.Session()
        self.session.add_joke(MOCK_JOKE)

    def test_command_quit(self):
        """/quit should return 'quit'."""
        result = cnj.handle_interactive_command("/quit", self.session, MOCK_JOKE)
        self.assertEqual(result, "quit")

    def test_command_next(self):
        """/next should return 'next'."""
        result = cnj.handle_interactive_command("/next", self.session, MOCK_JOKE)
        self.assertEqual(result, "next")

    def test_command_category(self):
        """/category should return 'category'."""
        result = cnj.handle_interactive_command("/category", self.session, MOCK_JOKE)
        self.assertEqual(result, "category")

    def test_command_search(self):
        """/search should return 'search'."""
        result = cnj.handle_interactive_command("/search", self.session, MOCK_JOKE)
        self.assertEqual(result, "search")

    def test_command_help(self):
        """/help should print help and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/help", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("/next", output)
            self.assertIn("/quit", output)

    def test_command_stats(self):
        """/stats should print stats and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/stats", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("Session Stats", output)

    def test_command_history(self):
        """/history should print history and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/history", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("Joke History", output)

    def test_command_favorites(self):
        """/favorites should print favorites and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/favorites", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("No favorites", output)

    def test_command_fave_with_joke(self):
        """/fave should toggle favorite on current joke."""
        with patch("sys.stdout", new_callable=StringIO):
            result = cnj.handle_interactive_command("/fave", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            self.assertEqual(len(self.session.favorites), 1)

    def test_command_fave_without_joke(self):
        """/fave should handle case with no current joke."""
        with patch("sys.stdout", new_callable=StringIO):
            result = cnj.handle_interactive_command("/fave", self.session, None)
            self.assertIsNone(result)
            self.assertEqual(len(self.session.favorites), 0)

    def test_command_banner(self):
        """/banner should print banner and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/banner", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("CHUCK NORRIS", output)

    def test_unknown_command(self):
        """An unknown command should print a message and return None."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cnj.handle_interactive_command("/unknown", self.session, MOCK_JOKE)
            self.assertIsNone(result)
            output = mock_stdout.getvalue()
            self.assertIn("Unknown command", output)


class TestStyle(unittest.TestCase):
    """Test the Style class for ANSI color handling."""

    def test_style_disabled_when_not_tty(self):
        """Style should return empty strings when not a TTY."""
        # Force _enabled to False
        with patch.object(cnj.Style, "_enabled", False):
            s = cnj.Style()
            self.assertEqual(s.RED, "")
            self.assertEqual(s.GREEN, "")
            self.assertEqual(s.BOLD, "")
            self.assertEqual(s.RESET, "")

    def test_style_enabled_when_tty(self):
        """Style should return ANSI codes when TTY."""
        with patch.object(cnj.Style, "_enabled", True):
            s = cnj.Style()
            self.assertEqual(s.RED, "\033[91m")
            self.assertEqual(s.GREEN, "\033[92m")
            self.assertEqual(s.BOLD, "\033[1m")
            self.assertEqual(s.RESET, "\033[0m")

    def test_emoji_helpers(self):
        """Emoji helpers should return emoji strings."""
        self.assertEqual(cnj.Style.thumbs_up(), "\U0001f44d")
        self.assertEqual(cnj.Style.thumbs_down(), "\U0001f44e")
        self.assertEqual(cnj.Style.fire(), "\U0001f525")
        self.assertEqual(cnj.Style.star(), "\u2b50")
        self.assertEqual(cnj.Style.thinking(), "\U0001f914")
        self.assertEqual(cnj.Style.party(), "\U0001f389")
        # chuck() returns a ZWJ sequence (person + scales emoji)
        self.assertIn("\U0001f9d1", cnj.Style.chuck())  # person emoji


class TestTypewriter(unittest.TestCase):
    """Test the typewriter animation function."""

    def test_typewriter_output(self):
        """typewriter should print the given text."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.typewriter("Hello Chuck!", delay=0.001)
            output = mock_stdout.getvalue()
            self.assertIn("Hello Chuck!", output)

    def test_typewriter_custom_ending(self):
        """typewriter should use custom ending."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cnj.typewriter("Test", ending="!!!")
            output = mock_stdout.getvalue()
            self.assertTrue(output.endswith("!!!"))


class TestRateJoke(unittest.TestCase):
    """Test the rate_joke function."""

    def setUp(self):
        self.session = cnj.Session()
        # Patch stdout to handle emoji characters on Windows
        self.stdout_patcher = patch("sys.stdout", new_callable=lambda: StringIO(newline=""))
        self.mock_stdout = self.stdout_patcher.start()

    def tearDown(self):
        self.stdout_patcher.stop()

    @patch("builtins.input", return_value="1")
    def test_rate_funny(self, mock_input):
        """Rating 1 should increment likes."""
        cnj.rate_joke(self.session, MOCK_JOKE)
        self.assertEqual(self.session.likes, 1)
        self.assertEqual(self.session.dislikes, 0)

    @patch("builtins.input", return_value="2")
    def test_rate_meh(self, mock_input):
        """Rating 2 should increment dislikes."""
        cnj.rate_joke(self.session, MOCK_JOKE)
        self.assertEqual(self.session.likes, 0)
        self.assertEqual(self.session.dislikes, 1)

    @patch("builtins.input", return_value="3")
    def test_rate_favorite(self, mock_input):
        """Rating 3 should add to favorites."""
        cnj.rate_joke(self.session, MOCK_JOKE)
        self.assertEqual(len(self.session.favorites), 1)

    @patch("builtins.input", return_value="4")
    def test_rate_skip(self, mock_input):
        """Rating 4 should skip rating."""
        cnj.rate_joke(self.session, MOCK_JOKE)
        self.assertEqual(self.session.likes, 0)
        self.assertEqual(self.session.dislikes, 0)
        self.assertEqual(len(self.session.favorites), 0)

    @patch("builtins.input", return_value="invalid")
    def test_rate_invalid(self, mock_input):
        """Invalid rating should not change stats."""
        cnj.rate_joke(self.session, MOCK_JOKE)
        self.assertEqual(self.session.likes, 0)
        self.assertEqual(self.session.dislikes, 0)


if __name__ == "__main__":
    unittest.main()
