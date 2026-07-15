#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Construit les données de la page « Récolte & Métiers » (metiers.html) à partir
# de la knowledge base — étape mécanique, sans IA, comme le BiS.
#
# Sortie (stdout) : un JSON compact { zones:[…], professions:[…] } prêt à être
# injecté dans metiers.html par inject_craft.py.
#
# Usage :  python3 scripts/build_craft.py <dossier data KB> > craft.json
# -----------------------------------------------------------------------------
import json, sys
from collections import defaultdict

DATA = sys.argv[1] if len(sys.argv) > 1 else '../wocc-knowledge-base/data'

def load(name, default):
    try:
        return json.load(open(f'{DATA}/{name}.json', encoding='utf-8'))
    except FileNotFoundError:
        return default

ITEMS   = load('ITEMS', {})
ZONES   = load('ZONES', [])
NODES   = load('GATHER_NODES', [])
FISH    = load('FISHING_TABLES', {})
RECIPES = load('ALL_RECIPES', [])

def iname(iid):
    it = ITEMS.get(iid)
    return it['name'] if isinstance(it, dict) and it.get('name') else iid

def iqual(iid):
    it = ITEMS.get(iid)
    return it.get('quality', 'common') if isinstance(it, dict) else 'common'

NODE_FR = {'ore': 'Minerai', 'wood': 'Bois', 'herb': 'Herbe'}
NODE_EN = {'ore': 'Ore', 'wood': 'Wood', 'herb': 'Herb'}
PROF_FR = {
    'weaponcrafting': 'Forge d’armes', 'armorcrafting': 'Forge d’armures',
    'tailoring': 'Couture', 'leatherworking': 'Travail du cuir',
    'cooking': 'Cuisine', 'alchemy': 'Alchimie', 'engineering': 'Ingénierie',
    'blacksmithing': 'Forge', 'jewelcrafting': 'Joaillerie', 'enchanting': 'Enchantement',
    'inscription': 'Calligraphie', 'mining': 'Minage', 'herbalism': 'Herboristerie',
    'skinning': 'Dépeçage',
}
PROF_EN = {
    'weaponcrafting': 'Weaponcrafting', 'armorcrafting': 'Armorcrafting',
    'tailoring': 'Tailoring', 'leatherworking': 'Leatherworking',
    'cooking': 'Cooking', 'alchemy': 'Alchemy', 'engineering': 'Engineering',
    'blacksmithing': 'Blacksmithing', 'jewelcrafting': 'Jewelcrafting', 'enchanting': 'Enchanting',
    'inscription': 'Inscription', 'mining': 'Mining', 'herbalism': 'Herbalism', 'skinning': 'Skinning',
}

# --- zones : ordre par niveau min, avec nœuds de récolte et table de pêche ----
zorder = sorted(ZONES, key=lambda z: (z.get('levelRange') or [99])[0])
zones_out = []
for z in zorder:
    zid = z['id']
    zn = [n for n in NODES if n.get('zoneId') == zid]
    fish = FISH.get(zid, [])
    if not zn and not fish:
        continue
    # nœuds groupés par type
    nodes = {}
    for t in ('ore', 'wood', 'herb'):
        pts = [n for n in zn if n.get('type') == t]
        if not pts:
            continue
        lvls = sorted({n.get('level') for n in pts if n.get('level') is not None})
        nodes[t] = {
            'fr': NODE_FR[t], 'en': NODE_EN[t], 'type': t,
            'count': len(pts),
            'levels': lvls,
            'pos': [{'x': n['pos']['x'], 'z': n['pos']['z']} for n in pts if n.get('pos')],
        }
    # pêche : poids -> pourcentage (on ignore l'entrée vide itemId=null)
    total = sum(e.get('weight', 0) for e in fish) or 1
    catches = []
    for e in fish:
        if not e.get('itemId'):
            continue
        catches.append({
            'name': iname(e['itemId']), 'q': iqual(e['itemId']), 'id': e['itemId'],
            'pct': round(100 * e.get('weight', 0) / total),
        })
    catches.sort(key=lambda c: -c['pct'])
    zones_out.append({
        'id': zid, 'name': z.get('name', zid),
        'range': z.get('levelRange'),
        'nodes': nodes, 'fishing': catches,
    })

# --- métiers : recettes groupées par profession, triées par niveau ------------
byprof = defaultdict(list)
for r in RECIPES:
    byprof[r.get('professionId', '?')].append(r)

prof_out = []
for pid in sorted(byprof, key=lambda p: PROF_FR.get(p, p)):
    recs = sorted(byprof[pid], key=lambda r: (r.get('level') or 0, iname(r.get('resultItemId', ''))))
    recipes = []
    for r in recs:
        rid = r.get('resultItemId')
        recipes.append({
            'result': iname(rid), 'q': iqual(rid), 'id': rid,
            'count': r.get('resultCount', 1),
            'level': r.get('level'),
            'trivial': r.get('trivialAt'),
            'reagents': [{'name': iname(rg['itemId']), 'q': iqual(rg['itemId']),
                          'id': rg['itemId'], 'count': rg.get('count', 1)}
                         for rg in r.get('reagents', [])],
        })
    prof_out.append({
        'id': pid, 'fr': PROF_FR.get(pid, pid), 'en': PROF_EN.get(pid, pid),
        'recipes': recipes,
    })

json.dump({'zones': zones_out, 'professions': prof_out},
          sys.stdout, ensure_ascii=False, indent=1)
