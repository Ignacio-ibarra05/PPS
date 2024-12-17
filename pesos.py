from coef import *
from tester import *

def pesos(input_stat, url):
    coef = getCoef(url, input_stat)
    in_stat = input_stat
    dano_base = calcular_dano(coef, in_stat)
    print(f'daño base: {dano_base}')
    pesos = {stat: 0 for stat in input_stat}
    input_stat_modified = in_stat.copy()

    for stat in input_stat:
        input_stat_modified = in_stat.copy()
        input_stat_modified[stat] += 1
        pesos[stat] = calcular_dano(coef, input_stat_modified) - dano_base
        print(f'stat {stat}: {calcular_dano(coef, input_stat_modified)}')
    
    input_stat_modified = in_stat.copy()
    input_stat_modified['crit_chance'] = 0.2

    dano_base2 = calcular_dano(coef, input_stat_modified)

    print(f'daño base 2: {calcular_dano(coef, input_stat_modified)}')
    
    input_stat_modified2 = input_stat_modified.copy()
    input_stat_modified2['crit_chance'] += 0.01
    print(f'stat crit_chance: {calcular_dano(coef, input_stat_modified2)}')
    

    pesos['crit_chance'] = calcular_dano(coef, input_stat_modified2) - dano_base2

    pesos['precision'] = pesos['crit_chance'] / 15
    pesos['crit_dmg'] /= 1500
    pesos['expertise_tormento'] /= 1500
    pesos['expertise_sangrado'] /= 1500
    pesos['expertise_quemado'] /= 1500
    pesos['expertise_veneno'] /= 1500
    pesos['expertise_confusion'] /= 1500
    pesos['expertise'] = pesos['expertise_tormento'] + pesos['expertise_sangrado'] + pesos['expertise_quemado'] + pesos['expertise_veneno'] + pesos['expertise_confusion']
    return pesos


input_stat = {
    'power': 3014,
    'precision': 2168,
    'crit_chance': 1,
    'crit_dmg': 2.243,
    'condi_dmg': 1371,
    'expertise': 225,
    'expertise_tormento': 1.15,
    'expertise_sangrado': 1.65,
    'expertise_quemado': 1.15,
    'expertise_veneno': 1.15,
    'expertise_confusion': 1.15
}

input_stat_2 = {
    'power': 2756,
    'precision': 2155,
    'crit_chance': 1,
    'crit_dmg': 1.603,
    'condi_dmg': 2594,
    'expertise': 225,
    'expertise_tormento': 1.15,
    'expertise_sangrado': 1.65,
    'expertise_quemado': 1.15,
    'expertise_veneno': 1.15,
    'expertise_confusion': 1.15
}

url = 'https://dps.report/6qrQ-20241215-094842_golem'

print(pesos(input_stat, url))