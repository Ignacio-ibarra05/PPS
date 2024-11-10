'''
Este codigo crea un grafo por profesion mostrando las especializaciones y a su vez los rasgos asociados. 

Para usar este codigo, primero se debe ejecutar los siguientes comandos:
 pip install requests
 pip install networkx
 pip install matplotlib

 
'''


import requests
import networkx as nx
import matplotlib.pyplot as plt

# Función para obtener detalles desde la API
def obtener_datos_desde_api(endpoint):
    url = f'https://api.guildwars2.com/v2/{endpoint}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error en la API: {response.status_code}')
        return None

# Crear grafos de profesiones
grafos_profesiones = {}

# Obtener lista de profesiones
profesiones_ids = obtener_datos_desde_api('professions')

# Crear un grafo para cada profesión
if profesiones_ids:
    for profesion_id in profesiones_ids:
        print(f'Procesando profesión: {profesion_id}')
        detalles_profesion = obtener_datos_desde_api(f'professions/{profesion_id}')
        if detalles_profesion:
            G = nx.Graph()  # Nuevo grafo para la profesión
            profesion_nombre = detalles_profesion['name']
            G.add_node(profesion_nombre, tipo='profesion')
            print(f' Añadida profesión: {profesion_nombre}')
            
            # Agregar especializaciones y sus conexiones
            for spec_id in detalles_profesion['specializations']:
                detalle_especializacion = obtener_datos_desde_api(f'specializations/{spec_id}')
                if detalle_especializacion:
                    espec_nombre = detalle_especializacion['name']
                    G.add_node(espec_nombre, tipo='especializacion')
                    G.add_edge(profesion_nombre, espec_nombre)
                    print(f'  Añadida especialización: {espec_nombre}')
                    
                    # Agregar rasgos de cada especialización
                    for trait_id in detalle_especializacion['major_traits'] + detalle_especializacion['minor_traits']:
                        detalle_trait = obtener_datos_desde_api(f'traits/{trait_id}')
                        if detalle_trait:
                            trait_nombre = detalle_trait['name']
                            G.add_node(trait_nombre, tipo='rasgo')
                            G.add_edge(espec_nombre, trait_nombre)
                            print(f'   Añadido rasgo: {trait_nombre}')
                        else:
                            print(f'   Error al obtener detalles del rasgo con ID: {trait_id}')
                else:
                    print(f'  Error al obtener detalles de la especialización con ID: {spec_id}')
            
            # Guardar el grafo de la profesión
            grafos_profesiones[profesion_nombre] = G
            print(f'Grafo para {profesion_nombre} creado con éxito.\n')
        else:
            print(f'Error al obtener detalles de la profesión: {profesion_id}')

# Verificar si los grafos fueron creados
if grafos_profesiones:
    print("Grafos creados para las siguientes profesiones:")
    for profesion in grafos_profesiones:
        print(f" - {profesion}")
else:
    print("No se creó ningún grafo de profesión.")

# Función para dibujar y mostrar cada grafo de profesión
for profesion, grafo in grafos_profesiones.items():
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(grafo)
    nx.draw(grafo, pos, with_labels=True, node_size=1500, node_color="lightblue", font_size=8, font_weight="bold", edge_color="gray")
    plt.title(f"Grafo de la Profesión: {profesion}")
    plt.show()
