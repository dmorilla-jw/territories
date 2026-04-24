let territoriesData = [];
let addressesData = [];

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",").map(h => h.trim());

  return lines.slice(1).map(line => {
    const values = line.split(",");
    const obj = {};
    headers.forEach((h, i) => obj[h] = values[i] ? values[i].trim() : "");
    return obj;
  });
}

function readFile(file, callback) {
  const reader = new FileReader();
  reader.onload = e => callback(parseCSV(e.target.result));
  reader.readAsText(file);
}

document.getElementById("territoriesFile").addEventListener("change", e => {
  readFile(e.target.files[0], data => {
    territoriesData = data;
  });
});

document.getElementById("addressesFile").addEventListener("change", e => {
  readFile(e.target.files[0], data => {
    addressesData = data;
  });
});

function processData() {
  const outputDiv = document.getElementById("output");

  const territoryLookup = {};
  territoriesData.forEach(t => {
    territoryLookup[t.TerritoryID] =
      `${t.CategoryCode}-${t.Number}${t.Suffix || ""} ${t.Area || ""}`;
  });

  const grouped = {};

  addressesData.forEach(a => {
    if (a.Status !== "DoNotCall") return;

    const territoryName = territoryLookup[a.TerritoryID] || a.TerritoryID;
    const address = `${a.Number} ${a.Street}, ${a.Suburb}`.trim();

    if (!grouped[territoryName]) grouped[territoryName] = [];
    grouped[territoryName].push(address);
  });

  let output = "";

  Object.keys(grouped).sort().forEach(territory => {
    output += `<h3>${territory}</h3><ul>`;
    grouped[territory].forEach(address => {
      output += `<li>${address} — Do Not Call</li>`;
    });
    output += `</ul>`;
  });

  outputDiv.innerHTML = output || "No Do Not Call addresses found.";
}
