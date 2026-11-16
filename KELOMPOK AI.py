import os
import re
import time
import random
import requests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CHATBOT LAYANAN AKADEMIK S1 TEKNIK INFORMATIKA UNP & ENSIKLOPEDIA AI
# Teknologi: Rule-Based + TF-IDF + Cosine Similarity + Gemini API
# Fakultas Teknik (FT) - Universitas Negeri Padang (UNP)
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

SIMILARITY_THRESHOLD = 0.38
MAX_RETRIES = 3
FALLBACK_RESPONSE = (
    "Maaf, pertanyaan Anda belum dapat dijawab oleh basis data lokal maupun asisten AI.\n"
    "Silakan konsultasikan langsung dengan Subbagian Akademik Fakultas Teknik UNP "
    "atau Dosen Pembimbing Akademik Anda di Kampus Air Tawar Padang."
)


# ============================================================
# 1. MODUL PEMBUAT TABEL & KOTAK TERMINAL (BOX DRAWING)
# ============================================================

def buat_tabel(headers, rows, title=None, max_widths=None):
    """
    Membuat tampilan tabel berbingkai kotak ASCII/Unicode yang rapi,
    sejajar, dan mudah dibaca di terminal.
    """
    if not rows:
        return "Tidak ada data yang ditemukan."
    if max_widths is None:
        max_widths = {}

    num_cols = len(headers)
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i in range(min(num_cols, len(row))):
            val_len = len(str(row[i]))
            if i in max_widths and val_len > max_widths[i]:
                val_len = max_widths[i]
            col_widths[i] = max(col_widths[i], val_len)

    total_w = sum(col_widths) + 3 * num_cols - 1

    lines = []
    if title:
        inner_w = total_w
        lines.append("┌" + "─" * (inner_w + 2) + "┐")
        lines.append("│ " + title.center(inner_w) + " │")
        lines.append("├" + "┬".join("─" * (w + 2) for w in col_widths) + "┤")
    else:
        lines.append("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")

    # Header
    head_str = "│ " + " │ ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(num_cols)) + " │"
    lines.append(head_str)
    lines.append("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")

    # Rows
    for row in rows:
        cells = []
        for i in range(num_cols):
            val = str(row[i]) if i < len(row) else ""
            if i in max_widths and len(val) > max_widths[i]:
                val = val[:max_widths[i]-3] + "..."
            cells.append(f"{val:<{col_widths[i]}}")
        lines.append("│ " + " │ ".join(cells) + " │")

    lines.append("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")
    return "\n".join(lines)


def buat_kotak(title, text, width=82):
    """
    Membungkus teks penjelasan ke dalam kotak berbingkai rapi
    dengan pemotongan kata otomatis (word-wrapping).
    """
    lines = []
    lines.append("┌" + "─" * (width - 2) + "┐")
    if title:
        lines.append("│ " + title.center(width - 4) + " │")
        lines.append("├" + "─" * (width - 2) + "┤")

    raw_lines = text.strip().split("\n")
    for raw in raw_lines:
        if not raw:
            lines.append("│ " + " " * (width - 4) + " │")
            continue
        while len(raw) > width - 4:
            split_idx = raw[:width - 4].rfind(" ")
            if split_idx == -1:
                split_idx = width - 4
            part = raw[:split_idx]
            lines.append("│ " + f"{part:<{width - 4}}" + " │")
            raw = raw[split_idx:].lstrip()
        lines.append("│ " + f"{raw:<{width - 4}}" + " │")

    lines.append("└" + "─" * (width - 2) + "┘")
    return "\n".join(lines)


# ============================================================
# 2. DATABASE AKADEMIK RESMI S1 TEKNIK INFORMATIKA FT UNP
# (100% INFORMATIKA SAJA - TANPA MATA KULIAH JURUSAN LAIN)
# ============================================================

FAKULTAS = {
    "kode": "FT-UNP",
    "nama": "Fakultas Teknik",
    "universitas": "Universitas Negeri Padang",
    "alamat": "Kampus Utama UNP Air Tawar, Jl. Prof. Dr. Hamka, Kota Padang, Sumatera Barat",
    "dekan": "Dr. Ir. Krismadinata, S.T., M.T.",
    "departemen": "Departemen Teknik Elektronika dan Informatika",
    "program_studi": [
        {
            "kode": "INF-S1",
            "nama": "S1 Teknik Informatika",
            "jenjang": "Sarjana (S1)",
            "gelar": "S.Kom. (Sarjana Komputer)",
            "akreditasi": "Unggul (BAN-PT / LAM INFOKOM)",
            "lama_studi": "8 Semester (4 Tahun)",
            "total_sks": 144,
            "ketua_prodi": "Dr. Raka Pratama, S.Kom., M.Kom.",
            "sekretaris_prodi": "Dina Kurniawati, S.T., M.Kom.",
            "bidang_kajian": [
                "Artificial Intelligence & Machine Learning (Sistem Cerdas)",
                "Software Engineering (Rekayasa Perangkat Lunak)",
                "Computer Network & Cyber Security (Jaringan & Keamanan)",
                "Data Science & Big Data Analytics (Sains Data)",
                "Cloud Computing & Internet of Things (IoT)"
            ]
        }
    ]
}

DOSEN = [
    {
        "nidn": "0003037903",
        "nama": "Dr. Asrul Huda, S.Kom., M.Kom.",
        "jabatan": "Dosen / Kepala Lab AI & Data Science",
        "bidang": "Artificial Intelligence (AI), Machine Learning, Data Mining, dan Deep Learning",
        "email": "asrul.huda@ft.unp.ac.id",
        "ruang": "Lab AI & Data Science Lt. 3 FT UNP",
        "pa": ["IF21-A"],
        "matkul_diampu": ["Artificial Intelligence (AI)", "Machine Learning", "Data Mining"]
    },
    {
        "nidn": "0004048104",
        "nama": "Dr. Ir. Zulhendra, S.Kom., M.Kom.",
        "jabatan": "Dosen Senior Informatika",
        "bidang": "Artificial Intelligence, Machine Learning, Computer Vision, dan Pengolahan Citra",
        "email": "zulhendra@ft.unp.ac.id",
        "ruang": "Gedung E7 Lantai 2 (R-204)",
        "pa": ["IF22-A"],
        "matkul_diampu": ["Machine Learning", "Pengolahan Citra Digital", "Computer Vision"]
    },
    {
        "nidn": "0001018001",
        "nama": "Dr. Raka Pratama, S.Kom., M.Kom.",
        "jabatan": "Ketua Program Studi S1 Teknik Informatika",
        "bidang": "Kecerdasan Buatan (AI), Knowledge Systems, dan Logika Informatika",
        "email": "raka.pratama@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 2 (Ruang Prodi IF-201)",
        "pa": ["IF24-A"],
        "matkul_diampu": ["Logika Informatika", "Teori Bahasa dan Otomata", "Topik Khusus AI"]
    },
    {
        "nidn": "0014147714",
        "nama": "Aditya Putra, S.Kom., M.Kom.",
        "jabatan": "Dosen / Peneliti AI & NLP",
        "bidang": "Artificial Intelligence, Deep Learning, Generative AI, dan NLP",
        "email": "aditya.putra@ft.unp.ac.id",
        "ruang": "Lab AI & Data Science Lt. 3 FT UNP",
        "pa": ["IF21-B"],
        "matkul_diampu": ["Praktikum Artificial Intelligence", "Deep Learning dan NLP"]
    },
    {
        "nidn": "0005057805",
        "nama": "Dr. Hansi Effendi, S.T., M.Kom.",
        "jabatan": "Dosen / Kepala Lab Jaringan",
        "bidang": "Jaringan Komputer, Keamanan Siber (Cyber Security), dan Cloud Computing",
        "email": "hansi.effendi@ft.unp.ac.id",
        "ruang": "Lab Jaringan Komputer Lt. 2 FT UNP",
        "pa": ["IF22-B"],
        "matkul_diampu": ["Jaringan Komputer", "Keamanan Informasi dan Kriptografi", "Cloud Security"]
    },
    {
        "nidn": "0002028202",
        "nama": "Dina Kurniawati, S.T., M.Kom.",
        "jabatan": "Sekretaris Program Studi",
        "bidang": "Rekayasa Perangkat Lunak (RPL), Manajemen Proyek TI, dan Software Quality",
        "email": "dina.kurniawati@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 2 (Ruang Prodi IF-202)",
        "pa": ["IF24-B"],
        "matkul_diampu": ["Rekayasa Perangkat Lunak (RPL)", "Proyek Perangkat Lunak"]
    },
    {
        "nidn": "0006068306",
        "nama": "Dedy Irfan, S.Pd., M.Kom.",
        "jabatan": "Dosen / Pembina Kemahasiswaan",
        "bidang": "Pemrograman Web, Fullstack Web Development, dan Web API",
        "email": "dedy.irfan@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 1 (R-105)",
        "pa": ["IF23-A"],
        "matkul_diampu": ["Pemrograman Web", "Pemrograman Berbasis Framework"]
    },
    {
        "nidn": "0007078007",
        "nama": "Fajar Hidayat, S.Kom., M.Cs.",
        "jabatan": "Dosen Informatika",
        "bidang": "Sistem Operasi, Arsitektur Komputer, dan Sistem Terdistribusi",
        "email": "fajar.hidayat@ft.unp.ac.id",
        "ruang": "Gedung E7 Lantai 1 (R-102)",
        "pa": ["IF23-B"],
        "matkul_diampu": ["Sistem Operasi", "Organisasi dan Arsitektur Komputer", "Sistem Terdistribusi"]
    },
    {
        "nidn": "0008088408",
        "nama": "Nadia Putri, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Data Science, Natural Language Processing (NLP), dan Big Data Analytics",
        "email": "nadia.putri@ft.unp.ac.id",
        "ruang": "Lab Data Science Lt. 3 FT UNP",
        "pa": ["IF23-C"],
        "matkul_diampu": ["Data Mining dan Business Intelligence", "Analisis Big Data"]
    },
    {
        "nidn": "0009097909",
        "nama": "Budi Santoso, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Algoritma dan Pemrograman, Struktur Data, dan Pemrograman Kompetitif",
        "email": "budi.santoso@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 2 (R-203)",
        "pa": ["IF25-A"],
        "matkul_diampu": ["Algoritma dan Pemrograman I", "Struktur Data dan Algoritma", "Desain Analisis Algoritma"]
    },
    {
        "nidn": "0010108110",
        "nama": "Andi Pratama, S.T., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Pengantar Informatika, Literasi Digital, dan Sistem Informasi",
        "email": "andi.pratama@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 1 (R-106)",
        "pa": ["IF25-B"],
        "matkul_diampu": ["Pengantar Teknik Informatika", "Literasi Digital", "Technopreneurship"]
    },
    {
        "nidn": "0011118211",
        "nama": "Rizki Maulana, S.T., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Internet of Things (IoT), Forensik Digital, dan Jaringan Komputer Lanjut",
        "email": "rizki.maulana@ft.unp.ac.id",
        "ruang": "Lab Jaringan Komputer Lt. 2 FT UNP",
        "pa": ["IF24-C"],
        "matkul_diampu": ["Praktikum Jaringan Komputer", "Internet of Things (IoT)", "Forensik Digital"]
    },
    {
        "nidn": "0012128012",
        "nama": "Siti Rahma, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Interaksi Manusia dan Komputer (IMK), UI/UX Design, dan Frontend Engineering",
        "email": "siti.rahma@ft.unp.ac.id",
        "ruang": "Lab Multimedia FT UNP",
        "pa": ["IF24-D"],
        "matkul_diampu": ["Interaksi Manusia dan Komputer (IMK)", "UI/UX Design"]
    },
    {
        "nidn": "0013138313",
        "nama": "Rina Amelia, S.Si., M.Kom.",
        "jabatan": "Dosen Matematika Informatika",
        "bidang": "Matematika Diskrit, Kalkulus, Aljabar Linear, dan Kriptografi",
        "email": "rina.amelia@ft.unp.ac.id",
        "ruang": "Gedung E7 Lantai 2 (R-205)",
        "pa": ["IF25-C"],
        "matkul_diampu": ["Kalkulus I", "Aljabar Linear dan Matriks", "Matematika Diskrit", "Metode Numerik"]
    },
    {
        "nidn": "0015158515",
        "nama": "Maya Lestari, S.Kom., M.T.",
        "jabatan": "Dosen Informatika",
        "bidang": "Sistem Basis Data, Manajemen Database Relasional, dan NoSQL",
        "email": "maya.lestari@ft.unp.ac.id",
        "ruang": "Lab Basis Data Lt. 2 FT UNP",
        "pa": [],
        "matkul_diampu": ["Sistem Basis Data I", "Sistem Basis Data Lanjut"]
    },
    {
        "nidn": "0016168116",
        "nama": "Yoga Saputra, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Pemrograman Berorientasi Objek (PBO), Pemrograman Mobile Android/Flutter",
        "email": "yoga.saputra@ft.unp.ac.id",
        "ruang": "Lab RPL Lt. 2 FT UNP",
        "pa": [],
        "matkul_diampu": ["Pemrograman Berorientasi Objek (PBO)", "Pemrograman Mobile"]
    },
    {
        "nidn": "0017178217",
        "nama": "Intan Permata, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Grafika Komputer, Pemrograman Game 2D/3D, dan Virtual Reality (VR)",
        "email": "intan.permata@ft.unp.ac.id",
        "ruang": "Lab Multimedia Lt. 3 FT UNP",
        "pa": [],
        "matkul_diampu": ["Grafika Komputer dan Pemrograman Game"]
    },
    {
        "nidn": "0018187818",
        "nama": "Dedi Firmansyah, S.T., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Komputasi Awan (Cloud Computing), DevOps, dan Server Administration",
        "email": "dedi.firmansyah@ft.unp.ac.id",
        "ruang": "Lab Cloud Computing Lt. 3 FT UNP",
        "pa": [],
        "matkul_diampu": ["Komputasi Awan (Cloud Computing)"]
    },
    {
        "nidn": "0019198619",
        "nama": "Laila Safitri, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Etika Profesi TI, Metodologi Penelitian Informatika, dan Hukum Siber",
        "email": "laila.safitri@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 2 (R-207)",
        "pa": [],
        "matkul_diampu": ["Metodologi Penelitian Informatika", "Etika Profesi dan Hukum Siber"]
    },
    {
        "nidn": "0020208420",
        "nama": "Dr. Dwi Kurniati, S.Kom., M.Kom.",
        "jabatan": "Dosen Informatika",
        "bidang": "Manajemen Proyek TI, Software Architecture, dan Rekayasa Kebutuhan",
        "email": "dwi.kurniati@ft.unp.ac.id",
        "ruang": "Gedung E6 Lantai 2 (R-208)",
        "pa": [],
        "matkul_diampu": ["Manajemen Proyek Perangkat Lunak"]
    }
]

