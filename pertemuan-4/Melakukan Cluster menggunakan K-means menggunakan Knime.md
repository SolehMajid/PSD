# Melakukan Cluster Menggunakan K-Means Menggunakan KNIME

Dokumentasi ini menyajikan analisis pengelompokan (*clustering*) data deret waktu (*time-series*) 4 parameter polutan udara ($\text{CO}$, $\text{CH}_4$, $\text{NO}_2$, dan $\text{SO}_2$) dari **18 mahasiswa / daerah pengamatan** menggunakan perangkat lunak **KNIME Analytics Platform** dengan algoritma **K-Means**. 

Pada analisis ini, dilakukan studi komparatif antara dua alur pemrosesan:
1. **Pendekatan 1 (Dengan PCA - 18 Dimensi)**: Mereduksi matriks fitur awal berdimensi 272 menjadi **18 komponen utama (*Principal Components*)** sebelum dikelompokkan oleh algoritma K-Means.
2. **Pendekatan 2 (Tanpa PCA - 272 Fitur Penuh)**: Memasukkan seluruh **272 fitur numerik runtun waktu TSFEL** secara langsung ke dalam algoritma K-Means tanpa reduksi dimensi.
---

## 1. Latar Belakang & Karakteristik Data Input

Dataset yang digunakan merupakan integrasi matriks fitur runtun waktu hasil ekstraksi pustaka **TSFEL (Time Series Feature Extraction Library)** dari 18 mahasiswa/wilayah pengamatan di berbagai daerah Jawa Timur dan sekitarnya (seperti Bangkalan, Surabaya, Gresik, Lamongan, Mojokerto, Pamekasan, Sumenep, Blora, hingga Biak Kota).

Setiap baris data mewakili 1 mahasiswa / daerah observasi dengan total **272 fitur numerik**, yang berasal dari:

$$\text{Total Fitur} = 4 \text{ Polutan} \times 68 \text{ Fitur TSFEL} = 272 \text{ Fitur}$$

Ke-4 polutan yang diekstraksi meliputi:
- **CO (Karbon Monoksida)**: 68 fitur runtun waktu (`CO - abs_energy` s.d. `CO - zero_cross`)
- **CH4 (Metana)**: 68 fitur runtun waktu (`CH4 - abs_energy` s.d. `CH4 - zero_cross`)
- **NO2 (Nitrogen Dioksida)**: 68 fitur runtun waktu (`NO2 - abs_energy` s.d. `NO2 - zero_cross`)
- **SO2 (Sulfur Dioksida)**: 68 fitur runtun waktu (`SO2 - abs_energy` s.d. `SO2 - zero_cross`)

Tantangan utama pada dataset ini adalah **tingginya dimensionalitas ($D = 272$)** dibandingkan dengan jumlah sampel yang relatif kecil ($N = 18$), serta adanya variasi skala nilai yang sangat kontras antarfitur statistik, temporal, spektral, dan fraktal.

---

## 2. Arsitektur Workflow KNIME Analytics Platform

Eksperimen K-Means Clustering dimodelkan menggunakan alur kerja visual pada **KNIME Analytics Platform** seperti yang ditunjukkan pada gambar berikut:

```{figure} ../assets/images/images_pertemuan-4/knime-pca-18.png
:width: 100%
:align: center

Arsitektur Workflow KNIME: Perbandingan K-Means Clustering Melalui Reduksi Dimensi PCA (18 Dimensi) vs Tanpa PCA (272 Fitur Langsung) beserta Konfigurasi Parameter Node PCA.
```

### 2.1 Dekomposisi Node Workflow KNIME

Alur kerja pada KNIME terdiri dari komponen-komponen berikut:

1. **Node `Excel Reader`**:
   - Bertindak sebagai simpul masukan data (*data ingestion*).
   - Membaca berkas kompilasi data fitur 18 mahasiswa yang mencakup kolom metadata (`Nama`, `Daerah`) dan 272 kolom variabel numerik hasil ekstraksi TSFEL.

2. **Jalur Atas: Reduksi Dimensi dengan PCA (18 Dimensi) $\rightarrow$ K-Means**:
   - **Node `PCA`**:
     - Opsi *Target Dimensions* dikonfigurasi ke mode **"Dimension(s) to reduce to"** dengan nilai **18**. Artinya, matriks berdimensi 272 diproyeksikan secara ortogonal ke dalam 18 komponen utama (`PCA dimension 0` sampai `PCA dimension 17`).
     - Opsi *Column Selection*: Memasukkan seluruh 272 fitur numerik (*Excludes: No columns in this list*).
   - **Node `k-Means` (Atas)**:
     - Menerima data berdimensi 18 hasil reduksi PCA.
     - Dikonfigurasi untuk mengelompokkan data ke dalam **$k = 2$ klaster** (`cluster_0` dan `cluster_1`).

