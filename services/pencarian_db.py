"""Pencarian pada database akademik dummy; hasil data tampil sebagai tabel."""

import re

from data.akademik import (
    ATURAN_AKADEMIK, BEASISWA, BOBOT_NILAI, DOSEN, DOSEN_PA, FAKULTAS,
    KALENDER_DUMMY, KURIKULUM, MATA_KULIAH, RUANG, SKS_DUMMY, UKT_DUMMY,
)
from utils.tabel import render_table, tabel_detail
from utils.teks import preprocess

HARI_URUT = {"senin": 1, "selasa": 2, "rabu": 3, "kamis": 4, "jumat": 5, "sabtu": 6}

CATATAN_SIMULASI = "Catatan: ketentuan di atas adalah contoh simulasi, bukan peraturan resmi UNP."


# ------------------------------------------------------------
# MATA KULIAH
# ------------------------------------------------------------
def cari_data_mata_kuliah(user_input):
    q = preprocess(user_input)
    hari = next((h for h in HARI_URUT if h in q), None)
    semester_match = re.search(r"semester\s+(\d+)", q)
    hasil = []

    # Nama atau kode mata kuliah spesifik.
    for mk in MATA_KULIAH:
        if mk["kode"].lower() in q or preprocess(mk["nama"]) in q:
            hasil.append(mk)

    # Pertanyaan tentang dosen pengampu.
    if not hasil:
        for mk in MATA_KULIAH:
            if preprocess(mk["dosen"]) in q and any(k in q for k in ["jadwal", "mengajar", "ampu", "mata kuliah"]):
                hasil.append(mk)

    # Jadwal per hari, semester, atau seluruh jadwal.
    if not hasil and hari and any(k in q for k in ["jadwal", "kuliah", "kelas", "matkul"]):
        hasil = [m for m in MATA_KULIAH if m["hari"].lower() == hari]
        if semester_match:
            hasil = [m for m in hasil if m["semester"] == int(semester_match.group(1))]
    if not hasil and semester_match and any(k in q for k in ["mata kuliah", "matkul", "kurikulum", "semester"]):
        hasil = [m for m in MATA_KULIAH if m["semester"] == int(semester_match.group(1))]
    if not hasil and any(k in q for k in ["semua jadwal", "jadwal lengkap", "seluruh jadwal"]):
        hasil = MATA_KULIAH

    if not hasil:
        return None

    hasil = sorted(hasil, key=lambda m: (m["semester"],
                                         HARI_URUT.get(m["hari"].lower(), 9),
                                         m["jam"]))
    rows = [[i, m["kode"], m["nama"], m["sks"], m["semester"],
             m["hari"], m["jam"], m["ruang"], m["dosen"]]
            for i, m in enumerate(hasil, 1)]
    return render_table(
        ["No", "Kode", "Mata Kuliah", "SKS", "Smt", "Hari", "Jam", "Ruang", "Dosen"],
        rows,
        title=f"JADWAL & MATA KULIAH S1 INFORMATIKA (DATA DUMMY) - {len(hasil)} data",
        note="Catatan: seluruh jadwal, dosen, kode, dan ruang adalah data fiktif, bukan jadwal resmi UNP.",
    )


# ------------------------------------------------------------
# DOSEN
# ------------------------------------------------------------
def cari_data_dosen(user_input):
    q = preprocess(user_input)
    found = []
    for d in DOSEN:
        nama_key = preprocess(d["nama"])
        nama_singkat = preprocess(d["nama"].split(",")[0])
        if nama_key in q or (len(nama_singkat) > 4 and nama_singkat in q):
            found.append(d)
    if not found and any(k in q for k in ["semua dosen", "daftar dosen", "data dosen", "nama dosen", "dosen informatika"]):
        found = DOSEN
    if not found:
        return None

    note = "Semua identitas, NIDN, email, jabatan, dan ruang dosen di atas fiktif."

    # Satu dosen: tampilkan detail lengkap (tabel vertikal).
    if len(found) == 1:
        d = found[0]
        pairs = [
            ("Nama", d["nama"]),
            ("NIDN (dummy)", d["nidn"]),
            ("Jabatan", d["jabatan"]),
            ("Bidang", d["bidang"]),
            ("Email (dummy)", d["email"]),
            ("Ruang", d["ruang"]),
            ("Kelas PA", ", ".join(d["pa"]) if d["pa"] else "Belum ditetapkan"),
        ]
        return tabel_detail(pairs, "DATA DOSEN S1 INFORMATIKA (DATA DUMMY)", note)

    # Banyak dosen: tabel ringkas.
    rows = [[i, d["nama"], d["bidang"], d["email"], d["ruang"],
             ", ".join(d["pa"]) if d["pa"] else "-"]
            for i, d in enumerate(found, 1)]
    return render_table(
        ["No", "Nama", "Bidang", "Email", "Ruang", "Kelas PA"],
        rows,
        title="DAFTAR DOSEN S1 INFORMATIKA (DATA DUMMY)",
        note=note,
    )


