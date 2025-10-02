import os
import rasterio
from rasterio.enums import Resampling

# Print statement paling atas untuk memastikan file ini dieksekusi
print("--- Skrip 'konversi_semua_cog.py' Mulai Dijalankan ---")


def konversi_ke_cog(input_path, output_path):
    """
    Membaca GeoTIFF biasa dan menyimpannya sebagai Cloud Optimized GeoTIFF (COG)
    yang sangat efisien untuk web.
    """
    try:
        # Membuka file GeoTIFF sumber
        with rasterio.open(input_path, "r") as src:
            print(f"Membaca: {input_path} ({src.width}x{src.height})")

            # Salin profil dari file sumber
            profile = src.profile.copy()

            # Perbarui profil dengan konfigurasi COG kita.
            profile.update(
                {
                    "driver": "COG",
                    "compress": "LZW",
                }
            )

            # Membuat file COG baru dengan profil yang sudah digabungkan
            with rasterio.open(output_path, "w", **profile) as dst:
                print(f"Menulis data ke: {output_path}...")

                # Menyalin data dari file lama ke file baru
                dst.write(src.read())

                # Membuat 'Overviews' (piramida resolusi) untuk zoom yang cepat
                factors = [2, 4, 8, 16]
                print(f"Membuat overviews dengan faktor: {factors}...")
                dst.build_overviews(factors, Resampling.average)

                # Menandai bahwa overviews sudah dibuat
                dst.update_tags(OVR_RESAMPLING_ALG="AVERAGE")

        print(f"✅ Konversi BERHASIL! File COG disimpan di: {output_path}\n")
    except Exception as e:
        print(f"❌ ERROR saat memproses {input_path}: {e}\n")


# --- BAGIAN EKSEKUSI UTAMA ---

# 1. Folder sumber tempat file TIF Anda disimpan
folder_sumber = "tif"

# 2. Daftar semua file TIF Anda yang akan dikonversi

# # Daftar file LST
# daftar_file_lst = [
#     "lst1999kpy.tif",
#     "lst2004kpy.tif",
#     "lst2009kpy.tif",
#     "lst2014kpy.tif",
#     "lst2019kpy.tif",
#     "lst2024kpy.tif",
#     "output_lst2029kpy.tif",
#     "output_prediksi_lst2024kpy.tif",
# ]

# # Daftar file NDBI
# daftar_file_ndbi = [
#     "ndbi1999kpy.tif",
#     "ndbi2004kpy.tif",
#     "ndbi2009kpy.tif",
#     "ndbi2014kpy.tif",
#     "ndbi2019kpy.tif",
#     "ndbi2024kpy.tif",
#     "output_ndbi2029kpy.tif",
#     "output_proyeksi_ndbi2024kpy.tif",
# ]

# # Daftar file NDMI
# daftar_file_ndmi = [
#     "ndmi1999kpy.tif",
#     "ndmi2004kpy.tif",
#     "ndmi2009kpy.tif",
#     "ndmi2014kpy.tif",
#     "ndmi2019kpy.tif",
#     "ndmi2024kpy.tif",
#     "output_ndmi2029kpy.tif",
#     "output_proyeksi_ndmi2024kpy.tif",
# ]

# # Daftar file NDVI
# daftar_file_ndvi = [
#     "ndvi1999kpy.tif",
#     "ndvi2004kpy.tif",
#     "ndvi2009kpy.tif",
#     "ndvi2014kpy.tif",
#     "ndvi2019kpy.tif",
#     "ndvi2024kpy.tif",
#     "output_ndvi2029kpy.tif",
#     "output_proyeksi_ndvi2024kpy.tif",
# ]

# # Daftar file Penutup Lahan (pl)
# daftar_file_pl = [
#     "pl1999kpy.tif",
#     "pl2004kpy.tif",
#     "pl2009kpy.tif",
#     "pl2014kpy.tif",
#     "pl2019kpy.tif",
#     "pl2024kpy.tif",
#     "output_pl2029kpy.tif",
#     "output_prediksi_pl2024kpy.tif",
# ]

# Daftar file LST
daftar_file_lst = [
    "lst1999kpy.tif",
    "lst2004kpy.tif",
    "lst2009kpy.tif",
    "lst2014kpy.tif",
    "lst2019kpy.tif",
    "lst2024kpy.tif",
    "output_lst2029kpy.tif",
    "output_prediksi_lst2024kpy.tif",
]

# Daftar file NDBI
daftar_file_ndbi = [
    "ndbi1999kpy.tif",
    "ndbi2004kpy.tif",
    "ndbi2009kpy.tif",
    "ndbi2014kpy.tif",
    "ndbi2019kpy.tif",
    "ndbi2024kpy.tif",
    "output_ndbi2029kpy.tif",
    "output_proyeksi_ndbi2024kpy.tif",
]

# Daftar file NDMI
daftar_file_ndmi = [
    "ndmi1999kpy.tif",
    "ndmi2004kpy.tif",
    "ndmi2009kpy.tif",
    "ndmi2014kpy.tif",
    "ndmi2019kpy.tif",
    "ndmi2024kpy.tif",
    "output_ndmi2029kpy.tif",
    "output_proyeksi_ndmi2024kpy.tif",
]

# Daftar file NDVI
daftar_file_ndvi = [
    "ndvi1999kpy.tif",
    "ndvi2004kpy.tif",
    "ndvi2009kpy.tif",
    "ndvi2014kpy.tif",
    "ndvi2019kpy.tif",
    "ndvi2024kpy.tif",
    "output_ndvi2029kpy.tif",
    "output_proyeksi_ndvi2024kpy.tif",
]

# Daftar file Penutup Lahan (pl)
daftar_file_pl = [
    "pl1999kpy.tif",
    "pl2004kpy.tif",
    "pl2009kpy.tif",
    "pl2014kpy.tif",
    "pl2019kpy.tif",
    "pl2024kpy.tif",
    "output_pl2029kpy.tif",
    "output_prediksi_pl2024kpy.tif",
]

# Gabungkan semua daftar menjadi satu daftar besar
daftar_file_total = (
    daftar_file_lst
    + daftar_file_ndbi
    + daftar_file_ndmi
    + daftar_file_ndvi
    + daftar_file_pl
)


# 3. Proses konversi akan berjalan otomatis untuk setiap file dalam daftar
print("--- Memulai Proses Konversi ke Cloud Optimized GeoTIFF (COG) ---")
for nama_file in daftar_file_total:
    # Membuat path input dan output secara otomatis
    path_input = os.path.join(folder_sumber, nama_file)
    path_output = os.path.join(
        folder_sumber, f"{os.path.splitext(nama_file)[0]}_COG.tif"
    )

    # Cek apakah file input ada sebelum diproses
    if os.path.exists(path_input):
        konversi_ke_cog(path_input, path_output)
    else:
        print(f"⚠️ PERINGATAN: File tidak ditemukan, dilewati -> {path_input}\n")

print("--- Semua proses konversi selesai. ---")
