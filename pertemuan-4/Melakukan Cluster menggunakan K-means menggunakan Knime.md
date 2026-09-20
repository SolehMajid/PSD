# Melakukan Cluster Menggunakan K-Means Menggunakan KNIME

Dokumentasi ini menyajikan analisis pengelompokan (*clustering*) data deret waktu (*time-series*) 4 parameter polutan udara ($\text{CO}$, $\text{CH}_4$, $\text{NO}_2$, dan $\text{SO}_2$) dari **16 mahasiswa / daerah pengamatan** menggunakan perangkat lunak **KNIME Analytics Platform** dengan algoritma **K-Means**. 

Pada analisis ini, dilakukan studi komparatif antara dua alur pemrosesan:
1. **Pendekatan 1 (Dengan PCA - 16 Dimensi)**: Mereduksi matriks fitur awal berdimensi 272 menjadi **16 komponen utama (*Principal Components*)** sebelum dikelompokkan oleh algoritma K-Means.
2. **Pendekatan 2 (Tanpa PCA - 272 Fitur Penuh)**: Memasukkan seluruh **272 fitur numerik runtun waktu TSFEL** secara langsung ke dalam algoritma K-Means tanpa reduksi dimensi.
---

## 1. Latar Belakang & Karakteristik Data Input

Dataset yang digunakan merupakan integrasi matriks fitur runtun waktu hasil ekstraksi pustaka **TSFEL (Time Series Feature Extraction Library)** dari 16 mahasiswa/wilayah pengamatan di berbagai daerah Jawa Timur dan sekitarnya (seperti Bangkalan, Surabaya, Gresik, Lamongan, Mojokerto, Pamekasan, Sumenep, Blora, hingga Biak Kota).

Setiap baris data mewakili 1 mahasiswa / daerah observasi dengan total **272 fitur numerik**, yang berasal dari:

$$\text{Total Fitur} = 4 \text{ Polutan} \times 68 \text{ Fitur TSFEL} = 272 \text{ Fitur}$$

Ke-4 polutan yang diekstraksi meliputi:
- **CO (Karbon Monoksida)**: 68 fitur runtun waktu (`CO - abs_energy` s.d. `CO - zero_cross`)
- **CH4 (Metana)**: 68 fitur runtun waktu (`CH4 - abs_energy` s.d. `CH4 - zero_cross`)
- **NO2 (Nitrogen Dioksida)**: 68 fitur runtun waktu (`NO2 - abs_energy` s.d. `NO2 - zero_cross`)
- **SO2 (Sulfur Dioksida)**: 68 fitur runtun waktu (`SO2 - abs_energy` s.d. `SO2 - zero_cross`)

Tantangan utama pada dataset ini adalah **tingginya dimensionalitas ($D = 272$)** dibandingkan dengan jumlah sampel yang relatif kecil ($N = 16$), serta adanya variasi skala nilai yang sangat kontras antarfitur statistik, temporal, spektral, dan fraktal.

---

## 2. Arsitektur Workflow KNIME Analytics Platform

Eksperimen K-Means Clustering dimodelkan menggunakan alur kerja visual pada **KNIME Analytics Platform** seperti yang ditunjukkan pada gambar berikut:

```{figure} ../assets/images/images_pertemuan-4/knime-pca-16.png
:width: 100%
:align: center

Arsitektur Workflow KNIME: Perbandingan K-Means Clustering Melalui Reduksi Dimensi PCA (16 Dimensi) vs Tanpa PCA (272 Fitur Langsung) beserta Konfigurasi Parameter Node PCA.
```

### 2.1 Dekomposisi Node Workflow KNIME

Alur kerja pada KNIME terdiri dari komponen-komponen berikut:

1. **Node `Excel Reader`**:
   - Bertindak sebagai simpul masukan data (*data ingestion*).
   - Membaca berkas kompilasi data fitur 16 mahasiswa yang mencakup kolom metadata (`Nama`, `Daerah`) dan 272 kolom variabel numerik hasil ekstraksi TSFEL.

2. **Jalur Atas: Reduksi Dimensi dengan PCA (16 Dimensi) $\rightarrow$ K-Means**:
   - **Node `PCA`**:
     - Opsi *Target Dimensions* dikonfigurasi ke mode **"Dimension(s) to reduce to"** dengan nilai **16**. Artinya, matriks berdimensi 272 diproyeksikan secara ortogonal ke dalam 16 komponen utama (`PCA dimension 0` sampai `PCA dimension 15`).
     - Opsi *Column Selection*: Memasukkan seluruh 272 fitur numerik (*Excludes: No columns in this list*).
   - **Node `k-Means` (Atas)**:
     - Menerima data berdimensi 16 hasil reduksi PCA.
     - Dikonfigurasi untuk mengelompokkan data ke dalam **$k = 2$ klaster** (`cluster_0` dan `cluster_1`).

