function toggleAcquisition() {
    fetch("/toggle_acquisition", { method: "POST" });
}

// Update status text live
function refreshStatus() {
    fetch("/acquisition_status")
        .then(res => res.json())
        .then(data => {
            document.getElementById("statusText").innerText =
                data.running ? "RUNNING" : "STOPPED";
        });
}

setInterval(refreshStatus, 500);