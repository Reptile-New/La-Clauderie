/* ============================================================================
   Badge « à jour de la version » — pages de contenu (Builds, PvP, Métiers).
   ----------------------------------------------------------------------------
   Chaque page déclare la version du jeu pour laquelle son contenu a été
   vérifié via l'attribut data-version de SA balise d'inclusion :

       <script src="assets/version.js" data-version="v0.28.0" defer></script>

   Le script compare cette version à la dernière entrée de patch-notes.json
   (la source de vérité du site, tenue à jour par la Routine de veille) et
   affiche un badge sous l'en-tête de la page :
     ✓ vert  — la page est à jour de la dernière version du jeu ;
     ⏳ orange — le jeu a avancé, la relecture est en cours (la Routine
                horaire s'en charge) : le lecteur sait quoi prendre avec des
                pincettes.

   Qui met à jour data-version ?
     - bis.html     → scripts/inject_bis.py (automatique, avec le recalcul) ;
     - pvp.html, metiers.html → la Routine éditoriale, après relecture
       (voir CLAUDE.md, procédure « nouvelle MAJ »).
   ============================================================================ */
(function () {
  'use strict';

  var script = document.currentScript;
  var pageV = script && script.getAttribute('data-version');
  if (!pageV) return;

  var lang = (localStorage.getItem('lang') === 'en') ? 'en' : 'fr';
  var root = /\/notes\//.test(location.pathname) ? '../' : '';

  function render(latest) {
    var head = document.querySelector('header.page, header.hero');
    if (!head) return;

    var css = document.createElement('style');
    css.textContent = [
      '.ver-badge { display: inline-flex; align-items: baseline; gap: 6px; margin: 14px 0 0;',
      '  font-family: var(--font-mono, monospace); font-size: 0.74rem; letter-spacing: 0.02em;',
      '  border: 1px solid color-mix(in srgb, var(--heal, #58c46a) 45%, transparent);',
      '  color: var(--heal, #58c46a); border-radius: 7px; padding: 4px 10px; }',
      '.ver-badge b { font-weight: 700; }',
      '.ver-badge.warn { border-color: color-mix(in srgb, var(--gold, #c8a04b) 55%, transparent);',
      '  color: var(--gold-bright, #e6c37a); }',
      '.ver-badge a { color: inherit; }'
    ].join('\n');
    document.head.appendChild(css);

    var el = document.createElement('p');
    el.className = 'ver-badge';
    if (latest && latest !== pageV) {
      el.className += ' warn';
      el.innerHTML = (lang === 'en'
        ? '⏳ Checked for <b>' + pageV + '</b> — the game is now on <b>' + latest + '</b>, review in progress. '
        : '⏳ Page vérifiée pour la <b>' + pageV + '</b> — le jeu est passé en <b>' + latest + '</b>, relecture en cours. ')
        + '<a href="' + root + 'patch-notes.html">' + (lang === 'en' ? 'See what changed' : 'Voir ce qui a changé') + '</a>';
    } else if (latest) {
      el.innerHTML = lang === 'en'
        ? '✓ Up to date with <b>' + latest + '</b> — the latest game version'
        : '✓ À jour de la <b>' + latest + '</b> — la dernière version du jeu';
    } else {
      // patch-notes.json injoignable : on affiche au moins la version vérifiée.
      el.innerHTML = (lang === 'en' ? 'Content checked for <b>' : 'Contenu vérifié pour la <b>') + pageV + '</b>';
    }
    head.appendChild(el);
  }

  fetch(root + 'patch-notes.json', { cache: 'no-cache' })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      var latest = d && d.versions && d.versions[0] && d.versions[0].version;
      render(latest || null);
    })
    .catch(function () { render(null); });
})();
