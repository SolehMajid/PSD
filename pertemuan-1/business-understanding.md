# Business Understanding: Mengamati Kualitas Udara di Kabupaten Bangkalan, Madura

Kualitas udara merupakan salah satu faktor penting yang dapat memengaruhi kesehatan manusia, lingkungan, dan aktivitas masyarakat. Udara dapat dikatakan memiliki kualitas yang kurang baik apabila terdapat peningkatan konsentrasi zat pencemar atau polutan di atmosfer. Polutan tersebut dapat berasal dari berbagai aktivitas manusia maupun proses alami, seperti kendaraan bermotor, kegiatan industri, pembakaran bahan bakar, pembakaran biomassa, pengelolaan sampah, serta aktivitas pertanian.

Pada proyek ini, pengamatan kualitas udara dilakukan di Kabupaten Bangkalan, Madura, Jawa Timur dengan memanfaatkan data pengamatan atmosfer dari satelit Copernicus Sentinel-5P dengan instrumen TROPOMI. Sentinel-5P memang dirancang untuk memantau berbagai komponen atmosfer yang berkaitan dengan kualitas udara dan perubahan iklim, termasuk karbon monoksida (CO), nitrogen dioksida (NO₂), sulfur dioksida (SO₂), dan metana (CH₄).

## Permasalahan

Kabupaten Bangkalan merupakan wilayah yang memiliki aktivitas masyarakat, transportasi, permukiman, perdagangan, pertanian, dan berbagai aktivitas ekonomi. Aktivitas tersebut dapat menghasilkan emisi yang berpotensi memengaruhi kondisi atmosfer.

Permasalahan yang ingin dikaji adalah:

> **"Bagaimana kondisi dan persebaran beberapa polutan udara di wilayah Kabupaten Bangkalan berdasarkan pengamatan satelit Sentinel-5P?"**

Analisis ini dilakukan untuk mengetahui pola spasial dan temporal dari beberapa gas atmosfer sehingga dapat diketahui wilayah atau periode yang menunjukkan nilai relatif lebih tinggi maupun lebih rendah.

## Polutan yang Diamati

Empat parameter utama yang digunakan dalam analisis adalah:

| Polutan | Nama | Sumber yang Umum | Dampak |
| :---: | :--- | :--- | :--- |
| **CO** | Karbon Monoksida | Pembakaran tidak sempurna, kendaraan, pembakaran biomassa | Berbahaya bagi sistem pernapasan dan mengurangi kemampuan darah membawa oksigen |
| **NO₂** | Nitrogen Dioksida| Kendaraan bermotor, pembakaran bahan bakar, industri | Dapat mengganggu sistem pernapasan dan berperan dalam pembentukan polutan sekunder |
| **SO₂** | Sulfur Dioksida | Pembakaran bahan bakar yang mengandung sulfur, aktivitas industri, sumber vulkanik | Dapat mengganggu sistem pernapasan dan berkontribusi terhadap pembentukan hujan asam |
| **CH₄** | Metana | Pertanian, peternakan, tempat pembuangan sampah, aktivitas energi | Merupakan gas rumah kaca yang kuat dan berpengaruh terhadap perubahan iklim |

CO terutama berkaitan dengan proses pembakaran bahan bakar dan biomassa. NO₂ banyak digunakan sebagai indikator emisi yang berkaitan dengan aktivitas transportasi dan pembakaran bahan bakar. BMKG juga menggunakan data TROPOMI Sentinel-5P untuk memantau persebaran NO₂ secara spasial.

SO₂ dapat berasal dari aktivitas antropogenik maupun sumber alami. Sementara itu, CH₄ berasal dari berbagai sumber, termasuk aktivitas manusia dan proses alami, serta merupakan salah satu gas rumah kaca utama.

## Tujuan

Analisis kualitas udara di Kabupaten Bangkalan bertujuan untuk:

1. Mengidentifikasi persebaran spasial CO, NO₂, SO₂, dan CH₄ di Kabupaten Bangkalan.
2. Mengetahui perubahan atau pola konsentrasi polutan dari waktu ke waktu.
3. Mengidentifikasi wilayah yang memiliki nilai polutan relatif lebih tinggi.
4. Mengamati kemungkinan hubungan antara pola polutan dengan aktivitas manusia dan kondisi lingkungan.
5. Menyajikan hasil analisis dalam bentuk peta dan visualisasi yang mudah dipahami.

## Data yang Digunakan

Data utama berasal dari **Copernicus Sentinel-5P/TROPOMI**. Satelit ini menyediakan pengamatan atmosfer secara global dan memiliki produk untuk CO, NO₂, SO₂, dan CH₄. Data Sentinel-5P dapat digunakan untuk mempelajari distribusi spasial berbagai komponen atmosfer.

Dalam analisis, wilayah pengamatan akan dibatasi menggunakan batas administratif Kabupaten Bangkalan sebagai *Area of Interest* (AOI). Selanjutnya, data satelit akan dipotong (*clipping*) berdasarkan wilayah tersebut sehingga analisis hanya berfokus pada Kabupaten Bangkalan.

## Catatan Interpretasi

- **Perbedaan Pengukuran:** Nilai yang diperoleh dari Sentinel-5P tidak dapat disamakan secara langsung dengan hasil pengukuran sensor kualitas udara di permukaan. Data satelit mengukur karakteristik gas dalam kolom atmosfer, sedangkan alat pemantau di permukaan umumnya mengukur konsentrasi pada lokasi tertentu. 
- **Fungsi Utama:** Oleh karena itu, hasil analisis dalam proyek ini lebih tepat digunakan untuk mengamati pola dan persebaran relatif polutan, bukan sebagai pengganti pengukuran kualitas udara langsung di permukaan.
- **Faktor Cuaca:** Selain itu, kondisi awan, angin, musim, dan perubahan aktivitas emisi dapat memengaruhi hasil pengamatan satelit. Karena itu, analisis sebaiknya tidak hanya melihat satu tanggal, tetapi menggunakan data dalam periode tertentu untuk mendapatkan pola yang lebih representatif.

## Hasil yang Diharapkan

Hasil akhir dari proyek ini diharapkan berupa:

- Peta persebaran CO di Kabupaten Bangkalan.
- Peta persebaran NO₂ di Kabupaten Bangkalan.
- Peta persebaran SO₂ di Kabupaten Bangkalan.
- Peta persebaran CH₄ di Kabupaten Bangkalan.
- Grafik perubahan polutan berdasarkan waktu.
- Identifikasi wilayah dengan nilai polutan relatif tinggi dan rendah.
- Perbandingan karakteristik keempat polutan.
- Interpretasi mengenai kemungkinan sumber dan faktor yang memengaruhi persebaran polutan.

---
*Dengan demikian, proyek ini tidak hanya menghasilkan visualisasi data satelit, tetapi juga memberikan gambaran mengenai kondisi dan pola persebaran beberapa polutan atmosfer di Kabupaten Bangkalan yang dapat digunakan sebagai dasar untuk eksplorasi lebih lanjut mengenai kualitas lingkungan di wilayah tersebut.*

