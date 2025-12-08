import streamlit as st

st.set_page_config(
    page_title="Selamat Datang di Spatify",
    layout="centered",  # centered # wide
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

st.title("Selamat datang di Spatify!")
st.write("---")
st.success(
    """
    **Spatial Information of Yogyakarta City (Spatify)** membantu Anda menelusuri bagaimana **suhu permukaan lahan, penutup lahan, kerapatan dan kelembapan vegetasi, serta persebaran area terbangun** di Kawasan Perkotaan Yogyakarta dan sekitarnya telah berubah dalam **25 tahun terakhir (1999-2024)**.
    
    Temukan polanya dan lihat juga **prediksi kondisi tahun 2029** untuk memahami dinamika lingkungan di masa mendatang!
    """
)

st.subheader("Mulai Eksplorasi!")
st.markdown(
    """
    👈 **Gunakan menu di *sidebar* kiri** untuk memulai eksplorasi Anda ke berbagai fitur utama Spatify.
    """
)

st.video(
    "https://youtu.be/1LbI5FbKMHs",
    start_time=70,
    end_time=80,
    format="video/mp4",
)
st.caption("Video Panduan Penggunaan Web App Spatify")
st.markdown(
    """
    ---

    ### Dasbor Visualisasi
    *Apa yang ingin Anda ketahui? Jelajahi dari sini.*

    Untuk memulai, silakan pilih parameter pada *sidebar*, lalu jelajahi lebih dalam melalui *tab* interaktif:
    - **Peta**: Visualisasikan sebaran spasial data secara interaktif dari tahun ke tahun.
    - **Tren**: Amati perubahan nilai rata-rata dari waktu ke waktu dalam bentuk grafik.
    - **Validasi**: Bandingkan data hasil ekstraksi dengan data observasi.
    - **Model**: Lihat akurasi model *machine learning* dan hasil prediksinya.
    - **Regresi**: Tinjau hubungan statistik yang terjadi antarparameter.

    ---

    ### Eksplorasi Hasil
    *Akses hasil akhir penelitian melalui peta yang telah disusun dan siap diunduh.*
    - **Unduh Peta**: Dapatkan peta hasil visualisasi dalam format PDF.

    ---
    
    ### Aset
    *Temukan berbagai sumber data dan alat yang digunakan dalam proses pemetaan dan pengolahan informasi.*
    - **Dataset**: Jelajahi dataset yang digunakan melalui pintasan kode.
    - **Alat**: Lihat serangkaian alat untuk ekstraksi, pemodelan prediksi, hingga visualisasi.
    - **Proyek**: Akses source code dalam proyek Google Earth Engine dan Google Colab. 

    ---
    """
)

with st.expander("Tentang Aplikasi"):
    st.markdown(
        """
        **Spatify** dirancang dan dikembangkan oleh **Pramitha Dewi** di bawah bimbingan Bapak **Karen Slamet Hardjo, S.Si., M.Sc.** sebagai bagian dari proyek akhir di Program Studi **Sarjana Terapan Sistem Informasi Geografis, Departemen Teknologi Kebumian, Sekolah Vokasi, Universitas Gadjah Mada** tahun 2025. 
        
        Spatify dikembangkan untuk mencapai tujuan dalam proyek akhir ini, yaitu:
        - **Memetakan kondisi historis (1999-2024)** dari berbagai parameter—LST, penutup lahan, NDVI, NDBI, dan NDMI—di Kawasan Perkotaan Yogyakarta dan sekitarnya menggunakan Google Earth Engine.
        - **Memprediksi perubahan** penutup lahan, indeks, dan LST pada tahun 2029 menggunakan model *machine learning* (XGBoost dan Cellular Automata-Markov Chain).
        - **Menyajikan data historis dan hasil prediksi** ke dalam sebuah *web app* interaktif.

        Spatify dibangun menggunakan **Streamlit** dan dihosting secara gratis melalui **Streamlit Community Cloud**. Beberapa konten ditampilkan dalam bentuk yang disederhanakan untuk menyesuaikan batas kapasitas server. Namun, penyesuaian ini tidak memengaruhi inti informasi maupun hasil analisis yang disajikan.
        """
    )

with st.expander("Tentang Pengembang"):
    col1, col2 = st.columns([0.6, 3.4])

    with col1:
        # st.image("./assets/foto_profil_5.svg", width=90)
        st.image("./assets/sidang2.svg", width=90)

    with col2:
        st.markdown(
            """
            ##### Halo! Saya Pramitha 👋

            Terima kasih telah menggunakan **Spatify**! Setiap saran untuk pengembangan aplikasi sangat berarti. **Mari terhubung melalui**:
            [Email](mailto:pramitha.dewi@mail.ugm.ac.id) | [LinkedIn](https://linkedin.com/in/pramithadi) | [GitHub](https://github.com/pramithadi) | [Instagram](https://instagram.com/pramithadi)

            """,
            unsafe_allow_html=True,
        )
