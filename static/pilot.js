let parcoursRunning = false;

function startParcours() {
    // 1. Tell Flask to create a new parcours row and set current_parcours_id
    fetch("/start_parcours", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (!data.ok) {
                document.getElementById("errorMsg").innerText = "Erreur: " + data.error;
                return;
            }
            parcoursRunning = true;
            document.getElementById("errorMsg").innerText = "";
            document.getElementById("parcoursStatus").innerText = "RUNNING";
            document.getElementById("parcoursButton").innerText = "Stop Parcours";
            document.getElementById("parcoursButton").onclick = stopParcours;

            // 2. Start GPS so points get sent to Flask every second
            startGeoTracking(); // from geolocalisation.js
        });
}

function stopParcours() {
    // Tell Flask to finalize the parcours (temps + vitesse_moyenne)
    fetch("/stop_parcours", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (!data.ok) {
                document.getElementById("errorMsg").innerText = "Erreur: " + data.error;
                return;
            }
            parcoursRunning = false;
            document.getElementById("parcoursStatus").innerText = "STOPPED";
            document.getElementById("parcoursButton").innerText = "Start Parcours";
            document.getElementById("parcoursButton").onclick = startParcours;
        });
}