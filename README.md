Buka '/.env/'
GEMINI_API_KEY=
abis itu masukkin api key nya

install dulu
pip install -r .\requirements.txt

dan untuk menghapus envrioment api terminal
Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:GEMINI_MODEL -ErrorAction SilentlyContinue

[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("GEMINI_MODEL", $null, "User")

ANGGOTA KELOMPOK
1. MUHAMMAD FAREL FRESH DANI
2. RAYHAN FADILAH OESMAN
3. DIMAS BAGUS SAPUTRA
4. RAIHAN MUHAMMAD IKHSAN
5. INDAH AZZAHRA
