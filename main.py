import heapq
import json

# Datos de entrada (ejemplo)
input_values = {
    "Toughness": 2,
    "CritDamage": 2,
    "Expertise": 2,
    "Power": 2,
    "Precision": 2,
    "ConditionDamage": 2
}

ITEMSTATS_CACHE_FILE = "itemstats_cache.json"
with open(ITEMSTATS_CACHE_FILE, "r", encoding="utf-8") as f:
    itemstats_cache = json.load(f)

stats_of_interest = list(input_values.keys())
num_items = len(itemstats_cache)
items = list(itemstats_cache.keys())

# Queremos exactamente 6 ítems
K = 6

# Crearemos nodos:
# F (fuente) = 0
# S_stat para cada stat de interés: 1..len(stats_of_interest)
# I_item para cada ítem: indices consecutivos
# W (sumidero) = último nodo

F = 0
stat_nodes = {}
for i, stat in enumerate(stats_of_interest, start=1):
    stat_nodes[stat] = i

# Ítems empiezan después de las stats
first_item_node = len(stats_of_interest) + 1

item_to_node = {}
for i, item_id in enumerate(items):
    item_to_node[item_id] = first_item_node + i

W = first_item_node + num_items  # sumidero

# Grafo para min cost max flow
# Cada arista: u->v con capacidad y costo
# Guardaremos lista de adyacencia con: [ (v, cap, cost, rev) ]
# rev es el índice de la arista inversa en adj[v]
adj = [[] for _ in range(W+1)]

def add_edge(u, v, cap, cost):
    adj[u].append([v, cap, cost, len(adj[v])])
    adj[v].append([u, 0, -cost, len(adj[u])-1])

# Construir el grafo
# F->S_stat con capacidad K y costo 0
for stat in stats_of_interest:
    add_edge(F, stat_nodes[stat], K, 0)

# S_stat->I_item
# Para cada ítem, calculamos su utilidad para cada stat
for item_id, data in itemstats_cache.items():
    item_node = item_to_node[item_id]
    attributes = data.get("attributes", [])
    # Podemos sumar la utilidad de cada stat. Pero necesitamos varias aristas?
    # El objetivo es que el flujo pueda venir de múltiples stats.
    # Cada stat aporta una arista independiente con costo negativo.
    # Capacidad de 1 por stat es suficiente, pues un ítem no necesita más de 1 unidad por stat.
    for attr in attributes:
        attribute_name = attr["attribute"]
        multiplier = attr["multiplier"]
        if attribute_name in input_values:
            stat_val = input_values[attribute_name]
            # Ganancia = stat_val * multiplier
            gain = stat_val * multiplier
            cost = -gain  # costo negativo para maximizar ganancia
            add_edge(stat_nodes[attribute_name], item_node, 1, cost)

# I_item->W con capacidad 1 y costo 0
for item_id in items:
    item_node = item_to_node[item_id]
    add_edge(item_node, W, 1, 0)

# Ahora implementamos min cost max flow con potencias (Johnson) + Dijkstra
def min_cost_max_flow(s, t):
    flow = 0
    cost = 0
    dist = [0]*(W+1)
    potential = [0]*(W+1)  # potencias para Johnson
    parent = [(0,0)]*(W+1) # (u, index of edge in adj[u])
    
    # Bellman-Ford inicial para potencias
    for i in range(W+1):
        potential[i] = 0
    # Podríamos ignorar Bellman-Ford si costos >=0, pero tenemos costos negativos.
    # Sin embargo, por construcción no debería haber ciclos negativos que se puedan saturar.
    # Si quieres seguridad, corre Bellman-Ford aquí para inicializar potential.
    # En este caso, asumimos que no hay ciclos negativos viables.
    
    while flow < K:
        # Dijkstra con Johnson (potencial)
        for i in range(W+1):
            dist[i] = float('inf')
        dist[s] = 0
        parent = [(-1,-1)]*(W+1)
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
        
        if dist[t] == float('inf'):
            # No hay más caminos aumentantes
            break
        
        # Actualizar potencial
        for i in range(W+1):
            if dist[i] < float('inf'):
                potential[i] += dist[i]
        
        # Aumentar flujo
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

print("Flujo máximo:", max_flow)
print("Costo mínimo (negativo):", min_cost)
print("Utilidad máxima:", -min_cost)  # el costo es negativo, la utilidad es -costo

# Para determinar qué ítems fueron escogidos:
# Si hay flujo en la arista I_item->W significa que ese ítem fue seleccionado.
# La arista I_item->W fue la última agregada para cada ítem, con índice conocido.
# Vamos a verificar qué ítems tienen flujo.

chosen_items = []
for item_id in items:
    item_node = item_to_node[item_id]
    # La arista item_node->W es la última en adj[item_node] o búscala
    for i, (v, cap, cst, rev) in enumerate(adj[item_node]):
        if v == W:
            # Esta es la arista item_node->W
            # Flujo = capacidad inicial (1) - cap residual
            initial_cap = 1
            flow_used = initial_cap - cap
            if flow_used > 0:
                chosen_items.append(item_id)
            break

print("Items seleccionados:", chosen_items)
print("Cantidad:", len(chosen_items))
