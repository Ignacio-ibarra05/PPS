from flask import Flask, render_template, request
from main import calcular_configuracion_optima
from pesos import *
from coef import *
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
    c = None
    p = None

    if request.method == "POST":
        # Obtener estadísticas desde el formulario
        input_values = {
            "power": int(request.form.get("power", 0)),
            "precision": int(request.form.get("precision", 0)),
            "crit_chance": float(request.form.get("crit_chance", 0)),
            "crit_dmg": float(request.form.get("crit_dmg", 0)),
            "condi_dmg": int(request.form.get("condi_dmg", 0)),
            "Expertise": int(request.form.get("Expertise", 0)),
            "expertise_tormento": float(request.form.get("expertise_tormento", 0)),
            "expertise_sangrado": float(request.form.get("expertise_sangrado", 0)),
            "expertise_quemado": float(request.form.get("expertise_quemado", 0)),
            "expertise_veneno": float(request.form.get("expertise_veneno", 0)),
            "expertise_confusion": float(request.form.get("expertise_confusion", 0)),
        }
        url = request.form.get("url", '')

        print("Valores recibidos del formulario:", input_values, url)  # Debugging para verificar valores

        # Llamar a la función principal de main.py para calcular
        configuracion_optima = calcular_configuracion_optima(input_values,url)


        print("Resultado de configuracion_optima:", configuracion_optima)  # Debugging para verificar resultado

        # Reemplazar los IDs de ítems con sus nombres del archivo itemstats_cache.json
        
        if configuracion_optima and isinstance(configuracion_optima.get("items", {}), dict):
            item_names = []
            for item_name, item_data in configuracion_optima["items"].items():
                # Usamos el siguiente valor como ejemplo para representar cada item
                item_value = round(next(iter(item_data.values())), 1)  # Esto obtiene el valor dentro del subdiccionario
                item_index = next(iter(item_data.keys()))   # Obtiene la clave de s[n]
                item_names.append(f"{item_name} ({item_index}): {item_value}")
            
            configuracion_optima["items"] = item_names
        else:
            configuracion_optima["items"] = []
            
        c = getCoef(url, input_values)
        p = pesos(input_values, url)
        print("Resultado de configuracion_optima:", configuracion_optima)
        print("Tipo de items:", type(configuracion_optima["items"]))
        print(c)


    return render_template(
        "index.html",
        configuracion_optima=configuracion_optima,
        coef = c,
        pesos = p
    )

if __name__ == "__main__":
    app.run(debug=True)
