import os
import azure.cognitiveservices.speech as speechsdk

class AudioManagement():
    static_folder = os.path.join("app", "static")
    def __init__(self):
        # Validasi environment variables
        api_key = os.getenv("AZURE_API_KEY")
        region = os.getenv("AZURE_REGION")
        if not api_key or not region:
            raise ValueError("AZURE_API_KEY atau region tidak ditemukan dalam environment variables.")
        
        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        self.speech_config.speech_recognition_language = "id-ID"  # Bahasa Indonesia
        self.speech_config.speech_synthesis_voice_name = "id-ID-ArdiNeural"  # Suara Neural Indonesia (pria)
        
        # Buat synthesizer sekali
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
        
        # Validasi folder
        if not os.path.exists(self.static_folder):
            os.makedirs(self.static_folder)

    def text_to_speech(self, text, file_name):
        file_path = os.path.join(self.static_folder, file_name)
        synthesis_result = self.synthesizer.speak_text_async(text).get()
        
        if synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Sukses menyintesis teks menjadi suara.")
            # Simpan file audio
            with open(file_path, 'wb') as audio_file:
                audio_file.write(synthesis_result.audio_data)
            audio_path = audio_file.name  # Di mana file_object adalah objek _io.BufferedWriter
            valid_audio_path = os.path.normpath(audio_path)
            audio_url_path = valid_audio_path.replace("\\", "/")
            return audio_url_path
        elif synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = synthesis_result.cancellation_details
            print(f"Gagal mensintesis suara. Alasan: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Detail Error: {cancellation_details.error_details}")
        else:
            print("GAGAL MENSINTESIS SUARA!")