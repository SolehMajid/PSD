# Pemrosesan Deret Waktu 4 Polutan Udara (Pertemuan 4)

Dokumentasi ini menyajikan alur pemrosesan data deret waktu (*time series*) untuk **4 parameter polutan udara utama** di Kabupaten Bangkalan: **Metana ($\text{CH}_4$)**, **Karbon Monoksida ($\text{CO}$)**, **Nitrogen Dioksida ($\text{NO}_2$)**, dan **Sulfur Dioksida ($\text{SO}_2$)**. 

Materi pada pertemuan ini merupakan **kelanjutan langsung dari Pertemuan ke-3**. Jika pada Pertemuan 3 pengolahan data difokuskan secara mendalam pada 1 jenis polutan tunggal (CO), maka pada Pertemuan 4 pipeline pemrosesan diperluas untuk menangani **4 polutan sekaligus** secara komparatif dan terstruktur melalui tahapan:
1. **Deteksi Outlier Bertahap dengan Metode Iterative Z-Score** (disertai daftar lengkap nilai pencilan).
2. **Perbandingan Komparatif Metode Z-Score vs Metode IQR**.
3. **Penambalan Missing Values Menggunakan Interpolasi Linear**.
4. **Hasil Ekstraksi 68 Fitur Runtun Waktu TSFEL untuk 4 Polutan** (langsung menyajikan matriks hasil tanpa pengulangan rumus teoritis).

Dataset yang digunakan bersumber dari rekaman satelit Sentinel-5P Level 2 (`data/csv/Hasil Polutan.csv`) pada rentang pengamatan **365 hari pertama** (24 Agustus 2025 s.d. 23 Agustus 2026).

---

## 1. Profil Data Awal 4 Polutan (Hari 1 – 365)

Sebelum pembersihan dilakukan, karakteristik ketersediaan data pada masing-masing sensor polutan dianalisis:

| Polutan | Nama Senyawa | Total Hari | Hari Terisi (Valid) | Persentase Valid | Missing Values (NaN) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **CH4** | Metana (*Methane*) | 365 hari | 27 hari | 7.40% | 338 hari (92.60%) |
| **CO** | Karbon Monoksida | 365 hari | 236 hari | 64.66% | 129 hari (35.34%) |
| **NO2** | Nitrogen Dioksida | 365 hari | 218 hari | 59.73% | 147 hari (40.27%) |
| **SO2** | Sulfur Dioksida | 365 hari | 249 hari | 68.22% | 116 hari (31.78%) |

> **Catatan Lapangan**: Tingginya nilai kosong pada polutan tertentu (khususnya $\text{CH}_4$) diakibatkan oleh keterbatasan sudut orbit satelit dan persyaratan kualitas piksel bebas awan tebal (*cloud fraction threshold*).

---

## 2. Deteksi Outlier Bertahap Menggunakan Metode Z-Score

### 2.1 Konsep Singkat Iterative Z-Score
Skor Z menyatakan jarak nilai observasi ($x$) terhadap rata-rata sampel ($\mu$) dalam satuan simpangan baku ($\sigma$):

$$Z = \frac{x - \mu}{\sigma}$$

Ambang batas yang digunakan adalah aturan **3-Sigma ($|Z| > 3.0$)**, di mana data di luar rentang $[\mu - 3\sigma, \mu + 3\sigma]$ diklasifikasikan sebagai pencilan ekstrem. Deteksi dilakukan secara **iteratif (bertahap)** agar pencilan raksasa tidak membiaskan nilai $\sigma$ yang dapat menyamarkan pencilan sekunder (*masking effect*).

### 2.2 Source Code Penting: Algoritma Iterative Z-Score
Berikut adalah implementasi kode esensial untuk mendeteksi outlier secara bertahap pada masing-masing polutan:

```python
import numpy as np
import pandas as pd

def detect_outliers_zscore(df, pollutants, threshold=3.0):
    all_outliers = []
    for pol in pollutants:
        df_iter = df.copy()
        iteration = 1
        while True:
            valid_s = df_iter[pol].dropna()
            mean, std = valid_s.mean(), valid_s.std()
            z_scores = (valid_s - mean) / std
            outliers = valid_s[z_scores.abs() > threshold]
            
            if len(outliers) == 0:
                break  # Konvergen, tidak ada outlier tersisa
            
            for idx, val in outliers.items():
                all_outliers.append({
                    'Polutan': pol, 'Hari ke-': idx + 1, 'Tanggal': df.loc[idx, 'tanggal'],
                    'Nilai Polutan': val, 'Z-Score': z_scores[idx], 'Iterasi': f'Tahap {iteration}'
                })
                df_iter.loc[idx, pol] = np.nan  # Hapus sementara untuk iterasi berikutnya
            iteration += 1
    return pd.DataFrame(all_outliers)
```