DOSEN_PA = [
    {"kode_kelas": "IF25-A", "angkatan": 2025, "dosen": "Budi Santoso, S.Kom., M.Kom.", "email": "budi.santoso@ft.unp.ac.id"},
    {"kode_kelas": "IF25-B", "angkatan": 2025, "dosen": "Andi Pratama, S.T., M.Kom.", "email": "andi.pratama@ft.unp.ac.id"},
    {"kode_kelas": "IF25-C", "angkatan": 2025, "dosen": "Rina Amelia, S.Si., M.Kom.", "email": "rina.amelia@ft.unp.ac.id"},
    {"kode_kelas": "IF24-A", "angkatan": 2024, "dosen": "Dr. Raka Pratama, S.Kom., M.Kom.", "email": "raka.pratama@ft.unp.ac.id"},
    {"kode_kelas": "IF24-B", "angkatan": 2024, "dosen": "Dina Kurniawati, S.T., M.Kom.", "email": "dina.kurniawati@ft.unp.ac.id"},
    {"kode_kelas": "IF24-C", "angkatan": 2024, "dosen": "Rizki Maulana, S.T., M.Kom.", "email": "rizki.maulana@ft.unp.ac.id"},
    {"kode_kelas": "IF24-D", "angkatan": 2024, "dosen": "Siti Rahma, S.Kom., M.Kom.", "email": "siti.rahma@ft.unp.ac.id"},
    {"kode_kelas": "IF23-A", "angkatan": 2023, "dosen": "Dedy Irfan, S.Pd., M.Kom.", "email": "dedy.irfan@ft.unp.ac.id"},
    {"kode_kelas": "IF23-B", "angkatan": 2023, "dosen": "Fajar Hidayat, S.Kom., M.Cs.", "email": "fajar.hidayat@ft.unp.ac.id"},
    {"kode_kelas": "IF23-C", "angkatan": 2023, "dosen": "Nadia Putri, S.Kom., M.Kom.", "email": "nadia.putri@ft.unp.ac.id"},
    {"kode_kelas": "IF22-A", "angkatan": 2022, "dosen": "Dr. Ir. Zulhendra, S.Kom., M.Kom.", "email": "zulhendra@ft.unp.ac.id"},
    {"kode_kelas": "IF22-B", "angkatan": 2022, "dosen": "Dr. Hansi Effendi, S.T., M.Kom.", "email": "hansi.effendi@ft.unp.ac.id"},
    {"kode_kelas": "IF21-A", "angkatan": 2021, "dosen": "Dr. Asrul Huda, S.Kom., M.Kom.", "email": "asrul.huda@ft.unp.ac.id"},
    {"kode_kelas": "IF21-B", "angkatan": 2021, "dosen": "Aditya Putra, S.Kom., M.Kom.", "email": "aditya.putra@ft.unp.ac.id"}
]

RUANG = {
    "LAB-AI": {
        "nama": "Laboratorium Artificial Intelligence & Data Science",
        "lokasi": "Lantai 3 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "30 Workstation GPU RTX 4080, Server High Performance Computing, Smart Screen, AC"
    },
    "LAB-RPL": {
        "nama": "Laboratorium Rekayasa Perangkat Lunak (Software Engineering)",
        "lokasi": "Lantai 2 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "35 PC Core i7, Dual Monitor, Server Web Lokal, AC, Proyektor Interaktif"
    },
    "LAB-JARINGAN": {
        "nama": "Laboratorium Jaringan Komputer & Keamanan Siber",
        "lokasi": "Lantai 2 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "30 PC Praktikum, 6 Rack Server Cisco Routers & Switches, Mikrotik Kit, Firewall"
    },
    "LAB-BASISDATA": {
        "nama": "Laboratorium Basis Data & Sistem Informasi",
        "lokasi": "Lantai 2 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "35 PC Core i7, Server Oracle, PostgreSQL & MySQL Enterprise, AC"
    },
    "LAB-KOMPUTASI": {
        "nama": "Laboratorium Algoritma & Komputasi Dasar",
        "lokasi": "Lantai 1 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "40 PC Core i7, Lingkungan Linux Ubuntu & Windows, AC, Proyektor"
    },
    "LAB-MULTIMEDIA": {
        "nama": "Laboratorium Multimedia, Grafika, & Game Technology",
        "lokasi": "Lantai 3 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "30 PC GPU RTX, Wacom Pen Tablets, VR Headset, Sound Recording Kit"
    },
    "LAB-CLOUD": {
        "nama": "Laboratorium Cloud Computing, DevOps, & Internet of Things (IoT)",
        "lokasi": "Lantai 3 Gedung Laboratorium FT UNP Kampus Air Tawar",
        "fasilitas": "25 PC, Server Cluster Proxmox/Kubernetes, ESP32/Raspberry Pi IoT Kits"
    },
    "E6.101": {
        "nama": "Ruang Teori Informatika E6.101",
        "lokasi": "Gedung E6 Lantai 1 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 45 Kursi Kuliah, Proyektor Laser, Sound System, AC"
    },
    "E6.102": {
        "nama": "Ruang Teori Informatika E6.102",
        "lokasi": "Gedung E6 Lantai 1 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 40 Kursi Kuliah, Proyektor Laser, Sound System, AC"
    },
    "E6.201": {
        "nama": "Ruang Teori Informatika E6.201",
        "lokasi": "Gedung E6 Lantai 2 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 45 Kursi Kuliah, Smart Screen Interactive 75-inch, AC"
    },
    "E6.202": {
        "nama": "Ruang Teori Informatika E6.202",
        "lokasi": "Gedung E6 Lantai 2 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 40 Kursi Kuliah, Proyektor Laser, Sound System, AC"
    },
    "E7.301": {
        "nama": "Ruang Seminar Proposal & Hasil Tugas Akhir",
        "lokasi": "Gedung E7 Lantai 3 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 35 Kursi, Smart Projector, Meja Dosen Penguji, AC"
    },
    "E7.302": {
        "nama": "Ruang Sidang Munaqasyah Skripsi S1 Informatika",
        "lokasi": "Gedung E7 Lantai 3 Fakultas Teknik UNP",
        "fasilitas": "Kapasitas 30 Kursi, Meja Sidang Resmi, Sound System, AC"
    }
}

# ============================================================
# JADWAL MATA KULIAH S1 TEKNIK INFORMATIKA (LENGKAP SEMESTER 1-8)
# MATKUL ARTIFICIAL INTELLIGENCE & JADWAL AI TERCANTUM RESMI!
# ============================================================

