import pygame, threading, queue, zlib, time, os
try: from lang import T
except Exception: T = lambda s: s
from collections import deque
_raw = getattr(pygame.image, "tobytes", None) or pygame.image.tostring
def _write(fr, size, path, dt, sc, out):
    try:
        n = len(fr); ts = [t for t, _ in fr]
        ms = [min(b - a, dt * 4) for a, b in zip(ts, ts[1:])] + [dt]
        cs, tot, prev = [], 0, 0
        for d in ms:
            tot += d; v = max(20, int(tot / 10 + 0.5) * 10 - prev); cs.append(v); prev += v
        try: from PIL import Image
        except ImportError:
            for i, (_, b) in enumerate(fr):
                pygame.image.save(pygame.image.frombuffer(zlib.decompress(b), size, "RGB"), "%s_%04d.png" % (path[:-4], i)); out["p"] = (i + 1) / n
            out.update(ok=True, msg=T("Đã lưu %d ảnh PNG") % n); return
        def gen():
            for i, (_, b) in enumerate(fr):
                im = Image.frombytes("RGB", size, zlib.decompress(b)).quantize(colors=256, method=2, dither=0)
                if sc > 1: im = im.resize((size[0] * sc, size[1] * sc), Image.NEAREST)
                out["p"] = (i + 1) / n; yield im
        g = gen(); first = next(g)
        first.save(path, save_all=True, append_images=g, duration=cs, loop=0)
        out.update(ok=True, msg=T("Đã lưu: ") + os.path.basename(path))
    except Exception as ex:
        out.update(ok=False, msg=T("Lỗi lưu: ") + type(ex).__name__)
    finally:
        out["done"] = True
