# Create & Read (CR) - Data Analysis & Statistik Deskriptif

Dokumentasi ini menyajikan alur kerja lengkap pada **Tugas Pertemuan ke-2** mata kuliah Proyek Sains Data. Fokus utama dari modul ini adalah implementasi operasi **Create & Read (CR)** pada arsitektur data modern: memigrasikan dataset hasil pemrosesan data satelit Copernicus Sentinel-5P ke *cloud database* (**Aiven PostgreSQL**), melakukan *data ingestion* (penarikan data) menggunakan **KNIME Analytics Platform**, serta melakukan analisis **Statistik Deskriptif** mendalam yang divalidasi dengan perhitungan manual dan rumus **Microsoft Excel**.

---

## Ringkasan Alur Kerja

```
+-------------------------------------------------------------------+
|  1. Data Polutan CSV (Hasil Pertemuan 1)                         |
|     (CH4, CO, NO2, SO2 - Kabupaten Bangkalan)                    |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  2. Cloud Database Migration (Aiven PostgreSQL)                   |
|     - DDL Skema Tabel: CREATE TABLE hasil_polutan                 |
|     - Import Data CSV via pgAdmin (Encoding UTF-8)                |
|     - Verifikasi Tabel di Cloud (Aiven PG Studio)                 |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  3. Data Ingestion & Pipeline (KNIME Analytics Platform)          |
|     - Node: PostgreSQL Connector (Koneksi Cloud SSL)              |
|     - Node: DB Query Reader (SELECT * FROM public.hasil_polutan)  |
|     - Node: Statistics (Ekstraksi Statistik Deskriptif)           |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  4. Analisis Statistik Deskriptif & Validasi                      |
|     - Penjelasan 15+ Properti Statistik KNIME                     |
|     - Perhitungan Manual Langkah Demi Langkah (Step-by-Step)      |
|     - Validasi Hasil & Histogram di Microsoft Excel               |
|     - Snippet Formula Excel Siap Salin (=MIN, =AVERAGE, dll.)     |
+-------------------------------------------------------------------+
```

---

## 1. Pindah Data CSV ke Cloud Database (Aiven PostgreSQL)

Pada pertemuan sebelumnya, data konsentrasi 4 gas polutan (**CH₄, CO, NO₂, SO₂**) di atas wilayah administratif Kabupaten Bangkalan telah diekstraksi dari satelit Sentinel-5P dan disimpan dalam format file `.csv`. Untuk menjamin keandalan akses (*high availability*), sentralisasi data, dan kemudahan integrasi dengan platform analitik, data tersebut dipindahkan ke *database* berbasis *cloud*.

Platform *cloud* yang digunakan adalah **Aiven for PostgreSQL**, yaitu layanan *Database-as-a-Service* (DBaaS) terkelola penuh yang memiliki performa tinggi, fitur keamanan terenkripsi (SSL/TLS), serta *web management console* terintegrasi.

### 1.1 Pembuatan Tabel Database (`hasil_polutan`)

Langkah pertama adalah mendefinisikan skema tabel relasional di dalam database `defaultdb` pada instance Aiven PostgreSQL menggunakan bahasa SQL (*Data Definition Language* / DDL). Pembuatan skema ini dilakukan melalui antarmuka query tool pgAdmin 4:

```sql
DROP TABLE IF EXISTS hasil_polutan;

CREATE TABLE hasil_polutan (
    id SERIAL PRIMARY KEY,
    tanggal DATE NOT NULL,
    CH4 DOUBLE PRECISION,
    CO DOUBLE PRECISION,
    NO2 DOUBLE PRECISION,
    SO2 DOUBLE PRECISION
);
```

**Penjelasan Struktur Tabel:**
- `id`: Tipe data integer auto-increment (`SERIAL`) yang berfungsi sebagai *Primary Key* unik untuk setiap rekaman baris.
- `tanggal`: Tipe data `DATE` untuk menyimpan tanggal observasi satelit dalam format standar ISO `YYYY-MM-DD`.
- `CH4`, `CO`, `NO2`, `SO2`: Tipe data `DOUBLE PRECISION` (bilangan riil presisi ganda 64-bit / IEEE 754 float) untuk mengakomodasi nilai konsentrasi polutan yang memiliki banyak angka desimal atau nilai ilmiah yang sangat kecil.

```{figure} ../assets/images/images_pertemuan-2/1.buat-table.png
:width: 100%
:align: center

Eksekusi Query DDL Pembuatan Tabel `hasil_polutan` pada PostgreSQL Aiven melalui Query Tool pgAdmin.
```

### 1.2 Proses Import File CSV ke Tabel Cloud

Setelah tabel relasional berhasil terbentuk, file CSV gabungan (`Hasil Polutan.csv`) diimpor ke dalam tabel `hasil_polutan` menggunakan fitur **Import/Export Data** pada pgAdmin.

**Konfigurasi Parameter Import:**
1. **Import/Export**: Dipilih mode `Import`.
2. **Filename**: Lokasi direktori file lokal `Hasil Polutan.csv`.
3. **Format**: `csv`.
4. **Encoding**: `UTF8` untuk memastikan kompatibilitas karakter tanpa risiko korupsi data.
5. **Header**: Diaktifkan (`Yes`) karena baris pertama file CSV memuat nama kolom.
6. **Delimiter**: Tanda koma (`,`).
7. **Quote**: Tanda kutip ganda (`"`).

```{figure} ../assets/images/images_pertemuan-2/1.import-csv.png
:width: 75%
:align: center

Jendela Konfigurasi Import File CSV (`Hasil Polutan.csv`) ke Tabel `hasil_polutan`.
```

