// Nav interactivity, scroll reveal, typo persistence
(function(){
  // Apply persisted typo variant
  try {
    const typo = localStorage.getItem('cfld-typo') || 'editorial';
    document.documentElement.setAttribute('data-typo', typo);
  } catch(e) {}

  window.CFLD = {
    mountShell: function() {
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

      // Back to top button
      const backToTop = document.querySelector('.back-to-top');
      if (backToTop) {
        var toggleBackToTop = function() {
          backToTop.classList.toggle('visible', window.scrollY > 300);
        };
        window.addEventListener('scroll', toggleBackToTop, { passive: true });
        toggleBackToTop();
      }

      // Nav scroll effect
      const nav = document.querySelector('.nav');
      if (nav) {
        var onScroll = function() {
          nav.classList.toggle('scrolled', window.scrollY > 40);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
      }

      // Scroll reveal
      if ('IntersectionObserver' in window) {
        const obs = new IntersectionObserver(function(entries) {
          entries.forEach(function(e) {
            if (e.isIntersecting) {
              e.target.classList.add('in');
              obs.unobserve(e.target);
            }
          });
        }, { rootMargin: '0px 0px -80px 0px' });
        document.querySelectorAll('.reveal').forEach(function(el) {
          obs.observe(el);
        });
      } else {
        document.querySelectorAll('.reveal').forEach(function(el) {
          el.classList.add('in');
        });
      }
    }
  };
})();
