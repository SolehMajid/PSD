# Melakukan Cluster Menggunakan K-Means Menggunakan KNIME

Dokumentasi ini menyajikan analisis pengelompokan (*clustering*) data deret waktu (*time series*) 4 polutan udara ($\text{CO}$, $\text{CH}_4$, $\text{NO}_2$, dan $\text{SO}_2$) dari **18 mahasiswa / wilayah pengamatan** menggunakan **KNIME Analytics Platform** dengan algoritma **K-Means**.

Tujuan analisis ini adalah membandingkan dua alur pengolahan:
1. **Pendekatan 1 (Dengan PCA - 18 Dimensi)**: Mereduksi 272 fitur awal menjadi **18 komponen utama** terlebih dahulu sebelum dikelompokkan oleh K-Means.
2. **Pendekatan 2 (Tanpa PCA - 272 Fitur Penuh)**: Memasukkan seluruh **272 fitur numerik TSFEL** secara langsung ke algoritma K-Means tanpa reduksi dimensi.

---

## 1. Karakteristik Data Input

Dataset merupakan gabungan fitur hasil ekstraksi pustaka **TSFEL** dari 18 mahasiswa/wilayah di Jawa Timur dan sekitarnya (Bangkalan, Surabaya, Gresik, Lamongan, Mojokerto, Pamekasan, Sumenep, Blora, hingga Biak Kota).

Setiap data mewakili 1 mahasiswa dengan total **272 fitur numerik**:

$$\text{Total Fitur} = 4 \text{ Polutan} \times 68 \text{ Fitur TSFEL} = 272 \text{ Fitur}$$

Ke-4 polutan yang dianalisis:
- **CO (Karbon Monoksida)**: 68 fitur statistik, temporal, spektral, dan fraktal.
- **CH4 (Metana)**: 68 fitur statistik, temporal, spektral, dan fraktal.
- **NO2 (Nitrogen Dioksida)**: 68 fitur statistik, temporal, spektral, dan fraktal.
- **SO2 (Sulfur Dioksida)**: 68 fitur statistik, temporal, spektral, dan fraktal.

---

## 2. Alur Kerja (Workflow) pada KNIME

Alur pemodelan divisualisasikan pada **KNIME Analytics Platform** seperti gambar berikut:

```{figure} ../assets/images/images_pertemuan-4/knime-pca-18.png
:width: 100%
:align: center

Workflow KNIME: Perbandingan K-Means Clustering Melalui Reduksi Dimensi PCA (18 Dimensi) vs Tanpa PCA (272 Fitur Penuh).
```

### Penjelasan Node Sederhana:
1. **Node `Excel Reader`**: Membaca berkas kompilasi data 18 mahasiswa (kolom metadata nama/wilayah dan 272 fitur polutan).
2. **Jalur Atas (Dengan PCA 18 Dimensi)**:
   - **Node `PCA`**: Mereduksi 272 fitur menjadi 18 dimensi utama (`PCA dimension 0` s.d. `PCA dimension 17`).
   - **Node `k-Means`**: Mengelompokkan data 18 dimensi tersebut ke dalam **2 klaster ($k = 2$)**.
3. **Jalur Bawah (Tanpa PCA)**:
   - **Node `k-Means`**: Mengelompokkan data langsung menggunakan seluruh 272 fitur awal ke dalam **2 klaster ($k = 2$)**.

---

## 3. Hasil Pengelompokan Data (Cluster Assignment)

Setelah kedua jalur K-Means dieksekusi di KNIME, diperoleh penetapan anggota klaster untuk ke-18 mahasiswa:

| No | Nama Mahasiswa | Wilayah Pantau | Klaster (Tanpa PCA) | Klaster (Dengan PCA 18-D) | Kesimpulan |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | Achmad Saiful Fuadi | Labang, Bangkalan | `cluster_1` | `cluster_1` | Sama |
| 2 | Ahmad Ubaidillah Mappattiro | Masalembu | `cluster_1` | `cluster_1` | Sama |
| 3 | Ahmad soleh majid | Socah, Bangkalan | `cluster_1` | `cluster_1` | Sama |
| 4 | Aisya | Biak Kota | `cluster_1` | `cluster_1` | Sama |
| 5 | Alif Baiatur Ridhwan El Habibie | Surabaya, Gubeng | `cluster_1` | `cluster_1` | Sama |
| 6 | **Firman Candra Dwi Nugroho** | **Kraton, Bangkalan** | **`cluster_0`** | **`cluster_0`** | **Terpisah (Outlier)** |
| 7 | Intan Resti Haslindawati | Kadur, Pamekasan | `cluster_1` | `cluster_1` | Sama |
| 8 | Irwan Dwi Mukhlisin | Lamongan kota | `cluster_1` | `cluster_1` | Sama |
| 9 | Mohammad Andri Firmansyah | Trowulan, Mojokerto | `cluster_1` | `cluster_1` | Sama |
| 10 | Mohammad Waqidi | Lenteng | `cluster_1` | `cluster_1` | Sama |
| 11 | Muhammad Ainul Fuady | Gresik, Bungah | `cluster_1` | `cluster_1` | Sama |
| 12 | Muhammad Fathul Iman Wahid | Burneh, Bangkalan | `cluster_1` | `cluster_1` | Sama |
| 13 | Muhammad Ilham | Mendenrejo | `cluster_1` | `cluster_1` | Sama |
| 14 | Muhammad Sirul Amin | Klampis | `cluster_1` | `cluster_1` | Sama |
| 15 | Raihan Aryanova Narendra | Sokobanah | `cluster_1` | `cluster_1` | Sama |
| 16 | Shofiatul Mahmudah | Guluk-Guluk, Sumenep | `cluster_1` | `cluster_1` | Sama |
| 17 | Wildan Haydar Amru | Krian | `cluster_1` | `cluster_1` | Sama |
| 18 | fikri mutawakkil | Pakong, Pamekasan | `cluster_1` | `cluster_1` | Sama |

