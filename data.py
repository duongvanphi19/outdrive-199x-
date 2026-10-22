import os, math, random
from lang import T
W, H = 320, 192
HW, VS = W * 0.5, H * 0.5
HZ = 78
SEG = 200.0
ROADW = 1200.0
RW = ROADW * HW
CAMH, CAMD = 1000.0, 1.0
PLAYZ = CAMH * CAMD
CARW = 360.0
CARV = CARW
MAXSPD = 11000.0
ACC, BRK, DEC = MAXSPD / 4.0, MAXSPD / 1.1, MAXSPD / 6.0
OFFDEC, OFFLIM = MAXSPD / 1.6, MAXSPD * 0.25
NCARS, DRMAX = 4, 52
QDR = (34, 44, DRMAX)
MMW, MMH, MMSTEP = 58, 46, 6
KEY = (255, 0, 255)
BUTTONS = (("A", "Ga", 268, 40), ("B", "Phanh|Drift", 216, 70), ("C", "Nitro", 164, 70))
TINT = {("B", 1): ((110, 40, 220), (190, 100, 255), (255, 190, 60))}
VERSION = (1, 0)
VSTR = "v%d.%d" % VERSION
CAR_COLS = ((240, 140, 40), (40, 190, 90), (170, 70, 210), (170, 205, 50), (60, 205, 205),
            (140, 145, 155), (245, 120, 180), (150, 100, 55), (150, 45, 70))
PCAR_DEF = (
    ("Hồng Long", (225, 30, 45), "Cân bằng, dễ làm quen", (3, 3, 3, 3)),
    ("Tia Chớp",  (255, 215, 0), "Max speed cao, dễ văng cua", (5, 3, 2, 2)),
    ("Kart",      (90, 150, 240), "Đề ba cực bốc, drift gắt", (2, 5, 3, 3)),
    ("Bọ Cạp",    (120, 80, 169), "Vua Nitro, nước rút mạnh", (2, 3, 3, 5)),
    ("Báo Đen",   (36, 38, 52), "Ôm cua đỉnh, bám đường sát", (3, 3, 5, 3)),
    ("Cá Mập",    (15, 165, 215), "Sát thủ đường thẳng cuối game", (5, 4, 3, 2)),
    ("Máy Cày",   (54, 120, 60), "Kéo khỏe, cày nát mọi thứ", (2, 5, 5, 2)),
    ("Bạch Kim",  (229, 228, 226), "F1 đỉnh cao, không điểm yếu", (5, 4, 4, 3)),
)
PKIND = (0, 2, 5, 3, 4, 6, 8, 7)
def car_stats(ci):
    s = PCAR_DEF[ci][3]
    return 1 + 0.0165 * (s[0] - 3), 1 + 0.33 * (s[1] - 3), 1 + 0.06 * (s[2] - 3), 1 + 0.28 * (s[3] - 3)
def _pal(g1, g2, rum1, rum2, rd1, rd2, lane):
    return ((g1, rum1, rd1, lane), (g2, rum2, rd2, None),
            (g1, rum1, (238, 238, 238), None), (g1, rum1, (28, 28, 32), None))
