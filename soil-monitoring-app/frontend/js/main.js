async function fetchJSON(url) {
    const res = await fetch(url);
    return res.json();
}

async function updateDashboard() {
    try {
        const moisture = await fetchJSON("http://127.0.0.1:8000/sensor/moisture");
        const humidity = await fetchJSON("http://127.0.0.1:8000/sensor/humidity");
        const temperature = await fetchJSON("http://127.0.0.1:8000/sensor/temperature");
        const ldr = await fetchJSON("http://127.0.0.1:8000/sensor/ldr");
        const water = await fetchJSON("http://127.0.0.1:8000/sensor/water");
        const mode = await fetchJSON("http://127.0.0.1:8000/switch/mode");

        document.getElementById("moistureValue").innerText = moisture.value + " %";
        document.getElementById("humidityValue").innerText = humidity.value + " %";
        document.getElementById("temperatureValue").innerText = temperature.value + " °C";
        document.getElementById("ldrValue").innerText = ldr.value + " ohm";
        document.getElementById("waterStatus").innerText = water.status ? "Water Needed" : "OK";
        document.getElementById("modeStatus").innerText = mode.mode;

    } catch (err) {
        console.error("Error fetching sensor data:", err);
    }
}

// Update every 5 seconds
setInterval(updateDashboard, 5000);
updateDashboard();