_RAW_MK = [
    # SEMESTER 1
    ("INF101", "Pengantar Teknik Informatika", 2, 1, "Senin", "08.00-09.40", "E6.101", "Andi Pratama, S.T., M.Kom."),
    ("INF102", "Algoritma dan Pemrograman I", 3, 1, "Senin", "10.00-12.30", "LAB-KOMPUTASI", "Budi Santoso, S.Kom., M.Kom."),
    ("INF103", "Kalkulus I", 3, 1, "Selasa", "08.00-10.30", "E6.101", "Rina Amelia, S.Si., M.Kom."),
    ("INF104", "Logika Informatika", 2, 1, "Selasa", "10.40-12.20", "E6.102", "Dr. Raka Pratama, S.Kom., M.Kom."),
    ("INF105", "Organisasi dan Arsitektur Komputer", 3, 1, "Rabu", "08.00-10.30", "E6.102", "Fajar Hidayat, S.Kom., M.Cs."),
    ("INF106", "Literasi Digital & Komputasi", 2, 1, "Rabu", "10.40-12.20", "LAB-KOMPUTASI", "Andi Pratama, S.T., M.Kom."),
    ("INF107", "Bahasa Inggris untuk TI", 2, 1, "Kamis", "08.00-09.40", "E6.101", "Laila Safitri, S.Kom., M.Kom."),
    ("INF108", "Pendidikan Agama & Pancasila", 2, 1, "Jumat", "08.00-09.40", "E6.101", "Laila Safitri, S.Kom., M.Kom."),

    # SEMESTER 2
    ("INF201", "Struktur Data dan Algoritma", 3, 2, "Senin", "08.00-10.30", "LAB-KOMPUTASI", "Budi Santoso, S.Kom., M.Kom."),
    ("INF202", "Sistem Operasi", 3, 2, "Senin", "10.40-13.10", "LAB-KOMPUTASI", "Fajar Hidayat, S.Kom., M.Cs."),
    ("INF203", "Aljabar Linear dan Matriks", 3, 2, "Selasa", "08.00-10.30", "E6.101", "Rina Amelia, S.Si., M.Kom."),
    ("INF204", "Sistem Basis Data I", 3, 2, "Selasa", "10.40-13.10", "LAB-BASISDATA", "Maya Lestari, S.Kom., M.T."),
    ("INF205", "Algoritma dan Pemrograman II", 3, 2, "Rabu", "08.00-10.30", "LAB-KOMPUTASI", "Yoga Saputra, S.Kom., M.Kom."),
    ("INF206", "Statistika dan Teori Peluang", 3, 2, "Kamis", "08.00-10.30", "E6.102", "Rina Amelia, S.Si., M.Kom."),
    ("INF207", "Pendidikan Kewarganegaraan", 2, 2, "Jumat", "08.00-09.40", "E6.101", "Laila Safitri, S.Kom., M.Kom."),

    # SEMESTER 3
    ("INF301", "Jaringan Komputer", 3, 3, "Senin", "08.00-10.30", "LAB-JARINGAN", "Dr. Hansi Effendi, S.T., M.Kom."),
    ("INF302", "Pemrograman Web", 3, 3, "Senin", "10.40-13.10", "LAB-RPL", "Dedy Irfan, S.Pd., M.Kom."),
    ("INF303", "Pemrograman Berorientasi Objek (PBO)", 3, 3, "Selasa", "08.00-10.30", "LAB-RPL", "Yoga Saputra, S.Kom., M.Kom."),
    ("INF304", "Rekayasa Perangkat Lunak (RPL)", 3, 3, "Selasa", "10.40-13.10", "E6.201", "Dina Kurniawati, S.T., M.Kom."),
    ("INF305", "Matematika Diskrit", 3, 3, "Rabu", "08.00-10.30", "E6.201", "Rina Amelia, S.Si., M.Kom."),
    ("INF306", "Sistem Basis Data Lanjut", 3, 3, "Rabu", "10.40-13.10", "LAB-BASISDATA", "Maya Lestari, S.Kom., M.T."),
    ("INF307", "Interaksi Manusia dan Komputer (IMK)", 3, 3, "Kamis", "08.00-10.30", "LAB-MULTIMEDIA", "Siti Rahma, S.Kom., M.Kom."),
    ("INF308", "Praktikum Jaringan Komputer", 1, 3, "Jumat", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana, S.T., M.Kom."),

    # SEMESTER 4 (MATA KULIAH WAJIB KECERDASAN BUATAN / AI!)
    ("IF401", "Artificial Intelligence (AI)", 3, 4, "Senin", "08.00-10.30", "LAB-AI", "Dr. Asrul Huda, S.Kom., M.Kom."),
    ("IF402", "Desain dan Analisis Algoritma", 3, 4, "Senin", "10.40-13.10", "E6.201", "Budi Santoso, S.Kom., M.Kom."),
    ("IF403", "Pemrograman Mobile", 3, 4, "Selasa", "08.00-10.30", "LAB-RPL", "Yoga Saputra, S.Kom., M.Kom."),
    ("IF404", "Keamanan Informasi dan Kriptografi", 3, 4, "Selasa", "10.40-13.10", "LAB-JARINGAN", "Dr. Hansi Effendi, S.T., M.Kom."),
    ("IF405", "Teori Bahasa dan Otomata", 3, 4, "Rabu", "08.00-10.30", "E6.202", "Dr. Raka Pratama, S.Kom., M.Kom."),
    ("IF406", "Metode Numerik Komputasi", 3, 4, "Rabu", "10.40-13.10", "E6.202", "Rina Amelia, S.Si., M.Kom."),
    ("IF407", "Manajemen Proyek Perangkat Lunak", 2, 4, "Kamis", "08.00-09.40", "E6.201", "Dr. Dwi Kurniati, S.Kom., M.Kom."),
    ("IF408", "Praktikum Artificial Intelligence (AI)", 1, 4, "Jumat", "08.00-10.30", "LAB-AI", "Aditya Putra, S.Kom., M.Kom."),

    # SEMESTER 5 (AI LANJUT: MACHINE LEARNING & COMPUTER VISION)
    ("IF501", "Machine Learning", 3, 5, "Senin", "08.00-10.30", "LAB-AI", "Dr. Ir. Zulhendra, S.Kom., M.Kom."),
    ("IF502", "Data Mining dan Business Intelligence", 3, 5, "Senin", "10.40-13.10", "LAB-AI", "Nadia Putri, S.Kom., M.Kom."),
    ("IF503", "Pemrograman Berbasis Framework", 3, 5, "Selasa", "08.00-10.30", "LAB-RPL", "Dedy Irfan, S.Pd., M.Kom."),
    ("IF504", "Komputasi Awan (Cloud Computing)", 3, 5, "Selasa", "10.40-13.10", "LAB-CLOUD", "Dedi Firmansyah, S.T., M.Kom."),
    ("IF505", "Pengolahan Citra Digital (Computer Vision)", 3, 5, "Rabu", "08.00-10.30", "LAB-AI", "Dr. Ir. Zulhendra, S.Kom., M.Kom."),
    ("IF506", "Sistem Terdistribusi", 3, 5, "Rabu", "10.40-13.10", "E6.202", "Fajar Hidayat, S.Kom., M.Cs."),
    ("IF507", "Metodologi Penelitian Informatika", 2, 5, "Kamis", "08.00-09.40", "E6.201", "Laila Safitri, S.Kom., M.Kom."),
    ("IF508", "Internet of Things (IoT)", 2, 5, "Jumat", "08.00-09.40", "LAB-CLOUD", "Rizki Maulana, S.T., M.Kom."),

    # SEMESTER 6 (DEEP LEARNING, NLP, & CAPSTONE)
    ("IF601", "Deep Learning dan NLP", 3, 6, "Senin", "08.00-10.30", "LAB-AI", "Aditya Putra, S.Kom., M.Kom."),
    ("IF602", "Analisis Big Data", 3, 6, "Senin", "10.40-13.10", "LAB-AI", "Nadia Putri, S.Kom., M.Kom."),
    ("IF603", "Keamanan Siber dan Forensik Digital", 3, 6, "Selasa", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana, S.T., M.Kom."),
    ("IF604", "Grafika Komputer dan Pemrograman Game", 3, 6, "Selasa", "10.40-13.10", "LAB-MULTIMEDIA", "Intan Permata, S.Kom., M.Kom."),
    ("IF605", "Etika Profesi dan Hukum Siber", 2, 6, "Rabu", "08.00-09.40", "E6.201", "Laila Safitri, S.Kom., M.Kom."),
    ("IF606", "Technopreneurship (Kewirausahaan TI)", 2, 6, "Kamis", "08.00-09.40", "E6.101", "Andi Pratama, S.T., M.Kom."),
    ("IF607", "Proyek Perangkat Lunak Terintegrasi", 3, 6, "Jumat", "08.00-10.30", "LAB-RPL", "Dina Kurniawati, S.T., M.Kom."),

    # SEMESTER 7 (MAGANG / MBKM & MK PILIHAN AI)
    ("IF701", "Magang Industri / MBKM Informatika", 4, 7, "Senin", "08.00-12.00", "E7.301", "Dr. Raka Pratama, S.Kom., M.Kom."),
    ("IF702", "Kerja Praktik (KP) Informatika", 2, 7, "Selasa", "08.00-09.40", "E7.301", "Dina Kurniawati, S.T., M.Kom."),
    ("IF703", "Seminar Proposal Skripsi (Sempro)", 2, 7, "Rabu", "08.00-09.40", "E7.302", "Dr. Asrul Huda, S.Kom., M.Kom."),
    ("IF704", "MK Pilihan AI: Computer Vision & GenAI", 3, 7, "Kamis", "08.00-10.30", "LAB-AI", "Aditya Putra, S.Kom., M.Kom."),
    ("IF705", "MK Pilihan Siber: Ethical Hacking", 3, 7, "Jumat", "08.00-10.30", "LAB-JARINGAN", "Dr. Hansi Effendi, S.T., M.Kom."),

    # SEMESTER 8 (TUGAS AKHIR / SKRIPSI)
    ("IF801", "Skripsi / Tugas Akhir Informatika", 6, 8, "Senin", "08.00-11.00", "E7.302", "Dr. Raka Pratama, S.Kom., M.Kom."),
    ("IF802", "Seminar Hasil (Semhas)", 1, 8, "Rabu", "09.00-10.40", "E7.302", "Dina Kurniawati, S.T., M.Kom."),
    ("IF803", "Sidang Munaqasyah Skripsi (S.Kom.)", 1, 8, "Kamis", "09.00-11.30", "E7.302", "Dr. Asrul Huda, S.Kom., M.Kom.")
]

MATA_KULIAH = []
for row in _RAW_MK:
    kode, nama, sks, semester, hari, jam, ruang, dosen = row
    MATA_KULIAH.append({
        "kode": kode,
        "nama": nama,
        "sks": sks,
        "semester": semester,
        "hari": hari,
        "jam": jam,
        "ruang": ruang,
        "dosen": dosen,
        "prodi": "S1 Teknik Informatika FT UNP"
    })

KURIKULUM = {}
for m in MATA_KULIAH:
    KURIKULUM.setdefault(m["semester"], []).append(m)

UKT_DATA = [
    ("Kelompok 1", "Rp 500.000", "Mahasiswa dari keluarga pra-sejahtera penerima bantuan khusus"),
    ("Kelompok 2", "Rp 1.000.000", "Mahasiswa dengan penghasilan kotor orang tua <= Rp 1.500.000"),
    ("Kelompok 3", "Rp 2.500.000", "Penghasilan kotor orang tua Rp 1.500.000 - Rp 3.000.000"),
    ("Kelompok 4", "Rp 3.500.000", "Penghasilan kotor orang tua Rp 3.000.000 - Rp 5.000.000"),
    ("Kelompok 5", "Rp 4.800.000", "Penghasilan kotor orang tua Rp 5.000.000 - Rp 7.500.000"),
    ("Kelompok 6", "Rp 5.800.000", "Penghasilan kotor orang tua Rp 7.500.000 - Rp 10.000.000"),
    ("Kelompok 7", "Rp 6.800.000", "Penghasilan kotor orang tua Rp 10.000.000 - Rp 15.000.000"),
    ("Kelompok 8", "Rp 7.500.000", "Penghasilan kotor orang tua > Rp 15.000.000 / Golongan Mandiri")
]

KALENDER_AKADEMIK_DATA = [
    ("Januari", "Pembayaran UKT Semester Genap dan Pengisian KRS Online di portal.unp.ac.id"),
    ("Februari", "Awal Perkuliahan dan Praktikum Semester Genap di Kampus Air Tawar"),
    ("Maret", "Batas Akhir Revisi KRS dan Perkuliahan Reguler"),
    ("April", "Ujian Tengah Semester (UTS) Genap"),
    ("Mei", "Pelaksanaan Perkuliahan Lanjutan dan Penyelesaian Proyek Lab"),
    ("Juni", "Ujian Akhir Semester (UAS) Genap dan Input Nilai KHS"),
    ("Juli", "Libur Semester Genap dan Pendaftaran Semester Antara (SP)"),
    ("Agustus", "Pembayaran UKT Semester Ganjil dan Pengisian KRS Mahasiswa S1 Informatika"),
    ("September", "Awal Perkuliahan Semester Ganjil dan Wisuda UNP"),
    ("Oktober", "Perkuliahan Reguler dan Praktikum Laboratorium Komputer FT UNP"),
    ("November", "Ujian Tengah Semester (UTS) Ganjil dan Seminar Proposal"),
    ("Desember", "Ujian Akhir Semester (UAS) Ganjil dan Input Nilai KHS")
]

BEASISWA_DATA = [
    ("KIP Kuliah Kemendikbudristek", "Bebas UKT + Uang Saku", "Mahasiswa pra-sejahtera berprestasi terdaftar di DTKS"),
    ("Beasiswa Bank Indonesia (BI)", "Bantuan Dana Rp 12 Jt/Thn", "Minimal semester 3, IPK >= 3.00, aktif organisasi"),
    ("Beasiswa BAZNAS UNP/Sumbar", "Bantuan Biaya UKT", "Mahasiswa muslim memenuhi 8 asnaf mustahik, IPK >= 2.75"),
    ("Beasiswa Bank Nagari & CSR", "Bantuan Biaya Pendidikan", "Mahasiswa berprestasi akademik FT UNP, IPK >= 3.25"),
    ("Djarum Beasiswa Plus", "Dana Pendidikan + Pelatihan", "Mahasiswa semester 4, IPK >= 3.20, aktif berprestasi")
]


# ============================================================
# 3. KNOWLEDGE BASE PERCAKAPAN, AKADEMIK, & KECERDASAN BUATAN
# ============================================================

knowledge_base = {
    "greeting": {
        "patterns": [
            "halo", "hai", "hi", "hello", "selamat pagi", "selamat siang",
            "selamat sore", "selamat malam", "assalamualaikum", "permisi",
            "pagi min", "siang min", "sore min", "halo bot"
        ],
        "responses": [
            "Halo! Saya Chatbot Layanan Akademik S1 Teknik Informatika Fakultas Teknik "
            "Universitas Negeri Padang (UNP) & Pusat Informasi AI.\n\n"
            "Saya siap membantu Anda dengan informasi:\n"
            "• Jadwal Kuliah Informatika (Senin - Jumat, termasuk jadwal AI & Praktikum)\n"
            "• Profil Dosen Informatika & Dosen Bidang AI (Kecerdasan Buatan)\n"
            "• Dosen Pembimbing Akademik (PA) per angkatan\n"
            "• Kurikulum Informatika Semester 1 s.d. 8\n"
            "• Ruangan & Laboratorium FT UNP (Lab AI, RPL, Jaringan, Basis Data, dll.)\n"
            "• Aturan Akademik (KRS, KHS, UKT, Cuti, Skripsi, Wisuda UNP)\n"
            "• Materi dan Teori Kecerdasan Buatan (Machine Learning, Deep Learning, NLP, Computer Vision, Sistem Pakar, dll.)"
        ]
    },

    "jadwal_kuliah": {
        "patterns": [
            "jadwal kuliah", "jadwal kelas", "kapan kuliah", "jam berapa kuliah",
            "jadwal perkuliahan", "jadwal matkul informatika", "jadwal informatika",
            "jadwal kuliah ti", "daftar jadwal", "lihat jadwal kuliah"
        ],
        "responses": [
            # Respon jadwal di-handle otomatis via database tabular!
            "JADWAL PERKULIAHAN INFORMATIKA"
        ]
    },

    "krs": {
        "patterns": [
            "krs", "kartu rencana studi", "isi krs", "pengisian krs", "jadwal krs unp",
            "ubah krs", "revisi krs", "ambil mata kuliah", "alur pengisian krs"
        ],
        "responses": [
            "PROSEDUR PENGISIAN KRS ONLINE S1 TEKNIK INFORMATIKA UNP:\n\n"
            "1. Pembayaran UKT: Pastikan telah melunasi UKT semester berjalan sehingga status registrasi menjadi AKTIF.\n"
            "2. Login Portal: Akses https://portal.unp.ac.id menggunakan NIM dan password akun mahasiswa Anda.\n"
            "3. Menu KRS: Pilih menu 'Akademik' -> 'Kartu Rencana Studi (KRS)'.\n"
            "4. Pemilihan Mata Kuliah: Pilih mata kuliah Informatika sesuai semester kurikulum Anda. Perhatikan prasyarat dan jangan sampai bentrok jam atau ruang praktikum.\n"
            "5. Batas SKS: Disesuaikan dengan IPS semester sebelumnya (IPS >= 3.00 dapat mengambil maksimal 24 SKS).\n"
            "6. Persetujuan Dosen PA: Ajukan persetujuan (approval) ke Dosen Pembimbing Akademik (Dosen PA) masing-masing.\n"
            "7. Cetak KRS: Unduh dan simpan bukti lembar KRS yang telah disetujui Dosen PA."
        ]
    },

    "khs": {
        "patterns": [
            "khs", "kartu hasil studi", "nilai semester", "lihat nilai",
            "hasil studi", "kapan nilai keluar", "cek khs unp", "komplain nilai"
        ],
        "responses": [
            "INFORMASI KHS (KARTU HASIL STUDI) MAHASISWA UNP:\n\n"
            "1. Akses KHS: Nilai semester dapat dilihat di portal akademik mahasiswa (https://portal.unp.ac.id) pada menu 'Nilai Semester / KHS'.\n"
            "2. Rentang Nilai: Nilai dinilai dengan huruf mutu A (4.00), A- (3.60), B+ (3.30), B (3.00), B- (2.60), C+ (2.30), C (2.00), D (1.00), E (0.00).\n"
            "3. Periode Input Nilai: Dosen menginput nilai akhir sesuai jadwal kalender akademik pada bulan Juni (Genap) dan Desember (Ganjil).\n"
            "4. Perbaikan Nilai: Jika terdapat kekeliruan atau nilai belum keluar (tanda BL), segera hubungi dosen pengampu mata kuliah sebelum masa sanggah berakhir."
        ]
    },

    "ukt": {
        "patterns": [
            "ukt", "uang kuliah tunggal", "pembayaran kuliah", "bayar kuliah",
            "tagihan ukt unp", "keringanan ukt", "penurunan ukt", "kelompok ukt"
        ],
        "responses": [
            "INFORMASI BIAYA & UKT S1 TEKNIK INFORMATIKA FT UNP"
        ]
    },

    "kalender_akademik": {
        "patterns": [
            "kalender akademik", "kalender kuliah unp", "awal semester", "akhir semester",
            "jadwal uts unp", "jadwal uas unp", "libur semester unp"
        ],
        "responses": [
            "AGENDA KALENDER AKADEMIK UNIVERSITAS NEGERI PADANG"
        ]
    },

    "dosen_pa": {
        "patterns": [
            "dosen pa", "pembimbing akademik", "dosen wali", "siapa pa saya",
            "konsultasi pa", "bimbingan akademik", "daftar dosen pa"
        ],
        "responses": [
            "DAFTAR DOSEN PEMBIMBING AKADEMIK (PA) S1 INFORMATIKA FT UNP"
        ]
    },

    "ruang_kuliah": {
        "patterns": [
            "ruang kuliah", "lokasi kelas", "kelas di ruang mana", "ruang lab",
            "daftar ruang", "fasilitas lab informatika", "gedung e6", "gedung e7"
        ],
        "responses": [
            "DAFTAR RUANG KULIAH & LABORATORIUM S1 TEKNIK INFORMATIKA FT UNP"
        ]
    },

    "cuti_akademik": {
        "patterns": [
            "cuti kuliah", "cuti akademik unp", "izin tidak kuliah", "berhenti sementara",
            "syarat cuti unp", "prosedur cuti unp"
        ],
        "responses": [
            "KETENTUAN CUTI AKADEMIK UNIVERSITAS NEGERI PADANG:\n\n"
            "1. Telah menyelesaikan perkuliahan aktif minimal 2 semester awal (semester 1 & 2 tidak diperbolehkan cuti).\n"
            "2. Maksimal cuti akademik adalah 2 semester berturut-turut atau maksimal 4 semester secara kumulatif.\n"
            "3. Pengajuan diajukan secara online di portal.unp.ac.id sebelum perkuliahan semester dimulai.\n"
            "4. Memerlukan persetujuan Dosen PA, Ketua Departemen Elektronika & Informatika, dan Dekan FT UNP.\n"
            "5. Selama masa cuti resmi, mahasiswa dibebaskan dari tagihan UKT dan masa cuti tidak dihitung dalam batas masa studi kelulusan."
        ]
    },

    "lokasi_kampus": {
        "patterns": [
            "lokasi kampus", "alamat unp", "dimana unp", "alamat universitas negeri padang",
            "lokasi fakultas teknik unp", "kampus unp air tawar"
        ],
        "responses": [
            "LOKASI KAMPUS FAKULTAS TEKNIK UNIVERSITAS NEGERI PADANG (UNP):\n\n"
            "• Alamat Utama: Jl. Prof. Dr. Hamka, Air Tawar Barat, Kec. Padang Utara, Kota Padang, Sumatera Barat 25171.\n"
            "• Lokasi Fakultas Teknik (FT UNP): Terletak di sebelah barat kampus utama UNP, dekat dengan Gedung Rektorat dan Auditorium UNP.\n"
            "• Gedung Perkuliahan Informatika: Gedung E6, Gedung E7, dan Gedung Laboratorium Komputer Terpadu FT UNP.\n"
            "• Transportasi: Dilayani halte Trans Padang Koridor 1 (Halte UNP Air Tawar) tepat di depan gerbang utama kampus."
        ]
    },

    "kontak_admin": {
        "patterns": [
            "kontak admin", "hubungi admin", "nomor admin unp", "kontak akademik ft unp",
            "email informatika unp", "call center unp"
        ],
        "responses": [
            "LAYANAN & KONTAK RESMI S1 TEKNIK INFORMATIKA FT UNP:\n\n"
            "• Website Resmi UNP: https://unp.ac.id\n"
            "• Website Fakultas Teknik: https://ft.unp.ac.id\n"
            "• Portal Akademik Mahasiswa: https://portal.unp.ac.id\n"
            "• Email Program Studi: informatika@ft.unp.ac.id\n"
            "• Kantor Pelayanan: Subbagian Tata Usaha & Akademik FT UNP, Gedung Dekanat Lantai 1, Jam Layanan: Senin-Jumat 07.30 - 16.00 WIB."
        ]
    },

    "skripsi_tugas_akhir": {
        "patterns": [
            "skripsi", "tugas akhir", "proposal skripsi", "sempro", "seminar proposal",
            "sidang skripsi", "ujian skripsi", "munaqasyah", "syarat skripsi"
        ],
        "responses": [
            "TAHAPAN SKRIPSI / TUGAS AKHIR S1 TEKNIK INFORMATIKA FT UNP:\n\n"
            "1. Prasyarat: Telah menyelesaikan minimal 120 SKS dengan IPK >= 2.00, lulus Metodologi Penelitian Informatika, dan tidak ada nilai E.\n"
            "2. Pengajuan Topik: Mengajukan judul ke Koordinator Skripsi (Topik unggulan: Artificial Intelligence, Machine Learning, Computer Vision, IoT, Keamanan Siber, Web/Mobile Engineering).\n"
            "3. Pembagian Pembimbing: Ditetapkan Dosen Pembimbing 1 dan Dosen Pembimbing 2.\n"
            "4. Seminar Proposal (Sempro): Ujian kelayakan rancangan penelitian di hadapan tim penguji.\n"
            "5. Pengembangan Sistem & Bimbingan: Minimal 8 kali bimbingan per dosen pembimbing.\n"
            "6. Seminar Hasil (Semhas): Pengujian produk perangkat lunak dan analisis hasil eksperimen.\n"
            "7. Sidang Munaqasyah: Ujian akhir komprehensif kelulusan Sarjana Komputer (S.Kom.)."
        ]
    },

    "wisuda": {
        "patterns": [
            "wisuda", "pendaftaran wisuda unp", "syarat wisuda unp", "jadwal wisuda unp",
            "yudisium unp", "syarat sarjana komputer", "ijazah unp"
        ],
        "responses": [
            "YUDISIUM DAN WISUDA UNIVERSITAS NEGERI PADANG (UNP):\n\n"
            "• Yudisium: Penetapan status kelulusan setelah tuntas 144 SKS, bebas perpustakaan UNP, dan bebas laboratorium FT UNP.\n"
            "• Periode Wisuda: Dilaksanakan 4 kali dalam setahun (Maret, Juni, September, dan Desember) bertempat di Auditorium Utama UNP Air Tawar.\n"
            "• Syarat Wisuda: Mengunggah naskah skripsi ke repositori e-theses UNP, artikel ilmiah/jurnal, pasfoto ijazah, dan bebas kewajiban keuangan/SPP.\n"
            "• Gelar Lulusan: Sarjana Komputer (S.Kom.)."
        ]
    },

    "beasiswa": {
        "patterns": [
            "beasiswa", "pendaftaran beasiswa unp", "syarat beasiswa", "kip kuliah unp",
            "beasiswa bank indonesia", "beasiswa baznas unp", "beasiswa prestasi unp"
        ],
        "responses": [
            "PROGRAM BEASISWA UNIVERSITAS NEGERI PADANG"
        ]
    },

    "praktikum": {
        "patterns": [
            "praktikum", "jadwal lab", "tata tertib laboratorium", "asisten praktikum",
            "aslab", "laporan praktikum", "responsi lab"
        ],
        "responses": [
            "TATA TERTIB PRAKTIKUM LABORATORIUM TEKNIK INFORMATIKA FT UNP:\n\n"
            "1. Pakaian & Kerapian: Wajib berpakaian rapi berkerah, memakai sepatu tertutup, dan mengenakan kartu tanda laboratorium.\n"
            "2. Waktu Hadir: Hadir tepat waktu dengan toleransi keterlambatan maksimal 10 menit.\n"
            "3. Kebersihan & Keamanan: Dilarang membawa makanan/minuman ke dalam laboratorium komputer dan dilarang mengubah konfigurasi perangkat keras tanpa izin.\n"
            "4. Penugasan: Setiap modul praktikum disertai Tugas Pendahuluan, Jurnal Praktikum, dan Laporan Akhir yang dikumpulkan melalui e-learning.\n"
            "5. Kelulusan: Wajib memenuhi kehadiran 100% dan mengikuti ujian responsi praktikum."
        ]
    },

    "presensi": {
        "patterns": [
            "presensi", "absensi", "kehadiran kuliah", "minimal kehadiran unp",
            "izin tidak hadir", "sakit kuliah", "persentase kehadiran"
        ],
        "responses": [
            "KETENTUAN PRESENSI KULIAH UNIVERSITAS NEGERI PADANG:\n\n"
            "• Minimal Kehadiran: Mahasiswa wajib hadir minimal 75% dari total tatap muka perkuliahan (minimal 12 dari 16 kali pertemuan).\n"
            "• Konsekuensi: Kehadiran di bawah 75% menyebabkan mahasiswa TIDAK BERHAK mengikuti Ujian Akhir Semester (UAS) dan otomatis memperoleh nilai akhir E.\n"
            "• Presensi Digital: Dicatat melalui portal presensi QR Code UNP atau lembar presensi dosen di kelas.\n"
            "• Surat Izin: Surat sakit dokter atau dispensasi resmi wajib diserahkan maksimal 7 hari setelah ketidakhadiran."
        ]
    },

    "wifi_kampus": {
        "patterns": [
            "wifi unp", "internet unp", "akun wifi unp", "ssid unp", "eduroam unp",
            "login wifi unp", "cara konek wifi unp"
        ],
        "responses": [
            "PANDUAN WI-FI KAMPUS UNIVERSITAS NEGERI PADANG:\n\n"
            "1. SSID Resmi: Pilih jaringan 'UNP-Wifi' atau 'eduroam' di area Fakultas Teknik UNP.\n"
            "2. Login Captive Portal: Buka peramban (browser) Anda, masukkan NIM sebagai username dan password portal akademik Anda.\n"
            "3. Eduroam: Jaringan 'eduroam' memungkinkan mahasiswa UNP mengakses internet gratis di ribuan universitas mitra di seluruh dunia dengan login akun email @mhs.unp.ac.id.\n"
            "4. Kendala Akses: Jika gagal terhubung, lupakan jaringan (forget network) lalu sambungkan ulang atau kunjungi UPT Komputer UNP di Gedung Perpustakaan Pusat."
        ]
    },

    "terima_kasih": {
        "patterns": [
            "terima kasih", "makasih", "thanks", "thank you", "terima kasih banyak",
            "makasih min", "tarimo kasih", "syukron", "terimakasih kak"
        ],
        "responses": [
            "Sama-sama! Senang bisa membantu mahasiswa Teknik Informatika UNP. "
            "Tetap semangat dalam perkuliahan dan riset Artificial Intelligence Anda!"
        ]
    },

    "goodbye": {
        "patterns": [
            "bye", "sampai jumpa", "keluar dari bot", "exit", "quit",
            "selamat tinggal", "sampai bertemu lagi", "selesai"
        ],
        "responses": [
            "Sampai jumpa lagi! Semoga sukses dalam studi di S1 Teknik Informatika FT UNP. "
            "Ketik pertanyaan kapan saja saat membutuhkan bantuan!"
        ]
    },

    # --------------------------------------------------------
    # ENSIKLOPEDIA TEORI KECERDASAN BUATAN / ARTIFICIAL INTELLIGENCE
    # --------------------------------------------------------
    "ai_definisi": {
        "patterns": [
            "apa itu ai", "pengertian ai", "definisi kecerdasan buatan",
            "apa itu kecerdasan buatan", "sejarah ai", "konsep dasar ai",
            "jelaskan apa itu ai", "mengapa ai penting", "turing test",
            "siapa bapak ai", "definisi artificial intelligence", "apa itu artificial intelegent"
        ],
        "responses": [
            "PENGERTIAN DAN KONSEP DASAR KECERDASAN BUATAN (ARTIFICIAL INTELLIGENCE):\n\n"
            "1. Definisi:\n"
            "Kecerdasan Buatan (Artificial Intelligence / AI) adalah cabang ilmu komputer yang "
            "berfokus pada perancangan sistem dan agen cerdas yang mampu meniru fungsi kognitif manusia, "
            "seperti kemampuan belajar (learning), bernalar (reasoning), mengambil keputusan (decision making), "
            "memahami bahasa alami (NLP), dan mengenali objek visual (computer vision).\n\n"
            "2. Tokoh & Sejarah:\n"
            "• Tahun 1950: Alan Turing memperkenalkan 'Turing Test' untuk menguji apakah mesin dapat menunjukkan perilaku cerdas setara manusia.\n"
            "• Tahun 1956: Istilah 'Artificial Intelligence' pertama kali diresmikan oleh John McCarthy dalam Dartmouth Summer Research Conference.\n"
            "• Era Modern: Berkembang pesat berkat komputasi GPU paralel, Big Data, dan Deep Learning.\n\n"
            "3. Klasifikasi AI:\n"
            "• Narrow AI (Weak AI): AI yang berfokus pada satu tugas spesifik (contoh: Face Recognition, ChatGPT, Siri, Kendaraan Otonom).\n"
            "• General AI (AGI): Kecerdasan mesin yang setara dengan seluruh kapasitas intelektual manusia (tahap riset masa depan).\n"
            "• Super AI (ASI): AI hipotesis yang melampaui seluruh kecerdasan manusia di segala dimensi."
        ]
    },

    "ai_cabang": {
        "patterns": [
            "cabang ai", "bidang ai", "sub bidang kecerdasan buatan",
            "apa saja cabang ai", "cabang kecerdasan buatan", "lingkup ai"
        ],
        "responses": [
            "CABANG-CABANG UTAMA DALAM KECERDASAN BUATAN (AI):\n\n"
            "1. Machine Learning (ML): Teknik di mana mesin belajar mengenali pola dari data untuk melakukan prediksi atau klasifikasi.\n"
            "2. Deep Learning (DL): Sub-bidang ML berbasis Jaringan Syaraf Tiruan dalam (Multi-layer Neural Network) untuk data kompleks (gambar, suara, teks).\n"
            "3. Natural Language Processing (NLP): Memungkinkan komputer membaca, mengerti makna bahasa manusia, dan merespon teks secara alami.\n"
            "4. Computer Vision (Visi Komputer): Kemampuan komputer menganalisis citra visual atau video digital untuk mendeteksi objek dan wajah.\n"
            "5. Sistem Pakar (Expert Systems): Program berbasis aturan logika (IF-THEN) yang mengadopsi kepakaran manusia untuk diagnosa dan solusi masalah.\n"
            "6. Robotika & Sistem Cerdas Otonom: Penggabungan AI dan mekanika perangkat keras untuk navigasi dan aksi fisik di dunia nyata.\n"
            "7. Fuzzy Logic & Algoritma Evolusioner: Logika samar untuk menangani ketidakpastian dan Algoritma Genetika untuk masalah optimasi global."
        ]
    },

    "ai_machine_learning": {
        "patterns": [
            "machine learning", "apa itu machine learning", "definisi ml",
            "jenis machine learning", "supervised learning", "unsupervised learning",
            "reinforcement learning", "pembelajaran mesin", "perbedaan supervised dan unsupervised"
        ],
        "responses": [
            "PARADIGMA PEMBELAJARAN MESIN (MACHINE LEARNING):\n\n"
            "Machine Learning adalah proses melatih algoritma komputasi menggunakan data historis "
            "sehingga sistem mampu membuat keputusan atau prediksi pada data baru tanpa diprogram langkah demi langkah.\n\n"
            "3 KATEGORI UTAMA MACHINE LEARNING:\n"
            "1. Supervised Learning (Pembelajaran Terarah):\n"
            "   • Data latih memiliki pasangan input (X) dan label target yang benar (Y).\n"
            "   • Kasus: Klasifikasi (kategori diskrit) dan Regresi (angka kontinu).\n"
            "   • Contoh: Prediksi kelulusan mahasiswa, klasifikasi email spam, estimasi harga rumah.\n\n"
            "2. Unsupervised Learning (Pembelajaran Tak Terarah):\n"
            "   • Data latih tidak memiliki label target. Model mencari struktur alami atau kelompok data sendiri.\n"
            "   • Kasus: Clustering (pengelompokan) dan Reduksi Dimensi.\n"
            "   • Contoh: Segmentasi profil mahasiswa, K-Means clustering, PCA.\n\n"
            "3. Reinforcement Learning (Pembelajaran Penguatan):\n"
            "   • Agen cerdas belajar dari interaksi lingkungan secara trial-and-error berdasarkan sistem Reward (hadiah) dan Penalty (hukuman).\n"
            "   • Contoh: AI Game (AlphaGo, Chess Bot), navigasi robot industri, mobil otonom."
        ]
    },

    "ai_algoritma_ml": {
        "patterns": [
            "algoritma machine learning", "algoritma ml", "decision tree",
            "random forest", "svm", "support vector machine", "k-means",
            "knn", "k-nearest neighbors", "naive bayes", "linear regression"
        ],
        "responses": [
            "ALGORITMA-ALGORITMA POPULER DALAM MACHINE LEARNING:\n\n"
            "• K-Nearest Neighbors (KNN): Mengklasifikasikan data baru berdasarkan mayoritas label dari 'k' tetangga terdekat dengan metrik jarak Euclidean.\n"
            "• Naive Bayes: Algoritma klasifikasi probabilistik berbasis Teorema Bayes dengan asumsi independensi fitur. Sangat cepat untuk klasifikasi teks.\n"
            "• Decision Tree: Struktur pohon keputusan berbasis Information Gain / Gini Impurity yang mudah diinterpretasikan manusia.\n"
            "• Random Forest: Metode ensemble yang menggabungkan puluhan hingga ratusan Decision Tree (Bagging) untuk akurasi tinggi dan tahan terhadap overfitting.\n"
            "• Support Vector Machine (SVM): Mencari bidang pemisah (hyperplane) berdimensi tinggi yang memaksimalkan jarak (margin) antar kelas.\n"
            "• K-Means Clustering: Mengelompokkan data ke dalam 'k' kelompok dengan memperbarui posisi titik pusat (centroid) secara iteratif."
        ]
    },

    "ai_deep_learning": {
        "patterns": [
            "deep learning", "apa itu deep learning", "jaringan syaraf tiruan",
            "neural network", "ann", "cnn", "rnn", "lstm", "backpropagation",
            "fungsi aktivasi", "relu", "sigmoid"
        ],
        "responses": [
            "DEEP LEARNING & JARINGAN SYARAF TIRUAN (NEURAL NETWORKS):\n\n"
            "1. Definisi:\n"
            "Deep Learning adalah cabang Machine Learning yang menggunakan Artificial Neural Networks dengan banyak lapisan tersembunyi (hidden layers). "
            "Deep Learning mampu melakukan 'Automatic Feature Extraction' langsung dari data mentah (raw pixels, audio, teks).\n\n"
            "2. Arsitektur Utama:\n"
            "• Artificial Neural Network (ANN / Multi-Layer Perceptron): Terdiri dari Input Layer, Hidden Layer berbobot, dan Output Layer.\n"
            "• Convolutional Neural Network (CNN): Dirancang khusus untuk citra digital menggunakan lapisan Convolution dan Pooling untuk mendeteksi fitur visual.\n"
            "• Recurrent Neural Network (RNN) & LSTM: Memiliki memori sekuensial berulang untuk memproses data berurutan waktu (time-series, teks, suara).\n\n"
            "3. Mekanisme Pelatihan:\n"
            "• Forward Propagation: Menghitung nilai luaran berdasarkan bobot dan fungsi aktivasi (ReLU, Sigmoid, Softmax).\n"
            "• Loss Function: Menghitung selisih error antara hasil prediksi dan target nyata.\n"
            "• Backpropagation: Menghitung gradien parsial error dan memperbarui bobot menggunakan optimizer (Adam, SGD, RMSprop)."
        ]
    },

    "ai_nlp": {
        "patterns": [
            "nlp", "natural language processing", "pemrosesan bahasa alami",
            "apa itu nlp", "text mining", "preprocessing teks", "tokenisasi",
            "stemming", "stopwords", "lemmatization", "word2vec"
        ],
        "responses": [
            "NATURAL LANGUAGE PROCESSING (NLP) — PEMROSESAN BAHASA ALAMI:\n\n"
            "1. Pengertian:\n"
            "NLP adalah cabang AI yang menjembatani interaksi manusia dan komputer menggunakan bahasa alami sehari-hari. "
            "Komputer mengubah teks mentah menjadi representasi numerik matematis agar dapat dipahami maknanya.\n\n"
            "2. Tahapan Preprocessing Teks dalam NLP:\n"
            "• Case Folding: Mengubah seluruh karakter menjadi huruf kecil (lowercase).\n"
            "• Data Cleaning: Menghapus tanda baca, angka, simbol, URL, dan karakter liar menggunakan Regular Expression (Regex).\n"
            "• Tokenizing: Memecah kalimat panjang menjadi unit-unit kata (tokens).\n"
            "• Stopwords Removal (Filtering): Membuang kata umum yang minim informasi (contoh: yang, dan, di, dari, ini, itu).\n"
            "• Stemming: Menghilangkan imbuhan kata menuju kata dasar (contoh: 'perkuliahan' -> 'kuliah').\n\n"
            "3. Representasi Vektor Teks:\n"
            "• TF-IDF (Term Frequency - Inverse Document Frequency): Membobot kata penting berdasarkan keunikan dokumen.\n"
            "• Word Embeddings (Word2Vec, FastText, BERT): Memetakan kata ke dalam ruang vektor kontinu berdimensi tinggi yang mempertahankan makna semantik."
        ]
    },

    "ai_tfidf_cosine": {
        "patterns": [
            "apa itu tf idf", "tf-idf", "cara kerja tf idf", "cosine similarity",
            "rumus tf idf", "rumus cosine similarity", "bagaimana chatbot ini bekerja",
            "arsitektur chatbot ini", "similarity threshold"
        ],
        "responses": [
            "CARA KERJA SISTEM TF-IDF & COSINE SIMILARITY PADA CHATBOT INI:\n\n"
            "Chatbot ini menggunakan pendekatan Temu Kembali Informasi (Information Retrieval) dengan dua formula matematika:\n\n"
            "1. TF-IDF (Term Frequency - Inverse Document Frequency):\n"
            "   • TF(t, d): Frekuensi kemunculan kata kunci 't' dalam pertanyaan 'd'.\n"
            "   • IDF(t, D) = log( N / DF(t) ): Mengukur seberapa unik kata tersebut di seluruh basis data 'N'. Kata umum diberi bobot kecil, kata spesifik diberi bobot tinggi.\n"
            "   • Bobot = TF x IDF. Teks masukan Anda dan seluruh contoh intent dikonversi menjadi vektor numerik multi-dimensi.\n\n"
            "2. Cosine Similarity (Kemiripan Kosinus):\n"
            "   • Mengukur besar sudut kosinus antara vektor input pengguna (A) dan vektor contoh intent (B):\n"
            "     Cosine Similarity = (A • B) / ( ||A|| x ||B|| )\n"
            "   • Menghasilkan skor 0.0 (sangat tidak cocok) hingga 1.0 (identik persis).\n\n"
            "3. Logika Penentuan Respons:\n"
            "   Jika skor kemiripan tertinggi >= 0.38, sistem mengenali maksud Anda dan menampilkan jawaban resmi dari basis data lokal. "
            "Jika pertanyaan sangat kompleks atau di luar data lokal, sistem secara cerdas meneruskannya ke Gemini API."
        ]
    },

    "ai_computer_vision": {
        "patterns": [
            "computer vision", "visi komputer", "apa itu computer vision",
            "pengolahan citra digital", "deteksi objek", "object detection",
            "yolo", "face recognition", "image classification"
        ],
        "responses": [
            "COMPUTER VISION (VISI KOMPUTER) & PENGOLAHAN CITRA:\n\n"
            "1. Definisi:\n"
            "Computer Vision adalah bidang AI yang melatih komputer untuk mengekstrak, menganalisis, dan memahami informasi visual dari gambar atau video digital.\n\n"
            "2. Tugas Utama Computer Vision:\n"
            "• Image Classification: Menentukan label objek tunggal dalam gambar (contoh: membedakan foto anjing dan kucing).\n"
            "• Object Detection: Menemukan lokasi koordinat kotak pembatas (bounding box) sekaligus mengklasifikasikan multi-objek (contoh: algoritma YOLO - You Only Look Once, SSD).\n"
            "• Semantic Segmentation: Menandai setiap piksel gambar ke dalam kelas objek tertentu (digunakan pada mobil otonom untuk mendeteksi lajur jalan).\n"
            "• Biometric Face Recognition: Mengenali identitas wajah manusia melalui pola visual."
        ]
    },

    "ai_expert_system": {
        "patterns": [
            "sistem pakar", "expert system", "apa itu sistem pakar",
            "forward chaining", "backward chaining", "inference engine",
            "basis pengetahuan sistem pakar"
        ],
        "responses": [
            "SISTEM PAKAR (EXPERT SYSTEM) — SISTEM BERBASIS ATURAN (RULE-BASED):\n\n"
            "1. Pengertian:\n"
            "Sistem Pakar adalah perangkat lunak AI yang mengadopsi pengetahuan pakar manusia untuk menyelesaikan masalah konsultasi atau diagnosis spesifik.\n\n"
            "2. Komponen Inti:\n"
            "• Knowledge Base (Basis Pengetahuan): Kumpulan fakta dan aturan logika (IF-THEN rules).\n"
            "• Inference Engine (Mesin Inferensi): Komponen penalaran yang menghubungkan data pengguna dengan aturan untuk menarik kesimpulan.\n"
            "• Working Memory (Memori Kerja): Menyimpan fakta-fakta masukan dari pengguna selama sesi konsultasi berlangsung.\n\n"
            "3. Metode Penalaran Inferensi:\n"
            "• Forward Chaining: Penalaran maju dimulai dari sekumpulan fakta yang diketahui menuju kesimpulan akhir (data-driven).\n"
            "• Backward Chaining: Penalaran mundur dimulai dari hipotesis tujuan lalu mencari fakta pembukti ke belakang (goal-driven)."
        ]
    },

    "ai_algoritma_pencarian": {
        "patterns": [
            "algoritma pencarian ai", "search algorithm ai", "bfs", "dfs",
            "a star", "a*", "heuristic search", "breadth first search",
            "minimax", "alpha beta pruning"
        ],
        "responses": [
            "ALGORITMA PENCARIAN DALAM KECERDASAN BUATAN (SEARCH ALGORITHMS):\n\n"
            "Pencarian adalah proses menemukan urutan aksi dari kondisi awal (initial state) menuju kondisi tujuan (goal state).\n\n"
            "1. Uninformed Search (Pencarian Buta / Tanpa Heuristik):\n"
            "• Breadth-First Search (BFS): Menjelajah simpul tingkat demi tingkat menggunakan antrean (Queue FIFO). Menjamin solusi rute terpendek jika biaya langkah seragam.\n"
            "• Depth-First Search (DFS): Menjelajah simpul sedalam mungkin menyusuri cabang menggunakan tumpukan (Stack LIFO). Sangat hemat memori.\n\n"
            "2. Informed Search (Pencarian Berheuristik):\n"
            "• A* Search (A-Star): Menggabungkan biaya aktual dari titik awal g(n) dan estimasi biaya menuju target h(n): f(n) = g(n) + h(n). "
            "Sangat optimal untuk penentuan rute navigasi terpendek (Google Maps, Game Pathfinding).\n\n"
            "3. Adversarial Search (Pencarian Game 2 Pemain):\n"
            "• Minimax & Alpha-Beta Pruning: Menentukan langkah optimal dalam permainan catur dengan memangkas cabang pohon keputusan yang tidak menguntungkan."
        ]
    },

    "ai_evaluasi_model": {
        "patterns": [
            "evaluasi model ai", "confusion matrix", "akurasi", "presisi",
            "recall", "f1 score", "f1-score", "overfitting", "underfitting"
        ],
        "responses": [
            "EVALUASI MODEL MACHINE LEARNING & METRIK PERFORMA:\n\n"
            "1. Confusion Matrix (Matriks Kebingungan Klasifikasi):\n"
            "• True Positive (TP): Data bernilai positif diprediksi benar positif.\n"
            "• True Negative (TN): Data bernilai negatif diprediksi benar negatif.\n"
            "• False Positive (FP / Type I Error): Data negatif salah diprediksi positif.\n"
            "• False Negative (FN / Type II Error): Data positif salah diprediksi negatif.\n\n"
            "2. Metrik Pengukuran:\n"
            "• Akurasi = (TP + TN) / (TP + TN + FP + FN) -> Persentase prediksi benar total.\n"
            "• Presisi = TP / (TP + FP) -> Dari yang diprediksi positif, seberapa banyak yang tepat?\n"
            "• Recall = TP / (TP + FN) -> Dari seluruh data positif nyata, seberapa banyak yang tertangkap model?\n"
            "• F1-Score = 2 x (Presisi x Recall) / (Presisi + Recall) -> Rata-rata harmonik antara presisi dan recall (sangat krusial untuk dataset tidak seimbang / imbalanced).\n\n"
            "3. Masalah Model:\n"
            "• Overfitting: Model menghafal data latih terlalu detail sehingga gagal memprediksi data uji baru. Solusi: Regularisasi, Dropout, tambah data latih.\n"
            "• Underfitting: Model terlalu sederhana sehingga gagal menangkap pola data. Solusi: Tambah fitur atau perbesar kapasitas arsitektur model."
        ]
    },

    "ai_generative_llm": {
        "patterns": [
            "generative ai", "gen ai", "llm", "large language model",
            "transformer", "self attention", "chatgpt", "gemini", "prompt engineering"
        ],
        "responses": [
            "GENERATIVE AI & LARGE LANGUAGE MODELS (LLM):\n\n"
            "1. Generative AI:\n"
            "Jenis kecerdasan buatan yang mampu menghasilkan konten baru orisinal (teks, kode program, citra gambar, audio, video) "
            "dari instruksi pengguna (prompt), bukan hanya mengklasifikasikan data yang sudah ada.\n\n"
            "2. Arsitektur Transformer (Google, 2017):\n"
            "Fondasi modern seluruh LLM berbasis mekanisme 'Self-Attention' yang mampu memproses seluruh kata secara paralel "
            "dan memahami keterhubungan makna antar kata jarak jauh dalam konteks kalimat.\n\n"
            "3. Large Language Models (LLM):\n"
            "Model bahasa berskala masif dengan ratusan miliar parameter (contoh: Google Gemini, GPT-4, LLaMA) yang dilatih menggunakan data teks skala internet.\n\n"
            "4. Istilah Kunci:\n"
            "• Prompt Engineering: Teknik merancang kalimat perintah terstruktur untuk memperoleh respon model AI yang paling akurat.\n"
            "• RAG (Retrieval-Augmented Generation): Menggabungkan pencarian dokumen lokal dengan LLM agar jawaban selalu faktual dan bebas dari halusinasi."
        ]
    },

    "ai_unp_informatika": {
        "patterns": [
            "ai di unp", "matkul ai unp", "laboratorium ai unp", "riset ai unp",
            "skripsi ai informatika unp", "dosen ai unp", "penerapan ai di informatika unp"
        ],
        "responses": [
            "STUDI DAN RISET ARTIFICIAL INTELLIGENCE DI S1 TEKNIK INFORMATIKA FT UNP:\n\n"
            "1. Laboratorium AI & Data Science:\n"
            "Terletak di Lantai 3 Gedung Laboratorium FT UNP Kampus Air Tawar. Memiliki 30 unit Workstation GPU RTX dan server komputasi untuk pelatihan model Deep Learning dan Machine Learning.\n\n"
            "2. Jalur Kurikulum AI S1 Informatika UNP:\n"
            "• Semester 4: Artificial Intelligence (3 SKS) & Praktikum Artificial Intelligence (1 SKS)\n"
            "• Semester 5: Machine Learning (3 SKS), Pengolahan Citra Digital (3 SKS), Data Mining (3 SKS)\n"
            "• Semester 6: Deep Learning dan NLP (3 SKS), Analisis Big Data (3 SKS)\n"
            "• Semester 7: MK Pilihan Lanjut: Computer Vision & Generative AI (3 SKS)\n\n"
            "3. Dosen Bidang Keahlian AI:\n"
            "• Dr. Asrul Huda, S.Kom., M.Kom. (Kepala Lab AI & Data Science)\n"
            "• Dr. Ir. Zulhendra, S.Kom., M.Kom. (Keahlian Machine Learning & Computer Vision)\n"
            "• Dr. Raka Pratama, S.Kom., M.Kom. (Keahlian AI & Knowledge Systems)\n"
            "• Aditya Putra, S.Kom., M.Kom. (Keahlian Deep Learning, Generative AI, & NLP)\n\n"
            "4. Topik Skripsi AI Mahasiswa Informatika UNP:\n"
            "• Deteksi Penyakit Tanaman Pertanian Sumbar Menggunakan Convolutional Neural Network (CNN).\n"
            "• Analisis Sentimen Ulasan Pariwisata Sumatera Barat Menggunakan IndoBERT / NLP.\n"
            "• Sistem Deteksi Pelanggaran Helm di Kawasan Kampus UNP Menggunakan Algoritma YOLO.\n"
            "• Sistem Temu Kembali Informasi & Chatbot Akademik Berbasis TF-IDF dan Cosine Similarity."
        ]
    }
}


# ============================================================
# 4. FUNGSI PENCARIAN DATABASE AKADEMIK TERSTRUKTUR (TABULAR)
# ============================================================

def cari_data_dosen(user_input):
    """
    Mencari dosen berdasarkan nama, bidang keahlian (khususnya AI),
    atau mata kuliah yang diampu, lalu menyajikannya dalam tabel berbingkai.
    """
    q = preprocess(user_input)
    is_dosen_keyword = any(k in q for k in ["dosen", "pengajar", "pengampu", "siapa yang mengajar", "siapa yang mengampu"])
    is_ai_keyword = bool(re.search(r"\b(ai|artificial intelligence|artificial intelegent|kecerdasan buatan|machine learning|deep learning|data science)\b", q))

    found = []

    # 1. Jika pengguna bertanya khusus dosen AI / Kecerdasan Buatan
    if is_ai_keyword and (is_dosen_keyword or "dosen" in q or "siapa" in q):
        for d in DOSEN:
            bidang_clean = preprocess(d["bidang"])
            matkul_clean = " ".join(preprocess(m) for m in d.get("matkul_diampu", []))
            if any(k in bidang_clean or k in matkul_clean for k in ["artificial intelligence", "kecerdasan buatan", "machine learning", "deep learning", "ai"]):
                found.append(d)
        if found:
            headers = ["Nama Dosen & Gelar", "NIDN", "Bidang Keahlian AI", "Ruang Kerja"]
            rows = []
            for d in found:
                rows.append([d["nama"], d["nidn"], d["bidang"][:45] + "...", d["ruang"]])
            return buat_tabel(headers, rows, title="DAFTAR DOSEN BIDANG ARTIFICIAL INTELLIGENCE (AI) - FT UNP")

    # 2. Jika pengguna mencari dosen mata kuliah tertentu (misal: "dosen sistem operasi", "dosen jaringan")
    if is_dosen_keyword:
        for d in DOSEN:
            bidang_clean = preprocess(d["bidang"])
            matkul_clean = " ".join(preprocess(m) for m in d.get("matkul_diampu", []))
            # Cek apakah ada kata kunci mata kuliah selain kata "dosen"
            q_sub = " ".join(w for w in q.split() if w not in ["dosen", "siapa", "pengampu", "pengajar", "unp", "informatika"])
            if len(q_sub) > 2 and (q_sub in bidang_clean or q_sub in matkul_clean):
                found.append(d)
        if found:
            headers = ["Nama Dosen & Gelar", "Bidang Keahlian", "Mata Kuliah Diampu", "Ruang Kerja"]
            rows = []
            for d in found:
                mk_str = ", ".join(d.get("matkul_diampu", []))
                rows.append([d["nama"], d["bidang"][:40] + "...", mk_str, d["ruang"]])
            return buat_tabel(headers, rows, title="DOSEN PENGAMPU SESUAI BIDANG KAJIAN - S1 INFORMATIKA UNP")

    # 3. Pencarian berdasarkan nama dosen spesifik
    for d in DOSEN:
        nama_tokens = [w for w in preprocess(d["nama"]).split() if len(w) > 3 and w not in ["kom", "dra", "prof"]]
        if any(token in q for token in nama_tokens):
            found.append(d)

    # 4. Pencarian daftar semua dosen
    if not found and any(k in q for k in ["semua dosen", "daftar dosen", "data dosen", "dosen informatika", "nama dosen"]):
        found = DOSEN

    if not found:
        return None

    headers = ["Nama Dosen & Gelar", "NIDN", "Bidang Keahlian", "Ruang Kerja"]
    rows = []
    for d in found:
        rows.append([d["nama"], d["nidn"], d["bidang"][:42] + "...", d["ruang"]])

    title = "DATA DOSEN S1 TEKNIK INFORMATIKA FT UNP" if len(found) > 1 else f"PROFIL DOSEN: {found[0]['nama']}"
    return buat_tabel(headers, rows, title=title)


def cari_data_mata_kuliah(user_input):
    """
    Mencari jadwal mata kuliah Informatika dan menyajikannya dalam tabel rapi.
    Mendukung pencarian jadwal AI, hari, semester, nama mata kuliah, atau jadwal lengkap.
    """
    q = preprocess(user_input)
    hari_list = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu"]
    hari = next((h for h in hari_list if h in q), None)
    sem_match = re.search(r"semester\s*(\d+)", q)
    semester_num = int(sem_match.group(1)) if sem_match else None

    is_ai_query = bool(re.search(r"\b(ai|artificial intelligence|artificial intelegent|kecerdasan buatan)\b", q))

    hasil = []

    # 1. PENCARIAN KHUSUS MATKUL & JADWAL ARTIFICIAL INTELLIGENCE (AI)
    if is_ai_query:
        # Jika bukan bertanya definisi murni AI (seperti "apa itu ai")
        if not any(k in q for k in ["apa itu", "pengertian", "definisi", "sejarah", "konsep dasar"]):
            for mk in MATA_KULIAH:
                nama_clean = preprocess(mk["nama"])
                if any(k in nama_clean for k in ["artificial intelligence", "machine learning", "deep learning", "kecerdasan buatan", "computer vision"]):
                    hasil.append(mk)
            if hasil:
                headers = ["Kode", "Mata Kuliah AI", "SKS", "Hari", "Jam", "Ruangan", "Dosen Pengampu"]
                rows = []
                for m in hasil:
                    rows.append([m["kode"], m["nama"], m["sks"], m["hari"], m["jam"], m["ruang"], m["dosen"]])
                return buat_tabel(headers, rows, title="JADWAL PERKULIAHAN BIDANG ARTIFICIAL INTELLIGENCE (AI) - FT UNP")

    # 2. Pencarian berdasarkan nama mata kuliah spesifik
    for mk in MATA_KULIAH:
        nama_clean = preprocess(mk["nama"])
        kode_clean = mk["kode"].lower()
        if kode_clean in q or (len(nama_clean) > 4 and nama_clean in q):
            hasil.append(mk)

    # 3. Pencarian berdasarkan hari
    if not hasil and hari and any(k in q for k in ["jadwal", "kuliah", "matkul", "kelas", "ada apa", "hari"]):
        hasil = [m for m in MATA_KULIAH if m["hari"].lower() == hari]
        if semester_num:
            hasil = [m for m in hasil if m["semester"] == semester_num]

    # 4. Pencarian berdasarkan semester tertentu
    if not hasil and semester_num and any(k in q for k in ["jadwal", "matkul", "mata kuliah", "kurikulum", "semester"]):
        hasil = [m for m in MATA_KULIAH if m["semester"] == semester_num]

    # 5. Permintaan jadwal umum / semua jadwal
    if not hasil and (q in ["jadwal", "jadwal kuliah", "jadwal kelas", "jadwal perkuliahan", "semua jadwal", "jadwal lengkap"]):
        hasil = MATA_KULIAH

    if not hasil:
        return None

    headers = ["Kode", "Mata Kuliah Informatika", "SKS", "Hari", "Jam", "Ruang", "Dosen Pengampu"]
    rows = []
    for m in hasil:
        rows.append([m["kode"], m["nama"], m["sks"], m["hari"], m["jam"], m["ruang"], m["dosen"]])

    judul = f"JADWAL PERKULIAHAN S1 TEKNIK INFORMATIKA UNP ({len(hasil)} MATA KULIAH)"
    if hari:
        judul = f"JADWAL KULIAH HARI {hari.upper()} - S1 TEKNIK INFORMATIKA FT UNP"
    elif semester_num:
        judul = f"JADWAL KULIAH SEMESTER {semester_num} - S1 TEKNIK INFORMATIKA FT UNP"

    return buat_tabel(headers, rows, title=judul)


def cari_dosen_pa(user_input):
    """
    Menampilkan data Dosen Pembimbing Akademik (PA) per angkatan dalam tabel.
    Hanya aktif jika query secara eksplisit menyebut PA / Pembimbing Akademik.
    """
    q = preprocess(user_input)
    # Pastikan kata PA adalah kesatuan kata, bukan substring dari kata lain
    is_pa = bool(re.search(r"\b(dosen pa|pembimbing akademik|dosen wali|pa saya|daftar pa|wali kelas)\b", q))
    if not is_pa:
        return None

    sem_match = re.search(r"(20\d{2})", q)
    angkatan = int(sem_match.group(1)) if sem_match else None

    if angkatan:
        rows_data = [x for x in DOSEN_PA if x["angkatan"] == angkatan]
    else:
        rows_data = DOSEN_PA

    if not rows_data:
        return f"Belum ada data Dosen PA untuk angkatan {angkatan} di S1 Teknik Informatika UNP."

    headers = ["Angkatan", "Kelas", "Dosen Pembimbing Akademik (PA)", "Email Institusi UNP"]
    rows = []
    for x in rows_data:
        rows.append([x["angkatan"], x["kode_kelas"], x["dosen"], x["email"]])

    return buat_tabel(headers, rows, title="DAFTAR DOSEN PEMBIMBING AKADEMIK (PA) S1 INFORMATIKA FT UNP")


def cari_informasi_lain(user_input):
    """
    Menampilkan informasi lain dalam tabel kotak:
    - Ruangan & Laboratorium
    - UKT (Uang Kuliah Tunggal)
    - Kurikulum per semester
    - Kalender Akademik
    - Program Beasiswa
    """
    q = preprocess(user_input)

    # 1. Ruangan & Laboratorium
    is_ruang_query = bool(re.search(r"\b(ruang|ruangan|lab|laboratorium|gedung e6|gedung e7|fasilitas lab)\b", q))
    if is_ruang_query and not any(k in q for k in ["uang kuliah", "ukt"]):
        headers = ["Kode", "Nama Ruang / Laboratorium", "Lokasi", "Fasilitas Utama"]
        rows = []
        for kode, r in RUANG.items():
            rows.append([kode, r["nama"], r["lokasi"][:30] + "...", r["fasilitas"][:40] + "..."])
        return buat_tabel(headers, rows, title="DAFTAR RUANG KULIAH & LABORATORIUM S1 TEKNIK INFORMATIKA FT UNP")

    # 2. Uang Kuliah Tunggal (UKT)
    is_ukt_query = bool(re.search(r"\b(ukt|uang kuliah|biaya kuliah|tarif ukt|kelompok ukt)\b", q))
    if is_ukt_query:
        headers = ["Kelompok UKT", "Tarif / Semester", "Kriteria Mahasiswa"]
        rows = [list(item) for item in UKT_DATA]
        tabel_ukt = buat_tabel(headers, rows, title="TARIF UKT S1 TEKNIK INFORMATIKA FAKULTAS TEKNIK UNP")
        catatan = (
            "\n\nCatatan Pembayaran:\n"
            "• Pembayaran dilakukan melalui Virtual Account Mitra Resmi UNP: Bank Nagari, BNI, Mandiri, BRI, BTN.\n"
            "• Mahasiswa yang mengambil <= 6 SKS pada semester 9 ke atas berhak mengajukan pemotongan UKT 50%."
        )
        return tabel_ukt + catatan

    # 3. Kurikulum Informatika per Semester
    if any(k in q for k in ["kurikulum", "daftar matkul", "daftar mata kuliah", "mata kuliah per semester"]):
        sem_match = re.search(r"semester\s*(\d+)", q)
        semesters = [int(sem_match.group(1))] if sem_match and int(sem_match.group(1)) in KURIKULUM else sorted(KURIKULUM.keys())

        output_tables = []
        for sem in semesters:
            mk_list = KURIKULUM[sem]
            total_sks = sum(m["sks"] for m in mk_list)
            headers = ["Kode", "Mata Kuliah", "SKS", "Ruang", "Dosen Pengampu"]
            rows = []
            for m in mk_list:
                rows.append([m["kode"], m["nama"], m["sks"], m["ruang"], m["dosen"]])
            output_tables.append(buat_tabel(headers, rows, title=f"KURIKULUM SEMESTER {sem} ({total_sks} SKS)"))
        return "\n\n".join(output_tables)

    # 4. Kalender Akademik UNP
    if any(k in q for k in ["kalender akademik", "agenda akademik", "jadwal uts unp", "jadwal uas unp", "awal semester unp"]):
        headers = ["Bulan", "Agenda Kegiatan Akademik UNP"]
        rows = [list(item) for item in KALENDER_AKADEMIK_DATA]
        return buat_tabel(headers, rows, title="AGENDA KALENDER AKADEMIK UNIVERSITAS NEGERI PADANG")

    # 5. Beasiswa UNP
    if any(k in q for k in ["beasiswa", "syarat beasiswa", "kip kuliah"]):
        headers = ["Program Beasiswa", "Bentuk Bantuan", "Persyaratan & Kriteria Utama"]
        rows = [list(item) for item in BEASISWA_DATA]
        return buat_tabel(headers, rows, title="PROGRAM BEASISWA UNIVERSITAS NEGERI PADANG")

    # 6. Profil Program Studi
    if any(k in q for k in ["profil prodi", "profil informatika", "tentang informatika unp", "kaprodi", "jurusan informatika"]):
        p = FAKULTAS["program_studi"][0]
        text_profil = (
            f"Universitas         : {FAKULTAS['universitas']}\n"
            f"Fakultas            : {FAKULTAS['nama']} ({FAKULTAS['kode']})\n"
            f"Program Studi       : {p['nama']} ({p['kode']})\n"
            f"Jenjang & Gelar     : {p['jenjang']} — {p['gelar']}\n"
            f"Akreditasi          : {p['akreditasi']}\n"
            f"Masa Studi / SKS    : {p['lama_studi']} ({p['total_sks']} SKS)\n"
            f"Ketua Program Studi : {p['ketua_prodi']}\n"
            f"Sekretaris Prodi    : {p['sekretaris_prodi']}\n"
            f"Lokasi Kampus       : {FAKULTAS['alamat']}\n\n"
            "Bidang Peminatan Unggulan:\n"
            "1. Artificial Intelligence & Machine Learning (Sistem Cerdas)\n"
            "2. Software Engineering (Rekayasa Perangkat Lunak)\n"
            "3. Computer Network & Cyber Security\n"
            "4. Data Science & Big Data Analytics\n"
            "5. Cloud Computing & Internet of Things (IoT)"
        )
        return buat_kotak("PROFIL PROGRAM STUDI S1 TEKNIK INFORMATIKA FT UNP", text_profil)

    return None


# ============================================================
# 5. PREPROCESSING & FEATURE EXTRACTION
# ============================================================

def preprocess(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


STOPWORDS = {
    "saya", "aku", "anda", "kamu", "yang", "dan", "atau", "di", "ke",
    "dari", "untuk", "dengan", "pada", "itu", "ini", "apa", "apakah",
    "bagaimana", "kenapa", "mengapa", "berapa", "dimana", "kapan",
    "tolong", "mohon", "bisa", "kah", "ya", "dong", "sih", "nya",
    "ingin", "mau", "tentang", "jelaskan", "jelaskanlah", "tahu", "adakah"
}


def meaningful_tokens(text):
    return [
        token for token in preprocess(text).split()
        if token not in STOPWORDS and len(token) > 1
    ]


# ============================================================
# 6. RULE-BASED MATCHING
# ============================================================

def match_intent_rule_based(user_input):
    processed = preprocess(user_input)
    for intent, data in knowledge_base.items():
        for pattern in data["patterns"]:
            pattern_clean = preprocess(pattern)
            if pattern_clean:
                # Gunakan word boundary agar tidak salah cocok substring
                if re.search(r"\b" + re.escape(pattern_clean) + r"\b", processed):
                    return intent
    return None


# ============================================================
# 7. MODEL TF-IDF & COSINE SIMILARITY
# ============================================================

training_examples = {}

for intent_name, intent_data in knowledge_base.items():
    training_examples[intent_name] = list(intent_data.get("patterns", []))

# Variasi training query realistis mahasiswa
training_examples["jadwal_kuliah"].extend([
    "kapan jadwal kuliah saya", "jadwal informatika hari senin apa saja",
    "hari selasa semester 4 ada kuliah apa", "jadwal matkul machine learning",
    "jam berapa kuliah pemrograman web", "apakah hari jumat ada praktikum",
    "tampilkan semua jadwal kuliah informatika"
])

training_examples["beasiswa"].extend([
    "apa saja beasiswa yang tersedia di unp", "daftar beasiswa unp",
    "informasi beasiswa di unp", "syarat beasiswa bank indonesia", "syarat beasiswa baznas"
])

corpus = []
labels = []

for intent, examples in training_examples.items():
    for example in examples:
        clean_example = preprocess(example)
        if clean_example:
            corpus.append(clean_example)
            labels.append(intent)

vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
tfidf_matrix = vectorizer.fit_transform(corpus)
TRAINING_VOCAB = set(vectorizer.get_feature_names_out())


def match_intent_tfidf(user_input, threshold=SIMILARITY_THRESHOLD):
    tokens = meaningful_tokens(user_input)
    if len(tokens) < 1:
        return None, 0.0

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
# 8. INTEGRASI GEMINI API
# ============================================================

def is_incomplete_question(user_input):
    tokens = meaningful_tokens(user_input)
    normalized = preprocess(user_input)
    short_messages = {
        "apa", "berapa", "dimana", "kapan", "kenapa", "mengapa",
        "bagaimana", "siapa", "itu", "ini", "yang", "apakah", "min", "bot"
    }
    return len(tokens) == 0 or normalized in short_messages


def is_complex_question(user_input):
    text = preprocess(user_input)
    complex_phrases = [
        "jelaskan secara rinci", "jelaskan secara detail", "analisis mendalam",
        "bandingkan dan jelaskan", "uraikan langkah langkah", "dari awal sampai akhir",
        "bagaimana proses matematis", "berikan contoh kode", "turunkan rumus",
        "kelebihan dan kelemahan secara lengkap"
    ]
    return any(phrase in text for phrase in complex_phrases) or len(text.split()) >= 18


def ask_gemini(user_input, intent=None, timeout=45):
    if not GEMINI_API_KEY:
        return None

    system_instruction = """
Kamu adalah asisten pintar untuk S1 Teknik Informatika Fakultas Teknik Universitas Negeri Padang (UNP).
Tugasmu:
1. Menjawab pertanyaan akademik prodi Teknik Informatika FT UNP secara ramah, jelas, dan akurat.
2. Menjelaskan topik-topik Kecerdasan Buatan (AI, Machine Learning, Deep Learning, NLP, Computer Vision, dll.) secara ilmiah, runtut, dan mudah dipahami mahasiswa.
Gunakan bahasa Indonesia yang santun, edukatif, dan jelas.
"""

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_input}]}
        ],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 1500
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
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** (attempt + 1))
                    continue
                return None
            if not response.ok:
                return None

            result = response.json()
            candidates = result.get("candidates", [])
            if not candidates:
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            answer = " ".join(part["text"] for part in parts if "text" in part).strip()
            return answer or None
        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** (attempt + 1))

    return None