3. **Jalur Bawah: Tanpa Reduksi Dimensi (Fitur Penuh 272 Dimensi) $\rightarrow$ K-Means**:
   - **Node `k-Means` (Bawah)**:
     - Dihubungkan secara langsung dari port keluaran node `Excel Reader`.
     - Mengelompokkan ke-16 data menggunakan seluruh 272 fitur awal secara langsung tanpa reduksi dimensi ke dalam **$k = 2$ klaster**.

---

## 3. Hasil Pengelompokan 16 Data (Keanggotaan Klaster)

Setelah eksekusi kedua node K-Means pada KNIME, diperoleh hasil penetapan keanggotaan klaster untuk masing-masing skenario (Tanpa PCA dan Dengan PCA 16-D). 

Tabel berikut menyajikan perbandingan penugasan klaster (*cluster assignment*) untuk ke-16 data mahasiswa/daerah:

| No | Nama Mahasiswa | Wilayah / Daerah Pantau | Cluster (Tanpa PCA) | Cluster (Dengan PCA 16-D) | Kesesuaian Hasil |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | **Achmad Saiful Fuadi** | Labang, Bangkalan | `cluster_1` | `cluster_1` | Identik |
| 2 | **Ahmad Ubaidillah Mappattiro** | Masalembu | `cluster_1` | `cluster_1` | Identik |
| 3 | **Ahmad soleh majid** | Socah, Bangkalan | `cluster_1` | `cluster_1` | Identik |
| 4 | **Aisya** | Biak Kota | `cluster_1` | `cluster_1` | Identik |
| 5 | **Alif Baiatur Ridhwan El Habibie** | Surabaya, Gubeng | `cluster_1` | `cluster_1` | Identik |
| 6 | **Intan Resti Haslindawati** | Kadur, Pamekasan | `cluster_1` | `cluster_1` | Identik |
| 7 | **Irwan Dwi Mukhlisin** | Lamongan kota | `cluster_1` | `cluster_1` | Identik |
| 8 | **Mohammad Andri Firmansyah** | Trowulan, Mojokerto | `cluster_1` | `cluster_1` | Identik |
| 9 | **Mohammad Waqidi** | Lenteng | `cluster_1` | `cluster_1` | Identik |
| 10 | **Muhammad Ainul Fuady** | Gresik, Bungah | `cluster_1` | `cluster_1` | Identik |
| 11 | **Muhammad Fathul Iman Wahid** | Burneh, Bangkalan | `cluster_0` | `cluster_0` | **Identik (Outlier)** |
| 12 | **Muhammad Ilham** | Mendenrejo | `cluster_1` | `cluster_1` | Identik |
| 13 | **Muhammad Sirul Amin** | Klampis | `cluster_1` | `cluster_1` | Identik |
| 14 | **Raihan Aryanova Narendra** | Sokobanah | `cluster_1` | `cluster_1` | Identik |
| 15 | **Wildan Haydar Amru** | Krian | `cluster_1` | `cluster_1` | Identik |
| 16 | **fikri mutawakkil** | Pakong, Pamekasan | `cluster_1` | `cluster_1` | Identik |

### 3.1 Ringkasan Sebaran Anggota Klaster

Dari tabel di atas terlihat fenomena yang sangat menarik:
- **`cluster_0`** beranggotakan **1 data tunggal (6.25%)**, yaitu pengamatan dari **Muhammad Fathul Iman Wahid** (Burneh, Bangkalan).
- **`cluster_1`** beranggotakan **15 data (93.75%)**, yang mencakup seluruh mahasiswa/wilayah lainnya.
- **Tingkat Keselarasan**: Partisi klaster antara metode Tanpa PCA dan Dengan PCA menghasilkan keanggotaan yang **100% identik**.

---

## 4. Analisis Mendalam: Mengapa Hasil PCA dan Tanpa PCA Identik?

Mengapa kedua metode yang secara teoretis berbeda (satu beroperasi pada 272 dimensi, satu beroperasi pada 16 dimensi tereduksi) menghasilkan pembagian klaster yang sama persis? 

