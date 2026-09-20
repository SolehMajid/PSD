# Melakukan Cluster Menggunakan K-Means Menggunakan KNIME

Dokumentasi ini menyajikan analisis pengelompokan (*clustering*) data deret waktu (*time series*) 4 polutan udara ($\text{CO}$, $\text{CH}_4$, $\text{NO}_2$, dan $\text{SO}_2$) dari **19 mahasiswa / wilayah pengamatan** menggunakan **KNIME Analytics Platform** dengan algoritma **K-Means**.

Tujuan analisis ini adalah membandingkan dua alur pengolahan:
1. **Pendekatan 1 (Dengan PCA - 19 Dimensi)**: Mereduksi 272 fitur awal menjadi **19 komponen utama** terlebih dahulu sebelum dikelompokkan oleh K-Means.
2. **Pendekatan 2 (Tanpa PCA - 272 Fitur Penuh)**: Memasukkan seluruh **272 fitur numerik TSFEL** secara langsung ke algoritma K-Means tanpa reduksi dimensi.

---

## 1. Karakteristik Data Input

Dataset merupakan gabungan fitur hasil ekstraksi pustaka **TSFEL** dari 19 mahasiswa/wilayah observasi (Bangkalan, Surabaya, Gresik, Lamongan, Mojokerto, Pamekasan, Sumenep, Blora, Biak Kota, hingga Nias).

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

```{figure} ../assets/images/images_pertemuan-4/knime-pca-19.png
:width: 100%
:align: center

Workflow KNIME: Perbandingan K-Means Clustering Melalui Reduksi Dimensi PCA (19 Dimensi) vs Tanpa PCA (272 Fitur Penuh).
```

### Penjelasan Node Sederhana:
1. **Node `Excel Reader`**: Membaca berkas kompilasi data 19 mahasiswa (kolom metadata nama/wilayah dan 272 fitur polutan).
2. **Jalur Atas (Dengan PCA 19 Dimensi)**:
   - **Node `PCA`**: Mereduksi 272 fitur menjadi 19 dimensi utama (`PCA dimension 0` s.d. `PCA dimension 18`).
   - **Node `k-Means`**: Mengelompokkan data 19 dimensi tersebut ke dalam **2 klaster ($k = 2$)**.
3. **Jalur Bawah (Tanpa PCA)**:
   - **Node `k-Means`**: Mengelompokkan data langsung menggunakan seluruh 272 fitur awal ke dalam **2 klaster ($k = 2$)**.

---

## 3. Hasil Pengelompokan Data (Cluster Assignment)

Setelah kedua jalur K-Means dieksekusi di KNIME, diperoleh penetapan anggota klaster untuk ke-19 mahasiswa:

