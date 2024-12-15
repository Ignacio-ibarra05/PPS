import requests
from functools import reduce
from tester import *

API_BASE_URL = "https://api.guildwars2.com/v2"

def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error en la API: {response.status_code}')
        return None

def get_data_API(endpoint):
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    return []


condition_ids = {
    "Burning": 737,
    "Bleeding": 736,
    "Poison": 723,
    "Torment": 19426,
    "Confusion": 861,
}

def getCoef(url,input_stat):
    coef_result = {
        'Power': 0,
        'Burning': 0,
        'Bleeding': 0,
        'Poison': 0,
        'Torment': 0,
        'Confusion': 0,
        'Crit': 0,
        'Tarmor': 0,
        'duracion': 0
    }

    urldata = 'https://dps.report/getJson?permalink=' + url
    data = get_data(urldata)

    totalDps = 0

    end = data['phases'][0]['end']
    start = data['phases'][0]['start']
    duration = (end -start)/1000
    coef_result['duracion'] = duration
    powerdps = data['players'][0]['dpsTargets'][0][0]['powerDps']
    powerdamage = data['players'][0]['dpsTargets'][0][0]['powerDamage']

    tArmor = data['targets'][0]['toughness']
    coef_result['Tarmor'] = tArmor
    critRate = data['players'][0]['statsAll'][0]['criticalRate']/data['players'][0]['statsAll'][0]['critableDirectDamageCount']

    coef_result['Crit'] = critRate - input_stat['crit_chance']

    damage_dist = data['players'][0]['targetDamageDist'][0][0]

    condition_data = {}

    # Procesamiento de las condiciones
    for condition, condition_id in condition_ids.items():
        entry = next((e for e in damage_dist if e.get("id") == condition_id), None)
        total_damage = entry.get("totalDamage", 0) if entry else 0
        dps = round((total_damage / duration), 2)
        condition_data[condition] = dps
        match condition:
            case 'Burning': # 0.155 * Condition Damage + 131
                dps1 = input_stat['condi_dmg'] * 0.155 + 131
                dps2 = dps1 * input_stat['expertice_quemado']

            case 'Bleeding': # 0.06 * Condition Damage + 22
                dps1 = input_stat['condi_dmg'] * 0.06 + 22
                dps2 = dps1 * input_stat['expertice_sangrado']

            case 'Poison': # 0.06 * Condition Damage + 33.5
                dps1 = input_stat['condi_dmg'] * 0.06 + 33.5
                dps2 = dps1 * input_stat['expertice_veneno']

            case 'Torment': # 0.09 * Condition Damage + 31.8
                dps1 = input_stat['condi_dmg'] * 0.09 + 31.8
                dps2 = dps1 * input_stat['expertice_tormento']

            case 'Confusion': # 0.05 * Condition Damage + 18.25
                dps1 = input_stat['condi_dmg'] * 0.05 + 18.25
                dps2 = dps1 * input_stat['expertice_confusion']
        coef_result[condition] = condition_data[condition]/dps2

    # Obtiene las entradas de buffs no relacionados con condiciones
    non_condition_buff_entries = [
        (int(buff_id.replace('b', '')), buff_data['name'])
        for buff_id, buff_data in data['buffMap'].items()
        if int(buff_id.replace('b', '')) not in condition_ids.values()
    ]

    # Procesa las entradas no relacionadas con condiciones
    non_condition_data_entries = []
    for buff_id, name in non_condition_buff_entries:

        entry = next((e for e in damage_dist if e.get("id") == buff_id), {})
        total_damage = entry.get("totalDamage", 0)
        connected_hits = entry.get("connectedHits", 0)
        
        if not total_damage:
            continue

        dps = round((total_damage / duration), 2)
        hits_per_second = round((connected_hits / duration), 2)

        non_condition_data_entries.append((f'{name} "Power" DPS ({hits_per_second} hit/sec)', dps))


    possibleLifestealDamageSum = reduce(lambda prev, item: prev + item[1], non_condition_data_entries, 0)

    powerDPSWithoutLifesteal = powerdps - possibleLifestealDamageSum

    for i in condition_data:
        totalDps += condition_data[i]

    totalDps += powerDPSWithoutLifesteal


    coef_result['Power'] = powerdps / ((1 - critRate) * (1000 * input_stat['power'] / tArmor) + critRate * input_stat['crit_dmg'] * (1000 * input_stat['power'] / tArmor))
    return coef_result



input_stat = {
    'power': 3103,
    'precision': 1813,
    'crit_chance': 0.6871,
    'crit_dmg': 1.5,
    'condi_dmg': 2924,
    'expertice': 747,
    'expertice_tormento': 1.798,
    'expertice_sangrado': 1.848,
    'expertice_quemado': 1.648,
    'expertice_veneno': 1.648,
    'expertice_confusion': 1.648
}
coef = getCoef('https://dps.report/LzVj-20231003-151324_golem',input_stat)

input_stat = {
    'power': 2820,
    'precision': 2155,
    'crit_chance': 1,
    'crit_dmg': 1.7167,
    'condi_dmg': 2392,
    'expertice': 747,
    'expertice_tormento': 1.35,
    'expertice_sangrado': 1.85,
    'expertice_quemado': 1.35,
    'expertice_veneno': 1.35,
    'expertice_confusion': 1.35
}
coef = getCoef('https://dps.report/YeGx-20231205-223957_golem',input_stat)

input_stat_2 = {
    'power': 2820,
    'precision': 2155,
    'crit_chance': 1,
    'crit_dmg': 1.7167,
    'condi_dmg': 2402,
    'expertice': 747,
    'expertice_tormento': 1.35,
    'expertice_sangrado': 1.85,
    'expertice_quemado': 1.35,
    'expertice_veneno': 1.35,
    'expertice_confusion': 1.35
}

print("\n")
print(f'Entrada de estadisticas 1: { input_stat }')
print("\n")
print(f'Coeficientes obtenidos: { coef }')
print("\n")
print(f'Daño para la entrada 1: {calcular_dano(coef, input_stat)}')
print("\n")
print(f'Entrada de estadisticas 2: { input_stat_2 }')
print("\n")
print(f'Daño para la entrada 2: {calcular_dano(coef, input_stat_2)}')
print("\n")
