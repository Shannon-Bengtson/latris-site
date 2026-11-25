// Latris site script: shared by every page. Loaded with `defer`.
// Pages work without it: content is visible, the nav is shown expanded,
// and the release-notes form falls back to a mailto link.
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');

  // Old single-page anchors -> their new pages, so shared links keep working.
  var moved = {
    '#why': '/how-it-works/',
    '#owners': '/for-reviewers/',
    '#about': '/about/',
    '#builders': '/open-source/',
    '#contact': '/about/#contact',
    '#foundations': '/methods/'
  };
  if (location.pathname === '/' && moved[location.hash]) {
    location.replace(moved[location.hash]);
    return;
  }

  // Sticky-header style on scroll
  var header = document.querySelector('header.site');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Mobile menu
  var menuBtn = document.querySelector('.menu-btn');
  if (header && menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = header.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('open')) {
        header.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.focus();
      }
    });
  }

  // Reveal-on-scroll (skipped under reduced motion)
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');
  if (!reduce && 'IntersectionObserver' in window) {
    root.classList.add('reveal-on');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  // Copy buttons: <button data-copy="text">
  document.querySelectorAll('button[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy');
      var done = function () {
        var was = btn.textContent;
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = was; }, 1600);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });

  // Release-notes form (a mailing list; sign-up to the app itself is open).
  // Posts to Formspree; if FORM_ENDPOINT is empty it opens a pre-filled email.
  var FORM_ENDPOINT = 'https://formspree.io/f/xeaezvyd';
  // After a sign-up goes through, add one to Latris's own count of sign-ups (the
  // address stays with Formspree; the ping carries nothing). Best-effort: if it
  // fails, nothing changes for the visitor.
  var COUNT_ENDPOINT = 'https://telemetry.latris.app/v1/site/mailing-list';
  var upForm = document.getElementById('updates');
  if (!upForm) return;
  var upStatus = document.getElementById('up-status');
  var upEmail = document.getElementById('up-email');

  function upSay(msg, isErr) {
    upStatus.textContent = msg;
    upStatus.classList.toggle('err', !!isErr);
  }

  upForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var email = upEmail.value.trim();
    if (!upEmail.checkValidity() || !email) {
      upSay('Please enter a valid email address.', true);
      upEmail.focus();
      return;
    }
    if (upForm.elements._gotcha.value) return; // spam honeypot

    var btn = upForm.querySelector('button');
    btn.disabled = true;

    if (!FORM_ENDPOINT) {
      window.location.href = 'mailto:hello@latris.app?subject='
        + encodeURIComponent('Latris release notes')
        + '&body=' + encodeURIComponent('Please add ' + email + ' to the release notes.');
      upSay('Opening your email app…');
      btn.disabled = false;
      return;
    }

    upSay('Sending…');
    fetch(FORM_ENDPOINT, {
      method: 'POST',
      headers: { 'Accept': 'application/json' },
      body: new FormData(upForm)
    }).then(function (res) {
      if (res.ok) {
        try { if (navigator.sendBeacon) navigator.sendBeacon(COUNT_ENDPOINT); } catch (e) {}
        upForm.style.display = 'none';
        upSay('Got it, thanks! You\'ll hear when there\'s a release.');
      } else {
        btn.disabled = false;
        upSay('That didn\'t go through. Please try again or email hello@latris.app.', true);
      }
    }).catch(function () {
      btn.disabled = false;
      upSay('Network problem. Please try again or email hello@latris.app.', true);
    });
  });
})();
