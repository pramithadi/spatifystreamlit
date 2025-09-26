#!/usr/bin/env python3

import numpy as np
import rasterio
from PIL import Image
import os


def process_pl_to_png(tif_path, output_path):
    print(f"Processing: {tif_path}")
    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds
            nodata = src.nodata

            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            colors = {
                0: [41, 75, 41, 255],  # 294b29 - Vegetasi
                1: [105, 195, 221, 255],  # 69c3dd - Tubuh Air
                2: [205, 154, 77, 255],  # cd9a4d - Lahan Terbangun
                3: [250, 245, 217, 255],  # faf5d9 - Lahan Terbuka
            }

            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)

            valid_mask = ~np.isnan(data)

            for class_value, color in colors.items():
                class_mask = valid_mask & (data == class_value)
                colored_data[class_mask] = color

            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Konversi ke PIL Image dan Save sebagai PNG
            img = Image.fromarray(colored_data, "RGBA")
            img.save(output_path, "PNG", optimize=True)

            print(f"✅ Saved: {output_path}")
            return bounds

    except Exception as e:
        print(f"❌ Error processing {tif_path}: {e}")
        return None


def preprocess_all_pl_files():
    os.makedirs("static", exist_ok=True)

    years = ["1999", "2004", "2009", "2014", "2019", "2024", "2029", "2024a"]

    bounds_dict = {}

    print("Memulai konversi NDVI COG -> PNG...")

    for year in years:
        if year == "2029":
            tif_path = "tif/output_pl2029kpy_COG.tif"
        elif year == "2024a":
            tif_path = "tif/output_prediksi_pl2024kpy_COG.tif"
        else:
            tif_path = f"tif/pl{year}kpy_COG.tif"

        output_path = f"static/pl_{year}.png"

        if not os.path.exists(tif_path):
            print(f"⚠️  File tidak ditemukan: {tif_path}")
            continue

        if os.path.exists(output_path):
            print(f"📁 File sudah ada, skip: {output_path}")
            continue

        bounds = process_pl_to_png(tif_path, output_path)

        if bounds:
            bounds_dict[year] = bounds

    print("✅ Konversi selesai!")
    print("\n📋 File yang berhasil diproses:")
    for year in years:
        png_path = f"static/pl_{year}.png"
        if os.path.exists(png_path):
            size_mb = os.path.getsize(png_path) / (1024 * 1024)
            print(f"   - pl_{year}.png ({size_mb:.1f} MB)")

    return bounds_dict


if __name__ == "__main__":
    bounds_result = preprocess_all_pl_files()

    if bounds_result:
        print("\n📊 Bounds Info (Debugging):")
        for year, bounds in bounds_result.items():
            print(f"   {year}: {bounds}")
