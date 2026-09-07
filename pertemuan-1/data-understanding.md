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

# Data Understanding

Data Understanding adalah tahap untuk **mengumpulkan**, **mengeksplorasi**, dan **menilai kualitas** data yang akan digunakan dalam analisis kualitas udara di Kabupaten Bangkalan.

---

## Library Python yang Diperlukan

Berikut adalah library Python beserta kegunaannya untuk mengerjakan proses data understanding ini:

| Library        | Kegunaan                                                                                                                |
| :------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `openeo`       | Menghubungkan dan memproses data satelit dari server openEO (Copernicus Data Space).                                    |
| `xarray`       | Membaca file hasil batch job openEO berformat NetCDF (`.nc`).                                                           |
| `pandas`       | Membaca dan mengolah data tabular (CSV), serta manipulasi deret waktu (_time-series_).                                  |
| `numpy`        | Komputasi numerik, misalnya perhitungan rata-rata, standar deviasi, dan statistik.                                      |
| `matplotlib`   | Membuat visualisasi grafik scatter plot (outliers), line plot (noise $\pm 1\sigma$), dan grafik komparatif dual X-axis. |
| `scikit-learn` | Deteksi pencilan (_outlier detection_) menggunakan algoritma _Isolation Forest_.                                        |
| `folium`       | Membuat visualisasi peta interaktif lokasi pengamatan (AOI Kabupaten Bangkalan).                                        |

Instalasi dapat dilakukan secara bersamaan:

```bash
pip install openeo xarray pandas numpy matplotlib scikit-learn folium
```

---

## 1. Collecting (Mengumpulkan Data)

### 1.1 Sumber Data

Data kualitas udara dikumpulkan dari **Copernicus Data Space** menggunakan layanan **openEO**. Berikut ringkasannya:

| Item                 | Keterangan                        |
| -------------------- | --------------------------------- |
| **Sumber**           | Copernicus Data Space             |
| **Layanan**          | openEO                            |
| **Server**           | `openeo.dataspace.copernicus.eu`  |
| **Produk / Koleksi** | Sentinel-5P L2                    |
| **Polutan**          | NO2, CO, SO2, CH4                 |
| **Perioda**          | 24 Agustus 2025 – 24 Agustus 2026 |
| **Lokasi**           | Kabupaten Bangkalan, Madura       |

### 1.2 Koneksi dan Otentikasi

Langkah pertama adalah menghubungkan ke server openEO dan melakukan otentikasi menggunakan akun **Copernicus Data Space**.

```python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

Saat dijalankan, akan muncul tautan untuk login (menggunakan _device code flow_). Setelah berhasil melakukan login, akan muncul konfirmasi seperti di bawah ini:

```
Visit (link authentikasi) to authenticate.
Authorized successfully
Authenticated using device code flow.
```

> **Catatan:** Proses **login/autentikasi sudah berhasil**. Ini menandakan koneksi ke server Copernicus Data Space berjalan benar.

### 1.3 Penentuan Area of Interest (AOI)

**Lokasi pengamatan** dibatasi pada area di **Kabupaten Bangkalan**. Area ini digambar sebagai **polygon** di atas peta menggunakan alat seperti [geojson.io](https://geojson.io). **Data peta (koordinat lokasi) dapat dilihat langsung dari file geojson** yang dihasilkan.

```{figure} ../assets/images/geojson.png
:width: 100%
:align: center

