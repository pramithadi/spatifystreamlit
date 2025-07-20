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
import geopandas as gpd

st.set_page_config(
    page_title="Peta Suhu Permukaan Lahan",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 0.2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
        /* Khusus untuk st.header */
        div[data-testid="stMarkdownContainer"] h1 {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        /* Untuk elemen header Streamlit */
        .stApp > header {
            color: #000000 !important;
        }
        
        /* Untuk semua text di Streamlit */
        .stApp {
            color: #000000 !important;
        }
        
        /* Paksa warna hitam untuk markdown */
        .stMarkdown {
            color: #000000 !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            # border: 0.5px solid rgba(0, 0, 0, 0.1) !important;
            border-radius: 1px !important;
            padding: 12px !important;
            # box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
            # background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
        
        /* Mengurangi Padding Top Halaman Utama */
        .block-container {
            padding-top: 0rem !important;
            max-width: 100% !important;
        }
        
        .main {
            padding-top: 0rem !important;
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
    },  # Data 2029 Sementara Menggunakan 2024
}

# Dictionary dummy LST per kecamatan (nanti akan diganti dengan data real)
lst_per_kecamatan = {
    "1999": {
        "Cangkringan": {"min": 32.1, "max": 45.3, "mean": 38.7, "wadmkk": "Sleman"},
        "Pakem": {"min": 30.5, "max": 42.8, "mean": 36.2, "wadmkk": "Sleman"},
        "Kalasan": {"min": 33.2, "max": 48.1, "mean": 40.5, "wadmkk": "Sleman"},
        "Prambanan": {"min": 31.8, "max": 44.6, "mean": 38.1, "wadmkk": "Sleman"},
        "Bantul": {"min": 34.5, "max": 49.2, "mean": 41.8, "wadmkk": "Bantul"},
        "Sewon": {"min": 32.9, "max": 46.7, "mean": 39.4, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 35.1, "max": 50.3, "mean": 42.6, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 34.8, "max": 49.9, "mean": 42.1, "wadmkk": "Yogyakarta"},
    },
    "2004": {
        "Cangkringan": {"min": 32.8, "max": 46.1, "mean": 39.2, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.2, "max": 43.5, "mean": 36.8, "wadmkk": "Sleman"},
        "Kalasan": {"min": 33.8, "max": 48.9, "mean": 41.1, "wadmkk": "Sleman"},
        "Prambanan": {"min": 32.4, "max": 45.2, "mean": 38.7, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.1, "max": 49.8, "mean": 42.3, "wadmkk": "Bantul"},
        "Sewon": {"min": 33.5, "max": 47.3, "mean": 40.0, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 35.7, "max": 51.0, "mean": 43.2, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 35.4, "max": 50.6, "mean": 42.7, "wadmkk": "Yogyakarta"},
    },
    "2009": {
        "Cangkringan": {"min": 33.5, "max": 46.9, "mean": 39.8, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.8, "max": 44.2, "mean": 37.4, "wadmkk": "Sleman"},
        "Kalasan": {"min": 34.4, "max": 49.6, "mean": 41.7, "wadmkk": "Sleman"},
        "Prambanan": {"min": 33.0, "max": 45.9, "mean": 39.3, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.7, "max": 50.5, "mean": 42.9, "wadmkk": "Bantul"},
        "Sewon": {"min": 34.1, "max": 48.0, "mean": 40.6, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 36.3, "max": 51.7, "mean": 43.8, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 36.0, "max": 51.3, "mean": 43.3, "wadmkk": "Yogyakarta"},
    },
    "2014": {
        "Cangkringan": {"min": 33.2, "max": 46.6, "mean": 39.5, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.5, "max": 43.9, "mean": 37.1, "wadmkk": "Sleman"},
        "Kalasan": {"min": 34.1, "max": 49.3, "mean": 41.4, "wadmkk": "Sleman"},
        "Prambanan": {"min": 32.7, "max": 45.6, "mean": 39.0, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.4, "max": 50.2, "mean": 42.6, "wadmkk": "Bantul"},
        "Sewon": {"min": 33.8, "max": 47.7, "mean": 40.3, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 36.0, "max": 51.4, "mean": 43.5, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 35.7, "max": 51.0, "mean": 43.0, "wadmkk": "Yogyakarta"},
    },
    "2019": {
        "Cangkringan": {"min": 32.9, "max": 46.3, "mean": 39.2, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.2, "max": 43.6, "mean": 36.8, "wadmkk": "Sleman"},
        "Kalasan": {"min": 33.8, "max": 49.0, "mean": 41.1, "wadmkk": "Sleman"},
        "Prambanan": {"min": 32.4, "max": 45.3, "mean": 38.7, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.1, "max": 49.9, "mean": 42.3, "wadmkk": "Bantul"},
        "Sewon": {"min": 33.5, "max": 47.4, "mean": 40.0, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 35.7, "max": 51.1, "mean": 43.2, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 35.4, "max": 50.7, "mean": 42.7, "wadmkk": "Yogyakarta"},
    },
    "2024": {
        "Cangkringan": {"min": 33.6, "max": 47.0, "mean": 39.9, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.9, "max": 44.3, "mean": 37.5, "wadmkk": "Sleman"},
        "Kalasan": {"min": 34.5, "max": 49.7, "mean": 41.8, "wadmkk": "Sleman"},
        "Prambanan": {"min": 33.1, "max": 46.0, "mean": 39.4, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.8, "max": 50.6, "mean": 43.0, "wadmkk": "Bantul"},
        "Sewon": {"min": 34.2, "max": 48.1, "mean": 40.7, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 36.4, "max": 51.8, "mean": 43.9, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 36.1, "max": 51.4, "mean": 43.4, "wadmkk": "Yogyakarta"},
    },
    "2029": {
        "Cangkringan": {"min": 33.6, "max": 47.0, "mean": 39.9, "wadmkk": "Sleman"},
        "Pakem": {"min": 31.9, "max": 44.3, "mean": 37.5, "wadmkk": "Sleman"},
        "Kalasan": {"min": 34.5, "max": 49.7, "mean": 41.8, "wadmkk": "Sleman"},
        "Prambanan": {"min": 33.1, "max": 46.0, "mean": 39.4, "wadmkk": "Sleman"},
        "Bantul": {"min": 35.8, "max": 50.6, "mean": 43.0, "wadmkk": "Bantul"},
        "Sewon": {"min": 34.2, "max": 48.1, "mean": 40.7, "wadmkk": "Bantul"},
        "Mergangsan": {"min": 36.4, "max": 51.8, "mean": 43.9, "wadmkk": "Yogyakarta"},
        "Umbulharjo": {"min": 36.1, "max": 51.4, "mean": 43.4, "wadmkk": "Yogyakarta"},
    },
}


# 2. TAMBAHKAN FUNCTION BARU untuk membuat grafik tren (letakkan setelah function get_toponim)
def create_trend_graph():
    # Data untuk grafik tren (hanya 1999-2024, tanpa 2029)
    years = [1999, 2004, 2009, 2014, 2019, 2024]

    # Ekstrak data min, max, mean dari dictionary
    min_values = [stats_by_year[str(year)]["min"] for year in years]
    max_values = [stats_by_year[str(year)]["max"] for year in years]
    mean_values = [stats_by_year[str(year)]["mean"] for year in years]

    # Buat grafik dengan Plotly
    fig = go.Figure()

    # Tambahkan line untuk Min (biru)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=min_values,
            mode="lines+markers",
            name="LST Min",
            line=dict(color="#003A87", width=3),
            marker=dict(size=8, color="#003A87"),
            hovertemplate="<b>Min:</b> %{y:.2f}°C<extra></extra>",
        )
    )

    # Tambahkan line untuk Max (merah)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=max_values,
            mode="lines+markers",
            name="LST Maks",
            line=dict(color="#7B0000", width=3),
            marker=dict(size=8, color="#7B0000"),
            hovertemplate="<b>Maks:</b> %{y:.2f}°C<extra></extra>",
        )
    )

    # Tambahkan line untuk Mean (kuning/emas)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=mean_values,
            mode="lines+markers",
            name="LST Rata-rata",
            line=dict(color="#F8CF00", width=3),
            marker=dict(size=8, color="#F8CF00"),
            hovertemplate="<b>Rata-rata:</b> %{y:.2f}°C<extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(
        xaxis=dict(
            title=dict(
                text="Tahun",
                font=dict(family="Poppins", size=12, color="black"),
            ),
            tickfont=dict(family="Poppins", size=11),
            gridcolor="rgba(128,128,128,0.2)",
            tickvals=years,
            ticktext=[str(year) for year in years],
        ),
        yaxis=dict(
            title=dict(
                text="LST (°C)", font=dict(family="Poppins", size=12, color="black")
            ),
            tickfont=dict(family="Poppins", size=11),
            gridcolor="rgba(128,128,128,0.2)",
        ),
        legend=dict(
            font=dict(family="Poppins", size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        plot_bgcolor="#fdfaf6",
        paper_bgcolor="#fdfaf6",
        margin=dict(l=10, r=10, t=10, b=10),
        height=284.5,
        hovermode="x unified",
        font=dict(family="Poppins"),
    )

    return fig


# Function untuk menentukan toponim sesuai wilayah
def get_toponim(wadmkk):
    if "Sleman" in wadmkk or "Bantul" in wadmkk:
        return "Kapanewon"
    elif "Yogyakarta" in wadmkk:
        return "Kemantren"
    else:
        return "Kecamatan"


# Function untuk Menambahkan SHP Batas Administrasi ke Peta Folium
def add_shapefile_to_map(map_obj, shapefile_path):
    try:
        # Geopandas untuk Membaca SHP
        gdf = gpd.read_file(shapefile_path)

        # Konversi ke WGS84
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        # Function Tooltip (Toponim) sesuai Kabupaten/Kota
        def create_tooltip_text(row):
            namobj = row.get("NAMOBJ", "Unknown")
            wadmkk = row.get("WADMKK", "")

            if "Sleman" in wadmkk or "Bantul" in wadmkk:
                return f"Kapanewon {namobj}"
            elif "Yogyakarta" in wadmkk:
                return f"Kemantren {namobj}"
            else:
                return namobj

        # Tambahkan Kolom Custom Tooltip
        gdf["tooltip_text"] = gdf.apply(create_tooltip_text, axis=1)

        # Konversi ke GeoJSON
        geojson_data = gdf.to_json()

        # Tambahkan GeoJSON ke Peta Folium dengan Custom Tooltip
        geojson_layer = folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                "fillColor": "white",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.05,
                "opacity": 1,
            },
            highlight_function=lambda feature: {
                "weight": 3,
                "fillOpacity": 0.1,  # Hover
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=["tooltip_text"],
                aliases=[""],
                style=(
                    "background-color: white; color: black; font-family: 'Poppins', sans-serif; font-size: 12px; padding: 8px; border: 1px solid black; border-radius: 3px;"
                ),
                sticky=True,
            ),
            name="Batas Administrasi",
        )

        geojson_layer.add_to(map_obj)

        return True
    except Exception as e:
        return False


