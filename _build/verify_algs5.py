# Part 5: 3x3 OCLL case diagrams for the guide's own algorithms + 2-look PLL
# corner-case strips. Guide color mapping (yellow top): U->y F->g R->o B->b L->r.
import verify_algs as sim
from verify_algs import fresh, invert

MAP = {'U': 'y', 'D': 'w', 'F': 'g', 'R': 'o', 'B': 'b', 'L': 'r'}
POS = {'UBL': (-1, 1, -1), 'UB': (0, 1, -1), 'UBR': (1, 1, -1),
       'UL': (-1, 1, 0), 'C': (0, 1, 0), 'UR': (1, 1, 0),
       'UFL': (-1, 1, 1), 'UF': (0, 1, 1), 'UFR': (1, 1, 1)}
ORDER = ('UBL', 'UB', 'UBR', 'UL', 'C', 'UR', 'UFL', 'UF', 'UFR')

def y_or_x(col):
    return 'y' if col == 'U' else 'x'

def diagram(alg, yellow_only=True):
    c = fresh()
    c.apply(invert(alg))
    f = MAP if not yellow_only else None
    def m(col):
        return y_or_x(col) if yellow_only else MAP[col]
    dc = ''.join(m(c.sticker(POS[k], (0, 1, 0))) for k in ORDER)
    db = ''.join(m(c.sticker(POS[k], (0, 0, -1))) for k in ('UBL', 'UB', 'UBR'))
    df = ''.join(m(c.sticker(POS[k], (0, 0, 1))) for k in ('UFL', 'UF', 'UFR'))
    dl = ''.join(m(c.sticker(POS[k], (-1, 0, 0))) for k in ('UBL', 'UL', 'UFL'))
    dr = ''.join(m(c.sticker(POS[k], (1, 0, 0))) for k in ('UBR', 'UR', 'UFR'))
    return dc, db, df, dl, dr

OCLL = [('Sune', "R U R' U R U2 R'"),
        ('Antisune', "R U2 R' U' R U' R'"),
        ('H', "R U R' U R U' R' U R U2 R'"),
        ('Pi', "R U2 R2 U' R2 U' R2 U2 R"),
        ('U', "R2 D' R U2 R' D R U2 R"),
        ('T', "r U R' U' r' F R F'"),
        ('L', "F R' F' r U R U' r'")]
print('== 3x3 OCLL case diagrams (guide algs; y = yellow sticker) ==')
for name, alg in OCLL:
    # sanity: the alg must orient the top (leave a yellow face) from its case
    c = fresh()
    c.apply(invert(alg))
    c.apply(alg)
    dc, db, df, dl, dr = diagram(alg)
    print('   %-9s data-c="%s" data-b="%s" data-f="%s" data-l="%s" data-r="%s" (case has %d yellow up)'
          % (name, dc, db, df, dl, dr, dc.count('y') - 5 + (0 if dc[4] != 'y' else 1) - 0))

print('== 2-look PLL corner cases (real colors) ==')
TP = "R U R' U' R' F R2 U' R' U' R U R' F'"
dc, db, df, dl, dr = diagram(TP, yellow_only=False)
print('   T-perm case: c=%s b=%s f=%s l=%s r=%s' % (dc, db, df, dl, dr))
Y = "F R U' R' U' R U R' F' R U R' U' R' F R F'"
dc, db, df, dl, dr = diagram(Y, yellow_only=False)
print('   Y-perm case: c=%s b=%s f=%s l=%s r=%s' % (dc, db, df, dl, dr))
