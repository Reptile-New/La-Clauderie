#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Calcul du BiS (Best in Slot) de La Clauderie — avec bonus de sets.
#
# Toutes les formules sont portées du code du jeu (World of ClaudeCraft,
# tag v0.23.0, fichiers src/sim/entity.ts, types.ts, combat/auto_attack.ts,
# item_level.ts, equipment_rules.ts) :
#   - AP mêlée : guerrier/paladin/chaman/druide = 2×For ; voleur/chasseur =
#     For+Agi ; casters = For. AP distance (chasseur) = 2×Agi.
#   - Puissance des sorts = 0.5×Int + SP fixe des objets/sets.
#   - Crit = 5% + 0.05%/Agi + rating/10 (10 rating = 1%). Crit mêlée ×2,
#     crit sort ×1.5 (hypothèse classic, le multiplicateur exact des sorts
#     n'est pas dans les fichiers audités).
#   - Hâte = rating/10 en %. Accélère attaques ET incantations.
#   - Armure : gear + 2×Agi ; mitigation = armure/(armure + 85×20 + 400),
#     plafonnée à 75% (attaquant niveau 20).
#   - PV = baseHp + hpPerLevel×19 + End (20 premières ×1, ensuite ×10).
#   - Mana = baseMana + manaPerLevel×19 + Int (20 premières ×1, ensuite ×15).
#   - Swing = moyenne d'arme + AP/14×vitesse ; Auto Shot chasseur : 0.6×arme.
#   - Formes druide : ours (armure ×1.9, PV ×1.15, AP +15+1.5×Agi),
#     félin (AP +8+2×niveau, +10 Agi ; les dégâts de l'arme ne comptent pas).
#
# Les procs de set 4P sont valorisés en espérance (uptime estimée à partir de
# chance / ICD / durée et d'un rythme de coups réaliste) — détails en bas.
#
# Usage :  python3 compute_bis.py <dossier data de la knowledge base> > bis.json
# -----------------------------------------------------------------------------
import json, sys, itertools, copy

DATA = sys.argv[1] if len(sys.argv) > 1 else '../wocc-knowledge-base/data'
ITEMS = json.load(open(f'{DATA}/ITEMS.json'))
SETS = json.load(open(f'{DATA}/ITEM_SETS.json'))

LVL = 20
CLASSES = {
    'warrior': {'base': {'str':23,'agi':20,'sta':22,'int':10,'spi':11,'armor':50}, 'per': {'str':2,'agi':1,'sta':2,'int':0,'spi':0,'armor':12}, 'hp': (50,18), 'mana': (100,0)},
    'paladin': {'base': {'str':22,'agi':17,'sta':22,'int':13,'spi':14,'armor':45}, 'per': {'str':2,'agi':1,'sta':2,'int':1,'spi':1,'armor':12}, 'hp': (55,17), 'mana': (80,20)},
    'shaman':  {'base': {'str':18,'agi':16,'sta':20,'int':18,'spi':18,'armor':40}, 'per': {'str':1,'agi':1,'sta':2,'int':2,'spi':2,'armor':10}, 'hp': (48,15), 'mana': (90,22)},
    'druid':   {'base': {'str':15,'agi':15,'sta':17,'int':19,'spi':20,'armor':30}, 'per': {'str':1,'agi':1,'sta':2,'int':2,'spi':2,'armor':6},  'hp': (45,13), 'mana': (95,22)},
    'priest':  {'base': {'str':10,'agi':11,'sta':13,'int':22,'spi':24,'armor':20}, 'per': {'str':0,'agi':0,'sta':1,'int':2,'spi':3,'armor':4},  'hp': (38,11), 'mana': (110,26)},
    'mage':    {'base': {'str':10,'agi':12,'sta':14,'int':24,'spi':22,'armor':25}, 'per': {'str':0,'agi':0,'sta':1,'int':3,'spi':2,'armor':4},  'hp': (40,12), 'mana': (100,24)},
    'warlock': {'base': {'str':11,'agi':12,'sta':15,'int':21,'spi':21,'armor':22}, 'per': {'str':0,'agi':0,'sta':1,'int':3,'spi':2,'armor':4},  'hp': (42,12), 'mana': (105,25)},
    'rogue':   {'base': {'str':17,'agi':25,'sta':17,'int':11,'spi':12,'armor':40}, 'per': {'str':1,'agi':3,'sta':1,'int':0,'spi':0,'armor':8},  'hp': (45,15), 'mana': (100,0)},
    'hunter':  {'base': {'str':14,'agi':25,'sta':19,'int':13,'spi':14,'armor':45}, 'per': {'str':1,'agi':3,'sta':2,'int':1,'spi':1,'armor':8},  'hp': (50,15), 'mana': (80,18)},
}
ROLES = {
    'warrior': ['tank','dps'], 'paladin': ['tank','heal','dps'], 'shaman': ['heal','dps'],
    'druid': ['tank','heal','dps'], 'priest': ['heal','dps'], 'mage': ['dps'],
    'warlock': ['dps'], 'rogue': ['dps'], 'hunter': ['dps'],
}
MAIL = {'warrior','paladin','shaman'}; LEATHER = {'druid','rogue','hunter'}
ARMOR_RANK = {'cloth':0,'leather':1,'mail':2}
W_WAR = {'warrior','rogue','hunter','shaman','paladin'}
W_CAST = {'mage','priest','warlock','shaman','paladin','druid'}
W_ROGUE = {'rogue','hunter'}
SLOTS = ['mainhand','helmet','shoulder','chest','waist','legs','gloves','feet','neck','ring1','ring2']

