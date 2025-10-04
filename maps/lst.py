from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap, Normalize
import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
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
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    confusion_matrix,
    cohen_kappa_score,
)

st.set_page_config(
    page_title="LST — Spatify",
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

# Dictionary Statistik LST
stats_dict = {
    "1999": {"min": 4.313, "max": 69.760, "mean": 34.531},
    "2004": {"min": 15.295, "max": 57.402, "mean": 35.481},
    "2009": {"min": 18.111, "max": 67.161, "mean": 37.745},
    "2014": {"min": 17.684, "max": 52.441, "mean": 36.630},
    "2019": {"min": 18.537, "max": 49.669, "mean": 35.739},
    "2024": {"min": 20.722, "max": 72.317, "mean": 37.262},
    "2029": {
        "min": 22.028,
        "max": 51.675,
        "mean": 38.347,
    },
}

# Dictionary Threshold LST
threshold_dict = {
    "1999": {"low": 30.499, "medium": 34.531, "high": 38.563},
    "2004": {"low": 31.412, "medium": 35.481, "high": 39.550},
    "2009": {"low": 33.243, "medium": 37.745, "high": 42.247},
    "2014": {"low": 32.168, "medium": 36.630, "high": 41.092},
    "2019": {"low": 31.923, "medium": 35.739, "high": 39.556},
    "2024": {"low": 33.207, "medium": 37.262, "high": 41.317},
    "2029": {
        "low": 34.010,
        "medium": 38.347,
        "high": 42.684,
    },
}

LST_IMAGE_BOUNDS = {
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
def load_stats_kec():
    csv_path = "./csv/lstStatsKec.csv"
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
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background-color: white; border: 1px solid #ccc; border-radius: 1px; padding: 10px; font-family: 'Poppins', sans-serif; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); min-width: 160px;">
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Kelas Suhu Permukaan Lahan (°C)</div>
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


def add_tiles_to_map(map_obj, year, thresholds):
    try:
        tiles_url = f"https://pramithadi.github.io/spatify2tiles/lst/{year}/{{z}}/{{x}}/{{y}}.png"

        folium.TileLayer(
            tiles=tiles_url,
            attr=f"Suhu Permukaan Lahan {year}",
            name=f"Suhu Permukaan Lahan {year}",
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


def create_regression_plot(df, x_col, y_col, title, x_label, y_label):
    # Menghapus Data yang Kosong
    clean_data = df[[x_col, y_col]].dropna()

    if len(clean_data) == 0:
        return None, None, None, None

    x = clean_data[x_col].values.reshape(-1, 1)
    y = clean_data[y_col].values

    # Membuat Model Regresi Linier
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)

    # Menghitung R² dan Slope
    r2 = r2_score(y, y_pred)
    slope = model.coef_[0]
    intercept = model.intercept_

    # Menghitung p-value
    correlation, p_value = stats.pearsonr(clean_data[x_col], clean_data[y_col])

    # Membuat Scatter Plot
    fig = px.scatter(
        x=clean_data[x_col],
        y=clean_data[y_col],
        labels={"x": x_label, "y": y_label},
        opacity=0.6,
        color_discrete_sequence=["#1f77b4"],
    )

    # Garis Trend (Memvisualisasikan Hubungan Linear)
    x_range = np.linspace(clean_data[x_col].min(), clean_data[x_col].max(), 100)
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
        height=323.9,
        showlegend=True,
        template="plotly_white",
        font=dict(
            family="Poppins, sans-serif",
            size=12,
            color="black",
        ),
        margin=dict(t=30, b=0, l=20, r=20),
        # Styling Sumbu X dan Y
        xaxis=dict(
            title=dict(
                text=x_label,
                font=dict(color="black", family="Poppins, sans-serif"),
            ),
            tickfont=dict(color="black", family="Poppins, sans-serif"),
        ),
        yaxis=dict(
            title=dict(
                text=y_label,
                font=dict(color="black", family="Poppins, sans-serif"),
            ),
            tickfont=dict(color="black", family="Poppins, sans-serif"),
        ),
        # Styling untuk Legenda
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.47,
            font=dict(family="Poppins, sans-serif", size=14, color="black"),
        ),
    )

    # Box Info - Persamaan Regresi dan R²
    equation = f"y = {slope:.2f}x + {intercept:.2f}<br>R² = {r2:.2f}"
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
        borderpad=7,  # Tambah Padding Internal
        xanchor="left",
        yanchor="top",
    )

    return fig, r2, p_value, slope