Polygon Area of Interest (AOI) di Kabupaten Bangkalan yang digambar pada peta geojson.
```

**Penjelasan koordinat:**

Setiap titik pada polygon memiliki format `[longitude (bujur), latitude (lintang)]`. Dari polygon tersebut, kita memperoleh:

| Atribut | Nilai       | Keterangan                       |
| ------- | ----------- | -------------------------------- |
| `west`  | 112.6654991 | Longitude terkecil (batas kiri)  |
| `east`  | 112.7995564 | Longitude terbesar (batas kanan) |
| `south` | -7.1679391  | Latitude terkecil (batas bawah)  |
| `north` | -7.0171347  | Latitude terbesar (batas atas)   |

> **Catatan:** Untuk data Sentinel-5P, `spatial_extent` pada `load_collection` menggunakan _bounding box_ (kotak batas) yang dibentuk oleh `west`, `south`, `east`, `north`. Sedangkan `aoi` (polygon) digunakan pada tahap `aggregate_spatial` untuk menghitung rata-rata di dalam area tersebut.

### 1.4 Memuat Data (Load Collection)

Data dimuat **per polutan**, karena server Sentinel-5P di openEO hanya mendukung **satu band per proses**. Oleh karena itu dibuat **4 notebook terpisah** (`1.zat-no2.ipynb`, `1.zat-co.ipynb`, `1.zat-so2.ipynb`, `1.zat-ch4.ipynb`), masing-masing untuk satu polutan.

#### a. Memuat Data NO2

```python
s5 = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent={
        "west": 112.6654991,
        "south": -7.1679391,
        "east": 112.7995564,
        "north": -7.0171347,
    },
    bands=["NO2"],
)
```

#### b. Memuat Data CO

```python
s5 = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent={
        "west": 112.6654991,
        "south": -7.1679391,
        "east": 112.7995564,
        "north": -7.0171347,
    },
    bands=["CO"],
)
```

#### c. Memuat Data SO2

```python
s5 = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent={
        "west": 112.6654991,
        "south": -7.1679391,
        "east": 112.7995564,
        "north": -7.0171347,
    },
    bands=["SO2"],
)
```

#### d. Memuat Data CH4

```python
s5 = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-24", "2026-08-24"],
    spatial_extent={
        "west": 112.6654991,
        "south": -7.1679391,
        "east": 112.7995564,
        "north": -7.0171347,
    },
    bands=["CH4"],
)
```

**Perhatikan:** Kode untuk CO, SO2, dan CH4 **identik** dengan NO2 — hanya berbeda pada parameter `bands`.

### 1.5 Definisi AOI (Polygon)

```python
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
                        [112.6654991, -7.0171347],
                        [112.6912024, -7.1679391],
                        [112.7995564, -7.0918788],
                        [112.6993392, -7.0334062],
                        [112.6654991, -7.0171347]
                    ]
                ]
            }
        }
    ]
}
```

### 1.6 Agregasi Data

Setiap datacube diagregasi menjadi **rata-rata harian**, lalu dihitung **rata-rata spasial** di dalam polygon AOI untuk menghasilkan deret waktu (time series).

```python
# Rata-rata harian, lalu rata-rata di dalam polygon AOI
s5 = s5.aggregate_temporal_period(reducer="mean", period="day")
s5 = s5.aggregate_spatial(reducer="mean", geometries=aoi)
```

### 1.7 Menjalankan Batch Job

Proses dijalankan sebagai **batch job** di server openEO. Hasilnya diunduh sebagai file NetCDF (`.nc`).

```python
job = s5.execute_batch(title="NO2 Bangkalan", outputfile="../data/nc/polutan_NO2_bangkalan.nc")
```

Setiap batch job membutuhkan beberapa menit (antre di server). Hasilnya disimpan pada folder **`data/nc/`**:

| Polutan | File NetCDF                     |
| ------- | ------------------------------- |
| NO2     | `data/nc/polutan_NO2_bangkalan.nc` |
| CO      | `data/nc/polutan_co_bangkalan.nc`  |
| SO2     | `data/nc/polutan_SO2_bangkalan.nc` |
| CH4     | `data/nc/polutan_CH4_bangkalan.nc` |

Proses crawling data. Notebook tersebut menjalankan **batch job** di server openEO, dan hasilnya dapat **dipantau (monitoring) melalui openEO Web Editor**.

```{figure} ../assets/images/openeoeditor.png
:width: 100%
:align: center

Pantauan batch job pada openEO Web Editor. Bisa dilihat langsung di https://editor.openeo.org/.
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
                        [112.6654991, -7.0171347],
                        [112.6912024, -7.1679391],
                        [112.7995564, -7.0918788],
                        [112.6993392, -7.0334062],
                        [112.6654991, -7.0171347]
                    ]
                ]
            }
        }
    ]
}

# Titik tengah AOI
center_lat = (-7.1613419 + -7.2296572 + -6.8602645 + -6.8602645) / 4
center_lon = (112.6669403 + 113.0865997 + 113.0865997 + 112.6725233) / 4

# Buat peta
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=10,
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

---

## 3. Menampilkan Hasil Data CSV

Setelah data NetCDF dikonversi menjadi CSV, kita dapat menampilkan isi data menggunakan **pandas** `pd.read_csv` diikuti `.head()` untuk melihat **5 baris paling atas**.

### 3.1 CH4

```{code-cell}
:tags: [hide-input]
import pandas as pd

# Menampilkan 5 data teratas CSV CH4
df_ch4 = pd.read_csv("../data/csv/polutan_ch4_bangkalan.csv")
df_ch4.head()
```

