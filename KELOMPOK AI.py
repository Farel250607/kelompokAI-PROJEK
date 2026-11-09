import os
import re
import time
import random
import requests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CHATBOT LAYANAN AKADEMIK UNP
# Rule-Based + TF-IDF + Cosine Similarity + Gemini API
# ============================================================

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

knowledge_base = {

    "greeting": {

        "patterns": [

            "halo", "hai", "selamat pagi", "selamat siang",

            "selamat sore", "assalamualaikum", "permisi"

        ],

        "responses": [

            "Halo! Saya Chatbot Layanan Akademik UNP. Ada yang bisa saya bantu?"

        ]

    },

    "jadwal_kuliah": {

        "patterns": [

            "jadwal kuliah", "jadwal kelas", "kapan kuliah",

            "jam berapa kuliah", "jadwal perkuliahan"

        ],

        "responses": [

            "CONTOH DATA DUMMY JADWAL KULIAH (BUKAN JADWAL RESMI UNP):\n"
            "Senin: 08.00-09.40 Matematika Teknik (Ruang A1.2); 10.00-11.40 Bahasa Indonesia (Ruang A1.2).\n"
            "Selasa: 08.00-09.40 Gambar Teknik (Lab Gambar); 13.00-14.40 Fisika Dasar (Ruang B2.1).\n"
            "Rabu: 09.00-10.40 Material Teknik (Ruang A2.3); 13.00-15.30 Praktikum Komputer (Lab Komputer).\n"
            "Kamis: 08.00-09.40 Matematika Teknik (Ruang A1.2); 10.00-11.40 Mekanika Teknik (Ruang B1.1).\n"
            "Jumat: 08.00-09.40 Pendidikan Pancasila (Ruang A1.2).\n"
            "Data ini hanya contoh untuk demonstrasi chatbot. Jadwal sebenarnya harus dilihat di Portal Akademik UNP."

        ]

    },

    "krs": {

        "patterns": [

            "krs", "kartu rencana studi", "isi krs",

            "pengisian krs", "ubah krs", "ambil mata kuliah"

        ],

        "responses": [

            "KRS (Kartu Rencana Studi) berisi mata kuliah yang direncanakan untuk diambil pada semester berjalan. Periksa kalender akademik dan portal akademik UNP untuk periode pengisian. Konsultasikan rencana studi dengan dosen PA."

        ]

    },

    "khs": {

        "patterns": [

            "khs", "kartu hasil studi", "nilai semester",

            "lihat nilai", "hasil studi", "nilai mata kuliah"

        ],

        "responses": [

            "KHS (Kartu Hasil Studi) menampilkan hasil studi pada semester tertentu. Periksa portal akademik mahasiswa UNP. Jika nilai belum muncul atau tidak sesuai, hubungi dosen pengampu atau program studi."

        ]

    },

    "ukt": {

        "patterns": [

            "ukt", "uang kuliah tunggal", "pembayaran kuliah",

            "bayar kuliah", "tagihan kuliah", "keringanan ukt",

            "penurunan ukt", "cicilan ukt"

        ],

        "responses": [

            "Informasi tagihan, jadwal pembayaran, dan permohonan terkait UKT dapat berubah setiap periode. Periksa pengumuman resmi UNP atau hubungi bagian keuangan/layanan mahasiswa untuk informasi yang berlaku."

        ]

    },

    "kalender_akademik": {

        "patterns": [

            "kalender akademik", "kalender kuliah", "awal semester",

            "akhir semester", "jadwal ujian", "uts", "uas",

            "libur semester"

        ],

        "responses": [

            "Tanggal awal semester, UTS, UAS, dan kegiatan akademik lainnya mengikuti kalender akademik resmi UNP. Gunakan kalender untuk tahun akademik yang sedang berjalan."

        ]

    },

    "cuti_akademik": {

        "patterns": [

            "cuti kuliah", "cuti akademik", "izin tidak kuliah",

            "berhenti sementara", "pengajuan cuti"

        ],

        "responses": [

            "Prosedur cuti akademik, tenggat pengajuan, dan persyaratannya perlu dikonfirmasi melalui program studi atau bagian akademik UNP sebelum periode pengajuan berakhir."

        ]

    },

    "lokasi_kampus": {

        "patterns": [

            "lokasi kampus", "alamat kampus", "dimana kampus",

            "kampus unp dimana", "alamat universitas negeri padang"

        ],

        "responses": [

            "Kampus utama Universitas Negeri Padang berada di kawasan Air Tawar, Kota Padang, Sumatera Barat. Untuk lokasi gedung atau fakultas tertentu, periksa peta dan informasi resmi UNP."

        ]

    },

    "kontak_admin": {

        "patterns": [

            "kontak admin", "hubungi admin", "nomor admin",

            "kontak akademik", "email akademik", "hubungi bagian akademik"

        ],

        "responses": [

            "Untuk menghindari informasi kontak yang keliru, gunakan halaman kontak resmi Universitas Negeri Padang atau hubungi administrasi fakultas/program studi."

        ]

    },

    "wisuda": {

        "patterns": [

            "wisuda", "pendaftaran wisuda", "syarat wisuda",

            "jadwal wisuda", "daftar wisuda"

        ],

        "responses": [

            "Persyaratan, jadwal, dan pendaftaran wisuda mengikuti pengumuman resmi UNP. Periksa persyaratan akademik, administrasi, dan tenggat pendaftaran pada periode wisuda yang dituju."

        ]

    },

    "terima_kasih": {

        "patterns": [

            "terima kasih", "makasih", "thanks",

            "terima kasih banyak"

        ],

        "responses": [

            "Sama-sama! Semoga informasi ini membantu."

        ]

    },

    "goodbye": {

        "patterns": [

            "bye", "sampai jumpa", "keluar", "exit",

            "selamat tinggal"

        ],

        "responses": [

            "Sampai jumpa! Semoga urusan akademikmu lancar."

        ]

    },

    "ruang_kuliah": {
        "patterns": ["ruang kuliah", "lokasi kelas", "kelas di ruang mana", "ruangan mata kuliah", "ruang perkuliahan"],
        "responses": ["CONTOH DATA DUMMY: Matematika Teknik di A1.2, Fisika Dasar di B2.1, Gambar Teknik di Lab Gambar, dan Praktikum Komputer di Lab Komputer. Ini hanya data simulasi, bukan informasi ruang resmi UNP."]
    },
    "dosen_pa": {
        "patterns": ["dosen pa", "dosen pembimbing akademik", "siapa dosen pa", "fungsi dosen pa", "konsultasi dosen wali"],
        "responses": ["Dosen PA membantu mahasiswa merencanakan studi, memberi arahan pemilihan mata kuliah, memantau perkembangan akademik, dan memberi konsultasi. Nama dosen PA pada contoh data dummy adalah Ibu Rina, M.Pd.; nama ini bukan data resmi."]
    },
    "registrasi": {
        "patterns": ["registrasi ulang", "daftar ulang", "herregistrasi", "aktif kuliah", "status mahasiswa aktif"],
        "responses": ["Secara umum, registrasi ulang dilakukan dengan memeriksa kewajiban administrasi, menyelesaikan pembayaran sesuai ketentuan, lalu memastikan status mahasiswa aktif pada portal akademik. Jadwal dan prosedur resmi harus mengikuti pengumuman UNP."]
    },
    "presensi": {
        "patterns": ["presensi", "absensi", "kehadiran kuliah", "persentase kehadiran", "tidak hadir kuliah"],
        "responses": ["CONTOH ATURAN DUMMY: Mahasiswa dianjurkan hadir minimal 75% dari pertemuan. Angka ini hanya contoh simulasi; ketentuan sebenarnya mengikuti RPS dan aturan mata kuliah."]
    },
    "praktikum": {
        "patterns": ["praktikum", "jadwal lab", "laboratorium", "laporan praktikum", "asisten praktikum"],
        "responses": ["Contoh jadwal praktikum dummy: Praktikum Komputer setiap Rabu pukul 13.00-15.30 di Lab Komputer. Mahasiswa menyiapkan modul, mengikuti instruksi keselamatan laboratorium, mengisi daftar hadir, dan mengumpulkan laporan sesuai arahan asisten."]
    },
    "perpustakaan": {
        "patterns": ["perpustakaan", "pinjam buku", "peminjaman buku", "pengembalian buku", "kartu anggota perpustakaan"],
        "responses": ["Layanan perpustakaan umumnya meliputi membaca di tempat, pencarian koleksi, peminjaman, dan pengembalian buku. Contoh data dummy: batas peminjaman 7 hari dengan maksimal 3 buku. Ketentuan sebenarnya perlu diperiksa pada layanan perpustakaan UNP."]
    },
    "beasiswa": {
        "patterns": ["beasiswa", "pendaftaran beasiswa", "syarat beasiswa", "kip kuliah", "bantuan pendidikan"],
        "responses": ["Persyaratan beasiswa berbeda menurut program. Umumnya mahasiswa perlu menyiapkan identitas, bukti status aktif, transkrip atau IPK, surat keterangan penghasilan jika diminta, dan dokumen pendukung. Periksa pengumuman resmi untuk syarat dan tenggat yang berlaku."]
    },
    "transkrip": {
        "patterns": ["transkrip nilai", "cetak transkrip", "nilai kumulatif", "daftar nilai", "transkrip akademik"],
        "responses": ["Transkrip akademik merangkum mata kuliah dan nilai yang telah ditempuh. Contoh alur: masuk portal akademik, buka menu hasil studi atau transkrip, periksa data, lalu ikuti prosedur fakultas jika membutuhkan transkrip yang disahkan."]
    },
    "yudisium": {
        "patterns": ["yudisium", "syarat yudisium", "pendaftaran yudisium", "daftar yudisium"],
        "responses": ["Yudisium merupakan proses penetapan kelulusan akademik mahasiswa. Persyaratan umum dapat mencakup penyelesaian seluruh mata kuliah, pemenuhan SKS, penyelesaian tugas akhir, dan administrasi. Persyaratan resmi berbeda menurut program studi dan periode."]
    },
    "skripsi_tugas_akhir": {
        "patterns": ["skripsi", "tugas akhir", "proposal penelitian", "seminar proposal", "sidang skripsi", "ujian tugas akhir"],
        "responses": ["Tahapan umum tugas akhir meliputi penentuan topik, konsultasi dengan calon pembimbing, penyusunan proposal, seminar proposal, pengumpulan dan analisis data, penulisan laporan, serta ujian akhir. Alur dan formulir resmi mengikuti ketentuan program studi."]
    },
    "magang": {
        "patterns": ["magang", "praktik industri", "praktik kerja lapangan", "pkl", "kerja praktik"],
        "responses": ["Persiapan magang umumnya mencakup mencari tempat magang, memenuhi persyaratan program studi, mengajukan surat pengantar, memperoleh persetujuan, melaksanakan kegiatan, dan menyusun laporan. Durasi dan prosedur harus dikonfirmasi ke program studi."]
    },
    "organisasi_mahasiswa": {
        "patterns": ["organisasi mahasiswa", "ukm", "himpunan mahasiswa", "bem", "kegiatan kemahasiswaan"],
        "responses": ["Mahasiswa dapat mengikuti organisasi seperti himpunan mahasiswa, BEM, atau UKM sesuai minat. Contoh kegiatan meliputi rapat, pelatihan, kompetisi, pengabdian masyarakat, dan kegiatan pengembangan minat bakat."]
    },
    "wifi_kampus": {
        "patterns": ["wifi kampus", "internet kampus", "akun wifi", "koneksi internet", "jaringan kampus"],
        "responses": ["Jika mengalami masalah Wi-Fi kampus, pastikan Wi-Fi aktif, pilih jaringan resmi, periksa akun akses jika diperlukan, lalu hubungi unit layanan TIK kampus. Nama jaringan dan prosedur akun perlu mengikuti informasi resmi."]
    },
    "fasilitas_kampus": {
        "patterns": ["fasilitas kampus", "toilet kampus", "parkir kampus", "kantin kampus", "ruang baca"],
        "responses": ["Fasilitas kampus dapat mencakup ruang kelas, laboratorium, perpustakaan, tempat ibadah, kantin, area parkir, dan ruang kegiatan mahasiswa. Lokasi serta jam operasional perlu diperiksa melalui informasi kampus."]
    },
    "nilai_ipk": {
        "patterns": ["ipk", "indeks prestasi kumulatif", "ips", "indeks prestasi semester", "menghitung ipk"],
        "responses": ["IPS menggambarkan capaian akademik dalam satu semester, sedangkan IPK merupakan rata-rata prestasi kumulatif dengan memperhitungkan bobot SKS. Untuk menghitungnya, jumlahkan nilai mutu seluruh mata kuliah lalu bagi dengan total SKS yang diperhitungkan."]
    },
    "semester_pendek": {
        "patterns": ["semester pendek", "semester antara", "kuliah antara", "mengulang mata kuliah"],
        "responses": ["Semester pendek atau semester antara dapat diselenggarakan sesuai kebijakan perguruan tinggi dan program studi. Mata kuliah yang dibuka, biaya, jadwal, dan syarat peserta harus diperiksa pada pengumuman resmi."]
    },
    "kartu_mahasiswa": {
        "patterns": ["kartu mahasiswa", "ktm", "kartu tanda mahasiswa", "ktm hilang", "cetak ktm"],
        "responses": ["Kartu Tanda Mahasiswa digunakan sebagai identitas mahasiswa. Jika hilang atau rusak, mahasiswa dapat menanyakan prosedur penggantian kepada layanan administrasi atau kemahasiswaan."]
    },
    "cuti_kembali_aktif": {
        "patterns": ["aktif kembali", "setelah cuti", "mengakhiri cuti", "kembali kuliah setelah cuti"],
        "responses": ["Mahasiswa yang akan aktif kembali setelah cuti perlu memastikan masa cuti telah berakhir, mengurus administrasi sesuai prosedur, dan mengonfirmasi status aktif sebelum mengisi KRS."]
    },

}







