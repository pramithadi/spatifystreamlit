import streamlit as st
from streamlit_image_comparison import image_comparison

st.set_page_config(
    page_title="Metodologi — Spatify",
    layout="wide",
    initial_sidebar_state="expanded",  # collapsed
)

# ==============================================================================
# CUSTOM CSS
# ==============================================================================
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    .main {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
    }
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
    div[data-testid="stMarkdownContainer"] h1 {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    .stApp > header {
        color: #000000 !important;
    }
    .stApp {
        color: #000000 !important;
    }
    .stMarkdown {
        color: #000000 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 12px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
        border: 0.5px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 1px !important;
        padding: 12px !important;
        # box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1) !important;
        # background: linear-gradient(135deg, #fdfaf6 0%, #f8fafc 100%) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important; # Shadow Hover
        border-color: #fdfaf6 !important;
    }     
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
        margin-top: 0rem !important;
    }

    div[data-testid="stToolbar"] {
        min-height: 40px !important;
    }
        
    /* Custom Justified */
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

# st.header("Metodologi")
(tab1, tab2, tab3, tab4, tab5) = st.tabs(
    [
        "🛠️ **Diagram Alir**",
        "🧹 **Prapengolahan Data**",
        "💻 **Pengolahan Data**",
        "✅ **Validasi Data**",
        "⚙️ **Pemodelan Prediksi**",
    ]
)

# ==============================================================================
# DIAGRAM ALIR
# ==============================================================================
with tab1:
    st.badge("**Diagram Alir Penelitian**", color="primary")
    st.image(
        "./assets/diagram_alir.svg",
    )

# ==============================================================================
# PRAPENGOLAHAN DATA
# ==============================================================================
with tab2:
    # Penyaringan Citra
    st.badge("**1. Penyaringan Citra**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        Tahap ini bertujuan untuk <b>menyortir citra</b> dalam Google Earth Engine sesuai dengan batasan penelitian yang telah ditetapkan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    codePenyaringanCitra = """
var landsat2024 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate('2024-04-21', '2024-10-31') // Periode Normal Rata-rata Klimatologi 1991-2020 menurut BMKG
    .filterBounds(loc)
    .map(applyScaleFactors8) // Function Scaling Factor
    .map(maskLsr) // Function Cloud Masking
    .median() // Median Composite
    .clip(loc);
"""
    st.code(codePenyaringanCitra, language="javascript", line_numbers=True)

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # Scaling Factor
    st.badge("**2. *Scaling Factor***", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <b><i>Scale factor</i></b> digunakan untuk <b>mengembalikan nilai</b> radiansi dan reflektansi citra Landsat <i>Surface Reflectance</i> yang awalnya berformat <b><i>integer</i></b> menjadi <b><i>float</i></b> agar data memiliki ketelitian sampai level desimal (USGS, 2023).
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

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # Cloud Masking
    st.badge("**3. *Cloud Masking***", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <b><i>Cloud masking</i></b> metode <b><i>quality assesment</i></b> <b>(QA)</b> merupakan teknik untuk <b>mengurangi tutupan awan</b> dalam citra (Sinabutar <em>et al.</em>, 2020).
        </div>
        """,
        unsafe_allow_html=True,
    )

    codeCloudMasking = """
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
    st.code(codeCloudMasking, language="javascript", line_numbers=True)

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
                - Sinabutar, J. J., Sasmito, B., Sukmono, A. (2020). Studi Cloud Masking Menggunakan Band Quality Assessment, Function of Mask, dan Multi-Temporal Cloud Masking pada Citra Landsat 8. *Jurnal Geodesi Undip*, 9(3). 51-60. https://doi.org/10.14710/jgundip.2020.28123 
                - United States Geological Survey. (2023). How Do I Use A Scale Factor with Landsat Level-2 Science Products?. (*https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products*, diakses 8 Juli 2025).
                """
        )

