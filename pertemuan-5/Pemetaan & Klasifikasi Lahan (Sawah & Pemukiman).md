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

# Pemetaan & Klasifikasi Lahan (Sawah & Bukan Sawah)

Modul ini membahas proses pemetaan dan klasifikasi lahan antara **Sawah** dan **Bukan Sawah** di **Kecamatan Socah, Kabupaten Bangkalan** menggunakan data koordinat GeoJSON dan citra satelit **Sentinel-2A**.

Seluruh kode praktikum dapat dijalankan pada notebook: [`ambil_data.ipynb`](ambil_data.ipynb).

---

## 1. Data Koordinat (GeoJSON)

Data titik lokasi lahan diambil dari berkas [`50,50,1.geojson`](50,50,1.geojson) yang memuat:
* **1 Batas Wilayah:** Poligon batas administrasi Kecamatan Socah.
* **50 Titik Sawah:** Sampel area persawahan.
* **50 Titik Bukan Sawah:** Sampel area selain sawah (mencakup pemukiman, tanah terbuka, vegetasi non-padi, jalan, dan fasilitas umum).

> **Catatan Penting:** 
> Kategori **Bukan Sawah** bersifat heterogen (tidak hanya pemukiman). Selain itu, **sawah belum tentu selalu berwarna hijau**, karena kondisi sawah bergantung pada fase siklus tanam padi (fase pengolahan tanah/tergenang air, fase hijau vegetatif, fase pematangan/menguning, hingga fase pasca-panen/tanah bera).

### Peta Interaktif (Folium) Wilayah Socah, Sawah, dan Bukan Sawah

Berikut visualisasi peta interaktif menggunakan **`folium`**:
* **Garis Biru:** Batas wilayah pengamatan Kecamatan Socah.
* **Titik Hijau:** 50 titik lokasi lahan sawah.
* **Titik Merah:** 50 titik lokasi bukan sawah.

```{code-cell}
:tags: [hide-input]
import os
import folium
import geopandas as gpd

# Path fleksibel agar dapat dijalankan dari root maupun folder pertemuan-5
geojson_path = "pertemuan-5/50,50,1.geojson" if os.path.exists("pertemuan-5/50,50,1.geojson") else "50,50,1.geojson"
gdf = gpd.read_file(geojson_path)

aoi = gdf[gdf["Sawah"] == "socah"]
sawah = gdf[gdf["Sawah"] == "sawah"]
bukan = gdf[gdf["Sawah"] == "bukan"]

# Titik tengah Kecamatan Socah
center_point = aoi.geometry.iloc[0].centroid
m = folium.Map(location=[center_point.y, center_point.x], zoom_start=13, tiles="OpenStreetMap")

# 1. Batas Wilayah Socah (Garis Biru)
folium.GeoJson(
    aoi,
    name="Batas Wilayah Socah",
    style_function=lambda x: {
        "color": "#0044ff",
        "weight": 2.5,
        "fillColor": "#3388ff",
        "fillOpacity": 0.08
    }
).add_to(m)

# 2. 50 Titik Sawah (Warna Hijau)
g_sawah = folium.FeatureGroup(name="50 Titik Sawah (Hijau)")
for _, row in sawah.iterrows():
    pt = row.geometry.centroid
    folium.CircleMarker(
        location=[pt.y, pt.x],
        radius=5,
        color="#1b5e20",
        fill=True,
        fill_color="#2ecc71",
        fill_opacity=0.9,
        popup=f"Sawah (Lat: {pt.y:.4f}, Lon: {pt.x:.4f})"
    ).add_to(g_sawah)
g_sawah.add_to(m)

# 3. 50 Titik Bukan Sawah (Warna Merah)
g_bukan = folium.FeatureGroup(name="50 Titik Bukan Sawah (Merah)")
for _, row in bukan.iterrows():
    pt = row.geometry.centroid
    folium.CircleMarker(
        location=[pt.y, pt.x],
        radius=5,
        color="#b71c1c",
        fill=True,
        fill_color="#e74c3c",
        fill_opacity=0.9,
        popup=f"Bukan Sawah (Lat: {pt.y:.4f}, Lon: {pt.x:.4f})"
    ).add_to(g_bukan)
g_bukan.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m
```

---

## 2. Pengunduhan Citra Satelit Sentinel-2A ke File TIF

