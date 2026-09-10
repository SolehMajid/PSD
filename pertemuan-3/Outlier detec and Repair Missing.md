# Deteksi Outlier & Penanganan Missing Value (Pertemuan 3)

Dokumentasi ini menyajikan laporan komprehensif mengenai pemrosesan data deret waktu (*time series*) konsentrasi polutan Karbon Monoksida (CO) di Kabupaten Bangkalan pada **Pertemuan ke-3**. Tahapan utama mencakup pemotongan data satu tahun (365 hari), deteksi dan pembersihan pencilan menggunakan **Metode Iterative Z-Score Bertahap**, serta penyelesaian nilai kosong menggunakan **Interpolasi Linear Bertahap** untuk menghasilkan dataset yang bersih sempurna (*clean dataset*).

Notebook eksekusi:
- [`detec_outlier.ipynb`](detec_outlier.ipynb) : Kode program deteksi outlier bertahap dan ekspor data bebas pencilan.
- [`tambal-missing.ipynb`](tambal-missing.ipynb) : Kode program penambalan *missing value* dengan interpolasi linear.

---

## 1. Pendahuluan & Pemilihan Data 1 Tahun (Hari 1 – 365)

Data mentah diambil dari rekaman satelit Copernicus Sentinel-5P Level 2 pada file `data/csv/polutan_co_bangkalan.csv`. Sesuai ketentuan analisis deret waktu tahunan, data dibatasi tepat pada **365 hari pengamatan pertama** (24 Agustus 2025 s.d. 23 Agustus 2026).

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np

# Membaca data mentah dan membatasi pada 365 baris pertama
df_raw = pd.read_csv("../data/csv/polutan_co_bangkalan.csv")
df = df_raw.iloc[:365].copy()
df['tanggal'] = pd.to_datetime(df['tanggal'])

print("=== PROFIL DATASET 1 TAHUN (HARI 1 - 365) ===")
print(f"Total Baris Data        : {len(df)} hari")
print(f"Rentang Tanggal         : {df['tanggal'].min().strftime('%Y-%m-%d')} s.d. {df['tanggal'].max().strftime('%Y-%m-%d')}")
print(f"Data Valid (Terisi)     : {df['CO'].notna().sum()} hari (64.38%)")
print(f"Missing Values (NaN)    : {df['CO'].isna().sum()} hari (35.62%)")
```

```
=== PROFIL DATASET 1 TAHUN (HARI 1 - 365) ===
Total Baris Data        : 365 hari
Rentang Tanggal         : 2025-08-24 s.d. 2026-08-23
Data Valid (Terisi)     : 235 hari (64.38%)
Missing Values (NaN)    : 130 hari (35.62%)
```

---

## 2. Eksplorasi Statistik Deskriptif Awal

Sebelum dilakukan deteksi outlier, karakteristik distribusi dari 235 data valid dihitung untuk memperoleh parameter pemusatan (*mean*, median) dan parameter penyebaran (*standard deviation*, IQR):

| Parameter Statistik | Formula Matematis | Nilai Terhitung | Interpretasi |
| :--- | :--- | :--- | :--- |
| **Jumlah Sampel ($n$)** | $\sum 1$ | $235$ hari | Jumlah hari pengamatan dengan rekaman sensor valid |
| **Rata-rata ($\mu$)** | $\frac{1}{n} \sum x_i$ | $0.02882526\text{ mol/m}^2$ | Titik pusat konsentrasi CO di Kabupaten Bangkalan |
| **Standar Deviasi ($\sigma$)** | $\sqrt{\frac{\sum (x_i - \mu)^2}{n-1}}$ | $0.00318052\text{ mol/m}^2$ | Variabilitas konsentrasi harian |
| **Median ($Q_2$)** | Nilai tengah | $0.02867761\text{ mol/m}^2$ | Nilai tengah membagi data menjadi dua bagian sama |
| **Kuartil Bawah ($Q_1$)** | Persentil ke-25 | $0.02677938\text{ mol/m}^2$ | Batas 25% data konsentrasi terendah |
| **Kuartil Atas ($Q_3$)** | Persentil ke-75 | $0.03058865\text{ mol/m}^2$ | Batas 75% data konsentrasi |
| **Rentang Antarkuartil ($IQR$)** | $Q_3 - Q_1$ | $0.00380927\text{ mol/m}^2$ | Sebaran 50% data di area tengah |
| **Nilai Minimum** | $\min(x_i)$ | $0.02048731\text{ mol/m}^2$ | Konsentrasi terendah (terekam pada 2026-04-06) |
| **Nilai Maksimum** | $\max(x_i)$ | $0.04421752\text{ mol/m}^2$ | Konsentrasi tertinggi (terekam pada 2025-10-07) |
| **Kemiringan (*Skewness*)** | $\frac{n}{(n-1)(n-2)} \sum (\frac{x_i-\mu}{\sigma})^3$ | $+0.7061$ | Miring ke kanan (*positive skew* / ekor kanan memanjang) |
| **Keruncingan (*Kurtosis*)** | Momen ke-4 terstandarisasi | $+1.9723$ | Leptokurtik (puncak runcing dengan indikasi ekor pencilan) |

```{figure} ../assets/images/images_pertemuan-3/1.distribusi_awal_co.png
:width: 100%
:align: center

