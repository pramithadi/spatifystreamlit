#!/usr/bin/env python3
"""
Mengubah semua file COG menjadi PNG untuk loading yang lebih cepat.
Jalankan script ini SEKALI untuk preprocessing semua file COG.
Setelah itu, ubah fungsi di lst.py.
"""

import numpy as np
import rasterio
from PIL import Image
import os
from io import BytesIO

# Dictionary Threshold yang sama persis dari lst.py
threshold_dict = {
    "1999": {"low": 30.499, "medium": 34.531, "high": 38.563},
    "2004": {"low": 31.412, "medium": 35.481, "high": 39.550},
    "2009": {"low": 33.243, "medium": 37.745, "high": 42.247},
    "2014": {"low": 32.168, "medium": 36.630, "high": 41.092},
    "2019": {"low": 31.923, "medium": 35.739, "high": 39.556},
    "2024": {"low": 33.207, "medium": 37.262, "high": 41.317},
    "2029": {"low": 34.041, "medium": 38.378, "high": 42.714},
}


def process_cog_to_png(tif_path, thresholds, output_path):
    """
    Proses GeoTIFF dengan logic yang sama persis seperti di lst.py
    Tapi save langsung sebagai PNG file.
    """
    print(f"Processing: {tif_path}")

    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds
            nodata = src.nodata

            # Handle NoData - sama persis dengan logic di lst.py
            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            # Set nilai 0 atau negatif sebagai NoData
            data = np.where(data <= 0, np.nan, data)

            # Warna untuk setiap kelas - sama persis dengan lst.py
            colors = {
                "very_low": [92, 160, 211, 255],  # #5ca0d3
                "low": [245, 235, 177, 255],  # #f5ebb1
                "medium": [219, 167, 88, 255],  # #dba758
                "high": [147, 34, 14, 255],  # #93220e
            }

            # Buat array warna berdasarkan threshold (RGBA)
            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)

            # Mask untuk data valid
            valid_mask = ~np.isnan(data)

            # Klasifikasi berdasarkan threshold - sama persis dengan lst.py
            very_low_mask = valid_mask & (data <= thresholds["low"])
            low_mask = (
                valid_mask & (data > thresholds["low"]) & (data <= thresholds["medium"])
            )
            medium_mask = (
                valid_mask
                & (data > thresholds["medium"])
                & (data <= thresholds["high"])
            )
            high_mask = valid_mask & (data > thresholds["high"])

            # Aplikasi warna berdasarkan klasifikasi
            colored_data[very_low_mask] = colors["very_low"]
            colored_data[low_mask] = colors["low"]
            colored_data[medium_mask] = colors["medium"]
            colored_data[high_mask] = colors["high"]

            # Set area yang tidak valid dengan warna transparan
            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Convert ke PIL Image dan save sebagai PNG
            img = Image.fromarray(colored_data, "RGBA")
            img.save(output_path, "PNG", optimize=True)

            print(f"✅ Saved: {output_path}")
            return bounds  # Return bounds untuk nanti digunakan di webapp

    except Exception as e:
        print(f"❌ Error processing {tif_path}: {e}")
        return None


def convert_all_files():
    os.makedirs("static", exist_ok=True)

    years = ["1999", "2004", "2009", "2014", "2019", "2024", "2029"]
    bounds_dict = {}

    print("Memulai konversi LST COG -> PNG...")

    for year in years:
        # Input
        if year == "2029":
            tif_path = "tif/output_lst2029kpy_COG.tif"
        else:
            tif_path = f"tif/lst{year}kpy_COG.tif"

        # Output
        output_path = f"static/lst_{year}.png"

        if not os.path.exists(tif_path):
            print(f"⚠️  File tidak ditemukan: {tif_path}")
            continue

        # Skip Jika PNG Sudah Ada
        if os.path.exists(output_path):
            print(f"📁 File sudah ada, skip: {output_path}")
            continue

        thresholds = threshold_dict[year]
        bounds = process_cog_to_png(tif_path, thresholds, output_path)
        if bounds:
            bounds_dict[year] = bounds

    print("✅ Konversi selesai!")
    print("\n📋 File yang berhasil dikonversi:")
    for year in years:
        png_path = f"static/lst_{year}.png"
        if os.path.exists(png_path):
            size_mb = os.path.getsize(png_path) / (1024 * 1024)
            print(f"   - lst_{year}.png ({size_mb:.1f} MB)")

    return bounds_dict


if __name__ == "__main__":
    bounds_result = convert_all_files()

    # Optional
    if bounds_result:
        print("\n📊 Bounds Info (Debugging):")
        for year, bounds in bounds_result.items():
            print(f"   {year}: {bounds}")