| tanggal | CH4 |
| :--- | :--- |
| 2025-08-24 | 1850.206787 |
| 2025-08-25 | 1867.289429 |
| 2025-08-26 | nan |
| 2025-08-27 | nan |
| 2025-08-28 | nan |

### 3.2 CO

```{code-cell}
:tags: [hide-input]
import pandas as pd

# Menampilkan 5 data teratas CSV CO
df_co = pd.read_csv("../data/csv/polutan_co_bangkalan.csv")
df_co.head()
```

| tanggal | CO |
| :--- | :--- |
| 2025-08-24 | 0.032369 |
| 2025-08-25 | 0.029644 |
| 2025-08-27 | 0.028471 |
| 2025-08-28 | 0.024230 |
| 2025-08-29 | 0.027042 |

### 3.3 NO2

```{code-cell}
:tags: [hide-input]
import pandas as pd

# Menampilkan 5 data teratas CSV NO2
df_no2 = pd.read_csv("../data/csv/polutan_no2_bangkalan.csv")
df_no2.head()
```

| tanggal | NO2 |
| :--- | :--- |
| 2025-08-24 | 0.000030 |
| 2025-08-25 | 0.000040 |
| 2025-08-26 | 0.000046 |
| 2025-08-28 | 0.000029 |
| 2025-08-29 | 0.000029 |

### 3.4 SO2

```{code-cell}
:tags: [hide-input]
import pandas as pd

# Menampilkan 5 data teratas CSV SO2
df_so2 = pd.read_csv("../data/csv/polutan_so2_bangkalan.csv")
df_so2.head()
```

| tanggal | SO2 |
| :--- | :--- |
| 2025-08-24 | 0.000544 |
| 2025-08-25 | 0.000182 |
| 2025-08-26 | -0.000258 |
| 2025-08-27 | 0.000107 |
| 2025-08-28 | -0.000066 |

### 3.5 Kenapa Ada Nilai NaN?

Perhatikan pada hasil data di atas, ada beberapa baris yang menunjukkan nilai **NaN** (Not a Number). Artinya, pada tanggal tersebut **tidak ada data pengamatan** yang tercatat.

Penyebab munculnya NaN pada data satelit Sentinel-5P antara lain:

1. **Tidak ada lintasan satelit** — Sentinel-5P tidak melewati lokasi Kabupaten Bangkalan setiap hari. Satelit memiliki _revisit time_ (jadwal orbit) tertentu, sehingga ada hari-hari tertentu yang tidak terlewati.

2. **Tutupan awan (cloud cover)** — Sentinel-5P menggunakan sensor optik/atmosferik yang hasilnya dipengaruhi oleh kondisi cuaca. Jika area tertutup awan tebal, data tidak dapat diukur sehingga dianggap kosong.

3. **Validasi kualitas (quality flag)** — data yang kualitasnya buruk (misal karena noise instrumen) disaring keluar oleh sistem quality assurance agar tidak mendistorsi analisis, menghasilkan celah (gap) pada deret waktu.

Karena itu, dari total **366 hari** dalam setahun, tidak semua tanggal memiliki nilai polutan. Hari-hari yang kosong inilah yang tampil sebagai **NaN** — dan ini akan dibahas lebih lanjut pada tahap **identifikasi _missing values_** di bagian selanjutnya.

---

## 4. Identifikasi Kualitas Data

Pada tahap ini dilakukan **identifikasi** (mencatat) masalah-masalah pada data, yaitu **missing values**, **outliers**, dan **noises**. Sesuai prinsip CRISP-DM, tahap Data Understanding hanya **menemukan dan mencatat** masalah tersebut — penanganan dilakukan pada tahap berikutnya (Data Preparation).

### 4.1 Missing Values

**Missing values** adalah tanggal yang tidak memiliki nilai polutan (NaN). Identifikasi missing value dilakukan menggunakan berkas [code-ms.ipynb](code-cekms.ipynb). Berikut identifikasinya:

1. CH4

```{code-cell}
:tags: [hide-input]
import pandas as pd

filepath = "../data/csv/polutan_ch4_bangkalan.csv"

df = pd.read_csv(filepath)

countMissing = df["CH4"].isna().sum()
countValid = df["CH4"].notna().sum()
print("Missing values:", countMissing)
print("Valid values:", countValid)
```