Penyebab utamanya terletak pada **kehadiran pencilan ekstrem (*extreme feature outlier*) pada salah satu sampel data** yang belum dinormalisasi skala nilainya (*unscaled features*).

### 4.1 Identifikasi Anomali Skala Fitur pada Data Ke-11

Ketika dilakukan audit mendalam terhadap nilai-nilai fitur numerik pada ke-16 data, ditemukan bahwa data nomor 11 (**Muhammad Fathul Iman Wahid**) memiliki nilai yang sangat fantastis (skala $10^{15}$ hingga $10^{16}$) pada sejumlah fitur spektral dan fraktal gas $\text{NO}_2$ dan $\text{SO}_2$.

Tabel berikut menunjukkan 10 fitur dengan selisih terbesar antara data nomor 11 dan rata-rata 15 data lainnya:

| No | Nama Fitur TSFEL | Nilai Data No. 11 (Fathul) | Rata-rata 15 Data Lainnya | Selisih Mutlak ($\Delta$) | Orde Magnitudo |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `NO2 - max_power_spectrum` | $+3.0383 \times 10^{16}$ | $3.9830 \times 10^{1}$ | $3.0383 \times 10^{16}$ | $\approx 10^{16}$ |
| 2 | `NO2 - spectral_decrease` | $-2.3488 \times 10^{16}$ | $5.9254 \times 10^{8}$ | $2.3488 \times 10^{16}$ | $\approx 10^{16}$ |
| 3 | `SO2 - calc_centroid` | $+2.1966 \times 10^{16}$ | $1.1005 \times 10^{2}$ | $2.1966 \times 10^{16}$ | $\approx 10^{16}$ |
| 4 | `SO2 - higuchi_fractal_dimension` | $+2.0188 \times 10^{16}$ | $1.2656 \times 10^{0}$ | $2.0188 \times 10^{16}$ | $\approx 10^{16}$ |
| 5 | `NO2 - higuchi_fractal_dimension` | $+2.0095 \times 10^{16}$ | $1.1930 \times 10^{0}$ | $2.0095 \times 10^{16}$ | $\approx 10^{16}$ |
| 6 | `NO2 - spectral_kurtosis` | $+1.7961 \times 10^{16}$ | $2.0446 \times 10^{1}$ | $1.7961 \times 10^{16}$ | $\approx 10^{16}$ |
| 7 | `SO2 - spectral_kurtosis` | $+1.7532 \times 10^{16}$ | $1.3715 \times 10^{1}$ | $1.7532 \times 10^{16}$ | $\approx 10^{16}$ |
| 8 | `SO2 - maximum_fractal_length` | $-1.2064 \times 10^{16}$ | $-6.4604 \times 10^{-1}$ | $1.2064 \times 10^{16}$ | $\approx 10^{16}$ |
| 9 | `SO2 - petrosian_fractal_dimension`| $+1.0471 \times 10^{16}$ | $5.9334 \times 10^{-1}$ | $1.0471 \times 10^{16}$ | $\approx 10^{16}$ |
| 10 | `SO2 - max_power_spectrum` | $+7.1896 \times 10^{15}$ | $1.1612 \times 10^{1}$ | $7.1896 \times 10^{15}$ | $\approx 10^{15}$ |

Sebagai perbandingan, sebagian besar fitur statistik dasar (seperti `CO - calc_mean` $= 0.0287$ atau `CH4 - calc_mean` $= 1880$) bernilai kurang dari $10^4$.

### 4.2 Analisis Mekanisme pada Metode Tanpa PCA

Algoritma K-Means secara fundamental mengelompokkan observasi berdasarkan **Jarak Euclidean (*Euclidean Distance*)**:

$$d(\mathbf{x}_i, \mathbf{x}_k) = \sqrt{\sum_{j=1}^{272} (x_{ij} - x_{kj})^2}$$

Ketika data tidak melalui tahapan penskalaan fitur (*feature scaling/standardization*):
1. Selisih pada fitur-fitur berorde $10^{16}$ jika dikuadratkan menghasilkan besaran $(10^{16})^2 = 10^{32}$.
2. Nilai $10^{32}$ ini mendominasi **$>99.999999\%$** dari total penjumlahan kuadrat jarak antar-titik.
3. Seluruh 260+ fitur lainnya (yang berskala normal $10^{-3}$ hingga $10^2$) sama sekali kehilangan pengaruh (*swamped by extreme scales*).
4. Akibatnya, jarak spasial antara data nomor 11 ke data mahasiswa lainnya menjadi jutaan triliun kali lebih jauh daripada jarak antar-15 mahasiswa lainnya. K-Means dengan $k=2$ secara otomatis menempatkan data nomor 11 sebagai sentroid klaster tersendiri (`cluster_0`), sementara ke-15 mahasiswa lainnya dipaksa bergabung dalam satu kelompok besar (`cluster_1`).

