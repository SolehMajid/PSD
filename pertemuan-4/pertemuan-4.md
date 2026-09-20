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
Berikut adalah rincian seluruh 23 nilai pengamatan yang terdeteksi sebagai anomali:

| No | Polutan | Hari ke- | Tanggal | Nilai Pengamatan | Nilai Rata-rata ($\mu$) | Simpangan Baku ($\sigma$) | Z-Score | Tahap Iterasi | Arah Pencilan |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **NO2** | 31 | 2025-09-23 | $0.000081$ | $0.000033$ | $0.000016$ | $+3.0191$ | Tahap 3 | Pencilan Atas (Tinggi) |
| 2 | **CO** | 32 | 2025-09-24 | $0.037800$ | $0.028718$ | $0.002962$ | $+3.0665$ | Tahap 2 | Pencilan Atas (Tinggi) |
| 3 | **NO2** | 32 | 2025-09-24 | $0.000117$ | $0.000036$ | $0.000024$ | $+3.3918$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 4 | **CO** | 45 | 2025-10-07 | $0.044218$ | $0.028825$ | $0.003181$ | $+4.8395$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 5 | **NO2** | 46 | 2025-10-08 | $0.000080$ | $0.000032$ | $0.000015$ | $+3.2324$ | Tahap 4 | Pencilan Atas (Tinggi) |
| 6 | **SO2** | 56 | 2025-10-18 | $-0.000518$ | $0.000058$ | $0.000190$ | $-3.0303$ | Tahap 2 | Pencilan Bawah (Rendah) |
| 7 | **NO2** | 91 | 2025-11-22 | $0.000074$ | $0.000031$ | $0.000013$ | $+3.1599$ | Tahap 5 | Pencilan Atas (Tinggi) |
| 8 | **NO2** | 109 | 2025-12-10 | $0.000083$ | $0.000033$ | $0.000016$ | $+3.1767$ | Tahap 3 | Pencilan Atas (Tinggi) |
| 9 | **NO2** | 207 | 2026-03-18 | $0.000108$ | $0.000036$ | $0.000024$ | $+3.0252$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 10 | **SO2** | 208 | 2026-03-19 | $0.000669$ | $0.000058$ | $0.000190$ | $+3.2201$ | Tahap 2 | Pencilan Atas (Tinggi) |
| 11 | **NO2** | 229 | 2026-04-09 | $0.000077$ | $0.000032$ | $0.000015$ | $+3.0503$ | Tahap 4 | Pencilan Atas (Tinggi) |
| 12 | **NO2** | 251 | 2026-05-01 | $0.000080$ | $0.000032$ | $0.000015$ | $+3.2257$ | Tahap 4 | Pencilan Atas (Tinggi) |
| 13 | **NO2** | 275 | 2026-05-25 | $0.000083$ | $0.000033$ | $0.000016$ | $+3.1388$ | Tahap 3 | Pencilan Atas (Tinggi) |
| 14 | **SO2** | 275 | 2026-05-25 | $0.000808$ | $0.000066$ | $0.000203$ | $+3.6507$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 15 | **NO2** | 276 | 2026-05-26 | $0.000124$ | $0.000036$ | $0.000024$ | $+3.6987$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 16 | **NO2** | 277 | 2026-05-27 | $0.000076$ | $0.000031$ | $0.000013$ | $+3.3014$ | Tahap 5 | Pencilan Atas (Tinggi) |
| 17 | **NO2** | 278 | 2026-05-28 | $0.000246$ | $0.000036$ | $0.000024$ | $+8.7717$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 18 | **NO2** | 279 | 2026-05-29 | $0.000087$ | $0.000033$ | $0.000017$ | $+3.1946$ | Tahap 2 | Pencilan Atas (Tinggi) |
| 19 | **SO2** | 312 | 2026-07-01 | $0.000690$ | $0.000066$ | $0.000203$ | $+3.0727$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 20 | **CO** | 334 | 2026-07-23 | $0.038510$ | $0.028825$ | $0.003181$ | $+3.0450$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 21 | **NO2** | 334 | 2026-07-23 | $0.000078$ | $0.000032$ | $0.000015$ | $+3.1110$ | Tahap 4 | Pencilan Atas (Tinggi) |
| 22 | **SO2** | 344 | 2026-08-02 | $0.000740$ | $0.000066$ | $0.000203$ | $+3.3188$ | Tahap 1 | Pencilan Atas (Tinggi) |
| 23 | **NO2** | 352 | 2026-08-10 | $0.000097$ | $0.000033$ | $0.000017$ | $+3.7720$ | Tahap 2 | Pencilan Atas (Tinggi) |

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

