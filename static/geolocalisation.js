let lastPosition = null;
let lastTimestamp = null;
let totalDistance = 0;
let startTime = null;
let speedHistory = [];

// Calculate distance between two GPS points using Haversine formula (in meters)
function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth radius in meters
    const toRad = deg => deg * (Math.PI / 180);

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) ** 2;

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// Get user GPS position
function startGeolocation() {
    if (!navigator.geolocation) {
        console.log("Geolocation not supported");
        return;
    }

    startTime = Date.now();

    navigator.geolocation.watchPosition(
        position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const now = Date.now();

            let instantSpeed = 0; // m/s

            if (lastPosition && lastTimestamp) {
                const distance = haversineDistance(
                    lastPosition.lat, lastPosition.lon,
                    lat, lon
                );
                const timeDelta = (now - lastTimestamp) / 1000; // seconds

                if (timeDelta > 0) {
                    instantSpeed = distance / timeDelta; // m/s
                    totalDistance += distance;
                    speedHistory.push(instantSpeed);
                }
            }

            const elapsedSeconds = (now - startTime) / 1000;
            const averageSpeed = elapsedSeconds > 0
                ? totalDistance / elapsedSeconds
                : 0;

            lastPosition = { lat, lon };
            lastTimestamp = now;

            // Send to Flask
            sendPosition(lat, lon, instantSpeed, averageSpeed);

            console.log(`Instant speed: ${(instantSpeed * 3.6).toFixed(2)} km/h`);
            console.log(`Average speed: ${(averageSpeed * 3.6).toFixed(2)} km/h`);
        },
        error => {
            console.log("GPS error:", error.message);
        },
        {
            enableHighAccuracy: true,
            maximumAge: 0,      // Always get fresh position
            timeout: 5000
        }
    );

    // Force a measurement update every second even if GPS hasn't changed
    setInterval(() => {
        if (!lastPosition) return;

        const elapsedSeconds = (Date.now() - startTime) / 1000;
        const averageSpeed = elapsedSeconds > 0
            ? totalDistance / elapsedSeconds
            : 0;

        const instantSpeed = speedHistory.length > 0
            ? speedHistory[speedHistory.length - 1]
            : 0;

        console.log(`[1s tick] Instant: ${(instantSpeed * 3.6).toFixed(2)} km/h | Average: ${(averageSpeed * 3.6).toFixed(2)} km/h`);

        sendPosition(lastPosition.lat, lastPosition.lon, instantSpeed, averageSpeed);
    }, 1000);
}

// Send GPS + speeds to Flask
function sendPosition(lat, lon, instantSpeed = 0, averageSpeed = 0) {
    fetch("/gps_update", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lon,
            instant_speed_ms: parseFloat(instantSpeed.toFixed(4)),
            instant_speed_kmh: parseFloat((instantSpeed * 3.6).toFixed(4)),
            average_speed_ms: parseFloat(averageSpeed.toFixed(4)),
            average_speed_kmh: parseFloat((averageSpeed * 3.6).toFixed(4))
        })
    });
}

// Start automatically
startGeolocation();