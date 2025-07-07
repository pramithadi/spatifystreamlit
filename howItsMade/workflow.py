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
        "**Prapengolahan**",
        "**Time-Series**",
        "**Prediksi**",
        "**Validasi**",
    ]
)

with tab1:
    st.subheader("Prapengolahan")
    # Scaling Factor
    st.badge("**Scaling Factor**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Scaling Factor</strong> digunakan untuk mengembalikan nilai reflektansi citra Landsat Surface Reflectance yang sebelumnya berformat integer menjadi float agar hasil pengolahan data memiliki ketelitian hingga tingkat desimal (USGS, 2020).
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
        <strong>Penyaringan</strong> bertujuan untuk menyortir citra sesuai dengan snippet, lokasi kajian (Kawasan Perkotaan Yogyakarta dan sekitarnya), periode musim kemarau; penerapan function scaling factor, cloud masking, median composite; dan pemotongan (clip) citra.
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
    option = st.selectbox(
        "Pilih Parameter:",
        ("LST", "NDBI", "NDMI", "NDVI", "Penutup Lahan", "Elevasi dan Slope"),
    )
    if option == "LST":
        st.markdown(
            """
            <div class="justified-text">
            Ekstraksi LST dalam penelitian ini menggunakan metode <strong>Single-Channel</strong> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2009). Metode ini terdiri atas empat tahapan utama yaitu:
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Nilai Radiansi Spektral
        st.badge("**Perhitungan Nilai Radiansi Spektral**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Pada citra Landsat Surface Reflectance, nilai radiansi spektral telah dikalibrasi secara otomatis melalui penerapan <strong>Scaling Factor</strong> dalam tahapan prapengolahan data.
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Perhitungan Emisivitas Permukaan
        st.badge("**Perhitungan Emisivitas Permukaan**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Emisivitas permukaan (ε) adalah kemampuan objek dalam menyerap radiasi matahari dan memancarkan radiasi termal (Mallick et al., 2012).
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Function Emisivitas Permukaan
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Formula Emisivitas Permukaan (ε)",
            r"\epsilon = 0.004 \times \text{Pv} + 0.986",
        )

        # Function Proporsi Vegetasi
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Formula Proporsi Vegetasi (Pv)",
            r"Pv = \left( \frac{NDVI - NDVI_{min}}{NDVI_{max} - NDVI_{min}} \right)^2",
        )

        # Function NDVI
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Formula NDVI",
            r"NDVI = \frac{NIR - Red}{NIR + Red}",
        )

        codeEmisivitasPermukaan = """
// Perhitungan NDVI
var ndvi = landsat.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi');

// Perhitungan Proporsi Vegetasi (Pv)
var ndviMin = ee.Number(ndvi.reduceRegion({
  reducer: ee.Reducer.min(),
  geometry: loc,
  scale: 30,
  maxPixels: 1e9
}).values().get(0));

var ndviMax = ee.Number(ndvi.reduceRegion({
  reducer: ee.Reducer.max(),
  geometry: loc,
  scale: 30,
  maxPixels: 1e9
}).values().get(0));

var pv = (ndvi.subtract(ndviMin).divide(ndviMax.subtract(ndviMin))).pow(ee.Number(2)).rename('pv');

// Perhitungan Emisivitas Permukaan (ε)
var k1 = ee.Number(0.004);
var k2 = ee.Number(0.986);
var emisivitas = pv.multiply(k1).add(k2).rename('emisivitas');
"""
        st.code(codeEmisivitasPermukaan, language="javascript", line_numbers=True)

        st.badge("**Perhitungan Brightness Temperature**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Brightness Temperature adalah representasi suhu permukaan dari pancaran radiasi termal objek yang direkam oleh sensor termal dalam format kelvin (Jatayu & Susetyo, 2017). Nilai saluran termal pada citra Landsat Surface Reflectance telah dikonversi ke satuan Kelvin melalui penerapan Scaling Factor sehingga dapat langsung digunakan dalam estimasi Brightness Temperature. Saluran termal yang digunakan berasal dari band 6 untuk citra Landsat 5 dan Landsat 7, serta band 10 untuk citra Landsat 8.
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeBrightnessTemperature = """
// Pemilihan Saluran Termal untuk Brightness Temperature
var btLandsat5 = landsat5.select('ST_B6');
var btLandsat7 = landsat7.select('ST_B6');
var btLandsat8 = landsat8.select('ST_B10');
"""
        st.code(codeBrightnessTemperature, language="javascript", line_numbers=True)

        st.badge("**Perhitungan LST**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Perhitungan LST melibatkan nilai brightness temperature, emisivitas permukaan, panjang gelombang elektromagnetik saluran termal, dan radiasi emisivitas yang didapatkan dari estimasi konstanta Planck, konstanta Stefan-Boltzmann, dan kecepatan cahaya (Waleed & Sajjad, 2021).
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Function NDVI
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Formula LST",
            r"LST = \left( \frac{B_T}{1 + \left( \frac{\lambda \cdot B_T}{\rho} \right) \cdot \ln \epsilon} \right) - 273.15",
        )

        codeLST = """
// Pemilihan LST
var lst = btLandsat8.expression(
  '(Bt/(1+(0.00115*(Bt/1.438))*log(Ep)))-273.15', {
    'Bt': bt,
    'Ep': emisi
  }).rename('lst');
"""
        st.code(codeLST, language="javascript", line_numbers=True)

    elif option == "NDBI":
        st.badge("**Normalized Difference Built-Up Index (NDBI)**", color="primary")
        st.write("NDBI adalah indeks kerapatan bangunan")
    elif option == "NDMI":
        st.badge("**Normalized Difference Moisture Index (NDMI)**", color="primary")
        st.write("NDBI adalah indeks kelembapan vegetasi")
    elif option == "NDVI":
        st.badge("**Normalized Difference Vegetation Index (NDVI)**", color="primary")
        st.write("NDBI adalah indeks kerapatan vegetasi")
    elif option == "Penutup Lahan":
        st.badge("**Penutup Lahan**", color="primary")
        st.write("Proses Penutup Lahan menggunakan citra Sentinel-2.")
    elif option == "Elevasi dan Slope":
        st.badge("**Elevasi**", color="primary")
        st.write("Proses Elevasi dan Slope menggunakan citra SRTM.")
        st.badge("**Slope**", color="primary")


with tab3:
    st.subheader("Prediksi")
    option = st.selectbox(
        "Pilih Pemodelan:",
        ("Prediksi LST 2029", "Prediksi Penutup Lahan 2029"),
    )
    if option == "Prediksi LST 2029":
        st.write("**Land Surface Temperature (LST)**")
        st.markdown(
            """
            <div class="justified-text">
            LST adalah ukuran kuantitatif mengenai seberapa panas permukaan bumi (Ahyar et al., 2024). Ekstraksi LST dalam penelitian ini menggunakan metode <strong>Single-Channel</strong> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2009). Metode ini terdiri atas empat tahapan utama yaitu:
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif option == "Prediksi Penutup Lahan 2029":
        st.badge("**Normalized Difference Built-Up Index (NDBI)**", color="primary")
        st.write("NDBI adalah indeks kerapatan bangunan")

with tab4:
    st.subheader("Validasi")
