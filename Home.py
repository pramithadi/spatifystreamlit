import streamlit as st

st.set_page_config(
    page_title="Selamat Datang di Spatify",
    layout="wide",  # centered # wide
    initial_sidebar_state="expanded",  # collapsed
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    .main {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 2rem !important;
    }
    .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
        font-family: 'Poppins', sans-serif !important;
    }
    div[data-testid="stMarkdownContainer"] * {
        font-family: 'Poppins', sans-serif !important;
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

st.title("Spatify — Spatial Information of Yogyakarta City")
st.write("---")
st.success(
    """
    Selamat datang di **Spatify**! Aplikasi *web* interaktif ini mengajak Anda untuk melihat bagaimana **suhu permukaan, penutup lahan, kerapatan area terbangun** dan **vegetasi** hingga **kelembapannya** di Kawasan Perkotaan Yogyakarta dan sekitarnya **telah berubah** selama 25 tahun terakhir (1999-2024). Temukan polanya dan lihat seperti apa prediksi kondisi di tahun 2029!
    """
)

st.subheader("Mulai Eksplorasi!")
st.markdown(
    """
    👈 **Gunakan menu di *sidebar* kiri** untuk memulai eksplorasi Anda ke tiga bagian utama aplikasi.

    ---

    ### Dasbor Analisis
    *Apa yang ingin Anda ketahui? Mulai analisis Anda dari sini.*

    Untuk memulai, silakan pilih parameter pada *sidebar*, lalu jelajahi lebih dalam melalui *tab* interaktif:
    - **Peta**: Visualisasikan sebaran spasial data secara interaktif dari tahun ke tahun.
    - **Tren**: Amati perubahan nilai rata-rata dari waktu ke waktu dalam bentuk grafik.
    - **Validasi**: Bandingkan data hasil ekstraksi dengan data observasi.
    - **Model**: Lihat akurasi model *machine learning* untuk prediksi masa depan.
    - **Regresi**: Analisis hubungan statistik yang terjadi antar parameter.

    ---

    ### Telisik Proses
    *Lihat lebih dalam bagaimana data diolah dan penelitian ini dilakukan.*

    - **Alat**: Temukan alat, *software*, *platform*, dan *library* yang digunakan dalam penelitian ini.
    - **Dataset**: Lihat sumber data (citra satelit, citra radar, dan *shapefile*) beserta *link* dan cuplikan kodenya.
    - **Metodologi**: Amati seluruh proses penelitian, mulai dari diagram alir, prapengolahan, ekstraksi, validasi, hingga pemodelan data.
    
    ---

    ### Eksplorasi Hasil
    *Akses hasil akhir penelitian dengan unduh peta atau jalankan aplikasi GEE yang interaktif.*

    - **Unduh Peta**: Unduh peta analisis dalam format PDF di sini.
    - **Earth Engine Apps**: Bandingkan peta antar tahun secara langsung menggunakan fitur *split panel* di Google Earth Engine.

    ---
    """
)

with st.expander("Tentang Aplikasi"):
    st.markdown(
        """
        **Spatify** dirancang dan dikembangkan oleh **Pramitha Dewi** di bawah bimbingan Bapak **Karen Slamet Hardjo, S.Si., M.Sc.** sebagai bagian dari Proyek Akhir di Program Studi **Sarjana Terapan Sistem Informasi Geografis, Sekolah Vokasi, Universitas Gadjah Mada** tahun 2025.
        
        Spatify dikembangkan untuk mencapai beberapa tujuan dalam Proyek Akhir ini, yaitu:
        - **Memetakan kondisi historis** (1999-2024) berbagai parameter (LST, penutup lahan, dan indeks spektral) di Kawasan Perkotaan Yogyakarta dan sekitarnya menggunakan  Google Earth Engine.
        - **Memprediksi** kondisi penutup lahan dan LST untuk tahun 2029 dengan model *machine learning* (XGBoost dan CA-Markov).
        - **Menyajikan seluruh data** historis dan prediksi dalam sebuah *web app* dan Earth Engine Apps yang interaktif.
        """
    )

with st.expander("Tentang Pengembang"):
    col1, col2 = st.columns([0.8, 3.2])

    with col1:
        # st.image("./assets/foto_profil_1.svg", width=142)

        st.image("./assets/foto_profil_9.svg", width=142)

    with col2:
        st.markdown(
            """
            ##### Halo! Saya Pramitha 👋

            Terima kasih telah menggunakan **Spatify**! Setiap saran untuk pengembangan aplikasi sangat berarti. **Mari terhubung dan berkolaborasi melalui**:

            - **Email**: [pramitha.dewi@mail.ugm.ac.id](mailto:pramitha.dewi@mail.ugm.ac.id)  
            - **LinkedIn**: [linkedin.com/in/pramithadi](https://linkedin.com/in/pramithadi)  
            - **GitHub**: [github.com/pramithadi](https://github.com/pramithadi) 

            """,
            unsafe_allow_html=True,
        )