```
Jumlah missing value pada data ch4 : 339
Jumlah data terisi (valid) pada data ch4 : 27
```

2. CO

```{code-cell}
:tags: [hide-input]
filepath = "../data/csv/polutan_co_bangkalan.csv"

df = pd.read_csv(filepath)

countMissing = df["CO"].isna().sum()
countValid = df["CO"].notna().sum()
print("Missing values:", countMissing)
print("Valid values:", countValid)
```

```
Jumlah missing value pada data co : 0
Jumlah data terisi (valid) pada data co : 236
```

3. NO2

```{code-cell}
:tags: [hide-input]
filepath = "../data/csv/polutan_no2_bangkalan.csv"

df = pd.read_csv(filepath)

countMissing = df["NO2"].isna().sum()
countValid = df["NO2"].notna().sum()
print("Missing values:", countMissing)
print("Valid values:", countValid)
```

```
Jumlah missing value pada data no2 : 0
Jumlah data terisi (valid) pada data no2 : 218
```

4. SO2

```{code-cell}
:tags: [hide-input]
filepath = "../data/csv/polutan_so2_bangkalan.csv"

df = pd.read_csv(filepath)

countMissing = df["SO2"].isna().sum()
countValid = df["SO2"].notna().sum()
print("Missing values:", countMissing)
print("Valid values:", countValid)
```

```
Jumlah missing value pada data so2 : 0
Jumlah data terisi (valid) pada data so2 : 249
```

### 4.2 Outliers

**Outliers** (pencilan) adalah nilai pengamatan yang menyimpang secara signifikan dari mayoritas data dalam suatu variabel. Deteksi outlier dilakukan menggunakan algoritma **Isolation Forest** dengan tingkat kontaminasi (`contamination`) sebesar **0.05** (5%) pada berkas [code-cejoutl.ipynb](code-cejoutl.ipynb).

Sebelum deteksi outlier dilakukan, data bernilai kosong (_missing values_ / `NaN`) dibuang terlebih dahulu (`dropna()`) agar populasi perhitungan pencilan selaras.

Berikut adalah hasil identifikasi outlier untuk masing-masing polutan:

1. CH4

```{code-cell}
:tags: [hide-input]
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../data/csv/polutan_ch4_bangkalan.csv")
df_clean = df.dropna(subset=['CH4']).copy()

# Ubah tanggal
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

# Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df_clean['outlier'] = model.fit_predict(df_clean[['CH4']])

normal_ch4 = df_clean[df_clean['outlier'] == 1]
outliers_ch4 = df_clean[df_clean['outlier'] == -1]

print(f"Jumlah outlier: {len(outliers_ch4)}")
print(f"Jumlah normal: {len(normal_ch4)}")

# Urutkan berdasarkan tanggal
df_clean = df_clean.sort_values('tanggal')

# Visualisasi
plt.figure(figsize=(12, 5))

# Garis seluruh data
plt.plot(
    df_clean['tanggal'],
    df_clean['CH4'],
    linewidth=1.5,
    label='Konsentrasi CH4'
)

# Tandai outlier
plt.scatter(
    outliers_ch4['tanggal'],
    outliers_ch4['CH4'],
    color='red',
    marker='X',
    s=100,
    label='Outlier'
)

plt.title('Deteksi Outlier Konsentrasi CH4 dengan Isolation Forest')
plt.xlabel('Tanggal')
plt.ylabel('Konsentrasi CH4')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
```

```
Jumlah outlier pada data ch4 : 2
Jumlah tidak outlier (normal) pada data ch4 : 25
```

2. CO

```{code-cell}
:tags: [hide-input]
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../data/csv/polutan_co_bangkalan.csv")
df_clean = df.dropna(subset=['CO']).copy()

# Ubah tanggal
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

# Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df_clean['outlier'] = model.fit_predict(df_clean[['CO']])

# Pisahkan data normal dan outlier
normal_co = df_clean[df_clean['outlier'] == 1]
outliers_co = df_clean[df_clean['outlier'] == -1]

print(f"Jumlah outlier: {len(outliers_co)}")
print(f"Jumlah normal: {len(normal_co)}")

# Urutkan berdasarkan tanggal
df_clean = df_clean.sort_values('tanggal')

# Visualisasi
plt.figure(figsize=(12, 5))

# Garis seluruh data
plt.plot(
    df_clean['tanggal'],
    df_clean['CO'],
    linewidth=1.5,
    label='Konsentrasi CO'
)

# Tandai outlier
plt.scatter(
    outliers_co['tanggal'],
    outliers_co['CO'],
    color='red',
    marker='X',
    s=100,
    label='Outlier'
)

plt.title('Deteksi Outlier Konsentrasi CO dengan Isolation Forest')
plt.xlabel('Tanggal')
plt.ylabel('Konsentrasi CO')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
```

