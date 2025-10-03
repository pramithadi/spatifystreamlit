#!/usr/bin/env python3

import numpy as np
import rasterio
from PIL import Image
import os
from io import BytesIO

# Dictionary Threshold
threshold_dict = {
    "2029": {"low": 34.010, "medium": 38.347, "high": 42.684},
    "2024a": {"low": 33.315, "medium": 37.267, "high": 41.218},
}


def process_lst_to_png(tif_path, thresholds, output_path):
    print(f"Konversi: {tif_path}")

    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds
            nodata = src.nodata

            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            data = np.where(data <= 0, np.nan, data)

            colors = {
                "very_low": [92, 160, 211, 255],  # #5ca0d3
                "low": [245, 235, 177, 255],  # #f5ebb1
                "medium": [219, 167, 88, 255],  # #dba758
                "high": [147, 34, 14, 255],  # #93220e
            }

            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)

            valid_mask = ~np.isnan(data)

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

            colored_data[very_low_mask] = colors["very_low"]
            colored_data[low_mask] = colors["low"]
            colored_data[medium_mask] = colors["medium"]
            colored_data[high_mask] = colors["high"]

            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Convert ke PIL Image dan Save sebagai PNG
            img = Image.fromarray(colored_data, "RGBA")
            img.save(output_path, "PNG", optimize=True)

            print(f"✅ Saved: {output_path}")
            return bounds

    except Exception as e:
        print(f"❌ Error processing {tif_path}: {e}")
        return None


def convert_all_files():
    os.makedirs("static", exist_ok=True)

    years = ["2029", "2024a"]
    bounds_dict = {}

    print("Memulai konversi LST -> PNG...")

    for year in years:
        # Input
        if year == "2029":
            tif_path = "tif/prediksi_lst_2029_TERBARU.tif"
        elif year == "2024a":
            tif_path = "tif/prediksi_lst_2024_TERBARU.tif"
        else:
            tif_path = f"tif/lst{year}kpy_COG.tif"

        # Output
        output_path = f"static/lst_{year}.png"

        if not os.path.exists(tif_path):
            print(f"⚠️ File tidak ditemukan: {tif_path}")
            continue

        # Skip Jika PNG Sudah Ada
        if os.path.exists(output_path):
            print(f"📁 File sudah ada, skip: {output_path}")
            continue

        thresholds = threshold_dict[year]
        bounds = process_lst_to_png(tif_path, thresholds, output_path)
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