def interpret_regression(r2, p_value, slope, x_var):
    # Interpretasi Signifikansi
    if p_value <= 0.001:
        significance = "sangat signifikan"
    elif p_value <= 0.01:
        significance = "signifikan"
    elif p_value <= 0.05:
        significance = "cukup signifikan"
    else:
        significance = "tidak signifikan"

    # Interpretasi R²
    r2_percent = r2 * 100

    # Cek Pengaruh
    is_influential = r2 >= 0.1 and p_value < 0.05

    direction = "peningkatan" if slope > 0 else "penurunan"

    interpretation = f"""
    - **Koefisien determinasi (R²)** menunjukkan bahwa **{x_var}** mampu menjelaskan :green-background[**{r2_percent:.2f}%**] variasi nilai LST, sedangkan {100 - r2_percent:.2f}% sisanya dipengaruhi oleh faktor lain<sup>[1]</sup>.
    - Setiap **kenaikan 1.0 unit nilai {x_var}** berasosiasi dengan **{direction}** LST sebesar :green-background[**{abs(slope):.2f}°C**].
    - Terdapat **hubungan positif yang {significance}** secara statistik antara {x_var} dan LST dibuktikan dengan nilai :green-background[**p-value < {p_value:.3f}**]<sup>[2]</sup>.
    """

    return interpretation, is_influential


@st.cache_data(ttl=3600)
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


