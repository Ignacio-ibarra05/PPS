import requests
import json

# URLs base
base_url = "https://api.guildwars2.com/v2"
races_url = f"{base_url}/races"
professions_url = f"{base_url}/professions"
specializations_url = f"{base_url}/specializations"

# Función para obtener datos desde un endpoint
def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al acceder a {url}: {response.status_code}")
        return None

# Obtener razas
def get_races():
    races_data = get_data(races_url)
    return races_data if races_data else []

# Obtener detalles de profesiones, especializaciones, habilidades y equipamiento
def get_professions():
    professions_data = get_data(professions_url)
    professions_details = []
    
    if professions_data:
        for profession in professions_data:
            profession_details = get_data(f"{professions_url}/{profession}")
            if profession_details:
                profession_info = {
                    "name": profession_details['name'],
                    "specializations": [],
                    "skills": [],
                    "equipment": {}
                }
                
                # Especializaciones
                for specialization_id in profession_details['specializations']:
                    specialization_details = get_data(f"{specializations_url}/{specialization_id}")
                    if specialization_details:
                        profession_info["specializations"].append(specialization_details['name'])
                
                # Habilidades
                for skill in profession_details['skills']:
                    skill_name = skill.get('id', 'Nombre no disponible')
                    skill_type = skill.get('type', 'Tipo no disponible')
                    profession_info["skills"].append({
                        "id": skill_name,
                        "type": skill_type
                    })
                
                # Equipamiento
                for weapon, details in profession_details['weapons'].items():
                    weapon_info = {
                        "skills": [skill['id'] for skill in details['skills']],
                        "specialization_required": details.get('specialization', 'Ninguna')
                    }
                    profession_info["equipment"][weapon] = weapon_info
                
                professions_details.append(profession_info)
    
    return professions_details

# Guardar datos en un archivo JSON
def save_to_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Datos guardados en {filename}")
    except Exception as e:
        print(f"Error al guardar en archivo: {e}")

# Ejecutar las funciones y guardar los datos
def main():
    # Obtener razas y profesiones
    races = get_races()
    professions = get_professions()
    
    # Organizar datos en un diccionario
    data = {
        "races": races,
        "professions": professions
    }
    
    # Guardar en archivo JSON
    save_to_json("guildwars2_data.json", data)

if __name__ == "__main__":
    main()
