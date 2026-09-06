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

Hasil eksekusi node ini menghasilkan tabel data dengan **366 baris (rows)** dan **6 kolom (columns)**:
- `id` (Integer)
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

Workflow KNIME (`PostgreSQL Connector` -> `DB Query Reader` -> `Statistics`) Beserta Tabel Ringkasan Statistik.
```

### 3.1 Tabel Ringkasan Statistik Deskriptif (KNIME)

Berdasarkan hasil eksekusi node **Statistics** pada KNIME, diperoleh ringkasan data sebagai berikut:

| Column | Min | Max | Mean | Std. deviation | Variance | Skewness | Kurtosis | Overall sum | No. missings | No. NaNs | No. +$\infty$ | No. -$\infty$ | Median | Row count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **id** | 1 | 366 | 183.5 | 105.799 | 11,193.5 | 0 | -1.2 | 67,161 | 0 | 0 | 0 | 0 | *(?)* | 366 |
| **ch4** | 1,632.623 | 1,934.86 | 1,868.202 | 43.644 | 1,904.78 | -2.431 | 10.171 | 149,456.129 | 286 | 0 | 0 | 0 | *(?)* | 366 |
| **co** | 0.02 | 0.044 | 0.029 | 0.003 | 0 | 0.887 | 2.65 | 7.843 | 92 | 0 | 0 | 0 | *(?)* | 366 |
| **no2** | 0 | 0 | 0 | 0 | 0 | 2.113 | 14.554 | 0.007 | 77 | 0 | 0 | 0 | *(?)* | 366 |
| **so2** | -0.001 | 0.001 | 0 | 0 | 0 | -1.241 | 15.298 | 0.012 | 49 | 0 | 0 | 0 | *(?)* | 366 |

> **Catatan Penting Mengenai Nilai Median di KNIME:**
> Pada gambar antarmuka KNIME di atas, kolom **Median** ditandai dengan ikon tanda tanya merah `(?)`. Hal ini terjadi karena secara *default*, opsi dialog konfigurasi **"Calculate median values (computationally expensive)"** dalam keadaan **tidak dicentang (unchecked)**. 
> 
> Penghitungan median memerlukan proses pengurutan (*sorting*) seluruh baris data dalam memori, yang pada dataset berskala besar (*big data*) membutuhkan alokasi memori dan waktu komputasi yang tinggi. Oleh karena itu, KNIME menjadikannya opsi opsional. Pada modul ini, nilai median tetap dihitung secara presisi melalui validasi perhitungan manual dan Microsoft Excel.

---

### 3.2 Penjelasan Komprehensif Masing-Masing Properti Statistik

Berikut adalah penjelasan teoretis, fungsi, dan interpretasi dari setiap properti statistik yang dihasilkan oleh KNIME:

#### 1. Column
- **Definisi**: Nama pengenal atribut atau variabel yang sedang dianalisis dalam tabel data.
- **Fungsi**: Membedakan dimensi pengamatan, misalnya `id` sebagai indeks baris, serta `ch4`, `co`, `no2`, dan `so2` sebagai variabel konsentrasi polutan atmosfer.

#### 2. Min (Minimum)
- **Definisi**: Nilai numerik terkecil di antara seluruh baris data valid pada kolom tertentu.
- **Formula**:
  $$\text{Min} = \min(x_1, x_2, \dots, x_n)$$
- **Interpretasi**: Menunjukkan batas bawah pengamatan polutan. Misalnya pada CH₄, nilai minimum tercatat adalah $1\,632.623\ \text{ppb}$, sedangkan pada SO₂ terdapat nilai negatif ($-0.001\ \text{mol/m}^2$) akibat ketidakpastian koreksi radiometrik sensor satelit pada konsentrasi gas yang sangat tipis.

#### 3. Max (Maximum)
- **Definisi**: Nilai numerik terbesar di antara seluruh baris data valid pada kolom tertentu.
- **Formula**:
  $$\text{Max} = \max(x_1, x_2, \dots, x_n)$$
- **Interpretasi**: Mengindikasikan puncak konsentrasi tertinggi yang pernah tercatat selama rentang waktu satu tahun (misalnya nilai maksimum CH₄ mencapai $1\,934.86\ \text{ppb}$).

#### 4. Mean (Rata-rata Hitung / Aritmetika)
- **Definisi**: Titik pusat massa atau nilai rerata aritmetika dari seluruh sampel data yang valid.
- **Formula**:
  $$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$
- **Interpretasi**: Memberikan estimasi nilai ekspektasi tipikal dari suatu polutan sehari-hari di Kabupaten Bangkalan. Nilai mean CH₄ adalah $1\,868.202$, dan mean CO adalah $0.029$.

#### 5. Median (Nilai Tengah)
- **Definisi**: Nilai yang membagi distribusi data menjadi dua bagian yang sama besar (50% data di bawah median dan 50% data di atas median) setelah seluruh data diurutkan dari terkecil ke terbesar.
- **Formula**:
  $$\text{Median} = \begin{cases} x_{\left(\frac{n+1}{2}\right)}, & \text{jika } n \text{ ganjil} \\[6pt] \frac{x_{\left(\frac{n}{2}\right)} + x_{\left(\frac{n}{2} + 1\right)}}{2}, & \text{jika } n \text{ genap} \end{cases}$$
- **Interpretasi**: Berbeda dengan mean, median bersifat *robust* (kebal terhadap pengaruh nilai ekstrem atau pencilan/*outliers*). Jika median dan mean memiliki perbedaan signifikan, hal itu menandakan adanya distribusi yang miring (*skewed*).

#### 6. Std. Deviation (Standar Deviasi / Simpangan Baku)
- **Definisi**: Ukuran dispersi atau variabilitas yang mengukur seberapa jauh nilai-nilai data individual menyebar dari nilai rata-ratanya ($\bar{x}$).
- **Formula (Sampel)**:
  $$s = \sqrt{\frac{1}{n - 1} \sum_{i=1}^{n} (x_i - \bar{x})^2}$$
- **Interpretasi**: Semakin besar nilai standar deviasi, semakin bervariasi atau fluktuatif konsentrasi gas polutan tersebut. Standar deviasi CH₄ sebesar $43.644$ menunjukkan fluktuasi konsentrasi yang cukup dinamis sepanjang tahun.

#### 7. Variance (Variansi / Ragam)
- **Definisi**: Rata-rata kuadrat deviasi nilai data dari nilai rata-ratanya, yang merupakan kuadrat dari standar deviasi ($s^2$).
- **Formula**:
  $$s^2 = \frac{1}{n - 1} \sum_{i=1}^{n} (x_i - \bar{x})^2$$
- **Interpretasi**: Menggambarkan besaran penyebaran kuadratik data. Karena satuannya adalah kuadrat dari satuan asli data, standar deviasi biasanya lebih mudah diinterpretasikan secara langsung dibandingkan variansi.

#### 8. Skewness (Kemiringan Distribusi)
- **Definisi**: Derajat ketidaksimetrisan (*asymmetry*) dari kurva distribusi probabilitas data di sekitar nilai rata-ratanya.
- **Formula (Sample Skewness / Fisher-Pearson)**:
  $$G_1 = \frac{n}{(n - 1)(n - 2)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^3$$
- **Interpretasi**:
  - **Skewness $\approx 0$**: Distribusi simetris (membentuk kurva lonceng normal), contohnya pada kolom `id` ($0$).
  - **Skewness $> 0$ (Positif / Right-skewed)**: Ekor distribusi memanjang ke arah kanan (nilai besar), contohnya pada `co` ($0.887$) dan `no2` ($2.113$). Sebagian besar data terkumpul di nilai rendah dengan sedikit lonjakan konsentrasi ekstrem.
  - **Skewness $< 0$ (Negatif / Left-skewed)**: Ekor distribusi memanjang ke arah kiri (nilai kecil), contohnya pada `ch4` ($-2.431$) dan `so2` ($-1.241$).

#### 9. Kurtosis (Keruncingan Distribusi)
- **Definisi**: Ukuran ketajaman puncak (*peakedness*) dan ketebalan ekor (*tailedness*) distribusi frekuensi data dibandingkan dengan distribusi normal standar.
- **Formula (Sample Excess Kurtosis)**:
  $$G_2 = \frac{n(n + 1)}{(n - 1)(n - 2)(n - 3)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^4 - \frac{3(n - 1)^2}{(n - 2)(n - 3)}$$
- **Interpretasi**:
  - **Kurtosis $> 0$ (Leptokurtik)**: Distribusi memiliki puncak yang sangat runcing dan ekor tebal (*heavy tails*), yang mengindikasikan adanya pencilan (*outliers*) yang signifikan. Polutan `so2` ($15.298$), `no2` ($14.554$), dan `ch4` ($10.171$) bertipe leptokurtik kuat.
  - **Kurtosis $\approx 0$ (Mesokurtik)**: Bentuk kurva serupa dengan distribusi normal standar.
  - **Kurtosis $< 0$ (Platikurtik)**: Distribusi berbentuk landai atau mendatar dengan ekor tipis, seperti pada kolom `id` ($-1.2$).

#### 10. Overall Sum (Jumlah Total)
- **Definisi**: Akumulasi penjumlahan aritmetika dari seluruh data numerik yang valid pada kolom yang bersangkutan.
- **Formula**:
  $$\text{Overall Sum} = \sum_{i=1}^{n} x_i$$
- **Interpretasi**: Total kumulatif nilai sampel. Contohnya pada CH₄ bernilai $149\,456.129$, dan jumlah total baris `id` adalah $67\,161$.

#### 11. No. Missings (Jumlah Nilai Hilang)
- **Definisi**: Jumlah baris data yang bernilai kosong (`null`), di mana sensor tidak merekam data pengukuran pada tanggal tersebut.
- **Formula**:
  $$\text{No. Missings} = N_{\text{total}} - n_{\text{valid}}$$
- **Interpretasi**: Kualitas data atmosfer satelit optik sangat dipengaruhi oleh kondisi atmosfer. Kolom `ch4` memiliki $286$ data *missing*, `co` memiliki $92$, `no2` memiliki $77$, dan `so2` memiliki $49$. Informasi ini menjadi landasan penting untuk tahap prapemrosesan (*imputasi*) berikutnya.

#### 12. No. NaNs (Not a Number)
- **Definisi**: Jumlah sel data yang berisi nilai *NaN*, yaitu simbol khusus komputasi numerik untuk nilai yang tidak terdefinisi secara matematis (misalnya hasil pembagian dengan nol $0/0$ atau akar bilangan negatif).
- **Interpretasi**: Pada dataset ini nilainya adalah $0$ untuk seluruh kolom, membuktikan tidak ada kegagalan komputasi numerik saat agregasi spasial.

#### 13. No. +$\infty$ (No. +unlimited / Positive Infinity)
- **Definisi**: Jumlah sel yang bernilai positif tak hingga ($+\infty$), biasanya muncul dari operasi pembagian nilai positif dengan nol ($x / 0$).
- **Interpretasi**: Bernilai $0$ untuk seluruh kolom (data berada dalam rentang terhingga yang wajar).

#### 14. No. -$\infty$ (No. -unlimited / Negative Infinity)
- **Definisi**: Jumlah sel yang bernilai negatif tak hingga ($-\infty$), biasanya terjadi akibat pembagian nilai negatif dengan nol ($-x / 0$) atau nilai logaritma dari nol ($\ln(0)$).
- **Interpretasi**: Bernilai $0$ untuk seluruh kolom.

#### 15. Row Count (Jumlah Total Baris)
- **Definisi**: Total keseluruhan baris pengamatan dalam tabel data, baik yang berisi nilai valid maupun nilai *missing*.
- **Interpretasi**: Bernilai $366$ baris untuk semua kolom, merepresentasikan 366 hari pengamatan (tahun kabisat).

#### 16. Histogram (Distribusi Frekuensi)
- **Definisi**: Representasi grafis berbentuk diagram batang yang memetakan frekuensi kemunculan nilai data ke dalam rentang interval (*bins*) tertentu.
- **Interpretasi**: Memvisualisasikan secara langsung kurva sebaran data, letak konsentrasi data terbanyak, serta keberadaan nilai pencilan di sisi ekor grafik.

---

## 4. Contoh Perhitungan Manual & Verifikasi Rumus Excel

Untuk memverifikasi kebenaran perhitungan statistik yang dihasilkan oleh KNIME, dilakukan pengujian ulang menggunakan lembar kerja **Microsoft Excel**. Hasil verifikasi membuktikan kecocokan penuh antara output KNIME dan rumus Excel.

```{figure} ../assets/images/images_pertemuan-2/perhitungan-manual_exel.png
:width: 100%
:align: center

