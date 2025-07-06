import streamlit as st

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Hanya memengaruhi konten, bukan elemen kontrol */
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
            font-family: 'Poppins', sans-serif !important;
        }

        div[data-testid="stMarkdownContainer"] * {
            font-family: 'Poppins', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #27548A !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover [data-baseweb="tab-highlight"] {
        background-color: #27548A !important;
    }
    .stTabs {
    margin-top: -5rem !important;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Google Colaboratory", "Data Sources", "Processing Pipeline", "Performance Metrics"])

with tab1:
    st.header("Google Colaboratory")
    st.write("Page under construction")
with tab2:
    st.header("Data Sources")
    st.write("Page under construction")
with tab3:
    st.header("Processing Pipeline")
    st.write("Page under construction")
with tab4:
    st.header("Performance Metrics")
    st.write("Page under construction")
