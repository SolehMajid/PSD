import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium import plugins
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import rasterio
from rasterio.warp import transform
from shapely.geometry import shape, mapping

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Web GIS Tutupan Lahan Jatim",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS untuk tampilan modern & responsif
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Menentukan basis direktori secara dinamis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# ==============================================================================
# 2. CACHING & PEMUATAN DATASET SERTA MODEL
# ==============================================================================
@st.cache_data
def load_dataset():
    csv_candidates = [os.path.join(BASE_DIR, "csv", "dataset_sampel_5kelas_jatim.csv"),
        os.path.join(ROOT_DIR, "UTS", "csv", "dataset_sampel_5kelas_jatim.csv"),
        "csv/dataset_sampel_5kelas_jatim.csv"
    ]
    for path in csv_candidates:
        if os.path.exists(path):
            return pd.read_csv(path)
    st.error("Berkas dataset CSV tidak ditemukan!")
    return None

FEATURE_COLS = ["B02", "B03", "B04", "B08", "B8A", "B11", "NDVI", "MNDWI", "NDBI", "Ratio_B8A_B11"]

@st.cache_resource
def load_rf_model(df):
    model_path = os.path.join(BASE_DIR, "model_rf.pkl")
    X = df[FEATURE_COLS]
    y = df["kelas_nama"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        joblib.dump(model, model_path)
        
    return model, X, X_train, X_test, y_train, y_test

df_fitur = load_dataset()
if df_fitur is None:
    st.stop()

rf_model, X, X_train, X_test, y_train, y_test = load_rf_model(df_fitur)
y_pred = rf_model.predict(X_test)
akurasi_test = accuracy_score(y_test, y_pred)

# Konfigurasi visual 5 kelas
class_configs = {
    "building": {
        "label": "Bangunan (Built-up)",
        "color": "#e74c3c",      # Merah
        "fill_color": "#ff7675",
        "file": os.path.join(BASE_DIR, "data", "geojson", "building.geojson")
    },
    "sawah": {
        "label": "Lahan Pertanian (Sawah)",
        "color": "#f1c40f",      # Kuning Terang
        "fill_color": "#f39c12",
        "file": os.path.join(BASE_DIR, "data", "geojson", "sawah.geojson")
    },
    "perairan": {
        "label": "Perairan (Water Body)",
        "color": "#0984e3",      # Biru
        "fill_color": "#74b9ff",
        "file": os.path.join(BASE_DIR, "data", "geojson", "perairan.geojson")
    },
    "hutan": {
        "label": "Hutan Biasa",
        "color": "#27ae60",      # Hijau Rimba
        "fill_color": "#2ecc71",
        "file": os.path.join(BASE_DIR, "data", "geojson", "Hutan Biasa.geojson")
    },
    "mangrove": {
        "label": "Hutan Mangrove",
        "color": "#8e44ad",      # Ungu Royal
        "fill_color": "#a29bfe",
        "file": os.path.join(BASE_DIR, "data", "geojson", "Mangrove.geojson")
    }
}

# ==============================================================================
# 3. SIDEBAR: KONTROL FILTER & MODE TAMPILAN
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3a8a, #0284c7); padding: 10px 14px; border-radius: 8px; color: white; margin-bottom: 12px;'>
        <div style='font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85;'>Dashboard Spasial Regional</div>
        <div style='font-size: 18px; font-weight: 700;'>Jawa Timur LULC</div>
    </div>
    """, unsafe_allow_html=True)
    st.title("Panel Kontrol GIS")
    st.markdown("**Proyek Sains Data - Jawa Timur**")
    st.markdown("---")
    
    st.subheader("1. Pilih Layer / Mode Peta")
    mode_peta = st.radio(
        "Pilih layer analisis yang ingin ditampilkan:",
        [
            "Sebelum Klasifikasi (Sampel Asli)",
            "Pembagian Data Split (Train vs Test)",
            "Hasil Evaluasi (Benar vs Meleset)",
            "Peta Tutupan Lahan Penuh (LULC Map)"
        ],
        index=2
    )
    
    st.markdown("---")
    st.subheader("2. Filter Kelas Tutupan Lahan")
    st.caption("Centang kelas yang ingin dimunculkan di atas peta satelit:")
    
    selected_classes = []
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        pilih_semua = st.button("Pilih Semua", use_container_width=True)
    with col_c2:
        hapus_semua = st.button("Hapus Semua", use_container_width=True)
        
    for k_code, cfg in class_configs.items():
        default_val = True
        if hapus_semua:
            default_val = False
        elif pilih_semua:
            default_val = True
        
        checked = st.checkbox(f"{cfg['label']}",
            value=default_val,
            key=f"chk_{k_code}"
        )
        if checked:
            selected_classes.append(cfg["label"])
            
    st.markdown("---")
    st.markdown("""
    **Spesifikasi Citra & Model:**
    - **Satelit**: Sentinel-2A L2A (CDSE)
    - **Resolusi**: 60 Meter (Anti-OOM)
    - **Band**: B02, B03, B04, B08, B8A, B11
    - **Model**: Random Forest (100 Trees)
    """)

# ==============================================================================
# 4. HEADER UTAMA & KARTU METRIK KPI
# ==============================================================================
st.markdown('<div class="main-title"> Web GIS: Klasifikasi Tutupan Lahan Jawa Timur</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Pemantauan 5 Kelas Tutupan Lahan Berbasis Citra Satelit Sentinel-2A & Model Random Forest (Skala Penuh Se-Provinsi)</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-val"style="color: #10b981;">82.35%</div>
        <div class="metric-lbl">Akurasi Data Uji</div>
    </div>
    """, unsafe_allow_html=True)
