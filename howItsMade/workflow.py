import streamlit as st
from streamlit_image_comparison import image_comparison

st.set_page_config(
    page_title="Workflow — Spatify",
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

# st.header("Workflow")
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
    with st.container(border=False):
        st.image(
            "./assets/diagram_alir2.svg",
        )

# ==============================================================================
# PRAPENGOLAHAN DATA
# ==============================================================================
with tab2:
    # Penyaringan Citra
    st.badge("**Penyaringan Citra**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        Tahap ini bertujuan untuk <strong>menyortir citra</strong> dalam Google Earth Engine sesuai dengan batasan penelitian yang telah ditetapkan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    codePenyaringanCitra = """
var landsat2024 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate('2024-04-21', '2024-10-31') // Mengacu pada kajian Periode Normal Rata-rata Klimatologi 1991-2020 dari Badan Meteorologi Klimatologi dan Geofisika
    .filterBounds(loc)
    .map(applyScaleFactors8) // Function Scaling Factor
    .map(maskLsr) // Function Cloud Masking
    .median() // Median Composite
    .clip(loc);
"""
    st.code(codePenyaringanCitra, language="javascript", line_numbers=True)

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # Scaling Factor
    st.badge("**Scaling Factor**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Scale factor</strong> digunakan untuk mengembalikan nilai radiansi dan reflektansi citra Landsat Surface Reflectance yang sebelumnya berformat <strong>integer</strong> menjadi <strong>float</strong> agar data memiliki ketelitian sampai level desimal (USGS, 2023).
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
    st.badge("**Cloud Masking**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Cloud masking</strong> metode <strong>Quality Assesment (QA)</strong> merupakan teknik untuk mengurangi tutupan awan dalam citra (Sinabutar <em>et al.</em>, 2020).
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

    # # Hasil Prapengolahan Data
    # st.write(
    #     "Berikut merupakan contoh tampilan citra Landsat 8 Surface Reflectance tahun 2024 **sebelum** dan **sesudah** dilakukan cloud masking:"
    # )

    # image_comparison(
    #     img1="./assets/before.png",
    #     img2="./assets/after.png",
    #     label1="Sebelum",
    #     label2="Sesudah",
    #     width=700,
    #     starting_position=50,
    #     show_labels=True,
    #     make_responsive=True,
    # )
    # st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

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
            Ekstraksi <strong>suhu permukaan lahan</strong> atau <strong>land surface temperature (LST)</strong> dalam penelitian ini menggunakan metode <strong>Single-Channel</strong> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2010). Metode ini terdiri atas empat tahap perhitungan, yaitu:
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Nilai Radiansi Spektral
        st.badge("**1. Perhitungan Radiansi Spektral**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        <strong>Nilai radiansi spektral</strong> pada dataset Landsat Surface Reflectance <strong>telah dikalibrasi</strong> secara otomatis melalui penerapan function <strong>Scaling Factor</strong>. Dengan demikian, nilai radiansi spektral dari saluran termal dataset ini dapat langsung digunakan dalam perhitungan LST.
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
        <strong>Emisivitas permukaan (ε)</strong> merupakan kapabilitas suatu objek dalam <strong>menyerap radiasi</strong> dari matahari dan <strong>memantulkan</strong> energi panas (radiasi <strong>termal</strong>) (Mallick <em>et al.</em>, 2012). Nilai emisivitas permukaan dalam penelitian ini dihitung menggunakan pendekatan <strong>NDVI</strong> dan <strong>Proportion of Vegetation (Pv)</strong>.
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
        <strong>• NDVI</strong>
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
        <strong>dengan:</strong><br>
        NDVI = Normalized Difference Vegetation Index<br>
        NIR = band 4 (Landsat 5 dan Landsat 7), band 5 (Landsat 8)<br>
        Red = band 3 (Landsat 5 dan Landsat 7), band 4 (Landsat 8)
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
        <strong>• Proportion of Vegetation</strong>
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
        <strong>dengan:</strong><br>
        Pv = Proportion of Vegetation<br>
        NDVI = nilai NDVI<br>
        NDVI<sub>min</sub> = nilai minimum NDVI <br>
        NDV<sub>max</sub> = nilai maksimum NDVI
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Kode Pv
        codePv = """
// Perhitungan Proportion of Vegetation (Pv)
var ndvi2024min = ee.Number(ndvi2024.reduceRegion({
  reducer: ee.Reducer.min(),
  geometry: loc,
  scale: 30,
  maxPixels: 1e9
}).values().get(0));

var ndvi2024max = ee.Number(ndvi2024.reduceRegion({
  reducer: ee.Reducer.max(),
  geometry: loc,
  scale: 30,
  maxPixels: 1e9
}).values().get(0));

var pv2024 = (ndvi2024.subtract(ndvi2024min).divide(ndvi2024max.subtract(ndvi2024min))).pow(ee.Number(2)).rename('pv2024');
"""
        st.code(codePv, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>• Emisivitas Permukaan</strong>
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
        <strong>dengan:</strong><br>
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
var emisi2024 = pv2024.multiply(k1).add(k2).rename('emisi2024');
"""
        st.code(codeEmisivitasPermukaan, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Perhitungan Brightness Temperature
        st.badge("**3. Perhitungan Brightness Temperature**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        <strong>Brightness temperature</strong> merupakan <strong>nilai suhu permukaan</strong> dari radiasi termal objek yang direkam oleh sensor termal dan disajikan ke dalam satuan <strong>kelvin</strong> (Jatayu & Susetyo, 2017). Penerapan function Scaling Factor telah <strong>mengkalibrasi</strong> saluran termal ke dalam satuan kelvin sehingga <strong>dapat langsung dimanfaatkan sebagai nilai brightness temperature</strong> (Waleed & Sajjad, 2022). Saluran termal citra Landsat 5 dan Landsat 7 adalah band 6, sedangkan dalam citra Landsat 8 adalah band 10.
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
        Nilai emisivitas permukaan dan brightness temperature yang telah didapatkan lantas <strong>dikalkulasi</strong> dengan <strong>panjang gelombang saluran termal</strong> dan nilai <strong>radiasi emisivitas</strong> yang diestimasi dari konstanta Planck, Stefan-Boltzmann, dan nilai kecepatan cahaya (Waleed & Sajjad, 2022). Untuk mendapatkan <strong>nilai LST</strong> dalam <strong>derajat celcius</strong> tidak luput untuk mengonversi hasilnya dengan 273.15.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # st.markdown(
        #     """
        # <div class="justified-text">
        # <strong>• Land Surface Temperature</strong>
        # </div>
        # """,
        #     unsafe_allow_html=True,
        # )

        # 3. Rumus LST
        display_equation_validate(
            r"LST = \left( \frac{B_T}{1 + \left( \frac{\lambda \cdot B_T}{\rho} \right) \cdot \ln \epsilon} \right) - 273.15",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>dengan:</strong><br>
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
            Perhitungan <strong>indeks kerapatan area terbangun</strong> (NDBI) dilakukan dengan mengekstraksi nilai dari <strong>saluran reflektif inframerah-dekat (NIR)</strong> dan <strong>inframerah-gelombang pendek (SWIR)</strong> yang sangat sensitif terhadap area terbangun (Wicaksono <em>et al.</em>, 2021).
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
        <strong>dengan:</strong><br>
        NDBI = Normalized Difference Built-Up Index<br>
        SWIR = band 5 (Landsat 5 dan Landsat 7), band 6 (Landsat 8)<br>
        NIR = band 4 (Landsat 5 dan Landsat 7), band 5 (Landsat 8)
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
            <strong>Indeks kelembapan vegetasi</strong> (NDMI) dihitung dengan memanfaatkan <strong>saluran reflektif inframerah-gelombang pendek (SWIR)</strong> dan <strong>inframerah-dekat (NIR)</strong> serupa NDBI. Namun, terdapat perbedaan urutan saluran reflektif yang digunakan dalam formula sebagaimana dirumuskan oleh Gao (1996). Perhitungan NDMI menempatkan saluran NIR sebagai pengurang, berbeda dengan NDBI yang menggunakan SWIR di posisi tersebut.
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
        <strong>dengan:</strong><br>
        NDMI = Normalized Difference Moisture Index<br>
        NIR = band 4 (Landsat 5 dan Landsat 7), Band 5 (Landsat 8)<br>
        SWIR = band 5 (Landsat 5 dan Landsat 7), Band 6 (Landsat 8)
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
            Perhitungan <strong>indeks kerapatan vegetasi</strong> (NDVI) dilakukan dengan mengekstraksi nilai dari reflektansi <strong>saluran inframerah-dekat (NIR)</strong> dan <strong>saluran merah (red)</strong> (Estoque <em>et al.</em>, 2017).
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
        <strong>dengan:</strong><br>
        NDVI = Normalized Difference Vegetation Index<br>
        NIR = band 4 (Landsat 5 dan Landsat 7), band 5 (Landsat 8)<br>
        Red = band 3 (Landsat 5 dan Landsat 7), band 4 (Landsat 8)
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
            Penutup lahan dipetakan menggunakan <strong>klasifikasi supervised</strong> pada citra multispektral. Metode ini <strong>memanfaatkan sampel</strong> dari tiap kelas penutup lahan untuk <strong>melatih model klasifikasi</strong>. Prosedur klasifikasi supervised penutup lahan di Google Earth Engine ditunjukkan berikut ini.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Pembuatan Training Area
        st.badge("**1. Pembuatan Training Area**", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        <strong>Training area</strong> adalah kumpulan sampel dari setiap kelas penutup lahan yang akan diklasifikasi. Klasifikasi penutup lahan mengacu pada sistem <strong>SNI 7645:2010</strong> yang telah disesuaikan dengan kondisi penutup lahan di lokasi penelitian. Kelas yang digunakan dalam penelitian ini meliputi <strong>vegetasi, tubuh air, lahan terbangun, dan lahan terbuka</strong>.
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

        # Sebaran Training Area
        st.write(
            "Di bawah ini adalah visualisasi sebaran training area pada citra Landsat 8 Surface Reflectance tahun 2024."
        )
        st.image(
            "./assets/training_area2.png",
            caption="Persebaran Sampel Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya Tahun 2024",
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Klasifikasi Supervised
        st.badge("**2. Klasifikasi Supervised**", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        Training area dianalisis menggunakan algoritma <strong>Classification and Regression Tree (CART)</strong>, yaitu metode <strong>machine learning</strong> berbasis <strong>decision tree (pohon keputusan)</strong> yang banyak digunakan dalam klasifikasi penutup lahan (Krzywinski & Altman, 2017). Algoritma ini membentuk <strong>aturan klasifikasi</strong> dari sampel training area yang tersedia kemudian <strong>diaplikasikan</strong> untuk <strong>mengidentifikasi kelas penutup lahan</strong> pada setiap piksel citra.
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

        # Hasil Klasifikasi Penutup Lahan
        st.write(
            "Visualisasi dari hasil klasifikasi penutup lahan di lokasi penelitian tahun 2024 ditunjukkan pada gambar berikut."
        )
        st.image(
            "./assets/hasil_klasifikasi2.png",
            caption="Visualisasi Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya Tahun 2024",
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Uji Akurasi Klasifikasi
        st.badge("**3. Uji Akurasi Klasifikasi**", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        <strong>Uji akurasi</strong> ini <strong>membandingkan hasil klasifikasi</strong> model CART dengan <strong>data training</strong> dan <strong>testing</strong> yang dibagi dengan skema split <strong>80% untuk training</strong> dan <strong>20% untuk testing</strong>. Hasil <strong>matriks konfusi</strong> menunjukkan <strong>akurasi keseluruhan</strong> mencapai <strong>91.43%</strong>. Berikut contoh implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )

        codeUjiAkurasi = """
// Uji Akurasi 
var confusionMatrix = ee.ConfusionMatrix(testSet.classify(classifier)
    .errorMatrix({
      actual: 'Class',
      predicted: 'classification'
    }));

print('Confusion Matrix:', confusionMatrix);
print('Overall Accuracy:', confusionMatrix.accuracy());
print('Producers Accuracy:', confusionMatrix.producersAccuracy());
print('Consumers Accuracy:', confusionMatrix.consumersAccuracy());
"""
        st.code(codeUjiAkurasi, language="javascript", line_numbers=True)

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Krzywinski, M., & Altman, N. (2017). Classification and Regression Trees. *Nature Methods*, 14(8). 757-758. https://doi.org/10.1038/nmeth.4370 
                """
            )

    elif option == "🌋 Elevasi dan Slope":
        st.subheader("**Elevasi dan Slope**")
        st.markdown(
            """
            <div class="justified-text">
           <strong>Citra radar NASA SRTM</strong> sudah disediakan dalam format <strong>digital elevation model (DEM)</strong> sehingga informasi <strong>elevasi</strong> yang diperlukan <strong>dapat langsung diambil</strong> tanpa proses konversi tambahan, sedangkan data <strong>slope</strong> dapat diperoleh dengan memanfaatkan <strong>application programming interface (API)</strong> Google Earth Engine bernama <strong>ee.Terrain.slope()</strong> yang <strong>menghasilkan nilai kemiringan lereng</strong> dari data elevasi.
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
        <strong>Data indeks spektral</strong>, baik NDBI, NDMI, dan NDVI dari citra <strong>Landsat Surface Reflectance</strong> yang <strong>beresolusi spasial 30 meter</strong> perlu <strong>divalidasi</strong> untuk memastikan <strong>akurasi data</strong>. Dalam penelitian ini, dilakukan <strong>perbandingan statistik</strong> dengan data sekunder dari citra lain yang memiliki resolusi spasial <strong>lebih tinggi</strong> yakni <strong>Sentinel-2 MSI Surface Reflectance</strong> yang <strong>beresolusi spasial 10 meter</strong>. Tahap validasi data indeks dari citra Landsat 8 tahun 2024 diuraikan sebagai berikut.
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
        <strong>• NDBI</strong>
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
        dengan:<br>
        NDBI = Normalized Difference Built-Up Index<br>
        SWIR-1 = band 11<br>
        NIR = band 8
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
        <strong>• NDMI</strong>
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
        dengan:<br>
        NDMI = Normalized Difference Moisture Index<br>
        NIR = band 8<br>
        SWIR-1 = band 11
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
        <strong>• NDVI</strong>
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
        dengan:<br>
        NDVI = Normalized Difference Vegetation Index<br>
        NIR = band 8<br>
        Red = band 4
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
            "**2. Resampling 30m**",
            color="primary",
        )

        st.markdown(
            """
        <div class="justified-text">
        Resolusi spasial data indeks Sentinel-2 yang semula 10 meter <strong>diatur ulang</strong> menjadi 30 meter menggunakan teknik <strong>resampling</strong> agar <strong>sesuai</strong> dengan <strong>resolusi citra Landsat</strong>.
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
        Untuk keperluan <strong>uji statistik</strong>, terlebih dahulu dibutuhkan <strong>sampel</strong> dari masing-masing data. Google Earth Engine menyediakan API <strong>ee.Image.sample</strong> yang memungkinkan <strong>pembuatan titik sampel secara acak</strong> dan otomatis.
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

// Filter Titik Sampel (Rentang NDBI -1 hingga 1)
var cleanSamplesVal = samplesVal.filter(
  ee.Filter.and(
    ee.Filter.gte('ndbiSentinel', -1),
    ee.Filter.lte('ndbiSentinel', 1),
    ee.Filter.gte('ndbiLandsat', -1),
    ee.Filter.lte('ndbiLandsat', 1),
    ee.Filter.notNull(['ndbiSentinel']),
    ee.Filter.notNull(['ndbiLandsat'])
  )
);

print('Jumlah Sampel Bersih:', cleanSamplesVal.size());
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
        Validasi indeks dari citra Sentinel-2 dilakukan melalui <strong>uji statistik korelasi Pearson</strong> dan perhitungan nilai <strong>RMSE</strong> serta <strong>MAE</strong>.
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
            "**1. Sampling dan Validasi**",
            color="primary",
        )
        st.markdown(
            """
        <div class="justified-text">
        Validasi penutup lahan dilakukan untuk menguji kesesuaian hasil klasifikasi dengan kondisi aktual. Jumlah total sampel ditentukan menggunakan rumus <strong>Fitzpatrick-Lins (1981)</strong> dengan asumsi <strong>akurasi yang diharapkan 85%</strong> dan <strong>toleransi kesalahan 10%</strong>.
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
        dengan:<br>
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
        Hasil kalkulasi menunjukkan bahwa dibutuhkan sekitar <strong>51 titik sampel</strong> untuk mencapai skema akurasi tersebut. Distribusi sampel tiap kelas penutup lahan (strata) diestimasi dengan metode <strong>Proportional Random Sampling<strong>.
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
        dengan:<br>
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
        Dari perhitungan tersebut, maka <strong>distribusi sampel</strong> pada kelas <strong>vegetasi</strong> adalah sebesar <strong>33 titik</strong>, <strong>tubuh air 0 titik</strong>, <strong>lahan terbangun 12 titik</strong>, dan <strong>lahan terbuka 6 titik</strong>. Apabila terdapat kelas yang tidak memperoleh sampel (misalnya tubuh air), dilakukan <strong>realokasi</strong> dari strata dengan alokasi terbesar (contohnya vegetasi) tanpa mengubah proporsi secara signifikan. Pada kasus ini, vegetasi menyumbangkan 3 titik ke kelas tubuh air sehingga masing-masing kelas tetap <strong>dapat divalidasi akurasinya</strong>.
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
        Ekstraksi titik sampel dilakukan menggunakan Google Earth Engine (GEE) melalui API ee.Image.stratifiedSample. Setiap titik sampel berisi informasi kelas penutup lahan sekaligus nilai LST tahun 2024 karena citra hasil pengolahan LST tahun terkait turut dimasukkan dalam proses ekstraksi. Titik sampel kemudian diekspor dalam format CSV. Kode dalam Google Earth Engine untuk ekstraksi dan ekspor otomatis ditunjukkan berikut ini.
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
        Validasi lapangan memanfaatkan aplikasi Google Maps (My Maps) untuk navigasi, Avenza Maps untuk plotting titik koordinat, GPS Map Camera untuk dokumentasi, dan Google Spreadsheet untuk pencatatan. Tabel checklist yang digunakan berisi informasi terkait:<br>
        • Nomor dan kode titik<br>
        • Koordinat (X, Y)<br>
        • Tanggal dan waktu observasi<br>
        • Kondisi cuaca<br>
        • Penutup lahan hasil klasifikasi<br>
        • Penutup lahan aktual<br>
        • Nilai LST hasil ekstraksi citra Landsat 8<br>
        • Pengukuran LST (1), (2), (3)<br>
        • LST aktual (rata-rata)<br>
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
        Untuk data penutup lahan tahun 2014 dan 2019, validasi dilakukan dengan metode serupa, tetapi verifikasi dilakukan menggunakan citra dari Google Earth dengan timestamps yang disesuaikan dengan tahun terkait.        
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
        Akurasi penutup lahan dihitung dengan matriks konfusi yang diadaptasi dari Stuckenberg (2013) sebagai berikut.
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
        Matriks konfusi menyajikan hasil perhitungan berupa <strong>user accuracy, producer accuracy, kesalahan omisi, kesalahan komisi, overall accuracy,</strong> dan <strong>kappa accuracy</strong>. Hasil perhitungan matriks tersebut menentukan apakah hasil klasifikasi penutup lahan <strong>dapat diterima atau tidak</strong> (Darmawan, 2023). Berikut ini adalah formula untuk menghitung masing-masing metrik akurasi tersebut.
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
        <strong>• Producer Accuracy</strong>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 1. Producer Accuracy
        display_equation_validate(r"\frac{X_{11}}{X_{+1}} \times 100\%")

        st.markdown(
            """
        <div class="justified-text">
        <strong>• User Accuracy</strong>
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
        <strong>• Kesalahan Omisi</strong>
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
        <strong>• Kesalahan Komisi</strong>
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
        <strong>• Overall Accuracy</strong>
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
        <strong>• Kappa Accuracy</strong>
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
        dengan:<br>
        N = Total sampel<br>
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
        <strong>Validasi suhu permukaan lahan (LST)</strong> dilakukan pada titik sampel yang sama dengan validasi penutup lahan sehingga kegiatan lapangan lebih efisien. Nilai LST lapangan diukur menggunakan <strong>termometer inframerah</strong> seri Fluke 561 dengan tiga kali pengulangan per titik untuk memperoleh rata-rata yang lebih stabil. Pengukuran LST lapangan dilaksanakan antara pukul 09.00-11.00 WIB dalam kondisi cuaca cerah untuk menyesuaikan dengan waktu perekaman citra satelit Landsat 8 (Atianta, 2020). <strong>Uji akurasi</strong> antara LST hasil ekstraksi citra Landsat 8 dengan data pengukuran lapangan dilakukan menggunakan metrik <strong>RMSE</strong> dan <strong>MAE</strong> untuk mengukur tingkat kesalahan, serta <strong>koefisien determinasi (R²)</strong> untuk menilai kesesuaian hubungan antar data. 
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
        <strong>• Root Mean Square Error (RMSE)</strong>
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
        <strong>• Mean Absolute Error (MAE)</strong>
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
        <strong>• Koefisien Determinasi (R²)</strong>
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
        dengan:<br>
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
            Visualisasi validasi ditampilkan dalam bentuk scatterplot regresi yang memperlihatkan distribusi nilai aktual terhadap hasil ekstraksi lengkap dengan garis regresi dan nilai koefisien determinasi.
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
        st.write("Page under construction.")
    elif option == "🌳 Indeks":
        st.subheader("**Indeks**")
        st.write("Page under construction.")
    elif option == "🌡️ Suhu Permukaan Lahan":
        st.subheader("**Suhu Permukaan Lahan**")
        st.write("Page under construction.")
