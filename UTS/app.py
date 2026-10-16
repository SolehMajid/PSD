import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

st.set_page_config(
    page_title="Klasifikasi Tutupan Lahan Jawa Timur | Sentinel-2A",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "csv")
FEATURE_COLS = ["B02", "B03", "B04", "B08", "B8A", "B11", "NDVI", "MNDWI", "NDBI", "Ratio_B8A_B11"]

COLOR_MAP = {
    "Bangunan (Built-up)": "#E6194B",
    "Hutan Biasa": "#2E7D32",
    "Hutan Mangrove": "#004D40",
    "Lahan Pertanian (Sawah)": "#FFE119",
    "Perairan (Water Body)": "#000075"
}

@st.cache_data
def load_datasets():
    csv_centroid = os.path.join(CSV_DIR, "dataset_sampel_5kelas_jatim.csv")
    csv_pixel = os.path.join(CSV_DIR, "dataset_sampel_all_pixels_jatim.csv")
    df_cent = pd.read_csv(csv_centroid) if os.path.exists(csv_centroid) else None
    df_pix = pd.read_csv(csv_pixel) if os.path.exists(csv_pixel) else None
    return df_cent, df_pix

@st.cache_resource
def load_models():
    p1 = os.path.join(BASE_DIR, "model_rf.pkl")
    p2 = os.path.join(BASE_DIR, "model_rf_pixel.pkl")
    m_cent = joblib.load(p1) if os.path.exists(p1) else None
    m_pix = joblib.load(p2) if os.path.exists(p2) else None
    return m_cent, m_pix

df_centroid, df_all_pixels = load_datasets()
model_centroid, model_pixel = load_models()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/satellite.png", width=70)
st.sidebar.title("🛰️ Panel Kontrol LULC")
st.sidebar.caption("Provinsi Jawa Timur (60m Sentinel-2A)")

pilihan_model = st.sidebar.radio(
    "🧠 Pilih Model Machine Learning:",
    ["Model 1: Centroid (270 Sampel Poligon)", "Model 2: Full-Pixel (52.327 Piksel)"],
    index=0,
    help="Pilih model yang akan digunakan untuk simulasi prediksi dan evaluasi."
)

use_pixel_model = "Full-Pixel" in pilihan_model
active_model = model_pixel if use_pixel_model and model_pixel is not None else model_centroid

st.sidebar.markdown("---")
model_aktif_str = "Model 2 (Full-Pixel)" if use_pixel_model else "Model 1 (Centroid)"
st.sidebar.markdown(f"""
**Status Model Aktif:**
- **Versi**: {model_aktif_str}
- **Algoritma**: Random Forest (100 Estimators)
- **Resolusi Spasial**: 60 meter / piksel
- **Area Kajian**: 38 Kab/Kota Jawa Timur
""")

# Header
st.markdown('<div class="main-header">Sistem Cerdas Klasifikasi Tutupan Lahan Jawa Timur</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Monitoring Dinamika LULC Skala Regional dengan Citra Satelit Sentinel-2A & Dual Random Forest Model</div>', unsafe_allow_html=True)

# Metric Summary Cards
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Akurasi Model Centroid", "82.35%", "Centroid Test Set")
with col_m2:
    st.metric("Akurasi Model Full-Pixel", "98.65%", "19.276 Test Pixels")
with col_m3:
    st.metric("Akurasi Poligon (Majority Vote)", "86.76%", "Agregasi 68 Poligon")
with col_m4:
    st.metric("Total Piksel Diekstraksi", "52.327 Piksel", "270 Poligon Sampel")

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Peta Interaktif & Visualisasi", 
    "⚖️ Komparasi Dua Model (Centroid vs Pixel)", 
    "🧪 Uji Prediksi Spektral Interaktif", 
    "📊 Eksplorasi Dataset Sampel"
])

