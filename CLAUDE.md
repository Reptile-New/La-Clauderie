# Runbook — site de La Clauderie

Site statique de guilde pour *World of ClaudeCraft*. Déployé sur
**laclauderie.fr** (OVH) et GitHub Pages **à chaque push sur `main`**.

## ⚡ Quand l'utilisateur dit « il y a une nouvelle MAJ »

> **Normalement, même ça, c'est automatique** : une Routine Claude horaire
> (« Veille nouvelle version WoCC ») détecte toute version absente de
> `patch-notes.json` et déroule elle-même la procédure ci-dessous. Si
> l'utilisateur le demande à la main, c'est pour publier tout de suite sans
> attendre le prochain passage — même procédure. Avant de commencer, vérifier
> que la version n'est pas déjà en tête de `patch-notes.json` sur `origin/main`
> (la Routine est peut-être passée avant toi) ; si c'est le cas, ne rien refaire.

Tout le reste est automatisé (voir plus bas) — **ne le refais pas**. Ta tâche
se limite à la partie rédactionnelle des « Nouveautés » :

1. **Trouver le contenu de la version.** Récupérer les notes de version du jeu
   (`https://github.com/levy-street/world-of-claudecraft/releases/tag/vX.Y.Z`).
2. **Créer `notes/vX.Y.Z.html` + `notes/vX.Y.Z.en.html`** en copiant la structure
   EXACTE de la version la plus récente du dossier `notes/` (même `<style>`, même
   scaffolding modal, mêmes classes). N'adapter que : version, méta, hero,
   sections (bulles + fiches détaillées au clic) et le dict `DETAILS`.
   - Marquer les termes/objets/sorts/monstres cliquables avec
     `<span data-codex="type|Nom">…</span>` (types : `term|ability|item|mob|npc`).
     Vérifier que les noms existent dans `../wocc-knowledge-base/data/*.json`.
   - La page FR redirige vers `.en.html` si `lang=en` (et inversement) — garder
     les deux scripts de redirection en tête de fichier.
3. **Ajouter une entrée en tête de `patch-notes.json`** (version, date, titre,
   resume, temps_forts, page + variantes `_en` et `page_en`). L'accueil et la
   page Nouveautés se mettent à jour tout seuls à partir de ce fichier.
3bis. **Mettre à jour le guide « Spé & talents » (`const BUILDS` de `bis.html`)**
   pour les classes touchées par la MAJ : choix par rangée de talents (format
   `["Option", "niv. X", {fr, en}]`), maîtrise, rotation, astuce — en vérifiant
   chaque nom contre `TALENTS.json` / `ABILITIES.json` de la KB. C'est la
   partie ÉDITORIALE de la page Builds : le recalcul automatique ne couvre que
   le bloc `const BIS` (l'équipement). Si la MAJ ajoute un rôle à une classe
   (ex. Mage soigneur en v0.27.0), ajouter aussi ce rôle dans `ROLES` de
   `scripts/compute_bis.py` pour que l'onglet et le BiS existent.
4. **Commit sur `claude/site-update-6uhdmv`, puis merge direct sur `main`**
   (fast-forward : `git push origin claude/site-update-6uhdmv:main`). Le déploiement
   part tout seul. **Ne pas ouvrir de PR** sauf demande explicite.

### Si la MAJ vient de sortir (à la minute près)
Les robots (Codex + BiS) tournent sur cron ; pour publier tout d'un coup sans
attendre, forcer les workflows côté chaque repo :
- KB : onglet Actions → « Update WoCC knowledge base » → *Run workflow*.
- Site : onglet Actions → « Recalcul du BiS (Builds) » → *Run workflow*.
Puis vérifier que `wocc-knowledge-base/data/_meta.json` est bien sur le nouveau tag
avant de t'appuyer dessus pour le BiS ou les liens Codex.

## 🤖 Ce qui est DÉJÀ automatique — ne pas le refaire à la main

| Quoi | Mécanisme | Fréquence |
|---|---|---|
| Données du Codex | `wocc-knowledge-base` → `update-knowledge-base.yml` | ~5 min après chaque tag du jeu |
| **Builds / BiS** (`bis.html`) | `update-bis.yml` → `compute_bis.py` + `inject_bis.py` | toutes les 15 min (commit seulement si les données changent) |
| **Récolte & Métiers** (`metiers.html`) | `update-bis.yml` → `build_craft.py` + `inject_craft.py` | toutes les 15 min (idem) |
| **Rédaction des « Nouveautés »** | Routine Claude « Veille nouvelle version WoCC » (session fraîche qui suit la procédure ⚡ ci-dessus) | toutes les heures |
| Classement guilde (`guild.json`) | `update-guild-rank.yml` | toutes les 3 h |
| Déploiement (OVH + Pages) | `deploy-ovh.yml` / `deploy-pages.yml` | à chaque push `main` + 6 h |
| Rappel « version manquante » (filet de secours) | `check-game-version.yml` ouvre une issue | toutes les heures |

> Le **BiS est déterministe** : il ne se rédige pas, il se calcule. Ne jamais
> éditer le bloc `const BIS = {…}` de `bis.html` à la main — c'est
> `scripts/compute_bis.py` (données réelles de la KB) réinjecté par
> `scripts/inject_bis.py` qui le produit, et le workflow le refait tout seul.
>
> Idem pour **`metiers.html`** (Récolte & Métiers) : le bloc `const CRAFT = {…}`
> est produit par `scripts/build_craft.py` + `scripts/inject_craft.py` à partir
> de `GATHER_NODES`, `FISHING_TABLES`, `ALL_RECIPES` et `ZONES` de la KB. Ne pas
> l'éditer à la main. La page se suffit à elle-même (données embarquées) pour
> marcher aussi bien sur OVH que sur GitHub Pages (où `/data/` n'est pas servi).

## 🧭 La barre de navigation — source de vérité UNIQUE

Les onglets du site (Accueil, Builds, Métiers, Nouveautés, Codex) sont définis
**à un seul endroit** : `assets/nav.js` (tableau `TABS`). Toutes les pages —
`index.html`, `bis.html`, `metiers.html`, `patch-notes.html`, `notes/*.html` —
et **la page Codex** (`../wocc-knowledge-base/site/index.html`) partagent cette
liste. Pour ajouter / renommer / réordonner un onglet : **modifier uniquement
`assets/nav.js`**, jamais les barres page par page.

- Chaque page a juste `<nav class="topnav" data-guild-nav data-current="X"></nav>`
  (ou `class="gb-nav"` sur le Codex) que `nav.js` remplit. `data-current` = l'id
  de l'onglet actif. `nav.js` gère les chemins selon l'hôte (racine du domaine,
  Pages, `/codex/`, `notes/`) et préserve le bouton FR/EN existant.
- Le Codex charge `nav.js` depuis `https://laclauderie.fr/assets/nav.js` (une
  seule copie, servie par le déploiement du site) — donc il ne peut plus « rater »
  un nouvel onglet.

## Branche & déploiement
- Développer sur `claude/site-update-6uhdmv`, merger sur `main` (source du déploiement).
- La knowledge base (`Reptile-New/wocc-knowledge-base`, repo public) fournit `data/`
  (servi sous `/data/`) et `site/` (le Codex sous `/codex/`).

Détails des pages et des fiches Codex : voir `README.md`.
