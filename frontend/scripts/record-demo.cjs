// Records the answers the web demo plays back (src/demo/data.json).
// 1. Fill an empty data folder with the invented sample data and start Groschen on it:
//      GROSCHEN_DATA=/tmp/demo python -m groschen.demo && GROSCHEN_DATA=/tmp/demo python -m groschen
// 2. Open http://localhost:8420, create the login alex / demo-password-123, skip the bank step.
// 3. node scripts/record-demo.cjs   (needs Playwright with Chromium)
// Then set RECORDED in src/demo/shim.ts to the day of the recording.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'http://localhost:8420';
const rec = {};
(async () => {
  const b = await chromium.launch();
  for (const lang of ['en', 'de']) {
    const ctx = await b.newContext({ viewport: { width: 1500, height: 950 }, locale: lang === 'de' ? 'de-DE' : 'en-GB' });
    const p = await ctx.newPage();
    p.on('response', async (r) => {
      const u = new URL(r.url());
      if (!u.pathname.startsWith('/api/') || r.request().method() !== 'GET' || r.status() !== 200) return;
      try { rec[`${lang} ${u.pathname.slice(4)}${u.search}`] = await r.json(); } catch {}
    });
    await p.goto(BASE + '/');
    await p.evaluate(async (lang) => {
      localStorage.setItem('groschen.lang', lang);
      await fetch('/api/login', { method: 'POST', headers: { 'content-type': 'application/json', 'x-groschen': '1' }, body: JSON.stringify({ username: 'alex', password: 'demo-password-123' }) });
    }, lang);
    const routes = ['/', '/transactions', '/spending', '/recurring', '/recurring?view=calendar', '/recurring?view=orbit', '/networth', '/investments', '/investments/forecast', '/investments/analysis', '/investments/payments', '/settings',
      '/investments/etf/IE00BK5BQT80', '/investments/etf/IE00BKM4GZ66', '/spending?flow=income'];
    await p.goto(BASE + '/'); await p.waitForTimeout(6000);
    const visit = async (u, ms = 1500) => { await p.evaluate((u) => { history.pushState(null, '', u); window.dispatchEvent(new Event('groschen:navigate')); }, u); await p.waitForTimeout(ms); };
    for (const preset of ['ytd', 'month', 'last30', 'year', 'last12', 'all']) {
      await p.evaluate((pr) => localStorage.setItem('groschen.period', JSON.stringify({ preset: pr })), preset); await p.goto(BASE + '/'); await p.waitForTimeout(6000);
      for (const r of routes) await visit(r);
    }
    await p.evaluate(() => localStorage.setItem('groschen.period', JSON.stringify({ preset: 'ytd' }))); await p.goto(BASE + '/'); await p.waitForTimeout(6000);
    // Drilldowns: every link-ish row on spending, and settings tabs.
    await visit('/spending');
        for (const g of ['Housing', 'Food & Dining', 'Transport', 'Shopping', 'Leisure & Travel', 'Subscriptions', 'Insurance', 'Personal', 'Uncategorized', 'Wohnen', 'Essen & Trinken', 'Mobilität', 'Einkaufen', 'Freizeit & Reisen', 'Abos', 'Versicherungen', 'Persönliches', 'Nicht kategorisiert'])
      await visit('/spending/group/' + encodeURIComponent(g));
    for (let c = 1; c <= 60; c++) await visit('/spending/category/' + c, 400);
        await visit('/settings');
    const tabs = await p.$$('.tabbar button, .tabs button, .tabs-bar button');
    for (let i = 0; i < tabs.length; i++) { const t = (await p.$$('.tabbar button, .tabs button, .tabs-bar button'))[i]; if (t) { await t.click({ timeout: 2000 }).catch(() => {}); await p.waitForTimeout(1200); } }
    await ctx.close();
  }
  // Login sessions would show this machine; the demo shows two invented ones instead.
  const fake = [
    { id: 2, current: true, created_at: '2026-10-28T18:12:00+00:00', last_seen: '2026-10-30T14:30:00+00:00', ip: '192.168.1.23', agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36', method: 'passkey' },
    { id: 1, current: false, created_at: '2026-10-20T07:45:00+00:00', last_seen: '2026-10-29T21:03:00+00:00', ip: '192.168.1.41', agent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1', method: 'password' },
  ];
  for (const k of Object.keys(rec)) if (k.split(' ')[1].startsWith('/sessions')) rec[k] = fake;
  fs.writeFileSync(process.argv[2] || 'src/demo/data.json', JSON.stringify(rec));
  console.log(Object.keys(rec).length, 'responses');
  await b.close();
})();
