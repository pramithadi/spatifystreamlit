import streamlit as st
from streamlit_image_comparison import image_comparison

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        # .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
        #     font-family: 'Poppins', sans-serif !important;
        # }
        # div[data-testid="stMarkdownContainer"] * {
        #     font-family: 'Poppins', sans-serif !important;
        # }
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
            # font-family: 'Poppins', sans-serif !important;
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
        "**Pengolahan Time-Series**",
        "**Pemodelan Prediksi**",
        "**Validasi Data**",
    ]
)

with tab1:
    st.header("Prapengolahan Data")
    # Filtering Citra
    st.badge("**Penyaringan Citra**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        Tahap ini bertujuan untuk menyortir citra dalam Google Earth Engine sesuai dengan batasan penelitian.
        </div>
        """,
        unsafe_allow_html=True,
    )

    codeScalingFactor = """
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate('2024-04-21', '2024-10-31') // Mengacu pada kajian Periode Normal Rata-rata Klimatologi 1991-2020 dari Badan Meteorologi Klimatologi dan Geofisika
    .filterBounds(loc)
    .map(applyScaleFactors) // Function Scaling Factor
    .map(maskLsr) // Function Cloud Masking
    .median() // Median Composite
    .clip(loc);
"""
    st.code(codeScalingFactor, language="javascript", line_numbers=True)

    # Scaling Factor
    st.badge("**Scaling Factor**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Scaling Factor</strong> digunakan untuk mengembalikan nilai radiansi dan reflektansi citra Landsat Surface Reflectance yang sebelumnya berformat <strong>integer</strong> menjadi <strong>float</strong> agar hasil pengolahan data memiliki ketelitian hingga tingkat desimal (USGS, 2020).
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
        <strong>Cloud Masking</strong> metode <strong>Quality Assesment (QA)</strong> merupakan teknik untuk mengurangi tutupan awan dalam citra (Sinabutar, 2020). Metode ini bekerja otomatis dengan memberi tanda pada piksel-piksel awan kemudian menyortir piksel tersebut agar tidak digunakan dalam analisis. Celah yang kosong lantas diisi dengan piksel lain yang lebih bersih melalui teknik <strong>Median Composite</strong>.
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
    st.write(
        "Berikut ini merupakan contoh tampilan citra Landsat 8 Surface Reflectance tahun 2024 sebelum dan sesudah dilakukan tahap pembersihan awan:"
    )
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

# tab 2
with tab2:
    st.header("Pengolahan Time-Series")
    option = st.pills(
        "Pilih Pengolahan Data:",
        ["LST", "NDBI", "NDMI", "NDVI", "Penutup Lahan", "Elevasi dan Slope"],
        default="LST",
    )

    if option == "LST":
        st.subheader("**Land Surface Temperature (LST)**")
        st.markdown(
            """
            <div class="justified-text">
            Ekstraksi Land Surface Temperature (LST) dalam penelitian ini menggunakan metode <strong>Single-Channel</strong> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2009). Metode ini terdiri atas empat tahap perhitungan, yaitu:
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Nilai Radiansi Spektral
        st.badge("**1. Perhitungan Nilai Radiansi Spektral**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Nilai radiansi spektral pada dataset Landsat Surface Reflectance telah dikalibrasi secara otomatis melalui penerapan function <strong>Scaling Factor</strong> dalam tahapan prapengolahan data. Dengan demikian, nilai radiansi spektral dari saluran termal citra Landsat Surface Reflectance dapat langsung digunakan untuk perhitungan LST.
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Perhitungan Emisivitas Permukaan
        st.badge("**2. Perhitungan Emisivitas Permukaan**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Emisivitas permukaan (ε) adalah kemampuan suatu objek dalam menyerap radiasi matahari dan memancarkan radiasi termal (Mallick et al., 2012). Penelitian ini menggunakan pendekatan NDVI dan Proportion of Vegetation (Pv) untuk mendapatkan nilai emisivitas permukaan. Berikut ini contoh rumus dan implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus NDVI
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Rumus NDVI",
            r"NDVI = \frac{NIR - Red}{NIR + Red}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        NDVI = Normalized Difference Vegetation Index<br>
        NIR = Band 4 (Landsat 5 dan Landsat 7), Band 5 (Landsat 8)<br>
        Red = Band 3 (Landsat 5 dan Landsat 7), Band 4 (Landsat 8)
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode NDVI
        codeNDVIEmisi = """
// Perhitungan NDVI
var ndvi = landsat.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi');
"""
        st.code(codeNDVIEmisi, language="javascript", line_numbers=True)

        # Rumus Proporsi Vegetasi
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Rumus Proportion of Vegetation",
            r"Pv = \left( \frac{NDVI - NDVI_{min}}{NDVI_{max} - NDVI_{min}} \right)^2",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        Pv = Proportion of Vegetation<br>
        NDVI = Nilai NDVI<br>
        NDVImin = Nilai Minimum NDVI <br>
        NDVImax = Nilai Maksimum NDVI
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Pv
        codePv = """
// Perhitungan Proportion of Vegetation (Pv)
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
"""
        st.code(codePv, language="javascript", line_numbers=True)

        # Rumus Emisivitas Permukaan
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Rumus Emisivitas Permukaan",
            r"\epsilon = 0.004 \times \text{Pv} + 0.986",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        ε = Emisivitas Permukaan<br>
        Pv = Nilai Proportion of Vegetation
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeEmisivitasPermukaan = """
// Perhitungan Emisivitas Permukaan (ε)
var k1 = ee.Number(0.004);
var k2 = ee.Number(0.986);
var emisivitas = pv.multiply(k1).add(k2).rename('emisivitas');
"""
        st.code(codeEmisivitasPermukaan, language="javascript", line_numbers=True)

        # Perhitungan Brightness Temperature
        st.badge("**3. Perhitungan Brightness Temperature**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Brightness temperature merupakan representasi suhu permukaan yang diperoleh dari radiasi termal objek kemudian direkam oleh sensor termal dan disajikan dalam satuan kelvin (Jatayu & Susetyo, 2017). Penerapan function Scaling Factor di tahapan sebelumnya telah mengkalibrasi saluran termal ke dalam satuan kelvin sehingga dapat langsung dimanfaatkan sebagai nilai brightness temperature (Waleed & Sajjad, 2021). Adapun saluran termal yang digunakan berasal dari band 6 untuk citra Landsat 5 dan Landsat 7, serta band 10 untuk citra Landsat 8.
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

        st.badge("**4. Perhitungan LST**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Perhitungan LST melibatkan nilai brightness temperature, emisivitas permukaan, panjang gelombang saluran termal, serta nilai radiasi emisivitas yang diestimasi dari konstanta Planck, Stefan-Boltzmann, dan kecepatan cahaya (Waleed & Sajjad, 2021). Berikut ini contoh rumus dan implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus LST
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

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        LST = Suhu Permukaan Lahan (°C)<br>
        BT = Nilai Brightness Temperature (K)<br>
        λ = Panjang Gelombang Saluran Termal (11,5 µm)<br>
        ρ = Radiasi Emisivitas (1,438 × 10-2 mK)<br>
        ε = Nilai Emisivitas Permukaan
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeLST = """
// Perhitungan LST
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