| No | Nama Mahasiswa | Wilayah Pantau | Klaster (Tanpa PCA) | Klaster (Dengan PCA 19-D) | Kesimpulan |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | Achmad Saiful Fuadi | Labang, Bangkalan | `cluster_0` | `cluster_0` | Sama |
| 2 | Ahmad Ubaidillah Mappattiro | Masalembu | `cluster_0` | `cluster_0` | Sama |
| 3 | Ahmad soleh majid | Socah, Bangkalan | `cluster_0` | `cluster_0` | Sama |
| 4 | Aisya | Biak Kota | `cluster_0` | `cluster_0` | Sama |
| 5 | Alif Baiatur Ridhwan El Habibie | Surabaya, Gubeng | `cluster_0` | `cluster_0` | Sama |
| 6 | Firman Candra Dwi Nugroho | Kraton, Bangkalan | `cluster_0` | `cluster_0` | Sama |
| 7 | Intan Resti Haslindawati | Kadur, Pamekasan | `cluster_0` | `cluster_0` | Sama |
| 8 | Irwan Dwi Mukhlisin | Lamongan kota | `cluster_0` | `cluster_0` | Sama |
| 9 | Kevin Koligombowo Mangaraja | Telukdalam, Nias | `cluster_0` | `cluster_0` | Sama |
| 10 | Mohammad Andri Firmansyah | Trowulan, Mojokerto | `cluster_0` | `cluster_0` | Sama |
| 11 | Mohammad Waqidi | Lenteng | `cluster_0` | `cluster_0` | Sama |
| 12 | Muhammad Ainul Fuady | Gresik, Bungah | `cluster_0` | `cluster_0` | Sama |
| 13 | **Muhammad Fathul Iman Wahid** | **Burneh, Bangkalan** | **`cluster_1`** | **`cluster_1`** | **Terpisah (Outlier)** |
| 14 | Muhammad Ilham | Mendenrejo | `cluster_0` | `cluster_0` | Sama |
| 15 | Muhammad Sirul Amin | Klampis | `cluster_0` | `cluster_0` | Sama |
| 16 | Raihan Aryanova Narendra | Sokobanah | `cluster_0` | `cluster_0` | Sama |
| 17 | Shofiatul Mahmudah | Guluk-Guluk, Sumenep | `cluster_0` | `cluster_0` | Sama |
| 18 | Wildan Haydar Amru | Krian | `cluster_0` | `cluster_0` | Sama |
| 19 | fikri mutawakkil | Pakong, Pamekasan | `cluster_0` | `cluster_0` | Sama |

### Intisari Hasil:
- **`cluster_0`**: Berisi **18 orang (94.74%)**, yang mencakup kelompok mayoritas mahasiswa dengan data yang homogen.
- **`cluster_1`**: Hanya berisi **1 orang (5.26%)**, yaitu **Muhammad Fathul Iman Wahid** (Burneh, Bangkalan).
- **Hasil Kedua Metode**: Jalur Tanpa PCA dan Dengan PCA menghasilkan pembagian kelompok yang **100% identik**.

---

## 4. Mengapa Hasil PCA dan Tanpa PCA Bisa Sama Persis?

Secara teori, satu metode bekerja pada 272 fitur dan metode lainnya pada 19 fitur. Mengapa hasilnya bisa sama persis?

Jawabannya adalah **adanya nilai ekstrem (pencilan/outlier) pada data Fathul yang belum dinormalisasi**:

1. **Pada Jalur Tanpa PCA (Jarak Euclidean)**:
   - Data Fathul memiliki nilai fitur spektral dan fraktal gas $\text{NO}_2$ dan $\text{SO}_2$ yang sangat raksasa (mencapai skala kuadriliun, $10^{15} - 10^{16}$):
     - `NO2 - max_power_spectrum`: $+3.04 \times 10^{16}$ (pada 18 mahasiswa lain rata-rata hanya $+34.95$).
     - `NO2 - spectral_decrease`: $-2.35 \times 10^{16}$ (pada 18 mahasiswa lain rata-rata $+4.94 \times 10^{8}$).
     - `SO2 - calc_centroid`: $+2.20 \times 10^{16}$ (pada 18 mahasiswa lain rata-rata hanya $+112.63$).
     - `SO2 - higuchi_fractal_dimension`: $+2.02 \times 10^{16}$ (pada 18 mahasiswa lain rata-rata hanya $+1.22$).
   - Karena algoritma K-Means menghitung jarak berdasarkan kuadrat selisih angka, angka raksasa ini mendominasi **$>99.99\%$** perhitungan jarak. Akibatnya, jarak Fathul ke mahasiswa lainnya menjadi teramat jauh sehingga ia otomatis dipisahkan menjadi kelompok tersendiri (`cluster_1`).

2. **Pada Jalur Dengan PCA (19 Dimensi)**:
   - PCA bertugas mencari arah variasi data terbesar. Karena perbedaan fitur data Fathul begitu masif, variasi tersebut langsung diserap hampir seluruhnya oleh dua komponen utama pertama:
     - **`PCA dimension 0`**: Menyerap **$96.11\%$** variasi data.
     - **`PCA dimension 1`**: Menyerap **$3.89\%$** variasi data.
   - Kedua dimensi ini mencakup **$100\%$ total variasi dataset**. Sumbu pemisah raksasa ini tetap ada di ruang PCA, sehingga K-Means pada ruang PCA 19-D menghasilkan pengelompokan yang persis sama.