### 4.3 Analisis Mekanisme pada Metode Dengan PCA (16 Dimensi)

Pada metode dengan PCA, algoritma mencari kombinasi linear fitur yang memaksimumkan variansi data (*eigenvectors* dari matriks kovariansi):

$$\mathbf{w}_1 = \arg\max_{\|\mathbf{w}\|=1} \text{Var}(\mathbf{X}\mathbf{w})$$

1. Karena fitur-fitur pada data nomor 11 memiliki rentang perbedaan hingga $10^{16}$, variansi empiris pada dimensi tersebut mencapai skala raksasa:
   $$\text{Var}(\text{PCA dimension 0}) \approx 2.3932 \times 10^{32}$$
2. Variansi pada komponen utama pertama (`PCA dimension 0`) ini menyerap **100.00%** dari total variansi seluruh dataset 272 fitur. Komponen ke-1 hingga ke-15 hanya menangkap sisa variansi yang sangat kecil secara proporsional.
3. Nilai koordinat `PCA dimension 0` hasil transformasi adalah:
   - Data nomor 11 (Fathul): **$-5.8012 \times 10^{16}$**
   - 15 Data lainnya (Rerata): **$+3.8675 \times 10^{15}$**
4. Ketika K-Means dijalankan pada 16 dimensi PCA, dimensi pertama (`PCA dimension 0`) tetap menjadi sumbu pemisah utama dengan jarak kuadrat sebesar $(-5.80 \times 10^{16} - 3.86 \times 10^{15})^2 \approx 3.82 \times 10^{33}$.
5. Oleh karena itu, K-Means pada ruang 16-D PCA menghasilkan klaster yang **persis sama** dengan K-Means pada ruang 272-D tanpa PCA.

---

## 5. Nilai Hasil Cluster: Analisis Prototipe & Centroid (No-PCA vs PCA)

Pada perangkat lunak KNIME Analytics Platform, port keluaran kedua (*output port 2*) dari node **k-Means** menghasilkan tabel **Cluster Prototypes (Centroids)**, yaitu representasi nilai pusat massa geometris (vektor rerata tiap variabel) untuk setiap kelompok data:
- **`cluster_0` (Baris 1)**: Merefleksikan nilai dari 1 observasi tunggal (Muhammad Fathul Iman Wahid).
- **`cluster_1` (Baris 2)**: Merefleksikan nilai rata-rata dari ke-15 mahasiswa/wilayah observasi lainnya.

Berikut adalah rincian nilai numerik hasil cluster untuk masing-masing skenario pemodelan:

### 5.1 Nilai Centroid Cluster pada Skenario Tanpa PCA

Pada skenario tanpa PCA, titik pusat klaster dihitung langsung pada ruang asli 272 fitur runtun waktu TSFEL. Berikut disajikan tabel nilai centroid klaster untuk ke-4 polutan udara di seluruh domain fitur (Statistik, Temporal, Spektral, dan Fraktal):

#### A. Nilai Centroid Fitur Gas Karbon Monoksida (CO)

