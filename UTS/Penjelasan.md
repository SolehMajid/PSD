# Laporan & Analisis Klasifikasi Tutupan Lahan Provinsi Jawa Timur

> **Mata Kuliah:** Proyek Sains Data (Semester 5)  
> **Topik Proyek:** Klasifikasi Tutupan Lahan (*Land Use / Land Cover*) 5 Kelas Se-Jawa Timur  
> **Citra Satelit:** Sentinel-2A Multispektral L2A (Copernicus CDSE)  
> **Model Klasifikasi:** Random Forest Classifier  

---

## 1. Business Understanding (Latar Belakang & Tujuan Masalah)

### Kenapa Proyek Ini Sangat Penting?
Provinsi Jawa Timur merupakan salah satu wilayah paling strategis di Indonesia: sebagai lumbung pangan padi nasional, pusat manufaktur dan industri terbesar kedua, serta memiliki ekosistem alam yang sangat bervariasi (mulai dari hutan mangrove pesisir Selat Madura hingga gugusan hutan pegunungan Bromo-Semeru-Ijen).

Alih fungsi lahan yang sangat cepat menimbulkan tantangan besar:
1. **Penyusutan Lahan Sawah**: Pembangunan kawasan industri dan perumahan mengancam ketahanan pangan nasional.
2. **Degradasi Hutan Mangrove**: Pengalihan hutan bakau pesisir menjadi permukiman atau tambak tanpa kontrol meningkatkan risiko abrasi dan banjir rob di pesisir utara dan timur Jawa Timur.
3. **Keterbatasan Survei Konvensional**: Mengirim tim terestrial untuk mengecek tutupan lahan di 38 kabupaten/kota se-Jawa Timur membutuhkan biaya miliaran rupiah dan waktu berbulan-bulan.

**Solusi Sains Data & Penginderaan Jauh:**  
Membangun sistem klasifikasi otomatis tutupan lahan (*Land Use / Land Cover* - LULC) skala regional berbasis citra satelit **Sentinel-2A** dan algoritma **Machine Learning**. Dengan pendekatan ini, seluruh daratan Jawa Timur (~47.800 km²) dapat dipantau secara objektif, berkala, cepat, dan presisi.

### 5 Kelas Tutupan Lahan yang Diklasifikasikan:
1. **Bangunan (*Built-up*)**: Area perkotaan padat, perumahan, kawasan industri, semen, aspal, dan genteng.
2. **Lahan Pertanian (*Sawah / Farmland*)**: Persawahan irigasi, tanaman padi musiman, dan lahan pertanian aluvial.
3. **Perairan (*Water Body*)**: Laut Jawa, Selat Madura, waduk (Karangkates, Selorejo), danau, dan sungai besar.
4. **Hutan Biasa (*Forest*)**: Vegetasi pohon kanopi rapat di dataran tinggi pegunungan (Arjuno, Semeru, Raung).
5. **Hutan Mangrove**: Komunitas pohon bakau di zona pasang-surut muara dan pesisir pantai.

---

## 2. Data Understanding & Rekayasa Fitur Spektral

### 2.1 Sebaran 270 Poligon Sampel Digitasi Se-Jawa Timur
Untuk melatih model secara akurat, dikumpulkan **270 poligon sampel representatif** yang tersebar merata dari ujung barat (Ngawi/Pacitan) sampai ujung timur (Banyuwangi/Madura):
- **Bangunan**: 60 poligon
- **Sawah**: 60 poligon
- **Perairan**: 50 poligon
- **Hutan Biasa**: 50 poligon
- **Hutan Mangrove**: 50 poligon

```{figure} ../assets/images/images_uts/1.peta_sebaran_sampel_270_jatim.png
:width: 95%
:align: center

Sebaran Spasial 270 Poligon Sampel Digitasi 5 Kelas Tutupan Lahan Se-Jawa Timur beserta Diagram Distribusi Jumlah Sampel.
```

