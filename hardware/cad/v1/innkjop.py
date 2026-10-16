"""Purchased parts for v1: frame, panels, insulation, pan, drive, dosing hardware, electronics.

Panels are described as 2D data (outline, holes, cut-outs) so the same
definition gives both the 3D assembly and the DXF cutting files.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from build123d import (
    Circle,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    Rot,
    extrude,
    loft,
    make_face,
)

from felles import G, S, box, cyl_x, cyl_y, cyl_z, flap_servo_pos, rounded_rect_points

P, T = G.P, G.T
X0, X1, Y0, Y1, SKX, H = G.X0, G.X1, G.Y0, G.Y1, G.SKX, G.H
M5D, M6D, M3D = S.skrue.m5_klaring, S.skrue.m6_klaring, S.skrue.m3_klaring


def door_transform(theta: float):
    """Location that opens the door by `theta` degrees about the hinge axis."""
    ax, ay = S.dor.hengsel_akse
    return Pos(ax, ay, 0) * Rot(0, 0, theta) * Pos(-ax, -ay, 0)


# ------------------------------------------------------------------ extrusions


def profiler():
    """2020 extrusions: (name, length, shape)."""
    out = []
    posts = [(X0, Y0), (X1 - P, Y0), (X0, Y1 - P), (X1 - P, Y1 - P), (SKX - P, Y0), (SKX - P, Y1 - P)]
    for x, y in posts:
        out.append(("stolpe", H, box(x, x + P, y, y + P, 0, H)))
    for i, (z0, z1) in enumerate(G.RINGS):
        for y in (Y0, Y1 - P):
            out.append(("tverr_x_taarn", SKX - P - (X0 + P), box(X0 + P, SKX - P, y, y + P, z0, z1)))
            out.append(("tverr_x_kammer", X1 - P - SKX, box(SKX, X1 - P, y, y + P, z0, z1)))
        for x in (X0, X1 - P):
            out.append(("tverr_y", Y1 - Y0 - 2 * P, box(x, x + P, Y0 + P, Y1 - P, z0, z1)))
        if i == 2:  # carries the top plate over the partition
            out.append(("tverr_y", Y1 - Y0 - 2 * P, box(SKX - P, SKX, Y0 + P, Y1 - P, z0, z1)))
    return out


# ------------------------------------------------------------------ panels


@dataclass
class Panel:
    navn: str
    plane: Plane
    u: tuple
    v: tuple
    t: float = T
    holes: list = field(default_factory=list)       # (u, v, diameter)
    cutouts: list = field(default_factory=list)     # (u0, u1, v0, v1)
    slots: list = field(default_factory=list)       # (u, v, length, diameter, angle_deg)
    notches: list = field(default_factory=list)     # corner/edge notches as (u0, u1, v0, v1)
    materiale: str = "3 mm aluminium-kompositt (ACM)"
    antall: int = 1
    dor: bool = False

    def face(self):
        u0, u1 = self.u
        v0, v1 = self.v
        f = Pos((u0 + u1) / 2, (v0 + v1) / 2) * Rectangle(u1 - u0, v1 - v0)
        for c0, c1, d0, d1 in self.cutouts + self.notches:
            f -= Pos((c0 + c1) / 2, (d0 + d1) / 2) * Rectangle(c1 - c0, d1 - d0)
        for hu, hv, d in self.holes:
            f -= Pos(hu, hv) * Circle(d / 2)
        for su, sv, ln, d, ang in self.slots:
            f -= Pos(su, sv) * Rot(0, 0, ang) * (Rectangle(ln, d) + Pos(-ln / 2, 0) * Circle(d / 2) + Pos(ln / 2, 0) * Circle(d / 2))
        return f

    def solid(self):
        return extrude(self.plane * self.face(), self.t)


def _frame_notches(x0=X0, x1=X1, y0=Y0, y1=Y1):
    n = [(x0 - 1, x0 + P, y0 - 1, y0 + P), (x1 - P, x1 + 1, y0 - 1, y0 + P),
         (x0 - 1, x0 + P, y1 - P, y1 + 1), (x1 - P, x1 + 1, y1 - P, y1 + 1),
         (SKX - P, SKX, y0 - 1, y0 + P), (SKX - P, SKX, y1 - P, y1 + 1)]
    return n


def _edge_holes(u0, u1, v0, v1, step=120, inset=10.0):
    """M5 holes into the frame slots along the edges of a side panel."""
    holes = []
    nu = max(2, round((u1 - u0) / step) + 1)
    nv = max(2, round((v1 - v0) / step) + 1)
    for i in range(nu):
        u = u0 + inset + (u1 - u0 - 2 * inset) * i / (nu - 1)
        holes += [(u, v0 + inset, M5D), (u, v1 - inset, M5D)]
    for j in range(1, nv - 1):
        v = v0 + inset + (v1 - v0 - 2 * inset) * j / (nv - 1)
        holes += [(u0 + inset, v, M5D), (u1 - inset, v, M5D)]
    return holes


def paneler():
    zb = -S.bunnplate_t
    ztop = H + T
    ax, _ay = S.dor.hengsel_akse
    pl = []
    # bottom plate (5 mm aluminium) – the frame and the load cell stand on it
    lc = S.lastcelle
    holes = [(x, y, M5D) for x in (X0 + 10, X1 - 10, SKX - 10) for y in (Y0 + 10, Y1 - 10)]
    holes += [(x, y, M5D) for x in (X0 + 10, X1 - 10) for y in (Y0 + 100, Y1 - 100)]
    holes += [(lc.x_fast + lc.hull_fra_ende + dx, lc.y, M6D) for dx in (0, 12)]
    holes += [(x, y, 5.0) for x, y in S.overlast.pos]   # tapped M6
    holes += [(x, y, M5D) for x in (X0 + 35, X1 - 35) for y in (Y0 + 35, Y1 - 35)]  # feet
    pl.append(Panel("panel_bunn", Plane.XY.offset(zb), (X0, X1), (Y0, Y1), t=S.bunnplate_t, holes=holes,
                    materiale="5 mm aluminium 5083 eller 6082"))
    # mellomgulv
    m = S.eltemotor
    holes = [(x, y, M5D) for x in (X0 + 10, X1 - 10) for y in (Y0 + 60, 0, Y1 - 60)]
    holes += [(-60, Y1 - 40, 16), (-200, -120, 16)]   # cable grommets
    pl.append(Panel("mellomgulv", Plane.XY.offset(G.Z_MG), (X0, X1), (Y0, Y1), t=S.mellomgulv.t,
                    holes=holes + [(0, 0, 2 * (S.lagersoyle.flens_r + 8))],
                    cutouts=[(m.pos[0] - 55, m.pos[0] + 55, m.pos[1] - 55, m.pos[1] + 55)],
                    notches=_frame_notches(), materiale="3 mm aluminium"))
    # top plate (chamber roof / floor of the dosing section)
    sx, sy = S.saltskrue.utlop[0], G.SALT_Y
    holes = [(S.melskrue.utlop_x, G.AUG_Y, 42), (sx, sy, 18), (S.vann.dyse[0], S.vann.dyse[1], 8),
             (S.tak.tof[0] - 20, S.tak.tof[1], 10), (S.tak.ir[0] + 18, S.tak.ir[1], 10),
             (-200, 100, 16), (-200, -60, 16), (70, -60, 12), (100, 60, 12)]
    holes += [(x, y, M5D) for x in (X0 + 10, X1 - 10, SKX - 10) for y in (Y0 + 60, 0, Y1 - 60)]
    tm = S.tak.modul
    holes += [(x, y, M3D) for x in (tm[0][0] + 6, tm[0][1] - 6) for y in (tm[1][0] + 6, tm[1][1] - 6)]
    cut = [(S.tak.kamera[0] + 14, S.tak.kamera[0] + 18, S.tak.kamera[1] - 10, S.tak.kamera[1] + 10)]
    for which in ("mel", "salt"):
        fx, fy = flap_servo_pos(which)
        cut.append((fx - 7, fx + 18, fy - 7.25, fy + 7.25))
    pl.append(Panel("toppplate", Plane.XY.offset(G.Z_TP), (X0, X1), (Y0, Y1), t=S.toppplate.t,
                    holes=holes, cutouts=cut, notches=_frame_notches(), materiale="3 mm aluminium"))
    # weighing platform (6 mm aluminium)
    pf = S.plattform
    holes = [(0, 0, S.aksel.d + 4)]
    holes += [(33 * math.cos(math.radians(a)), 33 * math.sin(math.radians(a)), M5D) for a in (45, 135, 225, 315)]
    holes += [(lc.x_fast + lc.l - lc.hull_fra_ende - dx, lc.y, M6D) for dx in (0, 12)]
    holes += [(m.pos[0], m.pos[1], m.aksel_d + 10)]
    ang = math.degrees(math.atan2(m.pos[1], m.pos[0]))
    slots = []
    for a in (45, 135, 225, 315):
        r = m.flens_hull / 2
        slots.append((m.pos[0] + r * math.cos(math.radians(a)), m.pos[1] + r * math.sin(math.radians(a)), 10, M5D, ang))
    holes += [(x, y, 4.2) for x, y in ((-199, 45), (-181, 45))]   # cable clamp (M5 tapped)
    holes += [(40, -20, 8), (-160, 30, 8)]                         # probe cable under the platform
    pl.append(Panel("plattform", Plane.XY.offset(G.Z_PL0), tuple(pf.x), tuple(pf.y), t=pf.t,
                    holes=holes, slots=slots, materiale="6 mm aluminium 6082"))
    # ceiling liner
    tm = S.tak.modul
    pl.append(Panel("takforing", Plane.XY.offset(G.Z_CEIL), (G.CX0, G.CX1), (Y0 + P, G.CY1),
                    cutouts=[(tm[0][0], tm[0][1], tm[1][0], tm[1][1])], materiale="3 mm ACM (hvit) eller PP-plate"))
    # side panels
    zl, zh = zb, ztop
    pl.append(Panel("panel_venstre", Plane.YZ.offset(X0 - T), (Y0, Y1), (zl, zh),
                    holes=_edge_holes(Y0, Y1, zl + 5, zh - 3),
                    cutouts=[(y, y + 8, 200, 300) for y in range(-60, 40, 16)]))
    pl.append(Panel("panel_hoyre", Plane.YZ.offset(X1), (Y0, Y1), (zl, zh),
                    holes=_edge_holes(Y0, Y1, zl + 5, zh - 3)
                    + [(Y0 + P / 2, z + dz, M5D) for z in S.dor.hengsel_z for dz in (-12, 12)]))
    rear = Plane(origin=(0, Y1 + T, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    pl.append(Panel("panel_bak", rear, (X0 - T, X1 + T), (zl, zh),
                    holes=_edge_holes(X0 - T, X1 + T, zl + 5, zh - 3),
                    cutouts=[(-262, -212, 80, 130)] + [(x, x + 8, 380, 460) for x in range(40, 130, 16)]))
    front = Plane(origin=(0, Y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    tk, kp = S.elektronikk.tankluke, S.elektronikk.kontrollpanel
    pl.append(Panel("panel_front_taarn", front, (X0 - T, SKX - 14), (40, 331),
                    holes=[(X0 + 10, z, M5D) for z in (60, 190, 320)] + [(SKX - 24, z, M5D) for z in (60, 190, 320)],
                    cutouts=[(tk[0][0], tk[0][1], tk[1][0], tk[1][1]), (kp[0][0] + 5, kp[0][1] - 5, kp[1][0] + 5, kp[1][1] - 5)]))
    pl.append(Panel("panel_front_topp", front, (X0 - T, X1 + T), (G.Z_TP, ztop),
                    holes=_edge_holes(X0 - T, X1 + T, G.Z_TP, ztop - 3)))
    pl.append(Panel("panel_front_sokkel", front, (X0 - T, X1 + T), (zl, 36),
                    holes=[(x, 10, M5D) for x in (X0 + 10, SKX - 10, X1 - 10)]))
    pl.append(Panel("panel_dor", front, (SKX - 12, ax - 4), (40, 331), dor=True,
                    holes=[(135, z + dz, M5D) for z in S.dor.hengsel_z for dz in (-12, 12)]
                    + [(SKX + 8, 185 + dz, M5D) for dz in (-20, 20)]))
    # top panel with the two filling openings
    t = S.trakt
    sb = S.saltboks
    pl.append(Panel("panel_topp", Plane.XY.offset(H), (X0 - T, X1 + T), (Y0 - T, Y1 + T),
                    holes=_edge_holes(X0 - T, X1 + T, Y0 - T, Y1 + T),
                    cutouts=[(t.x[0] - t.vegg - 1, t.x[1] + t.vegg + 1, G.AUG_Y - t.topp_b / 2 - t.vegg - 1, G.AUG_Y + t.topp_b / 2 + t.vegg + 1),
                             (sb.x[0] - 1, sb.x[1] + 1, sb.y[0] - 1, G.AUG_Y - t.topp_b / 2 - t.vegg)]))
    return pl


# ------------------------------------------------------------------ insulation


def isolasjon():
    """XPS pieces (name, shape). The holder column passes through the floor with a gap."""
    t = G.XPS
    out = []
    floor = box(G.CX0, G.CX1, Y0, G.CY1, G.Z_MG1, G.Z_FLOOR) - cyl_z(G.R_KRAGE_OUT, G.Z_MG1 - 1, G.Z_FLOOR + 1)
    out.append(("xps_gulv", floor))
    out.append(("xps_venstre", box(G.CX0 - t, G.CX0, Y0, Y1 - P, G.Z_MG1, G.Z_TP - t)))
    out.append(("xps_hoyre", box(G.CX1, G.CX1 + t, Y0, Y1 - P, G.Z_MG1, G.Z_TP - t)))
    out.append(("xps_bak", box(G.CX0, G.CX1, G.CY1, G.CY1 + t, G.Z_FLOOR, G.Z_TP - t)))
    tm = S.tak.modul
    ceil = box(G.CX0 - t, G.CX1 + t, Y0 + P, Y1 - P, G.Z_TP - t, G.Z_TP)
    ceil -= box(tm[0][0], tm[0][1], tm[1][0], tm[1][1], G.Z_TP - t - 1, G.Z_TP + 1)
    out.append(("xps_tak", ceil))
    return out


def dorplugg_taper():
    """How much the latch-side face of the plug must be cut back at the inside so it clears the jamb."""
    ax, ay = S.dor.hengsel_akse
    c, t = S.dor.klaring, S.dor.plugg_t
    r_jamb = math.hypot(ax - G.CX0, Y0 - ay) - 1.0
    x_in = ax - math.sqrt(r_jamb ** 2 - (Y0 + t - ay) ** 2)
    return max(0.0, x_in - (G.CX0 + c))


def dorplugg():
    """XPS plug in the door opening. The latch-side edge is cut at an angle (see dorplugg_taper)."""
    c, t = S.dor.klaring, S.dor.plugg_t
    k = dorplugg_taper()
    pts = [(G.CX0 + c, Y0), (G.CX1 - c, Y0), (G.CX1 - c, Y0 + t), (G.CX0 + c + k, Y0 + t)]
    face = make_face(Polyline(*pts, close=True))
    return extrude(Plane.XY.offset(G.Z_FLOOR + c) * face, G.Z_CEIL - G.Z_FLOOR - 2 * c)


# ------------------------------------------------------------------ pan and drive (weighed)


def _pan_outline(w, d, r, z):
    return Plane.XY.offset(z) * make_face(Polyline(*rounded_rect_points(w, d, r), close=True))


def brodform(theta=0.0, lift=0.0, dy=0.0):
    """Bread pan (hollow body + foot with two lugs). theta = unlock rotation in degrees."""
    f = S.form
    z0, z1 = G.Z_PAN, G.Z_RIM
    outer = loft([_pan_outline(f.bunn[0], f.bunn[1], f.hjorneradius - 4, z0),
                  _pan_outline(f.topp[0], f.topp[1], f.hjorneradius, z1)])
    g = f.gods
    inner = loft([_pan_outline(f.bunn[0] - 2 * g, f.bunn[1] - 2 * g, f.hjorneradius - 4 - g, z0 + g),
                  _pan_outline(f.topp[0] - 2 * g, f.topp[1] - 2 * g, f.hjorneradius - g, z1 + 0.01)])
    body = outer - inner
    foot = cyl_z(f.fot_d / 2, G.Z_CUP_FLOOR, z0 + 0.5) - cyl_z(f.fot_d / 2 - 3, G.Z_CUP_FLOOR - 1, z0 - 2)
    kw, kh = f.knast
    for a in (0, 180):
        lug = box(f.fot_d / 2 - 1, f.fot_d / 2 + kh, -kw / 2, kw / 2, G.Z_CUP_FLOOR + 3, G.Z_CUP_FLOOR + 9)
        foot += Rot(0, 0, a) * lug
    pan = body + foot
    return Pos(0, dy, lift) * Rot(0, 0, theta) * pan


def pan_inner_area(z_rel):
    """Inside cross-section area (mm²) of the pan at height z_rel above the inside bottom."""
    f = S.form
    k = max(0.0, min(1.0, z_rel / f.hoyde))
    w = f.bunn[0] + (f.topp[0] - f.bunn[0]) * k - 2 * f.gods
    d = f.bunn[1] + (f.topp[1] - f.bunn[1]) * k - 2 * f.gods
    r = f.hjorneradius - 4 * (1 - k) - f.gods
    return w * d - (4 - math.pi) * r * r


def koblingsdel():
    k = S.koblingsdel
    z0 = G.Z_CUP_FLOOR - 4
    part = cyl_z(k.d / 2, z0, z0 + k.h)
    for a in (0, 180):
        part += Rot(0, 0, a) * cyl_z(2.5, z0 + k.h, z0 + k.h + 6, k.d / 2 - 5, 0)
    return part


def drivverk():
    """Weighed drive parts below the holder: shaft, bearings, pulleys, belt, motor, load-cell top spacer."""
    m = S.eltemotor
    out = []
    z_c = G.Z_CUP_FLOOR - 4
    out.append(("aksel", cyl_z(S.aksel.d / 2, G.Z_PULLEY0 + 2, z_c)))
    out.append(("reimskive_aksel", cyl_z(G.R_P_SHAFT + 3, G.Z_PULLEY0, G.Z_PULLEY1) - cyl_z(S.aksel.d / 2, 0, 100)))
    mx, my = m.pos
    out.append(("reimskive_motor", cyl_z(G.R_P_MOTOR + 3, G.Z_PULLEY0, G.Z_PULLEY1, mx, my)))
    out.append(("reim", reim()))
    body = cyl_z(m.d / 2, G.Z_PL1, G.Z_PL1 + m.lengde, mx, my)
    body += box(mx - m.d / 2, mx + m.d / 2, my - m.d / 2, my + m.d / 2, G.Z_PL1, G.Z_PL1 + 8)
    body += cyl_z(m.aksel_d / 2, G.Z_PULLEY0 + 3, G.Z_PL1, mx, my)
    out.append(("eltemotor", body))
    lc = S.lastcelle
    xe = lc.x_fast + lc.l
    out.append(("lastcelle_kloss_topp", box(xe - 30, xe, lc.y - lc.b / 2, lc.y + lc.b / 2, G.Z_PL0 - lc.avstand_t, G.Z_PL0)))
    return out


def belt_geometry():
    """Centre distance, required pitch length and chosen standard belt."""
    m = S.eltemotor
    c = math.hypot(*m.pos)
    r1, r2 = G.R_P_MOTOR, G.R_P_SHAFT
    length = 2 * c + math.pi * (r1 + r2) + (r2 - r1) ** 2 / c
    std = min(S.reim.standard, key=lambda L: abs(L - length))
    return c, length, std


def reim():
    """Belt as a closed band around the two pulleys (pitch line ± 2 mm)."""
    m = S.eltemotor
    mx, my = m.pos
    shapes = []
    for off, sign in ((2.0, 1), (-2.0, -1)):
        r1, r2 = G.R_P_MOTOR + off, G.R_P_SHAFT + off
        pts = _belt_outline((mx, my), r1, (0.0, 0.0), r2)
        f = Plane.XY.offset(G.Z_BELT0) * make_face(Polyline(*pts, close=True))
        shapes.append(extrude(f, S.reim.bredde))
    return shapes[0] - shapes[1]


def _belt_outline(c1, r1, c2, r2, n=40):
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    base = math.atan2(dy, dx)
    a = math.acos((r1 - r2) / d)
    pts = []
    for i in range(n + 1):   # around the motor pulley, far side
        t = base + a + (2 * math.pi - 2 * a) * i / n
        pts.append((x1 + r1 * math.cos(t), y1 + r1 * math.sin(t)))
    for i in range(n + 1):   # around the shaft pulley
        t = base - a + 2 * a * i / n
        pts.append((x2 + r2 * math.cos(t), y2 + r2 * math.sin(t)))
    return pts


def lastcelle_fast():
    """Fixed parts of the weighing stack: bottom spacer, the cell, overload stops."""
    lc = S.lastcelle
    x0 = lc.x_fast
    out = [("lastcelle_kloss_bunn", box(x0, x0 + 30, lc.y - lc.b / 2, lc.y + lc.b / 2, 0, lc.avstand_t)),
           ("lastcelle", box(x0, x0 + lc.l, lc.y - lc.b / 2, lc.y + lc.b / 2, lc.avstand_t, lc.avstand_t + lc.h)
            - box(x0 + 40, x0 + lc.l - 40, lc.y - lc.b, lc.y + lc.b, lc.avstand_t + 6, lc.avstand_t + lc.h - 6))]
    for x, y in S.overlast.pos:
        out.append(("overlaststopp", cyl_z(3.0, 0, G.Z_PL0 - S.overlast.klaring, x, y)))
    return out


# ------------------------------------------------------------------ dosing hardware


def melmotor():
    mm = S.melmotor
    x_face = S.melskrue.utlop_x + 51
    y, z = G.AUG_Y, G.AUG_Z
    gear = cyl_x(mm.gir_d / 2, x_face, x_face + mm.gir_l, y, z)
    gear += box(x_face, x_face + 5, y - mm.kropp / 2, y + mm.kropp / 2, z - mm.kropp / 2, z + mm.kropp / 2)
    motor = box(x_face + mm.gir_l, x_face + mm.gir_l + mm.lengde, y - mm.kropp / 2, y + mm.kropp / 2,
                z - mm.kropp / 2, z + mm.kropp / 2)
    shaft = cyl_x(4, x_face - 20, x_face, y, z)
    coupler = cyl_x(10, x_face - 26, x_face - 1, y, z)
    return [("melmotor", gear + motor + shaft), ("kobling_mel", coupler)]


def saltmotor():
    sm = S.saltmotor
    x_face = S.saltskrue.utlop[0] + 12          # outside face of the motor plate on the salt box
    y, z = G.SALT_Y, G.SALT_Z
    motor = box(x_face, x_face + sm.lengde, y - sm.kropp / 2, y + sm.kropp / 2, z - sm.kropp / 2, z + sm.kropp / 2)
    return [("saltmotor", motor + cyl_x(2.5, x_face - 14, x_face, y, z))]


def aksler_dosering():
    t, rv = S.trakt, S.rorverk
    out = [("melaksel", cyl_x(S.melskrue.aksel_d / 2, t.x[0] - 16, S.melskrue.utlop_x + 38, G.AUG_Y, G.AUG_Z)),
           ("roreaksel", cyl_x(rv.aksel_d / 2, t.x[0] - 16, t.x[1] + 1, G.AUG_Y, G.AGI_Z))]
    pins = None
    n = int((t.x[1] - t.x[0] - 30) // 25) + 1
    for i in range(n):
        x = t.x[0] + 15 + 25 * i
        a = 45 * (i % 4)
        pin = Pos(x, G.AUG_Y, G.AGI_Z) * Rot(a, 0, 0) * cyl_z(rv.pinne_d / 2, -rv.r, rv.r)
        pins = pin if pins is None else pins + pin
    out.append(("rorepinner", pins))
    return out


def servoer():
    """Two MG90S servos standing in the ceiling module (output shaft down)."""
    sv = S.tak.servo
    out = []
    for name, (x, y) in (("servo_mel", flap_servo_pos("mel")), ("servo_salt", flap_servo_pos("salt"))):
        z0 = G.Z_CEIL + 2
        body = box(x - 6, x + sv[0] - 6, y - sv[1] / 2, y + sv[1] / 2, z0, z0 + sv[2])
        body += cyl_z(2.4, G.Z_CEIL - 0.5, z0, x, y)
        out.append((name, body))
    return out




def vannsystem():
    tk = S.vann.tank
    pu = S.vann.pumpe
    tank = box(tk[0][0], tk[0][1], tk[1][0], tk[1][1], tk[2][0], tk[2][1])
    tank -= box(tk[0][0] + 2, tk[0][1] - 2, tk[1][0] + 2, tk[1][1] - 2, tk[2][0] + 2, tk[2][1] - 6)
    pump = box(pu[0][0], pu[0][1], pu[1][0], pu[1][1], pu[2][0], pu[2][1])
    dx, dy = S.vann.dyse
    nozzle = cyl_z(2.0, G.Z_CEIL - 4, G.Z_TP1 + 15, dx, dy)
    return [("vanntank", tank), ("vannpumpe", pump), ("dyserør", nozzle)]


def varmeenhet():
    """Finned heatsink with the silicone pad behind it, on the rear wall."""
    v = S.varme
    w, h, t = v.plate
    y1 = G.CY1
    z0 = v.plate_z
    pad = box(-v.matte[0] / 2, v.matte[0] / 2, y1 - 1.5, y1, z0 + (h - v.matte[1]) / 2, z0 + (h + v.matte[1]) / 2)
    plate = box(-w / 2, w / 2, y1 - 1.5 - t, y1 - 1.5, z0, z0 + h)
    for i in range(v.finner):
        x = -w / 2 + 5 + i * (w - 10) / (v.finner - 1)
        plate += box(x - 1, x + 1, y1 - 1.5 - t - v.finne_d, y1 - 1.5 - t, z0, z0 + h)
    return [("varmematte", pad), ("kjoleribbe", plate)]


def vifte():
    v = S.varme
    y1 = G.CY1 - 1.5 - v.plate[2] - v.finne_d - v.kanal_vegg
    s = v.vifte
    z1 = G.Z_CEIL - 8
    f = box(-s / 2, s / 2, y1 - v.vifte_t, y1, z1 - s, z1) - cyl_y(s / 2 - 2, y1 - v.vifte_t - 1, y1 + 1, 0, z1 - s / 2)
    f += cyl_y(s / 5, y1 - v.vifte_t, y1, 0, z1 - s / 2)
    return [("vifte", f)]


def elektronikk():
    out = []
    bk = S.elektronikk.bærekort
    out.append(("bærekort", box(bk[0][0], bk[0][1], bk[1][0], bk[1][1], bk[2][0], bk[2][1])))
    kp = S.elektronikk.kontrollpanel
    xc = (kp[0][0] + kp[0][1]) / 2
    out.append(("e_stopp", cyl_y(20, Y0 - 32, Y0 - 3, xc + 28, 270) + cyl_y(14, Y0 + 6, Y0 + 40, xc + 28, 270)))
    out.append(("oled", box(xc - 50, xc - 10, Y0 + 6, Y0 + 12, 245, 285)))
    out.append(("dreieknapp", cyl_y(10, Y0 - 22, Y0 - 3, xc - 30, 220) + box(xc - 42, xc - 18, Y0 + 6, Y0 + 30, 208, 232)))
    out.append(("pi_zero", box(60, 125, -110, -80, G.Z_TP1 + 4, G.Z_TP1 + 9)))
    out.append(("din_kontakt", cyl_y(11, Y1 - 25, Y1 + T + 12, -237, 105)))
    return out


def dorbeslag():
    """Magnet catch and the safety switch behind the door (fixed side)."""
    return [("dorbryter", box(G.CX0 - G.XPS + 2, G.CX0 - 6, Y0 + 4, Y0 + 24, 175, 195))]