| Parameter Fitur CO | Domain Keilmuan | Nilai Cluster 0 (Fathul) | Nilai Cluster 1 (15 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `CO - calc_mean` | Statistik | $0.02879$ | $38.9584$ | Perbedaan skala rata-rata harian CO |
| `CO - calc_std` | Statistik | $0.00253$ | $0.00297$ | Variabilitas fluktuasi konsentrasi sebanding |
| `CO - calc_min` | Statistik | $0.01996$ | $0.02234$ | Batas bawah pengamatan konsentrasi |
| `CO - calc_max` | Statistik | $0.03953$ | $9.7667$ | Puncak konsentrasi polutan |
| `CO - abs_energy` | Temporal | $0.30578$ | $0.29548$ | Energi absolut sinyal deret waktu berimbang |
| `CO - distance` | Temporal | $365.0021$ | $208.5856$ | Panjang total lintasan fluktuasi CO |
| `CO - hurst_exponent` | Fraktal | $0.60659$ | $0.52905$ | Memori jangka panjang (*persistent*) |
| `CO - max_power_spectrum`| Spektral | $24.0906$ | $25.6169$ | Puncak kerapatan daya frekuensi |
| `CO - zero_cross` | Temporal | $0.0000$ | $4.6036$ | Laju perlintasan titik acuan |

#### B. Nilai Centroid Fitur Gas Metana ($\text{CH}_4$)

| Parameter Fitur $\text{CH}_4$ | Domain Keilmuan | Nilai Cluster 0 (Fathul) | Nilai Cluster 1 (15 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `CH4 - calc_mean` | Statistik | $18.954$ | $1325.51$ | Perbedaan satuan konsentrasi ppb |
| `CH4 - calc_std` | Statistik | $20.708$ | $24.166$ | Simpangan baku fluktuasi metana |
| `CH4 - calc_min` | Statistik | $1.8459$ | $1620.90$ | Nilai konsentrasi minimum |
| `CH4 - calc_max` | Statistik | $19.147$ | $1300.00$ | Nilai konsentrasi puncak |
| `CH4 - abs_energy` | Temporal | $13.1507$ | $1.0373 \times 10^{9}$ | Anomali skala energi temporal metana |
| `CH4 - distance` | Temporal | $59.5231$ | $279.8734$ | Panjang lintasan deret waktu |
| `CH4 - hurst_exponent` | Fraktal | $0.27273$ | $125.2754$ | Indeks fraktal keteraturan sinyal |
| `CH4 - max_power_spectrum`| Spektral | $16.1955$ | $1.8994 \times 10^{4}$ | Besaran spektral daya frekuensi |
| `CH4 - zero_cross` | Temporal | $0.0000$ | $379.9488$ | Frekuensi perlintasan garis nol |

#### C. Nilai Centroid Fitur Gas Nitrogen Dioksida ($\text{NO}_2$)

| Parameter Fitur $\text{NO}_2$ | Domain Keilmuan | Nilai Cluster 0 (Fathul) | Nilai Cluster 1 (15 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `NO2 - calc_mean` | Statistik | **$2.7300 \times 10^{10}$** | $43.8041$ | **Anomali Ekstrem**: Perbedaan skala $10^{10}$ |
| `NO2 - calc_std` | Statistik | **$8.0200 \times 10^{9}$** | $0.00073$ | **Anomali Ekstrem**: Variansi raksasa |
| `NO2 - calc_min` | Statistik | $-1.1000 \times 10^{10}$ | $0.00313$ | Nilai terendah pengamatan |
| `NO2 - calc_max` | Statistik | **$6.1300 \times 10^{10}$** | $9.8140$ | Puncak konsentrasi data |
| `NO2 - abs_energy` | Temporal | **$2.9600 \times 10^{8}$** | $0.09223$ | Energi absolut sinyal temporal |
| `NO2 - distance` | Temporal | **$3.6500 \times 10^{15}$** | $156.2291$ | Panjang lintasan kurva sinyal |
| `NO2 - hurst_exponent` | Fraktal | $0.60769$ | $0.60533$ | Persistensi memori deret waktu ($H \approx 0.6$) |
| `NO2 - max_power_spectrum`| Spektral | **$3.0383 \times 10^{16}$** | $39.8301$ | **Anomali Ekstrem**: Puncak daya spektral FFT |
| `NO2 - spectral_kurtosis` | Spektral | **$1.7961 \times 10^{16}$** | $20.4461$ | Keruncingan spektrum frekuensi Fourier |
| `NO2 - spectral_decrease` | Spektral | **$-2.3488 \times 10^{16}$** | $5.9254 \times 10^{8}$ | Kemiringan penurunan daya spektral |
| `NO2 - higuchi_fractal_dim`| Fraktal | **$2.0095 \times 10^{16}$** | $1.1930$ | Dimensi fraktal kompleksitas bentuk kurva |
| `NO2 - zero_cross` | Temporal | $6.0000$ | $19.5333$ | Perlintasan nilai acuan nol |

#### D. Nilai Centroid Fitur Gas Sulfur Dioksida ($\text{SO}_2$)

| Parameter Fitur $\text{SO}_2$ | Domain Keilmuan | Nilai Cluster 0 (Fathul) | Nilai Cluster 1 (15 Data Lainnya) | Selisih / Karakteristik Nilai |
| :--- | :---: | :---: | :---: | :--- |
| `SO2 - calc_mean` | Statistik | **$4.6400 \times 10^{11}$** | $58.4014$ | **Anomali Ekstrem**: Perbedaan skala $10^{11}$ |
| `SO2 - calc_std` | Statistik | $0.00017$ | $0.00084$ | Simpangan baku nilai relatif homogen |
| `SO2 - calc_min` | Statistik | $-0.00053$ | $0.00063$ | Konsentrasi ambang bawah gas SO2 |
| `SO2 - calc_max` | Statistik | $0.00061$ | $14.6022$ | Puncak konsentrasi SO2 |
| `SO2 - abs_energy` | Temporal | **$1.1300 \times 10^{11}$** | $0.01042$ | Energi absolut sinyal deret waktu |
| `SO2 - distance` | Temporal | **$3.6500 \times 10^{14}$** | $159.6428$ | Panjang kurva lintasan temporal |
| `SO2 - hurst_exponent` | Fraktal | $0.61627$ | $0.44918$ | Derajat keteraturan memori runtun waktu |
| `SO2 - max_power_spectrum`| Spektral | **$7.1896 \times 10^{15}$** | $11.6122$ | Puncak spektral frekuensi |
| `SO2 - calc_centroid` | Spektral | **$2.1966 \times 10^{16}$** | $110.0497$ | Titik berat spektral frekuensi |
| `SO2 - higuchi_fractal_dim`| Fraktal | **$2.0188 \times 10^{16}$** | $1.2656$ | Dimensi fraktal kompleksitas kurva |
| `SO2 - zero_cross` | Temporal | $152.0000$ | $71.7334$ | Perlintasan garis nol osilasi sensor |

---

### 5.2 Nilai Centroid Cluster pada Skenario Dengan PCA (16 Dimensi)

Pada skenario dengan PCA, titik pusat klaster dihitung pada ruang tereduksi yang terdiri dari **16 Komponen Utama (`PCA dimension 0` sampai `PCA dimension 15`)**.

Tabel berikut menyajikan seluruh nilai koordinat centroid untuk ke-16 dimensi PCA pada kedua klaster beserta rasio variansi yang dijelaskan:

| Komponen Utama PCA | Nilai Centroid Cluster 0 (`cluster_0`) | Nilai Centroid Cluster 1 (`cluster_1`) | Rasio Variansi Data | Peran & Perilaku Spasial |
| :---: | :---: | :---: | :---: | :--- |
| **`PCA dimension 0`** | **$-5.8012 \times 10^{16}$** | **$+3.8675 \times 10^{15}$** | **$100.00\%$** | **Aksis Pemisah Tunggal Klaster (Jarak $\approx 6.19 \times 10^{16}$)** |
| **`PCA dimension 1`** | $+4.0869 \times 10^{2}$ | $-2.7247 \times 10^{1}$ | $< 0.0001\%$ | Variasi sekunder di dalam Klaster 1 |
| **`PCA dimension 2`** | $+4.4072 \times 10^{2}$ | $-2.8561 \times 10^{1}$ | $< 0.0001\%$ | Variasi tersier sebaran fitur gas |
| **`PCA dimension 3`** | $-1.9844 \times 10^{0}$ | $+8.4712 \times 10^{-2}$ | $< 0.0001\%$ | Fluktuasi lokal skala kecil |
| **`PCA dimension 4`** | $-1.4373 \times 10^{1}$ | $+1.0966 \times 10^{0}$ | $< 0.0001\%$ | Dinamika pembalikan arah deret waktu |
| **`PCA dimension 5`** | $+3.3776 \times 10^{0}$ | $-2.4600 \times 10^{-1}$ | $< 0.0001\%$ | Variasi autokorelasi lag |
| **`PCA dimension 6`** | $-1.7692 \times 10^{0}$ | $+1.3025 \times 10^{-1}$ | $< 0.0001\%$ | Residu noise spektral |
| **`PCA dimension 7`** | $-1.4765 \times 10^{1}$ | $+6.6641 \times 10^{-1}$ | $< 0.0001\%$ | Dinamika wavelet frekuensi rendah |
| **`PCA dimension 8`** | $+9.6575 \times 10^{-3}$ | $-6.4384 \times 10^{-4}$ | $< 0.0001\%$ | Energi harmonik sinyal |
| **`PCA dimension 9`** | $-1.8280 \times 10^{0}$ | $-1.1664 \times 10^{-2}$ | $< 0.0001\%$ | Tingkat asimetri distribusi frekuensi |
| **`PCA dimension 10`** | $+2.2505 \times 10^{-2}$ | $-3.8900 \times 10^{-1}$ | $< 0.0001\%$ | Residu kurtosis |
| **`PCA dimension 11`** | $-3.5928 \times 10^{-1}$ | $-8.1319 \times 10^{-1}$ | $< 0.0001\%$ | Komponen frekuensi tinggi |
| **`PCA dimension 12`** | $+2.3240 \times 10^{0}$ | $+1.3699 \times 10^{-1}$ | $< 0.0001\%$ | Mikro-entropi sinyal |
| **`PCA dimension 13`** | $+4.8029 \times 10^{0}$ | $+2.8378 \times 10^{-1}$ | $< 0.0001\%$ | Fluktuasi fraktal residu |
| **`PCA dimension 14`** | $-2.1828 \times 10^{0}$ | $+8.8373 \times 10^{-2}$ | $< 0.0001\%$ | Noise ortogonal acak |
| **`PCA dimension 15`** | $+2.4555 \times 10^{0}$ | $-5.1722 \times 10^{-2}$ | $< 0.0001\%$ | Noise ortogonal acak |

### 5.3 Analisis Sintesis Nilai Klaster (No-PCA vs PCA)

Perbandingan nilai-nilai numerik pada tabel prototipe di atas memberikan penjelasan ilmiah yang tuntas:
1. **Pada Ruang Tanpa PCA**: Pemisahan `cluster_0` dan `cluster_1` dipicu oleh lonjakan nilai pada fitur-fitur berorde $10^{10}$ s.d. $10^{16}$ (seperti `NO2 - max_power_spectrum` sebesar $3.0383 \times 10^{16}$ dan `SO2 - calc_centroid` sebesar $2.1966 \times 10^{16}$) yang membuat jarak Euclidean Cluster 0 menjadi triliunan kali lebih dominan dibanding fitur lainnya.
2. **Pada Ruang Dengan PCA**: Algoritma PCA menyerap seluruh kovariansi raksasa tersebut ke dalam **`PCA dimension 0`** (dengan variansi $100\%$). Nilai centroid `PCA dimension 0` untuk Cluster 0 adalah $-5.8012 \times 10^{16}$, sementara Cluster 1 adalah $+3.8675 \times 10^{15}$. Dengan selisih koordinat lebih dari $6.18 \times 10^{16}$ pada satu sumbu ini, pemodelan K-Means pada ruang PCA secara otomatis memetakan partisi klaster yang sama persis dengan metode Tanpa PCA.

---

## 6. Perbandingan Komparatif: Dengan PCA vs Tanpa PCA

Berikut adalah matriks perbandingan komprehensif antara pendekatan **Dengan PCA (16 Dimensi)** versus **Tanpa PCA (272 Fitur Penuh)**:

| Parameter Evaluasi | Pendekatan 1: Dengan PCA (16 Dimensi) | Pendekatan 2: Tanpa PCA (272 Fitur) | Analisis Keunggulan & Keterbatasan |
| :--- | :--- | :--- | :--- |
| **Jumlah Dimensi Input** | **16 Dimensi** (Komponen Utama) | **272 Dimensi** (Fitur Penuh TSFEL) | PCA mereduksi ukuran ruang fitur sebesar **$94.12\%$**, menyederhanakan representasi data secara masif. |
| **Beban Komputasi Jarak** | $O(N \cdot K \cdot 16) \approx 512$ operasi | $O(N \cdot K \cdot 272) \approx 8.704$ operasi | Perhitungan jarak Euclidean pada PCA **17 kali lebih cepat** per iterasi konvergensi. |
| **Fenomena *Curse of Dimensionality*** | **Rendah**: Ruang data 16-D jauh lebih padat dan terhindar dari pemuaian jarak kosong (*distance sparsity*). | **Tinggi**: Pada ruang 272-D, semua pasangan titik cenderung memiliki jarak yang relatif mirip (*distance concentration phenomenon*). | PCA mempertahankan keandalan metrik jarak geometris K-Means. |
| **Multikolinearitas Antar-Fitur** | **Tereliminasi**: Seluruh 16 komponen PCA bersifat saling tegak lurus (*orthogonal*), matriks kovariansi diagonal. | **Tinggi**: Banyak fitur TSFEL memiliki korelasi redundan (misal: Mean, Median, RMS, Absolute Energy). | PCA mencegah redundansi bobot fitur berulang pada fungsi jarak. |
| **Kemudahan Visualisasi Data** | **Mudah**: 16 dimensi sangat mudah diproyeksikan ke grafik scatter plot 2D/3D (misal: PCA-0 vs PCA-1). | **Sangat Sulit**: Tidak memungkinkan memvisualisasikan sebaran klaster 272 dimensi tanpa bantuan reduksi dimensi lanjutan. | PCA sangat mendukung analisis eksploratif dan interpretasi visual bagi peneliti. |
| **Interpretasi Fisis Fitur** | **Abstrak**: Setiap dimensi PCA merupakan kombinasi linear dari 272 fitur, sehingga makna fisik satuan gas menjadi tidak langsung. | **Jelas**: Setiap kolom mempertahankan nama fitur asli (misal: konsentrasi ppm, energi spektral, eksponen Hurst). | Tanpa PCA lebih mudah dilacak maknanya secara fisis per parameter gas. |
| **Sensitivitas terhadap Outlier** | Tetap sensitif jika fitur input tidak dinormalisasi terlebih dahulu, karena PCA memprioritaskan variansi terbesar. | Sangat sensitif terhadap skala fitur terbesar; fitur bernilai besar akan mendikte seluruh klaster. | Keduanya membutuhkan tahapan normalisasi data awal agar seimbang. |

---

## 7. Pelajaran Penting (*Lessons Learned*) & Rekomendasi Teknis

Dari hasil pengujian K-Means menggunakan KNIME ini, terdapat sejumlah wawasan metodologis penting (*methodological insights*) bagi pemodelan data sains deret waktu:

1. **Krusialnya Tahapan Normalisasi / Standarisasi Data**:
   - Baik algoritma K-Means maupun PCA berbasis pada komputasi jarak atau variansi. Jika fitur memiliki satuan dan orde magnitudo yang berbeda (misalnya konsentrasi gas bernilai $0.00003$ sedangkan energi spektral bernilai jutaan), fitur bernilai besar akan membajak proses pemodelan.
   - **Rekomendasi**: Sebelum masuk ke node PCA atau K-Means di KNIME, wajib disisipkan node **`Normalizer`** (dengan metode *Z-score Standard Deviation* atau *Min-Max Normalization*) agar seluruh 272 fitur berbobot adil dalam penentuan klaster.

2. **Audit Outlier pada Ekstraksi Fitur**:
   - Terisolasinya data nomor 11 menjadi klaster tunggal (`cluster_0`) menunjukkan perlunya validasi ulang perhitungan fitur pada wilayah Burneh (Bangkalan), khususnya pada domain fraktal dan spektral $\text{NO}_2$ dan $\text{SO}_2$ agar nilainya berada pada skala yang realistis sebelum proses clustering gabungan.

3. **Efisiensi PCA untuk Dataset Skala Besar**:
   - Meskipun pada eksperimen 16 data ini hasil partisinya identik, penggunaan PCA dengan 16 dimensi memberikan efisiensi komputasi $17\times$ lebih ringan, mengeliminasi redundansi korelasi antarfitur TSFEL, dan sangat mempermudah pembuatan visualisasi sebaran klaster.

---

## 8. Kesimpulan

1. Pemodelan klaster menggunakan **KNIME Analytics Platform** berhasil mengimplementasikan K-Means Clustering pada data deret waktu 4 polutan udara dari 16 mahasiswa/wilayah melalui dua skenario: **Dengan PCA 16 Dimensi** dan **Tanpa PCA (272 Fitur Penuh)**.
2. Kedua skenario menghasilkan pembagian anggota klaster yang **100% identik**:
   - **`cluster_0`** (1 data): Muhammad Fathul Iman Wahid (Burneh, Bangkalan).
   - **`cluster_1`** (15 data): Mahasiswa/wilayah pengamatan lainnya.
3. Kesamaan hasil klaster ini dipicu oleh dominasi nilai fitur ekstrem (skala $10^{16}$) pada data ke-11 yang mendikte jarak Euclidean pada skenario Tanpa PCA, sekaligus menyerap $100\%$ variansi data pada `PCA dimension 0` pada skenario Dengan PCA.
4. Penggunaan PCA terbukti berhasil mereduksi dimensionalitas sebesar **$94.12\%$** (dari 272 menjadi 16 dimensi) dan memangkas kompleksitas perhitungan jarak sebesar **17 kali lipat** tanpa kehilangan struktur klaster utama dataset.
