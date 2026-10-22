import pygame, math, os
DIRS = (("down", 0, 1), ("up", 0, -1), ("left", -1, 0), ("right", 1, 0))
BTN = (("X", "", 262, 24), ("Y", "", 230, 56), ("A", "", 304, 56), ("B", "", 272, 88))
SM, SIDE, RATIO = 150, 100, 1.7
_TOUCH = (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP)
_MOUSE = (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP)
_LOST = tuple(getattr(pygame, n) for n in ("WINDOWFOCUSLOST", "APP_WILLENTERBACKGROUND") if hasattr(pygame, n))
def _cell(c, ox, oy, n):
    s = pygame.Surface((n, n)); s.fill(c); h, a, b, w = n // 2, n * 9 // 32, n * 5 // 32, n // 4
    bx, by = h - ox * b, h - oy * b
    pygame.draw.polygon(s, (235, 235, 245), [(h + ox * a, h + oy * a), (bx + oy * w, by + ox * w), (bx - oy * w, by - ox * w)])
    return s
class TouchPad:
    def __init__(s, w, h, ph=112, buttons=BTN, dpad=None, scale=3, touch=False, font=None, cell=36, tint=None):
        s.w, s.h, s.ph, s.sc0, s.btn, s.cell, s.on = w, h, ph, scale, buttons, cell, None
        s.dp = dpad or (cell * 3 // 2 + 6, ph // 2)
        s.ptr, s.held, s.pressed, s.released = {}, set(), set(), set()
        s.st, s.lab, s.tint = {}, True, tint or {}
        s.vp, s._dst, s._fs, s.canvas = (1, 0, 0), None, False, None
        s.land, s.side, s.vo, s.view, s.bgs, s.ov, s.bt, s.bp, s.pcs = False, SIDE, (SM, 0), None, [], {}, {}, {}, []
        s.kr, s.cl, s.dc = 21, cell, (0, 0)
        s.show(touch)
        s.canvas = pygame.Surface((w + 2 * SM, h + ph)).convert(); s.screen = s.canvas.subsurface((SM, 0, w, h))
        s._art(font or pygame.font.SysFont("tahoma", 12))
    def _wsz(s):
        try: return pygame.display.get_window_size()
        except Exception:
            try: return pygame.display.get_desktop_sizes()[0]
            except Exception: return (1, 1)
    def _want(s):
        ww, wh = s._wsz()
        if not (s.on and ww >= wh * RATIO): return False, s.side
        return True, max(SIDE, min(SM, int((ww / wh * s.h - s.w) / 2)))
    def _place(s):
        w, h, sd = s.w, s.h, s.side
        if not s.on: s.vo, s.view, s.pcs, s.bp, s.kr, s.cl = (SM, 0), s.screen, [], {}, 21, s.cell; return
        if not s.land:
            s.vo, s.view, s.kr, s.cl, s.pcs = (SM, 0), s.canvas.subsurface((SM, 0, w, h + s.ph)), 21, s.cell, [(SM, h, w, s.ph)]
            s.dc = (SM + s.dp[0], h + s.dp[1]); s.bp = {b[0]: (SM + b[2], h + b[3]) for b in s.btn}; return
        s.vo, s.view, s.cl = (SM - sd, 0), s.canvas.subsurface((SM - sd, 0, w + 2 * sd, h)), min(s.cell, (sd - 8) // 3)
        s.pcs = [(SM - sd, 0, sd, h), (SM + w, 0, sd, h)]; s.dc = (SM - sd // 2, h // 2 + 28); s.bp = {}
        if not s.btn: return
        cx = SM + w + sd // 2
        cy = h // 2
        s.kr = 21
        cx = SM + w + sd // 2
        cy = h // 2
        s.kr = 21
        s.bp = {
            "C": (cx-20, cy - 5),
            "A": (cx + 25, cy + 25),
            "B": (cx - 20, cy + 55)
        }
        for b in s.btn:
            if b[0] not in s.bp:
                s.bp[b[0]] = (cx, cy)
    def _art(s, font):
        s._font = font; s._build()
    def _build(s):
        s._place(); s.bgs, s.ov, s.bt = [], {}, {}
        if not s.on: return
        n, r, (px, py), font = s.cl, s.kr, s.dc, s._font
        for i, (x, y, w, h) in enumerate(s.pcs):
            b = pygame.Surface((w, h)); b.fill((14, 12, 28))
            ln = ((0, 0), (w, 0)) if not s.land else (((w - 1, 0), (w - 1, h)) if i == 0 else ((0, 0), (0, h)))
            pygame.draw.line(b, (60, 55, 90), *ln); s.bgs.append((b, (x, y)))
        b0, (x0, y0) = s.bgs[0]
        pygame.draw.rect(b0, (40, 38, 64), (px - x0 - n // 2, py - y0 - n // 2, n, n))
        for d, ox, oy in DIRS:
            pos = (px + ox * n - n // 2, py + oy * n - n // 2)
            b0.blit(_cell((52, 48, 82), ox, oy, n), (pos[0] - x0, pos[1] - y0)); s.ov[d] = (_cell((120, 112, 170), ox, oy, n), pos)
        DEF = ((81, 80, 136), (210, 90, 100))
        for d, cap, *_ in s.btn:
            L = []
            for i, cp in enumerate(cap.split("|")):
                tc = s.tint.get((d, i)); pr = []
                for col in (tc[:2] if tc else DEF):
                    c = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
                    pygame.draw.circle(c, col, (r, r), r - 1); pygame.draw.circle(c, (240, 240, 240), (r, r), r - 1, 1)
                    t = font.render(d, True, (255, 255, 255)); c.blit(t, t.get_rect(center=(r, r))); pr.append(c)
                L.append((pr[0], pr[1], font.render(cp, True, tc[1] if tc else (150, 150, 170))))
            s.bt[d] = (L, *s.bp[d])
    def _layout(s):
        if not s.canvas: return
        win = pygame.display.get_surface(); ww, wh = win.get_size()
        view = s.view; lw, lh = view.get_size()
        sc = min(ww / lw, wh / lh); sc = int(sc) if sc >= 2 else sc
        sz = (int(lw * sc), int(lh * sc)); s.vp = (sc, (ww - sz[0]) // 2, (wh - sz[1]) // 2)
        return win, view, (ww, wh), sz
    def _mode(s):
        s.land, s.side = s._want(); s.ptr.clear(); s._dst = None
        cw, ch = (s.w + 2 * s.side, s.h) if s.land else (s.w, s.h + (s.ph if s.on else 0))
        FS = pygame.FULLSCREEN if "ANDROID_ARGUMENT" in os.environ else 0     # p4a có biến này, Pydroid/PC thì không
        pygame.display.set_mode((cw, ch), pygame.SCALED | (FS or pygame.RESIZABLE))
        pygame.key.stop_text_input()                      # Android: tắt bàn phím ảo tự bật
        if s.canvas: s._build(); s._layout()    
    def show(s, v):
        if v != s.on: s.on = v; s._mode()
    def _cc(s, x, y): sc, ox, oy = s.vp; return (x - ox) / sc + s.vo[0], (y - oy) / sc + s.vo[1]
    def _cv(s, x, y): cx, cy = s._cc(x, y); return cx - SM, cy
    def event(s, e):
        t = e.type
        if t in _TOUCH:
            if not s._fs: s._fs = True; s.ptr.pop("m", None)
            s.show(True); s._layout()
            if t == pygame.FINGERUP: s.ptr.pop(e.finger_id, None)
            elif t == pygame.FINGERDOWN or e.finger_id in s.ptr:
                ww, wh = pygame.display.get_surface().get_size(); s.ptr[e.finger_id] = s._cc(e.x * ww, e.y * wh)
        elif t in _MOUSE:
            if getattr(e, "touch", False):
                if s._fs: return
                s.show(True)
            if not s.on: return
            s._layout()
            if t == pygame.MOUSEBUTTONUP: s.ptr.pop("m", None)
            elif (t == pygame.MOUSEBUTTONDOWN and e.button == 1) or (t == pygame.MOUSEMOTION and e.buttons[0] and "m" in s.ptr):
                s.ptr["m"] = s._cc(*e.pos)
        elif t in _LOST: s.ptr.clear()
    def _read(s):
        out, (px, py), reach, dead, hr = set(), s.dc, s.cl * 2.2, s.cl * 0.3, s.kr + 5
        for x, y in s.ptr.values():
            if SM <= x < SM + s.w and y < s.h: continue
            for n, (bx, by) in s.bp.items():
                if math.hypot(x - bx, y - by) < hr: out.add(n); break
            else:
                dx, dy = x - px, y - py
                if math.hypot(dx, dy) < reach and max(abs(dx), abs(dy)) > dead:
                    out.add(("left" if dx < 0 else "right") if abs(dx) > abs(dy) else ("up" if dy < 0 else "down"))
        return out
    def update(s):
        now = s._read() if s.on else set()
        s.pressed, s.released, s.held = now - s.held, s.held - now, now
    def present(s):
        if s.on and s._want()[0] != s.land: s._mode()
        win, view, wsz, sz = s._layout()
        if s.on:
            c, r = s.canvas, s.kr
            for b, pos in s.bgs: c.blit(b, pos)
            for n, (L, x, y) in s.bt.items():
                i = s.st.get(n, 0)
                if i < 0: continue
                a, b, t = L[i if i < len(L) else 0]
                c.blit(b if n in s.held else a, (x - r, y - r))
                if s.lab: c.blit(t, t.get_rect(center=(x, y + r + 8)))
            for n in s.held:
                if n in s.ov: c.blit(*s.ov[n])
        k = (sz, wsz, s.on, s.land, win)
        if not s._dst or s._dst[0] != k:
            win.fill((0, 0, 0)); s._dst = (k, win.subsurface((s.vp[1], s.vp[2], *sz)))
        pygame.transform.scale(view, sz, s._dst[1]); pygame.display.flip()