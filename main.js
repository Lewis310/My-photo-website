(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  var g = $('grid'), lb = $('lb'), items = [], flt = 'all', cur = 0, vis = [];

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function url(p) {
    return encodeURI(String(p)).replace(/'/g, '%27').replace(/"/g, '%22').replace(/\(/g, '%28').replace(/\)/g, '%29');
  }
  function bg(it) {
    if (it.img) return "center/cover no-repeat url('" + url(it.img) + "')";
    var c = it.g || ['#333', '#999'];
    return 'radial-gradient(ellipse at 30% 25%,' + c[1] + ',' + c[0] + ' 75%)';
  }

  function draw() {
    g.innerHTML = '';
    items.forEach(function (it, i) {
      var f = document.createElement('figure');
      f.className = 'tile rev in';
      f.dataset.c = it.c || '';
      f.dataset.i = i;
      var ratio = esc(it.r || '3/2');
      f.innerHTML = (it.img
        ? '<img class="ph" loading="lazy" decoding="async" src="' + esc(url(it.img)) + '" alt="' + esc(it.alt || it.t) + '" style="aspect-ratio:' + ratio + '">'
        : '<div class="ph" role="img" aria-label="' + esc(it.t) + '" style="aspect-ratio:' + ratio + ';background:' + bg(it) + '"></div>')
        + '<figcaption>' + esc(it.t) + (it.c ? ' — ' + esc(it.c) : '') + '</figcaption>';
      var im = f.querySelector('img');
      if (im && !it.r) im.onload = function () { it.r = im.naturalWidth + '/' + im.naturalHeight; im.style.aspectRatio = it.r; };
      f.classList.toggle('hide', flt !== 'all' && it.c !== flt);
      g.appendChild(f);
    });
  }

  function buildFilters() {
    var cats = [];
    items.forEach(function (it) { if (it.c && cats.indexOf(it.c) < 0) cats.push(it.c); });
    $('filters').innerHTML = ['all'].concat(cats).map(function (c) {
      return '<button data-f="' + esc(c) + '"' + (c === 'all' ? ' class="on"' : '') + '>' + (c === 'all' ? 'All' : esc(c)) + '</button>';
    }).join('');
  }
  $('filters').onclick = function (e) {
    var b = e.target.closest('button'); if (!b) return;
    [].forEach.call(this.children, function (x) { x.classList.remove('on'); });
    b.classList.add('on'); flt = b.dataset.f;
    [].forEach.call(g.children, function (t) { t.classList.toggle('hide', flt !== 'all' && t.dataset.c !== flt); });
  };

  function visible() { return [].slice.call(g.children).filter(function (t) { return !t.classList.contains('hide'); }); }
  function show(n) {
    vis = visible(); if (!vis.length) return;
    cur = (n + vis.length) % vis.length;
    var it = items[+vis[cur].dataset.i], p = $('lbph'), a = String(it.r || '3/2').split('/');
    p.style.background = bg(it);
    p.style.setProperty('--ar', it.r || '3/2');
    p.style.setProperty('--r', a[0] / (a[1] || 1));
    var rows = [['Location', it.loc], ['Date', it.date], ['Camera', it.cam], ['Settings', it.set]]
      .filter(function (r) { return r[1]; })
      .map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('');
    $('lbinfo').innerHTML = (it.c ? '<div class="cat">' + esc(it.c) + '</div>' : '') + '<h3>' + esc(it.t) + '</h3>'
      + (rows ? '<dl>' + rows + '</dl>' : '')
      + (it.story ? '<p>' + esc(it.story).replace(/\n/g, '<br>') + '</p>' : '');
  }
  g.onclick = function (e) {
    var t = e.target.closest('.tile'); if (!t) return;
    show(visible().indexOf(t)); lb.classList.add('open');
  };
  lb.onclick = function (e) {
    if (e.target.classList.contains('nx')) show(cur + 1);
    else if (e.target.classList.contains('pv')) show(cur - 1);
    else if (!e.target.closest('.lbin')) lb.classList.remove('open');
  };
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') lb.classList.remove('open');
    if (e.key === 'ArrowRight') show(cur + 1);
    if (e.key === 'ArrowLeft') show(cur - 1);
  });

  var io = new IntersectionObserver(function (es) {
    es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
  }, { threshold: .12 });
  document.querySelectorAll('.rev').forEach(function (el) { io.observe(el); });

  fetch('data.json').then(function (r) { return r.json(); }).then(function (d) {
    items = d.items || [];
    if (d.hero) $('top').style.background = 'linear-gradient(rgba(0,0,0,.3),rgba(0,0,0,.3)),' + bg({ img: d.hero });
    buildFilters(); draw();
  }).catch(function () {
    g.innerHTML = '<p>Could not load data.json. If you opened index.html straight from disk, run a local server (see README).</p>';
  });
})();
