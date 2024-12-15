def calcular_dano_fisico(coef_habilidad, power_stat, prob_crit, dano_crit, armadura_objetivo, duracion):
    crit = prob_crit
    if prob_crit > 1:
        crit = 1
    dano_normal = 1000 * coef_habilidad * power_stat / armadura_objetivo
    dano_critico = dano_normal * dano_crit
    dano = dano_normal * (1 - crit) + dano_critico * crit
    return dano * duracion

def calcular_dano_condi(coef_burning, coef_bleeding, coef_poison, coef_torment, coef_confusion, condi_stat, exp_burning, exp_bleeding, exp_poison, exp_torment, exp_confusion, duracion):
    dano = 0
    dano += (condi_stat * 0.155 + 131) * exp_burning * coef_burning
    dano += (condi_stat * 0.06 + 22) * exp_bleeding * coef_bleeding
    dano += (condi_stat * 0.06 + 33.5) * exp_poison * coef_poison
    dano += (condi_stat * 0.09 + 31.8) * exp_torment * coef_torment
    dano += (condi_stat * 0.05 + 18.25) * exp_confusion * coef_confusion
    return dano * duracion

def calcular_dano(coef, stat):
    coef_habilidad = coef['Power']
    power_stat = stat['power']
    prob_crit = coef['Crit'] + stat['crit_chance']
    dano_crit = stat['crit_dmg']
    armadura_objetivo = coef['Tarmor']
    duracion = coef['duracion']
    
    dano_fisico = calcular_dano_fisico(coef_habilidad, power_stat, prob_crit, dano_crit, armadura_objetivo, duracion)

    coef_burning = coef['Burning']
    coef_bleeding = coef['Bleeding']
    coef_poison = coef['Poison']
    coef_torment = coef['Torment']
    coef_confusion = coef['Confusion']
    condi_stat = stat['condi_dmg']
    exp_burning = stat['expertise_quemado']
    exp_bleeding = stat['expertise_sangrado']
    exp_poison = stat['expertise_veneno']
    exp_torment = stat['expertise_tormento']
    exp_confusion = stat['expertise_confusion']

    dano_condi = calcular_dano_condi(coef_burning, coef_bleeding, coef_poison, coef_torment, coef_confusion, condi_stat, exp_burning, exp_bleeding, exp_poison, exp_torment, exp_confusion, duracion)

    return dano_condi + dano_fisico