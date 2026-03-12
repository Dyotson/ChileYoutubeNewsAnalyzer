from __future__ import annotations

import re
import sys
import time

import requests
import scrapetube


def _count_channel_videos(channel_id: str, timeout: int = 10) -> int | None:
    """
    @param channel_id - YouTube channel ID (e.g. UCxxxxxxxx)
    @param timeout - request timeout in seconds
    @returns number of public videos, or None on failure
    """
    try:
        count = 0
        for _ in scrapetube.get_channel(channel_id=channel_id, limit=5, sleep=0):
            count += 1
        return count
    except Exception:
        return None


def _fetch_channel_page_info(channel_id: str, timeout: int = 10) -> dict:
    """Scrape basic metadata from the channel's about page HTML.

    @param channel_id - YouTube channel ID
    @param timeout - request timeout in seconds
    @returns dict with subscriber_text, joined_text, description snippet
    """
    url = f"https://www.youtube.com/channel/{channel_id}"
    info: dict = {"subscribers": None, "description_snippet": None}

    try:
        session = requests.Session()
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        session.headers["Accept-Language"] = "es-CL,es;q=0.9"
        session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
        resp = session.get(url, timeout=timeout, params={"ucbcb": 1})

        sub_match = re.search(
            r'"subscriberCountText":\{"simpleText":"([^"]+)"', resp.text,
        )
        if sub_match:
            info["subscribers"] = sub_match.group(1)

        desc_match = re.search(
            r'"description":\{"simpleText":"([^"]{0,200})', resp.text,
        )
        if desc_match:
            info["description_snippet"] = desc_match.group(1)[:200]

        session.close()
    except Exception:
        pass

    return info


def profile_users(
    bot_results: list[dict],
    score_threshold: float = 0.4,
    sleep_between: float = 1.0,
) -> dict[str, dict]:
    """Profile YouTube channels of suspected bots.

    @param bot_results - enriched comment dicts from bot_detector.analyze_bots
    @param score_threshold - only profile users with bot_score >= this
    @param sleep_between - delay between requests to avoid rate limiting
    @returns dict mapping channel_id to profile info
    """
    candidates: dict[str, dict] = {}
    for row in bot_results:
        if row["bot_score"] >= score_threshold:
            cid = row.get("channel_id", "")
            if cid and cid not in candidates:
                candidates[cid] = {
                    "author": row["author"],
                    "channel_id": cid,
                    "max_bot_score": row["bot_score"],
                }
            elif cid in candidates:
                candidates[cid]["max_bot_score"] = max(
                    candidates[cid]["max_bot_score"], row["bot_score"],
                )

    if not candidates:
        print("  No users above threshold to profile.")
        return {}

    print(f"  Profiling {len(candidates)} user channels (score >= {score_threshold})...")

    profiles: dict[str, dict] = {}
    for idx, (cid, info) in enumerate(candidates.items(), start=1):
        if idx % 10 == 0 or idx == 1:
            print(f"    [{idx}/{len(candidates)}] {info['author']}")

        video_count = _count_channel_videos(cid)
        page_info = _fetch_channel_page_info(cid)

        profiles[cid] = {
            "author": info["author"],
            "channel_id": cid,
            "max_bot_score": info["max_bot_score"],
            "public_videos": video_count,
            "has_zero_videos": video_count == 0 if video_count is not None else None,
            "subscribers": page_info.get("subscribers"),
            "description_snippet": page_info.get("description_snippet"),
        }

        time.sleep(sleep_between)

    zero_vids = sum(1 for p in profiles.values() if p.get("has_zero_videos"))
    print(f"  -> {zero_vids}/{len(profiles)} suspected bots have zero public videos")

    return profiles
