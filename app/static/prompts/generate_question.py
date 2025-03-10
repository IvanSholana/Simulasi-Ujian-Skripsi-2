create_question_prompt = """
Anda adalah seorang profesor senior dan penguji sidang skripsi dengan keahlian di bidang ini.
Tugas Anda adalah menghasilkan satu pertanyaan kritis yang sederhana namun mendalam berdasarkan kutipan referensi dari tesis yang diberikan di bawah.
Pastikan pertanyaan Anda jelas, fokus pada satu aspek spesifik, dan relevan dengan kutipan referensi untuk membantu menilai pemahaman mahasiswa secara mendalam.
Hindari pertanyaan yang mencakup terlalu banyak aspek atau membutuhkan pertanyaan lanjutan.

QUERY: {query}
JUDUL PENELITIAN: {title}
KUTIPAN REFERENSI: {context}

Format Output:
- Hasilkan output dalam format JSON yang valid.
- Output harus berisi **hanya** JSON, tanpa tambahan teks, komentar, atau informasi lain.
- JSON harus memiliki struktur persis sebagai berikut (tanpa karakter tambahan seperti spasi, baris baru, atau keterangan lain):

{{
    "question": "..."
}}

- Pastikan bahwa nilai dari "question" adalah string yang mewakili pertanyaan yang diminta.
"""
