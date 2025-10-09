import streamlit as st

st.set_page_config(
    page_title="GEE Apps — Spatify",
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
    # div[data-testid="stVerticalBlockBorderWrapper"] {
    #     padding: 12px !important;
    # }
    # div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
    #     border: 0.5px solid rgba(0, 0, 0, 0.1) !important;
    #     border-radius: 1px !important;
    #     padding: 12px !important;
    #     # box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
    #     # background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
    #     transition: all 0.3s ease !important;
    # }
    # div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
    #     transform: translateY(-4px) !important;
    #     box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important; # Shadow Hover
    #     border-color: #fdfaf6 !important;
    # }   
    .stLinkButton > a {
        background-color: #E4EFE7 !important;
        color: black !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .stLinkButton > a:hover {
        background-color: #6A9C89 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        # box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3) !important;
    }
    .stLinkButton > a:active {
        transform: translateY(0px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.header("Google Earth Engine Applications")
st.write("Temukan berbagai visualisasi data interaktif melalui GEE *Apps* berikut.")
col1, col2 = st.columns(2, gap="small")
with col1:
    with st.container(border=True):
        st.badge("**LST**", color="primary")
        st.image("./assets/GEE Apps LST.png")
        st.link_button(
            label="GEE Apps",
            url="https://ee-pramithadi.projects.earthengine.app/view/spatifylst",
            icon=":material/map:",
        )

with col2:
    with st.container(border=True):
        st.badge("**NDVI**", color="primary")
        st.image("./assets/GEE Apps NDVI.png")
        st.link_button(
            label="GEE Apps",
            url="https://ee-pramithadi.projects.earthengine.app/view/spatifyndvi",
            icon=":material/map:",
        )

col3, col4 = st.columns(2, gap="small")
with col3:
    with st.container(border=True):
        st.badge("**NDBI**", color="primary")
        st.image("./assets/GEE Apps NDBI.png")
        st.link_button(
            label="GEE Apps",
            url="https://ee-pramithadi.projects.earthengine.app/view/spatifyndbi",
            icon=":material/map:",
        )

with col4:
    with st.container(border=True):
        st.badge("**NDMI**", color="primary")
        st.image("./assets/GEE Apps NDMI.png")
        st.link_button(
            label="GEE Apps",
            url="https://ee-pramithadi.projects.earthengine.app/view/spatifyndmi",
            icon=":material/map:",
        )

col5, col6 = st.columns(2, gap="small")
with col5:
    with st.container(border=True):
        st.badge("**Penutup Lahan**", color="primary")
        st.image("./assets/GEE Apps PL.png")
        st.link_button(
            label="GEE Apps",
            url="https://ee-pramithadi.projects.earthengine.app/view/spatifypl",
            icon=":material/map:",
        )
