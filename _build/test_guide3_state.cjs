'use strict';
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');
const html = readFileSync(join(__dirname, '../3x3/rubiks-3x3-guide.html'), 'utf8');
const source = html.match(/<script data-guide3-runtime>([\s\S]*?)<\/script>/);

test('beginner runtime is available in the standalone source', () => {
  assert.ok(source, 'missing scoped beginner runtime');
});

function core() {
  assert.ok(source, 'missing scoped beginner runtime');
  const context = { module: { exports: {} } };
  vm.runInNewContext(source[1], context);
  return context.module.exports;
}

test('invalid stored pages recover to the introduction', () => {
  const guide = core();
  for (const value of [null, '', 'unknown', '__proto__', '8', 'NaN']) {
    assert.equal(guide.validPage(value), 'intro');
  }
  for (const value of ['intro', '1', '7', 'scramble']) {
    assert.equal(guide.validPage(value), value);
  }
});

test('previous and next stop at the ends and include practice', () => {
  const guide = core();
  assert.equal(guide.adjacentPage('intro', -1), 'intro');
  assert.equal(guide.adjacentPage('intro', 1), '1');
  assert.equal(guide.adjacentPage('3', -1), '2');
  assert.equal(guide.adjacentPage('7', 1), 'scramble');
  assert.equal(guide.adjacentPage('scramble', 1), 'scramble');
});

test('every scramble move has explicit face and direction guidance', () => {
  const guide = core();
  for (const face of 'RLUDFB') {
    assert.notEqual(guide.describeMove(face), guide.describeMove(face + "'"));
    assert.match(guide.describeMove(face + '2'), /180/);
    assert.ok(guide.describeMove(face).length > 20);
  }
  assert.equal(guide.describeMove('invalid'), '');
});

test('saved scramble cursor is validated without skipping moves', () => {
  const guide = core();
  assert.deepEqual(JSON.parse(JSON.stringify(guide.validPractice({ sequence: 3, move: 24 }))), { sequence: 3, move: 24 });
  for (const value of [null, {}, { sequence: -1, move: 1 }, { sequence: 6, move: 1 }, { sequence: 0, move: 99 }]) {
    assert.deepEqual(JSON.parse(JSON.stringify(guide.validPractice(value))), { sequence: 0, move: 0 });
  }
});
