from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap, Normalize
import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import os
import base64
from io import BytesIO
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
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 12px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
        border: 0.5px solid rgba(0, 0, 0, 0.1) !important;
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
        "low": 34.022,
        "medium": 38.347,
        "high": 42.672,
    },
}


# ==============================================================================
# DEKLARASI FUNGSI
# ==============================================================================
@st.cache_data
def load_stats_kec():
    """
    Load CSV Statistik LST tiap Kecamatan.
    """
    csv_path = "./csv/lstStatsKec.csv"
    try:
        df = pd.read_csv(csv_path)
        # Kolom Tahun di CSV Harus String
        df["Tahun"] = df["Tahun"].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"File CSV tidak ditemukan: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error membaca file CSV: {str(e)}")
        return pd.DataFrame()


def get_kec_by_year(df, year):
    """
    Filter LST Kecamatan Berdasarkan Tahun.
    """
    if df.empty:
        return {}

    year_data = df[df["Tahun"] == str(year)]
    if year_data.empty:
        return {}

    # Convert Menjadi Dictionary
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


@st.cache_data
def get_kecamatan_bounds(namobj):
    shapefile_path = "shp/aoi_kpy.shp"
    try:
        gdf = gpd.read_file(shapefile_path)

        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        kec_data = gdf[gdf["NAMOBJ"] == namobj]

        if not kec_data.empty:
            bounds = kec_data.total_bounds
            return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        else:
            return None
    except Exception as e:
        return None


def add_shp_to_map(map_obj, shapefile_path):
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

            # Tambahkan ke Peta
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
        height=266,
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
        significance = "Sangat Signifikan"
    elif p_value <= 0.01:
        significance = "Amat Signifikan"
    elif p_value <= 0.05:
        significance = "Signifikan"
    else:
        significance = "Tidak Signifikan"

    # Interpretasi R²
    r2_percent = r2 * 100

    # Cek Pengaruh
    is_influential = r2 >= 0.1 and p_value < 0.05

    direction = "meningkat" if slope > 0 else "menurun"

    interpretation = f"""
    - **Koefisien Determinasi (R²)**: Variabel :green-background[**{x_var}**] mampu menjelaskan variasi nilai LST sebesar :green-background[**{r2_percent:.2f}%**], sedangkan {100 - r2_percent:.2f}% sisanya dipengaruhi oleh faktor lain.⁽¹⁾
    - **Slope**: Nilai LST :green-background[**{direction} {abs(slope):.2f}°C**] untuk setiap kenaikan 0.1 unit nilai {x_var}.
    - **p-value**: {p_value:.3f} ({significance})⁽²⁾
    """

    return interpretation, is_influential


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

# Load DataFrame Kecamatan
df_kec_stats = load_stats_kec()