---

## 5. Nilai Pusat Klaster (Cluster Centroid)

Port keluaran kedua dari node **k-Means** di KNIME menghasilkan nilai rata-rata pusat kelompok (*centroid*):
- **`cluster_0`**: Nilai rata-rata dari 18 mahasiswa kelompok utama.
- **`cluster_1`**: Nilai dari 1 observasi tunggal (Muhammad Fathul Iman Wahid).

### 5.1 Rangkuman Karakteristik Fitur 4 Polutan (Jalur Tanpa PCA)

Tabel berikut menyederhanakan perbandingan nilai pusat klaster untuk parameter-parameter penting pada ke-4 gas polutan:

| Gas Polutan | Parameter Fitur Kunci | Nilai Cluster 0 (18 Mahasiswa) | Nilai Cluster 1 (Fathul) | Makna & Interpretasi Singkat |
| :---: | :--- | :---: | :---: | :--- |
| **CO** | Rata-rata Konsentrasi (`calc_mean`) | $48.69$ | $0.0288$ | Konsentrasi rata-rata CO kelompok utama |
| **CO** | Fluktuasi Harian (`calc_std`) | $0.0030$ | $0.0025$ | Variabilitas perubahan gas konsisten rendah |
| **CO** | Memori Jangka Panjang (`hurst_exp`) | $0.48$ | $0.61$ | Keteraturan memori tren sinyal berimbang |
| **CH4** | Rata-rata Konsentrasi (`calc_mean`) | $1418.7$ ppb | $18.95$ ppb | Rata-rata konsentrasi metana pada batas wajar |
| **CH4** | Fluktuasi Harian (`calc_std`) | $21.28$ | $20.71$ | Simpangan baku metana kedua klaster setara |
| **CH4** | Memori Jangka Panjang (`hurst_exp`) | $104.45$ | $0.27$ | Dinamika keteraturan sinyal deret waktu |
| **NO2** | Rata-rata Konsentrasi (`calc_mean`) | $52.73$ | **$2.73 \times 10^{10}$** | **Anomali Ekstrem**: Konsentrasi $\text{NO}_2$ Fathul melonjak |
| **NO2** | Puncak Daya Spektrum (`max_power`) | $34.95$ | **$3.04 \times 10^{16}$** | **Anomali Ekstrem**: Daya frekuensi spektrum Fourier raksasa |
| **NO2** | Penurunan Spektral (`spec_decrease`)| $+4.94 \times 10^{8}$ | **$-2.35 \times 10^{16}$** | **Anomali Ekstrem**: Kemiringan daya spektral anomali |
| **SO2** | Rata-rata Konsentrasi (`calc_mean`) | $64.89$ | **$4.64 \times 10^{11}$** | **Anomali Ekstrem**: Konsentrasi $\text{SO}_2$ melonjak masif |
| **SO2** | Titik Berat Frekuensi (`calc_centroid`) | $112.63$ | **$2.20 \times 10^{16}$** | **Anomali Ekstrem**: Pusat massa spektrum gas $\text{SO}_2$ |
| **SO2** | Dimensi Fraktal (`higuchi_dim`) | $1.22$ | **$2.02 \times 10^{16}$** | **Anomali Ekstrem**: Kompleksitas fraktal sinyal anomali |

> **Catatan**: Data mentah lengkap untuk seluruh 272 variabel sentroid tersimpan pada berkas `data/csv/pertemuan-4-csv/Knime cluster/nilai_cluster_nopca.csv`.

---

### 5.2 Rangkuman Komponen Utama PCA (Jalur Dengan PCA 19 Dimensi)

