from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Optional


# ---------------------------------------------------------------------------
# Curated phrase / pattern lists for Chilean political YouTube
# ---------------------------------------------------------------------------

GENERIC_PRAISE_PHRASES: list[str] = [
    "buen video", "excelente", "muy bueno", "muy buen video",
    "grande", "saludos", "tiene toda la razon", "tiene razon",
    "el mejor", "la mejor", "los mejores", "genial", "increible",
    "que crack", "crack", "totalmente de acuerdo", "de acuerdo",
    "exacto", "exactamente", "verdad", "pura verdad", "asi es",
    "apoyo total", "100%", "bien dicho", "muy bien dicho",
    "felicitaciones", "bravo", "que grande", "impecable",
    "admirable", "extraordinario", "fantastico", "buenisimo",
    "sigan asi", "exito", "bendiciones", "dios lo bendiga",
]

GENERIC_ATTACK_WORDS: set[str] = {
    "comunista", "comunistas", "facho", "fachos", "fascista", "fascistas",
    "vendido", "vendidos", "vendida", "vendidas",
    "corrupto", "corruptos", "corrupta", "corruptas",
    "payaso", "payasos", "payasa", "payasas",
    "ignorante", "ignorantes", "basura", "basuras",
    "asco", "asqueroso", "asquerosa",
    "ladron", "ladrones", "ladrona", "ladronas",
    "mentiroso", "mentirosos", "mentirosa", "mentirosas",
    "sinverguenza", "hipocrita", "hipocritas",
    "mediocre", "mediocres", "inutil", "inutiles",
    "traidor", "traidores", "traidora", "traidoras",
    "delincuente", "delincuentes", "narco", "narcos",
    "rata", "ratas", "vayanse", "fuera",
    "estupido", "estupida", "estupidos", "estupidas",
    "idiota", "idiotas", "imbecil", "imbeciles",
    "aweonao", "aweonado", "aweonada", "weon", "weona",
    "ctm", "csm", "conchetumare", "conchetumadre",
    "mierda", "porqueria",
}

GENERIC_ATTACK_PHRASES: list[str] = [
    "que asco", "dan asco", "vayanse a la mierda",
    "fuera comunistas", "fuera fachos", "mueran todos",
    "pais de mierda", "gobierno de mierda",
    "son todos iguales", "todos corruptos",
    "que verguenza", "verguenza ajena", "que vergüenza",
]

SPAM_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
AUTO_USERNAME_PATTERN = re.compile(r"^@?user-[a-z0-9]{4,}$", re.IGNORECASE)
EXCESSIVE_DIGITS_PATTERN = re.compile(r"\d{5,}")
RANDOM_STRING_PATTERN = re.compile(r"^[a-z0-9]{10,}$")

_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f6ff"
    "\U0001f1e0-\U0001f1ff"
    "\U00002702-\U000027b0"
    "\U000024c2-\U0001f251"
    "]+",
    flags=re.UNICODE,
)


def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = t.translate(str.maketrans("áéíóúüñ", "aeiouun"))
    return t


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[a-záéíóúüñ]+", text.lower()))


# ---------------------------------------------------------------------------
# Individual signal scorers
# ---------------------------------------------------------------------------

def _score_username(author: str, channel: str) -> tuple[float, list[str]]:
    score = 0.0
    flags: list[str] = []
    name = (author or "").strip()

    if AUTO_USERNAME_PATTERN.match(name):
        score += 0.15
        flags.append("generic_username")

    if EXCESSIVE_DIGITS_PATTERN.search(name):
        score += 0.10
        flags.append("excessive_digits_in_name")

    if not channel or channel.strip() == "":
        score += 0.05
        flags.append("blank_channel_id")

    clean_name = re.sub(r"[^a-z0-9]", "", name.lower())
    if RANDOM_STRING_PATTERN.match(clean_name) and " " not in name:
        score += 0.05
        flags.append("random_string_name")

    return score, flags


