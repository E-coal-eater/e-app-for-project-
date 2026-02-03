// Called when the user clicks the Start / Stop Acquisition button
function toggleAcquisition() {
    
    // Send a POST request to Flask to ask for acquisition toggle
    fetch("/toggle_acquisition", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            
            // If Flask answers with an error (ex: no Bluetooth connected)
            if (!data.ok) {
                // Display the error message in red text on the page
                document.getElementById("errorMsg").innerText =
                    "Can't start acquisition: " + data.error;
            } 
            else {
                // If everything is OK, clear any previous error message
                document.getElementById("errorMsg").innerText = "";
            }
        });
}


// This function continuously checks acquisition status from Flask
function refreshStatus() {
    fetch("/acquisition_status")
        .then(res => res.json())
        .then(data => {
            let text;
            if (!data.connected) text = "NO DEVICE";
            else if (data.running) text = "RUNNING";
            else text = "STOPPED";

            document.getElementById("statusText").innerText = text;
        });
}


// Call refreshStatus() every 500 milliseconds (0.5 seconds)
// This keeps the status text updated in real-time without reloading the page
setInterval(refreshStatus, 500);