import pyaudio
import wave
import time
import os
from groq import Groq
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import threading


load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Konfigurasi PyAudio
rate = 44100  # Sample rate
channels = 1  # Mono audio
format = pyaudio.paInt16  # Format audio
frames_per_buffer = 4096  # Ukuran buffer
stream = None
p = None
frames = []
last_output_filename = None
recording = False

# Inisialisasi Groq Client
client = Groq(api_key=GROQ_API_KEY)

class Utils:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)  # Untuk menjalankan proses transkripsi secara paralel

    def read_txt_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print("Error: File not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def simpan_hasil_transkripsi(self, teks, nama_file="hasil_transkripsi.txt"):
        try:
            with open(nama_file, "a", encoding="utf-8") as file:
                file.write(teks + "\n")
                print(f"Hasil transkripsi disimpan ke {nama_file}")
        except Exception as e:
            print(f"Terjadi kesalahan saat menyimpan hasil transkripsi: {e}")

    def bersihkan_transkripsi(self, nama_file="hasil_transkripsi.txt"):
        try:
            with open(nama_file, "w", encoding="utf-8") as file:  # "w" untuk mengosongkan file
                pass  # Tidak perlu menulis string kosong
            print(f"Hasil transkripsi dibersihkan.")
            return True  # Menandakan berhasil
        except Exception as e:
            print(f"Terjadi kesalahan saat membersihkan hasil transkripsi: {e}")
            return False  # Menandakan gagal

    # Fungsi untuk melakukan transkripsi secara asynchronous
    def transkripsi_audio(self, output_filename):
        with open(output_filename, "rb") as file:
            try:
                transcription = client.audio.transcriptions.create(
                    file=(output_filename, file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                )

                if hasattr(transcription, 'text'):
                    self.simpan_hasil_transkripsi(transcription.text)
                else:
                    print(f"Tidak ada teks yang terdeteksi dalam {output_filename}")
            except Exception as e:
                print(f"Terjadi kesalahan saat menggunakan Whisper: {e}")

    def start_recording(self, interval=20):
        global stream, p, frames, last_output_filename, recording

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True,
                        frames_per_buffer=frames_per_buffer)

        print("Merekam...")
        recording = True
        start_time = time.time()

        try:
            while recording:
                data = stream.read(frames_per_buffer)
                frames.append(data)

                if time.time() - start_time >= interval:
                    output_filename = f"output_{int(time.time())}.wav"

                    # Hapus file lama jika ada
                    if last_output_filename and os.path.exists(last_output_filename):
                        os.remove(last_output_filename)
                        print(f"File lama {last_output_filename} telah dihapus.")

                    # Simpan audio ke file WAV
                    with wave.open(output_filename, 'wb') as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(p.get_sample_size(format))
                        wf.setframerate(rate)
                        wf.writeframes(b''.join(frames))

                    last_output_filename = output_filename

                    # Jalankan transkripsi di thread terpisah
                    self.executor.submit(self.transkripsi_audio, output_filename)

                    # Reset frames dan waktu
                    frames = []
                    start_time = time.time()

        except KeyboardInterrupt:
            print("Perekaman dihentikan.")

    def _stop(self):
            global stream, p
            if stream:
                stream.stop_stream()
                stream.close()
                stream = None
            if p:
                p.terminate()
                p = None
            print("Perekaman selesai.")

    def stop_recording(self):
        global stream, p, recording
        print("Menghentikan perekaman...")
        recording = False  # Set flag untuk menghentikan loop di thread utama
        # Jalankan dalam thread baru agar Flask tidak terhenti
        threading.Thread(target=self._stop, daemon=True).start()

    
    
