"""
PLANTILLA -- no ejecutar como script independiente (python exportar_...py).

Copia el bloque de abajo como una CELDA NUEVA al final de
modelo_gcn_lstm.ipynb y ejecútala en el MISMO kernel donde ya corrieron
las celdas que construyen el grafo (grafo_iztapalapa, nodo_a_idx,
edge_index) y las que entrenan el modelo (modelo).

Por qué tiene que ser así y no un script aparte que reconstruya el
grafo por su cuenta: el orden de los nodos en nodo_a_idx (y por lo
tanto en edge_index) depende del orden de iteración de
grafo_iztapalapa.nodes() en esa corrida específica de OSMnx. Si el
dashboard reconstruyera el grafo de forma independiente (otra máquina,
otro momento, otra versión de OSMnx, o incluso el mismo query con datos
de OSM ligeramente distintos), no hay garantía de que el orden de nodos
coincida -- y si no coincide, los pesos entrenados (modelo.state_dict())
quedan aplicados a un edge_index que ya no corresponde a la misma
estructura, sin que eso se note como un error, solo como un modelo que
predice mal. Exportar todo junto, desde la misma sesión, elimina ese
riesgo por construcción.
"""

if __name__ == "__main__":
    raise SystemExit(
        "Este archivo es una plantilla para pegar en una celda de "
        "modelo_gcn_lstm.ipynb -- no está pensado para correr con `python "
        "exportar_despues_de_entrenar.py` directamente."
    )

# ================== A partir de aquí, pegar en la celda del notebook ==================

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

RUTA_DASHBOARD_DATA = Path(r"D:\Lic Ciencia de Datos\TT C5\dashboard\data")
RUTA_DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)

# 1) Coordenadas de cada nodo, en el MISMO orden que nodo_a_idx.
#    OSMnx guarda la longitud como 'x' y la latitud como 'y' en cada nodo.
filas_nodos = []
for nodo_id, idx in nodo_a_idx.items():
    datos_nodo = grafo_iztapalapa.nodes[nodo_id]
    filas_nodos.append({
        "nodo_id": nodo_id,
        "idx": idx,
        "lat": datos_nodo["y"],
        "lon": datos_nodo["x"],
    })
pd.DataFrame(filas_nodos).sort_values("idx").to_csv(
    RUTA_DASHBOARD_DATA / "nodos_grafo.csv", index=False
)

# 2) edge_index tal cual se usó para entrenar (ya en índices, no en
#    nodo_id originales de OSM).
np.save(RUTA_DASHBOARD_DATA / "edge_index.npy", edge_index.numpy())

# 3) Pesos del modelo entrenado.
torch.save(modelo.state_dict(), RUTA_DASHBOARD_DATA / "modelo_gcn_lstm.pt")

# 4) Metadatos mínimos para que el dashboard sepa con qué arquitectura y
#    ventana temporal se entrenó, sin tener que adivinarlo ni hardcodearlo.
metadatos = {
    "T": T,
    "gcn_hidden": 32,
    "lstm_hidden": 64,
    "n_nodos": len(nodo_a_idx),
    "n_aristas": int(edge_index.shape[1]),
}
with open(RUTA_DASHBOARD_DATA / "metadatos_modelo.json", "w") as f:
    json.dump(metadatos, f, indent=2)

print("Artefactos exportados a", RUTA_DASHBOARD_DATA)