#### Peta Interaktif Sebaran Sampel (Folium Leaflet):
Anda dapat menggeser peta, memperbesar tampilan, dan mengaktifkan/menonaktifkan (*filter checkbox*) layer per kelas di bawah ini:

<iframe src="peta_sampel_jatim.html" width="100%" height="520px" frameborder="0" style="border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;"></iframe>

---

### 2.2 Kenapa Memilih 6 Band Spektral Ini?
Citra satelit Sentinel-2A memiliki belasan band. Pada proyek ini dipilih **6 Band Kunci**:
`B02 (Blue)`, `B03 (Green)`, `B04 (Red)`, `B08 (NIR)`, `B8A (Narrow NIR)`, dan `B11 (SWIR-1)`.

#### Alasan Ilmiah Pemilihan Masing-Masing Band:
1. **`B02 (Blue, 490 nm)`, `B03 (Green, 560 nm)`, `B04 (Red, 665 nm)` (Spektrum Tampak - True Color)**:
   - Menghasilkan kenampakan warna alami permukaan bumi yang sesuai dengan penglihatan mata manusia.
   - Daun berfotosintesis menyerap kuat sinar merah (`B04`) dan biru (`B02`), lalu memantulkan warna hijau (`B03`). Sebaliknya, tanah kering dan bangunan memantulkan spektrum merah cukup tinggi.
2. **`B08 (Broad NIR, 842 nm)` (Inframerah Dekat)**:
   - Sangat sensitif terhadap struktur sel mesofil daun tumbuhan hijau yang sehat.
   - Gelombang ini dipantulkan sangat kuat oleh vegetasi lebat, tetapi **diserap hampir 100% oleh air murni**. Ini adalah pembeda nomor satu antara daratan hijau dan air.
3. **`B8A (Narrow NIR, 865 nm)` (Pita Sempit Inframerah Dekat)**:
   - Dirancang khusus menghindari gangguan serapan uap air atmosfer.
   - **Kunci pembeda Hutan Biasa vs Mangrove**: Struktur kanopi pohon bakau pesisir memiliki biomassa dan indeks luas daun yang berbeda dari pohon pegunungan; band B8A mampu membaca kerapatan tajuk ini tanpa mengalami kejenuhan (*saturation*).
4. **`B11 (SWIR-1, 1610 nm)` (Inframerah Gelombang Pendek)**:
   - Sangat peka terhadap **kadar kelembaban air pada tanah dan daun**.
   - Hutan Mangrove berada di substrat lumpur basah berair laut, sehingga nilai pantulan SWIR-nya jauh lebih rendah daripada Hutan Biasa di daratan tinggi kering.
   - Material atap perumahan, semen, dan aspal memantulkan gelombang SWIR dengan sangat kuat (nilai B11 sangat tinggi).

---

### 2.3 Kenapa Menggunakan Resolusi Spasial 60 Meter? (Anti-OOM)
Banyak pemula tergoda langsung menggunakan resolusi asli 10 meter untuk seluruh Jawa Timur. Namun, secara rekayasa komputasi, langkah tersebut menyebabkan kegagalan:

| Aspek Komputasi | Resolusi 10 Meter (Gagal) | Resolusi 60 Meter (Berhasil & Stabil) |
| :--- | :--- | :--- |
| **Dimensi Piksel per Band** | ~37.260 x 22.780 piksel | **6.210 x 3.797 piksel** |
| **Beban Piksel Total (6 Band)** | **> 5,08 Miliar piksel** | **~141,4 Juta piksel** (Turun 36x lipat) |
| **Konsumsi Memori RAM** | > 20 GB (Server Crash) | **~560 MB** (Sangat ringan di memori laptop) |
| **Status Cloud CDSE openEO** | **Pasti Gagal (Error 500 / Out-of-Memory / Timeout > 30 menit)** | **100% Sukses (Waktu komputasi 2–4 menit)** |
| **Ukuran Berkas GeoTIFF** | > 2,5 Gigabyte | **~257 Megabyte** |