# ============================================================
# DATABASE AKADEMIK INFORMATIKA (SELURUHNYA DATA DUMMY)
# Catatan: semua nama, NIP, email, kode, jadwal, tarif, dan aturan
# dibuat fiktif untuk demonstrasi chatbot, bukan data resmi UNP.
# ============================================================

FAKULTAS = {
    "kode": "FT-DUMMY",
    "nama": "Fakultas Teknik",
    "universitas": "Universitas Negeri Padang",
    "alamat": "Kawasan Kampus Air Tawar, Padang, Sumatera Barat",
    "deskripsi": "Fakultas yang menyelenggarakan pendidikan bidang teknik dan vokasi (profil simulasi).",
    "program_studi": [
        {"kode": "IF-S1", "nama": "S1 Informatika", "jenjang": "Sarjana", "gelar": "S.Kom.",
         "departemen": "Departemen Elektronika", "akreditasi": "Baik Sekali (dummy)",
         "lama_studi": "8 semester", "total_sks": 144, "ketua": "Dr. Raka Pratama, M.Kom. (dummy)"},
    ]
}

DOSEN = [
    {"nidn":"0001018001","nama":"Dr. Raka Pratama, S.Kom., M.Kom.","jabatan":"Ketua Program Studi (dummy)","bidang":"Kecerdasan Buatan dan Machine Learning","email":"raka.pratama@example.edu","ruang":"Kantor Prodi IF-301","pa":["IF24-A"]},
    {"nidn":"0002028202","nama":"Dina Kurniawati, S.T., M.Kom.","jabatan":"Dosen","bidang":"Rekayasa Perangkat Lunak dan Manajemen Proyek","email":"dina.kurniawati@example.edu","ruang":"Kantor Dosen IF-302","pa":["IF24-B"]},
    {"nidn":"0003037903","nama":"Fajar Hidayat, S.Kom., M.Cs.","jabatan":"Dosen","bidang":"Sistem Operasi dan Arsitektur Komputer","email":"fajar.hidayat@example.edu","ruang":"Kantor Dosen IF-303","pa":["IF23-A"]},
    {"nidn":"0004048104","nama":"Nadia Putri, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Data Mining dan Data Science","email":"nadia.putri@example.edu","ruang":"Kantor Dosen IF-304","pa":["IF23-B"]},
    {"nidn":"0005057805","nama":"Rizki Maulana, S.T., M.Kom.","jabatan":"Dosen","bidang":"Jaringan Komputer dan Keamanan Siber","email":"rizki.maulana@example.edu","ruang":"Kantor Dosen IF-305","pa":["IF22-A"]},
    {"nidn":"0006068306","nama":"Siti Rahma, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Interaksi Manusia dan Komputer serta UI/UX","email":"siti.rahma@example.edu","ruang":"Kantor Dosen IF-306","pa":["IF22-B"]},
    {"nidn":"0007078007","nama":"Budi Santoso, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Algoritma, Struktur Data, dan Pemrograman","email":"budi.santoso@example.edu","ruang":"Kantor Dosen IF-307","pa":["IF25-A"]},
    {"nidn":"0008088408","nama":"Andi Pratama, S.T., M.Kom.","jabatan":"Dosen","bidang":"Sistem Informasi dan Analisis Bisnis","email":"andi.pratama@example.edu","ruang":"Kantor Dosen IF-308","pa":["IF25-B"]},
    {"nidn":"0009097909","nama":"Rina Amelia, S.Si., M.Kom.","jabatan":"Dosen","bidang":"Matematika Diskrit dan Statistika","email":"rina.amelia@example.edu","ruang":"Kantor Dosen IF-309","pa":["IF21-A"]},
    {"nidn":"0010108110","nama":"Aditya Putra, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Deep Learning, Computer Vision, dan NLP","email":"aditya.putra@example.edu","ruang":"Kantor Dosen IF-310","pa":["IF21-B"]},
    {"nidn":"0011118211","nama":"Maya Lestari, S.Kom., M.T.","jabatan":"Dosen","bidang":"Basis Data dan Sistem Terdistribusi","email":"maya.lestari@example.edu","ruang":"Kantor Dosen IF-311","pa":[]},
    {"nidn":"0012128012","nama":"Yoga Saputra, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Pemrograman Web dan Mobile","email":"yoga.saputra@example.edu","ruang":"Kantor Dosen IF-312","pa":[]},
    {"nidn":"0013138313","nama":"Intan Permata, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Grafika Komputer dan Multimedia","email":"intan.permata@example.edu","ruang":"Kantor Dosen IF-313","pa":[]},
    {"nidn":"0014147714","nama":"Dedi Firmansyah, S.T., M.Kom.","jabatan":"Dosen","bidang":"Komputasi Awan dan DevOps","email":"dedi.firmansyah@example.edu","ruang":"Kantor Dosen IF-314","pa":[]},
    {"nidn":"0015158515","nama":"Laila Safitri, S.Kom., M.Kom.","jabatan":"Dosen","bidang":"Etika Profesi dan Metodologi Penelitian","email":"laila.safitri@example.edu","ruang":"Kantor Dosen IF-315","pa":[]},
]

