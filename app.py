from flask import Flask, request, redirect, url_for, render_template
from app.utils.ai_agent.llm_agent import LLM_Agent
import os

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

# Route untuk menangani unggah PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Tidak ada file yang diunggah', 400
    file = request.files['file']
    if file.filename == '':
        return 'Tidak ada file yang dipilih', 400
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        agent = LLM_Agent(document_path=filepath)
        audio_url = agent.create_question()
        # print(audio_url)
        audio_url = audio_url.replace('app/', '')  # Hapus 'app/'
        audio_url = audio_url.replace('static/', '')  # Hapus 'static/'
        return redirect(url_for('simulation', audio_url=audio_url)) # Redirect ke halaman simulasi
    return 'File harus berformat PDF', 400

# Route untuk halaman simulasi ujian
@app.route('/simulation')
def simulation():
    audio_url = request.args.get('audio_url')
    print(f"Audio Path = {audio_url}")
    return render_template('simulation.html',audio_url=audio_url)

if __name__ == '__main__':
    app.run(debug=True)