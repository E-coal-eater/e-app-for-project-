let lastPosition = null;
let lastTimestamp = null;
let totalDistance = 0;
let startTime = null;
let lastInstantSpeed = 0;

function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000;
    const toRad = deg => deg * (Math.PI / 180);
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function getLocation() {
    if (!navigator.geolocation) {
        document.getElementById('error').innerText = 'Geolocation not supported';
        return;
    }

    startTime = Date.now();

    navigator.geolocation.watchPosition(showPosition, showError, {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 5000
    });

    setInterval(() => {
        if (!startTime) return;
        const elapsedSeconds = (Date.now() - startTime) / 1000;
        const averageSpeed = elapsedSeconds > 0 ? totalDistance / elapsedSeconds : 0;
        document.getElementById('instant-speed').innerText = (lastInstantSpeed * 3.6).toFixed(2) + ' km/h';
        document.getElementById('average-speed').innerText = (averageSpeed * 3.6).toFixed(2) + ' km/h';
    }, 1000);
}

function showPosition(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const now = Date.now();

    document.getElementById('latitude').innerText = lat.toFixed(6);
    document.getElementById('longitude').innerText = lon.toFixed(6);
    document.getElementById('heading').innerText = position.coords.heading ? position.coords.heading.toFixed(2) + '°' : 'N/A';
    document.getElementById('error').innerText = '';
    if (lastPosition && lastTimestamp) {
        const distance = haversineDistance(lastPosition.lat, lastPosition.lon, lat, lon);
        const timeDelta = (now - lastTimestamp) / 1000;
        if (timeDelta > 0) {
            lastInstantSpeed = distance / timeDelta;
            totalDistance += distance;
        }
    }

    lastPosition = { lat, lon };
    lastTimestamp = now;
}

function showError(error) {
    document.getElementById('error').innerText = 'Error: ' + error.message;
}