import os, sys, gc, json, math, random, time, asyncio
WEB = sys.platform == "emscripten"
try: HERE = os.path.dirname(os.path.abspath(__file__))
except NameError: HERE = os.getcwd()
if HERE not in sys.path: sys.path.insert(0, HERE)
import pygame
from touchpad import TouchPad
try:
    if WEB: raise ImportError
    from recorder import Recorder
except Exception:
    class Recorder:
        def __init__(s, *a, **k): pass
        def event(s, e): pass
        def undraw(s): pass
        def tick(s): pass
        def draw(s): pass
try:
    if WEB: raise ImportError
    import netplay
except Exception: netplay = None
from data import *
import sprites as S
from sprites import *
from sprites import _font, _sysfont, _sc, _surf, _fin, txt, _glow
from sfx import init_sfx, sfx, sfx_stop, MIX, set_vol, play_bgm, stop_bgm, engine
from ui import *
from ui import _pn, _rc
from lang import T, set_lang
MM_CACHE = {}
CURVE = Y = BAND = SPR = MMP = TRK = None
PADS, RAMPS, CUTS, TUN, BRG = set(), {}, {}, set(), set()
MARKS = {}
SUNX = 0.0
N, TL, LAPS = 1, SEG, 3
FOG, PAL = THEMES[0]["fog"], THEMES[0]["pal"]
SKY = MT1 = MT2 = MMS = CLD = None
def load_track(i):
    global CURVE, Y, N, TL, BAND, SPR, MMP, LAPS, FOG, PAL, TRK, SKY, MT1, MT2, MMS, CLD, PADS, RAMPS, CUTS, TUN,SUNX, BRG
    t = TRK = TRACKS[i]; MM_CACHE.clear()
    CURVE, Y, N, TL, BAND, SPR, MMP, LAPS = t["curve"], t["y"], t["n"], t["tl"], t["band"], t["spr"], t["mmp"], t["laps"]
    th = THEMES[t["theme"]]; FOG, PAL = th["fog"], th["pal"]
    SUNX = max(-1.0, min(1.0, (HW - th["sunpos"][0]) / HW))
    TUN = t["tun"]
    BRG = t.get("brg", set())
    PADS, RAMPS, CUTS = t["pads"], t["ramps"], t["cuts"];
    if "sky" in t: SKY, MT1, MT2, MMS, CLD = t["sky"], t["mt1"], t["mt2"], t["mms"], t["cld"]
def set_laps(n):
    global LAPS
    LAPS = n
def _mix(c, f):
    return (int(c[0] + (FOG[0] - c[0]) * f), int(c[1] + (FOG[1] - c[1]) * f), int(c[2] + (FOG[2] - c[2]) * f))
def build_cols(dr):
    return [[tuple(None if c is None else _mix(c, min(0.92, (n / dr) ** 2)) for c in p)
             for n in range(dr + 1)] for p in PAL]
class Car:
    __slots__ = ("z", "x", "spd", "base", "dist", "key", "col", "rb", "bs", "nt", "dt", "cd", "tx", "sk", "jh", "jv")
    def __init__(s, z, x, base, ci):
        s.z, s.x, s.spd, s.base, s.dist, s.key = z, x, 0.0, base, z - PLAYZ, "c%d" % ci
        s.col = CAR_COLS[ci % len(CAR_COLS)]
        s.rb = 1.0; s.bs = s.sk = 0; s.nt = s.dt = s.cd = s.jh = s.jv = 0.0; s.tx = None
def new_cars(rnd):
    out = []
    for k in range(NCARS):
        row, col = divmod(k, 2)
        out.append(Car(PLAYZ + 520 + row * 560 + col * 170, (-0.45, 0.45)[col],
                       MAXSPD * rnd.uniform(0.74, 0.94), k % len(CAR_COLS)))
        out[-1].sk = rnd.randint(0, 3)
    return out
