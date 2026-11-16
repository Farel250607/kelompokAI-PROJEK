"""
DATABASE AKADEMIK INFORMATIKA (SELURUHNYA DATA DUMMY)
Catatan: semua nama, NIDN, email, kode, jadwal, tarif, dan aturan
dibuat fiktif untuk demonstrasi chatbot, bukan data resmi UNP.
"""

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
    ],
}

DOSEN = [
    {"nidn": "0001018001", "nama": "Dr. Raka Pratama, S.Kom., M.Kom.", "jabatan": "Ketua Program Studi (dummy)", "bidang": "Kecerdasan Buatan dan Machine Learning", "email": "raka.pratama@example.edu", "ruang": "Kantor Prodi IF-301", "pa": ["IF24-A"]},
    {"nidn": "0002028202", "nama": "Dina Kurniawati, S.T., M.Kom.", "jabatan": "Dosen", "bidang": "Rekayasa Perangkat Lunak dan Manajemen Proyek", "email": "dina.kurniawati@example.edu", "ruang": "Kantor Dosen IF-302", "pa": ["IF24-B"]},
    {"nidn": "0003037903", "nama": "Fajar Hidayat, S.Kom., M.Cs.", "jabatan": "Dosen", "bidang": "Sistem Operasi dan Arsitektur Komputer", "email": "fajar.hidayat@example.edu", "ruang": "Kantor Dosen IF-303", "pa": ["IF23-A"]},
    {"nidn": "0004048104", "nama": "Nadia Putri, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Data Mining dan Data Science", "email": "nadia.putri@example.edu", "ruang": "Kantor Dosen IF-304", "pa": ["IF23-B"]},
    {"nidn": "0005057805", "nama": "Rizki Maulana, S.T., M.Kom.", "jabatan": "Dosen", "bidang": "Jaringan Komputer dan Keamanan Siber", "email": "rizki.maulana@example.edu", "ruang": "Kantor Dosen IF-305", "pa": ["IF22-A"]},
    {"nidn": "0006068306", "nama": "Siti Rahma, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Interaksi Manusia dan Komputer serta UI/UX", "email": "siti.rahma@example.edu", "ruang": "Kantor Dosen IF-306", "pa": ["IF22-B"]},
    {"nidn": "0007078007", "nama": "Budi Santoso, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Algoritma, Struktur Data, dan Pemrograman", "email": "budi.santoso@example.edu", "ruang": "Kantor Dosen IF-307", "pa": ["IF25-A"]},
    {"nidn": "0008088408", "nama": "Andi Pratama, S.T., M.Kom.", "jabatan": "Dosen", "bidang": "Sistem Informasi dan Analisis Bisnis", "email": "andi.pratama@example.edu", "ruang": "Kantor Dosen IF-308", "pa": ["IF25-B"]},
    {"nidn": "0009097909", "nama": "Rina Amelia, S.Si., M.Kom.", "jabatan": "Dosen", "bidang": "Matematika Diskrit dan Statistika", "email": "rina.amelia@example.edu", "ruang": "Kantor Dosen IF-309", "pa": ["IF21-A"]},
    {"nidn": "0010108110", "nama": "Aditya Putra, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Deep Learning, Computer Vision, dan NLP", "email": "aditya.putra@example.edu", "ruang": "Kantor Dosen IF-310", "pa": ["IF21-B"]},
    {"nidn": "0011118211", "nama": "Maya Lestari, S.Kom., M.T.", "jabatan": "Dosen", "bidang": "Basis Data dan Sistem Terdistribusi", "email": "maya.lestari@example.edu", "ruang": "Kantor Dosen IF-311", "pa": []},
    {"nidn": "0012128012", "nama": "Yoga Saputra, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Pemrograman Web dan Mobile", "email": "yoga.saputra@example.edu", "ruang": "Kantor Dosen IF-312", "pa": []},
    {"nidn": "0013138313", "nama": "Intan Permata, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Grafika Komputer dan Multimedia", "email": "intan.permata@example.edu", "ruang": "Kantor Dosen IF-313", "pa": []},
    {"nidn": "0014147714", "nama": "Dedi Firmansyah, S.T., M.Kom.", "jabatan": "Dosen", "bidang": "Komputasi Awan dan DevOps", "email": "dedi.firmansyah@example.edu", "ruang": "Kantor Dosen IF-314", "pa": []},
    {"nidn": "0015158515", "nama": "Laila Safitri, S.Kom., M.Kom.", "jabatan": "Dosen", "bidang": "Etika Profesi dan Metodologi Penelitian", "email": "laila.safitri@example.edu", "ruang": "Kantor Dosen IF-315", "pa": []},
]

