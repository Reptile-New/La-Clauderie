# La Clauderie 🛡️

Site de la guilde francophone **La Clauderie** sur
[World of ClaudeCraft](https://worldofclaudecraft.com/).

Site statique, simple : un calendrier de guilde, le Discord, et les nouveautés du jeu.

## Pages

| Fichier | Rôle |
|---|---|
| `index.html` | Accueil : Discord, guides, puis 3 onglets — Calendrier (à venir + passés), Membres, Faits d'armes |
| `admin.html` | Espace officiers : gérer le calendrier, les membres et les faits d'armes |
| `patch-notes.html` | Historique de **toutes** les mises à jour du jeu, la plus récente en premier |
| `notes/vX.Y.Z.html` | Les nouveautés détaillées d'une version (une page par mise à jour) |
| `patch-notes.json` | La liste des mises à jour (alimente l'historique **et** la carte de l'accueil) |
| `events.json` | Les données du calendrier (modifiées via l'espace officiers) |
| `members.json` | Les membres de la guilde : pseudo, rôle, classe (modifiés via l'espace officiers) |
| `achievements.json` | Les faits d'armes, avec les membres participants (modifiés via l'espace officiers) |

## Ajouter les nouveautés d'une mise à jour

À chaque nouvelle version du jeu, on ajoute ses nouveautés au site **sans toucher
aux versions précédentes** — l'historique se construit au fil du temps :

1. **Créer `notes/vX.Y.Z.html`** sur le modèle de la version la plus récente du
   dossier `notes/` : mêmes sections (bulles résumées + fiches détaillées au
   clic), avec le contenu de la nouvelle mise à jour.
2. **Ajouter une entrée en tête de `patch-notes.json`** : version, date, titre,
   résumé, temps forts, et le chemin `notes/vX.Y.Z.html`.

C'est tout : la page « Nouveautés du jeu » et la carte de l'accueil (qui affiche
toujours la dernière version) se mettent à jour automatiquement.

> **Rappel automatique** : le workflow `.github/workflows/check-game-version.yml`
> vérifie toutes les 6 h si une nouvelle version du jeu est sortie. Si ses
> nouveautés manquent sur le site, il ouvre une issue sur le repo pour le
> signaler (une seule par version).

## Gérer le calendrier, les membres et les faits d'armes (pour les officiers)

Tout se fait depuis **`admin.html`** (lien « Espace officiers » en bas du site),
avec des formulaires simples — **aucun code à toucher** : ajouter/modifier les
events du calendrier, la liste des membres (pseudo, rôle, classe), et les faits
d'armes en cochant les membres qui y ont participé.

> Les events passés ne disparaissent plus : ils restent visibles sur l'accueil
> dans la section « Événements passés », pour montrer l'activité de la guilde.

### Créer sa clé d'accès (une fois, ~2 min)

L'espace officiers demande un **jeton GitHub fine-grained** pour pouvoir
enregistrer les changements :

1. [github.com → Fine-grained token](https://github.com/settings/personal-access-tokens/new)
   (connecté au compte qui a accès au repo).
2. **Repository access** → *Only select repositories* → **La-Clauderie**.
3. **Permissions** → *Repository* → **Contents** → **Read and write**.
4. Générer, copier le jeton, le coller dans l'espace officiers.

La clé est mémorisée sur l'appareil (option « rester connecté »). Chaque
modification est enregistrée dans le fichier JSON correspondant (`events.json`,
`members.json` ou `achievements.json`) et **le site se met à jour tout seul en
~1 min**.

## Mise en ligne (GitHub Pages)

Déjà configuré. Le workflow `.github/workflows/deploy-pages.yml` publie le site à
chaque push sur `main`. Adresse publique :
`https://reptile-new.github.io/La-Clauderie/`.

## Liens

- 🎮 Jeu : <https://worldofclaudecraft.com/>
- 💬 Discord officiel (salon **#france**) : <https://discord.gg/GjhnUsBtw>
- 📚 Codex WoCC : <https://github.com/Reptile-New/wocc-knowledge-base>
