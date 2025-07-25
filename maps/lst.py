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
    page_title="Dashboard Suhu Permukaan Lahan",
    layout="wide",
)

# CSS untuk Styling Komponen Streamlit
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

# Dictionary Statistik LST 1999-2024
stats_dict = {
    "1999": {"min": 4.313, "max": 69.760, "mean": 34.531},
    "2004": {"min": 15.295, "max": 57.402, "mean": 35.481},
    "2009": {"min": 18.111, "max": 67.161, "mean": 37.745},
    "2014": {"min": 17.684, "max": 52.441, "mean": 36.630},
    "2019": {"min": 18.537, "max": 49.669, "mean": 35.739},
    "2024": {"min": 20.722, "max": 72.317, "mean": 37.262},
    "2029": {
        "min": 20.722,
        "max": 72.317,
        "mean": 37.262,
    },  # 2029 Sementara Menggunakan Data 2024
}

# Dictionary Threshold LST 1999-2024
threshold_dict = {
    "1999": {"low": 30.499, "medium": 34.531, "high": 38.563},
    "2004": {"low": 31.412, "medium": 35.481, "high": 39.550},
    "2009": {"low": 33.243, "medium": 37.745, "high": 42.247},
    "2014": {"low": 32.168, "medium": 36.630, "high": 41.092},
    "2019": {"low": 31.923, "medium": 35.739, "high": 39.556},
    "2024": {"low": 33.207, "medium": 37.262, "high": 41.317},
    "2029": {
        "low": 33.207,
        "medium": 37.262,
        "high": 41.317,
    },  # 2029 Sementara Menggunakan Data 2024
}


# Function untuk Load CSV Statistik per Kecamatan
@st.cache_data
def load_stats_kec():
    csv_path = "./stats/lstStatsKec.csv"
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


# Function untuk Filter Kecamatan Berdasarkan Tahun
def get_kec_by_year(df, year):
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


# Function Condition untuk Menentukan Kapanewon/Kemantren Toponim
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


# Load DataFrame Kecamatan
df_kec_stats = load_stats_kec()

# Judul Halaman
st.subheader("Suhu Permukaan Lahan")

# Membuat Menu
selected_menu = st.pills(
    "**Lihat Analisis:**",
    [
        "🗺️ Peta",
        "📈 Tren",
        "⚙️ Model",
        "✅ Validasi",
        "📉 Regresi",
    ],
    selection_mode="single",
    default="🗺️ Peta",
)

# Peta
if selected_menu == "🗺️ Peta":
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
        with st.container(border=True):
            col_min, col_max, col_mean = st.columns([1, 1, 1])
            with col_min:
                st.metric("LST Minimum", f"{selected_data['min']:.1f}°C")
            with col_max:
                st.metric("LST Maksimum", f"{selected_data['max']:.1f}°C")
            with col_mean:
                st.metric("LST Rata-rata", f"{selected_data['mean']:.1f}°C")

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
                kecamatan_data = kec_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                description = f"Suhu permukaan lahan di **{toponim} {selected_kecamatan}** pada tahun **{option}** memiliki rerata suhu sebesar **{kecamatan_data['mean']:.2f}°C** dengan suhu terendah yakni **{kecamatan_data['min']:.2f}°C** dan suhu tertinggi adalah **{kecamatan_data['max']:.2f}°C**."

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
            st.warning(f"File GeoTIFF tidak ditemukan: {tif_path}")

        # Cek Ketersediaan AOI, Panggil Function Batas AOI, dan Tampilkan ke Peta
        shapefile_path = "shp/aoi_kpy.shp"
        if os.path.exists(shapefile_path):
            add_shapefile_to_map(m, shapefile_path)
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

# Tren
elif selected_menu == "📈 Tren":
    # Grafik Tren LST Perkotaan vs Non-Perkotaan
    df_urban_rural = pd.read_csv("./stats/lstStatsKec.csv")

    lst_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    lst_urban_rural_pivot = lst_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking LST
    st.badge(
        "**Tren Fluktuasi LST di Kawasan Perkotaan vs Non-Perkotaan Yogyakarta (1999-2024)**",
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

            if "Urban" in lst_urban_rural_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=lst_urban_rural_pivot.index,
                        y=lst_urban_rural_pivot["Urban"],
                        mode="lines+markers",
                        name="Perkotaan",
                        line=dict(color="#FF90BB", width=3),
                        marker=dict(size=8, symbol="circle"),
                        hovertemplate="<b>Perkotaan</b><br>Tahun: %{x}<br>LST Rata-rata: %{y:.2f}°C<extra></extra>",
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
                        hovertemplate="<b>Non-Perkotaan</b><br>Tahun: %{x}<br>LST Rata-rata: %{y:.2f}°C<extra></extra>",
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
                        text="LST Rata-rata (°C)",
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
                height=300,
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
            # 2029: {"mean": 37.26},
        }

        years_tren = sorted(mean_by_year.keys())
        mean_tren = [mean_by_year[y]["mean"] for y in years_tren]

        # Hitung Overall Mean (Rata-rata LST 1999-2024)
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
                    label="Rata-rata LST (1999-2024)",
                    value=f"{overall_mean:.2f}°C",
                )

        with col2_tren_metric:
            with st.container(border=True):
                st.metric(label="Perubahan Tahunan", value=f"{mac:.2f}°C")

        # Container Top 10 Wilayah Terpanas
        with st.container(border=True):
            st.write("**Analisis**")
            st.markdown(
                """Diagram garis di samping membuktikan kebenaran hipotesis awal bahwa :green-background[**kawasan perkotaan**] Yogyakarta cenderung memiliki nilai :green-background[**LST**] yang :green-background[**lebih tinggi**] dibandingkan :green-background[**kawasan non-perkotaan**] di sekitarnya pada masing-masing :green-background[**tahun**] yang :green-background[**sama**] dengan selisih nilai LST berkisar antara :green-background[**5.94°C**] hingga :green-background[**9.17°C**]."""
            )

    # Row Diagram Garis & Ranking LST
    st.badge(
        "**38 Kecamatan Terpanas Berdasarkan Rata-rata LST (1999-2024)**",
        color="primary",
    )

    col_rank = st.columns([1])[0]
    with col_rank:
        df_stats = pd.read_csv("./stats/lstStatsKec.csv")

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
                "Mean_LST": "LST Rata-rata (°C)",
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
            + "Rata-rata LST: %{customdata[1]:.2f}°C<extra></extra>",
            texttemplate="%{x:.2f}°C",
            textposition="outside",
            textfont_size=10,
            textfont_color="black",
        )

        # Update dan Styling Bar Plot
        fig.update_layout(
            height=800,
            font=dict(family="Poppins", size=11),
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
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

# Model
elif selected_menu == "⚙️ Model":
    st.write("Page under construction.")

# Validasi
elif selected_menu == "✅ Validasi":
    st.write("Page under construction.")

# Regresi
elif selected_menu == "📉 Regresi":
    st.write("Page under construction.")
