async function fetchMetrics() {
    try {
        const response = await fetch('/metrics');
        const data = await response.json();
        const metricsDiv = document.getElementById('metrics');
        metricsDiv.innerHTML = `
            <p>CPU Usage: ${data.cpu_usage}%</p>
            <p>Memory Usage: ${data.memory_usage}%</p>
            <p>Disk Usage: ${data.disk_usage}%</p>
        `;
    } catch (error) {
        console.error('Error fetching metrics:', error);
    }
}

// Refresh metrics every 2 seconds
setInterval(fetchMetrics, 2000);

function launchApp(appKey) {
    fetch(`/launch/${appKey}`)
        .then(response => response.text())
        .then(message => alert(message))
        .catch(error => console.error('Error launching app:', error));
}
