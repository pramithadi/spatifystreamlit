import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import rasterio
import os
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Peta Suhu Permukaan Lahan",
    layout="wide",
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
            font-family: 'Poppins', sans-serif !important;
        }
        div[data-testid="stMarkdownContainer"] * {
            font-family: 'Poppins', sans-serif !important;
        }
        .stMarkdown p {
            font-size: 14px !important;
            margin-bottom: 8px !important;
        }
        .stSubheader {
            font-size: 16px !important;
            margin-bottom: 12px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            border: 1px solid #e2e8f0 !important;
            border-radius: 3px !important;
            padding: 12px !important;
            box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #705c53 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #705c53 !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #705c53 !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover [data-baseweb="tab-highlight"] {
        background-color: #705c53 !important;
    }
    .stTabs {
        margin-top: -5rem !important;
    }
    
    .stLinkButton > a {
        background-color: #E4EFE7 !important;
        color: black !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
        
    .stLinkButton > a:hover {
        background-color: #6A9C89 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        # box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3) !important;
    }
        
    .stLinkButton > a:active {
        transform: translateY(0px) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Dictionary Statistik LST
stats_by_year = {
    "1999": {"min": 4.31, "max": 69.76, "mean": 34.53},
    "2004": {"min": 15.30, "max": 57.40, "mean": 35.48},
    "2009": {"min": 18.11, "max": 67.16, "mean": 37.75},
    "2014": {"min": 17.68, "max": 52.44, "mean": 36.63},
    "2019": {"min": 18.54, "max": 49.67, "mean": 35.74},
    "2024": {"min": 20.72, "max": 72.32, "mean": 37.26},
    "2029": {"min": 20.72, "max": 72.32, "mean": 37.26},  # Data 2029 menggunakan 2024
}

# Dictionary Threshold
threshold_dict = {
    "1999": {"low": 30.531, "medium": 34.554, "high": 38.577},
    "2004": {"low": 31.474, "medium": 35.508, "high": 39.542},
    "2009": {"low": 33.273, "medium": 37.729, "high": 42.185},
    "2014": {"low": 32.235, "medium": 36.646, "high": 41.058},
    "2019": {"low": 31.953, "medium": 35.729, "high": 39.504},
    "2024": {"low": 33.193, "medium": 37.206, "high": 41.219},
    "2029": {
        "low": 33.193,
        "medium": 37.206,
        "high": 41.219,
    },  # Data 2029 menggunakan 2024
}


def add_legend_to_map(map_obj, thresholds):
    """Fungsi untuk menambahkan legenda ke peta folium"""
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; 
                right: 10px; 
                z-index: 1000; 
                background-color: white; 
                border: 1px solid #ccc; 
                border-radius: 1px; 
                padding: 10px; 
                font-family: 'Poppins', sans-serif; 
                font-size: 11px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                min-width: 160px;">
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Kelas LST (°C)</div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #5ca0d3; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sangat Rendah (≤ {thresholds['low']:.1f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #f5ebb1; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Rendah ({thresholds['low']:.1f} - {thresholds['medium']:.1f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #dba758; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sedang ({thresholds['medium']:.1f} - {thresholds['high']:.1f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #93220e; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Tinggi (> {thresholds['high']:.1f}°C)</span>
            </div>
        </div>
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))


def add_geotiff_to_map(map_obj, tif_path, thresholds):
    """Fungsi untuk menambahkan GeoTIFF ke peta folium dengan klasifikasi threshold"""
    try:
        with rasterio.open(tif_path) as src:
            # Baca data raster
            data = src.read(1)

            # Dapatkan bounds
            bounds = src.bounds

            # Handle nodata dan nilai di luar area yang diinginkan
            if hasattr(src, "nodata") and src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)

            # Set nilai 0 atau negatif sebagai nodata juga
            data = np.where(data <= 0, np.nan, data)

            # Definisi warna untuk setiap kelas
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

            # Klasifikasi berdasarkan threshold
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

            # Set area yang tidak valid sebagai transparan
            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Konversi ke PIL Image
            img = Image.fromarray(colored_data, "RGBA")

            # Konversi ke base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Bounds untuk folium
            bounds_folium = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            # Tambahkan ke peta dengan transparansi
            lst_overlay = folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_folium,
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
                name="Suhu Permukaan Lahan",
            )
            lst_overlay.add_to(m)

        return True
    except Exception as e:
        return False


tab1, tab2 = st.tabs(["**Main Map**", "**Split Map**"])

with tab1:
    st.header("Suhu Permukaan Lahan")
    yearsSlider = st.select_slider(
        "Pilih Tahun:",
        options=["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
    )

    selected_data = stats_by_year[yearsSlider]

    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        with st.container(border=False):
            st.metric("Tahun", yearsSlider)
    with col2:
        with st.container(border=False):
            st.metric("Suhu Minimum", f"{selected_data['min']:.2f} °C")
    with col3:
        with st.container(border=False):
            st.metric("Suhu Maksimum", f"{selected_data['max']:.2f} °C")
    with col4:
        with st.container(border=False):
            st.metric("Suhu Rata-rata", f"{selected_data['mean']:.2f} °C")

    # Buat peta tanpa basemap default
    m = folium.Map(location=[-7.764326411862208, 110.3721676814108], zoom_start=10.5)

    # Tambahkan berbagai basemap sebagai layer
    folium.TileLayer(
        tiles="CartoDB positron", name="CartoDB Positron", overlay=False, control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="CartoDB Dark Matter",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Google Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
        name="Esri WorldImagery",
        overlay=False,
        control=True,
    ).add_to(m)

    # Path ke file GeoTIFF (untuk tahun 2029 gunakan file 2024)
    if yearsSlider == "2029":
        tif_path = "tif/lst2024kpy.tif"
    else:
        tif_path = f"tif/lst{yearsSlider}kpy.tif"

    # Ambil threshold untuk tahun yang dipilih
    thresholds = threshold_dict[yearsSlider]

    # Cek apakah file ada dan tambahkan ke peta
    if os.path.exists(tif_path):
        add_geotiff_to_map(m, tif_path, thresholds)

    # Tambahkan legenda ke peta
    add_legend_to_map(m, thresholds)

    # Tambahkan layer control ke peta setelah semua layer ditambahkan
    folium.LayerControl(position="topleft", collapsed=True).add_to(m)

    # Tambahkan CSS custom untuk memperkecil font layer control
    css = """
    <style>
    .leaflet-control-layers label {
        font-size: 11px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .leaflet-control-layers-list {
        font-size: 11px !important;
    }
    .leaflet-control-layers-expanded {
        font-size: 11px !important;
    }
    .leaflet-control-attribution {
        font-size: 11px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(css))

    st_data = st_folium(m, width=1110)

with tab2:
    st.header("Suhu Permukaan Lahan (Split Map)")
    st.write("Fitur split map akan tampil di sini...")
