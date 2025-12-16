const BASE_URL = "http://127.0.0.1:8000";

async function getMoisture() {
    return fetch(`${BASE_URL}/sensor/moisture`).then(r => r.json());
}

async function getHumidity() {
    return fetch(`${BASE_URL}/sensor/humidity`).then(r => r.json());
}

async function getTemperature() {
    return fetch(`${BASE_URL}/sensor/temperature`).then(r => r.json());
}

async function getLDR() {
    return fetch(`${BASE_URL}/sensor/ldr`).then(r => r.json());
}

async function getWaterStatus() {
    return fetch(`${BASE_URL}/sensor/water`).then(r => r.json());
}

async function getMode() {
    return fetch(`${BASE_URL}/switch/mode`).then(r => r.json());
}

async function updateMode(mode) {
    return fetch(`${BASE_URL}/switch/mode/${mode}`, { method: "POST" }).then(r => r.json());
}

async function updateManualState(state) {
    return fetch(`${BASE_URL}/switch/manual/${state}`, { method: "POST" }).then(r => r.json());
}