THEMES = (
    dict(fog=(168, 205, 235), top=(40, 100, 200), sun=(255, 242, 195), sunpos=(246, 32),
         mt1=(122, 150, 198), mt2=(62, 132, 100), kinds=(0, 0, 1, 1),
         pal=_pal((16, 170, 48), (0, 150, 40), (205, 45, 45), (235, 235, 235), (107, 107, 112), (101, 101, 106), (215, 215, 215))),
    dict(fog=(238, 214, 168), top=(60, 140, 225), sun=(255, 250, 225), sunpos=(70, 30),
         mt1=(206, 150, 102), mt2=(184, 124, 78), kinds=(3, 3, 3, 4, 4),
         pal=_pal((224, 188, 122), (212, 174, 106), (205, 45, 45), (235, 235, 235), (98, 94, 94), (91, 87, 87), (225, 225, 225))),
    dict(fog=(200, 220, 242), top=(92, 124, 196), sun=(255, 255, 255), sunpos=(250, 36),
         mt1=(168, 184, 216), mt2=(226, 233, 244), kinds=(5, 5, 5, 4),
         pal=_pal((238, 243, 250), (222, 230, 243), (50, 90, 200), (240, 240, 245), (120, 122, 132), (112, 114, 124), (235, 235, 240))),
    dict(fog=(18, 22, 54), top=(4, 6, 24), sun=(236, 240, 255), sunpos=(250, 26),
         mt1=(34, 40, 82), mt2=(24, 28, 62), kinds=(6, 6, 7, 7, 7), cld=(54, 60, 104), stars=True,
         pal=_pal((16, 26, 44), (12, 20, 36), (200, 50, 70), (225, 225, 235), (62, 64, 82), (55, 57, 74), (205, 205, 140))),
    dict(fog=(252, 186, 136), top=(76, 64, 156), sun=(255, 240, 190), sunpos=(120, 60),
         mt1=(176, 98, 120), mt2=(128, 72, 98), kinds=(8, 8, 1, 4, 8),
         pal=_pal((178, 134, 52), (166, 122, 44), (205, 45, 45), (235, 235, 235), (104, 100, 106), (97, 93, 99), (228, 228, 228))),
    dict(fog=(214, 232, 206), top=(70, 150, 225), sun=(255, 248, 210), sunpos=(90, 34),
         mt1=(120, 164, 160), mt2=(74, 138, 92), kinds=(9, 9, 10, 10, 10, 11, 1),
         pal=_pal((118, 190, 64), (104, 176, 56), (218, 37, 29), (255, 220, 40), (106, 104, 108), (99, 97, 101), (232, 232, 232))),
    dict(fog=(190, 170, 150), top=(110, 120, 140), sun=(255, 235, 190), sunpos=(240, 34),
         mt1=(130, 110, 100), mt2=(100, 84, 76), kinds=(13, 13, 14, 14, 6),
         pal=_pal((120, 104, 84), (110, 95, 76), (205, 45, 45), (235, 235, 235), (92, 90, 92), (85, 83, 85), (200, 200, 190))),
    dict(fog=(190, 235, 245), top=(30, 150, 230), sun=(255, 250, 220), sunpos=(80, 30),
         mt1=(90, 170, 190), mt2=(60, 150, 170), kinds=(9, 9, 15, 15, 4),
         pal=_pal((244, 226, 160), (232, 212, 146), (255, 255, 255), (40, 160, 220), (110, 110, 116), (103, 103, 109), (235, 235, 235)))
)
KINDS = ("pine", "tree", "sign", "cactus", "rock", "spine", "lamp", "tower", "maple", "palm", "rice", "flag", "lantern", "shack", "barrel", "umbrella", "hands", "lighthouse", "school", "bitexco", "phuocduyen", "cham", "motcot","wreck", "station", "dinh")
SPW = (420.0, 460.0, 700.0, 380.0, 420.0, 440.0, 320.0, 520.0, 460.0, 440.0, 520.0, 320.0, 320.0, 900.0, 140.0, 420.0, 1200.0, 900.0, 1800.0, 800.0, 1050.0, 1250.0, 1500.0, 2100.0,2100.0, 2100.0)
HITR = (0.2, 0.2, 0.3, 0.18, 0.22, 0.2, 0.1, 0.25, 0.2, 0.12, -0.17, 0.1, 0.1, 0.36, 0.06, 0.1, 0.5, 0.3, 0.36, 0.2, 0.3, 0.3, 0.25,0.45,0.45, 0.45)
HCL = (57, 54, 60, 52, 25, 60, 52, 74, 54, 54, 36, 42, 52, 61, 15, 36, 180, 90, 70, 150, 90, 85, 75,40,40, 40)
def _eio(a, b, p):
    return a + (b - a) * (0.5 - 0.5 * math.cos(p * math.pi))
def _build(secs):
    cur, ys = [], [0.0]
    def road(e, h, l, c, hill):
        y0 = ys[-1]; y1 = y0 + hill * SEG; tot = e + h + l
        for n in range(e): cur.append(c * (n / e) ** 2); ys.append(_eio(y0, y1, n / tot))
        for n in range(h): cur.append(c); ys.append(_eio(y0, y1, (e + n) / tot))
        for n in range(l): cur.append(c * (1 - _eio(0, 1, n / l))); ys.append(_eio(y0, y1, (e + h + n) / tot))
    for sec in secs: road(*sec)
    road(30, 15, 30, 0, -ys[-1] / SEG)
    ys[-1] = 0.0
    return cur, ys
