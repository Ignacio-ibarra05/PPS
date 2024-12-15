import heapq
import json

def calcular_configuracion_optima(input_values):
    with open("itemstats_cache.json", "r", encoding="utf-8") as f:
        itemstats_cache = json.load(f)

    stats_of_interest = list(input_values.keys())
    num_items = len(itemstats_cache)
    items = list(itemstats_cache.keys())

    # Queremos exactamente 6 ítems
    K = 6

    # Crearemos nodos:
    F = 0  # Nodo fuente
    stat_nodes = {stat: i for i, stat in enumerate(stats_of_interest, start=1)}

    first_item_node = len(stats_of_interest) + 1
    item_to_node = {item_id: first_item_node + i for i, item_id in enumerate(items)}
    W = first_item_node + num_items  # Nodo sumidero

    adj = [[] for _ in range(W + 1)]

    def add_edge(u, v, cap, cost):
        adj[u].append([v, cap, cost, len(adj[v])])
        adj[v].append([u, 0, -cost, len(adj[u]) - 1])

    # Construir el grafo
    for stat in stats_of_interest:
        add_edge(F, stat_nodes[stat], K, 0)

    for item_id, data in itemstats_cache.items():
        item_node = item_to_node[item_id]
        attributes = data.get("attributes", [])
        for attr in attributes:
            attribute_name = attr["attribute"]
            multiplier = attr["multiplier"]
            if attribute_name in input_values:
                stat_val = input_values[attribute_name]
                gain = stat_val * multiplier
                cost = -gain  # costo negativo para maximizar ganancia
                add_edge(stat_nodes[attribute_name], item_node, 1, cost)

    for item_id in items:
        item_node = item_to_node[item_id]
        add_edge(item_node, W, 1, 0)

    def min_cost_max_flow(s, t):
        flow = 0
        cost = 0
        dist = [0] * (W + 1)
        potential = [0] * (W + 1)
        parent = [(0, 0)] * (W + 1)

        while flow < K:
            for i in range(W + 1):
                dist[i] = float("inf")
            dist[s] = 0
            parent = [(-1, -1)] * (W + 1)
            pq = [(0, s)]

            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for i, (v, cap, cst, rev) in enumerate(adj[u]):
                    if cap > 0:
                        ndist = d + cst + potential[u] - potential[v]
                        if ndist < dist[v]:
                            dist[v] = ndist
                            parent[v] = (u, i)
                            heapq.heappush(pq, (ndist, v))

            if dist[t] == float("inf"):
                break

            for i in range(W + 1):
                if dist[i] < float("inf"):
                    potential[i] += dist[i]

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

    max_flow, min_cost = min_cost_max_flow(F, W)

    chosen_items = []
    for item_id in items:
        item_node = item_to_node[item_id]
        for i, (v, cap, cst, rev) in enumerate(adj[item_node]):
            if v == W:
                initial_cap = 1
                flow_used = initial_cap - cap
                if flow_used > 0:
                    chosen_items.append(item_id)
                break

    return {
        "items": chosen_items,
        "total_utility": -min_cost,
    }

##def calcular_configuracion_optima(input_values):
    # Ejemplo de datos de prueba: reemplázalos con la lógica real
    chosen_items = ["item_1_id", "item_2_id", "item_3_id"]  # Asegúrate de que esto es una lista
    total_utility = 100.0  # Ejemplo de utilidad total calculada

    return {
        "items": chosen_items,  # Lista de ítems seleccionados
        "total_utility": total_utility,  # Utilidad total calculada
    }
