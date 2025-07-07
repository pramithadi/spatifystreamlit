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
            margin-top: -3rem !important;
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
        
        .main {
            padding: 0 !important;
        }

        .block-container {
            padding: 0.5rem 1rem !important;
            margin-top: 1.5rem !important;
        }

        /* Mengurangi space header toolbar */
        div[data-testid="stToolbar"] {
            min-height: 40px !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.subheader("Google Colaboratory Projects")
col1, col2 = st.columns(2, gap="small")
with col1:
    with st.container(border=False):
        st.write("**Prediksi Penutup Lahan 2029**")
        st.image("./assets/lst.png")
        st.link_button(
            label="Project",
            url="https://code.earthengine.google.com/75fba0edce5cc401e8db57af47c6e6d6",
            icon=":material/touch_double:",
        )

with col2:
    with st.container(border=False):
        st.write("**Prediksi LST 2029**")
        st.image("./assets/ndbi.png")
        st.link_button(
            label="Project",
            url="",
            icon=":material/touch_double:",
        )
