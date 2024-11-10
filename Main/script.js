// URLs de la API de Guild Wars 2
const baseUrl = "https://api.guildwars2.com/v2";
const racesUrl = `${baseUrl}/races`;
const professionsUrl = `${baseUrl}/professions`;
const skillsUrl = `${baseUrl}/skills`;
const specializationsUrl = `${baseUrl}/specializations`;

// Referencias al DOM
const raceSelect = document.getElementById("race");
const professionSelect = document.getElementById("profession");
const specializationSelect = document.getElementById("specialization");
const skillSelect = document.getElementById("skill");
const resultsDiv = document.getElementById("results");

// Cargar opciones en un select
async function loadOptions(url, selectElement, key = "name") {
    try {
        const response = await fetch(url);
        const data = await response.json();
        selectElement.innerHTML = "<option value=''>Selecciona una opción</option>";
        data.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item[key] || item;
            opt.textContent = item[key] || item;
            selectElement.appendChild(opt);
        });
    } catch (error) {
        console.error("Error al cargar opciones:", error);
    }
}

// Mostrar estadísticas de habilidad seleccionada
async function showStats() {
    const selectedSkill = skillSelect.value;

    if (!selectedSkill) {
        resultsDiv.innerHTML = `<h2>Estadísticas de la Habilidad</h2><p>Selecciona una habilidad.</p>`;
        return;
    }

    try {
        const response = await fetch(`${skillsUrl}?ids=${selectedSkill}`);
        const data = await response.json();
        const skill = data[0]; // Primera habilidad

        let factsHtml = "<ul>";
        skill.facts?.forEach(fact => {
            factsHtml += `<li>${fact.text}: ${fact.value || fact.hit_count || "N/A"}</li>`;
        });
        factsHtml += "</ul>";

        resultsDiv.innerHTML = `
            <h2>${skill.name}</h2>
            <p>${skill.description || "Sin descripción."}</p>
            <img src="${skill.icon}" alt="${skill.name}" style="width: 50px;">
            <h3>Estadísticas:</h3>
            ${factsHtml}
        `;
    } catch (error) {
        console.error("Error al cargar estadísticas:", error);
    }
}

// Eventos de cambio para actualizar opciones
professionSelect.addEventListener("change", async () => {
    const selectedProfession = professionSelect.value;

    if (!selectedProfession) {
        specializationSelect.innerHTML = "<option value=''>Selecciona una especialización</option>";
        skillSelect.innerHTML = "<option value=''>Selecciona una habilidad</option>";
        return;
    }

    const response = await fetch(`${professionsUrl}/${selectedProfession}`);
    const profession = await response.json();

    // Cargar especializaciones
    const specializations = profession.specializations.map(id => ({ name: id }));
    specializationSelect.innerHTML = "<option value=''>Selecciona una especialización</option>";
    specializations.forEach(spec => {
        const opt = document.createElement("option");
        opt.value = spec.name;
        opt.textContent = spec.name;
        specializationSelect.appendChild(opt);
    });

    // Cargar habilidades
    skillSelect.innerHTML = "<option value=''>Selecciona una habilidad</option>";
    profession.skills.forEach(skill => {
        const opt = document.createElement("option");
        opt.value = skill.id;
        opt.textContent = skill.name || skill.id;
        skillSelect.appendChild(opt);
    });
});

// Cargar opciones iniciales
(async function init() {
    await loadOptions(racesUrl, raceSelect);
    await loadOptions(professionsUrl, professionSelect, "id");
})();

// Mostrar estadísticas al hacer clic
document.getElementById("show-stats").addEventListener("click", showStats);