# ============================================================
# 9. HYBRID CHATBOT ROUTING
# ============================================================

def get_response_hybrid(user_input):
    normalized = preprocess(user_input)

    # 1. Respons sapaan kilat
    if normalized in {"halo", "hai", "hi", "hello", "assalamualaikum"}:
        return buat_kotak("LAYANAN AKADEMIK INFORMATIKA UNP & AI", knowledge_base["greeting"]["responses"][0])

    if normalized in {"terima kasih", "makasih", "thanks", "terimakasih"}:
        return buat_kotak("LAYANAN AKADEMIK INFORMATIKA UNP & AI", knowledge_base["terima_kasih"]["responses"][0])

    if is_incomplete_question(user_input):
        return (
            "Pertanyaan Anda masih terlalu singkat untuk dipahami bot.\n"
            "Silakan ketik pertanyaan lebih lengkap mengenai perkuliahan Informatika UNP atau materi Kecerdasan Buatan (AI)!"
        )

    # 2. PENCARIAN DATABASE AKADEMIK TERSTRUKTUR DAHULU (TABULAR & KOTAK)
    # Khusus untuk jadwal, dosen, ruang, UKT, kurikulum, kalender
    for pencarian in (cari_data_dosen, cari_data_mata_kuliah, cari_dosen_pa, cari_informasi_lain):
        hasil_db = pencarian(user_input)
        if hasil_db:
            print("[INFO] Data ditemukan pada Database Akademik Informatika UNP.")
            return hasil_db

    # 3. Klasifikasi Intent menggunakan TF-IDF + Cosine Similarity
    intent, score = match_intent_tfidf(user_input)
    print(f"[TF-IDF] Intent: {intent} | Similarity: {score:.3f}")

    # 4. Pertanyaan kompleks diarahkan ke Gemini API
    if is_complex_question(user_input):
        print("[INFO] Pertanyaan terdeteksi kompleks, mengontak Gemini API...")
        answer = ask_gemini(user_input, intent)
        if answer:
            return buat_kotak("PENJELASAN AKADEMIK / AI DARI ASISTEN CERDAS", answer)
        if intent is not None:
            return buat_kotak(f"INFORMASI BASIS PENGETAHUAN [{intent.upper()}]", knowledge_base[intent]["responses"][0])
        return buat_kotak("PEMBERITAHUAN", FALLBACK_RESPONSE)

    # 5. Jika intent lokal cocok
    if intent is not None:
        print(f"[INFO] Menjawab menggunakan Knowledge Base lokal [{intent}].")
        raw_res = random.choice(knowledge_base[intent]["responses"])
        # Format ke dalam kotak rapi
        judul_kotak = intent.replace("_", " ").upper()
        return buat_kotak(f"INFORMASI AKADEMIK / AI: {judul_kotak}", raw_res)

    # 6. Fallback ke Gemini API jika intent tidak cocok
    print("[INFO] Mencoba Gemini API untuk pertanyaan di luar basis pengetahuan...")
    answer = ask_gemini(user_input)
    if answer:
        return buat_kotak("PENJELASAN DARI ASISTEN CERDAS", answer)

    # 7. Fallback lokal terakhir
    return buat_kotak("PEMBERITAHUAN", FALLBACK_RESPONSE)


