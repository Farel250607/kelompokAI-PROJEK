"""Klasifikasi intent: Rule-Based dan TF-IDF + Cosine Similarity."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import SIMILARITY_THRESHOLD
from data.knowledge_base import knowledge_base
from data.training_data import training_examples
from utils.teks import meaningful_tokens, preprocess


# ------------------------------------------------------------
# RULE-BASED (PEMBANDING EKSPERIMEN)
# ------------------------------------------------------------
def match_intent_rule_based(user_input):
    processed = preprocess(user_input)
    for intent, data in knowledge_base.items():
        for pattern in data["patterns"]:
            pattern_clean = preprocess(pattern)
            if pattern_clean and pattern_clean in processed:
                return intent
    return None


# ------------------------------------------------------------
# MODEL TF-IDF
# ------------------------------------------------------------
_corpus = []
_labels = []
for _intent, _examples in training_examples.items():
    for _example in _examples:
        _corpus.append(preprocess(_example))
        _labels.append(_intent)

_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
_tfidf_matrix = _vectorizer.fit_transform(_corpus)

# Kata bermakna yang memang muncul dalam contoh training.
TRAINING_VOCAB = set(_vectorizer.get_feature_names_out())


def match_intent_tfidf(user_input, threshold=SIMILARITY_THRESHOLD):
    tokens = meaningful_tokens(user_input)

    # Jangan klasifikasikan pesan terlalu pendek atau hanya kata umum.
    if len(tokens) < 1:
        return None, 0.0

    # Hindari false positive jika tidak ada kata bermakna yang dikenal model.
    if not any(token in TRAINING_VOCAB for token in tokens):
        return None, 0.0

    user_vector = _vectorizer.transform([preprocess(user_input)])
    scores = cosine_similarity(user_vector, _tfidf_matrix)[0]

    best_index = scores.argmax()
    best_score = float(scores[best_index])
    best_intent = _labels[best_index]

    if best_score >= threshold:
        return best_intent, best_score
    return None, best_score


# ------------------------------------------------------------
# VALIDASI DAN ROUTING PERTANYAAN
# ------------------------------------------------------------
def is_incomplete_question(user_input):
    tokens = meaningful_tokens(user_input)
    normalized = preprocess(user_input)
    short_messages = {
        "apa", "berapa", "dimana", "kapan", "kenapa", "mengapa",
        "bagaimana", "siapa", "itu", "ini", "yang", "apakah",
    }
    return len(tokens) == 0 or normalized in short_messages


def is_complex_question(user_input):
    text = preprocess(user_input)
    complex_phrases = [
        "jelaskan", "analisis", "bandingkan", "uraikan",
        "secara rinci", "secara detail", "langkah langkah",
        "dari awal sampai selesai", "apa dampak", "apa pengaruh",
        "mengapa hal", "bagaimana prosedur", "bagaimana proses",
        "strategi", "evaluasi", "berikan alasan", "beserta contoh",
        "kelebihan dan kekurangan", "perbedaan antara",
    ]
    return any(phrase in text for phrase in complex_phrases)
