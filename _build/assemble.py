# Assembles the unified cube guide (index.html) from the three original
# guides plus authored shell/kids fragments in _build/.
# Originals are read-only; output is written to ../index.html.
import re
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, '_build')

def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()

def prefix_ids(html, pfx):
    html = re.sub(r'id="([A-Za-z0-9_-]+)"', lambda m: 'id="%s-%s"' % (pfx, m.group(1)), html)
    html = re.sub(r'href="#([A-Za-z0-9_-]+)"', lambda m: 'href="#%s-%s"' % (pfx, m.group(1)), html)
    html = re.sub(r'data-step="([A-Za-z0-9_-]+)"', lambda m: 'data-step="%s-%s"' % (pfx, m.group(1)), html)
    return html

def extract_navs(src, pfx):
    navs = []
    for cls, level in (('beg-nav', 'beginner'), ('pro-nav', 'pro')):
        m = re.search(r'<nav class="steps %s".*?</nav>' % cls, src, re.S)
        if not m:
            raise SystemExit('nav %s not found for %s' % (cls, pfx))
        nav = m.group(0)
        nav = nav.replace('class="steps %s"' % cls, 'class="steps" data-for="%s:%s"' % (pfx, level))
        navs.append(prefix_ids(nav, pfx))
    return navs

def extract_main(src, pfx):
    m = re.search(r'<main class="wrap">(.*?)</main>', src, re.S)
    if not m:
        raise SystemExit('main not found for %s' % pfx)
    return prefix_ids(m.group(1), pfx)

def add_class(html, sec_id, cls):
    old = '<section id="%s">' % sec_id
    new = '<section class="%s" id="%s">' % (cls, sec_id)
    if old not in html:
        raise SystemExit('section %s not found' % sec_id)
    return html.replace(old, new, 1)

src_a2 = read(os.path.join(ROOT, '2x2', 'rubiks-2x2-guide.html'))
src_a3 = read(os.path.join(ROOT, '3x3', 'rubiks-3x3-guide.html'))
src_py = read(os.path.join(ROOT, 'pyraminx', 'rubiks-pyraminx-guide.html'))

navs = []
navs += extract_navs(src_a2, 'a2')
navs += extract_navs(src_a3, 'a3')
navs += extract_navs(src_py, 'py')

main_a2 = extract_main(src_a2, 'a2')
main_a3 = extract_main(src_a3, 'a3')
main_py = extract_main(src_py, 'py')

# 2x2: shared sections get hide-kids (kids level has its own intro/steps)
for sec in ('a2-uzbuve', 'a2-nota', 'a2-cheat', 'a2-padomi'):
    main_a2 = add_class(main_a2, sec, 'hide-kids')

# Pyraminx: shared sections get hide-kids
for sec in ('py-uzbuve', 'py-nota', 'py-padomi'):
    main_py = add_class(main_py, sec, 'hide-kids')

# Pyraminx: replace original beginner block with the rewritten detailed version
pat = re.compile(r'<div class="mode mode-beginner">.*?</div><!-- /mode-beginner -->', re.S)
if not pat.search(main_py):
    raise SystemExit('pyraminx mode-beginner block not found')
main_py = pat.sub(lambda m: read(os.path.join(BUILD, 'py-beginner.html')).strip(), main_py, count=1)

# 3x3 step 7: inject the "finish the algorithm before turning U" warning
anchor = '<p class="alg" data-alg="R\' D\' R D"></p>'
warn = (anchor + '\n    <div class="warn"><b>Ļoti svarīgi!</b> Kad stūrim dzeltenais parādās augšā '
        'pareizajā vietā — <strong>obligāti pabeidz algoritmu līdz galam</strong> (visiem 4 gājieniem '
        '<span class="alg tiny" style="display:inline-flex;vertical-align:middle" data-alg="R\' D\' R D"></span> '
        'jābūt izdarītiem; ja vajag — vēl pilnu ciklu, līdz apakšējās kārtas atkal izskatās '
        'kārtīgāk). <strong>Tikai pēc tam</strong> veic U pagriezienu, lai pievērstu nākamo stūri!</div>')
if main_a3.count(anchor) != 1:
    raise SystemExit('3x3 s7 anchor count = %d (expected 1)' % main_a3.count(anchor))
main_a3 = main_a3.replace(anchor, warn, 1)

def hero(flag_colors, title, sub):
    spans = ''.join('<span style="background:var(--%s)"></span>' % c for c in flag_colors)
    return ('<section class="panel-hero">\n'
            '  <div class="hero-flag" aria-hidden="true">%s</div>\n'
            '  <h1>%s</h1>\n'
            '  <p>%s</p>\n'
            '</section>\n' % (spans, title, sub))

kids_a2 = read(os.path.join(BUILD, 'kids-a2.html')).strip()
kids_a3 = read(os.path.join(BUILD, 'kids-a3.html')).strip()
kids_py = read(os.path.join(BUILD, 'kids-py.html')).strip()

panels = []
panels.append('<div class="cubepanel" id="panel-a2" data-n="2">\n' +
              hero(['cw', 'cy', 'cr', 'co', 'cg', 'cb'], '2×2 Rubika kubs',
                   'Kabatas kubs — 8 stūri, bez centriem. Izvēlies līmeni augšā un ej cauri soļiem; izvēle tiek saglabāta.') +
              kids_a2 + '\n' + main_a2 + '\n</div>')
panels.append('<div class="cubepanel" id="panel-a3" data-n="3">\n' +
              hero(['cw', 'cy', 'cr', 'co', 'cg', 'cb'], '3×3 Rubika kubs',
                   'Klasika — slānis pa slānim (7 soļi) vai CFOP profesionāļiem. Izvēlies līmeni augšā.') +
              kids_a3 + '\n' + main_a3 + '\n</div>')
panels.append('<div class="cubepanel" id="panel-py" data-n="3">\n' +
              hero(['cg', 'cr', 'cb', 'cy'], 'Pyraminx',
                   'Piramīdas puzle — vieglākā no trim. Slānis pa slānim vai L4E/Oka profesionāļiem.') +
              kids_py + '\n' + main_py + '\n</div>')

out = (read(os.path.join(BUILD, 'shell-top.html')).rstrip() + '\n\n' +
       '\n\n'.join(navs) + '\n\n' +
       '<main class="wrap">\n\n' + '\n\n'.join(panels) + '\n\n</main>\n\n' +
       read(os.path.join(BUILD, 'shell-end.html')))

dst = os.path.join(ROOT, 'cube-solving.html')
with io.open(dst, 'w', encoding='utf-8') as f:
    f.write(out)

print('OK -> %s (%d bytes, %d lines)' % (dst, len(out.encode('utf-8')), out.count('\n') + 1))
