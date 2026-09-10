# Ekstraksi Fitur Runtun Waktu Konsentrasi CO Menggunakan Pustaka TSFEL

## 1. Pendahuluan & Konsep Ekstraksi Fitur Runtun Waktu

Ekstraksi fitur deret waktu (*time-series feature extraction*) merupakan tahapan krusial dalam rekayasa data (*feature engineering*) untuk mengubah sinyal runtun waktu berdimensi tinggi menjadi representasi numerik ringkas yang sarat makna fisis, statistik, dan dinamis. Pada data kualitas udara, fluktuasi harian konsentrasi gas Karbon Monoksida (**CO**) di Kabupaten Bangkalan tidak hanya mencerminkan besaran emisi rata-rata, melainkan menyimpan karakteristik dinamika periodisitas cuaca, dispersi angin, aktivitas antropogenik kendaraan bermotor, serta persistensi memori jangka panjang.

Untuk mengekstraksi informasi tersebut secara komprehensif tanpa kehilangan aspek penting data, digunakan pustaka **TSFEL (Time Series Feature Extraction Library)**. TSFEL merupakan kerangka kerja komputasi deret waktu mutakhir yang mampu mengekstraksi seluruh spektrum fitur sinyal secara otomatis ke dalam empat domain keilmuan:

1. **Statistical Domain (21 Fitur)**: Mengukur tendensi sentral, dispersi, keruncingan kurva, asimetri, dan fungsi distribusi probabilitas data.
2. **Temporal Domain (15 Fitur)**: Mengukur laju perubahan antarhari, autokorelasi, titik balik arah (*turning points*), panjang lintasan, dan kompleksitas deret.
3. **Spectral Domain (26 Fitur)**: Menganalisis kandungan frekuensi melalui Transformasi Fourier Diskrit (FFT), Spektrogram STFT, Koefisien Kepstral (MFCC & LPCC), dan Transformasi Wavelet Kontinyu (CWT).
4. **Fractal Domain (6 Fitur)**: Mengukur derajat ketidakteraturan (*self-similarity*), eksponen persistensi memori jangka panjang (*Hurst Exponent* & *DFA*), serta entropi multi-skala (*Multiscale Entropy*).
---

## 2. Alur Program & Eksekusi Kode Ekstraksi Fitur TSFEL

Berikut adalah tahapan implementasi program Python untuk melakukan ekstraksi seluruh 68 fitur TSFEL pada kolom `CO`.

### 2.1 Memuat Dataset Bersih & Konfigurasi Fitur TSFEL

Pada tahap ini, dataset bersih dimuat ke dalam *DataFrame*, dan konfigurasi seluruh domain fitur TSFEL diaktifkan secara menyeluruh.

```{code-cell} python
import pandas as pd
import numpy as np
import tsfel
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings('ignore')

# 1. Memuat dataset bersih polutan CO Bangkalan
df = pd.read_csv('../data/csv/pertemuan-3-csv/polutan_co_bangkalan_final_clean.csv')

print("=== INFORMASI DATASET CO BANGKALAN ===")
print(f"Jumlah observasi: {len(df)} baris (365 hari)")
print(f"Rentang waktu   : {df['tanggal'].min()} s/d {df['tanggal'].max()}")
print(f"Missing values  : {df.isna().sum().sum()}")
df.head()
```

```text
=== INFORMASI DATASET CO BANGKALAN ===
Jumlah observasi: 365 baris (365 hari)
Rentang waktu   : 2025-08-24 s/d 2026-08-23
Missing values  : 0

      tanggal        CO
0  2025-08-24  0.032369
1  2025-08-25  0.029644
2  2025-08-26  0.029057
3  2025-08-27  0.028471
4  2025-08-28  0.024230
```

### 2.2 Menyiapkan Seluruh Domain Fitur TSFEL (Statistical, Temporal, Spectral, Fractal)

Seluruh fungsi fitur yang tersedia pada pustaka TSFEL diaktifkan tanpa terkecuali (`use='yes'`).

```{code-cell} python
# Mengambil konfigurasi seluruh fitur TSFEL
cfg = tsfel.get_features_by_domain()

# Mengaktifkan seluruh fitur yang ada (use='yes')
for domain, features_dict in cfg.items():
    for feat_name in features_dict:
        cfg[domain][feat_name]['use'] = 'yes'

print("=== DISTRIBUSI FITUR TSFEL YANG DIAKTIFKAN ===")
for domain, features_dict in cfg.items():
    print(f"- Domain {domain.capitalize():12}: {len(features_dict)} fungsi fitur")
print("- Fitur tambahan ecdf_slope : 1 fungsi fitur")
print("-> TOTAL KESELURUHAN        : 68 FUNGSI FITUR LENGKAP")
```

```text
=== DISTRIBUSI FITUR TSFEL YANG DIAKTIFKAN ===
- Domain Spectral    : 26 fungsi fitur
- Domain Statistical : 20 fungsi fitur
- Domain Temporal    : 15 fungsi fitur
- Domain Fractal     : 6 fungsi fitur
- Fitur tambahan ecdf_slope : 1 fungsi fitur
-> TOTAL KESELURUHAN        : 68 FUNGSI FITUR LENGKAP
```

### 2.3 Eksekusi Ekstraksi Fitur Runtun Waktu

Ekstraksi dijalankan menggunakan `tsfel.time_series_features_extractor()`, kemudian ditambahkan fitur `ecdf_slope` dari modul statistik TSFEL.

```{code-cell} python
# Ekstraksi fitur runtun waktu pada kolom CO
features_extracted = tsfel.time_series_features_extractor(cfg, df[['CO']], verbose=0)

# Menambahkan perhitungan ecdf_slope
features_extracted['CO_ECDF Slope'] = tsfel.ecdf_slope(df['CO'])

# Mengurutkan kolom secara alfabetis
features_extracted = features_extracted.reindex(sorted(features_extracted.columns), axis=1)

print(f"Matriks fitur berhasil diekstrak dengan ukuran: {features_extracted.shape}")
print(f"Total dimensi kolom fitur yang diperoleh: {features_extracted.shape[1]} nilai fitur numerik")
print(f"Jumlah nilai kosong (NaN/Inf): {features_extracted.isna().sum().sum()}")
```

```text
Matriks fitur berhasil diekstrak dengan ukuran: (1, 164)
Total dimensi kolom fitur yang diperoleh: 164 nilai fitur numerik
Jumlah nilai kosong (NaN/Inf): 0
```

---

## 3. Visualisasi Profil Fitur TSFEL & Sinyal CO

Hasil ekstraksi fitur menyajikan profil multi-dimensi dari dinamika konsentrasi polutan CO Bangkalan:

```{figure} ../assets/images/images_pertemuan-3/7.distribusi_fitur_tsfel_domain.png
---
name: gambar-distribusi-fitur-tsfel
width: 95%
align: center
---
Proporsi 68 fungsi fitur TSFEL per domain keilmuan (kiri) dan rincian 164 dimensi kolom koefisien yang diekstrak (kanan).
```

```{figure} ../assets/images/images_pertemuan-3/8.radar_karakteristik_fitur_co.png
---
name: gambar-radar-fitur-co
width: 70%
align: center
---
Diagram radar profil karakteristik sinyal CO Bangkalan berdasarkan representasi fitur-fitur utama TSFEL ternormalisasi.
```

---

## 4. Katalog Lengkap & Penjelasan 68 Fitur TSFEL

Berikut adalah dokumentasi komprehensif untuk seluruh **68 fitur TSFEL** yang diekstrak pada konsentrasi CO Bangkalan, dikelompokkan berdasarkan 4 domain keilmuan: **Statistical**, **Temporal**, **Spectral**, dan **Fractal**. Setiap fitur dilengkapi dengan deskripsi fisis, perumusan matematis LaTeX, penjelasan notasi rumus, dan nilai terhitungnya.


### 4.1 Domain Statistical (21 Fitur)

Domain **Statistical** berfokus pada analisis 
distribusi probabilitas, tendensi sentral, derajat dispersi, dan bentuk kurva sebaran nilai konsentrasi CO.