with col_m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-val"style="color: #3b82f6;">270</div>
        <div class="metric-lbl">Total Sampel Poligon</div>
    </div>
    """, unsafe_allow_html=True)
with col_m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-val"style="color: #6366f1;">202 / 68</div>
        <div class="metric-lbl">Train / Test (75:25)</div>
    </div>
    """, unsafe_allow_html=True)
with col_m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-val"style="color: #8b5cf6;">60 Meter</div>
        <div class="metric-lbl">Resolusi Spasial</div>
    </div>
    """, unsafe_allow_html=True)
with col_m5:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-val"style="color: #ec4899;">5 Kelas</div>
        <div class="metric-lbl">Kategori Tutupan</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 5. TAB NAVIGASI UTAMA
# ==============================================================================
tab_map, tab_eval, tab_geojson, tab_simulasi, tab_alur = st.tabs([
    "Peta Interaktif Leaflet",
    "Analisis & Evaluasi Model",
    "Prediksi Poligon GeoJSON (Digitasi Baru)",
    "Uji Simulasi Spektral Real-Time",
    "Alur Pipeline Data (Ambil-Proses-Klasifikasi)"
])

# ------------------------------------------------------------------------------
# TAB 1: PETA INTERAKTIF LEAFLET
# ------------------------------------------------------------------------------
with tab_map:
    st.subheader(f"Tampilan Peta: {mode_peta}")
    
    # Mode 4: Peta Statis Land Use / Land Cover
    if "LULC Map" in mode_peta:
        st.info(" **Peta Tematik Klasifikasi Tutupan Lahan Penuh Jawa Timur**: Dihasilkan dari prediksi model Random Forest ke seluruh ~5,8 juta piksel daratan Jawa Timur dengan resolusi efektif.")
        lulc_img_candidates = [os.path.join(ROOT_DIR, "assets", "images", "images_uts", "4.peta_landuse_landcover_jatim.png"),
            os.path.join(BASE_DIR, "data", "images", "peta_landuse_landcover_jatim.png")
        ]
        found_img = False
        for img_p in lulc_img_candidates:
            if os.path.exists(img_p):
                st.image(img_p, caption="Peta Tematik Land Use / Land Cover (LULC) Provinsi Jawa Timur (Format Standar Kartografi Ilmiah)", use_container_width=True)
                found_img = True
                break
        if not found_img:
            st.warning("Citra peta LULC belum ditemukan di direktori aset.")
            
    else:
        # Menyiapkan peta interaktif Folium
        center_lat, center_lon = -7.65, 112.55
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")
        
        # Basemap Citra Satelit Asli Esri
        folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="Citra Satelit Asli (Esri)"
        ).add_to(m)
        
        # Filter data sesuai kelas yang dipilih di sidebar
        df_filtered = df_fitur[df_fitur["kelas_nama"].isin(selected_classes)].copy()
        
        if len(df_filtered) == 0:
            st.warning("Tidak ada kelas yang dipilih. Silakan centang minimal satu kelas tutupan lahan pada panel samping (sidebar).")
        else:
            # Memuat data poligon dari GeoJSON jika ada
            gdf_dict = {}
            for k_code, cfg in class_configs.items():
                if os.path.exists(cfg["file"]):
                    try:
                        import geopandas as gpd
                        gdf_dict[cfg["label"]] = gpd.read_file(cfg["file"])
                    except Exception:
                        pass

            # MODE 1: SEBELUM KLASIFIKASI (SAMPEL ASLI)
            if "Sebelum Klasifikasi" in mode_peta:
                st.caption(f"Menampilkan {len(df_filtered)} poligon sampel hasil digitasi awal se-Jawa Timur:")
                for k_name in selected_classes:
                    cfg = [c for c in class_configs.values() if c["label"] == k_name][0]
                    sub_df = df_filtered[df_filtered["kelas_nama"] == k_name]
                    
                    fg = folium.FeatureGroup(name=f"{k_name} ({len(sub_df)} Sampel)")
                    for _, row in sub_df.iterrows():
                        popup_html = f"""
                        <div style='font-family: Arial; font-size: 12px; width: 220px;'>
                            <b style='color: {cfg["color"]}; font-size: 13px;'>{k_name}</b><br>
                            <b>No Sampel:</b> #{int(row.get('no', 0))}<br>
                            <hr style='margin: 4px 0;'>
                            <b>NDVI:</b> {row['NDVI']:.4f} | <b>MNDWI:</b> {row['MNDWI']:.4f}<br>
                            <b>NDBI:</b> {row['NDBI']:.4f} | <b>Ratio:</b> {row['Ratio_B8A_B11']:.4f}<br>
                            <small style='color: #64748b;'>Lon: {row['longitude']:.4f}, Lat: {row['latitude']:.4f}</small>
                        </div>
                        """
                        folium.CircleMarker(
                            location=[row["latitude"], row["longitude"]],
                            radius=7,
                            color="#2c3e50",
                            fill=True,
                            fill_color=cfg["color"],
                            fill_opacity=0.85,
                            popup=folium.Popup(popup_html, max_width=250)
                        ).add_to(fg)
                    fg.add_to(m)

            # MODE 2: SPLIT DATA (TRAIN VS TEST)
            elif "Pembagian Data Split" in mode_peta:
                st.caption("Menampilkan pembagian data: **Data Latih 75%** (Lingkaran Solid Biru) vs **Data Uji 25%** (Persegi Oranye Tebal):")
                fg_train = folium.FeatureGroup(name="Data Latih (Train 75%)")
                fg_test = folium.FeatureGroup(name="Data Uji (Test 25%)")
                
                for idx, row in df_filtered.iterrows():
                    cfg = [c for c in class_configs.values() if c["label"] == row["kelas_nama"]][0]
                    is_test = idx in X_test.index
                    status_split = "Data Uji (Test 25%)" if is_test else "Data Latih (Train 75%)"
                    popup_html = f"""
                    <div style='font-family: Arial; font-size: 12px; width: 220px;'>
                        <b style='color: {cfg["color"]};'>{row["kelas_nama"]}</b><br>
                        <b>Status:</b> <span style='color: {"#e67e22" if is_test else "#2980b9"}; font-weight: bold;'>{status_split}</span><br>
                        <hr style='margin: 4px 0;'>
                        <b>NDVI:</b> {row['NDVI']:.4f} | <b>MNDWI:</b> {row['MNDWI']:.4f}<br>
                        <b>B08 (NIR):</b> {int(row['B08'])} | <b>B11 (SWIR):</b> {int(row['B11'])}
                    </div>
                    """
                    if is_test:
                        folium.CircleMarker(location=[row["latitude"], row["longitude"]],
                            radius=9,
                            color="#d35400",
                            weight=3,
                            fill=True,
                            fill_color="#e67e22",
                            fill_opacity=0.9,
                            popup=folium.Popup(popup_html, max_width=250)
                        ).add_to(fg_test)
                    else:
                        folium.CircleMarker(location=[row["latitude"], row["longitude"]],
                            radius=6,
                            color="#1b4f72",
                            fill=True,
                            fill_color="#2980b9",
                            fill_opacity=0.75,
                            popup=folium.Popup(popup_html, max_width=250)
                        ).add_to(fg_train)
                        
                fg_train.add_to(m)
                fg_test.add_to(m)

            # MODE 3: HASIL EVALUASI (BENAR VS MELESET)
            elif "Hasil Evaluasi" in mode_peta:
                st.caption("Hasil pengujian model pada Data Uji:  **Prediksi BENAR** (Border Hijau Tebal) vs  **Prediksi MELESET** (Border Merah Putus-putus):")
                fg_benar = folium.FeatureGroup(name="Prediksi BENAR (56 Poligon)")
                fg_salah = folium.FeatureGroup(name="Prediksi SALAH (12 Poligon)")
                
                df_test_eval = df_filtered.loc[df_filtered.index.intersection(X_test.index)].copy()
                
                for idx, row in df_test_eval.iterrows():
                    actual = row["kelas_nama"]
                    pred = rf_model.predict(pd.DataFrame([row[["B02", "B03", "B04", "B08", "B8A", "B11", "NDVI", "MNDWI", "NDBI", "Ratio_B8A_B11"]]]))[0]
                    is_correct = (actual == pred)
                    
                    popup_html = f"""
                    <div style='font-family: Arial; font-size: 12px; width: 240px;'>
                        <b style='color: {"#27ae60" if is_correct else "#c0392b"}; font-size: 13px;'>
                            {"PREDIKSI BENAR" if is_correct else "PREDIKSI MELESET"}
                        </b><br>
                        <hr style='margin: 4px 0;'>
                        <b>Kelas Aktual:</b> {actual}<br>
                        <b>Prediksi Model:</b> <span style='font-weight: bold; color: {"#27ae60" if is_correct else "#c0392b"};'>{pred}</span><br>
                        <hr style='margin: 4px 0;'>
                        <b>NDVI:</b> {row['NDVI']:.4f} | <b>MNDWI:</b> {row['MNDWI']:.4f}<br>
                        <b>NDBI:</b> {row['NDBI']:.4f} | <b>Ratio:</b> {row['Ratio_B8A_B11']:.4f}
                    </div>
                    """
                    if is_correct:
                        folium.CircleMarker(location=[row["latitude"], row["longitude"]],
                            radius=9,
                            color="#27ae60",
                            weight=3.5,
                            fill=True,
                            fill_color="#2ecc71",
                            fill_opacity=0.9,
                            popup=folium.Popup(popup_html, max_width=260)
                        ).add_to(fg_benar)
                    else:
                        folium.CircleMarker(location=[row["latitude"], row["longitude"]],
                            radius=11,
                            color="#c0392b",
                            weight=4,
                            fill=True,
                            fill_color="#e74c3c",
                            fill_opacity=0.95,
                            popup=folium.Popup(popup_html, max_width=260)
                        ).add_to(fg_salah)
                        
                fg_benar.add_to(m)
                fg_salah.add_to(m)
            
            folium.LayerControl(collapsed=False).add_to(m)
            plugins.Fullscreen().add_to(m)
            
            # Render peta menggunakan komponen HTML
            html_map = m.get_root().render()
            components.html(html_map, height=580)
            
    st.caption("ℹ **Tip Interaksi**: Gunakan tombol fullscreen di kiri atas peta untuk memperluas tampilan, geser peta, dan klik setiap lingkaran/poligon untuk melihat detail profil spektral.")

# ------------------------------------------------------------------------------
# TAB 2: ANALISIS & EVALUASI MODEL
# ------------------------------------------------------------------------------
with tab_eval:
    st.subheader("Analisis Kinerja Model Random Forest Classifier")
    
    col_e1, col_e2 = st.columns([1.1, 1])
    
    with col_e1:
        st.markdown("**1. Matriks Kesalahan Klasifikasi (Confusion Matrix)**")
        labels_unique = list(class_configs.keys())
        labels_display = [class_configs[k]["label"] for k in labels_unique]
        
        cm = confusion_matrix(y_test, y_pred, labels=labels_display)
        
        fig_cm, ax_cm = plt.subplots(figsize=(7, 5.5), dpi=130)
        short_names = ["Bangunan", "Sawah", "Perairan", "Hutan", "Mangrove"]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
            xticklabels=short_names, yticklabels=short_names, ax=ax_cm,
            annot_kws={"size": 12, "weight": "bold"}
        )
        ax_cm.set_xlabel("Kelas Prediksi Model", fontsize=10, fontweight="bold")
        ax_cm.set_ylabel("Kelas Aktual (Ground Truth)", fontsize=10, fontweight="bold")
        ax_cm.set_title("Confusion Matrix (Data Uji 68 Sampel)", fontsize=11, fontweight="bold", pad=10)
        plt.tight_layout()
        st.pyplot(fig_cm)
        
        st.caption("""
        **Analisis Kesalahan Prediksi Utama:**
        - **4 sampel Air tertukar menjadi Sawah**: Karena sawah tergenang air irigasi di awal masa tanam memiliki pantulan mirip perairan dangkal.
        - **2 sampel Sawah tertukar menjadi Bangunan**: Sawah kering pada masa bera (*bare soil*) di bulan Agustus memantulkan gelombang SWIR mirip material atap/tanah.
        """)

    with col_e2:
        st.markdown("**2. Tingkat Kepentingan Fitur (Feature Importance)**")
        feat_imp = pd.Series(rf_model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=True)
        
        fig_fi, ax_fi = plt.subplots(figsize=(7, 5.5), dpi=130)
        bars = ax_fi.barh(feat_imp.index, feat_imp.values * 100, color="#3b82f6", edgecolor="black", linewidth=0.7)
        for b in bars:
            val = b.get_width()
            ax_fi.text(val + 0.3, b.get_y() + b.get_height()/2, f"{val:.1f}%", va="center", fontsize=9, fontweight="bold")
        ax_fi.set_xlim(0, 20)
        ax_fi.set_xlabel("Tingkat Kontribusi (%)", fontsize=10, fontweight="bold")
        ax_fi.set_title("10 Fitur Paling Berpengaruh dalam Klasifikasi", fontsize=11, fontweight="bold", pad=10)
        ax_fi.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_fi)
        
        st.caption("""
        **Wawasan Fitur:**
        - **MNDWI (16.1%) & NDVI (14.2%)**: Indeks matematika terbukti menyumbang kontribusi terbesar dalam memisahkan badan air dan vegetasi.
        - **B08 & B8A (>22%)**: Membuktikan spektrum inframerah sangat krusial memisahkan kerapatan kanopi pohon.
        """)
        
    st.markdown("---")
    st.markdown("**3. Tabel Laporan Klasifikasi Rinci (Classification Report)**")
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose()
    try:
        st.dataframe(report_df.style.format({
                "precision": "{:.2f}",
                "recall": "{:.2f}",
                "f1-score": "{:.2f}",
                "support": "{:.0f}"
            }).background_gradient(cmap="Blues", subset=["f1-score"]),
            use_container_width=True
        )
    except Exception:
        st.table(report_df.round(2))

# ------------------------------------------------------------------------------
# TAB 3: INPUT POLIGON GEOJSON & PREDIKSI MODEL RANDOM FOREST
# ------------------------------------------------------------------------------
with tab_geojson:
    st.subheader("Input Poligon GeoJSON & Prediksi Otomatis Model")
    st.markdown("""Fitur ini dirancang khusus untuk menguji **poligon baru hasil digitasi GeoJSON**.
    Sistem akan:
    1. Membaca geometri poligon digitasi Anda dan menghitung titik tengah (*centroid*).
    2. **Mengekstrak otomatis 6 band spektral** (`B02, B03, B04, B08, B8A, B11`) langsung dari citra satelit **Sentinel-2A se-Jawa Timur (60m)**.
    3. Menghitung 4 indeks spektral (**NDVI**, **MNDWI**, **NDBI**, **Ratio B8A/B11**).
    4. Mengirimkan nilai spektral ke model **Random Forest** untuk memprediksi kelas tutupan lahan dan tingkat keyakinan (*confidence score*).
    5. Menampilkan poligon Anda langsung di atas **peta satelit interaktif Leaflet** dengan warna sesuai kelas hasil prediksi!
    """)
    
    st.markdown("---")
    col_g1, col_g2 = st.columns([1.2, 1])
    
    with col_g1:
        st.markdown("##### 1. Pilih Sumber / Metode Input GeoJSON")
        metode_input = st.radio(
            "Metode Input:",
            [
                "Tempel Teks GeoJSON (Paste JSON)",
                "Unggah Berkas .geojson / .json",
                "Gunakan Preset Poligon Digitasi Jawa Timur"
            ],
            horizontal=True
        )
        
        presets_geojson = {
            "Poligon Sawah Aluvial (Bojonegoro)": {
                "desc": "Area persawahan aktif di Bojonegoro, Jawa Timur",
                "json": """{
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
              112.6635014,
              -7.265604
            ],
            [
              112.6651213,
              -7.2661689
            ],
            [
              112.6638304,
              -7.2673239
            ],
            [
              112.6626534,
              -7.2662819
            ],
            [
              112.6635014,
              -7.265604
            ]
          ]
        ]
      }
    }
  ]
}"""
            },
            "Poligon Hutan Rimba Pegunungan (Gunung Arjuno)": {
                "desc": "Kawasan hutan lebat di lereng Gunung Arjuno, Jawa Timur",
                "json": """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"keterangan": "Digitasi Hutan Arjuno"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [112.5850, -7.7650],
            [112.5970, -7.7650],
            [112.5970, -7.7750],
            [112.5850, -7.7750],
            [112.5850, -7.7650]
          ]
        ]
      }
    }
  ]
}"""
            },
            "Poligon Hutan Mangrove Pesisir (Wonorejo Surabaya)": {
                "desc": "Zona hutan bakau muara di pantai timur Surabaya",
                "json": """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"keterangan": "Digitasi Mangrove Wonorejo"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [112.8280, -7.3120],
            [112.8380, -7.3120],
            [112.8380, -7.3220],
            [112.8280, -7.3220],
            [112.8280, -7.3120]
          ]
        ]
      }
    }
  ]
}"""
            },
            "Poligon Bangunan / Perkotaan (Pusat Kota Surabaya)": {
                "desc": "Kawasan terbangun padat di pusat kota Surabaya",
                "json": """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"keterangan": "Digitasi Bangunan Surabaya"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [112.7420, -7.2620],
            [112.7520, -7.2620],
            [112.7520, -7.2720],
            [112.7420, -7.2720],
            [112.7420, -7.2620]
          ]
        ]
      }
    }
  ]
}"""
            },
            "Poligon Perairan Terbuka (Selat Madura)": {
                "desc": "Badan air laut di Selat Madura",
                "json": """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"keterangan": "Digitasi Perairan Selat Madura"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [112.7450, -7.1850],
            [112.7600, -7.1850],
            [112.7600, -7.2000],
            [112.7450, -7.2000],
            [112.7450, -7.1850]
          ]
        ]
      }
    }
  ]
}"""
            },
            "Contoh Poligon Anda (Koordinat Prompt)": {
                "desc": "Contoh koordinat poligon yang Anda tanyakan (Bujur 76.06°, Lintang 31.97°)",
                "json": """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [76.0628261, 31.9712874],
            [76.0896377, 31.9768312],
            [76.0939946, 31.9502462],
            [76.0572962, 31.9515258],
            [76.0628261, 31.9712874]
          ]
        ]
      }
    }
  ]
}"""
            }
        }
        
        raw_geojson_str = ""
        
        if "Preset" in metode_input:
            p_pilih = st.selectbox("Pilih Poligon Contoh:", list(presets_geojson.keys()))
            st.caption(presets_geojson[p_pilih]["desc"])
            raw_geojson_str = presets_geojson[p_pilih]["json"]
            st.text_area("Pratinjau Format GeoJSON:", value=raw_geojson_str, height=220)
            
        elif "Unggah" in metode_input:
            uploaded_file = st.file_uploader("Unggah berkas GeoJSON (.geojson atau .json):", type=["geojson", "json"])
            if uploaded_file is not None:
                raw_geojson_str = uploaded_file.read().decode("utf-8")
                st.success("Berkas GeoJSON berhasil diunggah!")
            else:
                st.info("Silakan pilih berkas .geojson dari laptop Anda.")
                
        else:
            raw_geojson_str = st.text_area(
                "Tempelkan kode GeoJSON Polygon Anda di sini:",
                value=presets_geojson["Poligon Sawah Aluvial (Bojonegoro)"]["json"],
                height=240,
                help="Pastikan format berupa FeatureCollection atau Polygon valid."
            )
            
        btn_prediksi_geojson = st.button("Proses & Prediksi Poligon GeoJSON Ini", type="primary", use_container_width=True)

    with col_g2:
        st.markdown("##### 2. Hasil Ekstraksi Citra & Prediksi Model")
        
        if btn_prediksi_geojson and raw_geojson_str.strip():
            try:
                parsed_json = json.loads(raw_geojson_str)
                
                if parsed_json.get("type") == "FeatureCollection"and len(parsed_json.get("features", [])) > 0:
                    geom_dict = parsed_json["features"][0]["geometry"]
                elif parsed_json.get("type") == "Feature":
                    geom_dict = parsed_json["geometry"]
                elif "coordinates" in parsed_json:
                    geom_dict = parsed_json
                else:
                    st.error("Format GeoJSON tidak memiliki struktur Polygon/Feature yang valid.")
                    geom_dict = None
                    
                if geom_dict:
                    poly_geom = shape(geom_dict)
                    centroid_lon = float(poly_geom.centroid.x)
                    centroid_lat = float(poly_geom.centroid.y)
                    
                    st.write(f" **Titik Tengah (Centroid)**: Bujur `{centroid_lon:.5f}°`, Lintang `{centroid_lat:.5f}°`")
                    
                    in_jatim = (111.0 <= centroid_lon <= 114.7) and (-8.9 <= centroid_lat <= -6.5)
                    
                    tif_path_candidates = [os.path.join(BASE_DIR, "data", "tif", "sentinel2_jatim_60m.tif"),
                        os.path.join(ROOT_DIR, "UTS", "data", "tif", "sentinel2_jatim_60m.tif"),
                        "data/tif/sentinel2_jatim_60m.tif"
                    ]
                    tif_path = None
                    for tp in tif_path_candidates:
                        if os.path.exists(tp):
                            tif_path = tp
                            break
                            
                    if in_jatim and tif_path:
                        with rasterio.open(tif_path) as src:
                            xs, ys = transform("EPSG:4326", src.crs, [centroid_lon], [centroid_lat])
                            coords_sample = [(xs[0], ys[0])]
                            pixel_values = list(src.sample(coords_sample))[0]
                            b2, b3, b4, b8, b8a, b11 = [float(v) for v in pixel_values]
                            
                        ndvi = (b8 - b4) / (b8 + b4 + 1e-6)
                        mndwi = (b3 - b11) / (b3 + b11 + 1e-6)
                        ndbi = (b11 - b8) / (b11 + b8 + 1e-6)
                        ratio_b8a_b11 = b8a / (b11 + 1e-6)
                        
                        fitur_input = pd.DataFrame([{
                            "B02": b2, "B03": b3, "B04": b4, "B08": b8,
                            "B8A": b8a, "B11": b11, "NDVI": ndvi,
                            "MNDWI": mndwi, "NDBI": ndbi, "Ratio_B8A_B11": ratio_b8a_b11
                        }])
                        
                        pred_kelas = rf_model.predict(fitur_input)[0]
                        pred_probabilitas = rf_model.predict_proba(fitur_input)[0]
                        max_prob = max(pred_probabilitas) * 100
                        pred_cfg = [c for c in class_configs.values() if c["label"] == pred_kelas][0]
                        
                        st.markdown(f"""
                        <div style="background-color: {pred_cfg['fill_color']}; border-left: 6px solid {pred_cfg['color']}; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                            <span style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: #1e293b;">HASIL KLASIFIKASI MODEL RANDOM FOREST:</span><br>
                            <span style="font-size: 22px; font-weight: 800; color: #0f172a;">{pred_kelas}</span><br>
                            <span style="font-size: 14px; color: #334155;">Tingkat Keyakinan Model: <b>{max_prob:.1f}%</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.caption("Nilai 6 Band & 4 Indeks dari Citra Sentinel-2A di Titik Poligon:")
                        st.dataframe(fitur_input.style.format({
                            "B02": "{:.0f}", "B03": "{:.0f}", "B04": "{:.0f}", "B08": "{:.0f}", "B8A": "{:.0f}", "B11": "{:.0f}",
                            "NDVI": "{:.4f}", "MNDWI": "{:.4f}", "NDBI": "{:.4f}", "Ratio_B8A_B11": "{:.4f}"
                        }), use_container_width=True)
                        
                        prob_df = pd.DataFrame({
                            "Kelas": rf_model.classes_,
                            "Probabilitas (%)": (pred_probabilitas * 100).round(1)
                        }).sort_values("Probabilitas (%)", ascending=False)
                        st.bar_chart(prob_df.set_index("Kelas"))
                        
                        st.markdown("##### 3. Tampilan Poligon Digitasi di Atas Citra Satelit")
                        m_poly = folium.Map(location=[centroid_lat, centroid_lon], zoom_start=14, tiles="CartoDB positron")
                        folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                            attr="Esri World Imagery",
                            name="Citra Satelit Asli (Esri)"
                        ).add_to(m_poly)
                        
                        popup_txt = f"<b>{pred_kelas}</b><br>Keyakinan: {max_prob:.1f}%<br>NDVI: {ndvi:.4f}"
                        folium.GeoJson(geom_dict,
                            style_function=lambda x, col=pred_cfg["color"], fcol=pred_cfg["fill_color"]: {
                                "color": col,
                                "weight": 3.5,
                                "fillColor": fcol,
                                "fillOpacity": 0.65
                            },
                            popup=popup_txt
                        ).add_to(m_poly)
                        
                        folium.Marker(location=[centroid_lat, centroid_lon],
                            icon=folium.Icon(color="red", icon="info-sign"),
                            popup=f"Centroid: {centroid_lat:.4f}, {centroid_lon:.4f}"
                        ).add_to(m_poly)
                        
                        components.html(m_poly.get_root().render(), height=380)
                        
                    else:
                        st.warning(f"""
                         **Poligon Berada di Luar Wilayah Jawa Timur:**
                        - Koordinat terdeteksi: **Bujur: `{centroid_lon:.4f}°`, Lintang: `{centroid_lat:.4f}°`**.
                        - Wilayah cakupan citra satelit Sentinel-2A lokal pada proyek ini adalah **Provinsi Jawa Timur** (Bujur 111.1° s/d 114.6° BT, Lintang -8.7° s/d -6.6° LS).
                        
                        *Sistem tetap menampilkan visualisasi spasial poligon Anda di bawah ini pada peta satelit global Esri:*
                        """)
                        
                        m_poly_out = folium.Map(location=[centroid_lat, centroid_lon], zoom_start=12, tiles="CartoDB positron")
                        folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                            attr="Esri World Imagery",
                            name="Citra Satelit Asli (Esri)"
                        ).add_to(m_poly_out)
                        
                        folium.GeoJson(geom_dict,
                            style_function=lambda x: {
                                "color": "#e74c3c",
                                "weight": 3,
                                "fillColor": "#ff7675",
                                "fillOpacity": 0.5
                            },
                            popup="Poligon Digitasi Pengguna"
                        ).add_to(m_poly_out)
                        
                        folium.Marker(location=[centroid_lat, centroid_lon],
                            popup=f"Centroid: {centroid_lat:.4f}, {centroid_lon:.4f}"
                        ).add_to(m_poly_out)
                        
                        components.html(m_poly_out.get_root().render(), height=380)
                        st.info(" **Tips:** Untuk melihat prediksi otomatis dari model Random Forest Jawa Timur, pilih salah satu contoh preset digitasi Jawa Timur (misalnya Sawah Bojonegoro, Hutan Arjuno, atau Mangrove Wonorejo) pada pilihan di sebelah kiri.")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses GeoJSON: {e}")
        else:
            st.info("Silakan pilih poligon GeoJSON di kolom sebelah kiri dan klik tombol **'Proses & Prediksi Poligon GeoJSON Ini'**.")