DOSEN_PA = [
    {"kode_kelas":"IF25-A","angkatan":2025,"dosen":"Budi Santoso, S.Kom., M.Kom.","email":"budi.santoso@example.edu"},
    {"kode_kelas":"IF25-B","angkatan":2025,"dosen":"Andi Pratama, S.T., M.Kom.","email":"andi.pratama@example.edu"},
    {"kode_kelas":"IF24-A","angkatan":2024,"dosen":"Dr. Raka Pratama, S.Kom., M.Kom.","email":"raka.pratama@example.edu"},
    {"kode_kelas":"IF24-B","angkatan":2024,"dosen":"Dina Kurniawati, S.T., M.Kom.","email":"dina.kurniawati@example.edu"},
    {"kode_kelas":"IF23-A","angkatan":2023,"dosen":"Fajar Hidayat, S.Kom., M.Cs.","email":"fajar.hidayat@example.edu"},
    {"kode_kelas":"IF23-B","angkatan":2023,"dosen":"Nadia Putri, S.Kom., M.Kom.","email":"nadia.putri@example.edu"},
    {"kode_kelas":"IF22-A","angkatan":2022,"dosen":"Rizki Maulana, S.T., M.Kom.","email":"rizki.maulana@example.edu"},
    {"kode_kelas":"IF22-B","angkatan":2022,"dosen":"Siti Rahma, S.Kom., M.Kom.","email":"siti.rahma@example.edu"},
    {"kode_kelas":"IF21-A","angkatan":2021,"dosen":"Rina Amelia, S.Si., M.Kom.","email":"rina.amelia@example.edu"},
    {"kode_kelas":"IF21-B","angkatan":2021,"dosen":"Aditya Putra, S.Kom., M.Kom.","email":"aditya.putra@example.edu"},
]

