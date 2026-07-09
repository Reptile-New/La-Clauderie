# La Clauderie 🛡️

Site de la guilde francophone **La Clauderie** sur
[World of ClaudeCraft](https://worldofclaudecraft.com/).

Site statique, simple : un calendrier de guilde, le Discord, et les nouveautés du jeu.

## Pages

| Fichier | Rôle |
|---|---|
| `index.html` | Accueil : calendrier des events, Discord, recrutement, lien nouveautés |
| `admin.html` | Espace officiers : gérer le calendrier (ajout/suppression d'events) |
| `patch-notes.html` | Notes de version complètes du jeu (briefing maître de guilde) |
| `events.json` | Les données du calendrier (modifiées via l'espace officiers) |

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