# ----------------- TAB 1: PETA INTERAKTIF -----------------
with tab1:
    st.subheader("Eksplorasi Peta Interaktif Spasial Jawa Timur")
    
    col_sel1, col_sel2 = st.columns([1.5, 1])
    with col_sel1:
        pilihan_peta = st.selectbox(
            "Pilih Lapisan Peta Tematik:",
            [
                "Peta Utama: Peta Interaktif Raster LULC (Overlay Google Hybrid)",
                "Peta 1: Sebaran 270 Poligon Sampel Digitasi Ground Truth",
                "Peta 2: Pembagian Data Spasial (Training 75% vs Testing 25%)",
                "Peta 3: Hasil Evaluasi Klasifikasi (Prediksi Benar vs Prediksi Meleset)"
            ],
            index=0
        )
    with col_sel2:
        st.markdown(f"**Model Aktif Terpilih:** `{model_aktif_str}`")
        st.caption("Pilihan model dapat diubah melalui menu sidebar di sebelah kiri.")

    if "Peta Utama" in pilihan_peta:
        # Load stats JSON if exists
        stats_file = os.path.join(BASE_DIR, "data", "lulc_stats.json")
        stats_dict = None
        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                stats_dict = json.load(f)
                
        active_key = "pixel" if use_pixel_model else "centroid"
        current_stats = stats_dict[active_key] if stats_dict else None
        
        # Header controls just like screenshot
        st.markdown("---")
        slider_col1, slider_col2 = st.columns([1.2, 1.8])
        with slider_col1:
            transparansi = st.slider(
                "Transparansi Lapisan Raster LULC:",
                min_value=0,
                max_value=100,
                value=90,
                step=5,
                help="Atur tingkat opasitas transparansi raster LULC di atas citra satelit."
            )
        with slider_col2:
            st.markdown(f"""
            <div style="padding-top: 15px; font-size: 13px;">
                <b>Tingkat Transparansi Aktif:</b> <span style="color: #ea580c; font-weight: bold;">{transparansi}% Opasitas ({100-transparansi}% Transparan)</span><br>
                <small style="color: #64748b;">💡 <i>Anda juga dapat menggeser slider transparansi interaktif langsung di dalam jendela peta Leaflet secara real-time.</i></small>
            </div>
            """, unsafe_allow_html=True)
            
        target_map_file = "peta_lulc_interactive_pixel.html" if use_pixel_model else "peta_lulc_interactive_centroid.html"
        map_path = os.path.join(BASE_DIR, target_map_file)
        
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                html_map = f.read()
                
            # If user adjusted slider at top, inject into default opacity
            html_map = html_map.replace("value=\"90\"", f"value=\"{transparansi}\"")
            html_map = html_map.replace("changeRasterOpacity(90)", f"changeRasterOpacity({transparansi})")
            st.components.v1.html(html_map, height=620, scrolling=True)
        else:
            st.warning(f"Berkas peta {target_map_file} sedang dipersiapkan...")
            
        # Expandable Table for Land Cover Summary (matching screenshot)
        if current_stats:
            with st.expander("📊 Lihat Tabel Rekapitulasi Luas Tutupan Lahan Full Jawa Timur (Data Raster)", expanded=True):
                rekap_data = []
                for k, v in current_stats.items():
                    rekap_data.append({
                        "Kelas Tutupan Lahan": v["display"],
                        "Jumlah Piksel Raster": f"{v['count']:,}",
                        "Estimasi Luas (Hektar)": f"{v['ha']:,.1f} Ha",
                        "Estimasi Luas (km²)": f"{v['km2']:,.2f} km²",
                        "Persentase Luas (%)": f"{v['pct']:.2f}%"
                    })
                rekap_df = pd.DataFrame(rekap_data)
                st.dataframe(rekap_df, use_container_width=True)
                st.caption(f"Rekapitulasi dihitung dari total 5.875.942 piksel daratan Jawa Timur menggunakan {model_aktif_str}.")

    else:
        file_map = {
            "Peta 1: Sebaran 270 Poligon Sampel Digitasi Ground Truth": "peta_sampel_jatim.html",
            "Peta 2: Pembagian Data Spasial (Training 75% vs Testing 25%)": "peta_split_data_jatim.html",
            "Peta 3: Hasil Evaluasi Klasifikasi (Prediksi Benar vs Prediksi Meleset)": "peta_evaluasi_klasifikasi_jatim.html"
        }
        
        map_filename = file_map.get(pilihan_peta, "peta_sampel_jatim.html")
        map_path = os.path.join(BASE_DIR, map_filename)
        
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=580, scrolling=True)
        else:
            st.warning(f"Berkas {map_filename} belum ditemukan di direktori.")

