from __future__ import annotations

import re


def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = t.replace("á", "a").replace("é", "e").replace("í", "i")
    t = t.replace("ó", "o").replace("ú", "u").replace("ü", "u")
    t = t.replace("ñ", "n")
    return t


# ---------------------------------------------------------------------------
# Chilean political leaning keyword lists
#
# Classification is based on typical discourse patterns:
#   - RIGHT-leaning commenters tend to attack left figures/concepts and
#     praise right-wing figures/policies.
#   - LEFT-leaning commenters tend to attack right figures/concepts and
#     praise left-wing figures/policies.
# ---------------------------------------------------------------------------

RIGHT_SIGNAL_KEYWORDS: list[str] = [
    # Attacks on the left (used overwhelmingly by right-leaning commenters)
    "comunista", "comunistas", "comunismo",
    "zurdo", "zurdos", "zurda", "zurdaje",
    "marxista", "marxistas", "marxismo",
    "castro-chavista", "chavista", "chavistas",
    "octubrista", "octubristas", "octubrismo",
    "socialismo", "socialistas fracasados",
    "zurdos de mierda", "rojos",
    "frenteamplista", "frenteamplistas",

    # Praise for right figures / policies
    "viva kast", "kast presidente", "arriba kast",
    "viva matthei", "matthei presidenta",
    "mano dura", "mano firme",
    "orden y seguridad", "orden publico",
    "chile libre", "libertad economica",
    "chile merece mas", "chile seguro",

    # Right-wing identity markers
    "patriota", "patriotas",
    "pro vida", "provida",
    "valores", "familia tradicional",

    # Anti-Boric / anti-FA
    "boris font", "boric comunista", "boric malo",
    "boric destruyo", "boric inutil",
    "bodeguero", "kkkast",  # ironic but search context matters
]

LEFT_SIGNAL_KEYWORDS: list[str] = [
    # Attacks on the right (used overwhelmingly by left-leaning commenters)
    "facho", "fachos", "facha", "fachas", "fachismo",
    "fascista", "fascistas", "fascismo",
    "pinochetista", "pinochetistas", "pinochet",
    "oligarca", "oligarcas", "oligarquia",
    "neoliberal", "neoliberales", "neoliberalismo",
    "empresarios ladrones", "patron de fundo",
    "milico", "milicos",
    "derechista", "derechistas",

    # Praise for left figures / policies
    "viva boric", "boric presidente", "arriba boric",
    "frente amplio", "apruebo dignidad",
    "justicia social", "derechos sociales",
    "dignidad", "pueblo unido",
    "no mas afp", "afp estafa",
    "salud publica", "educacion publica",

    # Left-wing identity markers
    "companero", "companera", "companeros",
    "clase trabajadora", "trabajadores",
    "lucha social", "resistencia",
    "asamblea constituyente",

    # Anti-Kast
    "kast fascista", "kast pinochetista",
    "kast dictador", "fuera kast",
]

_RIGHT_NORMALIZED = [_normalize(kw) for kw in RIGHT_SIGNAL_KEYWORDS]
_LEFT_NORMALIZED = [_normalize(kw) for kw in LEFT_SIGNAL_KEYWORDS]


def classify_political_leaning(text: str) -> tuple[str, int, int]:
    """
    @param text - comment text
    @returns (leaning, right_score, left_score) where leaning is 'right', 'left', or 'neutral'
    """
    norm = _normalize(text)

    right_hits = sum(1 for kw in _RIGHT_NORMALIZED if kw in norm)
    left_hits = sum(1 for kw in _LEFT_NORMALIZED if kw in norm)

    if right_hits > left_hits:
        return "right", right_hits, left_hits
    elif left_hits > right_hits:
        return "left", right_hits, left_hits
    else:
        return "neutral", right_hits, left_hits


def classify_all_comments(
    comments_by_video: dict[str, list[dict]],
) -> dict[str, dict]:
    """
    @param comments_by_video - dict mapping video URL to comment dicts
    @returns dict with per-video and overall stats
    """
    overall = {"left": 0, "right": 0, "neutral": 0, "total": 0}
    per_video: dict[str, dict] = {}

    for video_url, comments in comments_by_video.items():
        video_stats = {"left": 0, "right": 0, "neutral": 0, "total": len(comments)}
        for comment in comments:
            text = comment.get("text", "")
            leaning, _, _ = classify_political_leaning(text)
            video_stats[leaning] += 1
            overall[leaning] += 1
            overall["total"] += 1
        per_video[video_url] = video_stats

    return {"overall": overall, "per_video": per_video}
