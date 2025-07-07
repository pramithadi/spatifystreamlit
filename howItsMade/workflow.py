import streamlit as st
from streamlit_image_comparison import image_comparison

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
            text-align: justify !important;
            line-height: 1.6 !important;
        }
        .stSubheader {
            font-size: 16px !important;
            margin-bottom: 12px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 12px !important;
            box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            border-color: #fdfaf6 !important;
        }
        
        /* Custom class for justified text */
        .justified-text {
            text-align: justify !important;
            line-height: 1.6 !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
            font-family: 'Poppins', sans-serif !important;
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
    .stCode {
        margin-bottom: 0.5rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "**Prapengolahan Data**",
        "**Time-Series**",
        "**Pemodelan Prediksi**",
        "**Validasi**",
    ]
)

with tab1:
    st.subheader("Prapengolahan Data")
    # Scaling Factor
    st.badge("**Scaling Factor**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Scaling Factor</strong> digunakan untuk mengembalikan nilai reflektansi citra Landsat Surface Reflectance yang sebelumnya berformat <em>integer</em> menjadi <em>float</em> agar hasil pengolahan data memiliki ketelitian hingga tingkat desimal (USGS, 2020).
        </div>
        """,
        unsafe_allow_html=True,
    )

    codeScalingFactor = """
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBands, null, true);
}
"""
    st.code(codeScalingFactor, language="javascript", line_numbers=True)

    # Cloud Masking
    st.badge("**Cloud Masking**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Cloud Masking</strong> metode <strong>Quality Assesment (QA)</strong> merupakan metode untuk mengurangi tutupan awan dalam citra (Sinabutar, 2020). Metode ini bekerja otomatis dengan memberi tanda pada piksel-piksel awan kemudian menyortir piksel tersebut agar tidak digunakan dalam analisis. Celah yang kosong lantas diisi dengan piksel lain yang lebih bersih melalui teknik <strong>Median Composite</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    codeScalingFactor = """
function maskLsr(image) {
  var cloudShadowBitMask = (1 << 4);
  var cloudsBitMask = (1 << 3);
  var cirrus = (1 << 2);
  var qa = image.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
             .and(qa.bitwiseAnd(cloudsBitMask).eq(0))
             .and(qa.bitwiseAnd(cirrus).eq(0));
  return image.updateMask(mask);
}
"""
    st.code(codeScalingFactor, language="javascript", line_numbers=True)

    # Hasil Prapengolahan Data
    st.write("Tampilan citra sebelum dan sesudah Cloud Masking:")
    from streamlit_image_comparison import image_comparison

    image_comparison(
        img1="./assets/before.png",
        img2="./assets/after.png",
        label1="Sebelum",
        label2="Sesudah",
        width=700,
        starting_position=50,
        show_labels=True,
        make_responsive=True,
    )
    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # Filtering Citra
    st.badge("**Penyaringan Citra**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Penyaringan</strong> bertujuan untuk menyortir citra sesuai dengan <em>snippet</em>, lokasi kajian (Kawasan Perkotaan Yogyakarta dan sekitarnya), periode musim kemarau; pengaplikasian <em>function scaling factor, cloud masking,</em> <em>median composite</em>; dan pemotongan <em>(clip)</em> citra.
        </div>
        """,
        unsafe_allow_html=True,
    )

    codeScalingFactor = """
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate('2024-04-21', '2024-10-31') // berdasarkan kajian periode normal rata-rata klimatologi 1991-2020 yang dikeluarkan oleh BMKG
    .filterBounds(loc)
    .map(applyScaleFactors8)
    .map(maskLsr)
    .median()
    .clip(loc);
"""
    st.code(codeScalingFactor, language="javascript", line_numbers=True)

with tab2:
    st.subheader("Time-Series")


with tab3:
    st.subheader("Pemodelan Prediksi")

with tab4:
    st.subheader("Validasi")
