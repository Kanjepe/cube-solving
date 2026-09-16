'use strict';
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { join, resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { mkdirSync } = require('node:fs');
const { chromium } = require(process.env.CUBE_PLAYWRIGHT || 'playwright');
const rootPath = resolve(__dirname, '..');
const files = ['2x2/rubiks-2x2-guide.html', 'cube-solving.html'];
let browser;

before(async () => { browser = await chromium.launch({ headless: true, channel: 'msedge' }); });
after(async () => { if (browser) await browser.close(); });

async function open(file) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(join(rootPath, file)).href);
  await page.waitForSelector('.guide2.g2-ready', { state: 'attached' });
  if (file === 'cube-solving.html') await page.locator('.cubebtn[data-cube="a2"]').click();
  await page.waitForSelector('[data-g2-page="intro"]');
  return { context, page, errors };
}

async function go(page, name) {
  await page.locator('[data-g2-menu]').click();
  await page.locator('.g2-menu-list button').filter({ hasText: name }).click();
}

for (const file of files) {
  test(file + ': local help, optional Sune, persistence and step links', async () => {
    const { context, page, errors } = await open(file);
    try {
      assert.equal(await page.locator('[data-g2-page]:visible').count(), 1);
      assert.equal(await page.locator('nav.steps:visible').count(), 0);
      await page.locator('[data-g2-next]').click();
      assert.equal(await page.locator('[data-g2-page="1"]').isVisible(), true);
      await go(page, '2. Dzeltenā puse');
      const optional = page.locator('[data-g2-sune]');
      assert.equal(await optional.evaluate(node => node.open), false);
      assert.equal(await optional.locator('.alg').isVisible(), false);
      const algorithm = page.locator('[data-g2-page="2"] .alg').first();
      assert.equal(await algorithm.getAttribute('data-alg'), "R' D' R D");
      await algorithm.scrollIntoViewIfNeeded();
      const scrollBefore = await page.evaluate(() => window.scrollY);
      await algorithm.locator('button').first().click();
      assert.match(await page.locator('[data-g2-dialog-content]').innerText(), /Labā kārta/);
      await page.locator('[data-g2-close]').click();
      assert.equal(await page.evaluate(() => window.scrollY), scrollBefore);
      await page.locator('[data-g2-done="2"]').check();
      await page.reload();
      await page.waitForSelector('.guide2.g2-ready');
      assert.equal(await page.locator('[data-g2-page="2"]').isVisible(), true);
      assert.equal(await page.locator('[data-g2-done="2"]').isChecked(), true);
      const prefix = file === 'cube-solving.html' ? 'a2-' : '';
      await page.goto(pathToFileURL(join(rootPath, file)).href + '#' + prefix + 's3');
      await page.waitForSelector('[data-g2-page="3"]');
      await page.reload();
      await page.waitForSelector('[data-g2-page="3"]');
      assert.equal(await page.locator('[data-g2-page]:visible').count(), 1);
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': MIX and four longer scrambles use their actual lengths', async () => {
    const { context, page, errors } = await open(file);
    try {
      await go(page, 'Sajaukšana');
      for (let sequence = 0; sequence < 5; sequence += 1) {
        await page.locator('[data-g2-select]').selectOption(String(sequence));
        const moves = (await page.locator('[data-g2-scramble]:visible').getAttribute('data-g2-scramble')).split(' ');
        assert.equal(moves.length, sequence === 0 ? 10 : 25);
        assert.equal(await page.locator('[data-g2-scramble]:visible').count(), 1);
        for (let index = 0; index < moves.length; index += 1) {
          assert.equal(await page.locator('[data-g2-current]').innerText(), moves[index]);
          assert.equal(await page.locator('[data-g2-counter]').innerText(), 'Gājiens ' + (index + 1) + ' no ' + moves.length);
          await page.locator('[data-g2-move-next]').click();
        }
        assert.equal(await page.locator('[data-g2-current]').innerText(), '✓');
        assert.equal(await page.locator('[data-g2-move-next]').isDisabled(), true);
        await page.locator('[data-g2-move-back]').click();
        assert.equal(await page.locator('[data-g2-current]').innerText(), moves.at(-1));
      }
      await page.reload();
      await page.waitForSelector('.guide2.g2-ready');
      assert.equal(await page.locator('[data-g2-select]').inputValue(), '4');
      assert.equal(await page.locator('[data-g2-counter]').innerText(), 'Gājiens 25 no 25');
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': all pages fit phone widths and desktop', async () => {
    const { context, page, errors } = await open(file);
    try {
      for (const width of [320, 360, 390, 430, 1440]) {
        await page.setViewportSize({ width, height: 844 });
        for (const name of ['Pirms sākuma', '1. Baltais slānis', '2. Dzeltenā puse', '3. Stūri vietās', 'Sajaukšana']) {
          await go(page, name);
          await page.locator('[data-g2-page]:visible details:not([data-g2-sune])').evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
          const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
          assert.ok(scrollWidth <= width, width + 'px overflow on ' + name);
          const nav = await page.locator('.g2-bottom').boundingBox();
          assert.ok(nav.y >= 0 && nav.y + nav.height <= 844.5);
          for (const button of await page.locator('.g2-bottom button').all()) {
            assert.ok((await button.boundingBox()).height >= 44);
          }
          if (process.env.CUBE_SCREENSHOTS && ['Pirms sākuma', '2. Dzeltenā puse', '3. Stūri vietās'].includes(name)) {
            mkdirSync(process.env.CUBE_SCREENSHOTS, { recursive: true });
            const pageId = await page.locator('[data-g2-page]:visible').getAttribute('data-g2-page');
            await page.screenshot({ path: join(process.env.CUBE_SCREENSHOTS, (file === 'cube-solving.html' ? 'unified' : 'standalone') + '-' + width + '-' + pageId + '.png'), fullPage: true });
          }
        }
      }
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });
}

test('old four-step progress and links open the final step without a false solved checkmark', async () => {
  const { context, page, errors } = await open(files[0]);
  try {
    await page.evaluate(() => localStorage.setItem('cube2-beginner-v2', JSON.stringify({
      page: '4', done: { 1: true, 2: true, 3: true, 4: false }, practice: { sequence: 1, move: 7 }
    })));
    await page.reload();
    await page.waitForSelector('.guide2.g2-ready');
    assert.equal(await page.locator('[data-g2-page="3"]').isVisible(), true);
    assert.equal(await page.locator('[data-g2-done="3"]').isChecked(), false);
    assert.equal(await page.locator('[data-g2-done="2"]').isChecked(), true);
    assert.equal(await page.locator('[data-g2-location]').innerText(), '3. no 3 · Stūri vietās');
    assert.equal(await page.locator('[data-g2-next]').innerText(), 'Sajaukt →');
    assert.equal(await page.locator('[data-g2-white-recovery]').evaluate(node => node.open), false);
    assert.equal(await page.locator('[data-g2-page="3"] .g2-example:visible').count(), 2);
    await page.locator('[data-g2-done="3"]').check();
    await page.reload();
    await page.waitForSelector('.guide2.g2-ready');
    assert.equal(await page.locator('[data-g2-done="3"]').isChecked(), true);
    await go(page, 'Sajaukšana');
    assert.equal(await page.locator('[data-g2-counter]').innerText(), 'Gājiens 8 no 25');
    await page.locator('[data-g2-menu]').click();
    assert.equal(await page.locator('.g2-menu-list button').last().innerText(), 'Sajaukšana');
    await page.locator('[data-g2-close]').click();
    await page.goto(pathToFileURL(join(rootPath, files[0])).href + '#s4');
    await page.waitForSelector('[data-g2-page="3"]');
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});

test('2x2 and 3x3 keep independent state, dialogs and matching visual styles', async () => {
  const { context, page, errors } = await open('cube-solving.html');
  try {
    await go(page, '2. Dzeltenā puse');
    await page.locator('[data-g2-done="2"]').check();
    const style = selector => page.locator(selector).evaluate(node => {
      const css = getComputedStyle(node);
      return [css.fontFamily, css.fontSize, css.backgroundColor, css.borderRadius, css.padding];
    });
    const buttonStyle = await style('[data-g2-next]');
    const headingStyle = await style('[data-g2-page="2"] h2');
    await page.locator('.cubebtn[data-cube="a3"]').click();
    assert.equal(await page.locator('.g2-bottom').isVisible(), false);
    assert.deepEqual(await style('[data-g3-next]'), buttonStyle);
    assert.deepEqual(await style('[data-g3-page="intro"] h2'), headingStyle);
    await page.locator('[data-g3-next]').click();
    assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
    await page.locator('.cubebtn[data-cube="a2"]').click();
    assert.equal(await page.locator('[data-g2-page="2"]').isVisible(), true);
    assert.equal(await page.locator('[data-g2-done="2"]').isChecked(), true);
    await page.locator('.lvlbtn[data-level="pro"]').click();
    assert.equal(await page.locator('#a2-ortega').isVisible(), true);
    assert.equal(await page.locator('.g2-bottom').isVisible(), false);
    await page.locator('.cubebtn[data-cube="py"]').click();
    assert.equal(await page.locator('#panel-py').isVisible(), true);
    await page.locator('.cubebtn[data-cube="a2"]').click();
    await page.locator('.lvlbtn[data-level="beginner"]').click();
    await page.locator('[data-g2-page="2"] .alg button').first().click();
    // Simulate a programmatic mode change while help is open.
    await page.locator('.cubebtn[data-cube="a3"]').evaluate(node => node.click());
    assert.equal(await page.locator('[data-g2-dialog]').evaluate(node => node.open), false);
    assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});

test('2x2 recovers from corrupt stored JSON and a cursor past the end of MIX', async () => {
  const { context, page, errors } = await open(files[0]);
  try {
    for (const value of ['{broken', JSON.stringify({ page: 'invalid', practice: { sequence: 0, move: 25 } })]) {
      await page.evaluate(value => localStorage.setItem('cube2-beginner-v2', value), value);
      await page.reload();
      await page.waitForSelector('[data-g2-page="intro"]');
      await go(page, 'Sajaukšana');
      assert.equal(await page.locator('[data-g2-counter]').innerText(), 'Gājiens 1 no 10');
    }
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});
