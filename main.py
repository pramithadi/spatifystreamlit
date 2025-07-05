import streamlit as st

# Home Page
home = st.Page("home.py", title="Home", icon="🏠", default=True)

# Maps Section
lst = st.Page("maps/lst.py", title="LST", icon="🌡️")
lulc = st.Page("maps/lulc.py", title="Penutup Lahan", icon="🏔️")
ndbi = st.Page("maps/ndbi.py", title="NDBI", icon="🏢")
ndmi = st.Page("maps/ndmi.py", title="NDMI", icon="💧")
ndvi = st.Page("maps/ndvi.py", title="NDVI", icon="🌳")

# How It's Made Section
gee = st.Page("howItsMade/gee.py", title="Google Earth Engine", icon="🌍")
colab = st.Page("howItsMade/colab.py", title="Google Colab", icon="💻")

# Get Results Section
downloadMaps = st.Page("getResults/downloadMaps.py", title="Download Maps", icon="📥")
generateReports = st.Page("getResults/generateReports.py", title="Generate Reports", icon="📋")

pg = st.navigation(
    {
        "": [home],
        "Maps": [lst, lulc, ndbi, ndmi, ndvi],
        "How It's Made": [gee, colab],
        "Get Results": [downloadMaps, generateReports],
    }
)
pg.run()