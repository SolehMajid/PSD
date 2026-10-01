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

# Pemetaan & Klasifikasi Lahan (Sawah & Pemukiman)

Modul ini membahas langkah sederhana dalam memetakan dan mengklasifikasikan lahan **Sawah** dan **Pemukiman (Bukan Sawah)** di **Kecamatan Socah, Kabupaten Bangkalan** menggunakan data koordinat GeoJSON dan citra satelit **Sentinel-2A**.

Seluruh kode praktikum dapat dijalankan pada notebook: [`ambil_data.ipynb`](ambil_data.ipynb).

---

## 1. Data Koordinat (GeoJSON)

Data titik lokasi lahan diambil dari berkas [`50,50,1.geojson`](50,50,1.geojson) yang berisi 3 komponen:
1. **1 Batas Wilayah (Socah):** Area poligon batas Kecamatan Socah.
2. **50 Titik Sawah:** Lokasi lahan pertanian sawah aktif.
3. **50 Titik Bukan Sawah (Pemukiman):** Lokasi kawasan perumahan dan bangunan warga.

### Peta Interaktif (Folium) Wilayah Socah, Sawah, dan Pemukiman

Di bawah ini adalah peta interaktif menggunakan pustaka **`folium`** yang menampilkan:
* **Garis Biru:** Batas wilayah pengamatan Kecamatan Socah.
* **Titik Hijau:** 50 lokasi lahan sawah.
* **Titik Merah:** 50 lokasi pemukiman (bukan sawah).

```{code-cell}
:tags: [hide-input]
import os
import folium
import geopandas as gpd

# Path fleksibel agar dapat dijalankan dari root maupun folder pertemuan-5
geojson_path = "pertemuan-5/50,50,1.geojson" if os.path.exists("pertemuan-5/50,50,1.geojson") else "50,50,1.geojson"
gdf = gpd.read_file(geojson_path)

# Pisahkan layer batas wilayah dan sampel
aoi = gdf[gdf["Sawah"] == "socah"]
sawah = gdf[gdf["Sawah"] == "sawah"]
bukan = gdf[gdf["Sawah"] == "bukan"]

# Ambil titik tengah wilayah Socah
center_point = aoi.geometry.iloc[0].centroid
m = folium.Map(location=[center_point.y, center_point.x], zoom_start=13, tiles="OpenStreetMap")

# 1. Tambahkan Batas Wilayah Kecamatan Socah
folium.GeoJson(
    aoi,
    name="Batas Daerah (Socah)",
    style_function=lambda x: {
        "color": "#0044ff",
        "weight": 2.5,
        "fillColor": "#3388ff",
        "fillOpacity": 0.1
    }
).add_to(m)

# 2. Tambahkan 50 Titik Sawah (Warna Hijau)
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

# 3. Tambahkan 50 Titik Bukan Sawah / Pemukiman (Warna Merah)
g_bukan = folium.FeatureGroup(name="50 Titik Pemukiman (Merah)")
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

# Tambahkan kontrol layer
folium.LayerControl(collapsed=False).add_to(m)

# Tampilkan peta
m
```

---

## 2. Pengunduhan Citra Satelit Sentinel-2A ke File TIF

Citra satelit diunduh langsung dari platform resmi **Copernicus Data Space Ecosystem (CDSE)** menggunakan **openEO API**:
* **Koleksi:** `SENTINEL2_L2A` (Level-2A, sudah terkoreksi atmosfer).
* **Band yang Diambil (Resolusi 10 Meter):**
  * `B02` (Blue)
  * `B03` (Green)
  * `B04` (Red)
  * `B08` (NIR / Near-Infrared)
* **Batas Wilayah (*Extent*):** Berdasarkan koordinat batas Kecamatan Socah.
* **Metode Komposit:** Menggunakan nilai **median** pada periode musim kemarau (Agustus) agar citra bersih dan bebas awan.
* **Hasil Pengunduhan:** Disimpan dalam format GeoTIFF ke file: `../data/tif/pertemuan-5-tif/sentinel2_socah.tif`.

---

## 3. Ekstraksi Fitur Spektral & Indeks Vegetasi (NDVI)

Untuk membedakan tanaman padi di sawah dengan bangunan pemukiman, dihitung nilai **NDVI (*Normalized Difference Vegetation Index*)**:

$$\text{NDVI} = \frac{\text{B08 (NIR)} - \text{B04 (Red)}}{\text{B08 (NIR)} + \text{B04 (Red)}}$$

* **Sawah:** Tanaman padi yang hijau dan sehat menyerap cahaya merah (`B04`) dan memantulkan inframerah dekat (`B08`) secara kuat, sehingga menghasilkan **NDVI tinggi ($\approx 0.48$)**.
* **Pemukiman:** Atap rumah, semen, dan tanah kering memiliki pantulan merah yang lebih tinggi dan inframerah yang lebih rendah, sehingga menghasilkan **NDVI lebih rendah ($\approx 0.31$)**.

Nilai pantulan spektral 100 sampel ini disimpan ke berkas CSV:
`../data/csv/pertemuan-5-csv/dataset_sampel_sawah_pemukiman.csv`.

---

## 4. Hasil Klasifikasi Lahan (Machine Learning)

Dengan membagi data menjadi 75% data latih dan 25% data uji, model **Random Forest Classifier** dilatih untuk menguji validasi pemisahan sawah dan pemukiman:

| Metrik Evaluasi | Pemukiman (Bukan Sawah) | Sawah | Rata-Rata |
| :--- | :---: | :---: | :---: |
| **Precision** | $0.83$ | $0.77$ | **$0.80$** |
| **Recall** | $0.77$ | $0.83$ | **$0.80$** |
| **F1-Score** | $0.80$ | $0.80$ | **$0.80$** |
| **Akurasi Total** | - | - | **$80.0\%$** |

**Kesimpulan:**
Citra satelit Sentinel-2A dan indeks vegetasi NDVI terbukti mampu membedakan area persawahan dan pemukiman di Kecamatan Socah dengan akurasi yang baik dan teruji secara saintifik.
