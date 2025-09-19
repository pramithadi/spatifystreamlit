import streamlit as st

# --------------------
# KONFIGURASI HALAMAN
# --------------------
st.set_page_config(
    page_title="Selamat Datang di Spatify", page_icon="👋", layout="centered"
)


# --------------------
# KONTEN HALAMAN (COPYWRITING)
# --------------------

# --- BAGIAN 1: JUDUL UTAMA & SAMBUTAN ---
st.title("Selamat Datang di Dasbor Analisis Spatify! 🗺️")
st.write("---")


# --- BAGIAN 2: PENJELASAN SINGKAT ---
st.info(
    """
    Selamat datang di ruang kerja interaktif Spatify.
    Aplikasi ini adalah dasbor utama untuk memvisualisasikan, menganalisis, dan memahami
    data geospasial time-series di Kawasan Perkotaan Yogyakarta.
    """
)


# --- BAGIAN 3: ARAHAN PENGGUNAAN (CALL TO ACTION) ---
# **COPYWRITING DIPERBARUI SESUAI GAMBARAN ANDA**
st.header("Mulai Eksplorasi Anda")
st.markdown(
    """
    👈 **Gunakan menu di sidebar kiri** untuk menavigasi tiga bagian utama aplikasi:

    ---

    ### 🔬 Analisis
    *Bagian utama untuk eksplorasi hasil akhir penelitian.*

    Pilih parameter yang Anda minati (Penutup Lahan, NDBI, NDMI, NDVI, atau Suhu Permukaan Lahan), lalu jelajahi lebih dalam melalui tab interaktif:
    - **Peta**: Visualisasikan sebaran spasial data dari tahun ke tahun.
    - **Tren**: Amati perubahan nilai rata-rata dari waktu ke waktu melalui grafik.
    - **Validasi**: Lihat perbandingan data model dengan data observasi.
    - **Model**: Pahami model prediksi yang digunakan untuk data di masa depan.

    ---

    ### ⚙️ How It's Made
    *Bagian untuk transparansi, pelajari bagaimana data ini diolah.*

    - **Dataset**: Lihat sumber data citra satelit yang digunakan, lengkap dengan link dan cuplikan kode GEE.
    - **Alur Proses**: Pahami seluruh metodologi penelitian, mulai dari diagram alir, prapengolahan, pengolahan, hingga validasi data.
    - **GEE Apps**: Coba langsung aplikasi pengolahan data versi Google Earth Engine yang menjadi dasar penelitian ini.

    ---

    ### 📄 Get Results
    *Bagian untuk mengunduh hasil akhir penelitian.*

    - **Download Peta**: Unduh peta hasil analisis dalam format **PDF** berkualitas tinggi, siap untuk digunakan dalam laporan, presentasi, atau publikasi Anda.

    """
)
st.success("Semua halaman bersifat interaktif. Silakan pilih menu untuk memulai!")


# --- BAGIAN 4: KONTEKS PENELITIAN (MENAMBAH NILAI AKADEMIS) ---
with st.expander("Lihat Tujuan Aplikasi & Penelitian Ini"):
    st.markdown(
        """
        Aplikasi Spatify dikembangkan untuk mencapai beberapa tujuan utama:

        1.  **Memahami Fenomena Pulau Bahang Perkotaan (Urban Heat Island):** Menyajikan data suhu permukaan secara visual untuk mengidentifikasi area-area dengan anomali panas di Yogyakarta.

        2.  **Menganalisis Hubungan Parameter Biofisik:** Mempelajari korelasi antara Suhu Permukaan Lahan (LST) dengan kerapatan vegetasi (NDVI), area terbangun (NDBI), dan kelembapan (NDMI).

        3.  **Menyediakan Alat Bantu Keputusan:** Menyajikan data historis yang mudah diakses bagi para perencana kota, akademisi, dan publik untuk mendukung perencanaan kota yang lebih sejuk dan berkelanjutan.
        """
    )


# --- BAGIAN 5: TENTANG PENGEMBANG ---
with st.expander("Tentang Pengembang"):
    st.write(
        """
        Aplikasi ini dirancang dan dikembangkan oleh **Pramitha Dewi**
        sebagai bagian dari Proyek Skripsi untuk Program Studi Kartografi dan Penginderaan Jauh,
        Fakultas Geografi, Universitas Gadjah Mada.

        Saran dan masukan untuk pengembangan sangat dihargai untuk menunjang uji usabilitas.
        """
    )
