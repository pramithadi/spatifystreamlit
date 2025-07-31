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
    page_title="Dashboard NDVI",
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

# Dictionary Statistik NDVI
stats_by_year = {
    "1999": {"min": -0.120, "max": 0.884, "mean": 0.535},
    "2004": {"min": -0.214, "max": 0.944, "mean": 0.592},
    "2009": {"min": -0.220, "max": 0.890, "mean": 0.554},
    "2014": {"min": -0.482, "max": 0.928, "mean": 0.596},
    "2019": {"min": -0.271, "max": 0.971, "mean": 0.587},
    "2024": {"min": -0.488, "max": 0.982, "mean": 0.592},
}

# Dictionary Threshold
threshold_dict = {
    "1999": {"low": 0.407, "medium": 0.535, "high": 0.664},
    "2004": {"low": 0.454, "medium": 0.592, "high": 0.730},
    "2009": {"low": 0.411, "medium": 0.554, "high": 0.698},
    "2014": {"low": 0.445, "medium": 0.596, "high": 0.748},
    "2019": {"low": 0.429, "medium": 0.587, "high": 0.746},
    "2024": {"low": 0.426, "medium": 0.592, "high": 0.758},
}


# Function untuk Load Data Statistik Kecamatan dari CSV
@st.cache_data
def load_kecamatan_stats():
    """
    Load statistik NDVI per kecamatan dari file CSV
    """
    csv_path = "./csv/ndviStatsKec.csv"
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


