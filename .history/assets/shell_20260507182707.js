// Shared nav, footer, scroll reveal, typo persistence
(function(){
  // Apply persisted typo
  try {
    const typo = localStorage.getItem('cfld-typo') || 'editorial';
    document.documentElement.setAttribute('data-typo', typo);
  } catch(e) {}

  function navHTML(active) {
    const links = [
      ['accueil', 'Accueil'],
      ['club.html', 'Le Club'],
      ['effectif.html', 'Effectif'],
      ['academie.html', 'Académie'],
      ['matchs.html', 'Matchs'],
      ['medias.html', 'Médias'],
      ['contact.html', 'Contact'],
    ];
    return `
      <nav class="nav">
        <div class="nav-inner">
          <a href="accueil.html" class="brand">
            <span class="brand-mark">C</span>
            <span>CFLD</span>
          </a>
          <div class="nav-links">
            ${links.map(([h,t]) => `<a href="${h}" class="${active===h?'active':''}">${t}</a>`).join('')}
          </div>
          <a href="inscription.html" class="nav-cta">S'inscrire</a>
          <button class="nav-toggle" aria-label="Ouvrir le menu" aria-expanded="false">
            <span></span><span></span><span></span>
          </button>
          <div class="nav-drawer">
            ${links.map(([h,t]) => `<a href="${h}" class="${active===h?'active':''}">${t}</a>`).join('')}
            <a href="inscription.html" class="nav-cta-drawer">S'inscrire</a>
          </div>
        </div>
      </nav>
    `;
  }

  function footerHTML() {
    return `
      <footer class="footer">
        <div class="footer-inner">
          <div>
            <p class="footer-mark">Club Football<br><em>La Différence</em></p>
            <p style="max-width: 36ch; color: rgba(246,244,239,0.65); font-size: 14px; line-height: 1.55;">
              Forger le talent africain de demain — sur le terrain et au-delà.
            </p>
          </div>
          <div>
            <h4>Le Club</h4>
            <ul>
              <li><a href="club.html">Histoire</a></li>
              <li><a href="club.html#staff">Staff</a></li>
              <li><a href="effectif.html">Effectif</a></li>
              <li><a href="academie.html">Académie</a></li>
            </ul>
          </div>
          <div>
            <h4>Activités</h4>
            <ul>
              <li><a href="matchs.html">Matchs</a></li>
              <li><a href="medias.html">Actualités</a></li>
              <li><a href="inscription.html">Inscription</a></li>
              <li><a href="admin.html">Admin</a></li>
            </ul>
          </div>
          <div>
            <h4>Contact</h4>
            <ul>
              <li>Abidjan, Côte d'Ivoire</li>
              <li>+225 07 00 00 00 00</li>
              <li>contact@cfld-club.ci</li>
              <li><a href="contact.html">Formulaire</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© 2026 Club Football La Différence</span>
          <span>Fondé en 2008 · Affilié FIF</span>
        </div>
      </footer>
    `;
  }

  function whatsappHTML() {
    return `
      <a href="contact.html" class="whatsapp-fab" aria-label="WhatsApp">
        <svg width="28" height="28" viewBox="0 0 32 32" fill="currentColor"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.4.7 4.6 1.9 6.5L4 29l7.7-1.9c1.8 1 3.9 1.5 6 1.5h.3C24.6 28.6 30 23.2 30 16.6 30 13.4 28.7 10.4 26.5 8.2 24.3 6 21.3 4.7 18.1 4.6 17.4 4.5 16.7 3 16 3zm0 23.1c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-3.7.9.9-3.6-.2-.4c-1-1.6-1.5-3.4-1.5-5.3 0-5.5 4.5-9.9 9.9-9.9s9.9 4.5 9.9 9.9c0 5.5-4.4 9.9-9.8 10zm5.4-7.4c-.3-.1-1.7-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.1-1.2-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6.1-.1.3-.4.4-.5.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5 0-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1.1 1-1.1 2.5s1.1 2.9 1.3 3.1c.2.2 2.2 3.3 5.3 4.7.7.3 1.3.5 1.8.6.7.2 1.4.2 2 .1.6-.1 1.7-.7 2-1.4.2-.7.2-1.2.2-1.4-.1-.2-.3-.2-.6-.4z"/></svg>
      </a>
    `;
  }

  window.CFLD = {
    mountShell: function(active) {
      const navMount = document.getElementById('nav-mount');
      const footMount = document.getElementById('footer-mount');
      const fabMount = document.getElementById('fab-mount');
      if (navMount) navMount.outerHTML = navHTML(active);
      if (footMount) footMount.outerHTML = footerHTML();
      if (fabMount) fabMount.outerHTML = whatsappHTML();

      // Hamburger toggle
      const toggle = document.querySelector('.nav-toggle');
      const drawer = document.querySelector('.nav-drawer');
      if (toggle && drawer) {
        toggle.addEventListener('click', function() {
          const isOpen = drawer.classList.toggle('open');
          toggle.classList.toggle('open', isOpen);
          toggle.setAttribute('aria-expanded', isOpen);
        });
        drawer.querySelectorAll('a').forEach(function(a) {
          a.addEventListener('click', function() {
            drawer.classList.remove('open');
            toggle.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
          });
        });
      }

      // Scroll reveal
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            obs.unobserve(e.target);
          }
        });
      }, { rootMargin: '0px 0px -80px 0px' });
      document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
    }
  };
})();
