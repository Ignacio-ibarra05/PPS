from flask import Flask, render_template, request
from main import calcular_configuracion_optima
import requests
import json

app = Flask(__name__)

API_BASE_URL = "https://api.guildwars2.com/v2"

# Cargar el archivo itemstats_cache.json
with open("itemstats_cache.json", "r", encoding="utf-8") as f:
    itemstats_cache = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    configuracion_optima = None

    if request.method == "POST":
        # Obtener estadísticas desde el formulario
        input_values = {
            
            "CritDamage": int(request.form.get("CritDamage", 0)),
            "Power": int(request.form.get("Power", 0)),
            "Precision": int(request.form.get("Precision", 0)),
            "ConditionDamage": int(request.form.get("ConditionDamage", 0)),
            "Expertise": int(request.form.get("Expertise", 0)),
        }

        print("Valores recibidos del formulario:", input_values)  # Debugging para verificar valores

        # Llamar a la función principal de main.py para calcular
        configuracion_optima = calcular_configuracion_optima(input_values)

        print("Resultado de configuracion_optima:", configuracion_optima)  # Debugging para verificar resultado

        # Reemplazar los IDs de ítems con sus nombres del archivo itemstats_cache.json
        if configuracion_optima and isinstance(configuracion_optima.get("items", []), list):
            item_names = []
            for item_id in configuracion_optima["items"]:
                item_data = itemstats_cache.get(item_id)
                if item_data and "name" in item_data:
                    item_names.append(item_data["name"])
                else:
                    item_names.append(f"Unknown Item ({item_id})")
            configuracion_optima["items"] = item_names
        else:
            configuracion_optima["items"] = []


        print("Resultado de configuracion_optima:", configuracion_optima)
        print("Tipo de items:", type(configuracion_optima["items"]))
        
    return render_template(
        "index.html",
        configuracion_optima=configuracion_optima,
    )

if __name__ == "__main__":
    app.run(debug=True)