Hasil Validasi Statistik Deskriptif dan Visualisasi Histogram Menggunakan Microsoft Excel.
```

> 📥 **File Dataset CSV:**
> Data gabungan konsentrasi polutan yang digunakan dalam proses validasi dan perhitungan Excel di atas dapat diakses atau diunduh pada tautan berikut: [data/csv/Hasil Polutan.csv](../data/csv/Hasil%20Polutan.csv)

### 4.1 Tabel Validasi Komparasi Data Excel

Berikut adalah tabel hasil komputasi presisi tinggi yang dihasilkan pada lembar kerja Microsoft Excel untuk keempat gas polutan:

| Kolom Polutan | MIN | MAX | MEAN | STD DEVIATION | VARIANCE | SKEWNESS | KURTOSIS | OVERALL SUM | NO MISS | NO NaNs | No +oos | No -oos | Median | Row Count (Valid/Total) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH4** | 1632.623413 | 1934.859901 | 1868.201617 | 43.64379091 | 1904.780485 | -2.4306975 | 10.17082 | 149456.1293 | 286 | 0 | 0 | 0 | 1879.0479 | 80 / 366 |
| **CO** | 0.020487351 | 0.043854946 | 0.0286226 | 0.002866045 | 8.21421E-06 | 0.8873338 | 2.649587 | 7.842592315 | 92 | 0 | 0 | 0 | 0.028381 | 274 / 366 |
| **NO2** | 1.81E-06 | 1.04E-04 | 2.45E-05 | 9.76E-06 | 9.53E-11 | 2.11 | 14.6 | 7.08E-03 | 77 | 0 | 0 | 0 | 2.35E-05 | 289 / 366 |
| **SO2** | -0.001007149 | 0.000619241 | 3.65828E-05 | 0.000128303 | 1.64617E-08 | -1.2405101 | 15.29753 | 0.01159676 | 49 | 0 | 0 | 0 | 0.0000329 | 317 / 366 |

---

### 4.2 Simulasi Perhitungan Manual Langkah Demi Langkah (Step-by-Step)

Agar mekanisme kalkulasi statistik deskriptif dapat dipahami secara transparan, mari kita lakukan simulasi perhitungan manual menggunakan sampel data kecil ($n = 5$) yang diambil secara acak dari data terurut polutan CH₄:

$$X = \{ 1837.93,\ 1847.77,\ 1878.62,\ 1882.55,\ 1883.38 \}$$

Jumlah sampel valid: $n = 5$.

---

#### 1. Perhitungan Minimum (Min)
Mencari elemen data dengan nilai terkecil pada himpunan sampel:
$$\text{Min} = \min(1837.93,\ 1847.77,\ 1878.62,\ 1882.55,\ 1883.38) = \mathbf{1837.93}$$

---

#### 2. Perhitungan Maksimum (Max)
Mencari elemen data dengan nilai terbesar pada himpunan sampel:
$$\text{Max} = \max(1837.93,\ 1847.77,\ 1878.62,\ 1882.55,\ 1883.38) = \mathbf{1883.38}$$

---

#### 3. Perhitungan Mean ($\bar{x}$)
Menjumlahkan seluruh elemen data, kemudian membaginya dengan ukuran sampel ($n$):
$$\sum_{i=1}^{5} x_i = 1837.93 + 1847.77 + 1878.62 + 1882.55 + 1883.38 = 9330.25$$
$$\bar{x} = \frac{\sum_{i=1}^{5} x_i}{n} = \frac{9330.25}{5} = \mathbf{1866.05}$$

---

#### 4. Perhitungan Median
Karena data sudah terurut dan ukuran sampel $n = 5$ bernilai ganjil:
$$\text{Posisi Median} = \frac{n + 1}{2} = \frac{5 + 1}{2} = 3$$
$$\text{Median} = X_{(3)} = \mathbf{1878.62}$$

*(Jika $n$ genap, median dihitung dari rata-rata dua nilai tengah: $\frac{X_{(n/2)} + X_{(n/2 + 1)}}{2}$)*

---

#### 5. Perhitungan Variansi ($s^2$) & Standar Deviasi ($s$)
Dibuat tabel deviasi terhadap nilai rata-rata ($\bar{x} = 1866.05$):

| $i$ | $x_i$ | $(x_i - \bar{x})$ | $(x_i - \bar{x})^2$ | $(x_i - \bar{x})^3$ | $(x_i - \bar{x})^4$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1837.93 | $-28.12$ | $790.7344$ | $-22235.45$ | $625260.9$ |
| 2 | 1847.77 | $-18.28$ | $334.1584$ | $-6108.42$ | $111661.8$ |
| 3 | 1878.62 | $+12.57$ | $158.0049$ | $+1986.12$ | $24965.5$ |
| 4 | 1882.55 | $+16.50$ | $272.2500$ | $+4492.13$ | $74120.1$ |
| 5 | 1883.38 | $+17.33$ | $300.3289$ | $+5204.70$ | $90197.4$ |
| **Total ($\sum$)** | **9330.25** | **0.00** | **1855.4766** | **-16660.92** | **926205.7** |

**Variansi Sampel ($s^2$):**
$$s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1} = \frac{1855.4766}{5 - 1} = \frac{1855.4766}{4} = \mathbf{463.869}$$

**Standar Deviasi Sampel ($s$):**
$$s = \sqrt{s^2} = \sqrt{463.869} = \mathbf{21.5376}$$

---

#### 6. Perhitungan Skewness ($G_1$)
Menggunakan rumus Fisher-Pearson sample skewness:
$$G_1 = \frac{n}{(n - 1)(n - 2)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^3 = \frac{n}{(n - 1)(n - 2) \cdot s^3} \sum_{i=1}^{n} (x_i - \bar{x})^3$$
Substitusi nilai yang diperoleh:
$$s^3 = (21.5376)^3 \approx 9990.66$$
$$\frac{n}{(n - 1)(n - 2)} = \frac{5}{4 \times 3} = \frac{5}{12} \approx 0.4167$$
$$G_1 = 0.4167 \times \frac{-16660.92}{9990.66} = 0.4167 \times (-1.6676) = \mathbf{-0.6949}$$
*(Nilai negatif menunjukkan ekor distribusi memanjang ke sisi kiri / nilai kecil).*

---

#### 7. Perhitungan Kurtosis ($G_2$)
Menggunakan rumus sample excess kurtosis:
$$G_2 = \frac{n(n + 1)}{(n - 1)(n - 2)(n - 3)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^4 - \frac{3(n - 1)^2}{(n - 2)(n - 3)}$$
Substitusi nilai yang diperoleh:
$$s^4 = (463.869)^2 \approx 215174.45$$
$$\sum \left( \frac{x_i - \bar{x}}{s} \right)^4 = \frac{926205.7}{215174.45} \approx 4.3044$$
Faktor pengali pertama:
$$\frac{5 \times 6}{4 \times 3 \times 2} = \frac{30}{24} = 1.25$$
Faktor pengurang kedua:
$$\frac{3 \times (4)^2}{3 \times 2} = \frac{48}{6} = 8.00$$
$$G_2 = (1.25 \times 4.3044) - 8.00 = 5.3805 - 8.00 = \mathbf{-2.6195}$$

---

#### 8. Perhitungan Overall Sum
$$\text{Overall Sum} = \sum_{i=1}^{5} x_i = \mathbf{9330.25}$$

---

#### 9. Perhitungan No. Missings
Jika total baris tabel pengamatan adalah $N = 366$ dan baris yang memiliki nilai numerik valid adalah $n = 80$:
$$\text{No. Missings} = 366 - 80 = \mathbf{286}$$

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
3. **Analisis Statistik Deskriptif**: Node *Statistics* di KNIME memberikan gambaran profil distribusi data yang komprehensif untuk gas CH₄, CO, NO₂, dan SO₂. Diketahui bahwa data CH₄, NO₂, dan SO₂ memiliki nilai kurtosis tinggi (leptokurtik) dengan kemiringan distribusi yang mencerminkan keberadaan lonjakan emisi musiman.
4. **Validasi & Integritas Data**: Seluruh kalkulasi KNIME terbukti 100% konsisten terhadap hasil perhitungan manual serta rumus standar Microsoft Excel (`=MIN`, `=MAX`, `=AVERAGE`, `=MEDIAN`, `=STDEV.S`, `=VAR.S`, `=SKEW`, `=KURT`, `=SUM`, `=COUNTBLANK`).
5. Ketersediaan informasi *missing values* (seperti 286 baris missing pada CH₄ dan 92 pada CO) menjadi pijakan penting dalam merancang strategi pembersihan data (*data cleaning*) dan imputasi deret waktu pada pertemuan berikutnya.
