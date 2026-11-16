"""
CHATBOT LAYANAN AKADEMIK UNP
Rule-Based + TF-IDF + Cosine Similarity + Gemini API

Jalankan dari folder ini:  python main.py
"""

from chatbot import get_response_hybrid
from config import GEMINI_MODEL
from data.knowledge_base import knowledge_base
from evaluasi import evaluate_models
from services.gemini import ask_gemini
from utils.teks import preprocess


def test_gemini():
    print("\n[INFO] Model:", GEMINI_MODEL)
    answer = ask_gemini(
        "Jelaskan dalam dua kalimat apa fungsi chatbot akademik.",
        timeout=45,
    )
    if answer:
        print("\n[BERHASIL] Gemini memberikan respons:")
        print(answer)
    else:
        print("\n[GAGAL] Periksa API Key, nama model, kuota, "
              "koneksi internet, dan detail error di atas.")


def run_chatbot():
    print("\n" + "=" * 58)
    print("CHATBOT LAYANAN AKADEMIK UNP")
    print("Rule-Based + TF-IDF + Gemini API")
    print("CATATAN: jadwal dan beberapa angka adalah DATA DUMMY untuk demonstrasi.")
    print("=" * 58)
    print("Ketik 'keluar' untuk kembali ke menu.\n")

    while True:
        try:
            user_input = input("Anda: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBot: Sesi chatbot berakhir.")
            break

        if not user_input:
            print("Bot: Silakan masukkan pertanyaan.\n")
            continue

        if preprocess(user_input) in {"keluar", "exit", "quit"}:
            print("Bot:", knowledge_base["goodbye"]["responses"][0])
            break

        print("Bot:", get_response_hybrid(user_input))
        print()


def main():
    while True:
        print("\n" + "=" * 44)
        print(" CHATBOT LAYANAN AKADEMIK UNP")
        print("=" * 44)
        print("1. Jalankan chatbot")
        print("2. Evaluasi Rule-Based vs TF-IDF")
        print("3. Tes koneksi Gemini API")
        print("4. Keluar")

        choice = input("Pilih menu (1-4): ").strip()

        if choice == "1":
            run_chatbot()
        elif choice == "2":
            evaluate_models()
        elif choice == "3":
            test_gemini()
        elif choice == "4":
            print("Program selesai.")
            break
        else:
            print("Pilihan tidak valid. Masukkan angka 1 sampai 4.")


if __name__ == "__main__":
    main()
