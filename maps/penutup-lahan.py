import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import rasterio
import os
import base64
from io import BytesIO
from PIL import Image
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="Dashboard Penutup Lahan",
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
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
        
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


# Function untuk Load Data Penutup Lahan dari CSV
@st.cache_data
def load_aoi_data():
    """
    Load Statistik Penutup Lahan AOI dari File CSV
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


# Function untuk Load Data Penutup Lahan Kecamatan dari CSV
@st.cache_data
def load_kec_data():
    """
    Load Statistik Penutup Lahan Kecamatan dari File CSV
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


# Function untuk Get Sebutan Wilayah Berdasarkan WADMKK
def get_region_type(wadmkk):
    """
    Tentukan Sebutan Wilayah Berdasarkan WADMKK
    """
    if "Bantul" in wadmkk or "Sleman" in wadmkk:
        return "Kapanewon"
    elif "Yogyakarta" in wadmkk:
        return "Kemantren"
    else:
        return ""


# Function untuk Get Data Penutup Lahan Berdasarkan Tahun
def get_aoi_by_year(df, year):
    """
    Filter Data Penutup Lahan Berdasarkan Tahun (berdasarkan baris)
    Asumsi: baris 1=1999, baris 2=2004, dst.
    """
    if df.empty:
        return {}

    # Mapping Tahun ke Index Baris (0-based)
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
        "vegetasi_pct": row_data.get("vegetasi_pct", 0),
        "tubuh_air_pct": row_data.get("tubuh_air_pct", 0),
        "lahan_terbangun_pct": row_data.get("lahan_terbangun_pct", 0),
        "lahan_terbuka_pct": row_data.get("lahan_terbuka_pct", 0),
        "vegetasi_km2": row_data.get("vegetasi_km2", 0),
        "tubuh_air_km2": row_data.get("tubuh_air_km2", 0),
        "lahan_terbangun_km2": row_data.get("lahan_terbangun_km2", 0),
        "lahan_terbuka_km2": row_data.get("lahan_terbuka_km2", 0),
        "total_luas_km2": row_data.get("total_luas_km2", 791.07),
    }


# Function untuk Get Data Penutup Lahan Kecamatan Berdasarkan Tahun dan Nama
def get_kec_by_year_name(df, year, namobj):
    """
    Filter Data Penutup Lahan Kecamatan Berdasarkan Tahun dan Nama Kecamatan
    """
    if df.empty or not namobj:
        return {}

    # Filter Data Berdasarkan Tahun dan Nama Objek
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


# Function untuk Get List Kecamatan dari Data
def get_kec_list(df):
    """
    Ambil List Nama Kecamatan yang Unik dari Data
    """
    if df.empty:
        return []

    return sorted(df["NAMOBJ"].unique().tolist())


# Function untuk Menambahkan SHP Batas Administrasi ke Peta Folium
def add_shp_to_map(map_obj, shapefile_path):
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


# Function untuk Menambahkan Legenda Penutup Lahan ke Peta Folium
def add_legend(map_obj):
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


# Function untuk Menambahkan GeoTiff Penutup Lahan ke Peta Folium
def add_tiff_to_map(map_obj, tif_path):
    try:
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds

            if hasattr(src, "nodata") and src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)

            # Warna untuk Setiap Kelas Penutup Lahan (RGBA)
            colors = {
                0: [41, 75, 41, 255],  # 294b29 - Vegetasi
                1: [105, 195, 221, 255],  # 69c3dd - Tubuh Air
                2: [205, 154, 77, 255],  # cd9a4d - Lahan Terbangun
                3: [250, 245, 217, 255],  # faf5d9 - Lahan Terbuka
            }

            colored_data = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
            valid_mask = ~np.isnan(data)

            # Klasifikasi Berdasarkan Nilai Pixel
            for class_value, color in colors.items():
                class_mask = valid_mask & (data == class_value)
                colored_data[class_mask] = color

            # Set Area yang Tidak Valid dengan Warna Transparan
            colored_data[~valid_mask] = [0, 0, 0, 0]

            # Konversi ke PIL Image
            img = Image.fromarray(colored_data, "RGBA")

            # Konversi ke Base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Bounds untuk Folium
            bounds_folium = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            # Tambahkan ke Peta
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


