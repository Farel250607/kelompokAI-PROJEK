"""Evaluasi akurasi Rule-Based vs TF-IDF + Cosine Similarity."""

from services.intent import match_intent_rule_based, match_intent_tfidf

test_cases = [
    ("halo kak", "greeting"),
    ("kapan jadwal kuliah semester ini", "jadwal_kuliah"),
    ("bagaimana cara mengisi KRS", "krs"),
    ("saya ingin melihat nilai semester", "khs"),
    ("bagaimana cara bayar UKT", "ukt"),
    ("kapan jadwal UAS", "kalender_akademik"),
    ("bagaimana mengajukan cuti kuliah", "cuti_akademik"),
    ("dimana lokasi kampus UNP", "lokasi_kampus"),
    ("cara menghubungi bagian akademik", "kontak_admin"),
    ("apa syarat pendaftaran wisuda", "wisuda"),
    ("terima kasih banyak", "terima_kasih"),
    ("sampai jumpa", "goodbye"),
    ("berapa suhu matahari", None),
]


def evaluate_models():
    correct_rule = 0
    correct_tfidf = 0

    print("\n" + "=" * 58)
    print("EVALUASI RULE-BASED VS TF-IDF + COSINE SIMILARITY")
    print("=" * 58)

    for question, expected in test_cases:
        rule_result = match_intent_rule_based(question)
        tfidf_result, score = match_intent_tfidf(question)

        correct_rule += (rule_result == expected)
        correct_tfidf += (tfidf_result == expected)

        print("\nPertanyaan :", question)
        print("Expected   :", expected)
        print("Rule-Based :", rule_result)
        print("TF-IDF     :", tfidf_result)
        print("Similarity : {:.3f}".format(score))

    total = len(test_cases)
    print("\n" + "=" * 58)
    print("HASIL AKURASI")
    print("=" * 58)
    print("Rule-Based : {:.1f}% ({}/{})".format(
        correct_rule / total * 100, correct_rule, total))
    print("TF-IDF     : {:.1f}% ({}/{})".format(
        correct_tfidf / total * 100, correct_tfidf, total))
    print(
        "\nCatatan: akurasi dihitung hanya dari test_cases ini. "
        "Tambahkan data uji untuk evaluasi yang lebih representatif."
    )
