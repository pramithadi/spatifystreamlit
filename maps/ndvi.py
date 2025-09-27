import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import folium
from streamlit.components.v1 import html
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import os
import base64
from io import BytesIO
import requests
from PIL import Image
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error

st.set_page_config(
    page_title="NDVI — Spatify",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# CUSTOM CSS
# ==============================================================================
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    .main {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }
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
    div[data-testid="stMarkdownContainer"] h1 {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    .stApp > header {
        color: #000000 !important;
    }
    .stApp {
        color: #000000 !important;
    }
    .stMarkdown {
        color: #000000 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 12px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
        border: 0.5px solid rgba(0, 0, 0, 0.1)
        !important;
        border-radius: 1px !important;
        padding: 12px !important;
        # box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
        # background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important; # Shadow Hover
        border-color: #fdfaf6 !important;
    }           
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
        margin-top: 0rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Dictionary Statistik NDVI
stats_by_year = {
    "1999": {"min": -0.120, "max": 0.884, "mean": 0.535},
    "2004": {"min": -0.214, "max": 0.944, "mean": 0.592},
    "2009": {"min": -0.220, "max": 0.890, "mean": 0.554},
    "2014": {"min": -0.482, "max": 0.928, "mean": 0.596},
    "2019": {"min": -0.271, "max": 0.971, "mean": 0.587},
    "2024": {"min": -0.488, "max": 0.982, "mean": 0.592},
    "2029": {"min": -0.136, "max": 0.867, "mean": 0.585},
}

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

NDVI_IMAGE_BOUNDS = {
    "1999": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2004": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2009": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2014": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2019": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2024": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2029": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
}

PNG_URLS = {
    "1999": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_1999.png",
    "2004": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2004.png",
    "2009": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2009.png",
    "2014": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2014.png",
    "2019": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2019.png",
    "2024": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2024.png",
    "2029": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2029.png",
}

PLOT_VIZ_URLS = {
    "ndvi_2024": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2024.png",
    "ndvi_2024a": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2024a.png",
    "ndvi_2029": "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main/static/ndvi_2029.png",
}

KECAMATAN_BOUNDS = {
    "Pajangan": {
        "min_lat": -7.910154,
        "max_lat": -7.834027,
        "min_lon": 110.256581,
        "max_lon": 110.324644,
        "wadmkk": "Bantul",
    },
    "Bantul": {
        "min_lat": -7.920525,
        "max_lat": -7.861570,
        "min_lon": 110.309473,
        "max_lon": 110.363740,
        "wadmkk": "Bantul",
    },
    "Banguntapan": {
        "min_lat": -7.863121,
        "max_lat": -7.783162,
        "min_lon": 110.375198,
        "max_lon": 110.430849,
        "wadmkk": "Bantul",
    },
    "Pleret": {
        "min_lat": -7.900738,
        "max_lat": -7.854634,
        "min_lon": 110.375855,
        "max_lon": 110.454720,
        "wadmkk": "Bantul",
    },
    "Piyungan": {
        "min_lat": -7.872696,
        "max_lat": -7.817384,
        "min_lon": 110.420561,
        "max_lon": 110.521309,
        "wadmkk": "Bantul",
    },
    "Sewon": {
        "min_lat": -7.887412,
        "max_lat": -7.823997,
        "min_lon": 110.317446,
        "max_lon": 110.382072,
        "wadmkk": "Bantul",
    },
    "Kasihan": {
        "min_lat": -7.861318,
        "max_lat": -7.768220,
        "min_lon": 110.280408,
        "max_lon": 110.352569,
        "wadmkk": "Bantul",
    },
    "Sedayu": {
        "min_lat": -7.865454,
        "max_lat": -7.784616,
        "min_lon": 110.221201,
        "max_lon": 110.290698,
        "wadmkk": "Bantul",
    },
    "Gamping": {
        "min_lat": -7.835228,
        "max_lat": -7.735666,
        "min_lon": 110.280362,
        "max_lon": 110.355014,
        "wadmkk": "Sleman",
    },
    "Godean": {
        "min_lat": -7.797698,
        "max_lat": -7.734785,
        "min_lon": 110.262531,
        "max_lon": 110.330165,
        "wadmkk": "Sleman",
    },
    "Moyudan": {
        "min_lat": -7.815200,
        "max_lat": -7.739029,
        "min_lon": 110.218705,
        "max_lon": 110.287664,
        "wadmkk": "Sleman",
    },
    "Minggir": {
        "min_lat": -7.759545,
        "max_lat": -7.705374,
        "min_lon": 110.215910,
        "max_lon": 110.281926,
        "wadmkk": "Sleman",
    },
    "Seyegan": {
        "min_lat": -7.765134,
        "max_lat": -7.694704,
        "min_lon": 110.271502,
        "max_lon": 110.326240,
        "wadmkk": "Sleman",
    },
    "Mlati": {
        "min_lat": -7.774225,
        "max_lat": -7.700432,
        "min_lon": 110.304482,
        "max_lon": 110.385777,
        "wadmkk": "Sleman",
    },
    "Depok": {
        "min_lat": -7.801695,
        "max_lat": -7.731390,
        "min_lon": 110.369320,
        "max_lon": 110.447550,
        "wadmkk": "Sleman",
    },
    "Berbah": {
        "min_lat": -7.836623,
        "max_lat": -7.777257,
        "min_lon": 110.421167,
        "max_lon": 110.487754,
        "wadmkk": "Sleman",
    },
    "Kalasan": {
        "min_lat": -7.785957,
        "max_lat": -7.700159,
        "min_lon": 110.438728,
        "max_lon": 110.491072,
        "wadmkk": "Sleman",
    },
    "Ngemplak": {
        "min_lat": -7.755650,
        "max_lat": -7.667755,
        "min_lon": 110.408553,
        "max_lon": 110.482772,
        "wadmkk": "Sleman",
    },
    "Ngaglik": {
        "min_lat": -7.755560,
        "max_lat": -7.672081,
        "min_lon": 110.366557,
        "max_lon": 110.443259,
        "wadmkk": "Sleman",
    },
    "Tegalrejo": {
        "min_lat": -7.794187,
        "max_lat": -7.766468,
        "min_lon": 110.348662,
        "max_lon": 110.369357,
        "wadmkk": "Kota Yogyakarta",
    },
    "Gondokusuman": {
        "min_lat": -7.798199,
        "max_lat": -7.774690,
        "min_lon": 110.368024,
        "max_lon": 110.396002,
        "wadmkk": "Kota Yogyakarta",
    },
    "Danurejan": {
        "min_lat": -7.797274,
        "max_lat": -7.788140,
        "min_lon": 110.365368,
        "max_lon": 110.378419,
        "wadmkk": "Kota Yogyakarta",
    },
    "Gedongtengen": {
        "min_lat": -7.796348,
        "max_lat": -7.787196,
        "min_lon": 110.355268,
        "max_lon": 110.366438,
        "wadmkk": "Kota Yogyakarta",
    },
    "Ngampilan": {
        "min_lat": -7.808621,
        "max_lat": -7.795570,
        "min_lon": 110.353681,
        "max_lon": 110.362159,
        "wadmkk": "Kota Yogyakarta",
    },
    "Wirobrajan": {
        "min_lat": -7.813477,
        "max_lat": -7.792852,
        "min_lon": 110.344800,
        "max_lon": 110.355440,
        "wadmkk": "Kota Yogyakarta",
    },
    "Mantrijeron": {
        "min_lat": -7.826771,
        "max_lat": -7.808277,
        "min_lon": 110.350798,
        "max_lon": 110.368479,
        "wadmkk": "Kota Yogyakarta",
    },
    "Kraton": {
        "min_lat": -7.814891,
        "max_lat": -7.802875,
        "min_lon": 110.355851,
        "max_lon": 110.369373,
        "wadmkk": "Kota Yogyakarta",
    },
    "Gondomanan": {
        "min_lat": -7.808194,
        "max_lat": -7.796072,
        "min_lon": 110.360510,
        "max_lon": 110.374300,
        "wadmkk": "Kota Yogyakarta",
    },
    "Pakualaman": {
        "min_lat": -7.804580,
        "max_lat": -7.796715,
        "min_lon": 110.369749,
        "max_lon": 110.380511,
        "wadmkk": "Kota Yogyakarta",
    },
    "Mergangsan": {
        "min_lat": -7.826884,
        "max_lat": -7.801539,
        "min_lon": 110.367476,
        "max_lon": 110.381472,
        "wadmkk": "Kota Yogyakarta",
    },
    "Umbulharjo": {
        "min_lat": -7.840072,
        "max_lat": -7.788484,
        "min_lon": 110.374580,
        "max_lon": 110.398505,
        "wadmkk": "Kota Yogyakarta",
    },
    "Kotagede": {
        "min_lat": -7.833535,
        "max_lat": -7.802250,
        "min_lon": 110.390140,
        "max_lon": 110.404935,
        "wadmkk": "Kota Yogyakarta",
    },
    "Sleman": {
        "min_lat": -7.728679,
        "max_lat": -7.662370,
        "min_lon": 110.306495,
        "max_lon": 110.381601,
        "wadmkk": "Sleman",
    },
    "Turi": {
        "min_lat": -7.682863,
        "max_lat": -7.571829,
        "min_lon": 110.343410,
        "max_lon": 110.418494,
        "wadmkk": "Sleman",
    },
    "Pakem": {
        "min_lat": -7.702673,
        "max_lat": -7.541162,
        "min_lon": 110.377110,
        "max_lon": 110.445520,
        "wadmkk": "Sleman",
    },
    "Cangkringan": {
        "min_lat": -7.689823,
        "max_lat": -7.541162,
        "min_lon": 110.426367,
        "max_lon": 110.477433,
        "wadmkk": "Sleman",
    },
    "Jetis": {
        "min_lat": -7.789966,
        "max_lat": -7.773196,
        "min_lon": 110.355054,
        "max_lon": 110.371467,
        "wadmkk": "Kota Yogyakarta",
    },
}


# ==============================================================================
# DEKLARASI FUNGSI
# ==============================================================================
@st.cache_data
def load_and_prep_geojson(geojson_path):
    try:
        import json

        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        for feature in geojson_data["features"]:
            props = feature.get("properties", {})
            namobj = props.get("NAMOBJ", "Unknown")
            wadmkk = props.get("WADMKK", "")
            if "Sleman" in wadmkk or "Bantul" in wadmkk:
                tooltip_text = f"Kapanewon {namobj}"
            elif "Yogyakarta" in wadmkk:
                tooltip_text = f"Kemantren {namobj}"
            else:
                tooltip_text = namobj
            feature["properties"]["tooltip_text"] = tooltip_text
        return geojson_data
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        return None


@st.cache_data
def load_stats_kec():
    csv_path = "./csv/ndviStatsKec.csv"
    try:
        df = pd.read_csv(csv_path)
        df["Tahun"] = df["Tahun"].astype(str)
        return df
    except FileNotFoundError:
        return None


def get_kec_by_year(df, year):
    if df is None or df.empty:
        return {}
    year_data = df[df["Tahun"] == str(year)]
    if year_data.empty:
        return {}
    kecamatan_dict = {}
    for _, row in year_data.iterrows():
        kecamatan_dict[row["NAMOBJ"]] = {
            "min": row["min"],
            "max": row["max"],
            "mean": row["mean"],
            "wadmkk": row["WADMKK"],
        }
    return kecamatan_dict


def get_toponim(wadmkk):
    if "Sleman" in wadmkk or "Bantul" in wadmkk:
        return "Kapanewon"
    elif "Yogyakarta" in wadmkk:
        return "Kemantren"
    else:
        return "Kecamatan"


def get_kecamatan_bounds_static(namobj):
    if namobj in KECAMATAN_BOUNDS:
        bounds = KECAMATAN_BOUNDS[namobj]
        return [
            [bounds["min_lat"], bounds["min_lon"]],
            [bounds["max_lat"], bounds["max_lon"]],
        ]
    return None


def add_shp_to_map(map_obj, geojson_data):
    try:
        if geojson_data is None:
            st.warning("Batas administrasi tidak dapat dimuat.")
            return False
        geojson_layer = folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                "fillColor": "white",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.05,
            },
            highlight_function=lambda feature: {
                "weight": 3,
                "fillOpacity": 0.1,
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
            show=True,
        )
        geojson_layer.add_to(map_obj)
        return True
    except Exception as e:
        st.error(f"ERROR saat menambahkan GeoJSON: {e}")
        return False


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
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Tingkat Kerapatan Vegetasi</div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #8b0000; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Non-vegetasi (≤ {thresholds['low']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #ffffe0; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Rendah ({thresholds['low']:.3f} - {thresholds['medium']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #90ee90; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sedang ({thresholds['medium']:.3f} - {thresholds['high']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #006400; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Tinggi (> {thresholds['high']:.3f})</span>
            </div>
        </div>
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))


