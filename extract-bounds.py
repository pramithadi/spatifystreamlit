#!/usr/bin/env python3
"""
Script untuk extract bounds setiap kecamatan dari shapefile aoi_kpy.json
Jalankan script ini SEKALI untuk mendapatkan dictionary bounds.
"""

import json


def extract_kecamatan_bounds():
    """
    Extract bounds (koordinat minimal dan maksimal) untuk setiap kecamatan
    dari file GeoJSON shapefile.
    """
    print("Membaca file aoi_kpy.json...")

    try:
        # Baca file GeoJSON
        with open("shp/aoi_kpy.json", "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        bounds_dict = {}

        print("Mengekstrak bounds untuk setiap kecamatan...")
        print("=" * 60)

        # Loop setiap feature (kecamatan) di GeoJSON
        for feature in geojson_data["features"]:
            # Ambil nama kecamatan
            namobj = feature["properties"]["NAMOBJ"]
            wadmkk = feature["properties"].get("WADMKK", "")

            # Ambil koordinat polygon
            coords = feature["geometry"]["coordinates"][0]  # Koordinat polygon

            # Ekstrak longitude dan latitude
            lons = [coord[0] for coord in coords]  # Longitude (X)
            lats = [coord[1] for coord in coords]  # Latitude (Y)

            # Hitung bounds (min/max)
            bounds_dict[namobj] = {
                "min_lat": min(lats),
                "max_lat": max(lats),
                "min_lon": min(lons),
                "max_lon": max(lons),
                "wadmkk": wadmkk,  # Simpan info kabupaten juga
            }

            # Print info setiap kecamatan
            print(f"✓ {namobj} ({wadmkk})")
            print(f"  Lat: {min(lats):.6f} to {max(lats):.6f}")
            print(f"  Lon: {min(lons):.6f} to {max(lons):.6f}")

        print("=" * 60)
        print(f"Total kecamatan: {len(bounds_dict)}")
        print("\nDictionary bounds untuk copy-paste ke lst.py:")
        print("=" * 60)

        # Format output untuk copy-paste
        print("KECAMATAN_BOUNDS = {")
        for namobj, bounds in bounds_dict.items():
            print(f'    "{namobj}": {{')
            print(f'        "min_lat": {bounds["min_lat"]:.6f},')
            print(f'        "max_lat": {bounds["max_lat"]:.6f},')
            print(f'        "min_lon": {bounds["min_lon"]:.6f},')
            print(f'        "max_lon": {bounds["max_lon"]:.6f},')
            print(f'        "wadmkk": "{bounds["wadmkk"]}"')
            print("    },")
        print("}")

        return bounds_dict

    except FileNotFoundError:
        print("❌ ERROR: File 'shp/aoi_kpy.json' tidak ditemukan!")
        print("   Pastikan file shapefile ada di folder yang benar.")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


if __name__ == "__main__":
    print("🚀 Extract Bounds Kecamatan")
    print("Script ini akan membaca aoi_kpy.json dan menghasilkan dictionary bounds.")
    print("")

    bounds_result = extract_kecamatan_bounds()

    if bounds_result:
        print("\n✅ Extract berhasil!")
        print("\n📋 Langkah selanjutnya:")
        print("1. Copy dictionary KECAMATAN_BOUNDS di atas")
        print("2. Paste di lst.py setelah threshold_dict")
