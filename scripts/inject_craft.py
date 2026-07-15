#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Injecte les données de récolte/métiers dans metiers.html — mécanique, sans IA.
#
# Remplace TOUT le bloc de données « const CRAFT = …; » (de la ligne
# « const CRAFT = » jusqu'au </script> qui suit) par le JSON produit par
# build_craft.py. On remplace le bloc entier — pas une seule ligne — pour rester
# robuste si un formateur reformate le JSON sur plusieurs lignes (sinon une
# ré-injection laisserait l'ancien corps en place et casserait la page).
#
# Usage :
#   python3 scripts/build_craft.py <dossier data KB> > craft.json
#   python3 scripts/inject_craft.py metiers.html craft.json
# -----------------------------------------------------------------------------
import sys, json

html_path, craft_json_path = sys.argv[1], sys.argv[2]

new_json = open(craft_json_path, encoding="utf-8").read().strip()
json.loads(new_json)  # valide avant d'écrire (évite un metiers.html cassé)

lines = open(html_path, encoding="utf-8").read().split("\n")
start = next((i for i, l in enumerate(lines) if l.lstrip().startswith("const CRAFT = ")), None)
if start is None:
    sys.exit("inject_craft: ligne « const CRAFT = … » introuvable dans " + html_path)
# Fin du bloc = le </script> qui suit (les données JSON ne contiennent jamais
# la chaîne « </script> », donc le premier rencontré est le bon).
end = next((i for i in range(start, len(lines)) if lines[i].strip() == "</script>"), None)
if end is None:
    sys.exit("inject_craft: </script> de fermeture introuvable après const CRAFT")

lines[start:end] = ["const CRAFT = " + new_json + ";"]
open(html_path, "w", encoding="utf-8").write("\n".join(lines))
print("inject_craft: metiers.html mis à jour (bloc remplacé, {} → {})".format(start + 1, end + 1))