# Function untuk Menambahkan Legenda ke Peta Folium
def add_legend_to_map(map_obj, thresholds):
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
                font-size: 12px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                min-width: 160px;">
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Kelas LST (°C)</div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #5ca0d3; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sangat Rendah (≤ {thresholds['low']:.2f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #f5ebb1; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Rendah ({thresholds['low']:.2f} - {thresholds['medium']:.2f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #dba758; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sedang ({thresholds['medium']:.2f} - {thresholds['high']:.2f}°C)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #93220e; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Tinggi (> {thresholds['high']:.2f}°C)</span>
            </div>
        </div>
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))


# Function untuk Menambahkan GeoTiff ke Peta Folium
def add_geotiff_to_map(map_obj, tif_path, thresholds):
    try:
        with rasterio.open(tif_path) as src:
            # Rasterio untuk Membaca Data Raster
            data = src.read(1)

            # Menegaskan Batas
            bounds = src.bounds

            # Handle NoData dan Outlier Piksel
            if hasattr(src, "nodata") and src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)

            # Set Nilai 0 atau Negatif sebagai NoData
            data = np.where(data <= 0, np.nan, data)

            # Warna untuk Setiap Kelas
            colors = {
                "very_low": [92, 160, 211, 255],  # #5ca0d3
                "low": [245, 235, 177, 255],  # #f5ebb1
                "medium": [219, 167, 88, 255],  # #dba758
                "high": [147, 34, 14, 255],  # #93220e
            }

            # Buat Array Warna Berdasarkan Threshold (RGBA)
            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)

            # Mask untuk Data Valid
            valid_mask = ~np.isnan(data)

            # Klasifikasi Berdasarkan Threshold
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

            # Pengaplikasian Warna Berdasarkan Klasifikasi
            colored_data[very_low_mask] = colors["very_low"]
            colored_data[low_mask] = colors["low"]
            colored_data[medium_mask] = colors["medium"]
            colored_data[high_mask] = colors["high"]

            # Set Area yang Tidak Valid dengan Warna Transparan
            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Konversi ke PIL Image
            img = Image.fromarray(colored_data, "RGBA")

            # Konversi ke base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Bounds untuk Folium
            bounds_folium = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            # Tambahkan ke Peta dengan Transparansi
            lst_overlay = folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_folium,
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
                name="Suhu Permukaan Lahan",
            )
            lst_overlay.add_to(map_obj)

        return True
    except Exception as e:
        return False


st.header("Suhu Permukaan Lahan")

selected_tab = st.pills(
    "**Pilih Mode:**",
    [
        "🗺️ Peta",
        "🔍 Perbandingan",
        "🛠️ Model",
        "✅ Validasi",
        "📈 Regresi",
    ],
    selection_mode="single",
    default="🗺️ Peta",
)

# Peta
if selected_tab == "🗺️ Peta":
    col1_peta, col2_peta = st.columns([2.4, 1.6])  # Mengubah rasio dari 3:1 ke 2.5:1.5

    with col2_peta:
        # Container untuk grafik tren (selalu tampil)
        with st.container(border=True):
            st.write("**Tren Suhu Permukaan Lahan 1999-2024**")
            trend_fig = create_trend_graph()
            st.plotly_chart(trend_fig, use_container_width=True)

        # Container dengan border
        with st.container(border=True):
            # Selectbox Tahun
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = stats_by_year[option]

        with st.container(border=True):
            # Metrics dalam 3 kolom sejajar
            col_min, col_max, col_mean = st.columns([1, 1, 1])
            with col_min:
                st.metric("LST Minimum", f"{selected_data['min']:.2f}°C")
            with col_max:
                st.metric("LST Maksimum", f"{selected_data['max']:.2f}°C")
            with col_mean:
                st.metric("LST Rata-rata", f"{selected_data['mean']:.2f}°C")

        with st.container(border=True):
            # Selectbox Cari Kecamatan
            kecamatan_options = list(lst_per_kecamatan[option].keys())
            selected_kecamatan = st.selectbox(
                "**Cari Kecamatan**",
                [""] + kecamatan_options,
                index=0,
                placeholder="Pilih Kecamatan",
            )

        # Container terpisah untuk deskripsi kecamatan dengan border
        if selected_kecamatan and selected_kecamatan != "":
            with st.container(border=True):
                kecamatan_data = lst_per_kecamatan[option][selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                description = f"**Suhu permukaan lahan** di **{toponim} {selected_kecamatan}** pada tahun **{option}** memiliki rata-rata sebesar **{kecamatan_data['mean']:.1f}°C** dengan suhu terendah yakni **{kecamatan_data['min']:.1f}°C** dan suhu tertinggi adalah **{kecamatan_data['max']:.1f}°C**."

                st.write(description)

    with col1_peta:
        # Buat Peta Folium
        m = folium.Map(
            location=[-7.764326411862208, 110.3721676814108],
            zoom_start=10.5,
            tiles=None,
        )

        # Tambahkan Basemap
        folium.TileLayer(
            tiles="OpenStreetMap", name="OpenStreetMap", overlay=False, control=True
        ).add_to(m)

        folium.TileLayer(
            tiles="CartoDB positron",
            name="CartoDB Positron",
            overlay=False,
            control=True,
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

        # Panggil GeoTiff dari Aset Lokal (2029 Sementara Memakai Data 2024)
        if option == "2029":
            tif_path = "tif/lst2024kpy.tif"
        else:
            tif_path = f"tif/lst{option}kpy.tif"

        # Set Threshold untuk Tahun yang Dipilih
        thresholds = threshold_dict[option]

        # Cek Ketersediaan GeoTiff, Panggil Function GeoTiff, dan Tampilkan ke Peta
        if os.path.exists(tif_path):
            add_geotiff_to_map(m, tif_path, thresholds)
        else:
            # Jika file tidak ditemukan, tampilkan warning
            st.warning(f"File GeoTIFF tidak ditemukan: {tif_path}")

        # Cek Ketersediaan AOI, Panggil Function Batas AOI, dan Tampilkan ke Peta
        shapefile_path = "shp/aoi_kpy.shp"
        if os.path.exists(shapefile_path):
            add_shapefile_to_map(m, shapefile_path)
        else:
            # Jika file tidak ditemukan, tampilkan warning
            st.warning(f"File Shapefile tidak ditemukan: {shapefile_path}")

        # Tambahkan Legenda ke Peta
        add_legend_to_map(m, thresholds)

        # Tambahkan Control Layer ke Peta Setelah Semua Layer Ditambahkan
        folium.LayerControl(position="topleft", collapsed=True).add_to(m)

        # CSS untuk Custom Peta Folium
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
        st_data = st_folium(m, use_container_width=True)
