// Fungsi untuk men-trigger route '/gen-suggestion'
function triggerRoute() {
    fetch('/gen-suggestion', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response-text').value = data.response;
    })
    .catch(error => {
        document.getElementById('response-text').value = 'Error: ' + error;
    });
}

// Fungsi untuk men-trigger route '/start-recording'
function startRecording() {
    fetch('/start-recording', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response-text').value = data.message;
    })
    .catch(error => {
        document.getElementById('response-text').value = 'Error: ' + error;
    });
}

// Fungsi untuk men-trigger route '/stop-recording'
function stopRecording() {
    fetch('/stop-recording', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response-text').value = data.message;
    })
    .catch(error => {
        document.getElementById('response-text').value = 'Error: ' + error;
    });
}


function clearTranscription() {
    fetch('/clear-transcription', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response-text').value = data.message;
        document.getElementById('file-content-display').value = "";
    })
    .catch(error => {
        document.getElementById('response-text').value = 'Error: ' + error;
    });
}
function downloadTranscription() {
    fetch('/download-transcription')
        .then(response => {
            if (!response.ok) {
                throw new Error('Gagal mengunduh file.');
            }
            return response.blob(); // Mengambil file sebagai blob
        })
        .then(blob => {
            // Format tanggal: YYYY-MM-DD_HH-MM-SS
            const now = new Date();
            const timestamp = now.getFullYear() + '-' +
                              String(now.getMonth() + 1).padStart(2, '0') + '-' +
                              String(now.getDate()).padStart(2, '0') + '_' +
                              String(now.getHours()).padStart(2, '0') + '-' +
                              String(now.getMinutes()).padStart(2, '0') + '-' +
                              String(now.getSeconds()).padStart(2, '0');

            // Buat URL blob untuk file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Hasil_transkripsi_${timestamp}.txt`; // Nama file dengan timestamp
            document.body.appendChild(a);
            a.click(); // Klik otomatis untuk mengunduh
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url); // Bersihkan URL blob dari memori
        })
        .catch(error => {
            document.getElementById('response-text').textContent = 'Error: ' + error.message;
        });
}
function downloadValidation() {
    fetch('/download-validation')
        .then(response => {
            if (!response.ok) {
                throw new Error('Gagal mengunduh file.');
            }
            return response.blob(); // Mengambil file sebagai blob
        })
        .then(blob => {
            // Format tanggal: YYYY-MM-DD_HH-MM-SS
            const now = new Date();
            const timestamp = now.getFullYear() + '-' +
                              String(now.getMonth() + 1).padStart(2, '0') + '-' +
                              String(now.getDate()).padStart(2, '0') + '_' +
                              String(now.getHours()).padStart(2, '0') + '-' +
                              String(now.getMinutes()).padStart(2, '0') + '-' +
                              String(now.getSeconds()).padStart(2, '0');

            // Buat URL blob untuk file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Hasil_validasi_${timestamp}.txt`; // Nama file dengan timestamp
            document.body.appendChild(a);
            a.click(); // Klik otomatis untuk mengunduh
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url); // Bersihkan URL blob dari memori
        })
        .catch(error => {
            document.getElementById('response-text').textContent = 'Error: ' + error.message;
        });
}


// Fungsi untuk membaca konten file txt setiap beberapa detik
function getValidation() {
    fetch('/get-validation',{
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response-text').value = data.content;
        })
        .catch(error => {
            document.getElementById('response-text').value = 'Error: ' + error;
        });
}

function genDecision() {
    fetch('/get-decision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())  // Parse response ke JSON
    .then(data => {
        if (data.response) {
            let kecocokan = data.response.kecocokan;
            let kategori = data.response.kategori;
            let penjelasan = data.response.penjelasan; // Ambil penjelasan

            // Format tampilan agar lebih jelas
            document.getElementById('response-text').value = 
                `🔹 Kecocokan dengan JobDesc: ${kecocokan}\n` +
                `🔹 Kategori: ${kategori}\n\n` +
                `📌 Penjelasan:\n${penjelasan}`;
        } else {
            document.getElementById('response-text').value = "⚠️ Error: Response tidak ditemukan.";
        }
    })
    .catch(error => {
        document.getElementById('response-text').value = '⚠️ Error: ' + error;
    });
}



function fetchFileContent() {
    fetch('/read-txt')
        .then(response => response.json())
        .then(data => {
            document.getElementById('file-content-display').value = data.content;
        })
        .catch(error => {
            document.getElementById('file-content-display').value = 'Error: ' + error;
        });
}

// Panggil pertama kali dengan delay 1 detik
setTimeout(() => {
    fetchFileContent();

    // Setelah eksekusi pertama, jalankan setInterval tiap 20 detik
    setInterval(fetchFileContent, 20000);
}, 1000);