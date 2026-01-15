function refreshDB() {
    fetch("/db_data")
        .then(res => res.json())
        .then(data => {

            // ----- VELOS -----
            let velosTable = document.getElementById("velosTable");
            velosTable.innerHTML = `<tr><th>ID</th><th>Modèle</th></tr>`;
            data.velos.forEach(v => {
                velosTable.innerHTML += `<tr><td>${v.id}</td><td>${v.modele}</td></tr>`;
            });

            // ----- PARCOURS -----
            let parcoursTable = document.getElementById("parcoursTable");
            parcoursTable.innerHTML = `<tr><th>ID</th><th>ID Vélo</th><th>Temps</th></tr>`;
            data.parcours.forEach(p => {
                parcoursTable.innerHTML += `<tr><td>${p.id}</td><td>${p.id_velo ?? '-'}</td><td>${p.temps ?? '-'}</td></tr>`;
            });

            // ----- POINTS -----
            let pointsTable = document.getElementById("pointsTable");
            pointsTable.innerHTML = `<tr><th>ID</th><th>ID Parcours</th><th>Temps</th><th>Batterie</th></tr>`;
            data.points.forEach(pt => {
                pointsTable.innerHTML += `<tr><td>${pt.id}</td><td>${pt.id_parcours}</td><td>${pt.temps}</td><td>${pt.battery ?? '-'}</td></tr>`;
            });

        })
        .catch(err => console.log("DB refresh error:", err));
}

// first load
refreshDB();

// refresh every second
setInterval(refreshDB, 1000);