# Function untuk Get Data Kecamatan Berdasarkan Tahun
def get_kecamatan_data_by_year(df, year):
    """
    Filter data kecamatan berdasarkan tahun
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

            # Nilai NDVI Berkisar -1 Hingga +1
            # Maka Hanya Filter Nilai yang Benar-benar Tidak Valid (Outlier Ekstrem)
            data = np.where((data < -1) | (data > 1), np.nan, data)

            # Warna untuk Setiap Kelas
            colors = {
                "very_low": [139, 0, 0, 255],  # #8b0000
                "low": [255, 255, 224, 255],  # #ffffe0
                "medium": [144, 238, 144, 255],  # #90ee90
                "high": [0, 100, 0, 255],  # #006400
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
            ndvi_overlay = folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_folium,
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
                name="NDVI",
            )
            ndvi_overlay.add_to(map_obj)

        return True
    except Exception as e:
        return False


# Load Data Statistik Kecamatan
kecamatan_stats_df = load_kecamatan_stats()

st.subheader("Normalized Difference Vegetation Index")

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
            # Selectbox Tahun
            option = st.selectbox(
                "**Pilih Tahun**",
                ["1999", "2004", "2009", "2014", "2019", "2024"],
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
        def classify_ndvi(mean_value, thresholds):
            """
            Klasifikasi nilai mean NDVI berdasarkan threshold

            Args:
                mean_value (float): Nilai mean NDVI
                thresholds (dict): Dictionary threshold dengan key 'low', 'medium', 'high'

            Returns:
                tuple: (kategori, deskripsi)
            """
            if mean_value <= thresholds["low"]:
                return "sangat rendah", "sangat rendah"
            elif thresholds["low"] < mean_value <= thresholds["medium"]:
                return "tergolong rendah", "tergolong rendah"
            elif thresholds["medium"] < mean_value <= thresholds["high"]:
                return "cukup sedang", "cukup sedang"
            else:  # mean_value > thresholds['high']
                return "tinggi", "tinggi"

        # Container Analisis NDVI per Kecamatan
        if selected_kecamatan and selected_kecamatan != "" and kecamatan_data_year:
            with st.container(border=True):
                st.write("💡**Quick Insight**")
                kecamatan_data = kecamatan_data_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                current_thresholds = threshold_dict[option]

                kategori, deskripsi = classify_ndvi(
                    kecamatan_data["mean"], current_thresholds
                )

                description = f"Kerapatan vegetasi di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] menunjukkan nilai rata-rata NDVI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai tersebut mengindikasikan bahwa {toponim} {selected_kecamatan} memiliki tingkat :green-background[**kerapatan vegetasi**] yang :green-background[**{deskripsi}**]."

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

        # Panggil GeoTiff dari Aset Lokal
        if option == "2029":
            tif_path = "tif/ndvi2024kpy.tif"
        else:
            tif_path = f"tif/ndvi{option}kpy.tif"

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
        st_data = st_folium(m, use_container_width=True, height=597)

elif selected_tab == "📈 Tren":
    # Grafik Tren NDVI Perkotaan vs Non-Perkotaan
    df_urban_rural = pd.read_csv("./csv/ndviStatsKec.csv")

    ndvi_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    ndvi_urban_rural_pivot = ndvi_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking NDVI
    st.badge(
        "**Tren NDVI: Kawasan Perkotaan vs Non-Perkotaan Yogyakarta (1999-2024)**",
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
                        text="NDVI Mean",
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
        # Dictionary Mean NDVI
        mean_by_year = {
            1999: {"mean": 0.535},
            2004: {"mean": 0.592},
            2009: {"mean": 0.554},
            2014: {"mean": 0.596},
            2019: {"mean": 0.587},
            2024: {"mean": 0.592},
        }

        years_tren = sorted(mean_by_year.keys())
        mean_tren = [mean_by_year[y]["mean"] for y in years_tren]

        # Hitung Overall Mean (Rata-rata NDVI 1999-2024)
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
                    label="Rata-rata NDVI",
                    value=f"{overall_mean:.3f}",
                    help="Rata-rata NDVI di KPY dan Sekitarnya = (NDVImean₁₉₉₉ + NDVImean₂₀₀₄ + ... + NDVImean₂₀₂₄)/6",
                )

        with col2_tren_metric:
            with st.container(border=True):
                st.metric(
                    label="Rata-rata Perubahan",
                    value=f"{mac:.4f}",
                    help="Perubahan Absolut NDVI di KPY dan Sekitarnya = (|NDVImean₂₀₀₄ - NDVImean₁₉₉₉| + |NDVImean₂₀₀₉ - NDVImean₂₀₀₄| + ... + |NDVImean₂₀₂₄ - NDVImean₂₀₁₉|)/5",
                )

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡**Quick Insight**
                - Kawasan perkotaan Yogyakarta memiliki nilai NDVI :green-background[**lebih rendah**] dibanding kawasan non-perkotaan.
                - :green-background[**Selisih**] nilai NDVI perkotaan dan non-perkotaan berkisar antara :green-background[**0.179**] hingga :green-background[**0.238**].
                """
            )

    # Row Diagram Garis & Ranking NDVI
    st.badge(
        "**Top 38 Kecamatan: Kerapatan Vegetasi Tertinggi (1999-2024)**",
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

elif selected_tab == "✅ Validasi":
    try:
        # Load CSV Sampel NDVI untuk Validasi
        validation_data = pd.read_csv("csv/ndviSampelValidasi.csv")

        # Hapus Nilai NaN
        validation_data = validation_data.dropna()

        # Ekstraksi Nilai dari Field
        landsat_values = validation_data["ndviLandsat"].values
        sentinel_values = validation_data["ndviSentinel"].values

        # Hitung Korelasi Pearson
        correlation_coef, p_value = stats.pearsonr(landsat_values, sentinel_values)

        # RMSE
        rmse = np.sqrt(mean_squared_error(landsat_values, sentinel_values))

        # MAE
        mae = mean_absolute_error(landsat_values, sentinel_values)

        # Hitung Persamaan Linear
        slope, intercept, r_value, p_val, std_err = stats.linregress(
            landsat_values, sentinel_values
        )

        # Buat Persamaan
        if intercept >= 0:
            equation = f"y = {slope:.3f}x + {intercept:.3f}"
        else:
            equation = f"y = {slope:.3f}x - {abs(intercept):.3f}"

        # Row Diagram Garis dan Validasi NDVI
        st.badge(
            "**Korelasi Pearson NDVI: Landsat 8 vs Sentinel-2 (2024)**",
            color="primary",
        )

        col1_validate, col2_validate = st.columns([2.4, 1.6])
        with col1_validate:
            # Container Grafik Korelasi Pearson
            with st.container(border=True):
                # Buat Scatterplot
                fig = px.scatter(
                    x=landsat_values,
                    y=sentinel_values,
                    labels={"x": "NDVI Landsat 8", "y": "NDVI Sentinel-2"},
                    opacity=0.6,
                    color_discrete_sequence=["#1f77b4"],
                )

                # Garis Trend (Memvisualisasikan Hubungan Linear)
                x_range = np.linspace(landsat_values.min(), landsat_values.max(), 100)
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
                    height=362,
                    showlegend=True,
                    template="plotly_white",
                    font=dict(
                        family="Poppins, sans-serif",  # Font Poppins
                        size=10,
                        color="black",  # Font color hitam
                    ),
                    margin=dict(t=30, b=20, l=20, r=20),
                    # Styling Sumbu X dan Y
                    xaxis=dict(
                        title=dict(
                            text="NDVI Landsat 8",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    yaxis=dict(
                        title=dict(
                            text="NDVI Sentinel-2",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    # Styling untuk legend
                    legend=dict(font=dict(color="black", family="Poppins, sans-serif")),
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
                    borderpad=7,  # Tambah Padding Internal
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
                st.markdown("💡**Quick Insight**")

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
                - **Sampel**: {len(landsat_values)}
                - **Korelasi (r)**: {corr_interpretation}⁽¹⁾
                - **Akurasi (RMSE)**: Baik⁽²⁾
                - **p-value**: {p_value:.3f} (Sangat Signifikan)⁽³⁾
                """
                )

                # Status Validasi
                abs_corr = abs(correlation_coef)
                if abs_corr >= 0.7 and rmse <= 0.1:
                    st.success("✅ VALID! Data layak untuk prediksi LST")
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

    # Row Peta NDVI Landsat 8 vs Sentinel-2
    # Threshold untuk Peta Validasi
    validation_thresholds = {
        "landsat": {"low": 0.426, "medium": 0.592, "high": 0.758},
        "sentinel": {"low": 0.345, "medium": 0.530, "high": 0.714},
    }

    st.badge(
        "**Peta NDVI: Landsat 8 vs Sentinel-2 (2024)**",
        color="primary",
    )
    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #333; font-size: 14px;">📡 Landsat 8 NDVI (2024)</div>
                <div style="font-weight: 600; color: #333; font-size: 14px;">🛰️ Sentinel-2 NDVI (2024)</div>
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
        landsat_tif_path = "tif/ndvi2024kpy.tif"
        sentinel_tif_path = "tif/ndviSentinel30.tif"
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
            add_shapefile_to_map(dual_map.m1, shapefile_path)
            add_shapefile_to_map(dual_map.m2, shapefile_path)

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
                        <div style="width: 12px; height: 12px; background-color: #8b0000; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Non-vegetasi</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #ffffe0; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Rendah</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #90ee90; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Sedang</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #006400; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Tinggi</span>
                    </div>
                </div>
            </div>
            """
            map_obj.get_root().html.add_child(folium.Element(legend_html))

        add_universal_legend_to_map(dual_map.m1, "Kelas NDVI")

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
            content: '📡 Landsat 8 NDVI (2024)';
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
