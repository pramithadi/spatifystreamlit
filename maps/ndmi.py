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
from sklearn.metrics import mean_squared_error, mean_absolute_error

st.set_page_config(
    page_title="NDMI — Spatify",
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

# Dictionary Statistik NDMI
stats_by_year = {
    "1999": {"min": -0.372, "max": 0.615, "mean": 0.168},
    "2004": {"min": -0.569, "max": 0.696, "mean": 0.188},
    "2009": {"min": -0.555, "max": 0.605, "mean": 0.153},
    "2014": {"min": -0.819, "max": 0.564, "mean": 0.179},
    "2019": {"min": -0.940, "max": 0.581, "mean": 0.161},
    "2024": {"min": -0.454, "max": 0.604, "mean": 0.162},
    "2029": {"min": -0.230, "max": 0.477, "mean": 0.156},
}

# Dictionary Threshold
threshold_dict = {
    "1999": {"low": 0.053, "medium": 0.168, "high": 0.283},
    "2004": {"low": 0.067, "medium": 0.188, "high": 0.309},
    "2009": {"low": 0.027, "medium": 0.153, "high": 0.280},
    "2014": {"low": 0.056, "medium": 0.179, "high": 0.302},
    "2019": {"low": 0.022, "medium": 0.161, "high": 0.301},
    "2024": {"low": 0.015, "medium": 0.162, "high": 0.309},
    "2029": {"low": 0.012, "medium": 0.156, "high": 0.300},
}


# ==============================================================================
# DEKLARASI FUNGSI
# ==============================================================================
@st.cache_data
def load_kecamatan_stats():
    """
    Load CSV Statistik NDMI tiap Kecamatan.
    """
    csv_path = "./csv/ndmiStatsKec.csv"
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


def get_kecamatan_data_by_year(df, year):
    """
    Filter NDMI Kecamatan Berdasarkan Tahun.
    """
    if df.empty:
        return {}

    year_data = df[df["Tahun"] == str(year)]
    if year_data.empty:
        return {}

    # Convert ke Dictionary
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
    """
    Penentuan Istilah Kapanewon/Kemantren Berdasarkan Kabupaten/Kota (WADMKK).
    """
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
    """
    Menambahkan SHP Batas Administrasi ke Peta Folium.
    """
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
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Tingkat Kelembapan Vegetasi</div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #948979; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sangat Rendah (≤ {thresholds['low']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #ffffe0; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Rendah ({thresholds['low']:.3f} - {thresholds['medium']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #add8e6; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Sedang ({thresholds['medium']:.3f} - {thresholds['high']:.3f})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; background-color: #00008b; border: 1px solid #ddd;"></div>
                <span style="color: #333;">Tinggi (> {thresholds['high']:.3f})</span>
            </div>
        </div>
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))


def add_geotiff_to_map(map_obj, tif_path, thresholds):
    """
    Menambahkan GeoTiff Penutup Lahan ke Peta Folium.
    """
    try:
        with rasterio.open(tif_path) as src:
            # Rasterio untuk Membaca Data Raster
            data = src.read(1)

            # Menegaskan Batas
            bounds = src.bounds

            # Handle NoData dan Outlier Piksel
            if hasattr(src, "nodata") and src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)

            # Nilai NDMI Berkisar -1 Hingga +1
            # Maka Hanya Filter Nilai yang Benar-benar Tidak Valid (Outlier Ekstrem)
            data = np.where((data < -1) | (data > 1), np.nan, data)

            # Warna untuk Setiap Kelas (DIPERBAIKI - Konversi hex ke RGB)
            colors = {
                "very_low": [148, 137, 121, 255],  # #948979
                "low": [255, 255, 224, 255],  # #ffffe0
                "medium": [173, 216, 230, 255],  # #add8e6
                "high": [0, 0, 139, 255],  # #00008b
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

            # Pengaplikasian Warna Berdasarkan Klasifikasi (DIPERBAIKI)
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
            ndmi_overlay = folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_folium,
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
                name="NDMI",
            )
            ndmi_overlay.add_to(map_obj)

        return True
    except Exception as e:
        return False


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

kecamatan_stats_df = load_kecamatan_stats()

