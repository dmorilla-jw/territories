// Read CSV file
function readCSV(file, callback) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const text = e.target.result;
        const rows = text.split('\n').map(r => r.split(','));
        callback(rows);
    };
    reader.readAsText(file);
}

let territoriesData = [];
let addressesData = [];

// Handle Territories.csv
document.getElementById('territoriesFile').addEventListener('change', function (e) {
    readCSV(e.target.files[0], function (data) {
        territoriesData = data;
        console.log("Territories loaded", territoriesData);
    });
});

// Handle Territory Addresses.csv
document.getElementById('addressesFile').addEventListener('change', function (e) {
    readCSV(e.target.files[0], function (data) {
        addressesData = data;
        console.log("Addresses loaded", addressesData);
    });
});

// Process + display
function processData() {
    if (territoriesData.length === 0 || addressesData.length === 0) {
        alert("Please upload both files first.");
        return;
    }

    let output = "";

    // Skip headers
    const addrRows = addressesData.slice(1);

    const grouped = {};

    addrRows.forEach(row => {
        const territory = row[0];
        const address = row[1];
        const status = row[2];

        if (!grouped[territory]) {
            grouped[territory] = [];
        }

    if (status && status.toLowerCase().includes("do not call")) {
        grouped[territory].push({
            address: address,
            status: status
    });
}
    });

    for (let territory in grouped) {
        output += `<h3>${territory}</h3><ul>`;
    grouped[territory].forEach(item => {
        output += `<li>${item.address} (${item.status})</li>`;
    });
        output += "</ul>";
    }

    document.getElementById("output").innerHTML = output;
}
