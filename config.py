"""Konfigurasi global chatbot (API key, model, threshold, fallback)."""

import os

from dotenv import load_dotenv

load_dotenv()  # membaca GEMINI_API_KEY dari file .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

SIMILARITY_THRESHOLD = 0.42
MAX_RETRIES = 3
FALLBACK_RESPONSE = (
    "Maaf, layanan AI sedang tidak tersedia. Silakan coba lagi atau "
    "hubungi bagian akademik UNP untuk informasi resmi."
)
