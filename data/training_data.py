"""Data training untuk model TF-IDF + Cosine Similarity."""

from data.knowledge_base import knowledge_base

training_examples = {
    "greeting": [
        "halo", "hai", "selamat pagi", "selamat siang",
        "selamat sore", "assalamualaikum", "permisi",
    ],
    "jadwal_kuliah": [
        "jadwal kuliah", "jadwal kelas", "kapan kuliah",
        "jam berapa kuliah", "jadwal perkuliahan",
        "kapan jadwal kuliah semester ini",
        "saya ingin melihat jadwal kuliah", "jadwal semester",
    ],
    "krs": [
        "apa itu KRS", "kartu rencana studi",
        "bagaimana cara mengisi KRS", "kapan pengisian KRS",
        "saya ingin mengambil mata kuliah", "ubah KRS",
    ],
    "khs": [
        "apa itu KHS", "kartu hasil studi", "lihat nilai semester",
        "bagaimana melihat nilai", "nilai mata kuliah belum keluar",
    ],
    "ukt": [
        "apa itu UKT", "uang kuliah tunggal", "cara bayar UKT",
        "jadwal pembayaran kuliah", "keringanan UKT",
        "permohonan penurunan UKT",
    ],
    "kalender_akademik": [
        "kalender akademik", "kapan awal semester",
        "jadwal UTS", "jadwal UAS", "kapan libur semester",
        "jadwal ujian semester",
    ],
    "cuti_akademik": [
        "cara mengajukan cuti kuliah", "cuti akademik",
        "syarat cuti kuliah", "izin tidak kuliah satu semester",
    ],
    "lokasi_kampus": [
        "lokasi kampus", "alamat kampus", "dimana kampus",
        "dimana lokasi UNP", "alamat Universitas Negeri Padang",
        "cara menuju kampus UNP",
    ],
    "kontak_admin": [
        "kontak admin", "hubungi admin", "nomor admin",
        "kontak bagian akademik", "email akademik",
        "cara menghubungi program studi",
    ],
    "wisuda": [
        "cara daftar wisuda", "syarat wisuda",
        "jadwal wisuda", "pendaftaran wisuda",
        "dokumen untuk wisuda",
    ],
    "terima_kasih": [
        "terima kasih", "makasih", "thanks",
        "terima kasih banyak", "terima kasih atas bantuan",
    ],
    "goodbye": [
        "bye", "sampai jumpa", "keluar", "exit",
        "selamat tinggal", "saya mau pergi",
    ],
}

# Variasi pertanyaan tambahan.
training_examples["jadwal_kuliah"].extend([
    "jadwal kuliah hari senin", "mata kuliah hari selasa jam berapa",
    "hari rabu ada kelas apa", "jadwal kuliah kelas A",
    "jadwal matematika teknik", "kuliah di ruang A1.2",
    "jam berapa praktikum komputer", "jadwal kelas semester ini",
    "tolong tampilkan jadwal perkuliahan", "hari jumat ada kuliah atau tidak",
])
training_examples.setdefault("ruang_kuliah", []).extend([
    "dimana ruang matematika teknik", "fisika dasar di ruangan berapa",
    "lokasi lab komputer", "kelas saya di gedung mana",
])

# Semua pola Knowledge Base otomatis menjadi contoh training.
for _intent, _data in knowledge_base.items():
    training_examples.setdefault(_intent, []).extend(_data.get("patterns", []))
