'use strict';
// Browser integration tests for the three Pro blocks (standalone and unified).
// Playwright may be supplied outside the repository via CUBE_PLAYWRIGHT.
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { join, resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.CUBE_PLAYWRIGHT || 'playwright');
const rootPath = resolve(__dirname, '..');
let browser;

const GUIDES = [
  { cube: 'a2', ns: 'g2p', root: 'guide2pro', file: '2x2/rubiks-2x2-guide.html', key: 'cube2-pro-v1', pages: 7, total: 52, wide: 'y', groupPage: '4', firstStep: 'Viena puse' },
  { cube: 'a3', ns: 'g3p', root: 'guide3pro', file: '3x3/rubiks-3x3-guide.html', key: 'cube3-pro-v1', pages: 8, total: 121, wide: 'r', groupPage: '3', firstStep: 'Krusts (Cross)' },
  { cube: 'py', ns: 'gpp', root: 'guidepypro', file: 'pyraminx/rubiks-pyraminx-guide.html', key: 'pyraminx-pro-v1', pages: 6, total: 7, wide: 'u', groupPage: null, firstStep: 'V forma' },
];
const WIDTHS = [320, 360, 390, 430, 1440];

before(async () => { browser = await chromium.launch({ headless: true, channel: 'msedge' }); });
after(async () => { if (browser) await browser.close(); });

function invert(alg) {
  return alg.trim().split(/\s+/).reverse().map(m => m.endsWith('2') ? m : (m.endsWith("'") ? m.slice(0, -1) : m + "'")).join(' ');
}

async function open(g, unified, width = 390) {
  const context = await browser.newContext({ viewport: { width, height: 844 }, deviceScaleFactor: 1, isMobile: width < 800, hasTouch: width < 800 });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(join(rootPath, unified ? 'cube-solving.html' : g.file)).href);
  await page.waitForSelector('.' + g.root + '.' + g.ns + '-ready', { state: 'attached' });
  if (unified) {
    await page.locator('.tabbtn[data-cube="' + g.cube + '"]').click();
    await page.locator('.tabbtn[data-level="pro"]').click();
  } else {
    await page.locator('#mb-pro').click();
  }
  await page.waitForSelector('body.' + g.ns + '-active');
  return { context, page, errors };
}

async function menuGo(page, g, text) {
  await page.locator('[data-' + g.ns + '-menu]').click();
  await page.locator('.' + g.ns + '-menu-list button').filter({ hasText: text }).first().click();
}