def _score_positive_astroturfing(text: str) -> tuple[float, list[str]]:
    score = 0.0
    flags: list[str] = []
    norm = _normalize(text)

    for phrase in GENERIC_PRAISE_PHRASES:
        np = _normalize(phrase)
        if norm == np or (len(norm) < len(np) + 15 and np in norm):
            score += 0.20
            flags.append("generic_praise")
            break

    if SPAM_URL_PATTERN.search(text):
        score += 0.10
        flags.append("spam_url")

    words = re.findall(r"[a-záéíóúüñ]+", norm)
    meaningful = [w for w in words if len(w) > 2]
    if len(meaningful) < 3 and not flags:
        score += 0.10
        flags.append("very_short_generic")

    return score, flags


def _score_negative_attack(text: str) -> tuple[float, list[str]]:
    score = 0.0
    flags: list[str] = []
    norm = _normalize(text)

    words = re.findall(r"[a-záéíóúüñ]+", norm)
    if words:
        attack_count = sum(1 for w in words if w in GENERIC_ATTACK_WORDS)
        ratio = attack_count / len(words)
        if ratio > 0.5 or (len(words) <= 3 and attack_count >= 1 and len(words) == attack_count):
            score += 0.20
            flags.append("political_attack")

    for phrase in GENERIC_ATTACK_PHRASES:
        if _normalize(phrase) in norm:
            score += 0.20
            flags.append("attack_phrase")
            break

    alpha_chars = [c for c in text if c.isalpha()]
    if len(alpha_chars) > 10:
        upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if upper_ratio > 0.80:
            score += 0.10
            flags.append("all_caps")

    repeated = re.findall(r"(.)\1{4,}", text)
    if repeated:
        score += 0.10
        flags.append("repetitive_spam")

    emoji_matches = _EMOJI_RE.findall(text)
    total_emoji_chars = sum(len(m) for m in emoji_matches)
    if total_emoji_chars > 10:
        score += 0.10
        flags.append("emoji_flood")

    return score, flags


def _score_propaganda(
    text: str,
    text_to_authors: dict[str, set[str]],
) -> tuple[float, list[str]]:
    """
    @param text - comment text
    @param text_to_authors - map of normalized text -> set of distinct authors who posted it
    """
    score = 0.0
    flags: list[str] = []
    norm = _normalize(text)

    if norm in text_to_authors and len(text_to_authors[norm]) > 1:
        score += 0.20
        flags.append("copypaste_slogan")

    words = re.findall(r"[a-záéíóúüñ]+", norm)
    if len(words) > 15:
        has_colloquial = any(
            w in norm
            for w in ["weon", "po", "cachai", "wea", "onda", "poh", "xd", "jaja"]
        )
        has_contractions = any(w in norm for w in ["q", "pa", "tb", "x", "noo", "sii"])
        if not has_colloquial and not has_contractions:
            score += 0.10
            flags.append("formal_tone")

    return score, flags


# ---------------------------------------------------------------------------
# Cross-video behavioural analysis (pre-computed lookups)
# ---------------------------------------------------------------------------

def _build_cross_video_indexes(
    comments_by_video: dict[str, list[dict]],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, set[str]], dict[str, dict[str, list[str]]]]:
    """
    @returns (author_to_videos, author_to_texts, text_to_authors, author_to_video_texts)
    """
    author_to_videos: dict[str, list[str]] = defaultdict(list)
    author_to_texts: dict[str, list[str]] = defaultdict(list)
    text_to_authors: dict[str, set[str]] = defaultdict(set)
    author_to_video_texts: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for video_url, comments in comments_by_video.items():
        for c in comments:
            author = c.get("author", "")
            text = _normalize(c.get("text", ""))
            author_to_videos[author].append(video_url)
            author_to_texts[author].append(text)
            text_to_authors[text].add(author)
            author_to_video_texts[author][video_url].append(text)

    return author_to_videos, author_to_texts, text_to_authors, author_to_video_texts