# ============================================================
# 10. EVALUASI MODEL
# ============================================================

test_cases = [
    ("halo min", "greeting"),
    ("kapan jadwal kuliah informatika semester ini", "jadwal_kuliah"),
    ("bagaimana cara mengisi KRS di portal UNP", "krs"),
    ("kapan nilai KHS keluar di portal unp", "khs"),
    ("berapa biaya UKT kelompok 5 informatika unp", "ukt"),
    ("kapan jadwal UTS dan UAS unp", "kalender_akademik"),
    ("bagaimana prosedur mengajukan cuti kuliah unp", "cuti_akademik"),
    ("dimana lokasi fakultas teknik kampus unp", "lokasi_kampus"),
    ("siapa dosen pembimbing akademik angkatan 2024", "dosen_pa"),
    ("apa syarat tugas akhir dan skripsi informatika", "skripsi_tugas_akhir"),
    ("apa saja beasiswa yang tersedia di UNP", "beasiswa"),
    ("apa itu kecerdasan buatan", "ai_definisi"),
    ("apa saja cabang cabang ilmu ai", "ai_cabang"),
    ("jelaskan perbedaan supervised dan unsupervised machine learning", "ai_machine_learning"),
    ("bagaimana cara kerja algoritma random forest dan decision tree", "ai_algoritma_ml"),
    ("apa itu convolutional neural network cnn deep learning", "ai_deep_learning"),
    ("bagaimana tahapan preprocessing teks dalam nlp", "ai_nlp"),
    ("jelaskan rumus tf idf dan cosine similarity", "ai_tfidf_cosine"),
    ("bagaimana algoritma yolo mendeteksi objek citra", "ai_computer_vision"),
    ("apa perbedaan forward chaining dan backward chaining pada sistem pakar", "ai_expert_system"),
    ("bagaimana algoritma pencarian a* search bekerja", "ai_algoritma_pencarian"),
    ("apa itu confusion matrix precision recall f1-score", "ai_evaluasi_model"),
    ("apa itu generative ai dan transformer llm", "ai_generative_llm"),
    ("apa saja mata kuliah ai di teknik informatika unp", "ai_unp_informatika"),
    ("terima kasih banyak atas informasinya", "terima_kasih"),
    ("sampai jumpa lagi bot", "goodbye"),
    ("berapa jarak bumi ke planet mars", None)
]