```
Jumlah outlier pada data co : 12
Jumlah tidak outlier (normal) pada data co : 224
```

3. NO2

```{code-cell}
:tags: [hide-input]
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../data/csv/polutan_no2_bangkalan.csv")
df_clean = df.dropna(subset=['NO2']).copy()

# Ubah tanggal
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

# Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df_clean['outlier'] = model.fit_predict(df_clean[['NO2']])

# Pisahkan data normal dan outlier
normal_no2 = df_clean[df_clean['outlier'] == 1]
outliers_no2 = df_clean[df_clean['outlier'] == -1]

print(f"Jumlah outlier: {len(outliers_no2)}")
print(f"Jumlah normal: {len(normal_no2)}")

# Urutkan berdasarkan tanggal
df_clean = df_clean.sort_values('tanggal')

# Visualisasi
plt.figure(figsize=(12, 5))

# Garis seluruh data
plt.plot(
    df_clean['tanggal'],
    df_clean['NO2'],
    linewidth=1.5,
    label='Konsentrasi NO2'
)

# Tandai outlier
plt.scatter(
    outliers_no2['tanggal'],
    outliers_no2['NO2'],
    color='red',
    marker='X',
    s=100,
    label='Outlier'
)

plt.title('Deteksi Outlier Konsentrasi NO2 dengan Isolation Forest')
plt.xlabel('Tanggal')
plt.ylabel('Konsentrasi NO2')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
```

```
Jumlah outlier pada data no2 : 11
Jumlah tidak outlier (normal) pada data no2 : 207
```

4. SO2

```{code-cell}
:tags: [hide-input]
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../data/csv/polutan_so2_bangkalan.csv")
df_clean = df.dropna(subset=['SO2']).copy()

# Ubah tanggal
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

# Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df_clean['outlier'] = model.fit_predict(df_clean[['SO2']])

normal_so2 = df_clean[df_clean['outlier'] == 1]
outliers_so2 = df_clean[df_clean['outlier'] == -1]

print(f"Jumlah outlier: {len(outliers_so2)}")
print(f"Jumlah normal: {len(normal_so2)}")

# Urutkan berdasarkan tanggal
df_clean = df_clean.sort_values('tanggal')

# Visualisasi
plt.figure(figsize=(12, 5))

# Garis seluruh data
plt.plot(
    df_clean['tanggal'],
    df_clean['SO2'],
    linewidth=1.5,
    label='Konsentrasi SO2'
)

# Tandai outlier
plt.scatter(
    outliers_so2['tanggal'],
    outliers_so2['SO2'],
    color='red',
    marker='X',
    s=100,
    label='Outlier'
)

plt.title('Deteksi Outlier Konsentrasi SO2 dengan Isolation Forest')
plt.xlabel('Tanggal')
plt.ylabel('Konsentrasi SO2')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
```

```
Jumlah outlier pada data so2 : 13
Jumlah tidak outlier (normal) pada data so2 : 236
```

### 4.3 Noise

**Noise** (derau) adalah fluktuasi acak frekuensi tinggi pada data pengamatan yang disebabkan oleh kondisi dinamika atmosfer mikro, keterbatasan presisi instrumen satelit, atau interferensi cuaca lokal. Noise dihitung berdasarkan selisih antara nilai aktual dengan nilai rata-rata bergerak 7 hari (`noise = aktual - trend`). Analisis ini dijalankan pada berkas [code-ceknoise.ipynb](code-ceknoise.ipynb).

Berikut adalah hasil analisis noise untuk masing-masing polutan:

1. CH4

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/csv/polutan_ch4_bangkalan.csv")
df_clean = df.dropna(subset=['CH4']).copy()
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

window = 7
df_clean['trend'] = df_clean['CH4'].rolling(window=window, center=True).mean()
df_clean['noise'] = df_clean['CH4'] - df_clean['trend']
noise = df_clean['noise'].dropna()

print("Rata-rata noise       :", noise.mean())
print("Standar deviasi noise :", noise.std())
print("RMSE noise            :", np.sqrt(np.mean(noise**2)))