# Judul Halaman
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
    st.badge(
        "**Peta LST di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )

    col1_peta, col2_peta = st.columns([2.5, 1.5])
    with col2_peta:
        # Container Selectbox Tahun
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = stats_dict[option]

        # Container Metrics LST
        col1_peta_metric, col2_peta_metric, col3_peta_metric = st.columns([1, 1, 1])
        with col1_peta_metric:
            st.metric("LST Min", f"{selected_data['min']:.1f}°C")
        with col2_peta_metric:
            st.metric("LST Max", f"{selected_data['max']:.1f}°C")
        with col3_peta_metric:
            st.metric("LST Mean", f"{selected_data['mean']:.1f}°C")

        # Container Selectbox Kecamatan
        with st.container(border=True):
            # Ambil Data Statistik Kecamatan dari DataFrame
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
                st.warning(f"Data kecamatan untuk tahun {option} tidak tersedia")
                selected_kecamatan = ""

        # Container Analisis LST per Kecamatan
        if selected_kecamatan and selected_kecamatan != "" and kec_year:
            with st.container(border=True):
                st.write("💡**Quick Insight**")
                kecamatan_data = kec_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                # Pengkondisian Tahun 2029
                if option == "2029":
                    description = f"Suhu permukaan lahan di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] :green-background[**diprediksi**] sebesar :green-background[**{kecamatan_data['mean']:.2f}°C**] dengan suhu terendah yakni :green-background[**{kecamatan_data['min']:.2f}°C**] dan suhu tertinggi adalah :green-background[**{kecamatan_data['max']:.2f}°C**]."
                else:
                    description = f"Suhu permukaan lahan di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] memiliki rata-rata suhu sebesar :green-background[**{kecamatan_data['mean']:.2f}°C**] dengan suhu terendah yakni :green-background[**{kecamatan_data['min']:.2f}°C**] dan suhu tertinggi adalah :green-background[**{kecamatan_data['max']:.2f}°C**]."

                st.write(description)

    with col1_peta:
        if selected_kecamatan:
            kec_bounds = get_kecamatan_bounds(selected_kecamatan)
            if kec_bounds:
                center_lat = (kec_bounds[0][0] + kec_bounds[1][0]) / 2
                center_lon = (kec_bounds[0][1] + kec_bounds[1][1]) / 2
                map_center = [center_lat, center_lon]
                zoom_level = 14
            else:
                map_center = [-7.764326411862208, 110.3721676814108]
                zoom_level = 13
        else:
            map_center = [-7.764326411862208, 110.3721676814108]
            zoom_level = 10.5

        # Buat Peta Folium
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles=None,
        )

        # Tambahkan Basemap
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

        folium.TileLayer(
            tiles="OpenStreetMap",  # Letakkan di Bawah Sendiri Supaya Jadi Default
            name="OpenStreetMap",
            overlay=False,
            control=True,
        ).add_to(m)

        # Panggil GeoTiff dari Aset Lokal
        if option == "2029":
            tif_path = "tif/lst2029kpy.tif"
        else:
            tif_path = f"tif/lst{option}kpy.tif"

        # Set Threshold untuk Tahun yang Dipilih
        thresholds = threshold_dict[option]

        # Cek Ketersediaan GeoTiff, Panggil Function GeoTiff, dan Tampilkan ke Peta
        if os.path.exists(tif_path):
            add_geotiff_to_map(m, tif_path, thresholds)
        else:
            st.warning(f"File GeoTIFF tidak ditemukan: {tif_path}")

        # Cek Ketersediaan AOI, Panggil Function Batas AOI, dan Tampilkan ke Peta
        shapefile_path = "shp/aoi_kpy.shp"
        if os.path.exists(shapefile_path):
            add_shp_to_map(m, shapefile_path)
        else:
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
        st_data = st_folium(m, use_container_width=True, height=600)

