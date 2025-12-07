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
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    confusion_matrix,
    cohen_kappa_score,
)
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="Penutup Lahan — Spatify",
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
    # div[data-testid="stVerticalBlockBorderWrapper"] {
    #     padding: 12px !important;
    # }
    # div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
    #     border: 0.5px solid rgba(0, 0, 0, 0.1) !important;
    #     border-radius: 1px !important;
    #     padding: 12px !important;
    #     # box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
    #     # background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
    #     transition: all 0.3s ease !important;
    # }
    # div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
    #     transform: translateY(-4px) !important;
    #     box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important; # Shadow Hover
    #     border-color: #fdfaf6 !important;
    # }     
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

PL_IMAGE_BOUNDS = {
    "1999": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2004": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2009": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2014": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2019": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2024": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
    "2029": [[-7.94631734026, 110.215739513], [-7.54099748407, 110.521346373]],
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
@st.cache_data(ttl=3600)
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


@st.cache_data(ttl=3600)
def load_aoi_data():
    """
    Load CSV Statistik Penutup Lahan di AOI (KPY dan Sekitarnya).
    """
    csv_path = "./csv/luasPenutupLahanAOI.csv"
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return pd.DataFrame()
        return df
    except:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_kec_data():
    """
    Load CSV Statistik Penutup Lahan tiap Kecamatan.
    """
    csv_path = "./csv/luasPenutupLahanKec.csv"
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        st.error(f"File CSV tidak ditemukan: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error membaca file CSV: {str(e)}")
        return pd.DataFrame()


def get_region_type(wadmkk):
    """
    Penentuan Istilah Kapanewon/Kemantren Berdasarkan Kabupaten/Kota (WADMKK).
    """
    if "Bantul" in wadmkk or "Sleman" in wadmkk:
        return "Kapanewon"
    elif "Yogyakarta" in wadmkk:
        return "Kemantren"
    else:
        return ""


@st.cache_data(ttl=3600)
def get_aoi_by_year(df, year):
    """
    Filter Penutup Lahan AOI Berdasarkan Tahun.
    """
    if df is None or df.empty:
        return {}

    year_to_index = {
        "1999": 0,
        "2004": 1,
        "2009": 2,
        "2014": 3,
        "2019": 4,
        "2024": 5,
        "2029": 6,
    }

    if year not in year_to_index:
        return {}

    row_index = year_to_index[year]

    if row_index >= len(df):
        return {}

    row_data = df.iloc[row_index]

    return {
        "vegetasi_pct": row_data.get("vegetasi_pct", 0),  # pct adalah persentase
        "tubuh_air_pct": row_data.get("tubuh_air_pct", 0),
        "lahan_terbangun_pct": row_data.get("lahan_terbangun_pct", 0),
        "lahan_terbuka_pct": row_data.get("lahan_terbuka_pct", 0),
        "vegetasi_km2": row_data.get("vegetasi_km2", 0),
        "tubuh_air_km2": row_data.get("tubuh_air_km2", 0),
        "lahan_terbangun_km2": row_data.get("lahan_terbangun_km2", 0),
        "lahan_terbuka_km2": row_data.get("lahan_terbuka_km2", 0),
        "total_luas_km2": row_data.get("total_luas_km2", 791.07),
    }


@st.cache_data(ttl=3600)
def get_kec_by_year_name(df, year, namobj):
    """
    Filter Penutup Lahan Kecamatan Berdasarkan Tahun dan Nama.
    """
    if df.empty or not namobj:
        return {}

    filtered_data = df[(df["Tahun"] == int(year)) & (df["NAMOBJ"] == namobj)]

    if filtered_data.empty:
        return {}

    row_data = filtered_data.iloc[0]

    return {
        "vegetasi_pct": row_data.get("vegetasi_pct", 0),
        "tubuh_air_pct": row_data.get("tubuh_air_pct", 0),
        "lahan_terbangun_pct": row_data.get("lahan_terbangun_pct", 0),
        "lahan_terbuka_pct": row_data.get("lahan_terbuka_pct", 0),
        "wadmkk": row_data.get("WADMKK", ""),
    }


@st.cache_data(ttl=3600)
def get_kec_list(df):
    """
    Get List Nama Kecamatan Berdasarkan NAMOBJ.
    """
    if df is None or df.empty:
        return []

    return sorted(df["NAMOBJ"].unique().tolist())


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


def add_legend(map_obj):
    """
    Menambahkan Legenda Penutup Lahan ke Peta Folium.
    """
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; 
                right: 10px; 
                z-index: 1000; 
                background-color: white; 
                border: 1px solid #ccc; 
                border-radius: 3px; 
                padding: 10px; 
                font-family: 'Poppins', sans-serif; 
                font-size: 12px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                min-width: 160px;">
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Kelas Penutup Lahan</div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #294b29; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Vegetasi</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #69c3dd; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Tubuh Air</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #cd9a4d; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Lahan Terbangun</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #faf5d9; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Lahan Terbuka</span>
            </div>
        </div>
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))