# ------------------------------------------------------------------------------
# TAB 4: UJI SIMULASI SPEKTRAL REAL-TIME
# ------------------------------------------------------------------------------
with tab_simulasi:
    st.subheader("Uji Simulasi Prediksi Nilai Spektral Real-Time")
    st.write("Masukkan nilai pantulan band citra atau pilih profil contoh lahan di bawah ini untuk melihat bagaimana model Random Forest menebak kelas tutupan lahannya secara seketika:")
    
    preset = st.selectbox(
        "Pilih Profil Contoh Siap Pakai (Preset):",
        [
            "Custom (Atur Manual)",
            "Contoh Karakteristik Lahan Sawah Basah",
            "Contoh Karakteristik Hutan Biasa Pegunungan",
            "Contoh Karakteristik Hutan Mangrove Pesisir",
            "Contoh Karakteristik Bangunan / Area Perkotaan",
            "Contoh Karakteristik Perairan / Laut"
        ]
    )
    
    # Nilai default berdasarkan preset
    presets_data = {
        "Contoh Karakteristik Lahan Sawah Basah": {"b2": 706, "b3": 993, "b4": 1020, "b8": 1721, "b8a": 1765, "b11": 1684},
        "Contoh Karakteristik Hutan Biasa Pegunungan": {"b2": 568, "b3": 750, "b4": 707, "b8": 2535, "b8a": 2754, "b11": 2183},
        "Contoh Karakteristik Hutan Mangrove Pesisir": {"b2": 511, "b3": 734, "b4": 579, "b8": 2467, "b8a": 2644, "b11": 1159},
        "Contoh Karakteristik Bangunan / Area Perkotaan": {"b2": 1269, "b3": 1453, "b4": 1683, "b8": 2078, "b8a": 2130, "b11": 2593},
        "Contoh Karakteristik Perairan / Laut": {"b2": 663, "b3": 827, "b4": 625, "b8": 813, "b8a": 825, "b11": 603}
    }
    
    defaults = presets_data.get(preset, {"b2": 800, "b3": 1000, "b4": 900, "b8": 2000, "b8a": 2100, "b11": 1500})
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        in_b2 = st.slider("B02 - Blue (Pantulan Biru)", 200, 5000, int(defaults["b2"]))
        in_b3 = st.slider("B03 - Green (Pantulan Hijau)", 200, 5000, int(defaults["b3"]))
    with col_s2:
        in_b4 = st.slider("B04 - Red (Pantulan Merah)", 200, 5000, int(defaults["b4"]))
        in_b8 = st.slider("B08 - NIR (Inframerah Dekat)", 200, 6000, int(defaults["b8"]))
    with col_s3:
        in_b8a = st.slider("B8A - Narrow NIR", 200, 6000, int(defaults["b8a"]))
        in_b11 = st.slider("B11 - SWIR-1 (Inframerah Pendek)", 200, 5000, int(defaults["b11"]))
        
    # Kalkulasi 4 Indeks Spektral Otomatis
    c_ndvi = (in_b8 - in_b4) / (in_b8 + in_b4 + 1e-6)
    c_mndwi = (in_b3 - in_b11) / (in_b3 + in_b11 + 1e-6)
    c_ndbi = (in_b11 - in_b8) / (in_b11 + in_b8 + 1e-6)
    c_ratio = in_b8a / (in_b11 + 1e-6)
    
    st.markdown("##### Hasil Perhitungan Indeks Spektral Otomatis:")
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.metric("NDVI (Kehijauan)", f"{c_ndvi:.4f}")
    col_i2.metric("MNDWI (Kebasahan Air)", f"{c_mndwi:.4f}")
    col_i3.metric("NDBI (Bangunan)", f"{c_ndbi:.4f}")
    col_i4.metric("Ratio B8A/B11", f"{c_ratio:.4f}")
    
    if st.button("Prediksi Kelas Tutupan Lahan Sekarang", type="primary", use_container_width=True):
        input_data = pd.DataFrame([{
            "B02": in_b2, "B03": in_b3, "B04": in_b4, "B08": in_b8,
            "B8A": in_b8a, "B11": in_b11, "NDVI": c_ndvi,
            "MNDWI": c_mndwi, "NDBI": c_ndbi, "Ratio_B8A_B11": c_ratio
        }])
        
        pred_res = rf_model.predict(input_data)[0]
        pred_prob = rf_model.predict_proba(input_data)[0]
        
        st.success(f"### Hasil Prediksi Model: **{pred_res}**")
        
        # Probabilitas bar chart
        prob_df = pd.DataFrame({
            "Kelas": rf_model.classes_,
            "Probabilitas (%)": (pred_prob * 100).round(1)
        }).sort_values("Probabilitas (%)", ascending=False)
        
        st.write("Tingkat Keyakinan Prediksi per Kelas (Probability Confidence):")
        st.bar_chart(prob_df.set_index("Kelas"))

