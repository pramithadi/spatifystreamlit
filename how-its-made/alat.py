import streamlit as st

st.set_page_config(
    page_title="Alat — Spatify",
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

    div[data-testid="stToolbar"] {
        min-height: 40px !important;
    }
    
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

st.header("Alat")
st.write(
    "Serangkaian alat, *platform*, dan *software* untuk ekstraksi, pemodelan, validasi, dan visualisasi data."
)
st.write("")

col1, col2, col3, col4, col5 = st.columns(5, gap="small")
with col1:
    st.badge("**Laptop**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_laptop.svg")

with col2:
    st.badge("**Google Earth Engine**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_gee.svg")

with col3:
    st.badge("**Google Colab**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_colab.svg")

with col4:
    st.badge("**Google Chrome**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_chrome.svg")

with col5:
    st.badge("**ArcGIS**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_arcgis.svg")

col6, col7, col8, col9, col10 = st.columns(5, gap="small")
with col6:
    st.badge("**Google Spreadsheet**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_sheets.svg")

with col7:
    st.badge("**Google Maps**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_gmaps.svg")

with col8:
    st.badge("**Google Drive**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_drive.svg")

with col9:
    st.badge("**Google Earth Pro**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_googleearth.svg")

with col10:
    st.badge("**Visual Studio Code**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_visualstudiocode.svg")

col11, col12, col13, col14, col15 = st.columns(5, gap="small")
with col11:
    st.badge("**GitHub**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_github.svg")

with col12:
    st.badge("**Git Bash**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_gitbash.svg")

with col13:
    st.badge("**Canva**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_canva.svg")

with col14:
    st.badge("**Avenza Maps**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_avenza.svg")

with col15:
    st.badge("**Termometer Inframerah**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_termometer.svg")

st.markdown(
    """
    ---
    """
)

st.header("Library")
st.write(
    "*Framework* dan *library* Python untuk pemodelan *machine learning* dan pembangunan *web app* interaktif."
)
st.write("")

col16, col17, col18, col19, col20 = st.columns(5, gap="small")
with col16:
    st.badge("**Rasterio**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_rasterio.svg")

with col17:
    st.badge("**NumPy**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_numpy.svg")

with col18:
    st.badge("**scikit-learn**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_sklearn.svg")

with col19:
    st.badge("**XGBoost**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_xgboost.svg")

with col20:
    st.badge("**Streamlit**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_streamlit.svg")

col21, col22, col23, col24, col25 = st.columns(5, gap="small")
with col21:
    st.badge("**pandas**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_pandas.svg")

with col22:
    st.badge("**GeoPandas**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_geopandas.svg")

with col23:
    st.badge("**SHAP**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_shap.svg")

with col24:
    st.badge("**Matplotlib**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_matplotlib.svg")

with col25:
    st.badge("**Plotly**", color="primary")
    with st.container(border=True):
        st.image("./logo/logo_plotly.svg")
