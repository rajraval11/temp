let tempChart;

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('tempChart').getContext('2d');
    tempChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Actual Temperature (°C)',
                data: [],
                borderColor: '#0ea5e9',
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }, {
                label: 'Predicted Temp (°C)',
                data: [],
                borderColor: '#f59e0b',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                tension: 0.4,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: 20,
                    suggestedMax: 50,
                    grid: { color: document.body.classList.contains('dark-mode') ? '#334155' : '#f1f5f9' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function updateChartTheme() {
    if(!tempChart) return;
    const isDark = document.body.classList.contains('dark-mode');
    tempChart.options.scales.y.grid.color = isDark ? '#27272a' : '#f1f5f9';
    Chart.defaults.color = isDark ? '#a1a1aa' : '#64748b';
    tempChart.update();
}

// Polling and API fetch
async function fetchData() {
    try {
        const [latestRes, historyRes, statusRes, analyticsRes, alertsRes] = await Promise.all([
            fetch('/api/latest').catch(()=>null),
            fetch('/api/history').catch(()=>null),
            fetch('/api/status').catch(()=>null),
            fetch('/api/analytics').catch(()=>null),
            fetch('/api/alerts').catch(()=>null)
        ]);

        if (latestRes && latestRes.ok) updateDashboard(await latestRes.json());
        if (historyRes && historyRes.ok) updateHistory(await historyRes.json());
        if (statusRes && statusRes.ok) updateStatus(await statusRes.json());
        if (analyticsRes && analyticsRes.ok) updateAnalytics(await analyticsRes.json());
        if (alertsRes && alertsRes.ok) updateAlerts(await alertsRes.json());
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function updateDashboard(data) {
    if (data.length === 0) return;
    const latest = data[data.length - 1];
    
    document.getElementById('current-temp').innerText = latest.temperature.toFixed(1);
    
    if (latest.prediction !== null) {
        document.getElementById('predicted-temp').innerText = latest.prediction.toFixed(1);
    } else {
        document.getElementById('predicted-temp').innerText = "--";
    }
    
    const statusEl = document.getElementById('system-status');
    statusEl.innerText = latest.status;
    statusEl.className = 'card-value status-text ' + (latest.status === 'HIGH RISK' ? 'HIGH' : latest.status);
    
    if (data.length > 1) {
        const prev = data[data.length - 2];
        const diff = latest.temperature - prev.temperature;
        const trendEl = document.getElementById('temp-trend');
        if (diff > 0.5) trendEl.innerText = "↗ Increasing";
        else if (diff < -0.5) trendEl.innerText = "↘ Decreasing";
        else trendEl.innerText = "→ Stable";
    }

    let risk = 0;
    let health = 100;
    if (latest.status === 'WARNING') {
        risk = 45; health = 80;
    } else if (latest.status === 'HIGH RISK') {
        risk = 85; health = 35;
    }
    
    document.getElementById('ai-risk').innerText = risk + '%';
    document.getElementById('ai-risk-desc').innerText = 'Risk Level: ' + (latest.status === 'NORMAL' ? 'Low Risk' : (latest.status === 'WARNING' ? 'Medium Risk' : 'High Risk'));
    
    document.getElementById('machine-health').innerText = health + '%';
    document.getElementById('machine-health-desc').innerText = 'Condition: ' + (health > 50 ? 'Good' : 'Needs Maintenance');

    const predBox = document.getElementById('pred-box');
    const predText = document.getElementById('pred-text');
    const predDesc = document.getElementById('pred-desc');
    
    if (latest.status === 'NORMAL') {
        predBox.className = 'pred-box';
        predText.innerText = "No Failure Predicted";
        predDesc.innerText = "The AI system indicates that the machine is operating normally.";
    } else if (latest.status === 'WARNING') {
        predBox.className = 'pred-box warning';
        predText.innerText = "Warning Detected";
        predDesc.innerText = "The AI system predicts temperature rising to warning levels soon.";
    } else {
        predBox.className = 'pred-box danger';
        predText.innerText = "Anomaly Detected";
        predDesc.innerText = "Critical temperature spike predicted! Action required immediately.";
    }

    const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
    const temps = data.map(d => d.temperature);
    // The prediction at index i-1 was made for temperature at index i.
    const preds = data.map((d, i) => i > 0 ? data[i-1].prediction : null);

    // Add one future point for the newest prediction
    if (data.length > 0) {
        labels.push("Next");
        temps.push(null);
        preds.push(data[data.length - 1].prediction);
    }

    tempChart.data.labels = labels;
    tempChart.data.datasets[0].data = temps;
    tempChart.data.datasets[1].data = preds;
    tempChart.update();
}

function updateStatus(data) {
    // Mode dropdown
    document.getElementById('mode-selector').value = data.mode;
    document.getElementById('sim-scenario').value = data.simulator_scenario;
    
    // Buttons state
    const btnStart = document.getElementById('btn-start-sim');
    const simTag = document.getElementById('sim-status-tag');
    if (data.simulator_running) {
        btnStart.innerText = "● Running";
        btnStart.classList.add('running');
        simTag.innerText = "● Simulator Running";
        simTag.classList.add('active');
    } else {
        btnStart.innerText = "▶ Start";
        btnStart.classList.remove('running');
        simTag.innerText = "○ Simulator Stopped";
        simTag.classList.remove('active');
    }

    // System info tab
    document.getElementById('sys-backend').innerText = data.backend;
    document.getElementById('sys-db').innerText = data.database;
    document.getElementById('sys-ml').innerText = data.ml_model;
    document.getElementById('sys-mode').innerText = data.mode;
    
    const ardEl = document.getElementById('sys-arduino');
    ardEl.innerText = data.arduino;
    if (data.mode === 'HARDWARE' && data.arduino !== 'CONNECTED') {
        ardEl.className = 'card-value status-text HIGH';
        ardEl.innerText = 'NOT CONNECTED';
    } else {
        ardEl.className = 'card-value';
    }
}

function updateAnalytics(data) {
    document.getElementById('analytics-count').innerText = data.count;
    document.getElementById('analytics-avg-t').innerText = data.avg_temperature;
    document.getElementById('analytics-max-t').innerText = data.max_temperature;
    document.getElementById('analytics-avg-p').innerText = data.avg_prediction;
    document.getElementById('analytics-warn').innerText = data.warnings;
    document.getElementById('analytics-high').innerText = data.high_risks;
}

function updateAlerts(data) {
    const badge = document.getElementById('alert-badge');
    badge.innerText = data.length;
    
    const container = document.getElementById('alerts-container');
    container.innerHTML = '';
    
    if (data.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">No alerts found.</p>';
        return;
    }
    
    data.forEach(item => {
        const div = document.createElement('div');
        div.className = `alert-item ${item.status}`;
        div.innerHTML = `
            <div class="alert-header">
                <span>${item.status}</span>
                <span>${new Date(item.timestamp).toLocaleString()}</span>
            </div>
            <div class="alert-body">
                Current: <b>${item.temperature.toFixed(1)}°C</b> | 
                Predicted: <b>${item.prediction ? item.prediction.toFixed(1) : '--'}°C</b>
            </div>
        `;
        container.appendChild(div);
    });
}

function updateHistory(data) {
    const tbody = document.getElementById('history-tbody');
    tbody.innerHTML = '';
    data.forEach((row, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${row.timestamp}</td>
            <td>${row.temperature.toFixed(2)}</td>
            <td>${row.prediction ? row.prediction.toFixed(2) : '--'}</td>
            <td><span class="status-text ${row.status === 'HIGH RISK' ? 'HIGH' : row.status}">${row.status}</span></td>
            <td>${row.source}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Navigation and Theme
document.addEventListener('DOMContentLoaded', () => {
    // Theme setup
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('theme-toggle').innerText = '☀️ Light';
    }
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const isDark = document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        document.getElementById('theme-toggle').innerText = isDark ? '☀️ Light' : '🌙 Dark';
        updateChartTheme();
    });

    // Navigation setup
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.view-section');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('data-target');
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            sections.forEach(s => {
                s.style.display = s.id === target ? 'block' : 'none';
            });
            
            if(target === 'view-dashboard') {
                pageTitle.innerText = "Machine Overview";
                pageSubtitle.innerText = "Real-time monitoring and predictive analysis";
            } else if(target === 'view-analytics') {
                pageTitle.innerText = "Analytics";
                pageSubtitle.innerText = "Overall machine data";
            } else if(target === 'view-alerts') {
                pageTitle.innerText = "System Alerts";
                pageSubtitle.innerText = "Warnings and anomalies";
            } else if(target === 'view-history') {
                pageTitle.innerText = "Historical Readings";
                pageSubtitle.innerText = "Recent machine sensor data";
            } else if(target === 'view-system') {
                pageTitle.innerText = "System Information";
                pageSubtitle.innerText = "Backend, Database, and ML status";
            }
        });
    });

    // Start/Stop buttons
    document.getElementById('btn-start-sim').addEventListener('click', async () => {
        await fetch('/api/simulation/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({scenario: document.getElementById('sim-scenario').value})
        });
        fetchData();
    });

    document.getElementById('btn-stop-sim').addEventListener('click', async () => {
        await fetch('/api/simulation/stop', { method: 'POST' });
        fetchData();
    });

    // Dropdowns
    document.getElementById('sim-scenario').addEventListener('change', async (e) => {
        await fetch('/api/simulation/scenario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({scenario: e.target.value})
        });
    });

    document.getElementById('mode-selector').addEventListener('change', async (e) => {
        await fetch('/api/mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mode: e.target.value})
        });
    });

    setInterval(() => {
        document.getElementById('system-time').innerText = new Date().toLocaleString();
    }, 1000);

    initChart();
    updateChartTheme();
    fetchData();
    setInterval(fetchData, 2000);
});