Distribusi Data Mentah Konsentrasi CO: Boxplot (kiri) memperlihatkan titik-titik anomali di atas kumis atas, dan Histogram (kanan) memperlihatkan ekor distribusi yang condong ke kanan.
```

---

## 3. Deteksi Outlier Bertahap Menggunakan Metode Iterative Z-Score

### 3.1 Landasan Teori & Rumus Matematis Z-Score
Skor standar (**Z-Score**) menyatakan jarak suatu nilai observasi dari nilai rata-rata kelompoknya dalam kelipatan simpangan baku:

$$Z_i = \frac{x_i - \mu}{\sigma}$$

Dimana:
- $x_i$ : Nilai konsentrasi CO pada tanggal ke-$i$.
- $\mu$ : Rata-rata sampel (*sample mean*).
- $\sigma$ : Simpangan baku sampel (*sample standard deviation*).

Ambang batas yang digunakan adalah aturan **3-Sigma ($|Z| > 3.0$)**. Berdasarkan teorema probabilitas normal standar, rentang $[\mu - 3\sigma, \mu + 3\sigma]$ mencakup **99.73%** populasi normal. Nilai di luar rentang ini memiliki peluang kemunculan acak sangat kecil ($< 0.27\%$) sehingga diklasifikasikan sebagai **pencilan ekstrem (*extreme outlier*)**.

### 3.2 Efek Penyamaran (*Masking Effect*) & Perlunya Pendekatan Bertahap
Pada data runtun waktu, keberadaan pencilan ekstrem raksasa akan mendistorsi parameter statistik:
1. Nilai ekstrem tinggi menarik $\mu$ naik dan membuat $\sigma$ membesar.
2. Akibatnya, ambang batas $3\sigma$ menjadi terlalu lebar, sehingga pencilan sekunder yang sebenarnya abnormal dapat **tersamarkan (*masking effect*)** pada putaran pertama.
3. Begitu pencilan raksasa dihilangkan pada **Tahap 1**, simpangan baku $\sigma$ menyusut, sehingga batas menjadi lebih presisi. Pada **Tahap 2**, pencilan yang tadinya tersamarkan akan terdeteksi.
4. Pada **Tahap 3**, penghitungan Z-score diuji ulang hingga menghasilkan **0 outlier (konvergen sempurna)**.

```{code-cell}
:tags: [hide-input]
THRESHOLD = 3.0
df_iter = df.copy()
all_outliers = []
iteration = 1

