# Aplikasi Model Tutupan Lahan (Streamlit)

Aplikasi web interaktif ini dibangun menggunakan **Streamlit** untuk mendemonstrasikan implementasi model *machine learning* dalam klasifikasi dan pemetaan tutupan lahan (*Land Use / Land Cover*) di seluruh wilayah Provinsi Jawa Timur. 

---

### 🌟 Fitur Utama Dashboard Web GIS:

1. **Dukungan Dua Model Machine Learning (Dual-Model Switcher)**:
   - **Model 1: Centroid (`model_rf.pkl`)**: Dilatih dari 1 titik tengah per poligon (202 train, 68 test centroid, akurasi 82.35%).
   - **Model 2: Full-Pixel (`model_rf_pixel.pkl`)**: Dilatih dari seluruh 52.327 piksel poligon (33.051 train, 19.276 test, akurasi piksel 97.47%, akurasi poligon 81.82%).
   - Pengguna dapat beralih model kapan saja melalui tombol radio di sidebar kiri.

2. **Peta Interaktif Raster LULC (Overlay Google Hybrid)**:
   - Menampilkan tutupan lahan langsung di atas basemap satelit *Google Hybrid (Label)* dan *Google Satellite*.
   - **Kontrol Layer per Kelas**: Centang/hilangkan kelas tutupan lahan (Air, Mangrove, Hutan Non-Mangrove, Pemukiman, Sawah).
   - **Slider Transparansi Dinamis**: Atur tingkat opasitas lapisan raster secara *real-time* (0% s/d 100%).
   - **Tabel Rekapitulasi Luas Area**: Menghitung otomatis luas lahan dalam satuan Hektar (Ha), km², dan persentase luas wilayah.

3. **Komparasi Head-to-Head Kedua Model**:
   - Membandingkan metrik akurasi piksel vs akurasi poligon secara adil.
   - Grafik kontribusi *Feature Importance* 6 band spektral dan 4 indeks (MNDWI, NDVI, NDBI, Ratio B8A/B11).

4. **Simulator Prediksi Spektral Real-Time**:
   - Uji coba interaktif dengan menggeser nilai band Blue, Green, Red, NIR, SWIR untuk melihat prediksi kelas tutupan lahan dan bar chart probabilitasnya.

5. **Eksplorasi Data Sampel Ground Truth**:
   - Menjelajahi dataset 270 sampel centroid vs dataset 52.327 piksel poligon.

---

### 🔗 Akses Aplikasi Web

Aplikasi web dapat diakses secara langsung melalui tautan berikut:

👉 **[Buka Aplikasi Streamlit Tutupan Lahan Jawa Timur](https://psd-tutupan-lahan-jatim.streamlit.app/)**  
URL: `https://psd-tutupan-lahan-jatim.streamlit.app/`