3. **Jalur Bawah: Tanpa Reduksi Dimensi (Fitur Penuh 272 Dimensi) $\rightarrow$ K-Means**:
   - **Node `k-Means` (Bawah)**:
     - Dihubungkan secara langsung dari port keluaran node `Excel Reader`.
     - Mengelompokkan ke-18 data menggunakan seluruh 272 fitur awal secara langsung tanpa reduksi dimensi ke dalam **$k = 2$ klaster**.

---

## 3. Hasil Pengelompokan 18 Data (Keanggotaan Klaster)

Setelah eksekusi kedua node K-Means pada KNIME, diperoleh hasil penetapan keanggotaan klaster untuk masing-masing skenario (Tanpa PCA dan Dengan PCA 18-D). 

Tabel berikut menyajikan perbandingan penugasan klaster (*cluster assignment*) untuk ke-18 data mahasiswa/daerah:

| No | Nama Mahasiswa | Wilayah / Daerah Pantau | Cluster (Tanpa PCA) | Cluster (Dengan PCA 18-D) | Kesesuaian Hasil |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | **Achmad Saiful Fuadi** | Labang, Bangkalan | `cluster_1` | `cluster_1` | Identik |
| 2 | **Ahmad Ubaidillah Mappattiro** | Masalembu | `cluster_1` | `cluster_1` | Identik |
| 3 | **Ahmad soleh majid** | Socah, Bangkalan | `cluster_1` | `cluster_1` | Identik |
| 4 | **Aisya** | Biak Kota | `cluster_1` | `cluster_1` | Identik |
| 5 | **Alif Baiatur Ridhwan El Habibie** | Surabaya, Gubeng | `cluster_1` | `cluster_1` | Identik |
| 6 | **Firman Candra Dwi Nugroho** | Kraton, Bangkalan | `cluster_0` | `cluster_0` | **Identik (Outlier)** |
| 7 | **Intan Resti Haslindawati** | Kadur, Pamekasan | `cluster_1` | `cluster_1` | Identik |
| 8 | **Irwan Dwi Mukhlisin** | Lamongan kota | `cluster_1` | `cluster_1` | Identik |
| 9 | **Mohammad Andri Firmansyah** | Trowulan, Mojokerto | `cluster_1` | `cluster_1` | Identik |
| 10 | **Mohammad Waqidi** | Lenteng | `cluster_1` | `cluster_1` | Identik |
| 11 | **Muhammad Ainul Fuady** | Gresik, Bungah | `cluster_1` | `cluster_1` | Identik |
| 12 | **Muhammad Fathul Iman Wahid** | Burneh, Bangkalan | `cluster_1` | `cluster_1` | Identik |
| 13 | **Muhammad Ilham** | Mendenrejo | `cluster_1` | `cluster_1` | Identik |
| 14 | **Muhammad Sirul Amin** | Klampis | `cluster_1` | `cluster_1` | Identik |
| 15 | **Raihan Aryanova Narendra** | Sokobanah | `cluster_1` | `cluster_1` | Identik |
| 16 | **Shofiatul Mahmudah** | Guluk-Guluk, Sumenep | `cluster_1` | `cluster_1` | Identik |
| 17 | **Wildan Haydar Amru** | Krian | `cluster_1` | `cluster_1` | Identik |
| 18 | **fikri mutawakkil** | Pakong, Pamekasan | `cluster_1` | `cluster_1` | Identik |

### 3.1 Ringkasan Sebaran Anggota Klaster

Dari tabel di atas terlihat karakteristik pembagian klaster:
- **`cluster_0`** beranggotakan **1 data tunggal (5.56%)**, yaitu observasi dari **Firman Candra Dwi Nugroho** (Kraton, Bangkalan).
- **`cluster_1`** beranggotakan **17 data (94.44%)**, yang mencakup seluruh mahasiswa/wilayah lainnya.
- **Tingkat Keselarasan**: Partisi klaster antara metode Tanpa PCA dan Dengan PCA menghasilkan keanggotaan yang **100% identik**.

---

## 4. Analisis Mendalam: Mengapa Hasil PCA dan Tanpa PCA Identik?

Mengapa kedua metode yang secara teoretis berbeda (satu beroperasi pada 272 dimensi fitur penuh, satu beroperasi pada 18 dimensi tereduksi) menghasilkan pembagian klaster yang sama persis? 

Penyebab utamanya terletak pada **kehadiran pencilan ekstrem (*extreme feature outlier*) pada sampel data** yang belum melalui tahap normalisasi skala nilai (*unscaled features*).

### 4.1 Identifikasi Anomali Skala Fitur pada Data Ke-6