def update_cars(cars, allc, pl, D, dt, run):
    for a in cars:
        if not run: a.spd = 0.0; continue
        j = int(a.z // SEG) % N; cu = abs(CURVE[j])
        drf = a.sk and cu > 1.5 and a.spd > MAXSPD * 0.55
        tgt = a.base * DIF[0] * (1.0 - (0.006 if drf else (0.008 if a.bs else 0.012)) * cu)
        if drf: a.dt += dt; MARKS[(j - 1) % N] = (a.x, 0)
        elif a.dt > 0.0:
            if a.dt > 0.8: a.nt = 1.2
            a.dt = 0.0
        if a.nt > 0.0: a.nt -= dt; tgt *= 1.18
        elif a.sk and random.random() < dt * (0.5 if a.bs and D - a.dist > 3000.0 else 0.07): a.nt = 1.5
        a.cd -= dt
        if a.cd <= 0.0:
            a.cd = 0.25; a.tx = None
            if a.sk:
                for q in range(j + 2, j + 42):
                    q %= N
                    if q in PADS and (a.sk > 2 or (q + a.sk) % 3 == 0): a.tx = 0.0; break
                    if q in RAMPS and (a.sk > 2 or (q + a.sk) % 3 == 0): a.tx = RAMPS[q] * 0.6667; break
        r = (D - a.dist) / 60000.0
        tgt *= 1.0 + a.rb * max(-0.04, min(0.30, r * 2.0))
        dz_pl = (a.z - pl.z) % TL
        if a.bs and 0 < dz_pl < 1500.0 and pl.spd > a.spd:
            a.x += min(dt * 0.6, max(-dt * 0.6, pl.x - a.x))
        else:
            for b in allc:
                if b is a: continue
                dz = (b.z - a.z) % TL
                if 0 < dz < 1800.0 and abs(b.x - a.x) < 0.42:
                    if b is not pl and dz < 900.0 and b.spd < tgt: tgt = max(b.spd * 0.97, tgt * 0.94) if a.bs else b.spd * 0.97
                    d = 1.0 if a.x >= b.x else -1.0
                    if a.x > 0.6: d = -1.0
                    elif a.x < -0.6: d = 1.0
                    a.x += d * dt * 0.8
        if a.tx is not None: a.x += max(-dt * 0.7, min(dt * 0.7, a.tx - a.x))
        if a.x > 0.82: a.x = 0.82
        elif a.x < -0.82: a.x = -0.82
        a.spd += (tgt - a.spd) * min(1.0, dt * 1.5)
        mv = a.spd * dt; a.z += mv; a.dist += mv
        if a.z >= TL: a.z -= TL
        j = int(a.z // SEG) % N
        if a.jh <= 0.0 and a.jv <= 0.0 and a.spd > MAXSPD * 0.5 and j in RAMPS and abs(a.x - RAMPS[j] * 0.6667) < 0.33: a.jv = 120.0 + 180.0 * a.spd / MAXSPD
        if a.nt <= 0.0 and ((j in PADS and abs(a.x) < 0.45) or (j in RAMPS and abs(a.x - RAMPS[j] * 0.6667) < 0.33)):
            a.nt = 1.0; a.spd = min(a.spd + MAXSPD * 0.1, MAXSPD * 1.3)
        if a.jh > 0.0 or a.jv > 0.0:
            a.jv -= 600.0 * dt; a.jh += a.jv * dt
            if a.jh <= 0.0: a.jh = a.jv = 0.0
_FX = {}
_SP_CACHE = {}
def soft_particle(r, c):
    k = (r, c)
    if k not in _SP_CACHE:
        if len(_SP_CACHE) > 160: _SP_CACHE.clear()
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            pygame.draw.circle(s, (c[0], c[1], c[2], int(160 * (i / r) ** 1.5)), (r, r), i)
        _SP_CACHE[k] = s
    return _SP_CACHE[k]
def haze():
    s = _FX.get(("h", FOG))
    if s is None:
        s = _FX[("h", FOG)] = pygame.Surface((W, 24), pygame.SRCALPHA)
        for y in range(24): s.fill((FOG[0], FOG[1], FOG[2], int(210 * (y / 23.0) ** 1.5)), (0, y, W, 1))
    return s
def beam():
    s = _FX.get("b")
    if s is None:
        s = _FX["b"] = pygame.Surface((130, 74)).convert()
        s.fill((0, 0, 0))
        cx = 65
        for y in range(74):
            f = y / 73.0
            intensity = int(120 * (f ** 1.3))
            if y > 61:
                intensity = int(intensity * (73 - y) / 12.0)
            if intensity <= 0: continue
            offset = 4 + int(12 * f)
            w = int(6 + 32 * f)
            for layer in range(5):
                lw = w - layer * (w // 5)
                if lw <= 0: continue
                alpha = (layer + 1) / 5.0
                c = (int(intensity * alpha), int(intensity * 0.85 * alpha), int(intensity * 0.4 * alpha))
                pygame.draw.line(s, c, (cx - offset - lw, y), (cx - offset + lw, y))
                pygame.draw.line(s, c, (cx + offset - lw, y), (cx + offset + lw, y))
        s = pygame.transform.smoothscale(pygame.transform.smoothscale(s, (65, 37)), (130, 74))
        for r, alpha in ((10, 0.3), (6, 0.6), (3, 1.0)):
            c = (int(255 * alpha), int(240 * alpha), int(180 * alpha))
            pygame.draw.circle(s, c, (cx - 16, 68), r)
            pygame.draw.circle(s, c, (cx + 16, 68), r)
    return s
def render(scr, D, px, cars, dr, drmax, cols, ch=CAMH):
    _SEG, _N, _Y, _CURVE = SEG, N, Y, CURVE
    _CAMD, _HZ, _VS, _HW, _RW = CAMD, HZ, VS, HW, RW
    _W, _H, _ROADW, _PLAYZ = W, H, ROADW, PLAYZ
    _BAND, _MARKS, _PADS, _RAMPS, _CUTS, _TUN, _BRG = BAND, MARKS, PADS, RAMPS, CUTS, TUN, BRG
    _SPR, _SPW, _KINDS, _FOG, _SUNX = SPR, SPW, KINDS, FOG, SUNX
    _SK = -_SUNX * 1.2 if abs(_SUNX) > 0.2 else 0.0
    _drmax = drmax
    pos = D % TL
    base = int(pos // _SEG); bp = (pos - base * _SEG) / _SEG
    pz = pos + _PLAYZ; ps = int(pz // _SEG) % _N; pp = (pz % _SEG) / _SEG
    camy = ch + _Y[ps] + (_Y[ps + 1] - _Y[ps]) * pp
    cx = px * _ROADW
    x, dx = 0.0, -_CURVE[base] * bp
    maxy = float(_H); zr = -bp * _SEG; i = base
    vis = []; add = vis.append
    for n in range(dr):
        zn = zr; zf = zr + _SEG; zr = zf
        xn = cx - x; xf = xn - dx
        yn = camy - _Y[i]; yf = camy - _Y[i + 1]
        x += dx; dx += _CURVE[i]
        j = i; i += 1
        if i == _N: i = 0
        if zf < 300.0: continue
        if zn < 300.0: zn = 300.0
        sn = _CAMD / zn; sf = _CAMD / zf
        y1 = _HZ + sn * yn * _VS; y2 = _HZ + sf * yf * _VS
        if y2 >= y1 or y2 >= maxy: continue
        add((n, j, _HW - sn * xn * _HW, y1, sn * _RW, _HW - sf * xf * _HW, y2, sf * _RW, sn, sf, maxy))
        maxy = y1
    render.nv = len(vis)
    bucket = {}
    b0 = base * _SEG
    for c in cars:
        dz = (c.z - b0) % TL; n = int(dz // _SEG)
        if n < dr: bucket.setdefault(n, []).append((c, (dz - n * _SEG) / _SEG))
    rect, poly, blit = pygame.draw.rect, pygame.draw.polygon, scr.blit
    pend = []
    for v in reversed(vis):
        n, j, x1, y1, w1, x2, y2, w2, sn, sf, clip = v
        grass, rum, road, lane = cols[_BAND[j]][n]
        iy1 = int(y1); iy2 = int(y2)
        if j not in _BRG:
            rect(scr, grass, (0, iy2, _W, iy1 - iy2 + 1))
        r1 = w1 * 0.16; r2 = w2 * 0.16
        poly(scr, rum, ((x1 - w1 - r1, y1), (x1 + w1 + r1, y1), (x2 + w2 + r2, y2), (x2 - w2 - r2, y2)))
        poly(scr, road, ((x1 - w1, y1), (x1 + w1, y1), (x2 + w2, y2), (x2 - w2, y2)))
        if j in _BRG:
            rh1 = sn * 200.0 * _VS; rh2 = sf * 200.0 * _VS
            rcol = (220, 50, 50) if (j // 2) % 2 == 0 else (240, 240, 240)
            poly(scr, rcol, ((x1 - w1 - r1, y1), (x1 - w1 - r1, y1 - rh1), (x2 - w2 - r2, y2 - rh2), (x2 - w2 - r2, y2)))
            poly(scr, rcol, ((x1 + w1 + r1, y1), (x1 + w1 + r1, y1 - rh1), (x2 + w2 + r2, y2 - rh2), (x2 + w2 + r2, y2)))
        if lane is not None and w2 > 5.0:
            a1 = w1 * 0.3333; a2 = w2 * 0.3333; m1 = w1 * 0.025; m2 = w2 * 0.025
            for s in (-1, 1):
                l1 = x1 + s * a1; l2 = x2 + s * a2
                poly(scr, lane, ((l1 - m1, y1), (l1 + m1, y1), (l2 + m2, y2), (l2 - m2, y2)))
        mk = _MARKS.get(j)
        if mk:
            c_ = (grass[0] * 7 // 10, grass[1] * 7 // 10, grass[2] * 7 // 10) if mk[1] else (road[0] >> 1, road[1] >> 1, road[2] >> 1)
            m1 = min(2.0, w1 * 0.02); m2 = min(2.0, w2 * 0.02)
            for s_ in (-0.10, 0.10):
                a_ = mk[0] + s_; c1 = x1 + w1 * a_; c2 = x2 + w2 * a_
                poly(scr, c_, ((c1 - m1, y1), (c1 + m1, y1), (c2 + m2, y2), (c2 - m2, y2)))
        if j in _PADS:
            c_ = (255, 210, 50) if j & 1 else (235, 120, 20)
            poly(scr, c_, ((x1 - w1 * 0.4, y1), (x1 + w1 * 0.4, y1), (x2 + w2 * 0.4, y2), (x2 - w2 * 0.4, y2)))
        elif j in _RAMPS:
            ln = _RAMPS[j] * 0.6667; a_, b_ = ln - 0.31, ln + 0.31
            h1, h2 = (70.0, 140.0) if (j - 1) in _RAMPS else (0.0, 70.0)
            u1 = y1 - sn * h1 * _VS; u2 = y2 - sf * h2 * _VS
            e_ = b_ if x1 + w1 * ln < _HW else a_
            poly(scr, (50, 105, 150), ((x1 + w1 * e_, y1), (x2 + w2 * e_, y2), (x2 + w2 * e_, u2), (x1 + w1 * e_, u1)))
            poly(scr, (90, 200, 255) if j & 1 else (235, 245, 255), ((x1 + w1 * a_, u1), (x1 + w1 * b_, u1), (x2 + w2 * b_, u2), (x2 + w2 * a_, u2)))
        cs = _CUTS.get(j)
        if cs:
            a_, b_ = (1.22, 2.1) if cs > 0 else (-2.1, -1.22)
            d_ = (min(255, road[0] + 55), min(255, road[1] + 15), max(0, road[2] - 25))
            poly(scr, d_, ((x1 + w1 * a_, y1), (x1 + w1 * b_, y1), (x2 + w2 * b_, y2), (x2 + w2 * a_, y2)))
        if j in _TUN:
            b = _BAND[j] & 1; dk = max(0.0, min(1.0, (dr - n) / (dr * 0.45)))
            fw = 1.0 - dk * (0.5 - 0.1 * b); fc = 1.0 - dk * (0.65 - 0.1 * b)
            wc = (int(road[0] * fw), int(road[1] * fw), int(road[2] * fw)); cc = (int(road[0] * fc), int(road[1] * fc), int(road[2] * fc))
            a1 = w1 * 1.12; a2 = w2 * 1.12
            u1 = y1 - sn * 1150.0 * _VS; u2 = y2 - sf * 1150.0 * _VS; v1 = y1 - sn * 1600.0 * _VS; v2 = y2 - sf * 1600.0 * _VS
            poly(scr, wc, ((x1 - a1, y1), (x1 - a1, u1), (x2 - a2, u2), (x2 - a2, y2)))
            poly(scr, wc, ((x1 + a1, y1), (x1 + a1, u1), (x2 + a2, u2), (x2 + a2, y2)))
            poly(scr, cc, ((x1 - a1, u1), (x1, v1), (x2, v2), (x2 - a2, u2)))
            poly(scr, cc, ((x1 + a1, u1), (x1, v1), (x2, v2), (x2 + a2, u2)))
            if not j & 3: poly(scr, _mix((255, 235, 150), min(0.92, (n / dr) ** 2)), ((x1 - w1 * 0.08, v1), (x1 + w1 * 0.08, v1), (x2 + w2 * 0.08, v2), (x2 - w2 * 0.08, v2)))
        if pend:
            for p in pend:
                if p[0] <= iy1: blit(p[1], p[2])
            pend = [p for p in pend if p[0] > iy1]
        sp = _SPR[j]
        if sp:
            hid = iy1 - int(clip)
            for k, ofs in sp:
                w = int(sn * _SPW[k] * _HW); w = w & -8 if w > 64 else w & -4
                if w < 4 or w > (360 if k >= 16 else 200): continue
                nm = _KINDS[k] + (("_l" if _CURVE[j] < -1.5 else ("_r" if _CURVE[j] > 1.5 else "")) if k > 16 else "")
                s = scaled(nm, w, int(min(0.92, (n / _drmax) ** 2) * 6), _FOG, (1 if _SUNX > 0.2 else (-1 if _SUNX < -0.2 else 0)) if _KINDS[k] not in ("flag", "lantern", "barrel") else 0)
                h = s.get_height()
                if hid >= h: continue
                xx = int(x1 + ofs * w1) - (w >> 1)
                if xx >= _W or xx + w <= 0: continue
                if hid <= 0 and k >= 16 and _SK:
                    sh_s = shadow_3d(s, w, 110, _SK, nm)
                    pend.append((iy1 + sh_s.get_height(), sh_s, (xx - (sh_s.get_width() - w if _SK > 0 else 0), iy1)))
                if hid > 0: blit(s, (xx, iy1 - h), (0, 0, w, h - hid))
                else: blit(s, (xx, iy1 - h))
        bl = bucket.get(n)
        if bl:
            for c, pct in bl:
                w = int((sn + (sf - sn) * pct) * S.CARV * _HW); w = w & -8 if w > 64 else w & -4
                if w < 4 or w > 150: continue
                s = scaled(c.key + ("l" if _CURVE[j] < -1.5 else ("r" if _CURVE[j] > 1.5 else "s")), w); h = s.get_height()
                yy = int(y1 + (y2 - y1) * pct); hid = yy - int(clip)
                if hid >= h: continue
                xx = int(x1 + (x2 - x1) * pct + c.x * (w1 + (w2 - w1) * pct)) - (w >> 1)
                if xx >= _W or xx + w <= 0: continue
                if c.jh > 0.0:
                    sh_w_car = max(4, int(w * 0.8)) & -4
                    sh_ = shadow(sh_w_car, 140)
                    blit(sh_, (xx + ((w - sh_.get_width()) >> 1), yy - (sh_.get_height() >> 1)))
                    lift = int(c.jh * w / 60.0); yy -= lift; hid -= lift
                if c.nt > 0.0:
                    fw = max(2, w // 9); fh = max(3, h // 3) + ((pygame.time.get_ticks() >> 5) & 3) * max(1, h // 14)
                    for fx in (0.2, 0.68): rect(scr, (255, 170, 20), (xx + int(w * fx), yy - max(2, h // 8), fw, fh))
                if c.dt > 0.0:
                    sz = max(2, w // 8); fl = (pygame.time.get_ticks() >> 6) & 3
                    for fx in (0.04, 0.8): rect(scr, (205, 205, 212), (xx + int(w * fx), yy - sz - fl, sz, sz))
                if hid > 0: blit(s, (xx, yy - h), (0, 0, w, h - hid))
                else: blit(s, (xx, yy - h))
    for p in pend: blit(p[1], p[2])
DIF = [1.0]
render.nv = 0
MENU_ST = frozenset(("menu","title","set", "cred", "how", "story", "brief", "car", "track", "dif", "name", "gift", "vs", "nethome", "netjoin", "netip", "netlobby", "prof",))
SAVE = os.path.join(HERE, "racer_save.json")
if WEB: from platform import window as _win
def load_save():
    try:
        if WEB: d = json.loads(_win.localStorage.getItem("outdrive_save") or "{}")
        else:
            with open(SAVE, "r", encoding="utf-8") as f: d = json.load(f)
        if isinstance(d, dict): return d
    except Exception:
        pass
    return {}
def ram_mb():
    try:
        with open("/proc/self/statm") as f: return int(f.read().split()[1]) * 4096 / 1048576.0
    except Exception: return 0.0
def write_save(d):
    try:
        if WEB: _win.localStorage.setItem("outdrive_save", json.dumps(d)); return
        with open(SAVE + ".tmp", "w", encoding="utf-8") as f: json.dump(d, f,indent=2)
        os.replace(SAVE + ".tmp", SAVE)
    except Exception:
        pass
def pad_caps(pad, font):
    pad.btn = tuple((n, "|".join(T(p) for p in ("Trôi" if n == "A" else c).split("|")), x, y) for n, c, x, y in BUTTONS)
    pad._art(font)
KEYS = {pygame.K_LEFT: "left", pygame.K_a: "left", pygame.K_RIGHT: "right", pygame.K_d: "right",
        pygame.K_UP: "up", pygame.K_w: "up", pygame.K_DOWN: "down", pygame.K_s: "down",
        pygame.K_z: "A", pygame.K_SPACE: "A", pygame.K_RETURN: "A", pygame.K_x: "B",
        pygame.K_c: "C", pygame.K_LSHIFT: "C"}
BACKK = (pygame.K_ESCAPE, getattr(pygame, "K_AC_BACK", pygame.K_ESCAPE))
AWAY = tuple(getattr(pygame, n) for n in ("WINDOWFOCUSLOST", "WINDOWMINIMIZED", "WINDOWHIDDEN",
                                         "APP_WILLENTERBACKGROUND", "APP_DIDENTERBACKGROUND") if hasattr(pygame, n))
def net_cars(rs):
    out = []
    for pid, nm, c, *_ in rs:
        c %= len(PCAR_DEF); k = Car(PLAYZ, LANES[pid % len(LANES)], 0.0, 0); col = PCAR_DEF[c][1]
        k.key = "p%d" % c; k.col = col if sum(col) > 200 else lite(col); out.append(k)
    return out
def net_sync(net, cars, nids, ft, now, dt):
    k = min(1.0, dt * 12.0)
    for i, c in enumerate(cars):
        r = net.remote.get(nids[i])
        if r is None or now - r.t > 3.0:
            if i not in ft: c.dist = -1e9
            c.x = 50.0; c.spd = 0.0
            continue
        pred = r.D + r.spd * min(0.25, now - r.t)
        if c.x > 10.0 or c.dist < -1e8: c.dist, c.x = pred, r.px
        else:
            c.dist += c.spd * dt
            c.dist += (pred - c.dist) * k; c.x += (r.px - c.x) * k
        c.spd = r.spd
        z = c.dist % TL + PLAYZ
        c.z = z - TL if z >= TL else z
        if r.flags & 4 and i not in ft: ft[i] = r.ftime
NL, EGG = 11, "DUONGVANPHI"
CHS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
def draw_name(scr, nch, cur, tt):
    panel(scr, 10, 6, 300, 180, "TÊN TAY ĐUA"); ctext(scr, "Chọn từng ký tự cho tên của bạn", 34, C_DIM)
    d = pygame.draw
    for i, k in enumerate(nch):
        x, sel = 40 + i * 22, i == cur
        d.rect(scr, (70, 30, 100) if sel else (30, 28, 52), (x, 66, 20, 28)); d.rect(scr, C_CYAN if sel else (70, 66, 110), (x, 66, 20, 28), 1)
        t = txt(CHS[k], (255, 255, 255)); scr.blit(t, (x + 10 - (t.get_width() >> 1), 73))
        if sel:
            o = int(2 * math.sin(tt * 8))
            d.polygon(scr, C_AMB, ((x + 10, 57 + o), (x + 4, 63 + o), (x + 16, 63 + o))); d.polygon(scr, C_AMB, ((x + 10, 103 - o), (x + 4, 97 - o), (x + 16, 97 - o)))
    ctext(scr, "".join(CHS[k] for k in nch).strip() or "...", 120, (255, 230, 90), 2)
    hints(scr, 168, (("^ v", "Đổi chữ"), ("< >", "Chọn ô"), ("A", "Xong")))
async def main():
    pygame.mixer.pre_init(*MIX)
    pygame.init()
    pygame.event.set_allowed(None) # Chặn toàn bộ mọi sự kiện
    pygame.event.set_allowed([pygame.QUIT,pygame.KEYDOWN, pygame.KEYUP, pygame.FINGERDOWN, pygame.FINGERUP])

    touch = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
    pfont = _sysfont(12)
    pad = TouchPad(W, H, buttons=BUTTONS, scale=2 if touch or WEB else 3, touch=touch, font=pfont, tint=TINT)
    pad.lab = False
    pygame.display.set_caption("Outdrive 199x")
    pad.screen.fill((14, 12, 28))
    try: en = int(load_save().get("set", {}).get("lang", 0)) == 1
    except Exception: en = False
    base_text = "LOADING" if en else "ĐANG TẢI"
    async def draw_loading(step):
        pad.screen.fill((14, 12, 28)) # Nền tối mặc  
        cx, cy = W // 2, H // 2 - 10
        for i in range(8):
            angle = i * (math.pi / 4)
            px = cx + math.cos(angle) * 12
            py = cy + math.sin(angle) * 12
            is_lit = (i <= step * 3) 
            color = (40, 255, 220) if is_lit else (40, 42, 56)
            pygame.draw.circle(pad.screen, color, (int(px), int(py)), 2)
        t = _font(10).render(base_text, True,C_PINK)
        pad.screen.blit(t, t.get_rect(center=(W // 2, H // 2 + 15)))
        pad.present(); await asyncio.sleep(0)  
    await draw_loading(0)
    init_assets()
    await draw_loading(1)
    init_sfx()
    await draw_loading(2)
    rec = Recorder(pad.screen, fps=30, secs=20, scale=2, mode="long", max_mb=40, cv=pad._cv, font=S.FONT, folder=HERE)
    gc.disable()
    save = load_save()
    for k_ in ("rec", "set", "mas"):
        if not isinstance(save.get(k_), dict): save[k_] = {}
    recs, cfg = save["rec"], save["set"]
    for k_, v_, m_ in (("q", 2, 3), ("vol", 3, 4), ("dif", 1, 3), ("lang", 0, 2)):
        try: cfg[k_] = int(cfg.get(k_, v_)) % m_
        except Exception: cfg[k_] = v_
    drmax = QDR[cfg["q"]]; msel = ssel = 0
    set_lang(cfg["lang"]); pad_caps(pad, pfont)
    set_vol(cfg["vol"])
    try: car_i = int(save.get("car", 0)) % len(PCAR_DEF)
    except Exception: car_i = 0
    try: trk_i = int(save.get("track", 0)) % len(TRACKS)
    except Exception: trk_i = 0
    load_track(trk_i)
    pc = time.perf_counter
    sv = save.get("story"); sv = save["story"] = sv if isinstance(sv, dict) else {}
    if not isinstance(sv.get("stars"), dict): sv["stars"] = {}
    stg = sv["stars"]
    try: prog = max(0, min(len(STORY), int(sv.get("prog", 0))))
    except Exception: prog = 0
    for k in [k for k in stg if not (str(k).isdigit() and int(k) < prog)]: del stg[k]
    try: mp = max(0, min(2, int(sv.get("mp", 0))))
    except Exception: mp = 0
    mi = 0
    nc = ncar(prog,sum(stg.values())); mode, chap, csel, rv, won, newcar = "free", 0, 0, None, False, -1
    egg = save.get("egg") == 1
    newtrk, newleg = [], False
    def unlk(i): return i < nc or (i == 7 and egg)
    keep = None
    def setlock(f):
        nonlocal car_i, keep
        if f is None:
            if keep is not None: car_i, keep = keep, None
        elif car_i != f:
            if keep is None: keep = car_i
            car_i = f
    def nextcar(i, d):
        while d:
            i = (i + d) % len(PCAR_DEF)
            if unlk(i): break
        return i
    if not unlk(car_i): car_i = 0
    scr, clock, rnd = pad.screen, pygame.time.Clock(), random.Random()
    rect, line = pygame.draw.rect, pygame.draw.line
    pl = Car(PLAYZ, 0.0, 0.0, 0)
    cars = []; allc = [pl]
    st, run = "menu", True
    shot = False
    D = px = spd = shake = slip = tt = 0.0
    nitro, nb, boost, onpad = 0.4, 0.0, False, False
    drift, drift_t, kick, ddir, pbt = False, 0.0, 0.0, 1.0, 0.0
    vmax, acc, grip, nitm = MAXSPD, ACC, 1.0, 1.0
    cd = t_race = done_t = lap_start = 0.0
    lap_prev, newrec, res = 1, False, (1, 0.0)
    bg1 = bg2 = 0.0
    cut = False
    jh = jv = 0.0
    conf = []
    dr = drmax; cols = build_cols(dr); fps_t = 0.0; good = 0
    kb, kbp = set(), set()
    lbn = None
    ft = {}
    nm_cars = set()
    newlap, olds = False, None
    fl, ch = 0.0, CAMH
    pst, trn = "", None
    prev = pygame.Surface((W, H)).convert()
    ov = pygame.Surface((W, H)).convert(); ov.set_colorkey(KEY)
    mang = None
    paused, psel, snap, howto_next = False, 0, None, None
    net = netplay.Net() if netplay else None
    nids, quit_until, nsel, jsel, myip = [], 0.0, 0, 0, "127.0.0.1"
    octs, ocur, toast = [192, 168, 1, 1], 3, ["", 0.0]
    try: nname = int(save.get("nname", 0)) % len(NAMES)
    except Exception: nname = 0
    pname = str(save.get("pname", ""))[:NL]
    try: pts = max(0, int(save.get("pts", 0)))
    except Exception: pts = 0
    if title_of(pts)[0] >= 5 and not egg: egg = True; save["egg"] = 1
    bn_t = 9.0
    pg, promo, mgain = 0, False, 0
    nch, ncur, nret = [0] * NL, 0, "menu"
    if not pname: st = "name"
    tips, tip = save.get("tips", 0), ["", 0.0]
    def tipo(b, m):
        nonlocal tips
        if not tips & b: tips |= b; save["tips"] = tips; tip[0], tip[1] = m, 3.0
    def tset(m): toast[0], toast[1] = m, pc() + 2.5
    aq = []
    def mas_add(ci, t, dist, dm, tk):
        m = save["mas"].setdefault(str(ci), [0, 0, 0, 0]); tp = car_stats(ci)[0]
        q = pace(t, dist, tp, TCF[tk])
        g = int(100 * q * q * dm * max(0.6, min(1.3, dist / 1.09e6))); l0 = mas_lv(m)[0]
        m[0] += g; m[1] += 1; m[2] = max(m[2], int(100 * q)); l1 = mas_lv(m)[0]
        if l1 > l0: aq.append(T(PCAR_DEF[ci][0]) + ": " + T(MASN[l1]))
        return g
    def mas_txt(ci, g): return "%s +%d XP · %s" % (T(PCAR_DEF[ci][0]), g, T(MASN[mas_lv(save["mas"].get(str(ci), [0, 0, 0, 0]))[0]]))
    def mas_chip(ci, x, y):
        m = save["mas"].get(str(ci), [0, 0, 0, 0]); i, nx = mas_lv(m)
        chip(scr, x, y, T(MASN[i]) + (" %d/%d" % (m[0], nx) if nx else " MAX"), MCOL[i])
    parts = []
    gt = (3, True, "")
    vs_t = 0.0
    rw_steps, rw_i, rw_t, rw_old, rw_new = [], 0, 0.0, 0, 0
    pod, pt, seenp, pkey = [], 0.0, False, "A"
    sks = []
    skid = []
    fire = []
    def spark(d, n):
        if cfg["q"] and len(sks) < 48:
            x, y = 160 + int(slip * 7) + d * 24, H - 20
            _r = rnd.randint
            sks.extend([[x, y, d * _r(20, 170), _r(-190, -40), 0.0] for _ in range(min(n, 48 - len(sks)))])
    def puff(x, y, col, up=1.0):
        if cfg["q"] and len(parts) < 60: parts.append([x, y, rnd.uniform(-14, 14) - slip * 40, rnd.uniform(-22, -6) * up, 0.0, col])
    hoff_top = hoff_bot = 0 ;dbg = False; nlift = 0.0
    pf = 0.0
    pnit=0.0
    pros = 0
    sm_pitch = 0.0
    try: ptime = float(save.get("ptime", 0))
    except Exception: ptime = 0.0
    t_last = ptw = pc()
    tm = [0.0, 0.0, 0.0, 0.0]; ft_max = 0.0
    ram = 0.0; ram_t = 0.0
    def u_title():
        nonlocal st
        if "A" in pressed: st = "menu"
    def u_menu():
        nonlocal howto_next, mode, msel, myip, nsel, st
        setlock(None)
        msel = (msel + ("down" in pressed) - ("up" in pressed)) % len(MENU)
        if "C" in pressed: st = "prof"
        if "A" in pressed:
            if msel < 2:
                if msel == 0: mode = "free"
                nxt = "car" if msel == 0 else "story"
                if save.get("seen"): st = nxt
                else: st, howto_next = "how", nxt
            elif msel == 2:
                if netplay is None: tset("Chỉ có ở bản tải về" if WEB else "Thiếu file netplay.py")
                else: mode = "net"; st = "nethome"; nsel = 0; myip = netplay.Net.local_ip()
            elif msel == 3: st = "prof"
            else: st = "set"
    def u_set():
        nonlocal cols, d, dr, drmax, howto_next, ssel, st
        ssel = (ssel + ("down" in pressed) - ("up" in pressed)) % 5
        d = ("right" in pressed) - ("left" in pressed)
        if "B" in pressed: st = "menu"
        elif ssel > 2:
            if "A" in pressed:
                if ssel == 3: st, howto_next = "how", "set"
                else: st = "cred"
        elif d or "A" in pressed:
            d = d or 1
            key = ("q", "vol", "lang")[ssel]
            m_vals = (3, 4, 2)[ssel]
            cfg[key] = (cfg[key] + d) % m_vals
            if ssel == 0: drmax = QDR[cfg["q"]]; dr = drmax; cols = build_cols(dr)
            elif ssel == 1:
                set_vol(cfg["vol"])
                sfx('beep')
            elif ssel == 2: set_lang(cfg["lang"]); pad_caps(pad, pfont)
            write_save(save)
    def u_dif():
        nonlocal st
        cfg["dif"] = (cfg["dif"] + ("down" in pressed) - ("up" in pressed)) % 3
        if "A" in pressed: write_save(save); st = "flyin"
        elif "B" in pressed: st = "track"
    def u_cred():
        nonlocal st
        if "A" in pressed or "B" in pressed: st = "set"
    def u_prof():
        nonlocal shot, st
        if "C" in pressed: shot = True
        elif "A" in pressed or "B" in pressed: st = "menu"
    def u_how():
        nonlocal howto_next, st
        if "A" in pressed or "B" in pressed:
            st = howto_next or "menu"; howto_next = None
            if not save.get("seen"): save["seen"] = 1; write_save(save)
    def u_reward():
        nonlocal chap, conf, mi, rw_i, rw_t, st
        rw_t += dt
        if rw_steps[rw_i] == "star":
            for j in range(rw_new - rw_old):
                if rw_t - dt < 1.1 + 0.8 * j <= rw_t: sfx("star")
        if rw_t > 0.4 and ("A" in pressed or "B" in pressed):
            if rw_i + 1 < len(rw_steps):
                rw_i += 1; rw_t = 0.0
                if rw_steps[rw_i] == "car":
                    sfx("go"); conf = [[rnd.uniform(0, W), rnd.uniform(-60, 0), rnd.uniform(-18, 18), rnd.uniform(45, 85),
                                        RK[0] if rnd.random() < 0.5 else CONF[rnd.randrange(4)]] for _ in range(36)]
            elif not won: st = "restart" if "A" in pressed else "story"
            elif mi < 2: mi += 1; st = "brief"
            elif chap + 1 < len(STORY): chap += 1; mi = 0; st = "brief"
            else: st = "end"
    def u_vs():
        nonlocal h, st, vs_t
        vs_t += dt; h = VS_H * (mi == 2)
        if vs_t - dt < 0.2 <= vs_t: sfx("bump")
        if vs_t - dt < 0.8 + h <= vs_t: sfx("whoosh")
        if vs_t - dt < 1.05 + h <= vs_t: sfx("bump")
        if vs_t >= VS_T + h: st = "flyin"
    def u_gift():
        nonlocal rw_t, st
        rw_t += dt
        if rw_t > 0.4 and ("A" in pressed or "B" in pressed): st = nret
    def u_podium():
        nonlocal pt, st
        pt += dt
        if pt > 1.0 and ({"A", "B", "C"} & pressed): st = "done"; kbp.add(pkey)
    def u_end():
        nonlocal st
        if "A" in pressed or "B" in pressed: st = "menu"
    def u_name():
        nonlocal car_i, conf, egg, ncur, pname, rw_t, st
        nch[ncur] = (nch[ncur] + ("up" in pressed) - ("down" in pressed)) % len(CHS)
        ncur = max(0, min(NL - 1, ncur + ("right" in pressed) - ("left" in pressed)))
        if "A" in pressed:
            nm_ = "".join(CHS[i] for i in nch).strip()
            if nm_:
                pname = nm_; save["pname"] = nm_
                if nm_ == EGG and not egg:
                    egg = True; save["egg"] = 1; car_i = 7; st, rw_t = "gift", 0.0; sfx("go")
                    conf = [[rnd.uniform(0, W), rnd.uniform(-60, 0), rnd.uniform(-18, 18), rnd.uniform(45, 85),
                             RK[0] if rnd.random() < 0.5 else CONF[rnd.randrange(4)]] for _ in range(36)]
                else: st = nret
                write_save(save)
            else: tset("Nhập ít nhất 1 ký tự")
        elif "B" in pressed and pname: st = nret
    def u_nethome():
        nonlocal car_i, d, jsel, mode, nch, ncur, nret, nsel, octs, ocur, st
        nsel = (nsel + ("down" in pressed) - ("up" in pressed)) % 4
        d = ("right" in pressed) - ("left" in pressed)
        if nsel == 3 and "A" in pressed:
            nch = [CHS.index(c) if c in CHS else 0 for c in pname.ljust(NL)]; ncur = 0; nret = "nethome"; st = "name"
        elif "B" in pressed: st = "menu"; mode = "free"
        elif "A" in pressed and nsel < 3:
            if not unlk(car_i): car_i = 0
            if nsel == 0:
                if net.host(pname or NAMES[nname], trk_i, car_i, TCHK[trk_i]): st = "netlobby"
                else: tset(net.err or "Lỗi mạng")
            elif nsel == 1:
                if net.browse(): jsel = 0; st = "netjoin"
                else: tset(net.err or "Lỗi mạng")
            else:
                try:
                    octs = [max(0, min(255, int(x))) for x in (save.get("lastip") or myip).split(".")]
                    if len(octs) != 4: raise ValueError
                except Exception: octs = [192, 168, 1, 1]
                ocur = 3; st = "netip"
    def u_netjoin():
        nonlocal jsel, st
        rl = sorted(net.rooms.items())
        if net.old and not rl and not toast[0].startswith("Có phòng"): tset("Có phòng dùng bản game khác - hãy cập nhật")
        if rl: jsel %= len(rl)
        jsel = (jsel + ("down" in pressed) - ("up" in pressed)) % max(1, len(rl))
        if net.state != "browse": st = "nethome"
        elif "B" in pressed: net.close(); st = "nethome"
        elif "A" in pressed and rl:
            ad, rm = rl[jsel]
            if rm[4]: tset("Phòng đang đua")
            elif rm[1] >= len(TRACKS) or rm[5] != TCHK[rm[1]]: tset("Khác phiên bản đường đua - hãy cập nhật game")
            elif net.join(ad, pname or NAMES[nname], car_i): st = "netlobby"
            else: tset(net.err or "Lỗi mạng")
    def u_netip():
        nonlocal ocur, st
        ocur = (ocur + ("right" in pressed) - ("left" in pressed)) % 4
        octs[ocur] = (octs[ocur] + ("up" in pressed) - ("down" in pressed) + 10 * ("C" in pressed)) % 256
        if "B" in pressed: st = "nethome"
        elif "A" in pressed:
            ip = ".".join(str(v) for v in octs); save["lastip"] = ip; write_save(save)
            if net.join(ip, pname or NAMES[nname], car_i): st = "netlobby"
            else: tset(net.err or "Lỗi mạng")
    def u_netlobby():
        nonlocal D, car_i, cols, g, pros, r, st, trk_i
        if net.state == "idle":
            tset(net.err or "Đã ngắt kết nối"); st = "nethome"
        else:
            if len(net.roster) != pros:
                if pros and net.roster: tset(T("Có người vào phòng") if len(net.roster) > pros else T("Có người rời phòng")); sfx("ok")
                pros = len(net.roster)
            if not net.is_host and net.roster:
                if net.chk and net.chk != TCHK[net.track % len(TRACKS)]:
                    net.leave(); tset("Khác phiên bản game"); st = "nethome"
                elif net.track != trk_i and net.track < len(TRACKS):
                    trk_i = net.track; load_track(trk_i); cols = build_cols(dr); D = 0.0
                g = net.take_start()
                if g: trk_i = g[1]; st = "flyin"
            if st == "netlobby":
                if "B" in pressed: net.leave(); st = "nethome"
                elif "C" in pressed:
                    car_i = nextcar(car_i, 1); net.set_car(car_i)
                    if not net.is_host:
                        net.ready = 0; net._t_keep = -9.0
                elif net.is_host and net.state == "lobby":
                    chg = ("right" in pressed) - ("left" in pressed)
                    if chg:
                        trk_i = (trk_i + chg) % len(TRACKS); load_track(trk_i); cols = build_cols(dr); D = 0.0
                        net.set_track(trk_i, TCHK[trk_i])
                        for r in net.roster:
                            if r[0] != 0: r[3] = 0
                    elif "A" in pressed:
                        if len(net.roster) < 2: tset("Cần ít nhất 2 người")
                        elif not all(r[3] for r in net.roster if r[0] != 0): tset("Có người chưa sẵn sàng")
                        else: net.start(trk_i, TCHK[trk_i]); st = "flyin"
                elif not net.is_host:
                    if "A" in pressed:
                        net.ready = 1 - net.ready
                        net._t_keep = -9.0
    def u_story():
        nonlocal car_i, chap, csel, mi, st
        setlock(None)
        csel = (csel + ("down" in pressed) - ("up" in pressed)) % len(STORY)
        if "A" in pressed and csel <= prog:
            chap = csel; mi = mp if chap == prog else 2
            if not unlk(car_i): car_i = 0
            st = "brief"
        elif "B" in pressed: st = "menu"
    def u_brief():
        nonlocal car_i, fc, mode, st, trk_i, tt, vs_t
        if not hasattr(main, "dlg_step"): main.dlg_step = 0
        fc = FORCE.get((chap, mi)); setlock(fc)
        if fc is None: car_i = nextcar(car_i, ("right" in pressed) - ("left" in pressed))
        if "A" in pressed:
            if main.dlg_step == 0:
                main.dlg_step = 1; tt = 0.0
            else:
                main.dlg_step = 0; mode = "story"; trk_i = mc(chap, mi)[1]; st, vs_t = "vs", 0.0; sfx("rev")
        elif "B" in pressed:
            main.dlg_step = 0; st = "story"
    def u_car():
        nonlocal car_i, st
        if "left" in pressed: car_i = (car_i - 1) % len(PCAR_DEF); draw_car_menu.dir = -1
        elif "right" in pressed: car_i = (car_i + 1) % len(PCAR_DEF); draw_car_menu.dir = 1
        elif "A" in pressed and unlk(car_i): st = "track";sfx("rev")
        elif "B" in pressed: st = "menu"
    def u_track():
        nonlocal D, car_i, cols, st, trk_i
        chg = ("right" in pressed) - ("left" in pressed); dc = ("down" in pressed) - ("up" in pressed)
        if dc: car_i = nextcar(car_i, dc)
        elif chg:
            trk_i = (trk_i + chg) % len(TRACKS); load_track(trk_i); cols = build_cols(dr); D = 0.0
        elif "A" in pressed:
            if tunlk(trk_i, prog):
                if mode == "free": st = "dif"
                else: st = "flyin"
            else: tset(T("Thắng chương %d để mở đường") % TNEED[trk_i])
        elif "B" in pressed: st = "car"
    UPD = {"title": u_title, "menu": u_menu, "set": u_set, "dif": u_dif, "cred": u_cred, "prof": u_prof, "how": u_how, "reward": u_reward, "vs": u_vs, "gift": u_gift, "podium": u_podium, "end": u_end, "name": u_name, "nethome": u_nethome, "netjoin": u_netjoin, "netip": u_netip, "netlobby": u_netlobby, "story": u_story, "brief": u_brief, "car": u_car, "track": u_track}
    def d_brief():
        nonlocal fc
        draw_brief(scr, mc(chap, mi), chap, car_i, tt, getattr(main, "dlg_step", 0))
        if getattr(main, "dlg_step", 0) == 0:
            fc = FORCE.get((chap, mi)); sg = next((c for c in SUG[mc(chap, mi)[1]] if unlk(c)), -1)
            if fc is not None: scr.blit(txt(T("Xe bắt buộc: ") + T(PCAR_DEF[fc][0]), (255, 190, 60)), (W // 2 + 20, 148))
            elif sg >= 0 and sg != car_i: scr.blit(txt(T("Gợi ý: ") + T(PCAR_DEF[sg][0]), (120, 255, 255)), (W // 2 + 20, 148))
    DRAW = {
        "title": lambda: draw_title(scr, tt),
        "menu": lambda: draw_menu(scr, msel, tt),
        "prof": lambda: draw_prof(scr, save, pname, pts, sum(stg.values()), prog, int(ptime), tt, not shot, nc + egg),
        "name": lambda: draw_name(scr, nch, ncur, tt),
        "set": lambda: draw_settings(scr, ssel, cfg),
        "dif": lambda: draw_diff(scr, cfg["dif"], tt, trk_i),
        "cred": lambda: draw_credit(scr),
        "how": lambda: draw_howto(scr),
        "nethome": lambda: draw_netmenu(scr, nsel, pname or NAMES[nname], myip),
        "netjoin": lambda: draw_netjoin(scr, sorted(net.rooms.items()), jsel, tt),
        "netip": lambda: draw_netip(scr, octs, ocur, tt),
        "netlobby": lambda: draw_netlobby(scr, net, trk_i, tt,pts),
        "podium": lambda: draw_podium(scr, pod, pt, tt),
        "reward": lambda: draw_reward(scr, rw_steps[rw_i], rw_t, tt, mc(chap, mi), chap, car_i, rw_old, rw_new, newcar, res[0]),
        "vs": lambda: draw_vs(scr, mc(chap, mi), chap, car_i, vs_t, mi == 2),
        "gift": lambda: draw_reward(scr, "car", rw_t, tt, None, 0, car_i, 0, 0, 7, 0),
        "end": lambda: draw_end(scr, sum(stg.get(str(i), 0) for i in range(len(STORY))), nc + egg, tt),
        "story": lambda: draw_story(scr, csel, prog, stg, mp),
        "brief": d_brief,
        "car": lambda: draw_car_menu(scr, car_i, tt, not unlk(car_i), False, pts, save=save),
        "fly": lambda: draw_fly(scr, trk_i, fl),
        "track": lambda: draw_track_menu(scr, trk_i, recs, tt, pts, car_i, next((c for c in SUG[trk_i] if unlk(c)), -1), prog),
    }
    while run:
        await asyncio.sleep(0)
        dt = clock.tick(60) / 1000.0
        tf = pc()
        t0 = pc()
        if st == "race" and not paused: ptime += min(1.0, tf - t_last)
        t_last = tf
        save["ptime"] = int(ptime)
        if tf - ptw > 60.0: ptw = tf; write_save(save)
        if dt > 0.05: dt = 0.05
        back = pk = away = False
        online = mode == "net" and st in ("restart", "count", "race", "done")
        for e in pygame.event.get():
            et = e.type
            if et == pygame.QUIT: run = False
            elif et == pygame.KEYDOWN:
                if e.key in BACKK: back = True
                elif e.key == pygame.K_F3: dbg = not dbg
                elif e.key == pygame.K_p: pk = True
                n = KEYS.get(e.key)
                if n: kb.add(n); kbp.add(n)
            elif et == pygame.KEYUP:
                kb.discard(KEYS.get(e.key))
            elif et in AWAY: away = True; write_save(save)
            elif st == "menu" and (et == pygame.FINGERDOWN or (et == pygame.MOUSEBUTTONDOWN and e.button == 1 and not (pad._fs and getattr(e, "touch", False)))):
                if et == pygame.FINGERDOWN: ww, wh = pygame.display.get_surface().get_size(); tx, ty = pad._cv(e.x * ww, e.y * wh)
                else: tx, ty = pad._cv(*e.pos)
                if VER_HIT[0] <= tx < VER_HIT[2] and VER_HIT[1] <= ty < VER_HIT[3]: dbg = not dbg; tset("Debug " + ("BẬT" if dbg else "TẮT"))
            elif st in ("count", "race") and not paused and (et == pygame.FINGERDOWN or (
                    et == pygame.MOUSEBUTTONDOWN and e.button == 1 and not (pad._fs and getattr(e, "touch", False)))):
                if et == pygame.FINGERDOWN: ww, wh = pygame.display.get_surface().get_size(); tx, ty = pad._cv(e.x * ww, e.y * wh)
                else: tx, ty = pad._cv(*e.pos)
                if PAUSE_HIT[0] <= tx < PAUSE_HIT[2] and PAUSE_HIT[1] <= ty < PAUSE_HIT[3]: pk = True
            pad.event(e)
            rec.event(e)
        if paused:
            if back or pk: paused = False
        elif st in ("count", "race"):
            if online:
                if back or pk:
                    if tf < quit_until:
                        net.leave(); st = "nethome"; mode = "net"; cars = []; allc = [pl]; nids = []; D = 0.0; jh = jv = 0.0; online = False
                    else: quit_until = tf + 2.0; tset("Nhấn lại để rời trận")
            elif back or pk or away:rec.undraw(); paused, psel, snap = True, 0, scr.copy(); sfx_stop()
        elif back:
            if st == "title": run = WEB
            else: kbp.add("B")
        pad.update()
        held = pad.held | kb; pressed = pad.pressed | kbp; kbp.clear(); PRESS.update(dict.fromkeys(pressed, tf))
        if st == "done" and "C" in pressed and done_t > 2.6: shot = True
        if st in MENU_ST or st in ("podium", "reward", "end", "done"):
            if pressed & {"up", "down", "left", "right"}: sfx("tick")
            elif "A" in pressed: sfx("ok")
            if st in MENU_ST: play_bgm("menu")
        if net is not None:
            net.pts = pts
            if net.active: net.poll(tf)
        if online and net.state == "idle":
            tset(net.err or "Mất kết nối"); st = "menu"; mode = "free"; cars = []; allc = [pl]; nids = []; D = 0.0; jh = jv = 0.0; online = False; lbn = None
        if mode == "net" and st in ("flyin", "fly") and net.state == "idle":
            tset(net.err or "Mất kết nối"); st = "menu"; mode = "free"; cars = []; allc = [pl]; nids = []; D = 0.0; jh = jv = 0.0; lbn = None
        if trn:
            trn[0] += dt; transition(scr, trn, ov)
            if trn[0] >= trn[1]: trn = None
            rec.tick(); rec.draw(); pad.present(); continue
        if paused:
            psel = (psel + ("down" in pressed) - ("up" in pressed)) % 3
            if "A" in pressed or "B" in pressed:
                ok = "A" in pressed; paused = False; pressed = set()
                if ok and psel == 1: st = "restart";play_bgm('race')
                elif ok and psel == 2: st = "story" if mode == "story" else "track"; cars = []; allc = [pl]; D = 0.0; jh = jv = 0.0
            if paused:
                scr.blit(snap, (0, 0)); draw_pause(scr, psel); rec.draw(); pad.present(); continue
        tt += dt
        if st == "restart":
            load_track(trk_i); cols = build_cols(dr)
            top, am, grip, nitm = car_stats(car_i); vmax = MAXSPD * top; acc = ACC * am
            D = px = spd = shake = slip = 0.0; nitro, nb = 0.4, 0.0; drift, drift_t, kick, pbt = False, 0.0, 0.0, 0.0
            jh = jv = 0.0
            MARKS.clear()
            mang = None
            tank = car_i == 6
            seenp = False; bn_t = 9.0
            if mode == "net":
                others = [r for r in net.roster if r[0] != net.me]; nids = [r[0] for r in others]
                cars = net_cars(others); px = LANES[net.me % len(LANES)]; quit_until = 0.0
            else: cars = new_cars(rnd)
            allc = cars + [pl]; gc.collect()
            DIF[0] = (0.96, 1.06, 1.12)[cfg["dif"]] if mode == "free" else 1.0
            play_bgm("race")
            rv = None
            spw = False
            newlap = False
            lbn = None
            ft = {}
            nm_cars.clear()
            if mode == "story":
                c = mc(chap, mi); set_laps(c[2]); rv = cars[0]; gt = (c[7], c[8], goal(c))
                ci_ = c[4] % len(CAR_COLS); o = next((x for x in cars if x is not rv and x.key == "c%d" % ci_), None)
                if o: rv.key, o.key = o.key, rv.key; rv.col, o.col = o.col, rv.col
                else: rv.key = "c%d" % ci_; rv.col = CAR_COLS[ci_]
                rv.base = MAXSPD * c[5]; rv.rb = c[6]; rv.bs = 1; rv.sk = 3 if chap >= 3 else 1
                for x in cars:
                    if x is not rv: x.base *= 0.96 + 0.015 * chap
            st, cd, t_race, lap_start, lap_prev, newrec = "count", 3.0, 0.0, 0.0, 1, False
            sfx("rev")
            save["car"], save["track"] = (car_i if keep is None else keep), trk_i; write_save(save)
        ps = int((D % TL + PLAYZ) // SEG) % N
        cu = CURVE[ps]
        steer = ("right" in held) - ("left" in held)
        boost = False; was_drift, drift = drift, False
        ch = CAMH + (16.0 * math.sin(D * 0.0016) * spd / MAXSPD if st == "race" and jh <= 0.0 and cfg["q"] else 0.0)
        if st in UPD:
            spd = 7000.0; D += spd * dt; px = 0.45 * math.sin(tt * 0.7); steer = 0; jh = jv = 0.0
            UPD[st]()
        elif st == "fly":
            fl += dt; u = min(1.0, fl / FLYT); D = u * TL; px = 0.3 * math.sin(u * 9.0); spd = 9000.0
            ch = CAMH + 1800.0 * (1.0 - u) ** 2; steer = 0; jh = jv = 0.0
            if (mode != "net" and ("A" in pressed or "B" in pressed)) or u >= 1.0: st = "restart"
        elif st == "count":
            spd = 0.0; was_cd = math.floor(cd); cd -= dt
            if math.floor(cd) < was_cd: sfx('go' if cd <= 0 else 'beep')
            if ("A" in pressed or "up" in pressed) and 0.0 < cd < 0.3:
                pbt = 1.0
            if cd <= 0:
                st, t_race = "race", 0.0
                if pbt > 0.0:
                    shake = 0.4
                    sfx('pad')
                    tip[:] = ["PERFECT START!!!", 1.2]
        else:
            if st == "race":
                t_race += dt
                gas = "A" in held or "up" in held
                bkey = "B" in held
                drift = bkey and spd > MAXSPD * (0.45 if was_drift else 0.6) and (was_drift or steer != 0)
                if drift and not was_drift: ddir = float(steer)
                brk = bkey and not drift
                if pad.on: gas = "A" not in held and not brk
                ks = spd / MAXSPD
                if ks > 0.6 and abs(cu) > 3.0 and not drift and t_race > 6.0: tipo(8, "Giữ B + < > để DRIFT")
                if nb <= 0.0 and "C" in pressed and nitro >= 1.0 and spd > MAXSPD * 0.3:
                    nb = 1.0
                    sfx('nitro', chan='n', loops=-1)
                boost = nb > 0.0
                if not boost:
                    sfx_stop('n')
                if drift:
                    tgt = ddir * (1.0 if steer == ddir else (0.35 if steer else 0.65))
                else:
                    tgt = steer * 0.35 if spd > MAXSPD * 0.2 else 0.0
                slip += (tgt - slip) * min(1.0, dt * (6.0 if drift else 5.0))
                cap = vmax
                if boost:
                    cap = vmax * 1.35; gas = True
                    d_ = min(nb, 0.33 * dt); nitro -= d_; nb -= d_
                    if nitro <= 0.0: nitro = nb = 0.0
                n_gain = (0.25 * min(1.0, ks) * (abs(slip) ** 1.2) * (0.25 + min(0.75, abs(cu) / 4.0)) * (0.6 if boost else 1.0)) if drift else 0.0
                if was_drift and not drift and drift_t > 1.0: kick = 0.7; sfx("whoosh")
                nitro = min(2.0, nitro + (n_gain + (0.015 if not boost else 0.0)) * nitm * dt)
                if nitro >= 1.0 > pnit: sfx("star");tipo(4, "Nitro đầy! Bấm C")
                pnit = nitro
                if drift:
                    cap = cap * 0.88
                    spd -= MAXSPD * 0.11 * dt
                if drift:
                   if abs(slip) > 0.6 and abs(cu) > 1.5: drift_t += dt
                else:
                    if was_drift and drift_t > 1.0: kick = 0.7
                    drift_t = 0.0
                if kick > 0.0:
                    kick -= dt; spd += acc * 1.6 * dt; cap = max(cap, vmax * 1.12)
                if pbt > 0.0:
                    spd += acc * 1.6 * dt; cap = max(cap, vmax * (1.0 + 0.3 * min(1.0, pbt * 2.0)))
                if gas: spd += acc * 1.5 * dt
                elif brk: spd -= BRK * dt
                else: spd -= DEC * dt
                if spd > cap: spd = max(cap, spd - (MAXSPD * 0.45 + (acc - ACC) * 1.5 + acc * 1.6 * ((kick > 0.0) + (pbt > 0.0))) * dt)
            else:
                steer = 0; done_t += dt
                px -= px * min(1.0, dt * 2.5); jh = jv = 0.0
                spd -= BRK * 0.5 * dt
            cut = ps in CUTS and 1.15 < px * CUTS[ps] < 2.2
            if abs(px) > 1.0 and spd > OFFLIM and not cut:
                spd -= OFFDEC * dt * (0.4 if tank else 1.0)
            if spd < 0.0: spd = 0.0
            sp = spd / MAXSPD
            if sp > 0.0:
                k = dt * 1.9
                cf = k * sp * sp * cu * 0.18 / grip
                if drift: px += k * sp * 0.5 * slip - cf * 0.6
                else: px += steer * k * grip * grip * (sp if sp > 0.25 else 0.25) - cf
                bridge_limit = 1.0 if ps in BRG else 2.4
                if px > bridge_limit:
                    px = bridge_limit
                    if ps in BRG: spd *= 0.85; shake = max(shake, 0.3); sfx('bump')
                elif px < -bridge_limit:
                    px = -bridge_limit
                    if ps in BRG: spd *= 0.85; shake = max(shake, 0.3); sfx('bump')
            D += spd * dt * (1.5 if cut else 1.0)
            n2 = int((D % TL + PLAYZ) // SEG) % N
            for q in range(ps, ps + (n2 - ps) % N + 1):
                for k, o in SPR[q % N]:
                    if abs(px - o) < HITR[k] + 0.04 and spd > MAXSPD * 0.25 and jh < 10.0:
                        spd = MAXSPD * 0.25; shake = 0.4; sfx('bump'); spark(1 if o >= px else -1, 16)
            if st == "race":
                if jh > 0.0 or jv > 0.0:
                    jv -= 600.0 * dt; jh += jv * dt
                    nitro = min(2.0, nitro + 0.2 * dt)
                    if jh <= 0.0:
                        jh = jv = 0.0; shake = max(shake, 0.15)
                        for xo in (7, 52, 7, 52): puff(130 + int(slip * 7) + xo + rnd.randint(-3, 3), H - 8, PAL[0][0], 1.5)
                elif n2 in RAMPS and spd > MAXSPD * 0.5 and abs(px - RAMPS[n2] * 0.6667) < 0.33:
                    jv = 120.0 + 180.0 * spd / MAXSPD; sfx('whoosh'); tipo(2, "Dốc xanh: bay và nạp nitro!");
                pd_ = jh <= 0.0 and n2 in PADS and abs(px) < 0.45
                if pd_:
                    pbt = 1.0
                    if not onpad: spd = min(spd + MAXSPD * 0.12, vmax * 1.3); shake = max(shake, 0.25); sfx('pad');pf=1.0; tipo(1, "Vạch cam: bứt tốc!")
                onpad = pd_
            if st == "race":
                lp = min(LAPS, int(D // TL) + 1); fin = D >= LAPS * TL
                if lp != lap_prev or fin:
                    lt = t_race - lap_start; lap_start = t_race
                    cross = lp != lap_prev and not fin; lap_prev = lp
                    r = recs.setdefault(str(trk_i), {}); had = "lap" in r
                    isb = mode == "free" and (not had or lt < r["lap"])
                    if isb: r["lap"], r["ld"], r["lc"] = lt, time.strftime("%d/%m/%y"), car_i; newlap = True
                    if cross: lbn = [0.0, lp, lt, isb and had]; sfx('lap')
                if fin:
                    st, done_t = "done", 0.0
                    sfx_stop(); sfx("fin")
                    res = (1 + sum(1 for c in cars if c.dist > D), t_race)
                    if res[0] == 1: sfx("cheer")
                    conf = [[rnd.uniform(0, W), rnd.uniform(-60, 0), rnd.uniform(-18, 18), rnd.uniform(45, 85),
                             RK[res[0] - 1] if rnd.random() < 0.5 else CONF[rnd.randrange(4)]] for _ in range(36)] if res[0] <= 3 else []
                    r = recs.setdefault(str(trk_i), {})
                    h = r.get("hist")
                    if not isinstance(h, list): h = [[r["best"], r.get("bd", "--/--/--"), r.get("bc", 0)]] if "best" in r else []
                    cb = min((e[0] for e in h if e[2] == car_i), default=None)
                    ab = "best" not in r or t_race < r["best"]
                    newrec = mode == "free" and (ab or cb is None or t_race < cb)
                    olds = r.get("best") if ab else cb      
                    if newrec:
                        tset("Bấm C để lưu ảnh khoe")
                        d = time.strftime("%d/%m/%y")
                        h = h + [[t_race, d, car_i]]
                        while len(h) > len(PCAR_DEF):
                            h.pop(next((i for i, e in enumerate(h) if any(f[2] == e[2] for f in h[i + 1:])), 0))                   
                        r["hist"] = h
                        if ab: 
                            r["best"], r["bd"], r["bc"] = t_race, d, car_i
                    if mode == "free":
                        dz_ = max(0, min(2, int(cfg["dif"]))); pg = pts_gain(res[0], dz_, LAPS * TL); p0 = pts; pts += pg; save["pts"] = pts
                        promo = title_of(pts)[0] > title_of(p0)[0]; bn_t = 0.0 if promo else 9.0
                        newleg = title_of(pts)[0] >= 5 and not egg
                        if newleg: egg = True; save["egg"] = 1
                        rkc = save.get("rk")
                        if not (isinstance(rkc, list) and len(rkc) == 3 and all(isinstance(x, list) and len(x) == 5 for x in rkc)): rkc = save["rk"] = [[0] * 5 for _ in range(3)]
                        rkc[dz_][min(res[0], 5) - 1] += 1
                    if mode == "story":
                        c = mc(chap, mi); rk = res[0]; newcar = -1; newtrk = []
                        won = rk <= c[7]
                        a_ = save.setdefault("att", {}).setdefault("%d.%d" % (chap, mi), [0, 0]); a_[0] += 1; a_[1] += won
                        if won:
                            if mi == 2:
                                rw_old = stg.get(str(chap), 0)
                                rw_new = stg[str(chap)] = max(rw_old, 4 - rk)
                            pr0 = prog
                            if chap == prog:
                                if mi < 2: mp = mi + 1
                                else: prog += 1; mp = 0; sv["prog"] = prog
                                sv["mp"] = mp
                            n2 = ncar(prog, sum(stg.values()))
                            newtrk = [TRACKS[i]["name"] for i in range(len(TRACKS)) if pr0 < TNEED[i] <= prog]
                            if n2 > nc: nc = n2; newcar = nc - 1
                    if mode != "net":
                        mgain = mas_add(car_i, t_race, LAPS * TL, (0.9, 1.0, 1.1)[max(0, min(2, cfg["dif"]))] if mode == "free" else 1.0, trk_i)
                    write_save(save)
            else:
                g = net.take_start() if online and not net.is_host else None
                if g: trk_i = g[1]; st = "flyin"; lbn = None
                elif done_t > 1.5:
                    if not seenp and mode != "net" and res[0] <= 3 and (mode != "story" or (won and mi == 2)) and ("A" in pressed or "B" in pressed):
                        seenp = True; pkey = "A" if "A" in pressed else "B"; st = "podium"; pt = 0.0
                        conf = [[rnd.uniform(0, W), rnd.uniform(-60, 0), rnd.uniform(-18, 18), rnd.uniform(45, 85),
                                 RK[0] if rnd.random() < 0.5 else CONF[rnd.randrange(4)]] for _ in range(36)]
                    elif mode == "story":
                        if "A" in pressed:
                            cars = []; allc = [pl]; D = 0.0
                            if won and mi < 2: mi += 1; st = "brief"
                            else:
                                rw_steps = (["star"] + (["car"] if newcar >= 0 else []) + ["talk2"]) if won else ["taunt"]
                                st, rw_i, rw_t = "reward", 0, 0.0
                                if newtrk: tset(T("Mở khóa đường: ") + T(newtrk[0]))
                        elif "B" in pressed: st = "story"; cars = []; allc = [pl]; D = 0.0
                    elif mode == "net":
                        if "B" in pressed: net.leave(); st = "nethome"; cars = []; allc = [pl]; nids = []; D = 0.0
                        elif "A" in pressed and (not net.is_host or net.all_finished(tf)):
                            if net.is_host: net.end_race()
                            else: net.back_to_lobby()
                            st = "netlobby"; cars = []; allc = [pl]; nids = []; D = 0.0; lbn = None
                    elif "A" in pressed: st = "track"; cars = []; allc = [pl]; D = 0.0; stop_bgm()
                    elif "B" in pressed: st = "car"; cars = []; allc = [pl]; D = 0.0; stop_bgm()
        if st != "race": slip -= slip * min(1.0, dt * 5.0)
        pl.z = (D % TL) + PLAYZ
        if pl.z >= TL: pl.z -= TL
        pl.x, pl.spd = px, spd
        if online:
            net_sync(net, cars, nids, ft, tf, dt)
            if st != "restart":
                net.send_state(tf, D, px, spd, slip, (1 if boost else 0) | (2 if drift else 0) | (4 if st == "done" else 0),
                               res[1] if st == "done" else 0.0)
        else:
            update_cars(cars, allc, pl, D, dt, st != "count")
            if mode == "story" and st == "race" and rv:
                if chap >= 4 and mi == 2 and 0 < (LAPS * TL - rv.dist) < 50000.0:
                    rv.spd = max(rv.spd, MAXSPD * 1.1)
                    if not spw: spw = True; tipo(16,"Boss nước rút! Xả Nitro!"); sfx("whoosh")
                    if rnd.random() < 0.5:
                        boss_x = W // 2 + int((rv.x - px) * 160)
                        puff(boss_x + rnd.randint(-15, 15), H - 55, (255, 80, 20), 2.5)
        if st in ("race", "done") and not online:
            tn = t_race + (done_t if st == "done" else 0.0)
            for i, c in enumerate(cars):
                if i not in ft and c.dist >= LAPS * TL: ft[i] = tn
        if st == "race" and not online:
            for c in cars:
                dz = (c.z - pl.z) % TL
                if dz > TL * 0.5: dz -= TL
                if -20.0 - spd * dt < dz < 160.0 + spd * dt and jh < 10.0:
                    dist_x = abs(c.x - px)
                    if dist_x < 0.22:
                        if spd > c.spd * 0.9:
                            v = (spd + c.spd) * 0.5; c.spd = v * 1.1; spd = v * (0.98 if tank else 0.9)
                            c.x += (0.5 if c.x >= px else -0.5) if tank else (0.3 if c.x >= px else -0.3)
                        shake = 0.3; px += 0.05 if px >= c.x else -0.05; sfx('bump'); spark(1 if c.x >= px else -1, 10)
                    elif dist_x < 0.38 and spd > MAXSPD * 0.75:
                        if c not in nm_cars:
                            nm_cars.add(c)
                            nitro = min(2.0, nitro + 0.3)
                            sfx('star')
                            tip[:] = ["LÁCH SÁT! +NITRO", 1.0]
                            pf = max(pf, 0.4)
                elif c in nm_cars and (dz < -100 or dz > 1000):
                    nm_cars.remove(c)
        inr = st in ("count", "race")
        pad.lab = inr
        pad.st["B"] = 1 if st == "race" and spd > MAXSPD * (0.45 if was_drift else 0.6) else 0
        pad.st["C"] = -1 if inr and not (nitro >= 1.0 and nb <= 0.0) else 0
        if shake > 0.0: shake -= dt
        bgm = 1.0 + 0.6 * abs(slip)
        bg1 += cu * (spd / MAXSPD) * dt * 15.0 * bgm
        bg2 += cu * (spd / MAXSPD) * dt * 36.0 * bgm
        engine(spd / MAXSPD if st in ("count", "race") else None)
        global CAMD
        pbt = max(0.0, pbt - dt)
        CAMD += ((0.55 if boost else 1.0 - 0.3 * min(1.0, pbt * 2.0)) - CAMD) * min(1.0, dt * 6.0)
        t1 = pc(); tm[0] += ((t1 - tf) * 1000 - tm[0]) * 0.1
        far_idx = int(ps + dr * 0.75) % N
        camy_approx = ch + TRK["y"][ps]
        far_y_diff = camy_approx - TRK["y"][far_idx]
        far_z = max(1, int(dr * 0.75) * SEG)
        target_pitch = (CAMD / far_z) * far_y_diff * VS
        target_pitch = max(-60, min(60, target_pitch))
        sm_pitch += (target_pitch - sm_pitch) * min(1.0, dt * 5.0)
        pitch_y = int(sm_pitch)
        if pitch_y > 0:
            scr.fill(SKY.get_at((0, 0)), (0, 0, W, pitch_y))
        scr.blit(SKY, (0, pitch_y))
        th_idx = TRK["theme"]; sunv = False
        if cfg["q"]:
            big, g1, g2 = TRK["fl"]; sx0, sy0 = THEMES[th_idx]["sunpos"]; ADD = pygame.BLEND_RGB_ADD
            scr.blit(big, (sx0 - 44, sy0 - 44 + pitch_y), special_flags=ADD)
            if boost: scr.blit(big, (sx0 - 44, sy0 - 44 + pitch_y), special_flags=ADD)
            y1, y2 = sy0 - HZ + 46, sy0 - HZ + 24
            sunv = ((y1 < 0 or MT1.get_at(((sx0 + int(bg1)) % 640, y1))[:3] == KEY)
                    and (y2 < 0 or MT2.get_at(((sx0 + int(bg2)) % 640, y2))[:3] == KEY))
        o = int(bg1 * 0.25) % 640; scr.blit(CLD, (-o, 8 + pitch_y)); scr.blit(CLD, (640 - o, 8 + pitch_y))
        o = int(bg1) % 640; scr.blit(MT1, (-o, HZ - 46 + pitch_y)); scr.blit(MT1, (640 - o, HZ - 46 + pitch_y))
        o = int(bg2) % 640; scr.blit(MT2, (-o, HZ - 24 + pitch_y)); scr.blit(MT2, (640 - o, HZ - 24 + pitch_y))
        if cfg["q"]: scr.blit(haze(), (0, HZ - 24 + pitch_y))
        fill_h = max(0, H - (HZ + pitch_y))
        if fill_h > 0: scr.fill(FOG, (0, HZ + pitch_y, W, fill_h))
        render(scr, D, px, cars, dr,drmax, cols, ch)
        t2 = pc(); tm[1] += ((t2 - t1) * 1000 - tm[1]) * 0.1
        if cfg["q"]:
            if sunv and not THEMES[th_idx].get("stars"):
                for f, g in ((0.5, g1), (1.4, g2), (1.9, g1)):
                    r_ = g.get_width() >> 1
                    scr.blit(g, (sx0 + (HW - sx0) * f - r_, sy0 + (VS - sy0) * f - r_), special_flags=ADD)
            wx = TRK["wx"]
            if wx and spd > 0 and ps not in TUN:
                snow = th_idx == 2; v = (150 if snow else 700) * (1.0 + spd / MAXSPD * 0.5)
                ox = int(8 * math.sin(tt) - px * 6)
                for k_, im in enumerate(wx):
                    oy = int(tt * v * (1.0 + k_ * 0.6)) % H
                    scr.blit(im, (ox, oy - H)); scr.blit(im, (ox, oy))
        if st in ("race", "done") and spd > MAXSPD * 0.2 and cfg["q"] == 2 and dr >= drmax - 4:
            tilt = -slip * 6.0 * (spd / MAXSPD)
            if abs(tilt) >2.0:
                rot = pygame.transform.rotozoom(scr, tilt, 1.0 + abs(tilt) * 0.03)
                scr.blit(rot, rot.get_rect(center=(W // 2, H // 2)))
        nlift += ((7.0 if boost else (4.0 * min(1.0, pbt * 2.0))) - nlift) * min(1.0, dt * 10.0)
        cam_offset = (CAMH - ch) * (CAMD / PLAYZ) * VS
        sy = int(H - 44 - nlift - cam_offset) + (rnd.randint(-1, 1) if shake > 0.0 else 0)
        gy = sy + 34 + int(nlift)
        if jh > 0.0: sy -= int(jh)
        yi = int(round(slip * 3.0)); yi = -3 if yi < -3 else (3 if yi > 3 else yi)
        sx = 130 + int(slip * 7.0)
        if st != "fly":
            u = min(1.0, jh / 60.0 + nlift * 0.03)
            dynamic_w = int((54 - 26 * u) * (1.0 + abs(slip) * 0.45)) & -4
            s_ = shadow(max(4, dynamic_w), max(0, 160 - int(100 * u)) & -32)
            car_sprite = PCARS[car_i][yi + 3]
            if st in ("race", "done") and spd > MAXSPD * 0.2:
                car_tilt = -slip * 6.0 * (spd / MAXSPD)
                if abs(car_tilt) > 2.0:
                    car_sprite = pygame.transform.rotate(car_sprite, car_tilt)
            scr.blit(s_, (sx + 30 + int(slip * 3 + SUNX * (6 + 10 * u)) - (s_.get_width() >> 1), gy + 2 - (s_.get_height() >> 1)))
            scr.blit(car_sprite, (sx + 30 - (car_sprite.get_width() >> 1), sy + 38 - car_sprite.get_height()))
        if boost or pbt > 0.15:
            for _ in range(12 if boost else int(12 * pbt)):
                lx, ly = rnd.randint(0, W), rnd.randint(0, H)
                if abs(lx - HW) < 50 and ly > HZ - 20: continue
                line(scr, (210, 240, 255), (lx, ly), (lx + (lx - HW) * 0.5, ly + (ly - HZ) * 0.5), 1)
        if pf > 0.0: flash(scr, int(pf * 80)); pf -= dt * 5
        if drift and abs(slip) > 0.15:
            for wx2 in (sx + 9, sx + 51):
                if len(skid) < 40: skid.append([wx2 + rnd.randint(-1, 1), sy + 35, 0.0])
            sfx('drift', 'd', -1)
            if drift_t < 0.4:   lv, msg, mcol = 0, "DRIFT!", (200, 200, 200)
            elif drift_t < 1.0: lv, msg, mcol = 1, "GOOD DRIFT!", (255, 220, 90)
            elif drift_t < 2.0: lv, msg, mcol = 2, "GREAT DRIFT!", (255, 120, 40)
            else:               lv, msg, mcol = 3, "MASTER DRIFT!!!", C_CYAN
            ctag(scr, msg, 62 - hoff_top, mcol, rnd.randint(-2, 2) if lv > 1 else 0)
            n_ = 1 + lv * 2 + int(abs(slip) * 2 * (spd / MAXSPD) / max(0.6, grip))
            smoke = (200, 200, 208) if lv == 0 else ((225, 225, 232) if lv == 1 else (250, 235, 215))
            for _ in range(n_):
                wx_ = sx + (rnd.randint(2, 12) if rnd.random() < 0.5 else rnd.randint(46, 58))
                puff(wx_, sy + 36, smoke, 1.0 + 0.5 * lv + abs(slip))
                if lv and rnd.random() < 0.4 + 0.2 * lv:
                    z_ = rnd.randint(2, 3 + lv)
                    sp_col = ((255, 220, 90), (255, 120, 40), C_CYAN)[lv - 1]
                    r_col = (sp_col[0], max(0, sp_col[1] - rnd.randint(0, 40)), sp_col[2])
                    rect(scr, r_col, (wx_, sy + 33 + rnd.randint(0, 6), z_, z_))
        else: sfx_stop('d')
        if st == "race" and jh <= 0.0:
            q_ = (ps - 1) % N
            if abs(px) > 1.0 and spd > OFFLIM and not cut: MARKS[q_] = (px, 1)
        if abs(px) > 1.0 and spd > OFFLIM and not cut and st == "race" and rnd.random() < 0.6:
            puff(sx + rnd.choice((6, 52)), sy + 36, PAL[0][0], 1.5)
        if parts:
            nx_ = []
            for p in parts:
                p[4] += dt
                if p[4] >= 0.6: continue
                p[2] -= p[2] * dt * 4.0
                wind = (spd / MAXSPD) * 100.0
                p[3] += (wind - 60.0 - p[3]) * dt * 3.5
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                f = p[4] / 0.6; c = p[5]
                r = int(1 + f * 10)
                col = (int(c[0] + (FOG[0] - c[0]) * f), int(c[1] + (FOG[1] - c[1]) * f), int(c[2] + (FOG[2] - c[2]) * f))
                sp = soft_particle(r, col)
                scr.blit(sp, (int(p[0]) - r, int(p[1]) - r))
                nx_.append(p)
            parts[:] = nx_
        if skid:
            nx_ = []
            for p in skid:
                p[2] += dt; p[1] += (60 + spd / MAXSPD * 120) * dt
                if p[2] >= 0.5 or p[1] > H: continue
                c_ = int(40 + 90 * p[2] / 0.5)
                rect(scr, (c_, c_, c_ + 4), (int(p[0]) - 2, int(p[1]), 4, 5)); nx_.append(p)
            skid[:] = nx_
        if cfg["q"] and st in ("count", "race", "done") and (th_idx == 3 or ps in TUN):
            scr.blit(beam(), (sx + 30 - 65, sy + 12 - 74), special_flags=pygame.BLEND_RGB_ADD)
        if (boost or pbt > 0.15) and st != "fly":
            L = 34.0 if boost else 10.0 + 24.0 * pbt
            fc = ((50, 130, 255), (130, 220, 255), (255, 255, 255)) if boost else ((255, 80, 20), (255, 190, 50), (255, 250, 210))
            for nx in (sx + 21, sx + 39):
                l = L * rnd.uniform(0.7, 1.1) + 4
                for k in range(3):
                    w = 5 - k * 2; e = sy + 38 + l * (1.0 - k * 0.3)
                    pygame.draw.polygon(scr, fc[k], ((nx - w, sy + 38), (nx + w, sy + 38), (nx + rnd.uniform(-1.5, 1.5) - slip * 3, e)))
        if sks:
            nx_ = []
            for p in sks:
                p[4] += dt
                if p[4] >= 0.35: continue
                p[3] += 420.0 * dt; p[0] += p[2] * dt; p[1] += p[3] * dt; f = p[4] / 0.35
                line(scr, (255, 235 - int(f * 130), 120 - int(f * 100)), (int(p[0]), int(p[1])), (int(p[0] - p[2] * 0.04), int(p[1] - p[3] * 0.04)), 2 if f < 0.5 else 1)
                nx_.append(p)
            sks[:] = nx_
        if st in ("count", "race", "done"):
            hoff_top = int(min(1.0, done_t / 0.5) * 40) if st == "done" else 0
            hoff_bot = int(min(1.0, done_t / 0.5) * 50) if st == "done" else 0
            rank = 1 + sum(1 for c in cars if c.dist > D)
            lap = min(LAPS, int(D // TL) + 1)
            hud_top(scr, hoff_top, rank, len(cars) + 1, lap, LAPS, t_race, tt, st == "race" and LAPS > 1 and lap == LAPS, st != "done")
            if rv:
                g = int((D - rv.dist) / 500.0) * 5
                chip(scr, 8 + txt(T("VÒNG %d/%d") % (lap, LAPS)).get_width(), 21 - hoff_top, "%s %+dm" % (T(STORY[chap][3]), g), (120, 255, 120) if g >= 0 else (255, 120, 110))
                ok_ = rank <= gt[0]
                chip(scr, 4, 38 - hoff_top, T("TOP 3 · %d SAO") % max(0, 4 - rank) if gt[1] else (T("VỀ NHẤT") if gt[0] == 1 else T("VỀ TOP %d") % gt[0]), (120, 255, 120) if ok_ else (255, 120, 110))
                if st == "count": ctag(scr, gt[2], 100, (120, 255, 120))
            hud_speed(scr, W - 35, H - 30 + hoff_bot, spd / MAXSPD, boost, tt)
            hud_nitro(scr, 8, H - 30 + hoff_bot, nitro, boost, tt)
            mx, my = W - MMW - 3, 19 - hoff_top+3
            ML = TRK["mlp"]; q = MMSTEP * SEG; m = len(ML) - 1
            def mpos(z):
                f = z / q; i = int(f) % m; k = f - int(f); A = ML[i]; B = ML[(i + 1) % m]
                return A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k
            p = mpos(pl.z); p2 = mpos(pl.z + 3 * q)
            at = 90 - math.degrees(math.atan2(p[1] - p2[1], p2[0] - p[0]))
            if mang is None: mang = at
            else: mang += ((at - mang + 180) % 360 - 180) * min(1.0, dt * 6.0)
            ang = int(mang) // 6 * 6 % 360
            r_ = MM_CACHE.get((trk_i, ang))
            if r_ is None:
                r_ = MM_CACHE[(trk_i, ang)] = pygame.transform.rotate(TRK["mlk"], ang)
            rad = ang * 0.0174532925
            ca, sa = math.cos(rad), math.sin(rad)
            tx, ty = mx + MMW // 2, my + int(MMH * 0.65)
            def mmw(u, v): u -= p[0]; v -= p[1]; return tx + u * ca + v * sa, ty - u * sa + v * ca
            ix, iy = mmw(MMW, MMH)
            scr.blit(_pn(MMW, MMH, 150), (mx, my)); scr.set_clip((mx, my, MMW, MMH))
            scr.blit(r_, (int(ix - r_.get_width() / 2), int(iy - r_.get_height() / 2)))
            for c in cars:
                u, v = mmw(*mpos(c.z))
                if mx < u < mx + MMW and my < v < my + MMH:
                    if c is rv: rect(scr, (255, 255, 255), (int(u) - 2, int(v) - 2, 5, 5))
                    rect(scr, c.col, (int(u) - 1, int(v) - 1, 3, 3))
            scr.set_clip(None)
            rect(scr, (255, 255, 255), (tx - 2, ty - 2, 5, 5)); rect(scr, (230, 30, 45), (tx - 1, ty - 1, 3, 3))
            rect(scr, (110, 115, 140), (mx - 1, my - 1, MMW + 2, MMH + 2), 1)
        if lbn and st == "race":
            lbn[0] += dt
            if not draw_lap(scr, lbn, LAPS, tt): lbn = None
        _dw = DRAW.get(st)
        if _dw: _dw()
        elif st in ("count", "race") and (st == "count" or t_race < 0.9):
            msg = str(int(math.ceil(cd))) if st == "count" else "GO!"
            col = (255, 230, 90) if st == "count" else (120, 255, 120)
            frac = cd % 1.0 if st == "count" else (1.0 - t_race / 0.9)
            scale = 1.0 + (frac**3) * 1.5
            s = txt(msg, col, 1)
            if scale > 1.02: s = pygame.transform.rotozoom(s, 0, scale)
            scr.blit(s, (HW - s.get_width()//2, HZ - 10 - s.get_height()//2))
        elif st == "done" and done_t < 1.3:
            draw_finish(scr, done_t, "KỶ LỤC MỚI!" if newrec else "VỀ ĐÍCH!", T("HẠNG %d/%d") % (res[0], len(cars) + 1), RK[0] if newrec else (RK[res[0] - 1] if res[0] <= 3 else (255, 255, 255)))
        elif st == "done":
            tn = t_race + done_t; gend = LAPS * TL
            rows = [(pname or "BẠN", PCAR_DEF[car_i][1], res[1], True, True)]
            kk = {}
            for i, c in enumerate(cars):
                nm = T(STORY[chap][3]) if c is rv else (net.name_of(nids[i]) if online else NAMES[i])
                kk[nm] = c.key
                rows.append((nm, c.col, ft[i], True, False) if i in ft else (nm, c.col, tn + (gend - c.dist) / max(c.spd, 500.0), False, False))
            rows.sort(key=lambda x: x[2])
            AN = (6, 3, 9)
            pod[:] = [(r[0], PREVS[car_i][AN[i]] if r[4] else front(int(kk[r[0]][1:]), AN[i] * 22.5), r[2], r[4]) for i, r in enumerate(rows[:3])]
            r = recs.get(str(trk_i), {})
            rec_txt = None
            if mode == "story":
                ttl = "THẮNG!" if won else "CHƯA ĐẠT"
                if won and newcar >= 0: info, ic = T("Mở khóa xe: ") + T(PCAR_DEF[newcar][0]), (255, 205, 60)
                elif won and newtrk: info, ic = T("Mở khóa đường: ") + T(newtrk[0]), (120, 255, 120)
                elif won and chap == len(STORY) - 1 and mi == 2: info, ic = "VÔ ĐỊCH GIẢI ĐẤU!", (255, 205, 60)
                else: info, ic = goal(mc(chap, mi)), ((120, 255, 120) if won else (255, 120, 110))
                ha = "Nhận sao" if won and mi == 2 else "Tiếp"; hb = "Danh sách"
            elif mode == "net":
                ttl = "XẾP HẠNG"; hb = "Rời phòng"; info, ic = T("Đua mạng LAN · %d người") % (len(cars) + 1), (180, 230, 255)
                ha = "Phòng chờ" if (not net.is_host or net.all_finished(tf)) else "Chờ mọi người..."
            else:
                ttl = "XẾP HẠNG"; ha, hb = "Chọn đường", "Đổi xe"
                if newrec: rec_txt = T("KỶ LỤC") + (" -%.1fs" % (olds - res[1]) if olds else "")
                if newlap: info, ic = T("VÒNG NHANH MỚI: ") + fmt(r["lap"]), (255, 205, 60)
                else: info, ic = T("Kỷ lục: ") + (fmt(r["best"]) if "best" in r else "--:--.-"), (180, 230, 255)
                ln_ = [(info, ic), (T("+%d điểm · ") % pg + title_txt(pts), (180, 255, 180))]
                if promo: ln_.insert(0, (T("THĂNG HẠNG: ") + T(TITLES[title_of(pts)[0]][1]) + "!", (255, 205, 60)))
                if newleg: ln_.insert(0, (T("Mở khóa xe: ") + T(PCAR_DEF[7][0]), (255, 205, 60)))
                ln_.append((mas_txt(car_i, mgain), (255, 205, 120)))
                info, ic = ln_[int(max(0.0, done_t - 2.0) / 2.5) % len(ln_)]
            draw_rank(scr, rows, ttl, info, ic, ha if done_t > 2.6 else None, hb, done_t - 1.3, pts_gain=pg if mode == "free" else 0, xp_gain=0 if mode == "net" else mgain, rec=rec_txt)
            if bn_t < 1.7 and done_t > 2.0:
                if bn_t == 0.0: sfx("star")
                banner_rank(scr, title_of(pts)[0], bn_t); bn_t += dt
        if shot:
            shot = False; sd = os.path.join(HERE, "shots"); fn = os.path.join(sd, "card_%s.png" % time.strftime("%Y%m%d_%H%M%S"))
            try:
                os.makedirs(sd, exist_ok=True)
                pygame.image.save(pygame.transform.scale(scr, (W * 5, H * 5)), fn)
                tset(T("Đã lưu: ") + "shots/" + os.path.basename(fn));
            except Exception as ex: tset(T("Lỗi lưu: ") + type(ex).__name__)
        if dbg and tf - ram_t > 1.0: ram_t = tf; ram = ram_mb()
        if dbg:
            if not hasattr(main, "dbg_surf") or tf - getattr(main, "dbg_t", 0) > 0.25:
                main.dbg_t = tf
                ds = pygame.Surface((206, 6 * 12 + 4), pygame.SRCALPHA)
                ds.blit(_pn(206, 6 * 12 + 4, 200), (0, 0))
                G, Y, R, Wh = (120, 255, 120), (255, 220, 70), (255, 90, 80), (255, 255, 255)
                def lv(v, a, b): return G if v < a else (Y if v < b else R)
                f = clock.get_fps(); pm = int(ptime); nprt = len(parts) + len(skid) + len(sks)
                rows = (
                    (("FPS %d" % f, lv(-f, -55, -40)), ("worst %.0f" % ft_max, lv(ft_max, 22, 40)), ("dr %d/%d" % (dr, drmax), G if dr >= drmax else Y)),
                    (("upd %.1f" % tm[0], lv(tm[0], 3, 6)), ("road %.1f" % tm[1], lv(tm[1], 8, 12)),
                    ("hud %.1f" % tm[2], lv(tm[2], 3, 5)), ("pres %.1f" % tm[3], lv(tm[3], 4, 7))),
                    (("vis %d" % getattr(render, "nv", -1), Wh), ("seg %d/%d" % (ps, N), Wh), ("sum %.1fms" % sum(tm), lv(sum(tm), 15, 20))),
                    (("spr %d" % len(_sc), lv(len(_sc), 500, 1000)), ("txt %d" % len(S._tc), lv(len(S._tc), 350, 480)), ("dg %d" % len(S._dg), Wh),("shd %d" % len(S._sh), lv(len(S._sh), 40, 100))),
                    (("part %d" % nprt, lv(nprt, 30, 50)), (st, Wh), ("spd %d" % spd, Wh)),
                    (("play %d:%02d:%02d" % (pm // 3600, pm // 60 % 60, pm % 60), C_DIM),
                     ("RAM %d MB" % ram, lv(ram, 150, 250))),
                )
                for i, r in enumerate(rows):
                    x = 3
                    for s_, c_ in r:
                        t_ = S.FONT.render(s_, True, c_); ds.blit(t_, (x, 1 + i * 12)); x += t_.get_width() + 8
                main.dbg_surf = ds
            scr.blit(main.dbg_surf, (0, 0))
        if aq and toast[1] <= tf and (st != "done" or done_t > 2.6): tset(aq.pop(0)); sfx("star")
        if tip[1] > 0.0: tip[1] -= dt; ctag(scr, T(tip[0]), 40 - hoff_top, C_CYAN)
        if toast[1] > tf:
            scr.blit(_pn(W, 16, 215), (0, 130)); ctext(scr, toast[0], 131, (255, 190, 90))
        if conf and st in ("done", "podium", "reward", "gift") and dr >= 40:
            for p in conf:
                p[0] += (p[2] + 14 * math.sin(tt * 3 + p[3])) * dt; p[1] += p[3] * dt
                if p[1] >= H and (done_t < 5.0 or st != "done"): p[1] = -4.0
                elif p[1] < H: star(scr, int(p[0]), int(p[1]), 3 + ((int(p[1]) >> 3) & 1), p[4], p[0] * 0.1 + tt * 3)
        if st == "flyin":
            load_track(trk_i); cols = build_cols(dr); cars = []; allc = [pl]; fl = 0.0; st = "fly"
            play_bgm('race')
        if st in ("restart", "flyin"): scr.blit(prev, (0, 0))
        else:
            if st != pst:
                if (pst, st) not in QUIET:
                    trn = [0.0, 0.55 if st == "count" else 0.4, prev.copy(), scr.copy(), st == "count" or pst in ("race", "done")]
                    transition(scr, trn, ov)
                pst = st
            prev.blit(scr, (0, 0))
        t3 = pc(); tm[2] += ((t3 - t2) * 1000 - tm[2]) * 0.1
        if st == "race" and (boost or spd > MAXSPD * 0.85):
            vig_alpha = int(180 + 75 * math.sin(tt * 25)) if boost else 120
            S.VIGNETTE_SURF.set_alpha(vig_alpha)
            scr.blit(S.VIGNETTE_SURF, (0, 0))
        rec.tick()
        rec.draw()
        pad.present()
        t4 = pc(); tm[3] += ((t4 - t3) * 1000 - tm[3]) * 0.1
        ft_max = max(ft_max * 0.97, (t4 - tf) * 1000)
        fps_t += dt
        if fps_t >= 1.0:
            fps_t = 0.0; f = clock.get_fps()
            if f < 46 and dr > 28: dr -= 6; cols = build_cols(dr); good = 0
            elif f > 57:
                good += 1
                if good >= 8 and dr < drmax: dr += 4; cols = build_cols(dr); good = 0
            else: good = 0
    write_save(save)
    pygame.quit()
if __name__ == "__main__":
    asyncio.run(main())