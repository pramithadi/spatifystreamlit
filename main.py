import streamlit as st

# Font Poppins
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# Home Page
home = st.Page("home.py", title="Home", icon=":material/home:", default=True)

# Maps Section
lst = st.Page("maps/lst.py", title="LST", icon=":material/thermometer:")
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
    title="Workflow",
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
    "getResults/downloadMaps.py", title="Download Maps", icon=":material/download:"
)

pg = st.navigation(
    {
        "": [home],
        "Maps": [lst, ndbi, ndmi, ndvi, lulc],
        "How It's Made": [dataSource, workflow, gee, colab],
        "Get Results": [downloadMaps],
    }
)
pg.run()