for (const g of GUIDES) {
  for (const unified of [false, true]) {
    const label = g.cube + (unified ? ' unified' : ' standalone');

    test(label + ': one page at a time, beginner and step nav hidden, bottom nav usable', async () => {
      const { context, page, errors } = await open(g, unified);
      try {
        assert.equal(await page.locator('[data-' + g.ns + '-page]:visible').count(), 1);
        assert.equal(await page.locator('nav.steps:visible').count(), 0);
        assert.equal(await page.locator('.mode-beginner:visible').count(), 0);
        const bottom = page.locator('.' + g.ns + '-bottom');
        assert.equal(await bottom.isVisible(), true);
        for (const b of await bottom.locator('button').all()) {
          const box = await b.boundingBox();
          assert.ok(box.height >= 44, 'button height ' + box.height);
        }
        assert.match(await page.locator('[data-' + g.ns + '-location]').innerText(), /Pirms sākuma/);
        await page.locator('[data-' + g.ns + '-next]').click();
        assert.equal(await page.locator('[data-' + g.ns + '-page="1"]').isVisible(), true);
        assert.match(await page.locator('[data-' + g.ns + '-location]').innerText(), /^1\. no \d · /);
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    });

    test(label + ': every page opens without horizontal overflow at all widths', async () => {
      for (const width of WIDTHS) {
        const { context, page, errors } = await open(g, unified, width);
        try {
          for (let i = 0; i < g.pages; i += 1) {
            const visible = page.locator('[data-' + g.ns + '-page]:visible');
            assert.equal(await visible.count(), 1);
            for (const d of await visible.locator('details').all()) await d.evaluate(el => { el.open = true; });
            const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
            assert.ok(overflow <= 1, width + 'px page ' + i + ' overflows by ' + overflow);
            const next = page.locator('[data-' + g.ns + '-next]');
            if (i < g.pages - 1) { assert.equal(await next.isDisabled(), false); await next.click(); }
            else assert.equal(await next.isDisabled(), true);
          }
          assert.deepEqual(errors, []);
        } finally { await context.close(); }
      }
    });

    test(label + ': move help explains new notation and restores scroll', async () => {
      const { context, page, errors } = await open(g, unified);
      try {
        const chip = page.locator('[data-' + g.ns + '-page="intro"] .alg button').filter({ hasText: new RegExp('^' + g.wide + '$') }).first();
        await chip.scrollIntoViewIfNeeded();
        const before = await page.evaluate(() => window.scrollY);
        await chip.click();
        const text = await page.locator('[data-' + g.ns + '-dialog-content]').innerText();
        assert.match(text, g.cube === 'py' ? /tikai mazo galu/ : (g.cube === 'a2' ? /Viss kubs/ : /divas kārtas/));
        await page.locator('[data-' + g.ns + '-close]').click();
        assert.equal(await page.evaluate(() => window.scrollY), before);
        await page.locator('[data-' + g.ns + '-help]').click();
        assert.match(await page.locator('[data-' + g.ns + '-dialog-content]').innerText(), /Apostrofs/);
        await page.locator('[data-' + g.ns + '-close]').click();
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    });

    test(label + ': learned state is shared between pages, counted in badges and saved', async () => {
      const { context, page, errors } = await open(g, unified);
      try {
        const total = page.locator('[data-' + g.ns + '-total]').first();
        assert.equal(await total.innerText(), '0 no ' + g.total);
        await menuGo(page, g, g.firstStep);
        await page.locator('[data-' + g.ns + '-done="1"]').check();
        // first case card of the block: open its page through the menu, tick it
        const firstCase = page.locator('.' + g.ns + '-case').first();
        const id = await firstCase.getAttribute('data-' + g.ns + '-case');
        const title = await firstCase.evaluate((el, ns) => el.closest('[data-' + ns + '-page]').getAttribute('data-' + ns + '-title'), g.ns);
        await menuGo(page, g, title);
        const boxes = page.locator('[data-' + g.ns + '-learned="' + id + '"]');
        const box = boxes.first();
        await box.evaluate(el => { const d = el.closest('details'); if (d) d.open = true; });
        await box.check();
        assert.equal(await total.evaluate(el => el.textContent), '1 no ' + g.total);
        if (g.groupPage) {
          const badge = page.locator('details:has([data-' + g.ns + '-learned="' + id + '"]) [data-' + g.ns + '-group-count]').first();
          if (await badge.count()) assert.match(await badge.evaluate(el => el.textContent), /^1 \/ \d+$/);
        }
        await page.reload();
        await page.waitForSelector('.' + g.root + '.' + g.ns + '-ready', { state: 'attached' });
        const stored = await page.evaluate(k => JSON.parse(localStorage.getItem(k)), g.key);
        assert.equal(stored.learned[id], true);
        assert.equal(stored.done['1'], true);
        assert.equal(await page.locator('[data-' + g.ns + '-total]').first().evaluate(el => el.textContent), '1 no ' + g.total);
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    });

    test(label + ': drill setup is the inverse of the revealed algorithm and learned round-trips', async () => {
      const { context, page, errors } = await open(g, unified);
      try {
        await menuGo(page, g, 'Algoritmu treniņš');
        const setup = await page.locator('[data-' + g.ns + '-drill-setup] button').allInnerTexts();
        assert.ok(setup.length > 0);
        assert.equal(await page.locator('[data-' + g.ns + '-drill-answer]').isVisible(), false);
        await page.locator('[data-' + g.ns + '-drill-reveal]').click();
        assert.equal(await page.locator('[data-' + g.ns + '-drill-answer]').isVisible(), true);
        const answer = await page.locator('[data-' + g.ns + '-drill-alg] button').allInnerTexts();
        assert.equal(setup.join(' '), invert(answer.join(' ')));
        const name = await page.locator('[data-' + g.ns + '-drill-name]').innerText();
        assert.ok(name.trim().length > 0);
        await page.locator('[data-' + g.ns + '-drill-learned]').check();
        assert.match(await page.locator('[data-' + g.ns + '-drill-progress]').innerText(), /apgūti 1 no \d+/);
        await page.reload();
        await page.waitForSelector('.' + g.root + '.' + g.ns + '-ready', { state: 'attached' });
        assert.equal(await page.locator('[data-' + g.ns + '-page="drill"]').isVisible(), true);
        assert.equal(await page.locator('[data-' + g.ns + '-drill-name]').innerText(), name);
        assert.equal(await page.locator('[data-' + g.ns + '-drill-learned]').isChecked(), true);
        await page.locator('[data-' + g.ns + '-drill-next]').click();
        assert.equal(await page.locator('[data-' + g.ns + '-drill-answer]').isVisible(), false);
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    });

    test(label + ': malformed storage recovers to the introduction', async () => {
      const { context, page, errors } = await open(g, unified);
      try {
        await page.evaluate(k => localStorage.setItem(k, '{"page":"__proto__","done":7,"learned":"x","drill":[]'), g.key);
        await page.reload();
        await page.waitForSelector('.' + g.root + '.' + g.ns + '-ready', { state: 'attached' });
        assert.equal(await page.locator('[data-' + g.ns + '-page="intro"]').isVisible(), true);
        await page.evaluate(k => localStorage.setItem(k, JSON.stringify({ page: 'nowhere', done: null, learned: null })), g.key);
        await page.reload();
        await page.waitForSelector('.' + g.root + '.' + g.ns + '-ready', { state: 'attached' });
        assert.equal(await page.locator('[data-' + g.ns + '-page="intro"]').isVisible(), true);
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    });
  }

  test(g.cube + ' unified: deep link opens the Pro page and level switch isolates modes', async () => {
    const { context, page, errors } = await open(g, true);
    try {
      const target = g.cube === 'a2' ? 'cll' : g.cube === 'a3' ? 'oll' : 'l4e';
      await page.goto(pathToFileURL(join(rootPath, 'cube-solving.html')).href + '#' + g.cube + '-' + target);
      await page.waitForSelector('#' + g.cube + '-' + target + ':visible');
      assert.equal(await page.locator('[data-' + g.ns + '-page]:visible').count(), 1);
      await page.locator('.tabbtn[data-level="beginner"]').click();
      assert.equal(await page.locator('body.' + g.ns + '-active').count(), 0);
      assert.equal(await page.locator('.' + g.root + ':visible').count(), 0);
      assert.equal(await page.locator('.mode-beginner:visible').count(), 1);
      await page.locator('.tabbtn[data-level="pro"]').click();
      await page.waitForSelector('body.' + g.ns + '-active');
      const other = GUIDES.find(o => o.cube !== g.cube);
      await page.locator('.tabbtn[data-cube="' + other.cube + '"]').click();
      assert.equal(await page.locator('body.' + g.ns + '-active').count(), 0);
      await page.waitForSelector('body.' + other.ns + '-active');
      assert.equal(await page.locator('.' + other.root + ':visible').count(), 1);
      assert.equal(await page.locator('.' + g.root + ':visible').count(), 0);
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(g.cube + ' standalone: Pro buttons and headings share the beginner block styling', async () => {
    const { context, page, errors } = await open(g, false);
    try {
      const begNs = g.cube === 'a2' ? 'g2' : g.cube === 'a3' ? 'g3' : 'gpy';
      const pro = await page.locator('.' + g.ns + '-bottom button').first().evaluate(el => { const s = getComputedStyle(el); return [s.fontSize, s.minHeight, s.borderRadius, s.fontFamily]; });
      const beg = await page.locator('.' + begNs + '-bottom button').first().evaluate(el => { const s = getComputedStyle(el); return [s.fontSize, s.minHeight, s.borderRadius, s.fontFamily]; });
      assert.deepEqual(pro, beg);
      const h2pro = await page.locator('.' + g.root + ' h2:visible').first().evaluate(el => { const s = getComputedStyle(el); return [s.fontSize, s.lineHeight, s.fontFamily]; });
      const h2beg = await page.locator('.' + begNs.replace('g', 'guide') + ' h2').first().evaluate(el => { const s = getComputedStyle(el); return [s.fontSize, s.lineHeight, s.fontFamily]; });
      assert.deepEqual(h2pro, h2beg);
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });
}
