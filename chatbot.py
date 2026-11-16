"""Hybrid chatbot: database lokal -> Knowledge Base (TF-IDF) -> Gemini API."""

import random

from config import FALLBACK_RESPONSE
from data.knowledge_base import knowledge_base
from services.gemini import ask_gemini
from services.intent import (
    is_complex_question, is_incomplete_question, match_intent_tfidf,
)
from services.pencarian_db import PENCARIAN_DATABASE
from utils.teks import preprocess


def get_response_hybrid(user_input):
    normalized = preprocess(user_input)

    # Pencarian database lokal terstruktur sebelum klasifikasi intent.
    for pencarian in PENCARIAN_DATABASE:
        hasil_database = pencarian(user_input)
        if hasil_database:
            print("[INFO] Data ditemukan pada database akademik dummy.")
            return hasil_database

    # Respons percakapan sederhana yang pasti dan tidak perlu API.
    if normalized in {"halo", "hai", "hi", "hello", "assalamualaikum"}:
        return knowledge_base["greeting"]["responses"][0]

    if normalized in {"terima kasih", "makasih", "thanks"}:
        return knowledge_base["terima_kasih"]["responses"][0]

    if is_incomplete_question(user_input):
        return (
            "Pertanyaanmu masih terlalu singkat untuk saya pahami. "
            "Bisa jelaskan lebih lengkap apa yang ingin kamu tanyakan?"
        )

    intent, score = match_intent_tfidf(user_input)
    print("[TF-IDF] Intent:", intent)
    print("[TF-IDF] Similarity: {:.3f}".format(score))

    # Pertanyaan kompleks diarahkan ke Gemini walaupun intent ditemukan.
    if is_complex_question(user_input):
        print("[INFO] Pertanyaan terdeteksi kompleks.")
        print("[INFO] Mengirim pertanyaan dan konteks Knowledge Base ke Gemini...")
        answer = ask_gemini(user_input, intent)
        if answer:
            print("[INFO] Jawaban dari Gemini.")
            return answer
        print("[INFO] Gemini gagal, menggunakan informasi lokal jika tersedia.")

        if intent is not None:
            return (
                knowledge_base[intent]["responses"][0]
                + "\n\nCatatan: layanan penjelasan AI sedang tidak tersedia. "
                "Jawaban di atas hanya informasi ringkas."
            )
        return FALLBACK_RESPONSE

    # Intent sederhana yang cocok dijawab langsung oleh Knowledge Base.
    if intent is not None:
        print("[INFO] Menggunakan Knowledge Base lokal.")
        return random.choice(knowledge_base[intent]["responses"])

    # Tidak cocok dengan Knowledge Base: coba Gemini.
    print("[INFO] Pertanyaan tidak cocok dengan Knowledge Base.")
    print("[INFO] Mencoba Gemini API...")
    answer = ask_gemini(user_input)

    if answer:
        print("[INFO] Jawaban dari Gemini.")
        return answer

    print("[INFO] Menggunakan fallback.")
    return FALLBACK_RESPONSE