# Function To Generate Quick Insight Markdown From CSV Data (Academic Version)
def generate_quick_insight_markdown(penutup_lahan_df):
    """
    Function To Generate Quick Insight Markdown From DataFrame (Academic Version)

    Args:
        penutup_lahan_df: DataFrame With Land Cover Data

    Returns:
        str: Markdown String For Quick Insight
    """

    # Filter Data For Year 1999, 2024, and 2029
    data_1999 = penutup_lahan_df.iloc[0]  # First Row (1999)
    data_2024 = penutup_lahan_df.iloc[5]  # Sixth Row (2024)
    data_2029 = penutup_lahan_df.iloc[6]  # Seventh Row (2029)

    # Calculate percentage changes between periods
    def calculate_percentage_change(old_value, new_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    # Calculate historical changes (1999-2024)
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

    # Calculate prediction changes (2024-2029)
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

    # Helper function to format trend text
    def get_trend_description(
        change_pct, area_2024, area_2029, trend_type="diprediksi"
    ):
        if change_pct > 0:
            return f"{trend_type} akan **naik {change_pct:.1f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        elif change_pct < 0:
            return f"{trend_type} akan **turun {abs(change_pct):.1f}%** dari **{area_2024:.1f} km²** menjadi **{area_2029:.1f} km²** pada tahun 2029"
        else:
            return f"{trend_type} akan **stabil** di **{area_2024:.1f} km²** pada tahun 2029"

    # Generate Markdown Content (Concise Version with Years)
    markdown_content = f"""
💡**Quick Insight**\n
**Perubahan Luas Penutup Lahan**
- **Vegetasi**: turun **{abs(pct_change_vegetasi_hist):.1f}%**, dari **{data_1999['vegetasi_km2']:.1f} km²** (1999) menjadi **{data_2024['vegetasi_km2']:.1f} km²** (2024), {get_trend_description(pct_change_vegetasi_pred, data_2024['vegetasi_km2'], data_2029['vegetasi_km2'], "dan diprediksi")}.
- **Tubuh air**: turun **{abs(pct_change_tubuh_air_hist):.1f}%**, dari **{data_1999['tubuh_air_km2']:.1f} km²** (1999) menjadi **{data_2024['tubuh_air_km2']:.1f} km²** (2024), {get_trend_description(pct_change_tubuh_air_pred, data_2024['tubuh_air_km2'], data_2029['tubuh_air_km2'], "dan diprediksi")}.
- **Lahan terbangun**: naik **{pct_change_terbangun_hist:.1f}%**, dari **{data_1999['lahan_terbangun_km2']:.1f} km²** (1999) menjadi **{data_2024['lahan_terbangun_km2']:.1f} km²** (2024), {get_trend_description(pct_change_terbangun_pred, data_2024['lahan_terbangun_km2'], data_2029['lahan_terbangun_km2'], "dan diprediksi")}.
- **Lahan terbuka**: naik **{pct_change_terbuka_hist:.1f}%**, dari **{data_1999['lahan_terbuka_km2']:.1f} km²** (1999) menjadi **{data_2024['lahan_terbuka_km2']:.1f} km²** (2024), {get_trend_description(pct_change_terbuka_pred, data_2024['lahan_terbuka_km2'], data_2029['lahan_terbuka_km2'], "dan diprediksi")}.
"""

    return markdown_content


# Load Data Penutup Lahan
penutup_lahan_df = load_aoi_data()
penutup_lahan_kec_df = load_kec_data()

st.subheader("Dashboard Penutup Lahan")

selected_tab = st.pills(
    "**Lihat Analisis:**",
    [
        "🗺️ Peta",
        "📈 Tren",
        "✅ Validasi",
        "⚙️ Model",
    ],
    selection_mode="single",
    default="🗺️ Peta",
)

# Peta
if selected_tab == "🗺️ Peta":
    col1_peta, col2_peta = st.columns([2.6, 1.4])

    with col2_peta:
        # Container Selectbox Tahun
        with st.container(border=True):
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024", "2029"],
                index=0,
                placeholder="Tahun",
            )

            selected_data = get_aoi_by_year(penutup_lahan_df, option)

        # Container Metrics Penutup Lahan
        st.write("**Persentase Penutup Lahan di KPY dan Sekitarnya**")
        if selected_data:
            col1_metric, col2_metric = st.columns([1, 1])
            col3_metric, col4_metric = st.columns([1, 1])

            with col1_metric:
                with st.container(border=True):
                    st.metric("Vegetasi", f"{selected_data['vegetasi_pct']:.2f}%")
            with col2_metric:
                with st.container(border=True):
                    st.metric("Tubuh Air", f"{selected_data['tubuh_air_pct']:.2f}%")

            with col3_metric:
                with st.container(border=True):
                    st.metric(
                        "Lahan Terbangun",
                        f"{selected_data['lahan_terbangun_pct']:.2f}%",
                    )
            with col4_metric:
                with st.container(border=True):
                    st.metric(
                        "Lahan Terbuka", f"{selected_data['lahan_terbuka_pct']:.2f}%"
                    )

        # Container Selectbox Kecamatan
        with st.container(border=True):
            # Get List Kecamatan dari Data
            list_kecamatan = get_kec_list(penutup_lahan_kec_df)

            selected_kecamatan = st.selectbox(
                "**Cari Kecamatan**",
                [""] + list_kecamatan,
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
                    # Tentukan Jenis Kecamatan
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

                    # Kesimpulan Dominasi
                    classes_kec = {
                        "vegetasi": kec_data["vegetasi_pct"],
                        "tubuh air": kec_data["tubuh_air_pct"],
                        "lahan terbangun": kec_data["lahan_terbangun_pct"],
                        "lahan terbuka": kec_data["lahan_terbuka_pct"],
                    }
                    dominan_kec = max(classes_kec, key=classes_kec.get)

                    st.write(
                        f"**Kesimpulan**: {jenis_kec} {selected_kecamatan} :green-background[**didominasi**] oleh :green-background[**{dominan_kec}**]."
                    )
                else:
                    st.write(
                        "Data tidak tersedia untuk kecamatan dan tahun yang dipilih."
                    )

    with col1_peta:
        # Buat Peta Folium
        m = folium.Map(
            location=[-7.764326411862208, 110.3721676814108],
            zoom_start=10.5,
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
            tiles="OpenStreetMap",
            name="OpenStreetMap",
            overlay=False,
            control=True,
        ).add_to(m)

        # Panggil GeoTiff Penutup Lahan
        tif_path = f"tif/pl{option}kpy.tif"

        # Cek Ketersediaan GeoTiff dan Tampilkan ke Peta
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

        # Tambahkan Control Layer
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
        st_data = st_folium(m, use_container_width=True, height=803)

elif selected_tab == "📈 Tren":
    # Grafik Tren Penutup Lahan AOI

    # Buat Data Tren dari DataFrame AOI
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
        "**Tren Penutup Lahan Kawasan Perkotaan Yogyakarta dan Sekitarnya (1999-2029)**",
        color="primary",
    )
    col1_tren_main, col2_tren_main = st.columns([2.4, 1.6])

    with col1_tren_main:
        # Container Grafik Tren
        with st.container(border=True):
            # Buat Grafik
            fig = go.Figure()

            # Warna Sesuai Legenda Peta
            colors = {
                "Vegetasi": "#294b29",  # Hijau Tua
                "Tubuh Air": "#69c3dd",  # Biru
                "Lahan Terbangun": "#cd9a4d",  # Coklat
                "Lahan Terbuka": "#aaa68f",  # Coklat Muda (modifikasi dari #faf5d9 supaya warnanya lebih terlihat)
            }

            # Tambahkan Line untuk Setiap Kelas
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

            # Update Layout Grafik
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
                ),
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    font=dict(family="Poppins", size=12, color="black"),
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                height=480,
                font=dict(family="Poppins", size=12),
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(generate_quick_insight_markdown(penutup_lahan_df))