# kode, nama, SKS, semester, hari, jam, ruang, dosen pengampu
_RAW_MK = [
("IF101","Pendidikan Agama",2,1,"Senin","08.00-09.40","IF-101","Laila Safitri"),
("IF102","Pendidikan Pancasila",2,1,"Senin","09.50-11.30","IF-101","Laila Safitri"),
("IF103","Kalkulus",3,1,"Senin","13.00-15.30","IF-201","Rina Amelia"),
("IF104","Pengantar Informatika",2,1,"Selasa","08.00-09.40","IF-102","Andi Pratama"),
("IF105","Algoritma dan Pemrograman",3,1,"Selasa","09.50-12.20","LAB-1","Budi Santoso"),
("IF106","Matematika Diskrit",3,1,"Rabu","08.00-10.30","IF-201","Rina Amelia"),
("IF107","Bahasa Inggris",2,1,"Rabu","10.40-12.20","IF-102","Laila Safitri"),
("IF108","Literasi Digital",2,1,"Kamis","08.00-09.40","IF-103","Andi Pratama"),
("IF109","Dasar Sistem Komputer",3,1,"Kamis","09.50-12.20","LAB-2","Fajar Hidayat"),
("IF110","Bahasa Indonesia",2,1,"Jumat","08.00-09.40","IF-101","Laila Safitri"),
("IF201","Struktur Data",3,2,"Senin","08.00-10.30","LAB-1","Budi Santoso"),
("IF202","Basis Data",3,2,"Senin","10.40-13.10","LAB-2","Maya Lestari"),
("IF203","Sistem Operasi",3,2,"Selasa","08.00-10.30","LAB-2","Fajar Hidayat"),
("IF204","Pemrograman Berorientasi Objek",3,2,"Selasa","13.00-15.30","LAB-1","Yoga Saputra"),
("IF205","Aljabar Linear",3,2,"Rabu","08.00-10.30","IF-201","Rina Amelia"),
("IF206","Organisasi dan Arsitektur Komputer",3,2,"Rabu","10.40-13.10","IF-202","Fajar Hidayat"),
("IF207","Statistika dan Probabilitas",3,2,"Kamis","08.00-10.30","IF-201","Rina Amelia"),
("IF208","Pendidikan Kewarganegaraan",2,2,"Jumat","08.00-09.40","IF-101","Laila Safitri"),
("IF301","Jaringan Komputer",3,3,"Senin","08.00-10.30","LAB-JARINGAN","Rizki Maulana"),
("IF302","Pemrograman Web",3,3,"Senin","10.40-13.10","LAB-1","Yoga Saputra"),
("IF303","Analisis dan Desain Algoritma",3,3,"Selasa","08.00-10.30","IF-202","Budi Santoso"),
("IF304","Rekayasa Perangkat Lunak",3,3,"Selasa","10.40-13.10","IF-203","Dina Kurniawati"),
("IF305","Sistem Informasi",2,3,"Rabu","08.00-09.40","IF-102","Andi Pratama"),
("IF306","Interaksi Manusia dan Komputer",3,3,"Rabu","09.50-12.20","LAB-UX","Siti Rahma"),
("IF307","Metode Numerik",3,3,"Kamis","08.00-10.30","IF-201","Rina Amelia"),
("IF308","Praktikum Basis Data",1,3,"Jumat","08.00-09.40","LAB-2","Maya Lestari"),
("IF401","Kecerdasan Buatan",3,4,"Senin","08.00-10.30","LAB-AI","Aditya Putra"),
("IF402","Pemrograman Mobile",3,4,"Senin","10.40-13.10","LAB-1","Yoga Saputra"),
("IF403","Keamanan Informasi",3,4,"Selasa","08.00-10.30","LAB-JARINGAN","Rizki Maulana"),
("IF404","Manajemen Proyek Perangkat Lunak",2,4,"Selasa","10.40-12.20","IF-203","Dina Kurniawati"),
("IF405","Teori Bahasa dan Otomata",3,4,"Rabu","08.00-10.30","IF-202","Rina Amelia"),
("IF406","Grafika Komputer",3,4,"Rabu","10.40-13.10","LAB-MULTIMEDIA","Intan Permata"),
("IF407","Etika Profesi",2,4,"Kamis","08.00-09.40","IF-101","Laila Safitri"),
("IF408","Praktikum Jaringan Komputer",1,4,"Jumat","08.00-09.40","LAB-JARINGAN","Rizki Maulana"),
("IF501","Machine Learning",3,5,"Senin","08.00-10.30","LAB-AI","Aditya Putra"),
("IF502","Data Mining",3,5,"Senin","10.40-13.10","LAB-DATA","Nadia Putri"),
("IF503","Pemrograman Berbasis Framework",3,5,"Selasa","08.00-10.30","LAB-1","Yoga Saputra"),
("IF504","Komputasi Awan",3,5,"Selasa","10.40-13.10","LAB-CLOUD","Dedi Firmansyah"),
("IF505","Sistem Terdistribusi",3,5,"Rabu","08.00-10.30","IF-203","Maya Lestari"),
("IF506","Visi Komputer",3,5,"Rabu","10.40-13.10","LAB-AI","Aditya Putra"),
("IF507","Metodologi Penelitian",2,5,"Kamis","08.00-09.40","IF-202","Laila Safitri"),
("IF508","Pemrograman Game",2,5,"Jumat","08.00-09.40","LAB-MULTIMEDIA","Intan Permata"),
("IF601","Deep Learning",3,6,"Senin","08.00-10.30","LAB-AI","Aditya Putra"),
("IF602","Pemrosesan Bahasa Alami",3,6,"Senin","10.40-13.10","LAB-AI","Nadia Putri"),
("IF603","Forensik Digital",3,6,"Selasa","08.00-10.30","LAB-JARINGAN","Rizki Maulana"),
("IF604","Analisis Big Data",3,6,"Selasa","10.40-13.10","LAB-DATA","Nadia Putri"),
("IF605","Manajemen Layanan TI",2,6,"Rabu","08.00-09.40","IF-203","Dina Kurniawati"),
("IF606","Kewirausahaan Digital",2,6,"Kamis","08.00-09.40","IF-102","Andi Pratama"),
("IF607","Proyek Perangkat Lunak",3,6,"Jumat","08.00-10.30","LAB-1","Dina Kurniawati"),
("IF701","Seminar Proposal",2,7,"Senin","08.00-09.40","IF-301","Dina Kurniawati"),
("IF702","Kerja Praktik",2,7,"Selasa","08.00-09.40","IF-301","Raka Pratama"),
("IF703","Mata Kuliah Pilihan AI",3,7,"Rabu","08.00-10.30","LAB-AI","Aditya Putra"),
("IF704","Mata Kuliah Pilihan Keamanan Siber",3,7,"Kamis","08.00-10.30","LAB-JARINGAN","Rizki Maulana"),
("IF801","Skripsi",6,8,"Senin","08.00-09.40","IF-301","Raka Pratama"),
("IF802","Seminar Hasil dan Ujian Akhir",2,8,"Kamis","08.00-09.40","IF-301","Dina Kurniawati"),
]

