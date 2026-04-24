function parseCSV(text) {
    const rows = text.trim().split(/\r?\n/).map(row => row.split(","));
    const headers = rows[0].map(h => h.trim());
    return rows.slice(1).map(row => {
        const obj = {};
        headers.forEach((h, i) => obj[h] = row[i] ? row[i].trim() : "");
        return obj;
    });
}

let territoriesData = [];
let addressesData = [];

function readFile(file, callback) {
    const reader = new FileReader();
    reader.onload = e => callback(parseCSV(e.target.result));
    reader.readAsText(file);
}

document.getElementById("territoriesFile").addEventListener("change", e => {
    readFile(e.target.files[0], data => territoriesData = data);
});

document.getElementById("addressesFile").addEventListener("change", e => {
    readFile(e.target.files[0], data => addressesData = data);
});

function processData() {
    if (!territoriesData.length || !addressesData.length) {
        alert("Please upload both files first.");
        return;
    }

    const territoryLookup = {};
    territoriesData.forEach(t => {
        territoryLookup[t.TerritoryID] = `${t.CategoryCode}-${t.Number} ${t.Area || ""}`;
    });

    const grouped = {};

    addressesData.forEach(a => {
        if (a.Status !== "DoNotCall") return;

        const territoryName = territoryLookup[a.TerritoryID] || a.TerritoryID;
        const address = `${a.Number || ""} ${a.Street || ""} ${a.Suburb || ""}`.trim();

        if (!grouped[territoryName]) grouped[territoryName] = [];
        grouped[territoryName].push(address);
    });

    let output = "";

    Object.keys(grouped).sort().forEach(territory => {
        output += `<h3>${territory}</h3><ul>`;
        grouped[territory].forEach(addr => {
            output += `<li>${addr} (Do Not Call)</li>`;
        });
        output += `</ul>`;
    });

    document.getElementById("output").innerHTML = output;
}