plt.figure(figsize=(12, 5))
plt.plot(df_clean['tanggal'], df_clean['noise'])
plt.axhline(0, linestyle='--')
plt.title('Noise CH4')
plt.xlabel('Tanggal')
plt.ylabel('Noise CH4')
plt.grid()
plt.show()
```

```
Rata-rata noise       : 0.13775108839106343
Standar deviasi noise : 18.647873806320245
RMSE noise            : 18.198982745692533
```

2. CO

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/csv/polutan_co_bangkalan.csv")
df_clean = df.dropna(subset=['CO']).copy()
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

window = 7
df_clean['trend'] = df_clean['CO'].rolling(window=window, center=True).mean()
df_clean['noise'] = df_clean['CO'] - df_clean['trend']
noise = df_clean['noise'].dropna()

print("Rata-rata noise       :", noise.mean())
print("Standar deviasi noise :", noise.std())
print("RMSE noise            :", np.sqrt(np.mean(noise**2)))

plt.figure(figsize=(12, 5))
plt.plot(df_clean['tanggal'], df_clean['noise'])
plt.axhline(0, linestyle='--')
plt.title('Noise CO')
plt.xlabel('Tanggal')
plt.ylabel('Noise CO')
plt.grid()
plt.show()
```

```
Rata-rata noise       : -2.1676236559206584e-05
Standar deviasi noise : 0.0025884577022468784
RMSE noise            : 0.0025829154473703177
```

3. NO2

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/csv/polutan_no2_bangkalan.csv")
df_clean = df.dropna(subset=['NO2']).copy()
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

window = 7
df_clean['trend'] = df_clean['NO2'].rolling(window=window, center=True).mean()
df_clean['noise'] = df_clean['NO2'] - df_clean['trend']
noise = df_clean['noise'].dropna()

print("Rata-rata noise       :", noise.mean())
print("Standar deviasi noise :", noise.std())
print("RMSE noise            :", np.sqrt(np.mean(noise**2)))

plt.figure(figsize=(12, 5))
plt.plot(df_clean['tanggal'], df_clean['noise'])
plt.axhline(0, linestyle='--')
plt.title('Noise NO2')
plt.xlabel('Tanggal')
plt.ylabel('Noise NO2')
plt.grid()
plt.show()
```

```
Rata-rata noise       : -8.797525892828011e-08
Standar deviasi noise : 1.8697081577541818e-05
RMSE noise            : 1.86531400264127e-05
```

4. SO2

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/csv/polutan_so2_bangkalan.csv")
df_clean = df.dropna(subset=['SO2']).copy()
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])

window = 7
df_clean['trend'] = df_clean['SO2'].rolling(window=window, center=True).mean()
df_clean['noise'] = df_clean['SO2'] - df_clean['trend']
noise = df_clean['noise'].dropna()

print("Rata-rata noise       :", noise.mean())
print("Standar deviasi noise :", noise.std())
print("RMSE noise            :", np.sqrt(np.mean(noise**2)))

plt.figure(figsize=(12, 5))
plt.plot(df_clean['tanggal'], df_clean['noise'])
plt.axhline(0, linestyle='--')
plt.title('Noise SO2')
plt.xlabel('Tanggal')
plt.ylabel('Noise SO2')
plt.grid()
plt.show()
```

```
Rata-rata noise       : 9.77278029500097e-07
Standar deviasi noise : 0.00018049803864521538
RMSE noise            : 0.00018012891172158437
```

---

### 4.4 Visualisasi Komparatif 4 Polutan (Style Copernicus)

Untuk membandingkan tren perubahan konsentrasi ke-4 polutan (CH4, CO, NO2, SO2) secara bersamaan sepanjang periode pengamatan di Kabupaten Bangkalan, dibuat visualisasi **Dual X-Axis Line Plot** dengan gaya visualisasi Copernicus Sentinel-5P.

```{figure} ../assets/images/copernicus_4polutan_dual_axis.png
:width: 100%
:align: center

Grafik Komparatif Tren 4 Polutan di Kabupaten Bangkalan (Style Copernicus)
```

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load Data 4 Polutan
df_no2 = pd.read_csv("../data/csv/polutan_no2_bangkalan.csv").dropna(subset=['NO2'])
df_co  = pd.read_csv("../data/csv/polutan_co_bangkalan.csv").dropna(subset=['CO'])
df_ch4 = pd.read_csv("../data/csv/polutan_ch4_bangkalan.csv").dropna(subset=['CH4'])
df_so2 = pd.read_csv("../data/csv/polutan_SO2_bangkalan.csv").dropna(subset=['SO2'])

