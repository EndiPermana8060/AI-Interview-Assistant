from flask import Flask, render_template, jsonify
import os
from utils import Utils
from chatbot import ChatBot
from groq import Groq
import pyaudio
import wave
import time

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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)