#### Fitur 1: `abs_energy(signal)` — Absolute Energy

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung energi total absolut sinyal sebagai akumulasi jumlahan kuadrat seluruh konsentrasi harian CO. Fitur ini merefleksikan magnitudo energi keseluruhan emisi polutan selama satu tahun observasi di Bangkalan.
- **Rumus Matematis**:
  $$
  E = \sum_{i=1}^{N} x_i^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $N = 365$ adalah jumlah hari observasi dan $x_i$ adalah nilai konsentrasi CO pada hari ke-$i$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.300680`**

#### Fitur 2: `average_power(signal, fs)` — Average Power

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung daya rata-rata per satuan waktu dari sinyal. Merepresentasikan tingkat intensitas rata-rata fluktuasi konsentrasi polutan per hari.
- **Rumus Matematis**:
  $$
  P_{avg} = \frac{1}{N} \sum_{i=1}^{N} x_i^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $N$ adalah jumlah sampel data dan $x_i$ adalah nilai konsentrasi CO pada hari ke-$i$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.082604`**

#### Fitur 3: `calc_max(signal)` — Maximum Value

- **Domain**: `Statistical`
- **Deskripsi**: Menentukan nilai konsentrasi CO tertinggi yang tercatat selama rentang satu tahun setelah proses pembersihan outlier ekstrem.
- **Rumus Matematis**:
  $$
  x_{max} = \max_{1 \le i \le N} (x_i)
  $$
- **Penjelasan Notasi Rumus**: Di mana $\max$ mengambil elemen data terbesar dalam himpunan sinyal $x$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.036134`**

#### Fitur 4: `calc_mean(signal)` — Mean

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung nilai rata-rata aritmatika konsentrasi gas CO harian, menjadi ukuran tendensi sentral utama kualitas udara di Bangkalan.
- **Rumus Matematis**:
  $$
  \mu = \frac{1}{N} \sum_{i=1}^{N} x_i
  $$
- **Penjelasan Notasi Rumus**: Di mana $\mu$ adalah nilai rerata, $N$ adalah total 365 hari, dan $x_i$ adalah konsentrasi pada hari ke-$i$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.028584`**

#### Fitur 5: `calc_median(signal)` — Median

- **Domain**: `Statistical`
- **Deskripsi**: Menentukan nilai tengah dari deret data yang telah diurutkan. Nilai ini sangat kokoh (robust) terhadap pencilan data.
- **Rumus Matematis**:
  $$
  \tilde{x} = \begin{cases} x_{\left(\frac{N+1}{2}\right)}, & \text{jika } N \text{ ganjil} \\ \frac{x_{(N/2)} + x_{(N/2 + 1)}}{2}, & \text{jika } N \text{ genap} \end{cases}
  $$
- **Penjelasan Notasi Rumus**: Di mana $x_{(k)}$ melambangkan nilai urutan statistik ke-$k$ setelah deret data diurutkan dari terkecil ke terbesar.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.028389`**

#### Fitur 6: `calc_min(signal)` — Minimum Value

- **Domain**: `Statistical`
- **Deskripsi**: Menentukan batas konsentrasi CO terendah (kondisi udara paling bersih dari polutan CO) yang tercatat di Bangkalan.
- **Rumus Matematis**:
  $$
  x_{min} = \min_{1 \le i \le N} (x_i)
  $$
- **Penjelasan Notasi Rumus**: Di mana $\min$ mengambil elemen data terkecil dalam runtun waktu konsentrasi CO.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.020487`**

#### Fitur 7: `calc_std(signal)` — Standard Deviation

- **Domain**: `Statistical`
- **Deskripsi**: Mengukur dispersi atau simpangan baku persebaran konsentrasi CO di sekitar nilai rata-ratanya sepanjang tahun.
- **Rumus Matematis**:
  $$
  \sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana $\sigma$ adalah standar deviasi, $\mu$ adalah rata-rata sinyal, dan $N$ adalah jumlah titik data.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.002595`**

#### Fitur 8: `calc_var(signal)` — Variance

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung variansi kuadrat simpangan konsentrasi CO, mengindikasikan tingkat volatilitas variabilitas harian polutan.
- **Rumus Matematis**:
  $$
  \sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $\sigma^2$ adalah variansi populasi dari deret data.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000007`**

