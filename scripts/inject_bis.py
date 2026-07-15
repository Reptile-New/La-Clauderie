#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Injecte le BiS recalculé dans bis.html — étape mécanique, sans IA.
#
# Remplace le bloc « const BIS = { … }; » de bis.html par le JSON produit par
# compute_bis.py, et met à jour les libellés de version (« Patch vX.Y.Z » et
# « tag vX.Y.Z ») d'après data/_meta.json de la knowledge base.
#
# Usage :
#   python3 scripts/compute_bis.py <dossier data KB> > bis_new.json
#   python3 scripts/inject_bis.py <dossier data KB> bis.html bis_new.json
#
# Ne touche PAS aux mentions « (v0.25) » du guide de talents : celles-ci
# datent l'apparition d'un sort dans le jeu et doivent rester telles quelles.
# Seuls les libellés exacts « Patch vX.Y.Z » et « tag vX.Y.Z » sont bougés.
# -----------------------------------------------------------------------------
import sys, json, re

data_dir, html_path, bis_json_path = sys.argv[1], sys.argv[2], sys.argv[3]

tag = json.load(open(f"{data_dir}/_meta.json"))["tag"]
new_json = open(bis_json_path).read().rstrip("\n")
# Valide que c'est bien du JSON avant de l'injecter (évite d'écrire un bis.html cassé).
json.loads(new_json)

lines = open(html_path, encoding="utf-8").read().split("\n")
try:
    start = next(i for i, l in enumerate(lines) if l.startswith("const BIS = {"))
    end = next(i for i in range(start, len(lines)) if lines[i] == "};")
except StopIteration:
    sys.exit("inject_bis: bloc « const BIS = { … }; » introuvable dans " + html_path)

out_lines = lines[:start] + ("const BIS = " + new_json + ";").split("\n") + lines[end + 1:]

# Libellés de version : uniquement dans l'en-tête (avant « const BUILDS = »),
# là où vivent « Patch vX.Y.Z » (accroche) et « tag vX.Y.Z » (note méthodo).
# On ne touche NI aux « (v0.25) » du guide de talents (date d'apparition d'un
# sort), NI au commentaire de provenance des icônes (« tag v0.23.0 »), qui sont
# tous après ce point.
head_end = next((i for i, l in enumerate(out_lines) if l.startswith("const BUILDS = {")), len(out_lines))
for i in range(head_end):
    out_lines[i] = re.sub(r"Patch v\d+\.\d+\.\d+", f"Patch {tag}", out_lines[i])
    out_lines[i] = re.sub(r"tag v\d+\.\d+\.\d+", f"tag {tag}", out_lines[i])

open(html_path, "w", encoding="utf-8").write("\n".join(out_lines))
print(f"inject_bis: bis.html mis à jour sur {tag}")