df_no2['tanggal'] = pd.to_datetime(df_no2['tanggal'])
df_co['tanggal']  = pd.to_datetime(df_co['tanggal'])
df_ch4['tanggal'] = pd.to_datetime(df_ch4['tanggal'])
df_so2['tanggal'] = pd.to_datetime(df_so2['tanggal'])

# 2. Smooth data dengan 30-day moving average (seperti Copernicus)
df_no2['NO2_smooth'] = df_no2['NO2'].rolling(window=30, min_periods=1).mean()
df_co['CO_smooth']   = df_co['CO'].rolling(window=30, min_periods=1).mean()
df_ch4['CH4_smooth'] = df_ch4['CH4'].rolling(window=30, min_periods=1).mean()
df_so2['SO2_smooth'] = df_so2['SO2'].rolling(window=30, min_periods=1).mean()

# 3. Normalisasi Min-Max (0 - 1)
for df, col in [(df_no2, 'NO2_smooth'), (df_co, 'CO_smooth'), (df_ch4, 'CH4_smooth'), (df_so2, 'SO2_smooth')]:
    df[col + '_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# 4. Figure Dual X-Axis (Gaya Copernicus twiny())
fig, ax1 = plt.subplots(figsize=(11, 5), dpi=100)

# Sumbu Bawah: NO2 (Merah) & CO (Hijau)
line1, = ax1.plot(df_no2['tanggal'], df_no2['NO2_smooth_norm'], color="r", label="NO2 (Nitrogen Dioksida)", linewidth=1.8)
line2, = ax1.plot(df_co['tanggal'],  df_co['CO_smooth_norm'],   color="g", label="CO (Karbon Monoksida)", linewidth=1.8)

ax1.set_xlabel("Periode NO2 & CO (Sumbu Bawah)", color='r', fontsize=10)
ax1.set_ylabel("Skala Ternormalisasi (0 - 1)")
ax1.xaxis.label.set_color("r")
ax1.tick_params(axis="x", colors="r")
ax1.grid(True, linestyle='--', alpha=0.5)

# Sumbu Atas: CH4 (Biru) & SO2 (Oranye)
ax2 = ax1.twiny()
line3, = ax2.plot(df_ch4['tanggal'], df_ch4['CH4_smooth_norm'], color="b", label="CH4 (Metana)", linewidth=1.8)
line4, = ax2.plot(df_so2['tanggal'], df_so2['SO2_smooth_norm'], color="orange", label="SO2 (Sulfur Dioksida)", linewidth=1.8)

ax2.set_xlabel("Periode CH4 & SO2 (Sumbu Atas)", color='b', fontsize=10)
ax2.xaxis.label.set_color("b")
ax2.tick_params(axis="x", colors="b")

# Combine Legend
lines = [line1, line2, line3, line4]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc="upper left")