def evaluate_models():
    correct_rule = 0
    correct_tfidf = 0

    print("\n" + "=" * 65)
    print("EVALUASI AKURASI: RULE-BASED VS TF-IDF + COSINE SIMILARITY")
    print("Mencakup Domain Layanan Akademik UNP dan Pengetahuan AI")
    print("=" * 65)

    for question, expected in test_cases:
        rule_result = match_intent_rule_based(question)
        tfidf_result, score = match_intent_tfidf(question)

        is_rule_correct = (rule_result == expected)
        is_tfidf_correct = (tfidf_result == expected)

        correct_rule += is_rule_correct
        correct_tfidf += is_tfidf_correct

        print(f"\nPertanyaan : {question}")
        print(f"Target     : {expected}")
        print(f"Rule-Based : {rule_result} [{'OK' if is_rule_correct else 'FAIL'}]")
        print(f"TF-IDF     : {tfidf_result} (Similarity: {score:.3f}) [{'OK' if is_tfidf_correct else 'FAIL'}]")

    total = len(test_cases)
    print("\n" + "=" * 65)
    print("HASIL AKURASI EVALUASI:")
    print("=" * 65)
    print(f"Akurasi Rule-Based : {correct_rule / total * 100:.1f}% ({correct_rule}/{total})")
    print(f"Akurasi TF-IDF     : {correct_tfidf / total * 100:.1f}% ({correct_tfidf}/{total})")
    print("=" * 65)


