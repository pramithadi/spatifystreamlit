import streamlit as st
import os

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
            border-radius: 3px !important;
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


def column_download_section(title):
    st.badge(f"**{title}**", color="primary")


def create_download_section(title, image_path, file_path, file_name, key_suffix):
    st.image(image_path)

    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()

            st.download_button(
                label="Download",
                icon=":material/download:",
                data=file_data,
                file_name=file_name,
                mime="application/pdf",
                key=f"download_{key_suffix}",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.button("❌ Error", disabled=True, key=f"error_{key_suffix}")
    else:
        st.button(
            "Coming Soon :)",
            disabled=True,
            key=f"unavailable_{key_suffix}",
            use_container_width=True,
        )


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["**LST**", "**NDBI**", "**NDMI**", "**NDVI**", "**Penutup Lahan**"]
)

with tab1:
    st.header("Download Peta LST")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        column_download_section("LST 1999")
        with st.container(border=False):
            create_download_section(
                "LST 1999",
                "./assets/LST1999.png",
                "./downloads/LST 1999.pdf",
                "LST 1999.pdf",
                "lst_1999",
            )

    with col2:
        column_download_section("LST 2004")
        with st.container(border=False):
            create_download_section(
                "LST 2004",
                "./assets/lst.png",
                "./downloads/LST 2004.pdf",
                "LST 2004.pdf",
                "lst_2004",
            )

    col3, col4, col5 = st.columns(3, gap="small")
    with col3:
        column_download_section("LST 2009")
        with st.container(border=False):
            create_download_section(
                "LST 2009",
                "./assets/lst.png",
                "./downloads/LST 2009.pdf",
                "LST 2009.pdf",
                "lst_2009",
            )

    with col4:
        column_download_section("LST 2014")
        with st.container(border=False):
            create_download_section(
                "LST 2014",
                "./assets/lst.png",
                "./downloads/LST 2014.pdf",
                "LST 2014.pdf",
                "lst_2014",
            )

    with col5:
        column_download_section("LST 2019")
        with st.container(border=False):
            create_download_section(
                "LST 2019",
                "./assets/lst.png",
                "./downloads/LST 2019.pdf",
                "LST 2019.pdf",
                "lst_2019",
            )

    col6, col7 = st.columns(2, gap="small")
    with col6:
        column_download_section("LST 2024")
        with st.container(border=False):
            create_download_section(
                "LST 2024",
                "./assets/lst.png",
                "./downloads/LST 2024.pdf",
                "LST 2024.pdf",
                "lst_2024",
            )

    with col7:
        column_download_section("LST 2029")
        with st.container(border=False):
            create_download_section(
                "LST 2029",
                "./assets/lst.png",
                "./downloads/LST 2029.pdf",
                "LST 2029.pdf",
                "lst_2029",
            )

with tab2:
    st.header("Download Peta NDBI")

    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDBI 1999")
        with st.container(border=False):
            create_download_section(
                "NDBI 1999",
                "./assets/ndbi.png",
                "./downloads/NDBI 1999.pdf",
                "NDBI 1999.pdf",
                "ndbi_1999",
            )

    with col2:
        column_download_section("NDBI 2004")
        with st.container(border=False):
            create_download_section(
                "NDBI 2004",
                "./assets/ndbi.png",
                "./downloads/NDBI 2004.pdf",
                "NDBI 2004.pdf",
                "ndbi_2004",
            )

    with col3:
        column_download_section("NDBI 2009")
        with st.container(border=False):
            create_download_section(
                "NDBI 2009",
                "./assets/ndbi.png",
                "./downloads/NDBI 2009.pdf",
                "NDBI 2009.pdf",
                "ndbi_2009",
            )

    col4, col5, col6 = st.columns(3, gap="small")
    with col4:
        column_download_section("NDBI 2014")
        with st.container(border=False):
            create_download_section(
                "NDBI 2014",
                "./assets/ndbi.png",
                "./downloads/NDBI 2014.pdf",
                "NDBI 2014.pdf",
                "ndbi_2014",
            )

    with col5:
        column_download_section("NDBI 2019")
        with st.container(border=False):
            create_download_section(
                "NDBI 2019",
                "./assets/ndbi.png",
                "./downloads/NDBI 2019.pdf",
                "NDBI 2019.pdf",
                "ndbi_2019",
            )

    with col6:
        column_download_section("NDBI 2024")
        with st.container(border=False):
            create_download_section(
                "NDBI 2024",
                "./assets/ndbi.png",
                "./downloads/NDBI 2024.pdf",
                "NDBI 2024.pdf",
                "ndbi_2024",
            )

