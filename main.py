import streamlit as st

# Font Poppins
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif !important; }
    
    /* GLOBAL BLACK COLOR UNTUK SEMUA TEXT ELEMENTS */
    
    /* Headers - st.header, st.subheader, st.title */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Streamlit Headers Specific */
    .stMarkdown h1,
    .stMarkdown h2, 
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #000000 !important;
    }
    
    /* st.write, st.text, paragraph text */
    .stMarkdown p,
    .stText,
    .stMarkdown div,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] div,
    div[data-testid="stText"] {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #000000 !important;
    }
    
    /* Labels untuk input elements */
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
    
    /* Metrics labels */
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: #000000 !important;
    }
    
    /* Dataframe text */
    .stDataFrame,
    .stDataFrame table,
    .stDataFrame th,
    .stDataFrame td {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Alert/Info/Warning/Error text content */
    div[data-testid="stAlert"] div,
    div[data-testid="stInfo"] div,
    div[data-testid="stWarning"] div,
    div[data-testid="stError"] div,
    div[data-testid="stSuccess"] div {
        color: #000000 !important;
    }
    
    /* Sidebar navigation text only */
    section[data-testid="stSidebar"] a span {
        color: #000000 !important;
    }
    
    /* Container text */
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
    
    /* Column text */
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
    
    /* Tab text */
    .stTabs [data-baseweb="tab-list"] button p {
        color: #000000 !important;
    }
    
    /* Expander text */
    details summary p,
    .stExpander p,
    .stExpander div {
        color: #000000 !important;
    }
    
    /* Caption text */
    .stCaption,
    small {
        color: #000000 !important;
    }
    
    /* Badge/Pills tetap menggunakan warna default mereka */
    div[data-testid="stPills"] button,
    div[data-testid="stPills"] button p,
    .stButton button,
    .stButton button p {
        /* Biarkan warna default */
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Home Page
home = st.Page("home.py", title="Beranda", icon=":material/home:", default=True)

# Maps Section
lst = st.Page(
    "maps/lst.py", title="Suhu Permukaan Lahan", icon=":material/thermometer:"
)
ndbi = st.Page("maps/ndbi.py", title="NDBI", icon=":material/apartment:")
ndmi = st.Page("maps/ndmi.py", title="NDMI", icon=":material/water_voc:")
ndvi = st.Page("maps/ndvi.py", title="NDVI", icon=":material/psychiatry:")
lulc = st.Page("maps/lulc.py", title="Penutup Lahan", icon=":material/landscape_2:")

# How It's Made Section
dataSource = st.Page(
    "howItsMade/dataSource.py", title="Dataset", icon=":material/database:"
)
workflow = st.Page(
    "howItsMade/workflow.py",
    title="Alur Pemrosesan",
    icon=":material/flowchart:",
)
gee = st.Page(
    "howItsMade/gee.py",
    title="Google Earth Engine",
    icon=":material/globe_location_pin:",
)
colab = st.Page(
    "howItsMade/colab.py", title="Google Colaboratory", icon=":material/code_blocks:"
)

# Get Results Section
downloadMaps = st.Page(
    "getResults/downloadMaps.py", title="Download Peta", icon=":material/download:"
)

pg = st.navigation(
    {
        "": [home],
        "Dashboard": [lst, ndbi, ndmi, ndvi, lulc],
        "How It's Made": [dataSource, workflow, gee, colab],
        "Get Results": [downloadMaps],
    }
)
pg.run()
