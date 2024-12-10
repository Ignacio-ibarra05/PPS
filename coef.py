import requests
from functools import reduce

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

Power = 0
Power2 = 0
Burning = 0
Bleeding = 0
Poison = 0
Torment = 0
Confusion = 0


condition_ids = {
    "Burning": 737,
    "Bleeding": 736,
    "Poison": 723,
    "Torment": 19426,
    "Confusion": 861,
}


url = 'https://dps.report/getJson?permalink=https://dps.report/LzVj-20231003-151324_golem'
data = get_data(url)

totalDps = 0

end = data['phases'][0]['end']
start = data['phases'][0]['start']
duration = (end -start)/1000

powerdps = data['players'][0]['dpsTargets'][0][0]['powerDps']

print(f'duracion: {duration}')
print(f'powerDPS: {powerdps}')
damage_dist = data['players'][0]['targetDamageDist'][0][0]

condition_data = {}

# Procesamiento de las condiciones
for condition, condition_id in condition_ids.items():
    entry = next((e for e in damage_dist if e.get("id") == condition_id), None)
    total_damage = entry.get("totalDamage", 0) if entry else 0
    dps = round((total_damage / duration), 2)
    condition_data[condition] = dps

print(condition_data)

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

print(f'Power: {powerDPSWithoutLifesteal}')

print(condition_data)

for i in condition_data:
    totalDps += condition_data[i]

totalDps += powerDPSWithoutLifesteal



print(totalDps)
print('\n')
print(str(data.keys()))
print('\n')


print(data['players'][0]['rotation'][0])
print('\n')

coef_dmg = 0

for skill in data['players'][0]['rotation']:
    id = skill['id']
    print(f'Skill id: { id }')
    skill_hits = len(skill['skills'])
    print(f'Skill hits: { skill_hits }')

    skillAPIData = get_data_API(f'skills/{id}')
    if isinstance(skillAPIData, dict) and 'facts' in skillAPIData:
        damage_facts = [fact for fact in skillAPIData['facts'] if fact.get('type') == 'Damage']
        dmg_m = 0
        if damage_facts:
            for d in damage_facts:
                if d['dmg_multiplier'] > dmg_m:
                    dmg_m = d['dmg_multiplier']*d['hit_count']
        print(f'Damage modifier { dmg_m }')
    coef_dmg += skill_hits*dmg_m
    print('\n')

coef_dmg = coef_dmg*1000/duration
print(coef_dmg)

