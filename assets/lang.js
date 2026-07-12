/* ============================================================================
   Langue du site (FR / EN) — partagé par toutes les pages de La Clauderie.
   ----------------------------------------------------------------------------
   Le HTML est écrit en français ; la version anglaise de chaque texte statique
   est portée par l'attribut  data-en="…"  (ou  data-en-title  pour un title).
   Les noms du jeu (objets, quêtes, sorts, monstres…) restent en anglais dans
   les deux langues, comme dans le jeu.

   Le choix est mémorisé dans localStorage (clé « lang ») ; changer de langue
   recharge simplement la page. À charger AVANT le script de la page :
       <script src="assets/lang.js"></script>
   ============================================================================ */
(() => {
'use strict';

const LANG = localStorage.getItem('lang') === 'en' ? 'en' : 'fr';
window.LANG = LANG;
document.documentElement.lang = LANG;

/* T({fr:'…', en:'…'}) → texte dans la langue courante */
window.T = pair => pair[LANG];

/* pick(obj, 'titre') → obj.titre_en en anglais s'il existe, sinon obj.titre.
   Permet aux données (events.json, achievements.json, patch-notes.json…)
   de porter une traduction optionnelle champ par champ. */
window.pick = (obj, key) => (LANG === 'en' && obj[key + '_en']) ? obj[key + '_en'] : obj[key];

window.setLang = l => { localStorage.setItem('lang', l); location.reload(); };

/* Applique les data-en (le script est chargé en fin de body : le DOM est prêt). */
function applyLang(root) {
  if (LANG !== 'en') return;
  (root || document).querySelectorAll('[data-en]').forEach(el => {
    el.innerHTML = el.getAttribute('data-en');
  });
  (root || document).querySelectorAll('[data-en-title]').forEach(el => {
    el.title = el.getAttribute('data-en-title');
  });
}
window.applyLang = applyLang;

/* Bouton FR/EN dans la barre de navigation. */
function installLangButton() {
  const nav = document.querySelector('.topnav');
  if (!nav) return;
  const style = document.createElement('style');
  style.textContent = `
    .lang-btn { background: none; border: 1px solid color-mix(in srgb, var(--gold, #c8a04b) 40%, transparent);
      color: var(--gold, #c8a04b); font: 600 0.72rem/1 inherit; font-family: inherit; letter-spacing: 0.06em;
      padding: 5px 9px; border-radius: 7px; cursor: pointer; }
    .lang-btn:hover { color: var(--gold-bright, #e6c37a); border-color: var(--gold-bright, #e6c37a); }`;
  document.head.appendChild(style);
  const btn = document.createElement('button');
  btn.className = 'lang-btn';
  btn.type = 'button';
  btn.textContent = LANG === 'fr' ? 'EN' : 'FR';
  btn.title = LANG === 'fr' ? 'Switch this site to English' : 'Passer le site en français';
  btn.addEventListener('click', () => setLang(LANG === 'fr' ? 'en' : 'fr'));
  nav.appendChild(btn);
}

applyLang();
installLangButton();

})();