while True:
    valid_series = df_iter['CO'].dropna()
    curr_mean = valid_series.mean()
    curr_std = valid_series.std()
    curr_z = (df_iter['CO'] - curr_mean) / curr_std
    round_outliers = curr_z[curr_z.abs() > THRESHOLD]
    
    print(f"--- TAHAP {iteration} ---")
    print(f"Rata-rata (μ)        : {curr_mean:.8f}")
    print(f"Standar Deviasi (σ)  : {curr_std:.8f}")
    print(f"Outlier Ditemukan    : {len(round_outliers)} titik")
    
    if len(round_outliers) == 0:
        print(f">>> STATUS: KONVERGEN! Data 100% BEBAS DARI OUTLIER pada Tahap {iteration}.\\n")
        break
        
    for idx in round_outliers.index:
        tgl = df_iter.loc[idx, 'tanggal'].strftime('%Y-%m-%d')
        val = df_iter.loc[idx, 'CO']
        z_val = curr_z.loc[idx]
        all_outliers.append({'Tahap': f'Tahap {iteration}', 'Tanggal': tgl, 'Nilai CO': val, 'Z-Score': z_val})
        print(f"  * Dihilangkan: {tgl} | CO = {val:.8f} | Z = {z_val:+.2f}")
        
    df_iter.loc[round_outliers.index, 'CO'] = np.nan
    iteration += 1
```

```
--- TAHAP 1 ---
Rata-rata (μ)        : 0.02882526
Standar Deviasi (σ)  : 0.00318052
Outlier Ditemukan    : 2 titik
  * Dihilangkan: 2025-10-07 | CO = 0.04421752 | Z = +4.84
  * Dihilangkan: 2026-07-23 | CO = 0.03851003 | Z = +3.04
--- TAHAP 2 ---
Rata-rata (μ)        : 0.02871809
Standar Deviasi (σ)  : 0.00296170
Outlier Ditemukan    : 1 titik
  * Dihilangkan: 2025-09-24 | CO = 0.03780002 | Z = +3.07
--- TAHAP 3 ---
Rata-rata (μ)        : 0.02867911
Standar Deviasi (σ)  : 0.00290730
Outlier Ditemukan    : 0 titik
>>> STATUS: KONVERGEN! Data 100% BEBAS DARI OUTLIER pada Tahap 3.
```

### 3.3 Rincian Pencilan yang Dihilangkan
Total pencilan yang dihilangkan secara bertahap berjumlah **3 titik data**:

| Tahap | Tanggal | Konsentrasi CO ($\text{mol/m}^2$) | Skor $Z$ Awal | Skor $Z$ Tahap 2 | Keterangan |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **Tahap 1** | **2025-10-07** | $0.04421752$ | **$+4.84$** | — | Pencilan Atas Sangat Ekstrem |
| **Tahap 1** | **2026-07-23** | $0.03851003$ | **$+3.04$** | — | Pencilan Atas Ekstrem |
| **Tahap 2** | **2025-09-24** | $0.03780002$ | $+2.82$ | **$+3.07$** | Pencilan yang Sempat Tersamarkan (*Masked*) |

```{figure} ../assets/images/images_pertemuan-3/2.deteksi_outlier_bertahap.png
:width: 100%
:align: center

Visualisasi Deteksi Outlier Bertahap Menggunakan Metode Iterative Z-Score (|Z| > 3.0): Tanda silang merah ('X') menandai 3 titik anomali yang berhasil dihilangkan.
```

---

## 4. Penghilangan Outlier & Ekspor Data Bebas Pencilan

Dalam deret waktu, integritas indeks kalender 365 hari sangat vital agar proses pemulihan data (*gap filling*) dapat berjalan mulus. Oleh karena itu:
- Nilai konsentrasi pada 3 tanggal pencilan diubah menjadi **`NaN`** (*missing value*), menghasilkan file **`polutan_co_bangkalan_clean.csv`**.
- Total baris tetap **365 hari utuh**, dengan rincian: $232$ data valid dan $133$ data kosong ($130$ bawaan sensor satelit + $3$ dari pencilan yang telah dinetralkan).
- Saat diuji ulang dengan Z-Score, file ini terbukti menghasilkan **0 outlier**.

```{code-cell}
:tags: [hide-input]
# Verifikasi Z-score pada file bersih
df_clean = pd.read_csv("../data/csv/pertemuan-3-csv/polutan_co_bangkalan_clean.csv")
co_clean = df_clean['CO'].dropna()
z_clean = (co_clean - co_clean.mean()) / co_clean.std()
outliers_sisa = co_clean[z_clean.abs() > 3.0]

