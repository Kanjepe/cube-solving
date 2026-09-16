# Generates the Pro blocks (mobile step format, same layout as the beginner
# guides) for the three standalone guides and writes them between the
#   <div class="mode mode-pro"> ... </div><!-- /mode-pro -->
# markers. Case data and every picture attribute come from pro_cases.py;
# the presentation runtime is pro_runtime.html, namespaced per guide
# (.guide2pro/g2p-, .guide3pro/g3p-, .guidepypro/gpp-) exactly like the
# beginner blocks, so three copies can live in one unified page.
#
#   python _build/pro_blocks.py          # write blocks into the standalone files
#   python _build/pro_blocks.py --check  # exit 1 if any file differs from the generator
import io
import json
import os
import re
import sys

import pro_cases as pc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
MARK, END = '<div class="mode mode-pro">', '</div><!-- /mode-pro -->'
GUIDES = {
    'a2': {'file': os.path.join(ROOT, '2x2', 'rubiks-2x2-guide.html'), 'root': 'guide2pro', 'ns': 'g2p', 'key': 'cube2-pro-v1'},
    'a3': {'file': os.path.join(ROOT, '3x3', 'rubiks-3x3-guide.html'), 'root': 'guide3pro', 'ns': 'g3p', 'key': 'cube3-pro-v1'},
    'py': {'file': os.path.join(ROOT, 'pyraminx', 'rubiks-pyraminx-guide.html'), 'root': 'guidepypro', 'ns': 'gpp', 'key': 'pyraminx-pro-v1'},
}


def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


# ------------------------------------------------------------ components ----
def alg(a, cls='alg'):
    return '<p class="%s" data-alg="%s"></p>' % (cls, esc(a))


def fig(attrs, caption='', small=True):
    a = ' '.join('%s="%s"' % (k, v) for k, v in attrs.items())
    if small:
        a += ' data-small="1"'
    return '<figure class="dg" %s>%s</figure>' % (a, '<figcaption>%s</figcaption>' % caption if caption else '')


def case(cid, sets, name, a, hint='', figure='', extra=''):
    cls = 'gp-case' if figure else 'gp-case gp-case-text'
    figs = '<div class="gp-case-figs">%s</div>' % figure if figure else ''
    return ('<div class="%s" data-gp-case="%s" data-gp-sets="%s">%s<div class="gp-case-body">'
            '<p class="gp-case-name">%s</p>%s%s%s'
            '<label class="gp-learned"><input type="checkbox" data-gp-learned="%s"> Apgūts</label></div></div>'
            % (cls, cid, sets, figs, name, alg(a), ('<p class="gp-small">%s</p>' % hint) if hint else '', extra, cid))


def group(title, set_id, cases_html, open_=False):
    return ('<details class="gp-group"%s><summary>%s <span class="gp-badge" data-gp-group-count="%s"></span></summary>%s</details>'
            % (' open' if open_ else '', title, set_id, cases_html))


def page(pid, title, body, page_id=None):
    idattr = ' id="%s"' % page_id if page_id else ''
    return ('<section class="gp-page" data-gp-page="%s" data-gp-title="%s"%s>\n<h2 tabindex="-1">%s</h2>\n%s\n</section>\n'
            % (pid, esc(title), idattr, title, body))


def done(step, text):
    return '<label class="gp-done"><input type="checkbox" data-gp-done="%s"> %s</label>' % (step, text)


def heading(eyebrow):
    return ('<div class="gp-heading"><p class="gp-eyebrow">%s</p>'
            '<p class="gp-location" data-gp-location aria-live="polite">Pirms sākuma</p></div>' % eyebrow)


def progress(label):
    return '<div class="gp-progress"><strong>%s</strong> <span data-gp-total>0 no 0</span><div class="gp-bar"><span data-gp-total-bar></span></div></div>' % label


def cheat(groups):
    out = ''
    for title, rows in groups:
        out += '<h3>%s</h3><div class="gp-cheat">' % title
        for name, a in rows:
            out += '<div class="gp-cheat-row"><span class="gp-cheat-name">%s</span>%s</div>' % (name, alg(a))
        out += '</div>'
    return out


def sources(items):
    lis = ''.join('<li><a href="%s" rel="noopener">%s</a> – %s</li>' % (u, t, d) for t, u, d in items)
    return ('<h3>Avoti</h3><p>Visi algoritmi ir šajā lapā un pārbaudīti simulatorā. Saites ir papildu lasīšanai, video un pirkstu trikiem.</p>'
            '<ul class="gp-sources">%s</ul>' % lis)


NAV = ('<nav class="gp-bottom" aria-label="%s"><button type="button" data-gp-prev>← Atpakaļ</button>'
       '<button type="button" data-gp-menu>Soļi ☰</button><button type="button" class="gp-primary" data-gp-next>Tālāk →</button></nav>\n'
       '<dialog class="gp-dialog" data-gp-dialog aria-label="%s"><div class="gp-dialog-top"><strong data-gp-dialog-title></strong>'
       '<button type="button" data-gp-close aria-label="Aizvērt">Aizvērt ×</button></div><div data-gp-dialog-content></div></dialog>')


def drill(intro_html, options, grip):
    opts = ''.join('<option value="%s">%s</option>' % (v, t) for v, t in options)
    return (intro_html +
            '<div class="gp-grip"><strong>Sākuma stāvoklis</strong><br>%s</div>' % grip +
            '<label class="gp-select-label">Algoritmu kopa<select data-gp-drill-set aria-label="Algoritmu kopa">%s</select></label>' % opts +
            '<p class="gp-small" data-gp-drill-progress></p>'
            '<div class="gp-practice" data-gp-drill>'
            '<p><strong>1. Sagatavo gadījumu</strong> – izpildi šo secību uz salikta kuba:</p>'
            '<div data-gp-drill-setup class="alg"></div>'
            '<p><strong>2. Atpazīsti gadījumu</strong> un izpildi tā algoritmu no galvas. <strong>3. Pārbaudi</strong> – kubam jābūt saliktam.</p>'
            '<div class="gp-actions"><button type="button" data-gp-drill-reveal>Parādīt atbildi</button>'
            '<button type="button" class="gp-primary" data-gp-drill-next>Nākamais gadījums →</button></div>'
            '<div data-gp-drill-answer hidden class="gp-answer"><div data-gp-drill-figure></div><p class="gp-case-name" data-gp-drill-name></p><div data-gp-drill-alg class="alg"></div>'
            '<label class="gp-learned"><input type="checkbox" data-gp-drill-learned> Zināju no galvas – atzīmēt kā apgūtu</label></div>'
            '</div>'
            '<details><summary>Kā treniņš darbojas?</summary><p>Sagatavošanas secība ir gadījuma algoritma apgrieztā versija. Uz salikta kuba tā uzliek tieši šo gadījumu, tāpēc pēc pareizi izpildīta algoritma kubs atkal ir salikts. Vispirms tiek piedāvāti vēl neapgūtie gadījumi.</p></details>')