> **Kesimpulan:** Resampling ke 60 meter memangkas beban kalkulasi hingga **36 kali lipat**, menjamin proses crawling cloud di Copernicus Data Space Ecosystem (CDSE) berhasil tanpa *Out-of-Memory*, namun tetap mempertahankan akurasi spektral yang presisi untuk membedakan 5 kelas tutupan lahan regional.

---

### 2.4 Kenapa Menggunakan Komposit Median Agustus 2024?
- **Puncak Musim Kemarau**: Bulan Agustus adalah periode dengan tutupan awan (*cloud cover*) paling sedikit di Jawa Timur.
- **Reduksi Median Temporal**: Dengan mengumpulkan seluruh tangkapan satelit selama 1 bulan dan mengambil nilai **median** di setiap titik koordinat piksel, bayangan awan (nilai ekstrem rendah) dan awan putih tebal (nilai ekstrem tinggi) otomatis terbuang secara statistik. Hasilnya adalah citra komposit sintetis yang bersih 100% dari tutupan awan (*cloud-free composite*).

---

### 2.5 Kenapa Menghitung 4 Indeks Spektral Khusus?
Untuk mempertajam pemisahan kelas, dihitung 4 indeks matematika:
1. **NDVI (*Normalized Difference Vegetation Index*)**:
   $$\text{NDVI} = \frac{\text{B08} - \text{B04}}{\text{B08} + \text{B04}}$$
   Mengukur kepadatan klorofil hijau. Bernilai tinggi (>0.5) pada hutan dan sawah subur, serta mendekati 0 atau negatif pada air dan bangunan.
2. **MNDWI (*Modified Normalized Difference Water Index*)**:
   $$\text{MNDWI} = \frac{\text{B03} - \text{B11}}{\text{B03} + \text{B11}}$$
   Mengukur keberadaan badan air terbuka. Hanya air yang bernilai positif (>0), daratan bernilai negatif.
3. **NDBI (*Normalized Difference Built-up Index*)**:
   $$\text{NDBI} = \frac{\text{B11} - \text{B08}}{\text{B11} + \text{B08}}$$
   Mengukur kekedapan area terbangun. Bangunan bernilai positif karena material beton/genteng memantulkan SWIR lebih kuat daripada NIR.
4. **Ratio_B8A_B11**:
   $$\text{Ratio\_B8A\_B11} = \frac{\text{B8A}}{\text{B11}}$$
   Rasio pembeda unik antara tajuk Mangrove pesisir (nilai rasio tinggi ~2.65 karena B11 ditekan oleh lumpur basah) vs Hutan pegunungan (rasio ~1.39).

#### Tabel Profil Spektral Rata-Rata 5 Kelas Tutupan Lahan:
| Kelas Lahan | B02 (Blue) | B04 (Red) | B08 (NIR) | B11 (SWIR) | NDVI | MNDWI | NDBI | Ratio B8A/B11 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bangunan (Built-up)** | 1269.3 | 1683.6 | 2078.1 | 2593.2 | 0.119 | -0.307 | **+0.117** | 0.830 |
| **Hutan Biasa** | 568.3 | 707.2 | 2535.2 | 2183.8 | **0.583** | -0.505 | -0.083 | 1.392 |
| **Hutan Mangrove** | 511.5 | 579.1 | 2467.9 | 1159.3 | **0.631** | -0.212 | -0.385 | **2.658** |
| **Lahan Pertanian (Sawah)** | 706.5 | 1020.5 | 1721.7 | 1684.9 | 0.184 | -0.024 | -0.148 | 1.562 |
| **Perairan (Water Body)** | 663.1 | 625.2 | 813.6 | 604.0 | -0.062 | **+0.333** | -0.207 | 1.681 |

---

## 3. Visualisasi Citra Satelit: True Color vs False Color Spektral

Berikut adalah komparasi visual citra Sentinel-2A full Jawa Timur sebelum dilakukan pemodelan machine learning:

```{figure} ../assets/images/images_uts/2.visualisasi_citra_true_false_color.png
:width: 95%
:align: center

Komparasi Citra Sentinel-2A True Color RGB (Atas) dan False Color Spektral B8A-B11-B04 (Bawah) dengan Hamparan 270 Poligon Sampel Se-Jawa Timur.
```