# ----------------- TAB 2: KOMPARASI DUA MODEL -----------------
with tab2:
    st.subheader("Perbandingan Head-to-Head: Model Centroid vs Model Full-Pixel")
    
    st.markdown("""
    Untuk menjawab tantangan representasi data spasial, proyek ini mengekstrak dan melatih **dua model Machine Learning independen**:
    1. **Model Centroid (`model_rf.pkl`)**: 1 sampel per poligon (mengambil titik centroid).
    2. **Model Full-Pixel (`model_rf_pixel.pkl`)**: Seluruh piksel di dalam poligon (52.327 piksel).
    """)
    
    df_komparasi = pd.DataFrame({
        "Parameter Komparasi": [
            "Metode Ekstraksi Data",
            "Total Sampel Latih (Training)",
            "Total Sampel Uji (Testing)",
            "Akurasi Piksel (Pixel Accuracy)",
            "Akurasi Poligon (Majority Vote)",
            "Waktu Ekstraksi Citra",
            "Resistensi Bias Luas Poligon",
            "Representasi Spektral",
            "Tujuan Penggunaan Utama"
        ],
        "Model 1: Centroid (model_rf.pkl)": [
            "1 Titik Centroid per Poligon",
            "202 Sampel Centroid",
            "68 Sampel Centroid",
            "82.35% (56/68 poligon)",
            "82.35% (evaluasi centroid)",
            "< 1 Detik",
            "Sangat Tinggi (1 poligon = 1 sampel)",
            "Mewakili inti homogen poligon",
            "Klasifikasi cepat & benchmark baseline"
        ],
        "Model 2: Full-Pixel (model_rf_pixel.pkl)": [
            "Seluruh Piksel dalam Poligon (rasterio.mask)",
            "33.051 Sampel Piksel (202 Poligon)",
            "19.276 Sampel Piksel (68 Poligon Uji)",
            "98.65% (19.016/19.276 piksel)",
            "76.47% - 86.76% (Modus / Suara Terbanyak)",
            "~2.3 Detik",
            "Rentan jika luas poligon timpang",
            "Merekam variasi mikro & mixed pixels",
            "Pemetaan tutupan lahan raster detail"
        ]
    })
    
    st.table(df_komparasi)
    
    st.markdown("---")
    st.subheader("Analisis Feature Importance")
    
    col_fi1, col_fi2 = st.columns(2)
    with col_fi1:
        st.markdown("**Feature Importance: Model Centroid**")
        if model_centroid is not None:
            imp_c = pd.Series(model_centroid.feature_importances_, index=FEATURE_COLS).sort_values(ascending=True)
            fig_c, ax_c = plt.subplots(figsize=(6, 4))
            imp_c.plot(kind='barh', ax=ax_c, color='#2563EB')
            ax_c.set_xlabel('Relative Importance')
            st.pyplot(fig_c)
    with col_fi2:
        st.markdown("**Feature Importance: Model Full-Pixel**")
        if model_pixel is not None:
            imp_p = pd.Series(model_pixel.feature_importances_, index=FEATURE_COLS).sort_values(ascending=True)
            fig_p, ax_p = plt.subplots(figsize=(6, 4))
            imp_p.plot(kind='barh', ax=ax_p, color='#059669')
            ax_p.set_xlabel('Relative Importance')
            st.pyplot(fig_p)

