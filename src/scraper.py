from __future__ import annotations

import sys
from typing import Optional

from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT


def load_urls(filepath: str) -> list[str]:
    """
    @param filepath - path to a text file with one YouTube URL per line
    """
    urls: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                urls.append(stripped)
    return urls


def scrape_comments(
    url: str,
    limit: Optional[int] = None,
    sort_by: int = SORT_BY_RECENT,
) -> list[dict]:
    """
    @param url - YouTube video URL
    @param limit - max comments to fetch (None = all)
    @param sort_by - SORT_BY_RECENT (1) or SORT_BY_POPULAR (0)
    """
    downloader = YoutubeCommentDownloader()
    comments: list[dict] = []

    try:
        generator = downloader.get_comments_from_url(url, sort_by=sort_by)
        for i, comment in enumerate(generator):
            comment["video_url"] = url
            comments.append(comment)
            if limit and i + 1 >= limit:
                break
    except Exception as exc:
        print(f"  [ERROR] Failed to scrape {url}: {exc}", file=sys.stderr)

    return comments


def scrape_all(
    filepath: str,
    limit: Optional[int] = None,
) -> dict[str, list[dict]]:
    """
    @param filepath - path to links file
    @param limit - max comments per video
    @returns dict mapping video URL to its list of comment dicts
    """
    urls = load_urls(filepath)
    if not urls:
        print("[WARN] No URLs found in links file.", file=sys.stderr)
        return {}

    all_comments: dict[str, list[dict]] = {}

    for idx, url in enumerate(urls, start=1):
        print(f"[{idx}/{len(urls)}] Scraping: {url}")
        comments = scrape_comments(url, limit=limit)
        all_comments[url] = comments
        print(f"  -> {len(comments)} comments collected")

    total = sum(len(c) for c in all_comments.values())
    print(f"\nTotal: {total} comments from {len(urls)} videos\n")
    return all_comments
