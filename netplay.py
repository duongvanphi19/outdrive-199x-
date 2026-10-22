import socket, struct, time
PORT, VER, MAXP = 47474, 3, 4
MAGIC = b"OD"
H = struct.Struct("<2sBB")
(T_BEACON, T_JOIN, T_ACCEPT, T_REJECT, T_LOBBY, T_START,
 T_STATE, T_WORLD, T_LEAVE, T_KEEP) = range(1, 11)
S_BEACON = struct.Struct("<16sBBBBH8s")
S_JOIN = struct.Struct("<16sBI")
S_ACCEPT = struct.Struct("<BB")
S_LOBBY = struct.Struct("<BHBB")
S_PLAYER = struct.Struct("<B16sBBI")
S_START = struct.Struct("<BBH")
S_STATE = struct.Struct("<BHfffbBf")
S_KEEP = struct.Struct("<BBBI")
S_ID = struct.Struct("<B")
F_BOOST, F_DRIFT, F_FIN = 1, 2, 4
TIMEOUT_RACE, TIMEOUT_LOBBY = 3.0, 6.0
class Remote:
    __slots__ = ("D", "px", "spd", "slip", "flags", "ftime", "t", "seq")
    def __init__(s):
        s.D = s.px = s.spd = s.slip = s.ftime = s.t = 0.0
        s.flags, s.seq = 0, -1
