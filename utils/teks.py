"""Utilitas pemrosesan teks: preprocessing dan tokenisasi bermakna."""

import re

STOPWORDS = {
    "saya", "aku", "anda", "kamu", "yang", "dan", "atau", "di", "ke",
    "dari", "untuk", "dengan", "pada", "itu", "ini", "apa", "apakah",
    "bagaimana", "kenapa", "mengapa", "berapa", "dimana", "kapan",
    "tolong", "mohon", "bisa", "kah", "ya", "dong", "sih", "nya",
    "ingin", "mau", "tentang", "jelaskan", "jelaskanlah",
}


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def meaningful_tokens(text):
    return [
        token for token in preprocess(text).split()
        if token not in STOPWORDS and len(token) > 2
    ]
