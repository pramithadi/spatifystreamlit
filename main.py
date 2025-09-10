import streamlit as st

# Font Poppins
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif !important; }
    
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stMarkdown h1,
    .stMarkdown h2, 
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #000000 !important;
    }
    
    .stMarkdown p,
    .stText,
    .stMarkdown div,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] div,
    div[data-testid="stText"] {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stMarkdown {
        color: #000000 !important;
    }
    
    label,
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stTextArea label,
    .stDateInput label,
    .stTimeInput label,
    .stFileUploader label,
    .stColorPicker label {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: #000000 !important;
    }
    
    .stDataFrame,
    .stDataFrame table,
    .stDataFrame th,
    .stDataFrame td {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    div[data-testid="stAlert"] div,
    div[data-testid="stInfo"] div,
    div[data-testid="stWarning"] div,
    div[data-testid="stError"] div,
    div[data-testid="stSuccess"] div {
        color: #000000 !important;
    }
    
    section[data-testid="stSidebar"] a span {
        color: #000000 !important;
    }
    
    div[data-testid="stVerticalBlock"] p,
    div[data-testid="stVerticalBlock"] div,
    div[data-testid="stVerticalBlock"] h1,
    div[data-testid="stVerticalBlock"] h2,
    div[data-testid="stVerticalBlock"] h3,
    div[data-testid="stVerticalBlock"] h4,
    div[data-testid="stVerticalBlock"] h5,
    div[data-testid="stVerticalBlock"] h6 {
        color: #000000 !important;
    }
    
    div[data-testid="column"] p,
    div[data-testid="column"] div,
    div[data-testid="column"] h1,
    div[data-testid="column"] h2,
    div[data-testid="column"] h3,
    div[data-testid="column"] h4,
    div[data-testid="column"] h5,
    div[data-testid="column"] h6 {
        color: #000000 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button p {
        color: #000000 !important;
    }
    
    details summary p,
    .stExpander p,
    .stExpander div {
        color: #000000 !important;
    }
    
    .stCaption,
    small {
        color: #000000 !important;
    }
    
    div[data-testid="stPills"] button,
    div[data-testid="stPills"] button p,
    .stButton button,
    .stButton button p {
        /* Tetap Warna Default */
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Home Page
home = st.Page("home.py", title="Beranda", icon=":material/home:", default=True)

# Section Analisis
lulc = st.Page(
    "maps/penutup-lahan.py", title="Penutup Lahan", icon=":material/landscape_2:"
)
ndbi = st.Page("maps/ndbi.py", title="NDBI", icon=":material/apartment:")
ndmi = st.Page("maps/ndmi.py", title="NDMI", icon=":material/water_voc:")
ndvi = st.Page("maps/ndvi.py", title="NDVI", icon=":material/psychiatry:")
lst = st.Page(
    "maps/lst.py", title="Suhu Permukaan Lahan", icon=":material/thermometer:"
)

# Section How It's Made
dataset = st.Page("howItsMade/dataset.py", title="Dataset", icon=":material/database:")
workflow = st.Page(
    "howItsMade/workflow.py",
    title="Alur Proses",
    icon=":material/flowchart:",
)
project = st.Page(
    "howItsMade/proyek.py",
    title="Project",
    icon=":material/code_blocks:",
)
gee_apps = st.Page(
    "maps/gee-apps.py", title="GEE Apps", icon=":material/globe_location_pin:"
)

# Get Results Section
download_peta = st.Page(
    "getResults/download-peta.py", title="Download Peta", icon=":material/download:"
)
galeri = st.Page(
    "getResults/galeri.py", title="Galeri", icon=":material/gallery_thumbnail:"
)

pg = st.navigation(
    {
        "": [home],
        "Analisis": [lulc, ndbi, ndmi, ndvi, lst],
        "How It's Made": [dataset, workflow, gee_apps],
        "Get Results": [download_peta, galeri],
    }
)
pg.run()