plt.title("Grafik Komparatif Tren 4 Polutan di Kabupaten Bangkalan", pad=20)
plt.tight_layout()
plt.show()
```

#### Penjelasan Rinci Komponen Grafik:

1. **Struktur Dual X-Axis (Sumbu X Ganda)**:
   - **Sumbu X Bawah (Merah)**: Digunakan sebagai penanda garis waktu tanggal untuk polutan NO2 dan CO.
   - **Sumbu X Atas (Biru)**: Digunakan sebagai penanda garis waktu tanggal untuk polutan CH4 dan SO2.
   - **Fungsi `twiny()`**: Memungkinkan 2 pasangan polutan menggunakan sumbu Y bersama di sebelah kiri, namun memiliki skala waktu horizontal di atas dan bawah untuk menjaga keterbacaan grafik.

2. **Keterangan 4 Warna Polutan**:
   - Garis Merah (NO2): Menunjukkan tren emisi gas Nitrogen Dioksida (berasal dari transportasi kendaraan dan pembakaran industri).
   - Garis Hijau (CO): Menunjukkan tren emisi gas Karbon Monoksida (berasal dari pembuangan asap pembakaran).
   - Garis Biru (CH4): Menunjukkan tren konsentrasi gas Metana (gas rumah kaca dari zona industri/limbah/tambang).
   - Garis Oranye (SO2): Menunjukkan tren emisi gas Sulfur Dioksida (berasal dari pembakaran batu bara & pemrosesan industri).

3. **Mengapa Menggunakan Skala Ternormalisasi (0 - 1) di Sumbu Y?**:
   - Nilai asli dari masing-masing polutan memiliki rentang angka yang jauh berbeda (misalnya: CH4 bernilai tinggi sekitar ~1880, sedangkan NO2 bernilai kecil sekitar ~0.00003).
   - Jika diplot tanpa skala bersama, garis NO2, CO, dan SO2 akan terlihat datar mendekati angka 0.
   - Dengan **Normalisasi Min-Max ($0 - 1$)**, semua garis polutan dibawa ke rentang proporsional yang sama ($0$ = konsentrasi terendah, $1$ = konsentrasi tertinggi), sehingga naik-turunnya pola tren ke-4 polutan dapat dibandingkan secara langsung.

4. **Penghalusan Grafik (_30-Day Moving Average_)**:
   - Garis grafik dihaluskan menggunakan teknik _rolling mean_ 30 hari (`.rolling(window=30).mean()`) persis seperti pada kode acuan Copernicus.
   - Hal ini berfungsi untuk meredam derau (_noise_) harian, sehingga garis grafik terlihat mulus dan pembaca dapat melihat tren kenaikan/penurunan jangka panjang di Kabupaten Bangkalan secara jernih.

5. **Cara Membaca Arah dan Gerakan Garis Grafik**:
   - Garis Naik ke Atas: Menandakan konsentrasi polutan di Kabupaten Bangkalan sedang **meningkat / tinggi** (akibat lonjakan emisi industri, volume kendaraan padat, atau musim kemarau di mana emisi terperangkap di atmosfer).
   - Garis Turun ke Bawah: Menandakan kualitas udara sedang **lebih bersih / polusi rendah** (akibat pencucian polutan oleh air hujan, berkurangnya aktivitas, atau tiupan angin kencang).
   - Garis di Tengah / Datar: Menandakan konsentrasi polutan berada pada **kondisi rata-rata latar belakang yang stabil**.
   - Garis Fluktuasi (Bergerigi): Menandakan adanya variasi perubahan cuaca harian yang cepat serta derau (_noise_) instrumen pengamatan satelit Sentinel-5P.

---

## 5. Kesimpulan dan Rencana Tahap Data Preparation

Berdasarkan hasil pengumpulan, eksplorasi, dan identifikasi kualitas data kualitas udara Kabupaten Bangkalan (Sentinel-5P L2), diperoleh ringkasan evaluasi kualitas data sebagai berikut:

| Polutan | Total Baris | Missing Values (NaN) | Data Terisi (Valid) | Outliers Terdeteksi (5%) | Standar Deviasi Noise | Status Kualitas Data            |
| :------ | :---------- | :------------------- | :------------------ | :----------------------- | :-------------------- | :------------------------------ |
| **CH4** | 366         | 339 (92.62%)         | 27 (7.38%)          | 2                        | 18.6479               | Celah Data Cukup Besar          |
| **CO**  | 236         | 0 (0.00%)            | 236 (100.00%)       | 12                       | 0.0026                | Cukup Baik                      |
| **NO2** | 218         | 0 (0.00%)            | 218 (100.00%)       | 11                       | 1.8697e-05            | Baik                            |
| **SO2** | 249         | 0 (0.00%)            | 249 (100.00%)       | 13                       | 0.00018               | Sangat Baik                     |

---

### 5.1 Rencana Aksi Tahap Data Preparation

Temuan kualitas data di atas menjadi dasar utama dalam menyusun strategi pemrosesan pada tahap **Data Preparation** berikutnya:

1. **Imputasi Missing Values (_Time-Series Imputation_)**:
   - Celah tanggal kosong (terutama pada CH4 dan CO) akan diisi menggunakan teknik interpolasi linier (_linear interpolation_) atau _forward/backward fill_ agar deret waktu menjadi berkesinambungan harian.

2. **Penanganan Outliers (_Outlier Treatment_)**:
   - Nilai pencilan ekstrem hasil deteksi _Isolation Forest_ akan ditangani menggunakan teknik _winsorization_ (membatasi nilai ke rentang persentil tertentu) atau imputasi nilai batas wajar agar tidak menggangu pemodelan.

3. **Penghalusan Derau (_Noise Smoothing_)**:
   - Menerapkan fungsi _Moving Average_ (rata-rata bergerak 7 hari / 30 hari) untuk meredam fluktuasi acak frekuensi tinggi, sehingga tren perubahan pola polusi udara di Kabupaten Bangkalan dapat dianalisis secara akurat dan konsisten.
