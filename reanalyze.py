#!/usr/bin/env python3
"""Re-analyze previously scraped YouTube comments without re-scraping.

Reads raw_comments.json (saved by main.py), then re-runs bot detection
with tunable thresholds, classifies political leaning, optionally profiles
suspected bot channels, and exports updated CSVs.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

from src.bot_detector import analyze_bots
from src.word_analysis import compute_word_frequency
from src.political_classifier import classify_political_leaning, classify_all_comments
from src.user_profiler import profile_users
from src.exporter import export_word_frequency, export_video_summary


def _load_raw_comments(path: str) -> dict[str, list[dict]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _export_bot_analysis_with_leaning(
    bot_results: list[dict],
    user_profiles: dict[str, dict],
    output_dir: str,
) -> str:
    """Extended bot_analysis.csv with political leaning and user profile columns."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "bot_analysis.csv")

    fieldnames = [
        "video_url", "author", "channel_id", "comment_text",
        "votes", "time", "bot_score", "bot_category",
        "flags", "is_suspected_bot",
        "political_leaning", "right_signals", "left_signals",
        "user_public_videos", "user_subscribers",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in bot_results:
            leaning, r_score, l_score = classify_political_leaning(
                row["comment_text"],
            )
            profile = user_profiles.get(row.get("channel_id", ""), {})
            row_out = {
                **row,
                "political_leaning": leaning,
                "right_signals": r_score,
                "left_signals": l_score,
                "user_public_videos": profile.get("public_videos", ""),
                "user_subscribers": profile.get("subscribers", ""),
            }
            writer.writerow(row_out)

    bot_count = sum(1 for r in bot_results if r["is_suspected_bot"])
    print(f"  -> Wrote {filepath} ({len(bot_results)} comments, {bot_count} suspected bots)")
    return filepath


def _export_political_summary(
    political_stats: dict,
    output_dir: str,
) -> str:
    """Export political leaning summary CSV."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "political_summary.csv")

    fieldnames = [
        "video_url", "total_comments",
        "left_count", "right_count", "neutral_count",
        "left_pct", "right_pct", "neutral_pct",
    ]

    rows: list[dict] = []

    for url, stats in political_stats["per_video"].items():
        total = stats["total"]
        rows.append({
            "video_url": url,
            "total_comments": total,
            "left_count": stats["left"],
            "right_count": stats["right"],
            "neutral_count": stats["neutral"],
            "left_pct": round(stats["left"] / total * 100, 2) if total else 0,
            "right_pct": round(stats["right"] / total * 100, 2) if total else 0,
            "neutral_pct": round(stats["neutral"] / total * 100, 2) if total else 0,
        })

    overall = political_stats["overall"]
    total = overall["total"]
    rows.append({
        "video_url": "TOTAL",
        "total_comments": total,
        "left_count": overall["left"],
        "right_count": overall["right"],
        "neutral_count": overall["neutral"],
        "left_pct": round(overall["left"] / total * 100, 2) if total else 0,
        "right_pct": round(overall["right"] / total * 100, 2) if total else 0,
        "neutral_pct": round(overall["neutral"] / total * 100, 2) if total else 0,
    })

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"  -> Wrote {filepath}")
    return filepath


def _compute_bot_volume(bot_results: list[dict]) -> dict:
    """FactCheck-style analysis: unique bot accounts vs their total comment volume.

    A user is classified as a bot account if ANY of their comments scored above
    the threshold. Then ALL comments by that user are counted as bot-generated.
    """
    from collections import defaultdict

    author_comments: dict[str, list[dict]] = defaultdict(list)
    for row in bot_results:
        author_comments[row["author"]].append(row)

    total_accounts = len(author_comments)
    total_comments = len(bot_results)

    bot_accounts: set[str] = set()
    for author, comments in author_comments.items():
        if any(c["is_suspected_bot"] for c in comments):
            bot_accounts.add(author)

    bot_account_count = len(bot_accounts)
    bot_comment_volume = sum(
        len(author_comments[a]) for a in bot_accounts
    )

    flagged_comments = sum(1 for r in bot_results if r["is_suspected_bot"])

    return {
        "total_accounts": total_accounts,
        "total_comments": total_comments,
        "bot_accounts": bot_account_count,
        "bot_account_pct": round(bot_account_count / total_accounts * 100, 2) if total_accounts else 0,
        "bot_comment_volume": bot_comment_volume,
        "bot_comment_volume_pct": round(bot_comment_volume / total_comments * 100, 2) if total_comments else 0,
        "flagged_comments": flagged_comments,
        "flagged_comments_pct": round(flagged_comments / total_comments * 100, 2) if total_comments else 0,
        "avg_comments_per_bot": round(bot_comment_volume / bot_account_count, 1) if bot_account_count else 0,
        "avg_comments_per_human": round(
            (total_comments - bot_comment_volume) / (total_accounts - bot_account_count), 1
        ) if (total_accounts - bot_account_count) > 0 else 0,
    }


def _export_bot_volume_summary(
    bot_results: list[dict],
    output_dir: str,
) -> str:
    """Export FactCheck-style bot volume analysis CSV."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "bot_volume_summary.csv")

    from collections import defaultdict

    author_comments: dict[str, list[dict]] = defaultdict(list)
    for row in bot_results:
        author_comments[row["author"]].append(row)

    bot_accounts: set[str] = set()
    for author, comments in author_comments.items():
        if any(c["is_suspected_bot"] for c in comments):
            bot_accounts.add(author)

    fieldnames = [
        "author", "channel_id", "is_bot_account",
        "total_comments", "flagged_comments", "max_bot_score",
        "videos_appeared_in", "avg_bot_score",
    ]

    rows: list[dict] = []
    for author, comments in author_comments.items():
        flagged = [c for c in comments if c["is_suspected_bot"]]
        scores = [c["bot_score"] for c in comments]
        videos = set(c["video_url"] for c in comments)
        rows.append({
            "author": author,
            "channel_id": comments[0].get("channel_id", ""),
            "is_bot_account": author in bot_accounts,
            "total_comments": len(comments),
            "flagged_comments": len(flagged),
            "max_bot_score": max(scores),
            "videos_appeared_in": len(videos),
            "avg_bot_score": round(sum(scores) / len(scores), 3),
        })

    rows.sort(key=lambda r: r["max_bot_score"], reverse=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"  -> Wrote {filepath} ({len(rows)} unique accounts)")
    return filepath


def _export_user_profiles(
    profiles: dict[str, dict],
    output_dir: str,
) -> str:
    """Export user profile data for suspected bots."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "user_profiles.csv")

    fieldnames = [
        "author", "channel_id", "max_bot_score",
        "public_videos", "has_zero_videos",
        "subscribers", "description_snippet",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for profile in sorted(
            profiles.values(), key=lambda p: p["max_bot_score"], reverse=True,
        ):
            writer.writerow(profile)

    print(f"  -> Wrote {filepath} ({len(profiles)} users)")
    return filepath


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-analyze scraped YouTube comments without re-scraping",
    )
    parser.add_argument(
        "-r", "--raw",
        default="output/raw_comments.json",
        help="Path to raw_comments.json (default: output/raw_comments.json)",
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
        "--profile-threshold",
        type=float,
        default=0.4,
        help="Min bot score to trigger user profile scraping (default: 0.4)",
    )
    parser.add_argument(
        "--skip-profiling",
        action="store_true",
        help="Skip user channel profiling (faster re-runs)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Re-Analysis (no re-scraping)")
    print("=" * 60)
    print(f"  Raw data:          {args.raw}")
    print(f"  Output:            {args.output}/")
    print(f"  Bot threshold:     {args.threshold}")
    print(f"  Profile threshold: {args.profile_threshold}")
    print(f"  Skip profiling:    {args.skip_profiling}")
    print("=" * 60)
    print()

    t0 = time.time()

    print("[1/5] Loading raw comments...")
    if not os.path.exists(args.raw):
        print(
            f"[ERROR] {args.raw} not found. Run main.py first to scrape and save raw data.",
            file=sys.stderr,
        )
        sys.exit(1)
    comments_by_video = _load_raw_comments(args.raw)
    total = sum(len(v) for v in comments_by_video.values())
    print(f"  -> {total} comments from {len(comments_by_video)} videos\n")

    print("[2/5] Re-running bot detection (threshold={})...".format(args.threshold))
    bot_results = analyze_bots(comments_by_video, threshold=args.threshold)

    vol = _compute_bot_volume(bot_results)
    print(f"  -> {vol['flagged_comments']}/{vol['total_comments']} comments individually flagged ({vol['flagged_comments_pct']}%)")
    print()
    print("  --- FactCheck-style account vs volume analysis ---")
    print(f"  Unique accounts:       {vol['total_accounts']}")
    print(f"  Bot accounts:          {vol['bot_accounts']} ({vol['bot_account_pct']}% of accounts)")
    print(f"  Comments by bots:      {vol['bot_comment_volume']} ({vol['bot_comment_volume_pct']}% of all comments)")
    print(f"  Avg comments/bot:      {vol['avg_comments_per_bot']}")
    print(f"  Avg comments/human:    {vol['avg_comments_per_human']}")
    print()

    print("[3/5] Classifying political leaning...")
    political_stats = classify_all_comments(comments_by_video)
    ov = political_stats["overall"]
    lp = round(ov["left"] / ov["total"] * 100, 1) if ov["total"] else 0
    rp = round(ov["right"] / ov["total"] * 100, 1) if ov["total"] else 0
    np_ = round(ov["neutral"] / ov["total"] * 100, 1) if ov["total"] else 0
    print(f"  -> Left: {ov['left']} ({lp}%)  Right: {ov['right']} ({rp}%)  Neutral: {ov['neutral']} ({np_}%)\n")

    user_profiles: dict[str, dict] = {}
    if not args.skip_profiling:
        print("[4/5] Profiling suspected bot channels...")
        user_profiles = profile_users(
            bot_results,
            score_threshold=args.profile_threshold,
            sleep_between=0.5,
        )
        print()
    else:
        print("[4/5] Skipping user profiling (--skip-profiling)\n")

    print("[5/5] Exporting CSVs...")
    ranked_words = compute_word_frequency(comments_by_video)
    export_word_frequency(ranked_words, args.output)
    _export_bot_analysis_with_leaning(bot_results, user_profiles, args.output)
    export_video_summary(bot_results, args.output)
    _export_political_summary(political_stats, args.output)
    _export_bot_volume_summary(bot_results, args.output)
    if user_profiles:
        _export_user_profiles(user_profiles, args.output)

    elapsed = round(time.time() - t0, 1)
    print(f"\nDone in {elapsed}s. Results in {args.output}/")


if __name__ == "__main__":
    main()
