from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import networkx as nx
from typing import List

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definición de datos
locations = {
    'San Isidro': (-12.0901, -77.0465),
    'Miraflores': (-12.1210, -77.0297),
    'Barranco': (-12.1440, -77.0208),
    'Surco': (-12.1439, -76.9918),
    'San Borja': (-12.1061, -76.9860),
    'La Molina': (-12.0833, -76.9366),
    'Jesus Maria': (-12.0795, -77.0457),
    'Pueblo Libre': (-12.0753, -77.0724),
    'San Miguel': (-12.0783, -77.0841),
    'Callao': (-12.0553, -77.1180)
}

G = nx.Graph()

for location, coords in locations.items():
    G.add_node(location, pos=coords)

for loc1 in G.nodes:
    for loc2 in G.nodes:
        if loc1 != loc2:
            dist = ((G.nodes[loc1]['pos'][0] - G.nodes[loc2]['pos'][0]) ** 2 + 
                    (G.nodes[loc1]['pos'][1] - G.nodes[loc2]['pos'][1]) ** 2) ** 0.5
            G.add_edge(loc1, loc2, weight=dist)

class RouteRequest(BaseModel):
    start: str
    locations: List[str]

@app.get("/locations")
def get_locations():
    return list(locations.keys())

@app.post("/nearest_neighbor")
def nearest_neighbor_algorithm(data: RouteRequest):
    start = data.start
    selected_locations = data.locations

    if start not in locations or any(loc not in locations for loc in selected_locations):
        raise HTTPException(status_code=400, detail="Invalid location provided")

    subgraph = G.subgraph(selected_locations + [start])
    
    path = [start]
    nodes = set(subgraph.nodes)
    nodes.remove(start)
    current_node = start
    
    while nodes:
        next_node = min(nodes, key=lambda node: subgraph[current_node][node]['weight'])
        nodes.remove(next_node)
        path.append(next_node)
        current_node = next_node
        
    path.append(start)  # Regresar al punto de inicio
    
    # Crear la ruta con coordenadas
    route_with_coords = [{"name": loc, "coords": locations[loc]} for loc in path]
    
    return route_with_coords
