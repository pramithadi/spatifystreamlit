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

with tab1:
    st.badge("**Diagram Alir Penelitian**", color="primary")
    with st.container(border=False):
        st.image(
            "./assets/diagram_alir2.svg",
        )

with tab2:
    # Penyaringan Citra
    st.badge("**Penyaringan Citra**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        Penyaringan citra bertujuan untuk <strong>menyortir citra</strong> dalam Google Earth Engine sesuai dengan batasan penelitian yang telah ditetapkan.
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

    # Scaling Factor
    st.badge("**Scaling Factor**", color="primary")
    st.markdown(
        """
        <div class="justified-text">
        <strong>Scaling factor</strong> dilakukan untuk mengembalikan nilai radiansi dan reflektansi citra Landsat Surface Reflectance yang sebelumnya berformat <strong>integer</strong> menjadi <strong>float</strong> agar hasil pengolahan data memiliki ketelitian hingga tingkat desimal (USGS, 2023).
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
        <strong>Cloud masking</strong> metode <strong>Quality Assesment (QA)</strong> merupakan teknik untuk mengurangi tutupan awan dalam citra (Sinabutar <em>et al.</em>, 2020). Metode ini bekerja otomatis dengan memberi tanda pada piksel-piksel awan kemudian menyortir piksel tersebut agar tidak digunakan dalam analisis. Celah yang kosong lantas diisi dengan piksel lain yang lebih bersih melalui teknik <strong>median composite</strong>.
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

    # Hasil Prapengolahan Data
    st.write(
        "Berikut merupakan contoh tampilan citra Landsat 8 Surface Reflectance tahun 2024 **sebelum** dan **sesudah** dilakukan cloud masking:"
    )

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

    with st.expander("Lihat Referensi"):
        st.markdown(
            """
                - Sinabutar, J. J., Sasmito, B., Sukmono, A. (2020). Studi Cloud Masking Menggunakan Band Quality Assessment, Function of Mask, dan Multi-Temporal Cloud Masking pada Citra Landsat 8. *Jurnal Geodesi Undip*, 9(3). 51-60. https://doi.org/10.14710/jgundip.2020.28123 
                - United States Geological Survey. (2023). How Do I Use A Scale Factor with Landsat Level-2 Science Products?. (*https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products*, diakses 8 Juli 2025).
                """
        )

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
            Ekstraksi <strong>suhu permukaan lahan</strong> atau <strong>land surface temperature</strong> (LST) dalam penelitian ini menggunakan metode <strong>Single-Channel</strong> yang dikembangkan oleh Jiménez-Muñoz & Sobrino (2010). Metode ini terdiri atas empat tahap perhitungan, yaitu:
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Perhitungan Nilai Radiansi Spektral
        st.badge("**1. Perhitungan Nilai Radiansi Spektral**", color="primary")
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
        <strong>Emisivitas permukaan (ε)</strong> adalah kemampuan suatu objek dalam <strong>menyerap radiasi</strong> matahari dan <strong>memancarkan</strong> radiasi <strong>termal</strong> (Mallick <em>et al.</em>, 2012). Penelitian ini menggunakan pendekatan <strong>NDVI</strong> dan <strong>Proportion of Vegetation (Pv)</strong> untuk mendapatkan nilai emisivitas permukaan. Berikut rumus dan contoh implementasi kode dalam Google Earth Engine.
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
        codeNDVI = """
// Perhitungan NDVI
var ndvi1999 = landsat1999.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi1999'); // Landsat 5
var ndvi2004 = landsat2004.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi2004'); // Landsat 7
var ndvi2024 = landsat2024.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi2024'); // Landsat 8
"""
        st.code(codeNDVI, language="javascript", line_numbers=True)

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
var emisi2024 = pv2024.multiply(k1).add(k2).rename('emisi2024');
"""
        st.code(codeEmisivitasPermukaan, language="javascript", line_numbers=True)

        # Perhitungan Brightness Temperature
        st.badge("**3. Perhitungan Brightness Temperature**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        <strong>Brightness temperature</strong> adalah <strong>representasi suhu permukaan</strong> dari radiasi termal objek yang direkam oleh sensor termal dan disajikan ke dalam satuan <strong>kelvin</strong> (Jatayu & Susetyo, 2017). Penerapan function Scaling Factor telah <strong>mengkalibrasi</strong> saluran termal ke dalam satuan kelvin sehingga <strong>dapat langsung dimanfaatkan sebagai nilai brightness temperature</strong> (Waleed & Sajjad, 2022). Saluran termal citra Landsat 5 dan Landsat 7 adalah band 6, sedangkan dalam citra Landsat 8 adalah band 10.
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

        st.badge("**4. Perhitungan LST**", color="primary")
        st.markdown(
            """
        <div class="justified-text">
        Nilai emisivitas permukaan dan brightness temperature yang telah didapatkan lantas <strong>dikalkulasi</strong> dengan <strong>panjang gelombang saluran termal</strong> dan nilai <strong>radiasi emisivitas</strong> yang diestimasi dari konstanta Planck, Stefan-Boltzmann, dan nilai kecepatan cahaya (Waleed & Sajjad, 2022). Untuk mendapatkan <strong>nilai LST</strong> dalam <strong>derajat celcius</strong> tidak luput untuk mengonversi hasilnya dengan 273.15. Berikut rumus dan contoh implementasi kode dalam Google Earth Engine.
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
            "Rumus LST",
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
var lst2024 = bt2024.expression(
  '(Bt/(1+(0.00115*(Bt/1.438))*log(Ep)))-273.15', {
    'Bt': bt2024,
    'Ep': emisi2024
  }).rename('lst2024');
"""
        st.code(codeLST, language="javascript", line_numbers=True)

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
            Perhitungan <strong>indeks kerapatan area terbangun</strong> (NDBI) diestimasi dengan memanfaatkan <strong>saluran reflektif inframerah-dekat (NIR)</strong> dan <strong>inframerah-gelombang pendek (SWIR)</strong> yang sangat sensitif terhadap area terbangun (Wicaksono <em>et al.</em>, 2021). Berikut rumus dan contoh implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus NDBI
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Rumus NDBI",
            r"NDBI = \frac{SWIR - NIR}{SWIR + NIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        NDBI = Normalized Difference Built-Up Index<br>
        SWIR = Band 5 (Landsat 5 dan Landsat 7), Band 6 (Landsat 8)<br>
        NIR = Band 4 (Landsat 5 dan Landsat 7), Band 5 (Landsat 8)
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
            <strong>Indeks kelembapan vegetasi</strong> (NDMI) dihitung dengan memanfaatkan <strong>saluran reflektif inframerah-gelombang pendek (SWIR)</strong> dan <strong>inframerah-dekat (NIR)</strong> serupa NDBI. Namun, terdapat perbedaan urutan saluran reflektif yang digunakan dalam formula sebagaimana dirumuskan oleh Gao (1996). Perhitungan NDMI menempatkan saluran NIR sebagai pengurang, berbeda dengan NDBI yang menggunakan SWIR di posisi tersebut. Berikut rumus dan contoh implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Rumus NDMI
        def display_equation(title, equation):
            st.markdown(f"**{title}**")
            st.latex(equation)
            # st.markdown(
            #     "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
            # )

        display_equation(
            "Rumus NDMI",
            r"NDMI = \frac{NIR - SWIR}{NIR + SWIR}",
        )

        st.markdown(
            """
        <div class="justified-text">
        <strong>Keterangan:</strong><br>
        NDMI = Normalized Difference Moisture Index<br>
        NIR = Band 4 (Landsat 5 dan Landsat 7), Band 5 (Landsat 8)<br>
        SWIR = Band 5 (Landsat 5 dan Landsat 7), Band 6 (Landsat 8)
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
            Perhitungan <strong>indeks kerapatan vegetasi</strong> (NDVI) dilakukan dengan memanfaatkan reflektansi <strong>saluran inframerah-dekat (NIR)</strong> dan <strong>saluran merah (red)</strong> (Estoque <em>et al.</em>, 2017). Kedua saluran ini sensitif terhadap pigmen klorofil dan struktur sel daun sehingga dapat memetakan perbedaan kecerahan antara lahan bervegetasi dan non-vegetasi (‘Ain, 2021). Berikut rumus dan contoh implementasi kode dalam Google Earth Engine.
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
        codeNDVI = """
// Perhitungan NDVI
var ndvi1999 = landsat1999.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi1999'); // Landsat 5
var ndvi2004 = landsat2004.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi2004'); // Landsat 7
var ndvi2024 = landsat2024.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi2024'); // Landsat 8
"""
        st.code(codeNDVI, language="javascript", line_numbers=True)

        with st.expander("Lihat Referensi"):
            st.markdown(
                """
                - Estoque, Ronald, C., Murayama, Yuji. (2017). Landscape Pattern and Ecosystem Service Value Changes: Implications for Environmental Sustainability Planning for the Rapidly Urbanizing Summer Capital of the Philippines. *Landscape Urban Plan*, 116. 60-72. https://doi.org/10.1016/j.landurbplan.2013.04.008
                - ‘Ain, S. S. (2022). *Analisis Spasio-Temporal Suhu Permukaan Lahan di Provinsi DKI Jakarta Tahun 1991-2021 berbasis Cloud GIS: Google Earth Engine*. Tugas Akhir, Sekolah Vokasi. Yogyakarta: Universitas Gadjah Mada.
                """
            )

    elif option == "🏞️ Penutup Lahan":
        st.subheader("**Penutup Lahan**")
        st.markdown(
            """
            <div class="justified-text">
            Penutup lahan dipetakan menggunakan <strong>klasifikasi supervised</strong> pada citra multispektral. Metode ini <strong>memanfaatkan sampel</strong> dari tiap kelas penutup lahan untuk <strong>melatih model klasifikasi</strong>. Prosedur klasifikasi supervised penutup lahan di Google Earth Engine ditunjukkan berikut ini:
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Pembuatan Training Area
        st.badge("**1. Pembuatan Training Area**", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        <strong>Training area</strong> adalah kumpulan sampel dari setiap kelas penutup lahan yang akan diklasifikasi. Klasifikasi penutup lahan mengacu pada sistem <strong>SNI 7645:2010</strong> yang telah disesuaikan dengan kondisi penutup lahan di lokasi penelitian. Kelas yang digunakan dalam penelitian ini meliputi <strong>vegetasi, tubuh air, lahan terbangun, dan lahan terbuka</strong>. Berikut contoh implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
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

        # Sebaran Training Area
        st.write(
            "Di bawah ini merupakan visualisasi sebaran training area pada citra Landsat 8 Surface Reflectance tahun 2024."
        )
        st.image(
            "./assets/training_area.png",
            caption="Persebaran Sampel Kelas Penutup Lahan di Kawasan Perkotaan Yogyakarta dan Sekitarnya Tahun 2024",
        )

        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
        )

        # Klasifikasi Supervised
        st.badge("**2. Klasifikasi Supervised**", color="primary")
        st.markdown(
            """
        <div class="justified-text">        
        Training area dilatih menggunakan algoritma <strong>Classification and Regression Tree (CART)</strong> yakni algoritma <strong>machine learning</strong> dengan skema <strong>decision tree (pohon keputusan)</strong> yang umum digunakan dalam klasifikasi penutup lahan (Krzywinski & Altman, 2017). Algoritma ini membangun <strong>aturan klasifikasi<strong> dari sampel training area yang ada lalu <strong>menerapkannya</strong> untuk <strong>memetakan kelas penutup lahan</strong> pada setiap piksel citra. Berikut contoh implementasi kode dalam Google Earth Engine.
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
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

        # Hasil Klasifikasi Penutup Lahan
        st.write(
            "Visualisasi dari hasil klasifikasi penutup lahan di lokasi penelitian tahun 2024 ditunjukkan pada gambar berikut."
        )
        st.image(
            "./assets/hasil_klasifikasi.png",
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
        st.markdown(
            "<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True
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
           <strong>Citra radar NASA SRTM</strong> telah tersedia dalam format <strong>digital elevation model (DEM)</strong> sehingga data <strong>elevasi</strong> yang dibutuhkan <strong>dapat langsung diekstraksi</strong> tanpa memerlukan proses konversi tambahan. Sementara data <strong>slope</strong> dapat diturunkan melalui <strong>application programming interface (API)</strong> Google Earth Engine bernama <strong>ee.Terrain.slope()</strong> yang akan <strong>menghitung kemiringan lereng</strong> berdasarkan nilai elevasi. Berikut contoh implementasi kode dalam Google Earth Engine.
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

with tab4:
    option = st.pills(
        "**Lihat Validasi:**",
        [
            "🌳 Indeks",
            "🏞️ Penutup Lahan",
            "🌡️ Suhu Permukaan Lahan",
        ],
        default="🌳 Indeks",
    )

    if option == "🌳 Indeks":
        st.subheader("**Indeks**")
        st.write("Page under construction.")
    elif option == "🏞️ Penutup Lahan":
        st.subheader("**Penutup Lahan**")
        st.write("Page under construction.")
    elif option == "🌡️ Suhu Permukaan Lahan":
        st.subheader("**Suhu Permukaan Lahan**")
        st.write("Page under construction.")

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