elif selected_tab == "✅ Validasi":
    # Validasi Data 2014
    st.subheader("**Uji Akurasi Penutup Lahan Tahun 2014**")
    with st.container(border=True):
        st.write("**Matriks Konfusi Penutup Lahan Tahun 2014**")

        # Tambahkan matriks konfusi ilmiah di sini
        try:
            df = pd.read_csv("csv/validasiPL2014.csv")

            # Fungsi untuk membuat matriks konfusi ilmiah
            def create_confusion_matrix(df):
                from sklearn.metrics import (
                    confusion_matrix,
                    accuracy_score,
                    cohen_kappa_score,
                )
                import numpy as np

                y_true = df["PL Referensi"]
                y_pred = df["PL Aktual"]

                # Gunakan urutan kelas yang sudah ditentukan
                classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]
                # Filter hanya kelas yang ada di data
                classes = [
                    cls
                    for cls in classes
                    if cls in y_true.values or cls in y_pred.values
                ]

                cm = confusion_matrix(y_true, y_pred, labels=classes)
                n_total = np.sum(cm)

                row_totals = np.sum(cm, axis=1)
                col_totals = np.sum(cm, axis=0)

                # Producer's Accuracy = diagonal / row total
                producer_acc = np.diag(cm) / row_totals * 100

                # User's Accuracy = diagonal / column total
                user_acc = np.diag(cm) / col_totals * 100

                # Overall Accuracy
                overall_acc = np.sum(np.diag(cm)) / n_total * 100

                # Kappa Accuracy
                kappa = cohen_kappa_score(y_true, y_pred) * 100

                # Errors
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

            def display_confusion_matrix_html(results):
                cm = results["cm"]
                classes = results["classes"]
                row_totals = results["row_totals"]
                col_totals = results["col_totals"]
                producer_acc = results["producer_acc"]
                user_acc = results["user_acc"]
                commission_error = results["commission_error"]
                omission_error = results["omission_error"]
                overall_acc = results["overall_acc"]
                kappa = results["kappa"]
                n_total = results["n_total"]

                html_content = """
                <style>
                .conf-matrix {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-family: Arial, sans-serif;
                    font-size: 13px;
                    border: 2px solid #333;
                }}
                .conf-matrix th {{
                    background: #E4EFE7;
                    border: 1px solid #333;
                    padding: 10px 6px;
                    text-align: center;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix td {{
                    border: 1px solid #333;
                    padding: 8px 6px;
                    text-align: center;
                    background: white;
                }}
                .conf-matrix .header-main {{
                    background: #E4EFE7;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix .diagonal {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                .conf-matrix .important {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                </style>
                
                <table class="conf-matrix">
                    <thead>
                        <tr>
                            <th rowspan="2" class="header-main">Data Hasil<br/>Klasifikasi</th>
                            <th colspan="{num_classes}" class="header-main">Data Uji Klasifikasi (Referensi)</th>
                            <th rowspan="2" class="header-main">Total<br/>Baris</th>
                            <th rowspan="2" class="header-main">Producer<br/>Accuracy<br/>(%)</th>
                            <th rowspan="2" class="header-main">Kesalahan<br/>Omisi<br/>(%)</th>
                        </tr>
                        <tr>
                """.format(
                    num_classes=len(classes)
                )

                # Add class headers
                for cls in classes:
                    html_content += '<th class="header-main">{}</th>'.format(cls)

                html_content += "</tr></thead><tbody>"

                # Add data rows
                for i, cls in enumerate(classes):
                    html_content += '<tr><td class="header-main">{}</td>'.format(cls)

                    # Add confusion matrix values
                    for j in range(len(classes)):
                        cell_class = "diagonal" if i == j else ""
                        html_content += '<td class="{}">{}</td>'.format(
                            cell_class, cm[i][j]
                        )

                    # Add row total, producer accuracy, omission error
                    html_content += """
                    <td>{row_total}</td>
                    <td>{producer_acc:.1f}</td>
                    <td>{omis_err:.1f}</td>
                    </tr>""".format(
                        row_total=row_totals[i],
                        producer_acc=producer_acc[i],
                        omis_err=omission_error[i],
                    )

                # Add totals row
                html_content += '<tr><td class="header-main">Total Kolom</td>'
                for total in col_totals:
                    html_content += "<td>{}</td>".format(total)
                html_content += "<td>{}</td><td>-</td><td>-</td></tr>".format(n_total)

                # Add user accuracy row
                html_content += '<tr><td class="header-main">User Accuracy (%)</td>'
                for acc in user_acc:
                    html_content += "<td>{:.1f}</td>".format(acc)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add commission error row
                html_content += '<tr><td class="header-main">Kesalahan Komisi (%)</td>'
                for error in commission_error:
                    html_content += "<td>{:.1f}</td>".format(error)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add overall accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Overall Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{overall_acc:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>""".format(
                    num_classes=len(classes), overall_acc=overall_acc
                )

                # Add kappa accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Kappa Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{kappa:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>
                </tbody></table>""".format(
                    num_classes=len(classes), kappa=kappa
                )

                return html_content

            # Hitung dan tampilkan matriks konfusi
            results = create_confusion_matrix(df)

            # # Tampilkan metrics summary
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     st.metric("Total Sampel", results["n_total"])
            # with col2:
            #     st.metric("Akurasi yang Diharapkan", f"85%")
            # with col3:
            #     st.metric("Overall Accuracy", f"{results['overall_acc']:.2f}%")
            # with col4:
            #     st.metric("Kappa Accuracy", f"{results['kappa']:.2f}%")

            # Tampilkan matriks konfusi
            html_content = display_confusion_matrix_html(results)
            st.markdown(html_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error dalam membuat matriks konfusi: {str(e)}")

    with st.expander("**Tabel Sampel Validasi Tahun 2014**"):
        try:
            df = pd.read_csv("csv/validasiPL2014.csv")
            # foto_path = "img/31veg2014.png"

            def get_base64_encoded_image(image_path):
                try:
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except Exception as e:
                    return None

            def path_to_image_html(path):
                base64_img = get_base64_encoded_image(path)
                if base64_img:
                    return f'<img src="data:image/png;base64,{base64_img}" width="100" height="80" style="object-fit: cover; border-radius: 2px;">'
                else:
                    return "❌ Foto tidak ditemukan."

            def create_image_path(kode):
                kode_prefix = kode[:5].lower()
                return f"img/img_val_2014/{kode_prefix}14.png"

            # Tambahkan kolom Foto berdasarkan kode masing-masing
            df["Foto"] = df["Kode"].apply(create_image_path)

            @st.cache_data
            def convert_df_to_html(input_df):
                return input_df.to_html(
                    escape=False,
                    formatters=dict(Foto=path_to_image_html),
                    table_id="validasi-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html(df)
            st.markdown(
                """
            <style>
            #validasi-table {
                width: 100%;
                border-collapse: collapse;
                margin: 0px 0 10px 0;
            }
            #validasi-table th, #validasi-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                vertical-align: middle;
            }
            #validasi-table th {
                background-color: #E4EFE7;
                font-weight: bold;
            }
            #validasi-table img {
                margin: 0 auto;
                border-radius: 4px;
                display: block;
            }
            .stExpander > div > div > div > div {
                padding-top: 0rem !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="margin-top: -20px;"></div>', unsafe_allow_html=True
            )

            st.markdown(html_table, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("File 'csv/validasiPL2014.csv' tidak ditemukan!")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

    # Validasi Data 2019
    st.subheader("**Uji Akurasi Penutup Lahan Tahun 2019**")
    with st.container(border=True):
        st.write("**Matriks Konfusi Penutup Lahan Tahun 2019**")

        # Tambahkan matriks konfusi ilmiah di sini
        try:
            df = pd.read_csv("csv/validasiPL2019.csv")

            # Fungsi untuk membuat matriks konfusi ilmiah
            def create_confusion_matrix(df):
                from sklearn.metrics import (
                    confusion_matrix,
                    accuracy_score,
                    cohen_kappa_score,
                )
                import numpy as np

                y_true = df["PL Referensi"]
                y_pred = df["PL Aktual"]

                # Gunakan urutan kelas yang sudah ditentukan
                classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]
                # Filter hanya kelas yang ada di data
                classes = [
                    cls
                    for cls in classes
                    if cls in y_true.values or cls in y_pred.values
                ]

                cm = confusion_matrix(y_true, y_pred, labels=classes)
                n_total = np.sum(cm)

                row_totals = np.sum(cm, axis=1)
                col_totals = np.sum(cm, axis=0)

                # Producer's Accuracy = diagonal / row total
                producer_acc = np.diag(cm) / row_totals * 100

                # User's Accuracy = diagonal / column total
                user_acc = np.diag(cm) / col_totals * 100

                # Overall Accuracy
                overall_acc = np.sum(np.diag(cm)) / n_total * 100

                # Kappa Accuracy
                kappa = cohen_kappa_score(y_true, y_pred) * 100

                # Errors
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

            def display_confusion_matrix_html(results):
                cm = results["cm"]
                classes = results["classes"]
                row_totals = results["row_totals"]
                col_totals = results["col_totals"]
                producer_acc = results["producer_acc"]
                user_acc = results["user_acc"]
                commission_error = results["commission_error"]
                omission_error = results["omission_error"]
                overall_acc = results["overall_acc"]
                kappa = results["kappa"]
                n_total = results["n_total"]

                html_content = """
                <style>
                .conf-matrix {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-family: Arial, sans-serif;
                    font-size: 13px;
                    border: 2px solid #333;
                }}
                .conf-matrix th {{
                    background: #E4EFE7;
                    border: 1px solid #333;
                    padding: 10px 6px;
                    text-align: center;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix td {{
                    border: 1px solid #333;
                    padding: 8px 6px;
                    text-align: center;
                    background: white;
                }}
                .conf-matrix .header-main {{
                    background: #E4EFE7;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix .diagonal {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                .conf-matrix .important {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                </style>
                
                <table class="conf-matrix">
                    <thead>
                        <tr>
                            <th rowspan="2" class="header-main">Data Hasil<br/>Klasifikasi</th>
                            <th colspan="{num_classes}" class="header-main">Data Uji Klasifikasi (Referensi)</th>
                            <th rowspan="2" class="header-main">Total<br/>Baris</th>
                            <th rowspan="2" class="header-main">Producer<br/>Accuracy<br/>(%)</th>
                            <th rowspan="2" class="header-main">Kesalahan<br/>Omisi<br/>(%)</th>
                        </tr>
                        <tr>
                """.format(
                    num_classes=len(classes)
                )

                # Add class headers
                for cls in classes:
                    html_content += '<th class="header-main">{}</th>'.format(cls)

                html_content += "</tr></thead><tbody>"

                # Add data rows
                for i, cls in enumerate(classes):
                    html_content += '<tr><td class="header-main">{}</td>'.format(cls)

                    # Add confusion matrix values
                    for j in range(len(classes)):
                        cell_class = "diagonal" if i == j else ""
                        html_content += '<td class="{}">{}</td>'.format(
                            cell_class, cm[i][j]
                        )

                    # Add row total, producer accuracy, omission error
                    html_content += """
                    <td>{row_total}</td>
                    <td>{producer_acc:.1f}</td>
                    <td>{omis_err:.1f}</td>
                    </tr>""".format(
                        row_total=row_totals[i],
                        producer_acc=producer_acc[i],
                        omis_err=omission_error[i],
                    )

                # Add totals row
                html_content += '<tr><td class="header-main">Total Kolom</td>'
                for total in col_totals:
                    html_content += "<td>{}</td>".format(total)
                html_content += "<td>{}</td><td>-</td><td>-</td></tr>".format(n_total)

                # Add user accuracy row
                html_content += '<tr><td class="header-main">User Accuracy (%)</td>'
                for acc in user_acc:
                    html_content += "<td>{:.1f}</td>".format(acc)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add commission error row
                html_content += '<tr><td class="header-main">Kesalahan Komisi (%)</td>'
                for error in commission_error:
                    html_content += "<td>{:.1f}</td>".format(error)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add overall accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Overall Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{overall_acc:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>""".format(
                    num_classes=len(classes), overall_acc=overall_acc
                )

                # Add kappa accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Kappa Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{kappa:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>
                </tbody></table>""".format(
                    num_classes=len(classes), kappa=kappa
                )

                return html_content

            # Hitung dan tampilkan matriks konfusi
            results = create_confusion_matrix(df)

            # # Tampilkan metrics summary
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     st.metric("Total Sampel", results["n_total"])
            # with col2:
            #     st.metric("Akurasi yang Diharapkan", f"85%")
            # with col3:
            #     st.metric("Overall Accuracy", f"{results['overall_acc']:.2f}%")
            # with col4:
            #     st.metric("Kappa Accuracy", f"{results['kappa']:.2f}%")

            # Tampilkan matriks konfusi
            html_content = display_confusion_matrix_html(results)
            st.markdown(html_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error dalam membuat matriks konfusi: {str(e)}")

    with st.expander("**Tabel Sampel Validasi Tahun 2019**"):
        try:
            df = pd.read_csv("csv/validasiPL2019.csv")
            # foto_path = "img/31veg2019.png"

            def get_base64_encoded_image(image_path):
                try:
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except Exception as e:
                    return None

            def path_to_image_html(path):
                base64_img = get_base64_encoded_image(path)
                if base64_img:
                    return f'<img src="data:image/png;base64,{base64_img}" width="100" height="80" style="object-fit: cover; border-radius: 2px;">'
                else:
                    return "❌ Foto tidak ditemukan."

            def create_image_path(kode):
                kode_prefix = kode[:5].lower()
                return f"img/img_val_2019/{kode_prefix}19.png"

            # Tambahkan kolom Foto berdasarkan kode masing-masing
            df["Foto"] = df["Kode"].apply(create_image_path)

            @st.cache_data
            def convert_df_to_html(input_df):
                return input_df.to_html(
                    escape=False,
                    formatters=dict(Foto=path_to_image_html),
                    table_id="validasi-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html(df)
            st.markdown(
                """
            <style>
            #validasi-table {
                width: 100%;
                border-collapse: collapse;
                margin: 0px 0 10px 0;
            }
            #validasi-table th, #validasi-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                vertical-align: middle;
            }
            #validasi-table th {
                background-color: #E4EFE7;
                font-weight: bold;
            }
            #validasi-table img {
                margin: 0 auto;
                border-radius: 4px;
                display: block;
            }
            .stExpander > div > div > div > div {
                padding-top: 0rem !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="margin-top: -20px;"></div>', unsafe_allow_html=True
            )

            st.markdown(html_table, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("File 'csv/validasiPL2019.csv' tidak ditemukan!")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

    # Validasi Data 2024
    st.subheader("**Uji Akurasi Penutup Lahan Tahun 2024**")

    with st.container(border=True):
        st.write("**Matriks Konfusi Penutup Lahan Tahun 2024**")

        # Tambahkan matriks konfusi ilmiah di sini
        try:
            df = pd.read_csv("csv/validasiPL2024.csv")

            # Fungsi untuk membuat matriks konfusi ilmiah
            def create_confusion_matrix(df):
                from sklearn.metrics import (
                    confusion_matrix,
                    accuracy_score,
                    cohen_kappa_score,
                )
                import numpy as np

                y_true = df["PL Referensi"]
                y_pred = df["PL Aktual"]

                # Gunakan urutan kelas yang sudah ditentukan
                classes = ["Vegetasi", "Tubuh Air", "Lahan Terbangun", "Lahan Terbuka"]
                # Filter hanya kelas yang ada di data
                classes = [
                    cls
                    for cls in classes
                    if cls in y_true.values or cls in y_pred.values
                ]

                cm = confusion_matrix(y_true, y_pred, labels=classes)
                n_total = np.sum(cm)

                row_totals = np.sum(cm, axis=1)
                col_totals = np.sum(cm, axis=0)

                # Producer's Accuracy = diagonal / row total (avoid division by zero)
                producer_acc = (
                    np.divide(
                        np.diag(cm),
                        row_totals,
                        out=np.zeros_like(np.diag(cm), dtype=float),
                        where=row_totals != 0,
                    )
                    * 100
                )

                # User's Accuracy = diagonal / column total (avoid division by zero)
                user_acc = (
                    np.divide(
                        np.diag(cm),
                        col_totals,
                        out=np.zeros_like(np.diag(cm), dtype=float),
                        where=col_totals != 0,
                    )
                    * 100
                )

                # Overall Accuracy
                overall_acc = np.sum(np.diag(cm)) / n_total * 100

                # Kappa Accuracy
                kappa = cohen_kappa_score(y_true, y_pred) * 100

                # Errors
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

            def display_confusion_matrix_html(results):
                cm = results["cm"]
                classes = results["classes"]
                row_totals = results["row_totals"]
                col_totals = results["col_totals"]
                producer_acc = results["producer_acc"]
                user_acc = results["user_acc"]
                commission_error = results["commission_error"]
                omission_error = results["omission_error"]
                overall_acc = results["overall_acc"]
                kappa = results["kappa"]
                n_total = results["n_total"]

                html_content = """
                <style>
                .conf-matrix {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-family: Arial, sans-serif;
                    font-size: 13px;
                    border: 2px solid #333;
                }}
                .conf-matrix th {{
                    background: #E4EFE7;
                    border: 1px solid #333;
                    padding: 10px 6px;
                    text-align: center;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix td {{
                    border: 1px solid #333;
                    padding: 8px 6px;
                    text-align: center;
                    background: white;
                }}
                .conf-matrix .header-main {{
                    background: #E4EFE7;
                    font-weight: bold;
                    color: #333;
                }}
                .conf-matrix .diagonal {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                .conf-matrix .important {{
                    background: #3c5e51;
                    color: white;
                    font-weight: bold;
                }}
                </style>
                
                <table class="conf-matrix">
                    <thead>
                        <tr>
                            <th rowspan="2" class="header-main">Data Hasil<br/>Klasifikasi</th>
                            <th colspan="{num_classes}" class="header-main">Data Uji Klasifikasi (Referensi)</th>
                            <th rowspan="2" class="header-main">Total<br/>Baris</th>
                            <th rowspan="2" class="header-main">Producer<br/>Accuracy<br/>(%)</th>
                            <th rowspan="2" class="header-main">Kesalahan<br/>Omisi<br/>(%)</th>
                        </tr>
                        <tr>
                """.format(
                    num_classes=len(classes)
                )

                # Add class headers
                for cls in classes:
                    html_content += '<th class="header-main">{}</th>'.format(cls)

                html_content += "</tr></thead><tbody>"

                # Add data rows
                for i, cls in enumerate(classes):
                    html_content += '<tr><td class="header-main">{}</td>'.format(cls)

                    # Add confusion matrix values
                    for j in range(len(classes)):
                        cell_class = "diagonal" if i == j else ""
                        html_content += '<td class="{}">{}</td>'.format(
                            cell_class, cm[i][j]
                        )

                    # Add row total, producer accuracy, omission error
                    html_content += """
                    <td>{row_total}</td>
                    <td>{producer_acc:.1f}</td>
                    <td>{omis_err:.1f}</td>
                    </tr>""".format(
                        row_total=row_totals[i],
                        producer_acc=producer_acc[i],
                        omis_err=omission_error[i],
                    )

                # Add totals row
                html_content += '<tr><td class="header-main">Total Kolom</td>'
                for total in col_totals:
                    html_content += "<td>{}</td>".format(total)
                html_content += "<td>{}</td><td>-</td><td>-</td></tr>".format(n_total)

                # Add user accuracy row
                html_content += '<tr><td class="header-main">User Accuracy (%)</td>'
                for acc in user_acc:
                    if np.isnan(acc) or acc == 0:
                        html_content += "<td>0.0</td>"
                    else:
                        html_content += "<td>{:.1f}</td>".format(acc)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add commission error row
                html_content += '<tr><td class="header-main">Kesalahan Komisi (%)</td>'
                for error in commission_error:
                    if np.isnan(error) or error == 100:
                        html_content += "<td>0.0</td>"
                    else:
                        html_content += "<td>{:.1f}</td>".format(error)
                html_content += "<td>-</td><td>-</td><td>-</td></tr>"

                # Add overall accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Overall Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{overall_acc:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>""".format(
                    num_classes=len(classes), overall_acc=overall_acc
                )

                # Add kappa accuracy row
                html_content += """
                <tr>
                    <td class="header-main"><strong>Kappa Accuracy</strong></td>
                    <td colspan="{num_classes}" class="important">{kappa:.2f}%</td>
                    <td>-</td><td>-</td><td>-</td>
                </tr>
                </tbody></table>""".format(
                    num_classes=len(classes), kappa=kappa
                )

                return html_content

            # Hitung dan tampilkan matriks konfusi
            results = create_confusion_matrix(df)

            # # Tampilkan metrics summary
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     st.metric("Total Sampel", results["n_total"])
            # with col2:
            #     st.metric("Akurasi yang Diharapkan", f"85%")
            # with col3:
            #     st.metric("Overall Accuracy", f"{results['overall_acc']:.2f}%")
            # with col4:
            #     st.metric("Kappa Accuracy", f"{results['kappa']:.2f}%")

            # Tampilkan matriks konfusi
            html_content = display_confusion_matrix_html(results)
            st.markdown(html_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error dalam membuat matriks konfusi: {str(e)}")

    with st.expander("**Tabel Sampel Validasi Tahun 2024**"):
        try:
            df = pd.read_csv("csv/validasiPL2024.csv")

            def get_base64_encoded_image(image_path):
                try:
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except Exception as e:
                    return None

            def path_to_image_html(path):
                base64_img = get_base64_encoded_image(path)
                if base64_img:
                    return f'<img src="data:image/jpg;base64,{base64_img}" width="80" height="100" style="object-fit: cover; border-radius: 2px;">'
                else:
                    return "❌ Foto tidak ditemukan."

            def create_image_path(kode):
                import os

                # Ambil 2 digit pertama dari kode
                kode_prefix = kode[:2]

                # Semua kemungkinan pola nama file berdasarkan jenis penutup lahan
                possible_patterns = ["veg24", "urb24", "air24", "ope24"]
                possible_paths = []

                # Buat semua kemungkinan path dengan ekstensi JPG dan jpg
                for pattern in possible_patterns:
                    possible_paths.extend(
                        [
                            f"img/img_val_2024/{kode_prefix}{pattern}.JPG",
                            f"img/img_val_2024/{kode_prefix}{pattern}.jpg",
                        ]
                    )

                # Cek path mana yang ada
                for path in possible_paths:
                    if os.path.exists(path):
                        return path

                # Return path pertama sebagai fallback
                return possible_paths[0]

            # Tambahkan kolom Foto berdasarkan kode masing-masing
            df["Foto"] = df["Kode"].apply(create_image_path)

            @st.cache_data
            def convert_df_to_html(input_df):
                return input_df.to_html(
                    escape=False,
                    formatters=dict(Foto=path_to_image_html),
                    table_id="validasi-table",
                    classes="table table-striped",
                    index=False,
                )

            html_table = convert_df_to_html(df)
            st.markdown(
                """
            <style>
            #validasi-table {
                width: 100%;
                border-collapse: collapse;
                margin: 0px 0 10px 0;
            }
            #validasi-table th, #validasi-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                vertical-align: middle;
            }
            #validasi-table th {
                background-color: #E4EFE7;
                font-weight: bold;
            }
            #validasi-table img {
                margin: 0 auto;
                border-radius: 4px;
                display: block;
            }
            .stExpander > div > div > div > div {
                padding-top: 0rem !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="margin-top: -20px;"></div>', unsafe_allow_html=True
            )

            st.markdown(html_table, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("File 'csv/validasiPL2024.csv' tidak ditemukan!")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")


elif selected_tab == "⚙️ Model":
    st.write("Page under construction. Coming soon!")