def top_fig(d, caption='', extra=None):
    attrs = {'data-kind': 'top', 'data-c': d['c'], 'data-b': d['b'], 'data-f': d['f'], 'data-l': d['l'], 'data-r': d['r']}
    if extra:
        attrs.update(extra)
    return fig(attrs, caption)


# ------------------------------------------------------------------- 3x3 ----
def oll_card(d, name=None, sets='oll57'):
    label = 'OLL %d' % d['n'] + (' · %s' % name if name else '')
    hint = 'Augšā %d dzeltenas uzlīmes (ar centru). Pagriez U, līdz sānu strīpas sakrīt ar attēlu.' % d['ycount']
    return case(d['id'], sets, label, d['alg'], hint, top_fig(d))


SIDE = {'b': 'aizmugurē', 'f': 'priekšā', 'l': 'pa kreisi', 'r': 'pa labi'}


def pll_hint(d):
    bars, lights = [], []
    for k in 'bflr':
        s = d[k]
        if s[0] == s[1] == s[2]:
            bars.append(SIDE[k])
        elif s[0] == s[2]:
            lights.append(SIDE[k])
    parts = []
    if bars:
        parts.append('pilna josla ' + ', '.join(bars))
    if lights:
        parts.append('lukturi ' + ', '.join(lights))
    if not parts:
        parts.append('nav ne lukturu, ne joslu')
    return 'Atpazīšana: ' + '; '.join(parts) + '. Bultas rāda, kur gabaliņi pārvietojas.'


def pll_card(d, sets='pll21'):
    f = fig({'data-kind': 'top', 'data-c': 'yyyyyyyyy', 'data-b': d['b'], 'data-f': d['f'], 'data-l': d['l'], 'data-r': d['r'],
             'data-arrows': json.dumps(d['arrows'], separators=(',', ':')).replace('"', '&quot;')})
    return case(d['id'], sets, '%s perm · %s' % (d['n'], d['d']), d['alg'], pll_hint(d), f)


def f2l_card(d):
    f = fig({'data-kind': 'f2l', 'data-u': d['u'], 'data-f': d['f'], 'data-r': d['r']}, small=False)
    hint = 'Pelēkās uzlīmes nav svarīgas. Redzamas tikai pāra divas detaļas.'
    if d['alg'].startswith('y'):
        hint = 'Sākas ar y pagriezienu: vispirms pagriez visu kubu, tad ievieto no kreisās puses.'
    elif d['alg'].startswith('d'):
        hint = 'd griež apakšējās divas kārtas kopā; tas aizstāj kuba pagriešanu rokās.'
    return case(d['id'], 'f2l', 'F2L %d' % d['n'], d['alg'], hint, f)


