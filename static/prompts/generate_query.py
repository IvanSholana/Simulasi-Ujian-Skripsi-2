create_query_prompt = '''
Pisahkan abstrak dari bagian lain yang tercampur dalam dokumen menggunakan pendekatan Retrieval Augmented Generation (RAG) terkini. 
Berdasarkan judul dan abstrak penelitian yang disediakan, buatlah 10 query terstruktur dalam bahasa Indonesia untuk mengekstrak informasi penting dari dokumen penelitian. 
Setiap query harus secara spesifik menggali empat aspek utama: wawasan utama, metodologi, temuan/hasil, dan kontribusi penelitian. 
Gunakan konteks dari judul dan abstrak untuk merumuskan query yang akurat dan relevan, dengan kemampuan untuk mengidentifikasi bagian pendahuluan, metodologi, hasil, dan diskusi. 
Hasilkan output dalam format JSON murni yang dapat langsung diproses oleh json.loads(), tanpa karakter khusus seperti \n, blok kode, atau simbol {{ dan }}. 
Format output yang harus dihasilkan adalah sebagai berikut:

[ {{"query": "..."}}, {{"query": "..."}}, ..., {{"query": "..."}} ]

Berikut Abstrak dan Judulnya:

Judul : {title}
Abstrak : {abstract}

Pastikan tidak ada tambahan teks atau penjelasan lainnya di output.'''