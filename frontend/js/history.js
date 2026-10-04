async function loadHistory() {
    try {
        const res = await fetch('/api/latest');
        const data = await res.json();
        
        const tbody = document.getElementById('history-tbody');
        tbody.innerHTML = '';
        
        const reversed = [...data].reverse();
        
        reversed.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.id}</td>
                <td>${new Date(row.timestamp).toLocaleString()}</td>
                <td>Machine 01</td>
                <td>${row.temperature.toFixed(2)}</td>
                <td>${row.prediction ? row.prediction.toFixed(2) : '--'}</td>
                <td class="status-text ${row.status === 'HIGH RISK' ? 'HIGH' : row.status}">${row.status}</td>
                <td>${row.source}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading history:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setInterval(loadHistory, 5000);
});
