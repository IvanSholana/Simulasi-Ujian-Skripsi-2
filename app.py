from flask import Flask, request, redirect, url_for, render_template, jsonify
import logging
from app.utils.ai_agent.llm_agent import LLM_Agent
import os
import json
from app.utils.ai_agent.llm_instance import LLMInstance
from app.static.prompts.evaluation_answer import evaluation_answer_prompt

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# app = Flask(__name__)
app = Flask(__name__, static_folder='app/static') # Use this if you rename the static folder

app.config['UPLOAD_FOLDER'] = 'app/static/pdf'  # Direktori penyimpanan PDF
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Batas ukuran file 16MB

# Pastikan direktori upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Route untuk halaman unggah PDF
@app.route('/')
def index():
    return render_template('upload.html')

filepath = None
llm_agent  = None

# Route untuk menangani unggah PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Tidak ada file yang diunggah', 400
    file = request.files['file']
    if file.filename == '':
        return 'Tidak ada file yang dipilih', 400
    if file and file.filename.endswith('.pdf'):
        global filepath
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('simulation')) # Redirect ke halaman simulasi
    return 'File harus berformat PDF', 400

# Route untuk menyimpan transkripsi
@app.route('/save_transcription', methods=['POST'])
def save_transcription():
    """Menyimpan transkripsi jawaban siswa ke file JSON."""
    data = request.get_json()
    if not data or 'student_answer' not in data:
        logger.error("Invalid request data: Missing 'student_answer'")
        return jsonify({"error": "Missing 'student_answer' key"}), 400
    
    student_answer = data['student_answer']
    file_path = "transcriptions/student_answer.json"
    
    # Pastikan folder ada
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        logger.info(f"Membuat direktori: {folder_path}")
        os.makedirs(folder_path)
    
    # Baca data yang ada
    existing_data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
            if not isinstance(existing_data, list):
                logger.warning("Data bukan list, diinisialisasi ulang")
                existing_data = []
        except json.JSONDecodeError:
            logger.warning("File JSON rusak, diinisialisasi ulang")
            existing_data = []
    
    # Tambahkan transkripsi baru
    existing_data.append({"student_answer": student_answer})
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)
        logger.info("Transkripsi berhasil disimpan")
        return jsonify({"message": "Transcription saved"}), 200
    except Exception as e:
        logger.error(f"Gagal menyimpan transkripsi: {str(e)}")
        return jsonify({"error": "Failed to save transcription"}), 500

@app.route('/start_simulation')
def start_simulation():
    transcript_file = "transcriptions/student_answer.json"
    
    try:
        # Memastikan file JSON ada sebelum dibuka
        if not os.path.exists(transcript_file):
            return jsonify({"error": "Transcription file not found"}), 404

        # Baca file JSON
        with open(transcript_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        logging.info(f"Received student_answer: {data}")
        # Validasi data JSON dan pastikan ada student_answer
        valid_transcriptions = [item for item in data if item.get('student_answer')]
        
        logging.info(f"Received valid student_answer: {valid_transcriptions}")
        if not valid_transcriptions:
            return jsonify({"error": "No valid transcription found"}), 400

        # Ambil item terbaru
        latest_transcription = valid_transcriptions[-1]
        logging.info(f"Received latest student_answer: {latest_transcription}")
        
        latest_answer = latest_transcription['student_answer']
        
        return redirect(url_for('evaluation_answer', latest_answer=latest_answer))

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        print(f'{str(e)}')
        return redirect(url_for('simulation'))
    
    except Exception as e:
        print(f'{str(e)}')
        return redirect(url_for('simulation'))
  
# Route untuk halaman simulasi ujian
@app.route('/simulation')
def simulation():    
    
    global filepath
    global llm_agent
    llm_agent = LLM_Agent(document_path=filepath)
    
    global current_question
    current_question = llm_agent.question
    
    audio_url = llm_agent.create_question()
    audio_url = audio_url.replace('app/', '')  # Hapus 'app/'
    audio_url = audio_url.replace('static/', '')  # Hapus 'static/'
    
    print(f"Audio Path = {audio_url}")
    return render_template('simulation.html',audio_url=audio_url)

@app.route('/evaluation_answer')
def evaluation_answer():
    
    global llm_agent
    
    print("Start Evaluating")
    latest_answer = request.args.get('latest_answer')
    
    # Evaluasi jawaban menggunakan agent
    result = llm_agent.evaluation_answer(student_answer=latest_answer)
    
    print(f'Evaluation result : {result}')

    if result.get('quality_answer') == 'cukup':
        print("\n\nJAWABAN MAHASISWA CUKUP MAKA MARI BUAT PERTANYAAN BARU!\n\n")
        logging.info("Start simulation route accessed")
        return redirect(url_for('simulation'))
    else:
        print("MAHASISWA TOLOL, EVALUASI DULU!")
        logging.info("Evaluation simulation route accessed")

        # Memulai simulasi berdasarkan hasil evaluasi
        audio_url = result.get('audio_url')
        audio_url = audio_url.replace('app/', '')  # Hapus 'app/'
        audio_url = audio_url.replace('static/', '')  # Hapus 'static/'
    
        # Render template dengan nama file audio
        return render_template('simulation.html', audio_url=audio_url)
    
if __name__ == '__main__':
    app.run(debug=True)