class Net:
    def __init__(s, port=PORT):
        s.port = port
        s.sock = s.bsock = None
        s.err = None
        try:
            from data import VSTR; s.vstr = VSTR
        except Exception: s.vstr = ""
        s.pts = 0
        s.reset()
    def reset(s):
        s.state = "idle"; s.is_host = False; s.me = 0
        s.name = "Racer"; s.car = 0; s.ip = "127.0.0.1"
        s.old = 0
        s.rooms, s.roster, s.players, s.remote = {}, [], {}, {}
        s.track = s.chk = 0
        s.racing = s.room_racing = False
        s.host_addr = None; s.race_id = 0; s._seen = -1; s._go = None
        s._seq = 0; s._start_left = 0; s._bcast = ()
        s._t_beacon = s._t_lobby = s._t_send = s._t_keep = s._t_join = s._t_start = -9.0
        s._join_t0 = -1.0; s._last_rx = 0.0; s.ready = 0
    @property
    def active(s):
        return s.sock is not None or s.bsock is not None
    def close(s):
        for k in (s.sock, s.bsock):
            if k is not None:
                try: k.close()
                except Exception: pass
        s.sock = s.bsock = None
        s.reset()
    def _fail(s, msg):
        o = s.old; s.err = msg + (" (khác phiên bản)" if o else ""); s.close()
    @staticmethod
    def local_ip():
        for dst in (("8.8.8.8", 80), ("10.255.255.255", 1), ("192.168.255.255", 1)):
            k = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                k.connect(dst); ip = k.getsockname()[0]
                if ip and not ip.startswith("0."): return ip
            except Exception:
                pass
            finally:
                k.close()
        return "127.0.0.1"
    @staticmethod
    def _mk(port, reuse):
        k = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            if reuse:
                k.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if hasattr(socket, "SO_REUSEPORT"):
                    try: k.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    except Exception: pass
            try: k.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except Exception: pass
            k.bind(("", port)); k.setblocking(False)
        except Exception:
            k.close(); raise
        return k
    def host(s, name, track, car, chk):
        s.close(); s.err = None
        try: k = s._mk(s.port, True)
        except Exception: s.err = "Không mở được cổng mạng"; return False
        s.sock = k; s.is_host = True; s.me = 0; s.name = name; s.car = car
        s.track, s.chk = track, chk; s.roster = [[0, name, car, 1, max(0, int(s.pts))]]; s.state = "lobby"
        s.ip = s.local_ip()
        s._bcast = ("255.255.255.255",) + (() if s.ip.startswith("127.") else (s.ip.rsplit(".", 1)[0] + ".255",))
        return True
    def browse(s):
        s.close(); s.err = None
        try: s.bsock = s._mk(s.port, True)
        except Exception: s.err = "Không mở được cổng mạng"; return False
        s.state = "browse"
        return True
    def join(s, addr, name, car):
        s.close(); s.err = None
        try: s.sock = s._mk(0, False)
        except Exception: s.err = "Không mở được cổng mạng"; return False
        s.host_addr = addr if isinstance(addr, tuple) else (addr, s.port)
        s.name, s.car, s.state = name, car, "joining"
        return True
    def leave(s):
        if s.sock is not None and s.state in ("lobby", "joining"):
            for _ in range(2):
                if s.is_host:
                    pkt = s._pack(T_LEAVE, S_ID.pack(0))
                    for p in s.players.values(): s._send(pkt, p[0])
                elif s.host_addr:
                    s._send(s._pack(T_LEAVE, S_ID.pack(s.me)), s.host_addr)
        s.close()
    def set_track(s, track, chk):
        s.track, s.chk = track, chk; s._t_lobby = -9.0
    def set_car(s, car):
        s.car = car
        if s.is_host and s.roster: s.roster[0][2] = car; s._t_lobby = -9.0
    def name_of(s, pid):
        for r in s.roster:
            if r[0] == pid: return r[1]
        return "P%d" % (pid + 1)
    def take_start(s):
        g, s._go = s._go, None
        return g
    def start(s, track, chk):
        s.race_id = (s.race_id + 1) & 255; s.racing = True; s.remote = {}
        s.track, s.chk = track, chk; s._start_left = 4; s._t_start = -9.0
    def end_race(s):
        s.racing = False; s.remote = {}; s._t_lobby = -9.0
    def back_to_lobby(s):
        s.racing = False; s.remote = {}
    def alive(s, pid, now):
        r = s.remote.get(pid)
        return r is not None and now - r.t < TIMEOUT_RACE
    def all_finished(s, now):
        for pid in s.players:
            r = s.remote.get(pid)
            if r is not None and now - r.t < TIMEOUT_RACE and not (r.flags & F_FIN): return False
        return True
    @staticmethod
    def _pack(t, body=b""):
        return H.pack(MAGIC, VER, t) + body
    @staticmethod
    def _enc(n):
        return n.encode("utf-8", "ignore")[:16]
    @staticmethod
    def _name(b):
        return b.split(b"\0", 1)[0].decode("utf-8", "ignore") or "?"
    def _send(s, data, addr):
        try: s.sock.sendto(data, addr)
        except Exception: pass
    def _beacon(s):
        pkt = s._pack(T_BEACON, S_BEACON.pack(s._enc(s.name), s.track, len(s.roster), MAXP, 1 if s.racing else 0, s.chk, s.vstr.encode("ascii", "ignore")[:8]))
        for d in s._bcast: s._send(pkt, (d, s.port))
    def _lobby_send(s):
        body = S_LOBBY.pack(s.track, s.chk, 1 if s.racing else 0, len(s.roster))
        body += b"".join(S_PLAYER.pack(i, s._enc(n), c, rdy, pt) for i, n, c, rdy, pt in s.roster)
        pkt = s._pack(T_LOBBY, body)
        for p in s.players.values(): s._send(pkt, p[0])
    def send_state(s, now, D, px, spd, slip, flags, ftime):
        if now - s._t_send < 0.05: return
        s._t_send = now; s._seq = (s._seq + 1) & 0xFFFF
        ent = S_STATE.pack(s.me, s._seq, D, px, spd, max(-100, min(100, int(slip * 100))), flags & 255, ftime)
        if s.is_host:
            parts, n = [ent], 1
            for pid, r in s.remote.items():
                if pid in s.players and now - r.t < TIMEOUT_RACE:
                    parts.append(S_STATE.pack(pid, r.seq & 0xFFFF, r.D, r.px, r.spd, int(r.slip * 100), r.flags, r.ftime)); n += 1
            pkt = s._pack(T_WORLD, S_ID.pack(n) + b"".join(parts))
            for p in s.players.values(): s._send(pkt, p[0])
        elif s.state == "lobby" and s.host_addr:
            s._send(s._pack(T_STATE, ent), s.host_addr)
    def poll(s, now):
        if s.is_host and s.roster: s.roster[0][4] = max(0, int(s.pts))
        for k in (s.sock, s.bsock):
            if k is None: continue
            for _ in range(64):
                try: data, addr = k.recvfrom(512)
                except BlockingIOError: break
                except ConnectionResetError: continue
                except OSError: break
                if len(data) >= H.size: s._rx(data, addr, now)
        s._tick(now)
    def _rx(s, d, addr, now):
        try:
            m, v, t = H.unpack_from(d, 0)
            if m != MAGIC: return
            if v != VER:
                if s.state in ("browse", "joining"): s.old = v
                return
            o = H.size
            if t == T_BEACON:
                if s.state == "browse" and len(d) >= o + S_BEACON.size:
                    nm, tr, n, mp, rc, ck, vb = S_BEACON.unpack_from(d, o)
                    s.rooms[addr] = [s._name(nm), tr, n, mp, rc, ck, now, vb.split(b"\0", 1)[0].decode("ascii", "ignore")]
            elif s.is_host: s._rx_host(t, d, o, addr, now)
            elif s.state in ("joining", "lobby") and s.host_addr and addr[0] == s.host_addr[0]: s._rx_client(t, d, o, now)
        except struct.error:
            pass
    def _rx_host(s, t, d, o, addr, now):
        if t == T_JOIN:
            if len(d) < o + S_JOIN.size: return
            nm, car, pt = S_JOIN.unpack_from(d, o)
            for pid, p in s.players.items():
                if p[0] == addr:
                    p[1] = now; s._send(s._pack(T_ACCEPT, S_ACCEPT.pack(pid, MAXP)), addr); return
            if s.racing: s._send(s._pack(T_REJECT, S_ID.pack(2)), addr); return
            if len(s.roster) >= MAXP: s._send(s._pack(T_REJECT, S_ID.pack(1)), addr); return
            pid = next(i for i in range(1, MAXP + 1) if i not in s.players)
            s.players[pid] = [addr, now]; s.roster.append([pid, s._name(nm), car, 0, pt])
            s._send(s._pack(T_ACCEPT, S_ACCEPT.pack(pid, MAXP)), addr); s._t_lobby = -9.0
            return
        if t == T_STATE:
            if len(d) < o + S_STATE.size: return
            pid, seq, D, px, spd, sl, fl, ft = S_STATE.unpack_from(d, o)
            p = s.players.get(pid)
            if p is None or p[0] != addr: return
            p[1] = now
            if s.racing: s._put(pid, seq, D, px, spd, sl, fl, ft, now)
        elif t == T_KEEP:
            if len(d) < o + S_KEEP.size: return
            pid, car, rdy, pt = S_KEEP.unpack_from(d, o)
            p = s.players.get(pid)
            if p is None or p[0] != addr: return
            p[1] = now
            for r in s.roster:
                if r[0] == pid and (r[2] != car or r[3] != rdy or r[4] != pt):
                    r[2] = car; r[3] = rdy; r[4] = pt; s._t_lobby = -9.0
        elif t == T_LEAVE:
            if len(d) < o + 1: return
            pid = d[o]; p = s.players.get(pid)
            if p is not None and p[0] == addr: s._drop(pid)
    def _rx_client(s, t, d, o, now):
        s._last_rx = now
        if t == T_ACCEPT:
            if s.state == "joining" and len(d) >= o + S_ACCEPT.size:
                s.me = S_ACCEPT.unpack_from(d, o)[0]; s.state = "lobby"; s._t_keep = -9.0
        elif t == T_REJECT:
            s._fail("Phòng đã đầy" if d[o:o + 1] == b"\x01" else "Phòng đang đua")
        elif t == T_LOBBY:
            if len(d) < o + S_LOBBY.size: return
            tr, ck, rc, n = S_LOBBY.unpack_from(d, o); o += S_LOBBY.size
            if n > MAXP or len(d) < o + n * S_PLAYER.size: return
            ro = []
            for _ in range(n):
                i, nm, c, rdy, pt = S_PLAYER.unpack_from(d, o); o += S_PLAYER.size
                ro.append([i, s._name(nm), c, rdy, pt])
            s.track, s.chk, s.roster, s.room_racing = tr, ck, ro, bool(rc)
        elif t == T_START:
            if s.state == "lobby" and len(d) >= o + S_START.size:
                rid, tr, ck = S_START.unpack_from(d, o)
                if rid != s._seen:
                    s._seen = rid; s._go = (rid, tr, ck); s.racing = True; s.remote = {}; s.track = tr
        elif t == T_WORLD:
            if s.state == "lobby" and s.racing and len(d) > o:
                n = d[o]; o += 1
                for _ in range(n):
                    if len(d) < o + S_STATE.size: break
                    pid, seq, D, px, spd, sl, fl, ft = S_STATE.unpack_from(d, o); o += S_STATE.size
                    if pid != s.me: s._put(pid, seq, D, px, spd, sl, fl, ft, now)
        elif t == T_LEAVE:
            s._fail("Chủ phòng đã rời phòng")
    def _put(s, pid, seq, D, px, spd, sl, fl, ft, now):
        if D != D or px != px or spd != spd: return
        r = s.remote.get(pid)
        if r is None: r = s.remote[pid] = Remote()
        elif seq == r.seq or ((seq - r.seq) & 0xFFFF) >= 0x8000: return
        r.seq, r.D, r.px, r.spd, r.slip, r.flags, r.ftime, r.t = seq, D, px, spd, sl / 100.0, fl, ft, now
    def _drop(s, pid):
        s.players.pop(pid, None); s.remote.pop(pid, None)
        s.roster = [r for r in s.roster if r[0] != pid]; s._t_lobby = -9.0
    def _tick(s, now):
        st = s.state
        if st == "browse":
            for a in [a for a, r in s.rooms.items() if now - r[6] > 3.5]: del s.rooms[a]
        elif st == "lobby" and s.is_host:
            if now - s._t_beacon > 1.0: s._t_beacon = now; s._beacon()
            if now - s._t_lobby > (1.0 if s.racing else 0.25): s._t_lobby = now; s._lobby_send()
            if s._start_left > 0 and now - s._t_start >= 0.1:
                s._t_start = now; s._start_left -= 1
                pkt = s._pack(T_START, S_START.pack(s.race_id, s.track, s.chk))
                for p in s.players.values(): s._send(pkt, p[0])
            lim = TIMEOUT_RACE if s.racing else TIMEOUT_LOBBY
            for pid in [i for i, p in s.players.items() if now - p[1] > lim]: s._drop(pid)
        elif st == "joining":
            if s._join_t0 < 0: s._join_t0 = now
            if now - s._join_t0 > 4.0: s._fail("Không kết nối được"); return
            if now - s._t_join > 0.5:
                s._t_join = now; s._send(s._pack(T_JOIN, S_JOIN.pack(s._enc(s.name), s.car, max(0, int(s.pts)))), s.host_addr)
        elif st == "lobby":
            if now - s._last_rx > (TIMEOUT_RACE + 1.0 if s.racing else TIMEOUT_LOBBY): s._fail("Mất kết nối với chủ phòng"); return
            if now - s._t_keep > 1.0:
                s._t_keep = now; s._send(s._pack(T_KEEP, S_KEEP.pack(s.me, s.car, s.ready, max(0, int(s.pts)))), s.host_addr)