### Intisari Hasil:
- **`cluster_0`**: Hanya berisi **1 orang (5.56%)**, yaitu **Firman Candra Dwi Nugroho** (Kraton, Bangkalan).
- **`cluster_1`**: Berisi **17 orang lainnya (94.44%)**.
- **Hasil Kedua Metode**: Jalur Tanpa PCA dan Dengan PCA menghasilkan pembagian kelompok yang **100% identik**.

---

## 4. Mengapa Hasil PCA dan Tanpa PCA Bisa Sama Persis?

Secara teori, satu metode bekerja pada 272 fitur dan metode lainnya pada 18 fitur. Mengapa hasilnya bisa sama persis?

Jawabannya adalah **adanya nilai ekstrem (pencilan/outlier) pada data Firman yang belum dinormalisasi**:

1. **Pada Jalur Tanpa PCA (Jarak Euclidean)**:
   - Data Firman memiliki nilai fitur spektral metana ($\text{CH}_4$) yang sangat raksasa (mencapai skala kuadriliun, $10^{15} - 10^{16}$):
     - `CH4 - spectral_decrease`: $-1.02 \times 10^{16}$ (pada mahasiswa lain rata-rata hanya $+1.16 \times 10^{8}$).
     - `CH4 - spectral_kurtosis`: $+7.12 \times 10^{15}$ (pada mahasiswa lain rata-rata hanya $+448.34$).
   - Karena algoritma K-Means menghitung jarak berdasarkan kuadrat selisih angka, angka raksasa ini mendominasi **$>99.99\%$** perhitungan jarak. Akibatnya, jarak Firman ke mahasiswa lainnya menjadi teramat jauh sehingga ia otomatis dipisahkan menjadi kelompok sendiri (`cluster_0`).

2. **Pada Jalur Dengan PCA (18 Dimensi)**:
   - PCA bertugas mencari arah variasi data terbesar. Karena perbedaan fitur metana Firman begitu masif, variasi tersebut langsung diserap hampir seluruhnya oleh dua komponen utama pertama:
     - **`PCA dimension 0`**: Menyerap **$96.12\%$** variasi data.
     - **`PCA dimension 1`**: Menyerap **$3.88\%$** variasi data.
   - Kedua dimensi ini mencakup **$100\%$ total variasi dataset**. Sumbu pemisah raksasa ini tetap ada di ruang PCA, sehingga K-Means pada ruang PCA 18-D menghasilkan pengelompokan yang persis sama.

---

## 5. Nilai Pusat Klaster (Cluster Centroid)

Port keluaran kedua dari node **k-Means** di KNIME menghasilkan nilai rata-rata pusat kelompok (*centroid*):
- **`cluster_0`**: Nilai dari 1 observasi tunggal (Firman).
- **`cluster_1`**: Nilai rata-rata dari 17 mahasiswa lainnya.

### 5.1 Rangkuman Karakteristik Fitur 4 Polutan (Jalur Tanpa PCA)

Tabel berikut menyederhanakan perbandingan nilai pusat klaster untuk parameter-parameter penting pada ke-4 gas polutan:

| Gas Polutan | Parameter Fitur Kunci | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lain) | Makna & Interpretasi Singkat |
| :---: | :--- | :---: | :---: | :--- |
| **CO** | Rata-rata Konsentrasi (`calc_mean`) | $0.0296$ | $34.38$ | Tingkat konsentrasi CO relatif sebanding |
| **CO** | Fluktuasi Harian (`calc_std`) | $0.0037$ | $0.0029$ | Variabilitas perubahan gas konsisten rendah |
| **CO** | Memori Jangka Panjang (`hurst_exp`) | $0.88$ | $0.49$ | Menunjukkan keteraturan memori tren sinyal |
| **CH4** | Rata-rata Konsentrasi (`calc_mean`) | $1892.8$ ppb | $1280.6$ ppb | Rata-rata konsentrasi metana pada batas wajar |
| **CH4** | Penurunan Spektral (`spec_decrease`)| **$-1.02 \times 10^{16}$** | $+1.16 \times 10^{8}$ | **Anomali Ekstrem**: Nilai spektral Firman melompat raksasa |
| **CH4** | Keruncingan Spektra (`spec_kurtosis`)| **$+7.12 \times 10^{15}$** | $+448.34$ | **Anomali Ekstrem**: Distribusi frekuensi metana melonjak |
| **NO2** | Rata-rata Konsentrasi (`calc_mean`) | $5.02 \times 10^{-6}$ | $1.61 \times 10^{9}$ | Rata-rata konsentrasi gas nitrogen dioksida |
| **NO2** | Puncak Daya Spektrum (`max_power`) | $30.65$ | $1.79 \times 10^{15}$ | Puncak kerapatan daya frekuensi $\text{NO}_2$ |
| **SO2** | Rata-rata Konsentrasi (`calc_mean`) | $-1.52 \times 10^{-5}$ | $2.73 \times 10^{10}$ | Rata-rata konsentrasi gas sulfur dioksida |
| **SO2** | Titik Berat Frekuensi (`calc_centroid`) | $211.36$ | $1.29 \times 10^{15}$ | Pusat massa distribusi spektral gas $\text{SO}_2$ |

