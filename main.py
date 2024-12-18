import json
from tester import *
from pesos import *

def calcular_configuracion_optima(input_values, url):

    stat_weights = pesos(input_values, url)
    with open("itemstats_cache.json", "r", encoding="utf-8") as f:
        itemstats_cache = json.load(f)

    stats_of_interest = list(input_values.keys())
    num_items = len(itemstats_cache)
    items = list(itemstats_cache.keys())

    # Queremos exactamente 6 ítems
    K = 6

    # Nodos:
    F = 0  # Nodo fuente
    stat_nodes = {stat: i for i, stat in enumerate(stats_of_interest, start=1)}

    first_item_stat_sum_node = len(stats_of_interest) + 1
    item_sum_nodes = {item_id: first_item_stat_sum_node + i for i, item_id in enumerate(items)}

    first_item_node = first_item_stat_sum_node + len(items)
    item_to_node = {item_id: first_item_node + i for i, item_id in enumerate(items)}
    W = first_item_node + len(items)  # Nodo sumidero

    adj = [[] for _ in range(W + 1)]

    def add_edge(u, v, cap, cost):
        adj[u].append([v, cap, cost, len(adj[v])])
        adj[v].append([u, 0, -cost, len(adj[u]) - 1])

    # Fuente -> Stats con capacidad K y costo 0
    for stat in stats_of_interest:
        add_edge(F, stat_nodes[stat], K, 0)

    # Stats -> Item Sum Nodes (capa intermedia)
    for item_id, data in itemstats_cache.items():
        sum_node = item_sum_nodes[item_id]
        attributes = data.get("attributes", [])
        total_gain = 0
        for attr in attributes:
            attribute_name = attr["attribute"]
            multiplier = attr["multiplier"]
            weight = stat_weights.get(attribute_name, 0)
            if attribute_name in stat_weights:
                total_gain += multiplier * weight
        # Sumar beneficios de todos los atributos y agregar un único costo negativo
        cost = -total_gain
        add_edge(sum_node, item_to_node[item_id], 1, cost)

    # Item Sum Nodes -> Ítems individuales
    for item_id in items:
        sum_node = item_sum_nodes[item_id]
        add_edge(stat_nodes.get("Power", 1), sum_node, 1, 0)  # Conecta capa intermedia acumulativa

    # Ítems individuales -> Sumidero
    for item_id in items:
        item_node = item_to_node[item_id]
        add_edge(item_node, W, 1, 0)

    # Bellman-Ford
    def bellman_ford(s, t):
        N = W + 1
        dist = [float('inf')] * N
        parent = [(-1, -1)] * N
        dist[s] = 0

        for _ in range(N - 1):
            for u in range(N):
                for i, (v, cap, cost, rev) in enumerate(adj[u]):
                    if cap > 0 and dist[u] + cost < dist[v]:
                        dist[v] = dist[u] + cost
                        parent[v] = (u, i)

        return dist, parent

    # Min-Cost Max-Flow
    def min_cost_max_flow(s, t):
        flow = 0
        cost = 0

        while flow < K:
            dist, parent = bellman_ford(s, t)
            if dist[t] == float("inf"):
                break

            add_flow = K - flow
            v = t
            while v != s:
                u, i = parent[v]
                add_flow = min(add_flow, adj[u][i][1])
                v = u

            v = t
            path_cost = 0
            while v != s:
                u, i = parent[v]
                adj[u][i][1] -= add_flow
                rev = adj[u][i][3]
                adj[v][rev][1] += add_flow
                path_cost += adj[u][i][2]
                v = u

            flow += add_flow
            cost += path_cost * add_flow

        return flow, cost

    # Ejecutar flujo máximo con costo mínimo
    max_flow, min_cost = min_cost_max_flow(F, W)

    item_utility = {}
    # Determinar ítems seleccionados
    chosen_items = []
    for item_id in items:
        item_node = item_to_node[item_id]
        for v, cap, _, _ in adj[item_node]:
            if v == W and cap == 0:  # Capacidad agotada = flujo utilizado
                chosen_items.append(item_id)
                attributes = itemstats_cache[item_id]['attributes']
                item_utility[item_id] = 0
                for attr in attributes:
                    attribute_name = attr["attribute"]
                    multiplier = attr["multiplier"]
                    weight = stat_weights.get(attribute_name, 0)
                    item_utility[item_id] += multiplier * weight
                break
    dmg = []
    s = []

    for key in sorted(item_utility, key=lambda k: item_utility[k], reverse=True):
        dmg.append(item_utility[key])
        s.append(itemstats_cache[key]['name'])

    item_f = {
        'Helm' : {s[2] : dmg[2]*179.256},
        'Shoulders': {s[3] :dmg[3]*134.442},
        'Coat': {s[0] :dmg[0]*403.326},
        'Gloves': {s[4] :dmg[4]*134.442},
        'Leggings': {s[1] :dmg[1]*268.884},
        'Boots': {s[5] :dmg[5]*134.442},
    }
    

    return {
        "items": item_f,
        "total_utility": round(sum(next(iter(val.values())) for val in item_f.values()),1),
    }


# #### Ejemplo de entrada
# input_stat = {
#     'power': 3103,
#     'precision': 1813,
#     'crit_chance': 0.6871,
#     'crit_dmg': 1.5,
#     'condi_dmg': 2924,
#     'expertise': 747,
#     'expertise_tormento': 1.798,
#     'expertise_sangrado': 1.848,
#     'expertise_quemado': 1.648,
#     'expertise_veneno': 1.648,
#     'expertise_confusion': 1.648
# }

# url = 'https://dps.report/6qrQ-20241215-094842_golem'

# resultado = calcular_configuracion_optima(input_stat, url)
# print("Ítems seleccionados:", resultado["items"])
# print("Utilidad total:", resultado["total_utility"])
