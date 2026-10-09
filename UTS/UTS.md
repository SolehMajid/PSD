# Ujian Tengah Semester (UTS) - Proyek Sains Data

## Pemetaan & Klasifikasi Tutupan Lahan Se-Jawa Timur Berbasis Citra Sentinel-2A & Machine Learning

Selamat datang di modul dokumentasi **Ujian Tengah Semester (UTS) Mata Kuliah Proyek Sains Data (Semester 5)**. Modul ini menyajikan proyek *End-to-End Data Science & Remote Sensing* untuk melakukan digitasi ulang, pengunduhan citra satelit skala provinsi bebas awan, rekayasa fitur spektral, dan pemodelan klasifikasi tutupan lahan (*Land Use / Land Cover*) di seluruh wilayah **Provinsi Jawa Timur**.

---

### Ringkasan Eksekutif Proyek

| Parameter | Spesifikasi Proyek UTS |
| :--- | :--- |
| **Wilayah Pengamatan** | **Seluruh Provinsi Jawa Timur** (111.19° BT s.d. 114.46° BT, -6.65° LS s.d. -8.60° LS) |
| **Sensor Satelit** | **Sentinel-2A L2A** (Bottom-of-Atmosphere Surface Reflectance) |
| **Penyedia Layanan Cloud** | **Copernicus Data Space Ecosystem (CDSE)** via openEO Python API |
| **Jumlah Kelas Target** | **5 Kelas Tutupan Lahan**: Bangunan, Sawah, Perairan, Hutan Biasa, Hutan Mangrove |
| **Total Sampel Digitasi** | **270 Poligon Sampel** GeoJSON representatif se-Jawa Timur |
| **Band Citra Terpilih** | 6 Band: `B02` (Blue), `B03` (Green), `B04` (Red), `B08` (NIR), `B8A` (Narrow NIR), `B11` (SWIR-1) |
| **Indeks Spektral** | 4 Indeks: **NDVI**, **MNDWI**, **NDBI**, dan **Ratio_B8A_B11** |
| **Resolusi Spasial** | **60 Meter** (Optimasi Cloud: Waktu proses 2–4 menit, *Zero Out-of-Memory*) |
| **Algoritma Machine Learning** | **Random Forest Classifier** (100 Decision Trees) |
| **Performa Akurasi Uji** | **82.35%** pada 68 sampel data uji independen (*Stratified Test Set*) |

---

### Struktur Dokumen & Modul UTS

Modul UTS ini terbagi ke dalam sub-halaman berikut:

1. **[Dokumentasi & Laporan Metodologi (Penjelasan)](Penjelasan.md)**:
   - Pembahasan mendalam siklus hidup data sains (**CRISP-DM**): *Business Understanding*, *Data Understanding*, *Data Preprocessing*, *Modeling*, *Evaluation*, dan *Deployment*.
   - Alasan ilmiah pemilihan 6 band spektral, resolusi spasial 60 meter, dan komposit median Agustus 2024. - Analisis performa model: *Confusion Matrix*, *Classification Report*, dan *Feature Importance*.
   - **Code Walkthrough Rinci**: Penjelasan baris demi baris dari setiap blok kode pada notebook.

2. **[Notebook Pemrosesan & Pemodelan (`ambil_data_jatim_60m.ipynb`)](ambil_data_jatim_60m.ipynb)**:
   - Skrip interaktif pemrosesan data geospasial, batch job openEO cloud, ekstraksi piksel ke CSV, pelatihan Random Forest, serta perenderan peta interaktif Leaflet/Folium.

---

### Visualisasi Utama Hasil Klasifikasi

Proyek ini menghasilkan visualisasi tematik dan interaktif:

- **Peta Land Use / Land Cover (LULC) Penuh Jawa Timur**: Peta tematik standar publikasi ilmiah kartografi dengan skema 5 warna, legenda resmi, dan arah mata angin.
- **Peta Interaktif Sebaran Data Split (Folium)**: Peta interaktif berbasis Leaflet yang memisahkan poligon Data Latih (75%) dan Data Uji (25%) dengan fitur centang layer (*LayerControl*).
- **Peta Interaktif Evaluasi Prediksi (Folium)**: Visualisasi spasial hasil evaluasi model yang membedakan prediksi **BENAR** (border hijau tebal) dan prediksi **SALAH** (border merah tebal putus-putus) langsung di atas citra satelit asli.

---

*Silakan navigasikan ke menu di samping kiri untuk membaca dokumentasi laporan lengkap atau melihat notebook pengolahan citra.*