def build_3x3():
    oll = {d['n']: d for d in pc.OLL}
    pll = {d['n']: d for d in pc.PLL}
    edge_cards = ''.join(case(d['id'], 'oll2look', d['name'], d['alg'], d['hint'], fig({'data-kind': 'top', 'data-c': d['c']}))
                         for d in pc.OLL_EDGES)
    ocll_cards = ''.join(oll_card(oll[n], pc.OCLL_NAMES[n], 'ocll oll57') for n in (27, 26, 21, 22, 23, 24, 25))
    full_oll, oll_cheat = '', []
    for key, title in pc.OLL_GROUPS:
        items = [d for d in pc.OLL if d['g'] == key]
        cards = ''.join(oll_card(d, pc.OCLL_NAMES.get(d['n']), 'ocll oll57' if d['g'] == 'OCLL' else 'oll57') for d in items)
        full_oll += group('%s · %d' % (title, len(items)), 'oll57:%s' % key, cards)
        oll_cheat.append((title, [('OLL %d%s' % (d['n'], ' · ' + pc.OCLL_NAMES[d['n']] if d['n'] in pc.OCLL_NAMES else ''), d['alg']) for d in items]))
    full_pll, pll_cheat = '', []
    for title, names in pc.PLL_GROUPS:
        cards = ''.join(pll_card(pll[n], 'pll2look pll21' if n in pc.PLL_2LOOK else 'pll21') for n in names)
        full_pll += group('%s · %d' % (title, len(names)), 'pll21:%s' % title, cards)
        pll_cheat.append((title, [('%s perm · %s' % (n, pll[n]['d']), pll[n]['alg']) for n in names]))
    full_f2l, f2l_cheat = '', []
    for g in pc.F2L_GROUP_ORDER:
        items = [d for d in pc.F2L if d['g'] == g]
        cards = '<p class="gp-small">%s</p>' % pc.F2L_INTRO[g] + ''.join(f2l_card(d) for d in items)
        full_f2l += group('%s · %d' % (g, len(items)), 'f2l:%s' % g, cards)
        f2l_cheat.append((g, [('F2L %d' % d['n'], d['alg']) for d in items]))

    SOURCES = [('speedsolving.com wiki – OLL', 'https://www.speedsolving.com/wiki/index.php/OLL', 'visi 57 OLL ar alternatīvām'),
               ('speedcubedb.com – PLL', 'https://speedcubedb.com/a/3x3/PLL', 'PLL varianti un pirkstu triki'),
               ('speedsolving.com wiki – F2L', 'https://www.speedsolving.com/wiki/index.php/F2L', 'F2L 41 gadījumi, no kuriem ņemts šis saraksts'),
               ('cubeskills.com – F2L PDF', 'https://www.cubeskills.com/uploads/pdf/tutorials/f2l.pdf', 'Felika Zemdega F2L ar attēliem'),
               ('jperm.net', 'https://jperm.net/algs/oll', 'vizuālie OLL, PLL un F2L saraksti ar video'),
               ('ruwix.com – CFOP', 'https://ruwix.com/the-rubiks-cube/advanced-cfop-fridrich/', 'metodes pārskats')]

    p = []
    p.append(page('intro', 'CFOP – ātrsalicēju metode', '''
<p>Četri soļi: <strong>C</strong>ross (krusts), <strong>F</strong>2L (First Two Layers – pirmās divas kārtas), <strong>O</strong>LL (augšas orientācija), <strong>P</strong>LL (augšas permutācija). Iesācēju metode liek pa vienam gabaliņam; CFOP apvieno soļus, tāpēc griezienu ir uz pusi mazāk.</p>
<div class="gp-result"><strong>Tev vajag:</strong> iesācēju metodi bez lapas (apmēram 2 minūtēs) un gatavību mācīties algoritmus pa grupām, nevis visus uzreiz.</div>
''' + progress('Apgūtie algoritmi:') + '''
<h3>Kas mainās pret iesācēju metodi</h3>
<ol>
<li><strong>Krusts</strong> uzreiz apakšā, bez “puķītes” augšā.</li>
<li><strong>F2L</strong> – stūris un mala ievietoti kopā kā pāris. Pirmās divas kārtas vienā solī.</li>
<li><strong>OLL</strong> – visa dzeltenā puse vienā algoritmā (57 gadījumi; sāc ar 10).</li>
<li><strong>PLL</strong> – pēdējā slāņa gabaliņi savās vietās vienā algoritmā (21 gadījums; sāc ar 6).</li>
</ol>
<div class="gp-warning"><strong>Secība mainās.</strong> Iesācēju metodē vispirms liek stūrus vietās un tikai tad tos pagriež. CFOP dara otrādi: vispirms visa augša vienā krāsā (OLL), tad gabaliņi pa vietām (PLL).</div>
<h3>Vārdi, kas parādīsies tālāk</h3>
<ul>
<li><strong>Slots</strong> – vieta, kur apakšā pieder viens stūris ar savu malu virs tā. Kubam ir četri sloti.</li>
<li><strong>Lukturi</strong> – divi blakus stūri ar vienādu sānu krāsu, kā auto priekšējie lukturi.</li>
<li><strong>2-look</strong> – solis divos skatienos ar mazāk algoritmiem; <strong>1-look</strong> – tas pats vienā.</li>
<li><strong>Perm</strong> – saīsinājums no “permutācija”: gabaliņu pārvietošana vietām, nemainot krāsu virzienu.</li>
<li><strong>Sānu strīpas attēlos</strong> – krāsainās joslas ap augšas kvadrātu ir augšējās kārtas sānu uzlīmes. Attēlā aizmugure ir augšā, priekšpuse pie Tevis.</li>
</ul>
<h3>Jaunie apzīmējumi</h3>
<p>Mazie burti griež <strong>divas kārtas reizē</strong>. M, S un E ir vidējās kārtas. x, y un z pagriež <strong>visu kubu</strong>. Pieskaries jebkuram burtam, lai atvērtu skaidrojumu.</p>
''' + alg("r l u d f M S E x y z") + '''
<button type="button" data-gp-help="moves">Parādīt visu apzīmējumu skaidrojumu</button>
<h3>Ieteicamā mācību secība</h3>
<ol>
<li>Krusts apakšā un F2L četri pamatgadījumi. Pēdējo slāni pagaidām liec ar iesācēju 4.–7. soli.</li>
<li>2-look OLL: 3 malu gadījumi + 7 stūru gadījumi.</li>
<li>2-look PLL: 2 stūru + 2 malu algoritmi.</li>
<li>Pilnais PLL (21), tad pilnais OLL (57), tad pārējie F2L gadījumi – pa grupām, ar treniņa lapu.</li>
</ol>
<div class="gp-actions"><button type="button" class="gp-primary" data-gp-goto="1">Sākt ar krustu →</button><button type="button" data-gp-goto="drill">Uz algoritmu treniņu</button></div>
''', 'cfop'))

    p.append(page('1', 'Krusts (Cross)', '''
<p class="gp-goal">Rezultāts: balts krusts apakšā, katras malas sānu krāsa sakrīt ar centru. Bez algoritmiem, ne vairāk kā 8 griezieni.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Baltais centrs apakšā, dzeltenais augšā. Krustu būvē uzreiz apakšā, lai pēc tam neapgrieztu kubu.</div>
''' + fig({'data-kind': 'top', 'data-c': 'xwxwwwxwx', 'data-b': 'xbx', 'data-r': 'xrx', 'data-f': 'xgx', 'data-l': 'xox'},
          'Skats uz balto pusi no apakšas: katras malas sānu krāsa pie sava centra.', small=False) + '''
<ol>
<li>Pirms pirmā grieziena atrodi <strong>visas četras baltās malas</strong>. Sacensībās tam ir 15 sekunžu apskate.</li>
<li>Katru malu liec tieši apakšā vienā vai divos griezienos. Ja mala augšā ir ar balto uz augšu, izlīdzini tās sānu krāsu ar centru un griez šo pusi divreiz.</li>
<li>Ja mala ir vidējā kārtā, viens sānu kārtas grieziens nogādā to apakšā. Pārbaudi, ka nesabojā jau ieliktās malas.</li>
<li>Skaiti griezienus. Mērķis ir 8 vai mazāk; ar praksi 5–6.</li>
</ol>
<div class="gp-check"><strong>Vai gatavs?</strong> Apakšā balts krusts, un katrā sānā apakšējās malas krāsa sakrīt ar centru. Tikai tad sāc F2L.</div>
<details><summary>Nesanāk: krusts ir, bet divas malas samainītas</summary><p>Turi vienu no nepareizajām malām priekšā apakšā. Pacel to ar F2, ar U aizved līdz tās pareizajam centram un ar vēl vienu pusapgriezienu noliec lejā. Otro malu ievieto tāpat.</p></details>
<details><summary>Kā trenēt krustu atsevišķi</summary><p>Sajauc kubu, saliec tikai krustu un sāc no jauna. Desmit krusti pēc kārtas dod vairāk nekā viens pilns salikums.</p></details>
''' + done('1', 'Krusts apakšā ar pareiziem sāniem'), 'cross'))

    p.append(page('2', 'F2L – pirmās divas kārtas', '''
<p class="gp-goal">Rezultāts: pirmās divas kārtas gatavas. Četri stūra un malas pāri ievietoti savos slotos.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Krusts apakšā. Slots, kurā strādā, ir <strong>priekšā pa labi</strong>. Attēlos redzi augšu, priekšpusi un labo pusi; pelēkās uzlīmes nav svarīgas, krāsainas ir tikai pāra divas detaļas.</div>
<h3>Pāra ideja</h3>
<p>Katram baltajam stūrim pieder viena mala ar tām pašām divām sānu krāsām. Atrodi abus, savieno tos augšējā kārtā un ievieto kopā. Tas aizstāj iesācēju 2. un 3. soli.</p>
<h3>Sāc ar četriem pamatgadījumiem</h3>
<p>Ar šiem četriem un divām izcelšanas kustībām var ievietot jebkuru pāri: ja gadījums nav pazīstams, izcel gabaliņu augšā un padari to par pamatgadījumu.</p>
''' + ''.join(f2l_card(d) for d in pc.F2L[:4]) + '''
<details><summary>Izcelšana: gabaliņš slotā nepareizi</summary><p>Turi slotu priekšā pa labi un izpildi vienu no šīm secībām. Gabaliņš nonāk augšā, un Tu vari sākt no jauna.</p>''' + alg("R U R'") + alg("R U' R'") + '''</details>
<div class="gp-warning"><strong>Mācies F2L ar sapratni.</strong> Katrā gadījumā redzi, kā pāris savienojas un ieripo slotā. Pilnais saraksts zemāk ir tam, lai neminētu, nevis lai kaltu visus 41 no galvas pirmajā nedēļā.</div>
<h3>Pilnais F2L – 41 gadījums</h3>
<p>Grupēts pēc tā, kur atrodas stūris un mala. 37. gadījums ir jau ievietots pāris, tāpēc kartīšu ir 40.</p>
''' + full_f2l + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Visas četras sānu puses ir vienā krāsā apakšējās divās rindās. Augšā drīkst būt jebkas.</div>
<details><summary>Look-ahead: kā kļūt ātrākam</summary><p>Kamēr rokas ievieto vienu pāri, acis jau meklē nākamo stūri un malu. Griez lēni un vienmērīgi, nevis ātri un ar pauzēm.</p></details>
''' + done('2', 'Visi četri F2L pāri ievietoti'), 'f2l'))

    p.append(page('3', 'OLL – augšas orientācija', '''
<p class="gp-goal">Rezultāts: visa dzeltenā puse vienā krāsā. Sākumā divos skatienos (2-look), vēlāk vienā.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Dzeltenais centrs augšā. Skaties uz augšu un uz augšējās kārtas sānu strīpām: attēlos aizmugure ir augšā, priekšpuse pie Tevis. Dzeltenās uzlīmes attēlā ir tās, kurām jābūt dzeltenām arī uz Tava kuba; pelēkās var būt jebkuras krāsas.</div>
<h3>A. 2-look: vispirms malas (dzeltenais krusts)</h3>
<p>Skaiti tikai dzeltenās malas. Trīs iespējas:</p>
''' + edge_cards + '''
<h3>B. 2-look: tad stūri (7 gadījumi, saukti OCLL)</h3>
<p>Krusts jau ir. Saskaiti dzeltenos stūrus augšā un salīdzini sānu strīpas ar attēlu. Pagriez U, līdz sakrīt, tad izpildi.</p>
''' + ocll_cards + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Visa augša dzeltena. Sānu krāsas augšējā kārtā vēl drīkst nesakrist – tas ir PLL darbs.</div>
<h3>Pilnais OLL – 57 gadījumi vienā skatienā</h3>
<p>Grupēts pēc dzeltenās figūras uz augšas. Atzīmē apgūtos; skaitītājs pie grupas rāda progresu. Vienam gadījumam ir vairāki līdzvērtīgi algoritmi – šeit standarta publicētie, un katrs pārbaudīts simulatorā.</p>
''' + full_oll + '''
<details><summary>Nesanāk: pēc algoritma augša nav dzeltena</summary><p>Pārbaudi, vai sānu strīpas tiešām sakrita ar attēlu, nevis tikai augšas raksts. Divi gadījumi var izskatīties vienādi no augšas un atšķirties tikai sānos. Ja jāatgriežas, izpildi iesācēju 4.–5. soli – tie vienmēr strādā.</p></details>
''' + done('3', 'Augša vienā krāsā'), 'oll'))

    p.append(page('4', 'PLL – pēdējā slāņa permutācija', '''
<p class="gp-goal">Rezultāts: kubs salikts. Pēdējā slāņa gabaliņi pārvietoti savās vietās vienā algoritmā.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Dzeltenais augšā. Meklē <strong>lukturus</strong>: divus blakus stūrus ar vienādu sānu krāsu. Attēlos aizmugure ir augšā, priekšpuse pie Tevis; sānu strīpas ir reālas krāsas ar zaļo priekšā, bultas rāda, kurp gabaliņš pārvietojas.</div>
<h3>A. 2-look: vispirms stūri</h3>
<p>Ja lukturi ir vienā pusē, turi tos pa kreisi un izpildi T perm. Ja lukturu nav nevienā pusē, izpildi Y perm no jebkura leņķa.</p>
''' + pll_card(pll['T'], 'pll2look pll21') + pll_card(pll['Y'], 'pll2look pll21') + '''
<h3>B. 2-look: tad malas</h3>
<p>Stūri vietās. Ar U atrodi pusi, kur visa sānu josla ir vienā krāsā, un turi to aizmugurē. Trīs malas pa apli: Ua vai Ub. Nevienas gatavas puses: H vai Z.</p>
''' + pll_card(pll['Ua'], 'pll2look pll21') + pll_card(pll['H'], 'pll2look pll21') + '''
<div class="gp-warning"><strong>Pēc katra algoritma</strong> pagriez U, lai augšējā kārta sakristu ar sāniem. Tikai tad vērtē nākamo gadījumu.</div>
<h3>Pilnais PLL – 21 gadījums</h3>
<p>Bultas ar divām smailēm ir maiņa vietām, ar vienu – cikls.</p>
''' + full_pll + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Visas sešas puses vienā krāsā. Ja pēc algoritma palicis viens nepareizs gadījums, tas ir cits PLL – atpazīsti to no jauna.</div>
''' + done('4', 'Kubs salikts ar PLL'), 'pll'))

    p.append(page('drill', 'Algoritmu treniņš', drill('''
<p>Treniņš māca <strong>atpazīt</strong> gadījumu, ne tikai atcerēties algoritmu. Izvēlies kopu, sagatavo gadījumu uz salikta kuba un izpildi algoritmu no galvas.</p>
''', [('oll2look', '2-look OLL malas (3)'), ('ocll', 'OLL stūri – OCLL (7)'), ('pll2look', '2-look PLL (4)'), ('pll21', 'Pilnais PLL (21)'),
      ('oll57', 'Pilnais OLL (57)'), ('f2l', 'F2L (40)'), ('all', 'Viss kopā')],
        'Salikts kubs, <strong>dzeltenais augšā, zaļais pret Tevi</strong>. Visu sagatavošanas secību izpildi ar šo pašu priekšpusi – tad kubs izskatās tieši kā atbildes attēlā.'), 'drill'))

    p.append(page('algs', 'Visi algoritmi', '''
<p>Ātrā uzziņa bez skaidrojumiem: tie paši algoritmi, kas soļu lapās. Pieskaries burtam, lai atvērtu skaidrojumu.</p>
''' + cheat([('2-look OLL malas', [(d['name'], d['alg']) for d in pc.OLL_EDGES])] + oll_cheat + pll_cheat + f2l_cheat), 'algs'))

    p.append(page('summary', 'Kopsavilkums un avoti', '''
<p>Ceļš no iesācēja līdz CFOP parasti ilgst dažus mēnešus. Katrs solis dod izmērāmu rezultātu.</p>
<div class="gp-table-wrap"><table class="gp-table"><tr><th>Posms</th><th>Ko apgūt</th><th>Tipisks laiks</th></tr>
<tr><td>Krusts + F2L pamatgadījumi</td><td>4 algoritmi</td><td>ap 60 s</td></tr>
<tr><td>2-look OLL + 2-look PLL</td><td>14 algoritmi</td><td>zem 40 s</td></tr>
<tr><td>Pilnais PLL</td><td>+17 algoritmi</td><td>zem 30 s</td></tr>
<tr><td>Pilnais OLL</td><td>+47 algoritmi</td><td>zem 20 s</td></tr>
<tr><td>Pilnais F2L</td><td>+36 algoritmi</td><td>zem 15 s</td></tr>
</table></div>
''' + progress('Tavs progress:') + '''
<p class="gp-small">Katrs šīs lapas algoritms ir pārbaudīts kuba simulatorā: apgrieztā secība no salikta kuba dod attēloto gadījumu, un algoritms to atrisina.</p>
''' + sources(SOURCES) + '''
<div class="gp-actions"><button type="button" class="gp-primary" data-gp-goto="drill">Uz treniņu →</button><button type="button" data-gp-goto="intro">Uz sākumu</button></div>
''', 'cheat-pro'))
    return {'eyebrow': '3×3 · Pro · CFOP', 'steps': 4, 'letters': 'R L U D F B r M S E x y z', 'pages': p,
            'nav': ('3×3 Pro navigācija', '3×3 Pro palīdzība un soļi')}


# ------------------------------------------------------------------- 2x2 ----
def oll2_card(d):
    yc = d['c'].count('y')
    return case(d['id'], 'oll2', d['n'], d['alg'], 'Augšā %d dzeltenas uzlīmes. Pagriez kubu ap vertikālo asi, līdz sānu strīpas sakrīt.' % yc, top_fig(d))


def pbl_card(d, sets='pbl'):
    b = d['bottom']
    f = (fig({'data-kind': 'top', 'data-c': 'yyyy', 'data-b': d['b'], 'data-f': d['f'], 'data-l': d['l'], 'data-r': d['r']}, 'Augša') +
         fig({'data-kind': 'top', 'data-c': b['c'], 'data-b': b['b'], 'data-f': b['f'], 'data-l': b['l'], 'data-r': b['r']}, 'Apakša, kubs apgriezts otrādi ar to pašu priekšpusi'))
    return case(d['id'], sets, d['d'], d['alg'], '<strong>Kā turēt:</strong> %s' % d['hold'], f)


def build_2x2():
    oll2 = {d['n']: d for d in pc.OLL2}
    pbl = {d['n']: d for d in pc.PBL}
    CLL_HINT = 'Salīdzini dzeltenās uzlīmes augšā un sānos, tad arī pārējo sānu krāsu rakstu. y burts algoritma sākumā nozīmē pagriezt visu kubu.'
    full_cll, cll_cheat = '', []
    for key, title in pc.CLL_GROUPS:
        items = [d for d in pc.CLL if d['g'] == key]
        cards, rows = '', []
        for d in items:
            if key == 'O':
                name = 'Augša gatava – %s' % ('blakus maiņa (T perm)' if d['n'] == 1 else 'diagonāle (Y perm)')
                cards += case(d['id'], 'cll pbl', name, d['alg'], 'Tas pats algoritms, ko PBL.', top_fig(d))
            else:
                name = 'CLL %s %d' % (key, d['n'])
                cards += case(d['id'], 'cll', name, d['alg'], CLL_HINT, top_fig(d))
            rows.append((name, d['alg']))
        full_cll += group('%s · %d' % (title, len(items)), 'cll:%s' % key, cards)
        cll_cheat.append((title, rows))

    SOURCES = [('cubingcheatsheet.com – 2×2', 'https://cubingcheatsheet.com/algs2x.html', 'Ortega OLL un PBL vienā lapā'),
               ('speedcubedb.com – CLL', 'https://speedcubedb.com/a/2x2/CLL', 'visi 42 CLL ar alternatīvām; no šejienes ņemts šis saraksts'),
               ('jperm.net – CLL', 'https://jperm.net/algs/2x2/cll', 'CLL ar video'),
               ('speedsolving.com wiki – Ortega', 'https://www.speedsolving.com/wiki/index.php/Ortega_Method', 'metodes apraksts')]

    p = []
    p.append(page('intro', 'Ortega – ātrā 2×2 metode', '''
<p>Trīs soļi un 12 algoritmi. Lielākā daļa Tev jau pazīstama no iesācēju soļiem; pa īstam jauni ir daži. Kad Ortega ir rokā, nākamais līmenis ir CLL ar 42 algoritmiem – arī tas ir šajā ceļvedī.</p>
<div class="gp-result"><strong>Tev vajag:</strong> iesācēju metodi bez lapas. Labs Ortega salicējs kubu saliek ātrāk nekā 5 sekundēs.</div>
''' + progress('Apgūtie algoritmi:') + '''
<h3>Ideja</h3>
<ol>
<li><strong>Viena puse</strong> vienā krāsā. Sāni drīkst nesakrist.</li>
<li><strong>OLL</strong> – visa augša vienā krāsā ar vienu no 7 algoritmiem.</li>
<li><strong>PBL</strong> – abu slāņu stūri vietās ar vienu no 5 algoritmiem.</li>
</ol>
<div class="gp-warning"><strong>Atšķirība no iesācēju metodes:</strong> pirmais slānis nav jāsaliek pilnīgi. Sānu krāsas sakārto pašās beigās, abiem slāņiem reizē.</div>
<h3>Vārdi, kas parādīsies tālāk</h3>
<ul>
<li><strong>OLL</strong> – augšas orientācija: visa augša vienā krāsā, vietas vēl nav svarīgas.</li>
<li><strong>PBL</strong> – abu slāņu permutācija: stūri pārvietoti savās vietās augšā un apakšā reizē.</li>
<li><strong>CLL</strong> – pēdējā slāņa stūri vienā algoritmā: orientācija un vietas reizē.</li>
<li><strong>Lukturi</strong> – divi blakus stūri ar vienādu sānu krāsu vienā sānā.</li>
<li><strong>Sānu strīpas attēlos</strong> – krāsainās joslas ap augšas kvadrātu ir augšējā slāņa sānu uzlīmes. Aizmugure attēlā ir augšā, priekšpuse pie Tevis.</li>
</ul>
<h3>Apzīmējumi</h3>
<p>Tie paši burti, kas iesācējam, un y – visa kuba pagrieziens kā U. Pieskaries burtam, lai atvērtu skaidrojumu.</p>
''' + alg("R U R' U' F2 D y") + '''
<button type="button" data-gp-help="moves">Parādīt visu apzīmējumu skaidrojumu</button>
<div class="gp-actions"><button type="button" class="gp-primary" data-gp-goto="1">Sākt ar vienu pusi →</button><button type="button" data-gp-goto="drill">Uz algoritmu treniņu</button></div>
''', 'ortega'))

    p.append(page('1', 'Viena puse', '''
<p class="gp-goal">Rezultāts: viena puse vienā krāsā, parasti baltā. Sānu krāsas šoreiz nekontrolē.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Sāc ar diviem baltiem stūriem, kas jau ir blakus. Turi tos apakšā un pievieno pārējos divus.</div>
''' + fig({'data-kind': 'face', 'data-c': 'wwww'}, 'Pietiek ar vienu pusi vienā krāsā.') + '''
<ol>
<li>Atrodi divus baltos stūrus, kurus var savienot vienā griezienā. Novieto tos apakšā.</li>
<li>Katru nākamo balto stūri ar U novieto virs tukšās vietas un ielaid ar 2–3 griezieniem. Vari lietot arī iesācēju R U R' U'.</li>
<li>Neskaties uz sānu krāsām. Viss, kas svarīgs, ir balts apakšā.</li>
</ol>
<div class="gp-check"><strong>Vai gatavs?</strong> Visa apakšpuse balta. Sāni drīkst būt jaukti.</div>
<details><summary>Kāpēc nelikt pilnu slāni?</summary><p>Pilns slānis prasa vidēji par 3–4 griezieniem vairāk. PBL solis sakārto abus slāņus reizē, tāpēc šis darbs būtu lieks.</p></details>
''' + done('1', 'Apakšpuse vienā krāsā'), 'side'))

    p.append(page('2', 'OLL – augša vienā krāsā', '''
<p class="gp-goal">Rezultāts: visa augša dzeltena. Septiņi gadījumi, viens algoritms katram.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Gatavā puse apakšā. Saskaiti dzeltenās uzlīmes augšā: 1 – Sune vai Antisune; 2 – U, T vai L; 0 – Pi vai H. Tad pagriez kubu ap vertikālo asi, līdz sakrīt arī sānu strīpas.</div>
''' + ''.join(oll2_card(oll2[n]) for n in ('Sune', 'Antisune', 'U', 'T', 'L', 'Pi', 'H')) + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Augša vienā krāsā. Apakša joprojām vienā krāsā.</div>
<details><summary>Var sākt tikai ar diviem</summary><p>Ar Sune un Antisune vien var atrisināt jebkuru gadījumu divos piegājienos. Pārējos piecus pievieno pa vienam.</p></details>
''' + done('2', 'Augša vienā krāsā'), 'oll2'))

    p.append(page('3', 'PBL – abi slāņi vietās', '''
<p class="gp-goal">Rezultāts: kubs salikts. Katram slānim ir trīs stāvokļi: gatavs, blakus maiņa vai diagonāle.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Katram slānim atrodi <strong>lukturus</strong> – vienu sānu vienā krāsā. Ja tāds ir: blakus maiņa. Ja katrs sāns vienā krāsā: slānis gatavs. Ja neviena sāna vienā krāsā: diagonāle. Kubu drīkst apgriezt otrādi – abas puses jau ir vienā krāsā. Katrai kartītei ir divi attēli: augša un apakša.</div>
<details><summary>Abi slāņi gatavi</summary><p>Algoritms nav vajadzīgs. Izlīdzini ar U un, ja vajag, D.</p></details>
''' + ''.join(pbl_card(pbl[k]) for k in ('adj-top', 'diag-top', 'adj-adj', 'diag-diag', 'adj-diag')) + '''
<div class="gp-warning"><strong>Pēc algoritma</strong> izlīdzini abus slāņus ar U un D. Ja slānis, kam jābūt augšā, ir apakšā, apgriez kubu pirms algoritma.</div>
<div class="gp-check"><strong>Vai gatavs?</strong> Visas sešas puses vienā krāsā.</div>
''' + done('3', 'Kubs salikts ar PBL'), 'pbl'))

    p.append(page('4', 'CLL – pēdējais slānis vienā algoritmā', '''
<p class="gp-goal">Rezultāts: pēc pilna pirmā slāņa visa augša gatava ar vienu algoritmu. Nav atsevišķa OLL un PBL.</p>
<div class="gp-result"><strong>Kad pāriet:</strong> kad Ortega iet zem 5 sekundēm un gribi zem 3. Līdz tam Ortega ir pilnvērtīga pro metode.</div>
<div class="gp-grip"><strong>Kā turēt</strong><br>Pirmais slānis <strong>pilnībā</strong> salikts apakšā, arī sānu krāsas. Vispirms atpazīsti augšas figūru kā Ortega OLL (Sune, Antisune, U, T, L, Pi, H), tad grupā atrodi kartīti, kurai sakrīt arī pārējās sānu krāsas. Attēlos krāsas ir piemērs ar zaļo priekšā; svarīgs ir raksts, kuras uzlīmes ir vienādas.</div>
<h3>Kā mācīties</h3>
<ol>
<li>Sāc ar grupu, kuras Ortega OLL Tev jau labi padodas. Sešas kartītes vienā grupā ir viena nedēļa.</li>
<li>Katru jauno kartīti trenē treniņa lapā ar kopu “CLL”.</li>
<li>Kamēr grupa nav apgūta, tās gadījumus turpini likt ar Ortega OLL + PBL. Abas metodes var jaukt.</li>
</ol>
<h3>Visi 42 gadījumi</h3>
''' + full_cll + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Kubs salikts uzreiz pēc algoritma, atliek tikai izlīdzināt U.</div>
<div class="gp-table-wrap"><table class="gp-table"><tr><th>Metode</th><th>Algoritmi</th><th>Kad</th></tr>
<tr><td>Iesācēju</td><td>4</td><td>Sākums – vienmēr strādā</td></tr>
<tr><td>Ortega</td><td>12</td><td>Zem 5 s, maz jāmācās</td></tr>
<tr><td>CLL</td><td>42</td><td>Pēdējais slānis vienā skatienā</td></tr>
</table></div>
''' + done('4', 'CLL grupas apgūtas'), 'cll'))

    p.append(page('drill', 'Algoritmu treniņš', drill('''
<p>Sagatavo gadījumu uz salikta kuba, atpazīsti to un izpildi algoritmu no galvas.</p>
''', [('oll2', 'Ortega OLL – 7'), ('pbl', 'PBL – 5'), ('cll', 'CLL – 42'), ('all', 'Viss kopā')],
        'Salikts kubs, <strong>dzeltenais augšā, zaļais pret Tevi</strong>. Sagatavošanas secību izpildi ar šo pašu priekšpusi.'), 'drill'))

    p.append(page('algs', 'Visi algoritmi un avoti', '''
<p>Ātrā uzziņa bez skaidrojumiem: tie paši algoritmi, kas soļu lapās.</p>
''' + cheat([('Ortega OLL', [(d['n'], d['alg']) for d in pc.OLL2]), ('PBL', [(d['d'], d['alg']) for d in pc.PBL])] + cll_cheat) +
        progress('Tavs progress:') + sources(SOURCES), 'cheat-pro'))
    return {'eyebrow': '2×2 · Pro · Ortega un CLL', 'steps': 4, 'letters': 'R L U D F B y', 'pages': p,
            'nav': ('2×2 Pro navigācija', '2×2 Pro palīdzība un soļi')}


# -------------------------------------------------------------- Pyraminx ----
def build_pyraminx():
    src = read(GUIDES['py']['file'])
    m = re.search(r'<figure class="gpy-grip-figure">\s*<svg class="gpy-topview".*?</figure>', src, re.S)
    if not m:
        raise SystemExit('Pyraminx beginner top view figure not found')
    topview = (m.group(0).replace('gpy-grip-figure', 'gp-grip-figure').replace('gpy-topview', 'gp-topview')
               .replace(' data-gpy-topview', ''))

    def pycase(cid, sets=None):
        d = pc.PYRA_BY_ID[cid]
        return case(cid, sets or d['sets'], d['name'], d['alg'], d['hint'])

    SOURCES = [('speedsolving.com wiki – Pyraminx algorithms', 'https://www.speedsolving.com/wiki/index.php/Pyraminx_algorithms', 'L4E un ELL algoritmi'),
               ('cubingapp.com – Pyraminx L4E', 'https://cubingapp.com/algorithms/Pyraminx-L4E', 'visi L4E gadījumi ar attēliem'),
               ('speedsolving.com – Oka', 'https://www.speedsolving.com/wiki/index.php/Oka_Method', 'Oka un radniecīgās metodes'),
               ('WCA notācija', 'https://www.worldcubeassociation.org/regulations/#12e', 'oficiālie Pyraminx apzīmējumi')]
    L4E = ('l4e-cw', 'l4e-ccw', 'flip', 'sledge', 'hedge')
    ELL = ('sledge', 'hedge', 'uperm', 'uperm-m', 'flip')

    p = []
    p.append(page('intro', 'L4E un Oka – ātrās metodes', '''
<p>Abas pro metodes sāk ar stūriem un galiem intuitīvi, tāpat kā iesācēju 1. solī. Atšķirība ir malās: tās atrisina gudrāk un ar mazāk griezieniem.</p>
<div class="gp-result"><strong>Tev vajag:</strong> iesācēju metodi bez lapas un stabilu zaļās sejas atpazīšanu pēc S gabaliem.</div>
''' + progress('Apgūtie algoritmi:') + '''
<h3>Divas pieejas</h3>
<ol>
<li><strong>L4E</strong> (Last 4 Edges – pēdējās četras malas) – saliec visu, izņemot pēdējās četras malas, tad tās vienā piegājienā. Ieteicamais sākums.</li>
<li><strong>Oka</strong> (top-first – no augšas) – sāc no augšas, vienu malu apzināti atstāj nepareizā vietā kā “atslēgas caurumu”.</li>
</ol>
<div class="gp-warning"><strong>Jaunu algoritmu gandrīz nav.</strong> L4E intuitīvā versija lieto tos pašus trīs iesācēju 3. soļa algoritmus, tikai gudrākā secībā. Pa īstam jauni ir divi īsi četru griezienu ievietojumi un divi U perm.</div>
<h3>Vārdi, kas parādīsies tālāk</h3>
<ul>
<li><strong>V forma</strong> – salikts viss, izņemot četras malas: trīs augšējās un viena apakšējā.</li>
<li><strong>L4E</strong> – pēdējās četras malas (Last 4 Edges): metodes nosaukums un tās galvenais solis.</li>
<li><strong>ELL</strong> – pēdējā slāņa malas (Edges of Last Layer): Oka nobeiguma algoritmi.</li>
<li><strong>PK, PL, AM</strong> – priekšā pa kreisi, priekšā pa labi, aizmugures mala, kā iesācēju 3. solī.</li>
</ul>
<h3>Apzīmējumi</h3>
<p>Lielie burti griež virsotni ar diviem slānīšiem, mazie tikai galu. Pieskaries burtam, lai atvērtu skaidrojumu.</p>
''' + alg("U L R B u l") + '''
<button type="button" data-gp-help="moves">Parādīt visu apzīmējumu skaidrojumu</button>
<div class="gp-actions"><button type="button" class="gp-primary" data-gp-goto="1">Sākt ar V formu →</button><button type="button" data-gp-goto="drill">Uz algoritmu treniņu</button></div>
''', 'cfop'))

    p.append(page('1', 'V forma', '''
<p class="gp-goal">Rezultāts: visi četri stūri ar galiem un divas blakus apakšējās malas. Iztrūkst tieši četras malas.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Zaļā seja apakšā, kā iesācēju metodē. Abas ieliktās malas ir apakšējās sejas divas malas; trešā apakšējā mala paliek tukša.</div>
''' + fig({'data-kind': 'pyra', 'data-c': 'ggggggggg', 'data-mark': '0,2,4,5,6,7,8'}, 'V: gatavs viss, izņemot vienu apakšējo malu un trīs augšējās.', small=False) + '''
<ol>
<li>Pielīdzini četrus S gabalus zaļajai sejai un galus saviem S – kā iesācēju 1. solī.</li>
<li>Ievieto divas zaļas malas ar iesācēju A vai B ievietojumu. Trešo apzināti atstāj.</li>
<li>Ar treniņu abas malas izplāno 15 sekunžu apskatē un izpildi bez apstāšanās.</li>
</ol>
<div class="gp-check"><strong>Vai gatavs?</strong> Divas apakšējās malas sakrīt ar abām savām sejām. Visi S un gali ir vietās.</div>
<details><summary>Kāpēc neielikt arī trešo malu?</summary><p>Pēdējo četru malu gadījumi ir īsāki nekā trešās malas ievietošana un tad trīs augšējo malu sakārtošana. Ar laiku šo soli var izlaist pilnībā.</p></details>
''' + done('1', 'V forma gatava'), 'v'))

    p.append(page('2', 'L4E – pēdējās četras malas', '''
<p class="gp-goal">Rezultāts: piramīda salikta. Četras malas vienā vai divos piegājienos.</p>
<div class="gp-grip"><strong>Kā turēt</strong><br>Zaļā seja apakšā, tukšā apakšējā malas vieta <strong>priekšā</strong>. Pirms gadījuma izvēles pielīdzini augšējo S sāniem, kā iesācēju 3. solī.</div>
''' + topview + '''
<h3>Intuitīvā L4E – sākumam</h3>
<p>Ievieto priekšējo apakšējo malu ar iesācēju A vai B ievietojumu. Tad atlikušās trīs augšējās malas ar cikliem vai apgriešanu:</p>
''' + pycase('l4e-cw') + pycase('l4e-ccw') + pycase('flip') + '''
<h3>Algoritmiskā L4E – kodols</h3>
<p>Kad apakšējā mala vēl nav vietā, bet ir priekšā augšā, četri griezieni ieliek to ar apgriešanos. Tas ietaupa veselu piegājienu.</p>
''' + pycase('sledge') + pycase('hedge') + '''
<div class="gp-warning"><strong>Pilnajā L4E ir apmēram 35 gadījumi.</strong> Šeit ir pārbaudītais kodols, ar ko var atrisināt jebkuru stāvokli divos piegājienos. Pilnu sarakstu ar attēliem skaties avotos algoritmu lapā.</div>
<div class="gp-check"><strong>Vai gatavs?</strong> Visas četras sejas vienā krāsā. Ja pēc cikla divas malas ir apgrieztas, tas ir parasts otrais piegājiens, nevis kļūda.</div>
''' + done('2', 'Pēdējās četras malas saliktas'), 'l4e'))

    p.append(page('3', 'Oka – no augšas', '''
<p class="gp-goal">Rezultāts: piramīda salikta, sākot no augšas. Vienu malu apzināti atstāj nepareizā vietā; tukšā vieta ir “atslēgas caurums”, caur kuru sakārto pārējo.</p>
<div class="gp-result"><strong>Kad mēģināt:</strong> kad L4E iet stabili. Oka ir konceptuāla metode: tās soļi nav publicēti kā notācija, bet nobeigums ir konkrēti algoritmi.</div>
<div class="gp-grip"><strong>Kā turēt</strong><br>Sāc ar jebkuru seju augšā. Pēdējā slāņa ELL algoritmus izpildi ar pabeigto seju apakšā un neatrisinātajām malām augšā, tāpat kā L4E.</div>
<ol>
<li>Saliec vienu malu ar abiem tās stūriem un ieliec vēl vienu malu <strong>pareizi orientētu, bet nepareizā vietā</strong>. Tā ir Oka mala.</li>
<li>Caur brīvo vietu sakārto stūrus un S gabalus, neizjaucot salikto.</li>
<li>Vienā solī pārcel Oka malu uz tās īsto vietu un aizver atslēgas caurumu.</li>
<li>Pabeidz pēdējā slāņa malas ar ELL algoritmiem zemāk.</li>
</ol>
<h3>ELL – pēdējā slāņa malas</h3>
''' + ''.join(pycase(cid, 'ell') for cid in ELL) + '''
<div class="gp-check"><strong>Vai gatavs?</strong> Visas četras sejas vienā krāsā. Ja palikušas trīs malas pa apli vai divas apgrieztas, tas ir vēl viens ELL gadījums no saraksta.</div>
<details><summary>Radniecīgās metodes</summary><p><strong>WO</strong>: saliec visas trīs augšas malas, tad viens algoritms centriem. <strong>Nutella</strong>: divas malas pretējos stāvokļos. Oka atšķiras ar apzināti nepareizi novietoto malu.</p></details>
''' + done('3', 'Oka koncepts saprasts'), 'oka'))

    p.append(page('drill', 'Algoritmu treniņš', drill('''
<p>Sagatavo gadījumu uz saliktas piramīdas, atpazīsti to un izpildi algoritmu no galvas.</p>
''', [('l4e', 'L4E kodols (5)'), ('ell', 'ELL nobeigums (5)'), ('all', 'Viss kopā')],
        'Salikta piramīda, <strong>zaļā seja apakšā</strong>, izvēlētā priekšpuse pret Tevi. Sagatavošanas secību izpildi ar šo pašu priekšpusi.'), 'drill'))

    p.append(page('algs', 'Visi algoritmi un avoti', '''
<p>Ātrā uzziņa bez skaidrojumiem: tie paši algoritmi, kas soļu lapās.</p>
''' + cheat([('L4E', [(pc.PYRA_BY_ID[c]['name'], pc.PYRA_BY_ID[c]['alg']) for c in L4E]),
             ('Oka ELL', [(pc.PYRA_BY_ID[c]['name'], pc.PYRA_BY_ID[c]['alg']) for c in ELL])]) +
        progress('Tavs progress:') + sources(SOURCES), 'cheat-pro'))
    return {'eyebrow': 'Pyraminx · Pro · L4E un Oka', 'steps': 3, 'letters': 'U L R B u l', 'pages': p,
            'nav': ('Pyraminx Pro navigācija', 'Pyraminx Pro palīdzība un soļi')}


BUILDERS = {'a2': build_2x2, 'a3': build_3x3, 'py': build_pyraminx}


def namespace(text, cube):
    g = GUIDES[cube]
    return text.replace('guidepro', g['root']).replace('gp-', g['ns'] + '-')


def render(cube):
    g = GUIDES[cube]
    spec = BUILDERS[cube]()
    runtime = read(os.path.join(HERE, 'pro_runtime.html')).strip()
    body = (MARK + '\n'
            '<!-- Generated by _build/pro_blocks.py from _build/pro_cases.py; edit those and rerun, do not edit this block by hand. -->\n'
            '<div class="guidepro" data-gp-cube="%s" data-gp-key="%s" data-gp-steps="%d" data-gp-letters="%s">\n'
            % (cube, g['key'], spec['steps'], spec['letters']) +
            heading(spec['eyebrow']) + '\n' + ''.join(spec['pages']) + NAV % spec['nav'] + '\n' + runtime + '\n</div>\n' + END)
    out = namespace(body, cube)
    if '—' in out:
        raise SystemExit('em dash in generated %s Pro block' % cube)
    return out


def write_all(check=False):
    changed = []
    for cube, g in GUIDES.items():
        src = read(g['file'])
        if src.count(MARK) != 1 or src.count(END) != 1:
            raise SystemExit('Pro markers not unique in %s' % g['file'])
        before, rest = src.split(MARK, 1)
        _, after = rest.split(END, 1)
        new = before + render(cube) + after
        if new != src:
            changed.append(g['file'])
            if not check:
                with io.open(g['file'], 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new)
    return changed


if __name__ == '__main__':
    check = '--check' in sys.argv
    changed = write_all(check)
    for path in changed:
        print(('DIFFERS ' if check else 'written ') + os.path.relpath(path, ROOT))
    if not changed:
        print('all Pro blocks up to date')
    sys.exit(1 if (check and changed) else 0)