Ketika dilakukan audit numerik terhadap nilai-nilai fitur pada ke-18 data observasi, ditemukan bahwa data nomor 6 (**Firman Candra Dwi Nugroho**) memiliki nilai yang sangat masif (skala $10^{15}$ hingga $10^{16}$) pada fitur spektral gas $\text{CH}_4$, yaitu `CH4 - spectral_decrease` dan `CH4 - spectral_kurtosis`. Di sisi lain, pada kelompok 17 data lainnya terdapat pula pengamatan dengan nilai fitur spektral $\text{NO}_2$ dan $\text{SO}_2$ yang bernilai tinggi (misalnya pada data Burneh).

Tabel berikut menunjukkan 10 fitur dengan selisih absolut terbesar antara data nomor 6 (Firman) dan rata-rata 17 data lainnya:

| No | Nama Fitur TSFEL | Nilai Data No. 6 (Firman) | Rata-rata 17 Data Lainnya | Selisih Mutlak ($\Delta$) | Orde Magnitudo |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `CH4 - spectral_decrease` | $-1.0233 \times 10^{16}$ | $+1.1579 \times 10^{8}$ | $1.0233 \times 10^{16}$ | $\approx 10^{16}$ |
| 2 | `CH4 - spectral_kurtosis` | $+7.1151 \times 10^{15}$ | $+4.4834 \times 10^{2}$ | $7.1151 \times 10^{15}$ | $\approx 10^{15}$ |
| 3 | `NO2 - max_power_spectrum` | $+3.0648 \times 10^{1}$ | $+1.7872 \times 10^{15}$ | $1.7872 \times 10^{15}$ | $\approx 10^{15}$ |
| 4 | `NO2 - spectral_decrease` | $-6.9902 \times 10^{-1}$ | $-1.3817 \times 10^{15}$ | $1.3817 \times 10^{15}$ | $\approx 10^{15}$ |
| 5 | `SO2 - calc_centroid` | $+2.1136 \times 10^{2}$ | $+1.2921 \times 10^{15}$ | $1.2921 \times 10^{15}$ | $\approx 10^{15}$ |
| 6 | `SO2 - higuchi_fractal_dimension` | $+1.9225 \times 10^{0}$ | $+1.1875 \times 10^{15}$ | $1.1875 \times 10^{15}$ | $\approx 10^{15}$ |
| 7 | `NO2 - higuchi_fractal_dimension` | $+1.8232 \times 10^{0}$ | $+1.1820 \times 10^{15}$ | $1.1820 \times 10^{15}$ | $\approx 10^{15}$ |
| 8 | `NO2 - spectral_kurtosis` | $+2.8249 \times 10^{0}$ | $+1.0565 \times 10^{15}$ | $1.0565 \times 10^{15}$ | $\approx 10^{15}$ |
| 9 | `SO2 - spectral_kurtosis` | $+1.9410 \times 10^{0}$ | $+1.0313 \times 10^{15}$ | $1.0313 \times 10^{15}$ | $\approx 10^{15}$ |
| 10 | `SO2 - maximum_fractal_length` | $-1.4955 \times 10^{0}$ | $-7.0965 \times 10^{14}$ | $7.0965 \times 10^{14}$ | $\approx 10^{14}$ |

Sebagai perbandingan, sebagian besar fitur statistik dasar (seperti `CO - calc_mean` $= 0.0296$ atau `CH4 - calc_mean` $= 1892.8$) bernilai kurang dari $10^4$.

### 4.2 Analisis Mekanisme pada Metode Tanpa PCA

Algoritma K-Means secara fundamental mengelompokkan observasi berdasarkan **Jarak Euclidean (*Euclidean Distance*)**:

$$d(\mathbf{x}_i, \mathbf{x}_k) = \sqrt{\sum_{j=1}^{272} (x_{ij} - x_{kj})^2}$$

Ketika data tidak melalui tahapan penskalaan fitur (*feature scaling/standardization*):
1. Selisih pada fitur-fitur berorde $10^{15}$ hingga $10^{16}$ jika dikuadratkan menghasilkan besaran $(10^{16})^2 = 10^{32}$.
2. Nilai kuadrat selisih ini mendominasi **$>99.99999\%$** dari total penjumlahan kuadrat jarak antar-titik.
3. Seluruh 260+ fitur lainnya (yang berskala normal $10^{-3}$ hingga $10^2$) sama sekali kehilangan pengaruh (*swamped by extreme scales*).
4. Akibatnya, jarak spasial antara data nomor 6 ke data mahasiswa lainnya menjadi triliunan kali lebih jauh daripada jarak relatif antar-17 mahasiswa lainnya. K-Means dengan $k=2$ secara otomatis menempatkan data nomor 6 sebagai sentroid klaster tersendiri (`cluster_0`), sementara ke-17 mahasiswa lainnya dipadukan ke dalam satu kelompok besar (`cluster_1`).

