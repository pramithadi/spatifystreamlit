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


# ==============================================================================
# DEKLARASI FUNGSI
# ==============================================================================
@st.cache_data
def load_aoi_data():
    """
    Load CSV Statistik Penutup Lahan di AOI (KPY dan Sekitarnya).
    """
    csv_path = "./csv/luasPenutupLahanAOI.csv"
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        st.error(f"File CSV tidak ditemukan: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error membaca file CSV: {str(e)}")
        return pd.DataFrame()


@st.cache_data
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


@st.cache_data
def get_aoi_by_year(df, year):
    """
    Filter Penutup Lahan AOI Berdasarkan Tahun.
    """
    if df.empty:
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


@st.cache_data
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


@st.cache_data
def get_kec_list(df):
    """
    Get List Nama Kecamatan Berdasarkan NAMOBJ.
    """
    if df.empty:
        return []

    return sorted(df["NAMOBJ"].unique().tolist())


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
        gdf = gpd.read_file(shapefile_path)

        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        def create_tooltip_text(row):
            namobj = row.get("NAMOBJ", "Unknown")
            wadmkk = row.get("WADMKK", "")

            if "Sleman" in wadmkk or "Bantul" in wadmkk:
                return f"Kapanewon {namobj}"
            elif "Yogyakarta" in wadmkk:
                return f"Kemantren {namobj}"
            else:
                return namobj

        gdf["tooltip_text"] = gdf.apply(create_tooltip_text, axis=1)
        geojson_data = gdf.to_json()

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
        )

        geojson_layer.add_to(map_obj)
        return True
    except Exception as e:
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


def add_tiff_to_map(map_obj, tif_path):
    """
    Menambahkan GeoTiff Penutup Lahan ke Peta Folium.
    """
    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds

            if hasattr(src, "nodata") and src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)

            # Warna Penutup Lahan (RGBA)
            colors = {
                0: [41, 75, 41, 255],  # 294b29 - Vegetasi
                1: [105, 195, 221, 255],  # 69c3dd - Tubuh Air
                2: [205, 154, 77, 255],  # cd9a4d - Lahan Terbangun
                3: [250, 245, 217, 255],  # faf5d9 - Lahan Terbuka
            }

            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
            valid_mask = ~np.isnan(data)

            for class_value, color in colors.items():
                class_mask = valid_mask & (data == class_value)
                colored_data[class_mask] = color

            colored_data[~valid_mask] = [0, 0, 0, 0]

            img = Image.fromarray(colored_data, "RGBA")

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            bounds_folium = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            pl_overlay = folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_folium,
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
                name="Penutup Lahan",
            )
            pl_overlay.add_to(map_obj)

        return True
    except Exception as e:
        return False


@st.cache_data
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
            return f"{trend_type} akan **naik {change_pct:.1f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        elif change_pct < 0:
            return f"{trend_type} akan **turun {abs(change_pct):.1f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        else:
            return f"{trend_type} akan **stabil** di **{area_2024:.1f} km²** pada tahun 2029"

    markdown_tren = f"""
    💡**Quick Insight**\n
    **Perubahan Luas Penutup Lahan**\n
    :green-background[**Vegetasi**:]
    - Turun **{abs(pct_change_vegetasi_hist):.1f}%**, dari **{data_1999['vegetasi_km2']:.1f} km²** (1999) menjadi **{data_2024['vegetasi_km2']:.1f} km²** (2024).
    - {get_trend_description(pct_change_vegetasi_pred, data_2024['vegetasi_km2'], data_2029['vegetasi_km2'], "Diprediksi")}.\n
    :green-background[**Tubuh air**:]
    - Turun **{abs(pct_change_tubuh_air_hist):.1f}%**, dari **{data_1999['tubuh_air_km2']:.1f} km²** (1999) menjadi **{data_2024['tubuh_air_km2']:.1f} km²** (2024).
    - {get_trend_description(pct_change_tubuh_air_pred, data_2024['tubuh_air_km2'], data_2029['tubuh_air_km2'], "Diprediksi")}.\n
    :green-background[**Lahan terbangun**:]
    - Naik **{pct_change_terbangun_hist:.1f}%**, dari **{data_1999['lahan_terbangun_km2']:.1f} km²** (1999) menjadi **{data_2024['lahan_terbangun_km2']:.1f} km²** (2024).
    - {get_trend_description(pct_change_terbangun_pred, data_2024['lahan_terbangun_km2'], data_2029['lahan_terbangun_km2'], "Diprediksi")}.\n
    :green-background[**Lahan terbuka**:]
    - Naik **{pct_change_terbuka_hist:.1f}%**, dari **{data_1999['lahan_terbuka_km2']:.1f} km²** (1999) menjadi **{data_2024['lahan_terbuka_km2']:.1f} km²** (2024).
    - {get_trend_description(pct_change_terbuka_pred, data_2024['lahan_terbuka_km2'], data_2029['lahan_terbuka_km2'], "Diprediksi")}.
    """

    return markdown_tren


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