DOSEN_PA = [
    {"kode_kelas": "IF25-A", "angkatan": 2025, "dosen": "Budi Santoso, S.Kom., M.Kom.", "email": "budi.santoso@example.edu"},
    {"kode_kelas": "IF25-B", "angkatan": 2025, "dosen": "Andi Pratama, S.T., M.Kom.", "email": "andi.pratama@example.edu"},
    {"kode_kelas": "IF24-A", "angkatan": 2024, "dosen": "Dr. Raka Pratama, S.Kom., M.Kom.", "email": "raka.pratama@example.edu"},
    {"kode_kelas": "IF24-B", "angkatan": 2024, "dosen": "Dina Kurniawati, S.T., M.Kom.", "email": "dina.kurniawati@example.edu"},
    {"kode_kelas": "IF23-A", "angkatan": 2023, "dosen": "Fajar Hidayat, S.Kom., M.Cs.", "email": "fajar.hidayat@example.edu"},
    {"kode_kelas": "IF23-B", "angkatan": 2023, "dosen": "Nadia Putri, S.Kom., M.Kom.", "email": "nadia.putri@example.edu"},
    {"kode_kelas": "IF22-A", "angkatan": 2022, "dosen": "Rizki Maulana, S.T., M.Kom.", "email": "rizki.maulana@example.edu"},
    {"kode_kelas": "IF22-B", "angkatan": 2022, "dosen": "Siti Rahma, S.Kom., M.Kom.", "email": "siti.rahma@example.edu"},
    {"kode_kelas": "IF21-A", "angkatan": 2021, "dosen": "Rina Amelia, S.Si., M.Kom.", "email": "rina.amelia@example.edu"},
    {"kode_kelas": "IF21-B", "angkatan": 2021, "dosen": "Aditya Putra, S.Kom., M.Kom.", "email": "aditya.putra@example.edu"},
]