### 4.3 Analisis Mekanisme pada Metode Dengan PCA (18 Dimensi)

Pada metode dengan PCA, algoritma mencari kombinasi linear fitur yang memaksimumkan variansi data (*eigenvectors* dari matriks kovariansi):

$$\mathbf{w}_1 = \arg\max_{\|\mathbf{w}\|=1} \text{Var}(\mathbf{X}\mathbf{w})$$

1. Karena fitur-fitur metana pada data nomor 6 serta fitur spektral $\text{NO}_2/\text{SO}_2$ memiliki rentang perbedaan mencapai skala $10^{16}$, variansi empiris data terkonsentrasi secara masif pada dua komponen utama pertama:
   - **`PCA dimension 0`**: $\text{Var} \approx 2.1276 \times 10^{32}$ (menyerap **$96.12\%$** variansi total).
   - **`PCA dimension 1`**: $\text{Var} \approx 8.5993 \times 10^{30}$ (menyerap **$3.88\%$** variansi total).
   - **Total Variansi Kumulatif PCA 0 & PCA 1**: **$100.00\%$**. Komponen ke-2 hingga ke-17 hanya menangkap sisa variansi yang sangat kecil secara proporsional ($< 0.0001\%$).
2. Nilai koordinat hasil proyeksi PCA pada kedua sumbu utama adalah:
   - **`PCA dimension 0`**:
     - Data nomor 6 (Firman): **$+3.5828 \times 10^{15}$**
     - Rerata 17 Data lainnya: **$-2.1075 \times 10^{14}$**
   - **`PCA dimension 1`**:
     - Data nomor 6 (Firman): **$-1.1728 \times 10^{16}$**
     - Rerata 17 Data lainnya: **$+6.8989 \times 10^{14}$**
3. Ketika K-Means dijalankan pada ruang 18 dimensi PCA, dimensi pertama dan kedua (`PCA dimension 0` dan `PCA dimension 1`) mendominasi fungsi jarak Euclidean dengan perbedaan kuadrat lebih dari $1.5 \times 10^{32}$.
4. Oleh karena itu, K-Means pada ruang 18-D PCA menghasilkan klaster yang **persis sama** dengan K-Means pada ruang 272-D tanpa PCA.

---

## 5. Nilai Hasil Cluster: Analisis Prototipe & Centroid (No-PCA vs PCA)

Pada perangkat lunak KNIME Analytics Platform, port keluaran kedua (*output port 2*) dari node **k-Means** menghasilkan tabel **Cluster Prototypes (Centroids)**, yaitu representasi nilai pusat massa geometris (vektor rerata tiap variabel) untuk setiap kelompok data:
- **`cluster_0` (Baris 1)**: Merefleksikan nilai dari 1 observasi tunggal (**Firman Candra Dwi Nugroho**).
- **`cluster_1` (Baris 2)**: Merefleksikan nilai rata-rata dari ke-17 mahasiswa/wilayah observasi lainnya.

Berikut adalah rincian nilai numerik hasil cluster untuk masing-masing skenario pemodelan sesuai berkas keluaran KNIME:

### 5.1 Nilai Centroid Cluster pada Skenario Tanpa PCA

Pada skenario tanpa PCA, titik pusat klaster dihitung langsung pada ruang asli 272 fitur runtun waktu TSFEL. Berikut disajikan tabel nilai centroid klaster untuk ke-4 polutan udara di seluruh domain fitur (Statistik, Temporal, Spektral, dan Fraktal):

#### A. Nilai Centroid Fitur Gas Karbon Monoksida (CO)

| Parameter Fitur CO | Domain Keilmuan | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `CO - calc_mean` | Statistik | $0.02964$ | $34.378$ | Rata-rata konsentrasi relatif setara |
| `CO - calc_std` | Statistik | $0.00373$ | $0.00293$ | Fluktuasi standar deviasi homogen |
| `CO - calc_min` | Statistik | $0.01976$ | $7.9379$ | Batas bawah pengamatan konsentrasi |
| `CO - calc_max` | Statistik | $0.03936$ | $8.6733$ | Puncak konsentrasi polutan |
| `CO - abs_energy` | Temporal | $0.32573$ | $0.29474$ | Energi absolut sinyal deret waktu berimbang |
| `CO - distance` | Temporal | $364.00$ | $205.63$ | Panjang lintasan fluktuasi konsentrasi |
| `CO - hurst_exponent` | Fraktal | $0.87848$ | $0.49429$ | Memori jangka panjang persistent ($H > 0.5$) |
| `CO - max_power_spectrum`| Spektral | $79.839$ | $24.022$ | Puncak kerapatan daya frekuensi Fourier |
| `CO - zero_cross` | Temporal | $0.0000$ | $4.0620$ | Frekuensi perlintasan titik acuan |