def _score_cross_video(
    author: str,
    text: str,
    video_url: str,
    author_to_videos: dict[str, list[str]],
    author_to_texts: dict[str, list[str]],
    author_to_video_texts: dict[str, dict[str, list[str]]],
) -> tuple[float, list[str]]:
    score = 0.0
    flags: list[str] = []

    unique_videos = set(author_to_videos.get(author, []))
    if len(unique_videos) >= 2:
        score += 0.15
        flags.append("appears_in_many_videos")
    if len(unique_videos) >= 5:
        score += 0.10
        flags.append("appears_in_5plus_videos")

    norm = _normalize(text)
    ws = _word_set(text)
    video_texts = author_to_video_texts.get(author, {})
    for other_url, other_texts in video_texts.items():
        if other_url == video_url:
            continue
        for other_text in other_texts:
            if other_text == norm:
                score += 0.25
                flags.append("exact_cross_video_duplicate")
                break
            if _jaccard(ws, _word_set(other_text)) > 0.6:
                score += 0.20
                flags.append("cross_video_duplicate")
                break
        if flags:
            break

    return score, flags


# ---------------------------------------------------------------------------
# Category classifier
# ---------------------------------------------------------------------------

_CATEGORY_FLAG_MAP: dict[str, str] = {
    "generic_praise": "astroturfing",
    "very_short_generic": "astroturfing",
    "political_attack": "attack_bot",
    "attack_phrase": "attack_bot",
    "all_caps": "attack_bot",
    "repetitive_spam": "attack_bot",
    "emoji_flood": "attack_bot",
    "copypaste_slogan": "propaganda",
    "formal_tone": "propaganda",
    "spam_url": "spam",
    "generic_username": "spam",
    "excessive_digits_in_name": "spam",
    "blank_channel_id": "spam",
    "random_string_name": "spam",
    "appears_in_many_videos": "propaganda",
    "appears_in_5plus_videos": "propaganda",
    "cross_video_duplicate": "propaganda",
    "exact_cross_video_duplicate": "propaganda",
}


def _classify_category(flags: list[str]) -> str:
    if not flags:
        return ""
    counts: Counter[str] = Counter()
    for f in flags:
        cat = _CATEGORY_FLAG_MAP.get(f, "spam")
        counts[cat] += 1

    top = counts.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "mixed"
    return top[0][0]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_bots(
    comments_by_video: dict[str, list[dict]],
    threshold: float = 0.5,
) -> list[dict]:
    """
    @param comments_by_video - dict mapping video URL to comment dicts
    @param threshold - bot score threshold (0.0-1.0)
    @returns list of enriched comment dicts with bot_score, flags, etc.
    """
    author_to_videos, author_to_texts, text_to_authors, author_to_video_texts = (
        _build_cross_video_indexes(comments_by_video)
    )

    results: list[dict] = []

    for video_url, comments in comments_by_video.items():
        for comment in comments:
            author = comment.get("author", "")
            channel = comment.get("channel", "")
            text = comment.get("text", "")

            total_score = 0.0
            all_flags: list[str] = []

            s, f = _score_username(author, channel)
            total_score += s
            all_flags.extend(f)

            s, f = _score_positive_astroturfing(text)
            total_score += s
            all_flags.extend(f)

            s, f = _score_negative_attack(text)
            total_score += s
            all_flags.extend(f)

            s, f = _score_propaganda(text, text_to_authors)
            total_score += s
            all_flags.extend(f)

            s, f = _score_cross_video(
                author, text, video_url,
                author_to_videos, author_to_texts, author_to_video_texts,
            )
            total_score += s
            all_flags.extend(f)

            capped_score = min(total_score, 1.0)
            is_bot = capped_score >= threshold
            category = _classify_category(all_flags) if is_bot else ""

            results.append({
                "video_url": video_url,
                "author": author,
                "channel_id": channel,
                "comment_text": text,
                "votes": comment.get("votes", 0),
                "time": comment.get("time", ""),
                "bot_score": round(capped_score, 3),
                "bot_category": category,
                "flags": "|".join(dict.fromkeys(all_flags)),
                "is_suspected_bot": is_bot,
            })

    return results
