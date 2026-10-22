import os, pygame
import array, wave, math, random
MIX = (44100, -16, 2, 1024)
VOL_ADJ = {
    "beep": 0.8,
    "start": 1.0,
    "nitro": 1.0,
    "drift": 0.35,
    "pad": 1.0,
    "star": 0.9,
    "bump": 0.7,
    "lap": 0.8,
    "tick": 0.3,
    "ok": 0.15
}
GAP = {"bump": 0.35, "pad": 0.2, "nitro": 0.1, "drift": 0.15}
KEYS = ("beep", "go", "nitro", "pad", "star", "bump", "drift", "lap", "tick", "ok", "fin", "rev", "cheer", "whoosh")
VOL_ADJ.update(rev=0.9, cheer=0.9, whoosh=0.6)
GAP.update(rev=1.0, cheer=1.0, whoosh=0.3)
SYN = ("rev", "cheer", "whoosh")
VIB = {"bump": (0.8, 70), "whoosh": (0.4, 60)}
SFX, CHAN, _last = {}, {}, {}
_fo = set()
ANDROID = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
SNDMSG = ["Am thanh: chua khoi dong"]
def _synth(k, path):
    fr, _, ch = pygame.mixer.get_init(); r = random.Random(k); n_ = lambda: r.random() * 2 - 1
    if k == "rev":
        N = int(fr * 1.5); out = [0.0] * N; ph = lp = 0.0
        for i in range(N):
            t = i / N; ph = (ph + (50 + 160 * abs(math.sin(6.2832 * t)) ** 1.3) / fr) % 1.0
            lp += 0.2 * ((ph * 2 - 1) + 0.5 * (1 if ph < 0.5 else -1) + 0.15 * n_() - lp)
            out[i] = lp * 0.5 * min(1.0, t * 20, (1 - t) * 5)
    elif k == "cheer":
        N = int(fr * 2.6); out = [0.0] * N; y = 0.0; ev = lambda t: min(1.0, t * 6, (1 - t) * 2.5)
        for i in range(N): y += 0.3 * (n_() - y); out[i] = y * ev(i / N) * 0.35
        for _ in range(150):
            s0 = int(r.random() * (N - 500)); a = r.uniform(0.3, 0.8) * ev(s0 / N) * 0.5
            for j in range(500): out[s0 + j] += n_() * a * (1 - j / 500) ** 3
    else:
        N = int(fr * 0.7); out = [0.0] * N; y = 0.0
        for i in range(N):
            t = i / N; a = 0.03 + 0.5 * t * t; y += a * (n_() - y); out[i] = y * 1.4 * math.sin(3.1416 * t) ** 2
    m = array.array("h")
    for v in out: m.extend((int(max(-1.0, min(1.0, v)) * 30000),) * ch)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with wave.open(path, "wb") as w: w.setnchannels(ch); w.setsampwidth(2); w.setframerate(fr); w.writeframes(m.tobytes())
    except Exception: pass
    return pygame.mixer.Sound(buffer=m.tobytes())
_hp = [None]
def vibe(v=0.7, ms=80):
    if _hp[0] is False or not ANDROID: return
    try:
        if _hp[0] is None:
            from jnius import autoclass, cast
            act = cast("android.app.Activity", autoclass("org.libsdl.app.SDLActivity").getContext())
            _hp[0] = act.getWindow().getDecorView()
        _hp[0].performHapticFeedback(0 if v >= 0.7 else (1 if v >= 0.45 else 3), 3)
    except Exception as e:
        _hp[0] = False; print("[VIBE] tat:", e)
def _vb(name):
    v = VIB.get(name)
    if v: vibe(*v)
ENG, _MV = {}, [1.0]
def init_eng():
    fr, _, ch = pygame.mixer.get_init()
    for k, f in (("e1", 55), ("e2", 130)):
        P = round(fr / f); N = P * max(1, int(f * 0.5)); m = array.array("h"); lp = 0.0
        for i in range(N):
            ph = (i % P) / P
            lp += 0.25 * ((ph * 2 - 1) * 0.6 + (0.25 if ph < 0.5 else -0.25) + math.sin(12.566 * ph) * 0.2 - lp)
            m.extend((int(lp * 12000),) * ch)
        ENG[k] = pygame.mixer.Sound(buffer=m.tobytes())