#### Fitur 9: `ecdf(signal[, d])` — Empirical Cumulative Distribution Function (ECDF)

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung nilai fungsi distribusi kumulatif empiris pada 10 kuantil bertingkat untuk memetakan kurva probabilitas kumulatif konsentrasi.
- **Rumus Matematis**:
  $$
  \hat{F}_n(t) = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}_{\{x_i \le t\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana $\mathbf{1}_{\{x_i \le t\}}$ bernilai 1 jika sampel $x_i \le t$ dan bernilai 0 jika sebaliknya.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`10 nilai kuantil (rentang: [0.1000, 1.0000])`**

#### Fitur 10: `ecdf_percentile(signal[, percentile])` — ECDF Percentile

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung nilai batas konsentrasi CO pada persentil ke-20 (0.2) dan persentil ke-80 (0.8) dari kurva ECDF.
- **Rumus Matematis**:
  $$
  Q(p) = \inf \{x : \hat{F}_n(x) \ge p\}
  $$
- **Penjelasan Notasi Rumus**: Di mana $Q(p)$ adalah nilai ambang batas pada fraksi persentil kumulatif $p \in \{0.2, 0.8\}$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`2 koefisien: P20 = 0.026618, P80 = 0.030539`**

#### Fitur 11: `ecdf_percentile_count(signal[, percentile])` — ECDF Percentile Count

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung frekuensi kumulatif banyaknya sampel hari yang memiliki konsentrasi di bawah persentil ke-20 dan ke-80.
- **Rumus Matematis**:
  $$
  C(p) = \sum_{i=1}^{N} \mathbf{1}_{\{x_i \le Q(p)\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana $C(p)$ adalah jumlah sampel kumulatif yang memenuhi kriteria nilai di bawah persentil $p$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`2 nilai: C(0.2) = 73 hari, C(0.8) = 292 hari`**

#### Fitur 12: `ecdf_slope(signal[, p_init, p_end])` — ECDF Slope

- **Domain**: `Statistical`
- **Deskripsi**: Kemiringan laju pertumbuhan probabilitas kumulatif antara persentil ke-50 (median) dan persentil ke-75 (kuartil atas). Semakin curam, semakin pekat konsentrasi data di area median.
- **Rumus Matematis**:
  $$
  S_{ecdf} = \frac{p_{end} - p_{init}}{Q(p_{end}) - Q(p_{init})}
  $$
- **Penjelasan Notasi Rumus**: Di mana $p_{init} = 0.5$, $p_{end} = 0.75$, dan $Q(p)$ adalah nilai persentil terkait.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`127.679760`**

#### Fitur 13: `entropy(signal[, prob])` — Shannon Entropy

- **Domain**: `Statistical`
- **Deskripsi**: Mengukur tingkat ketidakpastian informasi dan derajat keacakan sebaran nilai konsentrasi polutan CO.
- **Rumus Matematis**:
  $$
  H(X) = -\sum_{i=1}^{K} p(x_i) \log_2 p(x_i)
  $$
- **Penjelasan Notasi Rumus**: Di mana $p(x_i)$ adalah probabilitas kemunculan status nilai dalam partisi ruang keadaan $K$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.000000`**

#### Fitur 14: `hist_mode(signal[, nbins])` — Histogram Mode

- **Domain**: `Statistical`
- **Deskripsi**: Menghitung nilai modus dari bin histogram dengan frekuensi kemunculan tertinggi pada sebaran konsentrasi CO.
- **Rumus Matematis**:
  $$
  M_{hist} = \text{center}\left(\arg\max_{k} \text{Bin}_k\right)
  $$
- **Penjelasan Notasi Rumus**: Di mana $\arg\max \text{Bin}_k$ adalah indeks bin dengan jumlah observasi terbanyak.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.027528`**

#### Fitur 15: `interq_range(signal)` — Interquartile Range (IQR)

- **Domain**: `Statistical`
- **Deskripsi**: Mengukur rentang dispersi non-parametrik antara kuartil ketiga ($Q_3$) dan kuartil pertama ($Q_1$), merepresentasikan sebaran 50% data tengah.
- **Rumus Matematis**:
  $$
  IQR = Q_3 - Q_1 = Q(0.75) - Q(0.25)
  $$
- **Penjelasan Notasi Rumus**: Di mana $Q_3$ adalah kuartil atas (persentil ke-75) dan $Q_1$ adalah kuartil bawah (persentil ke-25).
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.003516`**

#### Fitur 16: `kurtosis(signal)` — Kurtosis

- **Domain**: `Statistical`
- **Deskripsi**: Mengukur derajat keruncingan puncak distribusi data relatif terhadap kurva distribusi normal standar.
- **Rumus Matematis**:
  $$
  \text{Kurt} = \frac{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^4}{\left(\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2\right)^2} - 3
  $$
- **Penjelasan Notasi Rumus**: Di mana angka $-3$ merupakan penyesuaian (excess kurtosis) agar distribusi normal bernilai 0.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.070144`**

#### Fitur 17: `mean_abs_deviation(signal)` — Mean Absolute Deviation (MAD)

- **Domain**: `Statistical`
- **Deskripsi**: Rata-rata jarak simpangan mutlak setiap titik konsentrasi harian terhadap nilai rata-rata sampel.
- **Rumus Matematis**:
  $$
  MAD = \frac{1}{N} \sum_{i=1}^{N} |x_i - \mu|
  $$
- **Penjelasan Notasi Rumus**: Di mana $|x_i - \mu|$ adalah jarak absolut selisih sampel terhadap mean.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.002088`**

#### Fitur 18: `median_abs_deviation(signal)` — Median Absolute Deviation (MAD-Med)

- **Domain**: `Statistical`
- **Deskripsi**: Median dari selisih absolut setiap observasi terhadap nilai median, merupakan parameter dispersi yang paling kebal terhadap anomali.
- **Rumus Matematis**:
  $$
  MAD_{med} = \text{median}\left(|x_i - \tilde{x}|\right)
  $$
- **Penjelasan Notasi Rumus**: Di mana $\tilde{x}$ adalah nilai median dari seluruh deret konsentrasi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.001800`**

#### Fitur 19: `pk_pk_distance(signal)` — Peak to Peak Distance

- **Domain**: `Statistical`
- **Deskripsi**: Jarak rentang penuh dari puncak konsentrasi tertinggi ke lembah terendah selama periode observasi.
- **Rumus Matematis**:
  $$
  \Delta x_{p-p} = x_{max} - x_{min}
  $$
- **Penjelasan Notasi Rumus**: Di mana $x_{max}$ adalah nilai maksimum dan $x_{min}$ adalah nilai minimum data.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.015646`**

#### Fitur 20: `rms(signal)` — Root Mean Square (RMS)

- **Domain**: `Statistical`
- **Deskripsi**: Akar kuadrat dari nilai rata-rata kuadrat sinyal, mencerminkan magnitudo efektif kekuatan sinyal konsentrasi CO.
- **Rumus Matematis**:
  $$
  x_{rms} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana $x_{rms}$ dihitung dengan mengkuadratkan setiap titik, merata-ratakannya, lalu menarik akar kuadrat.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.028702`**

#### Fitur 21: `skewness(signal)` — Skewness

- **Domain**: `Statistical`
- **Deskripsi**: Mengukur derajat asimetri atau kemencengan kurva distribusi konsentrasi CO terhadap nilai rata-ratanya.
- **Rumus Matematis**:
  $$
  \text{Skew} = \frac{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^3}{\left(\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2\right)^{3/2}}
  $$
- **Penjelasan Notasi Rumus**: Nilai positif mengindikasikan kurva memiliki ekor lebih panjang di sisi kanan (konsentrasi tinggi sesekali).
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.224357`**

### 4.2 Domain Temporal (15 Fitur)

Domain **Temporal** berfokus pada analisis 
karakteristik urutan waktu, laju fluktuasi harian, memori lag, autokorelasi, dan dinamika pembalikan arah sinyal.

#### Fitur 22: `auc(signal, fs)` — Area Under the Curve (AUC)

- **Domain**: `Temporal`
- **Deskripsi**: Menghitung luas total area di bawah kurva konsentrasi CO menggunakan aturan integrasi trapesium numerik.
- **Rumus Matematis**:
  $$
  AUC = \sum_{i=1}^{N-1} \frac{x_i + x_{i+1}}{2} \Delta t
  $$
- **Penjelasan Notasi Rumus**: Di mana $\Delta t = 1/f_s$ adalah interval waktu antar dua sampel harian berturut-turut.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.104004`**

#### Fitur 23: `autocorr(signal)` — Autocorrelation 1/e Crossing

- **Domain**: `Temporal`
- **Deskripsi**: Menentukan lag waktu pertama saat fungsi autokorelasi sinyal meluruh di bawah nilai $1/e \approx 0.368$, mengukur durasi memori jangka pendek sinyal.
- **Rumus Matematis**:
  $$
  \tau^* = \arg\min_{\tau} \left( \frac{\sum (x_i - \mu)(x_{i+\tau} - \mu)}{\sum (x_i - \mu)^2} \le \frac{1}{e} \right)
  $$
- **Penjelasan Notasi Rumus**: Di mana $\tau$ adalah lag hari dan $e \approx 2.71828$ adalah bilangan natural Euler.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`2.000000`**

#### Fitur 24: `calc_centroid(signal, fs)` — Temporal Centroid

- **Domain**: `Temporal`
- **Deskripsi**: Menentukan pusat massa waktu dari sinyal konsentrasi, mengindikasikan kecenderungan waktu di mana emisi polutan terpusat.
- **Rumus Matematis**:
  $$
  C_t = \frac{\sum_{i=1}^{N} t_i \cdot x_i}{\sum_{i=1}^{N} x_i}
  $$
- **Penjelasan Notasi Rumus**: Di mana $t_i$ adalah koordinat waktu dan $x_i$ adalah bobot konsentrasi CO pada waktu tersebut.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.816485`**

#### Fitur 25: `distance(signal)` — Signal Distance

- **Domain**: `Temporal`
- **Deskripsi**: Total panjang lintasan 2 dimensi (waktu dan konsentrasi) yang ditempuh kurva sinyal sepanjang 365 hari.
- **Rumus Matematis**:
  $$
  D = \sum_{i=1}^{N-1} \sqrt{(\Delta t)^2 + (x_{i+1} - x_i)^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana $\Delta t$ adalah langkah waktu dan $x_{i+1} - x_i$ adalah fluktuasi konsentrasi harian.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`364.001153`**

#### Fitur 26: `lempel_ziv(signal[, threshold])` — Lempel-Ziv Complexity

- **Domain**: `Temporal`
- **Deskripsi**: Mengukur laju kemunculan sub-pola biner baru pada deret waktu yang dinormalisasi terhadap panjang sinyal.
- **Rumus Matematis**:
  $$
  LZC_{norm} = \frac{c(n) \log_2(n)}{n}
  $$
- **Penjelasan Notasi Rumus**: Di mana $c(n)$ adalah jumlah sub-kata biner unik dan $n$ adalah panjang deret sinyal terkuantisasi biner.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.189041`**

#### Fitur 27: `mean_abs_diff(signal)` — Mean Absolute Difference

- **Domain**: `Temporal`
- **Deskripsi**: Rerata perubahan mutlak konsentrasi CO antara dua hari yang berurutan, menggambarkan stabilitas harian.
- **Rumus Matematis**:
  $$
  \overline{|\Delta x|} = \frac{1}{N-1} \sum_{i=1}^{N-1} |x_{i+1} - x_i|
  $$
- **Penjelasan Notasi Rumus**: Di mana $|x_{i+1} - x_i|$ adalah besarnya lonjakan atau penurunan polutan harian.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.001781`**

#### Fitur 28: `mean_diff(signal)` — Mean Difference

- **Domain**: `Temporal`
- **Deskripsi**: Rerata selisih berarah antar hari berurutan, mencerminkan gradien tren linear netto sepanjang tahun.
- **Rumus Matematis**:
  $$
  \overline{\Delta x} = \frac{1}{N-1}\sum_{i=1}^{N-1}(x_{i+1} - x_i) = \frac{x_N - x_1}{N-1}
  $$
- **Penjelasan Notasi Rumus**: Di mana nilai positif menunjukkan kecenderungan kenaikan konsentrasi secara keseluruhan.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000002`**

#### Fitur 29: `median_abs_diff(signal)` — Median Absolute Difference

- **Domain**: `Temporal`
- **Deskripsi**: Nilai tengah (median) dari perubahan mutlak konsentrasi antardua hari observasi berturut-turut.
- **Rumus Matematis**:
  $$
  \widetilde{|\Delta x|} = \text{median}\left(|x_{i+1} - x_i|\right)
  $$
- **Penjelasan Notasi Rumus**: Di mana median diambil dari seluruh himpunan selisih harian absolut.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.001196`**

#### Fitur 30: `median_diff(signal)` — Median Difference

- **Domain**: `Temporal`
- **Deskripsi**: Nilai median dari selisih berarah harian, memberikan estimasi laju perubahan harian yang kebal fluktuasi temporer.
- **Rumus Matematis**:
  $$
  \widetilde{\Delta x} = \text{median}\left(x_{i+1} - x_i\right)
  $$
- **Penjelasan Notasi Rumus**: Di mana nilai median diambil dari selisih berarah bertanda positif atau negatif.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-0.000085`**

#### Fitur 31: `negative_turning(signal)` — Negative Turning Points

- **Domain**: `Temporal`
- **Deskripsi**: Menghitung banyaknya titik balik lembah (lokal minimum) di mana tren harian berbalik dari menurun menjadi meningkat.
- **Rumus Matematis**:
  $$
  N_{neg} = \sum_{i=2}^{N-1} \mathbf{1}_{\{x_i < x_{i-1} \ \land \ x_i < x_{i+1}\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana kondisi terpenuhi saat nilai titik ke-$i$ lebih rendah daripada kedua tetangganya.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`72.000000`**

#### Fitur 32: `neighbourhood_peaks(signal[, n])` — Neighbourhood Peaks

- **Domain**: `Temporal`
- **Deskripsi**: Menghitung jumlah puncak lokal dominan yang menonjol melebihi nilai seluruh sampel dalam jendela ketetanggaan radius $n$.
- **Rumus Matematis**:
  $$
  N_{peaks} = \sum_{i=1+n}^{N-n} \mathbf{1}_{\{x_i = \max(x_{i-n : i+n})\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana $n$ adalah ukuran jendela radius ketetanggaan pengujian puncak.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`16.000000`**

#### Fitur 33: `positive_turning(signal)` — Positive Turning Points

- **Domain**: `Temporal`
- **Deskripsi**: Menghitung banyaknya titik balik puncak (lokal maksimum) di mana tren harian berbalik dari meningkat menjadi menurun.
- **Rumus Matematis**:
  $$
  N_{pos} = \sum_{i=2}^{N-1} \mathbf{1}_{\{x_i > x_{i-1} \ \land \ x_i > x_{i+1}\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana kondisi terpenuhi saat nilai titik ke-$i$ lebih tinggi daripada kedua tetangganya.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`71.000000`**

#### Fitur 34: `slope(signal)` — Temporal Slope

- **Domain**: `Temporal`
- **Deskripsi**: Kemiringan garis regresi linear dari tren konsentrasi CO terhadap sumbu urutan waktu.
- **Rumus Matematis**:
  $$
  \beta = \frac{\sum_{i=1}^{N}(t_i - \bar{t})(x_i - \bar{x})}{\sum_{i=1}^{N}(t_i - \bar{t})^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana $\beta$ adalah gradien linear tren waktu $t_i$ terhadap konsentrasi polutan $x_i$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-0.000000`**

#### Fitur 35: `sum_abs_diff(signal)` — Sum Absolute Difference

- **Domain**: `Temporal`
- **Deskripsi**: Jumlahan kumulatif dari seluruh perubahan nilai absolut harian konsentrasi CO di sepanjang tahun.
- **Rumus Matematis**:
  $$
  \sum |\Delta x| = \sum_{i=1}^{N-1} |x_{i+1} - x_i|
  $$
- **Penjelasan Notasi Rumus**: Mencerminkan akumulasi total dinamika osilasi turun-naik polutan di Bangkalan.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.648295`**

#### Fitur 36: `zero_cross(signal)` — Zero Crossing Rate

- **Domain**: `Temporal`
- **Deskripsi**: Menghitung berapa kali sinyal memotong sumbu nol (melewati nilai nol). Karena konsentrasi gas CO selalu bernilai positif, nilainya 0.
- **Rumus Matematis**:
  $$
  ZCR = \sum_{i=1}^{N-1} \mathbf{1}_{\{x_i \cdot x_{i+1} < 0\}}
  $$
- **Penjelasan Notasi Rumus**: Di mana kondisi $x_i \cdot x_{i+1} < 0$ menandakan terjadinya pergantian tanda positif dan negatif.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000000`**

### 4.3 Domain Spectral (26 Fitur)

Domain **Spectral** berfokus pada analisis 
komposisi frekuensi Fourier, spektrogram waktu-frekuensi, dekomposisi koefisien wavelet multi-skala, dan filter bank kepstral (MFCC & LPCC).

#### Fitur 37: `fundamental_frequency(signal, fs)` — Fundamental Frequency

- **Domain**: `Spectral`
- **Deskripsi**: Frekuensi siklik dominan terendah dengan magnitudo spektrum Fourier tertinggi, menandai siklus periodik utama konsentrasi CO.
- **Rumus Matematis**:
  $$
  f_0 = \arg\max_{f > 0} |X(f)|
  $$
- **Penjelasan Notasi Rumus**: Di mana $X(f)$ adalah Transformasi Fourier Diskrit dari deret waktu konsentrasi CO.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.273973`**

#### Fitur 38: `human_range_energy(signal, fs)` — Human Range Energy Ratio

- **Domain**: `Spectral`
- **Deskripsi**: Rasio proporsi energi spektral sinyal pada pita frekuensi 0.6 Hz hingga 2.5 Hz terhadap energi spektrum total.
- **Rumus Matematis**:
  $$
  E_{human} = \frac{\sum_{f \in [0.6, 2.5]} |X(f)|^2}{\sum_{f} |X(f)|^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana pembilang adalah jumlahan daya pada rentang frekuensi gerak aktivitas manusia.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000798`**

#### Fitur 39: `lpcc(signal[, n_coeff])` — Linear Prediction Cepstral Coefficients (LPCC)

- **Domain**: `Spectral`
- **Deskripsi**: 12 koefisien kepstral hasil model prediksi linear autoregresif (LPC) yang menangkap amplop spektral sinyal.
- **Rumus Matematis**:
  $$
  c_m = a_m + \sum_{k=1}^{m-1} \left(1 - \frac{k}{m}\right) a_k c_{m-k}
  $$
- **Penjelasan Notasi Rumus**: Di mana $a_k$ adalah koefisien filter LPC dan $c_m$ adalah koefisien kepstral urutan ke-$m$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`12 koefisien (rentang: [0.5835, 1.3585])`**

#### Fitur 40: `max_frequency(signal, fs)` — Maximum Frequency

- **Domain**: `Spectral`
- **Deskripsi**: Komponen frekuensi tertinggi dalam spektrum Fourier yang masih memiliki magnitudo daya signifikan.
- **Rumus Matematis**:
  $$
  f_{max} = \max \{f : |X(f)| > \theta\}
  $$
- **Penjelasan Notasi Rumus**: Di mana $\theta$ adalah ambang batas daya minimum spektrum.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`39.178082`**

#### Fitur 41: `max_power_spectrum(signal, fs)` — Maximum Power Spectrum

- **Domain**: `Spectral`
- **Deskripsi**: Nilai kerapatan spektrum daya (Power Spectral Density / PSD) maksimum dari frekuensi dominan sinyal.
- **Rumus Matematis**:
  $$
  P_{max} = \max_{f} S_{xx}(f) = \max_f \frac{1}{N}|X(f)|^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $S_{xx}(f)$ adalah fungsi densitas spektrum daya dari sinyal.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.181557`**

#### Fitur 42: `median_frequency(signal, fs)` — Median Frequency

- **Domain**: `Spectral`
- **Deskripsi**: Frekuensi yang membagi total kurva spektrum daya sinyal menjadi dua bagian berenergi sama besar.
- **Rumus Matematis**:
  $$
  f_{med} : \sum_{f=0}^{f_{med}} S_{xx}(f) = \frac{1}{2}\sum_{f=0}^{f_s/2} S_{xx}(f)
  $$
- **Penjelasan Notasi Rumus**: Menggambarkan titik tengah keseimbangan distribusi energi frekuensi sinyal.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000000`**

#### Fitur 43: `mfcc(signal, fs[, ...])` — Mel-Frequency Cepstral Coefficients (MFCC)

- **Domain**: `Spectral`
- **Deskripsi**: 12 koefisien kepstral frekuensi Mel yang memetakan spektrum daya ke skala Mel non-linear.
- **Rumus Matematis**:
  $$
  MFCC_m = \sum_{k=1}^{M} \log(S_k) \cos\left[m\left(k - \frac{1}{2}\right)\frac{\pi}{M}\right]
  $$
- **Penjelasan Notasi Rumus**: Di mana $S_k$ adalah energi pada filter bank Mel ke-$k$ dan $M$ adalah total jumlah filter bank.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`12 koefisien (rentang: [-31.4257, 87.0460])`**

#### Fitur 44: `power_bandwidth(signal, fs)` — Power Bandwidth

- **Domain**: `Spectral`
- **Deskripsi**: Lebar pita frekuensi (bandwidth) yang memuat mayoritas spektrum daya sinyal konsentrasi CO.
- **Rumus Matematis**:
  $$
  BW = f_{high} - f_{low}
  $$
- **Penjelasan Notasi Rumus**: Diukur pada rentang pita frekuensi di mana kerapatan spektrum berada di atas ambang batas 3 dB.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`39.178082`**

#### Fitur 45: `spectral_centroid(signal, fs)` — Spectral Centroid

- **Domain**: `Spectral`
- **Deskripsi**: Titik pusat massa (barycenter) spektrum frekuensi Fourier, menunjukkan apakah energi sinyal condong ke frekuensi rendah atau tinggi.
- **Rumus Matematis**:
  $$
  C_{spec} = \frac{\sum_{k} f_k |X(f_k)|}{\sum_{k} |X(f_k)|}
  $$
- **Penjelasan Notasi Rumus**: Di mana $f_k$ adalah frekuensi pada bin ke-$k$ dan $|X(f_k)|$ adalah magnitudonya.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`7.929206`**

#### Fitur 46: `spectral_decrease(signal, fs)` — Spectral Decrease

- **Domain**: `Spectral`
- **Deskripsi**: Mengukur laju penurunan amplitudo spektral seiring dengan bertambahnya frekuensi.
- **Rumus Matematis**:
  $$
  D_{spec} = \frac{1}{\sum_{k=2}^K |X(f_k)|} \sum_{k=2}^{K} \frac{|X(f_k)| - |X(f_1)|}{k - 1}
  $$
- **Penjelasan Notasi Rumus**: Menunjukkan seberapa cepat energi spektrum meredup pada frekuensi tinggi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-8.151132`**

#### Fitur 47: `spectral_distance(signal, fs)` — Spectral Distance

- **Domain**: `Spectral`
- **Deskripsi**: Jarak kumulatif distribusi kerapatan spektral daya relatif terhadap nilai rata-rata spektrum daya.
- **Rumus Matematis**:
  $$
  D_{sd} = \sum_{k} |S_{xx}(f_k) - \bar{S}|^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $\bar{S}$ adalah nilai rata-rata energi seluruh bin spektrum daya.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-1112.202227`**

#### Fitur 48: `spectral_entropy(signal, fs)` — Spectral Entropy

- **Domain**: `Spectral`
- **Deskripsi**: Entropi Fourier yang mengukur tingkat ketidakteraturan atau kompleksitas distribusi daya spektral frekuensi.
- **Rumus Matematis**:
  $$
  H_{spec} = -\sum_{k} p_k \log_2(p_k), \quad p_k = \frac{|X(f_k)|^2}{\sum_j |X(f_j)|^2}
  $$
- **Penjelasan Notasi Rumus**: Di mana $p_k$ adalah probabilitas daya ternormalisasi pada komponen frekuensi ke-$k$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.851373`**

#### Fitur 49: `spectral_kurtosis(signal, fs)` — Spectral Kurtosis

- **Domain**: `Spectral`
- **Deskripsi**: Mengukur tingkat keruncingan sebaran energi spektral frekuensi di sekitar titik pusat centroid spektralnya.
- **Rumus Matematis**:
  $$
  K_{spec} = \frac{\sum_k (f_k - C_{spec})^4 p_k}{\left(\sum_k (f_k - C_{spec})^2 p_k\right)^2} - 3
  $$
- **Penjelasan Notasi Rumus**: Mengidentifikasi adanya komponen frekuensi harmonik tajam non-stasioner.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`4.501461`**

#### Fitur 50: `spectral_positive_turning(signal, fs)` — Spectral Positive Turning Points

- **Domain**: `Spectral`
- **Deskripsi**: Menghitung jumlah puncak positif pada kurva magnitudo transformasi Fourier (FFT) sinyal.
- **Rumus Matematis**:
  $$
  N_{s-pos} = \sum_{k=2}^{K-1} \mathbf{1}_{\{|X_k| > |X_{k-1}| \ \land \ |X_k| > |X_{k+1}|\}}
  $$
- **Penjelasan Notasi Rumus**: Menunjukkan banyaknya variasi osilasi frekuensi harmonik dalam spektrum CO.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`58.000000`**

#### Fitur 51: `spectral_roll_off(signal, fs)` — Spectral Roll-off

- **Domain**: `Spectral`
- **Deskripsi**: Frekuensi batas atas di mana 95% dari total energi spektral terkonsentrasi di bawahnya.
- **Rumus Matematis**:
  $$
  f_{ro} : \sum_{k=1}^{k_{ro}} |X(f_k)| = 0.95 \sum_{k=1}^{K} |X(f_k)|
  $$
- **Penjelasan Notasi Rumus**: Mengukur batas atas distribusi energi spektrum frekuensi dominan.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`39.178082`**

#### Fitur 52: `spectral_roll_on(signal, fs)` — Spectral Roll-on

- **Domain**: `Spectral`
- **Deskripsi**: Frekuensi batas bawah di mana 5% energi spektral awal mulai terakumulasi.
- **Rumus Matematis**:
  $$
  f_{ron} : \sum_{k=1}^{k_{ron}} |X(f_k)| = 0.05 \sum_{k=1}^{K} |X(f_k)|
  $$
- **Penjelasan Notasi Rumus**: Mengidentifikasi batas awal spektrum energi frekuensi terendah.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.000000`**

#### Fitur 53: `spectral_skewness(signal, fs)` — Spectral Skewness

- **Domain**: `Spectral`
- **Deskripsi**: Mengukur kemencengan asimetri kurva kerapatan spektrum di sekitar titik pusat massa centroidnya.
- **Rumus Matematis**:
  $$
  S_{spec} = \frac{\sum_k (f_k - C_{spec})^3 p_k}{\left(\sum_k (f_k - C_{spec})^2 p_k\right)^{3/2}}
  $$
- **Penjelasan Notasi Rumus**: Nilai positif menandakan energi spektral lebih banyak terkonsentrasi di frekuensi rendah.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.634549`**

#### Fitur 54: `spectral_slope(signal, fs)` — Spectral Slope

- **Domain**: `Spectral`
- **Deskripsi**: Kemiringan garis regresi linear magnitudo Fourier terhadap sumbu spektrum frekuensi.
- **Rumus Matematis**:
  $$
  \text{Slope}_{spec} = \frac{K\sum_k f_k |X_k| - \sum_k f_k \sum_k |X_k|}{K\sum_k f_k^2 - (\sum_k f_k)^2}
  $$
- **Penjelasan Notasi Rumus**: Mengindikasikan kemiringan peluruhan energi spektrum frekuensi tinggi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-0.000444`**

#### Fitur 55: `spectral_spread(signal, fs)` — Spectral Spread

- **Domain**: `Spectral`
- **Deskripsi**: Deviasi standar dari penyebaran spektrum di sekitar pusat massa centroid spektralnya.
- **Rumus Matematis**:
  $$
  \sigma_{spec} = \sqrt{\sum_{k} (f_k - C_{spec})^2 p_k}
  $$
- **Penjelasan Notasi Rumus**: Mengukur lebar dispersi distribusi spektrum di sekitar frekuensi tengah.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`13.189140`**

#### Fitur 56: `spectral_variation(signal, fs)` — Spectral Variation

- **Domain**: `Spectral`
- **Deskripsi**: Mengukur derajat variasi dan ketidakteraturan bentuk spektrum antar komponen frekuensi yang berdampingan.
- **Rumus Matematis**:
  $$
  V_{spec} = 1 - \frac{\sum_k |X_k| |X_{k-1}|}{\sqrt{\sum_k |X_k|^2 \sum_k |X_{k-1}|^2}}
  $$
- **Penjelasan Notasi Rumus**: Mengukur koefisien korelasi ternormalisasi spektral lintas frekuensi berturutan.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.730012`**

#### Fitur 57: `spectrogram_mean_coeff(signal, fs[, bins])` — Spectrogram Mean Coefficient

- **Domain**: `Spectral`
- **Deskripsi**: 32 koefisien rata-rata Power Spectral Density (PSD) untuk setiap pita frekuensi di seluruh rentang spektrogram waktu (STFT).
- **Rumus Matematis**:
  $$
  \overline{PSD}(f_b) = \frac{1}{M} \sum_{m=1}^{M} |STFT(m, f_b)|^2
  $$
- **Penjelasan Notasi Rumus**: Di mana $STFT(m, f_b)$ adalah transformasi Fourier waktu singkat pada jendela waktu ke-$m$ dan pita frekuensi $f_b$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`32 koefisien pita frekuensi (0.00 Hz s/d 50.00 Hz)`**

#### Fitur 58: `wavelet_abs_mean(signal, fs[, wavelet, max_width])` — Wavelet Absolute Mean

- **Domain**: `Spectral`
- **Deskripsi**: Rata-rata magnitudo absolut dari koefisien dekomposisi Wavelet Kontinyu (CWT Mexican Hat) pada 9 skala resolusi.
- **Rumus Matematis**:
  $$
  \overline{|W(a)|} = \frac{1}{N} \sum_{i=1}^{N} |CWT(a, t_i)|
  $$
- **Penjelasan Notasi Rumus**: Di mana $CWT(a, t_i)$ adalah koefisien wavelet pada skala dekomposisi $a \in [1, 9]$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`9 koefisien skala (rentang: [0.0001, 0.0037])`**

#### Fitur 59: `wavelet_energy(signal, fs[, wavelet, max_width])` — Wavelet Energy

- **Domain**: `Spectral`
- **Deskripsi**: Energi spektral total yang dikandung oleh masing-masing skala wavelet kontinyu pada rentang waktu dekomposisi.
- **Rumus Matematis**:
  $$
  E_w(a) = \sqrt{\frac{1}{N}\sum_{i=1}^{N} |CWT(a, t_i)|^2}
  $$
- **Penjelasan Notasi Rumus**: Mencerminkan distribusi energi sinyal pada berbagai skala resolusi waktu-frekuensi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`9 nilai skala (rentang: [0.0025, 0.0113])`**

#### Fitur 60: `wavelet_entropy(signal, fs[, wavelet, max_width])` — Wavelet Entropy

- **Domain**: `Spectral`
- **Deskripsi**: Entropi multi-resolusi yang mengukur ketidakteraturan distribusi energi lintas berbagai skala transformasi wavelet.
- **Rumus Matematis**:
  $$
  H_w = -\sum_{j} p_j \log_2(p_j), \quad p_j = \frac{E_w(j)}{\sum_k E_w(k)}
  $$
- **Penjelasan Notasi Rumus**: Di mana $p_j$ adalah proporsi fraksi energi pada skala wavelet ke-$j$.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`2.130313`**

#### Fitur 61: `wavelet_std(signal, fs[, wavelet, max_width])` — Wavelet Standard Deviation

- **Domain**: `Spectral`
- **Deskripsi**: Simpangan baku dari koefisien transformasi wavelet kontinyu pada masing-masing 9 skala dekomposisi.
- **Rumus Matematis**:
  $$
  \sigma_w(a) = \sqrt{\frac{1}{N}\sum_{i=1}^{N}\left(CWT(a, t_i) - \overline{CWT}(a)\right)^2}
  $$
- **Penjelasan Notasi Rumus**: Mengukur variabilitas persebaran koefisien wavelet pada setiap skala resolusi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`9 nilai skala (rentang: [0.0025, 0.0107])`**

#### Fitur 62: `wavelet_var(signal, fs[, wavelet, max_width])` — Wavelet Variance

- **Domain**: `Spectral`
- **Deskripsi**: Variansi kuadrat dispersi koefisien wavelet kontinyu pada masing-masing skala dekomposisi.
- **Rumus Matematis**:
  $$
  \text{Var}_w(a) = \frac{1}{N}\sum_{i=1}^{N}\left(CWT(a, t_i) - \overline{CWT}(a)\right)^2
  $$
- **Penjelasan Notasi Rumus**: Mengukur daya variansi fluktuasi sinyal pada skala multi-resolusi waktu-frekuensi.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`9 nilai skala (rentang: [0.0000, 0.0001])`**

### 4.4 Domain Fractal (6 Fitur)

Domain **Fractal** berfokus pada analisis 
derajat fraktalitas, sifat *self-similarity*, kompleksitas struktural, eksponen persistensi memori jangka panjang (*Hurst Exponent* dan *DFA*), serta entropi multi-skala.

#### Fitur 63: `dfa(signal)` — Detrended Fluctuation Analysis (DFA)

- **Domain**: `Fractal`
- **Deskripsi**: Menghitung eksponen korelasi jarak jauh ($\alpha$) pada deret waktu non-stasioner setelah membuang tren lokal polynomial.
- **Rumus Matematis**:
  $$
  F(s) = \sqrt{\frac{1}{N}\sum_{k=1}^{N} \left(y_k - y_{n,k}\right)^2} \propto s^\alpha
  $$
- **Penjelasan Notasi Rumus**: Di mana $\alpha \approx 0.828$ mengindikasikan sifat memori jangka panjang (persisten) pada konsentrasi polutan CO.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.827578`**

#### Fitur 64: `higuchi_fractal_dimension(signal)` — Higuchi Fractal Dimension (HFD)

- **Domain**: `Fractal`
- **Deskripsi**: Mengukur dimensi fraktal kurva sinyal dalam domain multi-skala waktu menggunakan metode Higuchi untuk mengukur kekasaran geometris deret waktu.
- **Rumus Matematis**:
  $$
  L(k) \propto k^{-D_H}, \quad D_H = -\lim_{k \to 0} \frac{\log \langle L(k) \rangle}{\log k}
  $$
- **Penjelasan Notasi Rumus**: Di mana $D_H$ adalah dimensi fraktal Higuchi ($1 \le D_H \le 2$). Nilai $1.912$ menandakan kurva fluktuasi konsentrasi CO sangat dinamis dan kompleks.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.911793`**

#### Fitur 65: `hurst_exponent(signal)` — Hurst Exponent

- **Domain**: `Fractal`
- **Deskripsi**: Mengukur persistensi memori jangka panjang deret waktu menggunakan analisis Rescaled Range (R/S). Nilai $H > 0.5$ membuktikan adanya memori persistensi jangka panjang.
- **Rumus Matematis**:
  $$
  \mathbb{E}\left[\frac{R(n)}{S(n)}\right] = C \cdot n^H \implies H = \lim_{n \to \infty} \frac{\log(R/S)}{\log(n)}
  $$
- **Penjelasan Notasi Rumus**: Di mana $R(n)$ adalah rentang deviasi kumulatif dan $S(n)$ adalah standar deviasi sampel. Nilai $H = 0.764 > 0.5$ membuktikan tren polutan CO bersifat persisten (berlanjut).
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`0.764445`**

#### Fitur 66: `maximum_fractal_length(signal)` — Maximum Fractal Length (MFL)

- **Domain**: `Fractal`
- **Deskripsi**: Mengukur panjang kurva fraktal rata-rata pada skala resolusi terkecil dari plot logaritmik estimasi Higuchi.
- **Rumus Matematis**:
  $$
  MFL = \lim_{k \to 1} \log\left(L(k)\right)
  $$
- **Penjelasan Notasi Rumus**: Mengukur kerapatan lintasan kurva fraktal sinyal pada skala mikroskopik.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`-0.101520`**

#### Fitur 67: `mse(signal[, m, maxscale, tolerance])` — Multiscale Entropy (MSE)

- **Domain**: `Fractal`
- **Deskripsi**: Menghitung entropi sampel deret waktu pada berbagai skala temporal coarse-graining, mencerminkan kompleksitas struktural dinamika sistem lingkungan.
- **Rumus Matematis**:
  $$
  MSE = \sum_{\tau=1}^{\tau_{max}} \text{SampEn}\left(y^{(\tau)}, m, r\right)
  $$
- **Penjelasan Notasi Rumus**: Di mana $y^{(\tau)}$ adalah deret waktu hasil coarse-graining pada skala faktor $\tau$, $m$ adalah panjang pola, dan $r$ adalah toleransi kemiripan.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.314635`**

#### Fitur 68: `petrosian_fractal_dimension(signal)` — Petrosian Fractal Dimension (PFD)

- **Domain**: `Fractal`
- **Deskripsi**: Menghitung dimensi fraktal berdasarkan laju pembalikan tanda pada turunan pertama deret sinyal.
- **Rumus Matematis**:
  $$
  D_P = \frac{\log_{10} N}{\log_{10} N + \log_{10}\left(\frac{N}{N + 0.4 \cdot N_\Delta}\right)}
  $$
- **Penjelasan Notasi Rumus**: Di mana $N$ adalah jumlah titik data dan $N_\Delta$ adalah jumlah pergantian tanda turunan pertama.
- **Nilai Hasil Ekstraksi (CO Bangkalan)**: **`1.025300`**

---

## 5. Tabel Ringkasan Seluruh 68 Fitur TSFEL

Tabel di bawah ini merangkum secara terpadu seluruh 68 fitur TSFEL yang telah diekstrak pada konsentrasi polutan CO Bangkalan:

| No | Fungsi TSFEL | Nama Fitur | Domain | Rumus Singkat | Nilai Hasil Ekstraksi |
|:---:|:---|:---|:---:|:---|:---:|
| 1 | `abs_energy(signal)` | Absolute energy | Statistical | $E = \sum_{i=1}^{N} x_i^2$ | 0.300680 |
| 2 | `average_power(signal)` | Average power | Statistical | $P_{avg} = \frac{1}{N} \sum_{i=1}^{N} x_i^2$ | 0.082604 |
| 3 | `calc_max(signal)` | Max | Statistical | $x_{max} = \max_{1 \le i \le N}(x_i)$ | 0.036134 |
| 4 | `calc_mean(signal)` | Mean | Statistical | $\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$ | 0.028584 |
| 5 | `calc_median(signal)` | Median | Statistical | $\tilde{x} = \text{median}(x)$ | 0.028389 |
| 6 | `calc_min(signal)` | Min | Statistical | $x_{min} = \min_{1 \le i \le N}(x_i)$ | 0.020487 |
| 7 | `calc_std(signal)` | Standard deviation | Statistical | $\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2}$ | 0.002595 |
| 8 | `calc_var(signal)` | Variance | Statistical | $\sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2$ | 0.000007 |
| 9 | `ecdf(signal)` | ECDF | Statistical | $\hat{F}_n(t) = \frac{1}{N} \sum_{i=1}^N \mathbf{1}_{x_i \le t}$ | Array (10 nilai, range: [0.0027, 0.0274]) |
| 10 | `ecdf_percentile(signal)` | ECDF Percentile | Statistical | $Q(p) = \inf\{x : \hat{F}_n(x) \ge p\}$ | Array (2 nilai, range: [0.0264, 0.0305]) |
| 11 | `ecdf_percentile_count(signal)` | ECDF Percentile Count | Statistical | $C(p) = \sum_{i=1}^N \mathbf{1}_{x_i \le Q(p)}$ | Array (2 nilai, range: [73.0000, 292.0000]) |
| 12 | `ecdf_slope(signal)` | ECDF Slope | Statistical | $S_{ecdf} = \frac{p_{end} - p_{init}}{Q(p_{end}) - Q(p_{init})}$ | 127.679760 |
| 13 | `entropy(signal)` | Entropy | Statistical | $H(X) = -\sum p(x_i) \log_2 p(x_i)$ | 1.000000 |
| 14 | `hist_mode(signal)` | Histogram mode | Statistical | $M_{hist} = \text{center}(\arg\max \text{Bin})$ | 0.027528 |
| 15 | `interq_range(signal)` | Interquartile range | Statistical | $IQR = Q_3 - Q_1$ | 0.003516 |
| 16 | `kurtosis(signal)` | Kurtosis | Statistical | $\text{Kurt} = \frac{\mu_4}{\sigma^4} - 3$ | 0.070144 |
| 17 | `mean_abs_deviation(signal)` | Mean absolute deviation | Statistical | $MAD = \frac{1}{N}\sum \vert x_i - \mu\vert $ | 0.002088 |
| 18 | `median_abs_deviation(signal)` | Median absolute deviation | Statistical | $MAD_{med} = \text{median}(\vert x_i - \tilde{x}\vert )$ | 0.001800 |
| 19 | `pk_pk_distance(signal)` | Peak to peak distance | Statistical | $\Delta x = x_{max} - x_{min}$ | 0.015646 |
| 20 | `rms(signal)` | Root mean square | Statistical | $x_{rms} = \sqrt{\frac{1}{N}\sum x_i^2}$ | 0.028702 |
| 21 | `skewness(signal)` | Skewness | Statistical | $\text{Skew} = \frac{\mu_3}{\sigma^3}$ | 0.224357 |
| 22 | `auc(signal)` | Area under the curve | Temporal | $AUC \approx \sum \frac{x_i + x_{i+1}}{2} \Delta t$ | 0.104004 |
| 23 | `autocorr(signal)` | Autocorrelation | Temporal | $\tau^* = \arg\min_\tau (R_{xx}(\tau) \le 1/e)$ | 2.000000 |
| 24 | `calc_centroid(signal)` | Centroid | Temporal | $C_t = \frac{\sum t_i \cdot x_i}{\sum x_i}$ | 1.816485 |
| 25 | `distance(signal)` | Signal distance | Temporal | $D = \sum \sqrt{(\Delta t)^2 + (\Delta x)^2}$ | 364.001153 |
| 26 | `lempel_ziv(signal)` | Lempel-Ziv complexity | Temporal | $LZC_{norm} = \frac{c(n)\log_2(n)}{n}$ | 0.189041 |
| 27 | `mean_abs_diff(signal)` | Mean absolute diff | Temporal | $\overline{\vert \Delta x\vert } = \frac{1}{N-1}\sum \vert x_{i+1} - x_i\vert $ | 0.001781 |
| 28 | `mean_diff(signal)` | Mean diff | Temporal | $\overline{\Delta x} = \frac{x_N - x_1}{N-1}$ | 0.000002 |
| 29 | `median_abs_diff(signal)` | Median absolute diff | Temporal | $\widetilde{\vert \Delta x\vert } = \text{median}(\vert x_{i+1} - x_i\vert )$ | 0.001196 |
| 30 | `median_diff(signal)` | Median diff | Temporal | $\widetilde{\Delta x} = \text{median}(x_{i+1} - x_i)$ | -0.000085 |
| 31 | `negative_turning(signal)` | Negative turning points | Temporal | $N_{neg} = \sum \mathbf{1}_{x_i < x_{i-1} \land x_i < x_{i+1}}$ | 72.000000 |
| 32 | `neighbourhood_peaks(signal)` | Neighbourhood peaks | Temporal | $N_{peaks} = \sum \mathbf{1}_{x_i = \max(x_{i-n:i+n})}$ | 16.000000 |
| 33 | `positive_turning(signal)` | Positive turning points | Temporal | $N_{pos} = \sum \mathbf{1}_{x_i > x_{i-1} \land x_i > x_{i+1}}$ | 71.000000 |
| 34 | `slope(signal)` | Slope | Temporal | $\beta = \frac{\sum (t_i - \bar{t})(x_i - \bar{x})}{\sum (t_i - \bar{t})^2}$ | -0.000000 |
| 35 | `sum_abs_diff(signal)` | Sum absolute diff | Temporal | $\sum \vert \Delta x\vert  = \sum \vert x_{i+1} - x_i\vert $ | 0.648295 |
| 36 | `zero_cross(signal)` | Zero crossing rate | Temporal | $ZCR = \sum \mathbf{1}_{x_i \cdot x_{i+1} < 0}$ | 0.000000 |
| 37 | `fundamental_frequency(signal)` | Fundamental frequency | Spectral | $f_0 = \arg\max_{f > 0} \vert X(f)\vert $ | 0.273973 |
| 38 | `human_range_energy(signal)` | Human range energy | Spectral | $E_{human} = \frac{\sum_{f \in [0.6, 2.5]} \vert X(f)\vert ^2}{\sum_f \vert X(f)\vert ^2}$ | 0.000798 |
| 39 | `lpcc(signal)` | LPCC | Spectral | $c_m = a_m + \sum \left(1 - \frac{k}{m}\right) a_k c_{m-k}$ | Array (12 nilai, range: [0.5835, 1.3585]) |
| 40 | `max_frequency(signal)` | Maximum frequency | Spectral | $f_{max} = \max \{f : \vert X(f)\vert  > \text{thresh}\}$ | 39.178082 |
| 41 | `max_power_spectrum(signal)` | Max power spectrum | Spectral | $P_{max} = \max_f S_{xx}(f)$ | 0.181557 |
| 42 | `median_frequency(signal)` | Median frequency | Spectral | $\sum_0^{f_{med}} S(f) = \frac{1}{2}\sum S(f)$ | 0.000000 |
| 43 | `mfcc(signal)` | MFCC | Spectral | $MFCC_m = \sum \log(S_k)\cos[m(k-0.5)\pi/M]$ | Array (12 nilai, range: [-31.4257, 87.0460]) |
| 44 | `power_bandwidth(signal)` | Power bandwidth | Spectral | $BW = f_{high} - f_{low}$ | 39.178082 |
| 45 | `spectral_centroid(signal)` | Spectral centroid | Spectral | $C_{spec} = \frac{\sum f_k \vert X_k\vert }{\sum \vert X_k\vert }$ | 7.929206 |
| 46 | `spectral_decrease(signal)` | Spectral decrease | Spectral | $D_{spec} = \frac{1}{\sum \vert X_k\vert } \sum \frac{\vert X_k\vert  - \vert X_1\vert }{k-1}$ | -8.151132 |
| 47 | `spectral_distance(signal)` | Spectral distance | Spectral | $D_{sd} = \sum \vert S_{xx}(f_k) - \bar{S}\vert ^2$ | -1112.202227 |
| 48 | `spectral_entropy(signal)` | Spectral entropy | Spectral | $H_{spec} = -\sum p_k \log_2(p_k)$ | 0.851373 |
| 49 | `spectral_kurtosis(signal)` | Spectral kurtosis | Spectral | $K_{spec} = \frac{\mu_{4,spec}}{\sigma_{spec}^4} - 3$ | 4.501461 |
| 50 | `spectral_positive_turning(signal)` | Spectral positive turning points | Spectral | $N_{s-pos} = \sum \mathbf{1}_{\vert X_k\vert  > \vert X_{k-1}\vert  \land \vert X_k\vert  > \vert X_{k+1}\vert }$ | 58.000000 |
| 51 | `spectral_roll_off(signal)` | Spectral roll-off | Spectral | $\sum_1^{f_{ro}} \vert X(f)\vert  = 0.95 \sum \vert X(f)\vert $ | 39.178082 |
| 52 | `spectral_roll_on(signal)` | Spectral roll-on | Spectral | $\sum_1^{f_{ron}} \vert X(f)\vert  = 0.05 \sum \vert X(f)\vert $ | 0.000000 |
| 53 | `spectral_skewness(signal)` | Spectral skewness | Spectral | $S_{spec} = \frac{\mu_{3,spec}}{\sigma_{spec}^3}$ | 1.634549 |
| 54 | `spectral_slope(signal)` | Spectral slope | Spectral | $\text{Slope}_{spec} = \frac{\Delta \vert X\vert }{\Delta f}$ | -0.000444 |
| 55 | `spectral_spread(signal)` | Spectral spread | Spectral | $\sigma_{spec} = \sqrt{\sum (f_k - C_{spec})^2 p_k}$ | 13.189140 |
| 56 | `spectral_variation(signal)` | Spectral variation | Spectral | $V_{spec} = 1 - \text{korelasi}(\vert X_k\vert , \vert X_{k-1}\vert )$ | 0.730012 |
| 57 | `spectrogram_mean_coeff(signal)` | Spectrogram mean coefficient | Spectral | $\overline{PSD}(f_b) = \frac{1}{M}\sum \vert STFT\vert ^2$ | Array (32 nilai, range: [0.0000, 0.0000]) |
| 58 | `wavelet_abs_mean(signal)` | Wavelet absolute mean | Spectral | $\overline{\vert W(a)\vert } = \frac{1}{N}\sum \vert CWT(a, t)\vert $ | Array (9 nilai, range: [0.0001, 0.0037]) |
| 59 | `wavelet_energy(signal)` | Wavelet energy | Spectral | $E_w(a) = \sqrt{\frac{1}{N}\sum \vert CWT(a,t)\vert ^2}$ | Array (9 nilai, range: [0.0025, 0.0113]) |
| 60 | `wavelet_entropy(signal)` | Wavelet entropy | Spectral | $H_w = -\sum p_j \log_2(p_j)$ | 2.130313 |
| 61 | `wavelet_std(signal)` | Wavelet standard deviation | Spectral | $\sigma_w(a) = \text{std}(CWT(a, t))$ | Array (9 nilai, range: [0.0025, 0.0107]) |
| 62 | `wavelet_var(signal)` | Wavelet variance | Spectral | $\text{Var}_w(a) = \text{var}(CWT(a, t))$ | Array (9 nilai, range: [0.0000, 0.0001]) |
| 63 | `dfa(signal)` | Detrended fluctuation analysis | Fractal | $F(s) \propto s^\alpha$ | 0.827578 |
| 64 | `higuchi_fractal_dimension(signal)` | Higuchi fractal dimension | Fractal | $L(k) \propto k^{-D_H}$ | 1.911793 |
| 65 | `hurst_exponent(signal)` | Hurst exponent | Fractal | $(R/S)_n \propto n^H$ | 0.764445 |
| 66 | `maximum_fractal_length(signal)` | Maximum fractal length | Fractal | $MFL = \lim_{k \to 1} \log(L(k))$ | -0.101520 |
| 67 | `mse(signal)` | Multiscale entropy | Fractal | $MSE = \sum_{\tau} \text{SampEn}(y^{(\tau)})$ | 1.314635 |
| 68 | `petrosian_fractal_dimension(signal)` | Petrosian fractal dimension | Fractal | $D_P = \frac{\log_{10} N}{\log_{10} N + \log_{10}(N/(N+0.4 N_\Delta))}$ | 1.025300 |

---

## 6. Kesimpulan & Relevansi untuk Tahap Proyek Selanjutnya

1. **Cakupan Fitur Menyeluruh (68 Fungsi / 164 Nilai Numerik)**:
   Proses ekstraksi berhasil mengeksekusi seluruh 68 fungsi fitur yang dimiliki pustaka TSFEL tanpa terkecuali, menghasilkan matriks berdimensi 164 kolom koefisien numerik yang bebas dari nilai *missing* maupun nilai tak berhingga (*infinite*).
2. **Karakteristik Fisik & Dinamika Sinyal CO Bangkalan**:
   - **Rata-rata Konsentrasi**: Rata-rata tahunan konsentrasi CO sebesar $0.028584 \text{ mg/m}^3$ dengan standar deviasi rendah ($0.002595$), menunjukkan kestabilan konsentrasi harian.
   - **Asimetri & Keruncingan**: Nilai *skewness* positif ($0.224357$) dan *kurtosis* ($0.070144$) mencerminkan sedikit kecenderungan adanya hari-hari tertentu dengan emisi polutan yang sedikit lebih pekat.
   - **Persistensi Memori Jangka Panjang**: Nilai *Hurst Exponent* sebesar $H = 0.764445 > 0.5$ dan *DFA* sebesar $\alpha = 0.827578$ membuktikan secara ilmiah bahwa emisi polutan CO di Bangkalan memiliki sifat **memori persistensi kuat** (tren peningkatan atau penurunan akan cenderung berlanjut dalam rentang waktu berikutnya).
   - **Periodisitas Dominan**: *Fundamental Frequency* sebesar $0.273973$ merepresentasikan adanya siklus berulang reguler terkait dinamika mingguan/musiman.
3. **Kesiapan Dataset untuk Pemodelan**:
   Dataset fitur yang tersimpan di `data/csv/pertemuan-3-csv/fitur_tsfel_co_bangkalan.csv` kini siap diintegrasikan untuk pemodelan deret waktu tahap lanjut, peramalan (*forecasting*), maupun klasifikasi anomali lingkungan.
