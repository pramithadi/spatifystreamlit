import streamlit as st

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
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 12px !important;
            box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
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
        margin-top: -5rem !important;
    }
    .stCode {
        margin-bottom: 0.5rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["**Catalog**", "**Snippets**"])

with tab1:
    st.subheader("Catalog")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.badge("**Citra Landsat 5 TM**", color="primary")
        with st.container(border=False):
            st.write("**Koleksi:** Collection 2 Level 2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write(
                "**Bands:** Band 3 (Red), Band 4 (NIR), Band 5 (SWIR-1), Band 6 (Thermal)"
            )
            st.write("**Tahun:** 1999, 2009")
            st.write("**Kegunaan:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(
                label="Detail",
                url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LT05_C02_T1_L2",
                icon=":material/touch_double:",
            )

    with col2:
        st.badge("**Citra Landsat 7 ETM+**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** Collection 2 Level 2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write(
                "**Bands:** Band 3 (Red), Band 4 (NIR), Band 5 (SWIR-1), Band 6 (Thermal)"
            )
            st.write("**Tahun:** 2004")
            st.write("**Kegunaan:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(
                label="Detail",
                url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C02_T1_L2",
                icon=":material/touch_double:",
            )

    col3, col4 = st.columns(2, gap="small")
    with col3:
        st.badge("**Citra Landsat 8 OLI/TIRS**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** Collection 2 Level 2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write(
                "**Bands:** Band 4 (Red), Band 5 (NIR), Band 6 (SWIR-1), Band 10 (TIRS-1)"
            )
            st.write("**Tahun:** 2014, 2019, 2024")
            st.write("**Kegunaan:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(
                label="Detail",
                url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2",
                icon=":material/touch_double:",
            )

    with col4:
        st.badge("**Citra Radar NASA SRTM**", color="primary")
        with st.container(border=True):
            st.write(
                "**Koleksi:** Shuttle Radar Topography Mission (SRTM) Digital Elevation"
            )
            st.write("**Penyedia:** NASA/USGS/JPL-Caltech")
            st.write("**Resolusi:** 1 arc-second (30m)")
            st.write("**Tahun:** 2000")
            st.write("**Kegunaan:** Elevasi, Kemiringan Lereng (Slope)")
            st.link_button(
                label="Detail",
                url="https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003",
                icon=":material/touch_double:",
            )

    col5, col6 = st.columns(2, gap="small")
    with col5:
        st.badge("**Citra Sentinel-2 MSI**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** Level-2A (Surface Reflectance) ")
            st.write("**Penyedia:** European Union/ESA/Copernicus")
            st.write("**Resolusi:** 10m")
            st.write("**Bands:** Band 4 (Red), Band 8 (NIR), Band 11 (SWIR-1)")
            st.write("**Tahun:** 2024")
            st.write("**Kegunaan:** Validasi NDBI, NDMI, NDVI")
            st.link_button(
                label="Detail",
                url="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
                icon=":material/touch_double:",
            )

    with col6:
        st.badge("**SHP Batas Administrasi**", color="primary")
        with st.container(border=True):
            st.write("**Penyedia:** Badan Informasi Geospasial")
            st.write("**Cakupan**: Kabupaten Bantul, Kabupaten Sleman, Kota Yogyakarta")
            st.write(
                "**Referensi**: Perda Daerah Istimewa Yogyakarta Nomor 5 Tahun 2019"
            )
            st.write(
                "**Kegunaan:** Area of Interest (AOI) Kawasan Perkotaan Yogyakarta dan Sekitarnya"
            )
            st.link_button(
                label="Detail",
                url="https://tanahair.indonesia.go.id/portal-web/",
                icon=":material/touch_double:",
            )

with tab2:
    st.subheader("Snippets")
    st.badge("**Citra Landsat 5 TM Surface Reflectance**", color="primary")
    snippetLandsat5 = """var dataset = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')"""
    st.code(snippetLandsat5, language="javascript", line_numbers=True)

    st.badge("**Citra Landsat 7 ETM+ Surface Reflectance**", color="primary")
    snippetLandsat7 = """var dataset = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')"""
    st.code(snippetLandsat7, language="javascript", line_numbers=True)

    st.badge("**Citra Landsat 8 OLI/TIRS Surface Reflectance**", color="primary")
    snippetLandsat8 = """var dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')"""
    st.code(snippetLandsat8, language="javascript", line_numbers=True)

    st.badge("**Citra Radar NASA SRTM**", color="primary")
    snippetRadar = """var dataset = ee.Image('USGS/SRTMGL1_003')"""
    st.code(snippetRadar, language="javascript", line_numbers=True)

    st.badge("**Citra Sentinel-2 MSI Surface Reflectance**", color="primary")
    snippetSentinel = (
        """var dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')"""
    )
    st.code(snippetSentinel, language="javascript", line_numbers=True)
