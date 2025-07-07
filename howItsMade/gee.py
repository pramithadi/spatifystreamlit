import streamlit as st

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
        
        /* Custom container styling dengan hover effect - hanya untuk container dengan border */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
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
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["**Projects**", "**Code**", "**Pipeline**"])

with tab1:
    st.subheader("Projects")
    st.write("Projects Google Earth Engine tersedia di:")
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        with st.container(border=True):
            st.write("**LST**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

    with col2:
        with st.container(border=True):
            st.write("**NDBI**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

    with col3:
        with st.container(border=True):
            st.write("**NDMI**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

    col4, col5, col6 = st.columns(3, gap="small")
    with col4:
        with st.container(border=True):
            st.write("**NDVI**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

    with col5:
        with st.container(border=True):
            st.write("**Penutup Lahan**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

    with col6:
        with st.container(border=True):
            st.write("**Elevasi dan Slope**")
            st.image("./assets/lst.png")
            st.link_button(
                label="Proyek",
                url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
                icon=":material/touch_double:",
            )

with tab2:
    st.subheader("Processing Pipeline")
    st.write("Page under construction")

with tab3:
    st.subheader("Processing Pipeline")
    st.write("Page under construction")
