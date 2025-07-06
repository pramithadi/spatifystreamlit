import streamlit as st

# Font Poppins
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif !important; }
    </style>
""", unsafe_allow_html=True)

# Home Page
home = st.Page("home.py", title="Home", icon=":material/home:", default=True)

# Maps Section
lst = st.Page("maps/lst.py", title="LST", icon=":material/thermometer:")
lulc = st.Page("maps/lulc.py", title="Penutup Lahan", icon=":material/landscape_2:")
ndbi = st.Page("maps/ndbi.py", title="NDBI", icon=":material/apartment:")
ndmi = st.Page("maps/ndmi.py", title="NDMI", icon=":material/water_voc:")
ndvi = st.Page("maps/ndvi.py", title="NDVI", icon=":material/psychiatry:")

# How It's Made Section
gee = st.Page("howItsMade/gee.py", title="Google Earth Engine", icon=":material/globe_location_pin:")
colab = st.Page("howItsMade/colab.py", title="Google Colaboratory", icon=":material/code_blocks:")

# Get Results Section
downloadMaps = st.Page("getResults/downloadMaps.py", title="Download Maps", icon=":material/download:")
generateReports = st.Page("getResults/generateReports.py", title="Generate Reports", icon=":material/file_save:")

pg = st.navigation(
    {
        "": [home],
        "Maps": [lst, lulc, ndbi, ndmi, ndvi],
        "How It's Made": [gee, colab],
        "Get Results": [downloadMaps, generateReports],
    }
)
pg.run()