### Kenapa Menghasilkan Gambar Ini & Maksud Visualnya:
1. **Gambar Panel Atas: True Color RGB (`B04, B03, B02`)**:
   - Menampilkan warna alami: Laut berwarna biru gelap, sawah berwarna hijau muda/kekuningan, hutan berwarna hijau pekat, dan kota Surabaya/Malang tampak abu-abu keputihan.
   - **Kelemahan True Color**: Sangat sulit membedakan Hutan Biasa vs Hutan Mangrove karena keduanya sama-sama tampak hijau tua di mata manusia.
2. **Gambar Panel Bawah: False Color Spektral (`B8A, B11, B04`)**:
   - Memanfaatkan kombinasi gelombang tak tampak:
     - **Hutan Biasa**: Menyala **Merah Terang** karena kanopi pohon daratan tinggi memantulkan Narrow NIR (`B8A`) secara maksimal.
     - **Hutan Mangrove**: Tampak **Merah Marun Gelap** di muara pantai karena substrat air laut menyerap sebagian gelombang inframerah.
     - **Perairan / Laut**: Berwarna **Hitam Pekat** karena molekul air menyerap gelombang inframerah secara total.
     - **Lahan Sawah**: Berwarna **Kuning Keemasan / Oranye**, membedakannya secara tegas dari hutan pegunungan.
     - **Bangunan**: Berwarna **Cyan / Abu-abu Terang**, memperlihatkan batas perkotaan padat penduduk.

#### Potongan Kode Ringkas Normalisasi Kontras Citra:
```python
# Normalisasi kontras persentil 2% - 98% untuk visualisasi optimal
def stretch(band):
    p2, p98 = np.percentile(band[band > 0], (2, 98))
    return np.clip((band - p2) / (p98 - p2 + 1e-6), 0, 1)

rgb_jatim = np.dstack([stretch(b4), stretch(b3), stretch(b2)])
false_jatim = np.dstack([stretch(b8a), stretch(b11), stretch(b4)])
```

---

## 4. Pembagian Dataset (Data Splitting: Train 75% vs Test 25%)

### Kenapa Menggunakan Rasio 75% : 25%?
1. **Keseimbangan Pembelajaran & Validasi**: Dari total 270 sampel, rasio 75% menyediakan **202 sampel latih** yang cukup kaya untuk mengenali variabilitas spektral lahan se-Jawa Timur, sementara 25% menyisihkan **68 sampel uji** yang cukup besar untuk menghasilkan evaluasi statistik yang valid dan tidak bias.
2. **Stratified Sampling (`stratify=y`)**: Memastikan persentase kelima kelas terbagi secara seimbang dan proporsional di data train maupun data test, sehingga model tidak bias terhadap kelas tertentu.
3. **Isolasi Penuh (*Zero Data Leakage*)**: Data uji (68 sampel) disimpan terpisah dan **belum pernah dilihat sama sekali** oleh model selama fase pelatihan.

```{figure} ../assets/images/images_uts/3.peta_split_train_test_jatim.png
:width: 95%
:align: center

Peta Sebaran Spasial Pembagian Data Latih 75% (Biru) vs Data Uji 25% (Oranye) Beserta Grafik Keseimbangan Proporsi Sampel per Kelas.
```

