"""Klien Gemini API dengan retry untuk error sementara."""

import time

import requests

from config import API_URL, GEMINI_API_KEY, MAX_RETRIES
from data.knowledge_base import knowledge_base

SYSTEM_INSTRUCTION = """
Kamu adalah asisten virtual yang membantu pengguna dan berfokus pada
layanan akademik Universitas Negeri Padang (UNP).

ATURAN MENJAWAB:
1. Pahami maksud pertanyaan dan jawab pertanyaan yang benar-benar diajukan.
2. Kamu boleh menjawab pertanyaan umum di luar akademik secara wajar,
   tetapi jangan mengaku memiliki pengalaman atau kehidupan manusia.
3. Untuk pertanyaan akademik UNP, gunakan konteks Knowledge Base jika relevan.
4. Jika pengguna meminta penjelasan kompleks, berikan jawaban terstruktur,
   bertahap, rinci, dan sertakan contoh bila membantu.
5. Jangan memberi jawaban satu kalimat untuk permintaan yang meminta
   penjelasan lengkap.
6. Jangan mengarang jadwal, biaya, nomor kontak, tanggal, prosedur resmi,
   atau kebijakan UNP yang tidak tersedia.
7. Jika informasi resmi tidak tersedia, bedakan informasi umum dari
   ketentuan resmi dan sarankan verifikasi melalui kanal resmi UNP.
8. Jangan mengalihkan semua pertanyaan ke layanan akademik jika pengguna
   sedang bertanya hal umum atau melakukan percakapan biasa.
9. Gunakan bahasa Indonesia yang natural, sopan, dan mudah dipahami.
10. Jika pertanyaan tidak jelas, tanyakan bagian yang perlu diperjelas.
"""

RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def get_relevant_knowledge(intent):
    if intent is None:
        return ""
    data = knowledge_base.get(intent, {})
    patterns = ", ".join(data.get("patterns", []))
    responses = " ".join(data.get("responses", []))
    return (
        f"Kategori: {intent}\n"
        f"Kata kunci terkait: {patterns}\n"
        f"Informasi lokal yang tersedia: {responses}"
    )


def ask_gemini(user_input, intent=None, timeout=45):
    if not GEMINI_API_KEY:
        print("[ERROR] API Key belum dimasukkan melalui GEMINI_API_KEY.")
        return None

    context = get_relevant_knowledge(intent)
    prompt = f"""
KONTEKS KNOWLEDGE BASE (gunakan hanya jika relevan):
{context if context else "Tidak ada informasi lokal yang cocok."}

PERTANYAAN PENGGUNA:
{user_input}
"""

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1200},
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )

            if response.status_code in RETRYABLE_STATUSES:
                print("[INFO] Gemini sementara tidak tersedia. HTTP:",
                      response.status_code)
                if attempt < MAX_RETRIES - 1:
                    delay = 2 ** (attempt + 1)
                    print(f"[INFO] Mencoba ulang dalam {delay} detik...")
                    time.sleep(delay)
                    continue
                return None

            if not response.ok:
                print("[ERROR] HTTP:", response.status_code)
                print("[DETAIL]", response.text[:1200])
                return None

            result = response.json()
            candidates = result.get("candidates", [])
            if not candidates:
                print("[ERROR] Gemini tidak mengembalikan jawaban.")
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            answer = " ".join(p["text"] for p in parts if "text" in p).strip()
            return answer or None

        except requests.exceptions.Timeout:
            print("[ERROR] Koneksi Gemini timeout.")
        except requests.exceptions.RequestException as error:
            print("[ERROR] Koneksi API:", error)
        except (ValueError, KeyError, TypeError) as error:
            print("[ERROR] Format respons tidak valid:", error)
            return None

        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** (attempt + 1))

    return None
