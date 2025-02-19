import pyaudio
import wave
import time
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY  = os.getenv('GROQ_API_KEY')

# Konfigurasi PyAudio
rate = 44100  # Sample rate
channels = 1  # Mono audio
format = pyaudio.paInt16  # Format audio
frames_per_buffer = 1024  # Ukuran buffer
stream = None
p = None
frames = []
last_output_filename = None
recording = False

# Inisialisasi Groq Client
client = Groq(api_key=GROQ_API_KEY)

class Utils:
    def read_txt_file(self, file_path):
        try:
            # Open the file in read mode and read its content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print("Error: File not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    # Fungsi untuk menyimpan hasil transkripsi ke file
    def simpan_hasil_transkripsi(self, teks, nama_file="hasil_transkripsi.txt"):
        try:
            with open(nama_file, "a", encoding="utf-8") as file:
                file.write(teks + "\n")
                print(f"Hasil transkripsi disimpan ke {nama_file}")
        except Exception as e:
            print(f"Terjadi kesalahan saat menyimpan hasil transkripsi: {e}")


    # Fungsi untuk memulai perekaman
    def start_recording(self, interval=10):
        global stream, p, frames, last_output_filename, recording

        # Inisialisasi PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True,
                        frames_per_buffer=frames_per_buffer)

        print("Merekam...")
        recording = True
        start_time = time.time()

        try:
            while recording:
                # Membaca data audio
                data = stream.read(frames_per_buffer)
                frames.append(data)

                # Simpan audio setiap interval
                if time.time() - start_time >= interval:
                    output_filename = f"output_{int(time.time())}.wav"

                    # Hapus file lama jika ada
                    if last_output_filename and os.path.exists(last_output_filename):
                        os.remove(last_output_filename)
                        print(f"File lama {last_output_filename} telah dihapus.")

                    # Simpan file WAV baru
                    with wave.open(output_filename, 'wb') as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(p.get_sample_size(format))
                        wf.setframerate(rate)
                        wf.writeframes(b''.join(frames))

                    last_output_filename = output_filename

                    # Konversi ke teks menggunakan Whisper dari Groq
                    with open(output_filename, "rb") as file:
                        try:
                            transcription = client.audio.transcriptions.create(
                                file=(output_filename, file.read()),
                                model="whisper-large-v3",
                                response_format="verbose_json",
                            )

                            if hasattr(transcription, 'text'):
                                print(transcription.text)
                                self.simpan_hasil_transkripsi(transcription.text)
                            else:
                                print(f"Tidak ada teks yang terdeteksi dalam {output_filename}")
                        except Exception as e:
                            print(f"Terjadi kesalahan saat menggunakan Whisper: {e}")

                    # Reset frames dan waktu
                    frames = []
                    start_time = time.time()

        except KeyboardInterrupt:
            print("Perekaman dihentikan.")


    # Fungsi untuk menghentikan perekaman
    def stop_recording(self):
        global stream, p, recording
        print("Menghentikan perekaman...")
        recording = False

        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()

        print("Perekaman selesai.")