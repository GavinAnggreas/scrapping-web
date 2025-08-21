# 🎌 Anime Search Website

Website sederhana untuk mencari dan menampilkan anime dari [Nonton Anime ID](https://s7.nontonanimeid.boats).

## ✨ Fitur

- 🔍 **Pencarian Anime**: Cari anime berdasarkan judul
- 📺 **Anime Terbaru**: Lihat daftar anime terbaru (50-500 anime)
- 🖼️ **Gambar Anime**: Tampilkan gambar anime dari `div class="sera"`
- ⭐ **Rating Lengkap**: Rating dari `span class="value"` dan type anime
- 📋 **Details Lengkap**: Informasi detail dari `ul class="details-list"`
- 📺 **Daftar Episode**: Semua episode dengan link langsung ke nontonanime
- 📱 **Responsive Design**: Tampilan yang bagus di desktop dan mobile
- 🎯 **Detail Anime**: Klik anime untuk melihat semua informasi lengkap

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
python anime_scraper.py
```

### 3. Buka Browser

Buka browser dan kunjungi: **http://localhost:5000**

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python Flask
- **Web Scraping**: BeautifulSoup4 + Requests
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: CSS Grid, Flexbox, Gradients

## 📋 Cara Penggunaan

1. **Lihat Anime Terbaru**: Biarkan kolom pencarian kosong dan klik "Cari"
2. **Pilih Jumlah Anime**: Gunakan dropdown untuk memilih 50, 100, 200, atau 500 anime
3. **Cari Anime**: Masukkan judul anime di kolom pencarian
4. **Lihat Detail**: Klik pada kartu anime untuk melihat semua informasi lengkap
5. **Lihat Rating**: Rating ditampilkan dengan bintang dan type anime
6. **Lihat Details**: Informasi lengkap seperti English title, synonyms, dll
7. **Lihat Episodes**: Daftar semua episode dengan link langsung ke nontonanime
8. **Tutup Modal**: Klik tombol X atau klik di luar modal

## 🔧 Struktur Kode

- `anime_scraper.py` - File utama dengan backend Flask dan frontend HTML
- `requirements.txt` - Dependencies Python yang diperlukan
- `README.md` - Dokumentasi ini

## 📱 API Endpoints

- `GET /api/search?q=<query>` - Cari anime berdasarkan query
- `GET /api/anime/<url>` - Dapatkan detail anime berdasarkan URL
- `GET /` - Halaman utama website

## ⚠️ Catatan Penting

- Website ini menggunakan web scraping, jadi pastikan untuk menghormati robots.txt
- Gunakan dengan bijak dan sesuai dengan Terms of Service website target
- Rate limiting mungkin diperlukan untuk penggunaan yang intensif

## 🎨 Customization

Anda dapat mengubah:
- Warna dan styling di bagian CSS
- Layout dan komponen di bagian HTML
- Logika scraping di fungsi Python
- Endpoint API sesuai kebutuhan

## 📞 Support

Jika ada masalah atau pertanyaan, silakan buat issue atau hubungi developer.
