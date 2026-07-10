# La Clauderie 🛡️

Site de la guilde francophone **La Clauderie** sur
[World of ClaudeCraft](https://worldofclaudecraft.com/).

Site statique, simple : un calendrier de guilde, le Discord, et les nouveautés du jeu.

## Pages

| Fichier | Rôle |
|---|---|
| `index.html` | Accueil : calendrier des events, Discord, recrutement, lien nouveautés |
| `admin.html` | Espace officiers : gérer le calendrier (ajout/suppression d'events) |
| `patch-notes.html` | Historique de **toutes** les mises à jour du jeu, la plus récente en premier |
| `notes/vX.Y.Z.html` | Les nouveautés détaillées d'une version (une page par mise à jour) |
| `patch-notes.json` | La liste des mises à jour (alimente l'historique **et** la carte de l'accueil) |
| `events.json` | Les données du calendrier (modifiées via l'espace officiers) |

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

## Gérer le calendrier (pour les officiers)

Tout se fait depuis **`admin.html`** (lien « Espace officiers » en bas du site),
avec un formulaire simple — **aucun code à toucher**.

### Créer sa clé d'accès (une fois, ~2 min)

L'espace officiers demande un **jeton GitHub fine-grained** pour pouvoir
enregistrer les changements :

1. [github.com → Fine-grained token](https://github.com/settings/personal-access-tokens/new)
   (connecté au compte qui a accès au repo).
2. **Repository access** → *Only select repositories* → **La-Clauderie**.
3. **Permissions** → *Repository* → **Contents** → **Read and write**.
4. Générer, copier le jeton, le coller dans l'espace officiers.

La clé est mémorisée sur l'appareil (option « rester connecté »). Chaque ajout ou
suppression est enregistré dans `events.json` et **le site se met à jour tout seul
en ~1 min**.

> Les events passés disparaissent automatiquement de l'accueil (seuls les events
> à venir sont affichés).

## Mise en ligne (GitHub Pages)

Déjà configuré. Le workflow `.github/workflows/deploy-pages.yml` publie le site à
chaque push sur `main`. Adresse publique :
`https://reptile-new.github.io/La-Clauderie/`.

## Liens

- 🎮 Jeu : <https://worldofclaudecraft.com/>
- 💬 Discord officiel (salon **#france**) : <https://discord.gg/GjhnUsBtw>
- 📚 Codex WoCC : <https://github.com/Reptile-New/wocc-knowledge-base>
