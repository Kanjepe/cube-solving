'use strict';
// Browser integration tests. Playwright may be supplied outside the repository.
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { join, resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { mkdirSync } = require('node:fs');
const { chromium } = require(process.env.CUBE_PLAYWRIGHT || 'playwright');
const rootPath = resolve(__dirname, '..');
const files = ['cube-solving.html', '3x3/rubiks-3x3-guide.html'];
let browser;

before(async () => {
  browser = await chromium.launch({ headless: true, channel: 'msedge' });
});
after(async () => { if (browser) await browser.close(); });

async function open(file, width = 390) {
  const context = await browser.newContext({ viewport: { width, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(join(rootPath, file)).href);
  await page.waitForSelector('.guide3.g3-ready');
  return { context, page, errors };
}

async function go(page, name) {
  await page.locator('[data-g3-menu]').click();
  await page.locator('.g3-menu-list button').filter({ hasText: name }).click();
}

for (const file of files) {
  test(file + ': direct step links open the requested page', async () => {
    const { context, page, errors } = await open(file);
    try {
      const prefix = file === 'cube-solving.html' ? 'a3-' : '';
      for (const step of ['2', '7']) {
        await page.goto(pathToFileURL(join(rootPath, file)).href + '#' + prefix + 's' + step);
        await page.waitForSelector('[data-g3-page="' + step + '"]:visible');
        await page.reload();
        await page.waitForSelector('.guide3.g3-ready');
        assert.equal(await page.locator('[data-g3-page="' + step + '"]').isVisible(), true);
        assert.equal(await page.locator('[data-g3-page]:visible').count(), 1);
      }
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': navigation, local help, saved page and completion', async () => {
    const { context, page, errors } = await open(file);
    try {
      assert.equal(await page.locator('[data-g3-page]:visible').count(), 1);
      assert.equal(await page.locator('nav.steps:visible').count(), 0);
      await page.locator('[data-g3-next]').click();
      assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
      await go(page, '2. Baltie stūri');
      await page.locator('[data-g3-done="2"]').check();
      const algorithm = page.locator('[data-g3-page="2"] .alg button').first();
      await algorithm.scrollIntoViewIfNeeded();
      const scrollBefore = await page.evaluate(() => window.scrollY);
      await algorithm.click();
      assert.match(await page.locator('[data-g3-dialog-content]').innerText(), /Labā kārta/);
      await page.locator('[data-g3-close]').click();
      assert.equal(await page.evaluate(() => window.scrollY), scrollBefore);
      await page.reload();
      await page.waitForSelector('.guide3.g3-ready');
      assert.equal(await page.locator('[data-g3-page="2"]').isVisible(), true);
      assert.equal(await page.locator('[data-g3-done="2"]').isChecked(), true);
      await page.locator('[data-g3-prev]').click();
      assert.equal(await page.locator('[data-g3-page="1"]').isVisible(), true);
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });

  test(file + ': all five practice sequences and cursor persistence', async () => {
    const { context, page, errors } = await open(file);
    try {
      await go(page, 'Sajaukšana');
      for (let i = 0; i < 5; i += 1) {
        await page.locator('[data-g3-select]').selectOption(String(i));
        assert.equal(await page.locator('[data-g3-scramble]:visible').count(), 1);
        const moves = (await page.locator('[data-g3-scramble]:visible').getAttribute('data-g3-scramble')).split(' ');
        assert.equal(await page.locator('[data-g3-current]').innerText(), moves[0]);
        await page.locator('[data-g3-move-next]').click();
        assert.equal(await page.locator('[data-g3-current]').innerText(), moves[1]);
      }
      await page.reload();
      await page.waitForSelector('.guide3.g3-ready');
      assert.equal(await page.locator('[data-g3-select]').inputValue(), '4');
      assert.equal(await page.locator('[data-g3-counter]').innerText(), 'Gājiens 2 no 25');
      for (let i = 1; i < 25; i += 1) await page.locator('[data-g3-move-next]').click();
      assert.equal(await page.locator('[data-g3-move-next]').isDisabled(), true);
      assert.equal(await page.locator('[data-g3-current]').innerText(), '✓');
      await page.locator('[data-g3-move-back]').click();
      assert.equal(await page.locator('[data-g3-counter]').innerText(), 'Gājiens 25 no 25');
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  });
}

for (const file of files) {
test(file + ': mobile layouts have no page overflow and keep navigation visible', async () => {
  const { context, page, errors } = await open(file);
  try {
    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 844 });
      for (const name of ['Pirms sākuma', '1. Baltais krusts', '2. Baltie stūri', '3. Vidējā kārta', '4. Dzeltenais krusts', '5. Dzeltenā krusta sāni', '6. Stūru vietas', '7. Stūru pagriezieni', 'Sajaukšana']) {
        await go(page, name);
        await page.locator('[data-g3-page]:visible details').evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
        const sizes = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, width: window.innerWidth }));
        assert.ok(sizes.scroll <= width && sizes.width === width, `${width}px ${name}: ${JSON.stringify(sizes)}`);
        const nav = await page.locator('.g3-bottom').boundingBox();
        assert.ok(nav.y >= 0 && nav.y + nav.height <= 844.5);
        for (const button of await page.locator('.g3-bottom button').all()) {
          assert.ok((await button.boundingBox()).height >= 44);
        }
      }
    }
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});
}

test('other puzzles and 3x3 Pro are isolated from the new beginner UI', async () => {
  const { context, page, errors } = await open(files[0]);
  try {
    for (const cube of ['a2', 'py']) {
      await page.locator('.cubebtn[data-cube="' + cube + '"]').click();
      assert.equal(await page.locator('body').evaluate(node => node.classList.contains('g3-active')), false);
      assert.equal(await page.locator('.g3-bottom').isVisible(), false);
      assert.equal(await page.locator('#panel-' + cube).isVisible(), true);
    }
    await page.locator('.cubebtn[data-cube="a3"]').click();
    await page.locator('.lvlbtn[data-level="pro"]').click();
    assert.equal(await page.locator('#a3-cfop').isVisible(), true);
    assert.equal(await page.locator('#a3-nota').isVisible(), true);
    assert.equal(await page.locator('.g3-bottom').isVisible(), false);
    await page.locator('.lvlbtn[data-level="beginner"]').click();
    assert.equal(await page.locator('.g3-bottom').isVisible(), true);
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});

test('corrupt storage recovers and optional screenshots can be captured', async () => {
  const { context, page, errors } = await open(files[0]);
  try {
    await page.evaluate(() => localStorage.setItem('cube3-beginner-v2', '{broken'));
    await page.reload();
    await page.waitForSelector('.guide3.g3-ready');
    assert.equal(await page.locator('[data-g3-page="intro"]').isVisible(), true);
    if (process.env.CUBE_SCREENSHOTS) {
      mkdirSync(process.env.CUBE_SCREENSHOTS, { recursive: true });
      await page.screenshot({ path: join(process.env.CUBE_SCREENSHOTS, '3x3-mobile-intro.png'), fullPage: true });
      await go(page, '7. Stūru pagriezieni');
      await page.screenshot({ path: join(process.env.CUBE_SCREENSHOTS, '3x3-mobile-step7.png'), fullPage: true });
      await go(page, 'Sajaukšana');
      await page.screenshot({ path: join(process.env.CUBE_SCREENSHOTS, '3x3-mobile-scramble.png'), fullPage: true });
    }
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});
