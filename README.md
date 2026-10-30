# Dashboard Analisis Populasi dan Ekonomi Dunia

Proyek tugas Visualisasi Data dan Informasi: integrasi dua DBMS menggunakan Python.

## 1. Arsitektur

- **SQLite**: menyimpan data indikator negara (populasi dan GDP per kapita).
- **MongoDB**: menyimpan metadata negara (wilayah dan kelompok pendapatan) serta log aktivitas dashboard.
- **Pandas**: menggabungkan data indikator SQLite dengan metadata negara MongoDB menggunakan `merge(on='country_code')`.
- **Streamlit + Plotly**: antarmuka web dan visualisasi interaktif.

Alur: World Bank API -> skrip seed -> SQLite. Aplikasi membaca metadata negara dari MongoDB, lalu Pandas menggabungkan kedua hasil query berdasarkan `country_code`. Hasil integrasi ditampilkan melalui Streamlit/Plotly. Aktivitas dashboard juga dicatat ke MongoDB.

## 2. Sumber data dan referensi

- World Bank Population: https://data.worldbank.org/indicator/SP.POP.TOTL
- World Bank GDP per capita: https://data.worldbank.org/indicator/NY.GDP.PCAP.CD
- World Bank API: https://api.worldbank.org/
- Dokumentasi Streamlit: https://docs.streamlit.io/
- Dokumentasi PyMongo: https://www.mongodb.com/docs/drivers/pymongo/
- Referensi kode/inspirasi teknis: https://github.com/streamlit/streamlit

Data indikator diunduh langsung dari API World Bank oleh `database/seed_data.py`.
Metadata wilayah/kelompok pendapatan di MongoDB merupakan metadata klasifikasi yang disiapkan untuk proyek; log MongoDB merupakan data aktivitas yang dihasilkan aplikasi, bukan dataset eksternal. Jelaskan asal dan cara penyusunan metadata ini di laporan.

## 3. Menjalankan di VS Code

Pastikan Python 3.10+ dan VS Code sudah terpasang.

### Windows PowerShell

```powershell
# 1. Buka folder proyek di VS Code, lalu buka Terminal
# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan environment
.venv\Scripts\Activate.ps1

# Jika aktivasi diblokir, jalankan perintah ini sekali untuk terminal saat ini:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1

# 4. Install library
pip install -r requirements.txt

# 5. Salin .env.example menjadi .env, lalu isi MONGO_URI dari MongoDB Atlas
# 6. Ambil data World Bank dan buat database SQLite
python database/seed_data.py

# 7. Jalankan dashboard
streamlit run app.py
```

Aplikasi akan terbuka di browser, biasanya pada http://localhost:8501.

## 4. Menyiapkan MongoDB Atlas

1. Buat akun di https://www.mongodb.com/atlas.
2. Buat cluster gratis (jika tersedia pada akun/wilayah).
3. Buat database user dan password.
4. Pada Network Access, izinkan IP komputer yang digunakan.
5. Pilih Connect -> Drivers -> Python, lalu salin connection string.
6. Tempelkan ke `MONGO_URI` pada file `.env`, ganti username, password, dan alamat cluster.
7. Jangan pernah mengunggah `.env` ke GitHub.

Jika MongoDB belum diatur, dashboard masih dapat menampilkan data SQLite, tetapi syarat integrasi dua DBMS belum terpenuhi sampai MongoDB tersambung.

## 5. Deploy ke Streamlit Community Cloud

1. Upload seluruh folder proyek ke repositori GitHub publik.
2. Buka https://share.streamlit.io/ dan hubungkan GitHub.
3. Pilih repositori dan file utama `app.py`.
4. Pada pengaturan aplikasi, masukkan `MONGO_URI` dan `MONGO_DB` di bagian Secrets.
5. Deploy.

**Catatan penting:** SQLite lokal pada hosting dapat bersifat sementara dan tidak ideal sebagai database produksi. Untuk demo tugas, skrip seed dapat dijalankan saat build/deploy atau data SQLite dapat diganti dengan database persisten. Jangan memasukkan password database ke kode.

## 6. Fitur dashboard

- Filter negara dan rentang tahun.
- Grafik garis populasi.
- Grafik garis GDP per kapita.
- Grafik perbandingan populasi.
- Tabel data terintegrasi.
- Unduh data hasil filter ke CSV.
- Pencatatan aktivitas ke MongoDB.

## 7. Struktur repositori

```text
dashboard_vdi/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── database/
    └── seed_data.py
```

Database SQLite dibuat otomatis ketika skrip seed dijalankan.