print("=== VERIFIKASI PADA FILE BERSIH (polutan_co_bangkalan_clean.csv) ===")
print(f"Total Baris Data        : {len(df_clean)} hari")
print(f"Jumlah Data Valid       : {len(co_clean)} hari")
print(f"Jumlah Missing (NaN)    : {df_clean['CO'].isna().sum()} hari")
print(f"Jumlah Outlier Sisa     : {len(outliers_sisa)} titik (100% BEBAS OUTLIER)")
```

```
=== VERIFIKASI PADA FILE BERSIH (polutan_co_bangkalan_clean.csv) ===
Total Baris Data        : 365 hari
Jumlah Data Valid       : 232 hari
Jumlah Missing (NaN)    : 133 hari
Jumlah Outlier Sisa     : 0 titik (100% BEBAS OUTLIER)
```

---

## 5. Penyelesaian Missing Value Menggunakan Interpolasi Linear Bertahap

Setelah data dipastikan bebas dari pencilan, langkah selanjutnya adalah menyelesaikan masalah **133 missing values** pada file notebook [`tambal-missing.ipynb`](tambal-missing.ipynb).

```{figure} ../assets/images/images_pertemuan-3/3.peta_missing_values.png
:width: 100%
:align: center

Peta Sebaran Missing Values Konsentrasi CO Sepanjang 1 Tahun (Merah = Data Kosong, Hijau = Data Valid).
```

### 5.1 Rasional Pemilihan Metode Interpolasi Linear
Berdasarkan karakteristik fisika lingkungan konsentrasi gas di Kabupaten Bangkalan:
1. **Mempertahankan Kontinuitas Tren Harian**: Konsentrasi polutan atmosfer tidak meloncat seketika melainkan bertransisi secara gradual seiring dinamika sirkulasi udara harian. Interpolasi linear menghubungkan titik sebelum dan sesudah kekosongan dengan gradien alami yang mulus.
2. **Menghindari Osilasi Liar (*Runge's Phenomenon*)**: Metode polinomial derajat tinggi (*spline*) rentan berosilasi liar pada celah data yang lebar, berpotensi memunculkan nilai konsentrasi negatif yang mustahil secara fisik.
3. **Mencegah Perataan Data Kaku**: Imputasi *Mean* atau *Median* menghasilkan garis datar konstan yang merusak dinamika spektral dan variabilitas deret waktu.

```{figure} ../assets/images/images_pertemuan-3/4.komparasi_metode_imputasi.png
:width: 100%
:align: center

Perbandingan Karakteristik Metode Imputasi: Interpolasi Linear (biru tebal) terbukti paling realistis dibandingkan Mean (garis datar kaku), Forward Fill (bertangga), maupun Spline (osilasi berlebih).
```

### 5.2 Rumus Matematis Interpolasi Linear
Untuk titik waktu $t$ yang hilang di antara dua pengamatan valid $(t_0, y_0)$ dan $(t_1, y_1)$:

$$y(t) = y_0 + (t - t_0) \times \frac{y_1 - y_0}{t_1 - t_0}$$

Dimana:
- $y(t)$ : Estimasi konsentrasi CO pada tanggal $t$ yang hilang.
- $y_0$ : Nilai konsentrasi valid terakhir sebelum kekosongan.
- $y_1$ : Nilai konsentrasi valid pertama setelah kekosongan.
- $t_0, t_1$ : Indeks tanggal observasi pengapit.
- $\frac{y_1 - y_0}{t_1 - t_0}$ : Kemiringan (*slope* / gradien) laju perubahan konsentrasi per hari.

---

## 6. Hasil Imputasi Linear & Evaluasi Statistik

Penambalan 133 titik data kosong dilakukan dengan mengeksekusi fungsi interpolasi linear berbasis tanggal:

```{code-cell}
:tags: [hide-input]
# Melakukan interpolasi linear
df_clean['CO_imputed'] = df_clean['CO'].interpolate(method='linear')
df_clean['CO_imputed'] = df_clean['CO_imputed'].bfill().ffill()