RUANG = {
"IF-101":"Ruang kuliah teori lantai 1, kapasitas อ40 orang",
"IF-102":"Ruang kuliah teori lantai 1, kapasitas 40 orang",
"IF-103":"Ruang kuliah teori lantai 1, kapasitas 35 orang",
"IF-201":"Ruang kuliah teori lantai 2, kapasitas 40 orang",
"IF-202":"Ruang kuliah teori lantai 2, kapasitas 40 orang",
"IF-203":"Ruang kuliah teori lantai 2, kapasitas 35 orang",
"IF-301":"Ruang seminar dan konsultasi tugas akhir, kapasitas 25 orang",
"LAB-1":"Laboratorium Pemrograman, 30 komputer",
"LAB-2":"Laboratorium Basis Data dan Sistem Komputer, 28 komputer",
"LAB-JARINGAN":"Laboratorium Jaringan Komputer dan Keamanan Siber, 24 unit perangkat praktik",
"LAB-AI":"Laboratorium Kecerdasan Buatan dan Komputasi, 25 workstation",
"LAB-DATA":"Laboratorium Data Science, 25 workstation",
"LAB-UX":"Laboratorium Interaksi Manusia-Komputer dan UI/UX, 20 workstation",
"LAB-MULTIMEDIA":"Laboratorium Grafika, Multimedia, dan Game, 25 workstation",
"LAB-CLOUD":"Laboratorium Cloud dan DevOps, 20 server virtual",
}

MATA_KULIAH = []
for row in _RAW_MK:
    kode,nama,sks,semester,hari,jam,ruang,dosen = row
    MATA_KULIAH.append({"kode":kode,"nama":nama,"sks":sks,"semester":semester,
        "hari":hari,"jam":jam,"ruang":ruang,"dosen":dosen,
        "prodi":"S1 Informatika","kelas":f"IF{2026-semester+1}-A"})

KURIKULUM = {
    1: ["Pendidikan Agama","Pendidikan Pancasila","Kalkulus","Pengantar Informatika","Algoritma dan Pemrograman","Matematika Diskrit","Bahasa Inggris","Literasi Digital","Dasar Sistem Komputer","Bahasa Indonesia"],
    2: ["Struktur Data","Basis Data","Sistem Operasi","Pemrograman Berorientasi Objek","Aljabar Linear","Organisasi dan Arsitektur Komputer","Statistika dan Probabilitas","Pendidikan Kewarganegaraan"],
    3: ["Jaringan Komputer","Pemrograman Web","Analisis dan Desain Algoritma","Rekayasa Perangkat Lunak","Sistem Informasi","Interaksi Manusia dan Komputer","Metode Numerik","Praktikum Basis Data"],
    4: ["Kecerdasan Buatan","Pemrograman Mobile","Keamanan Informasi","Manajemen Proyek Perangkat Lunak","Teori Bahasa dan Otomata","Grafika Komputer","Etika Profesi","Praktikum Jaringan Komputer"],
    5: ["Machine Learning","Data Mining","Pemrograman Berbasis Framework","Komputasi Awan","Sistem Terdistribusi","Visi Komputer","Metodologi Penelitian","Pemrograman Game"],
    6: ["Deep Learning","Pemrosesan Bahasa Alami","Forensik Digital","Analisis Big Data","Manajemen Layanan TI","Kewirausahaan Digital","Proyek Perangkat Lunak"],
    7: ["Seminar Proposal","Kerja Praktik","Mata Kuliah Pilihan AI","Mata Kuliah Pilihan Keamanan Siber"],
    8: ["Skripsi","Seminar Hasil dan Ujian Akhir"]
}

ATURAN_AKADEMIK = {
"krs": "KRS adalah rencana mata kuliah yang diambil mahasiswa pada semester berjalan. Alur simulasi: (1) pastikan status registrasi aktif, (2) cek prasyarat dan nilai mata kuliah, (3) konsultasi dengan dosen PA, (4) pilih kelas dan periksa bentrok jadwal, (5) simpan/finalisasi KRS, (6) unduh bukti KRS. Perubahan KRS hanya pada masa revisi yang ditentukan.",
"khs": "KHS memuat nilai setiap mata kuliah pada satu semester, jumlah SKS yang ditempuh, IPS, dan status hasil studi. Jika nilai kosong atau keliru, mahasiswa menghubungi dosen pengampu lalu mengikuti prosedur koreksi nilai prodi.",
"ipk": "IPS adalah indeks prestasi untuk satu semester. IPK adalah indeks prestasi kumulatif dari seluruh semester yang telah ditempuh. Rumus simulasi: IPK = total (bobot nilai x SKS) dibagi total SKS yang diperhitungkan. Contoh bobot: A=4, B=3, C=2, D=1, E=0. Konversi sebenarnya mengikuti peraturan akademik resmi.",
"sks": "Beban studi maksimum ditentukan oleh peraturan akademik dan hasil studi semester sebelumnya. Contoh simulasi: IPS >= 3,00 dapat mengambil hingga 24 SKS; IPS 2,50-2,99 hingga 22 SKS; IPS 2,00-2,49 hingga 20 SKS; IPS < 2,00 hingga 18 SKS. Ini bukan ketentuan resmi.",
"ukt": "Contoh simulasi kelompok UKT Informatika: Kelompok 1 Rp500.000/semester; Kelompok 2 Rp1.000.000; Kelompok 3 Rp2.500.000; Kelompok 4 Rp4.000.000; Kelompok 5 Rp5.500.000; Kelompok 6 Rp6.500.000; Kelompok 7 Rp7.500.000. Nominal fiktif untuk demonstrasi, bukan tarif UNP.",
"beasiswa": "Contoh program beasiswa: Beasiswa Prestasi Akademik (IPK minimal dummy 3,50), Beasiswa Bantuan Ekonomi (dokumen penghasilan), KIP Kuliah (mengikuti persyaratan nasional), Beasiswa Mitra Industri (seleksi mitra), dan Bantuan UKT. Berkas simulasi: formulir, KTM, KTP, KK, transkrip, surat penghasilan bila diminta, dan esai motivasi.",
"registrasi": "Registrasi semester: cek pengumuman, selesaikan kewajiban administrasi, lakukan aktivasi pada sistem akademik, pastikan status aktif, lalu konsultasi KRS dengan dosen PA. Simpan bukti registrasi.",
"cuti": "Pengajuan cuti simulasi: konsultasi prodi dan dosen PA, isi formulir cuti, lampirkan alasan dan dokumen pendukung, ajukan sebelum batas waktu, tunggu persetujuan, lalu simpan surat keputusan. Cuti tidak boleh diasumsikan otomatis disetujui.",
"praktikum": "Aturan laboratorium simulasi: memakai identitas mahasiswa, hadir sesuai jadwal, membaca modul, menjaga perangkat, tidak mengubah konfigurasi tanpa izin, mencatat hasil, melaporkan kerusakan, dan mengumpulkan laporan sesuai tenggat.",
"magang": "Prosedur kerja praktik simulasi: memenuhi prasyarat SKS, mencari instansi, mengajukan persetujuan prodi, mengurus surat pengantar, menetapkan pembimbing, melaksanakan kegiatan dan logbook, meminta penilaian pembimbing lapangan, lalu menyerahkan laporan.",
"skripsi": "Tahapan skripsi simulasi: memenuhi prasyarat, mengajukan topik, penetapan pembimbing, menyusun proposal, seminar proposal, pengambilan data, konsultasi berkala, ujian hasil, revisi, ujian akhir, unggah naskah final, dan mengurus administrasi kelulusan.",
"wisuda": "Persiapan wisuda simulasi: lulus seluruh mata kuliah, menyelesaikan skripsi dan revisi, memenuhi syarat yudisium, bebas pustaka/laboratorium sesuai ketentuan, melengkapi data lulusan, membayar biaya jika ditetapkan, dan mendaftar pada periode yang dibuka.",
"presensi": "Ketentuan presensi simulasi: dosen mencatat kehadiran tiap pertemuan. Contoh batas kehadiran 75% digunakan hanya untuk latihan; aturan sebenarnya mengikuti RPS dan kebijakan mata kuliah.",
"kalender": "Kalender akademik dummy: Januari registrasi semester genap; Februari perkuliahan dimulai; April evaluasi tengah semester; Juni ujian akhir semester; Juli libur dan administrasi; Agustus registrasi semester ganjil; September perkuliahan dimulai; November evaluasi tengah semester; Desember ujian akhir semester. Semua tanggal adalah contoh.",
}

