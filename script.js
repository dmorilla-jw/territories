let territoriesData = [];
let addressesData = [];

function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/);
    return lines.map(line => line.split(","));
}

function readFile(file, callback) {
    const reader = new FileReader();
    reader.onload = e => callback(parseCSV(e.target.result));
    reader.readAsText(file);
}

document.getElementById("territoriesFile").addEventListener("change", e => {
    readFile(e.target.files[0], data => {
        territoriesData = data;
        console.log("Territories loaded:", data);
    });
});

document.getElementById("addressesFile").addEventListener("change", e => {
    readFile(e.target.files[0], data => {
        addressesData = data;
        console.log("Addresses loaded:", data);
    });
});

function processData() {
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = "Processing...";

    if (!territoriesData.length || !addressesData.length) {
        outputDiv.innerHTML = "Please upload both files first.";
        return;
    }

    let output = "<h3>Do Not Call Addresses</h3><ul>";

    addressesData.forEach(row => {
        const rowText = row.join(" ");

        if (rowText.toLowerCase().includes("donotcall") || rowText.toLowerCase().includes("do not call")) {
            output += `<li>${rowText}</li>`;
        }
    });

    output += "</ul>";

    outputDiv.innerHTML = output;
}