penutup_lahan_df = load_aoi_data()
penutup_lahan_kec_df = load_kec_data()

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
    st.badge(
        "**Peta Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )

    col1_peta, col2_peta_query = st.columns([3, 1])
    with col2_peta_query:
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = get_aoi_by_year(penutup_lahan_df, option)

        with st.container(border=True):
            list_kec = get_kec_list(penutup_lahan_kec_df)

            selected_kecamatan = st.selectbox(
                "**Cari Kecamatan**",
                [""] + list_kec,
                index=0,
                placeholder="Ketik atau pilih kecamatan",
            )

        # Container Quick Insight
        if selected_kecamatan:
            with st.container(border=True):
                st.write("💡**Quick Insight**")

                kec_data = get_kec_by_year_name(
                    penutup_lahan_kec_df, option, selected_kecamatan
                )

                if kec_data:
                    jenis_kec = get_region_type(kec_data["wadmkk"])

                    st.write(
                        f"Persentase penutup lahan di :green-background[**{jenis_kec} {selected_kecamatan}**] pada tahun :green-background[**{option}**] yakni:"
                    )
                    st.write(
                        f"• Vegetasi: :green-background[**{kec_data['vegetasi_pct']:.2f}%**]"
                    )
                    st.write(
                        f"• Tubuh Air: :green-background[**{kec_data['tubuh_air_pct']:.2f}%**]"
                    )
                    st.write(
                        f"• Lahan Terbangun: :green-background[**{kec_data['lahan_terbangun_pct']:.2f}%**]"
                    )
                    st.write(
                        f"• Lahan Terbuka: :green-background[**{kec_data['lahan_terbuka_pct']:.2f}%**]"
                    )

                    # Kesimpulan
                    classes_kec = {
                        "vegetasi": kec_data["vegetasi_pct"],
                        "tubuh air": kec_data["tubuh_air_pct"],
                        "lahan terbangun": kec_data["lahan_terbangun_pct"],
                        "lahan terbuka": kec_data["lahan_terbuka_pct"],
                    }
                    dominan_kec = max(classes_kec, key=classes_kec.get)

                    # Pengkondisian untuk tahun 2029
                    if str(option) == "2029":
                        st.write(
                            f"**Kesimpulan**: {jenis_kec} {selected_kecamatan} :green-background[**diprediksi akan didominasi**] oleh :green-background[**{dominan_kec}**]."
                        )
                    else:
                        st.write(
                            f"**Kesimpulan**: {jenis_kec} {selected_kecamatan} :green-background[**didominasi**] oleh :green-background[**{dominan_kec}**]."
                        )
                else:
                    st.write(
                        "Data tidak tersedia untuk kecamatan dan tahun yang dipilih."
                    )

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
            tiles="OpenStreetMap",
            name="OpenStreetMap",
            overlay=False,
            control=True,
        ).add_to(m)

        # Panggil GeoTiff Penutup Lahan
        tif_path = f"tif/pl{option}kpy.tif"

        # Cek Ketersediaan Data kemudian Tampilkan ke Peta
        if os.path.exists(tif_path):
            add_tiff_to_map(m, tif_path)
        else:
            st.warning(f"File GeoTIFF tidak ditemukan: {tif_path}")

        # Cek Ketersediaan Shapefile Batas AOI
        shapefile_path = "shp/aoi_kpy.shp"
        if os.path.exists(shapefile_path):
            add_shp_to_map(m, shapefile_path)
        else:
            st.warning(f"File Shapefile tidak ditemukan: {shapefile_path}")

        # Tambahkan Legenda ke Peta
        add_legend(m)

        folium.LayerControl(position="topleft", collapsed=True).add_to(m)

        # Custom CSS Peta Folium
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
        st_data = st_folium(m, use_container_width=True, height=800)

# ==============================================================================
# SECTION 2: TREN
# ==============================================================================
with tab2:
    years = [1999, 2004, 2009, 2014, 2019, 2024, 2029]
    tren_data = []

    for year in years:
        year_data = get_aoi_by_year(penutup_lahan_df, str(year))
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
    col1_tren_main, col2_tren_main = st.columns([2.5, 1.5])

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
                    dtick=10,  # Interval
                    tickvals=list(range(0, 101, 10)),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=10, r=10, t=10, b=80),
                height=653,
                font=dict(family="Poppins", size=12),
            )

            # Menampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(generate_quick_insight(penutup_lahan_df))

