# La Clauderie 🛡️

Site de la guilde francophone **La Clauderie** sur
[World of ClaudeCraft](https://worldofclaudecraft.com/).

Site statique (aucune dépendance, aucun build) : nouveautés du jeu, roster,
calendrier des events et recrutement.

## Pages

| Fichier | Rôle |
|---|---|
| `index.html` | Accueil : hero, nouveautés, roster, calendrier, recrutement |
| `patch-notes.html` | Notes de version complètes du jeu (briefing maître de guilde) |

## Gérer le contenu (roster, events, recrutement)

Tout se modifie **sans coder**, directement depuis GitHub :

1. Ouvre `index.html` sur GitHub et clique sur le crayon ✏️ (*Edit*).
2. Descends jusqu'au bloc balisé **« ZONE À MODIFIER »** (vers la fin du fichier).
3. Édite les listes `MEMBRES`, `EVENEMENTS` et `RECRUTEMENT` :
   - **Membres** — `role` : `"Tank"`, `"Heal"` ou `"DPS"` ; `rang` : `"Maître de guilde"`,
     `"Officier"`, `"Vétéran"`, `"Membre"` ou `"Recrue"`.
   - **Events** — `type` : `"Raid"`, `"Héroïque"`, `"PvP"` ou `"Social"`.
4. **Commit changes**. Le site se redéploie tout seul en ~1 min.

## Mise en ligne (GitHub Pages)

Une seule fois : **Settings → Pages → Build and deployment → Source : « GitHub Actions »**.

Le workflow `.github/workflows/deploy-pages.yml` publie ensuite le site à chaque
push sur `main`. L'adresse publique apparaît dans **Settings → Pages** :
`https://reptile-new.github.io/la-clauderie/`.

## Liens

- 🎮 Jeu : <https://worldofclaudecraft.com/>
- 💬 Discord officiel (salon **#france**) : <https://discord.gg/GjhnUsBtw>
- 📚 Codex WoCC : <https://github.com/Reptile-New/wocc-knowledge-base>
