function refreshDB() {
    fetch("/db_data")
        .then(res => res.json())
        .then(data => {

            // ----- VELOS -----
            let velosTable = document.getElementById("velosTable");
            velosTable.innerHTML = `<tr>
                <th>ID</th>
                <th>Modèle</th>
            </tr>`;
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
                <th>Temps</th>
                <th>Vitesse Moyenne du Parcour</th>
            </tr>`;
            data.parcours.forEach(p => {
                parcoursTable.innerHTML += `<tr>
                    <td>${p.id}</td>
                    <td>${p.id_velo ?? '-'}</td>
                    <td>${p.temps ?? '-'}</td>
                    <td>${p.vitesse_moyenne_parcours ?? '-'}</td>
                </tr>`;
            });

            // ----- POINTS -----
            let pointsTable = document.getElementById("pointsTable");
            pointsTable.innerHTML = `<tr>
                <th>ID</th>
                <th>ID Parcours</th>
                <th>Chronomètre</th>
                <th>Batterie</th>
                <th>Position</th>
                <th>Distance</th>
                <th>Vitesse Instantanée</th>
                <th>Vitesse Moyenne</th>
            </tr>`;
            data.points.forEach(pt => {
                pointsTable.innerHTML += `<tr>
                    <td>${pt.id}</td>
                    <td>${pt.id_parcours}</td>
                    <td>${pt.chrono ?? '-'}</td>
                    <td>${pt.battery ?? '-'}</td>
                    <td>${pt.position ?? '-'}</td>
                    <td>${pt.distance ?? '-'}</td>
                    <td>${pt.instant_speed_ms ?? '-'}</td>
                    <td>${pt.average_speed_ms ?? '-'}</td>
                </tr>`;
            });

        })
        .catch(err => console.log("DB refresh error:", err));
}

// first load
refreshDB();

// refresh every second
setInterval(refreshDB, 1000);