# ------------------------------------------------------------
# DOSEN PA
# ------------------------------------------------------------
def cari_dosen_pa(user_input):
    q = preprocess(user_input)
    m = re.search(r"(20\d{2})", q)
    angkatan = int(m.group(1)) if m else None
    rows_src = [x for x in DOSEN_PA if x["angkatan"] == angkatan] if angkatan else DOSEN_PA
    if not any(k in q for k in ["dosen pa", "dosen pembimbing", "dosen wali", "angkatan", "pa saya", "pembimbing akademik"]):
        return None
    if not rows_src:
        return None
    rows = [[x["angkatan"], x["kode_kelas"], x["dosen"], x["email"]] for x in rows_src]
    return render_table(
        ["Angkatan", "Kelas", "Dosen PA", "Email"],
        rows,
        title="DAFTAR DOSEN PEMBIMBING AKADEMIK (DATA DUMMY)",
        note="Penetapan dosen PA pada daftar ini hanya simulasi.",
    )


# ------------------------------------------------------------
# INFORMASI LAIN
# ------------------------------------------------------------
def cari_informasi_lain(user_input):
    q = preprocess(user_input)

    if any(k in q for k in ["fakultas", "program studi", "prodi informatika", "profil informatika", "kaprodi"]):
        p = FAKULTAS["program_studi"][0]
        pairs = [
            ("Fakultas", FAKULTAS["nama"]),
            ("Program Studi", f"{p['nama']} ({p['kode']})"),
            ("Jenjang", p["jenjang"]),
            ("Gelar", p["gelar"]),
            ("Departemen", p["departemen"]),
            ("Akreditasi (contoh)", p["akreditasi"]),
            ("Lama Studi", p["lama_studi"]),
            ("Target Kurikulum", f"{p['total_sks']} SKS (simulasi)"),
            ("Ketua Prodi (dummy)", p["ketua"]),
        ]
        return tabel_detail(pairs, "PROFIL AKADEMIK (DATA DUMMY)",
                            "Seluruh rincian profil ini dibuat untuk demonstrasi.")

    if "kurikulum" in q or "daftar mata kuliah per semester" in q:
        sem_match = re.search(r"semester\s+(\d+)", q)
        semesters = ([int(sem_match.group(1))]
                     if sem_match and int(sem_match.group(1)) in KURIKULUM
                     else list(KURIKULUM))
        rows, ringkas = [], []
        for sem in semesters:
            mks = [m for m in MATA_KULIAH if m["semester"] == sem]
            rows += [[sem, m["kode"], m["nama"], m["sks"]] for m in mks]
            ringkas.append(f"Smt {sem}: {sum(m['sks'] for m in mks)} SKS")
        return render_table(
            ["Smt", "Kode", "Mata Kuliah", "SKS"], rows,
            title="KURIKULUM S1 INFORMATIKA (DATA DUMMY)",
            note="Total SKS terdata -> " + " | ".join(ringkas) +
                 ". Kurikulum dan SKS adalah rancangan fiktif untuk demonstrasi.",
        )

    if "ruang" in q and any(k in q for k in ["lab", "laboratorium", "daftar ruang", "ruang kelas", "fasilitas"]):
        return render_table(["Kode Ruang", "Keterangan"], list(RUANG.items()),
                            title="DAFTAR RUANG DAN LABORATORIUM (DATA DUMMY)")

    if any(k in q for k in ["daftar laboratorium", "laboratorium apa", "apa saja laboratorium", "daftar lab", "lab informatika"]):
        rows = [(k, v) for k, v in RUANG.items() if k.startswith("LAB-")]
        return render_table(["Kode Lab", "Keterangan"], rows,
                            title="DAFTAR LABORATORIUM INFORMATIKA (DATA DUMMY)")

    if any(k in q for k in ["beasiswa", "kip kuliah"]):
        rows = [[b["nama"], b["syarat"], b["berkas"]] for b in BEASISWA]
        return render_table(
            ["Program Beasiswa", "Syarat", "Berkas"], rows,
            title="PROGRAM BEASISWA (DATA DUMMY)",
            note="Seluruh kriteria seleksi di sini adalah simulasi; verifikasi ke pengumuman resmi.",
        )

    if any(k in q for k in ["kalender akademik", "jadwal uts", "jadwal uas", "awal semester", "akhir semester"]):
        return render_table(["Bulan", "Agenda"], KALENDER_DUMMY,
                            title="KALENDER AKADEMIK (DATA DUMMY)",
                            note="Bulan dan agenda hanya contoh, bukan tanggal resmi.")

    mapping = {
        "krs": ["krs", "kartu rencana studi", "isi krs", "ubah krs"],
        "khs": ["khs", "kartu hasil studi", "lihat nilai", "nilai semester"],
        "ipk": ["ipk", "ips", "indeks prestasi", "hitung ipk"],
        "sks": ["sks", "beban studi", "maksimal sks", "jumlah sks"],
        "ukt": ["ukt", "uang kuliah", "biaya kuliah", "tarif kuliah"],
        "registrasi": ["registrasi", "daftar ulang", "herregistrasi"],
        "cuti": ["cuti", "nonaktif", "kembali aktif"],
        "praktikum": ["praktikum", "laboratorium", "aturan lab"],
        "magang": ["magang", "kerja praktik", "pkl"],
        "skripsi": ["skripsi", "tugas akhir", "seminar proposal", "ujian skripsi"],
        "wisuda": ["wisuda", "yudisium", "syarat lulus"],
        "presensi": ["presensi", "absensi", "kehadiran"],
        "kalender": ["kalender", "uts", "uas"],
    }

    for key, patterns in mapping.items():
        if any(x in q for x in patterns):
            if key == "ukt":
                return render_table(
                    ["Kelompok UKT", "Nominal per Semester"], UKT_DUMMY,
                    title="CONTOH KELOMPOK UKT INFORMATIKA (DATA DUMMY)",
                    note="Nominal fiktif untuk demonstrasi, bukan tarif UNP.")
            if key == "sks":
                return render_table(
                    ["IPS Semester Sebelumnya", "Maksimal SKS"], SKS_DUMMY,
                    title="CONTOH BEBAN STUDI MAKSIMUM (DATA DUMMY)",
                    note="Ini bukan ketentuan resmi UNP.")
            if key == "ipk":
                tabel = render_table(["Nilai Huruf", "Bobot"], BOBOT_NILAI,
                                     title="CONTOH BOBOT NILAI (DATA DUMMY)")
                return ATURAN_AKADEMIK["ipk"] + "\n\n" + tabel + "\n" + CATATAN_SIMULASI
            return ATURAN_AKADEMIK[key] + "\n\n" + CATATAN_SIMULASI

    if any(k in q for k in ["wifi", "internet kampus", "jaringan kampus"]):
        return "Bantuan Wi-Fi dummy: aktifkan Wi-Fi, pilih SSID UNP-ACADEMIC-DUMMY, login memakai akun simulasi, lupakan jaringan lalu sambungkan ulang jika gagal. SSID ini fiktif dan bukan jaringan resmi."

    if any(k in q for k in ["fasilitas kampus", "perpustakaan", "kantin", "parkir", "tempat ibadah"]):
        return "Fasilitas contoh di lingkungan prodi: ruang kuliah IF-101 s.d. IF-301, Lab Pemrograman, Lab Basis Data, Lab Jaringan, Lab AI, Lab Data Science, Lab UX, Lab Multimedia, Lab Cloud, perpustakaan, kantin, area parkir, dan tempat ibadah. Lokasi ini data simulasi."

    return None


# Urutan pencarian yang dipakai chatbot.
PENCARIAN_DATABASE = (
    cari_data_mata_kuliah,
    cari_dosen_pa,
    cari_data_dosen,
    cari_informasi_lain,
)