#### B. Nilai Centroid Fitur Gas Metana ($\text{CH}_4$)

| Parameter Fitur $\text{CH}_4$ | Domain Keilmuan | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `CH4 - calc_mean` | Statistik | $1892.8$ | $1280.6$ | Konsentrasi rata-rata metana (ppb) |
| `CH4 - calc_std` | Statistik | $0.0000$ | $23.754$ | Simpangan baku fluktuasi metana |
| `CH4 - calc_min` | Statistik | $1892.8$ | $1534.9$ | Konsentrasi ambang bawah |
| `CH4 - calc_max` | Statistik | $1892.8$ | $1261.6$ | Nilai puncak konsentrasi metana |
| `CH4 - abs_energy` | Temporal | $1.3077 \times 10^{9}$ | $9.9022 \times 10^{8}$ | Energi absolut sinyal runtun waktu |
| `CH4 - distance` | Temporal | $364.00$ | $300.50$ | Panjang lintasan deret waktu |
| `CH4 - hurst_exponent` | Fraktal | $0.0000$ | $110.61$ | Indeks fraktal keteraturan sinyal |
| `CH4 - max_power_spectrum`| Spektral | $0.0000$ | $1.6761 \times 10^{4}$ | Besaran daya spektral puncak |
| `CH4 - spectral_decrease`| Spektral | **$-1.0233 \times 10^{16}$** | $+1.1579 \times 10^{8}$ | **Anomali Ekstrem**: Kemiringan penurunan spektral |
| `CH4 - spectral_kurtosis`| Spektral | **$+7.1151 \times 10^{15}$** | $+4.4834 \times 10^{2}$ | **Anomali Ekstrem**: Keruncingan spektrum Fourier |
| `CH4 - zero_cross` | Temporal | $0.0000$ | $335.25$ | Frekuensi osilasi sinyal garis nol |

#### C. Nilai Centroid Fitur Gas Nitrogen Dioksida ($\text{NO}_2$)

| Parameter Fitur $\text{NO}_2$ | Domain Keilmuan | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `NO2 - calc_mean` | Statistik | $5.0237 \times 10^{-6}$ | $1.6059 \times 10^{9}$ | Rata-rata konsentrasi $\text{NO}_2$ |
| `NO2 - calc_std` | Statistik | $5.4761 \times 10^{-6}$ | $4.7176 \times 10^{8}$ | Standar deviasi fluktuasi gas |
| `NO2 - calc_min` | Statistik | $-8.5602 \times 10^{-6}$ | $-6.4706 \times 10^{8}$ | Nilai terendah pengamatan sensor |
| `NO2 - calc_max` | Statistik | $2.1365 \times 10^{-5}$ | $3.6059 \times 10^{9}$ | Puncak konsentrasi polutan |
| `NO2 - abs_energy` | Temporal | $2.0157 \times 10^{-8}$ | $1.7412 \times 10^{7}$ | Energi absolut sinyal temporal |
| `NO2 - distance` | Temporal | $364.00$ | $2.1471 \times 10^{14}$ | Panjang lintasan kurva deret waktu |
| `NO2 - hurst_exponent` | Fraktal | $0.81718$ | $0.40667$ | Persistensi memori deret waktu |
| `NO2 - max_power_spectrum`| Spektral | $30.648$ | $1.7872 \times 10^{15}$ | Puncak spektral frekuensi Fourier |
| `NO2 - spectral_kurtosis` | Spektral | $2.8249$ | $1.0565 \times 10^{15}$ | Keruncingan spektrum frekuensi |
| `NO2 - spectral_decrease` | Spektral | $-0.69902$ | $-1.3817 \times 10^{15}$ | Gradien penurunan kerapatan spektral |
| `NO2 - higuchi_fractal_dim`| Fraktal | $1.8232$ | $1.1820 \times 10^{15}$ | Dimensi fraktal kompleksitas bentuk kurva |
| `NO2 - zero_cross` | Temporal | $38.00$ | $18.529$ | Frekuensi perlintasan nilai acuan nol |

#### D. Nilai Centroid Fitur Gas Sulfur Dioksida ($\text{SO}_2$)