> **Catatan**: Data mentah lengkap untuk seluruh 272 variabel sentroid tersimpan pada berkas `data/csv/pertemuan-4-csv/Knime cluster/nilai_cluster_nopca.csv`.

---

### 5.2 Rangkuman Komponen Utama PCA (Jalur Dengan PCA 18 Dimensi)

Pada jalur PCA, data dipadatkan menjadi 18 dimensi. Tabel berikut menyajikan ringkasan nilai centroid pada komponen penentu utama:

| Komponen PCA | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lain) | Kontribusi Variansi | Peran dalam Pengelompokan |
| :---: | :---: | :---: | :---: | :--- |
| **`PCA dimension 0`** | **$+3.58 \times 10^{15}$** | **$-2.11 \times 10^{14}$** | **$96.12\%$** | **Pemisah Utama**: Menyerap hampir seluruh variasi jarak antar data |
| **`PCA dimension 1`** | **$-1.17 \times 10^{16}$** | **$+6.90 \times 10^{14}$** | **$3.88\%$** | **Pemisah Kedua**: Menyerap sisa anomali spektral frekuensi |
| **`PCA dimension 2 s.d. 17`** | Rentang $-1021$ s.d. $+20$ | Rentang $-1.3$ s.d. $+60$ | **$< 0.01\%$** | Menangkap detail fluktuasi lokal skala kecil dan residu data |

> **Catatan**: Rincian numerik ke-18 dimensi PCA lengkap tersimpan pada berkas `data/csv/pertemuan-4-csv/Knime cluster/nilai_cluster_pca.csv`.

---

## 6. Perbandingan Ringkas: Dengan PCA vs Tanpa PCA

| Kriteria | Pendekatan Dengan PCA (18 Dimensi) | Pendekatan Tanpa PCA (272 Fitur) | Keuntungan Menggunakan PCA |
| :--- | :---: | :---: | :--- |
| **Jumlah Dimensi Input** | **18 Dimensi** | **272 Dimensi** | Ukuran dimensi berkurang **$93.38\%$**, data jauh lebih ringkas. |
| **Kecepatan Komputasi** | Cepat ($\approx 648$ operasi/iterasi) | Lambat ($\approx 9.792$ operasi/iterasi) | Perhitungan jarak **$15.1\times$ lebih cepat** pada PCA. |
| **Redundansi / Korelasi** | Tereliminasi (semua dimensi ortogonal) | Tinggi (banyak fitur mirip) | Menghilangkan bobot ganda pada fitur yang serupa. |
| **Kemudahan Visualisasi** | Sangat mudah (cukup plot PCA-0 vs PCA-1) | Sangat sulit (sulit membayangkan 272 dimensi) | Mempermudah peneliti melihat sebaran data secara 2D. |
| **Hasil Partisi Klaster** | `cluster_0` (1) vs `cluster_1` (17) | `cluster_0` (1) vs `cluster_1` (17) | Struktur klaster utama **$100\%$ terjaga sempurna**. |

---

## 7. Pelajaran Penting & Kesimpulan

1. **Pentingnya Normalisasi Data Awal**:
   - Jika fitur data belum dinormalisasi (skala nilainya sangat beragam dari $0.0001$ hingga miliaran), fitur bernilai raksasa akan mendominasi penentuan klaster.
   - Disarankan menambahkan node **`Normalizer`** (misal Z-Score atau Min-Max) di KNIME sebelum masuk ke node PCA atau K-Means agar seluruh fitur berkontribusi secara adil.

2. **Efisiensi Reduksi Dimensi PCA**:
   - Penggunaan PCA 18 dimensi terbukti sangat efisien: memangkas dimensi sebesar **$93.38\%$** dan mempercepat kalkulasi hingga **15.1 kali lipat** tanpa merusak hasil pengelompokan.

3. **Hasil Akhir**:
   - K-Means pada kedua metode membagi 18 mahasiswa menjadi dua kelompok yang identik:
     - **Klaster 0**: Firman Candra Dwi Nugroho (Kraton, Bangkalan) yang memiliki karakteristik nilai fitur metana sangat ekstrem.
     - **Klaster 1**: 17 mahasiswa lainnya yang memiliki sebaran data relatif homogen.
