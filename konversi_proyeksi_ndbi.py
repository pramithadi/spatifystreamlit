#!/usr/bin/env python3

import numpy as np
import rasterio
from PIL import Image
import os

# Dictionary Threshold
threshold_dict = {
    "2029": {"low": -0.305, "medium": -0.161, "high": -0.017},
    "2024a": {
        "low": -0.299,
        "medium": -0.162,
        "high": -0.025,
    },
}


def process_ndbi_to_png(tif_path, thresholds, output_path):
    """ """
    print(f"Konversi: {tif_path}")

    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds
            nodata = src.nodata

            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            # Filter Nilai NDBI yang Valid (-1 hingga +1)
            data = np.where((data < -1) | (data > 1), np.nan, data)

            colors = {
                "very_low": [0, 100, 0, 255],  # #006400 - Non-terbangun
                "low": [255, 255, 224, 255],  # #ffffe0 - Rendah
                "medium": [255, 165, 0, 255],  # #ffa500 - Sedang
                "high": [59, 6, 10, 255],  # #3b060a - Tinggi
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


def preprocess_all_ndbi_files():
    os.makedirs("static", exist_ok=True)

    years = ["2029", "2024a"]

    bounds_dict = {}

    print("Memulai konversi NDBI -> PNG...")

    for year in years:
        if year == "2029":
            tif_path = "tif/prediksi_ndbi_2029_TERBARU.tif"
        elif year == "2024a":
            tif_path = "tif/prediksi_ndbi_2024_TERBARU.tif"

        output_path = f"static/ndbi_{year}.png"

        if not os.path.exists(tif_path):
            print(f"⚠️ File tidak ditemukan: {tif_path}")
            continue

        if os.path.exists(output_path):
            print(f"📁 File sudah ada, skip: {output_path}")
            continue

        thresholds = threshold_dict[year]

        bounds = process_ndbi_to_png(tif_path, thresholds, output_path)

        if bounds:
            bounds_dict[year] = bounds

    print("✅ Konversi selesai!")
    print("\n📋 File yang berhasil diproses:")
    for year in years:
        png_path = f"static/ndbi_{year}.png"
        if os.path.exists(png_path):
            size_mb = os.path.getsize(png_path) / (1024 * 1024)
            print(f"   - ndbi_{year}.png ({size_mb:.1f} MB)")

    return bounds_dict


if __name__ == "__main__":
    bounds_result = preprocess_all_ndbi_files()

    if bounds_result:
        print("\n📊 Bounds info (untuk debugging):")
        for year, bounds in bounds_result.items():
            print(f"   {year}: {bounds}")