# ----------------- TAB 3: UJI PREDIKSI INTERAKTIF -----------------
with tab3:
    st.subheader("Simulator Klasifikasi Berdasarkan Pantulan Spektral Citra")
    st.info(f"Prediksi saat ini menggunakan: **{pilihan_model}**")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        st.markdown("**Input Band Spektral Sentinel-2A (Reflektansi x10.000):**")
        val_b2 = st.slider("Band 2 (Blue - 490 nm)", 0, 4000, 750, step=10)
        val_b3 = st.slider("Band 3 (Green - 560 nm)", 0, 4000, 920, step=10)
        val_b4 = st.slider("Band 4 (Red - 665 nm)", 0, 4000, 680, step=10)
    with col_input2:
        val_b8 = st.slider("Band 8 (NIR - 842 nm)", 0, 6000, 3100, step=10)
        val_b8a = st.slider("Band 8A (Narrow NIR - 865 nm)", 0, 6000, 3250, step=10)
        val_b11 = st.slider("Band 11 (SWIR - 1610 nm)", 0, 5000, 1400, step=10)
        
    calc_ndvi = (val_b8 - val_b4) / (val_b8 + val_b4 + 1e-6)
    calc_mndwi = (val_b3 - val_b11) / (val_b3 + val_b11 + 1e-6)
    calc_ndbi = (val_b11 - val_b8) / (val_b11 + val_b8 + 1e-6)
    calc_ratio = val_b8a / (val_b11 + 1e-6)
    
    st.markdown("**Indeks Spektral Terhitung Otomatis:**")
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.metric("NDVI (Vegetasi)", f"{calc_ndvi:.4f}")
    col_i2.metric("MNDWI (Air)", f"{calc_mndwi:.4f}")
    col_i3.metric("NDBI (Bangunan)", f"{calc_ndbi:.4f}")
    col_i4.metric("Ratio B8A/B11 (Mangrove)", f"{calc_ratio:.4f}")
    
    input_df = pd.DataFrame([{
        "B02": val_b2, "B03": val_b3, "B04": val_b4,
        "B08": val_b8, "B8A": val_b8a, "B11": val_b11,
        "NDVI": calc_ndvi, "MNDWI": calc_mndwi, "NDBI": calc_ndbi,
        "Ratio_B8A_B11": calc_ratio
    }])
    
    if active_model is not None:
        pred_label = active_model.predict(input_df[FEATURE_COLS])[0]
        pred_proba = active_model.predict_proba(input_df[FEATURE_COLS])[0]
        classes = active_model.classes_
        
        st.markdown("---")
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.success(f"### Hasil Prediksi: {pred_label}")
            color_hex = COLOR_MAP.get(pred_label, "#888")
            st.markdown(f"Warna Representatif: <span style='display:inline-block;width:20px;height:20px;background-color:{color_hex};vertical-align:middle;border-radius:3px;'></span>", unsafe_allow_html=True)
        with res_col2:
            st.markdown("**Probabilitas Tiap Kelas Tutupan Lahan:**")
            prob_df = pd.DataFrame({'Kelas': classes, 'Probabilitas': pred_proba * 100}).sort_values('Probabilitas', ascending=False)
            st.bar_chart(prob_df.set_index('Kelas'))

# ----------------- TAB 4: EKSPLORASI DATASET -----------------
with tab4:
    st.subheader("Eksplorasi Data Ground Truth Tutupan Lahan")
    subtab_a, subtab_b = st.tabs(["Dataset Centroid (270 Sampel)", "Dataset Full-Pixel (52.327 Piksel)"])
    
    with subtab_a:
        if df_centroid is not None:
            st.dataframe(df_centroid.head(100), use_container_width=True)
            st.caption(f"Total baris: {len(df_centroid)} sampel centroid")
            
    with subtab_b:
        if df_all_pixels is not None:
            st.dataframe(df_all_pixels.head(100), use_container_width=True)
            st.caption(f"Total baris: {len(df_all_pixels):,} piksel dari 270 poligon")
