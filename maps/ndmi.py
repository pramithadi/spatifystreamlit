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
    page_title="Dashboard NDMI",
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

# Dictionary Statistik NDMI
stats_by_year = {
    "1999": {"min": -0.372, "max": 0.615, "mean": 0.168},
    "2004": {"min": -0.569, "max": 0.696, "mean": 0.188},
    "2009": {"min": -0.555, "max": 0.605, "mean": 0.153},
    "2014": {"min": -0.819, "max": 0.564, "mean": 0.179},
    "2019": {"min": -0.940, "max": 0.581, "mean": 0.161},
    "2024": {"min": -0.454, "max": 0.604, "mean": 0.162},
}

# Dictionary Threshold
threshold_dict = {
    "1999": {"low": 0.053, "medium": 0.168, "high": 0.283},
    "2004": {"low": 0.067, "medium": 0.188, "high": 0.309},
    "2009": {"low": 0.027, "medium": 0.153, "high": 0.280},
    "2014": {"low": 0.056, "medium": 0.179, "high": 0.302},
    "2019": {"low": 0.022, "medium": 0.161, "high": 0.301},
    "2024": {"low": 0.015, "medium": 0.162, "high": 0.309},
}


# Function untuk Load Data Statistik Kecamatan dari CSV
@st.cache_data
def load_kecamatan_stats():
    """
    Load statistik NDMI per kecamatan dari file CSV
    """
    csv_path = "./stats/ndmiStatsKec.csv"
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
        <div style="margin: 0 0 8px 0; color: #333; font-weight: 600; font-size: 12px;">Tingkat Kerapatan Area Terbangun</div>
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

            # Nilai NDMI Berkisar -1 Hingga +1
            # Maka Hanya Filter Nilai yang Benar-benar Tidak Valid (Outlier Ekstrem)
            data = np.where((data < -1) | (data > 1), np.nan, data)

            # Warna untuk Setiap Kelas
            colors = {
                "very_low": "#948979",
                "low": "#ffffe0",
                "medium": "#add8e6",
                "high": "#00008b",
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


# Load Data Statistik Kecamatan
kecamatan_stats_df = load_kecamatan_stats()

st.subheader("Normalized Difference Moisture Index")

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
            """
            Klasifikasi nilai mean NDMI berdasarkan threshold

            Args:
                mean_value (float): Nilai mean NDMI
                thresholds (dict): Dictionary threshold dengan key 'low', 'medium', 'high'

            Returns:
                tuple: (kategori, deskripsi)
            """
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
                st.write("💡**Quick Insight**")
                kecamatan_data = kecamatan_data_year[selected_kecamatan]
                wadmkk = kecamatan_data["wadmkk"]
                toponim = get_toponim(wadmkk)

                current_thresholds = threshold_dict[option]

                kategori, deskripsi = classify_ndmi(
                    kecamatan_data["mean"], current_thresholds
                )

                description = f"Tingkat kerapatan area terbangun di :green-background[**{toponim} {selected_kecamatan}**] pada tahun :green-background[**{option}**] menunjukkan nilai rata-rata NDMI sebesar :green-background[**{kecamatan_data['mean']:.3f}**]. Nilai tersebut mengindikasikan bahwa {toponim} {selected_kecamatan} memiliki tingkat :green-background[**kerapatan area terbangun**] dan :green-background[**mobilitas penduduk**] yang :green-background[**{deskripsi}**]."

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
            tif_path = "tif/ndmi2024kpy.tif"
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
    # Grafik Tren NDMI Perkotaan vs Non-Perkotaan
    df_urban_rural = pd.read_csv("./stats/ndmiStatsKec.csv")

    ndmi_urban_rural = (
        df_urban_rural.groupby(["Tahun", "Zona"])["mean"].mean().reset_index()
    )

    ndmi_urban_rural_pivot = ndmi_urban_rural.pivot(
        index="Tahun", columns="Zona", values="mean"
    )

    # Row Diagram Garis & Ranking NDMI
    st.badge(
        "**Tren NDMI: Kawasan Perkotaan vs Non-Perkotaan Yogyakarta (1999-2024)**",
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
                        text="NDMI Mean",
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
                height=384.5,
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
        }

        years_tren = sorted(mean_by_year.keys())
        mean_tren = [mean_by_year[y]["mean"] for y in years_tren]

        # Hitung Overall Mean (Rata-rata NDMI 1999-2024)
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
                    label="NDMI Mean (1999-2024)",
                    value=f"{overall_mean:.3f}",
                )

        with col2_tren_metric:
            with st.container(border=True):
                st.metric(label="Fluktuasi Tahunan", value=f"{mac:.4f}")

        # Container Analisis Tren
        with st.container(border=True):
            st.markdown(
                """
                💡**Quick Insight**
                - Kawasan perkotaan di Provinsi DIY memiliki nilai NDMI yang cenderung :green-background[**lebih tinggi**] dibanding kawasan non-perkotaan di sekitarnya.
                - :green-background[**Selisih**] nilai NDMI antara kawasan perkotaan dan non-perkotaan berkisar antara :green-background[**0.148**] hingga :green-background[**0.196**].
                - Pola ini mengindikasikan bahwa :green-background[**area terbangun**] di perkotaan :green-background[**terus bertambah**] seiring waktu dengan :green-background[**tren kenaikan**] sekitar :green-background[**0.0196**] per tahun."""
            )

    # Row Diagram Garis & Ranking NDMI
    st.badge(
        "**Top 38 Kecamatan: Kerapatan Area Terbangun Tertinggi (1999-2024)**",
        color="primary",
    )

    col_rank = st.columns([1])[0]
    with col_rank:
        df_stats = pd.read_csv("./stats/ndmiStatsKec.csv")

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
        # Load CSV Sampel NDMI untuk Validasi
        validation_data = pd.read_csv("stats/ndmiSampelValidasi.csv")

        # Hapus Nilai NaN
        validation_data = validation_data.dropna()

        # Ekstraksi Nilai dari Field
        landsat_values = validation_data["ndmiLandsat"].values
        sentinel_values = validation_data["ndmiSentinel"].values

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
            equation = f"y = {slope:.4f}x + {intercept:.4f}"
        else:
            equation = f"y = {slope:.4f}x - {abs(intercept):.4f}"

        # Row Diagram Garis dan Validasi NDMI
        st.badge(
            "**Korelasi Pearson NDMI: Landsat 8 vs Sentinel-2 (2024)**",
            color="primary",
        )

        col1_validate, col2_validate = st.columns([2.3, 1.7])
        with col1_validate:
            # Container Grafik Korelasi Pearson
            with st.container(border=True):
                # Buat Scatterplot
                fig = px.scatter(
                    x=landsat_values,
                    y=sentinel_values,
                    labels={"x": "NDMI Landsat 8", "y": "NDMI Sentinel-2"},
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
                            text="NDMI Landsat 8",
                            font=dict(color="black", family="Poppins, sans-serif"),
                        ),
                        tickfont=dict(color="black", family="Poppins, sans-serif"),
                    ),
                    yaxis=dict(
                        title=dict(
                            text="NDMI Sentinel-2",
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
                        label="r (Korelasi)",
                        value=f"{correlation_coef:.4f}",
                        help="Koefisien Korelasi Pearson (-1 hingga 1)",
                    )

            with col2_validate_metric:
                with st.container(border=True):
                    st.metric(
                        label="RMSE", value=f"{rmse:.4f}", help="Root Mean Square Error"
                    )

            with col3_validate_metric:
                with st.container(border=True):
                    st.metric(
                        label="MAE", value=f"{mae:.4f}", help="Mean Absolute Error"
                    )

            # Container Analisis Tren
            with st.container(border=True):
                st.markdown("💡**Quick Insight**")

                # Interpretasi Korelasi
                if abs(correlation_coef) >= 0.9:
                    corr_interpretation = "Sangat Kuat"
                    corr_color = "🟢"
                elif abs(correlation_coef) >= 0.7:
                    corr_interpretation = "Kuat"
                    corr_color = "🟡"
                elif abs(correlation_coef) >= 0.5:
                    corr_interpretation = "Sedang"
                    corr_color = "🟠"
                else:
                    corr_interpretation = "Lemah"
                    corr_color = "🔴"

                # Interpretasi RMSE
                if rmse <= 0.05:
                    rmse_interpretation = "Sangat Baik"
                    rmse_color = "🟢"
                elif rmse <= 0.1:
                    rmse_interpretation = "Baik"
                    rmse_color = "🟡"
                elif rmse <= 0.15:
                    rmse_interpretation = "Cukup"
                    rmse_color = "🟠"
                else:
                    rmse_interpretation = "Perlu Perbaikan"
                    rmse_color = "🔴"

                st.markdown(
                    f"""
                - **Sampel**: {len(landsat_values)} Titik
                - **Korelasi**: {corr_color} {corr_interpretation} (r = {correlation_coef:.4f})
                - **Akurasi**: {rmse_color} {rmse_interpretation} (RMSE = {rmse:.4f})
                - **p-value**: {p_value:.3f} (Sangat Signifikan)
                """
                )

                # Status Validasi
                if correlation_coef >= 0.7 and rmse <= 0.1:
                    st.success("✅ Validasi SUKSES")
                elif correlation_coef >= 0.5 and rmse <= 0.15:
                    st.warning("⚠️ Validasi CUKUP - Ada perbedaan minor")
                else:
                    st.error("❌ Validasi KURANG - Perlu investigasi lebih lanjut")

    except FileNotFoundError:
        st.error("❌ File 'stats/ndmiSampelValidasi.csv' tidak ditemukan!")
        st.info(
            "Pastikan file CSV hasil sampling dari GEE sudah tersedia di folder 'stats/'"
        )

    except Exception as e:
        st.error(f"❌ Error dalam memproses data: {str(e)}")
        st.info(
            "Periksa format file CSV dan nama kolom ('ndmiLandsat' dan 'ndmiSentinel')"
        )

    # Row Peta NDMI Landsat 8 vs Sentinel-2
    # Threshold untuk Peta Validasi
    validation_thresholds = {
        "landsat": {"low": -0.309, "medium": -0.162, "high": -0.015},
        "sentinel": {"low": -0.238, "medium": -0.0927, "high": 0.053},
    }

    st.badge(
        "**Peta NDMI: Landsat 8 vs Sentinel-2 (2024)**",
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
                        <div style="width: 12px; height: 12px; background-color: #006400; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Non-terbangun</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #ffffe0; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Rendah</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #ffa500; border: 1px solid #ddd;"></div>
                        <span style="color: #333;">Sedang</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 12px; height: 12px; background-color: #3b060a; border: 1px solid #ddd;"></div>
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
