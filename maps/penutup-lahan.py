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
    year_to_index = {"1999": 0, "2004": 1, "2009": 2, "2014": 3, "2019": 4, "2024": 5}

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
                3: [205, 154, 77, 255],  # faf5d9 - Lahan Terbuka
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
                ["1999", "2004", "2009", "2014", "2019", "2024"],
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
    # Grafik Tren NDBI Perkotaan vs Non-Perkotaan
    df_urban_rural = pd.read_csv("./csv/ndbiStatsKec.csv")

    ndbi_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    ndbi_urban_rural_pivot = ndbi_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking NDBI
    st.badge(
        "**Tren NDBI: Kawasan Perkotaan vs Non-Perkotaan Yogyakarta (1999-2024)**",
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

            if "Urban" in ndbi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndbi_urban_rural_pivot.index,
                        y=ndbi_urban_rural_pivot["Urban"],
                        mode="lines+markers",
                        name="Perkotaan",
                        line=dict(color="#FF90BB", width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate="<b>Perkotaan</b><br>Tahun: %{x}<br>NDBI Mean: %{y:.3f}<extra></extra>",
                    )
                )

            if "Rural" in ndbi_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ndbi_urban_rural_pivot.index,
                        y=ndbi_urban_rural_pivot["Rural"],
                        mode="lines+markers",
                        name="Non-Perkotaan",
                        line=dict(color="#096B68", width=3),
                        marker=dict(size=8, symbol="square"),
                        hovertemplate="<b>Non-Perkotaan</b><br>Tahun: %{x}<br>NDBI Mean: %{y:.3f}<extra></extra>",
                    )
                )

            # Update Layout Grafik
            fig.update_layout(
                xaxis=dict(
                    title=dict(
                        text="Tahun",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    tickvals=[1999, 2004, 2009, 2014, 2019, 2024],
                    gridcolor="#9A9A9A",
                ),
                yaxis=dict(
                    title=dict(
                        text="NDBI Mean",
                        font=dict(family="Poppins", size=12, color="black"),
                    ),
                    tickfont=dict(family="Poppins", size=12, color="black"),
                    gridcolor="#9A9A9A",
                    zerolinecolor="#9A9A9A",
                    # range=[22, 40],
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
                height=305,
                font=dict(family="Poppins", size=12),
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)

    with col2_tren_main:
        # Dictionary Mean NDBI
        mean_by_year = {
            1999: {"mean": -0.168},
            2004: {"mean": -0.188},
            2009: {"mean": -0.154},
            2014: {"mean": -0.179},
            2019: {"mean": -0.161},
            2024: {"mean": -0.162},
        }

        years_tren = sorted(mean_by_year.keys())
        mean_tren = [mean_by_year[y]["mean"] for y in years_tren]

        # Hitung Overall Mean (Rata-rata NDBI 1999-2024)
        overall_mean = sum(mean_tren) / len(mean_tren)

        # Hitung Mean Absolute Change (Rata-rata Fluktuasi Tahunan)
        diffs = []
        for i in range(1, len(mean_tren)):
            diff = abs(mean_tren[i] - mean_tren[i - 1])
            diffs.append(diff)

        mac = sum(diffs) / len(diffs)

        # Row Metrics
        col1_tren_metric, col2_tren_metric = st.columns([1, 1])
        with col1_tren_metric:
            with st.container(border=True):
                st.metric(
                    label="Rata-rata NDBI",
                    value=f"{overall_mean:.3f}",
                    help="Rata-rata NDBI di KPY dan Sekitarnya = (NDBImean₁₉₉₉ + NDBImean₂₀₀₄ + ... + NDBImean₂₀₂₄)/6",
                )

        with col2_tren_metric:
            with st.container(border=True):
                st.metric(
                    label="Rata-rata Perubahan",
                    value=f"{mac:.4f}",
                    help="Perubahan Absolut NDBI di KPY dan Sekitarnya = (|NDBImean₂₀₀₄ - NDBImean₁₉₉₉| + |NDBImean₂₀₀₉ - NDBImean₂₀₀₄| + ... + |NDBImean₂₀₂₄ - NDBImean₂₀₁₉|)/5",
                )

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡**Quick Insight**
                - Kawasan perkotaan Yogyakarta memiliki nilai NDBI :green-background[**lebih tinggi**] dibanding kawasan non-perkotaan.
                - :green-background[**Selisih**] nilai NDBI perkotaan dan non-perkotaan berkisar antara :green-background[**0.148**] hingga :green-background[**0.196**].
                """
            )

elif selected_tab == "✅ Validasi":
    st.write("Page under construction. Coming soon!")