def rgba_to_classification(rgba_array):
    """Convert RGBA array to classification values"""
    if rgba_array is None:
        return None

    height, width, _ = rgba_array.shape
    classified = np.full((height, width), np.nan, dtype=np.float32)

    colors_rgb = {
        (92, 160, 211): 0,  # very_low - biru
        (245, 235, 177): 1,  # low - kuning muda
        (219, 167, 88): 2,  # medium - orange
        (147, 34, 14): 3,  # high - merah
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


def load_all_map_data():
    # 1. Load Statistik Kecamatan
    df_kec_stats = load_stats_kec()
    if df_kec_stats is None:
        st.error(
            "Gagal memuat file CSV statistik kecamatan. Pastikan file ada di `csv/lstStatsKec.csv`"
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


@st.cache_resource(ttl=3600)
def create_base_map():
    m = folium.Map(
        location=[-7.764326411862208, 110.3721676814108],
        zoom_start=10.5,
        tiles="OpenStreetMap",
    )

    folium.TileLayer(tiles="CartoDB positron", name="CartoDB Positron").add_to(m)

    return m


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

st.header("Suhu Permukaan Lahan")

(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
) = st.tabs(
    [
        "🗺️ Peta",
        "📈 Tren",
        "✅ Validasi",
        "⚙️ Model",
        "📉 Regresi",
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
    df_kec_stats = map_data.get("df_kec_stats")
    geojson_data = map_data.get("geojson_data")

    st.badge(
        "**Peta LST di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )

    col1_peta, col2_peta = st.columns([2.45, 1.55])
    with col2_peta:
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )
            selected_data = stats_dict[option]

        col1_peta_metric, col2_peta_metric, col3_peta_metric = st.columns([1, 1, 1])
        with col1_peta_metric:
            with st.container(border=True):
                st.metric("LST Min", f"{selected_data['min']:.1f}°C")
        with col2_peta_metric:
            with st.container(border=True):
                st.metric("LST Max", f"{selected_data['max']:.1f}°C")
        with col3_peta_metric:
            with st.container(border=True):
                st.metric("LST Mean", f"{selected_data['mean']:.1f}°C")

        with st.container(border=True):
            kec_year = get_kec_by_year(df_kec_stats, option)
            if kec_year:
                kecamatan_options = list(kec_year.keys())
                selected_kecamatan = st.selectbox(
                    "**Cari Kecamatan**",
                    [""] + kecamatan_options,
                    index=0,
                    placeholder="Ketik atau pilih kecamatan",
                )
            else:
                st.info(
                    f"Menghubungkan dengan data kecamatan untuk tahun {option}. Silakan *refresh* halaman."
                )
                selected_kecamatan = ""

        if selected_kecamatan and selected_kecamatan != "" and kec_year:
            with st.container(border=True):
                st.write("💡 **Quick Insight**")
                kecamatan_data = kec_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)
                if option == "2029":
                    description = f"Suhu permukaan lahan di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] **diprediksi** sebesar :green-background[**{kecamatan_data['mean']:.2f}°C**] dengan suhu terendah yakni :green-background[**{kecamatan_data['min']:.2f}°C**] dan suhu tertinggi adalah :green-background[**{kecamatan_data['max']:.2f}°C**]."
                else:
                    description = f"Suhu permukaan lahan di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] memiliki rata-rata suhu sebesar :green-background[**{kecamatan_data['mean']:.2f}°C**] dengan suhu terendah yakni :green-background[**{kecamatan_data['min']:.2f}°C**] dan suhu tertinggi adalah :green-background[**{kecamatan_data['max']:.2f}°C**]."
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
                zoom_level = 13

        m = folium.Map(
            location=map_center, zoom_start=zoom_level, tiles="OpenStreetMap"
        )

        folium.TileLayer(tiles="CartoDB positron", name="CartoDB Positron").add_to(m)

        thresholds = threshold_dict[option]
        tiles_success = add_tiles_to_map(m, option, thresholds)
        if not tiles_success:
            st.info("Menampilkan peta tanpa layer LST.")

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
    # Grafik Tren LST Perkotaan dan Non-Perkotaan
    df_urban_rural = pd.read_csv("./csv/lstStatsKec.csv")

    lst_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    lst_urban_rural_pivot = lst_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    st.badge(
        "**Tren LST di Kawasan Perkotaan dan Non-Perkotaan Yogyakarta (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2.3, 1.7])
    with col1_tren_main:
        # Container Grafik Tren
        with st.container(border=True):
            # Buat Grafik
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            fig = go.Figure()

            if "Urban" in lst_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=lst_urban_rural_pivot.index,
                        y=lst_urban_rural_pivot["Urban"],
                        mode="lines+markers",
                        name="Perkotaan",
                        line=dict(color="#FF90BB", width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate="<b>Perkotaan</b><br>Tahun: %{x}<br>LST Mean: %{y:.2f}°C<extra></extra>",
                    )
                )

            if "Rural" in lst_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=lst_urban_rural_pivot.index,
                        y=lst_urban_rural_pivot["Rural"],
                        mode="lines+markers",
                        name="Non-Perkotaan",
                        line=dict(color="#096B68", width=3),
                        marker=dict(size=8, symbol="square"),
                        hovertemplate="<b>Non-Perkotaan</b><br>Tahun: %{x}<br>LST Mean: %{y:.2f}°C<extra></extra>",
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
                        text="LST Mean (°C)",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    gridcolor="#9A9A9A",
                    zerolinecolor="#9A9A9A",
                    # range=[22, 40],
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=10, r=10, t=20, b=20),
                height=370,
                font=dict(family="Poppins", size=12),
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Dictionary Mean LST
        mean_by_year = {
            1999: {"mean": 34.531},
            2004: {"mean": 35.481},
            2009: {"mean": 37.745},
            2014: {"mean": 36.630},
            2019: {"mean": 35.739},
            2024: {"mean": 37.262},
            2029: {"mean": 38.347},
        }

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡 **Quick Insight**
                - :green-background[**Kawasan perkotaan**] Yogyakarta secara konsisten menunjukkan suhu permukaan yang **jauh lebih tinggi** dibandingkan :green-background[**kawasan non-perkotaan**] yang menjadi sebuah indikasi dari fenomena *urban heat island*.
                - **Suhu** di kawasan **perkotaan** menunjukkan **tren pemanasan** dalam jangka panjang yang diprediksi akan mencapai puncaknya pada tahun 2029 dengan rata-rata LST sebesar :green-background[**43.54°C**].
                - Meskipun lebih sejuk, kawasan **non-perkotaan** juga tidak luput dari **tren pemanasan** serupa dan diprediksi akan terus meningkat dengan rata-rata LST sebesar :green-background[**37.37°C**] pada tahun 2029.
                """
            )

    # Baris Kosong
    st.write("")

    # Row Diagram Garis & Ranking LST
    st.badge(
        "**Peringkat Kecamatan Berdasarkan Rata-rata LST (1999-2024)**",
        color="primary",
    )

    col_rank = st.columns([1])[0]
    with col_rank:
        df_stats = pd.read_csv("./csv/lstStatsKec.csv")

        # Hitung Rata-rata Mean untuk Setiap Kecamatan dari Semua Tahun
        df_ranking = (
            df_stats.groupby(["NAMOBJ", "WADMKK", "Zona"])["mean"].mean().reset_index()
        )
        df_ranking.columns = ["NAMOBJ", "WADMKK", "Zona", "Mean_LST"]

        # Sort dari Terpanas ke Terdingin
        df_ranking = df_ranking.sort_values("Mean_LST", ascending=False).reset_index(
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

        with st.container(border=True):
            # Buat Bar
            fig = px.bar(
                df_ranking,
                x="Mean_LST",
                y="Y_Label",
                color="Zona",
                color_discrete_map={"Urban": "#FF90BB", "Rural": "#096B68"},
                orientation="h",
                labels={
                    "Mean_LST": "LST Mean (°C)",
                    "Y_Label": "",
                    "Zona": "Kawasan",
                },
                # Isi Hover
                hover_data={"Mean_LST": ":.2f", "Zona": False, "Y_Label": False},
                custom_data=["Zona_Label", "Mean_LST"],
            )

            # Update Hover Template
            fig.update_traces(
                hovertemplate="<b>%{y}</b><br>"
                + "Kawasan: %{customdata[0]}<br>"
                + "LST Mean: %{customdata[1]:.2f}°C<extra></extra>",
                texttemplate="%{x:.2f}°C",
                textposition="outside",
                textfont_size=14,
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
                margin=dict(t=10, b=20),  # Mengurangi Margin Top Supaya Tidak Ada Gap
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
        # Load CSV Sampel LST untuk Validasi
        validation_data = pd.read_csv("csv/lstSampelValidasi.csv")

        # Hapus Nilai NaN
        validation_data = validation_data.dropna()

        # Ekstraksi Nilai dari Field
        lstAktual_values = validation_data["LST Aktual (°C)"].values  # X: Satelit
        lstReferensi_values = validation_data[
            "LST Landsat 8 (°C)"
        ].values  # Y: Lapangan

        # Hitung Metrik Regresi (X = satelit, Y = lapangan)
        slope, intercept, r_value, p_val, std_err = stats.linregress(
            lstAktual_values, lstReferensi_values
        )

        # R-squared (Koefisien Determinasi)
        r_squared = r_value**2

        # RMSE & MAE (Y = referensi, X = prediksi)
        rmse = np.sqrt(mean_squared_error(lstReferensi_values, lstAktual_values))
        mae = mean_absolute_error(lstReferensi_values, lstAktual_values)

        # Buat Persamaan
        if intercept >= 0:
            equation = f"y = {slope:.2f}x + {intercept:.2f}"
        else:
            equation = f"y = {slope:.2f}x - {abs(intercept):.2f}"

        # Row Diagram Garis dan Validasi LST
        st.badge(
            "**Validasi LST Landsat 8 dan LST Pengukuran Lapangan (2024)**",
            color="primary",
        )

        col1_validate, col2_validate = st.columns([2.3, 1.7])
        with col1_validate:
            with st.container(border=True):
                # Buat Scatterplot (X = Satelit, Y = Lapangan)
                fig = px.scatter(
                    x=lstAktual_values,
                    y=lstReferensi_values,
                    labels={"x": "LST Landsat 8 (°C)", "y": "LST Aktual (°C)"},
                    opacity=0.6,
                    color_discrete_sequence=["#1f77b4"],
                )

                # Garis Regresi Linear
                x_range = np.linspace(
                    lstAktual_values.min(), lstAktual_values.max(), 100
                )
                y_regression = slope * x_range + intercept

                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_regression,
                        mode="lines",
                        name="Garis Regresi",
                        line=dict(color="red", width=2),
                    )
                )

                # Update Layout
                fig.update_layout(
                    height=419,
                    showlegend=True,
                    template="plotly_white",
                    font=dict(
                        family="Poppins, sans-serif",
                        size=12,
                        color="black",
                    ),
                    margin=dict(t=30, b=20, l=20, r=20),
                    xaxis=dict(
                        title=dict(
                            text="LST Landsat 8 (°C)",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    yaxis=dict(
                        title=dict(
                            text="LST Aktual (°C)",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    legend={
                        "orientation": "h",
                        "yanchor": "top",
                        "y": -0.22,
                        "xanchor": "center",
                        "x": 0.5,
                        "font": {"family": "Poppins", "size": 14, "color": "black"},
                    },
                )

                # Box Info Persamaan
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
            col1_metric, col2_metric, col3_metric = st.columns([1, 1, 1])

            with col1_metric:
                with st.container(border=True):
                    st.metric(
                        label="R²",
                        value=f"{r_squared:.2f}",
                        help="Koefisien Determinasi (0-1)",
                    )

            with col2_metric:
                with st.container(border=True):
                    st.metric(
                        label="RMSE",
                        value=f"{rmse:.2f}",
                        help="*Root Mean Square Error*",
                    )

            with col3_metric:
                with st.container(border=True):
                    st.metric(
                        label="MAE",
                        value=f"{mae:.2f}",
                        help="*Mean Absolute Error*",
                    )

            # Container Analisis Validasi
            with st.container(border=True):
                st.write("💡 **Quick Insight**")
                st.markdown(
                    f"""
                    - Nilai *error* khususnya MAE (1.70°C) masih berada dalam **batas yang dapat diterima** karena toleransi kesalahan pada pemodelan LST adalah :green-background[**± 2°C**]<sup>[1]</sup>.
                    - Sebanyak :green-background[**75%**] variasi LST aktual **dapat dijelaskan** oleh LST Landsat 8 yang menunjukkan **hubungan cukup kuat** (:green-background[**r = 0.87**])<sup>[2]</sup>.
                """,
                    unsafe_allow_html=True,
                )

                # Status Validasi
                st.success("✅ VALID! Data LST layak digunakan.")

    except FileNotFoundError:
        st.error("❌ File 'csv/lstSampelValidasi.csv' tidak ditemukan!")
        st.info(
            "Pastikan file CSV hasil sampling sudah tersedia dengan kolom 'LST Aktual' dan 'LST Referensi'"
        )

    except Exception as e:
        st.error(f"❌ Error dalam memproses data: {str(e)}")
        st.info(
            "Periksa format file CSV dan nama kolom ('LST Aktual' dan 'LST Referensi')"
        )

    # Baris Kosong
    st.write("")

    st.badge(
        "**Tabel Perbandingan Nilai LST Landsat 8 dan LST Aktual**",
        color="primary",
    )

    col_sampel_perbandingan = st.columns(1)
    with col_sampel_perbandingan[0]:
        csv_path = "csv/lstSampelValidasi.csv"

        try:
            df = pd.read_csv(csv_path)

            def format_lst_value(value):
                try:
                    return f"{float(value):.2f}"
                except:
                    return str(value)

            def convert_df_to_html_lst(input_df):
                formatters = {}
                for col in input_df.columns:
                    if any(
                        keyword in col.lower()
                        for keyword in ["lst", "aktual", "prediksi", "pengukuran"]
                    ):
                        formatters[col] = format_lst_value

                return input_df.to_html(
                    escape=False,
                    formatters=formatters,
                    table_id="lst-sample-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html_lst(df)

            st.markdown(
                """
                <style>
                #lst-sample-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 0px 0 10px 0; 
                    font-family: 'Poppins', sans-serif;
                    margin-top: -15px;
                    margin-bottom: 15px;
                }
                #lst-sample-table th, #lst-sample-table td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: center; 
                    vertical-align: middle; 
                    font-size: 14px;
                }
                #lst-sample-table th { 
                    background-color: #E4EFE7; 
                    font-weight: bold; 
                    color: #333;
                }
                #lst-sample-table td:not(:first-child) {
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
            st.error(f"Error dalam menampilkan tabel sampel LST: {str(e)}")

    # Baris Kosong
    st.write("")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
        - [1] Arunab, K. S., & Mathew, A. (2024). Exploring Spatial Machine Learning Techniques for Improving Land Surface Temperature Prediction. *Kuwait Journal of Science*, 51. https://doi.org/10.1016/j.kjs.2024.100242 
        - [2] Ratner, B. (2009). The Correlation Coefficient: Its Values Range Between +1/-1, or Do They?. *Journal of Targeting, Measurement and Analysis for Marketing*, 17. 139-142. https://doi.org/10.1057/jt.2009.5
        """
        )

# ==============================================================================
# SECTION 4: MODEL
# ==============================================================================

with tab4:
    st.badge(
        "**Evaluasi Model XGBoost untuk Prediksi LST**",
        color="primary",
    )

    col1_metrik_img, col2_metrik_insight = st.columns([1.9, 2.1])
    with col1_metrik_img:
        with st.container(border=True):
            fig = go.Figure(
                data=[
                    go.Bar(
                        name="RMSE",
                        x=["RMSE"],
                        y=[0.7994],
                        text=["0.7994"],
                        textposition="outside",
                        marker_color="#F5C9B0",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="MAE",
                        x=["MAE"],
                        y=[0.6162],
                        text=["0.6162"],
                        textposition="outside",
                        marker_color="#A6B28B",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="R²",
                        x=["R²"],
                        y=[0.9609],
                        text=["0.9609"],
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
                    "range": [0, 1.2],
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
                # plot_bgcolor="#fdfaf6",
                # paper_bgcolor="#fdfaf6",
                margin=dict(l=0, r=0, t=20, b=30),
                height=324,
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
                - Model prediksi memiliki **tingkat akurasi sangat tinggi** dibuktikan dengan nilai *error* :green-background[**RMSE (0.7994)**] dan :green-background[**MAE (0.6162)**] yang rendah<sup>[1]</sup>. *Error* prediksi **dianggap wajar** karena masih berada dalam rentang toleransi yang diizinkan untuk pemodelan LST (:green-background[**± 2°C**])<sup>[2]</sup>.
                - **Koefisien determinasi (R²)** menunjukkan nilai :green-background[**96.09%**] artinya model mampu **menjelaskan mayoritas variasi** data LST dengan **sangat baik**<sup>[3]</sup>.
                """,
                unsafe_allow_html=True,
            )
            st.success("✅ Model **LAYAK** untuk memprediksi LST 2029!")

    # Baris Kosong
    st.write("")

    # Plot SHAP
    st.badge(
        "**Analisis SHAP: Kontribusi Fitur pada Prediksi LST 2024**",
        color="primary",
    )

    col1_2024, col2_2024 = st.columns([2.225, 1.775])
    with col1_2024:
        with st.container(border=True):
            st.image("img/shapLST2024.png")

    with col2_2024:
        with st.container(border=True):
            with st.expander("🧰 **Quick Guide: Plot Beeswarm SHAP**"):
                st.html(
                    """
                    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

                    <style>
                        .shap-guide {
                            font-family: 'Poppins', sans-serif;
                            font-size: 16px;
                            line-height: 1.6;
                        }
                        .shap-guide ol, 
                        .shap-guide ul {
                            margin-left: 20px;
                            margin-top: 4px;
                            margin-bottom: 4px;
                        }
                        .shap-guide li {
                            margin-bottom: 4px;
                            line-height: 1.6;
                        }
                        .shap-guide hr {
                            margin: 16px 0;
                        }
                    </style>

                    <div class="shap-guide">
                        <p><b>SHAP (SHapley Additive exPlanations)</b> adalah sebuah metode untuk menafsirkan model 
                        <i>machine learning</i> yang kompleks <sup>[4]</sup>. SHAP bekerja selayaknya <i>'blackbox'</i> untuk 
                        <b>mengungkap kontribusi</b> setiap fitur terhadap prediksi.</p>

                        <hr>

                        <p><b>Panduan Membaca Plot:</b></p>
                        <ol>
                            <li>
                                <b>Apa Fitur yang Paling Berpengaruh?</b><br>
                                Lihat urutan pada <b>sumbu Y</b>. Fitur yang berada <b>paling atas</b> adalah fitur yang memiliki kontribusi terbesar dalam prediksi.
                            </li>
                            <li>
                                <b>Bagaimana Arah Pengaruhnya?</b><br>
                                Lihat posisi titik pada <b>sumbu X</b> dan <b>warnanya</b>.
                                <ul style="margin-left:20px; margin-top:6px; list-style-type: disc; list-style-position: outside;">
                                    <li>Titik di <b>kanan</b> → Mendorong prediksi <b>naik</b> (lebih tinggi).</li>
                                    <li>Titik di <b>kiri</b> → Mendorong prediksi <b>turun</b> (lebih rendah).</li>
                                    <li>Warna <b>merah/pink</b> → Nilai fitur <b>tinggi</b> (misal: LST 2019 tinggi).</li>
                                    <li>Warna <b>biru</b> → Nilai fitur <b>rendah</b> (misal: LST 2019 rendah).</li>
                                </ul>
                            </li>
                        </ol>
                    </div>
                    """
                )

        with st.container(border=True):
            st.write("💡 **Quick Insight**")
            st.markdown(
                f"""
                - **LST 2019** menjadi fitur dengan **kontribusi tertinggi**. Nilai LST yang tinggi di masa lalu **mendorong** prediksi LST 2024 menjadi :green-background[**lebih tinggi**], begitu pula sebaliknya.
                - **Elevasi** menunjukkan **kontribusi negatif**. Lokasi dengan elevasi tinggi cenderung memiliki prediksi nilai LST 2024 yang :green-background[**lebih rendah**].
                - Lokasi di **koordinat Y** yang lebih besar (arah utara) cenderung :green-background[**menurunkan prediksi**] nilai LST 2024.
                - **NDVI 2024** juga berkontribusi penting, di mana nilai indeks yang rendah cenderung :green-background[**meningkatkan prediksi**] nilai LST 2024.
                - Fitur lain seperti **penutup lahan**, **NDMI**, dan **slope** memiliki pengaruh yang **relatif lebih kecil**.
                """,
                unsafe_allow_html=True,
            )

    # Baris Kosong
    st.write("")

    st.badge(
        "**Analisis SHAP: Kontribusi Fitur pada Prediksi LST 2029**",
        color="primary",
    )

    col1_2029, col2_2029 = st.columns([2.225, 1.775])
    with col1_2029:
        with st.container(border=True):
            st.image("img/shapLST2029.png")

    with col2_2029:
        with st.container(border=True):
            with st.expander("🧰 **Quick Guide: Plot Beeswarm SHAP**"):
                st.html(
                    """
                    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

                    <style>
                        .shap-guide {
                            font-family: 'Poppins', sans-serif;
                            font-size: 16px;
                            line-height: 1.6;
                        }
                        .shap-guide ol, 
                        .shap-guide ul {
                            margin-left: 20px;
                            margin-top: 4px;
                            margin-bottom: 4px;
                        }
                        .shap-guide li {
                            margin-bottom: 4px;
                            line-height: 1.6;
                        }
                        .shap-guide hr {
                            margin: 16px 0;
                        }
                    </style>

                    <div class="shap-guide">
                        <p><b>SHAP (SHapley Additive exPlanations)</b> adalah sebuah metode untuk menafsirkan model 
                        <i>machine learning</i> yang kompleks <sup>[4]</sup>. SHAP bekerja selayaknya <i>'blackbox'</i> untuk 
                        <b>mengungkap kontribusi</b> setiap fitur terhadap prediksi.</p>

                        <hr>

                        <p><b>Panduan Membaca Plot:</b></p>
                        <ol>
                            <li>
                                <b>Apa Fitur yang Paling Berpengaruh?</b><br>
                                Lihat urutan pada <b>sumbu Y</b>. Fitur yang berada <b>paling atas</b> adalah fitur yang memiliki kontribusi terbesar dalam prediksi.
                            </li>
                            <li>
                                <b>Bagaimana Arah Pengaruhnya?</b><br>
                                Lihat posisi titik pada <b>sumbu X</b> dan <b>warnanya</b>.
                                <ul style="margin-left:20px; margin-top:6px; list-style-type: disc; list-style-position: outside;">
                                    <li>Titik di <b>kanan</b> → Mendorong prediksi <b>naik</b> (lebih tinggi).</li>
                                    <li>Titik di <b>kiri</b> → Mendorong prediksi <b>turun</b> (lebih rendah).</li>
                                    <li>Warna <b>merah/pink</b> → Nilai fitur <b>tinggi</b> (misal: LST 2024 tinggi).</li>
                                    <li>Warna <b>biru</b> → Nilai fitur <b>rendah</b> (misal: LST 2024 rendah).</li>
                                </ul>
                            </li>
                        </ol>
                    </div>
                    """
                )

        with st.container(border=True):
            st.write("💡 **Quick Insight**")
            st.markdown(
                f"""               
                - **LST 2024** menjadi fitur dengan **kontribusi tertinggi**. Nilai LST yang tinggi di masa lalu **mendorong prediksi LST 2029** menjadi :green-background[**lebih tinggi**], begitu pula sebaliknya.
                - **Elevasi** menunjukkan **kontribusi negatif**. Lokasi dengan elevasi tinggi cenderung memiliki prediksi nilai LST 2029 yang :green-background[**lebih rendah**].
                - Lokasi di **koordinat Y** yang lebih besar (arah utara) cenderung :green-background[**menurunkan prediksi**] nilai LST 2029.
                - **NDVI 2029** juga berkontribusi penting, di mana nilai indeks yang rendah cenderung :green-background[**meningkatkan prediksi**] nilai LST 2029.
                - Fitur lain seperti **penutup lahan**, **NDMI**, dan **slope** memiliki pengaruh yang **relatif lebih kecil**.
                """,
                unsafe_allow_html=True,
            )

    # Baris Kosong
    st.write("")

    # Peta Perbandingan
    st.badge(
        "**Perbandingan Visual Peta LST Aktual dan Prediksi**",
        color="primary",
    )

    col_peta_perbandingan = st.columns(1)
    with col_peta_perbandingan[0]:
        with st.container(border=True):
            st.write("Hahaha")

    # Baris Kosong
    st.write("")

    st.badge(
        "**Tabel Perbandingan Sampel Nilai LST Aktual dan Prediksi**",
        color="primary",
    )

    col_sampel_perbandingan = st.columns(1)
    with col_sampel_perbandingan[0]:
        csv_path = "csv/lstSampelModel.csv"

        try:
            df = pd.read_csv(csv_path)

            def format_lst_value(value):
                try:
                    return f"{float(value):.2f}"
                except:
                    return str(value)

            def convert_df_to_html_lst(input_df):
                formatters = {}
                for col in input_df.columns:
                    if (
                        "lst" in col.lower()
                        or "aktual" in col.lower()
                        or "prediksi" in col.lower()
                    ):
                        formatters[col] = format_lst_value

                return input_df.to_html(
                    escape=False,
                    formatters=formatters,
                    table_id="lst-sample-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html_lst(df)

            st.markdown(
                """
                <style>
                #lst-sample-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 0px 0 10px 0; 
                    font-family: 'Poppins', sans-serif;
                    margin-top: -15px;
                    margin-bottom: 15px;
                }
                #lst-sample-table th, #lst-sample-table td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: center; 
                    vertical-align: middle; 
                    font-size: 14px;
                }
                #lst-sample-table th { 
                    background-color: #E4EFE7; 
                    font-weight: bold; 
                    color: #333;
                }
                #lst-sample-table td:not(:first-child) {
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
            st.error(f"Error dalam menampilkan tabel sampel LST: {str(e)}")

    # Baris Kosong
    st.write("")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
            - [1] Nurdin, Suarna, N., Prihartono, W. (2025). Algoritma Regresi Linier untuk Prediksi Penggunaan Volume Air Berdasarkan Jenis Pelanggan PDAM. *Jurnal Kecerdasan Buatan dan Teknologi Informasi*, 4(1). 43-52. https://doi.org/10.69916/jkbti.v4i1.187
            - [2] Arunab, K. S., & Mathew, A. (2024). Exploring Spatial Machine Learning Techniques for Improving Land Surface Temperature Prediction. *Kuwait Journal of Science*, 51. https://doi.org/10.1016/j.kjs.2024.100242 
            - [3] Man, A., Chaichana, C., Wicharuck, S., Rinchumphu, D. (2022). *Predicting Sunlight Availability for Vertical Shelves using Simulation*. *IOP Conference Series: Earth and Environmental Science*. 1094 012011. https://doi.org/10.1088/1755-1315/1094/1/012011
            - [4] Lundberg, S. M., & Lee, S. (2017). *A Unified Approach to Interpreting Model Predictions*. *Proceedings of the 31st International Conference on Neural Information Processing Systems (NIPS'17)*. Curran Associates Inc., Red Hook, New York, Amerika Serikat, 4768–4777.
            """
        )


# ==============================================================================
# SECTION 5: REGRESI
# ==============================================================================

with tab5:
    # Membaca Data CSV
    try:
        df_regression = pd.read_csv("csv/sampelRegresi.csv")

        # Row Diagram Garis & Ranking LST
        st.badge(
            "**Scatter Plot Regresi Linier LST dan NDBI**",
            color="primary",
        )

        col1_regresi_ndbi, col2_regresi_ndbi = st.columns([2, 2])
        with col1_regresi_ndbi:
            with st.container(border=True):
                # Membuat plot LST dan NDBI
                fig_ndbi, r2_ndbi, p_val_ndbi, slope_ndbi = create_regression_plot(
                    df_regression,
                    "NDBI",
                    "LST",
                    "Regresi Linier: LST dan NDBI",
                    "NDBI",
                    "LST (°C)",
                )

                if fig_ndbi is not None:
                    st.plotly_chart(fig_ndbi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDBI")

        with col2_regresi_ndbi:
            with st.container(border=True):
                st.markdown("💡 **Quick Insight**")
                if fig_ndbi is not None:
                    insight_ndbi, is_influential_ndbi = interpret_regression(
                        r2_ndbi, p_val_ndbi, slope_ndbi, "NDBI"
                    )
                    st.markdown(insight_ndbi, unsafe_allow_html=True)

                    if is_influential_ndbi:
                        st.success("✅ NDBI berpengaruh signifikan terhadap LST!")
                    else:
                        st.warning("❌ NDBI tidak berpengaruh terhadap LST!")

        # Baris Kosong
        st.write("")

        # Row Diagram Garis & Ranking LST
        st.badge(
            "**Scatter Plot Regresi Linier LST dan NDMI**",
            color="primary",
        )

        col1_regresi_ndmi, col2_regresi_ndmi = st.columns([2, 2])
        with col1_regresi_ndmi:
            with st.container(border=True):
                # Membuat plot LST dan NDMI
                fig_ndmi, r2_ndmi, p_val_ndmi, slope_ndmi = create_regression_plot(
                    df_regression,
                    "NDMI",
                    "LST",
                    "Regresi Linier: LST dan NDMI",
                    "NDMI",
                    "LST (°C)",
                )

                if fig_ndmi is not None:
                    st.plotly_chart(fig_ndmi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDMI")

        with col2_regresi_ndmi:
            with st.container(border=True):
                st.markdown("💡 **Quick Insight**")
                if fig_ndmi is not None:
                    insight_ndmi, is_influential_ndmi = interpret_regression(
                        r2_ndmi, p_val_ndmi, slope_ndmi, "NDMI"
                    )
                    st.markdown(insight_ndmi, unsafe_allow_html=True)

                    if is_influential_ndmi:
                        st.success("✅ NDMI berpengaruh  signifikan terhadap LST!")
                    else:
                        st.warning("❌ NDMI tidak berpengaruh terhadap LST!")

        # Baris Kosong
        st.write("")

        # Row Diagram Garis & Ranking LST
        st.badge(
            "**Scatter Plot Regresi Linier LST dan NDVI**",
            color="primary",
        )

        col1_regresi_ndvi, col2_regresi_ndvi = st.columns([2, 2])
        with col1_regresi_ndvi:
            with st.container(border=True):
                # Membuat plot LST dan NDVI
                fig_ndvi, r2_ndvi, p_val_ndvi, slope_ndvi = create_regression_plot(
                    df_regression,
                    "NDVI",
                    "LST",
                    "Regresi Linier: LST dan NDVI",
                    "NDVI",
                    "LST (°C)",
                )

                if fig_ndvi is not None:
                    st.plotly_chart(fig_ndvi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDVI")

        with col2_regresi_ndvi:
            with st.container(border=True):
                st.markdown("💡 **Quick Insight**")
                if fig_ndvi is not None:
                    insight_ndvi, is_influential_ndvi = interpret_regression(
                        r2_ndvi, p_val_ndvi, slope_ndvi, "NDVI"
                    )
                    st.markdown(insight_ndvi, unsafe_allow_html=True)

                    if is_influential_ndvi:
                        st.success("✅ NDVI berpengaruh signifikan terhadap LST!")
                    else:
                        st.warning("❌ NDVI tidak berpengaruh terhadap LST!")

    except FileNotFoundError:
        st.error(
            "File 'csv/sampelRegresi.csv' tidak ditemukan. Pastikan file sudah ada di folder yang benar."
        )
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")

    # Baris Kosong
    st.write("")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
        - [1] Sugiyono (2010). *Metode Penelitian Pendidikan Pendekatan Kuantitatif, Kualitatif, dan R&D*. Bandung: Penerbit Alfabeta.
        - [2] Schmidt, J., & Osebold, R. (2017). Environmental Management Systems as A Driver for Sustainability: State of Implementation, Benefits, and Barriers in German Construction Companies. *Journal of Civil Engineering and Management*, 23(1). 150-162. https://doi.org/10.3846/13923730.2014.946441
        """
        )