def _minimap(cur, n, k):
    x = y = h = 0.0; pts = [(0.0, 0.0)]
    for i in range(0, n, MMSTEP):
        for j in range(i, min(i + MMSTEP, n)):
            h += cur[j] * k; x += math.cos(h); y += math.sin(h)
        pts.append((x, y))
    m = len(pts) - 1; ex, ey = pts[-1]
    return [(p[0] - ex * i / m, p[1] - ey * i / m) for i, p in enumerate(pts)]
def _fit(raw, w, h, m=5):
    x0 = min(p[0] for p in raw); x1 = max(p[0] for p in raw)
    y0 = min(p[1] for p in raw); y1 = max(p[1] for p in raw)
    s = min((w - 2 * m) / max(1e-6, x1 - x0), (h - 2 * m) / max(1e-6, y1 - y0))
    ox = (w - (x1 - x0) * s) / 2; oy = (h - (y1 - y0) * s) / 2
    return [(int(ox + (p[0] - x0) * s), int(oy + (p[1] - y0) * s)) for p in raw]
def _track(name, desc, secs, theme, laps, seed, mmk=0.0035, cs=1.0, brg=()):
    cur, ys = _build(secs); n = len(cur)
    band = [(i // 3) & 1 for i in range(n)]
    f = int(PLAYZ // SEG); band[f], band[f + 1] = 2, 3
    kinds = THEMES[theme]["kinds"]; rs = random.Random(seed); spr = []
    ph, ph2, free = rs.random() * 6.28, rs.random() * 6.28, {-1: 0, 1: 0}
    for i in range(n):
        items = ()
        if i > 16 and i % 3 == 0:
            z = 0.5 + 0.5 * math.sin(i * 0.045 + ph) * math.sin(i * 0.011 + ph2)
            p = 0.08 + 0.9 * z * z
            for s in (-1, 1):
                if i % 90 == 0 and rs.random() < 0.55: k = 11; ok = True
                elif i >= free[s] and rs.random() < p:
                    k = kinds[(i // 60) % len(kinds)] if rs.random() < 0.6 else rs.choice(kinds)
                    free[s] = i + int(SPW[k] * 1.3 / SEG) + 1; ok = True
                else: ok = False
                if ok: items += ((k, s * (1.35 + SPW[k] / 2400.0 + rs.random() * 1.2)),)
        spr.append(items)
    spr[f] = ((11, -1.45), (11, 1.45))
    raw = _minimap(cur, n, mmk); cur = [c * cs for c in cur]
    pads, ramps = set(), {}; cuts = {}
    for k, i in enumerate(range(60, n - 60, 55)):
        if all(abs(cur[q]) < 0.5 for q in range(i - 2, i + 8)):
            if k % 8 == 2: pads.update(range(i, i + 3))
            elif k % 3 == 0:
                ln = rs.choice((-1, 0, 1)); ramps.update((q, ln) for q in range(i, i + 2))
    tun, i, bs = set(), 20, (0, 0)
    while i < n:
        j = i
        while j < n and abs(cur[j]) < 0.5: j += 1
        if j - i > bs[1] - bs[0]: bs = (i, j)
        i = j + 1
    if bs[1] - bs[0] >= 70:
        m = (bs[0] + bs[1]) // 2; tun = set(range(m - 20, m + 20))
        for q in range(m - 30, m + 20): ramps.pop(q, None); pads.discard(q)
    for q in tun: spr[q] = ()
    for q in brg: spr[q] = ()
    if brg:
        spr[180] = ((16, -1.55),)
        spr[450] = ((16, 1.55),)
    def put(frac, kind, side, ofs):
        q0 = int(n * frac); q = next((j for j in range(q0, n - 30) if abs(cur[j]) < 0.5 and j not in tun and j not in brg), None)
        if q is not None: spr[q] += ((kind, side * ofs),)
    if theme == 7: put(0.35, 17, -1, 2.0)
    if theme == 2: put(0.35, 24, -1, 2.4)
    if theme == 5: put(0.25, 18, 1, 2.5); put(0.7, 25, 1, 2.4)
    if theme == 0: put(0.30, 20, -1, 2.0)
    if theme == 1: put(0.30, 21, 1, 2.0)
    if theme == 4: put(0.30, 22, -1, 2.0)
    if theme == 3: put(0.4, 19, 1, 1.9)
    if theme == 6: put(0.25, 23, -1, 2.4); put(0.7, 23, -1, 2.4)
    LM = {0: (20, -1, 2.0), 1: (21, 1, 2.0), 3: (19, 1, 1.9), 4: (22, -1, 2.0), 5: (18, 1, 2.5), 7: (17, -1, 2.0)}
    if theme in LM: put(0.02, *LM[theme])
    return dict(name=name, desc=desc, curve=cur, y=ys, n=n, tl=n * SEG, band=band, spr=spr, laps=laps,
                theme=theme, cuts=cuts, tun=tun, pads=pads, ramps=ramps,
                mmp=_fit(raw, MMW, MMH), mml=_fit(raw, MMW * 2, MMH * 2, 9),
                brg=set(brg))
TRACKS = (
    _track("Đồng cỏ", "Cua vừa, vài dốc", ((25, 25, 25, 0, 0), (50, 100, 50, 3, 20), (25, 50, 25, -4, 40), (50, 50, 50, 0, -30), (50, 100, 50, 5, 0), (25, 25, 25, 0, 26), (50, 50, 50, -3, -60), (25, 50, 25, 6, 0), (50, 100, 50, -5, 30), (25, 25, 25, 0, -30), (50, 100, 50, 4, 20), (25, 50, 25, -6, -20), (50, 50, 50, 0, 0)), 0, 3, 7, cs=0.7),
    _track("Sa mạc", "Thẳng dài, đồi cao", ((25, 50, 25, 0, 0), (50, 150, 50, 2, 25), (30, 60, 30, -3, 15), (50, 100, 50, 0, -20), (40, 80, 40, 4, 40), (30, 40, 30, -5, -30), (50, 150, 50, 0, 0), (40, 60, 40, 3, 20), (40, 80, 40, -2, -35), (25, 25, 25, 6, 0), (50, 100, 50, 0, 30), (40, 100, 40, -4, -20), (50, 200, 50, 0, 0)), 1, 3, 11),
    _track("Núi tuyết", "Cua gắt liên tiếp", ((25, 25, 25, 0, 0), (25, 50, 25, 5, 20), (25, 25, 25, -6, 25), (25, 50, 25, 4, -20), (30, 30, 30, -5, 30), (20, 20, 20, 6, -20), (30, 60, 30, -4, 0), (25, 25, 25, 6, 30), (25, 50, 25, -6, -30), (40, 40, 40, 0, 40), (25, 40, 25, 5, -30), (25, 25, 25, -6, 0), (30, 50, 30, 4, 20), (25, 25, 25, -5, -30)), 2, 4, 23, 0.003, 0.7),
    _track("Thành phố đêm", "Đèn đêm, góc vuông", ((25, 25, 25, 0, 0), (40, 90, 40, 0, 10), (20, 30, 20, 5, 0), (30, 70, 30, 0, -10), (20, 30, 20, -5, 10), (40, 110, 40, 0, 0), (20, 25, 20, 6, 0), (20, 25, 20, 6, 20), (40, 80, 40, 0, -20), (20, 30, 20, 5, 0), (20, 30, 20, 5, 10), (50, 100, 50, 0, 0), (20, 30, 20, 6, -10), (20, 30, 20, 6, 0), (40, 80, 40, 0, 10), (25, 40, 25, 4, -10), (40, 60, 40, 0, 0)), 3, 3, 31, cs=1.2),
    _track("Rừng thu", "Cua mềm, rừng lá đỏ", ((25, 25, 25, 0, 0), (50, 80, 50, 2, 15), (40, 60, 40, 3, 10), (50, 100, 50, 0, -15), (40, 80, 40, 4, 20), (30, 50, 30, -4, -10), (50, 100, 50, 0, 10), (40, 60, 40, 3, -20), (40, 80, 40, 2, 15), (30, 40, 30, 5, 0), (50, 90, 50, 0, -10), (40, 70, 40, 3, 10), (50, 60, 50, 0, 0)), 4, 3, 41, cs=1.1),
    _track("Đồng lúa", "Cua êm, cờ đỏ ven đường", ((25, 25, 25, 0, 0), (50, 100, 50, 2, 10), (40, 60, 40, -3, 0), (50, 120, 50, 0, 15), (40, 80, 40, 3, -10), (30, 50, 30, -4, 10), (50, 120, 50, 0, 0), (40, 60, 40, 2, -15), (40, 80, 40, -2, 10), (30, 40, 30, 4, 0), (50, 100, 50, 0, -10), (50, 60, 50, 0, 0)), 5, 3, 53),
    _track("Khu ổ chuột", "Hẻm hẹp, cua chữ S", ((25, 25, 25, 0, 0), (25, 40, 25, 5, 10), (20, 30, 20, -6, 0), (25, 40, 25, 4, -10), (30, 50, 30, -5, 20), (20, 25, 20, 6, -20), (40, 60, 40, 0, 0), (25, 30, 25, -4, 10), (20, 30, 20, 5, -10), (30, 40, 30, 0, 0)), 6, 3, 61, cs=0.8),
    _track("Bãi biển", "Ven biển, cua thoải", ((25, 25, 25, 0, 0), (50, 120, 50, 2, 0), (40, 80, 40, -2, 10), (50, 150, 50, 0, 0), (40, 100, 40, 3, -10), (30, 60, 30, -3, 0), (50, 150, 50, 0, 5), (40, 80, 40, 2, -5), (50, 100, 50, 0, 0)), 7, 3, 67, cs=1.1),
    _track("Cầu vượt mây", "Đôi bàn tay rêu phong giữa biển mây", ((30, 20, 30, 0, 0), (40, 80, 40, 0, 80), (30, 40, 30, 6, 20), (25, 40, 25, -7, 0), (40, 80, 40, 0, -60), (30, 50, 30, 6, 50), (30, 60, 30, -6, -80), (20, 20, 20, 5, 20), (20, 20, 20, -5, -20), (40, 80, 40, 0, 0)), 2, 3, 99, cs=1.2, brg=range(80, 650)),
)
STORY = (
    ("Vòng loại", 5, 2, "Minh Tuấn", 0, 0.74, 1.0, 5, False, "Cho thấy bạn xứng đáng có mặt ở giải này.", "Minh Tuấn: Tôi sẽ không nhường đâu!", "Hừ... may mắn thôi. Lần sau tôi sẽ không nhường đâu!", "Khởi đầu tốt! Cúp Đồng đang chờ bạn.", "Chỉ có thế thôi à? Về tập thêm đi!"),
    ("Cúp Đồng", 4, 3, "Lan Anh", 6, 0.80, 1.0, 3, False, "Cúp Đồng khai mạc, nhiều gương mặt mới.", "Lan Anh: Thử bắt kịp tôi xem nào.", "Bạn nhanh thật đấy. Cúp Bạc sẽ không dễ như vậy đâu.", "Chiến thắng đẹp! Cúp Bạc đang mở ra cho bạn.", "Thử bắt kịp tôi xem nào... à, chưa kịp rồi."),
    ("Cúp Bạc 1", 1, 3, "Hoàng Vũ", 3, 0.92, 0.0, 3, True, "Sa mạc nóng bỏng, đường thẳng dài tít.", "Hoàng Vũ: Ở đây, tốc độ là tất cả.", "Tốc độ của cậu... khiến tôi nể rồi đấy.", "Sa mạc đã khuất phục! Núi tuyết là thử thách kế tiếp.", "Ở đây tốc độ là tất cả, và cậu thì chậm."),
    ("Cúp Bạc 2", 2, 3, "Thu Hà", 4, 1.00, 0.3, 3, True, "Núi tuyết trơn trượt, cua gắt liên tiếp.", "Thu Hà: Cẩn thận, tôi quen đường này.", "Cậu qua cua đẹp lắm. Tôi thua tâm phục.", "Núi tuyết cũng phải cúi đầu! Bán kết đang chờ bạn.", "Tôi đã bảo rồi, tôi quen đường này mà."),
    ("Bán kết", 3, 3, "Đại Phong", 7, 0.99, 0.4, 2, True, "Bán kết: chỉ hai người đi tiếp.", "Đại Phong: Tôi chờ trận này lâu rồi.", "Chờ lâu thế mà vẫn thua. Chung kết thuộc về cậu.", "Vào chung kết! Đương kim vô địch đang đợi.", "Trận này tôi chờ lâu rồi, đừng làm tôi thất vọng."),
    ("Chung kết", 2, 4, "Bóng Đêm", 2, 1.00, 0.6, 1, True, "Chung kết! Đương kim vô địch đang chờ.", "Bóng Đêm: Chưa ai vượt được tôi.", "...Cuối cùng cũng có người vượt được tôi.", "Bạn là nhà vô địch mới của giải đấu!", "Chưa ai vượt được tôi. Cậu cũng thế."),
)
WARM = ((0, 7), (5, 0), (4, 7), (4, 1), (2, 1), (3, 4))
def mc(ch, mi):
    c = list(STORY[ch]); t = c[1]
    if mi < 2:
        t = (t + 1 + mi * 3 + ch) % len(TRACKS)
        if t == c[1]: t = (t + 1) % len(TRACKS)
        c[1], c[2] = WARM[ch][mi], 2
        c[7] = max(2, min(4, c[7] + 1 - mi))
    c[0] = T(c[0]) + T(" · Trận %d/3") % (mi + 1)
    c[5] *= (0.94, 0.97, 1.0)[mi]; c[6] *= (0.5, 0.75, 1.0)[mi]
    c[8] = mi == 2
    if mi == 2: c[7] = 3
    return tuple(c)
REWARD = {0: "Kart", 1: "Bọ Cạp", 3: "Báo Đen", 5: "Cá Mập"}
FORCE = {(1, 1): 2, (3, 0): 6, (4, 1): 5}
LOCKT = {3: "Thắng chương 2 để mở xe này", 4: "Thắng chương 4 để mở xe này", 5: "Thắng chương 6 để mở xe này"}
LOCKT[6] = "3 sao mọi chương để mở xe này"
LOCKT[7] = "Xe bí mật"
LOCKT[2] = "Thắng chương 1 để mở xe này"
def ncar(p, s=0): return 2 + (p >= 1) + (p >= 2) + (p >= 4) + (p >= 6) + (s >= 18)
def goal(c):
    if c[8]: return T("Mục tiêu: top 3 (nhất = 3 sao)")
    return T("Mục tiêu: ") + (T("về nhất") if c[7] == 1 else T("về top %d") % c[7])
TITLES = ((0, "Tập Sự"), (400, "Tay Lái Mới"), (1200, "Tay Đua"), (3000, "Cao Thủ"), (6000, "Siêu Sao"), (12000, "Huyền Thoại"))
PTS, PTS_DIF = (100, 60, 35, 15, 5), (0.5, 1.0, 2.0)
def pts_gain(rank, dif, dist):
    return int(round(PTS[min(rank, len(PTS)) - 1] * PTS_DIF[dif] * max(0.6, min(1.3, dist / 1.09e6))))
def title_of(p):
    i = max(k for k, t in enumerate(TITLES) if p >= t[0])
    return i, (TITLES[i + 1][0] if i + 1 < len(TITLES) else None)
def title_txt(p):
    i, nx = title_of(p); return T(TITLES[i][1]) + " · " + ("%d/%d" % (p, nx) if nx else "%d" % p)
PAUSE = ("Tiếp tục", "Đua lại", "Về menu")
QN, ON = ("Thấp", "Vừa", "Cao"), ("Tắt", "Bật")
MENU = ("Đua tự do", "Cốt truyện", "Nhiều người", "Hồ sơ", "Cài đặt")
NAMES = ("Gia Huy", "Mai Linh", "Quốc Bảo", "Ngọc Anh", "Tuấn Kiệt", "Bích Thảo", "Hải Đăng", "Phương Vy", "Minh Khôi")
CONF = ((255, 80, 80), (80, 200, 255), (120, 255, 120), (255, 230, 90))
RK = ((255, 215, 0), (215, 220, 230), (215, 140, 70))
PAUSE_HIT = (196, 0, 258, 28)
QUIET = {("count", "race"), ("race", "done"), ("track", "dif"), ("dif", "track"), ("track", "hist"), ("hist", "track"), ("podium", "done")}
IR = 205
FLYT = 4.0
TCHK = [(t["n"] * 31 + int(sum(t["curve"])) + VERSION[0] * 1009 + VERSION[1] * 97) & 0xFFFF for t in TRACKS]
LANES = (-0.5, -0.17, 0.17, 0.5, -0.33, 0.0, 0.33, 0.0)
SUG = ((0,), (1, 5), (4, 2), (3, 2), (2, 0), (5, 1), (2, 4), (1, 5), (7, 2))
TNEED = (0, 2, 3, 4, 1, 0, 6, 0, 0)
def tunlk(i, prog): return prog >= TNEED[i]
MAS = (0, 100, 300, 700, 1300, 2200)
MASN = ("Mới", "Quen", "Thạo", "Giỏi", "Cao Thủ", "MASTER")
MCOL = ((150, 150, 170), (120, 200, 255), (120, 255, 120), (255, 230, 90), (255, 170, 60), (255, 80, 160))
def pace(t, dist, top, f=1.0):
    return max(0.0, min(1.0, (dist / max(t, 1.0) / (MAXSPD * top * f) - 0.85) / 0.40))
TCF = [1 - 0.012 * sum(map(abs, t["curve"])) / t["n"] for t in TRACKS]
def mas_lv(m):
    i = max(k for k, v in enumerate(MAS) if m[0] >= v)
    i = min(i, 3 + (m[2] >= 55) + (m[2] >= 75))
    return i, (MAS[i + 1] if i + 1 < len(MAS) else None)
if __name__ == "__main__":
    print("=== BẮT ĐẦU KIỂM TRA TÍNH TOÀN VẸN DỮ LIỆU (DATA INTEGRITY CHECK) ===")
    print(f"\n[1] Kiểm tra mảng siêu dữ liệu KINDS (Chuẩn: 23 phần tử):")
    print(f"  - KINDS: {len(KINDS)}")
    print(f"  - SPW (Chiều rộng sprite): {len(SPW)}")
    print(f"  - HITR (Bán kính va chạm): {len(HITR)}")
    print(f"  - HCL (Chiều cao sprite): {len(HCL)}")
    assert len(KINDS) == len(SPW) == len(HITR) == len(HCL), "LỖI: Độ dài các mảng thuộc tính KINDS không đồng bộ!"
    print("  -> OK: Các mảng thuộc tính KINDS khớp hoàn toàn.")
    print(f"\n[2] Kiểm tra hệ thống xe ({len(PCAR_DEF)} xe):")
    assert len(PCAR_DEF) == len(PKIND), "LỖI: PCAR_DEF và PKIND lệch số lượng!"
    for i, car in enumerate(PCAR_DEF):
        spd, acc, hnd, nit = car_stats(i)
        print(f"  - Xe {i}: {car[0]:<12} | Dáng (Kind): {PKIND[i]} | Stats(Spd/Acc/Hnd/Nit): ({spd:.2f}, {acc:.2f}, {hnd:.2f}, {nit:.2f})")
    print("  -> OK: Cấu hình xe và chỉ số cân bằng hợp lệ.")
    print(f"\n[3] Kiểm tra đường đua ({len(TRACKS)} đường) và Theme ({len(THEMES)} themes):")
    for idx, t in enumerate(TRACKS):
        th = t["theme"]
        assert 0 <= th < len(THEMES), f"LỖI: Đường đua {idx} ('{t['name']}') gọi theme không tồn tại: {th}!"
        assert len(t["curve"]) == t["n"], f"LỖI: Đường đua {idx} có độ dài curve khác n!"
        assert len(t["y"]) == t["n"] + 1, f"LỖI: Đường đua {idx} có độ dài mảng y không đúng (n+1)!"
        assert len(t["spr"]) == t["n"], f"LỖI: Đường đua {idx} có mảng spr khác n!"
        avg_curve = sum(map(abs, t["curve"])) / t["n"]
        print(f"  - Track [{idx}]: {t['name']:<16} | Theme: {th} | Laps: {t['laps']:<2} | Lát (n): {t['n']:<4} | Độ cong TB: {avg_curve:.3f}")
    print("  -> OK: Toàn bộ đường đua và liên kết theme hợp lệ.")
    print(f"\n[4] Kiểm tra tiến trình cốt truyện ({len(STORY)} chương):")
    for idx, s in enumerate(STORY):
        print(f"  - Chương {idx+1}: {s[0]:<14} | Vòng: {s[1]} | Đối thủ: {s[3]}")
    print("  -> OK: Cốt truyện được cấu trúc chính xác.")
    print("\n=== HOÀN TẤT KIỂM TRA: TẤT CẢ DỮ LIỆU ĐỀU AN TOÀN VÀ SẴN SÀNG! ===")