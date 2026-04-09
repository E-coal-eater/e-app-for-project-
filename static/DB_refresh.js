let selectedParcoursId = null;
let pointsInterval = null;

// ---------------- FETCH DB ----------------
async function fetchDB() {
    const res = await fetch("/db_data");
    return await res.json();
}

// ---------------- REFRESH DATABASE ----------------
async function refreshDB() {
    try {
        const data = await fetchDB();

        fillVelos(data.velos);
        fillParcours(data.parcours);

    } catch (err) {
        console.error("DB refresh error:", err);
    }
}

// ---------------- VELOS ----------------
function fillVelos(velos) {
    const table = document.getElementById("velosTable");

    let html = `<tr><th>ID</th><th>Modèle</th></tr>`;

    velos.forEach(v => {
        html += `
            <tr>
                <td>${v.id}</td>
                <td>${v.modele}</td>
            </tr>
        `;
    });

    table.innerHTML = html;
}

// ---------------- PARCOURS ----------------
function fillParcours(parcours) {
    const table = document.getElementById("parcoursTable");

    let html = `<tr>
        <th>ID</th>
        <th>ID Vélo</th>
        <th>Temps (s)</th>
        <th>Vitesse Moyenne</th>
        <th></th>
    </tr>`;

    parcours.forEach(p => {
        const isActive = selectedParcoursId === p.id;

        html += `
            <tr class="${isActive ? 'row-selected' : ''}">
                <td>${p.id}</td>
                <td>${p.id_velo ?? '-'}</td>
                <td>${p.temps ?? '-'}</td>
                <td>${p.vitesse_moyenne_parcours != null 
                    ? p.vitesse_moyenne_parcours.toFixed(2) + ' m/s' 
                    : '-'}</td>
                <td>
                    <button onclick="showPoints(${p.id})">
                        ${isActive ? '● Actif' : 'Voir'}
                    </button>
                </td>
            </tr>
        `;
    });

    table.innerHTML = html;
}

// ---------------- SHOW POINTS ----------------
function showPoints(parcoursId) {
    selectedParcoursId = parcoursId;
    
    refreshDB();

    document.getElementById("pointsBlock").style.display = "block";
    document.getElementById("selectedParcours").innerText = "#" + parcoursId;

    loadPoints(parcoursId);

    // Reset interval
    if (pointsInterval) clearInterval(pointsInterval);

    pointsInterval = setInterval(() => {
        if (selectedParcoursId !== null) {
            loadPoints(selectedParcoursId);
        }
    }, 1000);
}

// ---------------- CLOSE POINTS ----------------
function closePoints() {
    selectedParcoursId = null;

    document.getElementById("pointsBlock").style.display = "none";

    if (pointsInterval) {
        clearInterval(pointsInterval);
        pointsInterval = null;
    }

    // refresh UI to remove highlight
    refreshDB();
}

// ---------------- LOAD POINTS ----------------
async function loadPoints(parcoursId) {
    try {
        const res = await fetch(`/parcours/${parcoursId}/points`);
        const data = await res.json();

        document.getElementById("pointsCount").innerText =
            `${data.count} point(s) enregistré(s)`;

        const table = document.getElementById("pointsTable");

        let html = `<tr>
            <th>ID</th>
            <th>Chrono</th>
            <th>Batterie</th>
            <th>Position</th>
            <th>Distance (m)</th>
            <th>Vit. inst. (m/s)</th>
            <th>Vit. moy. (m/s)</th>
        </tr>`;

        if (data.count === 0) {
            html += `<tr>
                <td colspan="7" style="text-align:center; color:#888;">
                    Aucun point enregistré
                </td>
            </tr>`;
        } else {
            [...data.points].reverse().forEach(pt => {
                html += `
                    <tr>
                        <td>${pt.id}</td>
                        <td>${pt.chrono != null ? pt.chrono + 's' : '-'}</td>
                        <td>${pt.battery ?? '-'}</td>
                        <td>${pt.position ?? '-'}</td>
                        <td>${pt.distance != null ? pt.distance.toFixed(2) : '-'}</td>
                        <td>${pt.vitesse != null ? pt.vitesse.toFixed(3) : '-'}</td>
                        <td>${pt.vitesse_moyenne != null ? pt.vitesse_moyenne.toFixed(3) : '-'}</td>
                    </tr>
                `;
            });
        }

        table.innerHTML = html;

    } catch (err) {
        console.error("Points load error:", err);
    }
}

// ---------------- AUTO REFRESH ----------------
refreshDB();
setInterval(refreshDB, 2000);