Citra satelit optik diunduh dari platform **Copernicus Data Space Ecosystem (CDSE)** menggunakan **openEO API**:
* **Koleksi:** `SENTINEL2_L2A` (Surface Reflectance resolusi 10 meter).
* **Band Spektral:** Blue (`B02`), Green (`B03`), Red (`B04`), dan Near-Infrared / NIR (`B08`).
* **Batas Wilayah (*Extent*):** Bounding box koordinat Kecamatan Socah.
* **Komposit Temporal:** Median pada periode bulan Agustus agar citra jernih dan bebas tutupan awan (*cloud-free*).
* **Format Output:** Disimpan sebagai GeoTIFF di: `../data/tif/pertemuan-5-tif/sentinel2_socah.tif`.

---

## 3. Citra RGB & Peta Indeks Vegetasi (NDVI)

Kombinasi multi-band digunakan untuk menghitung indeks vegetasi **NDVI**:

$$\text{NDVI} = \frac{\text{B08 (NIR)} - \text{B04 (Red)}}{\text{B08 (NIR)} + \text{B04 (Red)}}$$

```{figure} ../assets/images/images_pertemuan-5/5.citra_rgb_dan_ndvi_socah.png
:width: 95%
:align: center

Perbandingan Citra Sentinel-2A True Color (RGB) dan Peta Sebaran Nilai NDVI Kecamatan Socah.
```

* **Nilai NDVI Tinggi ($\approx 0.48 - 0.70$):** Menunjukkan area sawah yang sedang berada pada fase pertumbuhan vegetatif aktif (banyak klorofil hijau).
* **Nilai NDVI Sedang / Rendah ($\approx 0.15 - 0.35$):** Menunjukkan area bukan sawah (pemukiman, tanah kering, jalan) ataupun sawah yang sedang dalam fase bera/panen.
* Oleh karena itu, klasifikasi tidak hanya mengandalkan satu nilai NDVI saja, melainkan menggabungkan seluruh 4 band spektral (`B02`, `B03`, `B04`, `B08`) ke dalam model Machine Learning.

---

## 4. Evaluasi Klasifikasi Machine Learning (Sawah vs Bukan Sawah)

Nilai spektral dari 100 titik sampel diekstrak dan disimpan ke tabel: `../data/csv/pertemuan-5-csv/dataset_sampel_sawah_pemukiman.csv`.

Model **Random Forest** dilatih menggunakan 75% data latih dan diuji pada 25% data uji:

```{figure} ../assets/images/images_pertemuan-5/6.evaluasi_klasifikasi_confusion_matrix.png
:width: 90%
:align: center

Confusion Matrix Prediksi Model Random Forest dan Boxplot Nilai NDVI Sawah vs Bukan Sawah.
```

### Tabel Evaluasi Model:

| Kelas Lahan | Precision | Recall | F1-Score | Akurasi Total |
| :--- | :---: | :---: | :---: | :---: |
| **Bukan Sawah** | $0.83$ | $0.77$ | $0.80$ | - |
| **Sawah** | $0.77$ | $0.83$ | $0.80$ | - |
| **Rata-Rata** | **$0.80$** | **$0.80$** | **$0.80$** | **$80.0\%$** |

---

## 5. Peta Hasil Klasifikasi & Estimasi Luas Lahan

Model diterapkan ke seluruh piksel di dalam batas administrasi Kecamatan Socah:

```{figure} ../assets/images/images_pertemuan-5/7.peta_hasil_klasifikasi_lahan_socah.png
:width: 95%
:align: center

Peta Hasil Klasifikasi Tutupan Lahan Kecamatan Socah (Hijau = Sawah, Merah = Bukan Sawah) dan Diagram Proporsi Luas.
```

### Estimasi Luas Wilayah:
* **Area Sawah (Hijau):** $\approx 2.193\text{ Hektar}$ ($34.6\%$).
* **Area Bukan Sawah (Merah):** $\approx 4.152\text{ Hektar}$ ($65.4\%$).
* **Total Luas Daratan Socah:** $\approx 6.345\text{ Hektar}$ ($\approx 63.45\text{ km}^2$).

Raster hasil klasifikasi ini tersimpan dalam format GeoTIFF di:
`../data/tif/pertemuan-5-tif/hasil_klasifikasi_lahan_socah.tif`.

---

## Kesimpulan
1. **Data Sampel:** 50 titik sawah dan 50 titik bukan sawah berhasil dipetakan secara interaktif di wilayah Kecamatan Socah.
2. **Karakteristik Lahan:** Kategori "Bukan Sawah" mencakup berbagai area non-persawahan, dan sawah memiliki fase spektral yang bervariasi sepanjang masa tanam (tidak selalu hijau).
3. **Hasil Klasifikasi:** Kombinasi 4 band multispektral Sentinel-2A dan model Random Forest berhasil membedakan sawah dan bukan sawah dengan akurasi **80%**.