@st.cache_data
def load_image_from_url(url):
    """Load image from URL and cache it to avoid repeated downloads"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return np.array(img)
    except Exception as e:
        st.error(f"Error loading image from {url}: {str(e)}")
        return None


def rgba_to_classification_ndvi(rgba_array):
    """Convert RGBA array to NDVI classification values"""
    if rgba_array is None:
        return None

    height, width, _ = rgba_array.shape
    classified = np.full((height, width), np.nan, dtype=np.float32)

    colors_rgb = {
        (139, 0, 0): 0,  # very_low - merah gelap (tanah kosong/bangunan)
        (255, 255, 224): 1,  # low - kuning muda (vegetasi sparse)
        (144, 238, 144): 2,  # medium - hijau muda (vegetasi sedang)
        (0, 100, 0): 3,  # high - hijau tua (vegetasi lebat)
    }

    # Ekstrak RGB
    r = rgba_array[:, :, 0]
    g = rgba_array[:, :, 1]
    b = rgba_array[:, :, 2]
    alpha = rgba_array[:, :, 3]

    for (target_r, target_g, target_b), class_val in colors_rgb.items():
        mask = (
            (np.abs(r - target_r) <= 5)
            & (np.abs(g - target_g) <= 5)
            & (np.abs(b - target_b) <= 5)
            & (alpha > 0)  # Not transparent
        )
        classified[mask] = class_val

    return classified


def add_png_to_map(map_obj, year, thresholds):
    try:
        png_url = PNG_URLS.get(year)
        if not png_url:
            st.error(f"File PNG untuk tahun: {year} tidak ditemukan.")
            return False

        if year not in NDVI_IMAGE_BOUNDS:
            st.error(f"Bounds untuk tahun {year} tidak ditemukan.")
            return False

        bounds_folium = NDVI_IMAGE_BOUNDS[year]
        ndvi_overlay = folium.raster_layers.ImageOverlay(
            image=png_url,
            bounds=bounds_folium,
            opacity=1.0,
            interactive=True,
            cross_origin=False,
            zindex=1,
            name=f"NDVI {year}",
            show=True,
        )
        ndvi_overlay.add_to(map_obj)
        return True
    except Exception as e:
        st.error(f"Error menambahkan PNG ke peta: {e}")
        return False


def load_all_map_data():
    # 1. Load Statistik Kecamatan
    df_kec_stats = load_stats_kec()
    if df_kec_stats is None:
        st.error(
            "Gagal memuat file CSV statistik kecamatan. Pastikan file ada di `csv/ndviStatsKec.csv`"
        )

    # 2. Load GeoJSON
    shapefile_path = "shp/aoi_kpy.json"
    geojson_data = None
    if os.path.exists(shapefile_path):
        geojson_data = load_and_prep_geojson(shapefile_path)
    else:
        st.warning(f"File SHP tidak ditemukan: {shapefile_path}")

    return {
        "df_kec_stats": df_kec_stats,
        "geojson_data": geojson_data,
    }


@st.cache_resource
def create_base_map():
    m = folium.Map(
        location=[-7.764326411862208, 110.3721676814108],
        zoom_start=10.5,
        tiles="OpenStreetMap",
    )

    folium.TileLayer(tiles="CartoDB positron", name="CartoDB Positron").add_to(m)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Google Satellite",
    ).add_to(m)
    return m


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

st.header("Normalized Difference Vegetation Index")

(
    tab1,
    tab2,
    tab3,
    tab4,
) = st.tabs(
    [
        "🗺️ Peta",
        "📈 Tren",
        "✅ Validasi",
        "⚙️ Model",
    ]
)

# ==============================================================================
# SECTION 1: PETA
# ==============================================================================
# Peta
with tab1:
    if "map_data_loaded" not in st.session_state:
        with st.spinner("Mempersiapkan data peta..."):
            map_data = load_all_map_data()
            st.session_state.map_data = map_data
            st.session_state.map_data_loaded = True

    map_data = st.session_state.get("map_data", {})

    df_aoi = map_data.get("df_aoi")
    df_kec = map_data.get("df_kec")
    df_kec_stats = map_data.get("df_kec_stats")
    geojson_data = map_data.get("geojson_data")

    st.badge(
        "**Peta NDVI di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )

    col1_peta, col2_peta = st.columns([2.5, 1.5])

    with col2_peta:
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = stats_by_year[option]

        # Container Metrics NDVI
        col1_peta_metric, col2_peta_metric, col3_peta_metric = st.columns([1, 1, 1])
        with col1_peta_metric:
            with st.container(border=True):
                st.metric("NDVI Min", f"{selected_data['min']:.2f}")
        with col2_peta_metric:
            with st.container(border=True):
                st.metric("NDVI Max", f"{selected_data['max']:.2f}")
        with col3_peta_metric:
            with st.container(border=True):
                st.metric("NDVI Mean", f"{selected_data['mean']:.2f}")

        # Container Selectbox Kecamatan
        with st.container(border=True):
            # Ambil Data Statistik Kecamatan dari DataFrame
            kec_year = get_kec_by_year(df_kec_stats, option)

            # Selectbox Cari Kecamatan
            if kec_year:
                kecamatan_options = list(kec_year.keys())
                selected_kecamatan = st.selectbox(
                    "**Cari Kecamatan**",
                    [""] + kecamatan_options,
                    index=0,
                    placeholder="Ketik atau pilih kecamatan",
                )
            else:
                st.warning(f"Data kecamatan untuk tahun {option} tidak tersedia.")
                selected_kecamatan = ""

        # Function Klasifikasi Deskripsi
        def classify_ndvi(mean_value, thresholds):
            if mean_value <= thresholds["low"]:
                return "sangat rendah", "sangat rendah"
            elif thresholds["low"] < mean_value <= thresholds["medium"]:
                return "tergolong rendah", "tergolong rendah"
            elif thresholds["medium"] < mean_value <= thresholds["high"]:
                return "cukup sedang", "cukup sedang"
            else:  # mean_value > thresholds['high']
                return "tinggi", "tinggi"

        # Container Analisis NDVI per Kecamatan
        if selected_kecamatan and selected_kecamatan != "" and kec_year:
            with st.container(border=True):
                st.write("💡 **Quick Insight**")
                kecamatan_data = kec_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                current_thresholds = threshold_dict[option]

                kategori, deskripsi = classify_ndvi(
                    kecamatan_data["mean"], current_thresholds
                )

                # Pengkondisian Tahun 2029
                if option == "2029":
                    description = f"Pada tahun :green-background[**{option}**], **{toponim} {selected_kecamatan}** :green-background[**diprediksi**] memiliki nilai rata-rata NDVI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai ini mengindikasikan bahwa :green-background[**{toponim} {selected_kecamatan}**] memiliki tingkat **kerapatan vegetasi** yang :green-background[**{deskripsi}**] pada masa mendatang."
                else:
                    description = f"Pada tahun :green-background[**{option}**], **{toponim} {selected_kecamatan}** memiliki nilai rata-rata NDVI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai ini mengindikasikan bahwa :green-background[**{toponim} {selected_kecamatan}**] memiliki tingkat **kerapatan vegetasi** yang :green-background[**{deskripsi}**]."

                st.write(description)

    with col1_peta:
        map_center = [-7.764326411862208, 110.3721676814108]
        zoom_level = 10.5

        if selected_kecamatan:
            kec_bounds = get_kecamatan_bounds_static(selected_kecamatan)
            if kec_bounds:
                center_lat = (kec_bounds[0][0] + kec_bounds[1][0]) / 2
                center_lon = (kec_bounds[0][1] + kec_bounds[1][1]) / 2
                map_center = [center_lat, center_lon]
                zoom_level = 15

        m = folium.Map(
            location=map_center, zoom_start=zoom_level, tiles="OpenStreetMap"
        )

        folium.TileLayer(tiles="CartoDB positron", name="CartoDB Positron").add_to(m)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite",
            name="Google Satellite",
        ).add_to(m)
        folium.TileLayer(tiles="OpenStreetMap", name="OpenStreetMap").add_to(m)

        thresholds = threshold_dict[option]
        png_success = add_png_to_map(m, option, thresholds)
        if not png_success:
            st.info("Menampilkan peta tanpa layer NDVI.")

        add_shp_to_map(m, geojson_data)

        try:
            add_legend_to_map(m, thresholds)
        except Exception as e:
            st.warning("Legenda tidak dapat ditampilkan.")

        folium.LayerControl(position="topleft", collapsed=True).add_to(m)

        css = """
        <style>
        .folium-map { height: 100% !important; }
        .leaflet-control-layers label, .leaflet-control-layers-list,
        .leaflet-control-layers-expanded, .leaflet-control-attribution {
            font-size: 11px !important;
            font-family: 'Poppins', sans-serif !important;
        }
        </style>
        """
        m.get_root().header.add_child(folium.Element(css))
        html(m.get_root().render(), height=600, scrolling=False)

# ==============================================================================
# SECTION 2: TREN
# ==============================================================================
with tab2:
    df_urban_rural = pd.read_csv("./csv/ndviStatsKec.csv")

    ndvi_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    ndvi_urban_rural_pivot = ndvi_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking NDVI
    st.badge(
        "**Tren NDVI di Kawasan Perkotaan dan Non-Perkotaan Yogyakarta (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2.2, 1.8])
    with col1_tren_main:
        # Container Grafik Tren
        with st.container(border=True):
            # Buat Grafik
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            fig = go.Figure()

            if "Urban" in ndvi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndvi_urban_rural_pivot.index,
                        y=ndvi_urban_rural_pivot["Urban"],
                        mode="lines+markers",
                        name="Perkotaan",
                        line=dict(color="#FF90BB", width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate="<b>Perkotaan</b><br>Tahun: %{x}<br>NDVI Mean: %{y:.3f}<extra></extra>",
                    )
                )

            if "Rural" in ndvi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndvi_urban_rural_pivot.index,
                        y=ndvi_urban_rural_pivot["Rural"],
                        mode="lines+markers",
                        name="Non-Perkotaan",
                        line=dict(color="#096B68", width=3),
                        marker=dict(size=8, symbol="square"),
                        hovertemplate="<b>Non-Perkotaan</b><br>Tahun: %{x}<br>NDVI Mean: %{y:.3f}<extra></extra>",
                    )
                )

            fig.add_vline(
                x=2024,
                line_width=2,
                line_dash="dash",
                line_color="grey",
                annotation_text="Proyeksi",
                annotation_position="top right",
            )

            # Update Tren
            fig.update_layout(
                xaxis=dict(
                    title=dict(
                        text="Tahun",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    tickvals=[1999, 2004, 2009, 2014, 2019, 2024, 2029],
                    gridcolor="#9A9A9A",
                ),
                yaxis=dict(
                    title=dict(
                        text="NDVI Mean",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    gridcolor="#9A9A9A",
                    zerolinecolor="#9A9A9A",
                    # range=[-0.25, 0.05],
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=10, r=10, t=20, b=5),
                height=320,
                font=dict(family="Poppins", size=12),
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Dictionary Mean NDVI
        mean_by_year = {
            1999: {"mean": 0.535},
            2004: {"mean": 0.592},
            2009: {"mean": 0.554},
            2014: {"mean": 0.596},
            2019: {"mean": 0.587},
            2024: {"mean": 0.592},
            2029: {"mean": 0.585},
        }

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡 **Quick Insight**
                - Nilai :green-background[**NDVI**] berkisar dari :green-background[**-1**] (area non-vegetasi) hingga :green-background[**+1**]. Semakin tinggi nilainya, semakin rapat vegetasinya.
                - Terlihat tren yang sangat kontras. :green-background[**Kawasan non-perkotaan**] secara konsisten menunjukkan nilai NDVI yang :green-background[**sangat tinggi (di atas 0.5)**], mengindikasikan **area dengan kehijauan vegetasi yang terjaga**.
                - Sebaliknya, :green-background[**kawasan non-perkotaan**] memiliki nilai NDVI yang :green-background[**jauh lebih rendah**] dan diproyeksikan akan terus **menurun**. Pola ini menandakan **berkurangnya kerapatan vegetasi** seiring waktu.
                """
            )

    # Row Diagram Garis & Ranking NDVI
    st.badge(
        "**Peringkat Kecamatan Berdasarkan Rata-rata NDVI (1999-2024)**",
        color="primary",
    )

    col_rank = st.columns([1])[0]
    with col_rank:
        df_stats = pd.read_csv("./csv/ndviStatsKec.csv")

        # Hitung Rata-rata Mean untuk Setiap Kecamatan dari Semua Tahun
        df_ranking = (
            df_stats.groupby(["NAMOBJ", "WADMKK", "Zona"])["mean"].mean().reset_index()
        )
        df_ranking.columns = ["NAMOBJ", "WADMKK", "Zona", "Mean_NDVI"]

        # Sort dari Tertinggi ke Terendah
        df_ranking = df_ranking.sort_values("Mean_NDVI", ascending=False).reset_index(
            drop=True
        )

        # Buat Label untuk Sumbu Y Berdasarkan WADMKK
        def create_y_label(row):
            if row["WADMKK"] in ["Bantul", "Sleman"]:
                return f"Kapanewon {row['NAMOBJ']}"
            elif row["WADMKK"] == "Kota Yogyakarta":
                return f"Kemantren {row['NAMOBJ']}"
            else:
                return row["NAMOBJ"]

        df_ranking["Y_Label"] = df_ranking.apply(create_y_label, axis=1)

        # Buat Label Zona untuk Tooltip
        df_ranking["Zona_Label"] = df_ranking["Zona"].map(
            {"Urban": "Perkotaan", "Rural": "Non-Perkotaan"}
        )

        # Buat Bar
        fig = px.bar(
            df_ranking,
            x="Mean_NDVI",
            y="Y_Label",
            color="Zona",
            color_discrete_map={"Urban": "#FF90BB", "Rural": "#096B68"},
            orientation="h",
            labels={
                "Mean_NDVI": "NDVI Mean",
                "Y_Label": "",
                "Zona": "Kawasan",
            },
            # Isi Hover
            hover_data={"Mean_NDVI": ":.3f", "Zona": False, "Y_Label": False},
            custom_data=["Zona_Label", "Mean_NDVI"],
        )

        # Update Hover Template
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>"
            + "Kawasan: %{customdata[0]}<br>"
            + "NDVI Mean: %{customdata[1]:.3f}<extra></extra>",
            texttemplate="%{x:.3f}",
            textposition="outside",
            textfont_size=12,
            textfont_color="black",
        )

        # Update dan Styling Bar Plot
        fig.update_layout(
            height=800,
            font=dict(family="Poppins", size=12),
            title_font_size=12,
            xaxis_title_font_size=12,
            yaxis_title_font_size=12,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="bottom",
                y=0.02,
                xanchor="right",
                x=0.98,
                font=dict(family="Poppins"),
            ),
            yaxis=dict(
                categoryorder="array", categoryarray=df_ranking["Y_Label"][::-1]
            ),
            title="",
            margin=dict(t=10),  # Mengurangi Margin Top Supaya Tidak Ada Gap
        )

        # Sumbu Warna Hitam
        fig.update_xaxes(title_font_color="black", tickfont_color="black")
        fig.update_yaxes(title_font_color="black", tickfont_color="black")

        # Update Legenda
        for trace in fig.data:
            if trace.name == "Urban":
                trace.name = "Perkotaan"
            elif trace.name == "Rural":
                trace.name = "Non-Perkotaan"

        # Display Bar Plot
        st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# SECTION 3: VALIDASI
