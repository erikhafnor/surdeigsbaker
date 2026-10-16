"""Purchased parts (extrusions, sheet panels, bowl, hook, motor, electronics).

Panels are described as 2D data (outline, holes, cut-outs) so the same
definition produces both the 3D assembly and the DXF cutting files.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from build123d import (
    Axis,
    Circle,
    FilletPolyline,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    Rot,
    Vector,
    extrude,
    make_face,
    revolve,
    sweep,
)

from felles import S, box, cyl_x, cyl_y, cyl_z, hook_points

P = S.ramme.profil
HALF = S.ramme.bredde / 2
INNER = HALF - P
H = S.ramme.hoyde
Z_MID = S.ramme.midtramme_z
T = 3.0
M5D = S.skrue.m5_klaring
M3D = S.skrue.m3_klaring
YH, ZH = S.lokk.hengsel_akse_y, S.lokk.hengsel_akse_z
LID_Z0 = H
LID_Z1 = H + S.lokk.hoyde


def lid_transform(theta: float):
    """Location that opens the lid by `theta` degrees about the hinge axis."""
    return Pos(0, YH, ZH) * Rot(-theta, 0, 0) * Pos(0, -YH, -ZH)


# ------------------------------------------------------------------ extrusions


def profiler():
    """2020 extrusions: (name, length, shape). Main frame + lid."""
    out = []
    zr = [(0, P), (Z_MID, Z_MID + P), (H - P, H)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * INNER, sx * HALF))
            y0, y1 = sorted((sy * INNER, sy * HALF))
            out.append(("stolpe", H, box(x0, x1, y0, y1, 0, H)))
    for z0, z1 in zr:
        for s in (-1, 1):
            y0, y1 = sorted((s * INNER, s * HALF))
            out.append(("tverr_x", 2 * INNER, box(-INNER, INNER, y0, y1, z0, z1)))
            x0, x1 = sorted((s * INNER, s * HALF))
            out.append(("tverr_y", 2 * INNER, box(x0, x1, -INNER, INNER, z0, z1)))
    return out


def lokkprofiler():
    out = []
    for s in (-1, 1):
        y0, y1 = sorted((s * INNER, s * HALF))
        out.append(("lokk_x", 2 * HALF, box(-HALF, HALF, y0, y1, LID_Z0, LID_Z1)))
        x0, x1 = sorted((s * INNER, s * HALF))
        out.append(("lokk_y", 2 * INNER, box(x0, x1, -INNER, INNER, LID_Z0, LID_Z1)))
    tx = S.lokk.tverrbjelke_x
    for s in (-1, 1):
        out.append(("lokk_tverr", 2 * INNER, box(s * tx - P / 2, s * tx + P / 2, -INNER, INNER, LID_Z0, LID_Z1)))
    return out


# ------------------------------------------------------------------ panels


@dataclass
class Panel:
    navn: str
    plane: Plane
    u: tuple
    v: tuple
    holes: list = field(default_factory=list)       # (u, v, diameter)
    cutouts: list = field(default_factory=list)     # (u0, u1, v0, v1)
    notch: float = 0.0                              # square corner notches
    materiale: str = "3 mm aluminium-kompositt (ACM)"
    antall: int = 1
    lokk: bool = False

    def face(self):
        u0, u1 = self.u
        v0, v1 = self.v
        f = Pos((u0 + u1) / 2, (v0 + v1) / 2) * Rectangle(u1 - u0, v1 - v0)
        if self.notch:
            n = self.notch
            for uc in (u0, u1):
                for vc in (v0, v1):
                    f -= Pos(uc, vc) * Rectangle(2 * n, 2 * n)
        for c0, c1, d0, d1 in self.cutouts:
            f -= Pos((c0 + c1) / 2, (d0 + d1) / 2) * Rectangle(c1 - c0, d1 - d0)
        for hu, hv, d in self.holes:
            f -= Pos(hu, hv) * Circle(d / 2)
        return f

    def solid(self):
        return extrude(self.plane * self.face(), T)


def _std_side_holes(span=160):
    holes = []
    for u in (-span, span):
        for v in (50, 160, 250):
            holes.append((u, v, M5D))
    for v in (P / 2, Z_MID + P / 2, H - P / 2):
        for u in (-100, 0, 100):
            holes.append((u, v, M5D))
    return holes


def _grid_holes(c=160, spacing=(-100, 0, 100)):
    holes = []
    for s in (-c, c):
        for t in spacing:
            holes.append((s, t, M5D))
            holes.append((t, s, M5D))
    return holes


def _pad_bolts():
    pts = []
    for a in S.kantpress.vinkler:
        ang = math.radians(a - 270)
        for dx in (-20, 20):
            x, y = dx, -S.kantpress.radius
            pts.append((x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)))
    return pts


def paneler():
    zc = (P + Z_MID) / 2
    kp = S.kontrollpanel
    bp = S.bakpanel
    xh = S.lokk.hengsel_x

    # front (u = x, v = z)
    front_holes = [h for h in _std_side_holes() if not (h[1] == H - P / 2 and h[0] == 100)]
    front_holes += [(110, H - P / 2, M5D)]
    w, h = kp.utsparing
    front_holes += [(x, z, M3D) for x in (-w / 2 - 3, w / 2 + 3) for z in (zc - h / 2 - 3, zc + h / 2 + 3)]
    front = Panel("panel_front", Plane(origin=(0, -HALF, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)),
                  (-HALF - T, HALF + T), (0, H), front_holes,
                  [(-w / 2, w / 2, zc - h / 2, zc + h / 2)])

    # back (u = -x, v = z)
    back_holes = [h for h in _std_side_holes() if not (h[1] == H - P / 2 and abs(h[0]) == 100)]
    back_holes += [(-(s * xh + d), H - P / 2, M5D) for s in (-1, 1) for d in (-12, 12)]
    bw, bh = bp.utsparing
    xc = 70.0
    back_holes += [(-x, z, M3D) for x in (xc - bw / 2 - 3, xc + bw / 2 + 3) for z in (zc - bh / 2 - 4, zc + bh / 2 + 4)]
    back_holes += [(100, 61, 6.0), (100, 53, M3D), (100, 69, M3D)]   # room sensor (u = -x)
    back = Panel("panel_bak", Plane(origin=(0, HALF, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)),
                 (-HALF - T, HALF + T), (0, H), back_holes,
                 [(-(xc + bw / 2), -(xc - bw / 2), zc - bh / 2, zc + bh / 2)])

    left = Panel("panel_side_venstre", Plane(origin=(-HALF, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0)),
                 (-HALF, HALF), (0, H), _std_side_holes())
    right = Panel("panel_side_hoyre", Plane(origin=(HALF, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)),
                  (-HALF, HALF), (0, H), _std_side_holes())

    bottom_holes = _grid_holes()
    bottom_holes += [(s * (HALF - 10), t * (HALF - 40), M5D) for s in (-1, 1) for t in (-1, 1)]
    vents = [(-90 + i * 20, -90 + i * 20 + 6, -100, 100) for i in range(10)]
    bottom = Panel("panel_bunn", Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 0, -1)),
                   (-HALF, HALF), (-HALF, HALF), bottom_holes, vents)

    floor_holes = _grid_holes()
    for a in (90, 210, 330):
        floor_holes.append((60 * math.cos(math.radians(a)), 60 * math.sin(math.radians(a)), M3D))
    for a0 in (30, 150, 270):
        for d in (-12, 12):
            a = math.radians(a0 + d)
            floor_holes.append((110 * math.cos(a), 110 * math.sin(a), M3D))
    floor_holes += [(39.0, 22.5, 14.0), (46.9, -88.3, 8.0)]
    floor = Panel("panel_gulv", Plane(origin=(0, 0, Z_MID + P), x_dir=(1, 0, 0), z_dir=(0, 0, 1)),
                  (-HALF, HALF), (-HALF, HALF), floor_holes, notch=P)

    tx = S.lokk.tverrbjelke_x
    top_holes = _grid_holes()
    top_holes += [(s * tx, y, M5D) for s in (-1, 1) for y in (-120, -60, -40, 40, 60, 120)]
    top_holes += [(x, y, M5D) for x, y in _pad_bolts()]
    sx, sy = S.sensorhus.pos
    top_holes += [(sx, sy + d, M5D) for d in (-16, 16)]
    top_holes += [(0, 0, S.kobling.d + 4), (-40, 60, 12.0)]
    lid_top = Panel("panel_lokk_topp", Plane(origin=(0, 0, LID_Z1), x_dir=(1, 0, 0), z_dir=(0, 0, 1)),
                    (-HALF, HALF), (-HALF, HALF), top_holes, lokk=True)

    liner_holes = [(s * tx, -y, M5D) for s in (-1, 1) for y in (-100, 100)]
    liner_holes += [(s * S.lagerhus.bolt_x, 0, M5D) for s in (-1, 1)]
    liner_holes += [(x, -y, M5D) for x, y in _pad_bolts()]
    liner_holes += [(sx, -(sy + d), M5D) for d in (-16, 16)]
    liner_holes += [(0, 0, 14.0), (-40, -60, 12.0)]
    liner = Panel("panel_lokk_foring", Plane(origin=(0, 0, LID_Z0), x_dir=(1, 0, 0), z_dir=(0, 0, -1)),
                  (-INNER + 2, INNER - 2), (-INNER + 2, INNER - 2), liner_holes,
                  [(sx - 21, sx + 21, -7, 7)], materiale="3 mm PP-plate (matgodkjent) eller ACM", lokk=True)

    return [front, back, left, right, bottom, floor, lid_top, liner]


def varmeplate_face():
    vp = S.varmeplate
    f = Circle(vp.d / 2)
    for dx in (-12, 12):
        f -= Pos(dx, -82) * Circle(M3D / 2)
    return f


# ------------------------------------------------------------------ insulation


def isolasjon():
    t = S.isolasjon_t
    z0, z1 = Z_MID + P + S.ramme.gulvplate_t, H - P
    i = INNER
    return [
        ("xps_front_bak", box(-i, i, -i, -i + t, z0, z1)),
        ("xps_front_bak", box(-i, i, i - t, i, z0, z1)),
        ("xps_side", box(-i, -i + t, -i + t, i - t, z0, z1)),
        ("xps_side", box(i - t, i, -i + t, i - t, z0, z1)),
    ]


# ------------------------------------------------------------------ bowl, heater, hook, drive


def bolle():
    b = S.bolle
    zb = S.varmeplate.topp_z
    r0, r1 = b.bunn_d / 2, b.kant_d / 2
    g = b.gods
    pts = [
        (0, 0, zb), (r0, 0, zb), (r1 - g, 0, zb + b.hoyde - 3), (r1 + 4, 0, zb + b.hoyde - 3),
        (r1 + 4, 0, zb + b.hoyde), (r1 - 2 * g, 0, zb + b.hoyde), (r0 - g, 0, zb + g), (0, 0, zb + g),
    ]
    return revolve(make_face(Polyline(*pts, close=True)), Axis.Z, 360)


def varmeplate_stack():
    vp = S.varmeplate
    z1 = vp.topp_z
    return [
        ("varmeplate", cyl_z(vp.d / 2, z1 - vp.t, z1)),
        ("varmeelement", cyl_z(vp.element_d / 2, z1 - vp.t - 1, z1 - vp.t)),
        ("kork", cyl_z(vp.d / 2 - 5, z1 - vp.t - 1 - vp.kork_t, z1 - vp.t - 1)),
    ]


def krok(park_angle_deg: float = 90.0):
    """Swept hook. park_angle 90° = the C points to +y (towards the hinge)."""
    k = S.krok
    a = math.radians(park_angle_deg)
    pts = [Vector(r * math.cos(a), r * math.sin(a), z) for r, z in hook_points()]
    path = FilletPolyline(*pts, radius=k.boyeradius)
    d = (pts[1] - pts[0]).normalized()
    profile = Plane(origin=pts[0], z_dir=d) * Circle(k.stang_d / 2)
    return sweep(profile, path)


def drivverk():
    m, kb = S.motor, S.kobling
    return [
        ("kobling", cyl_z(kb.d / 2, kb.bunn_z, kb.bunn_z + kb.lengde)),
        ("motor", cyl_z(m.kropp_d / 2, m.flate_z, m.flate_z + m.lengde)),
        ("motoraksel", cyl_z(m.aksel_d / 2, m.flate_z - m.aksel_lengde, m.flate_z)),
    ]


# ------------------------------------------------------------------ electronics (visual)


def elektronikk():
    z = S.elektronikkplate.z + S.elektronikkplate.t
    zc = (P + Z_MID) / 2
    y_front = -HALF - T
    parts = [
        ("esp32", box(-95, -40, 90, 118, z, z + 12)),
        ("buck", box(-95, -52, 30, 51, z, z + 14)),
        ("motordriver", box(20, 70, 70, 120, z, z + 30)),
        ("mosfet", box(20, 55, 20, 40, z, z + 12)),
        ("rele", box(80, 108, 20, 46, z, z + 26)),
        ("ina226", box(-30, -5, 30, 50, z, z + 6)),
        ("wago", box(-30, 10, -15, 5, z, z + 16)),
        ("e_stopp_hus", cyl_y(15, y_front + 4, y_front + 40, -48, zc)),
        ("e_stopp_knapp", cyl_y(20, y_front - 22, y_front - 4, -48, zc)),
        ("knapp", cyl_y(8, y_front - 6, y_front + 22, 40, zc)),
        ("knapp", cyl_y(8, y_front - 6, y_front + 22, 62, zc)),
        ("oled", box(2 - 14, 2 + 14, y_front + 2, y_front + 6, zc + 3 - 14, zc + 3 + 14)),
        ("dc_kontakt", cyl_y(6, HALF + T - 16, HALF + T + 6, 40, zc)),
    ]
    return parts


LATCH_X = (-70.0, 70.0)   # two toggle latches on the front, clear of the lid switch at x 100-150


def lokk_utstyr():
    """Small purchased items that move with the lid (visual)."""
    return [("spennlaas", box(x - 20, x + 20, -HALF - 12, -HALF, H + 2, H + 16)) for x in LATCH_X]


def ramme_utstyr():
    ms = S.mikrobryter
    return [
        *[("spennlaas_base", box(x - 20, x + 20, -HALF - T - 12, -HALF - T, H - 18, H - 2)) for x in LATCH_X],
        ("mikrobryter", box(125, 145, -HALF - T - 6 - ms.b, -HALF - T - 6, 300, 310)),
    ]