#### Tabel Rekapitulasi Pembagian Sampel:
| Kelas Tutupan Lahan | Data Latih (Train 75%) | Data Uji (Test 25%) | Total Sampel | Proporsi Train (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Bangunan (Built-up)** | 45 | 15 | 60 | 75.0% |
| **Lahan Pertanian (Sawah)** | 45 | 15 | 60 | 75.0% |
| **Perairan (Water Body)** | 37 | 13 | 50 | 74.0% |
| **Hutan Biasa** | 37 | 13 | 50 | 74.0% |
| **Hutan Mangrove** | 38 | 12 | 50 | 76.0% |
| **TOTAL KESELURUHAN** | **202 Sampel** | **68 Sampel** | **270 Sampel** | **74.8%** |

#### Peta Interaktif Sebaran Data Split (Folium Leaflet):
Pada peta di bawah ini, Data Latih digambarkan dengan garis solid, sedangkan Data Uji ditandai dengan **garis tepi oranye putus-putus tebal**:

<iframe src="peta_split_data_jatim.html" width="100%" height="520px" frameborder="0" style="border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;"></iframe>

---

## 5. Pemodelan: Kenapa Menggunakan Random Forest?

Model yang dilatih pada proyek ini adalah **Random Forest Classifier** dengan 100 pohon keputusan (*n_estimators=100*).

### Alasan Ilmiah Pemilihan Random Forest:
1. **Resistensi terhadap Overfitting**: Melalui metode *ensemble bagging* (menggabungkan prediksi 100 pohon keputusan acak), variansi model ditekan sehingga kemampuan generalisasi pada area Jawa Timur yang belum disampel tetap tinggi.
2. **Kemampuan Menangani Non-Linearitas Spektral**: Hubungan pantulan cahaya antar vegetasi, air, dan bangunan tidak bersifat garis lurus linier. Pohon keputusan sangat handal dalam membagi ruang fitur spektral secara non-parametrik.
3. **Kekebalan terhadap Multikolinieritas**: Band citra satelit seperti B08 dan B8A memiliki korelasi tinggi. Algoritma Random Forest memilih subset fitur acak pada setiap percabangan sehingga korelasi antar-band tidak merusak performa model.
4. **Memberikan Feature Importance yang Transparan**: Model secara otomatis menghitung kontribusi matematis dari masing-masing band dan indeks spektral.

#### Potongan Kode Ringkas Pelatihan Model:
```python
from sklearn.ensemble import RandomForestClassifier

# Pelatihan model murni pada 202 data latih
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Pengujian murni pada 68 data uji yang diisolasi
y_pred = rf_model.predict(X_test)
```

---

## 6. Evaluasi & Hasil Klasifikasi Model

Pengujian model pada **68 sampel data uji independen** menghasilkan performa yang solid:

$$\text{Akurasi Total Model} = \frac{\text{56 Sampel Tepat}}{\text{68 Sampel Uji}} = \mathbf{82.35\%}$$

```{figure} ../assets/images/images_uts/5.evaluasi_model_confusion_matrix_importance.png
:width: 95%
:align: center

Evaluasi Lengkap Model: (Kiri) Peta Sebaran Prediksi Benar Hijau vs Salah Merah; (Kanan Atas) Matriks Kesalahan Klasifikasi (Confusion Matrix); (Kanan Bawah) Tingkat Kepentingan Fitur Spektral.
```

### 6.1 Laporan Klasifikasi per Kelas (Classification Report)
| Kelas Tutupan Lahan | Precision | Recall | F1-Score | Support (Jumlah Data Uji) |
| :--- | :---: | :---: | :---: | :---: |
| **Bangunan (Built-up)** | 0.81 | 0.87 | 0.84 | 15 |
| **Hutan Biasa** | 0.87 | **1.00** | **0.93** | 13 |
| **Hutan Mangrove** | **0.91** | 0.83 | 0.87 | 12 |
| **Lahan Pertanian (Sawah)** | 0.75 | 0.80 | 0.77 | 15 |
| **Perairan (Water Body)** | 0.80 | 0.62 | 0.70 | 13 |
| **Rata-Rata (Weighted Avg)** | **0.82** | **0.82** | **0.82** | **68** |

### 6.2 Kenapa Terjadi Kesalahan Prediksi? (Analisis Confusion Matrix)
Dari 68 sampel data uji, model memprediksi **56 sampel dengan tepat (82.35%)** dan terdapat **12 sampel yang meleset (17.65%)**. Mengapa hal ini terjadi?
1. **Perairan Tertukar Menjadi Sawah (4 Sampel)**:
   - Terjadi pada sawah beririgasi basah penuh atau tambak air dangkal. Pada awal musim tanam padi di Jawa Timur, sawah dibanjiri air lumpur, sehingga pantulan spektralnya sangat menyerupai badan air terbuka.
2. **Sawah Tertukar Menjadi Bangunan (2 Sampel)**:
   - Terjadi pada sawah yang sedang mengalami masa bera (*bare soil*) atau pasca-panen di bulan Agustus. Tanah kering tanpa tanaman memantulkan spektrum merah dan SWIR yang mirip dengan atap perumahan dan material tanah perkotaan.
3. **Bangunan Tertukar Menjadi Hutan/Air (2 Sampel)**:
   - Pada resolusi 60 meter, satu piksel permukiman di pedesaan sering kali merupakan **piksel campuran (*mixed pixel*)**, di mana atap rumah bercampur dengan pohon pekarangan lebat atau kolam air warga.

### 6.3 Kenapa MNDWI dan NDVI Menjadi Fitur Paling Penting?
Berdasarkan analisis *Feature Importance*:
- **MNDWI menyumbang kontribusi terbesar (16.12%)**: Sangat efektif dalam memisahkan batas air vs daratan kering.
- **NDVI menyumbang kontribusi kedua (14.24%)**: Memisahkan vegetasi berklorofil dari area non-vegetasi.
- **B08, B8A, dan Ratio_B8A_B11 menyumbang total >32%**: Membuktikan bahwa spektrum inframerah adalah kunci utama dalam memisahkan struktur kanopi Hutan Biasa vs Hutan Mangrove.

#### Peta Interaktif Evaluasi Prediksi (Folium Leaflet):
Pada peta di bawah ini, data uji yang diprediksi **BENAR** diberi garis tepi **hijau tebal solid**, sedangkan data uji yang **SALAH / MELESET** diberi tanda **merah menyala putus-putus**:

<iframe src="peta_evaluasi_klasifikasi_jatim.html" width="100%" height="520px" frameborder="0" style="border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;"></iframe>

---

## 7. Peta Tematik Penuh Land Use / Land Cover (LULC) Jawa Timur

Setelah model Random Forest terbukti memiliki akurasi 82.35%, model diterapkan untuk memprediksi **seluruh piksel raster daratan Provinsi Jawa Timur** (~5,8 juta piksel):

```{figure} ../assets/images/images_uts/4.peta_landuse_landcover_jatim.png
:width: 95%
:align: center

Peta Tematik Klasifikasi Penuh Tutupan Lahan (Land Use / Land Cover Map) Provinsi Jawa Timur Menggunakan Model Random Forest Sentinel-2A.
```

### Maksud & Karakteristik Gambar Hasil Klasifikasi:
1. **Perairan (Water Body)**: Mengidentifikasi secara sempurna perairan Selat Madura, pesisir Laut Jawa, Samudra Hindia, serta danau dan waduk besar di Jawa Timur.
2. **Hutan Biasa (Forest)**: Terkonsentrasi kuat pada jalur pegunungan vulkanik tinggi di bagian selatan dan tengah Jawa Timur (Gunung Lawu, Wilis, Kelud, Arjuno-Welirang, Bromo, Semeru, hingga pegunungan Ijen-Raung).
3. **Hutan Mangrove**: Terpetakan secara presisi di sepanjang garis pesisir estuari pantai utara (Wonorejo Surabaya Timur, Ujung Pangkah Gresik, Pasuruan, dan Teluk Grajagan Banyuwangi).
4. **Lahan Pertanian (Sawah / Agriculture)**: Mendominasi lembah subur aluvial sepanjang aliran Sungai Brantas dan Bengawan Solo (Bojonegoro, Lamongan, Nganjuk, Madiun, Jombang, Kediri).
5. **Bangunan / Area Terbangun (Built-up)**: Menggambarkan pola aglomerasi perkotaan metropolitan Surabaya Raya (Surabaya, Sidoarjo, Gresik), Malang Raya, serta pusat-pusat kota kabupaten.

---

## 8. Penerapan Prediksi Spasial Poligon GeoJSON (Digitasi Baru Pengguna)

Salah satu keunggulan utama dari model yang telah dilatih adalah kemampuannya untuk mengklasifikasikan **poligon digitasi baru** yang dibuat oleh pengguna (misalnya melalui format standar spasial GeoJSON / QGIS / ArcGIS).

### Alur Kerja (Pipeline) Pemrosesan Poligon GeoJSON:
1. **Penerimaan Poligon Spasial**: Pengguna memasukkan struktur `FeatureCollection` atau `Polygon` GeoJSON yang memuat daftar koordinat (bujur, lintang).
2. **Kalkulasi Titik Berat (Centroid) & Zonal Sampling**: Sistem menghitung koordinat titik tengah poligon secara geometris menggunakan pustaka `shapely`.
3. **Ekstraksi Spektral Otomatis dari GeoTIFF Sentinel-2A**: Titik koordinat ditransformasikan ke sistem referensi koordinat raster (*Coordinate Reference System - CRS*), kemudian nilai reflektansi 6 band (`B02`, `B03`, `B04`, `B08`, `B8A`, `B11`) diekstrak secara otomatis menggunakan `rasterio`.
4. **Perhitungan Indeks Spektral Seketika**: Sistem menghitung 4 indeks matematika (`NDVI`, `MNDWI`, `NDBI`, `Ratio_B8A_B11`).
5. **Inferensi Model Machine Learning**: Fitur dikirim ke model Random Forest (`rf_model.predict()` dan `rf_model.predict_proba()`).
6. **Penyajian Hasil Spasial**:
   - **Label Kelas Tutupan Lahan** (contoh: *Sawah*, *Hutan Biasa*, *Bangunan*, dll.).
   - **Tingkat Keyakinan Model** (*confidence percentage*, misal: 92.4%).
   - **Visualisasi Poligon di Peta Satelit Interaktif**: Poligon digambar langsung di atas citra satelit Esri World Imagery dengan warna batas dan isi tematik sesuai kelas hasil prediksi.

---

## 9. Kesimpulan & Rekomendasi Pengembangan Web GIS

### Kesimpulan Utama:
1. **Efisiensi Komputasi Berhasil 100%**: Resampling 60m berhasil mereduksi ukuran piksel 36x lipat sehingga pemrosesan citra satelit 6 band se-Jawa Timur dapat berjalan cepat (2–4 menit) pada klaster gratis cloud Copernicus CDSE tanpa kendala memori (*Zero Out-of-Memory*).
2. **Keunggulan Kombinasi Spektral**: Pemilihan band `B8A` (Narrow NIR) dan `B11` (SWIR-1) serta rasio `Ratio_B8A_B11` terbukti menjadi faktor kunci yang berhasil memisahkan kelas yang secara visual mirip, yaitu Hutan Biasa pegunungan dan Hutan Mangrove pesisir.
3. **Akurasi Model Tinggi**: Random Forest Classifier mencapai akurasi **82.35%** pada data uji yang diisolasi, dengan F1-Score kelas Hutan Biasa mencapai 0.93 dan Mangrove mencapai 0.87.
4. **Penyajian Lengkap Sesuai Target Tugas**: Menghasilkan peta citra satelit asli, peta pembagian data split, peta evaluasi benar vs salah berbasis Folium Leaflet, serta peta tematik Land Use / Land Cover se-Jawa Timur berstandar kartografi ilmiah.

### Rekomendasi Pengembangan Aplikasi Web GIS:
Seluruh luaran yang dihasilkan (berkas GeoTIFF, peta interaktif HTML `peta_sampel_jatim.html`, `peta_split_data_jatim.html`, `peta_evaluasi_klasifikasi_jatim.html`, dataset CSV, serta model pickle `model_rf.pkl`) telah diintegrasikan secara menyeluruh ke dalam dashboard **Streamlit** (termasuk fitur interaktif digitasi GeoJSON) untuk kebutuhan pemantauan tata ruang berkelanjutan Provinsi Jawa Timur.

