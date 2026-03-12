from __future__ import annotations

import csv
import os
from collections import Counter


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def export_word_frequency(
    ranked_words: list[tuple[int, str, int]],
    output_dir: str,
) -> str:
    """
    @param ranked_words - list of (rank, word, count)
    @param output_dir - directory to write CSV into
    @returns path to the written CSV
    """
    _ensure_dir(output_dir)
    filepath = os.path.join(output_dir, "word_frequency.csv")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "word", "count"])
        for rank, word, count in ranked_words:
            writer.writerow([rank, word, count])

    print(f"  -> Wrote {filepath} ({len(ranked_words)} words)")
    return filepath


def export_bot_analysis(
    bot_results: list[dict],
    output_dir: str,
) -> str:
    """
    @param bot_results - enriched comment dicts from bot_detector.analyze_bots
    @param output_dir - directory to write CSV into
    @returns path to the written CSV
    """
    _ensure_dir(output_dir)
    filepath = os.path.join(output_dir, "bot_analysis.csv")

    fieldnames = [
        "video_url", "author", "channel_id", "comment_text",
        "votes", "time", "bot_score", "bot_category",
        "flags", "is_suspected_bot",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in bot_results:
            writer.writerow(row)

    bot_count = sum(1 for r in bot_results if r["is_suspected_bot"])
    print(f"  -> Wrote {filepath} ({len(bot_results)} comments, {bot_count} suspected bots)")
    return filepath


def export_video_summary(
    bot_results: list[dict],
    output_dir: str,
) -> str:
    """
    @param bot_results - enriched comment dicts from bot_detector.analyze_bots
    @param output_dir - directory to write CSV into
    @returns path to the written CSV
    """
    _ensure_dir(output_dir)
    filepath = os.path.join(output_dir, "video_summary.csv")

    video_stats: dict[str, dict] = {}

    for row in bot_results:
        url = row["video_url"]
        if url not in video_stats:
            video_stats[url] = {
                "video_url": url,
                "total_comments": 0,
                "suspected_bots": 0,
                "astroturfing_count": 0,
                "attack_bot_count": 0,
                "propaganda_count": 0,
                "spam_count": 0,
                "mixed_count": 0,
            }

        stats = video_stats[url]
        stats["total_comments"] += 1

        if row["is_suspected_bot"]:
            stats["suspected_bots"] += 1
            cat = row.get("bot_category", "")
            key = f"{cat}_count"
            if key in stats:
                stats[key] += 1

    fieldnames = [
        "video_url", "total_comments", "suspected_bots", "bot_percentage",
        "astroturfing_count", "attack_bot_count", "propaganda_count",
        "spam_count", "mixed_count",
    ]

    rows: list[dict] = []
    totals = {fn: 0 for fn in fieldnames}
    totals["video_url"] = "TOTAL"

    for stats in video_stats.values():
        pct = (
            round(stats["suspected_bots"] / stats["total_comments"] * 100, 2)
            if stats["total_comments"] > 0
            else 0.0
        )
        stats["bot_percentage"] = pct
        rows.append(stats)

        for fn in fieldnames:
            if fn not in ("video_url", "bot_percentage"):
                totals[fn] += stats.get(fn, 0)

    if totals["total_comments"] > 0:
        totals["bot_percentage"] = round(
            totals["suspected_bots"] / totals["total_comments"] * 100, 2,
        )
    else:
        totals["bot_percentage"] = 0.0

    rows.append(totals)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"  -> Wrote {filepath} ({len(video_stats)} videos)")
    return filepath
