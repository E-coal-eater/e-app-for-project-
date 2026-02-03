let lastPosition = null;

// Get user GPS position
function startGeolocation() {
    if (!navigator.geolocation) {
        console.log("Geolocation not supported");
        return;
    }

    navigator.geolocation.watchPosition(
        position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Send to Flask
            sendPosition(lat, lon);
        },
        error => {
            console.log("GPS error:", error.message);
        },
        {
            enableHighAccuracy: true,
            maximumAge: 1000,
            timeout: 5000
        }
    );
}

// Send GPS to Flask
function sendPosition(lat, lon) {
    fetch("/gps_update", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lon
        })
    });
}

// Start automatically
startGeolocation();