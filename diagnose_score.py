"""Diagnostic du score d'emergence."""
import sys, math, importlib
sys.path.insert(0, "src/repomix")

import verse_detector
importlib.reload(verse_detector)
from verse_detector import VERSE_DETECTOR

from adapters.known_repos_adapter import load_known_repos_graph
import networkx as nx
from pathlib import Path

G = load_known_repos_graph(Path("D:/DO/WEB/TOOLS/L0-CANON/GOVERNANCE-HUB/known_repositories.yaml"))

nb_noeuds = G.number_of_nodes()
nb_liens = G.number_of_edges()
degres = [d for n, d in G.degree()]
degre_moyen = sum(degres) / nb_noeuds if nb_noeuds else 0

connectivite = min(1.0, degre_moyen / 6)
noeuds_riches = sum(1 for n, a in G.nodes(data=True) if len(a) >= 3)
autoreference = noeuds_riches / nb_noeuds if nb_noeuds else 0
composantes = nx.number_connected_components(G)
fermeture = 1.0 / max(1, composantes)
scaling = math.log(nb_liens) / math.log(nb_noeuds) if nb_noeuds >= 2 else 0
non_linearite = min(1.0, max(0.0, scaling - 1.0))

score = connectivite * 0.4 + autoreference * 0.3 + fermeture * 0.2 + non_linearite * 0.1

print("Nodes: {}, Edges: {}".format(nb_noeuds, nb_liens))
print("Degre moyen: {:.2f}".format(degre_moyen))
print("  Connectivite:     {:.4f} x 0.4 = {:.4f}".format(connectivite, connectivite*0.4))
print("  Auto-reference:   {:.4f} x 0.3 = {:.4f}".format(autoreference, autoreference*0.3))
print("  Fermeture:        {:.4f} x 0.2 = {:.4f}".format(fermeture, fermeture*0.2))
print("  Non-linearite:    {:.4f} x 0.1 = {:.4f}".format(non_linearite, non_linearite*0.1))
print("  ---")
print("  SCORE TOTAL:      {:.4f} ({:.1f}%)".format(score, score*100))
print("  Statut:           {}".format(VERSE_DETECTOR.detect_status(score).name))
print("  Seuil BORN:       72.0%")
