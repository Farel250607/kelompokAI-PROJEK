"""Knowledge Base chatbot: intent -> pola kata kunci + respons."""

knowledge_base = {
    "greeting": {
        "patterns": ["halo", "hai", "selamat pagi", "selamat siang",
                     "selamat sore", "assalamualaikum", "permisi"],
        "responses": [
            "Halo! Saya Chatbot Layanan Akademik UNP. Ada yang bisa saya bantu?"
        ],
    },
    "jadwal_kuliah": {
        "patterns": ["jadwal kuliah", "jadwal kelas", "kapan kuliah",
                     "jam berapa kuliah", "jadwal perkuliahan"],
        "responses": [
            "CONTOH DATA DUMMY JADWAL KULIAH (BUKAN JADWAL RESMI UNP):\n"
            "Senin: 08.00-09.40 Matematika Teknik (Ruang A1.2); 10.00-11.40 Bahasa Indonesia (Ruang A1.2).\n"
            "Selasa: 08.00-09.40 Gambar Teknik (Lab Gambar); 13.00-14.40 Fisika Dasar (Ruang B2.1).\n"
            "Rabu: 09.00-10.40 Material Teknik (Ruang A2.3); 13.00-15.30 Praktikum Komputer (Lab Komputer).\n"
            "Kamis: 08.00-09.40 Matematika Teknik (Ruang A1.2); 10.00-11.40 Mekanika Teknik (Ruang B1.1).\n"
            "Jumat: 08.00-09.40 Pendidikan Pancasila (Ruang A1.2).\n"
            "Data ini hanya contoh untuk demonstrasi chatbot. Jadwal sebenarnya harus dilihat di Portal Akademik UNP."
        ],
    },
    "krs": {
        "patterns": ["krs", "kartu rencana studi", "isi krs",
                     "pengisian krs", "ubah krs", "ambil mata kuliah"],
        "responses": [
            "KRS (Kartu Rencana Studi) berisi mata kuliah yang direncanakan untuk diambil pada semester berjalan. Periksa kalender akademik dan portal akademik UNP untuk periode pengisian. Konsultasikan rencana studi dengan dosen PA."
        ],
    },
    "khs": {
        "patterns": ["khs", "kartu hasil studi", "nilai semester",
                     "lihat nilai", "hasil studi", "nilai mata kuliah"],
        "responses": [
            "KHS (Kartu Hasil Studi) menampilkan hasil studi pada semester tertentu. Periksa portal akademik mahasiswa UNP. Jika nilai belum muncul atau tidak sesuai, hubungi dosen pengampu atau program studi."
        ],
    },
    "ukt": {
        "patterns": ["ukt", "uang kuliah tunggal", "pembayaran kuliah",
                     "bayar kuliah", "tagihan kuliah", "keringanan ukt",
                     "penurunan ukt", "cicilan ukt"],
        "responses": [
            "Informasi tagihan, jadwal pembayaran, dan permohonan terkait UKT dapat berubah setiap periode. Periksa pengumuman resmi UNP atau hubungi bagian keuangan/layanan mahasiswa untuk informasi yang berlaku."
        ],
    },
    "kalender_akademik": {
        "patterns": ["kalender akademik", "kalender kuliah", "awal semester",
                     "akhir semester", "jadwal ujian", "uts", "uas",
                     "libur semester"],
        "responses": [
            "Tanggal awal semester, UTS, UAS, dan kegiatan akademik lainnya mengikuti kalender akademik resmi UNP. Gunakan kalender untuk tahun akademik yang sedang berjalan."
        ],
    },
    "cuti_akademik": {
        "patterns": ["cuti kuliah", "cuti akademik", "izin tidak kuliah",
                     "berhenti sementara", "pengajuan cuti"],
        "responses": [
            "Prosedur cuti akademik, tenggat pengajuan, dan persyaratannya perlu dikonfirmasi melalui program studi atau bagian akademik UNP sebelum periode pengajuan berakhir."
        ],
    },
    "lokasi_kampus": {
        "patterns": ["lokasi kampus", "alamat kampus", "dimana kampus",
                     "kampus unp dimana", "alamat universitas negeri padang"],
        "responses": [
            "Kampus utama Universitas Negeri Padang berada di kawasan Air Tawar, Kota Padang, Sumatera Barat. Untuk lokasi gedung atau fakultas tertentu, periksa peta dan informasi resmi UNP."
        ],
    },
    "kontak_admin": {
        "patterns": ["kontak admin", "hubungi admin", "nomor admin",
                     "kontak akademik", "email akademik", "hubungi bagian akademik"],
        "responses": [
            "Untuk menghindari informasi kontak yang keliru, gunakan halaman kontak resmi Universitas Negeri Padang atau hubungi administrasi fakultas/program studi."
        ],
    },
    "wisuda": {
        "patterns": ["wisuda", "pendaftaran wisuda", "syarat wisuda",
                     "jadwal wisuda", "daftar wisuda"],
        "responses": [
            "Persyaratan, jadwal, dan pendaftaran wisuda mengikuti pengumuman resmi UNP. Periksa persyaratan akademik, administrasi, dan tenggat pendaftaran pada periode wisuda yang dituju."
        ],
    },
    "terima_kasih": {
        "patterns": ["terima kasih", "makasih", "thanks", "terima kasih banyak"],
        "responses": ["Sama-sama! Semoga informasi ini membantu."],
    },
    "goodbye": {
        "patterns": ["bye", "sampai jumpa", "keluar", "exit", "selamat tinggal"],
        "responses": ["Sampai jumpa! Semoga urusan akademikmu lancar."],
    },
    "ruang_kuliah": {
        "patterns": ["ruang kuliah", "lokasi kelas", "kelas di ruang mana",
                     "ruangan mata kuliah", "ruang perkuliahan"],
        "responses": [
            "CONTOH DATA DUMMY: Matematika Teknik di A1.2, Fisika Dasar di B2.1, Gambar Teknik di Lab Gambar, dan Praktikum Komputer di Lab Komputer. Ini hanya data simulasi, bukan informasi ruang resmi UNP."
        ],
    },
    "dosen_pa": {
        "patterns": ["dosen pa", "dosen pembimbing akademik", "siapa dosen pa",
                     "fungsi dosen pa", "konsultasi dosen wali"],
        "responses": [
            "Dosen PA membantu mahasiswa merencanakan studi, memberi arahan pemilihan mata kuliah, memantau perkembangan akademik, dan memberi konsultasi. Nama dosen PA pada contoh data dummy adalah Ibu Rina, M.Pd.; nama ini bukan data resmi."
        ],
    },
    "registrasi": {
        "patterns": ["registrasi ulang", "daftar ulang", "herregistrasi",
                     "aktif kuliah", "status mahasiswa aktif"],
        "responses": [
            "Secara umum, registrasi ulang dilakukan dengan memeriksa kewajiban administrasi, menyelesaikan pembayaran sesuai ketentuan, lalu memastikan status mahasiswa aktif pada portal akademik. Jadwal dan prosedur resmi harus mengikuti pengumuman UNP."
        ],
    },
    "presensi": {
        "patterns": ["presensi", "absensi", "kehadiran kuliah",
                     "persentase kehadiran", "tidak hadir kuliah"],
        "responses": [
            "CONTOH ATURAN DUMMY: Mahasiswa dianjurkan hadir minimal 75% dari pertemuan. Angka ini hanya contoh simulasi; ketentuan sebenarnya mengikuti RPS dan aturan mata kuliah."
        ],
    },
    "praktikum": {
        "patterns": ["praktikum", "jadwal lab", "laboratorium",
                     "laporan praktikum", "asisten praktikum"],
        "responses": [
            "Contoh jadwal praktikum dummy: Praktikum Komputer setiap Rabu pukul 13.00-15.30 di Lab Komputer. Mahasiswa menyiapkan modul, mengikuti instruksi keselamatan laboratorium, mengisi daftar hadir, dan mengumpulkan laporan sesuai arahan asisten."
        ],
    },
    "perpustakaan": {
        "patterns": ["perpustakaan", "pinjam buku", "peminjaman buku",
                     "pengembalian buku", "kartu anggota perpustakaan"],
        "responses": [
            "Layanan perpustakaan umumnya meliputi membaca di tempat, pencarian koleksi, peminjaman, dan pengembalian buku. Contoh data dummy: batas peminjaman 7 hari dengan maksimal 3 buku. Ketentuan sebenarnya perlu diperiksa pada layanan perpustakaan UNP."
        ],
    },
    "beasiswa": {
        "patterns": ["beasiswa", "pendaftaran beasiswa", "syarat beasiswa",
                     "kip kuliah", "bantuan pendidikan"],
        "responses": [
            "Persyaratan beasiswa berbeda menurut program. Umumnya mahasiswa perlu menyiapkan identitas, bukti status aktif, transkrip atau IPK, surat keterangan penghasilan jika diminta, dan dokumen pendukung. Periksa pengumuman resmi untuk syarat dan tenggat yang berlaku."
        ],
    },
    "transkrip": {
        "patterns": ["transkrip nilai", "cetak transkrip", "nilai kumulatif",
                     "daftar nilai", "transkrip akademik"],
        "responses": [
            "Transkrip akademik merangkum mata kuliah dan nilai yang telah ditempuh. Contoh alur: masuk portal akademik, buka menu hasil studi atau transkrip, periksa data, lalu ikuti prosedur fakultas jika membutuhkan transkrip yang disahkan."
        ],
    },
    "yudisium": {
        "patterns": ["yudisium", "syarat yudisium", "pendaftaran yudisium",
                     "daftar yudisium"],
        "responses": [
            "Yudisium merupakan proses penetapan kelulusan akademik mahasiswa. Persyaratan umum dapat mencakup penyelesaian seluruh mata kuliah, pemenuhan SKS, penyelesaian tugas akhir, dan administrasi. Persyaratan resmi berbeda menurut program studi dan periode."
        ],
    },
    "skripsi_tugas_akhir": {
        "patterns": ["skripsi", "tugas akhir", "proposal penelitian",
                     "seminar proposal", "sidang skripsi", "ujian tugas akhir"],
        "responses": [
            "Tahapan umum tugas akhir meliputi penentuan topik, konsultasi dengan calon pembimbing, penyusunan proposal, seminar proposal, pengumpulan dan analisis data, penulisan laporan, serta ujian akhir. Alur dan formulir resmi mengikuti ketentuan program studi."
        ],
    },
    "magang": {
        "patterns": ["magang", "praktik industri", "praktik kerja lapangan",
                     "pkl", "kerja praktik"],
        "responses": [
            "Persiapan magang umumnya mencakup mencari tempat magang, memenuhi persyaratan program studi, mengajukan surat pengantar, memperoleh persetujuan, melaksanakan kegiatan, dan menyusun laporan. Durasi dan prosedur harus dikonfirmasi ke program studi."
        ],
    },
    "organisasi_mahasiswa": {
        "patterns": ["organisasi mahasiswa", "ukm", "himpunan mahasiswa",
                     "bem", "kegiatan kemahasiswaan"],
        "responses": [
            "Mahasiswa dapat mengikuti organisasi seperti himpunan mahasiswa, BEM, atau UKM sesuai minat. Contoh kegiatan meliputi rapat, pelatihan, kompetisi, pengabdian masyarakat, dan kegiatan pengembangan minat bakat."
        ],
    },
    "wifi_kampus": {
        "patterns": ["wifi kampus", "internet kampus", "akun wifi",
                     "koneksi internet", "jaringan kampus"],
        "responses": [
            "Jika mengalami masalah Wi-Fi kampus, pastikan Wi-Fi aktif, pilih jaringan resmi, periksa akun akses jika diperlukan, lalu hubungi unit layanan TIK kampus. Nama jaringan dan prosedur akun perlu mengikuti informasi resmi."
        ],
    },
    "fasilitas_kampus": {
        "patterns": ["fasilitas kampus", "toilet kampus", "parkir kampus",
                     "kantin kampus", "ruang baca"],
        "responses": [
            "Fasilitas kampus dapat mencakup ruang kelas, laboratorium, perpustakaan, tempat ibadah, kantin, area parkir, dan ruang kegiatan mahasiswa. Lokasi serta jam operasional perlu diperiksa melalui informasi kampus."
        ],
    },
    "nilai_ipk": {
        "patterns": ["ipk", "indeks prestasi kumulatif", "ips",
                     "indeks prestasi semester", "menghitung ipk"],
        "responses": [
            "IPS menggambarkan capaian akademik dalam satu semester, sedangkan IPK merupakan rata-rata prestasi kumulatif dengan memperhitungkan bobot SKS. Untuk menghitungnya, jumlahkan nilai mutu seluruh mata kuliah lalu bagi dengan total SKS yang diperhitungkan."
        ],
    },
    "semester_pendek": {
        "patterns": ["semester pendek", "semester antara", "kuliah antara",
                     "mengulang mata kuliah"],
        "responses": [
            "Semester pendek atau semester antara dapat diselenggarakan sesuai kebijakan perguruan tinggi dan program studi. Mata kuliah yang dibuka, biaya, jadwal, dan syarat peserta harus diperiksa pada pengumuman resmi."
        ],
    },
    "kartu_mahasiswa": {
        "patterns": ["kartu mahasiswa", "ktm", "kartu tanda mahasiswa",
                     "ktm hilang", "cetak ktm"],
        "responses": [
            "Kartu Tanda Mahasiswa digunakan sebagai identitas mahasiswa. Jika hilang atau rusak, mahasiswa dapat menanyakan prosedur penggantian kepada layanan administrasi atau kemahasiswaan."
        ],
    },
    "cuti_kembali_aktif": {
        "patterns": ["aktif kembali", "setelah cuti", "mengakhiri cuti",
                     "kembali kuliah setelah cuti"],
        "responses": [
            "Mahasiswa yang akan aktif kembali setelah cuti perlu memastikan masa cuti telah berakhir, mengurus administrasi sesuai prosedur, dan mengonfirmasi status aktif sebelum mengisi KRS."
        ],
    },
}