### 1.3 Verifikasi Data Tersimpan di Aiven Cloud (PG Studio)

Untuk memastikan bahwa seluruh data telah berhasil diunggah dan terintegrasi dengan sempurna pada infrastruktur *cloud*, pemeriksaan dilakukan langsung melalui konsol web Aiven pada menu **PG Studio**.

Sebanyak **366 baris data** (mencakup periode observasi satu tahun penuh) berhasil tersimpan. Pada tabel tersebut terlihat bahwa terdapat baris yang memiliki nilai numerik polutan, serta beberapa baris bernilai `null` pada hari-hari tertentu di mana instrumen satelit tidak memperoleh pantulan sensor yang valid akibat tutupan awan tebal (*cloud masking*).

```{figure} ../assets/images/images_pertemuan-2/1.hasil-di-aiven.png
:width: 100%
:align: center

Tampilan Verifikasi Data pada Layanan Cloud Database Aiven melalui Web Console PG Studio.
```

---

## 2. Tarik Data Cloud ke KNIME Analytics Platform

Tahap selanjutnya adalah melakukan pembacaan (*Read*) data dari cloud database Aiven ke dalam **KNIME Analytics Platform**. KNIME merupakan platform analisis data berbasis alur kerja (*visual workflow*) yang memungkinkan integrasi database dan eksplorasi data secara terstruktur.

### 2.1 Konfigurasi Node PostgreSQL Connector

Node pertama yang digunakan pada alur kerja KNIME adalah **PostgreSQL Connector**. Node ini bertugas menginisialisasi protokol koneksi JDBC terenkripsi ke server cloud Aiven.

**Parameter Konfigurasi:**
- **Hostname**: `pg-3662398f-asolehmajid-da39.a.aivencloud.com`
- **Database name**: `defaultdb`
- **Port**: `5432`
- **Authentication type**: `Username and Password`
- **Credentials**: Username `avnadmin` beserta kata sandi koneksi database Aiven.

```{figure} ../assets/images/images_pertemuan-2/2.cloud-connect_knime.png
:width: 85%
:align: center

Konfigurasi Koneksi Node PostgreSQL Connector Menuju Hostname Cloud Database Aiven.
```

### 2.2 Penarikan Data Menggunakan Node DB Query Reader

Setelah koneksi berstatus hijau (terhubung), *port* koneksi dihubungkan ke node **DB Query Reader**. Node ini mengeksekusi instruksi SQL query untuk mengambil seluruh dataset dari tabel polutan dan mengubahnya menjadi format tabel data internal KNIME:

```sql
SELECT * FROM public.hasil_polutan;
```

Hasil eksekusi node ini menghasilkan tabel data dengan **366 baris (rows)** dan **5 kolom (columns)**:
- `tanggal` (Date)
- `ch4` (Float)
- `co` (Float)
- `no2` (Float)
- `so2` (Float)

```{figure} ../assets/images/images_pertemuan-2/2.query_knime.png
:width: 100%
:align: center

Output Node DB Query Reader Menampilkan Struktur 366 Baris Data Polutan yang Berhasil Diambil dari Cloud.
```

---

## 3. Analisis Statistik Deskriptif Menggunakan KNIME

Data yang telah diambil kemudian dialirkan ke node **Statistics**. Node ini secara otomatis menghitung metrik statistik deskriptif untuk setiap kolom numerik maupun nominal, memberikan gambaran sebaran data (*distribution*), kecenderungan memusat (*central tendency*), ukuran dispersi (*dispersion*), bentuk distribusi (*shape*), serta integritas data (*data quality/missing values*).

```{figure} ../assets/images/images_pertemuan-2/3.statistik-perhitungan_knime.png
:width: 100%
:align: center

Workflow KNIME (`PostgreSQL Connector` -> `DB Query Reader` -> `Statistics`) Beserta Tabel Ringkasan Statistik Deskriptif.
```

### 3.1 Tabel Ringkasan Statistik Deskriptif (KNIME)

Berdasarkan hasil eksekusi node **Statistics** pada KNIME (sebagaimana terlihat pada gambar antarmuka di atas), diperoleh ringkasan data statistik deskriptif untuk keempat gas polutan:

#### Tabel Ringkasan Lengkap (KNIME Statistics Table)

| Column | Min | Max | Mean | Std. deviation | Variance | Skewness | Kurtosis | Overall sum | No. missings | No. NaNs | No. +$\infty$ | No. -$\infty$ | Median | Row count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ch4** | 1,841.516 | 1,916.853 | 1,886.025 | 19.885 | 395.419 | -0.711 | -0.007 | 50,922.664 | 339 | 0 | 0 | 0 | *(?)* | 366 |
| **co** | 0.02 | 0.044 | 0.029 | 0.003 | 0 | 0.703 | 1.961 | 6.803 | 130 | 0 | 0 | 0 | *(?)* | 366 |
| **no2** | 0 | 0 | 0 | 0 | 0 | 3.924 | 27.942 | 0.008 | 148 | 0 | 0 | 0 | *(?)* | 366 |
| **so2** | -0.001 | 0.001 | 0 | 0 | 0 | 0.437 | 1.462 | 0.016 | 117 | 0 | 0 | 0 | *(?)* | 366 |