@st.cache_data(ttl=3600)
def load_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return np.array(img)
    except Exception as e:
        st.error(f"Error loading image from {url}: {str(e)}")
        return None


def rgba_to_classification(rgba_array):
    if rgba_array is None:
        return None

    height, width, _ = rgba_array.shape
    classified = np.full((height, width), np.nan, dtype=np.float32)

    colors_rgb = {
        (41, 75, 41): 0,
        (105, 195, 221): 1,
        (205, 154, 77): 2,
        (250, 245, 217): 3,
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


def add_tiles_to_map(map_obj, year):
    try:
        tiles_url = f"https://pramithadi.github.io/spatify2tiles/pl/{year}/{{z}}/{{x}}/{{y}}.png"

        folium.TileLayer(
            tiles=tiles_url,
            attr=f"Penutup Lahan {year}",
            name=f"Penutup Lahan {year}",
            overlay=True,
            control=True,
            show=True,
            min_zoom=10,
            max_zoom=13,
            opacity=1.0,
        ).add_to(map_obj)
        return True
    except Exception as e:
        st.error(f"Error menambahkan tiles ke peta: {e}")
        return False


def load_all_map_data():
    # 1. Load Data AOI
    df_aoi = load_aoi_data()

    # 2. Load Data Kecamatan
    df_kec = load_kec_data()

    # 3. Load GeoJSON
    shapefile_path = "shp/aoi_kpy.json"
    geojson_data = None
    if os.path.exists(shapefile_path):
        geojson_data = load_and_prep_geojson(shapefile_path)
    else:
        st.warning(f"File SHP tidak ditemukan: {shapefile_path}")

    return {
        "df_aoi": df_aoi,
        "df_kec": df_kec,
        "geojson_data": geojson_data,
    }


@st.cache_resource(ttl=3600)
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


@st.cache_data(ttl=3600)
def generate_quick_insight(penutup_lahan_df):
    """
    Menambahkan Quick Insight Berdasarkan DataFrame.
    """
    data_1999 = penutup_lahan_df.iloc[0]
    data_2024 = penutup_lahan_df.iloc[5]
    data_2029 = penutup_lahan_df.iloc[6]

    def calculate_percentage_change(old_value, new_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    # Menghitung Perubahan Historis (1999-2024)
    pct_change_vegetasi_hist = calculate_percentage_change(
        data_1999["vegetasi_km2"], data_2024["vegetasi_km2"]
    )
    pct_change_terbangun_hist = calculate_percentage_change(
        data_1999["lahan_terbangun_km2"], data_2024["lahan_terbangun_km2"]
    )
    pct_change_terbuka_hist = calculate_percentage_change(
        data_1999["lahan_terbuka_km2"], data_2024["lahan_terbuka_km2"]
    )
    pct_change_tubuh_air_hist = calculate_percentage_change(
        data_1999["tubuh_air_km2"], data_2024["tubuh_air_km2"]
    )

    # Menghitung Perubahan Prediksi (2024-2029)
    pct_change_vegetasi_pred = calculate_percentage_change(
        data_2024["vegetasi_km2"], data_2029["vegetasi_km2"]
    )
    pct_change_terbangun_pred = calculate_percentage_change(
        data_2024["lahan_terbangun_km2"], data_2029["lahan_terbangun_km2"]
    )
    pct_change_terbuka_pred = calculate_percentage_change(
        data_2024["lahan_terbuka_km2"], data_2029["lahan_terbuka_km2"]
    )
    pct_change_tubuh_air_pred = calculate_percentage_change(
        data_2024["tubuh_air_km2"], data_2029["tubuh_air_km2"]
    )

    def get_trend_description(
        change_pct, area_2024, area_2029, trend_type="diprediksi"
    ):
        if change_pct > 0:
            return f"{trend_type} akan **naik {change_pct:.0f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        elif change_pct < 0:
            return f"{trend_type} akan **turun {abs(change_pct):.0f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        else:
            return f"{trend_type} akan **stabil** di **{area_2024:.1f} km²** pada tahun 2029"

    markdown_tren = f"""
    💡 **Quick Insight**\n
    - **Vegetasi**: Mengalami penurunan terbesar sekitar :green-background[**{abs(pct_change_vegetasi_hist):.0f}%**], dari :green-background[**{data_1999['vegetasi_km2']:.1f} km²**] (1999) menjadi :green-background[**{data_2024['vegetasi_km2']:.1f} km²**] (2024), dan diprediksi akan terus menyusut.
    - **Tubuh Air** dan **Lahan Terbuka**: Keduanya juga menunjukkan **tren penurunan** dalam jangka panjang.
    - **Lahan Terbangun**: Satu-satunya kelas yang naik secara masif sebesar :green-background[**{pct_change_terbangun_hist:.0f}%**] dari :green-background[**{data_1999['lahan_terbangun_km2']:.1f} km²**] (1999) menjadi :green-background[**{data_2024['lahan_terbangun_km2']:.1f} km²**] (2024), dan diprediksi akan terus berekspansi hingga :green-background[**{data_2029['lahan_terbangun_km2']:.1f} km²**] pada tahun 2029.
    """

    return markdown_tren


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

st.header("Penutup Lahan")
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
with tab1:
    if "map_data_loaded" not in st.session_state:
        with st.spinner("Mempersiapkan data peta..."):
            map_data = load_all_map_data()
            st.session_state.map_data = map_data
            st.session_state.map_data_loaded = True

    map_data = st.session_state.get("map_data", {})

    df_aoi = map_data.get("df_aoi")
    df_kec = map_data.get("df_kec")
    geojson_data = map_data.get("geojson_data")

    st.badge(
        "**Peta Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )

    col1_peta, col2_peta = st.columns([2.6, 1.4])
    with col2_peta:
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = get_aoi_by_year(df_aoi, option)

        with st.container(border=True):
            list_kec = get_kec_list(df_kec)

            selected_kecamatan = st.selectbox(
                "**Cari Kecamatan**",
                [""] + list_kec,
                index=0,
                placeholder="Ketik atau pilih kecamatan",
            )

        # Disclaimer untuk peta tahun 2004. Hanya muncul jika belum memilih kecamatan.
        if option == "2004" and (not selected_kecamatan or selected_kecamatan == ""):
            with st.container(border=True):
                st.write("⚠️ **Quick Note**")
                st.warning(
                    ""
                    "Peta tahun 2004 berasal dari citra Landsat 7 ETM+ yang mengalami kegagalan ***Scan Line Corrector* (SLC-*off*)** sejak 31 Mei 2003. Hal tersebut menyebabkan adanya **pola garis-garis (*striping*)** di beberapa bagian citra. Fenomena ini merupakan **keterbatasan data asli dari sensor** dan bukan kesalahan pada proses pengolahan data maupun visualisasi. Meskipun demikian, menurut **USGS**, **citra Landsat 7 tetap dapat digunakan** untuk analisis selama interpretasi dilakukan dengan mempertimbangkan keterbatasan tersebut."
                    ""
                )

        # Container Quick Insight
        if selected_kecamatan:
            with st.container(border=True):
                st.write("💡 **Quick Insight**")

                kec_data = get_kec_by_year_name(df_kec, option, selected_kecamatan)

                if kec_data:
                    jenis_kec = get_region_type(kec_data["wadmkk"])

                    st.write(
                        f"Persentase penutup lahan di :green-background[**{jenis_kec} {selected_kecamatan}**] pada tahun :green-background[**{option}**] yakni:"
                    )
                    st.write(f"• **Vegetasi**: {kec_data['vegetasi_pct']:.2f}%")
                    st.write(f"• **Tubuh Air**: {kec_data['tubuh_air_pct']:.2f}%")
                    st.write(
                        f"• **Lahan Terbangun**: {kec_data['lahan_terbangun_pct']:.2f}%"
                    )
                    st.write(
                        f"• **Lahan Terbuka**: {kec_data['lahan_terbuka_pct']:.2f}%"
                    )

                    # Kesimpulan
                    classes_kec = {
                        "vegetasi": kec_data["vegetasi_pct"],
                        "tubuh air": kec_data["tubuh_air_pct"],
                        "lahan terbangun": kec_data["lahan_terbangun_pct"],
                        "lahan terbuka": kec_data["lahan_terbuka_pct"],
                    }
                    dominan_kec = max(classes_kec, key=classes_kec.get)

                    # Pengkondisian untuk Tahun 2029
                    if str(option) == "2029":
                        st.write(
                            f"**Kesimpulan**: {jenis_kec} {selected_kecamatan} **diprediksi** akan **didominasi** oleh :green-background[**{dominan_kec}**]."
                        )
                    else:
                        st.write(
                            f"**Kesimpulan**: {jenis_kec} {selected_kecamatan} **didominasi** oleh :green-background[**{dominan_kec}**]."
                        )
                else:
                    st.write(
                        "Data tidak tersedia untuk kecamatan dan tahun yang dipilih."
                    )

    with col1_peta:
        map_center = [-7.764326411862208, 110.3721676814108]
        zoom_level = 10.5

        if selected_kecamatan:
            kec_bounds = get_kecamatan_bounds_static(selected_kecamatan)
            if kec_bounds:
                center_lat = (kec_bounds[0][0] + kec_bounds[1][0]) / 2
                center_lon = (kec_bounds[0][1] + kec_bounds[1][1]) / 2
                map_center = [center_lat, center_lon]
                zoom_level = 13

        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles="OpenStreetMap",
        )

        folium.TileLayer(tiles="CartoDB positron", name="CartoDB Positron").add_to(m)

        tiles_success = add_tiles_to_map(m, option)
        if not tiles_success:
            st.info(
                "⏳ Menampilkan peta tanpa layer Penutup Lahan. Silakan *refresh* Spatify!"
            )

        add_shp_to_map(m, geojson_data)

        try:
            add_legend(m)
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
    if df_aoi is None or df_aoi.empty:
        st.error("Data tidak tersedia")
        st.stop()

    years = [1999, 2004, 2009, 2014, 2019, 2024, 2029]
    tren_data = []

    for year in years:
        year_data = get_aoi_by_year(df_aoi, str(year))
        if year_data:
            tren_data.append(
                {
                    "Tahun": year,
                    "Vegetasi": year_data["vegetasi_pct"],
                    "Tubuh Air": year_data["tubuh_air_pct"],
                    "Lahan Terbangun": year_data["lahan_terbangun_pct"],
                    "Lahan Terbuka": year_data["lahan_terbuka_pct"],
                    "Vegetasi_km2": year_data["vegetasi_km2"],
                    "Tubuh Air_km2": year_data["tubuh_air_km2"],
                    "Lahan Terbangun_km2": year_data["lahan_terbangun_km2"],
                    "Lahan Terbuka_km2": year_data["lahan_terbuka_km2"],
                }
            )

    tren_df = pd.DataFrame(tren_data)

    st.badge(
        "**Tren Perubahan Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2.3, 1.7])

    with col1_tren_main:
        # Container Grafik Tren
        with st.container(border=True):
            # Membuat Grafik
            fig = go.Figure()
            colors = {
                "Vegetasi": "#294b29",
                "Tubuh Air": "#69c3dd",
                "Lahan Terbangun": "#cd9a4d",
                "Lahan Terbuka": "#aaa68f",
            }

            # Tambahkan Line
            for kelas, color in colors.items():
                fig.add_trace(
                    go.Scatter(
                        x=tren_df["Tahun"],
                        y=tren_df[kelas],
                        mode="lines+markers",
                        name=kelas,
                        line=dict(color=color, width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate=f"<b>{kelas}</b><br>Tahun: %{{x}}<br>Luas: %{{customdata:.1f}} km²<br>Persentase: %{{y:.1f}}%<extra></extra>",
                        customdata=tren_df[f"{kelas}_km2"],
                    )
                )

            fig.add_vline(
                x=2024,
                line_width=2,
                line_dash="dash",
                line_color="grey",
                annotation_text="Prediksi",
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
                        text="Persentase (%)",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    gridcolor="#9A9A9A",
                    zerolinecolor="#9A9A9A",
                    range=[0, 100],
                    dtick=20,  # Interval
                    tickvals=list(range(0, 101, 20)),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=20, r=20, t=20, b=80),
                height=319,
                font=dict(family="Poppins", size=12),
            )

            # Menampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(generate_quick_insight(df_aoi))

# ==============================================================================
# SECTION 3: VALIDASI
# ==============================================================================


# Fungsi untuk Membuat Matriks Konfusi
def create_confusion_matrix(df):
    y_true = df["PL Klasifikasi"]
    y_pred = df["PL Aktual"]
    classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]

    classes = [cls for cls in classes if cls in y_true.values or cls in y_pred.values]

    cm = confusion_matrix(y_true, y_pred, labels=classes)
    n_total = np.sum(cm)
    row_totals = np.sum(cm, axis=1)
    col_totals = np.sum(cm, axis=0)

    # np.divide untuk menghindari error pembagian nol
    producer_acc = (
        np.divide(
            np.diag(cm),
            row_totals,
            out=np.zeros_like(np.diag(cm), dtype=float),
            where=row_totals != 0,
        )
        * 100
    )
    user_acc = (
        np.divide(
            np.diag(cm),
            col_totals,
            out=np.zeros_like(np.diag(cm), dtype=float),
            where=col_totals != 0,
        )
        * 100
    )

    overall_acc = np.sum(np.diag(cm)) / n_total * 100 if n_total > 0 else 0
    kappa = cohen_kappa_score(y_true, y_pred) * 100

    commission_error = 100 - user_acc
    omission_error = 100 - producer_acc

    return {
        "cm": cm,
        "classes": classes,
        "row_totals": row_totals,
        "col_totals": col_totals,
        "producer_acc": producer_acc,
        "user_acc": user_acc,
        "commission_error": commission_error,
        "omission_error": omission_error,
        "overall_acc": overall_acc,
        "kappa": kappa,
        "n_total": n_total,
    }


# Fungsi untuk Menampilkan Matriks Konfusi dalam Format Tabel HTML
def display_confusion_matrix_html(results):
    cm, classes = results["cm"], results["classes"]
    row_totals, col_totals = results["row_totals"], results["col_totals"]
    producer_acc, user_acc = results["producer_acc"], results["user_acc"]
    commission_error, omission_error = (
        results["commission_error"],
        results["omission_error"],
    )
    overall_acc, kappa, n_total = (
        results["overall_acc"],
        results["kappa"],
        results["n_total"],
    )

    html_content = """
    <style>
    .conf-matrix {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif; font-size: 13px; border: 2px solid #333; }}
    .conf-matrix th {{ background: #E4EFE7; border: 1px solid #333; padding: 10px 6px; text-align: center; font-weight: bold; color: #333; }}
    .conf-matrix td {{ border: 1px solid #333; padding: 8px 6px; text-align: center; background: white; }}
    .conf-matrix .header-main {{ background: #E4EFE7; font-weight: bold; color: #333; }}
    .conf-matrix .diagonal {{ background: #3c5e51; color: white; font-weight: bold; }}
    .conf-matrix .important {{ background: #3c5e51; color: white; font-weight: bold; }}
    </style>
    <table class="conf-matrix">
        <thead>
            <tr>
                <th rowspan="2" class="header-main">Data Hasil<br/>Klasifikasi</th>
                <th colspan="{num_classes}" class="header-main">Data Uji Klasifikasi</th>
                <th rowspan="2" class="header-main">Total<br/>Baris</th>
                <th rowspan="2" class="header-main">Producer<br/>Accuracy<br/>(%)</th>
                <th rowspan="2" class="header-main">Kesalahan<br/>Omisi<br/>(%)</th>
            </tr>
            <tr>
    """.format(
        num_classes=len(classes)
    )

    for cls in classes:
        html_content += f'<th class="header-main">{cls}</th>'
    html_content += "</tr></thead><tbody>"

    for i, cls in enumerate(classes):
        html_content += f'<tr><td class="header-main">{cls}</td>'
        for j in range(len(classes)):
            cell_class = "diagonal" if i == j else ""
            html_content += f'<td class="{cell_class}">{cm[i][j]}</td>'
        html_content += f"""
            <td>{row_totals[i]}</td>
            <td>{producer_acc[i]:.1f}</td>
            <td>{omission_error[i]:.1f}</td>
        </tr>"""

    html_content += '<tr><td class="header-main">Total Kolom</td>'
    for total in col_totals:
        html_content += f"<td>{total}</td>"
    html_content += f"<td>{n_total}</td><td>-</td><td>-</td></tr>"

    html_content += '<tr><td class="header-main">User Accuracy (%)</td>'
    for acc in user_acc:
        html_content += f"<td>{acc:.1f}</td>"
    html_content += "<td>-</td><td>-</td><td>-</td></tr>"

    html_content += '<tr><td class="header-main">Kesalahan Komisi (%)</td>'
    for error in commission_error:
        html_content += f"<td>{error:.1f}</td>"
    html_content += "<td>-</td><td>-</td><td>-</td></tr>"

    html_content += f"""
        <tr>
            <td class="header-main"><strong>Overall Accuracy</strong></td>
            <td colspan="{len(classes)}" class="important">{overall_acc:.2f}%</td>
            <td>-</td><td>-</td><td>-</td>
        </tr>
        <tr>
            <td class="header-main"><strong>Kappa Accuracy</strong></td>
            <td colspan="{len(classes)}" class="important">{kappa:.2f}%</td>
            <td>-</td><td>-</td><td>-</td>
        </tr>
    </tbody></table>"""
    return html_content


# Fungsi untuk Encode Gambar ke Base64
def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None


# Fungsi untuk Menampilkan Matriks Konfusi dan Tabel Sampel
def display_validation_content(year):
    csv_path = f"csv/validasiPL{year}.csv"

    with st.container(border=True):
        st.write(f"**Matriks Konfusi Penutup Lahan {year}**")
        try:
            df = pd.read_csv(csv_path)
            results = create_confusion_matrix(df)
            html_matrix = display_confusion_matrix_html(results)
            st.markdown(html_matrix, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error(f"File '{csv_path}' tidak ditemukan!")
        except Exception as e:
            st.error(f"Error dalam membuat matriks konfusi: {str(e)}")


with tab3:
    st.badge(
        "**Uji Akurasi Penutup Lahan Kawasan Perkotaan Yogyakarta dan Sekitarnya**",
        color="primary",
    )

    selected_year = st.pills(
        "**Lihat Tahun:**",
        ["2014", "2019", "2024"],
        selection_mode="single",
        default="2014",
    )

    if selected_year:
        display_validation_content(selected_year)

# ==============================================================================
# SECTION 4: MODEL
# ==============================================================================

with tab4:
    st.badge(
        "**Evaluasi Model XGBoost Terintegrasi dengan Cellular Automata-Markov Chain untuk Prediksi Penutup Lahan**",
        color="primary",
    )

    col1_metrik_img, col2_metrik_insight = st.columns([1.9, 2.1])
    with col1_metrik_img:
        with st.container(border=True):
            fig = go.Figure(
                data=[
                    go.Bar(
                        name="Akurasi Keseluruhan",
                        x=["Akurasi Keseluruhan"],
                        y=[0.8941],
                        text=["0.8941"],
                        textposition="outside",
                        marker_color="#1C352D",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="Koefisien Kappa",
                        x=["Koefisien Kappa"],
                        y=[0.8324],
                        text=["0.8324"],
                        textposition="outside",
                        marker_color="#F5C9B0",
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
                    "y": -0.2,
                    "xanchor": "center",
                    "x": 0.5,
                    "font": {"family": "Poppins", "size": 12, "color": "black"},
                },
                font={"family": "Poppins"},
                # plot_bgcolor="#fdfaf6",
                # paper_bgcolor="#fdfaf6",
                margin=dict(l=70, r=50, t=20, b=30),
                height=241,
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
                - Model prediksi penutup lahan menunjukkan **akurasi tinggi** sebesar :green-background[**89.41%**] setelah divalidasi dengan data aktual terkini.
                - Koefisien kappa sebesar :green-background[**83.24%**] masuk ke dalam kategori *almost perfect agreement* yang menunjukkan tingkat kesepakatan **sangat baik**<sup>[1]</sup>.
                """,
                unsafe_allow_html=True,
            )
            st.success("✅ Model **LAYAK** untuk memprediksi penutup lahan tahun 2029.")

    # Baris Kosong
    st.write("")

    st.badge(
        "**Classification Report**",
        color="primary",
    )
    col2_classification_report, col2_report_insight = st.columns([2.285, 1.715])
    with col2_classification_report:
        with st.container(border=True):
            classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]
            precision = [0.84, 0.30, 0.72, 0.44]
            recall = [0.92, 0.43, 0.82, 0.08]
            f1_score = [0.88, 0.35, 0.77, 0.14]

            colors = {
                "precision": "#1C352D",
                "recall": "#A6B28B",
                "f1_score": "#F5C9B0",
            }

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    name="Precision",
                    x=classes,
                    y=precision,
                    text=[f"{val:.2f}" for val in precision],
                    textposition="outside",
                    marker_color=colors["precision"],
                    textfont=dict(family="Poppins", size=12, color="black"),
                )
            )

            fig.add_trace(
                go.Bar(
                    name="Recall",
                    x=classes,
                    y=recall,
                    text=[f"{val:.2f}" for val in recall],
                    textposition="outside",
                    marker_color=colors["recall"],
                    textfont=dict(family="Poppins", size=12, color="black"),
                )
            )

            fig.add_trace(
                go.Bar(
                    name="F1-Score",
                    x=classes,
                    y=f1_score,
                    text=[f"{val:.2f}" for val in f1_score],
                    textposition="outside",
                    marker_color=colors["f1_score"],
                    textfont=dict(family="Poppins", size=12, color="black"),
                )
            )

            fig.update_layout(
                xaxis={
                    "title": {
                        "text": "Kelas Penutup Lahan",
                        "font": {"family": "Poppins", "size": 12, "color": "black"},
                    },
                    "tickfont": {"family": "Poppins", "size": 12, "color": "black"},
                },
                yaxis={
                    "title": {
                        "text": "Skor",
                        "font": {"family": "Poppins", "size": 12, "color": "black"},
                    },
                    "tickfont": {"family": "Poppins", "size": 12, "color": "black"},
                    "range": [0, 1],
                },
                legend={
                    "orientation": "h",
                    "yanchor": "top",
                    "y": -0.20,
                    "xanchor": "center",
                    "x": 0.5,
                    "font": {"family": "Poppins", "size": 12, "color": "black"},
                },
                font={"family": "Poppins"},
                # plot_bgcolor="#fdfaf6",
                # paper_bgcolor="#fdfaf6",
                margin=dict(l=40, r=40, t=40, b=80),
                showlegend=True,
                barmode="group",
                height=413,
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")

            st.plotly_chart(fig, use_container_width=True)

    with col2_report_insight:
        with st.container(border=True):
            with st.expander("🧰 **Quick Guide: Metrik Precision, Recall, F1-Score**"):
                st.markdown(
                    f"""
                        - **Precision** menjawab pertanyaan, "Dari semua yang diprediksi sebagai kelas X, berapa persen yang benar?"
                        - **Recall** menjawab pertanyaan, "Dari semua kelas X yang sebenarnya ada, berapa persen yang berhasil ditemukan model?"
                        - **F1-Score** adalah rata-rata gabungan dari Precision dan Recall. Semakin mendekati 1, performa model semakin baik<sup>[2]</sup>.
                    """,
                    unsafe_allow_html=True,
                )

        with st.container(border=True):
            st.write("💡 **Quick Insight**")
            st.markdown(
                f"""
                - Model menunjukkan **performa terbaik** dalam mengidentifikasi kelas **vegetasi** dan **lahan terbangun**. Hal ini dibuktikan dengan nilai **F1-Score tinggi** masing-masing sebesar :green-background[**0.88**] dan :green-background[**0.77**].
                - Sebaliknya, model menunjukkan **performa yang lebih rendah** dalam mengidentifikasi kelas **tubuh air** dan **lahan terbuka**. Nilai **F1-Score rendah** menunjukkan model kesulitan membedakan kedua kelas tersebut. Hal ini dapat disebabkan oleh :green-background[**keterbatasan sampel training**] atau :green-background[**kemiripan spektral**] dengan kelas lain.
                """,
                unsafe_allow_html=True,
            )

    # Baris Kosong
    st.write("")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
            - [1] Viera, A. J., & Garrett, J. M. (2005). Understanding Interobserver Agreement: The Kappa Statistic. *Family Medicine*, 37(5). 360-363.
            - [2] Bobbitt, Z. (2022). *How to Interpret the Classification Report in sklearn (With Example)*. (*https://www.statology.org/sklearn-classification-report/,* diakses 19 Agustus 2025).
            """
        )
