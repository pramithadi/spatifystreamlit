import streamlit as st
import os
import requests

st.set_page_config(
    page_title="Download Peta — Spatify",
    layout="wide",
    initial_sidebar_state="expanded",  # collapsed
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
    .stDownloadButton > button {
        background-color: #E4EFE7 !important;
        color: black !important;
        border: none !important;
        border-radius: 3px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #6A9C89 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        # box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3) !important;
    }
    .stDownloadButton > button:active {
        transform: translateY(0px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "https://raw.githubusercontent.com/pramithadi/spatifystreamlit/main"


def column_download_section(title):
    st.badge(f"**{title}**", color="primary")


def create_download_section(title, image_file, pdf_file, file_name, key_suffix):
    image_url = f"{BASE_URL}/assets/{image_file}"
    pdf_url = f"{BASE_URL}/downloads/{pdf_file}"

    st.image(image_url)

    try:
        r = requests.get(pdf_url)
        if r.status_code == 200:
            file_data = r.content
            st.download_button(
                label="Download",
                icon=":material/download:",
                data=file_data,
                file_name=file_name,
                mime="application/pdf",
                key=f"download_{key_suffix}",
                use_container_width=True,
            )
        else:
            st.button(
                "Coming Soon!",
                disabled=True,
                key=f"unavailable_{key_suffix}",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.button("❌ Error", disabled=True, key=f"error_{key_suffix}")


st.header("Download Peta")
(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
) = st.tabs(
    [
        "🌡️ LST",
        "🏭 NDBI",
        "💧 NDMI",
        "🌳 NDVI",
        "🏞️ Penutup Lahan",
    ]
)

# ------------------------------------------------------------------
# TAB 1 – LST
# ------------------------------------------------------------------
with tab1:
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("LST 1999")
        with st.container(border=False):
            create_download_section(
                "LST 1999",
                "LST%201999.png",
                "LST%201999.pdf",
                "LST 1999.pdf",
                "lst_1999",
            )
    with col2:
        column_download_section("LST 2004")
        with st.container(border=False):
            create_download_section(
                "LST 2004",
                "LST%202004.png",
                "LST%202004.pdf",
                "LST 2004.pdf",
                "lst_2004",
            )
    with col3:
        column_download_section("LST 2009")
        with st.container(border=False):
            create_download_section(
                "LST 2009",
                "LST%202009.png",
                "LST%202009.pdf",
                "LST 2009.pdf",
                "lst_2009",
            )

    col4, col5, col6, col7 = st.columns(4, gap="small")
    with col4:
        column_download_section("LST 2014")
        with st.container(border=False):
            create_download_section(
                "LST 2014",
                "LST%202014.png",
                "LST%202014.pdf",
                "LST 2014.pdf",
                "lst_2014",
            )
    with col5:
        column_download_section("LST 2019")
        with st.container(border=False):
            create_download_section(
                "LST 2019",
                "LST%202019.png",
                "LST%202019.pdf",
                "LST 2019.pdf",
                "lst_2019",
            )
    with col6:
        column_download_section("LST 2024")
        with st.container(border=False):
            create_download_section(
                "LST 2024",
                "LST%202024.png",
                "LST%202024.pdf",
                "LST 2024.pdf",
                "lst_2024",
            )
    with col7:
        column_download_section("LST 2029")
        with st.container(border=False):
            create_download_section(
                "LST 2029",
                "LST%202029.png",
                "LST%202029.pdf",
                "LST 2029.pdf",
                "lst_2029",
            )

# ------------------------------------------------------------------
# TAB 2 – NDBI
# ------------------------------------------------------------------
with tab2:
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDBI 1999")
        with st.container(border=False):
            create_download_section(
                "NDBI 1999",
                "NDBI%201999.png",
                "NDBI%201999.pdf",
                "NDBI 1999.pdf",
                "ndbi_1999",
            )
    with col2:
        column_download_section("NDBI 2004")
        with st.container(border=False):
            create_download_section(
                "NDBI 2004",
                "NDBI%202004.png",
                "NDBI%202004.pdf",
                "NDBI 2004.pdf",
                "ndbi_2004",
            )
    with col3:
        column_download_section("NDBI 2009")
        with st.container(border=False):
            create_download_section(
                "NDBI 2009",
                "NDBI%202009.png",
                "NDBI%202009.pdf",
                "NDBI 2009.pdf",
                "ndbi_2009",
            )

    col4, col5, col6, col7 = st.columns(4, gap="small")
    with col4:
        column_download_section("NDBI 2014")
        with st.container(border=False):
            create_download_section(
                "NDBI 2014",
                "NDBI%202014.png",
                "NDBI%202014.pdf",
                "NDBI 2014.pdf",
                "ndbi_2014",
            )
    with col5:
        column_download_section("NDBI 2019")
        with st.container(border=False):
            create_download_section(
                "NDBI 2019",
                "NDBI%202019.png",
                "NDBI%202019.pdf",
                "NDBI 2019.pdf",
                "ndbi_2019",
            )
    with col6:
        column_download_section("NDBI 2024")
        with st.container(border=False):
            create_download_section(
                "NDBI 2024",
                "NDBI%202024.png",
                "NDBI%202024.pdf",
                "NDBI 2024.pdf",
                "ndbi_2024",
            )
    with col7:
        column_download_section("NDBI 2029")
        with st.container(border=False):
            create_download_section(
                "NDBI 2029",
                "NDBI%202029.png",
                "NDBI%202029.pdf",
                "NDBI 2029.pdf",
                "ndbi_2029",
            )

# ------------------------------------------------------------------
# TAB 3 – NDMI
# ------------------------------------------------------------------
with tab3:
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDMI 1999")
        with st.container(border=False):
            create_download_section(
                "NDMI 1999",
                "NDMI%201999.png",
                "NDMI%201999.pdf",
                "NDMI 1999.pdf",
                "ndmi_1999",
            )
    with col2:
        column_download_section("NDMI 2004")
        with st.container(border=False):
            create_download_section(
                "NDMI 2004",
                "NDMI%202004.png",
                "NDMI%202004.pdf",
                "NDMI 2004.pdf",
                "ndmi_2004",
            )
    with col3:
        column_download_section("NDMI 2009")
        with st.container(border=False):
            create_download_section(
                "NDMI 2009",
                "NDMI%202009.png",
                "NDMI%202009.pdf",
                "NDMI 2009.pdf",
                "ndmi_2009",
            )

    col4, col5, col6, col7 = st.columns(4, gap="small")
    with col4:
        column_download_section("NDMI 2014")
        with st.container(border=False):
            create_download_section(
                "NDMI 2014",
                "NDMI%202014.png",
                "NDMI%202014.pdf",
                "NDMI 2014.pdf",
                "ndmi_2014",
            )
    with col5:
        column_download_section("NDMI 2019")
        with st.container(border=False):
            create_download_section(
                "NDMI 2019",
                "NDMI%202019.png",
                "NDMI%202019.pdf",
                "NDMI 2019.pdf",
                "ndmi_2019",
            )
    with col6:
        column_download_section("NDMI 2024")
        with st.container(border=False):
            create_download_section(
                "NDMI 2024",
                "NDMI%202024.png",
                "NDMI%202024.pdf",
                "NDMI 2024.pdf",
                "ndmi_2024",
            )
    with col7:
        column_download_section("NDMI 2029")
        with st.container(border=False):
            create_download_section(
                "NDMI 2029",
                "NDMI%202029.png",
                "NDMI%202029.pdf",
                "NDMI 2029.pdf",
                "ndmi_2029",
            )

# ------------------------------------------------------------------
# TAB 4 – NDVI
# ------------------------------------------------------------------
with tab4:
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDVI 1999")
        with st.container(border=False):
            create_download_section(
                "NDVI 1999",
                "NDVI%201999.png",
                "NDVI%201999.pdf",
                "NDVI 1999.pdf",
                "ndvi_1999",
            )
    with col2:
        column_download_section("NDVI 2004")
        with st.container(border=False):
            create_download_section(
                "NDVI 2004",
                "NDVI%202004.png",
                "NDVI%202004.pdf",
                "NDVI 2004.pdf",
                "ndvi_2004",
            )
    with col3:
        column_download_section("NDVI 2009")
        with st.container(border=False):
            create_download_section(
                "NDVI 2009",
                "NDVI%202009.png",
                "NDVI%202009.pdf",
                "NDVI 2009.pdf",
                "ndvi_2009",
            )

    col4, col5, col6, col7 = st.columns(4, gap="small")
    with col4:
        column_download_section("NDVI 2014")
        with st.container(border=False):
            create_download_section(
                "NDVI 2014",
                "NDVI%202014.png",
                "NDVI%202014.pdf",
                "NDVI 2014.pdf",
                "ndvi_2014",
            )
    with col5:
        column_download_section("NDVI 2019")
        with st.container(border=False):
            create_download_section(
                "NDVI 2019",
                "NDVI%202019.png",
                "NDVI%202019.pdf",
                "NDVI 2019.pdf",
                "ndvi_2019",
            )
    with col6:
        column_download_section("NDVI 2024")
        with st.container(border=False):
            create_download_section(
                "NDVI 2024",
                "NDVI%202024.png",
                "NDVI%202024.pdf",
                "NDVI 2024.pdf",
                "ndvi_2024",
            )
    with col7:
        column_download_section("NDVI 2029")
        with st.container(border=False):
            create_download_section(
                "NDVI 2029",
                "NDVI%202029.png",
                "NDVI%202029.pdf",
                "NDVI 2029.pdf",
                "ndvi_2029",
            )

# ------------------------------------------------------------------
# TAB 5 – Penutup Lahan
# ------------------------------------------------------------------
with tab5:
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("Penutup Lahan 1999")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 1999",
                "Penutup%20Lahan%201999.png",
                "Penutup%20Lahan%201999.pdf",
                "Penutup Lahan 1999.pdf",
                "lulc_1999",
            )
    with col2:
        column_download_section("Penutup Lahan 2004")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2004",
                "Penutup%20Lahan%202004.png",
                "Penutup%20Lahan%202004.pdf",
                "Penutup Lahan 2004.pdf",
                "lulc_2004",
            )
    with col3:
        column_download_section("Penutup Lahan 2009")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2009",
                "Penutup%20Lahan%202009.png",
                "Penutup%20Lahan%202009.pdf",
                "Penutup Lahan 2009.pdf",
                "lulc_2009",
            )

    col4, col5, col6, col7 = st.columns(4, gap="small")
    with col4:
        column_download_section("Penutup Lahan 2014")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2014",
                "Penutup%20Lahan%202014.png",
                "Penutup%20Lahan%202014.pdf",
                "Penutup Lahan 2014.pdf",
                "lulc_2014",
            )
    with col5:
        column_download_section("Penutup Lahan 2019")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2019",
                "Penutup%20Lahan%202019.png",
                "Penutup%20Lahan%202019.pdf",
                "Penutup Lahan 2019.pdf",
                "lulc_2019",
            )
    with col6:
        column_download_section("Penutup Lahan 2024")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2024",
                "Penutup%20Lahan%202024.png",
                "Penutup%20Lahan%202024.pdf",
                "Penutup Lahan 2024.pdf",
                "lulc_2024",
            )
    with col7:
        column_download_section("Penutup Lahan 2029")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2029",
                "Penutup%20Lahan%202029.png",
                "Penutup%20Lahan%202029.pdf",
                "Penutup Lahan 2029.pdf",
                "lulc_2029",
            )
