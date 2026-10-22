import pygame
import os, math, random, pygame
from data import *
from lang import T
try: HERE = os.path.dirname(os.path.abspath(__file__))
except NameError: HERE = os.getcwd()
FONT = BIG = MED = None
FONT_FILE = os.path.join(HERE, "SVN-Retron 2000.ttf")
def _sysfont(sz):
    try: return pygame.font.SysFont("arial", sz)
    except Exception: return pygame.font.Font(None, sz + 4)
_dg = {}
def num(s, col=(255, 255, 255), big=0):
    out = []; w = 0
    for ch in s:
        k = (ch, col, big); g = _dg.get(k)
        if g is None:
            f = (FONT, BIG, MED)[big]; a, b = f.render(ch, True, col), f.render(ch, True, (0, 0, 0))
            g = pygame.Surface((a.get_width() + 2, a.get_height() + 2), pygame.SRCALPHA)
            g.blit(b, (2, 2)); g.blit(b, (1, 1)); g.blit(a, (0, 0)); _dg[k] = g
        out.append(g); w += g.get_width() - 2
    return out, w
def ntxt(scr, s, x, y, col=(255, 255, 255), big=0):
    gl, _ = num(s, col, big)
    for g in gl: scr.blit(g, (x, y)); x += g.get_width() - 2
def _font(sz):
    try: return pygame.font.Font(FONT_FILE, sz)
    except Exception: return _sysfont(sz + 1)
BASES, PCARS, PREVS = {}, [], []
_sc, _tc, _pc, _sh = {}, {}, {}, {}
def _surf(w, h):
    s = pygame.Surface((w, h)); s.fill(KEY); return s
def _fin(s):
    s = s.convert(); s.set_colorkey(KEY); return s
def _glow(r, col):
    s = pygame.Surface((2 * r, 2 * r))
    for i in range(r, 0, -2):
        k = (1 - i / r) ** 2
        pygame.draw.circle(s, (int(col[0] * k), int(col[1] * k), int(col[2] * k)), (r, r), i)
    return s.convert()
def _wx(snow, seed, n, col, z):
    r = random.Random(seed); s = _surf(W, H); d = pygame.draw
    for _ in range(n):
        x, y = r.randrange(W), r.randrange(H)
        if snow: d.rect(s, col, (x, y, z, z))
        else: d.line(s, col, (x, y), (x - 2, y + 6))
    return _fin(s)