BEASISWA = [
{"nama":"Beasiswa Prestasi Akademik","syarat":"IPK minimal 3,50 (dummy), aktif kuliah, tidak sedang terkena sanksi","berkas":"KTM, KTP, transkrip, surat rekomendasi, esai prestasi"},
{"nama":"Beasiswa Bantuan Ekonomi","syarat":"Memiliki kendala ekonomi berdasarkan verifikasi dokumen","berkas":"KTM, KK, KTP, surat penghasilan orang tua, surat keterangan kondisi ekonomi"},
{"nama":"KIP Kuliah","syarat":"Mengikuti persyaratan dan seleksi program KIP Kuliah yang berlaku","berkas":"Dokumen identitas, data keluarga, data ekonomi, dan dokumen pendidikan"},
{"nama":"Beasiswa Mitra Industri","syarat":"Mengikuti seleksi mitra dan memenuhi kriteria bidang studi","berkas":"CV, transkrip, portofolio, surat motivasi"}
]

KALENDER_DUMMY = [
("Januari","Registrasi ulang dan pengisian KRS semester genap"),
("Februari","Awal perkuliahan semester genap"),
("Maret","Perkuliahan dan evaluasi tugas"),
("April","Ujian tengah semester genap"),
("Mei","Perkuliahan dan praktikum"),
("Juni","Ujian akhir semester genap dan input nilai"),
("Juli","Libur semester dan administrasi akademik"),
("Agustus","Registrasi ulang dan pengisian KRS semester ganjil"),
("September","Awal perkuliahan semester ganjil"),
("Oktober","Perkuliahan dan evaluasi tugas"),
("November","Ujian tengah semester ganjil"),
("Desember","Ujian akhir semester ganjil dan input nilai")
]

def _format_mk(mk):
    dosen_lengkap = next((d["nama"] for d in DOSEN if d["nama"].startswith(mk["dosen"])), mk["dosen"])
    return (f"- {mk['nama']} ({mk['kode']}) | {mk['sks']} SKS | Semester {mk['semester']}\n"
            f"  Hari: {mk['hari']} | Jam: {mk['jam']} | Ruang: {mk['ruang']}\n"
            f"  Dosen: {dosen_lengkap} | Prodi: {mk['prodi']}")

def _is_data_query(q):
    keys = ["jadwal","mata kuliah","matkul","kode mk","sks","semester","dosen","pengampu","ruang","kelas","kurikulum","informatika"]
    return any(k in q for k in keys)

def cari_data_mata_kuliah(user_input):
    q = preprocess(user_input)
    tokens = [t for t in q.split() if len(t) > 2]
    hari = next((h for h in ["senin","selasa","rabu","kamis","jumat","sabtu"] if h in q), None)
    semester_match = re.search(r"semester\s+(\d+)", q)
    hasil = []

    # Nama atau kode mata kuliah spesifik.
    for mk in MATA_KULIAH:
        nama = preprocess(mk["nama"])
        if mk["kode"].lower() in q or nama in q:
            hasil.append(mk)

    # Pertanyaan tentang dosen pengampu.
    if not hasil:
        for mk in MATA_KULIAH:
            if preprocess(mk["dosen"]) in q and any(k in q for k in ["jadwal","mengajar","ampu","mata kuliah"]):
                hasil.append(mk)

    # Jadwal per hari, semester, atau seluruh jadwal.
    if not hasil and hari and any(k in q for k in ["jadwal","kuliah","kelas","matkul"]):
        hasil = [m for m in MATA_KULIAH if m["hari"].lower() == hari]
        if semester_match:
            hasil = [m for m in hasil if m["semester"] == int(semester_match.group(1))]
    if not hasil and semester_match and any(k in q for k in ["mata kuliah","matkul","kurikulum","semester"]):
        hasil = [m for m in MATA_KULIAH if m["semester"] == int(semester_match.group(1))]
    if not hasil and any(k in q for k in ["semua jadwal","jadwal lengkap","seluruh jadwal"]):
        hasil = MATA_KULIAH

    if not hasil:
        return None
    header = ["DATABASE AKADEMIK INFORMATIKA — DATA DUMMY / SIMULASI",
              f"Ditemukan {len(hasil)} data mata kuliah:"]
    return "\n".join(header + [_format_mk(m) for m in hasil] +
                      ["Catatan: seluruh jadwal, dosen, kode, dan ruang adalah data fiktif, bukan jadwal resmi UNP."])

def cari_data_dosen(user_input):
    q = preprocess(user_input)
    found = []
    for d in DOSEN:
        nama_key = preprocess(d["nama"])
        nama_singkat = preprocess(d["nama"].split(",")[0])
        if nama_key in q or (len(nama_singkat) > 4 and nama_singkat in q):
            found.append(d)
    if not found and any(k in q for k in ["semua dosen","daftar dosen","data dosen","nama dosen","dosen informatika"]):
        found = DOSEN
    if not found:
        return None
    out = ["DAFTAR DOSEN S1 INFORMATIKA — DATA DUMMY"]
    for d in found:
        out.append(f"- {d['nama']} | NIDN dummy: {d['nidn']} | {d['jabatan']}\n  Bidang: {d['bidang']}\n  Email dummy: {d['email']}\n  Ruang: {d['ruang']}\n  Kelas PA: {', '.join(d['pa']) if d['pa'] else 'Belum ditetapkan'}")
    out.append("Semua identitas, NIDN, email, jabatan, dan ruang dosen di atas fiktif.")
    return "\n".join(out)