### 2.3 Visualisasi & Rekapitulasi Deteksi Outlier Z-Score
Dari proses deteksi di atas, ditemukan sebanyak **23 titik data outlier** pada ke-4 polutan udara:

```{figure} ../assets/images/images_pertemuan-4/1.deteksi_outlier_zscore_4polutan.png
:width: 100%
:align: center

Visualisasi Deret Waktu 4 Polutan dan Sebaran Titik Outlier Berdasarkan Ambang Batas Z-Score (|Z| > 3.0).
```

*Tabel Rekapitulasi Deteksi Z-Score Per Polutan:*

| Polutan | Data Valid Awal | Outlier Ditemukan | Persentase Outlier | Data Valid Bersih |
| :---: | :---: | :---: | :---: | :---: |
| **CH4** | 27 | **0** | 0.00% | 27 |
| **CO** | 236 | **3** | 1.27% | 233 |
| **NO2** | 218 | **15** | 6.88% | 203 |
| **SO2** | 249 | **5** | 2.01% | 244 |
| **Total** | **730** | **23** | **3.15%** | **707** |

### 2.4 Daftar Lengkap Nilai Data Outlier yang Terdeteksi
### 2.4 Karakteristik Titik Outlier Kunci yang Terdeteksi

Dari 23 titik outlier yang teridentifikasi, berikut adalah ringkasan karakteristik pencilan utama untuk masing-masing polutan:

| Polutan | Jumlah Outlier | Tanggal Kejadian Menonjol | Nilai Ekstrem | Rata-rata Normal ($\\mu$) | Arah & Karakteristik Pencilan |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **CH4** | **0 titik** | - | - | .45\\text{ ppb}$ | Tidak ditemukan outlier (data homogen pada 27 hari valid) |
| **CO** | **3 titik** | 2025-10-07 (Hari 45) | .0442$ | .0288$ | Lonjakan tajam konsentrasi gas CO ( = +4.84$) |
| **NO2** | **15 titik** | 2026-05-28 (Hari 278) | .000246$ | .000036$ | Puncak lonjakan ekstrem gas nitrogen dioksida ( = +8.77$) |
| **SO2** | **5 titik** | 2025-10-18 & 2026-05-25 | $-0.000518$ s.d. $+0.000808$ | .000058$ | Terdeteksi pencilan atas ( > +3$) dan anomali negatif di bawah nol |

> **Catatan**: Seluruh 23 data outlier di atas dihapus dan diubah menjadi NaN agar tidak membiaskan proses interpolasi. Rincian tanggal dan nilai ke-23 titik outlier tersimpan lengkap di berkas data/csv/pertemuan-4-csv/polutan_4_outliers_list.csv.

---

## 3. Perbandingan Komparatif: Metode Z-Score vs Metode IQR