# kode, nama, SKS, semester, hari, jam, ruang, dosen pengampu
_RAW_MK = [
    ("IF101", "Pendidikan Agama", 2, 1, "Senin", "08.00-09.40", "IF-101", "Laila Safitri"),
    ("IF102", "Pendidikan Pancasila", 2, 1, "Senin", "09.50-11.30", "IF-101", "Laila Safitri"),
    ("IF103", "Kalkulus", 3, 1, "Senin", "13.00-15.30", "IF-201", "Rina Amelia"),
    ("IF104", "Pengantar Informatika", 2, 1, "Selasa", "08.00-09.40", "IF-102", "Andi Pratama"),
    ("IF105", "Algoritma dan Pemrograman", 3, 1, "Selasa", "09.50-12.20", "LAB-1", "Budi Santoso"),
    ("IF106", "Matematika Diskrit", 3, 1, "Rabu", "08.00-10.30", "IF-201", "Rina Amelia"),
    ("IF107", "Bahasa Inggris", 2, 1, "Rabu", "10.40-12.20", "IF-102", "Laila Safitri"),
    ("IF108", "Literasi Digital", 2, 1, "Kamis", "08.00-09.40", "IF-103", "Andi Pratama"),
    ("IF109", "Dasar Sistem Komputer", 3, 1, "Kamis", "09.50-12.20", "LAB-2", "Fajar Hidayat"),
    ("IF110", "Bahasa Indonesia", 2, 1, "Jumat", "08.00-09.40", "IF-101", "Laila Safitri"),
    ("IF201", "Struktur Data", 3, 2, "Senin", "08.00-10.30", "LAB-1", "Budi Santoso"),
    ("IF202", "Basis Data", 3, 2, "Senin", "10.40-13.10", "LAB-2", "Maya Lestari"),
    ("IF203", "Sistem Operasi", 3, 2, "Selasa", "08.00-10.30", "LAB-2", "Fajar Hidayat"),
    ("IF204", "Pemrograman Berorientasi Objek", 3, 2, "Selasa", "13.00-15.30", "LAB-1", "Yoga Saputra"),
    ("IF205", "Aljabar Linear", 3, 2, "Rabu", "08.00-10.30", "IF-201", "Rina Amelia"),
    ("IF206", "Organisasi dan Arsitektur Komputer", 3, 2, "Rabu", "10.40-13.10", "IF-202", "Fajar Hidayat"),
    ("IF207", "Statistika dan Probabilitas", 3, 2, "Kamis", "08.00-10.30", "IF-201", "Rina Amelia"),
    ("IF208", "Pendidikan Kewarganegaraan", 2, 2, "Jumat", "08.00-09.40", "IF-101", "Laila Safitri"),
    ("IF301", "Jaringan Komputer", 3, 3, "Senin", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana"),
    ("IF302", "Pemrograman Web", 3, 3, "Senin", "10.40-13.10", "LAB-1", "Yoga Saputra"),
    ("IF303", "Analisis dan Desain Algoritma", 3, 3, "Selasa", "08.00-10.30", "IF-202", "Budi Santoso"),
    ("IF304", "Rekayasa Perangkat Lunak", 3, 3, "Selasa", "10.40-13.10", "IF-203", "Dina Kurniawati"),
    ("IF305", "Sistem Informasi", 2, 3, "Rabu", "08.00-09.40", "IF-102", "Andi Pratama"),
    ("IF306", "Interaksi Manusia dan Komputer", 3, 3, "Rabu", "09.50-12.20", "LAB-UX", "Siti Rahma"),
    ("IF307", "Metode Numerik", 3, 3, "Kamis", "08.00-10.30", "IF-201", "Rina Amelia"),
    ("IF308", "Praktikum Basis Data", 1, 3, "Jumat", "08.00-09.40", "LAB-2", "Maya Lestari"),
    ("IF401", "Kecerdasan Buatan", 3, 4, "Senin", "08.00-10.30", "LAB-AI", "Aditya Putra"),
    ("IF402", "Pemrograman Mobile", 3, 4, "Senin", "10.40-13.10", "LAB-1", "Yoga Saputra"),
    ("IF403", "Keamanan Informasi", 3, 4, "Selasa", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana"),
    ("IF404", "Manajemen Proyek Perangkat Lunak", 2, 4, "Selasa", "10.40-12.20", "IF-203", "Dina Kurniawati"),
    ("IF405", "Teori Bahasa dan Otomata", 3, 4, "Rabu", "08.00-10.30", "IF-202", "Rina Amelia"),
    ("IF406", "Grafika Komputer", 3, 4, "Rabu", "10.40-13.10", "LAB-MULTIMEDIA", "Intan Permata"),
    ("IF407", "Etika Profesi", 2, 4, "Kamis", "08.00-09.40", "IF-101", "Laila Safitri"),
    ("IF408", "Praktikum Jaringan Komputer", 1, 4, "Jumat", "08.00-09.40", "LAB-JARINGAN", "Rizki Maulana"),
    ("IF501", "Machine Learning", 3, 5, "Senin", "08.00-10.30", "LAB-AI", "Aditya Putra"),
    ("IF502", "Data Mining", 3, 5, "Senin", "10.40-13.10", "LAB-DATA", "Nadia Putri"),
    ("IF503", "Pemrograman Berbasis Framework", 3, 5, "Selasa", "08.00-10.30", "LAB-1", "Yoga Saputra"),
    ("IF504", "Komputasi Awan", 3, 5, "Selasa", "10.40-13.10", "LAB-CLOUD", "Dedi Firmansyah"),
    ("IF505", "Sistem Terdistribusi", 3, 5, "Rabu", "08.00-10.30", "IF-203", "Maya Lestari"),
    ("IF506", "Visi Komputer", 3, 5, "Rabu", "10.40-13.10", "LAB-AI", "Aditya Putra"),
    ("IF507", "Metodologi Penelitian", 2, 5, "Kamis", "08.00-09.40", "IF-202", "Laila Safitri"),
    ("IF508", "Pemrograman Game", 2, 5, "Jumat", "08.00-09.40", "LAB-MULTIMEDIA", "Intan Permata"),
    ("IF601", "Deep Learning", 3, 6, "Senin", "08.00-10.30", "LAB-AI", "Aditya Putra"),
    ("IF602", "Pemrosesan Bahasa Alami", 3, 6, "Senin", "10.40-13.10", "LAB-AI", "Nadia Putri"),
    ("IF603", "Forensik Digital", 3, 6, "Selasa", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana"),
    ("IF604", "Analisis Big Data", 3, 6, "Selasa", "10.40-13.10", "LAB-DATA", "Nadia Putri"),
    ("IF605", "Manajemen Layanan TI", 2, 6, "Rabu", "08.00-09.40", "IF-203", "Dina Kurniawati"),
    ("IF606", "Kewirausahaan Digital", 2, 6, "Kamis", "08.00-09.40", "IF-102", "Andi Pratama"),
    ("IF607", "Proyek Perangkat Lunak", 3, 6, "Jumat", "08.00-10.30", "LAB-1", "Dina Kurniawati"),
    ("IF701", "Seminar Proposal", 2, 7, "Senin", "08.00-09.40", "IF-301", "Dina Kurniawati"),
    ("IF702", "Kerja Praktik", 2, 7, "Selasa", "08.00-09.40", "IF-301", "Raka Pratama"),
    ("IF703", "Mata Kuliah Pilihan AI", 3, 7, "Rabu", "08.00-10.30", "LAB-AI", "Aditya Putra"),
    ("IF704", "Mata Kuliah Pilihan Keamanan Siber", 3, 7, "Kamis", "08.00-10.30", "LAB-JARINGAN", "Rizki Maulana"),
    ("IF801", "Skripsi", 6, 8, "Senin", "08.00-09.40", "IF-301", "Raka Pratama"),
    ("IF802", "Seminar Hasil dan Ujian Akhir", 2, 8, "Kamis", "08.00-09.40", "IF-301", "Dina Kurniawati"),
]

RUANG = {
    "IF-101": "Ruang kuliah teori lantai 1, kapasitas 40 orang",
    "IF-102": "Ruang kuliah teori lantai 1, kapasitas 40 orang",
    "IF-103": "Ruang kuliah teori lantai 1, kapasitas 35 orang",
    "IF-201": "Ruang kuliah teori lantai 2, kapasitas 40 orang",
    "IF-202": "Ruang kuliah teori lantai 2, kapasitas 40 orang",
    "IF-203": "Ruang kuliah teori lantai 2, kapasitas 35 orang",
    "IF-301": "Ruang seminar dan konsultasi tugas akhir, kapasitas 25 orang",
    "LAB-1": "Laboratorium Pemrograman, 30 komputer",
    "LAB-2": "Laboratorium Basis Data dan Sistem Komputer, 28 komputer",
    "LAB-JARINGAN": "Laboratorium Jaringan Komputer dan Keamanan Siber, 24 unit perangkat praktik",
    "LAB-AI": "Laboratorium Kecerdasan Buatan dan Komputasi, 25 workstation",
    "LAB-DATA": "Laboratorium Data Science, 25 workstation",
    "LAB-UX": "Laboratorium Interaksi Manusia-Komputer dan UI/UX, 20 workstation",
    "LAB-MULTIMEDIA": "Laboratorium Grafika, Multimedia, dan Game, 25 workstation",
    "LAB-CLOUD": "Laboratorium Cloud dan DevOps, 20 server virtual",
}

MATA_KULIAH = []
for _row in _RAW_MK:
    _kode, _nama, _sks, _semester, _hari, _jam, _ruang, _dosen = _row
    MATA_KULIAH.append({
        "kode": _kode, "nama": _nama, "sks": _sks, "semester": _semester,
        "hari": _hari, "jam": _jam, "ruang": _ruang, "dosen": _dosen,
        "prodi": "S1 Informatika", "kelas": f"IF{2026 - _semester + 1}-A",
    })

KURIKULUM = {
    1: ["Pendidikan Agama", "Pendidikan Pancasila", "Kalkulus", "Pengantar Informatika", "Algoritma dan Pemrograman", "Matematika Diskrit", "Bahasa Inggris", "Literasi Digital", "Dasar Sistem Komputer", "Bahasa Indonesia"],
    2: ["Struktur Data", "Basis Data", "Sistem Operasi", "Pemrograman Berorientasi Objek", "Aljabar Linear", "Organisasi dan Arsitektur Komputer", "Statistika dan Probabilitas", "Pendidikan Kewarganegaraan"],
    3: ["Jaringan Komputer", "Pemrograman Web", "Analisis dan Desain Algoritma", "Rekayasa Perangkat Lunak", "Sistem Informasi", "Interaksi Manusia dan Komputer", "Metode Numerik", "Praktikum Basis Data"],
    4: ["Kecerdasan Buatan", "Pemrograman Mobile", "Keamanan Informasi", "Manajemen Proyek Perangkat Lunak", "Teori Bahasa dan Otomata", "Grafika Komputer", "Etika Profesi", "Praktikum Jaringan Komputer"],
    5: ["Machine Learning", "Data Mining", "Pemrograman Berbasis Framework", "Komputasi Awan", "Sistem Terdistribusi", "Visi Komputer", "Metodologi Penelitian", "Pemrograman Game"],
    6: ["Deep Learning", "Pemrosesan Bahasa Alami", "Forensik Digital", "Analisis Big Data", "Manajemen Layanan TI", "Kewirausahaan Digital", "Proyek Perangkat Lunak"],
    7: ["Seminar Proposal", "Kerja Praktik", "Mata Kuliah Pilihan AI", "Mata Kuliah Pilihan Keamanan Siber"],
    8: ["Skripsi", "Seminar Hasil dan Ujian Akhir"],
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
    {"nama": "Beasiswa Prestasi Akademik", "syarat": "IPK minimal 3,50 (dummy), aktif kuliah, tidak sedang terkena sanksi", "berkas": "KTM, KTP, transkrip, surat rekomendasi, esai prestasi"},
    {"nama": "Beasiswa Bantuan Ekonomi", "syarat": "Memiliki kendala ekonomi berdasarkan verifikasi dokumen", "berkas": "KTM, KK, KTP, surat penghasilan orang tua, surat keterangan kondisi ekonomi"},
    {"nama": "KIP Kuliah", "syarat": "Mengikuti persyaratan dan seleksi program KIP Kuliah yang berlaku", "berkas": "Dokumen identitas, data keluarga, data ekonomi, dan dokumen pendidikan"},
    {"nama": "Beasiswa Mitra Industri", "syarat": "Mengikuti seleksi mitra dan memenuhi kriteria bidang studi", "berkas": "CV, transkrip, portofolio, surat motivasi"},
]

KALENDER_DUMMY = [
    ("Januari", "Registrasi ulang dan pengisian KRS semester genap"),
    ("Februari", "Awal perkuliahan semester genap"),
    ("Maret", "Perkuliahan dan evaluasi tugas"),
    ("April", "Ujian tengah semester genap"),
    ("Mei", "Perkuliahan dan praktikum"),
    ("Juni", "Ujian akhir semester genap dan input nilai"),
    ("Juli", "Libur semester dan administrasi akademik"),
    ("Agustus", "Registrasi ulang dan pengisian KRS semester ganjil"),
    ("September", "Awal perkuliahan semester ganjil"),
    ("Oktober", "Perkuliahan dan evaluasi tugas"),
    ("November", "Ujian tengah semester ganjil"),
    ("Desember", "Ujian akhir semester ganjil dan input nilai"),
]

# Data tabel pendukung (sebelumnya hanya berupa teks di ATURAN_AKADEMIK).
UKT_DUMMY = [
    ("Kelompok 1", "Rp500.000"), ("Kelompok 2", "Rp1.000.000"),
    ("Kelompok 3", "Rp2.500.000"), ("Kelompok 4", "Rp4.000.000"),
    ("Kelompok 5", "Rp5.500.000"), ("Kelompok 6", "Rp6.500.000"),
    ("Kelompok 7", "Rp7.500.000"),
]

SKS_DUMMY = [
    ("IPS >= 3,00", "24 SKS"), ("IPS 2,50 - 2,99", "22 SKS"),
    ("IPS 2,00 - 2,49", "20 SKS"), ("IPS < 2,00", "18 SKS"),
]

BOBOT_NILAI = [("A", 4), ("B", 3), ("C", 2), ("D", 1), ("E", 0)]