def max_armor(cls): return 2 if cls in MAIL else 1 if cls in LEATHER else 0

# Port exact de canEquipItem (equipment_rules.ts) : pour une armure avec
# armorType, SEUL le rang d'armure compte (le jeu ignore requiredClass là-dessus,
# la mention de classe du tooltip est purement indicative). Les bijoux (pas
# d'armorType) et les armes hors groupes passent par requiredClass.
def can_equip(cls, it):
    at = it.get('armorType') if it.get('kind') == 'armor' else None
    rc = it.get('requiredClass')
    if at: return ARMOR_RANK[at] <= max_armor(cls)
    if it.get('kind') == 'weapon' and rc:
        s = set(rc)
        if s == W_WAR: return cls in W_WAR
        if s == W_CAST: return cls in W_CAST
        if s == W_ROGUE: return cls in W_ROGUE
    if rc: return cls in rc
    return True

def slot_key(it):
    return it.get('slot')

# --- feuille de personnage complète (port de recalcPlayerStats) --------------
def sheet(cls, role, equip):
    cd = CLASSES[cls]
    s = {k: cd['base'][k] + cd['per'][k]*(LVL-1) for k in ('str','agi','sta','int','spi','armor')}
    sp_flat = 0; crit_r = 0; haste_r = 0
    counts = {}
    for slot, iid in equip.items():
        if not iid: continue
        it = ITEMS[iid]
        if it.get('set'): counts[it['set']] = counts.get(it['set'],0)+1
        sp_flat += it.get('spellPower',0); crit_r += it.get('critRating',0); haste_r += it.get('hasteRating',0)
        for k,v in (it.get('stats') or {}).items():
            if k in s: s[k] += v
    ap_bonus = 0; procs = []
    for sid, n in counts.items():
        for b in SETS[sid]['bonuses']:
            if b['pieces'] <= n:
                e = b['effect']
                for k in ('str','agi','sta','int','spi'):
                    s[k] += e.get(k,0)
                sp_flat += e.get('sp',0); ap_bonus += e.get('ap',0)
                crit_r += e.get('critRating',0); haste_r += e.get('hasteRating',0)
                if 'proc' in e: procs.append(e['proc'])
    s['armor'] += 2*s['agi']
    bear = (cls=='druid' and role=='tank'); cat = (cls=='druid' and role=='dps')
    if bear:
        s['armor'] = round(s['armor']*1.9); ap_bonus += 15 + round(s['agi']*1.5)
    if cat:
        ap_bonus += 8 + 2*LVL; s['agi'] += max(2, LVL//2)
    ap_stats = (2*s['str'] if cls in ('warrior','paladin','shaman','druid')
                else s['str']+s['agi'] if cls in ('rogue','hunter') else s['str'])
    ap = max(0, ap_stats + ap_bonus)
    rap = max(0, 2*s['agi'] + ap_bonus) if cls=='hunter' else 0
    sp = max(0, round(s['int']*0.5 + sp_flat))
    crit = 0.05 + s['agi']*0.0005 + crit_r/1000
    haste = haste_r/1000
    hp = cd['hp'][0] + cd['hp'][1]*(LVL-1) + min(s['sta'],20) + max(0,s['sta']-20)*10
    if bear: hp = round(hp*1.15)
    mana = cd['mana'][0] + cd['mana'][1]*(LVL-1) + min(s['int'],20) + max(0,s['int']-20)*15
    w = ITEMS[equip['mainhand']]['weapon'] if equip.get('mainhand') and ITEMS[equip['mainhand']].get('weapon') else {'min':1,'max':2,'speed':2}
    return dict(stats=s, ap=ap, rap=rap, sp=sp, crit=crit, haste=haste, hp=hp, mana=mana, w=w, procs=procs, counts=counts)

# --- valorisation des procs de set (espérance, hypothèses documentées) -------
def proc_value(p, sh, kind):
    # rythme d'événements : mêlée ~1.6 coups d'arme/cycle de swing (blanc+jaune),
    # casters : un sort ~2.5 s.
    if p['trigger'] == 'weaponCrit':
        swings_per_s = (1+sh['haste']) * 1.6 / max(1.0, sh['w']['speed'])
        crit_events = swings_per_s * sh['crit'] * p.get('chance',1)
        ttp = 1/max(crit_events, 1e-9)
        period = p.get('icd',0) + ttp
        uptime = min(1.0, p.get('duration',0)/period) if p.get('aura','').startswith('buff') else 0
        if p['aura'] == 'buff_ap': return ('ap', p['value']*uptime)
        if p['aura'] == 'buff_haste': return ('haste', (p['value']-1)*uptime)
        if p['aura'] == 'dot':
            # dot moyen : monte en stacks si les crits s'enchaînent plus vite que 12 s
            stacks = min(p.get('maxStacks',1), max(1.0, p['duration']/max(ttp,1e-9)))
            return ('dps', p['value']/p['tickInterval']*min(1.0, stacks))
    if p['trigger'] == 'spellCast':
        cast_t = 2.5
        ttp = cast_t/max(p.get('chance',1),1e-9)
        period = max(p.get('icd',0), 0) + ttp
        if p['aura'] == 'buff_spellpower':
            return ('sp', p['value']*min(1.0, p.get('duration',0)/period))
        if p['aura'] == 'next_cast_free':
            return ('mana_pct', p.get('chance',1))  # ~10% d'économie de mana
    return ('none', 0)

# --- objectifs par rôle -------------------------------------------------------
def objective(cls, role, sh):
    bonus = {'ap':0,'sp':0,'haste':0,'dps':0,'mana_pct':0}
    for p in sh['procs']:
        k,v = proc_value(p, sh, role)
        if k in bonus: bonus[k]+=v
    crit=sh['crit']; haste=sh['haste']+bonus['haste']
    if role=='dps':
        if cls in ('mage','warlock') or (cls=='priest'):
            spd=(60+(sh['sp']+bonus['sp'])*0.714)/2.5*(1+haste)*(1+0.5*crit)
            return spd
        if cls=='hunter':
            w=sh['w']; avg=0.6*(w['min']+w['max'])/2
            per=avg+(sh['rap']+bonus['ap'])/14*w['speed']
            return (per/w['speed'])*(1+haste)*(1+crit)+bonus['dps']
        if cls=='druid':  # félin : l'arme ne compte que par ses stats
            return ((sh['ap']+bonus['ap'])/14)*(1+haste)*(1+crit)*3.0+bonus['dps']
        w=sh['w']; avg=(w['min']+w['max'])/2
        per=avg+(sh['ap']+bonus['ap'])/14*w['speed']
        return (per/w['speed'])*(1+haste)*(1+crit)+bonus['dps']
    if role=='tank':
        mit=min(0.75, sh['stats']['armor']/(sh['stats']['armor']+85*LVL+400))
        ehp=sh['hp']/(1-mit)
        w=sh['w']; avg=(w['min']+w['max'])/2
        threat=(avg+(sh['ap']+bonus['ap'])/14*w['speed'])/w['speed']*(1+haste)*(1+crit)
        return ehp + 6.0*threat   # l'EHP domine, la menace départage
    if role=='heal':
        hps=(80+(sh['sp']+bonus['sp'])*0.714)/2.5*(1+haste)*(1+0.5*crit)
        sustain=sh['mana']+15*sh['stats']['spi']
        sustain*= (1+bonus['mana_pct'])
        return hps*(0.7+0.3*sustain/2500)
    return 0

# --- candidats par slot --------------------------------------------------------
def candidates(cls, role):
    pool = {sl: [] for sl in SLOTS}
    for iid, it in ITEMS.items():
        sl = slot_key(it)
        if sl not in ('mainhand','helmet','shoulder','chest','waist','legs','gloves','feet','neck','ring'): continue
        if it.get('kind') not in ('armor','weapon'): continue
        if not can_equip(cls, it): continue
        if sl == 'ring':
            pool['ring1'].append(iid); pool['ring2'].append(iid)
        else:
            pool[sl].append(iid)
    return pool

def evaluate(cls, role, equip):
    return objective(cls, role, sheet(cls, role, equip))

def optimize(cls, role):
    pool = candidates(cls, role)
    # pièces de sets pertinentes pour la classe
    class_sets = {}
    for sid in SETS:
        pieces = [iid for iid,it in ITEMS.items() if it.get('set')==sid and can_equip(cls,it)]
        if len(pieces) >= 2: class_sets[sid]=pieces
    # configurations : pour chaque set, sous-ensembles de pièces (0 ou >=2)
    def subsets(pieces):
        out=[()]
        for r in range(2, len(pieces)+1):
            out += list(itertools.combinations(pieces, r))
        return out
    configs=[()]
    for sid, pieces in class_sets.items():
        configs=[c+s for c in configs for s in subsets(pieces)
                 if len(set(ITEMS[i]['slot'] for i in c+s))==len(c+s)]
    best=None
    for forced in configs:
        equip={sl:None for sl in SLOTS}
        used=set()
        ok=True
        for iid in forced:
            sl=ITEMS[iid]['slot']
            if sl=='ring':
                sl='ring1' if not equip['ring1'] else 'ring2' if not equip['ring2'] else None
            if sl is None or equip[sl]: ok=False; break
            equip[sl]=iid; used.add(iid)
        if not ok: continue
        # remplissage glouton multi-passes des slots libres
        free=[sl for sl in SLOTS if not equip[sl]]
        for sl in free:
            bs=None
            for iid in pool[sl]:
                if iid in used: continue
                equip[sl]=iid
                v=evaluate(cls,role,equip)
                if bs is None or v>bs[0]: bs=(v,iid)
            equip[sl]=bs[1] if bs else None
            if bs: used.add(bs[1])
        for _ in range(4):  # passes de raffinement (slots libres uniquement)
            changed=False
            for sl in free:
                cur=equip[sl]
                bs=(evaluate(cls,role,equip),cur)
                for iid in pool[sl]:
                    if iid==cur or iid in used: continue
                    equip[sl]=iid
                    v=evaluate(cls,role,equip)
                    if v>bs[0]+1e-9: bs=(v,iid)
                equip[sl]=bs[1]  # TOUJOURS restaurer le meilleur (bug: le slot restait sur le dernier essayé)
                if bs[1]!=cur:
                    used.discard(cur); used.add(bs[1]); changed=True
            if not changed: break
        v=evaluate(cls,role,equip)
        if best is None or v>best[0]: best=(v,dict(equip))
    # alternatives : meilleur remplaçant par slot dans le build final
    score, equip = best
    alts={}
    for sl in SLOTS:
        cur=equip[sl]; bs=None
        for iid in pool[sl]:
            if iid==cur or iid in equip.values(): continue
            e2=dict(equip); e2[sl]=iid
            v=evaluate(cls,role,e2)
            if bs is None or v>bs[0]: bs=(v,iid)
        if bs: alts[sl]=bs[1]
    return score, equip, alts

def item_export(iid, cls):
    it=ITEMS[iid]
    # itemScore du jeu (item_level.ts) : stats primaires + armure/12 + DPS×0.5
    sc=sum(v for k,v in (it.get('stats') or {}).items() if k!='armor')
    sc+=(it.get('stats') or {}).get('armor',0)/12
    if it.get('weapon'):
        w=it['weapon']; sc+=(w['min']+w['max'])/2/w['speed']*0.5
    return {
        'name': it['name'], 'q': it.get('quality','common'),
        'set': SETS[it['set']]['name'] if it.get('set') else None,
        'stats': it.get('stats') or {}, 'w': it.get('weapon'),
        'sp': it.get('spellPower'), 'id': iid, 'score': round(sc,1),
        'xclass': bool(it.get('armorType') and it.get('requiredClass') and cls not in it['requiredClass']),
    }

FR={'warrior':'Guerrier','paladin':'Paladin','shaman':'Chaman','druid':'Druide','priest':'Prêtre','mage':'Mage','warlock':'Démoniste','rogue':'Voleur','hunter':'Chasseur'}
out={}
for cls in ROLES:
    out[cls]={'fr':FR[cls],'roles':{}}
    for role in ROLES[cls]:
        score,equip,alts=optimize(cls,role)
        sh=sheet(cls,role,equip)
        setline=[]
        for sid,n in sorted(sh['counts'].items()):
            reached=[b['pieces'] for b in SETS[sid]['bonuses'] if b['pieces']<=n]
            if reached: setline.append({'name':SETS[sid]['name'],'pieces':n,'bonus':max(reached)})
        picks={}
        for sl in SLOTS:
            iid=equip[sl]
            if not iid: continue
            entry={"best":item_export(iid, cls)}
            if sl in alts:
                e2=dict(equip); e2[sl]=alts[sl]
                entry["alt"]=item_export(alts[sl], cls)
            picks[sl]=entry
        out[cls]['roles'][role]={'picks':picks,'sets':setline,'score':round(score,1)}
        print(f"{cls}/{role}: score={score:.1f} sets={[(s['name'],s['pieces']) for s in setline]}", file=sys.stderr)
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