def cari_dosen_pa(user_input):
    q = preprocess(user_input)
    m = re.search(r"(20\d{2})", q)
    angkatan = int(m.group(1)) if m else None
    if angkatan:
        rows = [x for x in DOSEN_PA if x["angkatan"] == angkatan]
    else:
        rows = DOSEN_PA
    if not any(k in q for k in ["dosen pa","dosen pembimbing","dosen wali","angkatan","pa saya","pembimbing akademik"]):
        return None
    out = ["DAFTAR DOSEN PEMBIMBING AKADEMIK — DATA DUMMY"]
    for x in rows:
        out.append(f"- Angkatan {x['angkatan']} / Kelas {x['kode_kelas']}: {x['dosen']} | {x['email']}")
    out.append("Penetapan dosen PA pada daftar ini hanya simulasi.")
    return "\n".join(out)

def cari_informasi_lain(user_input):
    q = preprocess(user_input)
    if any(k in q for k in ["fakultas","program studi","prodi informatika","profil informatika","kaprodi"]):
        p = FAKULTAS["program_studi"][0]
        return ("PROFIL AKADEMIK — DATA DUMMY\n"
                f"Fakultas: {FAKULTAS['nama']}\nProgram Studi: {p['nama']} ({p['kode']})\n"
                f"Jenjang: {p['jenjang']} | Gelar: {p['gelar']}\nDepartemen: {p['departemen']}\n"
                f"Akreditasi contoh: {p['akreditasi']} | Lama studi: {p['lama_studi']}\n"
                f"Target kurikulum simulasi: {p['total_sks']} SKS\nKetua prodi dummy: {p['ketua']}\n"
                "Seluruh rincian profil ini dibuat untuk demonstrasi.")
    if "kurikulum" in q or "daftar mata kuliah per semester" in q:
        out = ["KURIKULUM S1 INFORMATIKA — DATA DUMMY"]
        sem_match = re.search(r"semester\s+(\d+)", q)
        semesters = [int(sem_match.group(1))] if sem_match and int(sem_match.group(1)) in KURIKULUM else list(KURIKULUM)
        for sem in semesters:
            names = KURIKULUM[sem]
            total = sum(m["sks"] for m in MATA_KULIAH if m["semester"] == sem)
            out.append(f"Semester {sem} ({total} SKS terdata): " + "; ".join(names))
        out.append("Kurikulum dan SKS di atas adalah rancangan fiktif untuk demonstrasi.")
        return "\n".join(out)
    if "ruang" in q and any(k in q for k in ["lab","laboratorium","daftar ruang","ruang kelas","fasilitas"]):
        return "DAFTAR RUANG DAN LABORATORIUM — DATA DUMMY\n" + "\n".join(f"- {k}: {v}" for k,v in RUANG.items())
    if any(k in q for k in ["daftar laboratorium","laboratorium apa","apa saja laboratorium","daftar lab","lab informatika"]):
        return "DAFTAR LABORATORIUM INFORMATIKA — DATA DUMMY\n" + "\n".join(f"- {k}: {v}" for k,v in RUANG.items() if k.startswith("LAB-"))
    if any(k in q for k in ["beasiswa","kip kuliah"]):
        return "PROGRAM BEASISWA — DATA DUMMY\n" + "\n".join(f"- {b['nama']}\n  Syarat: {b['syarat']}\n  Berkas: {b['berkas']}" for b in BEASISWA) + "\nSeluruh program dan kriteria selain nama program nasional yang disebut sebagai contoh harus diverifikasi; data seleksi di sini simulasi."
    if any(k in q for k in ["kalender akademik","jadwal uts","jadwal uas","awal semester","akhir semester"]):
        return "KALENDER AKADEMIK — DATA DUMMY\n" + "\n".join(f"- {bulan}: {agenda}" for bulan,agenda in KALENDER_DUMMY) + "\nBulan dan agenda hanya contoh, bukan tanggal resmi."
    mapping = {
        "krs":["krs","kartu rencana studi","isi krs","ubah krs"],
        "khs":["khs","kartu hasil studi","lihat nilai","nilai semester"],
        "ipk":["ipk","ips","indeks prestasi","hitung ipk"],
        "sks":["sks","beban studi","maksimal sks","jumlah sks"],
        "ukt":["ukt","uang kuliah","biaya kuliah","tarif kuliah"],
        "registrasi":["registrasi","daftar ulang","herregistrasi"],
        "cuti":["cuti","nonaktif","kembali aktif"],
        "praktikum":["praktikum","laboratorium","aturan lab"],
        "magang":["magang","kerja praktik","pkl"],
        "skripsi":["skripsi","tugas akhir","seminar proposal","ujian skripsi"],
        "wisuda":["wisuda","yudisium","syarat lulus"],
        "presensi":["presensi","absensi","kehadiran"],
        "kalender":["kalender","uts","uas"]
    }
    for key, patterns in mapping.items():
        if any(x in q for x in patterns):
            return ATURAN_AKADEMIK[key] + "\n\nCatatan: ketentuan di atas adalah contoh simulasi, bukan peraturan resmi UNP."
    if any(k in q for k in ["wifi","internet kampus","jaringan kampus"]):
        return "Bantuan Wi-Fi dummy: aktifkan Wi-Fi, pilih SSID UNP-ACADEMIC-DUMMY, login memakai akun simulasi, lupakan jaringan lalu sambungkan ulang jika gagal. SSID ini fiktif dan bukan jaringan resmi."
    if any(k in q for k in ["fasilitas kampus","perpustakaan","kantin","parkir","tempat ibadah"]):
        return "Fasilitas contoh di lingkungan prodi: ruang kuliah IF-101 s.d. IF-301, Lab Pemrograman, Lab Basis Data, Lab Jaringan, Lab AI, Lab Data Science, Lab UX, Lab Multimedia, Lab Cloud, perpustakaan, kantin, area parkir, dan tempat ibadah. Lokasi ini data simulasi."
    return None

# ============================================================
# PREPROCESSING
# ============================================================

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


STOPWORDS = {
    "saya", "aku", "anda", "kamu", "yang", "dan", "atau", "di", "ke",
    "dari", "untuk", "dengan", "pada", "itu", "ini", "apa", "apakah",
    "bagaimana", "kenapa", "mengapa", "berapa", "dimana", "kapan",
    "tolong", "mohon", "bisa", "kah", "ya", "dong", "sih", "nya",
    "ingin", "mau", "tentang", "jelaskan", "jelaskanlah"
}


def meaningful_tokens(text):
    return [
        token for token in preprocess(text).split()
        if token not in STOPWORDS and len(token) > 2
    ]


# ============================================================
# RULE-BASED MATCHING (PEMBANDING EKSPERIMEN)
# ============================================================

def match_intent_rule_based(user_input):
    processed = preprocess(user_input)
    for intent, data in knowledge_base.items():
        for pattern in data["patterns"]:
            pattern_clean = preprocess(pattern)
            if pattern_clean and pattern_clean in processed:
                return intent
    return None


# ============================================================
# DATA TRAINING TF-IDF
# ============================================================