def engine(v):
    if not ENG or "e1" not in CHAN: return
    for k, vol in (("e1", 0.45 * max(0.0, 1.0 - v * 1.5) if v is not None else 0), ("e2", 0.55 * min(1.0, v * 1.4) if v is not None else 0)):
        c = CHAN[k]
        if v is None:
            if c.get_busy(): c.stop()
            continue
        if not c.get_busy(): c.play(ENG[k], loops=-1)
        c.set_volume(vol * _MV[0] * 0.6)
def init_sfx():
    try:
        if ANDROID: pygame.mixer.quit(); os.environ["SDL_AUDIODRIVER"] = "openslES"
        if not pygame.mixer.get_init():
            try: pygame.mixer.init(*MIX)
            except pygame.error:
                os.environ.pop("SDL_AUDIODRIVER", None); pygame.mixer.init(*MIX)
        here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        d = next((p for p in (os.path.join(here, "sfx"), os.path.join(os.getcwd(), "sfx")) if os.path.isdir(p)), None)
        miss = []
        for k in KEYS:
            for ext in (".wav", ".WAV"):
                p = os.path.join(d, k + ext) if d else ""
                if os.path.exists(p):
                    try: SFX[k] = pygame.mixer.Sound(p)
                    except Exception: miss.append(k)
                    break
            else: miss.append(k)
        for k in [k for k in miss if k in SYN]:
            try: SFX[k] = _synth(k, os.path.join(d or os.path.join(here, "sfx"), k + ".wav")); miss.remove(k)
            except Exception: pass
        pygame.mixer.set_reserved(4)
        CHAN["d"] = pygame.mixer.Channel(0)
        CHAN["n"] = pygame.mixer.Channel(1)
        CHAN["e1"] = pygame.mixer.Channel(2); CHAN["e2"] = pygame.mixer.Channel(3)
        init_eng()
        if miss: print("[CANH BAO] thieu/hong:", miss, "| thu muc:", d)
        SNDMSG[0] = ("Am thanh OK: Da load %d/%d file wav" % (len(SFX), len(KEYS))) if not miss else ("Am thanh thieu: " + ",".join(miss))[:44]
    except Exception as e:
        SNDMSG[0] = "LOI AM THANH: " + str(e)[:44]
def sfx(name, chan=None, loops=0):
    s = SFX.get(name)
    if s is None: return
    if chan and chan in CHAN:
        c = CHAN[chan]
        if chan in _fo: c.stop(); _fo.discard(chan)
        if not c.get_busy(): c.play(s, loops=loops);_vb(name)
        return
    t = pygame.time.get_ticks() / 1000.0
    if t - _last.get(name, -9.0) >= GAP.get(name, 0.08):
        _last[name] = t
        s.play();_vb(name)
def sfx_stop(chan=None):
    if chan is None:
        _fo.clear()
        if pygame.mixer.get_init(): pygame.mixer.stop()
    else:
        c = CHAN.get(chan)
        if c and c.get_busy():
            if chan not in _fo: _fo.add(chan); c.fadeout(250)
        else: _fo.discard(chan)
_cur = [None]
def play_bgm(name):
    if not pygame.mixer.get_init() or _cur[0] == name: return
    _cur[0] = name
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    d = next((p for p in (os.path.join(here, "sfx"), os.path.join(os.getcwd(), "sfx")) if os.path.isdir(p)), here)
    p = os.path.join(d, name + ".ogg")
    if os.path.exists(p):
        try: pygame.mixer.music.load(p); pygame.mixer.music.play(loops=-1)
        except Exception as e: SNDMSG[0] = "BGM: " + str(e)[:40]
    else: SNDMSG[0] = "Thieu " + name + ".ogg"
def stop_bgm():
    _cur[0] = None
    if pygame.mixer.get_init(): pygame.mixer.music.fadeout(1000)
def set_vol(level):
    v = level / 3.0
    _MV[0] = v
    for k, s in SFX.items():
        adj = VOL_ADJ.get(k, 1.0)
        s.set_volume(v * adj)
    for c in CHAN.values():
        c.set_volume(1.0)
    if pygame.mixer.get_init():
        try: pygame.mixer.music.set_volume(v * 0.6)
        except Exception: pass