# ==============================================================================
# SECTION 3: VALIDASI
# ==============================================================================


# Fungsi untuk Membuat Matriks Konfusi
def create_confusion_matrix(df):
    y_true = df["PL Referensi"]
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

    # Expander Tabel
    with st.expander(f"**📍 Tabel Sampel Penutup Lahan {year}**"):
        try:

            def path_to_image_html(path):
                img_width, img_height = (80, 100) if year == "2024" else (100, 80)

                base64_img = get_base64_encoded_image(path)
                if base64_img:
                    mime_type = (
                        "jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "png"
                    )
                    return f'<img src="data:image/{mime_type};base64,{base64_img}" width="{img_width}" height="{img_height}" style="object-fit: cover; border-radius: 2px;">'
                return "❌ Foto tidak ditemukan."

            def convert_df_to_html_local(input_df):
                return input_df.to_html(
                    escape=False,
                    formatters=dict(Foto=path_to_image_html),
                    table_id="validasi-table",
                    classes="table table-striped",
                    index=False,
                )

            df = pd.read_csv(csv_path)

            def create_image_path(kode):
                kode_prefix = kode[:5].lower()
                if year == "2024":
                    return f"img/img_val_{year}/{kode_prefix}24.JPG"
                elif year == "2019":
                    return f"img/img_val_{year}/{kode_prefix}19.png"
                else:
                    return f"img/img_val_{year}/{kode_prefix}14.png"

            df["Foto"] = df["Kode"].apply(create_image_path)
            html_table = convert_df_to_html_local(df)

            st.markdown(
                """
                <style>
                #validasi-table { width: 100%; border-collapse: collapse; margin: 0px 0 10px 0; }
                #validasi-table th, #validasi-table td { border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; }
                #validasi-table th { background-color: #E4EFE7; font-weight: bold; }
                #validasi-table img { margin: 0 auto; border-radius: 4px; display: block; }
                .stExpander > div > div > div > div { padding-top: 0rem !important; }
                </style>
                <div style="margin-top: -20px;"></div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(html_table, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error(f"File '{csv_path}' tidak ditemukan!")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")


with tab3:
    st.badge(
        "**Uji Akurasi di Penutup Lahan Kawasan Perkotaan Yogyakarta dan Sekitarnya**",
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
        "**Evaluasi Model Prediksi Cellular Automata-Markov Chain dan XGBoost**",
        color="primary",
    )

    col1_metrik_img, col2_metrik_insight = st.columns([1.7, 2.3])
    with col1_metrik_img:
        with st.container(border=True):
            fig = go.Figure(
                data=[
                    go.Bar(
                        name="Akurasi Keseluruhan",
                        x=["Akurasi Keseluruhan"],
                        y=[0.8963],
                        text=["0.8963"],
                        textposition="outside",
                        marker_color="#DEE8CE",
                        textfont=dict(family="Poppins", size=12, color="black"),
                    ),
                    go.Bar(
                        name="Koefisien Kappa",
                        x=["Koefisien Kappa"],
                        y=[0.8351],
                        text=["0.8351"],
                        textposition="outside",
                        marker_color="#BB6653",
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
                margin=dict(l=20, r=20, t=20, b=60),
                height=263,
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
                - :green-background[**Akurasi**] model prediksi penutup lahan menunjukkan angka yang :green-background[**tinggi**] sebesar :green-background[**89.63%**] setelah dilakukan validasi dengan data aktual terkini.
                - :green-background[**Koefisien kappa**] sebesar :green-background[**83.51%**] masuk ke dalam kategori :green-background[**almost perfect agreement**⁽¹⁾], menunjukkan tingkat kesepakatan yang :green-background[**sangat baik**].
                """,
                unsafe_allow_html=True,
            )
            st.success(
                "✅ Model **LAYAK** untuk prediksi perubahan penutup lahan 2029."
            )

    st.badge(
        "**Classification Report**",
        color="primary",
    )
    col2_classification_report, col2_report_insight = st.columns([2.3, 1.7])
    with col2_classification_report:
        with st.container(border=True):
            classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]
            precision = [0.83, 0.30, 0.77, 0.44]
            recall = [0.94, 0.44, 0.78, 0.08]
            f1_score = [0.88, 0.36, 0.77, 0.14]

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
                plot_bgcolor="#fdfaf6",
                paper_bgcolor="#fdfaf6",
                margin=dict(l=40, r=40, t=40, b=80),
                showlegend=True,
                barmode="group",
                height=407,
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")

            st.plotly_chart(fig, use_container_width=True)

    with col2_report_insight:
        with st.container(border=True):
            with st.expander("📐**Penjelasan Metrik**"):
                st.markdown(
                    f"""
                        - **Precision**: Dari semua yang diprediksi sebagai kelas X, berapa % yang benar?
                        - **Recall**: Dari semua kelas X yang sebenarnya ada, berapa % yang berhasil ditemukan?
                        - **F1-Score**: Nilai gabungan Precision & Recall (semakin mendekati 1, maka model semakin baik)⁽²⁾
                    """,
                    unsafe_allow_html=True,
                )

        with st.container(border=True):
            st.write("💡**Quick Insight**")
            st.markdown(
                f"""
                - :green-background[**Vegetasi**] dan :green-background[**Lahan Terbangun**] menunjukkan :green-background[**performa terbaik**] dengan :green-background[**F1-Score tinggi**] (**0.88** dan **0.77**) yang mengindikasikan :green-background[**model dapat mengidentifikasi**] kedua kelas ini dengan baik.
                - :green-background[**Tubuh Air**] dan :green-background[**Lahan Terbuka**] memiliki :green-background[**performa rendah**] (F1-Score :green-background[**0.36**] dan :green-background[**0.14**]), menunjukkan :green-background[**model kesulitan membedakan**] kedua kelas tersebut. Hal ini mungkin disebabkan oleh :green-background[**keterbatasan data training**] atau :green-background[**kemiripan spektral**] dengan kelas lain.
                """,
                unsafe_allow_html=True,
            )

    st.badge(
        "**Perbandingan Visual Peta Penutup Lahan Aktual vs Prediksi**",
        color="primary",
    )

    col_peta_perbandingan = st.columns(1)
    with col_peta_perbandingan[0]:
        with st.container(border=True):
            try:

                def process_raster_data(data):
                    data = data.astype("float32")
                    data[data > 3] = np.nan  # Nilai > 3 NoData
                    data[data < 0] = np.nan  # Nilai < 0 NoData
                    return data

                with rasterio.open("tif/pl2024kpy.tif") as src:
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
                    data_2024_actual = process_raster_data(data_2024_actual)

                with rasterio.open("tif/prediksi_pl2024kpy.tif") as src:
                    data_2024_pred = src.read(1)
                    bounds_pred = src.bounds
                    height, width = data_2024_pred.shape
                    x_pred_24 = np.linspace(bounds_pred.left, bounds_pred.right, width)
                    y_pred_24 = np.linspace(bounds_pred.bottom, bounds_pred.top, height)
                    data_2024_pred = np.flipud(data_2024_pred)
                    data_2024_pred = process_raster_data(data_2024_pred)

                with rasterio.open("tif/pl2029kpy.tif") as src:
                    data_2029_pred = src.read(1)
                    bounds_2029 = src.bounds
                    height, width = data_2029_pred.shape
                    x_pred_29 = np.linspace(bounds_2029.left, bounds_2029.right, width)
                    y_pred_29 = np.linspace(bounds_2029.bottom, bounds_2029.top, height)
                    data_2029_pred = np.flipud(data_2029_pred)
                    data_2029_pred = process_raster_data(data_2029_pred)

                colorscale = [
                    [0.0, "rgb(41, 75, 41)"],  # Vegetasi
                    [0.33, "rgb(105, 195, 221)"],  # Tubuh Air
                    [0.67, "rgb(205, 154, 77)"],  # Lahan Terbangun
                    [1.0, "rgb(250, 245, 217)"],  # Lahan Terbuka
                ]

                fig = make_subplots(
                    rows=1,
                    cols=3,
                    subplot_titles=["Aktual 2024", "Prediksi 2024", "Prediksi 2029"],
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
                    {"name": "Vegetasi", "color": "rgb(41, 75, 41)"},
                    {"name": "Tubuh Air", "color": "rgb(105, 195, 221)"},
                    {"name": "Lahan Terbangun", "color": "rgb(205, 154, 77)"},
                    {"name": "Lahan Terbuka", "color": "rgb(250, 245, 217)"},
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
                    height=462,
                    showlegend=True,
                    font=dict(family="Poppins, sans-serif", size=12, color="black"),
                    plot_bgcolor="#fdfaf6",
                    paper_bgcolor="#fdfaf6",
                    margin=dict(l=50, r=50, t=30, b=50),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.1,
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

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
            - [1] Viera, A. J., & Garrett, J. M. (2005). Understanding Interobserver Agreement: The Kappa Statistic. *Family Medicine*, 37(5). 360-363.
            - [2] Bobbitt, Z. (2022). *How to Interpret the Classification Report in sklearn (With Example)*. (*https://www.statology.org/sklearn-classification-report/,* diakses 19 Agustus 2025).
            """
        )