training_examples = {

    "greeting": [

        "halo", "hai", "selamat pagi", "selamat siang",

        "selamat sore", "assalamualaikum", "permisi"

    ],

    "jadwal_kuliah": [

        "jadwal kuliah", "jadwal kelas", "kapan kuliah",

        "jam berapa kuliah", "jadwal perkuliahan",

        "kapan jadwal kuliah semester ini",

        "saya ingin melihat jadwal kuliah", "jadwal semester"

    ],

    "krs": [

        "apa itu KRS", "kartu rencana studi",

        "bagaimana cara mengisi KRS", "kapan pengisian KRS",

        "saya ingin mengambil mata kuliah", "ubah KRS"

    ],

    "khs": [

        "apa itu KHS", "kartu hasil studi", "lihat nilai semester",

        "bagaimana melihat nilai", "nilai mata kuliah belum keluar"

    ],

    "ukt": [

        "apa itu UKT", "uang kuliah tunggal", "cara bayar UKT",

        "jadwal pembayaran kuliah", "keringanan UKT",

        "permohonan penurunan UKT"

    ],

    "kalender_akademik": [

        "kalender akademik", "kapan awal semester",

        "jadwal UTS", "jadwal UAS", "kapan libur semester",

        "jadwal ujian semester"

    ],

    "cuti_akademik": [

        "cara mengajukan cuti kuliah", "cuti akademik",

        "syarat cuti kuliah", "izin tidak kuliah satu semester"

    ],

    "lokasi_kampus": [

        "lokasi kampus", "alamat kampus", "dimana kampus",

        "dimana lokasi UNP", "alamat Universitas Negeri Padang",

        "cara menuju kampus UNP"

    ],

    "kontak_admin": [

        "kontak admin", "hubungi admin", "nomor admin",

        "kontak bagian akademik", "email akademik",

        "cara menghubungi program studi"

    ],

    "wisuda": [

        "cara daftar wisuda", "syarat wisuda",

        "jadwal wisuda", "pendaftaran wisuda",

        "dokumen untuk wisuda"

    ],

    "terima_kasih": [

        "terima kasih", "makasih", "thanks",

        "terima kasih banyak", "terima kasih atas bantuan"

    ],

    "goodbye": [

        "bye", "sampai jumpa", "keluar", "exit",

        "selamat tinggal", "saya mau pergi"

    ]
}

# Variasi pertanyaan tambahan untuk data training.
training_examples.setdefault("jadwal_kuliah", []).extend([
    "jadwal kuliah hari senin", "mata kuliah hari selasa jam berapa",
    "hari rabu ada kelas apa", "jadwal kuliah kelas A",
    "jadwal matematika teknik", "kuliah di ruang A1.2",
    "jam berapa praktikum komputer", "jadwal kelas semester ini",
    "tolong tampilkan jadwal perkuliahan", "hari jumat ada kuliah atau tidak"
])
training_examples.setdefault("ruang_kuliah", []).extend([
    "dimana ruang matematika teknik", "fisika dasar di ruangan berapa",
    "lokasi lab komputer", "kelas saya di gedung mana"
])

# Semua pola Knowledge Base otomatis menjadi contoh training untuk TF-IDF.
for intent_name, intent_data in knowledge_base.items():
    training_examples.setdefault(intent_name, [])
    training_examples[intent_name].extend(intent_data.get("patterns", []))






# ============================================================
# MEMBANGUN MODEL TF-IDF
# ============================================================

corpus = []
labels = []

for intent, examples in training_examples.items():
    for example in examples:
        corpus.append(preprocess(example))
        labels.append(intent)

vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
tfidf_matrix = vectorizer.fit_transform(corpus)

# Kata bermakna yang memang muncul dalam contoh training.
TRAINING_VOCAB = set(vectorizer.get_feature_names_out())


def match_intent_tfidf(user_input, threshold=SIMILARITY_THRESHOLD):
    tokens = meaningful_tokens(user_input)

    # Jangan klasifikasikan pesan terlalu pendek atau hanya kata umum.
    if len(tokens) < 1:
        return None, 0.0

    # Hindari false positive jika tidak ada kata bermakna yang dikenal model.
    if not any(token in TRAINING_VOCAB for token in tokens):
        return None, 0.0

    processed = preprocess(user_input)
    user_vector = vectorizer.transform([processed])
    scores = cosine_similarity(user_vector, tfidf_matrix)[0]

    best_index = scores.argmax()
    best_score = float(scores[best_index])
    best_intent = labels[best_index]

    if best_score >= threshold:
        return best_intent, best_score

    return None, best_score


# ============================================================
# VALIDASI DAN ROUTING PERTANYAAN
# ============================================================

def is_incomplete_question(user_input):
    tokens = meaningful_tokens(user_input)
    normalized = preprocess(user_input)

    short_messages = {
        "apa", "berapa", "dimana", "kapan", "kenapa", "mengapa",
        "bagaimana", "siapa", "itu", "ini", "yang", "apakah"
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
        "kelebihan dan kekurangan", "perbedaan antara"
    ]
    return any(phrase in text for phrase in complex_phrases)


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


# ============================================================
# GEMINI API
# ============================================================

def ask_gemini(user_input, intent=None, timeout=45):
    if not GEMINI_API_KEY:
        print("[ERROR] API Key belum dimasukkan melalui GEMINI_API_KEY.")
        return None

    context = get_relevant_knowledge(intent)

    system_instruction = """
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

    prompt = f"""
KONTEKS KNOWLEDGE BASE (gunakan hanya jika relevan):
{context if context else "Tidak ada informasi lokal yang cocok."}

PERTANYAAN PENGGUNA:
{user_input}
"""

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1200
        }
    }

    retryable_statuses = {429, 500, 502, 503, 504}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=timeout
            )

            if response.status_code in retryable_statuses:
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
            answer = " ".join(
                part["text"] for part in parts if "text" in part
            ).strip()
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


# ============================================================
# HYBRID CHATBOT DENGAN INTELLIGENT ROUTING
# ============================================================

def get_response_hybrid(user_input):
    normalized = preprocess(user_input)

    # Pencarian database lokal terstruktur sebelum klasifikasi intent.
    for pencarian in (cari_data_mata_kuliah, cari_dosen_pa, cari_data_dosen, cari_informasi_lain):
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


# ============================================================
# EVALUASI RULE-BASED VS TF-IDF
# ============================================================

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
    ("berapa suhu matahari", None)
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


# ============================================================
# TES KONEKSI GEMINI
# ============================================================

def test_gemini():
    print("\n[INFO] Model:", GEMINI_MODEL)
    answer = ask_gemini(
        "Jelaskan dalam dua kalimat apa fungsi chatbot akademik.",
        timeout=45
    )
    if answer:
        print("\n[BERHASIL] Gemini memberikan respons:")
        print(answer)
    else:
        print("\n[GAGAL] Periksa API Key, nama model, kuota, "
              "koneksi internet, dan detail error di atas.")


# ============================================================
# CHATBOT TERMINAL
# ============================================================

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

        response = get_response_hybrid(user_input)
        print("Bot:", response)
        print()


# ============================================================
# MENU UTAMA
# ============================================================

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
