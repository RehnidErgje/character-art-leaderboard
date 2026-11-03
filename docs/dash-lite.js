// A small stand-in for the dashboard runtime the page was written for, so the
// same page runs as a plain static site. It gives the page what it uses:
//   dash.data(id)   a dataset (a JSON file listed in window.DASH_DATASETS) or a calc
//   dash.calc(id, {inputs, fn})
//   dash.draw(name, fn | {mount, update, unmount}) and dash.draw(name) to run it again
//   dash.onData(fn), dash.colors
// A dataset is fetched the first time something reads it, so only the shown
// game's files are downloaded. Drawings run after the page's scripts, again
// whenever data arrives, and for one element when its width changes.
(function () {
  const files = window.DASH_DATASETS || {};
  const loaded = new Map(); // id -> {status, data, message}
  const calcs = new Map(); // id -> {inputs, fn, last}
  const draws = new Map(); // name -> fn or {mount, update, unmount}
  const made = new WeakMap(); // element -> what mount returned
  const widths = new WeakMap(); // element -> last width it was drawn at
  const listeners = [];

  const rowsOf = (json) => (Array.isArray(json) ? json : json.rows || json.data || json.results || []);

  // while any file is on its way the page carries dash-loading (a spinner)
  let pending = 0;
  const busy = (step) => {
    pending += step;
    document.documentElement.classList.toggle('dash-loading', pending > 0);
  };
  const load = (id) => {
    loaded.set(id, { status: 'loading', data: [] });
    busy(1);
    fetch(files[id])
      .then((r) => { if (!r.ok) throw new Error(`${files[id]}: ${r.status}`); return r.json(); })
      .then((json) => { loaded.set(id, { status: 'ok', data: rowsOf(json) }); })
      .catch((error) => { loaded.set(id, { status: 'error', data: [], message: String(error) }); console.error(error); })
      .finally(() => { busy(-1); changed(); });
  };

  const calcData = (id) => {
    const calc = calcs.get(id);
    const ins = calc.inputs.map(data);
    const bad = ins.find((d) => d.status !== 'ok');
    if (bad) return { status: bad.status === 'error' ? 'error' : 'loading', data: [] };
    // worked out again only when an input changed
    if (!calc.last || ins.some((d, i) => d.data !== calc.last.inputs[i])) {
      calc.last = { inputs: ins.map((d) => d.data), result: { status: 'ok', data: calc.fn(...ins.map((d) => d.data)) } };
    }
    return calc.last.result;
  };

  function data(id) {
    if (calcs.has(id)) return calcData(id);
    if (!loaded.has(id)) {
      if (!(id in files)) return { status: 'missing', data: [] };
      load(id);
    }
    return loaded.get(id);
  }

  const runOn = (name, el) => {
    const spec = draws.get(name);
    if (!spec) return;
    widths.set(el, el.clientWidth);
    try {
      if (typeof spec === 'function') { spec(el); return; }
      if (!made.has(el)) made.set(el, spec.mount ? spec.mount(el) : {});
      if (spec.update) spec.update(el, made.get(el));
    } catch (error) {
      console.error(`drawing ${name}:`, error);
      if (typeof spec !== 'function' && made.has(el)) {
        try { if (spec.unmount) spec.unmount(el, made.get(el)); } catch (e) { /* already failing */ }
        made.delete(el);
      }
    }
  };
  const run = (name) => document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => runOn(name, el));

  const resize = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const el = entry.target;
      if (widths.has(el) && widths.get(el) !== el.clientWidth) runOn(el.dataset.draw, el);
    }
  });

  let queued = false;
  function changed() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      listeners.forEach((fn) => fn());
      draws.forEach((spec, name) => run(name));
    });
  }

  let started = false;
  const start = () => {
    started = true;
    document.querySelectorAll('[data-draw]').forEach((el) => resize.observe(el));
    changed();
  };

  window.dash = {
    colors: ['#4a7fd4', '#d97757', '#5aa469', '#c98a2b', '#8a63d2', '#d1567c', '#3aa0a8', '#8c8a80'],
    data,
    calc: (id, spec) => { calcs.set(id, { inputs: spec.inputs, fn: spec.fn, last: null }); },
    onData: (fn) => { listeners.push(fn); if (started) fn(); },
    draw: (name, spec) => {
      if (spec === undefined) { run(name); return; }
      draws.set(name, spec);
    },
    refresh: () => {},
  };
  // the page's scripts register everything first; drawing starts after them
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else setTimeout(start, 0);
})();
