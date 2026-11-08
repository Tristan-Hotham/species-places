/* Named for a place, living somewhere else: the map. The Inked World base map with every taxon named after a place
 * (drawn at the namesake place, coloured by whether GBIF records it in that country), its GBIF range box and the line
 * to it, and a second view of Latin place epithets (anglica, japonica...). Dr Tristan Hotham, Independent researcher,
 * 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const BASE = window.INKBASE;
  const V = '?v=20261108';
  const ENGINE = ['js/curated.js', 'js/ink-palette.js', 'js/ink-icons.js', 'js/ink-houses.js', 'js/ink-map.js', 'js/ink-extras.js'];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const VCOL = { yes: '#4F7A3A', no: '#B0301F', few: '#C9A86A', norecords: '#B8AE9C', nokey: '#B8AE9C', nocountry: '#B8AE9C', synonym: '#B8AE9C', excluded: '#B8AE9C' };
  const VLAB = { yes: 'recorded in the namesake country', no: 'not recorded in the namesake country', few: 'fewer than 5 records, none there',
    norecords: 'no GBIF records with coordinates', nokey: 'no GBIF match', nocountry: 'namesake has no country (open sea, Antarctica)',
    synonym: 'not tested: GBIF key is a synonym, with no records at home', excluded: 'not tested: wrong namesake link (hand check)' };
  let map = null, S = null, T = [], byQ = {}, EPP = [], mode = qs.get('view') === 'epithets' ? 'ep' : 'named', group = 'all', pop = null;

  document.getElementById('theme').addEventListener('click', () => {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme = dark ? 'light' : 'dark';
  });
  const ct = document.getElementById('cartouche');
  const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  function loadScripts(list) {
    return list.reduce((p, src) => p.then(() => new Promise((res, rej) => {
      const el = document.createElement('script'); el.src = BASE + src + V; el.onload = res; el.onerror = () => rej(new Error('script ' + src)); document.head.appendChild(el);
    })), Promise.resolve());
  }
  const cname = c => (S.iso[c] || c);
  const fc = f => ({ type: 'FeatureCollection', features: f });
  const gbifLink = k => k ? `<a href="https://www.gbif.org/species/${esc(k)}" target="_blank" rel="noopener">GBIF ${esc(k)}</a>` : '';
  const wdLink = q => `<a href="https://www.wikidata.org/wiki/${esc(q)}" target="_blank" rel="noopener">Wikidata ${esc(q)}</a>`;
  function topList(top, iso) {
    if (!top) return '<i>none</i>';
    const set = new Set(String(iso || '').split(' '));
    return top.split(' ').map(x => { const [c, n] = x.split(':'); return `${set.has(c) ? '<b>' : ''}${esc(cname(c))} ${(+n).toLocaleString('en-GB')}${set.has(c) ? '</b>' : ''}`; }).join(', ');
  }

  // ---------------- the named-after layer
  function namedFeatures() {
    return T.filter(t => group === 'all' || t.g === group).map((t, i) => ({ type: 'Feature', id: i, properties: { q: t.qid, v: t.v, o: t.v === 'no' ? 2 : t.v === 'yes' ? 1 : 0 },
      geometry: { type: 'Point', coordinates: [t.lon, t.lat] } }));
  }
  function lineFeatures() {
    const out = [];
    T.filter(t => t.v === 'no' && t.box && (group === 'all' || t.g === group)).forEach(t => {
      const b = t.box, la = Math.min(Math.max(t.lat, b[0]), b[1]), lo = Math.min(Math.max(t.lon, b[2]), b[3]);
      if (Math.abs(la - t.lat) + Math.abs(lo - t.lon) > 0.01) out.push({ type: 'Feature', properties: { q: t.qid }, geometry: { type: 'LineString', coordinates: [[t.lon, t.lat], [lo, la]] } });
    });
    return out;
  }
  function boxFeature(t) {
    if (!t || !t.box) return fc([]);
    const [a, b, c, d] = t.box;
    const ring = [[c, a], [d, a], [d, b], [c, b], [c, a]];
    const la = Math.min(Math.max(t.lat, a), b), lo = Math.min(Math.max(t.lon, c), d);
    return fc([{ type: 'Feature', properties: { k: 'box' }, geometry: { type: 'Polygon', coordinates: [ring] } },
      { type: 'Feature', properties: { k: 'line' }, geometry: { type: 'LineString', coordinates: [[t.lon, t.lat], [lo, la]] } }]);
  }
  function taxonHtml(t) {
    const share = t.share == null ? '' : `${t.share}% of records`;
    return `<b class="t"><i>${esc(t.name)}</i></b><div>${esc(S.groups.find(g => g[0] === t.g)?.[1] || '')}${t.family ? ' · ' + esc(t.family) : ''}</div>
      <table><tr><td>Named after</td><td>${esc(t.place)}${t.iso ? ' (' + esc(t.iso.split(' ').slice(0, 3).map(cname).join(', ')) + ')' : ''}</td></tr>
      <tr><td>Verdict</td><td><span class="vd" style="background:${VCOL[t.v]}"></span>${esc(VLAB[t.v])}</td></tr>
      ${t.note ? `<tr><td>Note</td><td>${esc(t.note)}</td></tr>` : ''}
      ${t.n > 0 ? `<tr><td>GBIF records</td><td>${t.n.toLocaleString('en-GB')}${share ? ', ' + share + ' in the namesake country' : ''}</td></tr>
      <tr><td>Most records</td><td>${topList(t.top, t.iso)}</td></tr>` : ''}</table>
      ${t.box ? '<p class="nt">The dashed box is the extent of GBIF records (whole degrees); the red line joins the namesake to it.</p>' : ''}
      <div class="lk">${wdLink(t.qid)}${gbifLink(t.gbif)}<a href="https://www.wikidata.org/wiki/${esc(t.pq)}" target="_blank" rel="noopener">The place</a></div>`;
  }
  function showTaxon(t, fly) {
    closePop();
    map.getSource('sel').setData(boxFeature(t));
    pop = new maplibregl.Popup({ maxWidth: '320px', offset: 8, anchor: small ? 'bottom' : undefined, focusAfterOpen: false }).setLngLat([t.lon, t.lat]).setHTML(taxonHtml(t)).addTo(map);
    if (small) { map.easeTo({ center: [t.lon, t.lat], zoom: Math.max(map.getZoom(), 2.6), offset: [0, 200], duration: fly ? 900 : 300 }); }
    else if (fly && t.box) {
      const b = t.box; const w = Math.min(t.lon, b[2]), e = Math.max(t.lon, b[3]), s = Math.min(t.lat, b[0]), n = Math.max(t.lat, b[1]);
      if (e - w < 300) map.fitBounds([[w, s], [e, n]], { padding: small ? 40 : 120, maxZoom: 6, duration: 1200 });
    } else if (fly) map.flyTo({ center: [t.lon, t.lat], zoom: Math.max(map.getZoom(), 5), duration: 1200 });
    const u = new URL(location.href); u.searchParams.set('taxon', t.qid); history.replaceState(null, '', u);
  }
  function listHtml(ts) {
    const pl = ts[0].place;
    const order = { no: 0, yes: 1, few: 2, norecords: 3, nokey: 4, nocountry: 5, synonym: 6, excluded: 7 };
    ts = ts.slice().sort((a, b) => order[a.v] - order[b.v] || b.n - a.n);
    const k = ts.reduce((m, t) => (m[t.v] = (m[t.v] || 0) + 1, m), {});
    return `<b class="t">${esc(pl)}</b><div>${ts.length} taxa named after it here: ${k.yes || 0} recorded in the country, ${k.no || 0} not, ${ts.length - (k.yes || 0) - (k.no || 0)} not tested.</div>
      <ul class="tl">${ts.slice(0, 60).map(t => `<li><a href="#" data-q="${esc(t.qid)}"><span class="vd" style="background:${VCOL[t.v]}"></span><i>${esc(t.name)}</i></a>${t.n > 0 ? ' ' + t.n.toLocaleString('en-GB') : ''}</li>`).join('')}</ul>
      ${ts.length > 60 ? `<p class="nt">and ${ts.length - 60} more (search by name)</p>` : ''}`;
  }
  function closePop() { if (pop) { pop.remove(); pop = null; } }

  // ---------------- the epithet layer
  function epFeatures() {
    return EPP.map((p, i) => ({ type: 'Feature', id: i, properties: { i, s: p.share == null ? -1 : p.share, wd: p.wd, b: p.brit, l: p.place },
      geometry: { type: 'Point', coordinates: [p.lon, p.lat] } }));
  }
  function epHtml(p) {
    const ex = (S.ex[p.place] || []);
    const no = ex.filter(x => x[3] === 0), yes = ex.filter(x => x[3] > 0);
    return `<b class="t">${esc(p.place)}</b><div>Epithets: <i>${esc(p.stems.split(' ').join(', '))}</i></div>
      <table><tr><td>Wikidata taxa</td><td>${p.wd.toLocaleString('en-GB')}</td></tr>
      <tr><td>${p.brit ? 'Checked (all with a GBIF key)' : 'Checked (random sample)'}</td><td>${p.sampled}, of which ${p.assessed} have enough records</td></tr>
      <tr><td>Recorded in ${p.region ? 'the region' : 'the country'}</td><td>${p.share == null ? 'n/a' : p.yes + ' (' + p.share + '%)'}</td></tr>
      <tr><td>Counted as</td><td>${esc(p.iso.split(' ').map(cname).join(', '))}</td></tr></table>
      ${no.length ? `<p class="nt">Not recorded there (most GBIF records first):</p><ul class="tl">${no.slice(0, 12).map(x => `<li><a href="https://www.gbif.org/species/${esc(x[1])}" target="_blank" rel="noopener"><i>${esc(x[0])}</i></a> ${x[2].toLocaleString('en-GB')}: ${topList(x[4], '')}</li>`).join('')}</ul>` : ''}
      ${yes.length ? `<p class="nt">Recorded there, e.g. ${yes.slice(0, 4).map(x => '<i>' + esc(x[0]) + '</i>').join(', ')}.</p>` : ''}`;
  }

  // ---------------- view switching and filters
  function setMode(m) {
    mode = m; closePop(); map.getSource('sel').setData(fc([]));
    const named = m === 'named';
    ['pl', 'plines'].forEach(id => map.setLayoutProperty(id, 'visibility', named && (id !== 'plines' || document.getElementById('lyLines').checked) && document.getElementById('lyPts').checked ? 'visible' : 'none'));
    ['ep', 'epl'].forEach(id => map.setLayoutProperty(id, 'visibility', !named && document.getElementById('lyEp').checked ? 'visible' : 'none'));
    document.querySelectorAll('.chip[data-m]').forEach(b => b.setAttribute('aria-pressed', b.dataset.m === m));
    document.getElementById('grpRow').hidden = !named;
    document.querySelectorAll('.key').forEach(k => k.hidden = k.dataset.m !== m);
    const u = new URL(location.href); u.searchParams.set('view', named ? 'named' : 'epithets'); history.replaceState(null, '', u);
  }
  function setGroup(g) {
    group = g;
    map.getSource('pl').setData(fc(namedFeatures())); map.getSource('plines').setData(fc(lineFeatures()));
    document.getElementById('grp').value = g;
  }

  // ---------------- search
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    let items = [], k = -1;
    const show = () => {
      const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1;
      if (v.length < 2) { sug.style.display = 'none'; return; }
      const a = T.filter(t => norm(t.name).includes(v)).slice(0, 8).map(t => ({ t, lab: `<i>${esc(t.name)}</i> <span>after ${esc(t.place)}</span>` }));
      const places = [...new Set(T.filter(t => norm(t.place).includes(v)).map(t => t.place))].slice(0, 5).map(p => ({ p, lab: `${esc(p)} <span>namesake place</span>` }));
      const eps = EPP.filter(p => norm(p.place).includes(v) || norm(p.stems).includes(v)).slice(0, 4).map(p => ({ e: p, lab: `${esc(p.place)} <span>Latin epithet: ${esc(p.stems.split(' ')[0])}…</span>` }));
      items = places.concat(a, eps).slice(0, 14);
      items.forEach((it, i) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = it.lab;
        li.addEventListener('mousedown', e => { e.preventDefault(); pick(i); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none';
    };
    const pick = i => {
      const it = items[i]; if (!it) return; sug.style.display = 'none'; fold(true);
      if (it.t) { q.value = it.t.name; if (mode !== 'named') setMode('named'); if (group !== 'all') setGroup('all'); showTaxon(it.t, true); }
      else if (it.p) { q.value = it.p; if (mode !== 'named') setMode('named'); const ts = T.filter(t => t.place === it.p);
        map.flyTo({ center: [ts[0].lon, ts[0].lat], zoom: Math.max(map.getZoom(), 5), duration: 1200 }); showList(ts); }
      else if (it.e) { q.value = it.e.place; if (mode !== 'ep') setMode('ep'); map.flyTo({ center: [it.e.lon, it.e.lat], zoom: Math.max(map.getZoom(), 4), duration: 1200 }); showEp(it.e); }
    };
    q.addEventListener('input', show);
    q.addEventListener('keydown', e => {
      const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show(); pick(k < 0 ? 0 : k); }
      else if (e.key === 'Escape') sug.style.display = 'none';
    });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }
  function showList(ts) {
    if (ts.length === 1) { showTaxon(ts[0], false); return; }
    closePop(); map.getSource('sel').setData(fc([]));
    pop = new maplibregl.Popup({ maxWidth: '320px', offset: 8, anchor: small ? 'bottom' : undefined, focusAfterOpen: false }).setLngLat([ts[0].lon, ts[0].lat]).setHTML(listHtml(ts)).addTo(map);
    if (small) map.easeTo({ center: [ts[0].lon, ts[0].lat], zoom: Math.max(map.getZoom(), 2.6), offset: [0, 200], duration: 300 });
    pop.getElement().addEventListener('click', e => { const a = e.target.closest('a[data-q]'); if (a) { e.preventDefault(); showTaxon(byQ[a.dataset.q], true); } });
  }
  function showEp(p) {
    closePop();
    pop = new maplibregl.Popup({ maxWidth: '340px', offset: 10, anchor: small ? 'bottom' : undefined, focusAfterOpen: false }).setLngLat([p.lon, p.lat]).setHTML(epHtml(p)).addTo(map);
    if (small) map.easeTo({ center: [p.lon, p.lat], zoom: Math.max(map.getZoom(), 2.6), offset: [0, 200], duration: 300 });
  }

  // ---------------- layers
  function setupLayers() {
    const ins = (map.getStyle().layers.find(l => l.metadata && ['names'].includes(l.metadata.group)) || {}).id;
    map.addSource('pl', { type: 'geojson', data: fc(namedFeatures()), attribution: 'Taxa and namesakes: Wikidata (CC0) · Records: GBIF.org' });
    map.addSource('plines', { type: 'geojson', data: fc(lineFeatures()) });
    map.addSource('sel', { type: 'geojson', data: fc([]) });
    map.addSource('ep', { type: 'geojson', data: fc(epFeatures()) });
    map.addLayer({ id: 'plines', type: 'line', source: 'plines', paint: { 'line-color': '#B0301F', 'line-width': 1, 'line-opacity': 0.4, 'line-dasharray': [3, 2] } });
    if (small) document.getElementById('lyLines').checked = false;
    map.addLayer({ id: 'selbox', type: 'fill', source: 'sel', filter: ['==', ['get', 'k'], 'box'], paint: { 'fill-color': '#3C6C9C', 'fill-opacity': 0.12 } });
    map.addLayer({ id: 'selboxl', type: 'line', source: 'sel', filter: ['==', ['get', 'k'], 'box'], paint: { 'line-color': '#264A70', 'line-width': 1.6, 'line-dasharray': [3, 2] } });
    map.addLayer({ id: 'selline', type: 'line', source: 'sel', filter: ['==', ['get', 'k'], 'line'], paint: { 'line-color': '#B0301F', 'line-width': 2.4 } });
    map.addLayer({ id: 'pl', type: 'circle', source: 'pl', layout: { 'circle-sort-key': ['get', 'o'] },
      paint: { 'circle-color': ['match', ['get', 'v'], 'yes', VCOL.yes, 'no', VCOL.no, 'few', VCOL.few, '#B8AE9C'],
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, ['match', ['get', 'v'], 'no', 4, 2.6], 6, ['match', ['get', 'v'], 'no', 7, 5]],
        'circle-stroke-color': '#2B2119', 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 1, 0.5, 6, 1], 'circle-opacity': 0.9 } }, ins);
    map.addLayer({ id: 'ep', type: 'circle', source: 'ep', layout: { visibility: 'none', 'circle-sort-key': ['-', 0, ['get', 'wd']] },
      paint: { 'circle-color': ['step', ['get', 's'], '#B8AE9C', 0, '#B0301F', 70, '#D98A3A', 80, '#E7C25A', 90, '#8DAA5B', 99.95, '#4F7A3A'],
        'circle-radius': ['interpolate', ['linear'], ['sqrt', ['get', 'wd']], 3, 5, 40, 22], 'circle-stroke-color': '#2B2119',
        'circle-stroke-width': ['case', ['==', ['get', 'b'], 1], 2.2, 1], 'circle-opacity': 0.88 } });
    map.addLayer({ id: 'epl', type: 'symbol', source: 'ep', layout: { visibility: 'none', 'text-field': ['get', 'l'], 'text-font': ['Ink Italic'], 'text-size': 12,
      'text-offset': [0, 1.3], 'text-anchor': 'top', 'text-optional': true }, minzoom: 2.5, paint: { 'text-color': '#2B2119', 'text-halo-color': 'rgba(251,245,228,0.92)', 'text-halo-width': 1.5 } });
    map.on('click', 'pl', e => {
      const qsx = new Set(e.features.map(f => f.properties.q));
      const t0 = byQ[e.features[0].properties.q];
      const ts = T.filter(t => (group === 'all' || t.g === group) && t.lon === t0.lon && t.lat === t0.lat);
      showList(ts.length ? ts : [...qsx].map(q => byQ[q]));
    });
    map.on('click', 'ep', e => showEp(EPP[e.features[0].properties.i]));
    for (const id of ['pl', 'ep']) { map.on('mouseenter', id, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', id, () => map.getCanvas().style.cursor = ''); }
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', () => { const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.querySelectorAll('.chip[data-m]').forEach(b => b.addEventListener('click', () => setMode(b.dataset.m)));
    ['lyPts', 'lyLines', 'lyEp'].forEach(id => document.getElementById(id).addEventListener('change', () => setMode(mode)));
    const sel = document.getElementById('grp');
    S.groups.forEach(([k, n]) => { const o = document.createElement('option'); o.value = k; o.textContent = n; sel.appendChild(o); });
    sel.addEventListener('change', () => setGroup(sel.value));
    const boxes = [...lp.querySelectorAll('input[data-g]')], modern = document.getElementById('modern');
    const base = () => {
      const m = modern.checked;
      boxes.forEach(b => { const g = b.dataset.g; const inkOnly = ['mountains', 'forests', 'sea', 'tint'].includes(g); try { InkMap.setGroup(map, g, b.checked && !(m && inkOnly)); } catch (e) { } });
      try { InkMap.setGroup(map, 'paper', !m); InkMap.setGroup(map, 'modern', m); InkMap.setGroup(map, 'coast', !m); if (m) InkMap.setGroup(map, 'roads', false); } catch (e) { }
    };
    boxes.forEach(b => b.addEventListener('change', base)); modern.addEventListener('change', base); base();
    setMode(mode);
  }

  // ---------------- start
  fetch('data/site.json').then(r => r.json()).then(j => {
    S = j;
    T = j.pts.map(a => { const o = {}; j.fields.forEach((f, i) => o[f] = a[i]); o.qid = o.qid; return o; });
    T.forEach(t => byQ[t.qid] = t);
    EPP = j.ep.map(a => { const o = {}; j.ep_fields.forEach((f, i) => o[f] = a[i]); return o; });
    const opts = { base: BASE, winter: false };
    if (qs.get('tj')) opts.tilejson = qs.get('tj');
    if (qs.get('dem')) opts.dem = qs.get('dem');
    if (qs.get('demmax')) opts.demMax = +qs.get('demmax');
    const at = (qs.get('at') || '').split(',').map(Number);
    opts.mapOptions = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { center: [20, 25], zoom: small ? 0.6 : 1.6 };
    return loadScripts(ENGINE).then(() => InkMap.create('map', opts));
  }).then(m => {
    map = m; m.__inkWinter = false; window.__map = m;
    const n = document.getElementById('nojs'); if (n) n.remove();
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    m.once('idle', foldAt); m.on('resize', () => setTimeout(foldAt, 50)); setTimeout(foldAt, 1500);
    setupLayers(); setupSearch();
    if (qs.get('taxon') && byQ[qs.get('taxon')]) { setMode('named'); showTaxon(byQ[qs.get('taxon')], !qs.get('at')); }
    if (qs.get('place')) { const p = EPP.find(x => x.place === qs.get('place')); if (p) { setMode('ep'); showEp(p); } }
    const first = e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.mfs-btn,.maplibregl-ctrl')) return; fold(true); };
    document.getElementById('mapWrap').addEventListener('pointerdown', first, { capture: true, passive: true, once: true });
    document.querySelectorAll('a[data-go]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); setMode('named'); setGroup('all'); showTaxon(byQ[a.dataset.go], true); }));
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
