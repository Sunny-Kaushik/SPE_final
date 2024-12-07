async function getSpecialists() {
    const symptoms = document.getElementById("symptoms").value;
    const response = await fetch("http://localhost:8082/get-specialists", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms }),
    });
    const data = await response.json();

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<h2>Recommended Specialists:</h2>";
    data.specialists.forEach((specialist, index) => {
        resultsDiv.innerHTML += `<p>${index + 1}. ${specialist[0]} (Score: ${specialist[1]})</p>`;
    });
}
