import streamlit as st

st.markdown("""
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
        
        /* Custom container styling dengan hover effect - hanya untuk container dengan border */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
        
        # /* Hide border untuk row containers */
        # div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        #     border: none !important;
        #     background: transparent !important;
        #     box-shadow: none !important;
        #     padding: 0 !important;
        # }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover [data-baseweb="tab-highlight"] {
        background-color: #27548A !important;
    }
    .stTabs {
        margin-top: -5rem !important;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["**Google Colaboratory**", "**Data**", "**Processing Pipeline**"])

with tab1:
    st.header("Google Colaboratory")
    st.write("Page under construction")
with tab2:
    st.subheader("Data")
    # Row 1: Landsat datasets
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        st.badge("**Citra Landsat 5 TM**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** C02 L2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write("**Bands:** Band 3 (Red), Band 4 (NIR), Band 5 (SWIR-1), Band 6 (Thermal)")
            st.write("**Tahun:** 1999, 2004")
            st.write("**Aplikasi:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(label="Detail", url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LT05_C02_T1_L2", icon=":material/touch_double:")
    
    with col2:
        st.badge("**Citra Landsat 7 ETM+**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** C02 L2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write("**Bands:** Band 3 (Red), Band 4 (NIR), Band 5 (SWIR-1), Band 6 (Thermal)")
            st.write("**Tahun:** 2004")
            st.write("**Aplikasi:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(label="Detail", url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C02_T1_L2", icon=":material/touch_double:")
    
    with col3:
        st.badge("**Citra Landsat 8 OLI/TIRS**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** C02 L2 Tier 1 (Surface Reflectance)")
            st.write("**Penyedia:** USGS")
            st.write("**Resolusi:** 30m")
            st.write("**Bands:** Band 4 (Red), Band 5 (NIR), Band 6 (SWIR-1), Band 10 (TIRS-1)")
            st.write("**Tahun:** 2014, 2019, 2024")
            st.write("**Aplikasi:** LST, NDBI, NDMI, NDVI, Penutup Lahan")
            st.link_button(label="Detail", url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2", icon=":material/touch_double:")
    
    # Row 2: Sentinel-2, SRTM, and SHP
    col4, col5, col6 = st.columns(3, gap="small")
    
    with col4:
        st.badge("**SHP Batas Administrasi**", color="primary")
        with st.container(border=True):
            st.write("**Penyedia:** Badan Informasi Geospasial")
            st.write("**Cakupan**: Kawasan Perkotaan Yogyakarta dan Sekitarnya")
            st.write("**Referensi**: Perda Daerah Istimewa Yogyakarta Nomor 5 Tahun 2019")
            st.write("**Aplikasi:** Area of Interest (AOI)")
            st.link_button(label="Detail", url="https://tanahair.indonesia.go.id/portal-web/", icon=":material/touch_double:")
    
    with col5:
        st.badge("**Citra Radar NASA SRTM**", color="primary")
        with st.container(border=True):
            st.write("**Penyedia:** NASA/USGS/JPL-Caltech")
            st.write("**Resolusi:** 30m")
            st.write("**Aplikasi:** Elevasi, Kemiringan Lereng (Slope)")
            st.link_button(label="Detail", url="https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003", icon=":material/touch_double:")
    
    with col6:
        st.badge("**Citra Sentinel-2 MSI**", color="primary")
        with st.container(border=True):
            st.write("**Koleksi:** Level-2A (Surface Reflectance) ")
            st.write("**Penyedia:** European Union/ESA/Copernicus")
            st.write("**Resolusi:** 10m")
            st.write("**Bands:** Band 4 (Red), Band 8 (NIR), Band 11 (SWIR-1)")
            st.write("**Tahun:** 2024")
            st.write("**Aplikasi:** Validasi Indeks")
            st.link_button(label="Detail", url="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED", icon=":material/touch_double:")
    
with tab3:
    st.header("Processing Pipeline")
    st.write("Page under construction")