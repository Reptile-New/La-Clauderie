#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Injecte les données de récolte/métiers dans metiers.html — mécanique, sans IA.
#
# Remplace la ligne « const CRAFT = …; » de metiers.html par le JSON produit par
# build_craft.py.
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
idx = next((i for i, l in enumerate(lines) if l.lstrip().startswith("const CRAFT = ")), None)
if idx is None:
    sys.exit("inject_craft: ligne « const CRAFT = …; » introuvable dans " + html_path)

lines[idx] = "const CRAFT = " + new_json + ";"
open(html_path, "w", encoding="utf-8").write("\n".join(lines))
print("inject_craft: metiers.html mis à jour")
