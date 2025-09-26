#!/usr/bin/env python3

import numpy as np
import rasterio
from PIL import Image
import os

# Dictionary Threshold
threshold_dict = {
    "1999": {"low": 0.407, "medium": 0.535, "high": 0.664},
    "2004": {"low": 0.454, "medium": 0.592, "high": 0.730},
    "2009": {"low": 0.411, "medium": 0.554, "high": 0.698},
    "2014": {"low": 0.445, "medium": 0.596, "high": 0.748},
    "2019": {"low": 0.429, "medium": 0.587, "high": 0.746},
    "2024": {"low": 0.426, "medium": 0.592, "high": 0.758},
    "2029": {"low": 0.421, "medium": 0.585, "high": 0.750},
}


def process_ndvi_to_png(tif_path, thresholds, output_path):
    """ """
    print(f"Konversi: {tif_path}")

    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds
            nodata = src.nodata

            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            # Filter Nilai NDVI yang Valid (-1 hingga +1)
            data = np.where((data < -1) | (data > 1), np.nan, data)

            colors = {
                "very_low": [139, 0, 0, 255],  # #8b0000
                "low": [255, 255, 224, 255],  # #ffffe0
                "medium": [144, 238, 144, 255],  # #90ee90
                "high": [0, 100, 0, 255],  # #006400
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

            # Konversi ke PIL Image dan Save sebagai PNG
            img = Image.fromarray(colored_data, "RGBA")
            img.save(output_path, "PNG", optimize=True)

            print(f"✅ Saved: {output_path}")
            return bounds

    except Exception as e:
        print(f"❌ Error processing {tif_path}: {e}")
        return None


def preprocess_all_ndvi_files():
    os.makedirs("static", exist_ok=True)

    years = ["1999", "2004", "2009", "2014", "2019", "2024", "2029"]

    bounds_dict = {}

    print("Memulai konversi NDVI COG -> PNG...")

    for year in years:
        if year == "2029":
            tif_path = "tif/output_ndvi2029kpy_COG.tif"
        else:
            tif_path = f"tif/ndvi{year}kpy_COG.tif"

        output_path = f"static/ndvi_{year}.png"

        if not os.path.exists(tif_path):
            print(f"⚠️ File tidak ditemukan: {tif_path}")
            continue

        if os.path.exists(output_path):
            print(f"📁 File sudah ada, skip: {output_path}")
            continue

        thresholds = threshold_dict[year]

        bounds = process_ndvi_to_png(tif_path, thresholds, output_path)

        if bounds:
            bounds_dict[year] = bounds

    print("✅ Konversi selesai!")
    print("\n📋 File yang berhasil diproses:")
    for year in years:
        png_path = f"static/ndvi_{year}.png"
        if os.path.exists(png_path):
            size_mb = os.path.getsize(png_path) / (1024 * 1024)
            print(f"   - ndvi_{year}.png ({size_mb:.1f} MB)")

    return bounds_dict


if __name__ == "__main__":
    bounds_result = preprocess_all_ndvi_files()

    if bounds_result:
        print("\n📊 Bounds Info (Debugging):")
        for year, bounds in bounds_result.items():
            print(f"   {year}: {bounds}")