### 5.3 Tabel Matriks Hasil Fitur Kunci 4 Polutan

Tabel berikut menyajikan seluruh 68 fitur runtun waktu terstandarisasi (`f1` s.d. `f68`) hasil komputasi TSFEL secara lengkap untuk ke-4 polutan udara di Kabupaten Bangkalan:

| Kode Fitur | Nama Fitur TSFEL | Domain | CH4 (Metana) | CO (Karbon Monoksida) | NO2 (Nitrogen Dioksida) | SO2 (Sulfur Dioksida) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| `f1_abs_energy` | Absolute energy | Statistical | 1.2907e+09 | 0.300680 | 4.7529e-07 | 1.1583e-05 |
| `f2_auc` | Area under the curve | Temporal | 6844.8321 | 0.104004 | 0.000122 | 0.000423 |
| `f3_autocorr` | Autocorrelation | Temporal | 17 | 2 | 7 | 2 |
| `f4_average_power` | Average power | Statistical | 3.5459e+08 | 0.082604 | 1.3057e-07 | 3.1821e-06 |
| `f5_calc_centroid` | Centroid | Temporal | 1.8283 | 1.8165 | 1.6994 | 1.8607 |
| `f6_calc_max` | Max | Statistical | 1916.8535 | 0.036134 | 6.8600e-05 | 0.000554 |
| `f7_calc_mean` | Mean | Statistical | 1880.4490 | 0.028584 | 3.3592e-05 | 5.4959e-05 |
| `f8_calc_median` | Median | Statistical | 1879.6080 | 0.028389 | 3.3200e-05 | 4.8600e-05 |
| `f9_calc_min` | Min | Statistical | 1841.5158 | 0.020487 | 5.2300e-06 | -0.000478 |
| `f10_calc_std` | Standard deviation | Statistical | 10.4006 | 0.002595 | 1.3181e-05 | 0.000169 |
| `f11_calc_var` | Variance | Statistical | 108.1728 | 6.7317e-06 | 1.7375e-10 | 2.8713e-08 |
| `f12_dfa` | Detrended fluctuation analysis | Fractal | 1.0012 | 0.827578 | 1.1202 | 0.787936 |
| `f13_distance` | Signal distance | Temporal | 846.1216 | 364.0012 | 364.0000 | 364.0000 |
| `f14_ecdf` | ECDF | Statistical | 0.015068 | 0.015068 | 0.015068 | 0.015068 |
| `f15_ecdf_percentile` | ECDF Percentile | Statistical | 1879.3281 | 0.028493 | 3.3200e-05 | 5.6903e-05 |
| `f16_ecdf_percentile_count` | ECDF Percentile Count | Statistical | 182.5000 | 182.5000 | 182.5000 | 182.5000 |
| `f17_ecdf_slope` | ECDF Slope | Statistical | 0.040589 | 127.6798 | 3.0488e+04 | 2380.4660 |
| `f18_entropy` | Entropy | Statistical | 0.997425 | 1.0000 | 0.965067 | 0.996781 |
| `f19_fundamental_frequency` | Fundamental frequency | Spectral | 0.273973 | 0.273973 | 0.273973 | 0.273973 |
| `f20_higuchi_fractal_dimension` | Higuchi fractal dimension | Fractal | 1.7022 | 1.9118 | 1.7804 | 1.9658 |
| `f21_hist_mode` | Histogram mode | Statistical | 1882.9515 | 0.027528 | 3.3746e-05 | -1.3862e-05 |
| `f22_human_range_energy` | Human range energy | Spectral | 4.1439e-06 | 0.000798 | 0.017210 | 0.059520 |
| `f23_hurst_exponent` | Hurst exponent | Fractal | 0.927860 | 0.764445 | 0.869815 | 0.701973 |
| `f24_interq_range` | Interquartile range | Statistical | 12.5781 | 0.003516 | 1.6500e-05 | 0.000206 |
| `f25_kurtosis` | Kurtosis | Statistical | 1.2719 | 0.070144 | 0.103475 | 0.560417 |
| `f26_lempel_ziv` | Lempel-Ziv complexity | Temporal | 0.115068 | 0.189041 | 0.167123 | 0.202740 |
| `f27_lpcc` | LPCC | Spectral | 0.980869 | 0.906560 | 0.716331 | 0.217518 |
| `f28_max_frequency` | Maximum frequency | Spectral | 0 | 39.1781 | 43.2877 | 46.8493 |
| `f29_max_power_spectrum` | Max power spectrum | Spectral | 0.251306 | 0.181557 | 0.531363 | 0.213358 |
| `f30_maximum_fractal_length` | Maximum fractal length | Fractal | 2.9388 | -0.101520 | -2.5819 | -1.2274 |
| `f31_mean_abs_deviation` | Mean absolute deviation | Statistical | 7.9266 | 0.002088 | 1.0296e-05 | 0.000129 |
| `f32_mean_abs_diff` | Mean absolute diff | Temporal | 1.6084 | 0.001781 | 5.5105e-06 | 0.000131 |
| `f33_mean_diff` | Mean diff | Temporal | 0.167370 | 2.2104e-06 | 1.8681e-08 | -2.0904e-06 |
| `f34_median_abs_deviation` | Median absolute deviation | Statistical | 6.3148 | 0.001800 | 8.1857e-06 | 0.000104 |
| `f35_median_abs_diff` | Median absolute diff | Temporal | 0.079991 | 0.001196 | 2.5818e-06 | 9.3231e-05 |
| `f36_median_diff` | Median diff | Temporal | 0.079991 | -8.5349e-05 | 3.3333e-07 | -2.2286e-06 |
| `f37_median_frequency` | Median frequency | Spectral | 0 | 0 | 4.3836 | 18.3562 |
| `f38_mfcc` | MFCC | Spectral | -0.872663 | 19.9395 | 18.6419 | 37.8421 |
| `f39_mse` | Multiscale entropy | Fractal | 0.090951 | 1.3146 | 1.2085 | 1.1621 |
| `f40_negative_turning` | Negative turning points | Temporal | 8 | 72 | 56 | 77 |
| `f41_neighbourhood_peaks` | Neighbourhood peaks | Temporal | 4 | 16 | 15 | 17 |
| `f42_petrosian_fractal_dimension` | Petrosian fractal dimension | Fractal | 1.0031 | 1.0253 | 1.0200 | 1.0272 |
| `f43_pk_pk_distance` | Peak to peak distance | Statistical | 75.3376 | 0.015646 | 6.3370e-05 | 0.001032 |
| `f44_positive_turning` | Positive turning points | Temporal | 8 | 71 | 56 | 77 |
| `f45_power_bandwidth` | Power bandwidth | Spectral | 15.3425 | 39.1781 | 24.3836 | 45.2055 |
| `f46_rms` | Root mean square | Statistical | 1880.4777 | 0.028702 | 3.6085e-05 | 0.000178 |
| `f47_skewness` | Skewness | Statistical | 0.456233 | 0.224357 | 0.346497 | 0.123603 |
| `f48_slope` | Slope | Temporal | 0.070288 | -4.8450e-07 | -1.8427e-08 | 2.4007e-07 |
| `f49_spectral_centroid` | Spectral centroid | Spectral | 0.472249 | 7.9292 | 11.4779 | 20.5727 |
| `f50_spectral_decrease` | Spectral decrease | Spectral | -176.5308 | -8.1511 | -2.2081 | -0.178684 |
| `f51_spectral_distance` | Spectral distance | Spectral | -6.3637e+07 | -1112.2022 | -2.1272 | -8.3674 |
| `f52_spectral_entropy` | Spectral entropy | Spectral | 0.654235 | 0.851373 | 0.702653 | 0.862080 |
| `f53_spectral_kurtosis` | Spectral kurtosis | Spectral | 101.5632 | 4.5015 | 3.1370 | 1.8899 |
| `f54_spectral_positive_turning` | Spectral positive turning points | Spectral | 35 | 58 | 57 | 59 |
| `f55_spectral_roll_off` | Spectral roll-off | Spectral | 0 | 39.1781 | 43.2877 | 46.8493 |
| `f56_spectral_roll_on` | Spectral roll-on | Spectral | 0 | 0 | 0 | 0.273973 |
| `f57_spectral_skewness` | Spectral skewness | Spectral | 9.5311 | 1.6345 | 1.1780 | 0.370075 |
| `f58_spectral_slope` | Spectral slope | Spectral | -0.000638 | -0.000444 | -0.000351 | -0.000114 |
| `f59_spectral_spread` | Spectral spread | Spectral | 3.6433 | 13.1891 | 14.3657 | 15.1680 |
| `f60_spectral_variation` | Spectral variation | Spectral | 0.537916 | 0.730012 | 0.387386 | 0.244944 |
| `f61_spectrogram_mean_coeff` | Spectrogram mean coefficient | Spectral | 0.870720 | 1.1090e-07 | 2.8343e-12 | 5.1441e-10 |
| `f62_sum_abs_diff` | Sum absolute diff | Temporal | 585.4684 | 0.648295 | 0.002006 | 0.047764 |
| `f63_wavelet_abs_mean` | Wavelet absolute mean | Spectral | 109.9337 | 0.001668 | 1.4124e-06 | 3.0021e-06 |
| `f64_wavelet_energy` | Wavelet energy | Spectral | 403.2121 | 0.006869 | 2.1039e-05 | 0.000209 |
| `f65_wavelet_entropy` | Wavelet entropy | Spectral | 1.9452 | 2.1303 | 2.1150 | 2.1853 |
| `f66_wavelet_std` | Wavelet standard deviation | Spectral | 387.2365 | 0.006642 | 2.0985e-05 | 0.000209 |
| `f67_wavelet_var` | Wavelet variance | Spectral | 1.8789e+05 | 5.1137e-05 | 5.0050e-10 | 4.4428e-08 |
| `f68_zero_cross` | Zero crossing rate | Temporal | 0 | 0 | 0 | 109 |

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

Sebagai tindak lanjut dari integrasi matriks fitur runtun waktu 4 polutan yang dikompilasi dari 18 mahasiswa / wilayah pengamatan, dilakukan pemodelan klaster menggunakan **KNIME Analytics Platform** dengan algoritma **K-Means Clustering**.

Pada pengujian ini, dianalisis dua pendekatan pemodelan:
1. **Menggunakan PCA dengan 18 Dimensi**: Mereduksi 272 fitur awal menjadi 18 komponen utama sebelum K-Means.
2. **Tanpa PCA (272 Fitur Penuh)**: Memasukkan seluruh 272 fitur TSFEL secara langsung ke K-Means tanpa reduksi dimensi.

Dokumentasi lengkap, arsitektur workflow KNIME, tabel hasil pengelompokan 18 data, analisis nilai centroid klaster, serta evaluasi komparatif disajikan pada halaman berikut:

👉 **[Melakukan Cluster menggunakan K-means menggunakan Knime](Melakukan%20Cluster%20menggunakan%20K-means%20menggunakan%20Knime.md)**
