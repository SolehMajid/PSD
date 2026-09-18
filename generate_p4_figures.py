import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.makedirs('assets/images/images_pertemuan-4', exist_ok=True)
pollutants = ['CH4', 'CO', 'NO2', 'SO2']
colors_dict = {'CH4': '#1f77b4', 'CO': '#ff7f0e', 'NO2': '#2ca02c', 'SO2': '#9467bd'}

# 1. Figure 1: Deteksi Outlier Z-Score
df_raw = pd.read_csv('data/csv/Hasil Polutan.csv').iloc[:365].copy()
df_raw['tanggal'] = pd.to_datetime(df_raw['tanggal'])
df_z_out = pd.read_csv('data/csv/pertemuan-4-csv/polutan_4_outliers_list.csv')

fig, axes = plt.subplots(4, 1, figsize=(15, 14), sharex=True)
for i, pol in enumerate(pollutants):
    ax = axes[i]
    pol_out = df_z_out[df_z_out['Polutan'] == pol]
    out_dates = pd.to_datetime(pol_out['Tanggal'])
    out_vals = pol_out['Nilai Polutan']
    
    ax.plot(df_raw['tanggal'], df_raw[pol], color=colors_dict[pol], alpha=0.6, label=f'Data Valid {pol}', marker='o', markersize=3, linewidth=1)
    if len(pol_out) > 0:
        ax.scatter(out_dates, out_vals, color='red', s=80, zorder=5, label=f'Outlier Z-Score ({len(pol_out)} titik)', edgecolors='black', marker='X')
    
    ax.set_title(f'Runtun Waktu {pol} & Deteksi Outlier Z-Score (|Z| > 3.0)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Konsentrasi', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')

plt.xlabel('Tanggal Pengamatan (Hari 1 - 365)', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('assets/images/images_pertemuan-4/1.deteksi_outlier_zscore_4polutan.png', dpi=200)
plt.close()
print("Saved Figure 1")

# 2. Figure 2: Komparasi Z-Score vs IQR Outliers
df_iqr_out = pd.read_csv('data/csv/pertemuan-4-csv/polutan_4_outliers_list_iqr.csv')
fig, axes = plt.subplots(4, 1, figsize=(15, 14), sharex=True)

for i, pol in enumerate(pollutants):
    ax = axes[i]
    z_out = df_z_out[df_z_out['Polutan'] == pol]
    iqr_out = df_iqr_out[df_iqr_out['Polutan'] == pol]
    
    ax.plot(df_raw['tanggal'], df_raw[pol], color='lightgray', linewidth=1, alpha=0.8, label=f'Data {pol}')
    
    if len(z_out) > 0:
        ax.scatter(pd.to_datetime(z_out['Tanggal']), z_out['Nilai Polutan'], color='blue', s=70, marker='o', alpha=0.7, label=f'Z-Score ({len(z_out)})')
    if len(iqr_out) > 0:
        ax.scatter(pd.to_datetime(iqr_out['Tanggal']), iqr_out['Nilai Polutan'], color='crimson', s=90, marker='x', linewidth=2, label=f'IQR ({len(iqr_out)})')
    
    ax.set_title(f'Komparasi Deteksi Outlier {pol}: Z-Score vs IQR Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Konsentrasi', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')

plt.xlabel('Tanggal Pengamatan (Hari 1 - 365)', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('assets/images/images_pertemuan-4/2.komparasi_zscore_iqr_4polutan.png', dpi=200)
plt.close()
print("Saved Figure 2")

# 3. Figure 3: Hasil Imputasi Linear (Sebelum vs Sesudah Tambal Missing)
df_clean = pd.read_csv('data/csv/pertemuan-4-csv/polutan_4_clean.csv')
df_final = pd.read_csv('data/csv/pertemuan-4-csv/polutan_4_final_clean.csv')
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])
df_final['tanggal'] = pd.to_datetime(df_final['tanggal'])

fig, axes = plt.subplots(4, 1, figsize=(15, 14), sharex=True)
for i, pol in enumerate(pollutants):
    ax = axes[i]
    ax.plot(df_final['tanggal'], df_final[pol], color=colors_dict[pol], linestyle='-', linewidth=1.5, alpha=0.7, label=f'{pol} Hasil Interpolasi Linear (365 Hari Penuh)')
    
    # Titik asli
    valid_mask = df_clean[pol].notna()
    ax.scatter(df_clean.loc[valid_mask, 'tanggal'], df_clean.loc[valid_mask, pol], color='darkblue', s=12, alpha=0.6, label='Data Asli Bebas Outlier')
    
    ax.set_title(f'Hasil Penambalan Missing Value ({pol}) dengan Interpolasi Linear', fontsize=12, fontweight='bold')
    ax.set_ylabel('Konsentrasi', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')

plt.xlabel('Tanggal Pengamatan (Hari 1 - 365)', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('assets/images/images_pertemuan-4/3.hasil_imputasi_linear_4polutan.png', dpi=200)
plt.close()
print("Saved Figure 3")

# 4. Figure 4: Visualisasi Hasil Fitur TSFEL Terpilih 4 Polutan
df_feat = pd.read_csv('data/csv/pertemuan-4-csv/fitur_68_4_polutan.csv')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

key_metrics = [
    ('f7_calc_mean', 'Rata-rata Konsentrasi (Mean)', axes[0, 0]),
    ('f10_calc_std', 'Standar Deviasi (Variabilitas)', axes[0, 1]),
    ('f18_entropy', 'Shannon Entropy (Kompleksitas)', axes[1, 0]),
    ('f23_hurst_exponent', 'Hurst Exponent (Persistensi Memori)', axes[1, 1])
]

for col, title, ax in key_metrics:
    bars = ax.bar(df_feat['Polutan'], df_feat[col], color=[colors_dict[p] for p in df_feat['Polutan']], alpha=0.85, edgecolor='black')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        if abs(yval) < 0.001 and yval != 0:
            ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2e}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('assets/images/images_pertemuan-4/4.komparasi_fitur_kunci_4polutan.png', dpi=200)
plt.close()
print("Saved Figure 4")