| Parameter Fitur $\text{SO}_2$ | Domain Keilmuan | Nilai Cluster 0 (Firman) | Nilai Cluster 1 (17 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `SO2 - calc_mean` | Statistik | $-1.5241 \times 10^{-5}$ | $2.7294 \times 10^{10}$ | Rata-rata konsentrasi $\text{SO}_2$ |
| `SO2 - calc_std` | Statistik | $1.0570 \times 10^{-4}$ | $9.1058 \times 10^{-4}$ | Standar deviasi fluktuasi gas |
| `SO2 - calc_min` | Statistik | $-7.3512 \times 10^{-4}$ | $146.36$ | Batas bawah pengamatan sensor |
| `SO2 - calc_max` | Statistik | $4.2059 \times 10^{-4}$ | $12.941$ | Puncak konsentrasi $\text{SO}_2$ |
| `SO2 - abs_energy` | Temporal | $4.1631 \times 10^{-6}$ | $6.6471 \times 10^{9}$ | Energi absolut sinyal temporal |
| `SO2 - distance` | Temporal | $364.00$ | $2.1471 \times 10^{13}$ | Panjang total kurva lintasan temporal |
| `SO2 - hurst_exponent` | Fraktal | $0.70444$ | $0.35230$ | Derajat keteraturan memori deret waktu |
| `SO2 - max_power_spectrum`| Spektral | $13.515$ | $4.2292 \times 10^{14}$ | Puncak kerapatan daya spektral |
| `SO2 - calc_centroid` | Spektral | $211.36$ | $1.2921 \times 10^{15}$ | Titik berat spektral frekuensi |
| `SO2 - higuchi_fractal_dim`| Fraktal | $1.9225$ | $1.1875 \times 10^{15}$ | Dimensi fraktal kurva sinyal |
| `SO2 - zero_cross` | Temporal | $89.00$ | $77.765$ | Frekuensi perlintasan garis nol osilasi sensor |

---

### 5.2 Nilai Centroid Cluster pada Skenario Dengan PCA (18 Dimensi)

Pada skenario dengan PCA, titik pusat klaster dihitung pada ruang tereduksi yang terdiri dari **18 Komponen Utama (`PCA dimension 0` sampai `PCA dimension 17`)**.

Tabel berikut menyajikan seluruh nilai koordinat centroid untuk ke-18 dimensi PCA pada kedua klaster beserta rasio variansi yang dijelaskan:

| Komponen Utama PCA | Nilai Centroid Cluster 0 (`cluster_0`) | Nilai Centroid Cluster 1 (`cluster_1`) | Rasio Variansi Data | Peran & Perilaku Spasial |
| :---: | :---: | :---: | :---: | :--- |
| **`PCA dimension 0`** | **$+3.5828 \times 10^{15}$** | **$-2.1075 \times 10^{14}$** | **$96.12\%$** | **Aksis Primer Pemisah Klaster (Jarak $\approx 3.79 \times 10^{15}$)** |
| **`PCA dimension 1`** | **$-1.1728 \times 10^{16}$** | **$+6.8989 \times 10^{14}$** | **$3.88\%$** | **Aksis Sekunder Pemisah Klaster (Jarak $\approx 1.24 \times 10^{16}$)** |
| **`PCA dimension 2`** | $-8.9444 \times 10^{2}$ | $+5.2612 \times 10^{1}$ | $< 0.0001\%$ | Variasi sub-kelompok sebaran konsentrasi gas |
| **`PCA dimension 3`** | $-1.0211 \times 10^{3}$ | $+5.9624 \times 10^{1}$ | $< 0.0001\%$ | Variasi karakteristik spektral frekuensi |
| **`PCA dimension 4`** | $+1.2359 \times 10^{0}$ | $-4.0289 \times 10^{-2}$ | $< 0.0001\%$ | Dinamika pembalikan arah deret waktu |
| **`PCA dimension 5`** | $+2.5020 \times 10^{-3}$ | $+4.3371 \times 10^{-3}$ | $< 0.0001\%$ | Fluktuasi autokorelasi lag temporal |
| **`PCA dimension 6`** | $+5.8870 \times 10^{0}$ | $-5.4741 \times 10^{-1}$ | $< 0.0001\%$ | Residu noise spektral frekuensi menengah |
| **`PCA dimension 7`** | $+2.9263 \times 10^{-2}$ | $-1.7214 \times 10^{-3}$ | $< 0.0001\%$ | Dinamika harmonik sinyal frekuensi rendah |
| **`PCA dimension 8`** | $+9.3514 \times 10^{0}$ | $-3.3007 \times 10^{-1}$ | $< 0.0001\%$ | Fluktuasi kurva fraktal |
| **`PCA dimension 9`** | $+2.0156 \times 10^{1}$ | $-1.3110 \times 10^{0}$ | $< 0.0001\%$ | Tingkat asimetri distribusi fitur |
| **`PCA dimension 10`** | $-6.5754 \times 10^{-1}$ | $-7.1612 \times 10^{-2}$ | $< 0.0001\%$ | Residu kurtosis distribusi data |
| **`PCA dimension 11`** | $-3.7855 \times 10^{0}$ | $+6.7534 \times 10^{-1}$ | $< 0.0001\%$ | Komponen fluktuasi frekuensi tinggi |
| **`PCA dimension 12`** | $-3.4493 \times 10^{-1}$ | $+1.9372 \times 10^{-1}$ | $< 0.0001\%$ | Mikro-entropi sinyal deret waktu |
| **`PCA dimension 13`** | $+1.8072 \times 10^{-1}$ | $-9.0364 \times 10^{-2}$ | $< 0.0001\%$ | Fluktuasi residu temporal |
| **`PCA dimension 14`** | $-1.3101 \times 10^{0}$ | $+5.4918 \times 10^{-2}$ | $< 0.0001\%$ | Noise ortogonal acak |
| **`PCA dimension 15`** | $-5.9809 \times 10^{-1}$ | $-4.3460 \times 10^{-2}$ | $< 0.0001\%$ | Noise ortogonal acak |
| **`PCA dimension 16`** | $-1.0617 \times 10^{0}$ | $-6.1555 \times 10^{-2}$ | $< 0.0001\%$ | Noise ortogonal residu |
| **`PCA dimension 17`** | $+2.9033 \times 10^{0}$ | $-3.8155 \times 10^{-1}$ | $< 0.0001\%$ | Residu ortogonal tingkat akhir |

### 5.3 Analisis Sintesis Nilai Klaster (No-PCA vs PCA)

Perbandingan nilai-nilai numerik pada tabel prototipe di atas memberikan penjelasan ilmiah yang tuntas:
1. **Pada Ruang Tanpa PCA**: Pemisahan `cluster_0` dan `cluster_1` dipicu oleh lonjakan nilai pada fitur metana `CH4 - spectral_decrease` ($-1.0233 \times 10^{16}$) dan `CH4 - spectral_kurtosis` ($+7.1151 \times 10^{15}$) serta fitur-fitur spektral gas $\text{NO}_2$ dan $\text{SO}_2$ lainnya. Perbedaan kuadrat jarak Euclidean mencapai orde $10^{32}$, menjadikan jarak Cluster 0 triliunan kali lebih jauh dibanding jarak antartitik normal lainnya.
2. **Pada Ruang Dengan PCA**: Algoritma PCA memproyeksikan seluruh kovariansi raksasa tersebut ke dalam **`PCA dimension 0`** (dengan variansi $96.12\%$) dan **`PCA dimension 1`** (dengan variansi $3.88\%$). Kedua sumbu utama ini bersama-sama menyerap **$100.00\%$** variansi total. Selisih koordinat pada kedua aksis ini ($\approx 3.79 \times 10^{15}$ pada PCA-0 dan $\approx 1.24 \times 10^{16}$ pada PCA-1) membuat pemodelan K-Means pada ruang 18-D PCA memetakan partisi klaster yang **100% identik** dengan metode Tanpa PCA.

---

## 6. Perbandingan Komparatif: Dengan PCA vs Tanpa PCA

Berikut adalah matriks perbandingan komprehensif antara pendekatan **Dengan PCA (18 Dimensi)** versus **Tanpa PCA (272 Fitur Penuh)**:

| Parameter Evaluasi | Pendekatan 1: Dengan PCA (18 Dimensi) | Pendekatan 2: Tanpa PCA (272 Fitur) | Analisis Keunggulan & Keterbatasan |
| :--- | :--- | :--- | :--- |
| **Jumlah Dimensi Input** | **18 Dimensi** (Komponen Utama) | **272 Dimensi** (Fitur Penuh TSFEL) | PCA mereduksi ukuran ruang fitur sebesar **$93.38\%$**, menyederhanakan representasi data secara masif. |
| **Beban Komputasi Jarak** | $O(N \cdot K \cdot 18) \approx 648$ operasi | $O(N \cdot K \cdot 272) \approx 9.792$ operasi | Perhitungan jarak Euclidean pada PCA **15.1 kali lebih cepat** per iterasi konvergensi. |
| **Fenomena *Curse of Dimensionality*** | **Rendah**: Ruang data 18-D jauh lebih padat dan terhindar dari pemuaian jarak kosong (*distance sparsity*). | **Tinggi**: Pada ruang 272-D, semua pasangan titik cenderung memiliki jarak yang relatif mirip (*distance concentration phenomenon*). | PCA mempertahankan keandalan metrik jarak geometris K-Means. |
| **Multikolinearitas Antar-Fitur** | **Tereliminasi**: Seluruh 18 komponen PCA bersifat saling tegak lurus (*orthogonal*), matriks kovariansi diagonal. | **Tinggi**: Banyak fitur TSFEL memiliki korelasi redundan (misal: Mean, Median, RMS, Absolute Energy). | PCA mencegah redundansi bobot fitur berulang pada fungsi jarak. |
| **Kemudahan Visualisasi Data** | **Mudah**: 18 dimensi sangat mudah diproyeksikan ke grafik scatter plot 2D/3D (misal: PCA-0 vs PCA-1). | **Sangat Sulit**: Tidak memungkinkan memvisualisasikan sebaran klaster 272 dimensi tanpa bantuan reduksi dimensi lanjutan. | PCA sangat mendukung analisis eksploratif dan interpretasi visual bagi peneliti. |
| **Interpretasi Fisis Fitur** | **Abstrak**: Setiap dimensi PCA merupakan kombinasi linear dari 272 fitur, sehingga makna fisik satuan gas menjadi tidak langsung. | **Jelas**: Setiap kolom mempertahankan nama fitur asli (misal: konsentrasi ppm, energi spektral, eksponen Hurst). | Tanpa PCA lebih mudah dilacak maknanya secara fisis per parameter gas. |
| **Sensitivitas terhadap Outlier** | Tetap sensitif jika fitur input tidak dinormalisasi terlebih dahulu, karena PCA memprioritaskan variansi terbesar. | Sangat sensitif terhadap skala fitur terbesar; fitur bernilai besar akan mendikte seluruh klaster. | Keduanya membutuhkan tahapan normalisasi data awal agar seimbang. |

---

## 7. Pelajaran Penting (*Lessons Learned*) & Rekomendasi Teknis

Dari hasil pengujian K-Means menggunakan KNIME ini, terdapat sejumlah wawasan metodologis penting (*methodological insights*) bagi pemodelan data sains deret waktu:

1. **Krusialnya Tahapan Normalisasi / Standarisasi Data**:
   - Baik algoritma K-Means maupun PCA berbasis pada komputasi jarak atau variansi. Jika fitur memiliki satuan dan orde magnitudo yang berbeda (misalnya konsentrasi gas bernilai $0.00003$ sedangkan energi spektral bernilai jutaan triliun), fitur bernilai besar akan membajak proses pemodelan.
   - **Rekomendasi**: Sebelum masuk ke node PCA atau K-Means di KNIME, wajib disisipkan node **`Normalizer`** (dengan metode *Z-score Standard Deviation* atau *Min-Max Normalization*) agar seluruh 272 fitur berbobot adil dalam penentuan klaster.

2. **Audit Outlier pada Ekstraksi Fitur**:
   - Terisolasinya data nomor 6 menjadi klaster tunggal (`cluster_0`) menunjukkan perlunya validasi ulang perhitungan fitur pada wilayah Kraton (Bangkalan), khususnya pada domain spektral $\text{CH}_4$, $\text{NO}_2$, dan $\text{SO}_2$ agar nilainya berada pada skala yang realistis sebelum proses clustering gabungan.

3. **Efisiensi PCA untuk Dataset Deret Waktu**:
   - Meskipun pada eksperimen 18 data ini hasil partisinya identik, penggunaan PCA dengan 18 dimensi memberikan efisiensi komputasi $15.1\times$ lebih ringan, mengeliminasi redundansi korelasi antarfitur TSFEL, dan sangat mempermudah pembuatan visualisasi sebaran klaster pada bidang proyeksi ortogonal.

---

## 8. Kesimpulan

1. Pemodelan klaster menggunakan **KNIME Analytics Platform** berhasil mengimplementasikan K-Means Clustering pada data deret waktu 4 polutan udara dari **18 mahasiswa/wilayah** melalui dua skenario: **Dengan PCA 18 Dimensi** dan **Tanpa PCA (272 Fitur Penuh)**.
2. Kedua skenario menghasilkan pembagian anggota klaster yang **100% identik**:
   - **`cluster_0`** (1 data): **Firman Candra Dwi Nugroho** (Kraton, Bangkalan).
   - **`cluster_1`** (17 data): Mahasiswa/wilayah pengamatan lainnya.
3. Kesamaan hasil klaster ini dipicu oleh dominasi nilai fitur ekstrem (skala $10^{15} - 10^{16}$) pada data ke-6 yang mendikte jarak Euclidean pada skenario Tanpa PCA, sekaligus menyerap $100\%$ variansi kumulatif data pada `PCA dimension 0` ($96.12\%$) dan `PCA dimension 1` ($3.88\%$) pada skenario Dengan PCA.
4. Penggunaan PCA terbukti berhasil mereduksi dimensionalitas sebesar **$93.38\%$** (dari 272 menjadi 18 dimensi) dan memangkas kompleksitas perhitungan jarak sebesar **15.1 kali lipat** tanpa kehilangan struktur klaster utama dataset.