st.header("Normalized Difference Moisture Index")

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
    st.badge(
        "**Peta NDMI di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
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

            selected_data = stats_by_year[option]

        # Container Metrics NDMI
        col1_peta_metric, col2_peta_metric, col3_peta_metric = st.columns([1, 1, 1])
        with col1_peta_metric:
            with st.container(border=True):
                st.metric("NDMI Min", f"{selected_data['min']:.2f}")
        with col2_peta_metric:
            with st.container(border=True):
                st.metric("NDMI Max", f"{selected_data['max']:.2f}")
        with col3_peta_metric:
            with st.container(border=True):
                st.metric("NDMI Mean", f"{selected_data['mean']:.2f}")

        # Container Selectbox Kecamatan
        with st.container(border=True):
            # Ambil Data Statistik Kecamatan dari DataFrame
            kecamatan_data_year = get_kecamatan_data_by_year(kecamatan_stats_df, option)

            # Selectbox Cari Kecamatan
            if kecamatan_data_year:
                kecamatan_options = list(kecamatan_data_year.keys())
                selected_kecamatan = st.selectbox(
                    "**Cari Kecamatan**",
                    [""] + kecamatan_options,
                    index=0,
                    placeholder="Ketik atau pilih kecamatan",
                )
            else:
                st.warning(f"Data kecamatan untuk tahun {option} tidak tersedia")
                selected_kecamatan = ""

        # Function Klasifikasi Deskripsi
        def classify_ndmi(mean_value, thresholds):

            if mean_value <= thresholds["low"]:
                return "sangat rendah", "sangat rendah"
            elif thresholds["low"] < mean_value <= thresholds["medium"]:
                return "cenderung rendah", "cenderung rendah"
            elif thresholds["medium"] < mean_value <= thresholds["high"]:
                return "cukup sedang", "cukup sedang"
            else:  # mean_value > thresholds['high']
                return "tinggi", "tinggi"

        # Container Analisis NDMI per Kecamatan
        if selected_kecamatan and selected_kecamatan != "" and kecamatan_data_year:
            with st.container(border=True):
                st.write("💡 **Quick Insight**")
                kecamatan_data = kecamatan_data_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                current_thresholds = threshold_dict[option]

                kategori, deskripsi = classify_ndmi(
                    kecamatan_data["mean"], current_thresholds
                )

                # Pengkondisian Tahun 2029
                if option == "2029":
                    description = f"Pada tahun :green-background[**{option}**], **{toponim} {selected_kecamatan}** :green-background[**diprediksi**] memiliki nilai rata-rata NDMI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai ini mengindikasikan bahwa :green-background[**{toponim} {selected_kecamatan}**] memiliki tingkat **kelembapan vegetasi** yang :green-background[**{deskripsi}**] pada masa mendatang."
                else:
                    description = f"Pada tahun :green-background[**{option}**], **{toponim} {selected_kecamatan}** memiliki nilai rata-rata NDMI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai ini mengindikasikan bahwa :green-background[**{toponim} {selected_kecamatan}**] memiliki tingkat **kelembapan vegetasi** yang :green-background[**{deskripsi}**]."

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
            tif_path = "tif/output_ndmi2029kpy.tif"
        else:
            tif_path = f"tif/ndmi{option}kpy.tif"

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
        st_data = st_folium(m, use_container_width=True, height=597)

# ==============================================================================
# SECTION 2: TREN
# ==============================================================================
with tab2:
    df_urban_rural = pd.read_csv("./csv/ndmiStatsKec.csv")

    ndmi_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    ndmi_urban_rural_pivot = ndmi_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking NDMI
    st.badge(
        "**Tren NDMI di Kawasan Perkotaan dan Non-Perkotaan Yogyakarta (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2, 2])
    with col1_tren_main:
        # Container Grafik Tren
        with st.container(border=True):
            # Buat Grafik
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            fig = go.Figure()

            if "Urban" in ndmi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndmi_urban_rural_pivot.index,
                        y=ndmi_urban_rural_pivot["Urban"],
                        mode="lines+markers",
                        name="Perkotaan",
                        line=dict(color="#FF90BB", width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate="<b>Perkotaan</b><br>Tahun: %{x}<br>NDMI Mean: %{y:.3f}<extra></extra>",
                    )
                )

            if "Rural" in ndmi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndmi_urban_rural_pivot.index,
                        y=ndmi_urban_rural_pivot["Rural"],
                        mode="lines+markers",
                        name="Non-Perkotaan",
                        line=dict(color="#096B68", width=3),
                        marker=dict(size=8, symbol="square"),
                        hovertemplate="<b>Non-Perkotaan</b><br>Tahun: %{x}<br>NDMI Mean: %{y:.3f}<extra></extra>",
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
                        text="NDMI Mean",
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
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                height=319,
                font=dict(family="Poppins", size=12),
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Dictionary Mean NDMI
        mean_by_year = {
            1999: {"mean": 0.168},
            2004: {"mean": 0.188},
            2009: {"mean": 0.153},
            2014: {"mean": 0.179},
            2019: {"mean": 0.161},
            2024: {"mean": 0.162},
            2029: {"mean": 0.156},
        }

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡 **Quick Insight**
                - Nilai :green-background[**NDMI**] berkisar dari :green-background[**-1**] (area kering/kadar air rendah) hingga :green-background[**+1**] (area lembap/kadar air tinggi).
                - Terlihat tren yang **sangat kontras** antara kedua kawasan. **Kawasan non-perkotaan** secara konsisten menunjukkan nilai NDMI yang :green-background[**tinggi**], mengindikasikan tingkat **kelembapan vegetasi yang terjaga**.
                - Sebaliknya, **kawasan perkotaan** menunjukkan nilai NDMI yang **jauh lebih rendah** dan mengalami **tren penurunan yang signifikan**. Kondisi ini mengindikasikan :green-background[**berkurangnya area bervegetasi sehat**] dan :green-background[**meningkatnya kekeringan vegetasi dan tanah**] seiring waktu.
                """
            )

    # Row Diagram Garis & Ranking NDMI
    st.badge(
        "**Peringkat Kecamatan Berdasarkan Rata-rata NDMI (1999-2024)**",
        color="primary",
    )

    col_rank = st.columns([1])[0]
    with col_rank:
        df_stats = pd.read_csv("./csv/ndmiStatsKec.csv")

        # Hitung Rata-rata Mean untuk Setiap Kecamatan dari Semua Tahun
        df_ranking = (
            df_stats.groupby(["NAMOBJ", "WADMKK", "Zona"])["mean"].mean().reset_index()
        )
        df_ranking.columns = ["NAMOBJ", "WADMKK", "Zona", "Mean_NDMI"]

        # Sort dari Tertinggi ke Terendah
        df_ranking = df_ranking.sort_values("Mean_NDMI", ascending=False).reset_index(
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
            x="Mean_NDMI",
            y="Y_Label",
            color="Zona",
            color_discrete_map={"Urban": "#FF90BB", "Rural": "#096B68"},
            orientation="h",
            labels={
                "Mean_NDMI": "NDMI Mean",
                "Y_Label": "",
                "Zona": "Kawasan",
            },
            # Isi Hover
            hover_data={"Mean_NDMI": ":.3f", "Zona": False, "Y_Label": False},
            custom_data=["Zona_Label", "Mean_NDMI"],
        )

        # Update Hover Template
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>"
            + "Kawasan: %{customdata[0]}<br>"
            + "NDMI Mean: %{customdata[1]:.3f}<extra></extra>",
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
        # Load CSV Sampel NDMI untuk Validasi
        validation_data = pd.read_csv("csv/ndmiSampelValidasi.csv")

        # Hapus Nilai NaN
        validation_data = validation_data.dropna()

        # Ekstraksi Nilai dari Field
        sentinel_values = validation_data["ndmiSentinel"].values  # X
        landsat_values = validation_data["ndmiLandsat"].values  # Y

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

        # Row Diagram Garis dan Validasi NDMI
        st.badge(
            "**Korelasi Pearson NDMI Landsat 8 dan Sentinel-2 (2024)**",
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
                    labels={"x": "NDMI Sentinel-2", "y": "NDMI Landsat 8"},
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
                            text="NDMI Sentinel-2",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    yaxis=dict(
                        title=dict(
                            text="NDMI Landsat 8",
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
                    - **Korelasi Sangat Kuat**: NDMI Landsat 8 dan Sentinel-2 memiliki hubungan kuat (:green-background[**r**] = :green-background[**{correlation_coef:.3f}**])<sup>[1]</sup>.
                    - **Akurasi Tinggi**: Kesalahan antar data :green-background[**sangat kecil**] (RMSE = {rmse:.3f}, MAE = {mae:.3f}) menandakan hasil pengolahan NDMI kedua satelit hampir :green-background[**identik**]<sup>[2]</sup>.
                    - Hubungan kedua NDMI :green-background[**valid secara statistik**] dengan nilai **p-value sangat signifikan** (< 0.01)<sup>[3]</sup>.
                """,
                    unsafe_allow_html=True,
                )

                # Status Validasi
                abs_corr = abs(correlation_coef)
                if abs_corr >= 0.7 and rmse <= 0.1:
                    st.success("✅ VALID! Data NDMI layak untuk memprediksi LST!")
                elif abs_corr >= 0.5 and rmse <= 0.15:
                    st.warning("⚠️ CUKUP VALID — Data dapat digunakan dengan catatan.")
                elif abs_corr >= 0.3 and rmse <= 0.2:
                    st.warning("⚠️ KURANG VALID — Data perlu perbaikan.")
                else:
                    st.error("❌ TIDAK VALID — Data tidak layak digunakan.")

    except FileNotFoundError:
        st.error("❌ File 'csv/ndmiSampelValidasi.csv' tidak ditemukan!")
        st.info(
            "Pastikan file CSV hasil sampling dari GEE sudah tersedia di folder 'csv/'"
        )

    except Exception as e:
        st.error(f"❌ Error dalam memproses data: {str(e)}")
        st.info(
            "Periksa format file CSV dan nama kolom ('ndmiLandsat' dan 'ndmiSentinel')"
        )

    # Row Peta NDMI Landsat 8 dan Sentinel-2
    # Threshold untuk Peta Validasi
    validation_thresholds = {
        "landsat": {"low": 0.015, "medium": 0.162, "high": 0.309},
        "sentinel": {"low": -0.053, "medium": 0.093, "high": 0.238},
    }

    st.badge(
        "**Peta NDMI Landsat 8 dan Sentinel-2 (2024)**",
        color="primary",
    )
    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #333; font-size: 14px;">📡 Landsat 8 NDMI (2024)</div>
                <div style="font-weight: 600; color: #333; font-size: 14px;">🛰️ Sentinel-2 NDMI (2024)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Import DualMap Plugin
        from folium.plugins import DualMap

        # Buat DualMap dengan Synchronized View
        dual_map = DualMap(
            location=[-7.764326411862208, 110.3721676814108],
            zoom_start=10.5,
            tiles=None,
        )

        # Tambahkan Basemap ke Kedua Sisi
        # Sisi Kiri (Landsat)
        folium.TileLayer(
            tiles="CartoDB positron",
            name="CartoDB Positron",
            overlay=False,
            control=True,
        ).add_to(dual_map.m1)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="OpenStreetMap",
            overlay=False,
            control=True,
        ).add_to(dual_map.m1)

        # Sisi Kanan (Sentinel)
        folium.TileLayer(
            tiles="CartoDB positron",
            name="CartoDB Positron",
            overlay=False,
            control=True,
        ).add_to(dual_map.m2)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="OpenStreetMap",
            overlay=False,
            control=True,
        ).add_to(dual_map.m2)

        # Path untuk File GeoTIFF
        landsat_tif_path = "tif/ndmi2024kpy.tif"
        sentinel_tif_path = "tif/ndmiSentinel30.tif"
        shapefile_path = "shp/aoi_kpy.shp"

        # Tambahkan GeoTiff Landsat ke Sisi Kiri
        if os.path.exists(landsat_tif_path):
            add_geotiff_to_map(
                dual_map.m1, landsat_tif_path, validation_thresholds["landsat"]
            )
        else:
            st.warning(f"File Landsat GeoTIFF tidak ditemukan: {landsat_tif_path}")

        # Tambahkan GeoTiff Sentinel ke Sisi Kanan
        if os.path.exists(sentinel_tif_path):
            add_geotiff_to_map(
                dual_map.m2, sentinel_tif_path, validation_thresholds["sentinel"]
            )
        else:
            st.warning(f"File Sentinel GeoTIFF tidak ditemukan: {sentinel_tif_path}")

        # Tambahkan Batas Administrasi ke Kedua Peta
        if os.path.exists(shapefile_path):
            add_shp_to_map(dual_map.m1, shapefile_path)
            add_shp_to_map(dual_map.m2, shapefile_path)

        # Function untuk Menambahkan Legenda Universal
        def add_universal_legend_to_map(map_obj, title):
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
                <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">{title}</div>
                <div style="display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #948979; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Sangat Rendah</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #ffffe0; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Rendah</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #add8e6; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Sedang</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #00008b; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Tinggi</span>
                    </div>
                </div>
            </div>
            """
            map_obj.get_root().html.add_child(folium.Element(legend_html))

        add_universal_legend_to_map(dual_map.m1, "Kelas NDMI")

        # Tambahkan Layer Control ke Kedua Peta
        folium.LayerControl(position="topleft", collapsed=True).add_to(dual_map.m1)
        folium.LayerControl(position="topleft", collapsed=True).add_to(dual_map.m2)

        # CSS untuk Custom Peta dan Title
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
        
        /* Title untuk peta kiri (Landsat) */
        .leaflet-left .leaflet-top::after {
            content: '📡 Landsat 8 NDMI (2024)';
            position: absolute;
            top: 50px;
            left: 0;
            background: rgba(255, 255, 255, 0.95);
            padding: 6px 10px;
            border: 1px solid #333;
            border-radius: 3px;
            font-family: 'Poppins', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #333;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1001;
        }
        </style>
        """
        dual_map.get_root().html.add_child(folium.Element(css))

        # Display DualMap
        st_folium(dual_map, use_container_width=True, height=500)

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
        "**Evaluasi Model XGBoost untuk Proyeksi Indeks**",
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
                        y=[0.0539],
                        text=["0.0539"],
                        textposition="outside",
                        marker_color="#F5C9B0",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="MAE",
                        x=["MAE"],
                        y=[0.0409],
                        text=["0.0409"],
                        textposition="outside",
                        marker_color="#A6B28B",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="R²",
                        x=["R²"],
                        y=[0.8648],
                        text=["0.8648"],
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
                height=341.5,
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
                - **Koefisien determinasi (R²)** menunjukkan bahwa :green-background[**86.48%**] variasi data **dapat dijelaskan oleh model** yang mengindikasikan **hasil proyeksi akurat**<sup>[2]</sup>.
                """,
                unsafe_allow_html=True,
            )

            st.success("✅ Model **LAYAK** untuk memproyeksikan NDMI 2029!")
            st.success(
                "✅ Data proyeksi NDMI 2029 **VALID** untuk memprediksi LST 2029!"
            )

    st.badge(
        "**Perbandingan Visual Peta NDMI Aktual dan Proyeksi**",
        color="primary",
    )

    col_peta_perbandingan = st.columns(1)
    with col_peta_perbandingan[0]:
        with st.container(border=True):
            try:

                def process_raster_data_with_threshold(data, thresholds):
                    data = data.astype("float32")
                    data = np.where((data < -1) | (data > 1), np.nan, data)

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

                thresholds = {
                    "aktual_2024": {"low": 0.015, "medium": 0.162, "high": 0.309},
                    "proyeksi_2024": {
                        "low": 0.025,
                        "medium": 0.162,
                        "high": 0.299,
                    },
                    "proyeksi_2029": {"low": 0.012, "medium": 0.156, "high": 0.300},
                }

                # Aktual NDMI 2024
                with rasterio.open("tif/ndmi2024kpy.tif") as src:
                    data_2024_actual = src.read(1)
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

                # Proyeksi NDMI 2024
                with rasterio.open("tif/output_proyeksi_ndmi2024kpy.tif") as src:
                    data_2024_pred = src.read(1)
                    bounds_pred = src.bounds
                    height, width = data_2024_pred.shape
                    x_pred_24 = np.linspace(bounds_pred.left, bounds_pred.right, width)
                    y_pred_24 = np.linspace(bounds_pred.bottom, bounds_pred.top, height)
                    data_2024_pred = np.flipud(data_2024_pred)
                    data_2024_pred = process_raster_data_with_threshold(
                        data_2024_pred, thresholds["proyeksi_2024"]
                    )

                # Proyeksi NDMI 2029
                with rasterio.open("tif/output_ndmi2029kpy.tif") as src:
                    data_2029_pred = src.read(1)
                    bounds_2029 = src.bounds
                    height, width = data_2029_pred.shape
                    x_pred_29 = np.linspace(bounds_2029.left, bounds_2029.right, width)
                    y_pred_29 = np.linspace(bounds_2029.bottom, bounds_2029.top, height)
                    data_2029_pred = np.flipud(data_2029_pred)
                    data_2029_pred = process_raster_data_with_threshold(
                        data_2029_pred, thresholds["proyeksi_2029"]
                    )

                colorscale = [
                    [0.0, "rgb(148, 137, 121)"],
                    [0.33, "rgb(255, 255, 224)"],
                    [0.67, "rgb(173, 216, 230)"],
                    [1.0, "rgb(0, 0, 139)"],
                ]

                fig = make_subplots(
                    rows=1,
                    cols=3,
                    subplot_titles=[
                        "Aktual NDBI 2024",
                        "Proyeksi NDBI 2024",
                        "Proyeksi NDBI 2029",
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
                        "color": "rgb(148, 137, 121)",
                    },
                    {
                        "name": "Rendah",
                        "color": "rgb(255, 255, 224)",
                    },
                    {
                        "name": "Sedang",
                        "color": "rgb(173, 216, 230)",
                    },
                    {
                        "name": "Tinggi",
                        "color": "rgb(0, 0, 139)",
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

    st.badge(
        "**Tabel Perbandingan Sampel Nilai NDMI Aktual dan Proyeksi**",
        color="primary",
    )

    col_sampel_perbandingan = st.columns(1)
    with col_sampel_perbandingan[0]:
        csv_path = "csv/ndmiSampelModel.csv"

        try:
            df = pd.read_csv(csv_path)

            def format_ndmi_value(value):
                try:
                    return f"{float(value):.3f}"
                except:
                    return str(value)

            def convert_df_to_html_ndmi(input_df):
                formatters = {}
                for col in input_df.columns:
                    if (
                        "ndmi" in col.lower()
                        or "aktual" in col.lower()
                        or "proyeksi" in col.lower()
                    ):
                        formatters[col] = format_ndmi_value

                return input_df.to_html(
                    escape=False,
                    formatters=formatters,
                    table_id="ndmi-sample-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html_ndmi(df)

            st.markdown(
                """
                <style>
                #ndmi-sample-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 0px 0 10px 0; 
                    font-family: 'Poppins', sans-serif;
                    margin-top: -15px;
                    margin-bottom: 15px;
                }
                #ndmi-sample-table th, #ndmi-sample-table td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: center; 
                    vertical-align: middle; 
                    font-size: 14px;
                }
                #ndmi-sample-table th { 
                    background-color: #E4EFE7; 
                    font-weight: bold; 
                    color: #333;
                }
                #ndmi-sample-table td:not(:first-child) {
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
            st.error(f"Error dalam menampilkan tabel sampel NDMI: {str(e)}")

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
            - [1] Nurdin, Suarna, N., Prihartono, W. (2025). Algoritma Regresi Linier untuk Prediksi Penggunaan Volume Air Berdasarkan Jenis Pelanggan PDAM. *Jurnal Kecerdasan Buatan dan Teknologi Informasi*, 4(1). 43-52. https://doi.org/10.69916/jkbti.v4i1.187
            - [2] Man, A., Chaichana, C., Wicharuck, S., Rinchumphu, D. (2022). *Predicting Sunlight Availability for Vertical Shelves using Simulation*. *IOP Conference Series: Earth and Environmental Science*. 1094 012011. https://doi.org/10.1088/1755-1315/1094/1/012011
            """
        )
