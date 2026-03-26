let lastPosition = null;
let lastTimestamp = null;
let totalDistance = 0;
let startTime = null;
let lastInstantSpeed = 0;
let geoTracking = false;

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

function startGeoTracking() {
    if (geoTracking) return;
    geoTracking = true;

    if (!navigator.geolocation) {
        document.getElementById('geo-error').innerText = 'Geolocation not supported';
        geoTracking = false;
        return;
    }

    startTime = Date.now();

    navigator.geolocation.watchPosition(onGpsPosition, onGpsError, {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 5000
    });

    // Every second: update speeds + send to Flask
    setInterval(() => {
        if (!startTime || !lastPosition) return;

        const elapsedSeconds = (Date.now() - startTime) / 1000;
        const averageSpeed = elapsedSeconds > 0 ? totalDistance / elapsedSeconds : 0;

        document.getElementById('instant-speed').innerText = (lastInstantSpeed * 3.6).toFixed(2) + ' km/h';
        document.getElementById('average-speed').innerText = (averageSpeed * 3.6).toFixed(2) + ' km/h';

        sendGpsToFlask(lastPosition.lat, lastPosition.lon, lastInstantSpeed, averageSpeed);
    }, 1000);
}

function onGpsPosition(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const now = Date.now();

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

    document.getElementById('geo-error').innerText = '';
}

function onGpsError(error) {
    document.getElementById('geo-error').innerText = 'GPS Error: ' + error.message;
}

function sendGpsToFlask(lat, lon, instantSpeed = 0, averageSpeed = 0) {
    fetch("/gps_update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            latitude: lat,
            longitude: lon,
            instant_speed_ms: parseFloat(instantSpeed.toFixed(4)),
            average_speed_ms: parseFloat(averageSpeed.toFixed(4))
        })
    });
}