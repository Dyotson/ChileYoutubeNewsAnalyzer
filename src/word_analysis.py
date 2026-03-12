from __future__ import annotations

import re
import string
from collections import Counter

import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

SPANISH_STOPWORDS: set[str] = set(stopwords.words("spanish"))

YOUTUBE_NOISE_WORDS: set[str] = {
    "jajaja", "jajajaja", "jajajajaja", "jaja", "ja",
    "xd", "xdd", "xddd", "xdddd",
    "like", "likes", "subscribe", "suscribete",
    "video", "canal", "https", "http", "www", "com",
    "youtube", "watch", "si", "no", "mas", "solo",
    "ver", "hace", "van", "va", "ser", "tan", "puede",
    "asi", "aca", "alla", "aqui", "ahora", "bien",
    "mal", "todo", "toda", "todos", "todas", "uno",
    "una", "unos", "unas", "algo", "nada", "nadie",
    "cada", "otro", "otra", "otros", "otras",
    "mismo", "misma", "mismos", "mismas",
    "donde", "cuando", "como", "porque", "pero",
    "sino", "aunque", "pues", "ya", "aun", "vez",
    "siempre", "nunca", "tambien", "ademas",
    "despues", "antes", "hoy", "dia", "año",
    "gente", "cosa", "cosas", "parte",
}

ALL_STOPWORDS: set[str] = SPANISH_STOPWORDS | YOUTUBE_NOISE_WORDS

_EMOJI_PATTERN = re.compile(
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


def _clean_text(text: str) -> str:
    text = text.lower()
    text = _EMOJI_PATTERN.sub(" ", text)
    text = text.translate(str.maketrans("áéíóúüñ", "aeiouun"))
    text = re.sub(r"https?://\S+", " ", text)
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    text = re.sub(r"\d+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    """
    @param text - raw comment text
    """
    cleaned = _clean_text(text)
    tokens = cleaned.split()
    return [t for t in tokens if len(t) > 1 and t not in ALL_STOPWORDS]


def compute_word_frequency(
    comments_by_video: dict[str, list[dict]],
) -> list[tuple[int, str, int]]:
    """
    @param comments_by_video - dict mapping video URL to list of comment dicts
    @returns ranked list of (rank, word, count)
    """
    counter: Counter[str] = Counter()

    for comments in comments_by_video.values():
        for comment in comments:
            tokens = tokenize(comment.get("text", ""))
            counter.update(tokens)

    ranked: list[tuple[int, str, int]] = []
    for rank, (word, count) in enumerate(counter.most_common(), start=1):
        ranked.append((rank, word, count))

    return ranked