# ------------------------------------------------------------------------------
# TAB 4: ALUR PIPELINE DATA (AMBIL - PROSES - KLASIFIKASI - INFORMASI)
# ------------------------------------------------------------------------------
with tab_alur:
    st.subheader("Alur Pipeline Data Science Sesuai Arahan Tugas")
    st.info("Sesuai instruksi: **Ambil -> Proses -> Klasifikasi -> Dapatkan Informasi**")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("""
        #### 1. Tahap AMBIL (Data Ingestion)
        - **Sumber**: Cloud Copernicus Data Space Ecosystem (CDSE) melalui openEO Python Client.
        - **Cakupan Spasial**: 100% full Provinsi Jawa Timur (Ngawi hingga Banyuwangi).
        - **Reduksi Median**: Periode 1–31 Agustus 2024 (puncak musim kemarau) untuk mengeliminasi awan secara otomatis (*cloud-free mosaic*).
        - **Resampling 60 Meter**: Mengurangi beban piksel 36x lipat sehingga pemrosesan bebas dari error *Out-of-Memory (OOM)*.
        
        #### 2. Tahap PROSES (Data Preprocessing & Feature Engineering)
        - Penyelarasan sistem proyeksi vektor WGS84 (`EPSG:4326`) ke UTM Zone 49S (`EPSG:32749`).
        - Ekstraksi nilai piksel dari 270 titik centroid poligon GeoJSON.
        - Perhitungan 4 indeks kunci: **NDVI**, **MNDWI**, **NDBI**, dan **Ratio_B8A_B11**.
        - Pembagian dataset secara berstrata (*Stratified Split 75% : 25%*) untuk menjamin keseimbangan proporsi kelas.
        """)
    with col_p2:
        st.markdown("""
        #### 3. Tahap KLASIFIKASI (Machine Learning Modeling)
        - Pelatihan model **Random Forest Classifier** (100 pohon keputusan).
        - Model dilatih murni pada 202 sampel data latih, dan diuji pada 68 sampel data uji independen.
        - Hasil pengujian membuktikan akurasi mencapai **82.35%**, dengan F1-Score kelas Hutan Biasa sebesar 0.93 dan Mangrove sebesar 0.87.
        
        #### 4. Tahap DAPAT INFORMASI (Insights & Deployment)
        - Dihasilkan peta tematik tutupan lahan penuh (*Land Use / Land Cover Map*) se-Jawa Timur.
        - Identifikasi sebaran sabuk hutan pegunungan, jalur mangrove estuari, dan koridor perkotaan Surabaya-Malang.
        - Aplikasi interaktif Web GIS berbasis **Streamlit & Folium Leaflet** yang siap digunakan oleh pengambil kebijakan dan akademisi.
        """)
        
    st.markdown("---")
    st.markdown("##### Daftar Berkas GeoJSON Sampel yang Digunakan:")
    st.table(pd.DataFrame([
        {"File": "data/geojson/building.geojson", "Label Kelas": "Bangunan (Built-up)", "Jumlah Sampel": "60 Poligon", "Warna": "Merah (#e74c3c)"},
        {"File": "data/geojson/sawah.geojson", "Label Kelas": "Lahan Pertanian (Sawah)", "Jumlah Sampel": "60 Poligon", "Warna": "Kuning (#f1c40f)"},
        {"File": "data/geojson/perairan.geojson", "Label Kelas": "Perairan (Water Body)", "Jumlah Sampel": "50 Poligon", "Warna": "Biru (#0984e3)"},
        {"File": "data/geojson/Hutan Biasa.geojson", "Label Kelas": "Hutan Biasa", "Jumlah Sampel": "50 Poligon", "Warna": "Hijau (#27ae60)"},
        {"File": "data/geojson/Mangrove.geojson", "Label Kelas": "Hutan Mangrove", "Jumlah Sampel": "50 Poligon", "Warna": "Ungu (#8e44ad)"}
    ]))