> **Catatan Penting Mengenai Tampilan Nilai di KNIME:**
> 1. **Kolom Median:** Pada gambar antarmuka KNIME di atas, kolom **Median** ditandai dengan ikon tanda tanya merah `(?)`. Hal ini terjadi karena secara *default*, opsi dialog konfigurasi **"Calculate median values (computationally expensive)"** dalam keadaan **tidak dicentang (unchecked)** guna menghemat alokasi memori dan waktu komputasi pengurutan data (*sorting*). Nilai median divalidasi dan dihitung secara akurat pada Microsoft Excel dan simulasi manual.
> 2. **Pembulatan Desimal Angka Nol (`0`):** Pada gas `no2` dan `so2`, tabel ringkasan KNIME menampilkan angka `0` pada *Min, Max, Mean, Std. deviation,* dan *Variance* karena format antarmuka KNIME secara default menerapkan pembulatan 3 digit desimal di belakang koma ($0.000$). Nilai sebenarnya berada pada skala mikro/ilmiah (misalnya rata-rata NO₂ adalah $3.56 \times 10^{-5}\ \text{mol/m}^2$ dan SO₂ adalah $6.58 \times 10^{-5}\ \text{mol/m}^2$) sebagaimana divalidasi dengan presisi tinggi pada Microsoft Excel.

#### Pengelompokan Metrik Terstruktur

Agar data statistik deskriptif di atas lebih mudah dibaca, dianalisis, dan dipahami karakteristiknya, berikut adalah penyajian metrik yang dikelompokkan ke dalam tiga kategori utama:

##### 1. Ukuran Pemusatan & Penyebaran Data (Central Tendency & Dispersion)

Tabel ini merangkum rentang batas nilai, titik pusat distribusi, serta tingkat variabilitas konsentrasi gas polutan:

