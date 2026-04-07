let selectedParcoursId = null;
let pointsInterval = null;

function refreshDB() {
    fetch("/db_data")
        .then(res => res.json())
        .then(data => {

            // ----- VELOS -----
            let velosTable = document.getElementById("velosTable");
            velosTable.innerHTML = `<tr><th>ID</th><th>Modèle</th></tr>`;
            data.velos.forEach(v => {
                velosTable.innerHTML += `<tr>
                    <td>${v.id}</td>
                    <td>${v.modele}</td>
                </tr>`;
            });

            // ----- PARCOURS -----
            let parcoursTable = document.getElementById("parcoursTable");
            parcoursTable.innerHTML = `<tr>
                <th>ID</th>
                <th>ID Vélo</th>
                <th>Temps (s)</th>
                <th>Vitesse Moyenne</th>
                <th></th>
            </tr>`;
            data.parcours.forEach(p => {
                const isActive = selectedParcoursId === p.id;
                parcoursTable.innerHTML += `<tr class="${isActive ? 'row-selected' : ''}">
                    <td>${p.id}</td>
                    <td>${p.id_velo ?? '-'}</td>
                    <td>${p.temps ?? '-'}</td>
                    <td>${p.vitesse_moyenne_parcours != null ? p.vitesse_moyenne_parcours.toFixed(2) + ' m/s' : '-'}</td>
                    <td><button onclick="showPoints(${p.id})">${isActive ? '● Actif' : 'Voir'}</button></td>
                </tr>`;
            });
        })
        .catch(err => console.error("DB refresh error:", err));
}

function showPoints(parcoursId) {
    selectedParcoursId = parcoursId;
    document.getElementById("pointsBlock").style.display = "block";
    document.getElementById("selectedParcours").innerText = "#" + parcoursId;

    // Load immediately
    loadPoints(parcoursId);

    // Clear any old interval and start a fresh one
    if (pointsInterval) clearInterval(pointsInterval);
    pointsInterval = setInterval(() => {
        if (selectedParcoursId !== null) loadPoints(selectedParcoursId);
    }, 1000);
}

function closePoints() {
    selectedParcoursId = null;
    document.getElementById("pointsBlock").style.display = "none";
    if (pointsInterval) {
        clearInterval(pointsInterval);
        pointsInterval = null;
    }
}

function loadPoints(parcoursId) {
    fetch(`/parcours/${parcoursId}/points`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("pointsCount").innerText =
                `${data.count} point(s) enregistré(s)`;

            let table = document.getElementById("pointsTable");
            table.innerHTML = `<tr>
                <th>ID</th>
                <th>Chrono</th>
                <th>Batterie</th>
                <th>Position</th>
                <th>Distance (m)</th>
                <th>Vit. inst. (m/s)</th>
                <th>Vit. moy. (m/s)</th>
            </tr>`;

            if (data.count === 0) {
                table.innerHTML += `<tr><td colspan="7" style="text-align:center; color:#888;">Aucun point enregistré</td></tr>`;
                return;
            }

            // Show newest points first
            [...data.points].reverse().forEach(pt => {
                table.innerHTML += `<tr>
                    <td>${pt.id}</td>
                    <td>${pt.chrono != null ? pt.chrono + 's' : '-'}</td>
                    <td>${pt.battery ?? '-'}</td>
                    <td>${pt.position ?? '-'}</td>
                    <td>${pt.distance != null ? pt.distance.toFixed(2) : '-'}</td>
                    <td>${pt.vitesse != null ? pt.vitesse.toFixed(3) : '-'}</td>
                    <td>${pt.vitesse_moyenne != null ? pt.vitesse_moyenne.toFixed(3) : '-'}</td>
                </tr>`;
            });
        })
        .catch(err => console.error("Points load error:", err));
}

// DB refreshes every 2s (no need for 1s since points have their own interval)
refreshDB();
setInterval(refreshDB, 2000);