# ==============================================================================
# PENGOLAHAN DATA
# ==============================================================================
# tab 3
with tab3:
    option = st.pills(
        "**Lihat Pengolahan:**",
        [
            "🌡️ Suhu Permukaan Lahan",
            "🏭 NDBI",
            "💧 NDMI",
            "🌳 NDVI",
            "🏞️ Penutup Lahan",
            "🌋 Elevasi dan Slope",
        ],
        default="🌡️ Suhu Permukaan Lahan",
    )

    if option == "🌡️ Suhu Permukaan Lahan":
        st.subheader("**Suhu Permukaan Lahan**")
        st.markdown(
            """
            <div class="justified-text">
            Ekstraksi <b>suhu permukaan lahan</b> atau <i>land surface temperature</i> (LST) dilakukan dengan metode <b><i>Single-Channel</i></b> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2010).
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Nilai Radiansi Spektral
        st.badge("**1. Perhitungan Radiansi Spektral**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        <b>Nilai radiansi spektral</b> pada citra Landsat <i>Surface Reflectance</i> <b>telah dikalibrasi</b> secara otomatis melalui pengaplikasian <i>function</i> <b><i>scaling factor</i></b>. Dengan demikian, nilai radiansi spektral dari saluran termal di dataset ini dapat langsung digunakan dalam perhitungan LST.
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
        <b>Emisivitas permukaan (ε)</b> merupakan kapabilitas suatu objek dalam <b>menyerap radiasi</b> dari matahari dan <b>memantulkan</b> energi panas (radiasi termal) (Mallick <em>et al.</em>, 2012). Nilai emisivitas permukaan dalam penelitian ini dihitung menggunakan pendekatan NDVI dan <i>Proportion of Vegetation</i> (Pv).
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Validasi LST
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="justified-text">
        <b>• NDVI</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. Rumus NDVI
        display_equation_validate(
            r"NDVI = \frac{NIR - Red}{NIR + Red}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDVI = <i>Normalized Difference Vegetation Index</i><br>
        NIR = <i>band</i> 4 (Landsat 5 dan Landsat 7), <i>band</i> 5 (Landsat 8)<br>
        Red = <i>band</i> 3 (Landsat 5 dan Landsat 7), <i>band</i> 4 (Landsat 8)
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode NDVI
        codeNDVI = """
// Perhitungan NDVI
var ndvi1999 = landsat1999.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi1999'); // Landsat 5
var ndvi2004 = landsat2004.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi2004'); // Landsat 7
var ndvi2024 = landsat2024.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi2024'); // Landsat 8
"""
        st.code(codeNDVI, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Proportion of Vegetation</i> (Pv)</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 2. Rumus Pv
        display_equation_validate(
            r"Pv = \left( \frac{NDVI - NDVI_{min}}{NDVI_{max} - NDVI_{min}} \right)^2",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        Pv = proporsi vegetasi<br>
        NDVI = nilai NDVI<br>
        NDVI<sub>min</sub> = nilai minimum NDVI <br>
        NDVI<sub>max</sub> = nilai maksimum NDVI
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Pv
        codePv = """
// Perhitungan Pv
var pv2024 = (ndvi2024.subtract(ndvi2024min).divide(ndvi2024max.subtract(ndvi2024min))).pow(ee.Number(2)).rename('pv2024');
"""
        st.code(codePv, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• Emisivitas Permukaan</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. Rumus Emisivitas Permukaan
        display_equation_validate(
            r"\epsilon = 0.004 \times \text{Pv} + 0.986",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        ε = emisivitas permukaan<br>
        Pv = nilai Pv
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeEmisivitasPermukaan = """
// Perhitungan Emisivitas Permukaan (ε)
var k1 = ee.Number(0.004);
var k2 = ee.Number(0.986);
var emisi2024 = pv2024.multiply(k1).add(k2).rename('emisi2024');
"""
        st.code(codeEmisivitasPermukaan, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Perhitungan Brightness Temperature
        st.badge("**3. Perhitungan *Brightness Temperature***", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        <b><i>Brightness temperature</i></b> merupakan <b>nilai suhu permukaan</b> dari radiasi termal objek yang direkam oleh sensor termal kemudian disimpan dalam satuan <b>kelvin</b> (Jatayu & Susetyo, 2017). Penerapan <i>function scaling factor</i> di tahap sebelumnya telah <b>mengkalibrasi</b> saluran termal ke dalam satuan kelvin sehingga <b>dapat langsung dimanfaatkan</b> sebagai nilai <i>brightness temperature</i> (Waleed & Sajjad, 2022).
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeBrightnessTemperature = """
// Pemilihan Saluran Termal untuk Brightness Temperature
var bt1999 = landsat1999.select('ST_B6');
var bt2004 = landsat2004.select('ST_B6');
var bt2024 = landsat2024.select('ST_B10');
"""
        st.code(codeBrightnessTemperature, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.badge("**4. Perhitungan LST**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Nilai emisivitas permukaan dan <i>brightness temperature</i> yang telah didapatkan lalu <b>dikalkulasi</b> dengan <b>panjang gelombang saluran termal</b> dan nilai <b>radiasi emisivitas</b> (Waleed & Sajjad, 2022). Untuk mendapatkan <b>nilai LST</b> dalam derajat <b>celcius</b> maka perlu mengonversi hasilnya dengan nilai 273.15.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 3. Rumus LST
        display_equation_validate(
            r"LST = \left( \frac{B_T}{1 + \left( \frac{\lambda \cdot B_T}{\rho} \right) \cdot \ln \epsilon} \right) - 273.15",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        LST = suhu permukaan lahan (°C)<br>
        BT = nilai <i>brightness temperature</i> (K)<br>
        λ = panjang gelombang saluran termal (11,5 µm)<br>
        ρ = radiasi emisivitas (1,438 × 10-2 mK)<br>
        ε = nilai emisivitas permukaan
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeLST = """
// Perhitungan LST
var lst2024 = bt2024.expression(
  '(Bt/(1+(0.00115*(Bt/1.438))*log(Ep)))-273.15', {
    'Bt': bt2024,
    'Ep': emisi2024
  }).rename('lst2024');
"""
        st.code(codeLST, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Jatayu, A., & Susetyo, C. (2017). Analisis Perubahan Temperatur Permukaan Wilayah Surabaya Timur Tahun 2001-2016 Menggunakan Citra Landsat. *Jurnal Teknik ITS*, 6(2). 429-433. 
                - Jiménez-Muñoz, J. C., & Sobrino, J. A. (2010). A Single-Channel Algorithm for Land-Surface Temperature Retrieval from ASTER Data. *IEEE Geoscience and Remote Sensing Letters*, 7(1). 176-179. https://doi.org/10.1109/LGRS.2009.2029534
                - Mallick, J., Singh, C. K., Shashtri, S. Rahman, A., Mukherjee, S. (2012). Land Surface Emissivity Retrieval based on Moisture Index from Landsat TM Satellite Data over Heterogeneous Surfaces of Delhi City. *Internasional Journal of Applied Earth Observation and Geoinformation*, 19. 384-358. https://doi.org/10.1016/j.jag.2012.06.002
                - Waleed, M., & Sajjad, M. (2022). Leveraging Cloud-based Computing and Spatial Modelling Approaches for Land Surface Temperature Disparities in Response to Land Cover Change: Evidence from Pakistan. *Remote Sensing Applications: Society and Environment*, 25. 1-19. https://doi.org/10.1016/j.rsase.2021.100665 
                """
            )

    elif option == "🏭 NDBI":
        st.subheader("**Normalized Difference Built-Up Index (NDBI)**")
        st.markdown(
            """
            <div class="justified-text">
            Perhitungan <b>indeks kerapatan area terbangun</b> (NDBI) dilakukan dengan mengekstraksi nilai dari <b>saluran reflektif inframerah-dekat (NIR)</b> dan <b>inframerah-gelombang pendek (SWIR)</b> yang sangat sensitif terhadap area terbangun (Wicaksono <em>et al.</em>, 2021).
        </div>
        """,
            unsafe_allow_html=True,
        )

        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        # Rumus NDBI
        display_equation_validate(
            r"NDBI = \frac{SWIR - NIR}{SWIR + NIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDBI = <i>Normalized Difference Built-Up Index</i><br>
        SWIR = <i>band</i> 5 (Landsat 5 dan Landsat 7), <i>band</i> 6 (Landsat 8)<br>
        NIR = <i>band</i> 4 (Landsat 5 dan Landsat 7), <i>band</i> 5 (Landsat 8)
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode NDBI
        codeNDBI = """
// Perhitungan NDBI
var ndbi1999 = landsat1999.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndbi1999'); // Landsat 5
var ndbi2004 = landsat2004.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndbi2004'); // Landsat 7
var ndbi2024 = landsat2024.normalizedDifference(['SR_B6', 'SR_B5']).rename('ndbi2024'); // Landsat 8
"""
        st.code(codeNDBI, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Wicaksono, C. S. A., Sukmono, A., Hadi, F. (2021). Analisis Pengaruh Perubahan Komposisi Vegetasi dan Kawasan Terbangun terhadap Suhu Permukaan (Studi Kasus: Kota Tegal). *Jurnal Geodesi Undip*, 10(3). 1-10. https://doi.org/10.14710/jgundip.2021.31120 
                """
            )

    elif option == "💧 NDMI":
        st.subheader("**Normalized Difference Moisture Index (NDMI)**")
        st.markdown(
            """
            <div class="justified-text">
            <b>Indeks kelembapan vegetasi</b> (NDMI) dihitung dengan memanfaatkan <b>saluran reflektif inframerah-gelombang pendek (SWIR)</b> dan <b>inframerah-dekat (NIR)</b> serupa NDBI. Namun, terdapat perbedaan urutan saluran reflektif yang digunakan dalam formula sebagaimana dirumuskan oleh Gao (1996). Perhitungan NDMI menempatkan saluran NIR sebagai pengurang, berbeda dengan NDBI yang menggunakan SWIR di posisi tersebut.
        </div>
        """,
            unsafe_allow_html=True,
        )

        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        # Rumus NDMI
        display_equation_validate(
            r"NDMI = \frac{NIR - SWIR}{NIR + SWIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDMI = <i>Normalized Difference Moisture Index</i><br>
        NIR = <i>band</i> 4 (Landsat 5 dan Landsat 7), <i>band</i> 5 (Landsat 8)<br>
        SWIR = <i>band</i> 5 (Landsat 5 dan Landsat 7), <i>band</i> 6 (Landsat 8)
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode NDMI
        codeNDMI = """
// Perhitungan NDMI
var ndmi1999 = landsat1999.normalizedDifference(['SR_B4', 'SR_B5']).rename('ndbi1999'); // Landsat 5
var ndmi2004 = landsat2004.normalizedDifference(['SR_B4', 'SR_B5']).rename('ndbi2004'); // Landsat 7
var ndmi2024 = landsat2024.normalizedDifference(['SR_B5', 'SR_B6']).rename('ndbi2024'); // Landsat 8
"""
        st.code(codeNDMI, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Gao, B. C. (1996). NDWI - A Normalized Difference Water Index for Remote Sensing of Liquid Water from Space. *Remote Sensing of Environment*, 58. 257-266. https://doi.org/10.1016/S0034-4257(96)00067-3 
                """
            )

    elif option == "🌳 NDVI":
        st.subheader("**Normalized Difference Vegetation Index (NDVI)**")
        st.markdown(
            """
            <div class="justified-text">
            Perhitungan <b>indeks kerapatan vegetasi</b> (NDVI) dilakukan dengan mengekstraksi nilai dari reflektansi <b>saluran inframerah-dekat (NIR)</b> dan <b>saluran merah <i>(red)</i></b> (Estoque <em>et al.</em>, 2017).
        </div>
        """,
            unsafe_allow_html=True,
        )

        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        display_equation_validate(
            r"NDVI = \frac{NIR - Red}{NIR + Red}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDVI = <i>Normalized Difference Vegetation Index</i><br>
        NIR = <i>band</i> 4 (Landsat 5 dan Landsat 7), <i>band</i> 5 (Landsat 8)<br>
        Red = <i>band</i> 3 (Landsat 5 dan Landsat 7), <i>band</i> 4 (Landsat 8)
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode NDVI
        codeNDVI = """
// Perhitungan NDVI
var ndvi1999 = landsat1999.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi1999'); // Landsat 5
var ndvi2004 = landsat2004.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi2004'); // Landsat 7
var ndvi2024 = landsat2024.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi2024'); // Landsat 8
"""
        st.code(codeNDVI, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Estoque, Ronald, C., Murayama, Yuji. (2017). Landscape Pattern and Ecosystem Service Value Changes: Implications for Environmental Sustainability Planning for the Rapidly Urbanizing Summer Capital of the Philippines. *Landscape Urban Plan*, 116. 60-72. https://doi.org/10.1016/j.landurbplan.2013.04.008
                """
            )

    elif option == "🏞️ Penutup Lahan":
        st.subheader("**Penutup Lahan**")
        st.markdown(
            """
            <div class="justified-text">
            Penutup lahan dipetakan menggunakan metode <b>klasifikasi <i>supervised</i></b> pada citra multispektral. Metode ini <b>memanfaatkan sampel</b> dari tiap kelas penutup lahan untuk <b>melatih model klasifikasi</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Pembuatan Training Area
        st.badge("**1. Pembuatan *Training Area***", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        <b><i>Training area</i></b> adalah kumpulan sampel dari setiap kelas penutup lahan yang akan diklasifikasi. Klasifikasi penutup lahan mengacu pada sistem <b>SNI 7645:2010</b> yang telah disesuaikan dengan kondisi penutup lahan di lokasi penelitian. Kelas yang dipetakan meliputi <b>vegetasi, tubuh air, lahan terbangun, dan lahan terbuka</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeTrainingArea = """
// Pembuatan Training Area
var label = 'Class';
var bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'];
var input = landsat2024.select(bands);

// Penggabungan Training Area
var training = vegetasi
              .merge(tubuh_air)
              .merge(lahan_terbangun)
              .merge(lahan_terbuka);
print(training);

var trainImage = input.sampleRegions({
  collection: training,
  properties: [label],
  scale: 30
})
print(trainImage)
"""
        st.code(codeTrainingArea, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.image(
            "./assets/training_area2.png",
            caption="Persebaran Sampel Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya Tahun 2024",
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Klasifikasi Supervised
        st.badge("**2. Klasifikasi *Supervised***", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        Training area dianalisis menggunakan algoritma <b><i>Classification and Regression Tree</i> (CART)</b>. CART akan membentuk <b>aturan klasifikasi</b> dari sampel training area yang tersedia lalu <b>diaplikasikan</b> untuk <b>mengidentifikasi kelas penutup lahan</b> pada setiap piksel citra.
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeKlasifikasiSupervised = """
// Training Data pada Model CART
var trainingData = trainImage.randomColumn();
var trainSet = trainingData.filter(ee.Filter.lessThan('random', 0.8)); // Training Data 
var testSet = trainingData.filter(ee.Filter.greaterThanOrEquals('random', 0.8)); // Testing Data 

var classifier = ee.Classifier.smileCart().train(trainSet, label, bands);

// Klasifikasi Citra
var lulc2024 = input.classify(classifier);
print(lulc2024.getInfo());

// Visualisasi
var landcoverPalette = [
  '#294b29', // vegetasi
  '#69c3dd', // tubuh_air
  '#cd9a4d', // lahan_terbangun
  '#faf5d9', // lahan_terbuka
  ];
Map.addLayer(lulc2024, {palette: landcoverPalette, min: 0, max:3}, 'Klasifikasi Penutup Lahan');
"""
        st.code(codeKlasifikasiSupervised, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.image(
            "./assets/hasil_klasifikasi2.png",
            caption="Hasil Klasifikasi Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya Tahun 2024",
        )

        # st.markdown(
        #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        # )

        # # Uji Akurasi Model Klasifikasi
        # st.badge("**3. Uji Akurasi Model Klasifikasi**", color="primary")
        # st.markdown(
        #     """
        # <div class="justified-text">
        # <b>Uji akurasi</b> pada tahap ini dilakukan untuk <b>membandingkan hasil klasifikasi</b> model CART dengan <b>data training</b> dan <b>testing</b> yang dibagi dengan skema split <b>80% untuk training</b> dan <b>20% untuk testing</b>. Hasil <b>matriks konfusi</b> menunjukkan <b>akurasi keseluruhan</b> mencapai <b>91.43%</b>. Berikut contoh implementasi kode dalam Google Earth Engine.
        # </div>
        # """,
        #     unsafe_allow_html=True,
        # )

    #         codeUjiAkurasi = """
    # // Uji Akurasi
    # var confusionMatrix = ee.ConfusionMatrix(testSet.classify(classifier)
    #     .errorMatrix({
    #       actual: 'Class',
    #       predicted: 'classification'
    #     }));

    # print('Confusion Matrix:', confusionMatrix);
    # print('Overall Accuracy:', confusionMatrix.accuracy());
    # print('Producers Accuracy:', confusionMatrix.producersAccuracy());
    # print('Consumers Accuracy:', confusionMatrix.consumersAccuracy());
    # """
    #         st.code(codeUjiAkurasi, language="javascript", line_numbers=True)

    #         st.markdown(
    #             "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
    #         )

    elif option == "🌋 Elevasi dan Slope":
        st.subheader("**Elevasi dan Slope**")
        st.markdown(
            """
            <div class="justified-text">
           <b>Citra radar NASA SRTM</b> telah tersaji dalam format <b><i>digital elevation model</i> (DEM)</b> sehingga informasi <b>elevasi</b> yang diperlukan <b>dapat langsung diambil</b> tanpa proses konversi tambahan. Sementara itu, data <b><i>slope</i></b> dapat diperoleh dengan memanfaatkan <i>application programming interface</i> (API) Google Earth Engine bernama <b>ee.Terrain.slope()</b> yang akan <b>menghasilkan nilai kemiringan lereng</b> dari data elevasi.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Elevasi dan Slope
        codeDEM = """
// Pemanggilan Citra Radar NASA SRTM
dem = ee.Image("USGS/SRTMGL1_003");

// Ekstraksi Data Elevasi dan Slope
var elevation = dem.clip(loc);
var slope = ee.Terrain.slope(elevation);
"""
        st.code(codeDEM, language="javascript", line_numbers=True)

# ==============================================================================
# VALIDASI DATA
# ==============================================================================
with tab4:
    option = st.pills(
        "**Lihat Validasi:**",
        ["🌳 Indeks", "🏞️ Penutup Lahan", "🌡️ Suhu Permukaan Lahan"],
        default="🌳 Indeks",
    )

    if option == "🌳 Indeks":
        st.subheader("**Indeks**")
        st.markdown(
            """
        <div class="justified-text">
        <b>Data indeks spektral</b>, baik NDBI, NDMI, dan NDVI dari citra <b>Landsat <i>Surface Reflectance</i></b> yang beresolusi spasial <b>30 meter</b> perlu <b>divalidasi</b> untuk memastikan <b>akurasi data</b>. Dalam penelitian ini, dilakukan <b>perbandingan statistik</b> dengan data sekunder dari citra lain yang memiliki resolusi spasial <b>lebih tinggi</b> yakni <b>Sentinel-2 MSI <i>Surface Reflectance</i></b> yang beresolusi spasial <b>10 meter</b>. Tahap validasi data indeks dari citra Landsat 8 tahun 2024 diuraikan sebagai berikut.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Indeks Sentinel-2
        st.badge(
            "**1. Perhitungan NDBI, NDMI, dan NDVI dari Citra Sentinel-2**",
            color="primary",
        )
        st.markdown(
            """
        <div class="justified-text">
        Rumus yang digunakan untuk menghitung nilai NDBI, NDMI, dan NDVI dari citra Sentinel-2 serta contoh implementasi kode dalam Google Earth Engine ditunjukkan berikut ini.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Validasi LST
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="justified-text">
        <b>• NDBI</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. Rumus NDBI
        display_equation_validate(
            r"\frac{SWIR - NIR}{SWIR + NIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDBI = <i>Normalized Difference Built-Up Index</i><br>
        SWIR = <i>band</i> 11<br>
        NIR = <i>band</i> 8
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• NDMI</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus NDMI
        display_equation_validate(
            r"\frac{NIR - SWIR}{NIR + SWIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDMI = <i>Normalized Difference Moisture Index</i><br>
        NIR = <i>band</i> 8<br>
        SWIR-1 = <i>band</i> 11
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• NDVI</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        display_equation_validate(
            r"\frac{NIR - Red}{NIR + Red}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        NDVI = <i>Normalized Difference Vegetation Index</i><br>
        NIR = <i>band</i> 8<br>
        Red = <i>band</i> 4
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Sentinel
        codeSentinel = """
// Perhitungan NDBI, NDMI, dan NDVI Citra Sentinel-2
var ndbiSentinel = sentinel2024.normalizedDifference(['B11', 'B8'])
    .setDefaultProjection({
    crs: 'EPSG:4326',
    scale: 10 // Resolusi spasial
    })
    .rename('ndbiSentinel');
    
var ndmiSentinel = sentinel2024.normalizedDifference(['B8', 'B11'])
    .setDefaultProjection({
    crs: 'EPSG:4326',
    scale: 10 // Resolusi spasial
  })
  .rename('ndmiSentinel');
  
var ndviSentinel = sentinel2024.normalizedDifference(['B8', 'B4'])
    .setDefaultProjection({
    crs: 'EPSG:4326',
    scale: 10 // Resolusi spasial
  })
  .rename('ndviSentinel');
"""
        st.code(codeSentinel, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Resampling Resolusi Sentinel-2 (10m) ke Landsat 8 (30m)
        st.badge(
            "**2. *Resampling* ke 30 Meter**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Resolusi spasial data indeks Sentinel-2 yang semula 10 meter <b>diatur ulang</b> menjadi 30 meter menggunakan teknik <b><i>resampling</i></b> agar <b>sesuai</b> dengan <b>resolusi citra Landsat</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Resampling Sentinel
        codeResamplingSentinel = """
// Resampling ke 30m
var ndbiSentinel30m = ndbiSentinel
  .reduceResolution({
    reducer: ee.Reducer.mean(),
    maxPixels: 1024
  })
  .reproject({
    crs: ndbi2024.projection(), // NDBI 
    scale: 30
  });
"""
        st.code(codeResamplingSentinel, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Sampling
        st.badge(
            "**3. Pembuatan Titik Sampel Acak**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Untuk keperluan <b>uji statistik</b>, terlebih dahulu dibutuhkan <b>sampel</b> dari masing-masing data. Google Earth Engine menyediakan API <b>ee.Image.sample</b> yang memungkinkan <b>pembuatan titik sampel secara acak</b> dan otomatis.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Sampling Sentinel
        codeSamplingSentinel = """
// Stacking NDBI Sentinel dan NDBI Landsat
var stackedNDBI = ndbiSentinel30m.addBands(ndbi2024); // ndbi2024 dari Landsat 8

// Pembuatan Sampel Acak
var samplesVal = stackedNDBI.sample({
  region: loc,
  scale: 30,
  numPixels: 300,
  seed: 42,
  geometries: true
});
"""
        st.code(codeSamplingSentinel, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Uji Korelasi Pearson
        st.badge(
            "**4. Uji Korelasi Pearson**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Validasi indeks dari citra Sentinel-2 dilakukan melalui <b>uji statistik korelasi Pearson</b> dan perhitungan nilai <b>RMSE</b> serta <b>MAE</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Sampling Sentinel
        codeKorelasiPearson = """
// Uji Korelasi Pearson
var correlationNDBI = cleanSamplesVal.reduceColumns({
  selectors: ['ndbiSentinel', 'ndbiLandsat'],
  reducer: ee.Reducer.pearsonsCorrelation()
});

print('Korelasi Pearson NDBI Landsat vs Sentinel:', correlationNDBI);

// Perhitungan RMSE dan MAE
var samplesWithError = cleanSamplesVal.map(function (sample) {
  var sentinel = ee.Number(sample.get('ndbiSentinel'));
  var landsat = ee.Number(sample.get('ndbiLandsat'));
  var error = sentinel.subtract(landsat);
  var absoluteError = error.abs();
  var squaredError = error.pow(2);

  return sample.set({
    error: error,
    abs_error: absoluteError,
    squared_error: squaredError
  });
});

// RMSE
var mse = samplesWithError.reduceColumns({
  selectors: ['squared_error'],
  reducer: ee.Reducer.mean()
});

var rmse = ee.Number(mse.get('mean')).sqrt();
print('RMSE (Root Mean Square Error):', rmse);

// MAE
var mae = samplesWithError.reduceColumns({
  selectors: ['abs_error'],
  reducer: ee.Reducer.mean()
});

print('MAE (Mean Absolute Error):', mae.get('mean'));
"""
        st.code(codeKorelasiPearson, language="javascript", line_numbers=True)

    elif option == "🏞️ Penutup Lahan":
        st.subheader("**Penutup Lahan**")
        st.badge(
            "**1. *Sampling* dan Validasi**",
            color="primary",
        )
        st.markdown(
            """
        <div class="justified-text">
        Validasi penutup lahan dilakukan untuk menguji kesesuaian hasil klasifikasi dengan kondisi aktual. Jumlah total sampel ditentukan menggunakan rumus Fitzpatrick-Lins (1981) dengan asumsi <b>akurasi yang diharapkan 85%</b> dan <b>toleransi kesalahan 10%</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Penentuan Sampel
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        display_equation_validate(r"n = \frac{Z^2 \times p \times q}{E^2}")

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        n = jumlah total sampel<br>
        Z² = standar deviasi normal untuk tingkat kepercayaan 95% (bernilai 2)<br>
        p = akurasi yang diharapkan (%)<br>
        q = 100-p<br>
        E² = tingkat kesalahan yang diizinkan (%)<br>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        Hasil kalkulasi menunjukkan bahwa dibutuhkan sekitar <b>51 titik sampel</b> untuk mencapai skema akurasi tersebut. Selanjutnya, dilakukan distribusi titik sampel untuk tiap kelas penutup lahan (strata) yang diestimasi dengan metode <b><i>Proportional Random Sampling</i></b> berikut ini.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Proportional Random Sampling
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        display_equation_validate(r"n_h = \frac{N_h \times n}{N}")

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        n<sub>h</sub> = jumlah sampel pada strata h<br>
        N<sub>h</sub> = jumlah populasi strata h<br>
        N = jumlah total populasi<br>
        n = jumlah total sampel<br>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        Dari perhitungan tersebut, maka <b>distribusi sampel</b> pada kelas vegetasi adalah sebesar <b>33 titik</b>, tubuh air <b>0 titik</b>, lahan terbangun <b>12 titik</b>, dan lahan terbuka <b>6 titik</b>. Apabila terdapat kelas yang tidak memperoleh sampel (misalnya tubuh air), maka dilakukan <b>realokasi</b> dari strata dengan alokasi terbesar (contohnya vegetasi) tanpa mengubah proporsi secara signifikan. Pada kasus ini, vegetasi menyumbangkan 3 titik ke kelas tubuh air sehingga masing-masing kelas tetap <b>dapat divalidasi akurasinya</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        Ekstraksi titik sampel dilakukan menggunakan Google Earth Engine melalui API <b>ee.Image.stratifiedSample</b>. Setiap titik sampel berisi informasi kelas penutup lahan sekaligus nilai LST tahun 2024 karena citra hasil pengolahan LST tahun terkait turut dimasukkan dalam proses ekstraksi. Titik sampel kemudian diekspor dalam format CSV. Kode untuk ekstraksi dan mengekspor otomatis titik sampel ditunjukkan berikut ini.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Sampling Sentinel
        codeEkstraksiSampel = """
// Pemanggilan LST 2024 dari Assets
var lst2024 = ee.Image("users/pramithadi/regresi/lst2024");

// Distribusi Sampel Hasil Sampling
var alokasiSampel = {
  0: 30, // Vegetasi
  1: 3,  // Tubuh Air  
  2: 12, // Lahan Terbangun
  3: 6   // Lahan Terbuka
}

// Deklarasi Nama Kelas
var classNames = {
  0: 'Vegetasi',
  1: 'Tubuh Air',
  2: 'Lahan Terbangun', 
  3: 'Lahan Terbuka'
}

// Function untuk Ekstraksi Sampel
var generateStratifiedSamples = function(classValue, numSamples) {
  // Masking Kelas
  var classMask = lulc2024.eq(classValue);
  var classRegion = classMask.selfMask();
  
  // Generate Titik Sampel Acak
  var stratifiedRandomPoints = classRegion.stratifiedSample({
    numPoints: numSamples, // diatur per kelas
    classBand: 'classification',
    region: loc,
    scale: 30,
    seed: 42,
    geometries: true
  });
  
  return stratifiedRandomPoints;
};

// Menjalankan Function
var allSamples = ee.FeatureCollection([]);

Object.keys(alokasiSampel).forEach(function(classValue) {
  var numSamples = alokasiSampel[classValue];
  var classSamples = generateStratifiedSamples(parseInt(classValue), numSamples);
  allSamples = allSamples.merge(classSamples);
});

// Ekstraksi Kelas Penutup Lahan dan Nilai LST di Titik yang Sama
var samplesWithData = allSamples.map(function(point) {
  // Kelas Penutup Lahan
  var lulcValue = lulc2024.sample({
    region: point.geometry(),
    scale: 30,
    numPixels: 1
  }).first().get('classification');
  
  // Nilai LST
  var lstValue = lst2024.sample({
    region: point.geometry(), 
    scale: 30,
    numPixels: 1
  }).first().get('lst2024');
  
  // Koordinat
  var koordinat = point.geometry().coordinates();
  
  return point.set({
    'ID': ee.Number(point.get('system:index')),
    'X': koordinat.get(0),
    'Y': koordinat.get(1),
    'Kelas': ee.String(ee.Algorithms.If(
      ee.Number(lulcValue).eq(0), 'Vegetasi',
      ee.Algorithms.If(
        ee.Number(lulcValue).eq(1), 'Tubuh Air',
        ee.Algorithms.If(
          ee.Number(lulcValue).eq(2), 'Lahan Terbangun', 'Lahan Terbuka'
        )
      )
    )),
    'LST_Celcius': lstValue
  })
})

// Menampilkan Titik Sampel
Map.addLayer(samplesWithData, {color: 'red'}, 'Titik Sampel');
print('Total Titik Sampel:', samplesWithData.size());
var sampleCount = samplesWithData.aggregate_histogram('Kelas');
print('Jumlah Sampel per Kelas:', sampleCount);

// Ekspor Titik Sampel ke Google Drive (CSV)
Export.table.toDrive({
   collection: samplesWithData,
   description: 'Titik_Sampel_LULC_LST',
   folder: 'survei_lapangan',
   fileFormat: 'CSV',
   selectors: [
     'ID',
     'X',
     'Y',
     'Kelas',
     'LST_Celcius',
   ]
});
"""
        st.code(codeEkstraksiSampel, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>Validasi lapangan</b> dilakukan dengan memanfaatkan aplikasi <b>Google Maps (My Maps)</b> untuk navigasi, <b>Avenza Maps</b> untuk <i>plotting</i> titik koordinat, <b>GPS Map Camera</b> untuk dokumentasi, dan <b>Google Spreadsheet</b> untuk pencatatan. Tabel <i>checklist</i> yang digunakan berisi informasi sebagai berikut:<br>
        • Nomor dan kode titik<br>
        • Koordinat (X, Y)<br>
        • Tanggal dan waktu observasi<br>
        • Kondisi cuaca<br>
        • Penutup lahan hasil klasifikasi<br>
        • Penutup lahan aktual<br>
        • Nilai LST hasil ekstraksi citra Landsat 8<br>
        • Pengukuran LST (ke-1), (ke-2), (ke-3)<br>
        • LST aktual (rata-rata hasil pengukuran)<br>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        Sementara itu, untuk <b>data penutup lahan tahun 2014 dan 2019</b>, validasi dilakukan dengan metode serupa, tetapi <b>verifikasi</b> dilakukan menggunakan <b>citra dari Google Earth</b> dengan <i>timestamps</i> yang telah disesuaikan dengan tahun terkait.
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.badge(
            "**2. Uji Akurasi**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Akurasi penutup lahan dihitung dengan matriks konfusi yang diadaptasi dari Stuckenberg (2013) dengan format matriks sebagai berikut.
        </div>
        """,
            unsafe_allow_html=True,
        )

        def display_confusion_matrix_template():
            html_content = """
            <style>
            .conf-matrix { width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif; font-size: 13px; border: 2px solid #333; }
            .conf-matrix th { background: #E4EFE7; border: 1px solid #333; padding: 10px 6px; text-align: center; font-weight: bold; color: #333; }
            .conf-matrix td { border: 1px solid #333; padding: 8px 6px; text-align: center; background: white; }
            .conf-matrix .header-main { background: #E4EFE7; font-weight: bold; color: #333; }
            .conf-matrix .row-label { background: #E4EFE7; font-weight: bold; color: #333; }
            .conf-matrix .row-kolom { background: #E4EFE7; font-weight: bold; color: #333; }
            </style>

            <table class="conf-matrix">
            <thead>
                <tr>
                <th rowspan="2" class="header-main">Data Hasil<br/>Klasifikasi</th>
                <th colspan="3" class="header-main">Data Uji Klasifikasi</th>
                <th rowspan="2" class="header-main">Total<br/>Baris</th>
                <th rowspan="2" class="header-main">Producer<br/>Accuracy</th>
                <th rowspan="2" class="header-main">Kesalahan<br/>Omisi</th>
                </tr>
                <tr>
                <th class="header-main">A</th>
                <th class="header-main">B</th>
                <th class="header-main">C</th>
                </tr>
            </thead>
            <tbody>
                <!-- Baris A -->
                <tr>
                <td class="row-label">A</td>
                <td>X<sub>11</sub></td>
                <td>X<sub>12</sub></td>
                <td>X<sub>13</sub></td>
                <td>X<sub>+1</sub></td>
                <td></td>
                <td></td>
                </tr>
                <!-- Baris B -->
                <tr>
                <td class="row-label">B</td>
                <td>X<sub>21</sub></td>
                <td>X<sub>22</sub></td>
                <td>X<sub>23</sub></td>
                <td>X<sub>+2</sub></td>
                <td></td>
                <td></td>
                </tr>
                <!-- Baris C -->
                <tr>
                <td class="row-label">C</td>
                <td>X<sub>31</sub></td>
                <td>X<sub>32</sub></td>
                <td>X<sub>33</sub></td>
                <td>X<sub>+3</sub></td>
                <td></td>
                <td></td>
                </tr>
                <!-- Total kolom -->
                <tr>
                <td class="row-label">Total Kolom</td>
                <td>X<sub>1+</sub></td>
                <td>X<sub>2+</sub></td>
                <td>X<sub>3+</sub></td>
                <td>N</td>
                <td></td>
                <td></td>
                </tr>
                <!-- User accuracy (kolom A–C), Xii diletakkan di kolom Producer accuracy -->
                <tr>
                <td class="row-kolom">User Accuracy</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>X<sub>ii</sub></td>
                <td></td>
                </tr>
                <!-- Kesalahan komisi -->
                <tr>
                <td class="row-kolom">Kesalahan Komisi</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                </tr>
                <!-- Overall accuracy (merge semua kolom sisanya) -->
                <tr>
                <td class="row-kolom">Overall Accuracy</td>
                <td colspan="6"></td>
                </tr>
                <!-- Kappa accuracy (merge semua kolom sisanya) -->
                <tr>
                <td class="row-kolom">Kappa Accuracy</td>
                <td colspan="6"></td>
                </tr>
            </tbody>
            </table>
            """
            st.markdown(html_content, unsafe_allow_html=True)

        display_confusion_matrix_template()

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        Matriks konfusi menyajikan hasil perhitungan berupa <b><i>user accuracy</i>, <i>producer accuracy</i>, kesalahan omisi, kesalahan komisi, <i>overall accuracy</i>,</b> dan <b><i>kappa accuracy</i></b>. Hasil perhitungan matriks tersebut menentukan apakah hasil klasifikasi penutup lahan <b>dapat diterima atau tidak</b> (Darmawan, 2023). Berikut ini adalah formula untuk menghitung masing-masing metrik akurasi tersebut.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Matriks Konfusi
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Producer Accuracy</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. Producer Accuracy
        display_equation_validate(r"\frac{X_{11}}{X_{+1}} \times 100\%")

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>User Accuracy</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 2. User Accuracy
        display_equation_validate(
            r"\frac{X_{11}}{X_{1+}} \times 100\%",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• Kesalahan Omisi</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 3. Kesalahan Omisi
        display_equation_validate(
            r"100\% - \text{Producer Accuracy}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• Kesalahan Komisi</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 4. Kesalahan Komisi
        display_equation_validate(
            r"100\% - \text{User Accuracy}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Overall Accuracy</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 5. Overall Accuracy
        display_equation_validate(
            r"\left( \frac{\sum_{i=1}^{r} X_{ii}}{N} \right) \times 100\%",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Kappa Accuracy</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 6. Kappa Accuracy
        display_equation_validate(
            r"\left[ \frac{N \sum_{i=1}^{r} X_{ii} - \sum_{i=1}^{r} X_{i1+} X_{+1}}{N^{2} - \sum_{i=1}^{r} X_{i1+} X_{+1}} \right] \times 100\%",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        N = total sampel<br>
        X<sub>+i</sub> = jumlah sampel dalam baris ke-i<br>
        X<sub>i+</sub> = jumlah sampel dalam kolom ke-i<br>
        X<sub>ii</sub> = nilai diagonal dari baris ke-i kolom ke-i<br>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                    - Darmawan, R. (2023). *Analisis Tren Perubahan Tutupan Lahan di Kota Pontianak Tahun 2019 Sampai Tahun 2022 dan Kesesuaian terhadap Rencana Detail Tata Ruang (RDTR) Kota Pontianak*. Skripsi, Fakultas Teknik. Yogyakarta: Universitas Gadjah Mada.
                    - Fitzpatrick-Lins, K. (1981). Comparison of Sampling Procedures and Data Analysis for a Land-Use and Land-Cover Map. *Photogrammetric Engineering and Remote Sensing*, 47(3), 343-351. 
                    - Stuckenberg, T., Munch, Z., Van Niekerk, A. (2013). Multi-temporal Remote Sensing Land-cover Change Detection for Biodiversity Assessment in the Berg River Catchment. *South African Journal of Geomatics*, 2(3). 189-205.
                    """
            )

    elif option == "🌡️ Suhu Permukaan Lahan":
        st.subheader("**Suhu Permukaan Lahan**")
        st.markdown(
            """
        <div class="justified-text">
        <b>Validasi suhu permukaan lahan (LST)</b> dilakukan pada titik sampel yang sama dengan validasi penutup lahan sehingga kegiatan lapangan lebih efisien. Nilai LST lapangan diukur menggunakan <b>termometer inframerah</b> seri Fluke 561 dengan tiga kali pengulangan per titik untuk memperoleh rata-rata yang lebih stabil. Pengukuran LST lapangan dilaksanakan antara pukul 09.00-11.00 WIB mulai bulan Juni hingga Agustus dalam kondisi cuaca cerah untuk menyesuaikan dengan waktu perekaman citra satelit Landsat 8 (Atianta, 2020). <b>Uji akurasi</b> antara LST hasil ekstraksi citra Landsat 8 dengan data pengukuran lapangan dilakukan menggunakan metrik <b>RMSE</b> dan <b>MAE</b> untuk mengukur tingkat kesalahan, serta <b>koefisien determinasi (R²)</b> untuk menilai kesesuaian hubungan antar data. 
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus Validasi LST
        def display_equation_validate(equation):
            st.markdown(f"$${equation}$$", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Root Mean Square Error (RMSE)</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. RMSE
        display_equation_validate(
            r"\sqrt{\frac{1}{n} \sum_{i=1}^{n} (Y_{i} - \hat{Y}_{i})^{2}}"
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• <i>Mean Absolute Error (MAE)</i></b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 2. MAE
        display_equation_validate(
            r"\frac{1}{n} \sum_{i=1}^{n} |Y_{i} - \hat{Y}_{i}|",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>• Koefisien Determinasi (R²)</b>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 3. Koefisien Determinasi
        display_equation_validate(
            r"1 - \frac{\sum_{i=1}^{n}(Y_{i} - \hat{Y}_{i})^{2}}{\sum_{i=1}^{n}(Y_{i} - \bar{Y})^{2}}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>dengan:</b><br>
        Y<sub>i</sub> = nilai LST hasil pengukuran lapangan<br>
        Ŷ<sub>i</sub> = nilai LST hasil pengolahan citra Landsat 8<br>
        Ȳ = rata-rata nilai LST dari pengukuran lapangan<br>
        n = jumlah sampel
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="justified-text">
            Visualisasi hasil uji akurasi  ditampilkan dalam bentuk <i>scatterplot</i> yang memperlihatkan distribusi nilai aktual terhadap hasil ekstraksi LST lengkap dengan garis regresi dan nilai koefisien determinasi.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                    - Atianta, L. (2020). Suhu Permukaan Lahan dan Intensitas Pemanfaatan Ruang di Perkotaan Yogyakarta. *Jurnal Pengembangan Kota*, 8(2). 151-162. https://doi.org/10.14710/jpk.8.2.151-162 
                    """
            )

with tab5:
    option = st.pills(
        "**Lihat Prediksi:**",
        [
            "🏞️ Penutup Lahan",
            "🌳 Indeks",
            "🌡️ Suhu Permukaan Lahan",
        ],
        default="🏞️ Penutup Lahan",
    )

    if option == "🏞️ Penutup Lahan":
        st.subheader("**Penutup Lahan**")

        # Transisi Penutup Lahan
        st.badge(
            "**1. Perhitungan Transisi Penutup Lahan**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Pada tahap ini, dilakukan perhitungan <b>perubahan penutup lahan historis</b> dari tahun 1999-2004, 2004-2009, 2009-2014, 2014-2019, dan 2019-2024 menggunakan metode <b>Markov Chain</b>. Dengan menganalisis transisi antar periode, model menghasilkan <b>laju perubahan rata-rata per tahun</b>. Laju inilah yang menjadi dasar untuk memproyeksikan <b>jumlah total area yang akan berubah di masa depan</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Matriks Transisi
        codeMatriksTransisi = """
transition_quantities = []
for i in range(len(YEARS) - 1):
    t1, t2 = YEARS[i], YEARS[i+1]
    cm = get_transition_matrix(os.path.join(PL_DIR, f'pl{t1}kpy.tif'), os.path.join(PL_DIR, f'pl{t2}kpy.tif'))
    print(f"   -> Matriks Transisi (Jumlah Piksel) Periode {t1}-{t2}")
    df_cm = pd.DataFrame(cm, index=CLASS_PROPERTY.values(), columns=CLASS_PROPERTY.values())
    display(df_cm)
    interval_quantity = cm[TARGET_TRANSITION['from'], TARGET_TRANSITION['to']]
    transition_quantities.append(interval_quantity)
    print(f"   -> Perubahan {t1}-{t2}: {interval_quantity} Piksel")

avg_annual_rate = sum(transition_quantities) / (YEARS[-1] - YEARS[0])
"""
        st.code(codeMatriksTransisi, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Penentuan Lokasi Perubahan
        st.badge(
            "**2. Penentuan Lokasi Perubahan**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Berikutnya, <b>model XGBoost</b> akan dilatih untuk menentukan <b>area mana</b> yang <b>paling berpotensi</b> mengalami perubahan. Pertimbangan penentuan lokasi perubahan ini didasarkan pada tiga faktor yaitu kondisi fisik (<b>elevasi</b> dan <b><i>slope</i></b>) serta <b>pengaruh tetangga</b> di sekitarnya yang merupakan implementasi dari <b>Cellular Automata</b>. Dengan mempertimbangkan faktor-faktor tersebut, model akan belajar dan menghasilkan output berupa <b>peta kesesuaian <i>(suitability map)</i></b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Lokasi Perubahan
        codeLokasiPerubahan = """
# Menyiapkan Data Latih untuk Belajar
df_train = pd.DataFrame({
    'elevasi': map_elevasi[candidate_mask],
    'slope': map_slope[candidate_mask],
    'tetangga': feature_neighbor[candidate_mask], # Cellular Automata
    'target': target_change[candidate_mask]
})

X = df_train.drop('target', axis=1) # Fitur
y = df_train['target'] # Target
pos_weight_ratio = np.sum(y == 0) / np.sum(y == 1) if np.sum(y == 1) > 0 else 1

# Melatih Model XGBoost
suitability_model = xgb.XGBClassifier(objective='binary:logistic', scale_pos_weight=pos_weight_ratio, eval_metric='logloss', random_state=42)
suitability_model.fit(X, y)
"""
        st.code(codeLokasiPerubahan, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Alokasi Perubahan dan Generate Peta
        st.badge(
            "**3. Alokasi Perubahan dan Generate Peta**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Terakhir, model akan menggabungkan hasil dari dua tahap sebelumnya. <b>Jumlah total area yang akan berubah</b> (dari tahap 1) <b>dialokasikan</b> ke lokasi-lokasi dengan <b>skor kesesuaian tertinggi</b> (dari tahap 2). Area yang paling berpotensi akan diprioritaskan terlebih dahulu untuk berubah hingga target jumlah perubahan yang telah ditentukan terpenuhi. Hasil akhir dari proses ini adalah <b>peta prediksi penutup lahan tahun 2029</b> yang menunjukkan di mana perubahan lahan di masa depan.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Alokasi
        codeAlokasi = """
# Jumlah Piksel yang Akan Berubah
projection_interval = PREDICTION_YEAR - VALIDATION_YEAR
projection_quantity_normal = int(avg_annual_rate * projection_interval)
projection_quantity_scenario = int(projection_quantity_normal * ACCELERATION_FACTOR)

with rasterio.open(os.path.join(PL_DIR, f'pl{VALIDATION_YEAR}kpy.tif')) as src:
    base_map_prediction = src.read(1)
neighbor_feature_prediction = create_neighborhood_feature(base_map_prediction, TARGET_TRANSITION['to'])

df_predict_2029 = pd.DataFrame({
    'elevasi': map_elevasi[valid_mask],
    'slope': map_slope[valid_mask],
    'tetangga': neighbor_feature_prediction[valid_mask]
})

# Alokasi Perubahan ke Lokasi dengan Kesesuaian Tertinggi
map_prediksi_2029 = allocate_changes(
    base_map_prediction,
    suitability_map_prediction,
    projection_quantity_scenario,
    TARGET_TRANSITION
)
"""
        st.code(codeAlokasi, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

    elif option == "🌳 Indeks":
        st.subheader("**Indeks**")

        # Persiapan Data Training
        st.badge(
            "**1. Persiapan Data Training**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Nilai sebuah indeks di masa depan dapat diprediksi dengan melihat tren nilainya di masa lalu dan kondisi penutup lahan pada masa tersebut. Dari hipotesis tersebut, maka disusunlah <b>'bahan ajar'</b> yang berisi kumpulan <b>'soal-soal'</b> yang dalam <i>machine learning</i> disebut sebagai <b><i>feature</i> (X)</b> dan <b>'kunci jawabannya'</b> yang disebut <b>target (y)</b>. <b><i>Feature</i></b> yang digunakan untuk <b>melatih model XGBoost</b> dalam proyeksi indeks tahun 2024 adalah nilai <b>indeks</b> tahun <b>2019</b>, <b>penutup lahan</b> tahun <b>2024</b>, <b>elevasi</b>, dan <b><i>slope</i></b>. Sementara itu, <b>targetnya</b> adalah nilai <b>indeks</b> aktual tahun <b>2024</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Data Training
        codeDataTraining = """
training_feature_paths = {
    'ndbi_2019': os.path.join(BASE_DIR, 'NDBI', 'ndbi2019kpy.tif'),
    'ndmi_2019': os.path.join(BASE_DIR, 'NDMI', 'ndmi2019kpy.tif'),
    'ndvi_2019': os.path.join(BASE_DIR, 'NDVI', 'ndvi2019kpy.tif'),
    'pl_2024': os.path.join(PL_DIR, f'pl{VALIDATION_YEAR}kpy.tif'),
    'elevasi': os.path.join(DEM_DIR, 'elevasi.tif'),
    'slope': os.path.join(DEM_DIR, 'slope.tif'),
    'target': os.path.join(INDEX_DIR, f'{index}{VALIDATION_YEAR}kpy.tif'),
}

df_training, raster_meta = raster_to_df(training_feature_paths, sample_size=SAMPLING_SIZE)
"""
        st.code(codeDataTraining, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Train Test Split
        st.badge(
            "**2. *Train Test Split***",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Bahan ajar yang telah disusun kemudian <b>dibagi</b> menjadi dua bagian, yaitu <b>80%</b> sebagai <b>data <i>training</i> (X_train, y_train)</b> untuk <b>melatih model</b> dan <b>20%</b> sebagai <b>data <i>testing</i> (X_test, y_test)</b> untuk <b>menguji performa model</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Train Test Split
        codeTrainTestSplit = """
# Memisahkan Data Training dan Testing
X = df_training.drop('target', axis=1)
y = df_training['target']

# Membagi Data (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
"""
        st.code(codeTrainTestSplit, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Training dan Evaluasi Model
        st.badge(
            "**3. *Training* dan Evaluasi Model**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>Model XGBoost</b> kemudian <b>dilatih</b> untuk <b>belajar</b> dan menganalisis pola-pola dari puluhan ribu sampel piksel yang terdapat dalam <b>bahan ajar (X_train, y_train)</b>. Tujuannya untuk memproyeksikan nilai indeks pada tahun 2024. Setelah proses <i>training</i> selesai, model XGBoost lantas <b>diuji</b> dengan <b>data <i>testing</i> (X_test)</b>. Hasil ujian tersebut lalu <b>dievaluasi</b> dengan <b>kunci jawabannya (y_test)</b> menggunakan metrik <b>RMSE</b>, <b>MAE</b>, dan <b>R²</b> untuk menilai seberapa akurat model XGBoost ini bekerja.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Training dan Evaluasi Model
        codeTrainingEvaluasi = """
# Membuat dan Melatih Model XGBoost 
model = xgb.XGBRegressor(
    objective='reg:squarederror', n_estimators=1000, learning_rate=0.05,
    max_depth=7, subsample=0.8, n_jobs=-1, random_state=42,
    early_stopping_rounds=50
)

model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# Menguji Model dengan Data Testing
y_pred_test = model.predict(X_test)

# Evaluasi Model
metrics = {
    'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_test)),
    'MAE': mean_absolute_error(y_test, y_pred_test),
    'R-Squared': r2_score(y_test, y_pred_test)
}
"""
        st.code(codeTrainingEvaluasi, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Prediksi Indeks Tahun 2029
        st.badge(
            "**4. Prediksi Indeks Tahun 2029**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Setelah <b>terbukti andal</b>, model XGBoost lantas digunakan untuk tujuan utamanya yaitu <b>memproyeksikan</b> nilai <b>indeks</b> pada tahun <b>2029</b>. Pada tahap ini, model diberikan satu <b><i>set</i> data <i>input</i> baru</b> yang terdiri atas nilai <b>indeks</b> tahun <b>2024</b>, <b>penutup lahan</b> tahun <b>2029</b>, <b>elevasi</b>, dan <b><i>slope</i></b>. Model yang sudah terlatih ini kemudian menerapkan pengetahuannya pada data <i>input</i> baru tersebut untuk memproyeksi nilai indeks pada tahun 2029 untuk setiap piksel. Hasilnya adalah peta proyeksi masing-masing indeks (NDBI, NDMI, dan NDVI) tahun 2029.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Prediksi Indeks 2029
        codePrediksiIndeks = """
# Menyiapkan Set Data Input
prediction_feature_paths = {
    'ndbi_2024': os.path.join(BASE_DIR, 'NDBI', 'ndbi2024kpy.tif'),
    'ndmi_2024': os.path.join(BASE_DIR, 'NDMI', 'ndmi2024kpy.tif'),
    'ndvi_2024': os.path.join(BASE_DIR, 'NDVI', 'ndvi2024kpy.tif'),
    'pl_2029': os.path.join(OUTPUT_DIR, f'prediksi_pl_{PREDICTION_YEAR}.tif'),
    'elevasi': os.path.join(DEM_DIR, 'elevasi.tif'),
    'slope': os.path.join(DEM_DIR, 'slope.tif'),
}

# Mengaplikasikan Model XGBoost yang Sudah Terlatih
predicted_2029_values = model.predict(df_prediction[X.columns])

# Menyimpan Hasil Proyeksi Indeks 2029
path_proyeksi_2029 = os.path.join(OUTPUT_DIR, f'proyeksi_{index}_{PREDICTION_YEAR}.tif')
save_geotiff(path_proyeksi_2029, predicted_2029_values, prediction_mask, raster_meta)
"""
        st.code(codePrediksiIndeks, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

    elif option == "🌡️ Suhu Permukaan Lahan":
        st.subheader("**Suhu Permukaan Lahan**")

        # Persiapan Data Training
        st.badge(
            "**1. Persiapan Data *Training***",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Tahap pertama dari proses pemodelan prediksi LST adalah menyusun <b>'bahan ajar'</b> yang berisi kumpulan <b>'soal-soal' (<i>feature</i>, X)</b> dan <b>'kunci jawabannya' (target, y)</b>. Dalam prediksi LST 2024, <b><i>feature</i></b> yang digunakan untuk melatih <b>model XGBoost</b> dirinci sebagai berikut:<br>
        • LST 2019, NDBI 2019, NDMI 2019, NDVI 2019, penutup lahan 2019,<br>
        • NDBI 2024, NDMI 2024, NDVI 2024, penutup lahan 2024,<br>
        • elevasi, <i>slope</i>, dan koordinat (X, Y)<br>
        <br>
        sedangkan <b>targetnya</b> adalah nilai LST aktual tahun 2024.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Data Training
        codeDataTrainingLST = """
df_full, meta = build_dataset(years=[2019], target_year=2024)

target_column = f'LST {VALIDATION_YEAR}'
features = df_full.drop(target_column, axis=1)
target = df_full[target_column]
"""
        st.code(codeDataTrainingLST, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Train Test Split
        st.badge(
            "**2. *Train Test Split***",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Bahan ajar yang telah disusun selanjutnya <b>dibagi</b> menjadi dua bagian, yaitu <b>80%</b> sebagai <b>data <i>training</i> (X_train, y_train)</b> untuk <b>melatih model</b> dan <b>20%</b> sebagai <b>data <i>testing</i> (X_test, y_test)</b> untuk <b>menguji akurasi model</b>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Training dan Evaluasi Model
        codeTrainTestSplitLST = """
# Membagi Data (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
"""
        st.code(codeTrainTestSplitLST, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Training dan Evaluasi Model
        st.badge(
            "**3. *Training* dan Evaluasi Model**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        <b>Model XGBoost</b> kemudian <b>dilatih</b> untuk menganalisis pola-pola yang terdapat dalam <b>bahan ajar (X_train, y_train)</b>. Setelah proses <i>training</i> selesai, model XGBoost lalu <b>diuji</b> dengan <b>data <i>testing</i> (X_test)</b> untuk memprediksi nilai LST pada tahun 2024. Hasil ujian tersebut lalu <b>dievaluasi</b> dengan <b>kunci jawabannya (y_test)</b> menggunakan metrik <b>RMSE</b>, <b>MAE</b>, dan <b>R²</b> untuk menilai seberapa akurat model XGBoost ini bekerja.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Training dan Evaluasi Model
        codeTrainingEvaluasiLST = """
# Membuat dan Melatih Model XGBoost
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=1000, learning_rate=0.05,
                        max_depth=7, subsample=0.8, n_jobs=-1, random_state=42,
                        early_stopping_rounds=50)
                         
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# Menguji Model dengan Data Testing
predictions_test = model.predict(X_test)

# Evaluasi Model
validation_metrics = {
    'RMSE': np.sqrt(mean_squared_error(y_test, predictions_test)),
    'MAE': mean_absolute_error(y_test, predictions_test),
    'R-Squared': r2_score(y_test, predictions_test)
}
"""
        st.code(codeTrainingEvaluasiLST, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Prediksi LST Tahun 2029
        st.badge(
            "**4. Prediksi LST Tahun 2029**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Setelah <b>terbukti andal</b>, model XGBoost lantas dapat digunakan untuk tujuan utamanya yakni <b>memprediksi</b> nilai <b>LST</b> pada tahun <b>2029</b>. Pada tahap ini, model diberikan satu <b><i>set</i> data <i>input</i> baru</b> yang dirinci sebagai berikut:<br>
        • LST 2024, NDBI 2024, NDMI 2024, NDVI 2024, penutup lahan 2024,<br>
        • NDBI 2029, NDMI 2029, NDVI 2029, penutup lahan 2029,<br>
        • elevasi, <i>slope</i>, dan koordinat (X, Y)<br>
        <br>
        Model yang sudah terlatih ini kemudian menerapkan pengetahuannya pada data <i>input</i> baru tersebut untuk memprediksi nilai LST pada tahun 2029 untuk setiap piksel. Hasilnya adalah peta prediksi LST tahun 2029.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Prediksi LST 2029
        codePrediksiLST = """
# Menyiapkan Set Data Input
df_prediction, meta_prediction = build_dataset(years=[2024], target_year=2029, is_prediction=True)

# Mengaplikasikan Model XGBoost yang Sudah Terlatih
predicted_values_2029 = model.predict(df_for_model)

# Menyimpan Hasil Prediksi LST 2029
output_path = os.path.join(OUTPUT_DIR, f'prediksi_lst_{PREDICTION_YEAR}.tif')
"""
        st.code(codePrediksiLST, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Analisis SHAP
        st.badge(
            "**5. Analisis Kontribusi Fitur dengan SHAP**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Untuk menganalisis <b>tingkat kontribusi</b> masing-masing <b>fitur</b> dalam <b>prediksi LST</b> ini digunakanlah metode <b>SHAP (SHapley Additive exPlanations)</b>. SHAP adalah <i>library</i> yang akan <b>'membongkar'</b> bagaimana setiap fitur memengaruhi hasil prediksi model XGBoost. Dengan ini, faktor-faktor kunci yang paling berpengaruh terhadap perubahan LST di masa depan dapat teridentifikasi.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Analisis SHAP
        codeAnalisisSHAP = """
# Menyiapkan SHAP Explainer
explainer = shap.TreeExplainer(model)

# Menghitung Nilai SHAP untuk Sampel Data
shap_values = explainer(shap_sample)

# Membuat Plot SHAP
shap.summary_plot(shap_values, shap_sample, plot_type="dot")
"""
        st.code(codeAnalisisSHAP, language="python", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )
