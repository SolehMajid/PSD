---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Pemrosesan Data Polutan Udara Satelit (Pertemuan 5)

Dokumentasi ini menyajikan alur pemrosesan data deret waktu (*time series*) untuk **4 parameter polutan udara utama** di wilayah **Kecamatan Socah, Kabupaten Bangkalan**: **Metana ($\text{CH}_4$)**, **Karbon Monoksida ($\text{CO}$)**, **Nitrogen Dioksida ($\text{NO}_2$)**, dan **Sulfur Dioksida ($\text{SO}_2$)**.

Materi pada Pertemuan 5 ini mengintegrasikan seluruh tahapan pemrosesan data secara lengkap dan terstruktur:
1. **Crawling Data Satelit Sentinel-5P** menggunakan platform Copernicus OpenEO API.
2. **Visualisasi Peta Wilayah Pengamatan (Folium)** menggunakan koordinat variabel AOI (*Area of Interest*) Kecamatan Socah.
3. **Deteksi dan Pembersihan Outlier** menggunakan metode non-parametrik **Interquartile Range (IQR / Tukey's Fences)**.
4. **Penambalan Missing Values Bertahap** menggunakan metode **Interpolasi Polinomial Orde 2** (menghasilkan dataset 365 hari penuh tanpa nilai kosong).
5. **Ekstraksi 68 Fitur Runtun Waktu** menggunakan pustaka **TSFEL (*Time Series Feature Extraction Library*)** menjadi satu matriks terstandarisasi.

---

## Berkas Terkait di Folder `pertemuan-5`

Seluruh skrip dan notebook pemrosesan tersimpan secara mandiri di dalam folder `pertemuan-5/`:

| Berkas / Notebook | Jenis | Deskripsi Pemrosesan |
| :--- | :--- | :--- |
| [`1.zat-ch4.ipynb`](1.zat-ch4.ipynb) | Jupyter Notebook | Penarikan data satelit Sentinel-5P L2 untuk polutan Metana ($\text{CH}_4$) via openEO. |
| [`1.zat-co.ipynb`](1.zat-co.ipynb) | Jupyter Notebook | Penarikan data satelit Sentinel-5P L2 untuk polutan Karbon Monoksida ($\text{CO}$) via openEO. |
| [`1.zat-no2.ipynb`](1.zat-no2.ipynb) | Jupyter Notebook | Penarikan data satelit Sentinel-5P L2 untuk polutan Nitrogen Dioksida ($\text{NO}_2$) via openEO. |
| [`1.zat-so2.ipynb`](1.zat-so2.ipynb) | Jupyter Notebook | Penarikan data satelit Sentinel-5P L2 untuk polutan Sulfur Dioksida ($\text{SO}_2$) via openEO. |
| [`code-map.ipynb`](code-map.ipynb) | Jupyter Notebook | Visualisasi peta interaktif batas wilayah pengamatan (*Area of Interest* / AOI) Kecamatan Socah, Bangkalan menggunakan Folium. |
| [`detec-outlier-iqr.ipynb`](detec-outlier-iqr.ipynb) | Jupyter Notebook | Identifikasi dan pembersihan nilai pencilan (*outlier*) menggunakan metode IQR murni. |
| [`interpolasi-polinomial.ipynb`](interpolasi-polinomial.ipynb) | Jupyter Notebook | Penambalan missing value secara bertahap menggunakan interpolasi kurva polinomial orde 2. |
| [`ekstaksi-fitur-4-polutan.ipynb`](ekstaksi-fitur-4-polutan.ipynb) | Jupyter Notebook | Ekstraksi 68 fitur TSFEL untuk 4 polutan menjadi matriks 4 baris × 69 kolom. |

---

## 1. Crawling Data Satelit (`1.zat-parameternya.ipynb`)

### 1.1 Penjelasan Sederhana
* **Inti:** Mengambil data konsentrasi gas polutan secara otomatis langsung dari instrumen sensor satelit Sentinel-5P Level 2 via platform Copernicus OpenEO menggunakan Python.
* **Cara Kerja:** Kode program menghubungi server OpenEO, memasukkan poligon koordinat batas wilayah (AOI Kecamatan Socah), menetapkan rentang tanggal 1 tahun (24 Agustus 2025 s.d. 24 Agustus 2026), mengunduh file agregasi harian berformat NetCDF (`.nc`), lalu mengekstraknya ke file tabel `.csv`.
* **Manfaat:** Menghemat waktu dibanding pengunduhan manual yang rumit, data dijamin akurat langsung dari satelit resmi ESA/Copernicus, dan format deret waktu harian konsisten.

### 1.2 Batasan Spasial Koordinat (Spatial Extent)
Koordinat batas geografis (*bounding box*) poligon yang digunakan pada pemanggilan fungsi `load_collection`:
* **Longitude Min (`west`)**: `112.6736254°`
* **Longitude Max (`east`)**: `112.7899726°`
* **Latitude Min (`south`)**: `-7.1242393°`
* **Latitude Max (`north`)**: `-7.0522304°`

### 1.3 Source Code Penting: Pengambilan Data OpenEO
```python
import openeo

# 1. Autentikasi ke Copernicus Data Space Ecosystem (CDSE)
connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

# 2. Definisikan poligon batas wilayah studi (AOI Socah)
aoi = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [112.6736254, -7.063601], [112.6736254, -7.075242],
                        [112.6865832, -7.0936504], [112.7010414, -7.0960868],
                        [112.7059517, -7.1058321], [112.7018597, -7.1196376],
                        [112.7283209, -7.1242393], [112.7446886, -7.1155772],
                        [112.7479622, -7.1055614], [112.7738777, -7.1131409],
                        [112.7899726, -7.1109754], [112.7866991, -7.0841756],
                        [112.7648755, -7.0871534], [112.7689674, -7.077137],
                        [112.7528725, -7.0749713], [112.7441430, -7.0592693],
                        [112.7062245, -7.0525011], [112.6759442, -7.0522304],
                        [112.6739496, -7.0571792], [112.6736254, -7.063601]
                    ]
                ]
            }
        }
    ]
}

# 3. Muat koleksi data satelit Sentinel-5P L2
datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent={
        "west": 112.6736254,
        "south": -7.1242393,
        "east": 112.7899726,
        "north": -7.0522304
    },
    bands=["CO"],  # Disesuaikan: CH4, CO, NO2, atau SO2
)

# 4. Agregasi nilai temporal harian dan spasial rata-rata area poligon
datacube = datacube.aggregate_temporal_period(reducer="mean", period="day")
datacube = datacube.aggregate_spatial(reducer="mean", geometries=aoi)

# 5. Jalankan proses batch job dan unduh file NetCDF (.nc)
job = datacube.execute_batch(
    title="CO Socah Bangkalan",
    outputfile="../data/nc/pertemuan-5-nc/polutan_co_bangkalan.nc"
)
```

---

## 2. Visualisasi Peta (folium)

Lokasi pengamatan di Kabupaten Bangkalan divisualisasikan pada **peta interaktif** menggunakan library **`folium`** pada file [code-map.ipynb](code-map.ipynb). Area polygon AOI ditandai pada peta.

```{code-cell}
:tags: [hide-input]
import folium

aoi = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              112.6736254,
              -7.063601
            ],
            [
              112.6736254,
              -7.075242
            ],
            [
              112.6865832,
              -7.0936504
            ],
            [
              112.7010414,
              -7.0960868
            ],
            [
              112.7059517,
              -7.1058321
            ],
            [
              112.7018597,
              -7.1196376
            ],
            [
              112.7283209,
              -7.1242393
            ],
            [
              112.7446886,
              -7.1155772
            ],
            [
              112.7479622,
              -7.1055614
            ],
            [
              112.7738777,
              -7.1131409
            ],
            [
              112.7899726,
              -7.1109754
            ],
            [
              112.7866991,
              -7.0841756
            ],
            [
              112.7648755,
              -7.0871534
            ],
            [
              112.7689674,
              -7.077137
            ],
            [
              112.7528725,
              -7.0749713
            ],
            [
              112.744143,
              -7.0592693
            ],
            [
              112.7062245,
              -7.0525011
            ],
            [
              112.6759442,
              -7.0522304
            ],
            [
              112.6739496,
              -7.0571792
            ],
            [
              112.6736254,
              -7.063601
            ]
          ]
        ]
      }
    }
  ]
}

# Titik tengah AOI
center_lat = (-7.1242393 + -7.0522304) / 2
center_lon = (112.6736254 + 112.7899726) / 2

# Buat peta
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# Tambahkan AOI
folium.GeoJson(
    aoi,
    name="AOI",
    style_function=lambda feature: {
        "fillColor": "blue",
        "color": "red",
        "weight": 2,
        "fillOpacity": 0.3
    }
).add_to(m)

# Tambahkan kontrol layer
folium.LayerControl().add_to(m)

# Tampilkan
m
```

```{figure} ../assets/images/images_pertemuan-5/1.peta_aoi_socah_bangkalan.png
:width: 90%
:align: center

Visualisasi Peta Spasial Batas Poligon Area of Interest (AOI) Kecamatan Socah, Kabupaten Bangkalan menggunakan Folium dan Basemap OpenStreetMap.
```

---

## 3. Deteksi Outlier dengan Metode IQR (`detec-outlier-iqr.ipynb`)

### 3.1 Penjelasan Sederhana
* **Inti:** Menemukan dan memisahkan "data aneh" (pencilan) yang nilainya melonjak terlalu tinggi atau anjlok terlalu rendah akibat derau (*noise*) sensor satelit menggunakan batas persentil kuartil.
* **Cara Kerja:** Menggunakan metode **Interquartile Range (IQR)** dengan aturan pagar Tukey (*Tukey's Fences*). Rentang tengah data ($IQR = Q_3 - Q_1$) digunakan untuk membuat batas pagar aman:
  $$\text{Batas Bawah} = Q_1 - 1.5 \times IQR$$
  $$\text{Batas Atas} = Q_3 + 1.5 \times IQR$$
  Nilai pengamatan yang jatuh di luar batas aman dicatat ke dalam katalog outlier, kemudian nilainya diubah menjadi `NaN` agar dapat ditambal secara kontinu pada tahap berikutnya.
* **Manfaat:** Berbeda dengan Z-Score yang mengasumsikan kurva normal simetris, metode IQR bersifat **non-parametrik dan kebal (*robust*)** terhadap lonjakan ekstrem, sehingga sangat cocok untuk data emisi polutan yang cenderung miring (*skewed*).

### 3.2 Source Code Penting: Deteksi Outlier IQR
```python
import pandas as pd
import numpy as np

# 1. Baca data mentah 4 polutan
df = pd.read_csv("data/csv/pertemuan-5-csv/Hasil Polutan.csv")
pollutants = ['CH4', 'CO', 'NO2', 'SO2']

# 2. Hitung kuartil dan pagar IQR per polutan
all_outliers_records = []
for p in pollutants:
    valid_data = df[p].dropna()
    q1 = valid_data.quantile(0.25)
    q3 = valid_data.quantile(0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    
    # Identifikasi titik di luar pagar aman
    outliers = valid_data[(valid_data < lower_fence) | (valid_data > upper_fence)]
    for idx, val in outliers.items():
        all_outliers_records.append({
            'Polutan': p,
            'Hari ke-': idx + 1,
            'Tanggal': df.loc[idx, 'tanggal'],
            'Nilai': val,
            'Q1': q1, 'Q3': q3, 'IQR': iqr,
            'Batas Bawah': lower_fence, 'Batas Atas': upper_fence,
            'Kategori': 'Pencilan Atas' if val > upper_fence else 'Pencilan Bawah'
        })

df_outliers = pd.DataFrame(all_outliers_records)

# 3. Simpan daftar outlier ke CSV
df_outliers.to_csv("data/csv/pertemuan-5-csv/clean outlier/daftar_outlier_iqr.csv", index=False)

# 4. Bersihkan dataset: ubah outlier menjadi NaN
df_clean = df.copy()
for r in all_outliers_records:
    df_clean.loc[df_clean['tanggal'] == r['Tanggal'], r['Polutan']] = np.nan

# 5. Simpan dataset hasil pembersihan
df_clean.to_csv("data/csv/pertemuan-5-csv/clean outlier/polutan_4_clean_iqr.csv", index=False)
```

### 3.3 Visualisasi Hasil Deteksi Outlier IQR
Visualisasi deret waktu 4 polutan dengan batas zona aman IQR (area hijau), batas pagar atas/bawah (garis putus-putus), dan sebaran **21 titik data outlier** (tanda silang merah):

```{figure} ../assets/images/images_pertemuan-5/2.deteksi_outlier_iqr_4polutan.png
:width: 100%
:align: center

Visualisasi Deret Waktu 4 Polutan dengan Zona Pagar Aman IQR dan Sebaran 21 Titik Outlier.
```

### 3.4 Rekapitulasi dan Daftar Rincian Outlier
*Tabel Parameter Batas Pagar IQR per Polutan:*

| Polutan | $Q_1$ (25%) | $Q_3$ (75%) | $IQR$ | Batas Bawah | Batas Atas | Outlier Terdeteksi | Data Bersih |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH4** | $1881.69$ | $1907.41$ | $25.73$ | $1843.10$ | $1946.00$ | **0** | $17$ hari |
| **CO** | $0.026558$ | $0.030827$ | $0.004269$ | $0.020154$ | $0.037231$ | **2** | $212$ hari |
| **NO2** | $0.000019$ | $0.000039$ | $0.000020$ | $-0.000011$ | $0.000069$ | **7** | $181$ hari |
| **SO2** | $-0.000093$ | $0.000144$ | $0.000237$ | $-0.000448$ | $0.000500$ | **12** | $218$ hari |
| **Total** | - | - | - | - | - | **21 Outlier** | **628 hari** |

*Rincian 21 Titik Outlier yang Terdeteksi:*
1. **CO (2 titik)**:
   * Hari ke-45 (`2025-10-07`): Nilai $= 0.046483\text{ mol/m}^2$ (Pencilan Atas, Batas Atas $= 0.037231$).
   * Hari ke-48 (`2025-10-10`): Nilai $= 0.037367\text{ mol/m}^2$ (Pencilan Atas, Batas Atas $= 0.037231$).
2. **NO2 (7 titik)**: Seluruhnya merupakan pencilan atas yang melampaui batas $0.000069\text{ mol/m}^2$:
   * Hari ke-46 (`2025-10-08`), Hari ke-109 (`2025-12-10`), Hari ke-207 (`2026-03-18`), Hari ke-229 (`2026-04-09`), Hari ke-276 (`2026-05-26`), Hari ke-279 (`2026-05-29`), dan Hari ke-352 (`2026-08-10`).
3. **SO2 (12 titik)**:
   * **7 Pencilan Bawah** ($< -0.000448\text{ mol/m}^2$): Nilai anomali negatif sensor satelit pada tanggal `2025-08-26`, `2025-09-06`, `2025-11-20`, `2026-01-09`, `2026-06-26`, `2026-08-07`, dan `2026-08-13`.
   * **5 Pencilan Atas** ($> +0.000500\text{ mol/m}^2$): Lonjakan konsentrasi SO2 pada tanggal `2026-06-09`, `2026-06-10`, `2026-06-21`, `2026-07-08`, dan `2026-08-02`.
4. **CH4 (0 titik)**: Tidak ditemukan outlier karena sebaran konsentrasi metana pada 17 hari valid berada seragam di dalam batas aman $[1843.10, 1946.00]\text{ ppb}$.

---

## 4. Penambalan Missing Values dengan Interpolasi Polinomial (`interpolasi-polinomial.ipynb`)

### 4.1 Penjelasan Sederhana
* **Inti:** Mengisi data yang kosong (*missing values*) menggunakan estimasi kurva matematika lengkung yang mulus (*smooth curve*), bukan sekadar garis lurus kaku atau nilai rata-rata datar.
* **Cara Kerja:** Menerapkan fungsi polinomial kuadratik orde 2 ($P(x) = ax^2 + bx + c$) untuk menghubungkan titik-titik data observasi asli yang ada. Titik tanggal kosong diisi dengan nilai yang berada tepat di sepanjang kurva tersebut. Nilai kosong pada ujung tepi awal atau akhir disempurnakan dengan `bfill()` dan `ffill()`.
* **Manfaat:** Menghasilkan deret waktu 365 hari penuh tanpa celah (0 NaN) dengan lengkungan transisi yang lebih alami dan realistis sesuai dinamika konsentrasi gas di atmosfer.

### 4.2 Mengapa Memilih Polinomial Orde 2?
1. **Interpolasi Linear (Orde 1)** menghasilkan patahan sudut kaku pada titik-titik balik yang tidak mencerminkan sifat fluida atmosfer.
2. **Interpolasi Polinomial Orde 3 (Kubik)** rentan terhadap fenomena *Runge's Phenomenon* (osilasi liar pada celah data kosong yang lebar).
3. **Interpolasi Polinomial Orde 2 (Kuadratik)** memberikan kelengkungan alami yang fleksibel namun tetap stabil dan terikat erat pada tren lokal data.

### 4.3 Source Code Penting: Interpolasi Polinomial
```python
import pandas as pd
import numpy as np

# 1. Baca dataset hasil pembersihan outlier IQR
df_clean = pd.read_csv("data/csv/pertemuan-5-csv/clean outlier/polutan_4_clean_iqr.csv")
df_imputed = df_clean.copy()

# 2. Terapkan interpolasi polinomial orde 2 dan penanganan batas ujung
for p in ['CH4', 'CO', 'NO2', 'SO2']:
    df_imputed[p] = df_clean[p].interpolate(method='polynomial', order=2).bfill().ffill()

# 3. Verifikasi ketiadaan missing value (wajib 0 NaN)
print("Sisa missing value per polutan:")
print(df_imputed[['CH4', 'CO', 'NO2', 'SO2']].isna().sum())

# 4. Simpan satu berkas final bersih ke folder 'data bersih'
output_clean = "data/csv/pertemuan-5-csv/data bersih/polutan_4_clean.csv"
df_imputed[['tanggal', 'CH4', 'CO', 'NO2', 'SO2']].to_csv(output_clean, index=False)
print("Dataset bersih berhasil disimpan ke:", output_clean)
```

### 4.4 Visualisasi Hasil Imputasi Polinomial
Visualisasi 365 hari penuh memperlihatkan garis kurva kontinu hasil penambalan (garis tebal), titik observasi asli (lingkaran warna), dan titik imputasi (titik merah):

```{figure} ../assets/images/images_pertemuan-5/3.hasil_interpolasi_polinomial_4polutan.png
:width: 100%
:align: center

Visualisasi Runtun Waktu Lengkap 4 Polutan Setelah Penambalan Nilai Kosong dengan Interpolasi Polinomial Orde 2.
```

### 4.5 Rekapitulasi Hasil Penambalan Data
*Tabel Kelengkapan Data 4 Polutan (365 Hari Sempurna):*

| Polutan | Total Hari | Data Valid Awal | Outlier Dibuang | Data Asli Valid | Data Ditambal (Interpolasi) | Sisa NaN (Akhir) | Status Kelengkapan |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CH4** | 365 hari | 17 | 0 | 17 hari | **348 hari** | **0** | **100% Sempurna ✓** |
| **CO** | 365 hari | 214 | 2 | 212 hari | **153 hari** | **0** | **100% Sempurna ✓** |
| **NO2** | 365 hari | 188 | 7 | 181 hari | **184 hari** | **0** | **100% Sempurna ✓** |
| **SO2** | 365 hari | 230 | 12 | 218 hari | **147 hari** | **0** | **100% Sempurna ✓** |

---

## 5. Ekstraksi Fitur Runtun Waktu TSFEL (`ekstaksi-fitur-4-polutan.ipynb`)

### 5.1 Penjelasan Sederhana
* **Inti:** Mengubah deret angka panjang 365 hari menjadi kumpulan angka ringkasan karakteristik (*features*) yang mewakili sifat unik masing-masing polutan.
* **Cara Kerja:** Pustaka **TSFEL** mengekstrak 68 formula matematika dari 4 domain sinyal utama:
  1. **Domain Statistik (22 fitur)**: Mengukur rata-rata, variansi, kemiringan kurva (*skewness*), kurtosis, dan energi sinyal total.
  2. **Domain Temporal (15 fitur)**: Mengukur dinamika waktu, panjang lintasan (*distance*), autokorelasi, dan titik perlintasan garis nol (*zero crossing*).
  3. **Domain Spektral (27 fitur)**: Menganalisis kerapatan daya spektrum frekuensi Fourier (FFT), frekuensi median, dan pusat spektral.
  4. **Domain Fraktal (4 fitur)**: Menganalisis tingkat kompleksitas bentuk kurva dan memori jangka panjang (*Hurst Exponent*).
  
  Hasil ekstraksi disusun menjadi **Matriks Horizontal 4 Baris × 69 Kolom** (1 kolom identitas `Polutan` + 68 kolom fitur numerik `f1_abs_energy` s.d. `f68_zero_cross`).
* **Manfaat:** Algoritma Machine Learning (seperti K-Means Clustering) tidak perlu memproses 365 tanggal satu per satu, melainkan langsung belajar dari 68 fitur karakteristik ini.

### 5.2 Source Code Penting: Ekstraksi Fitur TSFEL
```python
import tsfel
import pandas as pd

# 1. Konfigurasi seluruh fitur aktif dari 4 domain TSFEL
cfg = tsfel.get_features_by_domain()
for domain in cfg:
    for feat in cfg[domain]:
        cfg[domain][feat]['use'] = 'yes'

# 2. Baca dataset bersih 365 hari
df_clean = pd.read_csv("data/csv/pertemuan-5-csv/data bersih/polutan_4_clean.csv")

# 3. Ekstraksi fitur untuk setiap polutan
results = []
for pol in ['CH4', 'CO', 'NO2', 'SO2']:
    series = df_clean[pol]
    feat_df = tsfel.time_series_features_extractor(cfg, series.to_frame(pol), fs=1, verbose=0)
    feat_df.insert(0, 'Polutan', pol)
    results.append(feat_df)
    
    # Simpan juga file ekstraksi individual 1 baris
    feat_df.to_csv(f"data/csv/pertemuan-5-csv/ekstraksi fitur/fitur_68_{pol.lower()}_1baris.csv", index=False)

# 4. Gabungkan ke dalam satu matriks horizontal 4 baris x 69 kolom
df_all_features = pd.concat(results, ignore_index=True)
output_matrix = "data/csv/pertemuan-5-csv/ekstraksi fitur/fitur_68_4_polutan.csv"
df_all_features.to_csv(output_matrix, index=False)
print("Matriks fitur 4 baris x 69 kolom berhasil disimpan ke:", output_matrix)
```

### 5.3 Visualisasi Komparasi Fitur Kunci Antar Polutan
Perbandingan nilai fitur-fitur kunci terstandarisasi antara CH4, CO, NO2, dan SO2:

```{figure} ../assets/images/images_pertemuan-5/4.komparasi_fitur_tsfel_4polutan.png
:width: 90%
:align: center

Perbandingan Nilai Fitur Kunci TSFEL Terstandarisasi Antar 4 Polutan Udara di Kecamatan Socah.
```

### 5.4 Rangkuman Fitur Kunci 4 Polutan Berdasarkan Domain
Tabel berikut merangkum fitur-fitur paling esensial yang mewakili 4 domain keilmuan TSFEL:

| Domain Fitur | Parameter Fitur TSFEL | CH4 (Metana) | CO (Karbon Monoksida) | NO2 (Nitrogen Dioksida) | SO2 (Sulfur Dioksida) | Makna Analisis |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **Statistik** | Rata-rata (`f7_calc_mean`) | $1426.63\text{ ppb}$ | $0.0282\text{ mol/m}^2$ | $2.45 \times 10^{-5}\text{ mol/m}^2$ | $4.01 \times 10^{-5}\text{ mol/m}^2$ | Skala besaran konsentrasi gas tipikal |
| **Statistik** | Simpangan Baku (`f10_calc_std`) | $412.16$ | $0.0033$ | $2.34 \times 10^{-5}$ | $2.60 \times 10^{-4}$ | Derajat variabilitas harian |
| **Statistik** | Konsentrasi Puncak (`f6_calc_max`) | $2121.14$ | $0.0367$ | $7.99 \times 10^{-5}$ | $7.23 \times 10^{-4}$ | Titik tertinggi konsentrasi polutan |
| **Temporal** | Panjang Lintasan (`f13_distance`) | $3081.70$ | $364.00$ | $364.00$ | $364.00$ | Akumulasi perubahan deret waktu |
| **Temporal** | Perlintasan Garis Nol (`f68_zero_cross`) | $0\text{ kali}$ | $0\text{ kali}$ | $18\text{ kali}$ | $101\text{ kali}$ | Frekuensi osilasi di sekitar nilai nol |
| **Spektral** | Daya Spektrum Maks (`f29_max_power`) | $0.2513$ | $0.1816$ | $0.5314$ | $0.2134$ | Puncak kerapatan spektrum FFT |
| **Fraktal** | Hurst Exponent (`f23_hurst_exp`) | **$0.9279$** | **$0.7644$** | **$0.8698$** | **$0.7020$** | Sifat memori tren ($H > 0.5$) |
| **Fraktal** | Dimensi Higuchi (`f20_higuchi_dim`) | $1.7022$ | $1.9118$ | $1.7804$ | $1.9658$ | Tingkat kompleksitas bentuk kurva |

---

## 6. Profil Ketersediaan Data Awal 4 Polutan (Hari 1 – 365)

Dataset gabungan yang diekstrak dari pengamatan satelit Copernicus Sentinel-5P disimpan pada berkas `data/csv/pertemuan-5-csv/Hasil Polutan.csv` dengan rentang waktu **365 hari** (24 Agustus 2025 s.d. 23 Agustus 2026).

Sebelum pembersihan dilakukan, karakteristik ketersediaan data pada masing-masing sensor polutan dianalisis:

| Polutan | Nama Senyawa | Total Hari | Hari Terisi (Valid) | Persentase Valid | Missing Values (NaN) | Satuan Baku |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **CH4** | Metana (*Methane*) | 365 hari | 17 hari | 4.66% | 348 hari (95.34%) | $\text{ppb}$ |
| **CO** | Karbon Monoksida | 365 hari | 214 hari | 58.63% | 151 hari (41.37%) | $\text{mol/m}^2$ |
| **NO2** | Nitrogen Dioksida | 365 hari | 188 hari | 51.51% | 177 hari (48.49%) | $\text{mol/m}^2$ |
| **SO2** | Sulfur Dioksida | 365 hari | 230 hari | 63.01% | 135 hari (36.99%) | $\text{mol/m}^2$ |

> **Catatan Lapangan**: Tingginya persentase nilai kosong (*missing values*), terutama pada gas $\text{CH}_4$, disebabkan oleh tutupan awan tebal di atas wilayah pesisir Madura dan lintasan orbit sensor satelit Sentinel-5P TROPOMI yang hanya melintasi wilayah pengamatan pada interval waktu tertentu.

---

## 7. Ringkasan Alur Berkas dan Struktur Output

Seluruh alur pemrosesan data menggunakan struktur folder relatif yang rapi dan terorganisir:

| Tahapan | Notebook Pemroses | Folder Input | Folder Output | File Luaran Utama |
| :--- | :--- | :--- | :--- | :--- |
| **1. Crawling Data** | `1.zat-ch4.ipynb`<br>`1.zat-co.ipynb`<br>`1.zat-no2.ipynb`<br>`1.zat-so2.ipynb` | Platform Satelit Copernicus OpenEO | `data/nc/pertemuan-5-nc/`<br>`data/csv/pertemuan-5-csv/` | File `.nc` & `.csv` per polutan |
| **2. Visualisasi Peta** | `code-map.ipynb` | Koordinat AOI GeoJSON (20 Titik) | `assets/images/images_pertemuan-5/` | `peta_aoi_socah.html`<br>`1.peta_aoi_socah_bangkalan.png` |
| **3. Deteksi Outlier** | `detec-outlier-iqr.ipynb` | `data/csv/pertemuan-5-csv/Hasil Polutan.csv` | `data/csv/pertemuan-5-csv/clean outlier/` | `polutan_4_clean_iqr.csv`<br>`daftar_outlier_iqr.csv` |
| **4. Interpolasi Polinomial** | `interpolasi-polinomial.ipynb` | `data/csv/pertemuan-5-csv/clean outlier/` | `data/csv/pertemuan-5-csv/data bersih/` | `polutan_4_clean.csv` (365 hari, 0 NaN) |
| **5. Ekstraksi Fitur** | `ekstaksi-fitur-4-polutan.ipynb` | `data/csv/pertemuan-5-csv/data bersih/` | `data/csv/pertemuan-5-csv/ekstraksi fitur/` | `fitur_68_4_polutan.csv`<br>Berkas 1 baris per polutan |

---

## 8. Kesimpulan

Melalui seluruh tahapan pemrosesan terpadu pada Pertemuan 5 ini:
1. **Ekstraksi Spasial Presisi**: Data polutan $\text{CH}_4$, $\text{CO}$, $\text{NO}_2$, dan $\text{SO}_2$ berhasil diekstrak secara spesifik untuk wilayah Kecamatan Socah, Kabupaten Bangkalan menggunakan poligon 20 titik koordinat dan divisualisasikan secara interaktif pada [`code-map.ipynb`](code-map.ipynb) dengan pustaka Folium.
2. **Pembersihan Anomali Robust**: Metode IQR berhasil mengidentifikasi **21 titik pencilan ekstrem** (0 CH4, 2 CO, 7 NO2, dan 12 SO2) tanpa terdistorsi oleh bentuk sebaran asimetris data atmosfer.
3. **Rekonstruksi Data Kontinu**: Interpolasi polinomial orde 2 berhasil menambal seluruh nilai kosong menjadi dataset kontinu **365 hari penuh (0 missing value)** dengan kelengkungan yang alami pada satu berkas `polutan_4_clean.csv`.
4. **Kesiapan Machine Learning**: Matriks 68 fitur TSFEL (`fitur_68_4_polutan.csv`) menyediakan ruang fitur terstandarisasi yang siap digunakan untuk pemodelan klaster (*clustering*) maupun analisis komparatif antar wilayah kualitas udara.
