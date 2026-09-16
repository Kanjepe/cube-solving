'use strict';
// Pure-function checks of the three namespaced Pro runtimes (no browser).
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');

const GUIDES = [
  { cube: 'a2', file: '../2x2/rubiks-2x2-guide.html', root: 'guide2pro', pyra: false },
  { cube: 'a3', file: '../3x3/rubiks-3x3-guide.html', root: 'guide3pro', pyra: false },
  { cube: 'py', file: '../pyraminx/rubiks-pyraminx-guide.html', root: 'guidepypro', pyra: true },
];

function load(g) {
  const html = readFileSync(join(__dirname, g.file), 'utf8');
  const block = html.split('<div class="mode mode-pro">')[1].split('</div><!-- /mode-pro -->')[0];
  const source = block.match(new RegExp('<script data-' + g.root + '-runtime>([\\s\\S]*?)<\\/script>'));
  assert.ok(source, g.cube + ': missing namespaced Pro runtime');
  const context = { module: { exports: {} } };
  vm.runInNewContext(source[1], context);
  return { api: context.module.exports, block };
}

for (const g of GUIDES) {
  test(g.cube + ': invert handles wide moves, slices, rotations and primes', () => {
    const { api } = load(g);
    assert.equal(api.invert("R U R' U'"), "U R U' R'");
    assert.equal(api.invert("r U2 d' y M2"), "M2 y' d U2 r'");
    assert.equal(api.invert("L R' L' R"), "R' L R L'");
    assert.equal(api.invert("u l' R"), "R' l u'");
  });

  test(g.cube + ': every move used in a Pro algorithm has an explanation', () => {
    const { api, block } = load(g);
    const describe = g.pyra ? api.describePyra : api.describeCube;
    const moves = new Set();
    for (const m of block.matchAll(/data-alg="([^"]+)"/g)) {
      for (const mv of m[1].trim().split(/\s+/)) moves.add(mv);
    }
    assert.ok(moves.size > 5, g.cube + ': no algorithms found');
    for (const mv of moves) {
      const text = describe(mv);
      assert.ok(text.length > 20, g.cube + ': no explanation for ' + mv);
      assert.match(text, /°/, g.cube + ': explanation without angle for ' + mv);
    }
    assert.equal(describe('invalid'), '');
    assert.equal(describe(''), '');
  });

  test(g.cube + ': prime and plain moves are explained differently', () => {
    const { api } = load(g);
    const describe = g.pyra ? api.describePyra : api.describeCube;
    for (const face of (g.pyra ? 'ULRB' : 'RLUDFB')) {
      assert.notEqual(describe(face), describe(face + "'"));
    }
    if (!g.pyra) {
      assert.match(describe('R2'), /180/);
      assert.match(describe('y'), /Viss kubs/);
      assert.match(describe('r'), /divas kārtas/i);
    } else {
      assert.match(describe('u'), /tikai mazo galu/);
      assert.match(describe('U'), /divus slānīšus/);
    }
  });
}

test('runtimes are identical apart from their namespace', () => {
  const [a2, a3, py] = GUIDES.map(load);
  const norm = (g, src) => src.block.match(new RegExp('<script data-' + g.root + '-runtime>([\\s\\S]*?)<\\/script>'))[1]
    .split(g.root).join('guidepro').split(g.cube === 'a2' ? 'g2p-' : g.cube === 'a3' ? 'g3p-' : 'gpp-').join('gp-');
  assert.equal(norm(GUIDES[0], a2), norm(GUIDES[1], a3));
  assert.equal(norm(GUIDES[1], a3), norm(GUIDES[2], py));
});
