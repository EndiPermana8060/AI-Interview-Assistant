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

// Fungsi untuk membaca konten file txt setiap beberapa detik
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

// Refresh isi file txt setiap 5 detik
setInterval(fetchFileContent, 5000);