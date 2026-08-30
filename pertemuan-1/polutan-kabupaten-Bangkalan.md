# Polutan Kabupaten Bangkalan

Halaman ini merupakan pintu masuk utama untuk analisis kualitas udara dan pemetaan polutan di **Kabupaten Bangkalan, Madura**. Analisis ini menggunakan data observasi atmosfer yang diperoleh dari instrumen **TROPOMI** pada satelit **Copernicus Sentinel-5P**.

Tujuan utama dari modul ini adalah untuk memahami kondisi kualitas udara secara spasial dan temporal, serta menganalisis pola penyebaran gas-gas polutan utama.

---

## Daftar Isi Modul

Analisis pada modul ini dibagi menjadi beberapa tahapan penting yang saling berkaitan:

1. **[Business Understanding](business-understanding.md)**
   * Membahas latar belakang proyek, perumusan masalah, tujuan analisis, serta pemahaman teoretis mengenai empat zat polutan utama yang diamati (CO, NO₂, SO₂, dan CH₄).
2. **[Data Understanding](data-understanding.md)**
   * Menjelaskan proses pengumpulan data (*data collecting*) dari server openEO, penentuan batas wilayah (*Area of Interest* - AOI) Kabupaten Bangkalan, pemrosesan awal data (*data preprocessing*), hingga analisis kualitas data seperti deteksi pencilan (*outliers*) dan reduksi derau (*noise*).

---

## Parameter Polutan yang Diamati

Dalam proyek ini, terdapat empat parameter gas atmosfer utama yang dipantau untuk menilai kualitas udara di Kabupaten Bangkalan:

| Polutan | Deskripsi Singkat | Sumber Utama |
| :---: | :--- | :--- |
| **CO** (Karbon Monoksida) | Gas tidak berwarna dan tidak berbau yang dihasilkan dari pembakaran tidak sempurna. | Lalu lintas kendaraan bermotor, aktivitas industri, dan pembakaran biomassa. |
| **NO₂** (Nitrogen Dioksida) | Gas indikator polusi udara perkotaan yang berhubungan erat dengan emisi pembakaran. | Kendaraan bermotor, pembangkit listrik, dan pembakaran bahan bakar fosil. |
| **SO₂** (Sulfur Dioksida) | Gas berbau tajam yang dapat memicu hujan asam dan masalah pernapasan. | Pembakaran batubara/minyak bumi pada industri dan emisi pembangkit listrik. |
| **CH₄** (Metana) | Gas rumah kaca kuat yang berkontribusi signifikan terhadap pemanasan global. | TPA (Tempat Pembuangan Akhir), aktivitas pertanian/peternakan, dan kebocoran gas alam. |

---

## Alur Analisis Data

Metodologi analisis kualitas udara di Kabupaten Bangkalan mengikuti langkah-langkah terstruktur berikut:

1. **Definisi Masalah & Tujuan (Business Understanding)**: Memahami latar belakang kualitas udara dan menetapkan target analisis parameter polutan.
2. **Koneksi & Unduh Data**: Melakukan autentikasi ke Copernicus Data Space dan memproses koleksi data Sentinel-5P L2 melalui openEO.
3. **Pemotongan Area (Clipping)**: Membatasi pengamatan satelit pada area polygon batas administrasi Kabupaten Bangkalan.
4. **Agregasi Data**: Menghitung rata-rata harian secara spasial untuk mendapatkan deret waktu (*time-series*) yang kontinu.
5. **Deteksi Pencilan (Outliers)**: Mengidentifikasi dan menangani nilai ekstrem/pencilan menggunakan algoritma *Isolation Forest*.
6. **Reduksi Derau (Noise Reduction)**: Menerapkan fungsi *Moving Average* (rata-rata bergerak harian) untuk meredam fluktuasi acak harian.
7. **Visualisasi & Interpretasi**: Menyajikan data akhir dalam peta interaktif (menggunakan `folium`) dan grafik garis komparatif (*Dual X-Axis Line Plot*).

---

## Cara Membaca Modul Ini

Silakan gunakan navigasi di sebelah kiri (atau klik tautan di bawah) untuk mulai membaca analisis:

* Lanjutkan ke **[Business Understanding](business-understanding.md)** untuk mempelajari latar belakang dan tujuan proyek secara mendalam.
* Lanjutkan ke **[Data Understanding](data-understanding.md)** untuk melihat kode Python, pemrosesan data, deteksi pencilan, dan visualisasi tren polutan.