def test_gemini():
    print("\n[INFO] Mengetes Koneksi ke Gemini API...")
    print(f"[INFO] Model: {GEMINI_MODEL}")
    answer = ask_gemini("Jelaskan secara singkat apa keunggulan mahasiswa Teknik Informatika UNP mempelajari AI.", timeout=30)
    if answer:
        print("\n[BERHASIL] Respons diterima dari Gemini API:")
        print(answer)
    else:
        print("\n[PERINGATAN] Gemini API belum dapat dihubungi. Pastikan GEMINI_API_KEY sudah disetel di environment.")
        print("Chatbot tetap dapat berjalan penuh menggunakan Basis Data & Basis Pengetahuan Lokal UNP + AI.")


# ============================================================
# 11. ANTARMUKA TERMINAL CHATBOT
# ============================================================

def run_chatbot():
    banner = (
        "CHATBOT LAYANAN AKADEMIK S1 TEKNIK INFORMATIKA FT UNP\n"
        "& PUSAT PENGETAHUAN ARTIFICIAL INTELLIGENCE (AI)\n"
        "Fakultas Teknik - Universitas Negeri Padang\n"
        "Teknologi: Rule-Based + TF-IDF + Cosine Similarity + Gemini API\n"
        "Semua Jadwal & Dosen: 100% INFORMATIKA SAJA (Disajikan dalam Tabel/Kotak Rapi)"
    )
    print("\n" + buat_kotak("SELAMAT DATANG", banner))
    print("Ketik 'keluar' untuk kembali ke menu utama.\n")

    while True:
        try:
            user_input = input("Mahasiswa: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBot: Sesi chatbot diakhiri.")
            break

        if not user_input:
            continue

        if preprocess(user_input) in {"keluar", "exit", "quit"}:
            print("\n" + buat_kotak("SAMPAI JUMPA", knowledge_base["goodbye"]["responses"][0]))
            break

        response = get_response_hybrid(user_input)
        print("\nBot:")
        print(response)
        print("\n" + "─" * 82 + "\n")


def main():
    while True:
        print("\n" + "┌" + "─" * 58 + "┐")
        print("│ " + "CHATBOT AKADEMIK S1 TEKNIK INFORMATIKA UNP & AI".center(56) + " │")
        print("│ " + "Fakultas Teknik - Universitas Negeri Padang".center(56) + " │")
        print("├" + "─" * 58 + "┤")
        print("│  1. Jalankan Chatbot Interaktif                          │")
        print("│  2. Evaluasi Model (Rule-Based vs TF-IDF)                │")
        print("│  3. Uji Koneksi Gemini API                               │")
        print("│  4. Keluar                                               │")
        print("└" + "─" * 58 + "┘")

        pilihan = input("Pilih menu (1-4): ").strip()
        if pilihan == "1":
            run_chatbot()
        elif pilihan == "2":
            evaluate_models()
        elif pilihan == "3":
            test_gemini()
        elif pilihan == "4":
            print("Terima kasih telah menggunakan Chatbot Informatika UNP.")
            break
        else:
            print("Pilihan tidak valid. Silakan pilih 1 s.d. 4.")


if __name__ == "__main__":
    main()
