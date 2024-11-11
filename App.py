from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_BASE_URL = "https://api.guildwars2.com/v2"

# Obtener datos desde la API
def obtener_datos(endpoint):
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    profesiones = obtener_datos("professions")
    especializaciones = []
    configuracion_optima = None

    if request.method == "POST":
        profesion_id = request.form.get("profesion")
        especializacion_id = request.form.get("especializacion")

        if profesion_id:
            especializaciones = obtener_especializaciones(profesion_id)

        if especializacion_id:
            configuracion_optima = calcular_configuracion_optima(especializacion_id)

    return render_template(
        "index.html",
        profesiones=profesiones,
        especializaciones=especializaciones,
        configuracion_optima=configuracion_optima,
    )

# Obtener especializaciones de una profesión
def obtener_especializaciones(profesion_id):
    profesion = obtener_datos(f"professions/{profesion_id}")
    if not profesion:
        return []

    especializaciones = []
    for spec_id in profesion.get("specializations", []):
        especializacion = obtener_datos(f"specializations/{spec_id}")
        if especializacion:
            especializaciones.append({
                "id": spec_id,
                "name": especializacion["name"],
                "description": especializacion.get("description", "Sin descripción"),
            })

    return especializaciones

# Calcular la configuración óptima para una especialización
def calcular_configuracion_optima(especializacion_id):
    especializacion = obtener_datos(f"specializations/{especializacion_id}")
    if not especializacion:
        return None

    dps_total, quickness_total, alacrity_total = 0, 0, 0
    habilidades_optimas = []
    equipamiento_optimo = {"arma": "Sin definir", "runas": "Sin definir"}

    # Calcular contribuciones de los rasgos
    for trait_id in especializacion.get("major_traits", []):
        rasgo = obtener_datos(f"traits/{trait_id}")
        if rasgo:
            dps_total += rasgo.get("dps", 0)
            quickness_total += rasgo.get("quickness", 0)
            alacrity_total += rasgo.get("alacrity", 0)

    # Determinar habilidades óptimas
    for skill_id in especializacion.get("skills", []):
        habilidad = obtener_datos(f"skills/{skill_id}")
        if habilidad:
            dps = sum(fact.get("value", 0) for fact in habilidad.get("facts", []) if fact.get("text") == "DPS")
            quickness = sum(fact.get("value", 0) for fact in habilidad.get("facts", []) if fact.get("text") == "Quickness")
            alacrity = sum(fact.get("value", 0) for fact in habilidad.get("facts", []) if fact.get("text") == "Alacrity")

            habilidades_optimas.append({
                "name": habilidad["name"],
                "dps": dps,
                "quickness": quickness,
                "alacrity": alacrity,
            })

    # Elegir el mejor equipamiento basado en atributos
    equipamiento_optimo = {
        "arma": "Espada de Poder" if dps_total > 50 else "Báculo de Rapidez",
        "runas": "Runas de la Rapidez" if quickness_total > alacrity_total else "Runas de la Precisión",
    }

    return {
        "especializacion": especializacion["name"],
        "dps": dps_total,
        "quickness": quickness_total,
        "alacrity": alacrity_total,
        "habilidades_optimas": habilidades_optimas,
        "equipamiento_optimo": equipamiento_optimo,
    }

if __name__ == "__main__":
    app.run(debug=True)