Selain Z-Score, pendekatan non-parametrik yang umum digunakan dalam analisis kualitas udara adalah **Interquartile Range (IQR / Tukey's Fences)**.

### 3.1 Perbedaan Konseptual
1. **Z-Score (Parametrik)**: Berbasis asumsi bahwa data menyebar mengikuti distribusi normal Gaussian. Menggunakan $\mu$ dan $\sigma$ yang rentan ditarik oleh pencilan ekstrem.
2. **IQR (Non-Parametrik)**: Menggunakan nilai persentil posisi data, yaitu Kuartil 1 ($Q_1$) dan Kuartil 3 ($Q_3$). Metode ini kebal (*robust*) terhadap pengaruh anomali ekstrem karena didasarkan pada $IQR = Q_3 - Q_1$ dengan batas aman:
   $$\text{Batas Bawah} = Q_1 - 1.5 \times IQR \quad \text{dan} \quad \text{Batas Atas} = Q_3 + 1.5 \times IQR$$

### 3.2 Source Code Penting: Deteksi Outlier Metode IQR
```python
def detect_outliers_iqr(df, pollutants):
    iqr_outliers = []
    for pol in pollutants:
        s = df[pol].dropna()
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        
        outliers = s[(s < lower_fence) | (s > upper_fence)]
        for idx, val in outliers.items():
            iqr_outliers.append({
                'Polutan': pol, 'Hari ke-': idx + 1, 'Tanggal': df.loc[idx, 'tanggal'],
                'Nilai Polutan': val, 'Q1': q1, 'Q3': q3, 'IQR': iqr
            })
    return pd.DataFrame(iqr_outliers)
```

### 3.3 Visualisasi & Tabel Perbandingan Hasil Deteksi

```{figure} ../assets/images/images_pertemuan-4/2.komparasi_zscore_iqr_4polutan.png
:width: 100%
:align: center

Komparasi Titik Outlier yang Terdeteksi Menggunakan Metode Z-Score vs Metode IQR pada 4 Polutan.
```

*Tabel Komparasi Jumlah Deteksi Outlier:*

| Metode Deteksi | Tipe Statistik | CH4 | CO | NO2 | SO2 | Total Outlier | Karakteristik Utama |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Iterative Z-Score ($3\sigma$)** | Parametrik | 0 | 3 | 15 | 5 | **23** | Menargetkan pencilan yang sangat ekstrem secara probabilistik ($<0.27\%$). |
| **IQR (Pagar $1.5\times IQR$)** | Non-Parametrik | 1 | 4 | 15 | 10 | **30** | Lebih sensitif pada sebaran asimetris (*skewed*), menangkap lebih banyak titik di ekor bawah $\text{SO}_2$ & $\text{CO}$. |

> **Kesimpulan Perbandingan**: Metode IQR mendeteksi **30 outlier** (7 titik lebih banyak dari Z-Score). Hal ini terjadi karena sebaran gas $\text{SO}_2$ memiliki keruncingan tinggi (*leptokurtic*) dengan nilai-nilai mendekati nol sehingga pagar IQR menjadi lebih ketat. Namun, untuk menjaga data valid pengamatan satelit agar tidak terlalu banyak terbuang, **hasil deteksi Z-Score (23 outlier)** dipilih sebagai acuan utama untuk tahap penambalan nilai kosong.

---

## 4. Penambalan Missing Value (Imputasi Linear)

### 4.1 Mengapa Memilih Interpolasi Linear?
Setelah 23 titik outlier digantikan dengan nilai kosong (`NaN`), data harus dilengkapi kembali agar menjadi deret kontinu 365 hari penuh tanpa celah. 

Pada fenomena atmosfer:
- **Pengisian Rata-rata (Mean Imputation)** tidak cocok karena menciptakan pola garis lurus datar (*flat line*) yang menghilangkan dinamika musim.
- **Forward Fill / Backward Fill** menciptakan undakan tangga (*step function*) yang tidak alami.
- **Interpolasi Linear** merupakan metode paling representatif karena menghubungkan dua titik pengamatan yang valid sebelum ($t_0$) dan sesudahnya ($t_1$) dengan gradien garis lurus, menjaga kelancaran kurva deret waktu secara proporsional:
  $$x_t = x_{t_0} + \frac{t - t_0}{t_1 - t_0} (x_{t_1} - x_{t_0})$$

### 4.2 Source Code Penting: Imputasi Linear Bertahap
```python
# Menerapkan interpolasi linear dan penanganan titik batas (boundary fill)
df_clean = pd.read_csv("data/csv/pertemuan-4-csv/polutan_4_clean.csv")
df_imputed = df_clean.copy()

for pol in ['CH4', 'CO', 'NO2', 'SO2']:
    # Interpolasi linear untuk titik interior + backward/forward fill untuk batas ujung
    df_imputed[pol] = df_clean[pol].interpolate(method='linear').bfill().ffill()

# Simpan dataset final bersih sempurna (365 hari penuh, 0 NaN)
df_imputed.to_csv("data/csv/pertemuan-4-csv/polutan_4_final_clean.csv", index=False)
```

### 4.3 Visualisasi & Hasil Rekapitulasi Imputasi

```{figure} ../assets/images/images_pertemuan-4/3.hasil_imputasi_linear_4polutan.png
:width: 100%
:align: center

Hasil Rekonstruksi Deret Waktu 365 Hari Penuh 4 Polutan Setelah Dilakukan Penambalan Missing Value.
```

*Tabel Hasil Penambalan Missing Value 4 Polutan (365 Hari Lengkap):*

| Polutan | Total Baris | Data Valid Awal | Outlier Dibuang | Data Asli Valid | Data Ditambal (Interpolasi) | Sisa NaN (Akhir) | Status Kelengkapan |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH4** | 365 hari | 27 | 0 | 27 hari | **338 hari** | **0** | **100% Sempurna** |
| **CO** | 365 hari | 236 | 3 | 233 hari | **132 hari** | **0** | **100% Sempurna** |
| **NO2** | 365 hari | 218 | 15 | 203 hari | **162 hari** | **0** | **100% Sempurna** |
| **SO2** | 365 hari | 249 | 5 | 244 hari | **121 hari** | **0** | **100% Sempurna** |

---

## 5. Ekstraksi Fitur Runtun Waktu TSFEL (Hasil 4 Polutan)

Dataset final yang telah bebas dari anomali dan bernilai utuh 365 hari (`polutan_4_final_clean.csv`) diekstraksi menggunakan pustaka **TSFEL (Time Series Feature Extraction Library)**. 

Seluruh 68 fitur runtun waktu terstandarisasi yang mencakup 4 domain keilmuan (*Statistical*, *Temporal*, *Spectral*, dan *Fractal*) berhasil diekstrak dan disusun ke dalam format **Matriks 4 Baris × 69 Kolom** (1 kolom nama `Polutan` + 68 kolom fitur numerik `f1_abs_energy` s/d `f68_zero_cross`) pada berkas `fitur_68_4_polutan.csv`.

### 5.1 Source Code Penting: Ekstraksi Fitur TSFEL 4 Polutan
```python
import tsfel
import pandas as pd

# 1. Konfigurasi seluruh fitur aktif (68 fitur terstandarisasi)
cfg = tsfel.get_features_by_domain()
for domain in cfg:
    for feat in cfg[domain]:
        cfg[domain][feat]['use'] = 'yes'

# 2. Ekstraksi fitur untuk masing-masing polutan
df_clean = pd.read_csv("data/csv/pertemuan-4-csv/polutan_4_final_clean.csv")
results = []

for pol in ['CH4', 'CO', 'NO2', 'SO2']:
    # Ekstraksi matriks TSFEL
    feat_df = tsfel.time_series_features_extractor(cfg, df_clean[pol], fs=1, verbose=0)
    feat_df.insert(0, 'Polutan', pol)
    results.append(feat_df)

# 3. Penggabungan menjadi satu matriks horizontal (4 x 69)
df_all_features = pd.concat(results, ignore_index=True)
df_all_features.to_csv("data/csv/pertemuan-4-csv/fitur_68_4_polutan.csv", index=False)
```

### 5.2 Visualisasi Komparasi Karakteristik Fitur Kunci

```{figure} ../assets/images/images_pertemuan-4/4.komparasi_fitur_kunci_4polutan.png
:width: 90%
:align: center

Perbandingan Fitur Kunci (Pusat Konsentrasi, Variabilitas, Kompleksitas Sinyal, dan Memori Jangka Panjang) Antar 4 Polutan.
```

### 5.3 Rangkuman Fitur Kunci 4 Polutan Berdasarkan Domain

Daripada menampilkan seluruh 68 kolom angka mentah, tabel berikut merangkum fitur-fitur paling esensial yang mewakili 4 domain keilmuan TSFEL:

| Domain Fitur | Parameter Fitur TSFEL | CH4 (Metana) | CO (Karbon Monoksida) | NO2 (Nitrogen Dioksida) | SO2 (Sulfur Dioksida) | Makna Analisis |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **Statistik** | Rata-rata (7_calc_mean) | .45\\text{ ppb}$ | .0286\\text{ mol/m}^2$ | .36 \\times 10^{-5}\\text{ mol/m}^2$ | .50 \\times 10^{-5}\\text{ mol/m}^2$ | Skala konsentrasi gas tipikal |
| **Statistik** | Simpangan Baku (10_calc_std) | .40$ | .0026$ | .32 \\times 10^{-5}$ | .69 \\times 10^{-4}$ | Derajat variabilitas harian polutan |
| **Statistik** | Konsentrasi Puncak (6_calc_max)| .85$ | .0361$ | .86 \\times 10^{-5}$ | .54 \\times 10^{-4}$ | Titik tertinggi konsentrasi polutan |
| **Temporal** | Panjang Lintasan (13_distance)| .12$ | .00$ | .00$ | .00$ | Total akumulasi perubahan deret waktu |
| **Temporal** | Titik Balik Arah (40_neg_turn) | $ kali | $ kali | $ kali | $ kali | Dinamika pembalikan tren fluktuasi |
| **Temporal** | Perlintasan Garis Nol (68_zero_cross) | $ | $ | $ | $ kali | Frekuensi osilasi sinyal di sekitar nol |
| **Spektral** | Daya Spektrum Maks (29_max_power)| .2513$ | .1816$ | .5314$ | .2134$ | Puncak kerapatan energi frekuensi Fourier |
| **Spektral** | Pusat Spektral (49_spectral_centroid)| .4722$ | .9292$ | .4779$ | .5727$ | Distribusi titik berat spektrum frekuensi |
| **Fraktal** | Hurst Exponent (23_hurst_exp)| **.9279$** | **.7644$** | **.8698$** | **.7020$** | Sifat memori jangka panjang ( > 0.5$) |
| **Fraktal** | Dimensi Higuchi (20_higuchi_dim)| .7022$ | .9118$ | .7804$ | .9658$ | Tingkat kompleksitas bentuk kurva |

> **Catatan**: Matriks lengkap berisi seluruh 68 fitur TSFEL untuk ke-4 polutan tersimpan pada berkas data/csv/pertemuan-4-csv/fitur_68_4_polutan.csv.


### 5.4 Interpretasi Fisis Hasil Fitur 4 Polutan
1. **Skala Besaran Emisi (`f7_calc_mean` & `f1_abs_energy`)**:
   - $\text{CH}_4$ memiliki nilai absolut energi dan konsentrasi skala ribuan ($1880\text{ ppb}$), sedangkan $\text{CO}$, $\text{NO}_2$, dan $\text{SO}_2$ berada pada skala konsentrasi gas mikro ($\text{mol/m}^2$).
2. **Keteraturan & Persistensi Tren (`f23_hurst_exponent`)**:
   - Seluruh polutan memiliki nilai Hurst Exponent $> 0.5$ ($0.70$ s.d. $0.93$), yang membuktikan bahwa dinamika polusi udara di Kabupaten Bangkalan memiliki sifat **persistensi kuat** (memiliki ketergantungan temporal jangka panjang, di mana tren kenaikan atau penurunan cenderung berlanjut).
3. **Fluktuasi Dinamis & Pembalikan Arah (`f40_neg_turn`, `f44_pos_turn`, `f68_zero_cross`)**:
   - Gas $\text{SO}_2$ dan $\text{CO}$ menunjukkan dinamika titik balik paling tinggi ($>65$ kali berbalik arah per tahun), menandakan respon yang sangat dinamis terhadap perubahan pola lalu lintas harian serta angin laut di wilayah pesisir Bangkalan.
   - $\text{SO}_2$ mencatatkan $109$ kali perlintasan garis nol (`f68_zero_cross`), selaras dengan nilai latar belakang sensor yang berosilasi di sekitar angka nol.

---

## 6. Ringkasan & Kesiapan Analisis Lanjutan

Dengan selesainya alur pengolahan pada Pertemuan 4 ini:
1. **Dataset Bersih Terpadu**: Berkas `polutan_4_final_clean.csv` telah terbebas $100\%$ dari outlier dan missing value untuk 365 hari pengamatan.
2. **Matriks Fitur Terstandarisasi**: Berkas `fitur_68_4_polutan.csv` menyediakan representasi numerik ringkas (4 baris × 69 kolom) yang siap diintegrasikan dengan dataset mahasiswa lain atau digunakan langsung sebagai variabel input (*feature space*) untuk pemodelan *Machine Learning* dan *Clustering* kualitas udara.

---

## 7. Analisis Lanjutan: Melakukan Cluster Menggunakan K-Means Menggunakan KNIME

Sebagai tindak lanjut dari integrasi matriks fitur runtun waktu 4 polutan yang dikompilasi dari 19 mahasiswa / wilayah pengamatan, dilakukan pemodelan klaster menggunakan **KNIME Analytics Platform** dengan algoritma **K-Means Clustering**.

Pada pengujian ini, dianalisis dua pendekatan pemodelan:
1. **Menggunakan PCA dengan 19 Dimensi**: Mereduksi 272 fitur awal menjadi 18 komponen utama sebelum K-Means.
2. **Tanpa PCA (272 Fitur Penuh)**: Memasukkan seluruh 272 fitur TSFEL secara langsung ke K-Means tanpa reduksi dimensi.

Dokumentasi lengkap, arsitektur workflow KNIME, tabel hasil pengelompokan 19 data, analisis nilai centroid klaster, serta evaluasi komparatif disajikan pada halaman berikut:

👉 **[Melakukan Cluster menggunakan K-means menggunakan Knime](Melakukan%20Cluster%20menggunakan%20K-means%20menggunakan%20Knime.md)**
