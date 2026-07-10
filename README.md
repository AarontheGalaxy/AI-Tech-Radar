# AI Tech Radar

[![CI](https://github.com/AarontheGalaxy/AI-Tech-Radar/actions/workflows/ci.yml/badge.svg)](https://github.com/AarontheGalaxy/AI-Tech-Radar/actions/workflows/ci.yml)

A Python CLI tool that automatically fetches the latest tech and AI news from multiple sources, processes them with a local LLM (Ollama), and generates a clean daily summary report.

## Features

- **Multi-source Fetching**: Aggregates top daily content from Hacker News, Arxiv, GitHub Trending, and Dev.to.
- **Local AI Processing**: Uses Ollama (Llama 3.1) locally to summarize and rank the news. No API costs!
- **Smart Deduplication**: Identifies and removes duplicate news across different platforms.
- **Fast & Concurrent**: Fetches from all sources in parallel using multithreading.
- **Advanced Interactive TUI**: A terminal dashboard to browse Top 20 developments, filter by category, and view full details with keyboard navigation.
- **Markdown Reports**: Automatically saves daily summaries in a `reports/` folder.

## Tech Stack

| Technology   | Purpose             |
| ------------ | ------------------- |
| Python 3.11+ | Core Language       |
| Ollama       | Local LLM Engine    |
| Llama 3.1    | AI Model            |
| Textual      | TUI Framework       |
| Requests     | HTTP Library        |
| Dev.to API   | Tech & AI Articles  |
| Arxiv        | Arxiv API Wrapper   |
| Feedparser   | RSS Parsing         |
| Rich         | Terminal Formatting |

## Project Structure

```text
ai-tech-radar/
├── src/
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── hackernews.py
│   │   ├── reddit.py
│   │   ├── arxiv_fetcher.py
│   │   ├── github_trending.py
│   │   └── devto.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── summarizer.py
│   ├── interactive.py
│   └── main.py
├── reports/
├── .env.example
├── .gitignore
├── requirements.txt
├── run.sh
├── run.bat
└── README.md
```

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/AarontheGalaxy/AI-Tech-Radar.git
   cd ai-tech-radar
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv venv

   # macOS/Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama**
   - Download and install [Ollama](https://ollama.com/).
   - Pull the Llama 3.1 model:

     ```bash
     ollama run llama3.1
     ```

5. **Configure Environment Variables**
   - Copy `.env.example` to `.env`:

     ```bash
     cp .env.example .env
     ```

   - Fill in your Reddit credentials in `.env`.

## How to get Reddit API Credentials

1. Log in to your Reddit account.
2. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps).
3. Click "Create app" or "Create another app" at the bottom.
4. Select "script".
5. Name your app (e.g., `ai-tech-radar`).
6. Set "redirect uri" to `http://localhost:8080` (it won't be used, but is required).
7. Click "create app".
8. The string under your app name is the `REDDIT_CLIENT_ID`.
9. The string next to "secret" is the `REDDIT_CLIENT_SECRET`.

## Usage

Simply run the launch script for your platform to start fetching, analyzing, and summarising with the interactive TUI:

```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

Alternatively, you can run the main script directly:

```bash
python src/main.py
```

## Keyboard Shortcuts

| Key          | Action                        |
| ------------ | ----------------------------- |
| `Arrow Keys` | Navigate list                 |
| `Enter`      | Focus detail panel            |
| `O`          | Open URL in browser           |
| `F`          | Cycle category filter         |
| `S`          | Toggle Top 20 vs. All Results |
| `Q / Esc`    | Quit app                      |

## Example Output

The application generates two types of output:

**1. Markdown Reports (`reports/`)**
A daily summary file is automatically saved, starting with a one-liner overview of the day's tech news, followed by the Top 20 most important developments. Each item includes its category, an importance score (out of 10), a brief summary, and a direct link to the source.

**2. Interactive Terminal UI (TUI)**
When launched in interactive mode, the app provides a split-screen dashboard:

- **Left Panel:** A navigable list displaying rank, source badge (e.g., `[HN]`, `[GIT]`), title, and importance score. You can toggle between the curated "Top 20" and "All Results".
- **Right Panel:** The detail view showing full metadata, the complete AI-generated summary, and the URL.
- **Filtering:** You can filter the view by categories like AI/ML, DevTools, Security, Research, and Web.

## License

MIT License
🐢
AarontheGalaxy
