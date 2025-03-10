def extract_abstract(split_document):
    """
    Fungsi untuk mengekstrak abstrak dari dokumen yang telah dipisahkan ke dalam halaman-halaman.

    Parameters:
        split_document (list): Daftar halaman dokumen yang telah dipisah, 
                               masing-masing dengan atribut 'page_content'.

    Returns:
        str: Abstrak yang diekstrak, termasuk teks dari halaman berikutnya jika relevan.
    """
    abstract = ""  # Inisialisasi variabel untuk menyimpan teks abstrak
    next_page_text = ""  # Variabel untuk menyimpan teks halaman berikutnya

    # Daftar kata kunci yang digunakan untuk mencari 'Abstrak' atau 'Abstract'
    keywords = ['abstrak', 'abstract']

    # Daftar varian kata kunci yang tidak akan dilanjutkan ke halaman berikutnya
    stop_keywords = [
        'kata kunci:', 'kata - kunci', 'kata kunci: ', 'kata kunci', 'kata-kunci',
        'kata kunci ;', 'kata kunci -', 'kata kunci:', 'kata kunci :', 'kata kunci - ',
        'kata kunci ;', 'kata kunci -', 'kata_kunci', 'kata kunci :', 'kata kunci-',
        'daftar kata kunci', 'daftar-kata kunci', 'daftar-kata kunci :', 'daftar kata - kunci',
        'table of contents', 'table of contents:', 'daftar isi:', 'contents:', 'index:',
        'contents list', 'index list'
    ]

    for i, page in enumerate(split_document):
        text = getattr(page, 'page_content', "").strip()  # Menggunakan getattr untuk menghindari AttributeError

        # Periksa apakah halaman ini mengandung 'Daftar Isi' atau 'Table of Contents'
        if 'daftar isi' in text.lower() or 'table of contents' in text.lower():
            continue  # Lewati halaman ini jika merupakan daftar isi

        # Mencari kata kunci 'Abstrak' atau 'Abstract'
        start_index = -1
        for keyword in keywords:
            start_index = text.lower().find(keyword)
            if start_index != -1:
                break  # Keluar dari loop jika salah satu kata kunci ditemukan

        if start_index != -1:
            # Ambil teks dari awal abstrak hingga akhir halaman atau sebelum dua newline
            end_index = text.find('\n\n', start_index)
            if end_index == -1:
                end_index = len(text)

            abstract_text = text[start_index:end_index]
            abstract = abstract_text.strip()  # Simpan teks yang telah dipotong

            # Periksa apakah ada varian kata kunci yang ditemukan di halaman ini
            if any(stop_keyword in text.lower() for stop_keyword in stop_keywords):
                next_page_text = ""  # Jangan ambil teks dari halaman berikutnya
            else:
                # Coba ambil teks dari halaman berikutnya jika ada
                if i + 1 < len(split_document):
                    next_page_text = getattr(split_document[i + 1], 'page_content', "").strip()

            break  # Hentikan pencarian setelah menemukan abstrak

    # Gabungkan teks abstrak dan teks dari halaman berikutnya jika diperlukan
    abstract += next_page_text
    return abstract