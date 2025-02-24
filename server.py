from flask import Flask, render_template, jsonify
from utils import Utils
from chatbot import ChatBot
from datetime import datetime
from flask import send_file
import os

app = Flask(__name__)

utility = Utils()
bot = ChatBot()
# Variable kontrol untuk status perekaman
recording_started = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-recording', methods=['POST'])
def start_recording_endpoint():
    global recording_started
    if not recording_started:
        recording_started = True
        # Jalankan perekaman di background
        import threading
        threading.Thread(target=utility.start_recording).start()  # Menjalankan fungsi di thread terpisah
        return jsonify({"message": "Perekaman dimulai"}), 200
    else:
        return jsonify({"message": "Perekaman sudah berjalan"}), 400


@app.route('/stop-recording', methods=['POST'])
def stop_recording_endpoint():
    global recording_started
    if recording_started:
        utility.stop_recording()
        recording_started = False
        return jsonify({"message": "Perekaman dihentikan"}), 200
    else:
        return jsonify({"message": "Tidak ada perekaman yang sedang berjalan"}), 400


@app.route('/read-txt', methods=['GET'])
def read_txt_file():
    try:
        # Nama file yang akan dibaca
        file_path = 'hasil_transkripsi.txt'  # Ganti dengan path file Anda

        # Membaca isi file
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Mengembalikan isi file dalam format JSON
        return jsonify({"content": file_content})

    except FileNotFoundError:
        return jsonify({"content": "File not found"}), 404

    except Exception as e:
        return jsonify({"content": f"Error: {str(e)}"}), 500
    
@app.route('/gen-suggestion', methods=['POST'])
def gen_suggestion():
    # Path to the text file
    file_path = "hasil_transkripsi.txt"  # Ensure correct path format
    try:
        # Read the file content
        content = utility.read_txt_file(file_path)
        # Ensure content is not empty
        if content:
            # Generate suggestions using the bot's generate_suggestion method
            response = bot.generate_suggestion(content)
            return jsonify({'response': response}), 200
        else:
            return "Failed to read file or file is empty.", 400
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/clear-transcription', methods=['POST'])
def clear_transcription():
    # Path ke file hasil transkripsi
    file_path = "hasil_transkripsi.txt"

    try:
        # Panggil fungsi untuk membersihkan transkripsi
        success = utility.bersihkan_transkripsi(file_path)

        if success:
            return jsonify({"message": "Hasil transkripsi sudah dibersihkan."}), 200
        else:
            return jsonify({"message": "Gagal membersihkan hasil transkripsi."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/download-transcription', methods=['GET'])
def download_transcription():
    # Path ke file hasil transkripsi
    file_path = "hasil_transkripsi.txt"

    try:
        # Generate nama file baru berdasarkan tanggal saat ini
        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nama_file_baru = f"hasil_transkripsi_{tanggal_sekarang}.txt"

        # Kirim file ke user untuk diunduh
        return send_file(file_path, as_attachment=True, download_name=nama_file_baru, mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get-validation', methods=['POST'])
def get_validation():
    file_path = "hasil_transkripsi.txt"

    # Pastikan file input ada
    if not os.path.exists(file_path):
        return jsonify({"error": "File hasil transkripsi tidak ditemukan."}), 404

    try:
        # Membaca isi file hasil transkripsi
        with open(file_path, "r", encoding="utf-8") as input_file:
            input_text = input_file.read()

        # Generate validation text menggunakan fungsi bot
        validation_text = bot.generate_validation(input_text)

        # Simpan hasil validasi ke file baru
        output_filename = "validation_output.txt"
        output_filepath = os.path.join(os.path.dirname(file_path), output_filename)

        with open(output_filepath, "w", encoding="utf-8") as output_file:
            output_file.write(validation_text)

        # Membaca ulang file hasil validasi untuk dikirim ke frontend
        with open(output_filepath, "r", encoding="utf-8") as file:
            content = file.read()

        return jsonify({"content": content}), 200

    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500


@app.route('/download-validation', methods=['GET'])
def download_validation():
    # Path ke file hasil transkripsi
    file_path = "validation_output.txt"

    try:
        # Generate nama file baru berdasarkan tanggal saat ini
        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nama_file_baru = f"hasil_validasi_{tanggal_sekarang}.txt"

        # Kirim file ke user untuk diunduh
        return send_file(file_path, as_attachment=True, download_name=nama_file_baru, mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)