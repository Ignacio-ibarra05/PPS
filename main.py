import json
from tester import *

def calcular_configuracion_optima(input_values):
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
            if attribute_name in input_values:
                stat_val = input_values[attribute_name]
                total_gain += stat_val * (1.0 + multiplier)
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

    # Determinar ítems seleccionados
    chosen_items = []
    for item_id in items:
        item_node = item_to_node[item_id]
        for v, cap, _, _ in adj[item_node]:
            if v == W and cap == 0:  # Capacidad agotada = flujo utilizado
                chosen_items.append(item_id)
                break

    return {
        "items": chosen_items,
        "total_utility": -min_cost,
    }

'''
#### Ejemplo de entrada
input_values = {
    "Toughness": 8,
    "CritDamage": 5,
    "Expertise": 15,
    "Power": 6,
    "Precision": 1,
    "ConditionDamage": 3
}

resultado = calcular_configuracion_optima(input_values)
print("Ítems seleccionados:", resultado["items"])
print("Utilidad total:", resultado["total_utility"])
'''