# ==============================================================================

with tab3:
    try:
        # Load CSV Sampel NDVI untuk Validasi
        validation_data = pd.read_csv("csv/ndviSampelValidasi.csv")

        # Hapus Nilai NaN
        validation_data = validation_data.dropna()

        # Ekstraksi Nilai dari Field
        sentinel_values = validation_data["ndviSentinel"].values  # X
        landsat_values = validation_data["ndviLandsat"].values  # Y

        # Hitung Korelasi Pearson
        correlation_coef, p_value = stats.pearsonr(sentinel_values, landsat_values)

        # RMSE
        rmse = np.sqrt(mean_squared_error(sentinel_values, landsat_values))

        # MAE
        mae = mean_absolute_error(sentinel_values, landsat_values)

        # Hitung Persamaan Linear
        slope, intercept, r_value, p_val, std_err = stats.linregress(
            sentinel_values, landsat_values
        )

        # Buat Persamaan
        if intercept >= 0:
            equation = f"y = {slope:.3f}x + {intercept:.3f}"
        else:
            equation = f"y = {slope:.3f}x - {abs(intercept):.3f}"

        # Row Diagram Garis dan Validasi NDVI
        st.badge(
            "**Korelasi Pearson NDVI Landsat 8 dan Sentinel-2 (2024)**",
            color="primary",
        )

        col1_validate, col2_validate = st.columns([2.2, 1.8])
        with col1_validate:
            # Container Grafik Korelasi Pearson
            with st.container(border=True):
                # Buat Scatterplot (X = Sentinel, Y = Landsat)
                fig = px.scatter(
                    x=sentinel_values,
                    y=landsat_values,
                    labels={"x": "NDVI Sentinel-2", "y": "NDVI Landsat 8"},
                    opacity=0.6,
                    color_discrete_sequence=["#1f77b4"],
                )

                # Garis Trend (Y = slope*X + intercept)
                x_range = np.linspace(sentinel_values.min(), sentinel_values.max(), 100)
                y_trend = slope * x_range + intercept

                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_trend,
                        mode="lines",
                        name="Garis Regresi",
                        line=dict(color="red", width=2),
                    )
                )

                # Update Layout
                fig.update_layout(
                    height=445,
                    showlegend=True,
                    template="plotly_white",
                    font=dict(
                        family="Poppins, sans-serif",  # Font Poppins
                        size=12,
                        color="black",
                    ),
                    margin=dict(t=30, b=20, l=20, r=20),
                    # Styling Sumbu X dan Y
                    xaxis=dict(
                        title=dict(
                            text="NDVI Sentinel-2",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    yaxis=dict(
                        title=dict(
                            text="NDVI Landsat 8",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    legend={
                        "orientation": "h",
                        "yanchor": "top",
                        "y": -0.25,
                        "xanchor": "center",
                        "x": 0.5,
                        "font": {"family": "Poppins", "size": 14, "color": "black"},
                    },
                )

                # Box Info
                fig.add_annotation(
                    x=0.02,
                    y=0.98,
                    xref="paper",
                    yref="paper",
                    text=f"<b>{equation}</b>",
                    showarrow=False,
                    font=dict(size=12, color="black", family="Poppins, sans-serif"),
                    bgcolor="#fdfaf6",
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=7,
                    xanchor="left",
                    yanchor="top",
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2_validate:
            # Row Metrics
            col1_validate_metric, col2_validate_metric, col3_validate_metric = (
                st.columns([1, 1, 1])
            )
            with col1_validate_metric:
                with st.container(border=True):
                    st.metric(
                        label="r",
                        value=f"{correlation_coef:.3f}",
                        help="Koefisien Korelasi Pearson (-1 hingga 1)",
                    )

            with col2_validate_metric:
                with st.container(border=True):
                    st.metric(
                        label="RMSE",
                        value=f"{rmse:.3f}",
                        help="Root Mean Square Error",
                    )

            with col3_validate_metric:
                with st.container(border=True):
                    st.metric(
                        label="MAE",
                        value=f"{mae:.3f}",
                        help="Mean Absolute Error",
                    )

            # Container Analisis Tren
            with st.container(border=True):
                st.markdown("💡 **Quick Insight**")

                # Interpretasi Korelasi
                if correlation_coef == 0:
                    corr_interpretation = "Tidak Ada Korelasi"
                    corr_color = "🔴"
                elif correlation_coef == 1:
                    corr_interpretation = "Korelasi Positif Sempurna"
                    corr_color = "🔵"
                elif correlation_coef == -1:
                    corr_interpretation = "Korelasi Negatif Sempurna"
                    corr_color = "🔵"
                elif 0 < correlation_coef < 0.3:
                    corr_interpretation = "Korelasi Positif Lemah"
                    corr_color = "🟡"
                elif -0.3 < correlation_coef < 0:
                    corr_interpretation = "Korelasi Negatif Lemah"
                    corr_color = "🟡"
                elif 0.3 <= correlation_coef < 0.7:
                    corr_interpretation = "Korelasi Positif Sedang"
                    corr_color = "🟠"
                elif -0.7 < correlation_coef <= -0.3:
                    corr_interpretation = "Korelasi Negatif Sedang"
                    corr_color = "🟠"
                elif 0.7 <= correlation_coef < 1:
                    corr_interpretation = "Korelasi Positif Kuat"
                    corr_color = "🟢"
                elif -1 < correlation_coef <= -0.7:
                    corr_interpretation = "Korelasi Negatif Kuat"
                    corr_color = "🟢"
                else:
                    corr_interpretation = "Tidak Terdefinisi"
                    corr_color = "🔴"

                st.markdown(
                    f"""
                    - **Korelasi Sangat Kuat**: NDVI Landsat 8 dan Sentinel-2 memiliki hubungan kuat (:green-background[**r**] = :green-background[**{correlation_coef:.3f}**])<sup>[1]</sup>.
                    - **Akurasi Tinggi**: Kesalahan antar data :green-background[**sangat kecil**] (RMSE = {rmse:.3f}, MAE = {mae:.3f}) menandakan hasil pengolahan NDVI kedua satelit hampir :green-background[**identik**]<sup>[2]</sup>.
                    - Hubungan kedua NDVI :green-background[**valid secara statistik**] dengan nilai **p-value sangat signifikan** (< 0.01)<sup>[3]</sup>.
                """,
                    unsafe_allow_html=True,
                )

                # Status Validasi
                abs_corr = abs(correlation_coef)
                if abs_corr >= 0.7 and rmse <= 0.1:
                    st.success("✅ VALID! Data layak untuk prediksi LST!")
                elif abs_corr >= 0.5 and rmse <= 0.15:
                    st.warning("⚠️ CUKUP VALID — Data dapat digunakan dengan catatan.")
                elif abs_corr >= 0.3 and rmse <= 0.2:
                    st.warning("⚠️ KURANG VALID — Data perlu perbaikan.")
                else:
                    st.error("❌ TIDAK VALID — Data tidak layak digunakan.")

    except FileNotFoundError:
        st.error("❌ File 'csv/ndviSampelValidasi.csv' tidak ditemukan!")
        st.info(
            "Pastikan file CSV hasil sampling dari GEE sudah tersedia di folder 'csv/'"
        )

    except Exception as e:
        st.error(f"❌ Error dalam memproses data: {str(e)}")
        st.info(
            "Periksa format file CSV dan nama kolom ('ndviLandsat' dan 'ndviSentinel')"
        )

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
        - [1] Ratner, B. (2009). The Correlation Coefficient: Its Values Range Between +1/-1, or Do They?. *Journal of Targeting, Measurement and Analysis for Marketing*, 17. 139-142. https://doi.org/10.1057/jt.2009.5
        - [2] Chen, J., Zhu, X., Imura, H., Chen, X. (2010). Consistency of Accuracy Assessment Indices for Soft Classification: Simulation Analysis. *ISPRS Journal of Photogrammetry and Remote Sensing*, 65(6). 156-164. https://doi.org/10.1016/j.isprsjprs.2009.10.003
        - [3] Schmidt, J., & Osebold, R. (2017). Environmental Management Systems as A Driver for Sustainability: State of Implementation, Benefits, and Barriers in German Construction Companies. *Journal of Civil Engineering and Management*, 23(1). 150-162. https://doi.org/10.3846/13923730.2014.946441
        """
        )

# ==============================================================================
# SECTION 4: MODEL
# ==============================================================================

with tab4:
    st.badge(
        "**Evaluasi Model Proyeksi XGBoost**",
        color="primary",
    )

    col1_metrik_img, col2_metrik_insight = st.columns([1.85, 2.15])
    with col1_metrik_img:
        with st.container(border=True):
            fig = go.Figure(
                data=[
                    go.Bar(
                        name="RMSE",
                        x=["RMSE"],
                        y=[0.0585],
                        text=["0.0585"],
                        textposition="outside",
                        marker_color="#F5C9B0",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="MAE",
                        x=["MAE"],
                        y=[0.0439],
                        text=["0.0439"],
                        textposition="outside",
                        marker_color="#A6B28B",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="R²",
                        x=["R²"],
                        y=[0.8765],
                        text=["0.8765"],
                        textposition="outside",
                        marker_color="#1C352D",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                ]
            )

            fig.update_layout(
                xaxis={"tickfont": {"family": "Poppins", "size": 12, "color": "black"}},
                yaxis={
                    "title": {
                        "text": "Nilai",
                        "font": {"family": "Poppins", "size": 12, "color": "black"},
                    },
                    "tickfont": {"family": "Poppins", "size": 12, "color": "black"},
                    "range": [0, 1],
                },
                legend={
                    "orientation": "h",
                    "yanchor": "top",
                    "y": -0.15,
                    "xanchor": "center",
                    "x": 0.5,
                    "font": {"family": "Poppins", "size": 12, "color": "black"},
                },
                font={"family": "Poppins"},
                plot_bgcolor="#fdfaf6",
                paper_bgcolor="#fdfaf6",
                margin=dict(l=0, r=0, t=10, b=30),
                height=335,
                showlegend=True,
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")

            st.plotly_chart(fig, use_container_width=True)

    with col2_metrik_insight:
        with st.container(border=True):
            st.write("💡 **Quick Insight**")
            st.markdown(
                f"""
                - **RMSE** dan **MAE** menunjukkan nilai yang **sangat kecil** artinya model proyeksi memiliki :green-background[**tingkat kesalahan**] yang **sangat rendah**<sup>[1]</sup>.
                - **Koefisien determinasi (R²)** menunjukkan bahwa :green-background[**87.65%**] variasi data **dapat dijelaskan oleh model** yang mengindikasikan **hasil proyeksi akurat**<sup>[2]</sup>.
                """,
                unsafe_allow_html=True,
            )

            st.success("✅ Model **LAYAK** untuk memproyeksikan NDVI 2029!")
            st.success(
                "✅ Data proyeksi NDVI 2029 **VALID** untuk memprediksi LST 2029!"
            )

    st.badge(
        "**Perbandingan Visual Peta NDVI Aktual dan Proyeksi**",
        color="primary",
    )

    col_peta_perbandingan = st.columns(1)
    with col_peta_perbandingan[0]:
        with st.container(border=True):
            try:
                with st.spinner("Memuat plot..."):
                    # Aktual NDVI 2024
                    data_2024_actual_raw = load_image_from_url(
                        PLOT_VIZ_URLS["ndvi_2024"]
                    )
                    if data_2024_actual_raw is not None:
                        data_2024_actual = rgba_to_classification_ndvi(
                            data_2024_actual_raw
                        )
                        data_2024_actual = np.flipud(data_2024_actual)  # Flip Orientasi
                    else:
                        st.error("Gagal memuat data aktual NDVI 2024")
                        st.stop()

                    # Prediksi NDVI 2024
                    data_2024_pred_raw = load_image_from_url(
                        PLOT_VIZ_URLS["ndvi_2024a"]
                    )
                    if data_2024_pred_raw is not None:
                        data_2024_pred = rgba_to_classification_ndvi(data_2024_pred_raw)
                        data_2024_pred = np.flipud(data_2024_pred)
                    else:
                        st.error("Gagal memuat data proyeksi NDVI 2024")
                        st.stop()

                    # Prediksi NDVI 2029
                    data_2029_pred_raw = load_image_from_url(PLOT_VIZ_URLS["ndvi_2029"])
                    if data_2029_pred_raw is not None:
                        data_2029_pred = rgba_to_classification_ndvi(data_2029_pred_raw)
                        data_2029_pred = np.flipud(data_2029_pred)
                    else:
                        st.error("Gagal memuat data proyeksi NDVI 2029")
                        st.stop()

                colorscale = [
                    [0.0, "rgb(139, 0, 0)"],
                    [0.33, "rgb(255, 255, 224)"],
                    [0.67, "rgb(144, 238, 144)"],
                    [1.0, "rgb(0, 100, 0)"],
                ]

                fig = make_subplots(
                    rows=1,
                    cols=3,
                    subplot_titles=[
                        "Aktual NDVI 2024",
                        "Proyeksi NDVI 2024",
                        "Proyeksi NDVI 2029",
                    ],
                    horizontal_spacing=0.08,
                )

                fig.add_trace(
                    go.Heatmap(
                        z=data_2024_actual,
                        colorscale=colorscale,
                        zmin=0,
                        zmax=3,
                        showscale=False,
                        hovertemplate="<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

                fig.add_trace(
                    go.Heatmap(
                        z=data_2024_pred,
                        colorscale=colorscale,
                        zmin=0,
                        zmax=3,
                        showscale=False,
                        hovertemplate="<extra></extra>",
                    ),
                    row=1,
                    col=2,
                )

                fig.add_trace(
                    go.Heatmap(
                        z=data_2029_pred,
                        colorscale=colorscale,
                        zmin=0,
                        zmax=3,
                        showscale=False,
                        hovertemplate="<extra></extra>",
                    ),
                    row=1,
                    col=3,
                )

                legend_data = [
                    {
                        "name": "Sangat Rendah",
                        "color": "rgb(139, 0, 0)",
                    },
                    {
                        "name": "Rendah",
                        "color": "rgb(255, 255, 224)",
                    },
                    {
                        "name": "Sedang",
                        "color": "rgb(144, 238, 144)",
                    },
                    {
                        "name": "Tinggi",
                        "color": "rgb(0, 100, 0)",
                    },
                ]

                for i, legend_item in enumerate(legend_data):
                    fig.add_trace(
                        go.Scatter(
                            x=[None],
                            y=[None],
                            mode="markers",
                            marker=dict(
                                size=11, color=legend_item["color"], symbol="square"
                            ),
                            name=legend_item["name"],
                            showlegend=True,
                            hovertemplate="<extra></extra>",
                        )
                    )

                fig.update_layout(
                    height=512.5,
                    showlegend=True,
                    font=dict(family="Poppins, sans-serif", size=12, color="black"),
                    plot_bgcolor="#fdfaf6",
                    paper_bgcolor="#fdfaf6",
                    margin=dict(l=50, r=50, t=50, b=100),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        bgcolor="rgba(0,0,0,0)",
                        bordercolor="rgba(0,0,0,0)",
                        borderwidth=0,
                        font=dict(size=12, color="black"),
                    ),
                )

                for i in range(1, 4):
                    fig.update_xaxes(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        row=1,
                        col=i,
                        tickfont=dict(size=12, color="black"),
                        title_font=dict(size=12, color="black"),
                    )
                    fig.update_yaxes(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        row=1,
                        col=i,
                        tickfont=dict(size=12, color="black"),
                        title_font=dict(size=12, color="black"),
                    )

                for annotation in fig.layout.annotations:
                    annotation.font.size = 12
                    annotation.font.color = "black"

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback

                st.error(f"Traceback: {traceback.format_exc()}")

    st.badge(
        "**Tabel Perbandingan Sampel Nilai NDVI Aktual dan Proyeksi**",
        color="primary",
    )

    col_sampel_perbandingan = st.columns(1)
    with col_sampel_perbandingan[0]:
        csv_path = "csv/ndviSampelModel.csv"

        try:
            df = pd.read_csv(csv_path)

            def format_ndvi_value(value):
                try:
                    return f"{float(value):.3f}"
                except:
                    return str(value)

            def convert_df_to_html_ndvi(input_df):
                formatters = {}
                for col in input_df.columns:
                    if (
                        "ndvi" in col.lower()
                        or "aktual" in col.lower()
                        or "proyeksi" in col.lower()
                    ):
                        formatters[col] = format_ndvi_value

                return input_df.to_html(
                    escape=False,
                    formatters=formatters,
                    table_id="ndvi-sample-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html_ndvi(df)

            st.markdown(
                """
                <style>
                #ndvi-sample-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 0px 0 10px 0; 
                    font-family: 'Poppins', sans-serif;
                    margin-top: -15px;
                    margin-bottom: 15px;
                }
                #ndvi-sample-table th, #ndvi-sample-table td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: center; 
                    vertical-align: middle; 
                    font-size: 14px;
                }
                #ndvi-sample-table th { 
                    background-color: #E4EFE7; 
                    font-weight: bold; 
                    color: #333;
                }
                #ndvi-sample-table td:not(:first-child) {
                    font-family: 'Courier New', monospace;
                }
                .stContainer > div > div > div > div { 
                    padding-top: 0rem !important; 
                }
                </style>
                <div style="margin-top: -25px;"></div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(html_table, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error(f"File '{csv_path}' tidak ditemukan!")
        except Exception as e:
            st.error(f"Error dalam menampilkan tabel sampel NDVI: {str(e)}")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
            - [1] Nurdin, Suarna, N., Prihartono, W. (2025). Algoritma Regresi Linier untuk Prediksi Penggunaan Volume Air Berdasarkan Jenis Pelanggan PDAM. *Jurnal Kecerdasan Buatan dan Teknologi Informasi*, 4(1). 43-52. https://doi.org/10.69916/jkbti.v4i1.187
            - [2] Man, A., Chaichana, C., Wicharuck, S., Rinchumphu, D. (2022). *Predicting Sunlight Availability for Vertical Shelves using Simulation*. *IOP Conference Series: Earth and Environmental Science*. 1094 012011. https://doi.org/10.1088/1755-1315/1094/1/012011
            """
        )