sisa_nan = df_clean['CO_imputed'].isna().sum()
print("=== HASIL IMPUTASI INTERPOLASI LINEAR ===")
print(f"Total Baris Data        : {len(df_clean)} hari")
print(f"Data Valid Asli         : {(~df_clean['CO'].isna()).sum()} hari")
print(f"Data Berhasil Ditambal  : {df_clean['CO'].isna().sum()} hari")
print(f"Sisa Missing Values     : {sisa_nan} hari (100% LENGKAP)")
```

```
=== HASIL IMPUTASI INTERPOLASI LINEAR ===
Total Baris Data        : 365 hari
Data Valid Asli         : 232 hari
Data Berhasil Ditambal  : 133 hari
Sisa Missing Values     : 0 hari (100% LENGKAP)
```

### Perbandingan Karakteristik Statistik Sebelum vs Sesudah Imputasi:

| Parameter Statistik | Data Awal Mentah | Data Bebas Outlier | Data Bersih Sempurna (Setelah Imputasi) |
| :--- | :---: | :---: | :---: |
| **Jumlah Baris ($n$)** | $365$ | $365$ | **$365$ hari (100% Lengkap)** |
| **Data Terisi Valid** | $235$ | $232$ | **$365$ hari** |
| **Missing Values (NaN)** | $130$ | $133$ | **$0$ hari (0 NaN)** |
| **Jumlah Outlier (|Z| > 3)** | $2$ titik | **$0$ titik** | **$0$ titik** |
| **Rata-rata ($\mu$)** | $0.02882526\text{ mol/m}^2$ | $0.02867911\text{ mol/m}^2$ | **$0.02858408\text{ mol/m}^2$** |
| **Standar Deviasi ($\sigma$)** | $0.00318052\text{ mol/m}^2$ | $0.00290730\text{ mol/m}^2$ | **$0.00259837\text{ mol/m}^2$** |
| **Nilai Minimum** | $0.02048731\text{ mol/m}^2$ | $0.02048735\text{ mol/m}^2$ | **$0.02048735\text{ mol/m}^2$** |
| **Nilai Maksimum** | $0.04421752\text{ mol/m}^2$ | $0.03613363\text{ mol/m}^2$ | **$0.03613363\text{ mol/m}^2$** |

```{figure} ../assets/images/images_pertemuan-3/5.hasil_interpolasi_linear.png
:width: 100%
:align: center

Runtun Waktu Konsentrasi CO 365 Hari Lengkap: Titik oranye menunjukkan 133 data yang berhasil ditambal secara kontinu menggunakan interpolasi linear.
```

```{figure} ../assets/images/images_pertemuan-3/6.zoom_in_dan_boxplot.png
:width: 100%
:align: center

Detail Kontinuitas Interpolasi pada Celah Data (kiri) dan Perbandingan Boxplot Sebelum vs Sesudah Imputasi (kanan) yang membuktikan distribusi data tetap terjaga stabil tanpa anomali.
```

---

## 7. File Output Akhir & Kesiapan Data

File hasil akhir pemrosesan disimpan pada direktori target:
**`data/csv/pertemuan-3-csv/polutan_co_bangkalan_final_clean.csv`**

### Verifikasi Integritas File:
- **Rentang Waktu**: 365 hari berurutan tanpa putus (24 Agustus 2025 s.d. 23 Agustus 2026).
- **Kelengkapan Nilai**: **100% terisi (0 NaN)**.
- **Kebersihan Anomali**: **0 Outlier**.
- **Kesiapan Modul Berikutnya**: Dataset ini memenuhi seluruh kualifikasi kualitas data (*data quality standards*) untuk dilanjutkan ke tahap **Tugas ke-5: Ekstraksi 68 Fitur Deret Waktu Menggunakan TSFEL**.
