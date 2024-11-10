import React from "react";

const Selector = ({ label, options, valueKey, labelKey, onChange }) => {
  return (
    <div>
      <label>{label}:</label>
      <select onChange={(e) => onChange(e.target.value)}>
        <option value="">Selecciona una opción</option>
        {options.map((option) => (
          <option key={option[valueKey]} value={option[valueKey]}>
            {option[labelKey]}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Selector;