with tab3:
    st.header("Download Peta NDMI")

    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDMI 1999")
        with st.container(border=False):
            create_download_section(
                "NDMI 1999",
                "./assets/ndmi.png",
                "./downloads/NDMI 1999.pdf",
                "NDMI 1999.pdf",
                "ndmi_1999",
            )

    with col2:
        column_download_section("NDMI 2004")
        with st.container(border=False):
            create_download_section(
                "NDMI 2004",
                "./assets/ndmi.png",
                "./downloads/NDMI 2004.pdf",
                "NDMI 2004.pdf",
                "ndmi_2004",
            )

    with col3:
        column_download_section("NDMI 2009")
        with st.container(border=False):
            create_download_section(
                "NDMI 2009",
                "./assets/ndmi.png",
                "./downloads/NDMI 2009.pdf",
                "NDMI 2009.pdf",
                "ndmi_2009",
            )

    col4, col5, col6 = st.columns(3, gap="small")
    with col4:
        column_download_section("NDMI 2014")
        with st.container(border=False):
            create_download_section(
                "NDMI 2014",
                "./assets/ndmi.png",
                "./downloads/NDMI 2014.pdf",
                "NDMI 2014.pdf",
                "ndmi_2014",
            )

    with col5:
        column_download_section("NDMI 2019")
        with st.container(border=False):
            create_download_section(
                "NDMI 2019",
                "./assets/ndmi.png",
                "./downloads/NDMI 2019.pdf",
                "NDMI 2019.pdf",
                "ndmi_2019",
            )

    with col6:
        column_download_section("NDMI 2024")
        with st.container(border=False):
            create_download_section(
                "NDMI 2024",
                "./assets/ndmi.png",
                "./downloads/NDMI 2024.pdf",
                "NDMI 2024.pdf",
                "ndmi_2024",
            )

with tab4:
    st.header("Download Peta NDVI")

    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        column_download_section("NDVI 1999")
        with st.container(border=False):
            create_download_section(
                "NDVI 1999",
                "./assets/ndvi.png",
                "./downloads/NDVI 1999.pdf",
                "NDVI 1999.pdf",
                "ndvi_1999",
            )

    with col2:
        column_download_section("NDVI 2004")
        with st.container(border=False):
            create_download_section(
                "NDVI 2004",
                "./assets/ndvi.png",
                "./downloads/NDVI 2004.pdf",
                "NDVI 2004.pdf",
                "ndvi_2004",
            )

    with col3:
        column_download_section("NDVI 2009")
        with st.container(border=False):
            create_download_section(
                "NDVI 2009",
                "./assets/ndvi.png",
                "./downloads/NDVI 2009.pdf",
                "NDVI 2009.pdf",
                "ndvi_2009",
            )

    col4, col5, col6 = st.columns(3, gap="small")
    with col4:
        column_download_section("NDVI 2014")
        with st.container(border=False):
            create_download_section(
                "NDVI 2014",
                "./assets/ndvi.png",
                "./downloads/NDVI 2014.pdf",
                "NDVI 2014.pdf",
                "ndvi_2014",
            )

    with col5:
        column_download_section("NDVI 2019")
        with st.container(border=False):
            create_download_section(
                "NDVI 2019",
                "./assets/ndvi.png",
                "./downloads/NDVI 2019.pdf",
                "NDVI 2019.pdf",
                "ndvi_2019",
            )

    with col6:
        column_download_section("NDVI 2024")
        with st.container(border=False):
            create_download_section(
                "NDVI 2024",
                "./assets/ndvi.png",
                "./downloads/NDVI 2024.pdf",
                "NDVI 2024.pdf",
                "ndvi_2024",
            )

with tab5:
    st.header("Download Peta Penutup Lahan")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        column_download_section("Penutup Lahan 1999")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 1999",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 1999.pdf",
                "Penutup Lahan 1999.pdf",
                "lulc_1999",
            )

    with col2:
        column_download_section("Penutup Lahan 2004")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2004",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2004.pdf",
                "Penutup Lahan 2004.pdf",
                "lulc_2004",
            )

    col3, col4, col5 = st.columns(3, gap="small")
    with col3:
        column_download_section("Penutup Lahan 2009")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2009",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2009.pdf",
                "Penutup Lahan 2009.pdf",
                "lulc_2009",
            )

    with col4:
        column_download_section("Penutup Lahan 2014")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2014",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2014.pdf",
                "Penutup Lahan 2014.pdf",
                "lulc_2014",
            )

    with col5:
        column_download_section("Penutup Lahan 2019")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2019",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2019.pdf",
                "Penutup Lahan 2019.pdf",
                "lulc_2019",
            )

    col6, col7 = st.columns(2, gap="small")
    with col6:
        column_download_section("Penutup Lahan 2024")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2024",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2024.pdf",
                "Penutup Lahan 2024.pdf",
                "lulc_2024",
            )

    with col7:
        column_download_section("Penutup Lahan 2029")
        with st.container(border=False):
            create_download_section(
                "Penutup Lahan 2029",
                "./assets/lulc.png",
                "./downloads/Penutup Lahan 2029.pdf",
                "Penutup Lahan 2029.pdf",
                "lulc_2029",
            )