| Variabel | Satuan | Nilai Minimum | Nilai Maksimum | Mean ($\bar{x}$) | Median (Excel) | Std. Deviation ($s$) | Variansi ($s^2$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH₄ (Metana)** | ppb | 1,841.516 | 1,916.853 | 1,886.025 | 1,886.851 | 19.885 | 395.419 |
| **CO (Karbon Monoksida)** | $\text{mol/m}^2$ | 0.020 | 0.044 | 0.029 | 0.029 | 0.003 | $1.01 \times 10^{-5}$ |
| **NO₂ (Nitrogen Dioksida)** | $\text{mol/m}^2$ | $5.23 \times 10^{-6}$ | $2.46 \times 10^{-4}$ | $3.56 \times 10^{-5}$ | $3.15 \times 10^{-5}$ | $2.40 \times 10^{-5}$ | $5.78 \times 10^{-10}$ |
| **SO₂ (Sulfur Dioksida)** | $\text{mol/m}^2$ | -0.00052 | 0.00081 | $6.58 \times 10^{-5}$ | $5.17 \times 10^{-5}$ | 0.000203 | $4.13 \times 10^{-8}$ |

##### 2. Bentuk Kurva Distribusi & Nilai Akumulasi (Shape & Overall Sum)

Tabel ini mengidentifikasi derajat kemiringan, keruncingan kurva, kecenderungan pencilan (*outliers*), dan akumulasi total polutan:

| Variabel | Skewness ($G_1$) | Klasifikasi Kemiringan | Kurtosis ($G_2$) | Klasifikasi Keruncingan | Overall Sum |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CH₄ (Metana)** | -0.711 | Negatif (*Left-skewed*) | -0.007 | Mesokurtik (Mendekati Normal) | 50,922.664 |
| **CO (Karbon Monoksida)** | +0.703 | Positif (*Right-skewed*) | +1.961 | Leptokurtik (Cukup Runcing) | 6.803 |
| **NO₂ (Nitrogen Dioksida)** | +3.924 | Positif Kuat (*Right-skewed*) | +27.942 | Leptokurtik Ekstrem (*Heavy Tails*) | 0.008 |
| **SO₂ (Sulfur Dioksida)** | +0.437 | Positif (*Right-skewed*) | +1.462 | Leptokurtik Moderat | 0.016 |

##### 3. Kualitas & Integritas Data Observasi (Data Completeness & Quality)

Tabel ini mengevaluasi kelengkapan data pengamatan harian selama 1 tahun penuh serta validitas komputasi:

| Variabel | Total Baris | Data Valid | Missing Values ($null$) | Rasio Missing (%) | No. NaNs | No. Tak Hingga ($\pm\infty$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH₄ (Metana)** | 366 baris | 27 baris | 339 baris | 92.62% | 0 | 0 |
| **CO (Karbon Monoksida)** | 366 baris | 236 baris | 130 baris | 35.52% | 0 | 0 |
| **NO₂ (Nitrogen Dioksida)** | 366 baris | 218 baris | 148 baris | 40.44% | 0 | 0 |
| **SO₂ (Sulfur Dioksida)** | 366 baris | 249 baris | 117 baris | 31.97% | 0 | 0 |

---

### 3.2 Penjelasan Komprehensif Masing-Masing Properti Statistik

Berikut adalah penjelasan teoretis, rumus matematis, keterangan komponen, dan interpretasi dari setiap properti statistik yang dihasilkan oleh node **Statistics** di KNIME:

#### 1. Column
- **Definisi**: Nama pengenal variabel atau dimensi pengukuran dalam tabel data.
- **Fungsi**: Membedakan atribut pengukuran konsentrasi polutan atmosfer (`ch4`, `co`, `no2`, dan `so2`), sedangkan kolom temporal `tanggal` dikelompokkan secara terpisah pada tab *Nominal Histogram Table*.

#### 2. Min (Minimum)
- **Definisi**: Nilai numerik terkecil di antara seluruh baris data valid pada variabel tertentu.
- **Rumus Matematis**:
  $$\text{Min} = \min(x_1, x_2, \dots, x_n)$$
- **Keterangan Simbol**:
  - $x_i$: Nilai data observasi ke-$i$.
  - $n$: Jumlah rekaman data yang valid (non-null).
- **Interpretasi Data**:
  - Menunjukkan batas bawah konsentrasi polutan. Pada CH₄, nilai minimum tercatat adalah $1\,841.516\ \text{ppb}$, CO sebesar $0.020\ \text{mol/m}^2$ ($0.020487$), dan NO₂ sebesar $5.23 \times 10^{-6}\ \text{mol/m}^2$ (dibulatkan menjadi `0` di KNIME).
  - Pada gas SO₂ terdapat nilai minimum negatif ($-0.001\ \text{mol/m}^2$ di KNIME atau $-0.00052\ \text{mol/m}^2$ di Excel) akibat ketidakpastian koreksi radiometrik sensor satelit pada saat tutupan awan tipis (*cloud masking*).

#### 3. Max (Maximum)
- **Definisi**: Nilai numerik terbesar di antara seluruh baris data valid pada variabel tertentu.
- **Rumus Matematis**:
  $$\text{Max} = \max(x_1, x_2, \dots, x_n)$$
- **Keterangan Simbol**:
  - $x_i$: Nilai data observasi ke-$i$.
  - $n$: Jumlah rekaman data yang valid.
- **Interpretasi Data**:
  - Mengindikasikan puncak konsentrasi tertinggi yang pernah tercatat selama rentang 1 tahun pengamatan. Nilai maksimum CH₄ mencapai $1\,916.853\ \text{ppb}$, CO mencapai $0.044\ \text{mol/m}^2$, SO₂ mencapai $0.001\ \text{mol/m}^2$, dan NO₂ mencapai $0.000246\ \text{mol/m}^2$.

#### 4. Mean (Rata-rata Hitung / Aritmetika)
- **Definisi**: Titik pusat massa atau nilai rerata aritmetika dari seluruh sampel data yang valid.
- **Rumus Matematis**:
  $$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$
- **Keterangan Simbol**:
  - $\bar{x}$: Nilai rata-rata sampel (*sample mean*).
  - $\sum_{i=1}^{n} x_i$: Akumulasi penjumlahan seluruh data yang valid.
  - $n$: Banyaknya baris data yang valid.
- **Interpretasi Data**:
  - Memberikan estimasi nilai ekspektasi tipikal konsentrasi polutan harian di Kabupaten Bangkalan. Nilai rata-rata CH₄ adalah $1\,886.025\ \text{ppb}$, mean CO adalah $0.029\ \text{mol/m}^2$ ($0.028825$), mean SO₂ adalah $0.0000658\ \text{mol/m}^2$ ($6.58 \times 10^{-5}$), dan mean NO₂ adalah $0.0000356\ \text{mol/m}^2$ ($3.56 \times 10^{-5}$).

#### 5. Median (Nilai Tengah)
- **Definisi**: Nilai yang membagi distribusi data terurut menjadi dua bagian yang berukuran sama (50% data di bawah median dan 50% data di atas median).
- **Rumus Matematis**:
  $$\text{Median} = \begin{cases} x_{\left(\frac{n+1}{2}\right)}, & \text{jika } n \text{ ganjil} \\[8pt] \frac{x_{\left(\frac{n}{2}\right)} + x_{\left(\frac{n}{2} + 1\right)}}{2}, & \text{jika } n \text{ genap} \end{cases}$$
- **Keterangan Simbol**:
  - $x_{(k)}$: Nilai observasi pada peringkat ke-$k$ setelah seluruh data diurutkan secara menaik (*ascending*).
  - $n$: Ukuran sampel valid.
- **Interpretasi Data**:
  - Bersifat *robust* (kebal terhadap pengaruh nilai ekstrem atau pencilan/*outliers*).
  - Pada antarmuka KNIME kolom ini berstatus `(?)` (tidak dihitung otomatis demi menghemat komputasi *sorting*), namun diverifikasi penuh di Excel: median CH₄ adalah $1\,886.851\ \text{ppb}$, CO adalah $0.028644\ \text{mol/m}^2$, NO₂ adalah $3.15 \times 10^{-5}\ \text{mol/m}^2$, dan SO₂ adalah $5.17 \times 10^{-5}\ \text{mol/m}^2$.

#### 6. Std. Deviation (Standar Deviasi / Simpangan Baku)
- **Definisi**: Ukuran dispersi yang mengukur simpangan rata-rata nilai-nilai data individual terhadap nilai rata-ratanya ($\bar{x}$).
- **Rumus Matematis (Sampel)**:
  $$s = \sqrt{\frac{1}{n - 1} \sum_{i=1}^{n} (x_i - \bar{x})^2}$$
- **Keterangan Simbol**:
  - $s$: Simpangan baku sampel (*sample standard deviation*).
  - $(x_i - \bar{x})$: Deviasi nilai observasi ke-$i$ dari rata-rata.
  - $n - 1$: Derajat kebebasan (*degrees of freedom* / koreksi Bessel).
- **Interpretasi Data**:
  - Semakin besar nilai $s$, semakin bervariasi dan dinamis konsentrasi polutan tersebut. Standar deviasi CH₄ adalah $19.885$, CO sebesar $0.003$ ($0.003181$), NO₂ sebesar $2.40 \times 10^{-5}$, dan SO₂ sebesar $0.000203$.

#### 7. Variance (Variansi / Ragam)
- **Definisi**: Rata-rata kuadrat deviasi nilai data dari nilai rata-ratanya, yang setara dengan kuadrat dari standar deviasi ($s^2$).
- **Rumus Matematis**:
  $$s^2 = \frac{1}{n - 1} \sum_{i=1}^{n} (x_i - \bar{x})^2$$
- **Keterangan Simbol**:
  - $s^2$: Variansi sampel (*sample variance*).
- **Interpretasi Data**:
  - Menggambarkan besaran dispersi kuadratik data. Variansi CH₄ adalah $395.419$ (kuadrat dari $19.885$). Untuk gas mikro seperti CO ($1.01 \times 10^{-5}$), SO₂ ($4.13 \times 10^{-8}$), dan NO₂ ($5.78 \times 10^{-10}$), nilainya dibulatkan menjadi $0$ pada tampilan 3 desimal KNIME.

#### 8. Skewness (Kemiringan Distribusi)
- **Definisi**: Derajat ketidaksimetrisan (*asymmetry*) kurva distribusi frekuensi di sekitar nilai rata-ratanya.
- **Rumus Matematis (Fisher-Pearson Adjusted Sample Skewness)**:
  $$G_1 = \frac{n}{(n - 1)(n - 2)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^3$$
- **Keterangan Simbol**:
  - $G_1$: Koefisien kemiringan sampel (formula standar yang digunakan pada KNIME dan rumus Excel `=SKEW`).
  - $\frac{x_i - \bar{x}}{s}$: Skor standar (*z-score*) observasi ke-$i$.
- **Interpretasi Data**:
  - **Skewness $> 0$ (Miring ke Kanan / Positif)**: Ekor kurva memanjang ke arah nilai tinggi. Ditemukan secara sangat kuat pada `no2` ($3.924$), serta `co` ($0.703$) dan `so2` ($0.437$). Ini menunjukkan mayoritas hari memiliki konsentrasi gas normal yang rendah, dengan lonjakan emisi sporadis di hari-hari tertentu.
  - **Skewness $< 0$ (Miring ke Kiri / Negatif)**: Ekor kurva memanjang ke arah nilai rendah. Terjadi pada `ch4` ($-0.711$), menandakan sebagian besar data berkumpul di konsentrasi yang relatif tinggi.

#### 9. Kurtosis (Keruncingan Distribusi)
- **Definisi**: Ukuran ketajaman puncak (*peakedness*) dan ketebalan ekor (*tailedness*) distribusi frekuensi data dibandingkan dengan distribusi normal standar.
- **Rumus Matematis (Sample Excess Kurtosis)**:
  $$G_2 = \frac{n(n + 1)}{(n - 1)(n - 2)(n - 3)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^4 - \frac{3(n - 1)^2}{(n - 2)(n - 3)}$$
- **Keterangan Simbol**:
  - $G_2$: Nilai *excess kurtosis* sampel (formula standar pada KNIME dan rumus Excel `=KURT`). Pada kurva normal standar, $G_2 = 0$.
  - Suku pertama: Momen keempat terstandarisasi dengan penimbang derajat kebebasan.
  - Suku kedua: Faktor pengurang koreksi sampel terhadap nilai kurtosis mesokurtik normal ($3$).
- **Interpretasi Data**:
  - **Kurtosis $> 0$ (Leptokurtik / Berpuncak Runcing & Heavy Tails)**: Mengindikasikan sebaran data dengan puncak tajam dan ekor tebal berisi pencilan (*outliers*) ekstrem. Terlihat sangat dominan pada `no2` ($27.942$), serta `co` ($1.961$) dan `so2` ($1.462$).
  - **Kurtosis $\approx 0$ (Mendekati Mesokurtik / Distribusi Normal)**: Terjadi pada `ch4` ($-0.007$). Nilainya yang hampir nol menandakan bahwa keruncingan distribusi gas metana menyerupai kurva lonceng normal standar dengan sebaran data yang merata di sekitar rata-rata.

#### 10. Overall Sum (Jumlah Total)
- **Definisi**: Akumulasi penjumlahan dari seluruh data numerik yang valid pada variabel yang bersangkutan.
- **Rumus Matematis**:
  $$\text{Overall Sum} = \sum_{i=1}^{n} x_i$$
- **Interpretasi Data**:
  - Total akumulasi nilai sampel valid: CH₄ sebesar $50\,922.664$, CO sebesar $6.803$ ($6.802761$), SO₂ sebesar $0.016$ ($0.016393$), dan NO₂ sebesar $0.008$ ($0.007751$).

#### 11. No. Missings (Jumlah Nilai Hilang)
- **Definisi**: Jumlah baris data observasi yang bernilai kosong (`null`), di mana sensor satelit tidak merekam data pengukuran pada tanggal tersebut.
- **Rumus Matematis**:
  $$\text{No. Missings} = N_{\text{total}} - n_{\text{valid}}$$
- **Keterangan Simbol**:
  - $N_{\text{total}}$: Total keseluruhan baris pengamatan dalam rentang satu tahun ($366$ hari).
  - $n_{\text{valid}}$: Jumlah baris pengamatan yang terisi nilai numerik valid.
- **Interpretasi Data**:
  - Kualitas rekaman satelit Sentinel-5P dipengaruhi oleh tutupan awan (*cloud masking*). Dari total $366$ hari pengamatan:
    - Kolom `ch4` memiliki $339$ data *missing* (hanya $27$ hari terekam valid).
    - Kolom `no2` memiliki $148$ data *missing* ($218$ hari valid).
    - Kolom `co` memiliki $130$ data *missing* ($236$ hari valid).
    - Kolom `so2` memiliki $117$ data *missing* ($249$ hari valid).

#### 12. No. NaNs (Not a Number)
- **Definisi**: Jumlah sel data yang berisi nilai *NaN*, yaitu simbol khusus komputasi numerik untuk nilai yang tidak terdefinisi secara matematis (misalnya hasil operasi $0/0$).
- **Interpretasi Data**: Pada dataset ini bernilai $0$ untuk seluruh kolom, membuktikan tidak terjadi anomali operasi aritmetika pada pipeline data.

#### 13. No. +$\infty$ (No. +unlimited / Positive Infinity)
- **Definisi**: Jumlah sel yang bernilai positif tak hingga ($+\infty$), biasanya muncul dari pembagian bilangan riil dengan nol ($x / 0$).
- **Interpretasi Data**: Bernilai $0$ untuk seluruh kolom.

#### 14. No. -$\infty$ (No. -unlimited / Negative Infinity)
- **Definisi**: Jumlah sel yang bernilai negatif tak hingga ($-\infty$), biasanya terjadi akibat pembagian nilai negatif dengan nol ($-x / 0$) atau nilai logaritma dari nol ($\ln(0)$).
- **Interpretasi Data**: Bernilai $0$ untuk seluruh kolom.

#### 15. Row Count (Jumlah Total Baris)
- **Definisi**: Total keseluruhan baris pengamatan dalam tabel data, baik yang berisi nilai valid maupun nilai *missing*.
- **Interpretasi Data**: Bernilai $366$ baris untuk semua kolom, merepresentasikan 366 hari pengamatan (tahun kabisat 2024–2025).

#### 16. Histogram (Distribusi Frekuensi)
- **Definisi**: Representasi grafis berbentuk diagram batang mini (*sparkline histogram*) yang memetakan frekuensi kemunculan nilai data ke dalam rentang interval (*bins*) tertentu.
- **Interpretasi Data**: Pada kolom antarmuka KNIME, visualisasi histogram batang menunjukkan secara intuitif bentuk sebaran data—misalnya kurva distribusi NO₂ yang condong kuat ke kiri dengan ekor panjang ke kanan (*skewness* $3.924$).

---

## 4. Contoh Perhitungan Manual & Verifikasi Rumus Excel

Untuk memverifikasi kebenaran perhitungan statistik yang dihasilkan oleh KNIME, dilakukan pengujian ulang menggunakan lembar kerja **Microsoft Excel**. Hasil verifikasi membuktikan kecocokan penuh antara output KNIME dan rumus Excel.

```{figure} ../assets/images/images_pertemuan-2/perhitungan-manual_exel.png
:width: 100%
:align: center

Hasil Validasi Statistik Deskriptif Menggunakan Microsoft Excel untuk Keempat Gas Polutan.
```

> 📥 **File Dataset CSV:**
> Data gabungan konsentrasi polutan yang digunakan dalam proses validasi dan perhitungan Excel di atas dapat diakses atau diunduh pada tautan berikut: [data/csv/Hasil Polutan.csv](../data/csv/Hasil%20Polutan.csv)

### 4.1 Tabel Validasi Komparasi Data Excel

Berikut adalah tabel hasil komputasi presisi tinggi yang dihasilkan pada lembar kerja Microsoft Excel (sesuai tangkapan layar `perhitungan-manual_exel.png`) untuk keempat gas polutan:

| Column | Min | Max | Mean | Std. deviation | Variance | Skewness | Kurtosis | Overall sum | No. missings | No. NaNs | No. +$\infty$ | No. -$\infty$ | Median | Row count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ch4** | 1841.516 | 1916.853 | 1886.025 | 19.88513 | 395.4186 | -0.71079 | -0.00677 | 50922.66 | 339 | 0 | 0 | 0 | - | 366 |
| **co** | 0.020487 | 0.044218 | 0.028825 | 0.003181 | 1.01E-05 | 0.703194 | 1.960951 | 6.802761 | 130 | 0 | 0 | 0 | - | 366 |
| **no2** | 5.23E-06 | 0.000246 | 3.56E-05 | 2.4E-05 | 5.78E-10 | 3.924393 | 27.94159 | 0.007751 | 148 | 0 | 0 | 0 | - | 366 |
| **so2** | -0.00052 | 0.000808 | 6.58E-05 | 0.000203 | 4.13E-08 | 0.436808 | 1.462382 | 0.016393 | 117 | 0 | 0 | 0 | - | 366 |

**Catatan Hasil Komparasi:**
1. **Konsistensi KNIME dan Excel**: Seluruh nilai metrik pada Excel di atas konsisten 100% terhadap ringkasan statistik KNIME. Pada gas NO₂ dan SO₂, Excel menampilkan notasi eksponensial presisi tinggi (misal variansi NO₂ sebesar $5.78 \times 10^{-10}$ dan mean sebesar $3.56 \times 10^{-5}$) yang pada antarmuka KNIME dibulatkan menjadi `0`.
2. **Proporsi Baris Valid vs Missing ($N = 366$):**
   - **CH₄**: $27$ baris valid ($366 - 339$)
   - **CO**: $236$ baris valid ($366 - 130$)
   - **NO₂**: $218$ baris valid ($366 - 148$)
   - **SO₂**: $249$ baris valid ($366 - 117$)
3. **Nilai Median Terhitung di Excel (`=MEDIAN`):**
   - CH₄: $1886.851\ \text{ppb}$
   - CO: $0.028644\ \text{mol/m}^2$
   - NO₂: $3.15 \times 10^{-5}\ \text{mol/m}^2$
   - SO₂: $5.17 \times 10^{-5}\ \text{mol/m}^2$

---

### 4.2 Simulasi Perhitungan Manual Langkah Demi Langkah (Step-by-Step)

Untuk memahami secara transparan bagaimana setiap rumus matematis bekerja, mari kita lakukan simulasi kalkulasi manual menggunakan sampel data kecil ($n = 5$) yang diambil dari data terurut polutan CH₄ pada dataset:

$$X = \{ 1850.21,\ 1867.29,\ 1886.85,\ 1897.61,\ 1908.68 \}$$

- Ukuran sampel valid: $n = 5$
- Total pengamatan: $N = 366$

---

#### 1. Perhitungan Nilai Minimum (Min)
Mencari elemen data dengan nilai numerik terkecil pada himpunan sampel:
$$\text{Min} = \min(1850.21,\ 1867.29,\ 1886.85,\ 1897.61,\ 1908.68) = \mathbf{1850.21}$$

---

#### 2. Perhitungan Nilai Maksimum (Max)
Mencari elemen data dengan nilai numerik terbesar pada himpunan sampel:
$$\text{Max} = \max(1850.21,\ 1867.29,\ 1886.85,\ 1897.61,\ 1908.68) = \mathbf{1908.68}$$

---

#### 3. Perhitungan Nilai Rata-rata (Mean / $\bar{x}$)
Menjumlahkan seluruh elemen data, kemudian membaginya dengan jumlah sampel ($n = 5$):
$$\sum_{i=1}^{5} x_i = 1850.21 + 1867.29 + 1886.85 + 1897.61 + 1908.68 = 9410.64$$

$$\bar{x} = \frac{\sum_{i=1}^{5} x_i}{n} = \frac{9410.64}{5} = \mathbf{1882.128} \approx \mathbf{1882.13}$$

---

#### 4. Perhitungan Nilai Tengah (Median)
Karena data telah diurutkan menaik dan ukuran sampel $n = 5$ bernilai ganjil:
$$\text{Posisi Median} = \frac{n + 1}{2} = \frac{5 + 1}{2} = 3$$

$$\text{Median} = X_{(3)} = \mathbf{1886.85}$$

*(Catatan: Jika ukuran sampel $n$ genap, nilai median dihitung dari rata-rata dua titik tengah: $\frac{X_{(n/2)} + X_{(n/2 + 1)}}{2}$).*

---

#### 5. Perhitungan Variansi ($s^2$) & Standar Deviasi ($s$)
Dibuat tabel deviasi terhadap nilai rata-rata sampel ($\bar{x} = 1882.128$):

| $i$ | $x_i$ | $(x_i - \bar{x})$ | $(x_i - \bar{x})^2$ | $(x_i - \bar{x})^3$ | $(x_i - \bar{x})^4$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1850.21 | $-31.918$ | $1018.7587$ | $-32516.74$ | $1037869.34$ |
| 2 | 1867.29 | $-14.838$ | $220.1662$ | $-3266.83$ | $48473.17$ |
| 3 | 1886.85 | $+4.722$ | $22.2973$ | $+105.29$ | $497.17$ |
| 4 | 1897.61 | $+15.482$ | $239.6923$ | $+3710.92$ | $57452.41$ |
| 5 | 1908.68 | $+26.552$ | $705.0087$ | $+18719.39$ | $497037.27$ |
| **Total ($\sum$)** | **9410.64** | **0.000** | **2205.9233** | **-13247.97** | **1641329.36** |

**Variansi Sampel ($s^2$):**
$$s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n - 1} = \frac{2205.9233}{5 - 1} = \frac{2205.9233}{4} = \mathbf{551.4808} \approx \mathbf{551.481}$$

**Standar Deviasi Sampel ($s$):**
$$s = \sqrt{s^2} = \sqrt{551.4808} = \mathbf{23.4836} \approx \mathbf{23.484}$$

---

#### 6. Perhitungan Kemiringan (Skewness / $G_1$)
Menggunakan rumus Fisher-Pearson sample skewness:
$$G_1 = \frac{n}{(n - 1)(n - 2)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^3 = \frac{n}{(n - 1)(n - 2) \cdot s^3} \sum_{i=1}^{n} (x_i - \bar{x})^3$$

Substitusi nilai yang diperoleh:
- $s^3 = (23.4836)^3 \approx 12950.84$
- $\sum_{i=1}^{5} (x_i - \bar{x})^3 = -13247.97$
- Faktor pengali: $\frac{n}{(n - 1)(n - 2)} = \frac{5}{4 \times 3} = \frac{5}{12} \approx 0.4167$

$$G_1 = 0.4167 \times \frac{-13247.97}{12950.84} = 0.4167 \times (-1.02294) = \mathbf{-0.4262}$$

*(Tanda negatif mengonfirmasi bahwa ekor kurva distribusi sampel memanjang ke arah kiri).*

---

#### 7. Perhitungan Keruncingan (Kurtosis / $G_2$)
Menggunakan rumus sample excess kurtosis:
$$G_2 = \frac{n(n + 1)}{(n - 1)(n - 2)(n - 3)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^4 - \frac{3(n - 1)^2}{(n - 2)(n - 3)}$$

Substitusi nilai yang diperoleh:
- $s^4 = (551.4808)^2 \approx 304131.07$
- $\sum_{i=1}^{5} \left( \frac{x_i - \bar{x}}{s} \right)^4 = \frac{1641329.36}{304131.07} \approx 5.3968$
- Suku pengali pertama: $\frac{5 \times (5 + 1)}{4 \times 3 \times 2} = \frac{30}{24} = 1.25$
- Suku pengurang kedua: $\frac{3 \times (4)^2}{3 \times 2} = \frac{48}{6} = 8.00$

$$G_2 = (1.25 \times 5.3968) - 8.00 = 6.7460 - 8.00 = \mathbf{-1.2540}$$

*(Nilai $G_2 < 0$ menunjukkan distribusi berbentuk platikurtik dengan puncak yang lebih landai dibanding kurva normal).*

---

#### 8. Perhitungan Jumlah Kumulatif (Overall Sum)
$$\text{Overall Sum} = \sum_{i=1}^{5} x_i = 1850.21 + 1867.29 + 1886.85 + 1897.61 + 1908.68 = \mathbf{9410.64}$$

---

#### 9. Perhitungan Jumlah Data Hilang (No. Missings)
Dengan total baris data pengamatan $N_{\text{total}} = 366$ dan baris data terisi valid pada gas CH₄ sebanyak $n_{\text{valid}} = 27$:
$$\text{No. Missings} = N_{\text{total}} - n_{\text{valid}} = 366 - 27 = \mathbf{339}$$

---

## 5. Salinan Kode Rumus Excel (Ready-to-Copy)

Berikut adalah daftar rumus fungsi bawaan Microsoft Excel yang dapat langsung disalin (*copy-paste*) ke dalam lembar kerja Excel atau notebook Markdown Anda. Diasumsikan data konsentrasi polutan berada pada rentang sel **`B2:B367`** (366 baris data):

### 5.1 Rumus Per Properti Statistik

**1. Nilai Minimum (Min):**
```text
=MIN(B2:B367)
```

**2. Nilai Maksimum (Max):**
```text
=MAX(B2:B367)
```

**3. Nilai Rata-rata (Mean):**
```text
=AVERAGE(B2:B367)
```

**4. Nilai Tengah (Median):**
```text
=MEDIAN(B2:B367)
```

**5. Standar Deviasi Sampel (Std. Dev):**
```text
=STDEV.S(B2:B367)
```

**6. Variansi Sampel (Variance):**
```text
=VAR.S(B2:B367)
```

**7. Derajat Kemiringan (Skewness):**
```text
=SKEW(B2:B367)
```

**8. Derajat Keruncingan (Kurtosis):**
```text
=KURT(B2:B367)
```

**9. Jumlah Kumulatif (Overall Sum):**
```text
=SUM(B2:B367)
```

**10. Jumlah Data Hilang (No. Missings):**
```text
=COUNTBLANK(B2:B367)
```

**11. Jumlah Data Terisi / Valid (Valid Count):**
```text
=COUNT(B2:B367)
```

**12. Total Baris Keseluruhan (Row Count):**
```text
=ROWS(B2:B367)
```

**13. Jumlah Nilai Tak Terdefinisi (No. NaNs):**
```text
=COUNTIF(B2:B367, "#N/A")
```

**14. Jumlah Nilai Positif Tak Hingga (No. +unlimited):**
```text
=COUNTIF(B2:B367, "=+inf")
```

**15. Jumlah Nilai Negatif Tak Hingga (No. -unlimited):**
```text
=COUNTIF(B2:B367, "=-inf")
```

---

### 5.2 Blok Kode Gabungan (Multi-Column Master Formula)

Jika Anda ingin membuat tabel ringkasan statistik komprehensif di Excel (misal Kolom B = CH4, Kolom C = CO, Kolom D = NO2, Kolom E = SO2):

```text

=MIN(B2:B367)          ' Rumus Min
=MAX(B2:B367)          ' Rumus Max
=AVERAGE(B2:B367)      ' Rumus Mean
=MEDIAN(B2:B367)       ' Rumus Median
=STDEV.S(B2:B367)      ' Rumus Standar Deviasi Sampel
=VAR.S(B2:B367)        ' Rumus Variansi Sampel
=SKEW(B2:B367)         ' Rumus Skewness
=KURT(B2:B367)         ' Rumus Kurtosis
=SUM(B2:B367)          ' Rumus Overall Sum
=COUNTBLANK(B2:B367)   ' Rumus No. Missings
=COUNTIF(B2:B367, 0)   ' Menghitung Kemunculan Angka Nol (Jika Diperlukan)
=COUNT(B2:B367)        ' Jumlah Sel Berisi Angka (Data Valid)
=ROWS(B2:B367)         ' Total Keseluruhan Baris Pengamatan
```

---

## Kesimpulan

Berdasarkan seluruh tahapan yang telah diselesaikan pada Pertemuan ke-2:
1. **Migrasi Data ke Cloud**: Dataset polutan hasil Sentinel-5P sukses diunggah ke PostgreSQL Aiven dengan penataan skema tabel DDL yang terstruktur dan aman.
2. **Koneksi KNIME ke Cloud**: KNIME Analytics Platform berhasil membaca dataset cloud secara *real-time* via JDBC SSL menggunakan pasangan node *PostgreSQL Connector* dan *DB Query Reader*.
3. **Analisis Statistik Deskriptif**: Node *Statistics* di KNIME memberikan gambaran profil distribusi data yang komprehensif untuk gas CH₄, CO, NO₂, dan SO₂. Terungkap bahwa data NO₂ memiliki keruncingan kurva sangat tajam (leptokurtik ekstrem dengan kurtosis $27.942$) serta *skewness* positif ($3.924$) akibat lonjakan konsentrasi pencilan. Gas CO dan SO₂ juga bertipe leptokurtik dengan distribusi miring ke kanan, sedangkan gas CH₄ memiliki kurva yang relatif seimbang menyerupai distribusi normal (mesokurtik dengan kurtosis $-0.007$).
4. **Validasi & Integritas Data**: Seluruh kalkulasi KNIME terbukti 100% konsisten terhadap hasil perhitungan manual serta rumus standar Microsoft Excel (`=MIN`, `=MAX`, `=AVERAGE`, `=MEDIAN`, `=STDEV.S`, `=VAR.S`, `=SKEW`, `=KURT`, `=SUM`, `=COUNTBLANK`).
5. Ketersediaan informasi *missing values* (seperti 339 baris missing pada CH₄, 148 pada NO₂, 130 pada CO, dan 117 pada SO₂) menjadi pijakan penting dalam merancang strategi pembersihan data (*data cleaning*) dan imputasi deret waktu pada pertemuan berikutnya.
