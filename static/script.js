// Update the time in the status bar
function updateTime() {
    const timeElement = document.getElementById('time');
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    timeElement.innerText = timeString;
}

// Update the current application name in the status bar
function updateAppName(appName) {
    const appNameElement = document.getElementById('app-name');
    appNameElement.innerText = `Application: ${appName}`;
}

// Graph for System Metrics
const ctx = document.getElementById('metricsGraph').getContext('2d');
const metricsChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time points
        datasets: [
            { label: 'CPU Usage', data: [], borderColor: 'red', fill: false },
            { label: 'Memory Usage', data: [], borderColor: 'blue', fill: false },
            { label: 'Disk Usage', data: [], borderColor: 'green', fill: false },
        ],
    },
    options: {
        responsive: true,
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: '%' }, min: 0, max: 100 },
        },
    },
});

// Update Graph Data Periodically
async function fetchAndUpdateGraph() {
    try {
        const response = await fetch('/metrics');
        const data = await response.json();
        const now = new Date().toLocaleTimeString();

        metricsChart.data.labels.push(now);
        metricsChart.data.datasets[0].data.push(data.cpu_usage);
        metricsChart.data.datasets[1].data.push(data.memory_usage);
        metricsChart.data.datasets[2].data.push(data.disk_usage);

        if (metricsChart.data.labels.length > 10) {
            metricsChart.data.labels.shift(); // Keep max 10 points
            metricsChart.data.datasets.forEach((dataset) => dataset.data.shift());
        }
        metricsChart.update();

        // Update text values for the metrics
        document.getElementById('cpu').innerText = `CPU: ${data.cpu_usage}%`;
        document.getElementById('memory').innerText = `Memory: ${data.memory_usage}%`;
        document.getElementById('disk').innerText = `Disk: ${data.disk_usage}%`;

    } catch (error) {
        console.error('Error updating graph:', error);
    }
}

// Periodically Update Graph
setInterval(fetchAndUpdateGraph, 2000);

// Periodically Update Time
setInterval(updateTime, 1000);

// Launch application and update the status bar
function launchApp(appKey) {
    fetch(`/launch/${appKey}`)
        .then(response => response.text())
        .then(message => {
            alert(message);
            updateAppName(appKey);  // Update the app name in the status bar
        })
        .catch(error => console.error('Error launching app:', error));
}
