#!/usr/bin/env python3
"""Scan YouTube channels and collect political video URLs for analysis.

Reads channel identifiers from a text file, fetches video listings via
scrapetube, filters by Chilean political keywords in the title, and writes
matching URLs to a links file consumable by the comment analyzer.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

import scrapetube
import scrapetube.scrapetube as _scrapetube_internals

# Monkey-patch scrapetube to request Spanish titles from YouTube.
# The library hardcodes Accept-Language to "en", causing YouTube to
# auto-translate every title to English -- useless for Spanish keyword matching.
_original_get_session = _scrapetube_internals.get_session

def _get_session_es(proxies=None):
    session = _original_get_session(proxies)
    session.headers["Accept-Language"] = "es-CL,es;q=0.9"
    return session

_scrapetube_internals.get_session = _get_session_es


# ---------------------------------------------------------------------------
# Default Chilean political keyword list
# ---------------------------------------------------------------------------

POLITICAL_KEYWORDS: list[str] = [
    # Institutions / roles
    "diputado", "diputada", "diputados", "diputadas",
    "senador", "senadora", "senadores", "senadoras",
    "congreso", "parlamento", "camara",
    "gobierno", "ministerio", "ministro", "ministra",
    "fiscal", "contralor", "contraloria",
    "constituyente", "constitucional", "constitucion",
    "municipalidad", "alcalde", "alcaldesa",
    "gobernador", "gobernadora", "intendente",
    "seremi", "subsecretario", "subsecretaria",
    "presidente", "presidenta", "presidencia",
    "canciller", "cancilleria",

    # Political figures (surnames)
    "boric", "kast", "vallejo", "jackson", "siches",
    "grau", "toha", "tohá", "chadwick", "matthei",
    "provoste", "jadue", "pamela jiles", "jiles",
    "kaiser", "schalper", "van rysselberghe",
    "chahuan", "ossandon", "ossandón", "desbordes",
    "lucas palacios", "insulza", "lagos", "bachelet",
    "pinera", "piñera", "lavin", "lavín",
    "sichel", "meo", "artés", "parisi",

    # Parties / coalitions
    "apruebo dignidad", "chile vamos", "chile seguro",
    "republicano", "republicanos", "partido republicano",
    "frente amplio", "udi", "renovacion nacional", "renovación nacional",
    "socialista", "partido socialista",
    "democrata cristiano", "demócrata cristiano", "pdc",
    "evopoli", "comunista", "partido comunista",
    "revolucion democratica", "revolución democrática",

    # Political topics
    "reforma", "impuesto", "impuestos",
    "pension", "pensiones", "afp", "isapre", "isapres",
    "salario minimo", "sueldo minimo",
    "salario mínimo", "sueldo mínimo",
    "proyecto de ley", "votacion", "votación",
    "eleccion", "elección", "elecciones",
    "plebiscito", "primarias", "segunda vuelta",
    "carabineros", "pdi",
    "seguridad", "delincuencia", "crimen",
    "migracion", "migración", "migrantes", "inmigrantes",
    "litio", "royalty", "tributaria", "tributario",
    "acusacion constitucional", "acusación constitucional",
    "estado de excepcion", "estado de excepción",
    "ley de presupuesto", "presupuesto fiscal",
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def _extract_title(video: dict) -> str:
    title_data = video.get("title", {})
    if isinstance(title_data, str):
        return title_data

    runs = title_data.get("runs")
    if runs and isinstance(runs, list):
        return runs[0].get("text", "")

    simple = title_data.get("simpleText")
    if simple:
        return simple

    accessibility = title_data.get("accessibility", {})
    label = accessibility.get("accessibilityData", {}).get("label", "")
    if label:
        return label

    return ""


def _video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _matches_keywords(title: str, keywords: list[str]) -> list[str]:
    """
    @param title - video title
    @param keywords - political keyword list
    @returns list of matched keywords (empty if no match)
    """
    norm_title = _normalize(title)
    norm_title_no_accents = (
        norm_title
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u").replace("ü", "u")
        .replace("ñ", "n")
    )
    matched: list[str] = []
    for kw in keywords:
        norm_kw = _normalize(kw)
        norm_kw_no_accents = (
            norm_kw
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u").replace("ü", "u")
            .replace("ñ", "n")
        )
        if norm_kw in norm_title or norm_kw_no_accents in norm_title_no_accents:
            matched.append(kw)
    return matched


# ---------------------------------------------------------------------------
# Channel loading
# ---------------------------------------------------------------------------

def load_channels(filepath: str) -> list[str]:
    """
    @param filepath - path to channels text file
    """
    channels: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                channels.append(stripped)
    return channels


def _parse_channel_entry(entry: str) -> dict:
    """Determine whether entry is a URL, channel ID, or username and return
    the appropriate kwarg dict for scrapetube.get_channel()."""
    entry = entry.strip()

    if entry.startswith("http"):
        return {"channel_url": entry}

    if entry.startswith("UC") and len(entry) == 24:
        return {"channel_id": entry}

    cleaned = entry.lstrip("@")
    return {"channel_username": cleaned}


def load_extra_keywords(filepath: str) -> list[str]:
    """
    @param filepath - path to extra keywords file
    """
    keywords: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                keywords.append(stripped)
    return keywords


# ---------------------------------------------------------------------------
# Core scanning logic
# ---------------------------------------------------------------------------

def scan_channel(
    channel_entry: str,
    keywords: list[str],
    limit: Optional[int] = None,
    sleep: int = 1,
) -> tuple[list[dict], int]:
    """
    @param channel_entry - channel URL, ID, or username
    @param keywords - political keyword list
    @param limit - max *matched* political videos to collect (None = all)
    @param sleep - seconds between requests
    @returns (matched_videos, total_scanned)
    """
    kwargs = _parse_channel_entry(channel_entry)
    kwargs["sleep"] = sleep
    kwargs["content_type"] = "videos"

    matched_videos: list[dict] = []
    scanned = 0

    try:
        for video in scrapetube.get_channel(**kwargs):
            scanned += 1
            video_id = video.get("videoId", "")
            title = _extract_title(video)

            hits = _matches_keywords(title, keywords)
            if hits:
                matched_videos.append({
                    "video_id": video_id,
                    "url": _video_url(video_id),
                    "title": title,
                    "matched_keywords": hits,
                })
                if limit and len(matched_videos) >= limit:
                    break
    except Exception as exc:
        print(f"  [ERROR] Failed to scan {channel_entry}: {exc}", file=sys.stderr)

    return matched_videos, scanned


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def _load_existing_urls(filepath: str) -> set[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return {
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            }
    except FileNotFoundError:
        return set()


def write_output(
    matched: list[dict],
    output_path: str,
    append: bool = False,
) -> int:
    """
    @param matched - list of matched video dicts
    @param output_path - path to write URLs to
    @param append - if True, append and deduplicate; if False, overwrite
    @returns number of URLs written
    """
    existing: set[str] = set()
    if append:
        existing = _load_existing_urls(output_path)

    new_urls = [v["url"] for v in matched if v["url"] not in existing]
    unique_urls = list(dict.fromkeys(new_urls))

    mode = "a" if append else "w"
    with open(output_path, mode, encoding="utf-8") as f:
        if not append:
            f.write("# Political video URLs (auto-generated by fetch_political_videos.py)\n")
        for url in unique_urls:
            f.write(url + "\n")

    return len(unique_urls)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan YouTube channels for Chilean political videos",
    )
    parser.add_argument(
        "-i", "--input",
        default="channels.txt",
        help="Path to channels file (default: channels.txt)",
    )
    parser.add_argument(
        "-o", "--output",
        default="links.txt",
        help="Output file for matched video URLs (default: links.txt)",
    )
    parser.add_argument(
        "--keywords-file",
        default=None,
        help="Optional file with extra keywords, one per line",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to output instead of overwriting",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max political videos to collect per channel (default: no limit)",
    )
    parser.add_argument(
        "--sleep",
        type=int,
        default=1,
        help="Seconds between requests (default: 1)",
    )
    args = parser.parse_args()

    keywords = list(POLITICAL_KEYWORDS)
    if args.keywords_file:
        extra = load_extra_keywords(args.keywords_file)
        keywords.extend(extra)
        print(f"Loaded {len(extra)} extra keywords from {args.keywords_file}")

    channels = load_channels(args.input)
    if not channels:
        print(f"[ERROR] No channels found in {args.input}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("  Chilean Political Video Scanner")
    print("=" * 60)
    print(f"  Channels file: {args.input}")
    print(f"  Output:        {args.output}")
    print(f"  Keywords:      {len(keywords)}")
    print(f"  Channels:      {len(channels)}")
    print(f"  Limit/channel: {args.limit or 'no limit'}")
    print(f"  Append mode:   {args.append}")
    print("=" * 60)
    print()

    all_matched: list[dict] = []

    for idx, channel in enumerate(channels, start=1):
        print(f"[{idx}/{len(channels)}] Scanning: {channel}")
        matched, scanned = scan_channel(
            channel, keywords, limit=args.limit, sleep=args.sleep,
        )
        all_matched.extend(matched)
        print(f"  -> {len(matched)} political videos found (scanned {scanned} total)")

        if matched:
            sample = matched[0]
            kws = ", ".join(sample["matched_keywords"][:3])
            print(f"     e.g. \"{sample['title'][:60]}...\" [{kws}]")

    print(f"\nTotal: {len(all_matched)} political videos across {len(channels)} channels")

    written = write_output(all_matched, args.output, append=args.append)
    print(f"Wrote {written} URLs to {args.output}")


if __name__ == "__main__":
    main()
