import React, { useState, useEffect } from "react";
import Selector from "./components/Selector";
import "./styles.css";

const API_BASE_URL = "https://api.guildwars2.com/v2";

function App() {
  const [races, setRaces] = useState([]);
  const [professions, setProfessions] = useState([]);
  const [skills, setSkills] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [skillStats, setSkillStats] = useState(null);

  // Cargar datos iniciales (razas y profesiones)
  useEffect(() => {
    const fetchData = async () => {
      const racesData = await fetch(`${API_BASE_URL}/races`).then((res) =>
        res.json()
      );
      const professionsData = await fetch(`${API_BASE_URL}/professions`).then(
        (res) => res.json()
      );
      setRaces(racesData);
      setProfessions(professionsData);
    };

    fetchData();
  }, []);

  // Cargar habilidades al seleccionar una profesión
  const handleProfessionChange = async (professionId) => {
    if (!professionId) {
      setSpecializations([]);
      setSkills([]);
      return;
    }

    const professionData = await fetch(
      `${API_BASE_URL}/professions/${professionId}`
    ).then((res) => res.json());
    setSpecializations(professionData.specializations || []);
    setSkills(professionData.skills || []);
  };

  // Cargar estadísticas de habilidades
  const handleSkillChange = async (skillId) => {
    if (!skillId) {
      setSkillStats(null);
      return;
    }

    const skillData = await fetch(`${API_BASE_URL}/skills?ids=${skillId}`).then(
      (res) => res.json()
    );
    setSkillStats(skillData[0] || null);
  };

  return (
    <div className="App">
      <h1>Guild Wars 2 Skill Stats</h1>
      <Selector
        label="Raza"
        options={races}
        valueKey="id"
        labelKey="id"
        onChange={() => {}}
      />
      <Selector
        label="Profesión"
        options={professions}
        valueKey="id"
        labelKey="id"
        onChange={handleProfessionChange}
      />
      <Selector
        label="Especialización"
        options={specializations}
        valueKey="id"
        labelKey="id"
        onChange={() => {}}
      />
      <Selector
        label="Habilidad"
        options={skills}
        valueKey="id"
        labelKey="name"
        onChange={handleSkillChange}
      />
      <div className="results">
        <h2>Estadísticas de Habilidad</h2>
        {skillStats ? (
          <div>
            <h3>{skillStats.name}</h3>
            <p>{skillStats.description || "Sin descripción"}</p>
            <img src={skillStats.icon} alt={skillStats.name} />
            <ul>
              {skillStats.facts?.map((fact, index) => (
                <li key={index}>
                  {fact.text}: {fact.value || fact.hit_count || "N/A"}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p>Selecciona una habilidad para ver las estadísticas.</p>
        )}
      </div>
    </div>
  );
}

export default App;
