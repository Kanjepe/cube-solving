'use strict';
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { join, resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { mkdirSync } = require('node:fs');
const { chromium } = require(process.env.CUBE_PLAYWRIGHT || 'playwright');
const rootPath = resolve(__dirname, '..');
const files = ['pyraminx/rubiks-pyraminx-guide.html', 'cube-solving.html'];
let browser;

before(async () => { browser = await chromium.launch({ headless: true, channel: 'msedge' }); });
after(async () => { if (browser) await browser.close(); });

async function open(file) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(join(rootPath, file)).href);
  await page.waitForSelector('.guidepy.gpy-ready', { state: 'attached' });
  if (file === 'cube-solving.html') await page.locator('.cubebtn[data-cube="py"]').click();
  await page.waitForSelector('[data-gpy-page="intro"]');
  return { context, page, errors };
}

async function go(page, name) {
  await page.locator('[data-gpy-menu]').click();
  await page.locator('.gpy-menu-list button').filter({ hasText: name }).click();
}

for (const file of files) {
  test(file + ': local help, persistence and step links', async () => {
    const { context, page, errors } = await open(file);
    try {
      assert.equal(await page.locator('[data-gpy-page]:visible').count(), 1);
      assert.equal(await page.locator('nav.steps:visible').count(), 0);
      await page.locator('[data-gpy-next]').click();
      assert.equal(await page.locator('[data-gpy-page="1"]').isVisible(), true);
      await go(page, '2. Zaļais slānis');
      const algorithm = page.locator('[data-gpy-page="2"] .alg').first();
      assert.equal(await algorithm.getAttribute('data-alg'), "R U' R'");
      await algorithm.scrollIntoViewIfNeeded();
      const scrollBefore = await page.evaluate(() => window.scrollY);
      await algorithm.locator('button').first().click();
      assert.match(await page.locator('[data-gpy-dialog-content]').innerText(), /Labā virsotne/);
      await page.locator('[data-gpy-close]').click();
      assert.equal(await page.evaluate(() => window.scrollY), scrollBefore);
      await page.locator('[data-gpy-done="2"]').check();
      await page.reload();
      await page.waitForSelector('.guidepy.gpy-ready');
      assert.equal(await page.locator('[data-gpy-page="2"]').isVisible(), true);
      assert.equal(await page.locator('[data-gpy-done="2"]').isChecked(), true);
      const prefix = file === 'cube-solving.html' ? 'py-' : '';
      await page.goto(pathToFileURL(join(rootPath, file)).href + '#' + prefix + 's3');
      await page.waitForSelector('[data-gpy-page="3"]');
      await page.reload();
      await page.waitForSelector('[data-gpy-page="3"]');
      assert.equal(await page.locator('[data-gpy-page]:visible').count(), 1);
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': Five scrambles use their actual lengths', async () => {
    const { context, page, errors } = await open(file);
    try {
      await go(page, 'Sajaukšana');
      for (let sequence = 0; sequence < 5; sequence += 1) {
        await page.locator('[data-gpy-select]').selectOption(String(sequence));
        const moves = (await page.locator('[data-gpy-scramble]:visible').getAttribute('data-gpy-scramble')).split(' ');
        assert.equal(moves.length, sequence === 0 ? 8 : 12);
        assert.equal(await page.locator('[data-gpy-scramble]:visible').count(), 1);
        for (let index = 0; index < moves.length; index += 1) {
          assert.equal(await page.locator('[data-gpy-current]').innerText(), moves[index]);
          assert.equal(await page.locator('[data-gpy-counter]').innerText(), 'Gājiens ' + (index + 1) + ' no ' + moves.length);
          await page.locator('[data-gpy-move-next]').click();
        }
        assert.equal(await page.locator('[data-gpy-current]').innerText(), '✓');
        assert.equal(await page.locator('[data-gpy-move-next]').isDisabled(), true);
        await page.locator('[data-gpy-move-back]').click();
        assert.equal(await page.locator('[data-gpy-current]').innerText(), moves.at(-1));
      }
      await page.reload();
      await page.waitForSelector('.guidepy.gpy-ready');
      assert.equal(await page.locator('[data-gpy-select]').inputValue(), '4');
      assert.equal(await page.locator('[data-gpy-counter]').innerText(), 'Gājiens 12 no 12');
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': all pages fit phone widths and desktop', async () => {
    const { context, page, errors } = await open(file);
    try {
      for (const width of [320, 360, 390, 430, 1440]) {
        await page.setViewportSize({ width, height: 844 });
        for (const name of ['Pirms sākuma', '1. Stūri un gali', '2. Zaļais slānis', '3. Pēdējās 3 malas', 'Sajaukšana']) {
          await go(page, name);
          await page.locator('[data-gpy-page]:visible details').evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
          const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
          assert.ok(scrollWidth <= width, width + 'px overflow on ' + name);
          const nav = await page.locator('.gpy-bottom').boundingBox();
          assert.ok(nav.y >= 0 && nav.y + nav.height <= 844.5);
          for (const button of await page.locator('.gpy-bottom button').all()) {
            assert.ok((await button.boundingBox()).height >= 44);
          }
          if (process.env.CUBE_SCREENSHOTS && ['Pirms sākuma', '2. Zaļais slānis', '3. Pēdējās 3 malas'].includes(name)) {
            mkdirSync(process.env.CUBE_SCREENSHOTS, { recursive: true });
            const pageId = await page.locator('[data-gpy-page]:visible').getAttribute('data-gpy-page');
            await page.screenshot({ path: join(process.env.CUBE_SCREENSHOTS, (file === 'cube-solving.html' ? 'unified' : 'standalone') + '-' + width + '-' + pageId + '.png'), fullPage: true });
          }
        }
      }
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });
}

test('Pyraminx and 3x3 keep independent state, dialogs and matching visual styles', async () => {
  const { context, page, errors } = await open('cube-solving.html');
  try {
    await go(page, '2. Zaļais slānis');
    await page.locator('[data-gpy-done="2"]').check();
    const style = selector => page.locator(selector).evaluate(node => {
      const css = getComputedStyle(node);
      return [css.fontFamily, css.fontSize, css.backgroundColor, css.borderRadius, css.padding];
    });
    const buttonStyle = await style('[data-gpy-next]');
    const headingStyle = await style('[data-gpy-page="2"] h2');
    await page.locator('.cubebtn[data-cube="a3"]').click();
    assert.equal(await page.locator('.gpy-bottom').isVisible(), false);
    assert.deepEqual(await style('[data-g3-next]'), buttonStyle);
    assert.deepEqual(await style('[data-g3-page="intro"] h2'), headingStyle);
    await page.locator('[data-g3-next]').click();
    assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
    await page.locator('.cubebtn[data-cube="py"]').click();
    assert.equal(await page.locator('[data-gpy-page="2"]').isVisible(), true);
    assert.equal(await page.locator('[data-gpy-done="2"]').isChecked(), true);
    await page.locator('.lvlbtn[data-level="pro"]').click();
    assert.equal(await page.locator('#py-cfop').isVisible(), true);
    assert.equal(await page.locator('.gpy-bottom').isVisible(), false);
    await page.locator('.cubebtn[data-cube="py"]').click();
    assert.equal(await page.locator('#panel-py').isVisible(), true);
    await page.locator('.cubebtn[data-cube="py"]').click();
    await page.locator('.lvlbtn[data-level="beginner"]').click();
    await page.locator('[data-gpy-page="2"] .alg button').first().click();
    // Simulate a programmatic mode change while help is open.
    await page.locator('.cubebtn[data-cube="a3"]').evaluate(node => node.click());
    assert.equal(await page.locator('[data-gpy-dialog]').evaluate(node => node.open), false);
    assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});

test('Pyraminx recovers from corrupt stored JSON and a cursor past the end of MIX', async () => {
  const { context, page, errors } = await open(files[0]);
  try {
    for (const value of ['{broken', JSON.stringify({ page: 'invalid', practice: { sequence: 0, move: 25 } })]) {
      await page.evaluate(value => localStorage.setItem('pyraminx-beginner-v2', value), value);
      await page.reload();
      await page.waitForSelector('[data-gpy-page="intro"]');
      await go(page, 'Sajaukšana');
      assert.equal(await page.locator('[data-gpy-counter]').innerText(), 'Gājiens 1 no 8');
    }
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});
