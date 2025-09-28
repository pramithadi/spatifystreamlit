import streamlit as st

st.set_page_config(
    page_title="Project — Spatify",
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

st.header("Proyek")
st.write(
    "Pilih salah satu proyek di bawah untuk mengakses *source code* dan melihat proses pemodelan."
)

st.write("")
st.badge("**Google Earth Engine**", color="blue")
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    with st.container(border=True):
        st.badge("**Suhu Permukaan Lahan**", color="primary")
        st.image("./assets/GEE LST.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/fa4a032754384daa0bfaefde1b1c4f69",
            icon=":material/code_blocks:",
        )

with col2:
    with st.container(border=True):
        st.badge("**NDBI**", color="primary")
        st.image("./assets/GEE NDBI.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/b43d07c746b983ff080138893eed1a06",
            icon=":material/code_blocks:",
        )

with col3:
    with st.container(border=True):
        st.badge("**NDMI**", color="primary")
        st.image("./assets/GEE NDMI.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/b38e0814eabe25e4e0367e035c3a9961",
            icon=":material/code_blocks:",
        )

st.write("")

col4, col5, col6 = st.columns(3, gap="small")
with col4:
    with st.container(border=True):
        st.badge("**NDVI**", color="primary")
        st.image("./assets/GEE NDVI.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/0c8dc99810e93869024106b2049cf593",
            icon=":material/code_blocks:",
        )

with col5:
    with st.container(border=True):
        st.badge("**Penutup Lahan**", color="primary")
        st.image("./assets/GEE PL.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/3e3bf0e723ee4f6d9faa18077064416f",
            icon=":material/code_blocks:",
        )

with col6:
    with st.container(border=True):
        st.badge("**Elevasi dan Slope**", color="primary")
        st.image("./assets/GEE DEM.png")
        st.link_button(
            label="Source Code",
            url="https://code.earthengine.google.com/0be4ecfe67a86c42719d81bec2497843",
            icon=":material/code_blocks:",
        )

st.markdown(
    """
    ---
    """
)

st.badge("**Google Colab**", color="orange")

col7, col8, col9 = st.columns(3, gap="small")
with col7:
    with st.container(border=True):
        st.badge("**Prediksi Suhu Permukaan Lahan 2029**", color="primary")
        st.image("./assets/Colab LST.png")
        st.link_button(
            label="Source Code",
            url="https://colab.research.google.com/drive/1rrMcMVWlQcpqy-NFUf0cQeIKmd4uWjhA?usp=sharing",
            icon=":material/code_blocks:",
        )

with col8:
    with st.container(border=True):
        st.badge("**Prediksi Penutup Lahan 2029**", color="primary")
        st.image("./assets/Colab PL.png")
        st.link_button(
            label="Source Code",
            url="https://colab.research.google.com/drive/14ZqVdo-GDFBnRXpx1GIVthxeduIXpEfp?usp=sharing",
            icon=":material/code_blocks:",
        )

with col9:
    with st.container(border=True):
        st.badge("**Proyeksi Indeks 2029**", color="primary")
        st.image("./assets/Colab Indeks.png")
        st.link_button(
            label="Source Code",
            url="https://colab.research.google.com/drive/17qZCeWXODz7oDnSGS1vN5hHcbbY4k_Dk?usp=sharing",
            icon=":material/code_blocks:",
        )
