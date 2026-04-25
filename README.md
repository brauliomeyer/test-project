# Chuck Norris Joke Fetcher — Interactive Edition

Fetches random Chuck Norris jokes from [api.chucknorris.io](https://api.chucknorris.io) using only the Python standard library.

## Features

- **Interactive mode** — A full REPL experience with slash commands
- **Random jokes** — With optional category filtering
- **Interactive category browser** — Browse and pick categories with pagination
- **Keyword search** — Search jokes by keyword, pick your favorite from results
- **Joke rating** — Rate jokes 👍/👎 and track your session stats
- **Favorites** — Save jokes you love during a session
- **Joke history** — Review all jokes you've seen
- **Typewriter animation** — Dramatic text reveal for comedic effect
- **Colorful output** — ANSI colors and emojis (auto-disabled when piping)

## Usage

```bash
# Interactive mode (just run it!)
python chuck_norris_joke.py

# Fetch a single random joke
python chuck_norris_joke.py --random

# Fetch a joke from a specific category
python chuck_norris_joke.py --category animal

# List available categories
python chuck_norris_joke.py --categories

# Search jokes by keyword
python chuck_norris_joke.py --search roundhouse

# Show help
python chuck_norris_joke.py --help
```

## Interactive Commands

Once in interactive mode, type any of these at the `chuck>` prompt:

| Command | Description |
|---------|-------------|
| `Enter` (empty) | Fetch a random joke |
| `/next` | Show another random joke |
| `/category` | Browse and pick a category |
| `/search` | Search jokes by keyword |
| `/fave` | Toggle favorite on the current joke |
| `/history` | Show all jokes this session |
| `/favorites` | Show your saved favorites |
| `/stats` | Show session statistics |
| `/banner` | Show the welcome banner again |
| `/help` | Show available commands |
| `/quit` | Exit |
| *anything else* | Quick search by keyword |

## Requirements

- Python 3.10+ (uses `dict | list` union type syntax)
- No third-party packages required
