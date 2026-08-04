document.addEventListener("DOMContentLoaded", function () {
    const cells = document.querySelectorAll("[data-weather-city]");
    if (!cells.length) {
        return;
    }

    // Group cells by city so contacts sharing a city only trigger one
    // fetch each, instead of one per row.
    const cellsByCity = new Map();
    cells.forEach(function (cell) {
        const city = cell.dataset.weatherCity;
        if (!cellsByCity.has(city)) {
            cellsByCity.set(city, []);
        }
        cellsByCity.get(city).push(cell);
    });

    function renderWeather(cell, data) {
        cell.textContent =
            Math.round(data.temperature_c) + "°C, " +
            Math.round(data.humidity_percent) + "% humidity, " +
            Math.round(data.wind_speed_kmh) + " km/h wind";
    }

    function renderUnavailable(cell) {
        cell.textContent = "Unavailable";
        cell.classList.add("text-gray-400");
    }

    cellsByCity.forEach(function (cellsForCity, city) {
        fetch("/weather/?city=" + encodeURIComponent(city))
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("weather request failed");
                }
                return response.json();
            })
            .then(function (data) {
                cellsForCity.forEach(function (cell) {
                    renderWeather(cell, data);
                });
            })
            .catch(function () {
                cellsForCity.forEach(function (cell) {
                    renderUnavailable(cell);
                });
            });
    });
});