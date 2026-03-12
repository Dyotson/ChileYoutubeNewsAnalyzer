# Chilean YouTube News Comment Analyzer

Research tool for analyzing bot activity in Chilean political YouTube news comments. Scrapes comments without the YouTube API, performs word frequency analysis, detects suspected bots using multi-signal heuristics, and exports results to CSV.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On first run the NLTK Spanish stopwords corpus is downloaded automatically.

## Usage

1. Add YouTube URLs to `links.txt` (one per line, lines starting with `#` are ignored).

2. Run the analyzer:

```bash
python main.py
```

### CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `-i`, `--input` | `links.txt` | Path to file with YouTube URLs |
| `-o`, `--output` | `output/` | Directory for CSV output files |
| `-t`, `--threshold` | `0.6` | Bot score threshold (0.0 - 1.0) |
| `-l`, `--limit` | no limit | Max comments to fetch per video |

Example with options:

```bash
python main.py -i links.txt -o output -t 0.5 -l 500
```

## Output

Three CSV files are generated in the output directory:

### `word_frequency.csv`

| Column | Description |
|--------|-------------|
| rank | Position by frequency (1 = most common) |
| word | The word (lowercased, accents stripped) |
| count | Number of occurrences across all videos |

Spanish stopwords and YouTube noise words are filtered out.

### `bot_analysis.csv`

One row per comment across all videos.

| Column | Description |
|--------|-------------|
| video_url | Source video |
| author | Comment author display name |
| channel_id | Author's YouTube channel ID |
| comment_text | Full comment text |
| votes | Like count |
| time | Timestamp |
| bot_score | Heuristic score 0.0 - 1.0 |
| bot_category | `astroturfing`, `attack_bot`, `propaganda`, `spam`, `mixed`, or empty |
| flags | Pipe-separated heuristic tags that triggered |
| is_suspected_bot | `True` if bot_score >= threshold |

### `video_summary.csv`

One row per video plus a TOTAL row.

| Column | Description |
|--------|-------------|
| video_url | Video URL |
| total_comments | Comments scraped |
| suspected_bots | Count above threshold |
| bot_percentage | `suspected_bots / total_comments * 100` |
| astroturfing_count | Positive astroturfing bots |
| attack_bot_count | Negative / attack bots |
| propaganda_count | Copy-paste propaganda bots |
| spam_count | Generic spam bots |
| mixed_count | Bots matching multiple categories |

## Bot detection heuristics

Designed for Chilean political content. Detects five bot archetypes:

- **Astroturfing** -- generic praise without substance ("buen video", "tiene toda la razon")
- **Attack bots** -- political insults as entire comments, ALL CAPS, repetitive spam
- **Propaganda** -- identical text posted by different authors, unusually formal tone
- **Spam** -- promotional URLs, auto-generated usernames
- **Mixed** -- triggers signals from multiple categories equally

Signals are grouped into: username patterns, positive astroturfing, negative/attack, propaganda, and cross-video behaviour. Each signal adds to a cumulative score capped at 1.0. See `src/bot_detector.py` for the full scoring logic and curated word lists.

## Project structure

```
ChileYoutubeNewsAnalyzer/
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── links.txt                 # Input: YouTube URLs
├── src/
│   ├── __init__.py
│   ├── scraper.py            # Comment scraping
│   ├── word_analysis.py      # Word frequency analysis
│   ├── bot_detector.py       # Bot detection heuristics
│   └── exporter.py           # CSV export
└── output/                   # Generated CSV files
```
