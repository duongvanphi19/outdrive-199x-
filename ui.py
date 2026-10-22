import math, time, pygame
try: import netplay
except Exception: netplay = None
from data import *
from lang import T
import sprites as S
from sprites import txt, BASES, PREVS, scaled, front, shadow
_pc = {}
C_DIM, C_OFF = (175, 185, 215), (135, 140, 170)
_an = {}
def since(name, key=0):
    now = time.perf_counter(); v = _an.get(name)
    if v is None or v[0] != key or now - v[2] > 0.15: v = _an[name] = [key, now, now]
    v[2] = now
    return now - v[1]
def fmt(t):
    return "%02d:%04.1f" % (int(t // 60), t % 60)
VER_HIT = (0, H - 18, 60, H)
def _pn(w, h, a=165):
    k = (w, h, a); p = _pc.get(k)
    if p is None:
        p = pygame.Surface((w, h), pygame.SRCALPHA); p.fill((6, 8, 22, a)); _pc[k] = p
    return p
def ctext(scr, s, y, col=(255, 255, 255), big=0):
    t = txt(s, col, big); scr.blit(t, ((W - t.get_width()) // 2, y))
def arrows(scr, y, tt):
    o = int(2.5 * math.sin(tt * 7.0)); c = (255, 220, 70)
    pygame.draw.polygon(scr, c, ((12 + o, y), (24 + o, y - 9), (24 + o, y + 9)))
    pygame.draw.polygon(scr, c, ((W - 12 - o, y), (W - 24 - o, y - 9), (W - 24 - o, y + 9)))
def stars(scr, x, y, n):
    for i in range(5):
        c = (255, 215, 0) if i < n else (40, 42, 56)
        ox = x + i * 12
        pygame.draw.polygon(scr, c, [(ox + 4, y), (ox + 12, y), (ox + 8, y + 8), (ox, y + 8)])
def draw_ver(scr):
    scr.blit(txt(VSTR, C_DIM), (4, H - 16))
def _t_sky(y):
    f = min(1.0, y / 112.0) ** 1.6
    return (int(14 + 241 * f), int(0 + 95 * f), int(50 + 60 * f))
def _t_logo(txt_, big_scale=2):
    a = pygame.transform.scale(S.BIG.render(txt_, True, (255, 255, 255)), (S.BIG.size(txt_)[0] * big_scale, S.BIG.get_height() * big_scale))
    w, h = a.get_size(); t = a.copy(); dk = a.copy(); dk.fill((150, 12, 90), special_flags=pygame.BLEND_RGB_MULT)
    for y in range(h):
        f = y / h
        col = (int(255 - 135 * f * 2), int(255 - 15 * f * 2), 255) if f < 0.5 else (255, int(110 - 60 * (f - 0.5) * 2), int(180 - 40 * (f - 0.5) * 2))
        t.fill(col, (0, y, w, 1), pygame.BLEND_RGB_MULT)
    out = pygame.Surface((w + h // 3 + 8, h + 8), pygame.SRCALPHA)
    for img, ox, oy in [(dk, k, k) for k in (4, 3, 2, 1)] + [(t, 0, 0)]:
        for y in range(h): out.blit(img, (ox + (h - y) // 3, oy + y), (0, y, w, 1))
    return out
def _t_bg():
    s = pygame.Surface((W, H)).convert(); d = pygame.draw; HZt = 112
    for y in range(0, HZt, 2): s.fill(_t_sky(y), (0, y, W, 2))
    for i in range(36): s.set_at(((i * 97 + 13) % W, (i * 53) % 70), (230, 220, 255))
    for y in range(-44, 45):
        yy = 88 + y
        if yy >= HZt: break
        hw = int((44 * 44 - y * y) ** 0.5); f = (y + 44) / 88.0
        d.line(s, (255, int(235 - 195 * f), int(90 + 50 * f)), (160 - hw, yy), (160 + hw, yy))
    for k in range(6):
        y0 = 80 + k * 6; s.fill(_t_sky(y0), (110, y0, 100, 1 + k // 2))
    d.polygon(s, (28, 0, 56), [(0, HZt), (0, 96), (30, 84), (54, 100), (84, 80), (112, HZt)])
    d.polygon(s, (28, 0, 56), [(W, HZt), (W, 92), (284, 78), (254, 98), (226, 84), (200, HZt)])
    s.fill((16, 0, 38), (0, HZt, W, H - HZt)); d.line(s, C_PINK, (0, HZt), (W, HZt)); d.line(s, C_CYAN, (0, HZt + 1), (W, HZt + 1))
    for i in range(-9, 10): d.line(s, (120, 30, 170), (160 + i * 7, HZt), (160 + i * 46, H))
    return s
def draw_title(scr, tt):
    el = since("title"); d = pygame.draw; HZt = 112
    bg = _lk.get("tb")
    if bg is None:
        bg = _lk["tb"] = _t_bg(); c = S.PCARS[0][3]
        _lk["t2"] = pygame.transform.scale(c, (c.get_width() * 2, c.get_height() * 2))
    scr.blit(bg, (0, 0))
    for i in range(8):
        ph = (tt * 0.6 + i / 8.0) % 1.0; y = int(HZt + ph * ph * (H - HZt))
        d.line(scr, (255, 60, 170) if ph > 0.5 else (170, 40, 200), (0, y), (W, y), 2 if ph > 0.7 else 1)
    car = _lk["t2"]; cw = car.get_width()
    scr.blit(shadow(cw - 8, 150), (HW - (cw - 8) // 2, 154))
    scr.blit(car, (HW - cw // 2, 158 - car.get_height() + int(math.sin(tt * 9))))
    scr.blit(_pn(W, 140, 120), (0, 22))
    d.line(scr, C_PINK, (0, 22), (W, 22)); d.line(scr, C_CYAN, (0, 161), (W, 161))
    u = min(1.0, el / 0.8); u = 1.0 - (1.0 - u) ** 3
    draw_logo(scr, "OUTDRIVE 199X", 28 - int(90 * (1.0 - u)), tt)
    for i in range(25):
        if abs(i - 12) * 8 > max(0.0, el - 0.6) * 400: continue
        for r in range(2): d.rect(scr, (240, 240, 240) if (i + r) & 1 else (30, 30, 36), (60 + i * 8, 62 + r * 4, 8, 4))
    if 0.8 < el < 1.05: flash(scr, int(150 * (1.05 - el) / 0.25))
    if el > 1.4 and int(tt * 2) & 1: ctext(scr, "NHẤN A ĐỂ BẮT ĐẦU", 78, (255, 235, 120))
    draw_ver(scr)
def talk(scr, c, ci, title, rival, text, el, foot, fcol, hint, sw, ax=0, bx=0, ay=0):
    panel(scr, 10, 6, 300, 180, title)
    pn, pcol = T(PCAR_DEF[ci][0]), PCAR_DEF[ci][1]; opp = c[3].upper(); trk = TRACKS[c[1]]
    p = PREVS[ci][8]; scr.blit(p, (70 + ax - p.get_width() // 2, max(27, 72 - p.get_height()) + ay))
    o = front(c[4] % len(CAR_COLS), 240)
    scr.blit(o, (250 + bx - o.get_width() // 2, max(27, 72 - o.get_height()) + ay))
    mms = trk["mms"]
    mw, mh = mms.get_size()
    mx, my = HW - mw // 2, 54 - mh // 2
    scr.blit(mms, (mx, my))
    pygame.draw.rect(scr, (70, 60, 140), (mx - 1, my - 1, mw + 2, mh + 2), 1,1)
    t1 = txt("%s" % pn if sw else pn, lite(pcol)); scr.blit(t1, (70 - t1.get_width() // 2, 75))
    t2 = txt(opp, (255, 90, 90)); scr.blit(t2, (250 - t2.get_width() // 2, 75))
    ctext(scr, trk["name"], 72, C_DIM); ctext(scr, T("%d vòng") % c[2], 85, C_DIM)
    card(scr, 20, 102, 280, 42)
    tag = txt(opp if rival else "BAN TỔ CHỨC"); tw = tag.get_width() + 10
    pygame.draw.polygon(scr, (200, 30, 120) if rival else (160, 110, 20), ((22, 95), (28 + tw, 95), (22 + tw, 109), (20, 109)))
    scr.blit(tag, (25, 94))
    cnt = int(el * 50); words, lines, cur = T(text).split(" "), [], ""
    for w in words:
        if len(cur + " " + w) < 36: cur += (" " + w) if cur else w
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    for i, l in enumerate(lines[:2]):
        seg = l[:max(0, cnt)]; cnt -= len(l)
        if seg: scr.blit(S.FONT.render(seg, True, (230, 235, 245)), (28, 112 + i * 14))
    scr.blit(txt(foot, fcol), (24, 148))
    hints(scr, 168, hint)
def banner(scr, n, name, el):
    o = -W * (1.0 - el / 0.3) ** 2 if el < 0.3 else (W * ((el - 1.4) / 0.3) ** 2 if el > 1.4 else 0.0)
    o = int(o); pygame.draw.rect(scr, (12, 10, 30), (o, 74, W, 44))
    pygame.draw.rect(scr, C_PINK, (o, 74, W, 1)); pygame.draw.rect(scr, C_PINK, (o, 116, W, 1))
    a = txt(T("CHƯƠNG %d") % (n + 1), C_AMB, 1); b = txt(name.upper(), (255, 255, 255), 0)
    scr.blit(a, ((W - a.get_width()) // 2 + o, 79)); scr.blit(b, ((W - b.get_width()) // 2 + o - o // 3, 100))
def draw_brief(scr, c, n, ci, tt, dlg_step):
    key = (n, dlg_step); now = time.perf_counter()
    if getattr(draw_brief, "k", None) != key: draw_brief.k = key; draw_brief.t0 = now
    talk(scr, c, ci, T("CHƯƠNG %d: %s") % (n + 1, c[0]), dlg_step == 1, c[10] if dlg_step == 1 else c[9], now - draw_brief.t0 - (1.2 if dlg_step == 0 else 0.0),
         goal(c), (120, 255, 120), (("< >", "Xe"), ("A", "Tiếp" if dlg_step == 0 else "Đua"), ("B", "Quay lại")), True)
    if dlg_step == 0 and now - draw_brief.t0 < 1.7: banner(scr, n, c[0], now - draw_brief.t0)
VS_T, VS_H = 1.3, 0.5
def draw_vs(scr, c, n, ci, el, boss=False):
    h = VS_H if boss else 0.0; e = el if el < 0.45 else max(0.45, el - h)
    k = min(1.0, e / 0.45); wind = 1.0 - (1.0 - k) ** 2
    d = max(0.0, min(1.0, (e - 0.8) / 0.25)); dash = d * d
    ax = int(-26 * wind + 106 * dash); ay = (1 + (e > 0.6 or boss)) if (0.3 < e < 1.05 and int(el * 40) & 1) else 0
    talk(scr, c, ci, T("SẴN SÀNG!"), True, c[10], 9.0, goal(c), (120, 255, 120), (), False, ax, -ax, ay)
    if el > 0.1 and e < 0.85:
        v = _lk.get("vs")
        if v is None: t = txt("VS", C_PINK, 1); v = _lk["vs"] = pygame.transform.scale(t, (t.get_width() * 2, t.get_height() * 2))
        r = v.get_rect(center=(160, 50 - int(70 * (1.0 - min(1.0, (el - 0.1) / 0.2)) ** 2)))
        pygame.draw.rect(scr, (12, 10, 30), r.inflate(12, 6), 0, 6); scr.blit(v, r)
        if 0.3 < el < 0.55: pygame.draw.circle(scr, (255, 255, 255), (160, 50), int(14 + (el - 0.3) * 240), 1)
    if boss and el > 0.3:
        bl = int(el * 10) & 1; t = txt("BOSS", (255, 70, 70) if bl else (255, 200, 200)); scr.blit(t, (250 - t.get_width() // 2, 88))
        if bl: pygame.draw.rect(scr, (255, 50, 70), (0, 0, W, H), 2)
    if 0.0 < d < 1.0:
        for j in range(3):
            y = 38 + j * 10; ln = int(8 + 30 * dash)
            pygame.draw.line(scr, (255, 255, 255), (70 + ax - 20 - ln, y), (70 + ax - 20, y))
            pygame.draw.line(scr, (255, 90, 90), (250 - ax + 20 + ln, y), (250 - ax + 20, y))
    if e > 1.05:
        r = (e - 1.05) * 170
        for a in range(10):
            g = a * 0.6283; cs, sn = math.cos(g), math.sin(g)
            pygame.draw.line(scr, (255, 230, 120), (160 + cs * r * 0.4, 50 + sn * r * 0.4), (160 + cs * r, 50 + sn * r))
        flash(scr, min(255, int((e - 1.05) * 1100)))
_SP = [((1.0 if i % 2 == 0 else 0.42) * math.cos(i * 0.6283 - 1.5708), (1.0 if i % 2 == 0 else 0.42) * math.sin(i * 0.6283 - 1.5708)) for i in range(10)]
def star(scr, cx, cy, r, col, a=0.0):
    if a: c_, s_ = math.cos(a), math.sin(a); pts = [(cx + r * (u * c_ - v * s_), cy + r * (u * s_ + v * c_)) for u, v in _SP]
    else: pts = [(cx + r * u, cy + r * v) for u, v in _SP]
    pygame.draw.polygon(scr, col, pts)
def flash(scr, a):
    s = _lk.get("f")
    if s is None: s = _lk["f"] = pygame.Surface((W, H)).convert(); s.fill((255, 255, 255))
    s.set_alpha(a); scr.blit(s, (0, 0))
TCOL = ((175, 185, 215), (205, 127, 50), (200, 205, 215), (255, 205, 60), (60, 230, 255), (255, 60, 170))
def badge(i):
    bd = _lk.setdefault("bd", {}); s = bd.get(i)
    if s is None:
        s = bd[i] = pygame.Surface((16, 18), pygame.SRCALPHA); c = TCOL[i]
        if i == 0: pygame.draw.polygon(s, c, ((8, 5), (13, 10), (8, 15), (3, 10)), 1)
        else:
            top = 7 if i >= 4 else 3
            for k in range(min(3, i)): y = top + k * 3; pygame.draw.lines(s, c, False, ((1, y), (8, y + 3), (15, y)), 2)
            if i >= 4: star(s, 8, 3, 3, (255, 245, 170) if i == 4 else (255, 255, 255))
    return s
def banner_rank(scr, i, el):
    o = int(-W * (1.0 - el / 0.3) ** 2 if el < 0.3 else (W * ((el - 1.4) / 0.3) ** 2 if el > 1.4 else 0.0)); c = TCOL[i]
    pygame.draw.rect(scr, (12, 10, 30), (o, 74, W, 44)); pygame.draw.rect(scr, c, (o, 74, W, 1)); pygame.draw.rect(scr, c, (o, 117, W, 1))
    b = _lk.setdefault("bd2", {}).get(i)
    if b is None: b = _lk["bd2"][i] = pygame.transform.scale(badge(i), (32, 36))
    a = txt("THĂNG HẠNG", C_AMB); t = txt(T(TITLES[i][1]).upper(), c, 1); x = (W - 42 - t.get_width()) // 2 + o
    scr.blit(b, (x, 78)); scr.blit(a, (x + 42, 79)); scr.blit(t, (x + 42, 95))
def draw_reward(scr, sp, rt, tt, c, n, ci, old, new, nci, rk):
    if sp == "star":
        panel(scr, 10, 6, 300, 180, T("CHƯƠNG %d: %s") % (n + 1, c[0]))
        ctext(scr, T("VỀ HẠNG %d") % rk, 30, C_AMB, 2)
        for k in range(3):
            cx, cy = 80 + k * 80, 92 - 12 * (k == 1); u = (rt - 0.4 - 0.8 * (k - old)) / 0.7 if k >= old else 9.0
            if k >= new or u < 0.0: star(scr, cx, cy, 24, (44, 42, 70))
            elif u >= 1.0:
                star(scr, cx, cy, 24, (255, 205, 60))
                if k >= old and u < 1.4: pygame.draw.circle(scr, (255, 240, 150), (cx, cy), int(24 + 40 * (u - 1.0)), 1)
            else:
                f = (1.0 - u) ** 2; sx, sy = cx + (W * (0.3 if k & 1 else -0.3)) * f, cy - (cy + 30) * f
                for j in (1, 2): pygame.draw.rect(scr, (255, 230, 120), (int(sx + (W * (0.3 if k & 1 else -0.3)) * 0.12 * j * (1 - u)), int(sy - (cy + 30) * 0.12 * j * (1 - u)), 3 - j, 3 - j))
                star(scr, int(sx), int(sy), int(10 + 14 * u), (255, 255, 200), (1.0 - u) * 9.0)
            if k >= old and k < new and u >= 1.0:
                for a in range(4):
                    g = tt * 3 + a * 1.5708; pygame.draw.rect(scr, (255, 240, 150), (int(cx + 33 * math.cos(g)), int(cy + 33 * math.sin(g)), 2, 2))
        if rt > 0.9 + 0.8 * (new - old): ctext(scr, T("+%d sao mới!") % (new - old) if new > old else T("Đã có %d sao") % new, 124, (255, 255, 255))
        ctext(scr, "HOÀN HẢO!" if new == 3 else "Về nhất để đạt 3 sao", 142, C_AMB if new == 3 else C_DIM)
        hints(scr, 168, (("A", "Tiếp"),))
    elif sp == "car":
        draw_car_menu(scr, nci, tt, False, True); flash(scr, max(0, 255 - int(rt * 450)))
    else:
        win = sp != "taunt"
        talk(scr, c, ci, "THẮNG!" if win else "CHƯA ĐẠT", sp != "talk2", c[11] if sp == "talk1" else (c[12] if win else c[13]), rt,
             T("Về hạng %d") % rk if win else goal(c), (255, 220, 70) if win else (255, 120, 110),
             (("A", "Tiếp"),) if win else (("A", "Thử lại"), ("B", "Danh sách")), False)
def lite(c): return (min(255, c[0] + 80), min(255, c[1] + 80), min(255, c[2] + 80))
def chip(scr, x, y, s, col=C_DIM, p=6):
    t = txt(s, col,0); w = t.get_width() + 2 * p
    pygame.draw.rect(scr, (34, 30, 76), (x, y, w, 15), border_radius=7); pygame.draw.rect(scr, (90, 80, 170), (x, y, w, 15), 1, border_radius=7)
    scr.blit(t, (x + p, y - 1)); return w
def draw_lap(scr, b, n, tt):
    t, lp, lt, best = b; fin = lp == n; dur = 2.6 if fin else 1.8
    if t >= dur: return False
    e = min(1.0, t / 0.2, (dur - t) / 0.2); e = e * e * (3 - 2 * e)
    BW, y, h = 252, 36, (24 if fin else 18)
    w = int(BW * e); x0 = 2 + (BW - w) // 2
    if fin:
        pygame.draw.rect(scr, (176, 24, 34) if int(tt * 8) & 1 else (214, 70, 24), (x0, y, w, h))
        o = int(tt * 14)
        for i in range(0, w, 8):
            c = (240, 240, 240) if ((i >> 3) + o) & 1 else (30, 30, 36); q = min(8, w - i)
            pygame.draw.rect(scr, c, (x0 + i, y - 3, q, 3)); pygame.draw.rect(scr, c, (x0 + i, y + h, q, 3))
        if int(tt * 6) & 1:
            pygame.draw.rect(scr, (255, 70, 40), (0, 16, 2, H - 16)); pygame.draw.rect(scr, (255, 70, 40), (W - 2, 16, 2, H - 16))
        msg = T("VÒNG CUỐI!  ") + fmt(lt)
    else:
        scr.blit(_pn(BW, h, 150), (x0, y), ((BW - w) // 2, 0, w, h))
        pygame.draw.rect(scr, (255, 205, 60), (x0, y + h, w, 1))
        msg = T("VÒNG %d/%d  ·  %s") % (lp, n, fmt(lt))
    if best: msg += T("  · KỶ LỤC!")
    s = txt(msg, (255, 205, 60) if best else (255, 255, 255), 2 if fin else 0)
    dx = int(3 * math.sin(tt * 45)) if fin and t < 0.6 else 0
    scr.set_clip((x0, y, w, h))
    scr.blit(s, (2 + (BW - s.get_width()) // 2 + dx, y + (h - s.get_height()) // 2))
    scr.set_clip(None)
    return True
def draw_finish(scr, t, title, sub, gold):
    k = min(1.0, t / 0.35); e = 1.0 - (1.0 - k) ** 3; w = int(W * e)
    scr.blit(_pn(W, 44, 200), (0, 74), (0, 0, w, 44))
    o = int(t * 12)
    for i in range(0, w, 8):
        c = (240, 240, 240) if ((i >> 3) + o) & 1 else (30, 30, 36)
        pygame.draw.rect(scr, c, (i, 70, min(8, w - i), 4)); pygame.draw.rect(scr, c, (i, 118, min(8, w - i), 4))
    s = txt(title, gold, 1)
    scr.blit(s, (int((W - s.get_width()) / 2 - (1.0 - e) * W), 76))
    if t > 0.5: ctext(scr, sub, 100, C_DIM)
def transition(scr, tr, ov):
    t, tT, old, new, iris = tr; p = min(1.0, t / tT); c = p < 0.42
    q = p / 0.42 if c else (p - 0.42) / 0.58
    k = q * q * (3 - 2 * q)
    if not c: k = 1.0 - k
    scr.blit(old if c else new, (0, 0))
    if iris:
        ov.fill((0, 0, 0)); r = int(IR * (1.0 - k))
        if r > 0: pygame.draw.circle(ov, KEY, (160, 120), r)
        scr.blit(ov, (0, 0))
    else:
        h = int(H * 0.5 * k + 0.5)
        if h > 0:
            pygame.draw.rect(scr, (0, 0, 0), (0, 0, W, h)); pygame.draw.rect(scr, (0, 0, 0), (0, H - h, W, h))
            pygame.draw.rect(scr, C_CYAN, (0, h - 1, W, 1)); pygame.draw.rect(scr, C_PINK, (0, H - h, W, 1))
_pf = {}
def _profile(ti, w=300, h=22):
    s = _pf.get(ti)
    if s is None:
        t = TRACKS[ti]; Yv, C, n = t["y"], t["curve"], t["n"]
        idx = [x * (n - 1) // (w - 1) for x in range(w)]
        ys = [Yv[i] for i in idx]; lo, hi = min(ys), max(ys); k = (h - 6) / max(1.0, hi - lo)
        s = _pf[ti] = pygame.Surface((w, h), pygame.SRCALPHA); s.fill((0, 0, 0, 150))
        pts = [(x, h - 1 - int((ys[x] - lo) * k)) for x in range(w)]
        pygame.draw.polygon(s, (60, 90, 150), pts + [(w - 1, h - 1), (0, h - 1)])
        pygame.draw.lines(s, (150, 190, 255), False, pts)
        for x in range(w):
            c = min(1.0, abs(C[idx[x]]) / 6.0)
            pygame.draw.line(s, (40 + int(215 * c), 200 - int(150 * c), 60), (x, 0), (x, 3))
    return s
C_PINK, C_CYAN, C_AMB = (255, 40, 150), (40, 255, 220), (255, 200, 60)
_lg, _lk = {}, {}
_PT = [""]
PRESS = {}
_HK = {"< >": ("left", "right"), "^ v": ("up", "down")}
def panel(scr, x, y, w, h, title):
    _PT[0] = title; scr.blit(_pn(w, h, 205), (x, y))
    pygame.draw.rect(scr, (70, 60, 140), (x, y, w, h), 1)
    for qx, qy, sx, sy in ((x, y, 1, 1), (x + w - 1, y, -1, 1), (x, y + h - 1, 1, -1), (x + w - 1, y + h - 1, -1, -1)):
        pygame.draw.line(scr, C_CYAN, (qx, qy), (qx + 10 * sx, qy));
        pygame.draw.line(scr, C_CYAN, (qx, qy), (qx, qy + 10 * sy))
    t = txt(title); tw = t.get_width() + 14
    pygame.draw.polygon(scr, (200, 30, 120), ((x + 10, y + 3), (x + 18 + tw, y + 3), (x + 10 + tw, y + 19), (x + 2, y + 19)))
    scr.blit(t, (x + 12, y + 2))
def card(scr, x, y, w, h, hot=False):
    pygame.draw.rect(scr, (22, 20, 50), (x, y, w, h), border_radius=4)
    pygame.draw.rect(scr, C_PINK if hot else (70, 60, 140), (x, y, w, h), 1, border_radius=4)
PRESS = {}; _HK = {"< >": ("left", "right"), "^ v": ("up", "down")}
def hints(scr, y, items):
    ks = [txt(k) for k, _ in items]; ls = [txt(l, C_DIM) for _, l in items]
    bw = [max(16, k.get_width() + 8) for k in ks]
    x = (W - sum(b + 4 + l.get_width() for b, l in zip(bw, ls)) - 10 * (len(items) - 1)) // 2
    now = time.perf_counter()
    for (kk, _), k, l, b in zip(items, ks, ls, bw):
        p = any(now - PRESS.get(n, -9.0) < 0.12 for n in _HK.get(kk, (kk,))); dy = 2 if p else 0
        pygame.draw.rect(scr, (28, 24, 64), (x, y + 2, b, 14), border_radius=3)
        pygame.draw.rect(scr, (150, 140, 255) if p else (86, 78, 170), (x, y + dy, b, 14), border_radius=3)
        pygame.draw.rect(scr, (235, 230, 255) if p else (170, 160, 255), (x, y + dy, b, 14), 1, border_radius=3)
        scr.blit(k, (x + (b - k.get_width()) // 2, y - 1 + dy))
        scr.blit(l, (x + b + 4, y - 1))
        x += b + 4 + l.get_width() + 10
def row(scr, y, label, sel, col=(255, 255, 255), val=None, x=24, w=272):
    x -= int(120 * (1.0 - min(1.0, max(0.0, (since(("r", y), _PT[0]) - y * 0.002) / 0.22))) ** 2)
    if sel:
        t = time.perf_counter(); pu = int(20 * math.sin(t * 8))
        pts = ((x + 6, y - 2), (x + w, y - 2), (x + w - 6, y + 18), (x, y + 18))
        pygame.draw.polygon(scr, (120 + pu, 20, 90 + pu), pts); pygame.draw.polygon(scr, C_PINK, pts, 1)
        sw = (t * 1.8) % 1.5 - 0.25
        if 0 <= sw <= 1:
            sx = x + int(sw * (w - 12))
            pygame.draw.polygon(scr, (255, 255, 255), ((sx + 6, y - 2), (sx + 12, y - 2), (sx + 6, y + 18), (sx, y + 18)))
        pygame.draw.polygon(scr, C_CYAN, ((x + 12, y + 3), (x + 18, y + 8), (x + 12, y + 13)))
        tx = x + 24 + int(1.5 * math.sin(t * 8))
    else:
        tx = x + 14
    scr.blit(txt(label, col), (tx, y))
    if val:
        tv = txt(val, (255, 220, 70)); k = min(1.0, since(("v", y), val) / 0.15)
        scr.blit(tv, (x + w - 10 - tv.get_width(), y - int(5 * (1.0 - k) ** 2)))
def _glyph3d(c, front):
    k = (c, front); s = _lg.get(k)
    if s is None:
        a = S.BIG.render(c, True, front); w, h = a.get_size()
        s = pygame.Surface((w + 7, h + 7), pygame.SRCALPHA)
        for d in range(6, 0, -1): s.blit(S.BIG.render(c, True, C_PINK if d % 2 == 0 else (40, 20, 80)), (6 - d, d))
        s.blit(a, (6, 0)); _lg[k] = s
    return s
def draw_logo(scr, title, y, tt):
    cw = [S.BIG.size(c)[0] for c in title]
    beat = max(0.0, math.sin(tt * 5.0)) ** 6
    cx = (W - sum(cw)) // 2
    xs = []
    for w in cw:
        xs.append(cx)
        cx += w
    for i in range(len(title) - 1, -1, -1):
        c = title[i]
        yo = int(math.sin(tt * 3.0 + i * 0.4) * 4 - beat * 8)
        fl = (int(tt * 20 + i * 3) % 15) == 0
        scr.blit(_glyph3d(c, (255, 255, 255) if fl else C_CYAN), (xs[i] - 6, y + yo))
def draw_menu(scr, sel, tt):
    scr.blit(_pn(W, 200, 120), (0, 0))
    draw_logo(scr, "OUTDRIVE 199X", 28, tt)
    for i in range(25):
        for r in range(2):
            pygame.draw.rect(scr, (240, 240, 240) if (i + r) & 1 else (30, 30, 36), (60 + i * 8, 62 + r * 4, 8, 4))
    for i, m in enumerate(MENU): row(scr, 74 + i * 17, m, i == sel, x=60, w=200)
    draw_ver(scr)
def draw_mode(scr, sel, pts, prog):
    panel(scr, 10, 6, 300, 180, "CHẾ ĐỘ")
    vals = (T(TITLES[title_of(pts)[0]][1]), "%d/%d" % (min(prog, len(STORY)), len(STORY)))
    for i, (lb, ds) in enumerate(MODES):
        y = 48 + i * 40
        row(scr, y, lb, i == sel, val=vals[i]); scr.blit(txt(ds, C_DIM), (46, y + 15))
    hints(scr, 168, (("^ v", "Chọn"), ("A", "OK"), ("B", "Quay lại")))
def _stamp():
    s = _lk.get(0)
    if s is None:
        t = txt("LOCKED", (255, 70, 50), 1)
        b = pygame.Surface((t.get_width() + 12, t.get_height() + 4), pygame.SRCALPHA)
        pygame.draw.rect(b, (255, 70, 50), b.get_rect(), 2, border_radius=3); b.blit(t, (6, 2))
        s = _lk[0] = pygame.transform.rotozoom(b, 18, 1.0)
    return s
def draw_howto(scr):
    panel(scr, 10, 6, 300, 180, "CÁCH CHƠI")
    ctext(scr, "ĐIỀU KHIỂN", 24, C_AMB)
    hints(scr, 40, (("< >", "Lái xe"), ("A", "Ga / Trôi (tự ga)")))
    hints(scr, 58, (("B", "Phanh / Drift"), ("C", "Nitro khi đầy")))
    pygame.draw.line(scr, (50, 50, 70), (20, 78), (300, 78))
    ctext(scr, "KỸ NĂNG: DRIFT", 84, C_AMB)
    ctext(scr, "Giữ B + < > khi chạy nhanh để lết bánh", 100, (255, 255, 255))
    ctext(scr, "Góc cua càng gắt -> Nạp Nitro càng nhanh", 114, C_DIM)
    pygame.draw.rect(scr, C_AMB, (22, 144, 6, 6)); scr.blit(txt("Cam: Bứt tốc", C_DIM, 0), (32, 140))
    pygame.draw.rect(scr, (90, 200, 255), (116, 144, 6, 6)); scr.blit(txt("Xanh: Bay", C_DIM, 0), (126, 140))
    hints(scr, 168, (("A", "Tiếp"), ("B", "Quay lại")))
def draw_podium(scr, pod, t, tt):
    d = pygame.draw; rect = d.rect; FL = 166
    bg = _lk.get("pb")
    if bg is None:
        bg = _lk["pb"] = pygame.Surface((W, H)).convert()
        for i in range(8): bg.fill((10 + i * 3, 8 + i * 2, 28 + i * 6), (0, i * 24, W, 24))
    scr.blit(bg, (0, 0))
    for i in range(14):
        if (int(tt * 3) + i) & 3 == 0:
            x, y = (i * 53 + 17) % W, (i * 29) % 80 + 26
            rect(scr, (255, 240, 170), (x - 1, y, 3, 1)); rect(scr, (255, 240, 170), (x, y - 1, 1, 3))
    scr.blit(_pn(W, 22, 200), (0, 0)); rect(scr, C_PINK, (0, 22, W, 1))
    ctext(scr, "BỤC VINH DANH", 3, RK[0], 2)
    rect(scr, (14, 12, 28), (0, FL, W, H - FL)); rect(scr, C_CYAN, (0, FL, W, 1))
    for r_, cx, h, t0 in ((2, 244, 56, 0.2), (1, 76, 72, 0.7), (0, 160, 92, 1.2)):
        if r_ >= len(pod): continue
        name, sp, tm, me = pod[r_]; col = RK[r_]; dk = (col[0] * 6 // 10, col[1] * 6 // 10, col[2] * 6 // 10)
        u = max(0.0, min(1.0, (t - t0) / 0.5)); u = 1.0 - (1.0 - u) ** 3
        top = FL - int(h * u)
        rect(scr, (56, 52, 100), (cx - 36, top, 72, FL - top)); rect(scr, (40, 36, 78), (cx - 36, top + 20, 72, FL - top - 20))
        d.polygon(scr, col, ((cx - 36, top), (cx + 36, top), (cx + 31, top - 5), (cx - 31, top - 5)))
        rect(scr, dk, (cx - 36, top, 72, FL - top), 1)
        c = t - t0 - 0.5
        if u < 1.0 or c <= 0: continue
        off = 100 * (1 - c / 0.35) ** 2 if c < 0.35 else 5 * max(0.0, 1 - (c - 0.35) / 0.4) * abs(math.sin((c - 0.35) * 12))
        w_, h_ = sp.get_size(); scr.blit(shadow(w_, 140), (cx - (w_ >> 1), top - 7))
        scr.blit(sp, (cx - (w_ >> 1), top - 2 - h_ - int(off)))
        d.circle(scr, col, (cx, top + 13), 9); d.circle(scr, dk, (cx, top + 13), 9, 1)
        n = txt(str(r_ + 1), (200, 250, 255), 0); scr.blit(n, (cx - (n.get_width() >> 1), top + 6))
        n = txt(name, (255, 230, 90) if me else (255, 255, 255)); scr.blit(n, (cx - (n.get_width() >> 1), top + 25))
        n = txt(fmt(tm), (180, 230, 255)); scr.blit(n, (cx - (n.get_width() >> 1), top + 38))
        if me and c > 0.8:
            ay = top - h_ - 10 + int(2 * math.sin(tt * 6)); d.polygon(scr, (255, 230, 90), ((cx - 4, ay - 4), (cx + 4, ay - 4), (cx, ay + 1)))
    if t > 1.0: hints(scr, 168, (("A", "Tiếp tục"),))
_CR = (("LẬP TRÌNH & THIẾT KẾ", "Dương Văn Phi", C_AMB),
       ("ĐỒ HỌA", "Vẽ hoàn toàn bằng code", (255, 255, 255)),
       ("ÂM THANH", "Nhạc & hiệu ứng miễn phí bản quyền", (255, 255, 255)),
       ("CÔNG NGHỆ", "Python 3 · Pygame 2", (255, 255, 255)),
       ("LIÊN HỆ", "duongvanphi19@gmail.com", C_AMB),
       ("CẢM ƠN", "Bạn đã đồng hành cùng OUTDRIVE 199X!", C_PINK),("VERSION",VSTR, C_DIM))
def draw_credit(scr):
    tt = time.perf_counter(); d = pygame.draw
    panel(scr, 10, 6, 300, 180, "GIỚI THIỆU")
    draw_logo(scr, "OUTDRIVE 199X", 26, tt)
    d.line(scr, C_PINK, (40, 54), (W - 40, 54)); d.line(scr, C_CYAN, (40, 152), (W - 40, 152))
    BH, TOP, VH = 34, 56, 94
    off = (since("cred") * 18) % (len(_CR) * BH + VH)
    scr.set_clip((12, TOP, 296, VH))
    for i, (role, who, col) in enumerate(_CR):
        y = TOP + VH - off + i * BH
        if -BH < y - TOP < VH:
            ctext(scr, role, int(y), C_CYAN); ctext(scr, who, int(y) + 12, col)
    scr.blit(_pn(296, 10, 230), (12, TOP)); scr.blit(_pn(296, 10, 230), (12, TOP + VH - 10))
    scr.set_clip(None)
    hints(scr, 168, (("A", "Về Menu"),))
def _trophy(scr, cx, y):
    g, d, l = (255, 205, 60), (190, 140, 20), (255, 240, 170)
    pygame.draw.polygon(scr, g, ((cx - 16, y), (cx + 16, y), (cx + 12, y + 20), (cx + 4, y + 26), (cx - 4, y + 26), (cx - 12, y + 20)))
    pygame.draw.polygon(scr, d, ((cx + 5, y), (cx + 16, y), (cx + 12, y + 20), (cx + 4, y + 26), (cx + 5, y + 26)))
    pygame.draw.lines(scr, g, False, ((cx - 16, y + 3), (cx - 22, y + 3), (cx - 20, y + 14), (cx - 13, y + 17)), 2)
    pygame.draw.lines(scr, g, False, ((cx + 16, y + 3), (cx + 22, y + 3), (cx + 20, y + 14), (cx + 13, y + 17)), 2)
    pygame.draw.rect(scr, g, (cx - 3, y + 26, 6, 6)); pygame.draw.rect(scr, d, (cx - 10, y + 32, 20, 5))
    pygame.draw.line(scr, l, (cx - 10, y + 3), (cx - 8, y + 16), 2)
def draw_end(scr, got, ncars, tt):
    tot = 3 * len(STORY)
    panel(scr, 10, 6, 300, 180, "KẾT THÚC")
    _trophy(scr, W // 2, 27 + int(math.sin(tt * 3) * 1.5))
    ctext(scr, "VÔ ĐỊCH!", 66, C_AMB, 1)
    ctext(scr, "Bạn đã chinh phục cả giải đấu", 102, C_DIM)
    x0 = (W - tot * 12) // 2
    for i in range(tot): pygame.draw.rect(scr, C_AMB if i < got else (44, 42, 70), (x0 + i * 12, 120, 9, 8))
    ctext(scr, T("Sao %d/%d   ·   Xe đã mở %d/%d") % (got, tot, ncars, len(PCAR_DEF)), 131, (255, 255, 255))
    if got >= tot:
        if int(tt * 2) & 1 == 0: ctext(scr, "HOÀN HẢO - 3 SAO MỌI CHƯƠNG!", 149, C_AMB)
    else: ctext(scr, "Đạt 3 sao ở mọi chương để hoàn hảo", 149, C_DIM)
    hints(scr, 168, (("A", "Về menu"),))
def draw_pause(scr, sel):
    scr.blit(_pn(W, H, 130), (0, 0))
    panel(scr, 60, 30, 200, 130, "TẠM DỪNG")
    for i, m in enumerate(PAUSE): row(scr, 56+ i * 24, m, i == sel, x=70, w=180)
    hints(scr, 134, (("^ v", "Chọn"), ("A", "OK"), ("B", "Tiếp")))
def draw_fly(scr, ti, fl):
    t = TRACKS[ti]; u = min(1.0, fl / FLYT); r = pygame.draw.rect
    r(scr, (0, 0, 0), (0, 0, W, 16)); r(scr, (0, 0, 0), (0, H - 40, W, 40))
    r(scr, C_PINK, (0, 16, W, 1)); r(scr, C_CYAN, (0, H - 41, W, 1))
    t1 = txt(t["name"]); pygame.draw.polygon(scr, (200, 30, 120), ((0, 0), (t1.get_width() + 18, 0), (t1.get_width() + 10, 15), (0, 15)))
    scr.blit(t1, (5, 1))
    s = txt(t["desc"], C_DIM); scr.blit(s, (W - 4 - s.get_width(), 1))
    scr.blit(_profile(ti), (10, H - 38))
    x = 10 + int(u * 299); pygame.draw.line(scr, (255, 255, 255), (x, H - 38), (x, H - 17))
    mx, my = W - MMW - 3, 20
    scr.blit(t["mms"], (mx, my)); r(scr, (70, 60, 140), (mx - 1, my - 1, MMW + 2, MMH + 2), 1)
    p = t["mmp"][int(u * (len(t["mmp"]) - 1))]
    r(scr, (255, 255, 255), (mx + p[0] - 2, my + p[1] - 2, 5, 5)); r(scr, (230, 30, 45), (mx + p[0] - 1, my + p[1] - 1, 3, 3))
    if u > 0.9 and int(fl * 6) & 1 == 0: ctext(scr, "SẴN SÀNG!", 60, (255, 230, 90), 1)
    hints(scr, H - 16, (("A", "Bỏ qua"),))
def draw_settings(scr, sel, cfg):
    panel(scr, 10, 6, 300, 180, "CÀI ĐẶT")
    vol_labels = ("Tắt", "Nhỏ", "Vừa", "Lớn")
    items = (
        ("Chất lượng đồ họa", QN[cfg["q"]]),
        ("Âm lượng", vol_labels[cfg.get("vol", 3)]),
        ("Ngôn ngữ", ("Tiếng Việt", "English")[cfg.get("lang", 0)]),
        ("Cách chơi", None),
        ("Giới thiệu", None)
    )
    for i, (lb, v) in enumerate(items):
        row(scr, 38 + i * 20, lb, i == sel, val=v)
    hints(scr, 168, (("^ v", "Chọn"), ("< >", "Đổi"), ("A", "OK"), ("B", "Quay lại")))
def draw_diff(scr, sel, tt, ti):
    panel(scr, 10, 6, 300, 180, "ĐỘ KHÓ")
    ctext(scr, TRACKS[ti]["name"], 28, C_DIM)
    INF = (("Dễ", "Đối thủ chậm", 0, (120, 255, 120)), ("Thường", "Cân bằng", 1, (255, 220, 70)), ("Khó", "Đối thủ nhanh, ráo riết", 2, (255, 90, 80)))
    for i, (lb, ds, k, c) in enumerate(INF):
        y = 48 + i * 30
        row(scr, y, lb, i == sel, c if i == sel else (255, 255, 255), val="x%g %s" % (PTS_DIF[k], T("điểm")))
        scr.blit(txt(ds, C_DIM), (46, y + 15))
        for p in range(3): pygame.draw.rect(scr, c if p <= k else (44, 42, 70), (254 + p * 12, y + 20, 9, 5))
    hints(scr, 168, (("^ v", "Chọn"), ("A", "Đua"), ("B", "Quay lại")))
def draw_netmenu(scr, sel, name, ip):
    panel(scr, 10, 6, 300, 180, "NHIỀU NGƯỜI · LAN")
    items = (("Tạo phòng", None), ("Tìm phòng", None), ("Nhập địa chỉ IP", None), ("Tên tay đua", name))
    for i, (lb, v) in enumerate(items): row(scr, 30 + i * 22, lb, i == sel, val=v)
    ctext(scr, T("Cùng Wi-Fi hoặc hotspot · tối đa %d người") % netplay.MAXP, 144, C_DIM)
    hints(scr, 168, (("^ v", "Chọn"), ("A", "OK"), ("B", "Quay lại")))
def draw_netjoin(scr, rl, sel, tt):
    panel(scr, 10, 6, 300, 180, "TÌM PHÒNG LAN")
    if not rl:
        ctext(scr, T("Đang tìm phòng") + "." * (int(tt * 3) % 4), 62, C_DIM)
        ctext(scr, "Không thấy? Nhờ chủ phòng đọc IP,", 92, C_DIM)
        ctext(scr, "rồi chọn \"Nhập địa chỉ IP\"", 106, C_DIM)
    for i, (a, r) in enumerate(rl[:5]):
        busy = bool(r[4]); v = r[7] if len(r) > 7 else ""
        col = (255, 90, 90) if v and v != VSTR else (C_DIM if busy else (255, 255, 255))
        row(scr, 30 + i * 22, ("%s  %d/%d  %s" % (r[0], r[2], r[3], v)).rstrip(), i == sel, col,
            "Đang đua" if busy else TRACKS[r[1] % len(TRACKS)]["name"])
    hints(scr, 168, (("^ v", "Chọn"), ("A", "Vào"), ("B", "Quay lại")))
def draw_netip(scr, octs, cur, tt):
    panel(scr, 10, 6, 300, 180, "NHẬP ĐỊA CHỈ IP")
    for i, v in enumerate(octs):
        bx = 24 + i * 68; on = i == cur
        card(scr, bx, 66, 56, 30, on)
        t = txt(str(v), (255, 255, 255) if on else C_DIM, 2); scr.blit(t, (bx + (56 - t.get_width()) // 2, 73))
        if i < 3: scr.blit(txt("."), (bx + 59, 78))
        if on:
            o = int(2 * math.sin(tt * 8)); cx = bx + 28
            pygame.draw.polygon(scr, C_CYAN, ((cx - 6, 60 - o), (cx + 6, 60 - o), (cx, 54 - o)))
            pygame.draw.polygon(scr, C_CYAN, ((cx - 6, 102 + o), (cx + 6, 102 + o), (cx, 108 + o)))
    ctext(scr, "^ v: ±1   ·   C: +10   ·   < >: đổi ô", 124, C_DIM)
    ctext(scr, "Thường chỉ cần sửa ô cuối cùng", 140, C_DIM)
    hints(scr, 168, (("A", "Kết nối"), ("B", "Quay lại")))
def draw_netlobby(scr, net, trk, tt, pts=0):
    joined = net.state == "lobby" and net.roster
    panel(scr, 10, 6, 300, 180, "PHÒNG CHỜ" if joined else "ĐANG KẾT NỐI")
    if not joined:
        ctext(scr, T("Đang kết nối") + "." * (int(tt * 3) % 4), 80, C_DIM)
        hints(scr, 168, (("B", "Hủy"),)); return
    t = TRACKS[trk]; pg = pygame.draw
    scr.blit(txt("Map: " + T(t["name"]), (255, 255, 255), 0), (24, 26))
    chip(scr, 224, 26, T("%d vòng") % t["laps"], C_AMB)
    for i in range(netplay.MAXP):
        x = 14 + i * 72; cx = x + 34; r = net.roster[i] if i < len(net.roster) else None
        me = r is not None and r[0] == net.me
        card(scr, x, 46, 68, 92, me)
        if r is None:
            e = txt("Trống", (90, 95, 120)); scr.blit(e, (cx - e.get_width() // 2, 84)); continue
        c = (net.car if me else r[2]) % len(PCAR_DEF); nm, col = T(PCAR_DEF[c][0]), lite(PCAR_DEF[c][1])
        pp = pts if me else (r[4] if len(r) > 4 else 0)
        scr.blit(badge(title_of(pp)[0]), (x + 3, 49))
        pg.ellipse(scr, col, (x + 9, 76, 50, 12), 1)
        p = PREVS[c][int(tt * 6 + i * 7) % 24]; scr.blit(p, (cx - p.get_width() // 2, 87 - p.get_height()))
        n = txt(r[1]); scr.blit(n, (cx - n.get_width() // 2, 90))
        n = txt(nm, col); scr.blit(n, (cx - n.get_width() // 2, 102))
        is_ready = r[3] if len(r) > 3 else 0
        if r[0] == 0:
            lbl, tcol = "CHỦ", C_AMB
        elif is_ready:
            lbl, tcol = "SẴN SÀNG", (120, 255, 120)
        elif me:
            lbl, tcol = "BẠN", C_PINK
        else:
            lbl = None
        if lbl:
            cw = txt(lbl).get_width() + 12
            chip(scr, cx - cw // 2, 120, lbl, tcol, 3)
    if net.is_host:
        ctext(scr, "IP: " + net.ip, 13, (255, 220, 70))
        ctext(scr, "Tất cả Sẵn sàng thì bấm A để bắt đầu", 144, C_DIM)
        hints(scr, 168, (("< >", "Đường"), ("C", "Xe"), ("A", "Bắt đầu"), ("B", "Rời")))
    else:
        ctext(scr, "Bấm A để Sẵn Sàng / Hủy", 146, C_DIM)
        hints(scr, 168, (("A", "Sẵn sàng"), ("C", "Xe"), ("B", "Rời")))
def draw_story(scr, sel, prog, stg, mp=0):
    panel(scr, 10, 6, 300, 180, "CỐT TRUYỆN")
    for i, c in enumerate(STORY):
        y = 29 + i * 21; ok = i <= prog
        row(scr, y, "%d. %s" % (i + 1, T(c[0])), i == sel, (255, 255, 255) if ok else C_DIM)
        if not ok:
            pygame.draw.rect(scr, C_DIM, (279, y + 1, 7, 9), 2, border_radius=3)
            pygame.draw.rect(scr, C_DIM, (277, y + 6, 11, 8), border_radius=2)
            pygame.draw.circle(scr, (20, 18, 40), (282, y + 9), 1)
            pygame.draw.rect(scr, (20, 18, 40), (282, y + 10, 1, 3))
        elif i == prog:
            pygame.draw.rect(scr, (200, 30, 120), (246, y + 2, 32, 13), border_radius=6); scr.blit(txt("MỚI" if not mp else "%d/3" % (mp + 1)), (252, y))
        else:
            for k in range(3):
                col_s = (255, 205, 60) if k < stg.get(str(i), 0) else (70, 72, 96)
                sx = 246 + k * 9; sy = y + 8 - (k * 1) if k % 2 == 0 else y + 5 + (k)
                pygame.draw.polygon(scr, col_s, [(sx, sy - 5), (sx + 1, sy - 2), (sx + 4, sy - 2), (sx + 2, sy + 1), (sx + 4, sy + 5),
                                                 (sx, sy + 3), (sx - 4, sy + 5), (sx - 2, sy + 1), (sx - 4, sy - 2), (sx - 1, sy - 2)])
    if sel in REWARD: ctext(scr, T("Thưởng: mở xe ") + T(REWARD[sel]), 152, C_AMB)
    hints(scr, 168, (("^ v", "Chọn"), ("A", "OK"), ("B", "Quay lại")))
PCX = W - 20
PAUSE_HIT = (PCX - 30, 0, W, 30)
_hs = {"r": 0, "t": -9.0, "c": (200, 30, 120)}
def hud_top(scr, o, rank, tot, lap, laps, tm, tt, last, pause):
    y = -o; d = pygame.draw
    if tm < 0.2: _hs["r"] = 0
    if rank != _hs["r"]:
        if _hs["r"]: _hs["c"] = (40, 170, 90) if rank < _hs["r"] else (210, 50, 50); _hs["t"] = tt
        _hs["r"] = rank
    rc = _hs["c"] if tt - _hs["t"] < 0.8 else (200, 30, 120)
    scr.blit(_pn(W, 18, 170), (0, y)); d.line(scr, C_PINK, (0, y + 18), (W, y + 18))
    t = txt(T("HẠNG %d/%d") % (rank, tot)); tw = t.get_width() + 14
    d.polygon(scr, rc, ((0, y), (tw + 8, y), (tw, y + 17), (0, y + 17))); scr.blit(t, (5, y + 1))
    s_ = fmt(tm); _, tw_ = S.num(s_); S.ntxt(scr, s_, (W - tw_) // 2, y + 1)
    t = txt(T("VÒNG %d/%d") % (lap, laps), ((255, 90, 60) if int(tt * 4) & 1 else C_AMB) if last else (255, 255, 255))
    d.polygon(scr, (34, 30, 76), ((PCX - 26, y), (W, y), (W, y + 17), (PCX - 18, y + 17))); scr.blit(t, (2, y + 20))
    if pause:
        d.rect(scr, (66, 70, 128), (PCX - 12, y + 2, 24, 14), border_radius=3)
        d.rect(scr, (235, 235, 245), (PCX - 6, y + 5, 4, 8)); d.rect(scr, (235, 235, 245), (PCX + 2, y + 5, 4, 8))
def dial():
    s = getattr(dial, "s", None)
    if s is None:
        r = 24; c = r + 2; d = pygame.draw; s = dial.s = pygame.Surface((2 * c, 2 * c), pygame.SRCALPHA)
        d.circle(s, (10, 8, 26, 225), (c, c), r); d.circle(s, (90, 84, 170), (c, c), r, 1); d.circle(s, (36, 34, 78), (c, c), r - 9, 1)
        for k in range(19):
            f = k / 18.0; u = f * 2 if f < 0.5 else (f - 0.5) * 2
            p, q = ((40, 230, 255), (255, 210, 60)) if f < 0.5 else ((255, 210, 60), (255, 50, 50))
            col = tuple(int(a + (b - a) * u) for a, b in zip(p, q)); a = 3.84 - f * 4.5; L = r - (8 if k % 3 == 0 else 5)
            d.line(s, col, (c + math.cos(a) * L, c - math.sin(a) * L), (c + math.cos(a) * (r - 2), c - math.sin(a) * (r - 2)), 2 if k % 3 == 0 else 1)
    return s
def hud_speed(scr, cx, cy, v, boost, tt):
    d = pygame.draw; scr.blit(dial(), (cx - 26, cy - 26)); v0 = v; v = min(1.08, v); hot = v > 0.95
    if boost or hot: d.circle(scr, (70, 200, 255) if boost else ((255, 60, 50) if int(tt * 10) & 1 else (120, 30, 40)), (cx, cy), 25, 1)
    a = 3.84 - (v + (math.sin(tt * 90) * 0.03 if hot else 0.0)) * 4.5; ca, sa = math.cos(a), math.sin(a)
    d.polygon(scr, (70, 200, 255) if boost else (255, 70, 45), ((cx + ca * 19, cy - sa * 19), (cx + sa * 2, cy + ca * 2), (cx - ca * 5, cy + sa * 5), (cx - sa * 2, cy - ca * 2)))
    d.circle(scr, (30, 28, 60), (cx, cy), 3); d.circle(scr, (255, 255, 255), (cx, cy), 1)
    s_ = str(int(v0 * 180)); _, w_ = S.num(s_); S.ntxt(scr, s_, cx - (w_ >> 1), cy + 7)
_nb = {}
_BL = ((5, 0), (33, 0), (41, 5), (33, 10), (0, 10))
def _blade():
    s = _nb.get(0)
    if s is None:
        s = _nb[0] = pygame.Surface((42, 11), pygame.SRCALPHA); pygame.draw.polygon(s, (0, 0, 0, 130), _BL)
    return s
def hud_nitro(scr, x, y, nitro, boost, tt):
    full = nitro >= 1.0; d = pygame.draw
    col, hi = ((70, 200, 255), (200, 240, 255)) if boost else (((255, 255, 255), (255, 255, 255)) if full and int(tt * 8) & 1 else ((255, 150, 40), (255, 215, 120)))
    for i in range(2):
        bx = x + i * 5; by = y + 13 - i * 13; f = max(0.0, min(1.0, nitro - i)); scr.blit(_blade(), (bx, by))
        if f > 0.02:
            xc = f * 33
            pts = _BL if xc > 28 else ((5, 0), (xc + 5, 0), (xc, 10), (0, 10))
            d.polygon(scr, col, [(bx + a, by + b) for a, b in pts])
            d.line(scr, hi, (bx + 5, by + 1), (bx + (33 if xc > 28 else xc + 4), by + 1))
        for q in (1, 2, 3): d.line(scr, (0, 0, 0), (bx + q * 8 + 4, by), (bx + q * 8 - 1, by + 10))
        d.polygon(scr, (255, 255, 255) if f >= 1.0 or boost else (150, 156, 176), [(bx + a, by + b) for a, b in _BL], 1)
    scr.blit(txt("NITRO", (70, 200, 255) if boost else ((255, 255, 255) if full else (255, 170, 40))), (x + 48, y + 6))
def ctag(scr, s, y, col, dx=0):
    t = txt(s, col); w = t.get_width() + 14; x = (W - w) // 2 + dx
    scr.blit(_pn(w, 15, 190), (x, y)); pygame.draw.rect(scr, col, (x, y, w, 15), 1, border_radius=4)
    scr.blit(t, (x + 7, y - 1))
def _sm(img, h):
    k = (id(img), h); s = _lk.get(k)
    if s is None:
        w0, h0 = img.get_size(); s = _lk[k] = pygame.transform.scale(img, (max(1, w0 * h // h0), h))
    return s
DIFF = (2, 2, 4, 3, 3, 1, 4, 1, 5)
def _diff(ti): return DIFF[ti]
def draw_track_menu(scr, ti, recs, tt, pts=0, ci=0, sg=-1, prog=0):
    t = TRACKS[ti]; r = recs.get(str(ti), {}); L, R = 30, 142; d = pygame.draw; cb = 132
    panel(scr, 10, 6, 300, 180, T("CHỌN ĐƯỜNG   %d/%d") % (ti + 1, len(TRACKS)))
    title_corner(scr, pts)
    m = t["mml"]; mm = _lk.get(("mm", ti))
    if mm is None:
        w0, h0 = m.get_size(); s = min(90 / w0, 70 / h0)
        mm = _lk[("mm", ti)] = pygame.transform.smoothscale(m, (int(w0 * s), int(h0 * s)))
    mw, mh = mm.get_size()
    arrows(scr, (36 + cb) // 2, tt)
    card(scr, L, 34, 102, cb - 36+4)
    scr.blit(mm, (L + 6 + (90 - mw) // 2, 40 + (70 - mh) // 2))
    lk = not tunlk(ti, prog)
    if lk: s_ = _stamp(); scr.blit(s_, (L + 51 - s_.get_width() // 2, 36 + (cb - 36) // 2 - s_.get_height() // 2))
    fy = cb - 18; d.line(scr, (70, 60, 140), (L + 4, fy), (L + 97, fy)); d.line(scr, (70, 60, 140), (L + 51, fy + 3), (L + 51, fy + 15))
    a = txt(T("%d vòng") % t["laps"], C_AMB); scr.blit(a, (L + 27 - a.get_width() // 2, fy ))
    b = txt("%.1f km" % (t["tl"] / 100000.0), C_CYAN); scr.blit(b, (L + 75 - b.get_width() // 2, fy ))
    ox = int(60 * (1 - min(1.0, since("trk", ti) / 0.25)) ** 2)
    scr.blit(txt(t["name"], (255, 255, 255), 2), (R + ox, 34))
    scr.blit(txt(T("Độ khó"), C_DIM), (R, 54)); lv = _diff(ti)
    for i in range(5):
        c = ((90, 230, 120), (190, 230, 70), (255, 200, 60), (255, 130, 50), (255, 60, 60))[lv - 1] if i < lv else (44, 42, 70)
        d.polygon(scr, c, [(R + 54 + i * 12 + 3, 57), (R + 54 + i * 12 + 11, 57), (R + 54 + i * 12 + 8, 65), (R + 54 + i * 12, 65)])
        ch = cb - 76; card(scr, R, 76, 148, ch); best = "best" in r
    scr.blit(txt("KỶ LỤC", C_AMB), (R + 8, 79))
    scr.blit(txt(fmt(r["best"]) if best else "--:--.-", (255, 255, 255), 2), (R + 8, 95))
    scr.blit(txt(T("Vòng ") + (fmt(r["lap"]) if "lap" in r else "--:--.-"), (180, 230, 255)), (R + 8, 72 + ch - 16))
    if best:
        bi = r.get("bc", 0) % len(PCAR_DEF); p = _sm(PREVS[bi][8], 28); cx = R + 120
        n = txt(T(PCAR_DEF[bi][0]), lite(PCAR_DEF[bi][1]))
        nx = cx - 6 - n.get_width() // 2; ny = 78
        scr.blit(n, (nx, ny)); scr.blit(_crown(), (nx - 14, ny + 3))
        sh = S.shadow_real(p, p.get_width(), 140)
        sh_x = cx + 3 - (sh.get_width() >> 1)
        sh_y = 76 + ch - (sh.get_height() >> 1) - 1
        scr.blit(sh, (sh_x, sh_y))
        scr.blit(p, (cx + 3 - (p.get_width() >> 1), 76 + ch - p.get_height()))
    lm = _lm(ti)
    if lm:
        b_ = BASES[lm]; lw, lh = b_.get_size(); lp = _sm(b_, max(12, min(20, 32 * lh // lw))); lx, ly = R + 132, 72
        lsh = S.shadow_real(lp, lp.get_width(), 140)
        scr.blit(lsh, (lx - (lsh.get_width() >> 1), ly - (lsh.get_height() >> 1) - 1));
        scr.blit(lp, (lx - (lp.get_width() >> 1), ly - lp.get_height()))
    if lk: scr.blit(txt(T("Thắng chương %d để mở") % TNEED[ti], (255, 120, 110)), (30, cb + 9))
    else:
        scr.blit(txt(T("Lái: ") + T(PCAR_DEF[ci % len(PCAR_DEF)][0]), (255, 255, 255)), (30, cb + 9))
        if sg >= 0: scr.blit(txt(T("Xe hợp đường này") if sg == ci else T("Hợp: ") + T(PCAR_DEF[sg][0]), (120, 255, 120)), (R + 8, cb + 9))
    hints(scr, 168, (("^ v", "Đổi xe"),("< >", "Chọn"), ("A", "Đua"), ("B", "Quay lại")))
def _lm(ti):
    k = _lk.get(("lm", ti))
    if k is None:
        k = next((KINDS[o[0]] for q in TRACKS[ti]["spr"] for o in q if o[0] >= 16), ""); k = _lk[("lm", ti)] = k if k in BASES else ""
    return k
def _crown():
    s = _lk.get("crown")
    if s is None:
        s = _lk["crown"] = pygame.Surface((11, 8), pygame.SRCALPHA); g = (255, 205, 60)
        pygame.draw.polygon(s, g, ((0, 1), (3, 4), (5, 0), (7, 4), (10, 1), (9, 7), (1, 7)))
        pygame.draw.line(s, (190, 140, 20), (1, 7), (9, 7))
        for x in (0, 5, 10): s.set_at((x, 0 if x == 5 else 1), (255, 245, 170))
    return s
def title_corner(scr, pts):
    k, nx = title_of(pts); a = txt(T(TITLES[k][1]), TCOL[k]); b = txt("%d/%d" % (pts, nx) if nx else str(pts), C_DIM)
    x = 304 - b.get_width(); scr.blit(b, (x, 8)); x -= a.get_width() + 5; scr.blit(a, (x, 8)); scr.blit(badge(k), (x - 18, 7))
def _rc(r):
    h = r.get("hist")
    if not isinstance(h, list): h = [[r["best"], 0, r.get("bc", 0)]] if "best" in r else []
    return {e[2]: e[0] for e in h if isinstance(e, list) and len(e) > 2}
PA = 8
def draw_rank(scr, rows, title, info, icol, ha, hb, t=9.0, pts_gain=0, xp_gain=0, rec=None):
    panel(scr, 10, 6, 300, 180, title)
    lead = rows[0][2]; n = len(rows); x, w = 24, 272
    scr.set_clip((11, 25, 298, 116))
    for i, (nm, col, tm, ok, me) in enumerate(rows):
        k = min(1.0, (t - 0.25 - i * 0.07) / 0.25)
        if k <= 0.0: continue
        o = int((1.0 - k) ** 3 * 300); y = 29 + i * 21; c = (255, 220, 70) if me else (255, 255, 255)
        card(scr, x + o, y - 2, w, 20, me)
        if me:
            pygame.draw.rect(scr, (70, 16, 60), (x + o + 1, y - 1, w - 2, 18), border_radius=3)
            if t < 2.2 and int(t * 6) & 1: pygame.draw.rect(scr, (255, 255, 255), (x + o, y - 2, w, 20), 1, border_radius=4)
        if i < 3: pygame.draw.rect(scr, RK[i], (x + o + 1, y + 2, 3, 12))
        scr.blit(txt(str(i + 1), RK[i] if i < 3 else C_DIM), (x + 10 + o, y))
        pygame.draw.rect(scr, col, (x + 28 + o, y + 4, 10, 7))
        nt = txt(nm, c, 0); scr.blit(nt, (x + 44 + o, y))
        if me and rec:
            r_txt = txt(rec, (255, 205, 60), 0)
            scr.blit(r_txt, (x + 44 + o + nt.get_width() + 12, y))
        s = txt((fmt(tm) if i == 0 else "+%.1f" % (tm - lead)) if ok else "...", c)
        scr.blit(s, (x + w - 8 + o - s.get_width(), y))
    scr.set_clip(None)
    if t > 0.5 + n * 0.07:
        y_pos = 133
        if pts_gain > 0:
            chip(scr, 28, y_pos, f"+{pts_gain} PTS", (255, 215, 0))
        if xp_gain > 0:
            chip(scr, 150, y_pos, f"+{xp_gain} XP Xe", (80, 230, 255))
        ctext(scr, info, 153, icol)
    if ha: hints(scr, 168, (("A", ha), ("B", hb)))
def draw_car_menu(scr, ci, tt, lk=False, rw=False, pts=0, save=None):
    nm, col, desc, st_ = PCAR_DEF[ci]
    panel(scr, 10, 6, 300, 180, "XE MỚI MỞ KHÓA" if rw else T("CHỌN XE   %d/%d") % (ci + 1, len(PCAR_DEF)))
    if not rw: title_corner(scr, pts)
    is_master = (not lk and not rw and save is not None and mas_lv(save.get("mas", {}).get(str(ci), [0]*4))[0] == 5)
    nm_col = C_AMB if is_master else (255, 255, 255)
    ctext(scr, nm if not lk else "???", 26, nm_col, 2)
    if is_master:
        nm_w = txt(nm, nm_col, 2).get_width()
        scr.blit(_crown(), ((W + nm_w) // 2 + 6, 32))
    if not lk and not rw and save is not None:
        mas_data = save.get("mas", {}).get(str(ci), [0, 0, 0, 0])
        i_lv, nx_lv = mas_lv(mas_data)
        chip(scr, W // 2 - 42, 45, T(MASN[i_lv]) + (" %d/%d" % (mas_data[0], nx_lv) if nx_lv else " MAX"), MCOL[i_lv])
    cy = 84
    p = PREVS[ci][int(tt * 6) % 24]; pw, ph = p.get_size()
    cx_, cy_ = (W - pw) // 2, cy - ph + 6
    if is_master:
        pulse = abs(math.sin(tt * 2.5))
    sh = S.shadow_real(p, pw, 140)
    scr.blit(sh, (cx_ + (pw - sh.get_width()) // 2, cy_ + ph - sh.get_height() // 2 - 2))
    scr.blit(p, (cx_, cy_))
    if is_master:
        phase = (tt * 0.8) % 1.0
        if phase < 0.2:
            sz = int(math.sin(phase / 0.2 * math.pi) * 5)
            if sz > 0:
                gx, gy = cx_ + pw//3, cy_ + ph//3
                pygame.draw.line(scr, (255, 255, 255), (gx - sz, gy), (gx + sz, gy), 1)
                pygame.draw.line(scr, (255, 255, 255), (gx, gy - sz), (gx, gy + sz), 1)
    if lk:
        s = _stamp()
        scr.blit(s, ((W - s.get_width()) // 2, cy_ + (ph - s.get_height()) // 2))
    if not rw: arrows(scr, cy - 18, tt)
    ctext(scr, LOCKT.get(ci, "") if lk else desc, 100, (255, 120, 110) if lk else C_DIM)
    card(scr, 30, 121, 260, 40)
    for k, lb in enumerate(("Tốc độ", "Tăng tốc", "Độ bám", "Nitro")):
        x = 42 + (k & 1) * 128; y = 124 + (k >> 1) * 17
        scr.blit(txt(lb, (150, 155, 163)), (x, y))
        if lk: scr.blit(txt("?", (100, 100, 110)), (x + 58, y))
        else: stars(scr, x + 58, y + 3, st_[k])
    hints(scr, 168, (("A", "Tiếp"),) if rw else (("< >", "Chọn"), ("A", "OK"), ("B", "Quay lại")))
def draw_prof(scr, save, name, pts, stars, prog, secs, tt, hint=True, own=1):
    d = pygame.draw; G = (150, 150, 170); recs = save.get("rec") or {}; nT, nC = len(TRACKS), len(PCAR_DEF)
    rc = [_rc(recs.get(str(t)) or {}) for t in range(nT)]
    mas = save.get("mas") or {}
    def xp(c):
        try: return int(mas[str(c)][0])
        except Exception: return 0
    fav = max(range(nC), key=lambda c: (xp(c), sum(c in r for r in rc), -c)) if any(xp(c) for c in range(nC)) else int(save.get("car", 0)) % nC
    try: li = mas_lv(mas[str(fav)])[0]
    except Exception: li = 0
    wl = None
    try:
        rk_data = save.get("rk", [[0]*5 for _ in range(3)])
        total_races = sum(sum(diff) for diff in rk_data)
        if total_races > 0:
            raw_wins = rk_data[0][0] + rk_data[1][0] + rk_data[2][0]
            win_rate = min(100, int(100 * raw_wins / total_races))
            wl = (win_rate, raw_wins, total_races)
    except Exception: pass
    wt = "Thắng"
    done = sum(1 for t in range(nT) if (recs.get(str(t)) or {}).get("best"))
    panel(scr, 10, 6, 300, 180, "HỒ SƠ")
    i, nx = title_of(pts); col = TCOL[i]
    n_ = txt(name or "BẠN", (255, 230, 90), 2); scr.blit(n_, (28, 34))
    if prog >= len(STORY): scr.blit(_crown(), (26 + n_.get_width(), 31))
    scr.blit(badge(i), (26, 53)); scr.blit(txt(T(TITLES[i][1]), col), (46, 54))
    t = txt("%d/%d" % (pts, nx) if nx else "%d" % pts, G); scr.blit(t, (180- t.get_width(), 50))
    rows = (
        ("Giờ đua", "%dh %02dm %02ds" % (secs // 3600, secs // 60 % 60, secs % 60), (255, 255, 255), (90, 90, 130)),
        ("Cốt truyện", ("%d/%d" % (prog, len(STORY)), "%d/%d" % (stars, 3 * len(STORY))), C_AMB, C_AMB),
        (wt, "%d%%  [%d/%d]" % (wl[0], wl[1], wl[2]) if wl else "--", (120, 255, 120) if wl and wl[0] >= 50 else (255, 255, 255), (120, 255, 120)),
        ("Đường đã đua", "%d/%d" % (done, nT), C_CYAN, C_CYAN)
    )
    for k, (lb, v, c, ac) in enumerate(rows):
        y = 82 + k * 19
        scr.blit(txt(lb, G), (27, y - 1))
        if isinstance(v, tuple):
            a, b = txt(v[0], c), txt(v[1], c); x = 180 - b.get_width()
            scr.blit(b, (x, y - 1)); star(scr, x - 8, y + 7, 5, (255, 205, 60)); scr.blit(a, (x - 18 - a.get_width(), y - 1))
        else: t = txt(v, c); scr.blit(t, (180 - t.get_width(), y - 1))
    cx = 246
    t = txt(T("Xe") + ": %d/%d" % (min(own, nC), nC), C_AMB); scr.blit(t, (cx - (t.get_width() >> 1), 31))
    cc = lite(PCAR_DEF[fav][1])
    sp = PREVS[fav][int(tt * 6) % 24 if hint else PA]
    if li == 5:
        pulse = abs(math.sin(tt * 2.5))
        pygame.draw.ellipse(scr, (255, 215, 0), (cx - 35, 87, 70, 16), 1)
        pygame.draw.ellipse(scr, (150, 110, 20), (cx - 35 - 3*pulse, 87 - 1*pulse, 70 + 6*pulse, 16 + 2*pulse), 1)
        cc = C_AMB
    sh = S.shadow_real(sp, sp.get_width(), 140)
    scr.blit(sh, (cx - (sh.get_width() >> 1), 93 - (sh.get_height() >> 1) - 2))
    scr.blit(sp, (cx - (sp.get_width() >> 1), 93 - sp.get_height()))
    if li == 5:
        phase = (tt * 0.8) % 1.0
        if phase < 0.2:
            sz = int(math.sin(phase / 0.2 * math.pi) * 5)
            if sz > 0:
                gx, gy = cx - 10, 93 - sp.get_height() + 10
                pygame.draw.line(scr, (255, 255, 255), (gx - sz, gy), (gx + sz, gy), 1)
                pygame.draw.line(scr, (255, 255, 255), (gx, gy - sz), (gx, gy + sz), 1)
    t = txt(T(PCAR_DEF[fav][0]), cc)
    if li == 5:
        scr.blit(_crown(), (cx - (t.get_width() >> 1) - 16, 103))
    scr.blit(t, (cx - (t.get_width() >> 1), 101))
    t = txt("Thành thạo nhất", C_DIM); scr.blit(t, (cx - (t.get_width() >> 1), 121))
    if hint: hints(scr, 168, (("C", "Lưu ảnh"), ("B", "Quay lại")))
    else: t = txt("OUTDRIVE 199X  %s  %s" % (VSTR, time.strftime("%d/%m/%y %H:%M")), C_DIM); scr.blit(t, ((W - t.get_width()) >> 1, 166))