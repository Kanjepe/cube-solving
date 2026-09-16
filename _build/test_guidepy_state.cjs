'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const html = readFileSync(join(__dirname, '../pyraminx/rubiks-pyraminx-guide.html'), 'utf8');
const match = html.match(/<script data-guidepy-runtime>([\s\S]*?)<\/script>/);
assert.ok(match, 'Standalone Pyraminx runtime must exist');
const sandbox = { module: { exports: {} } };
vm.runInNewContext(match[1], sandbox);
const api = sandbox.module.exports;

test('five-page navigation stays within bounds', () => {
  assert.equal(api.validPage('wrong'), 'intro');
  assert.equal(api.adjacentPage('intro', -1), 'intro');
  assert.equal(api.adjacentPage('3', 1), 'scramble');
  assert.equal(api.adjacentPage('scramble', 1), 'scramble');
});

test('Pyraminx help uses 120 degrees and distinguishes tips', () => {
  for (const move of ['U', "R'", 'L', 'B', 'u', "r'", 'l', 'b']) {
    assert.match(api.describeMove(move), /120°/);
  }
  assert.match(api.describeMove('r'), /tikai.*gal/i);
  assert.match(api.describeMove('R'), /malas/);
  assert.match(api.describeMove("U'"), /pretēji/);
  for (const move of ['U2', 'F', 'D', 'Rw', '']) assert.equal(api.describeMove(move), '');
});

test('practice validation uses each actual sequence length', () => {
  assert.equal(api.validPractice({ sequence: 1, move: 12 }, [8, 12]).move, 12);
  assert.equal(api.validPractice({ sequence: 0, move: 12 }, [8, 12]).move, 0);
  assert.equal(api.validPractice(null, [8]).sequence, 0);
});
