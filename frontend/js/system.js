async function loadSystemStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        document.getElementById('sys-backend').innerText = data.backend;
        document.getElementById('sys-db').innerText = data.database;
        document.getElementById('sys-ml').innerText = data.ml_model;
        document.getElementById('sys-mode').innerText = data.mode;
        
        const ardEl = document.getElementById('sys-arduino');
        ardEl.innerText = data.arduino;
        if(data.arduino === "CONNECTED") {
            ardEl.className = "card-value status-text NORMAL";
        } else {
            ardEl.className = "card-value status-text WARNING";
        }
        
    } catch (e) {
        console.error("Error loading system status:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadSystemStatus();
    setInterval(loadSystemStatus, 5000);
});