Pada jalur PCA, data dipadatkan menjadi 19 dimensi. Tabel berikut menyajikan ringkasan nilai centroid pada komponen penentu utama:

| Komponen PCA | Nilai Cluster 0 (18 Mahasiswa) | Nilai Cluster 1 (Fathul) | Kontribusi Variansi | Peran dalam Pengelompokan |
| :---: | :---: | :---: | :---: | :--- |
| **`PCA dimension 0`** | **$+3.26 \times 10^{15}$** | **$-5.86 \times 10^{16}$** | **$96.11\%$** | **Pemisah Utama**: Menyerap hampir seluruh variasi jarak antar data |
| **`PCA dimension 1`** | **$+1.54 \times 10^{12}$** | **$-2.76 \times 10^{13}$** | **$3.89\%$** | **Pemisah Kedua**: Menyerap sisa anomali spektral frekuensi |
| **`PCA dimension 2 s.d. 18`** | Rentang $-0.05$ s.d. $+24$ | Rentang $-435$ s.d. $+0.8$ | **$< 0.01\%$** | Menangkap detail fluktuasi lokal skala kecil dan residu data |

> **Catatan**: Rincian numerik ke-19 dimensi PCA lengkap tersimpan pada berkas `data/csv/pertemuan-4-csv/Knime cluster/nilai_cluster_pca.csv`.

---

## 6. Perbandingan Ringkas: Dengan PCA vs Tanpa PCA

| Kriteria | Pendekatan Dengan PCA (19 Dimensi) | Pendekatan Tanpa PCA (272 Fitur) | Keuntungan Menggunakan PCA |
| :--- | :---: | :---: | :--- |
| **Jumlah Dimensi Input** | **19 Dimensi** | **272 Dimensi** | Ukuran dimensi berkurang **$93.01\%$**, data jauh lebih ringkas. |
| **Kecepatan Komputasi** | Cepat ($\approx 722$ operasi/iterasi) | Lambat ($\approx 10.336$ operasi/iterasi) | Perhitungan jarak **$14.3\times$ lebih cepat** pada PCA. |
| **Redundansi / Korelasi** | Tereliminasi (semua dimensi ortogonal) | Tinggi (banyak fitur mirip) | Menghilangkan bobot ganda pada fitur yang serupa. |
| **Kemudahan Visualisasi** | Sangat mudah (cukup plot PCA-0 vs PCA-1) | Sangat sulit (sulit membayangkan 272 dimensi) | Mempermudah peneliti melihat sebaran data secara 2D. |
| **Hasil Partisi Klaster** | `cluster_0` (18) vs `cluster_1` (1) | `cluster_0` (18) vs `cluster_1` (1) | Struktur klaster utama **$100\%$ terjaga sempurna**. |

---

## 7. Pelajaran Penting & Kesimpulan

1. **Pentingnya Normalisasi Data Awal**:
   - Jika fitur data belum dinormalisasi (skala nilainya sangat beragam dari $0.0001$ hingga miliaran), fitur bernilai raksasa akan mendominasi penentuan klaster.
   - Disarankan menambahkan node **`Normalizer`** (misal Z-Score atau Min-Max) di KNIME sebelum masuk ke node PCA atau K-Means agar seluruh fitur berkontribusi secara adil.

2. **Efisiensi Reduksi Dimensi PCA**:
   - Penggunaan PCA 19 dimensi terbukti sangat efisien: memangkas dimensi sebesar **$93.01\%$** dan mempercepat kalkulasi hingga **14.3 kali lipat** tanpa merusak hasil pengelompokan.

3. **Hasil Akhir**:
   - K-Means pada kedua metode membagi 19 mahasiswa menjadi dua kelompok yang identik:
     - **Klaster 0**: 18 mahasiswa dengan sebaran data relatif homogen.
     - **Klaster 1**: Muhammad Fathul Iman Wahid (Burneh, Bangkalan) yang memiliki karakteristik nilai fitur $\text{NO}_2$ dan $\text{SO}_2$ sangat ekstrem.
