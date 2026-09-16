'use strict';
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');

function core() {
  const html = readFileSync(join(__dirname, '../2x2/rubiks-2x2-guide.html'), 'utf8');
  const script = html.match(/<script data-guide2-runtime>([\s\S]*?)<\/script>/);
  assert.ok(script, 'missing 2x2 beginner runtime');
  const context = { module: { exports: {} } };
  vm.runInNewContext(script[1], context);
  return context.module.exports;
}

test('2x2 navigation follows three steps and restores only valid pages', () => {
  const guide = core();
  for (const invalid of [null, '', '7', '__proto__']) assert.equal(guide.validPage(invalid), 'intro');
  assert.equal(guide.adjacentPage('intro', -1), 'intro');
  assert.equal(guide.adjacentPage('intro', 1), '1');
  assert.equal(guide.adjacentPage('3', 1), 'scramble');
  assert.equal(guide.validPage('4'), 'intro');
  assert.equal(guide.adjacentPage('scramble', -1), '3');
  assert.equal(guide.adjacentPage('scramble', 1), 'scramble');
});

test('2x2 practice cursor respects actual sequence lengths including ten-move MIX', () => {
  const guide = core();
  const clean = value => JSON.parse(JSON.stringify(value));
  assert.deepEqual(clean(guide.validPractice({ sequence: 0, move: 10 }, [10, 25, 25, 25, 25])), { sequence: 0, move: 10 });
  for (const value of [null, {}, { sequence: 0, move: 11 }, { sequence: 5, move: 0 }, { sequence: 1, move: 26 }, { sequence: 0, move: -1 }]) {
    assert.deepEqual(clean(guide.validPractice(value, [10, 25, 25, 25, 25])), { sequence: 0, move: 0 });
  }
});

test('2x2 move help describes every outer turn and rejects unknown moves', () => {
  const guide = core();
  for (const face of 'RLUDFB') {
    assert.notEqual(guide.describeMove(face), guide.describeMove(face + "'"));
    assert.match(guide.describeMove(face + '2'), /180/);
  }
  assert.equal(guide.describeMove('invalid'), '');
});