CW_, CL_ = 18, 30
def _layers(body, kind):
    dk = tuple(c * 6 // 10 for c in body); lt = tuple(min(255, c + 55) for c in body)
    gl, tire, red, lamp = (46, 72, 112), (16, 16, 20), (255, 55, 45), (250, 245, 200)
    R, L = pygame.draw.rect, []
    for z in range(9):
        s = pygame.Surface((CW_, CL_), pygame.SRCALPHA); L.append(s)
        if z < 4 and kind not in (5, 7,8):
            R(s, ((24, 24, 30), dk, body, body)[z], (2, 2, 14, 26) if z == 0 else ((1, 1, 16, 28) if z < 3 else (1, 2, 16, 26)))
            if z < 3:
                for x, y in ((0, 3), (15, 3), (0, 20), (15, 20)): R(s, tire, (x, y, 3, 7))
            if z > 1:
                b = z == 3
                R(s, red, (2, 27 - b, 4, 2)); R(s, red, (12, 27 - b, 4, 2))
                R(s, lamp, (2, 1 + b, 4, 2)); R(s, lamp, (12, 1 + b, 4, 2))
                if z == 2: R(s, (235, 235, 235), (7, 27, 4, 2))
        elif kind == 5:
            hm, vz, gr = (240, 240, 245), (40, 60, 120), (24, 24, 30)
            if z < 4:
                c = (6, 10, 10, 6)[z]; R(s, tire, (0, 23 - c // 2, 4, c)); R(s, tire, (14, 23 - c // 2, 4, c))
                c = (4, 6, 6, 4)[z]; R(s, tire, (1, 5 - c // 2, 3, c)); R(s, tire, (14, 5 - c // 2, 3, c))
            if z == 0: R(s, gr, (4, 4, 10, 2)); R(s, gr, (4, 22, 10, 2))
            elif z == 1: R(s, dk, (4, 1, 10, 28))
            elif z == 2: R(s, body, (4, 1, 10, 27)); R(s, body, (3, 9, 12, 9)); R(s, lt, (3, 0, 12, 2)); R(s, red, (5, 27, 3, 2)); R(s, red, (10, 27, 3, 2))
            elif z == 3: R(s, body, (5, 0, 8, 9)); R(s, lt, (3, 9, 3, 9)); R(s, lt, (12, 9, 3, 9)); R(s, dk, (6, 12, 6, 9)); R(s, dk, (5, 21, 8, 6))
            elif z == 4: R(s, lt, (6, 1, 6, 6)); R(s, gr, (5, 9, 8, 2)); R(s, dk, (5, 18, 8, 4)); R(s, dk, (6, 22, 6, 3))
            elif z == 5: R(s, lt, (6, 14, 6, 7)); R(s, lt, (5, 10, 2, 5)); R(s, lt, (11, 10, 2, 5))
            elif z == 6: R(s, hm, (6, 14, 6, 6)); R(s, vz, (7, 14, 4, 2))
            elif z == 7: R(s, hm, (6, 14, 6, 6)); R(s, vz, (7, 14, 4, 2)); R(s, body, (8, 16, 2, 4))
            else: R(s, hm, (7, 15, 4, 4))
        elif kind == 7:
            if z < 3:
                for x, y, w, l in ((0, 3, 3, 6), (15, 3, 3, 6), (0, 19, 4, 8), (14, 19, 4, 8)): R(s, tire, (x, y, w, l))
            if z == 0: R(s, (24, 24, 30), (5, 2, 8, 26))
            elif z == 1: R(s, dk, (6, 2, 6, 26)); R(s, dk, (1, 0, 16, 2))
            elif z == 2: R(s, body, (6, 2, 6, 26)); R(s, body, (3, 11, 12, 11)); R(s, dk, (1, 0, 16, 1))
            elif z == 3: R(s, body, (6, 3, 6, 24)); R(s, body, (3, 12, 12, 10)); R(s, red, (7, 27, 4, 2))
            elif z == 4: R(s, body, (6, 11, 6, 15)); R(s, lt, (7, 3, 4, 8)); R(s, lt, (4, 12, 10, 9))
            elif z == 5: R(s, dk, (6, 12, 6, 8)); R(s, (40, 90, 220), (7, 14, 4, 4)); R(s, lt, (5, 21, 8, 4))
            elif z == 6: R(s, dk, (7, 17, 4, 5)); R(s, dk, (8, 23, 2, 3)); R(s, dk, (1, 25, 16, 2))
            elif z == 7: R(s, lt, (1, 25, 16, 2)); R(s, dk, (1, 24, 1, 4)); R(s, dk, (16, 24, 1, 4))
            else: R(s, lt, (1, 25, 16, 1))
        elif kind == 8:
            gy_, bk = (62, 62, 70), (24, 24, 30)
            if z < 3: R(s, tire, (0, 4, 3, 7)); R(s, tire, (15, 4, 3, 7))
            if z < 5:
                R(s, tire, (0, 17, 5, 12) if z < 4 else (1, 18, 3, 10)); R(s, tire, (13, 17, 5, 12) if z < 4 else (14, 18, 3, 10))
            if z == 0: R(s, bk, (6, 2, 6, 26)); R(s, bk, (1, 5, 16, 2)); R(s, bk, (1, 22, 16, 2))
            elif z == 1: R(s, dk, (5, 1, 8, 28))
            elif z == 2: R(s, body, (5, 1, 8, 17)); R(s, dk, (4, 17, 10, 12)); R(s, lamp, (5, 0, 3, 2)); R(s, lamp, (10, 0, 3, 2))
            elif z == 3: R(s, body, (5, 1, 8, 16)); R(s, dk, (4, 17, 10, 12)); R(s, red, (4, 28, 3, 2)); R(s, red, (11, 28, 3, 2))
            elif z == 4: R(s, body, (5, 2, 8, 14)); R(s, body, (4, 17, 10, 11))
            elif z == 5: R(s, lt, (6, 3, 6, 12)); R(s, body, (0, 18, 5, 10)); R(s, body, (13, 18, 5, 10)); R(s, dk, (4, 17, 10, 11)); R(s, gy_, (11, 4, 2, 2))
            elif z == 6: R(s, lt, (0, 18, 5, 10)); R(s, lt, (13, 18, 5, 10)); R(s, gl, (4, 17, 10, 11)); R(s, gy_, (11, 4, 2, 2))
            elif z == 7:
                R(s, body, (3, 16, 12, 13)); R(s, dk, (3, 16, 12, 1)); R(s, gy_, (11, 4, 2, 2))
                for x, y in ((3, 16), (13, 16), (3, 27), (13, 27)): R(s, dk, (x, y, 2, 2))
            else: R(s, lt, (4, 17, 10, 11)); R(s, (255, 170, 30), (8, 20, 2, 2)); R(s, (30, 30, 34), (11, 4, 2, 2))
        elif kind == 0:
            if z < 6: R(s, body if z == 4 else lt, (2, 3, 14, 24))
            elif z == 6: R(s, dk, (3, 11, 12, 12)); R(s, gl, (4, 12, 10, 11))
            elif z == 7: R(s, dk, (3, 12, 12, 10)); R(s, gl, (4, 13, 10, 9)); R(s, dk, (3, 25, 12, 2))
            else: R(s, lt, (4, 14, 10, 7))
        elif kind == 2:
            if z == 4: R(s, body, (3, 1, 12, 26))
            elif z == 5: R(s, lt, (4, 3, 10, 22))
            elif z == 6:
                R(s, dk, (5, 12, 8, 9)); R(s, gl, (6, 13, 6, 7)); R(s, dk, (3, 24, 2, 3)); R(s, dk, (13, 24, 2, 3))
            elif z == 7: R(s, body, (0, 24, 18, 3))
            else: R(s, lt, (0, 24, 18, 2))
        elif kind == 3:
            if z < 6:
                R(s, body, (1, 2, 16, 26) if z == 4 else (2, 3, 14, 24)); R(s, (238, 238, 238), (7, 2, 4, 24))
            elif z == 6: R(s, dk, (6, 3, 6, 6)); R(s, dk, (3, 12, 12, 12)); R(s, gl, (4, 13, 10, 10))
            elif z == 7: R(s, lt, (4, 13, 10, 9)); R(s, dk, (2, 25, 14, 2))
        elif kind == 6:
            cg = (200, 200, 210)
            if z == 4: R(s, body, (3, 4, 12, 22))
            elif z == 5: R(s, lt, (4, 5, 10, 20))
            elif z == 6: R(s, dk, (4, 12, 10, 10)); R(s, cg, (3, 10, 2, 14)); R(s, cg, (13, 10, 2, 14))
            else: R(s, cg, (3, 10, 12, 2)); R(s, cg, (3, 22, 12, 2))
        elif kind == 4:
            if z < 6: R(s, body, (1, 2, 16, 26) if z == 4 else (1, 3, 16, 24))
            elif z == 6:
                R(s, lt, (1, 5, 2, 18)); R(s, lt, (15, 5, 2, 18)); R(s, dk, (4, 10, 10, 14)); R(s, gl, (5, 11, 8, 12))
            elif z == 7: R(s, dk, (4, 10, 10, 13)); R(s, gl, (5, 11, 8, 11)); R(s, dk, (2, 25, 14, 2))
            else: R(s, lt, (5, 11, 8, 10))
        else:
            R(s, (140, 144, 152) if z == 8 else (205, 207, 212), (1, 13, 16, 15))
            if z < 8: R(s, dk, (8, 13, 1, 15))
            if z < 6: R(s, body, (1, 2, 16, 11 if z == 4 else 10))
            elif z == 6: R(s, dk, (2, 3, 14, 8)); R(s, gl, (3, 4, 12, 6))
            elif z == 7: R(s, lt, (2, 3, 14, 8))
    return L
def _outline(f, col=(16, 14, 24)):
    w, h = f.get_size(); sil = _surf(w, h); pygame.mask.from_surface(f).to_surface(sil, setcolor=col, unsetcolor=None); sil.set_colorkey(KEY)
    n = _surf(w + 2, h + 1)
    for dx, dy in ((0, 1), (2, 1), (1, 0)): n.blit(sil, (dx, dy))
    n.blit(f, (1, 1)); return _fin(n)
def _stack(L, S, angles, sq=0.22, shade=0.0):
    big = [pygame.transform.scale(l, (l.get_width() * S, l.get_height() * S)) for l in L]
    if shade:
        n_ = max(1, len(big) - 1)
        for z, l in enumerate(big):
            v = int(255 * (1.0 - shade * (1.0 - z / n_))); l.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
    fr = []; mw = mh = 0
    for a in angles:
        row = []
        for b in big:
            r = pygame.transform.rotate(b, -a); w, h = r.get_size()
            row.append(pygame.transform.scale(r, (w, max(1, int(h * sq)))))
        fr.append(row); mw = max(mw, row[0].get_width()); mh = max(mh, row[0].get_height())
    ch = mh + len(L) * S + 1; cy = ch - mh // 2
    out = []
    for row in fr:
        s = _surf(mw, ch)
        for z, r in enumerate(row):
            o0 = z * S
            for o in range(o0, o0 + S):
                s.blit(r, r.get_rect(center=(mw // 2, cy - o)))
        out.append(_fin(s))
    return out
def _pine():
    s = _surf(24, 40); d = pygame.draw
    d.rect(s, (90, 60, 30), (10, 30, 4, 10))
    d.polygon(s, (20, 110, 50), [(12, 0), (3, 14), (21, 14)])
    d.polygon(s, (26, 130, 60), [(12, 7), (1, 24), (23, 24)])
    d.polygon(s, (34, 150, 70), [(12, 15), (0, 33), (24, 33)])
    return _fin(s)
def _spine():
    s = _surf(24, 40); d = pygame.draw
    d.rect(s, (90, 62, 40), (10, 30, 4, 10))
    d.polygon(s, (28, 96, 72), [(12, 0), (3, 14), (21, 14)]); d.polygon(s, (245, 248, 252), [(12, 0), (7, 8), (17, 8)])
    d.polygon(s, (30, 108, 78), [(12, 7), (1, 24), (23, 24)]); d.polygon(s, (245, 248, 252), [(12, 7), (6, 16), (18, 16)])
    d.polygon(s, (34, 118, 84), [(12, 15), (0, 33), (24, 33)]); d.polygon(s, (245, 248, 252), [(12, 15), (5, 26), (19, 26)])
    return _fin(s)
def _tree(c1=(30, 125, 50), c2=(40, 150, 62), c3=(52, 168, 76)):
    s = _surf(28, 40); d = pygame.draw
    d.rect(s, (95, 62, 32), (12, 24, 4, 16))
    d.circle(s, c1, (14, 14), 13); d.circle(s, c2, (9, 19), 8); d.circle(s, c3, (19, 18), 8)
    return _fin(s)
def _lamp():
    s = _surf(20, 40); d = pygame.draw
    d.rect(s, (90, 92, 104), (9, 10, 2, 30)); d.rect(s, (90, 92, 104), (7, 38, 6, 2))
    d.rect(s, (70, 72, 84), (4, 7, 12, 3))
    d.circle(s, (150, 140, 80), (10, 8), 7); d.circle(s, (255, 238, 160), (10, 8), 4); d.circle(s, (255, 252, 225), (10, 8), 2)
    return _fin(s)
def _tower():
    s = _surf(32, 56); d = pygame.draw
    d.rect(s, (36, 40, 70), (2, 6, 28, 50)); d.rect(s, (28, 31, 56), (2, 6, 4, 50)); d.rect(s, (52, 56, 92), (2, 4, 28, 3))
    d.rect(s, (110, 110, 124), (15, 0, 2, 5))
    for r in range(6):
        for c in range(3):
            d.rect(s, (255, 226, 120) if (r * 5 + c * 3 + (r & c)) % 4 else (24, 28, 52), (7 + c * 8, 10 + r * 8, 5, 5))
    return _fin(s)
def _flag():
    s = _surf(26, 42); d = pygame.draw
    d.rect(s, (200, 200, 206), (2, 0, 2, 42)); d.rect(s, (218, 37, 29), (4, 2, 21, 14))
    d.polygon(s, (255, 255, 0), [(14.5 + (4.5 if i % 2 == 0 else 1.8) * math.sin(i * math.pi / 5),
                                  9.5 - (4.5 if i % 2 == 0 else 1.8) * math.cos(i * math.pi / 5)) for i in range(10)])
    return _fin(s)
def _rice():
    s = _surf(28, 24); d = pygame.draw
    for x, h in ((4, 14), (9, 19), (14, 22), (19, 18), (24, 13)):
        d.line(s, (150, 170, 50), (14, 23), (x, 23 - h), 2)
        d.line(s, (236, 196, 64), (x, 23 - h), (x + (x - 14) // 3 + 1, 25 - h), 3)
    return _fin(s)
def _palm():
    s = _surf(32, 48); d = pygame.draw
    d.polygon(s, (122, 88, 52), [(15, 47), (19, 47), (20, 19), (17, 19)])
    for x, y, c in ((1, 24, (30, 120, 52)), (6, 9, (40, 150, 66)), (16, 2, (30, 120, 52)), (27, 9, (40, 150, 66)), (31, 24, (30, 120, 52))):
        d.line(s, c, (18, 18), (x, y), 3)
    d.circle(s, (100, 68, 34), (16, 21), 2); d.circle(s, (100, 68, 34), (21, 21), 2)
    return _fin(s)
def _lantern():
    s = _surf(20, 40); d = pygame.draw
    d.rect(s, (90, 70, 50), (9, 10, 2, 30))
    d.ellipse(s, (218, 37, 29), (3, 3, 14, 16)); d.ellipse(s, (255, 120, 60), (7, 6, 6, 10))
    d.rect(s, (255, 205, 50), (6, 1, 8, 3)); d.rect(s, (255, 205, 50), (6, 18, 8, 3))
    d.line(s, (255, 205, 50), (10, 21), (10, 26), 1)
    return _fin(s)
def _cactus():
    s = _surf(24, 40); d = pygame.draw; g = (46, 140, 64); g2 = (66, 168, 84)
    d.rect(s, g, (9, 4, 6, 36)); d.rect(s, g2, (9, 4, 2, 36))
    d.rect(s, g, (2, 18, 8, 4)); d.rect(s, g, (2, 10, 4, 12)); d.rect(s, g2, (2, 10, 1, 12))
    d.rect(s, g, (14, 22, 8, 4)); d.rect(s, g, (18, 14, 4, 12)); d.rect(s, g2, (18, 14, 1, 12))
    return _fin(s)
def _rock():
    s = _surf(28, 20); d = pygame.draw
    d.polygon(s, (118, 116, 124), [(0, 20), (4, 8), (11, 2), (20, 4), (27, 12), (28, 20)])
    d.polygon(s, (150, 148, 156), [(11, 2), (20, 4), (24, 10), (14, 9)])
    d.polygon(s, (92, 90, 98), [(0, 20), (4, 8), (9, 14), (8, 20)])
    return _fin(s)
def _shack():
    s = _surf(36, 30); d = pygame.draw
    d.rect(s, (120, 92, 70), (3, 10, 30, 20))
    for x in range(6, 33, 6): d.line(s, (96, 72, 54), (x, 10), (x, 29))
    d.polygon(s, (150, 155, 160), [(0, 12), (18, 2), (36, 12)]); d.rect(s, (180, 70, 50), (22, 7, 6, 4))
    d.rect(s, (50, 38, 32), (14, 18, 8, 12)); d.rect(s, (240, 210, 120), (25, 15, 5, 5))
    return _fin(s)
def _barrel():
    s = _surf(14, 18); d = pygame.draw
    d.rect(s, (60, 100, 160), (1, 1, 12, 16)); d.rect(s, (40, 70, 120), (1, 5, 12, 2)); d.rect(s, (40, 70, 120), (1, 11, 12, 2))
    d.ellipse(s, (130, 170, 220), (1, 0, 12, 4))
    return _fin(s)
def _umbrella():
    s = _surf(34, 36); d = pygame.draw
    d.rect(s, (240, 240, 240), (16, 8, 2, 28)); d.rect(s, (40, 160, 220), (8, 32, 18, 4))
    d.polygon(s, (235, 60, 60), [(17, 2), (0, 13), (17, 13)]); d.polygon(s, (250, 250, 250), [(17, 2), (17, 13), (34, 13)])
    return _fin(s)
def _tight(fr):
    w, h = fr[0].get_size(); cx = w // 2; rs = [f.get_bounding_rect() for f in fr]
    hw = max(max(cx - r.left, r.right - cx) for r in rs); t = min(r.top for r in rs); b = max(r.bottom for r in rs)
    out = []
    for f in fr:
        n = _surf(2 * hw, b - t); n.blit(f, (hw - cx, -t)); out.append(_fin(n))
    return out
def _sl(w, h): return pygame.Surface((w, h), pygame.SRCALPHA)
def _L_lighthouse():
    L, d = [], pygame.draw; WH, RD = (240, 240, 244), (214, 48, 40)
    for z in range(53):
        s = _sl(20, 20); L.append(s)
        if z < 36:
            r = 8 - 3 * z // 35; c = RD if (z // 6) & 1 == 0 else WH
            dk = tuple(v * 62 // 100 for v in c); d.circle(s, c, (10, 10), r); d.rect(s, dk, (10 - r, 8, 1, 5)); d.rect(s, dk, (9 + r, 8, 1, 5))
            if z < 6: d.rect(s, (30, 26, 34), (8, 10 + r - 2, 4, 3))
        elif z < 38: d.circle(s, (70, 72, 84), (10, 10), 9); d.circle(s, (120, 122, 134), (10, 10), 8)
        elif z == 38: d.circle(s, (150, 152, 164), (10, 10), 9, 1); d.circle(s, (255, 214, 90), (10, 10), 4)
        elif z < 44:
            d.circle(s, (255, 214, 90), (10, 10), 4); d.rect(s, (255, 246, 175), (8, 12, 4, 2))
        elif z < 52: d.circle(s, (190, 36, 36), (10, 10), max(1, 6 - (z - 44) * 6 // 8))
        else: d.circle(s, WH, (10, 10), 1)
    return L
def _L_school():
    L, R = [], pygame.draw.rect; WL, WIN, DR = (236, 206, 112), (90, 150, 205), (110, 70, 44)
    for z in range(22):
        s = _sl(48, 18); L.append(s)
        if z < 2: R(s, (196, 166, 86), (2, 2, 44, 14))
        elif z < 12:
            R(s, WL, (2, 2, 44, 14))
            if z in (3, 4, 8, 9):
                for x in (6, 12, 18, 30, 36, 42): R(s, WIN, (x, 14, 3, 2))
                for y in (6, 10): R(s, WIN, (2, y, 2, 2)); R(s, WIN, (44, y, 2, 2))
            if z < 7: R(s, DR, (22, 14, 4, 2))
            elif z < 9: R(s, (250, 250, 250), (20, 14, 8, 2))
            elif z == 9: R(s, (210, 40, 36), (20, 14, 8, 2))
        elif z < 18:
            k = (z - 12) * 2; R(s, (176, 62, 42) if z & 1 else (150, 50, 36), (k, k // 2, 48 - 2 * k, 18 - k))
        if z < 21: R(s, (205, 205, 210), (3, 15, 1, 1))
        if 16 <= z < 21: R(s, (218, 37, 29), (4, 15, 5, 1))
        if z in (18, 19): R(s, (255, 240, 0), (6, 15, 1, 1))
    return L
def _L_bitexco():
    L, d = [], pygame.draw; GL, DK = (44, 96, 168), (28, 64, 120)
    for z in range(54):
        s = _sl(30, 16); L.append(s)
        if z < 5: hw, hd, c = 9, 7, (40, 56, 96)
        elif z < 44: t = (z - 5) / 38.0; hw, hd, c = int(6.5 - 3.5 * t * t + 0.5), int(6 - 2 * t * t + 0.5), GL
        elif z < 49: hw, hd, c = max(1, 3 - (z - 44)), max(1, 4 - (z - 44)), GL
        else: hw = hd = 0; c = None
        if c:
            x0, y0 = 16 - hw, 8 - hd; d.rect(s, DK, (x0, y0, 2 * hw, 2 * hd)); d.rect(s, c, (x0 + 1, y0 + 1, 2 * hw - 2, 2 * hd - 2))
            if 5 <= z < 44 and z % 3 == 1:
                for x in range(x0 + 2, x0 + 2 * hw - 1, 2): d.rect(s, (255, 226, 130) if (x * 5 + z) % 2 == 0 else (22, 52, 108), (x, y0 + 2 * hd - 1, 1, 1))
                for y in range(y0 + 2, y0 + 2 * hd - 1, 2): d.rect(s, (255, 226, 130) if (y * 3 + z) % 2 == 0 else (22, 52, 108), (x0, y, 1, 1)); d.rect(s, (255, 226, 130) if (y * 7 + z) % 2 == 0 else (22, 52, 108), (x0 + 2 * hw - 1, y, 1, 1))
        if 24 <= z < 27: d.rect(s, (150, 160, 180), (9, 7, 4, 2)); d.rect(s, (150, 160, 180), (8, 8, 1, 1))
        if z in (27, 28): d.circle(s, (80, 84, 100), (9, 8), 4); d.circle(s, (235, 235, 240) if z == 28 else (110, 114, 130), (9, 8), 2)
        if 49 <= z < 54: d.rect(s, (255, 60, 60) if z == 53 else (150, 150, 160), (15, 8, 1, 1))
    return L
def _p8(s, c, cx, cy, r):
    pygame.draw.polygon(s, c, [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4), cy + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)])
def _sq(s, d, c, cx, hw):
    R = pygame.draw.rect; R(s, d, (cx - hw, cx - hw, 2 * hw, 2 * hw)); R(s, c, (cx - hw + 1, cx - hw + 1, 2 * hw - 2, 2 * hw - 2))
def _L_phuocduyen():
    L, R = [], pygame.draw.rect; WL, WD, RF, RD, GD, DR = (214, 196, 160), (150, 128, 96), (176, 70, 44), (124, 48, 34), (230, 190, 70), (40, 24, 20)
    for z in range(38):
        s = _sl(24, 24); L.append(s)
        if z < 35:
            t, k = divmod(z, 5); r = 10.5 - t * 0.9
            if k < 3:
                w = r - 1.5; _p8(s, WD, 12, 12, w); _p8(s, WL, 12, 12, w - 1)
                if t == 0 and k < 2: R(s, DR, (10, 12 + int(w) - 2, 4, 3))
                elif k == 1: R(s, DR, (11, 12 + int(w) - 2, 2, 2))
            else: _p8(s, RD, 12, 12, r); _p8(s, RF, 12, 12, r - 1)
        else: pygame.draw.circle(s, GD, (12, 12), (2, 1, 1)[z - 35])
    return L
def _L_cham():
    L, R = [], pygame.draw.rect; B, DK, LT, DR, GD = (178, 88, 54), (122, 54, 38), (208, 122, 80), (38, 20, 16), (230, 190, 70)
    for z in range(40):
        s = _sl(22, 22); L.append(s)
        if z < 10: hw = 8
        elif z < 34:
            t, k = divmod(z - 10, 8); hw = (7, 5, 4)[t] + (k == 7)
        else: hw = 3 - (z - 34) // 2
        _sq(s, DK, B, 11, hw); R(s, LT, (12 - hw, 12 - hw, 1, 2 * hw - 2))
        if z < 8: R(s, DR, (9, 11 + hw - 3, 4, 3))
        elif 10 <= z < 34 and (z - 10) % 8 in (2, 3, 4): R(s, DR, (10, 11 + hw - 2, 2, 2))
        if z == 39: R(s, GD, (10, 10, 2, 2))
    return L
def _L_motcot():
    L, R = [], pygame.draw.rect; WT, ST, SD, RD, RF, RL, GD = (70, 140, 175), (160, 160, 166), (112, 112, 120), (170, 50, 40), (150, 64, 46), (190, 96, 66), (230, 190, 70)
    SW, STT, SR = (150, 100, 62), (196, 148, 96), (104, 60, 42); cy = 22
    def sq(s, d, c, hw): R(s, d, (13 - hw, cy - hw, 2 * hw, 2 * hw)); R(s, c, (14 - hw, cy - hw + 1, 2 * hw - 2, 2 * hw - 2))
    for z in range(36):
        s = _sl(26, 44); L.append(s)
        if z == 0: R(s, ST, (1, cy - 12, 24, 24)); R(s, WT, (3, cy - 10, 20, 20)); R(s, ST, (9, 34, 8, 10))
        elif z == 1:
            R(s, WT, (3, cy - 10, 20, 20))
            for x, y in ((5, 15), (19, 17), (7, 28), (20, 29), (15, 13)): R(s, (60, 160, 80), (x, y, 3, 2)); R(s, (250, 150, 190), (x + 1, y, 1, 1))
        elif z < 18: pygame.draw.circle(s, SD, (13, cy), 3); pygame.draw.circle(s, (74, 112, 74) if z % 5 == 0 else ST, (12, cy - 1), 2)
        elif z < 20: sq(s, (80, 44, 30), (130, 78, 52), 8)
        elif z < 26:
            if z < 22: R(s, (50, 30, 24), (8, cy - 5, 10, 10))
            for x, y in ((6, cy - 7), (18, cy - 7), (6, cy + 5), (18, cy + 5)): R(s, RD, (x, y, 2, 2))
        elif z < 29:
            sq(s, RD, RF, 11 - (z - 26))
            if z == 26:
                for x, y in ((2, cy - 11), (22, cy - 11), (2, cy + 9), (22, cy + 9)): R(s, RL, (x, y, 2, 2))
        elif z < 31: sq(s, (100, 36, 30), RD, 5)
        elif z < 33: sq(s, RD, RF, 8 - (z - 31))
        elif z < 35: sq(s, RD, RF, 4 - (z - 33))
        else: R(s, GD, (12, cy - 1, 2, 2))
        if z < 20:
            ye = 43 - (z >> 1) * 13 // 10
            R(s, SR, (9, 30, 8, ye - 29)); R(s, SW, (10, 30, 6, ye - 29)); R(s, STT, (10, ye, 6, 1))
    return L
def _L_wreck():
    L, d = [], pygame.draw
    def pt(cx, cy, a, ox, oy):
        r = math.radians(a); return (cx + ox * math.cos(r) - oy * math.sin(r), cy + ox * math.sin(r) + oy * math.cos(r))
    def box(s, c, cx, cy, a, hl, hw, ox=0.0):
        d.polygon(s, c, [pt(cx, cy, a, ox + x, y) for x, y in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))])
    CARS = ((14, 15, 8, 0, (156, 58, 48), 0, 1), (42, 12, -14, 0, (178, 152, 66), 0, 0), (70, 16, 20, 0, (74, 98, 140), 1, 0),
            (28, 14, -5, 5, (170, 172, 178), 0, 1), (57, 13, 12, 5, (70, 118, 92), 0, 0))
    for z in range(13):
        s = _sl(84, 30); L.append(s)
        if z < 2:
            for x, y in ((5, 26), (78, 6), (36, 27)): d.circle(s, (22, 22, 26), (x, y), 3); d.circle(s, (60, 60, 66), (x, y), 1)
            box(s, (110, 76, 56), 62, 26, -8, 5, 1.5)
        for cx, cy, a, z0, col, flip, sp in CARS:
            u = z - z0
            if not 0 <= u < 7: continue
            dk, lt = tuple(v * 6 // 10 for v in col), tuple(min(255, v + 40) for v in col)
            if flip:
                if u < 3: box(s, dk if u == 0 else col, cx, cy, a, 12, 6)
                elif u < 5: box(s, (40, 40, 46), cx, cy, a, 11, 5)
                else:
                    for ox, oy in ((-8, -6), (8, -6), (-8, 6), (8, 6)): d.circle(s, (22, 22, 26), pt(cx, cy, a, ox, oy), 2)
                continue
            if u < 2:
                box(s, (28, 28, 34), cx, cy, a, 11, 5)
                for ox in (-8, 8): box(s, (22, 22, 26), cx, cy, a, 2.5, 7, ox)
            elif u < 5:
                box(s, dk if u == 2 else col, cx, cy, a, 13, 6.5)
                if u == 3: box(s, (200, 190, 150), cx, cy, a, 1, 5, 12.5)
                if sp and u == 4: box(s, (30, 30, 36), cx, cy, a, 1.5, 7, -12)
            elif u == 5: box(s, (46, 72, 112), cx, cy, a, 6, 5, -2); box(s, col, cx, cy, a, 3, 6, 10)
            else: box(s, lt, cx, cy, a, 5, 4.5, -2)
    return L
def _L_station():
    L, d = [], pygame.draw; R = d.rect; SN, SD, WD, ST, WN, RD = (244, 247, 252), (196, 208, 230), (126, 92, 62), (112, 116, 124), (255, 214, 120), (218, 37, 29)
    for z in range(20):
        s = _sl(84, 30); L.append(s)
        if z < 2:
            for e in ((0, 21, 26, 8), (52, 22, 30, 7), (30, 3, 24, 6)): d.ellipse(s, SN if z else SD, e)
            R(s, ST, (8, 8, 68, 16))
        elif z < 9:
            R(s, ST if z < 4 else WD, (9, 9, 66, 14))
            if z in (4, 5):
                for x in range(14, 70, 10):
                    if not 36 < x < 48: R(s, WN, (x, 21, 4, 2))
            if z < 7: R(s, (40, 28, 24), (38 if z < 6 else 39, 20, 8 if z < 6 else 6, 3))
        elif z < 15:
            k = z - 9; R(s, SD if k < 1 else SN, (4, 6 + 5 * k // 3, 76, max(2, 20 - 10 * k // 3)))
        for px in (4, 77):
            R(s, ST, (px, 14, 3, 3))
            if z >= 17: R(s, ST, (px - 3, 13, 9, 5))
        if 15 <= z < 18: R(s, (210, 50, 45), (36, 13, 8, 5)); R(s, (200, 230, 255), (38, 14, 4, 2)) if z == 16 else None
        if z == 18: R(s, (40, 40, 48), (10, 15, 64, 1))
        if 15 <= z < 18: R(s, (205, 205, 210), (62, 15, 1, 1))
        if z in (16, 17): R(s, RD, (63, 14, 5, 2)); R(s, (255, 240, 0), (65, 14, 1, 1)) if z == 17 else None
    return L
def _L_dinh():
    L, d = [], pygame.draw; R = d.rect; PIL, TL, TD, TT, GD = (170, 40, 34), (146, 86, 60), (112, 60, 44), (172, 106, 72), (230, 190, 70)
    CAN = (7, 8, 9, 10, 11, 11, 10, 10, 9, 8, 7, 5)
    for z in range(20):
        s = _sl(84, 30); L.append(s)
        if z < 2: R(s, (176, 120, 92), (2, 6, 60, 22)); R(s, (150, 140, 128), (5, 8, 54, 18))
        elif z < 8:
            if z == 2: R(s, (140, 100, 70), (7, 9, 52, 14))
            R(s, (120, 70, 44), (8, 9, 50, 2))
            for x in range(9, 56, 10): R(s, PIL, (x, 20, 3, 3)); R(s, PIL, (x, 10, 3, 3))
            if z in (5, 6):
                for x in (14, 44): d.circle(s, (230, 60, 40), (x, 22), 2)
        if 8 <= z < 16:
            k = z - 8; fl = max(0, k - 3); R(s, TD if k < 1 else (TT if k > 5 else TL), (4 - fl, 6 + 4 * k // 3, 56 + 2 * fl, max(2, 20 - 8 * k // 3)))
            if z == 15: R(s, GD, (0, 15, 3, 2)); R(s, GD, (61, 15, 3, 2))
        if z < 10:
            d.circle(s, (92, 64, 38), (72, 16), 3)
            if z >= 5:
                for x, y in ((66, 18), (77, 19), (70, 21)): d.line(s, (80, 56, 34), (x, y), (x, y + 3))
        if z >= 8:
            r = CAN[z - 8]; d.circle(s, (30, 112, 48), (72, 16), r)
            d.circle(s, (44, 138, 60), (67, 18), r * 7 // 10); d.circle(s, (56, 156, 72), (76, 13), r * 6 // 10)
    return L
def _L_hands():
    L, d = [], pygame.draw; SB, SDK, MS = (112, 116, 112), (76, 80, 76), (60, 96, 66)
    for z in range(52):
        s = _sl(40, 26); L.append(s)
        if z < 22:
            d.rect(s, SDK, (14, 8, 12, 12))
            if z % 6 < 3: d.rect(s, MS, (14, 8, 4, 12))
        elif z < 34:
            d.ellipse(s, SDK, (5, 3, 30, 20)); d.ellipse(s, SB, (6, 4, 28, 17))
            if (z // 3) & 1: d.ellipse(s, MS, (10, 7, 20, 10))
        else:
            r = 3 if z < 46 else 2
            for x, y in ((9, 6), (16, 5), (24, 5), (31, 6)): d.circle(s, SDK, (x, y), r); d.circle(s, MS if (x + z) % 7 < 2 else SB, (x - 1, y - 1), r - 1)
            if z < 44: d.circle(s, SB, (5, 14), 3); d.circle(s, MS, (4, 13), 1)
    return L
BUILD = (("lighthouse", _L_lighthouse), ("school", _L_school), ("bitexco", _L_bitexco),
         ("hands", _L_hands), ("phuocduyen", _L_phuocduyen), ("cham", _L_cham), ("motcot", _L_motcot),("wreck", _L_wreck),("station", _L_station), ("dinh", _L_dinh))
YAW = {"lighthouse": -35, "school": 25, "bitexco": 35, "phuocduyen": -35, "cham": 35, "motcot": -35, "hands": 0, "wreck": -20,"wreck": -20, "station": -20, "dinh": 20}
def _layer(P, mh, col, ks, seed):
    r = random.Random(seed); ph = [r.random() * 6.283 for _ in ks]
    s = _surf(P, mh); pts = [(0, mh)]
    for x in range(0, P + 1, 4):
        v = sum(math.sin(6.283 * k * x / P + p) / (j + 1) for j, (k, p) in enumerate(zip(ks, ph)))
        pts.append((x, mh - max(3, min(mh, mh * (0.55 + 0.45 * v / 1.8)))))
    pts.append((P, mh)); pygame.draw.polygon(s, col, pts)
    return _fin(s)
def _sky(th):
    s = pygame.Surface((W, HZ)).convert(); a_, b_ = th["top"], th["fog"]
    M = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
    row = pygame.Surface((W, 1))
    for y in range(HZ):
        f = y / (HZ - 1.0); m = M[y & 3]
        for x in range(4):
            t = (m[x] + 0.5) / 16.0
            row.set_at((x, 0), tuple(min(255, int(a + (b - a) * f + t)) for a, b in zip(a_, b_)))
        w = 4
        while w < W: row.blit(row.copy(), (w, 0)); w *= 2
        s.blit(row, (0, y))
    if th.get("stars"):
        r = random.Random(7)
        for _ in range(45): s.set_at((r.randrange(W), r.randrange(HZ - 24)), (225, 228, 255))
    hz = tuple((a + b) // 2 for a, b in zip(th["sun"], th["fog"])); pygame.draw.circle(s, hz, th["sunpos"], 24)
    pygame.draw.circle(s, th["sun"], th["sunpos"], 14)
    return s
def _clouds(col=(250, 252, 255)):
    s = _surf(640, 30); r = random.Random(5)
    for _ in range(9):
        x, y = r.randrange(20, 580), r.randrange(2, 14)
        for dx, dy, w in ((0, 0, 44), (-14, 6, 30), (16, 6, 34)):
            pygame.draw.ellipse(s, col, (x + dx, y + dy, w, 12))
    return _fin(s)
def _mm_surface(pts, w, h, lw):
    s = pygame.Surface((w, h), pygame.SRCALPHA); s.fill((0, 0, 0, 120))
    pygame.draw.lines(s, (235, 235, 245), True, pts[:-1], lw)
    pygame.draw.rect(s, (255, 220, 70), (pts[0][0] - 2, pts[0][1] - 2, 4, 4))
    return s
def _mm_key(pts, w, h, lw):
    s = pygame.Surface((w, h)); s.fill(KEY)
    pygame.draw.lines(s, (235, 235, 245), True, pts[:-1], lw)
    pygame.draw.rect(s, (255, 220, 70), (pts[0][0] - 2, pts[0][1] - 2, 4, 4))
    s = s.convert(); s.set_colorkey(KEY); return s
def init_assets():
    global FONT, BIG, MED, CARV , VIGNETTE_SURF
    FONT, BIG, MED = _font(12), _font(16), _font(14)
    BASES["pine"], BASES["tree"] = _pine(), _tree()
    BASES["cactus"], BASES["rock"], BASES["spine"] = _cactus(), _rock(), _spine()
    BASES["lamp"], BASES["tower"], BASES["maple"] = _lamp(), _tower(), _tree((196, 80, 28), (226, 128, 38), (238, 172, 60))
    BASES["palm"], BASES["rice"], BASES["flag"], BASES["lantern"] = _palm(), _rice(), _flag(), _lantern()
    for nm_, Lf in BUILD:
        L_, y_ = Lf(), YAW[nm_]
        for sf_, f_ in zip(("", "_l", "_r"), _tight(_stack(L_, 2, (y_, y_ - 22, y_ + 22), shade=0.4))): BASES[nm_ + sf_] = _outline(f_)
    BASES["shack"], BASES["barrel"], BASES["umbrella"] = _shack(), _barrel(), _umbrella()
    VIGNETTE_SURF = create_speed_vignette(W, H)
    for k, c in enumerate(CAR_COLS):
        for n, s in zip("slr", _stack(_layers(c, k & 1), 3, (0, -10, 10))): BASES["c%d%s" % (k, n)] = s
    CARV = CARW * BASES["c0s"].get_width() / (CW_ * 3) * 0.94 * 2 / 3
    for i, d in enumerate(PCAR_DEF):
        L = _layers(d[1], PKIND[i])
        for n, s in zip("slr", _stack(L, 3, (0, -10, 10))): BASES["p%d%s" % (i, n)] = s
        PCARS.append(_stack(L, 2, (-24, -16, -8, 0, 8, 16, 24)))
        PREVS.append(_stack(L, 2, [i * 15 for i in range(24)]))
    for i, t in enumerate(TRACKS):
        th = THEMES[t["theme"]]
        t["sky"] = _sky(th); t["cld"] = _clouds(th.get("cld", (250, 252, 255))); t["mt1"] = _layer(640, 46, th["mt1"], (1, 3, 5), 3 + i); t["mt2"] = _layer(640, 24, th["mt2"], (2, 5, 9), 11 + i)
        t["mlp"] = t["mml"]
        t["mlk"] = _mm_key(t["mlp"], MMW * 2, MMH * 2, 3)
        t["mms"] = _mm_surface(t["mmp"], MMW, MMH, 2); t["mml"] = _mm_surface(t["mml"], MMW * 2, MMH * 2, 3)
        g = 0.4 if th.get("stars") else 0.8
        t["fl"] = (_glow(44, tuple(int(c * g) for c in th["sun"])), _glow(7, (60, 50, 30)), _glow(12, (30, 50, 70)))
        sn = t["theme"] == 2
        t["wx"] = ((_wx(sn, 1, 60, (240, 245, 255) if sn else (110, 130, 170), 2), _wx(sn, 2, 35, (240, 245, 255) if sn else (150, 170, 210), 3))
                   if t["theme"] in (2, 3) else None)
_FR = {}
def front(k, a):
    s = _FR.get((k, a))
    if s is None: s = _FR[(k, a)] = _stack(_layers(CAR_COLS[k], k & 1), 2, (a,))[0]
    return s
def scaled(name, w, q=0, fog=None, sd=0):
    k = (name, w, q, fog, sd); s = _sc.get(k)
    if s is None:
        g = name[0] == "g"; b = BASES["p" + name[1:]] if g else BASES[name]
        s = pygame.transform.scale(b, (w, max(1, w * b.get_height() // b.get_width())))
        s.set_colorkey(KEY)
        if sd and w >= 12:
            h = s.get_height(); half = w // 2; m = pygame.mask.from_surface(s)
            t = s.copy(); t.set_colorkey(None)
            dx, lx = (w - half, 0) if sd > 0 else (0, w - half)
            t.fill((175, 175, 175), (dx, 0, half, h), pygame.BLEND_RGB_MULT)
            t.fill((30, 30, 30), (lx, 0, half, h), pygame.BLEND_RGB_ADD)
            n = _surf(*s.get_size()); m.to_surface(n, setsurface=t, unsetcolor=None); s = _fin(n)
        if q and fog:
            f = q / 6.0; t = s.copy(); t.set_colorkey(None)
            t.fill((int(255 * (1 - f)),) * 3, special_flags=pygame.BLEND_RGB_MULT)
            t.fill(tuple(int(c * f) for c in fog), special_flags=pygame.BLEND_RGB_ADD)
            n = _surf(*s.get_size()); pygame.mask.from_surface(s).to_surface(n, setsurface=t, unsetcolor=None); s = _fin(n)
        if g: s.set_alpha(100)
        if len(_sc) > 1200: _sc.clear()
        _sc[k] = s
    return s
def shadow(w, a):
    w = w & -4
    k = (w, a); s = _sh.get(k)
    if s is None:
        h = w // 10 + 1; s = _surf(w, h)
        pygame.draw.ellipse(s, (60, 60, 68), (0, 0, w, h))
        pygame.draw.ellipse(s, (8, 8, 12), (w // 8, h // 5, w - w // 4, h - h // 5 * 2))
        s = _fin(s); s.set_alpha(a); _sh[k] = s
    return s
def txt(s, col=(255, 255, 255), big=0):
    s = T(s); k = (s, col, big); t = _tc.get(k)
    if t is None:
        if len(_tc) > 500: _tc.clear()
        f = (FONT, BIG, MED)[big]
        a, b = f.render(s, True, col), f.render(s, True, (0, 0, 0))
        t = pygame.Surface((a.get_width() + 2, a.get_height() + 2), pygame.SRCALPHA)
        t.blit(b, (2, 2)); t.blit(b, (1, 1)); t.blit(a, (0, 0)); _tc[k] = t
    return t
def _shadow_bake(L, S, yaw, sq=0.22, kx=0.4, kd=0.3):
    rs = []
    for l in L:
        r = pygame.transform.rotate(pygame.transform.scale(l, (l.get_width() * S, l.get_height() * S)), -yaw); w, h = r.get_size()
        rs.append(pygame.transform.scale(r, (w, max(1, int(h * sq)))))
    mw, mh = rs[0].get_size(); n = len(rs)
    s = _surf(mw + int(n * S * kx) + 1, mh + int(n * S * kd) + 1)
    for z, r in enumerate(rs):
        t = pygame.mask.from_surface(r).to_surface(setcolor=(20, 18, 22), unsetcolor=KEY)
        s.blit(t, (int(z * S * kx), int(z * S * kd)))
    return _fin(s), mw // 2, mh // 2
def shadow_cast(name, w, flip, a=110):
    k = ("sc", name, w, flip, a); r = _sh.get(k)
    if r is None:
        b, ax, ay = BASES[name + "_sh"]; f = w / BASES[name].get_width()
        s = pygame.transform.scale(b, (max(1, int(b.get_width() * f)), max(1, int(b.get_height() * f)))); ax = int(ax * f); ay = int(ay * f)
        if flip: s = pygame.transform.flip(s, True, False); ax = s.get_width() - ax
        s.set_colorkey(KEY); s.set_alpha(a); r = _sh[k] = (s, ax, ay)
    return r
def shadow_real(img, w, a=120):
    w = w & -4; k = ("sh_real", id(img), w, a); s = _sh.get(k)
    if s is None:
        sh = max(1, int(w * img.get_height() / img.get_width() * 0.28))
        t = pygame.transform.scale(img, (w, sh)); t.set_colorkey(KEY)
        s = _fin(pygame.mask.from_surface(t).to_surface(setcolor=(20, 18, 24), unsetcolor=KEY)); s.set_alpha(a); _sh[k] = s
    return s
def shadow_real_a(img, w, a=120, key=None):
    w = w & -4; q = 0.5; key = id(img) if key is None else key
    k = ("sh_real_sync", key, w, a, q); res = _sh.get(k)
    if res is None:
        sh = max(4, int(w * 0.25))
        t = pygame.transform.flip(pygame.transform.scale(img, (w, sh)), False, True); t.set_colorkey(KEY)
        flat = pygame.mask.from_surface(t).to_surface(setcolor=(20, 18, 24), unsetcolor=KEY)
        surf = _surf(w + math.ceil(q * sh), sh)
        for y in range(sh): surf.blit(flat, (math.floor(y * q), y), (0, y, w, 1))
        surf = _fin(surf); surf.set_alpha(a); res = _sh[k] = (surf, w // 2, 0)
    return res
def create_speed_vignette(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(4):
        alpha = 30 + i * 25
        pygame.draw.rect(s, (0, 0, 0, alpha), (i*2, i*2, w - i*4, h - i*4), 2, border_radius=12)
    return s.convert_alpha()
def shadow_3d(img, w, a=120, skew=0.0, key=None):
    w = w & -4
    if key is None: key = id(img)
    q = -round(skew * 4) / 4.0
    k = ("sh3", key, w, a, q); s = _sh.get(k)
    if s is None:
        if len(_sh) > 500: _sh.clear()
        sh = max(1, int(w * img.get_height() / img.get_width() * 0.25))
        t = pygame.transform.flip(pygame.transform.scale(img, (w, sh)), False, True)
        t.set_colorkey(KEY)
        flat = pygame.mask.from_surface(t).to_surface(setcolor=(20, 18, 22), unsetcolor=KEY)
        sft = int(abs(q) * sh)
        s = _surf(w + sft, sh)
        offset = sft if q < 0 else 0
        for y in range(sh):
            s.blit(flat, (offset + math.floor(y * q), y), (0, y, w, 1))
        s = _fin(s); s.set_alpha(a); _sh[k] = s
    return s
def layer_sheet(L, pg, fnt):
    lw, lh = L[0].get_size(); n = len(L); aw, ah = W - 8, H - 44
    for s in (4, 3, 2, 1):
        cw, ch = lw * s + 4, lh * s + 4; cols, rows = max(1, aw // cw), max(1, ah // ch)
        if cols * rows >= min(n, 8): break
    cap = cols * rows; np_ = -(-n // cap); pg %= np_; sf = pygame.Surface((W, H), pygame.SRCALPHA)
    for k, z in enumerate(range(pg * cap, min(n, pg * cap + cap))):
        x, y = 4 + (k % cols) * cw, 22 + (k // cols) * ch
        pygame.draw.rect(sf, (44, 46, 62), (x, y, cw - 2, ch - 2)); pygame.draw.rect(sf, (90, 80, 160), (x, y, cw - 2, ch - 2), 1)
        sf.blit(pygame.transform.scale(L[z], (lw * s, lh * s)), (x + 1, y + 1))
        sf.blit(fnt.render(str(z), True, (255, 230, 90)), (x + 2, y + 1))
    return sf, np_, pg
if __name__ == "__main__":
    import sys
    if HERE not in sys.path: sys.path.insert(0, HERE)
    from touchpad import TouchPad
    pygame.init()
    touch = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
    BTN_VIEWER = (("A", "Xem lớp", 268, 50),)
    pad = TouchPad(W, H, buttons=BTN_VIEWER, scale=2 if touch else 3, touch=touch)
    pygame.display.set_caption("3D Sprite Viewer")
    init_assets()
    b360, blay = {}, {}
    for nm_, Lf in BUILD:
        blay[nm_] = Lf()
        b360[nm_] = [_outline(f) for f in _tight(_stack(blay[nm_], 2, [i * 15 for i in range(24)], shade=0.4))]
    items = []
    for i, car_name in enumerate(PCAR_DEF):
        items.append({"name": f"Xe: {car_name[0]}", "frames": PREVS[i], "type": "3d", "layers": _layers(car_name[1], PKIND[i])})
    for nm_ in b360:
        items.append({"name": f"Công trình: {nm_.upper()}", "frames": b360[nm_], "type": "3d", "layers": blay[nm_]})
    static_names = ["pine", "tree", "cactus", "rock", "spine", "lamp", "tower", "maple", "palm", "rice", "flag", "lantern", "shack", "barrel", "umbrella"]
    for nm in static_names:
        if nm in BASES: items.append({"name": f"Vật thể: {nm}", "frames": [BASES[nm]], "type": "static"})
    clock = pygame.time.Clock()
    run = True
    idx = 0
    tt = 0.0
    shadow_mode = 2
    sheet, pg, cache, sfont = False, 0, {}, pygame.font.SysFont("arial", 9)
    while run:
        dt = clock.tick(60) / 1000.0
        tt += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                run = False
            pad.event(e)
        pad.update()
        if "left" in pad.pressed: idx = (idx - 1) % len(items); pg = 0
        if "right" in pad.pressed: idx = (idx + 1) % len(items); pg = 0
        if "B" in pad.pressed: shadow_mode = (shadow_mode + 1) % 3
        if "A" in pad.pressed and items[idx].get("layers"): sheet = not sheet; pg = 0
        pg += ("down" in pad.pressed) - ("up" in pad.pressed)
        pad.screen.fill((30, 32, 45))
        item = items[idx]
        if sheet and item.get("layers"):
            if (idx, pg) not in cache: cache[(idx, pg)] = layer_sheet(item["layers"], pg, sfont)
            sf, npg, pg = cache[(idx, pg)]; pad.screen.blit(sf, (0, 0))
            f14 = pygame.font.SysFont("arial", 12, bold=True)
            pad.screen.blit(f14.render(f"{item['name']}  ·  {len(item['layers'])} lớp  ·  trang {pg + 1}/{npg}", True, (255, 230, 90)), (10, 4))
            pad.screen.blit(pygame.font.SysFont("arial", 12).render("^ v: Đổi trang  |  < >: Đổi vật thể  |  A: Thoát xem lớp", True, (180, 180, 200)), (10, H - 20))
            pad.present(); continue
        frames = item["frames"]
        if item["type"] == "3d":
            img = frames[0]; f_idx = 0
            speed = 6
            f_idx = int(tt * speed) % len(frames)
            img = frames[f_idx]
        else:
            img = frames[0]
        w, h = img.get_size()
        scale = 1
        big_w, big_h = w * scale, h * scale
        img_big = pygame.transform.scale(img, (big_w, big_h))
        cx, cy = W // 2, H // 2 + 50
        if shadow_mode == 0:
            sh = shadow(big_w, 150)
            pad.screen.blit(sh, (cx - sh.get_width() // 2, cy - sh.get_height() // 2))
        elif shadow_mode == 1:
            sh, ax, ay = shadow_real_a(img_big, big_w, 150, (idx, f_idx))
            pad.screen.blit(sh, (cx - ax, cy - ay))
        elif shadow_mode == 2:
            sh = shadow_3d(img_big, big_w, 150, 1.2, (idx, f_idx))
            q = -round(1.2 * 4) / 4.0
            sft = int(abs(q) * sh.get_height())
            offset = sft if q < 0 else 0
            pad.screen.blit(sh, (cx - big_w // 2 - offset, cy-2))
        pad.screen.blit(img_big, (cx - big_w // 2, cy - big_h))
        font = pygame.font.SysFont("arial", 14, bold=True)
        txt_name = font.render(f"[{idx+1}/{len(items)}] {item['name']}", True, (255, 230, 90))
        pad.screen.blit(txt_name, (10, 10))
        txt_help = pygame.font.SysFont("arial", 12).render("< >: Đổi vật thể  |  B: Đổi kiểu bóng  |  Giữ A: Xoay nhanh", True, (180, 180, 200))
        pad.screen.blit(txt_help, (10, H - 20))
        pad.present()
    pygame.quit()