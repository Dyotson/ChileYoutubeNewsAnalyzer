#!/usr/bin/env python3
"""Chilean YouTube News Comment Analyzer

Scrapes YouTube comments, analyses word frequency, detects suspected bots,
and exports results to CSV.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from src.scraper import scrape_all
from src.word_analysis import compute_word_frequency
from src.bot_detector import analyze_bots
from src.exporter import (
    export_word_frequency,
    export_bot_analysis,
    export_video_summary,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze YouTube comments for bot activity in Chilean political news",
    )
    parser.add_argument(
        "-i", "--input",
        default="links.txt",
        help="Path to file with YouTube URLs, one per line (default: links.txt)",
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Directory for CSV output files (default: output/)",
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.5,
        help="Bot score threshold 0.0-1.0 (default: 0.5)",
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=None,
        help="Max comments to fetch per video (default: no limit)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Chilean YouTube News Comment Analyzer")
    print("=" * 60)
    print(f"  Input:     {args.input}")
    print(f"  Output:    {args.output}/")
    print(f"  Threshold: {args.threshold}")
    print(f"  Limit:     {args.limit or 'no limit'}")
    print("=" * 60)
    print()

    t0 = time.time()

    print("[1/4] Scraping comments...")
    comments_by_video = scrape_all(args.input, limit=args.limit)
    if not comments_by_video:
        print("No comments collected. Exiting.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    raw_path = os.path.join(args.output, "raw_comments.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(comments_by_video, f, ensure_ascii=False, indent=2)
    total_raw = sum(len(v) for v in comments_by_video.values())
    print(f"  -> Saved {total_raw} raw comments to {raw_path}")

    print("[2/4] Computing word frequency...")
    ranked_words = compute_word_frequency(comments_by_video)

    print("[3/4] Running bot detection...")
    bot_results = analyze_bots(comments_by_video, threshold=args.threshold)

    bot_count = sum(1 for r in bot_results if r["is_suspected_bot"])
    total = len(bot_results)
    pct = round(bot_count / total * 100, 2) if total else 0.0
    print(f"  -> {bot_count}/{total} comments flagged as suspected bots ({pct}%)")

    print("\n[4/4] Exporting CSVs...")
    export_word_frequency(ranked_words, args.output)
    export_bot_analysis(bot_results, args.output)
    export_video_summary(bot_results, args.output)

    elapsed = round(time.time() - t0, 1)
    print(f"\nDone in {elapsed}s. Results in {args.output}/")


if __name__ == "__main__":
    main()
