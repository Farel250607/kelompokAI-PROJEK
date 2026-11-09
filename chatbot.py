import re
import random
import google.generativeai as genai

# =========================
# API GEMINI
# =========================

API_KEY = "AQ.Ab8RN6KKjmbtZ-mYqcYq5_dA28u_qSoV4Crr8bJWBGLoDb-5Hw"

genai.configure(api_key=API_KEY)

# Model cepat
model = genai.GenerativeModel("models/gemini-flash-lite-latest")

# =========================
# KNOWLEDGE BASE
# =========================

knowledge_base = {
    "greeting": {
        "patterns": ["halo", "hai", "selamat pagi", "selamat siang"],
        "responses": [
            "Halo! Ada yang bisa saya bantu terkait informasi kampus?"
        ]
    },

    "jadwal_kuliah": {
        "patterns": [
            "jadwal kuliah",
            "jadwal kelas",
            "kapan kuliah"
        ],
        "responses": [
            "Jadwal kuliah dapat dilihat pada Portal Akademik."
        ]
    },

    "lokasi_kampus": {
        "patterns": [
            "lokasi kampus",
            "alamat kampus",
            "dimana kampus"
        ],
        "responses": [
            "Kampus berlokasi di Jl. Pendidikan No. 1."
        ]
    },

    "kontak_admin": {
        "patterns": [
            "kontak admin",
            "hubungi admin",
            "nomor admin"
        ],
        "responses": [
            "Admin akademik dapat dihubungi melalui admin@kampus.ac.id"
        ]
    },

    "terima_kasih": {
        "patterns": [
            "terima kasih",
            "makasih",
            "thanks"
        ],
        "responses": [
            "Sama-sama! Senang bisa membantu."
        ]
    },

    "goodbye": {
        "patterns": [
            "bye",
            "keluar",
            "exit",
            "sampai jumpa"
        ],
        "responses": [
            "Sampai jumpa! Semoga harimu menyenangkan."
        ]
    }
}

# =========================
# PREPROCESSING
# =========================

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# =========================
# INTENT MATCHING
# =========================

def match_intent(user_input):

    processed = preprocess(user_input)

    for intent, data in knowledge_base.items():

        for pattern in data["patterns"]:

            if pattern in processed:
                return intent

    return None

# =========================
# RESPONSE LOCAL
# =========================

def generate_response(intent):

    if intent is None:
        return None

    return random.choice(
        knowledge_base[intent]["responses"]
    )

# =========================
# GEMINI FALLBACK
# =========================

def ask_gemini(question):

    try:

        print("Bot sedang berpikir...")

        prompt = f"""
        Kamu adalah chatbot informasi kampus.

        Jawab singkat, jelas dan sopan.

        Pertanyaan:
        {question}
        """

        response = model.generate_content(
            prompt,
            request_options={"timeout": 20}
        )

        return response.text

    except Exception as e:
        return f"Error Gemini: {e}"

# =========================
# HYBRID RESPONSE
# =========================

def get_response(user_input):

    intent = match_intent(user_input)

    if intent is not None:
        return generate_response(intent)

    return ask_gemini(user_input)

# =========================
# CHATBOT
# =========================

def run_chatbot():

    print("=" * 50)
    print("CHATBOT FAQ KAMPUS + GEMINI")
    print("Ketik 'keluar' untuk berhenti")
    print("=" * 50)

    while True:

        user_input = input("\nAnda: ")

        if user_input.lower() == "keluar":

            print(
                "Bot :",
                knowledge_base["goodbye"]["responses"][0]
            )

            break

        response = get_response(user_input)

        print("\nBot :", response)

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    run_chatbot()