# ==============================================================================
# SECTION 2: TREN
# ==============================================================================
with tab2:
    # Grafik Tren LST Perkotaan vs Non-Perkotaan
    df_urban_rural = pd.read_csv("./csv/lstStatsKec.csv")

    lst_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    lst_urban_rural_pivot = lst_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    st.badge(
        "**Tren LST: Kawasan Perkotaan vs Non-Perkotaan Yogyakarta (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2.4, 1.6])
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
                margin=dict(l=10, r=10, t=10, b=10),
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
                💡**Quick Insight**
                - Kedua kawasan menunjukkan :green-background[**pola fluktuasi yang serupa**]; di mana LST naik sejak 1999, mencapai puncak pada 2009 dan bergerak turun hingga 2019, lalu diprediksi akan naik pada 2029.
                - :green-background[**Kawasan perkotaan:**] LST terendah tercatat 39.47°C (1999), LST tertinggi sebesar 43.28°C (2009), dan diprediksi :green-background[**naik**] menjadi 43.54°C (2029).
                - :green-background[**Kawasan non-perkotaan:**] LST terendah tercatat 33.73°C (1999), LST tertinggi sebesar 36.86°C (2009), dan diprediksi :green-background[**naik**] menjadi 37.37°C (2029).
                """
            )

    # Row Diagram Garis & Ranking LST
    st.badge(
        "**Top 38 Kecamatan: Suhu Permukaan Tertinggi (1999-2024)**",
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
            textfont_size=10,
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
    st.write("Page under construction.")

# ==============================================================================
# SECTION 4: MODEL
# ==============================================================================

with tab4:
    st.badge(
        "**Evaluasi Model Prediksi XGBoost**",
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
                plot_bgcolor="#fdfaf6",
                paper_bgcolor="#fdfaf6",
                margin=dict(l=0, r=0, t=20, b=30),
                height=342.5,
                showlegend=True,
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")

            st.plotly_chart(fig, use_container_width=True)

    with col2_metrik_insight:
        with st.container(border=True):
            st.write("💡**Quick Insight**")
            st.markdown(
                f"""
                - :green-background[**RMSE**] dan :green-background[**MAE**] menunjukkan nilai yang :green-background[**relatif kecil**] artinya model prediksi memiliki :green-background[**tingkat kesalahan**] yang :green-background[**sangat rendah**]⁽¹⁾.
                - :green-background[**Error prediksi < 1°C**] masih dianggap :green-background[**wajar**] karena batas toleransi kesalahan yang :green-background[**dapat diterima**] data latih dalam prediksi LST adalah :green-background[**± 2°C**]⁽²⁾.
                - :green-background[**Koefisien determinasi (R²)**] menunjukkan bahwa :green-background[**96.09%**] variasi data :green-background[**dapat dijelaskan oleh model**] sehingga dapat dikatakan bahwa :green-background[**hasil prediksi sangat baik**]⁽³⁾.
                """,
                unsafe_allow_html=True,
            )
            st.success("✅ Model XGBoost **LAYAK** untuk prediksi LST 2029!")

    # Plot SHAP
    st.badge(
        "**Analisis SHAP: Kontribusi Fitur pada Prediksi LST 2024**",
        color="primary",
    )

    col1_2024, col2_2024 = st.columns([2.21, 1.79])
    with col1_2024:
        with st.container(border=True):
            st.image("img/shapLST2024.png")

    with col2_2024:
        with st.container(border=True):
            with st.expander("🧰 **Quick Guide: Plot SHAP**"):
                st.markdown(
                    f"""
                        - **SHAP (SHapley Additive exPlanations)** adalah sebuah framework untuk menafsirkan model prediksi⁽⁴⁾. SHAP bekerja selayaknya "blackbox" untuk **mengungkap kontribusi** atau tingkat kepentingan setiap **fitur** pada suatu prediksi tertentu.
                        - **Sumbu Y** merupakan **daftar fitur** dalam model yang telah **diurutkan** sesuai tingkat **kepentingannya**.
                        - **Sumbu X** adalah **nilai SHAP** yang menunjukkan **dampak** pada output model. Semakin jauh sebuah titik dari garis nol (ke kanan atau ke kiri), semakin besar dampaknya pada prediksi.
                        - **Nilai positif**: fitur tersebut **mendorong** prediksi ke **nilai** yang lebih **tinggi**.
                        - **Nilai negatif**: fitur tersebut **mendorong** prediksi ke **nilai** yang lebih **rendah**.
                        - **Nilai nol**: fitur tersebut **tidak berdampak** pada prediksi.
                        - **Warna titik** menunjukkan **nilai asli** dari fitur tersebut.
                        - Warna **merah/pink** (high) menunjukkan **nilai fitur** yang **tinggi**.
                        - Warna **biru** (low) menunjukkan **nilai fitur** yang **rendah**.
                    """,
                    unsafe_allow_html=True,
                )

        with st.container(border=True):
            st.write("💡**Quick Insight**")
            st.markdown(
                f"""
                - :green-background[**LST 2019**] dinyatakan sebagai fitur yang :green-background[**paling berkontribusi**] dalam prediksi LST 2024; diikuti :green-background[**koordinat**], :green-background[**elevasi**], :green-background[**NDVI 2024**], :green-background[**NDBI 2024**], dan :green-background[**NDVI 2019**].
                - Fitur dengan :green-background[**kontribusi lebih kecil**] meliputi :green-background[**penutup lahan**], :green-background[**NDMI**], :green-background[**NDBI 2019**], dan :green-background[**slope**].
                - Titik merah (LST tinggi) di sisi kanan dengan :green-background[**nilai SHAP positif**]. Artinya, ketika :green-background[**LST 2019**] memiliki :green-background[**nilai tinggi**], maka LST 2019 berkontribusi :green-background[**positif**] (meningkatkan) terhadap prediksi LST 2024.
                - Titik biru (LST rendah) di sisi kiri dengan :green-background[**nilai SHAP negatif**]. Artinya, ketika :green-background[**LST 2019**] memiliki :green-background[**nilai rendah**], maka LST 2019 berkontribusi :green-background[**negatif**] (menurunkan) terhadap prediksi LST 2024.
                """,
                unsafe_allow_html=True,
            )

    st.badge(
        "**Analisis SHAP: Kontribusi Fitur pada Prediksi LST 2029**",
        color="primary",
    )

    col1_2029, col2_2029 = st.columns([2.21, 1.79])
    with col1_2029:
        with st.container(border=True):
            st.image("img/shapLST2029.png")

    with col2_2029:
        with st.container(border=True):
            with st.expander("🧰 **Quick Guide: Plot SHAP**"):
                st.markdown(
                    f"""
                        - **SHAP (SHapley Additive exPlanations)** adalah sebuah framework untuk menafsirkan model prediksi⁽⁴⁾. SHAP bekerja selayaknya "blackbox" untuk **mengungkap kontribusi** atau tingkat kepentingan setiap **fitur** pada suatu prediksi tertentu.
                        - **Sumbu Y** merupakan **daftar fitur** dalam model yang telah **diurutkan** sesuai tingkat **kepentingannya**.
                        - **Sumbu X** adalah **nilai SHAP** yang menunjukkan **dampak** pada output model. Semakin jauh sebuah titik dari garis nol (ke kanan atau ke kiri), semakin besar dampaknya pada prediksi.
                        - **Nilai positif**: fitur tersebut **mendorong** prediksi ke **nilai** yang lebih **tinggi**.
                        - **Nilai negatif**: fitur tersebut **mendorong** prediksi ke **nilai** yang lebih **rendah**.
                        - **Nilai nol**: fitur tersebut **tidak berdampak** pada prediksi.
                        - **Warna titik** menunjukkan **nilai asli** dari fitur tersebut.
                        - Warna **merah/pink** (high) menunjukkan **nilai fitur** yang **tinggi**.
                        - Warna **biru** (low) menunjukkan **nilai fitur** yang **rendah**.
                    """,
                    unsafe_allow_html=True,
                )

        with st.container(border=True):
            st.write("💡**Quick Insight**")
            st.markdown(
                f"""
                - :green-background[**LST 2024**] dinyatakan sebagai fitur yang :green-background[**paling berkontribusi**] dalam prediksi LST 2029; diikuti informasi :green-background[**koordinat**], :green-background[**elevasi**], :green-background[**NDVI 2029**], :green-background[**NDVI 2024**], :green-background[**NDBI 2029**], dan :green-background[**penutup lahan 2029**].
                - Fitur dengan :green-background[**kontribusi lebih kecil**] meliputi :green-background[**NDMI**], :green-background[**NDBI 2024**],:green-background[**penutup lahan 2024**], dan :green-background[**slope**].
                - Titik merah (LST tinggi) di sisi kanan dengan :green-background[**nilai SHAP positif**]. Artinya, ketika :green-background[**LST 2024**] memiliki :green-background[**nilai tinggi**], maka LST 2024 berkontribusi :green-background[**positif**] (meningkatkan) terhadap prediksi LST 2029.
                - Titik biru (LST rendah) di sisi kiri dengan :green-background[**nilai SHAP negatif**]. Artinya, ketika :green-background[**LST 2024**] memiliki :green-background[**nilai rendah**], maka LST 2024 berkontribusi :green-background[**negatif**] (menurunkan) terhadap prediksi LST 2029.
                """,
                unsafe_allow_html=True,
            )

    # Peta Perbandingan
    st.badge(
        "**Perbandingan Visual Peta LST Aktual vs Prediksi**",
        color="primary",
    )

    col_peta_perbandingan = st.columns(1)
    with col_peta_perbandingan[0]:
        with st.container(border=True):
            try:

                def process_raster_data_with_threshold(data, thresholds):
                    data = data.astype("float32")

                    # # Filter sesuai threshold LST (30-45°C range yang wajar untuk LST)
                    # min_threshold = (
                    #     min(thresholds["low"], thresholds["medium"], thresholds["high"])
                    #     - 5
                    # )
                    # max_threshold = (
                    #     max(thresholds["low"], thresholds["medium"], thresholds["high"])
                    #     + 5
                    # )
                    # data = np.where(
                    #     (data < min_threshold) | (data > max_threshold), np.nan, data
                    # )

                    colors = {
                        "very_low": 0,
                        "low": 1,
                        "medium": 2,
                        "high": 3,
                    }

                    classified_data = np.full(data.shape, np.nan, dtype=np.float32)
                    valid_mask = ~np.isnan(data)
                    very_low_mask = valid_mask & (data <= thresholds["low"])
                    low_mask = (
                        valid_mask
                        & (data > thresholds["low"])
                        & (data <= thresholds["medium"])
                    )
                    medium_mask = (
                        valid_mask
                        & (data > thresholds["medium"])
                        & (data <= thresholds["high"])
                    )
                    high_mask = valid_mask & (data > thresholds["high"])

                    classified_data[very_low_mask] = colors["very_low"]
                    classified_data[low_mask] = colors["low"]
                    classified_data[medium_mask] = colors["medium"]
                    classified_data[high_mask] = colors["high"]

                    return classified_data

                # Threshold LST yang sudah direvisi
                thresholds = {
                    "aktual_2024": {"low": 33.207, "medium": 37.262, "high": 41.317},
                    "prediksi_2024": {"low": 33.315, "medium": 37.267, "high": 41.218},
                    "prediksi_2029": {"low": 34.022, "medium": 38.347, "high": 42.672},
                }

                # Aktual LST 2024
                with rasterio.open("tif/lst2024kpy.tif") as src:
                    data_2024_actual = src.read(1)
                    # Handle NoData
                    if src.nodata is not None:
                        data_2024_actual = np.where(
                            data_2024_actual == src.nodata, np.nan, data_2024_actual
                        )
                    bounds_actual = src.bounds
                    height, width = data_2024_actual.shape
                    x_actual = np.linspace(
                        bounds_actual.left, bounds_actual.right, width
                    )
                    y_actual = np.linspace(
                        bounds_actual.bottom, bounds_actual.top, height
                    )
                    data_2024_actual = np.flipud(data_2024_actual)
                    data_2024_actual = process_raster_data_with_threshold(
                        data_2024_actual, thresholds["aktual_2024"]
                    )

                # Prediksi LST 2024
                with rasterio.open("tif/prediksi_lst2024kpy.tif") as src:
                    data_2024_pred = src.read(1)
                    # Handle NoData
                    if src.nodata is not None:
                        data_2024_pred = np.where(
                            data_2024_pred == src.nodata, np.nan, data_2024_pred
                        )
                    bounds_pred = src.bounds
                    height, width = data_2024_pred.shape
                    x_pred_24 = np.linspace(bounds_pred.left, bounds_pred.right, width)
                    y_pred_24 = np.linspace(bounds_pred.bottom, bounds_pred.top, height)
                    data_2024_pred = np.flipud(data_2024_pred)
                    data_2024_pred = process_raster_data_with_threshold(
                        data_2024_pred, thresholds["prediksi_2024"]
                    )

                # Prediksi LST 2029
                with rasterio.open("tif/lst2029kpy.tif") as src:
                    data_2029_pred = src.read(1)
                    # Handle NoData
                    if src.nodata is not None:
                        data_2029_pred = np.where(
                            data_2029_pred == src.nodata, np.nan, data_2029_pred
                        )
                    bounds_2029 = src.bounds
                    height, width = data_2029_pred.shape
                    x_pred_29 = np.linspace(bounds_2029.left, bounds_2029.right, width)
                    y_pred_29 = np.linspace(bounds_2029.bottom, bounds_2029.top, height)
                    data_2029_pred = np.flipud(data_2029_pred)
                    data_2029_pred = process_raster_data_with_threshold(
                        data_2029_pred, thresholds["prediksi_2029"]
                    )

                colorscale = [
                    [0.0, "rgb(92, 160, 211)"],
                    [0.33, "rgb(245, 235, 177)"],
                    [0.67, "rgb(219, 167, 88)"],
                    [1.0, "rgb(147, 34, 14)"],
                ]

                fig = make_subplots(
                    rows=1,
                    cols=3,
                    subplot_titles=[
                        "Aktual LST 2024",
                        "Prediksi LST 2024",
                        "Prediksi LST 2029",
                    ],
                    horizontal_spacing=0.08,
                )

                fig.add_trace(
                    go.Heatmap(
                        z=data_2024_actual,
                        x=x_actual,
                        y=y_actual,
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
                        x=x_pred_24,
                        y=y_pred_24,
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
                        x=x_pred_29,
                        y=y_pred_29,
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
                        "color": "rgb(92, 160, 211)",
                    },
                    {
                        "name": "Rendah",
                        "color": "rgb(245, 235, 177)",
                    },
                    {
                        "name": "Sedang",
                        "color": "rgb(219, 167, 88)",
                    },
                    {
                        "name": "Tinggi",
                        "color": "rgb(147, 34, 14)",
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
                    height=507,
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
                        row=1,
                        col=i,
                        tickfont=dict(size=12, color="black"),
                        title_font=dict(size=12, color="black"),
                    )
                    fig.update_yaxes(
                        showgrid=False,
                        zeroline=False,
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
                # DEBUGGING: Print traceback untuk info lebih detail
                import traceback

                st.error(f"Traceback: {traceback.format_exc()}")

    st.badge(
        "**Tabel Perbandingan Sampel Nilai LST Aktual vs Prediksi**",
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
    # Membaca data CSV
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
                # Membuat Plot LST vs NDBI
                fig_ndbi, r2_ndbi, p_val_ndbi, slope_ndbi = create_regression_plot(
                    df_regression,
                    "NDBI",
                    "LST",
                    "Regresi Linier: LST vs NDBI",
                    "NDBI",
                    "LST (°C)",
                )

                if fig_ndbi is not None:
                    st.plotly_chart(fig_ndbi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDBI")

        with col2_regresi_ndbi:
            with st.container(border=True):
                st.markdown("💡**Quick Insight**")
                if fig_ndbi is not None:
                    insight_ndbi, is_influential_ndbi = interpret_regression(
                        r2_ndbi, p_val_ndbi, slope_ndbi, "NDBI"
                    )
                    st.markdown(insight_ndbi)

                    if is_influential_ndbi:
                        st.success(
                            "✅ NDBI berpengaruh positif signifikan terhadap LST!"
                        )
                    else:
                        st.warning("❌ NDBI tidak berpengaruh terhadap LST!")

        # Row Diagram Garis & Ranking LST
        st.badge(
            "**Scatter Plot Regresi Linier LST dan NDMI**",
            color="primary",
        )

        col1_regresi_ndmi, col2_regresi_ndmi = st.columns([2, 2])
        with col1_regresi_ndmi:
            with st.container(border=True):
                # Membuat plot LST vs NDMI
                fig_ndmi, r2_ndmi, p_val_ndmi, slope_ndmi = create_regression_plot(
                    df_regression,
                    "NDMI",
                    "LST",
                    "Regresi Linier: LST vs NDMI",
                    "NDMI",
                    "LST (°C)",
                )

                if fig_ndmi is not None:
                    st.plotly_chart(fig_ndmi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDMI")

        with col2_regresi_ndmi:
            with st.container(border=True):
                st.markdown("💡**Quick Insight**")
                if fig_ndmi is not None:
                    insight_ndmi, is_influential_ndmi = interpret_regression(
                        r2_ndmi, p_val_ndmi, slope_ndmi, "NDMI"
                    )
                    st.markdown(insight_ndmi)

                    if is_influential_ndmi:
                        st.success(
                            "✅ NDMI berpengaruh positif signifikan terhadap LST!"
                        )
                    else:
                        st.warning("❌ NDMI tidak berpengaruh terhadap LST!")

        # Row Diagram Garis & Ranking LST
        st.badge(
            "**Scatter Plot Regresi Linier LST dan NDVI**",
            color="primary",
        )

        col1_regresi_ndvi, col2_regresi_ndvi = st.columns([2, 2])
        with col1_regresi_ndvi:
            with st.container(border=True):
                # Membuat plot LST vs NDVI
                fig_ndvi, r2_ndvi, p_val_ndvi, slope_ndvi = create_regression_plot(
                    df_regression,
                    "NDVI",
                    "LST",
                    "Regresi Linier: LST vs NDVI",
                    "NDVI",
                    "LST (°C)",
                )

                if fig_ndvi is not None:
                    st.plotly_chart(fig_ndvi, use_container_width=True)
                else:
                    st.error("Data tidak dapat diproses untuk NDVI")

        with col2_regresi_ndvi:
            with st.container(border=True):
                st.markdown("💡**Quick Insight**")
                if fig_ndvi is not None:
                    insight_ndvi, is_influential_ndvi = interpret_regression(
                        r2_ndvi, p_val_ndvi, slope_ndvi, "NDVI"
                    )
                    st.markdown(insight_ndvi)

                    if is_influential_ndvi:
                        st.success(
                            "✅ NDVI berpengaruh positif signifikan terhadap LST!"
                        )
                    else:
                        st.warning("❌ NDVI tidak berpengaruh terhadap LST!")

    except FileNotFoundError:
        st.error(
            "File 'csv/sampelRegresi.csv' tidak ditemukan. Pastikan file sudah ada di folder yang benar."
        )
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
        - [1] Sugiyono (2010). *Metode Penelitian Pendidikan Pendekatan Kuantitatif, Kualitatif, dan R&D*. Bandung: Penerbit Alfabeta.
        - [2] Schmidt, J., & Osebold, R. (2017). Environmental Management Systems as A Driver for Sustainability: State of Implementation, Benefits, and Barriers in German Construction Companies. *Journal of Civil Engineering and Management*, 23(1). 150-162. https://doi.org/10.3846/13923730.2014.946441
        """
        )