class Recorder:
    def __init__(s, surf, fps=30, secs=60, scale=2, folder=".", mode="box", cv=None, font=None, max_mb=60):
        s.surf, s.dt, s.scale, s.folder, s.mode, s.cv = surf, 1000 // fps, scale, folder, mode, cv or s._stretch
        s.lim, s.maxb = secs * 1000, int(max_mb * 1048576)
        s.buf = deque() if mode == "long" else deque(maxlen=fps * secs)
        s.nb, s.nxt, s.th, s.last, s._fs = 0, 0, None, "", False
        s.on = mode != "long"
        s.rect = pygame.Rect(0, 92, 26, 26)
        s.f = font or pygame.font.SysFont("tahoma", 11)
        s.out, s.t0, s._lt, s._bk, s._rc = None, 0, -999, [], {}
        s.toast, s.toast_t, s.toast_ok = "", 0, True
        s.q = queue.Queue(8)
        threading.Thread(target=s._work, daemon=True).start()
    def _work(s):
        while True:
            t, b = s.q.get()
            try: z = zlib.compress(b, 1); s.buf.append((t, z)); s.nb += len(z)
            finally: s.q.task_done()
    @property
    def busy(s): return bool(s.th and s.th.is_alive())
    @property
    def mb(s): return sum(len(b) for _, b in list(s.buf)) / 1048576.0
    def _stretch(s, x, y):
        ww, wh = pygame.display.get_surface().get_size(); w, h = s.surf.get_size()
        return x * w / ww, y * h / wh
    def _say(s, msg, ok=True, ms=2500):
        s.toast, s.toast_ok, s.toast_t = msg, ok, pygame.time.get_ticks() + ms
    def _r(s, txt, col):
        txt = T(txt); k = (txt, col); v = s._rc.get(k)
        if v is None:
            if len(s._rc) > 60: s._rc.clear()
            v = s._rc[k] = s.f.render(T(txt), True, col)
        return v
    def toggle(s):
        if s.busy: s._say("Đang lưu, đợi xíu...", False, 1500); return
        if s.mode != "long": s.save()
        elif s.on: s.on = False; s.save()
        else:
            s.q.join(); s.buf.clear(); s.nb = 0
            s.on = True; s.t0 = s.nxt = pygame.time.get_ticks(); s._say("Bắt đầu quay", True, 1200)
    def event(s, e):
        if e.type == pygame.FINGERDOWN:
            s._fs = True; ww, wh = pygame.display.get_surface().get_size(); p = (e.x * ww, e.y * wh)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if s._fs and getattr(e, "touch", False): return
            p = e.pos
        else: return
        now = pygame.time.get_ticks()
        if now - s._lt < 300: return
        if s.rect.inflate(10, 10).collidepoint(s.cv(*p)): s._lt = now; s.toggle()
    def tick(s):
        if not s.on: return
        t = pygame.time.get_ticks()
        if s.mode == "long" and (t - s.t0 >= s.lim or s.nb >= s.maxb):
            s.on = False; s.save(); s._say("Tự dừng: đủ giới hạn", True, 3500); return
        if t + 6 >= s.nxt:
            s.nxt = max(s.nxt + s.dt, t + s.dt // 2)
            try: s.q.put_nowait((t, _raw(s.surf, "RGB")))
            except queue.Full: pass
    def undraw(s):
        for a, c in reversed(s._bk): s.surf.blit(c, a.topleft)
        s._bk = []
    def draw(s):
        b, r, now = s.surf, s.rect, pygame.time.get_ticks()
        o = s.out
        if o and o.get("done"): s.out = None; s._say(o["msg"], o["ok"], 3500)
        s._bk = []; bsy = s.busy; rec = s.on and s.mode == "long"
        if bsy:
            p = int((s.out or {}).get("p", 0) * 20) * 5
            msg, col = (T("Đang lưu GIF... %d%%") % p if p else T("Đang lưu GIF...")), (255, 170, 0)
        elif now < s.toast_t: msg, col = s.toast, ((110, 230, 120) if s.toast_ok else (255, 110, 100))
        else: msg = None
        if msg:
            a = pygame.Rect(8, 128, b.get_width() - 16, 20); s._bk.append((a, b.subsurface(a).copy()))
            t = s._r(msg, col); p = pygame.Rect(0, 0, t.get_width() + 16, 18); p.center = a.center
            pygame.draw.rect(b, (10, 10, 24), p, border_radius=4); pygame.draw.rect(b, col, p, 1, border_radius=4)
            b.blit(t, t.get_rect(center=p.center))
        s._bk.append((r.copy(), b.subsurface(r).copy()))
        pygame.draw.rect(b, (90, 12, 22) if rec else (14, 12, 28), r, border_radius=3)
        pygame.draw.rect(b, (235, 60, 60) if rec else (150, 150, 170), r, 1, border_radius=3)
        c = (r.centerx, r.y + 9)
        if bsy: pygame.draw.circle(b, (255, 170, 0), c, 4)
        elif rec: pygame.draw.circle(b, (240, 40, 40) if (now // 400) & 1 == 0 else (110, 25, 35), c, 4)
        else: pygame.draw.circle(b, (235, 60, 60) if s.mode != "long" else (150, 150, 170), c, 4)
        col = (240, 240, 240)
        if rec:
            e = (now - s.t0) // 1000; lb = "%d:%02d" % (e // 60, e % 60)
            if s.lim - (now - s.t0) < 10000 or s.nb > s.maxb * 0.85: col = (255, 170, 0)
        else: lb = "REC" if s.mode == "long" else "LƯU"
        t = s._r(lb, col); b.blit(t, t.get_rect(center=(r.centerx, r.y + 19)))
    def _save(s, path, out):
        s.q.join()
        _write(list(s.buf), s.surf.get_size(), path, s.dt, s.scale, out)
    def save(s, name=None):
        if s.busy: return False
        if not s.buf and s.q.empty(): s._say("Chưa có gì để lưu", False); return False
        rec_dir = os.path.join(s.folder, "records")
        os.makedirs(rec_dir, exist_ok=True)
        s.last = os.path.join(rec_dir, name or time.strftime("rec_%H%M%S.gif"))
        s.out = {}
        s.th = threading.Thread(target=s._save, args=(s.last, s.out)); s.th.start(); return True