"""Printed parts for Surdeigsbaker v1.

Every part is modelled in machine (assembly) coordinates so that the
assembly, the clearance checks and the drawings share one geometry.
`print_rot` turns a part into a good print orientation before export.
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    Axis,
    Cylinder,
    Helix,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    Rot,
    extrude,
    fillet,
    make_face,
    sweep,
)

from felles import G, S, Part, box, cyl_x, cyl_y, cyl_z, flap_servo_pos, gear_x, prism_x, ring_z

M3, M4, M5, M6 = (S.skrue.m3_klaring / 2, S.skrue.m4_klaring / 2, S.skrue.m5_klaring / 2, S.skrue.m6_klaring / 2)
M5_HEAD = S.skrue.m5_hode / 2
INSERT = S.skrue.m3_innsats / 2
B608_R, B608_W = 11.05, 7.0
PROBE_ANGLE = 30.0          # dough probe in the holder, clear of the bayonet lugs and the bolts

DOWN_MIN_X = Rot(0, -90, 0)    # face with the smallest x ends up on the bed
DOWN_MIN_Y = Rot(90, 0, 0)
DOWN_MAX_Y = Rot(-90, 0, 0)
FLIP = Rot(180, 0, 0)
NONE = Rot(0, 0, 0)


def round_vertical(part, r):
    """Cosmetic fillet on vertical edges; silently skipped if OCC refuses."""
    try:
        return fillet(part.edges().filter_by(Axis.Z), r)
    except Exception:  # noqa: BLE001 - cosmetic only
        return part


def sector(r0, r1, a0, a1, z0, z1, n=24):
    """Annular sector between angles a0 and a1 (degrees)."""
    pts = [(r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    pts += [(r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n)))
            for i in range(n + 1)]
    return extrude(Plane.XY.offset(z0) * make_face(Polyline(*pts, close=True)), z1 - z0)


def d_hole_x(d, flat, x0, x1, y, z):
    """D-shaped hole along x (flat on top) for a D-shaft."""
    r = d / 2 + 0.1
    return cyl_x(r, x0, x1, y, z) - box(x0 - 1, x1 + 1, y - r - 1, y + r + 1, z + r - flat, z + r + 1)


def auger_x(d, core, pitch, x0, x1, y, z, flight_t, bore=0.0, flat=0.0):
    """Printed screw conveyor segment along +x."""
    length = x1 - x0
    r_in, r_out = core / 2 - 0.6, d / 2
    r_mid = (r_in + r_out) / 2
    helix = Helix(pitch=pitch, height=length, radius=r_mid)
    prof = Plane.XZ * Pos(r_mid, 0) * Rectangle(r_out - r_in, flight_t)
    flight = sweep(prof, helix, is_frenet=True)
    flight &= cyl_z(d / 2, 0, length)
    shape = Cylinder(core / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN)) + flight
    shape = Pos(x0, y, z) * Rot(0, 90, 0) * shape
    if bore:
        shape -= d_hole_x(bore, flat, x0 - 1, x1 + 1, y, z) if flat else cyl_x(bore / 2 + 0.1, x0 - 1, x1 + 1, y, z)
    return shape


# ------------------------------------------------------------------ weighed: holder and bearing column


def formholder():
    """Bayonet cup for the pan foot. Sits on the bearing column, never touches the chamber."""
    fh = S.formholder
    body = cyl_z(G.R_CUP_OUT, G.Z_SKIRT, G.Z_CUP_TOP)
    body -= cyl_z(G.R_CUP_IN, G.Z_CUP_FLOOR, G.Z_CUP_TOP + 1)
    body -= ring_z(G.R_HUB, G.R_GROOVE_OUT, G.Z_SKIRT - 1, G.Z_GROOVE_TOP)
    body -= cyl_z(S.koblingsdel.d / 2 + 1, G.Z_SKIRT - 1, G.Z_CUP_FLOOR + 1)
    # bayonet: vertical entry at the unlock angle, then a horizontal slot to the locked angle
    kw = S.form.knast[0] + 2
    half = math.degrees(kw / 2 / G.R_CUP_IN)
    lug0, lug1 = G.Z_CUP_FLOOR + 2, G.Z_CUP_FLOOR + 10
    for base in (0, 180):
        a_un = base - fh.knast_vinkel
        body -= sector(G.R_CUP_IN - 1, G.R_CUP_OUT + 1, a_un - half, a_un + half, lug0, G.Z_CUP_TOP + 1)
        body -= sector(G.R_CUP_IN - 1, G.R_CUP_OUT + 1, a_un - half, base + half, lug0, lug1)
    # spring-loaded DS18B20 probe pressing against the pan bottom, with a cable channel to the hub
    r_p, a_p = 75.0, PROBE_ANGLE
    probe = box(G.R_CUP_OUT - 2, r_p + 8, -8, 8, G.Z_SKIRT, G.Z_CUP_TOP - 2)
    probe -= cyl_z(3.3, G.Z_SKIRT + 6, G.Z_CUP_TOP, r_p, 0)
    probe_ch = cyl_x(2.2, 20.5, r_p, 0, G.Z_SKIRT + 8) + cyl_z(2.2, G.Z_SKIRT - 1, G.Z_SKIRT + 10, 20.5, 0)
    body += Rot(0, 0, a_p) * probe
    body -= Rot(0, 0, a_p) * probe_ch
    # M5 into heat inserts in the bearing column, heads below the cup floor
    for a in (0, 90, 180, 270):
        x, y = 21 * math.cos(math.radians(a)), 21 * math.sin(math.radians(a))
        body -= cyl_z(M5, G.Z_SKIRT - 1, G.Z_CUP_FLOOR + 1, x, y)
        body -= cyl_z(M5_HEAD, G.Z_CUP_FLOOR - 5, G.Z_CUP_FLOOR + 1, x, y)
    return body


def lagersoyle():
    """Bearing column for the 12 mm drive shaft (2 × 6001-2RS), bolted to the platform."""
    ls = S.lagersoyle
    _d, od, w = ls.lager
    z0, z1 = G.Z_PL1, G.Z_COL_TOP
    col = cyl_z(ls.flens_r, z0, z0 + ls.flens_t) + cyl_z(ls.r, z0, z1)
    col -= cyl_z(S.aksel.d / 2 + 1.0, z0 - 1, z1 + 1)
    col -= cyl_z(od / 2 + 0.05, z0 - 1, z0 + w)
    col -= cyl_z(od / 2 + 0.05, z1 - w, z1 + 1)
    for a in (45, 135, 225, 315):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        col -= cyl_z(M5, z0 - 1, z0 + ls.flens_t + 1, 33 * c, 33 * s)
    for a in (0, 90, 180, 270):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        col -= cyl_z(INSERT + 0.4, z1 - 10, z1 + 1, 21 * c, 21 * s)    # M5 heat inserts
    ch = cyl_z(2.2, z0 + ls.flens_t + 2, z1 + 1, 20.5, 0) + cyl_x(2.2, 20.5, ls.r + 1, 0, z0 + ls.flens_t + 4)
    col -= Rot(0, 0, PROBE_ANGLE) * ch                                 # probe cable
    return col


def kabelklemme():
    """Clamp for the flexible cable loop, on the platform inside the motor opening (weighed side)."""
    x, y = -190.0, 45.0
    z = G.Z_PL1
    c = box(x - 12, x + 12, y - 6, y + 6, z, z + 9) - box(x - 6, x + 6, y - 7, y + 7, z - 1, z + 5)
    c -= cyl_z(M5, z - 1, z + 10, x - 9, y) + cyl_z(M5, z - 1, z + 10, x + 9, y)
    return c


# ------------------------------------------------------------------ fixed: floor collar


def krage():
    """Collar lining the hole in the chamber floor. The holder skirt laps over it with a gap."""
    k = ring_z(G.R_KRAGE_IN, G.R_KRAGE_OUT, G.Z_MG1, G.Z_KRAGE_TOP)
    k += ring_z(G.R_KRAGE_IN, G.R_KRAGE_OUT + 10, G.Z_FLOOR, G.Z_FLOOR + G.KRAGE_FLENS_T)
    return k


# ------------------------------------------------------------------ flour: hopper, trough, outlet, screw


def hopper_profile(off):
    """(y, z) outline of the hopper + U-trough, offset outwards by `off`."""
    t = S.trakt
    yc, zc = G.AUG_Y, G.AUG_Z
    r = G.R_TROUGH + off
    tan = math.tan(math.radians(t.vinkel))
    sh = off / math.sin(math.radians(t.vinkel))
    z_s = G.Z_SLOT + (off - sh) * tan
    half_top = t.topp_b / 2 + off
    z_t = G.Z_SLOT + (half_top - G.R_TROUGH - sh) * tan
    z_top = G.Z_HOPPER_TOP + (0 if off else 1)
    pts = [(yc - r, z_s), (yc - r, zc)]
    for i in range(1, 24):
        a = math.pi + math.pi * i / 24
        pts.append((yc + r * math.cos(a), zc + r * math.sin(a)))
    pts += [(yc + r, zc), (yc + r, z_s), (yc + half_top, z_t), (yc + half_top, z_top),
            (yc - half_top, z_top), (yc - half_top, z_t)]
    return pts


def trakt():
    """Flour hopper with U-trough, bearing boss and agitator bushing. Printed in one piece."""
    t = S.trakt
    w = t.vegg
    x0, x1 = t.x
    yc, zc, za = G.AUG_Y, G.AUG_Z, G.AGI_Z
    outer = prism_x(hopper_profile(w), x0 - w, x1 + w)
    inner = prism_x(hopper_profile(0), x0, x1)
    body = outer - inner
    body -= cyl_x(G.R_TROUGH, x1 - 1, x1 + w + 6, yc, zc)
    # base plate on the top plate, joined to the trough
    zb = G.Z_TP1
    base = box(x0 - w, x1 + w, yc - 30, yc + 30, zb, zb + 4)
    base += box(x0 - w, x1 + w, yc - 10, yc + 10, zb, zc - G.R_TROUGH - 0.5)   # web into the trough wall
    body += base
    for x in (x0 + 12, (x0 + x1) / 2, x1 - 12):
        for y in (yc - 23, yc + 23):
            body -= cyl_z(M4, zb - 1, zb + 5, x, y)
    # flange to the outlet tube
    fl = box(x1 + w, x1 + w + 4, yc - 24, yc + 24, zb, zc + 24) - cyl_x(G.R_TROUGH, x1, x1 + w + 5, yc, zc)
    for dy in (-17, 17):
        for dz in (-17, 17):
            fl -= cyl_x(M3, x1, x1 + w + 5, yc + dy, zc + dz)
    body += fl
    # left end: 608 bearing for the screw, plain bushing for the agitator
    xl = x0 - w
    body += cyl_x(15, xl - 8, xl, yc, zc) + cyl_x(8, xl - 8, xl, yc, za)
    body -= cyl_x(B608_R, xl - 9, xl - 1, yc, zc)
    body -= cyl_x(5, xl - 9, x0 + 1, yc, zc)
    body -= cyl_x(S.rorverk.aksel_d / 2 + 0.2, xl - 9, x1 + w + 1, yc, za)
    return body


def skruror():
    """Closed outlet tube after the hopper: choke, outlet hole, end bearing (608)."""
    t = S.trakt
    x1 = t.x[1] + t.vegg + 4
    xo = S.melskrue.utlop_x
    xe = xo + 18
    yc, zc = G.AUG_Y, G.AUG_Z
    r_o = G.R_TROUGH + 2.4
    body = box(x1, x1 + 4, yc - 24, yc + 24, G.Z_TP1, zc + 24)
    body += cyl_x(r_o, x1 + 4, xe, yc, zc)
    body += cyl_x(15, xe, xe + 8, yc, zc)
    body += box(x1 + 4, xe + 8, yc - 24, yc + 24, G.Z_TP1, zc - r_o + 1.5)
    body -= cyl_x(G.R_TROUGH, x1 - 1, xe, yc, zc)
    body -= cyl_x(B608_R, xe + 1, xe + 9, yc, zc)
    body -= cyl_x(5, xe - 1, xe + 9, yc, zc)
    body -= cyl_z(16, G.Z_TP1 - 1, zc, xo, yc)
    body -= cyl_z(26.5, G.Z_TP1 - 1, G.Z_TP1 + 3.2, xo, yc)            # flange of the drop tube
    for dy in (-17, 17):
        for dz in (-17, 17):
            body -= cyl_x(M3, x1 - 1, x1 + 5, yc + dy, zc + dz)
    for x in (x1 + 10, xe + 2):
        for y in (yc - 19, yc + 19):
            body -= cyl_z(M4, G.Z_TP1 - 1, G.Z_TP1 + 6, x, y)
    return body


def fallror(r_in, r_out, r_flange, x, y):
    """Short drop tube through the roof. The flange rests on the top plate."""
    tube = cyl_z(r_out, G.Z_CEIL, G.Z_TP1, x, y) + cyl_z(r_flange, G.Z_TP1, G.Z_TP1 + 3, x, y)
    return tube - cyl_z(r_in, G.Z_CEIL - 1, G.Z_TP1 + 4, x, y)


def melskrue(seg: int):
    ms = S.melskrue
    x0 = S.trakt.x[0] + 1
    x1 = ms.utlop_x + 16
    n = ms.segmenter
    a = x0 + (x1 - x0) * seg / n
    b = x0 + (x1 - x0) * (seg + 1) / n
    return auger_x(ms.d, ms.kjerne_d, ms.stigning, a, b, G.AUG_Y, G.AUG_Z, ms.vinge_t, ms.aksel_d, 0.5)


def tannhjul(teeth: int, axis_z: float, bore: float, flat: float):
    x0 = S.trakt.x[0] - S.trakt.vegg - 17
    g = gear_x(S.rorverk.modul, teeth, x0, x0 + 6, G.AUG_Y, axis_z, bore=bore, flat=flat)
    g += cyl_x(bore / 2 + 4, x0 + 6, x0 + 9, G.AUG_Y, axis_z) - cyl_x(bore / 2 + 0.1, x0, x0 + 10, G.AUG_Y, axis_z)
    g -= cyl_z(1.4, axis_z, axis_z + bore / 2 + 5, x0 + 7.5, G.AUG_Y)     # M3 set screw (tapped)
    return g


def melmotorfeste():
    """Bracket for the NEMA17 planetary gearbox at the outlet end."""
    yc, zc = G.AUG_Y, G.AUG_Z
    xf = S.melskrue.utlop_x + 51
    plate = box(xf - 5, xf, yc - 23, yc + 23, G.Z_TP1, zc + 23)
    foot = box(xf - 25, xf, yc - 23, yc + 23, G.Z_TP1, G.Z_TP1 + 5)
    br = plate + foot
    br -= cyl_x(11.5, xf - 6, xf + 1, yc, zc)
    for dy in (-15.5, 15.5):
        for dz in (-15.5, 15.5):
            br -= cyl_x(M3, xf - 6, xf + 1, yc + dy, zc + dz)
    for y in (yc - 16, yc + 16):
        br -= cyl_z(M4, G.Z_TP1 - 1, G.Z_TP1 + 6, xf - 16, y)
    return br


def traktlokk():
    t = S.trakt
    x0, x1 = t.x
    yc = G.AUG_Y
    h = t.topp_b / 2
    z = G.H + G.T
    lid = box(x0 - 6, x1 + 6, yc - h - 6, yc + h - 0.5, z, z + 4)
    lid += box(x0 + 0.5, x1 - 0.5, yc - h + 0.5, yc + h - 0.5, G.Z_HOPPER_TOP - 6, z) - box(
        x0 + 2.5, x1 - 2.5, yc - h + 2.5, yc + h - 2.5, G.Z_HOPPER_TOP - 7, z - 2)
    lid += box((x0 + x1) / 2 - 30, (x0 + x1) / 2 + 30, yc - 6, yc + 6, z + 4, z + 14) - box(
        (x0 + x1) / 2 - 22, (x0 + x1) / 2 + 22, yc - 7, yc + 7, z + 4, z + 10)
    return lid


# ------------------------------------------------------------------ salt


def saltboks():
    """Sealed salt box with V-bottom, 10 mm screw channel, outlet and the stepper plate."""
    sb, ss = S.saltboks, S.saltskrue
    x0, x1 = sb.x
    y0, y1 = sb.y
    w = sb.vegg
    yc, zc = G.SALT_Y, G.SALT_Z
    xo = ss.utlop[0]
    r = ss.d / 2 + 0.5
    zb = G.Z_TP1
    body = box(x0, x1, y0, y1, sb.z[0], sb.z[1])
    body += box(x0, xo + 12, yc - 10, yc + 10, zb, zc + r + w)
    body += cyl_x(r + w, x1, xo + 6, yc, zc)
    body += box(xo + 6, xo + 12, yc - 21, yc + 21, zc - 21, zc + 21)        # motor plate
    body += box(x0, x1, y0, y1, zb, sb.z[0]) & box(x0, x1, yc - 10, yc + 10, zb, sb.z[0])
    tan = math.tan(math.radians(sb.bunnvinkel))
    half_in = (y1 - y0) / 2 - w
    z_v = zc + (half_in - r) * tan
    cav = [(yc - r, zc), (yc + r, zc), (yc + half_in, z_v), (yc + half_in, sb.z[1] + 1),
           (yc - half_in, sb.z[1] + 1), (yc - half_in, z_v)]
    body -= prism_x(cav, x0 + w, x1 - w)
    body -= cyl_x(r, x0 + w - 0.5, xo + 6, yc, zc)
    body -= cyl_x(2.2, x0 + 0.8, x0 + w + 1, yc, zc)                     # pin of the screw
    body -= cyl_x(3.0, xo + 5, xo + 13, yc, zc)                           # stepper shaft
    body -= cyl_x(11.5, xo + 10, xo + 13, yc, zc)                         # stepper pilot
    for dy in (-15.5, 15.5):
        for dz in (-15.5, 15.5):
            body -= cyl_x(M3, xo + 5, xo + 13, yc + dy, zc + dz)
    body -= cyl_z(5, zb - 1, zc, xo, yc)
    body -= cyl_z(13.5, zb - 1, zb + 3.2, xo, yc)
    for x in (x0 + 8, xo):
        for y in (yc - 15, yc + 15):
            if x == xo:
                continue
            body -= cyl_z(M4, zb - 1, zb + 12, x, y)
    body -= cyl_z(M4, zb - 1, zb + 12, (x1 + xo) / 2, yc + 15) + cyl_z(M4, zb - 1, zb + 12, (x1 + xo) / 2, yc - 15)
    return body


def saltlokk():
    sb = S.saltboks
    x0, x1 = sb.x
    y0, y1 = sb.y
    z = sb.z[1]
    w = sb.vegg
    lid = box(x0 - 0.5, x1 + 0.5, y0 - 0.5, y1 + 0.5, z, z + 6)
    plug = box(x0 + w + 0.3, x1 - w - 0.3, y0 + w + 0.3, y1 - w - 0.3, z - 8, z)
    plug -= box(x0 + w + 2.3, x1 - w - 2.3, y0 + w + 2.3, y1 - w - 2.3, z - 9, z + 3)   # silica gel pocket
    lid += plug
    lid -= box(x0 + 2, x1 - 2, y0 + 2, y1 - 2, z - 0.01, z + 1.2) - box(x0 + w + 0.3, x1 - w - 0.3, y0 + w + 0.3, y1 - w - 0.3, z - 1, z + 2)  # gasket groove
    lid += box((x0 + x1) / 2 - 12, (x0 + x1) / 2 + 12, (y0 + y1) / 2 - 4, (y0 + y1) / 2 + 4, z + 6, z + 11)
    return lid


def saltskrue():
    ss = S.saltskrue
    x0 = S.saltboks.x[0] + S.saltboks.vegg
    x1 = ss.utlop[0] + 6
    s = auger_x(ss.d, ss.kjerne_d, ss.stigning, x0, x1 - 12, G.SALT_Y, G.SALT_Z, 1.5)
    s += cyl_x(4.5, x1 - 14, x1 - 1, G.SALT_Y, G.SALT_Z)                   # hub for the stepper shaft
    s += cyl_x(2.0, x0 - 2, x0 + 1, G.SALT_Y, G.SALT_Z)                    # pin in the left wall
    s -= d_hole_x(ss.aksel_d, 0.5, x1 - 11, x1, G.SALT_Y, G.SALT_Z)
    return s


# ------------------------------------------------------------------ ceiling module and flaps


def takmodul():
    """Ceiling tray with the outlets, the sensor pockets and the two flap servos."""
    tm = S.tak.modul
    x0, x1 = tm[0]
    y0, y1 = tm[1]
    z0, z1 = G.Z_CEIL, G.Z_TP
    tray = box(x0, x1, y0, y1, z0, z0 + 3) + (box(x0, x1, y0, y1, z0, z1) - box(x0 + 2.4, x1 - 2.4, y0 + 2.4, y1 - 2.4, z0 + 3, z1 + 1))
    bosses = []
    tof, ir, cam = S.tak.tof, S.tak.ir, S.tak.kamera
    bosses.append(box(tof[0] - 15, tof[0] + 15, tof[1] - 9, tof[1] + 9, z0, z0 + 10))
    bosses.append(cyl_z(10, z0, z0 + 12, ir[0], ir[1]))
    bosses.append(box(cam[0] - 16, cam[0] + 16, cam[1] - 15, cam[1] + 15, z0, z0 + 8))
    for which in ("mel", "salt"):
        sx, sy = flap_servo_pos(which)
        bosses.append(box(sx - 9, sx + 20, sy - 9, sy + 9, z0, z1))
    tube_r = {"mel": 20.0, "salt": 9.0}
    holes = [(S.melskrue.utlop_x, G.AUG_Y, tube_r["mel"]), (S.saltskrue.utlop[0], G.SALT_Y, tube_r["salt"])]
    for x, y, r in holes:
        bosses.append(cyl_z(r + 2.4, z0, z1, x, y))
    dx, dy = S.vann.dyse
    bosses.append(cyl_z(6, z0, z1, dx, dy))
    for b in bosses:
        tray += b
    for x, y, r in holes:
        tray -= cyl_z(r, z0 - 1, z1 + 1, x, y)
    tray -= cyl_z(2.6, z0 - 1, z1 + 1, dx, dy)
    tray -= box(tof[0] - 13, tof[0] + 13, tof[1] - 7, tof[1] + 7, z0 + 3, z1 + 1)
    tray -= cyl_z(4.5, z0 - 1, z0 + 4, tof[0], tof[1])
    tray -= cyl_z(4.85, z0 - 1, z1 + 1, ir[0], ir[1])
    tray -= box(cam[0] - 13, cam[0] + 13, cam[1] - 12.5, cam[1] + 12.5, z0 + 3, z1 + 1)
    tray -= cyl_z(6.5, z0 - 1, z0 + 4, cam[0], cam[1])
    for lx in (cam[0] - 3, cam[0] + 19):
        tray -= cyl_z(2.6, z0 - 1, z1 + 1, lx, cam[1] - 27)
        tray += ring_z(2.6, 4.4, z0, z0 + 8, lx, cam[1] - 27)
    sv = S.tak.servo
    for which in ("mel", "salt"):
        sx, sy = flap_servo_pos(which)
        tray -= box(sx - 6.3, sx + sv[0] - 5.7, sy - sv[1] / 2 - 0.3, sy + sv[1] / 2 + 0.3, z0 + 2, z1 + 1)
        tray -= cyl_z(3.2, z0 - 1, z0 + 3, sx, sy)
        for ex in (sx - 8.5, sx + sv[0] - 3.5):
            tray -= cyl_z(1.0, z1 - 8, z1 + 1, ex, sy)
    for x in (x0 + 6, x1 - 6):
        for y in (y0 + 6, y1 - 6):
            tray += cyl_z(4.5, z0, z1, x, y)
            tray -= cyl_z(INSERT, z1 - 7, z1 + 1, x, y)
    return tray


def klaff(which: str):
    """Rotating flap on the servo horn, 0.5 mm below the mouth of the drop tube."""
    sx, sy = flap_servo_pos(which)
    tx, ty = (S.melskrue.utlop_x, G.AUG_Y) if which == "mel" else (S.saltskrue.utlop[0], G.SALT_Y)
    r_plate = 19.0 if which == "mel" else 8.0
    z1 = G.Z_CEIL - 0.5
    z0 = z1 - 3
    arm_l = math.hypot(tx - sx, ty - sy)
    arm = box(sx - 5, sx + 5, sy, sy + arm_l, z0, z1)
    f = arm + cyl_z(r_plate, z0, z1, tx, ty) + cyl_z(7, z0, z1, sx, sy)
    f -= cyl_z(2.4, z0 - 1, z1 + 1, sx, sy)
    for d in (-5.5, 5.5):
        f -= cyl_z(0.8, z0 - 1, z1 + 1, sx + d, sy)      # horn screws
    return f


# ------------------------------------------------------------------ heater duct


def varmekanal():
    """Duct over the finned heatsink. The fan blows in at the top, warm air leaves at the floor."""
    v = S.varme
    w, h, _t = v.plate
    y_front = G.CY1 - 1.5 - v.plate[2] - v.finne_d
    wall = v.kanal_vegg
    x0, x1 = -w / 2 - wall, w / 2 + wall
    z0, z1 = v.plate_z - 25, G.Z_CEIL - 5
    duct = box(x0, x1, y_front - wall, G.CY1, z0, z1)
    duct -= box(-w / 2, w / 2, y_front - 0.01, G.CY1 + 1, z0 - 1, z1 - wall)
    duct -= box(-w / 2, w / 2, y_front - wall - 1, G.CY1 + 1, z0 - 1, v.plate_z)     # outlet at the floor
    s = v.vifte
    zf = G.Z_CEIL - 8 - s / 2
    duct -= cyl_y(s / 2 - 2, y_front - wall - 1, y_front + 1, 0, zf)
    for dx in (-16, 16):
        for dz in (-16, 16):
            duct -= cyl_y(1.6, y_front - wall - 1, y_front + 1, dx, zf + dz)
    for z in (z0 + 12, z1 - 12):
        for x in (x0, x1):
            duct += box(x - 4 if x < 0 else x, x if x < 0 else x + 4, G.CY1 - 10, G.CY1, z - 7, z + 7)
            duct -= cyl_y(M4, G.CY1 - 11, G.CY1 + 1, x - 2 if x < 0 else x + 2, z)
    return duct


# ------------------------------------------------------------------ door


def dorhengsel_ramme(zh: float):
    ax, ay = S.dor.hengsel_akse
    xp = G.X1 + G.T
    plate = box(xp, xp + 5, G.Y0 + 2, G.Y0 + 18, zh - 20, zh + 20)
    arm = box(xp, ax + 2, ay - 2, G.Y0 + 2, zh - 7.75, zh + 7.75)
    knuckle = cyl_z(7, zh - 7.75, zh + 7.75, ax, ay)
    leaf = plate + arm + knuckle
    leaf -= cyl_z(M6, zh - 9, zh + 9, ax, ay)
    for dz in (-12, 12):
        leaf -= cyl_x(M5, xp - 1, xp + 6, G.Y0 + G.P / 2, zh + dz)
    return leaf


def dorhengsel_dor(zh: float):
    ax, ay = S.dor.hengsel_akse
    yf = G.Y0 - G.T
    plate = box(125, ax - 4, yf - 4, yf, zh - 20, zh + 20)
    leaf = plate
    for z0, z1 in ((zh - 20, zh - 8.25), (zh + 8.25, zh + 20)):
        leaf += box(ax - 6, ax, yf - 4, ay + 2, z0, z1) + cyl_z(7, z0, z1, ax, ay)
    leaf -= cyl_z(M6, zh - 21, zh + 21, ax, ay)
    for dz in (-12, 12):
        leaf -= cyl_y(M5, yf - 5, yf + 1, 135, zh + dz)
    return leaf


def dorhandtak():
    yf = G.Y0 - G.T
    x = G.SKX + 8
    h = box(x - 8, x + 8, yf - 6, yf, 150, 220) + box(x - 8, x + 8, yf - 28, yf - 6, 150, 162) + box(x - 8, x + 8, yf - 28, yf - 6, 208, 220)
    h += box(x - 8, x + 8, yf - 28, yf - 20, 150, 220)
    for z in (165, 205):
        h -= cyl_y(M5, yf - 29, yf + 1, x, z)
        h -= cyl_y(M5_HEAD, yf - 29, yf - 22, x, z)
    h -= cyl_y(5.1, yf - 1.5, yf + 0.1, x, 185)     # magnet ⌀10 × 3 (pressed in from the back)
    return h


def bryternese():
    """Pin on the inside of the door that presses the safety switch."""
    x = G.CX0 - G.XPS / 2
    return box(x - 4, x + 4, G.Y0, G.Y0 + 10, 180, 190) + box(x - 9, x + 9, G.Y0, G.Y0 + 2, 175, 195)


def bryterholder():
    """Holder for the KW11 switch, glued into a pocket in the left XPS wall at the front edge."""
    x0, x1 = G.CX0 - G.XPS + 1, G.CX0 - 1
    h = box(x0, x1, G.Y0 + 2, G.Y0 + 28, 170, 200) - box(x0 + 2, x1 - 2, G.Y0 + 1, G.Y0 + 22, 174, 196)
    for z in (180.25, 189.75):
        h -= cyl_x(1.15, x0 - 1, x1 + 1, G.Y0 + 14, z)
    return h


# ------------------------------------------------------------------ tower: panels, tank, electronics


def kontrollpanel():
    kp = S.elektronikk.kontrollpanel
    x0, x1 = kp[0]
    z0, z1 = kp[1]
    yf = G.Y0 - G.T
    p = box(x0, x1, yf - 3, yf, z0, z1) + box(x0 + 5.2, x1 - 5.2, yf, G.Y0, z0 + 5.2, z1 - 5.2)
    xc = (x0 + x1) / 2
    p -= cyl_y(11.25, yf - 4, G.Y0 + 1, xc + 28, 270)            # emergency stop ⌀22
    p -= box(xc - 43, xc - 17, yf - 4, G.Y0 + 1, 257.5, 272.5)   # OLED window 26 × 15
    for dx in (-11.75, 11.75):
        for dz in (-11.9, 11.9):
            p -= cyl_y(1.1, yf - 1, G.Y0 + 1, xc - 30 + dx, 265 + dz)
    p -= cyl_y(3.75, yf - 4, G.Y0 + 1, xc - 30, 220)             # encoder
    p -= cyl_y(2.6, yf - 4, G.Y0 + 1, xc + 28, 225)              # status LED
    for x in (x0 + 4, x1 - 4):
        for z in (z0 + 4, z1 - 4):
            p -= cyl_y(M3, yf - 4, G.Y0 + 1, x, z)
    return p


def bakpanelinnsats():
    yr = G.Y1 + G.T
    p = box(-266, -208, yr, yr + 3, 76, 134) + box(-261.8, -212.2, G.Y1, yr, 80.2, 129.8)
    p -= cyl_y(8.0, G.Y1 - 1, yr + 4, -237, 112)                 # ⚠️ KPJX-PM-4S, measure the panel hole
    p -= box(-243, -231, G.Y1 - 1, yr + 4, 87, 93)               # USB-C service port
    for x in (-262, -212):
        for z in (80, 130):
            p -= cyl_y(M3, G.Y1 - 1, yr + 4, x, z)
    return p


def tankskuff():
    """Tray for the 1 l water box. Its front closes the hatch in the tower front."""
    tk = S.elektronikk.tankluke
    x0, x1 = tk[0][0] + 1, tk[0][1] - 1
    z0, z1 = tk[1][0] + 1, tk[1][1] - 1
    tank = S.vann.tank
    tray = box(x0, x1, tank[1][0] - 2, tank[1][1] + 2, G.Z_MG1, G.Z_MG1 + 3)
    tray += box(x0, x1, G.Y0 - G.T, G.Y0 + 3, G.Z_MG1, z1)
    tray += box(x0, x1, tank[1][1] + 2, tank[1][1] + 4, G.Z_MG1, G.Z_MG1 + 20)
    tray -= box((x0 + x1) / 2 - 25, (x0 + x1) / 2 + 25, G.Y0 - G.T - 1, G.Y0 + 4, z1 - 22, z1 - 8)
    return tray


def elektronikkplate():
    bk = S.elektronikk.bærekort
    plate = box(G.X0, G.X0 + 3, bk[1][0], bk[1][1], bk[2][0], bk[2][1])
    for y in (bk[1][0] + 8, bk[1][1] - 8):
        for z in (bk[2][0] + 8, bk[2][1] - 8):
            plate += cyl_x(4, G.X0 + 3, G.X0 + 10, y, z)
            plate -= cyl_x(INSERT, G.X0 + 4, G.X0 + 11, y, z)
            plate -= cyl_x(M5, G.X0 - 1, G.X0 + 4, y + (6 if y < 0 else -6), z)
    plate -= box(G.X0 - 1, G.X0 + 4, -50, 30, 210, 290)        # air from the vents in the side panel
    return plate


def fot():
    x, y = G.X0 + 35, G.Y0 + 35
    zb = -S.bunnplate_t
    f = cyl_z(20, zb - S.fot_h, zb, x, y) - cyl_z(M5, zb - S.fot_h - 1, zb + 1, x, y)
    f -= cyl_z(M5_HEAD, zb - S.fot_h - 1, zb - 4, x, y)
    f -= ring_z(13, 18, zb - S.fot_h - 1, zb - S.fot_h + 1.5, x, y)
    return f


# ------------------------------------------------------------------ registry


def alle_deler() -> list[Part]:
    ms = S.melskrue
    tk = [S.rorverk.tenner[0], S.rorverk.tenner[1]]
    parts = [
        Part("formholder", formholder(), 1, "PETG", "som modellert", gruppe="vekt",
             merknad="Bajonett for formfoten. 6 perimetre og 50 % fyll. Mål formen før du printer."),
        Part("lagersoyle", lagersoyle(), 1, "PETG", "som modellert", gruppe="vekt",
             merknad="2 × 6001-2RS presses inn, ett fra hver side. 4 × M5-innsatser på toppen. 6 perimetre."),
        Part("kabelklemme", kabelklemme(), 1, "PETG", "som modellert", gruppe="vekt",
             merknad="Holder kabelsløyfa fast på plattformen, slik at bare myke ledninger krysser veiespalten."),
        Part("krage", krage(), 1, "PETG", "flensen ned", merknad="Limes i hullet i XPS-gulvet."),
        Part("trakt", trakt(), 1, "PETG (naturfarget, matkontakt)", "som modellert",
             merknad="Melbeholder og trau i ett. Rustfri dyse, 0,2 mm lag, 3 perimetre, glatt ytterflate."),
        Part("skruror", skruror(), 1, "PETG (naturfarget, matkontakt)", "som modellert",
             merknad="Lukket rør etter beholderen, utløp og 608-lager for skruen."),
        Part("fallror_mel", fallror(16, 19, 26, ms.utlop_x, G.AUG_Y), 1, "PETG (naturfarget, matkontakt)", "flensen ned"),
        Part("melskrue", melskrue(0), ms.segmenter, "PETG (naturfarget, matkontakt)", "stående",
             merknad="Tres på rustfri D-aksel ⌀8. Begge segmentene er like."),
        Part("tannhjul_skrue", tannhjul(tk[0], G.AUG_Z, ms.aksel_d, 0.5), 1, "PETG", "liggende",
             merknad=f"{tk[0]} tenner, modul {S.rorverk.modul}. M3-settskrue."),
        Part("tannhjul_rorer", tannhjul(tk[1], G.AGI_Z, S.rorverk.aksel_d, 0.0), 1, "PETG", "liggende",
             merknad=f"{tk[1]} tenner. Røreverket går {tk[0]}/{tk[1]} så fort som skruen."),
        Part("melmotorfeste", melmotorfeste(), 1, "PETG", "foten ned"),
        Part("traktlokk", traktlokk(), 1, "PETG", "toppen ned"),
        Part("saltboks", saltboks(), 1, "PETG (naturfarget, matkontakt)", "toppen ned",
             merknad="Med motorplate for NEMA17 pannekake. Printes opp-ned."),
        Part("saltlokk", saltlokk(), 1, "PETG", "toppen ned",
             merknad="Lomme for silikagel. 2 mm silikonsnor i sporet."),
        Part("saltskrue", saltskrue(), 1, "PETG (naturfarget, matkontakt)", "stående",
             merknad="Stepperens aksel (⌀5 med flate) går rett inn i enden."),
        Part("fallror_salt", fallror(5, 8, 13, S.saltskrue.utlop[0], G.SALT_Y), 1, "PETG (naturfarget, matkontakt)", "flensen ned"),
        Part("takmodul", takmodul(), 1, "PETG", "toppen ned",
             merknad="ToF, IR-føler, kamera, lys, dyse og de to klaffservoene. Skrus til topplata med M3."),
        Part("klaff_mel", klaff("mel"), 1, "PETG (naturfarget, matkontakt)", "som modellert",
             merknad="Skrus på servoarmen. Dreies 90° til siden under dosering."),
        Part("klaff_salt", klaff("salt"), 1, "PETG (naturfarget, matkontakt)", "som modellert"),
        Part("varmekanal", varmekanal(), 1, "PETG", "baksiden ned",
             merknad="Holder kjøleribba mot bakveggen. 40 mm vifte foran åpningen øverst."),
        Part("dorhengsel_ramme", dorhengsel_ramme(S.dor.hengsel_z[0]), 2, "PETG", "liggende",
             merknad="M6 × 45 hengselbolt med låsemutter."),
        Part("dorhengsel_dor", dorhengsel_dor(S.dor.hengsel_z[0]), 2, "PETG", "liggende", gruppe="dor"),
        Part("dorhandtak", dorhandtak(), 1, "PETG", "liggende", gruppe="dor",
             merknad="Magnet ⌀10 × 3 presses inn bak. Stålskive på skilleveggstolpen."),
        Part("bryternese", bryternese(), 1, "PETG", "flensen ned", gruppe="dor", merknad="Limes på innsiden av døra."),
        Part("bryterholder", bryterholder(), 1, "PETG", "liggende", merknad="For KW11-dørbryteren."),
        Part("kontrollpanel", kontrollpanel(), 1, "PETG", "frontflaten ned"),
        Part("bakpanelinnsats", bakpanelinnsats(), 1, "PETG", "utsiden ned"),
        Part("tankskuff", tankskuff(), 1, "PETG", "frontflaten ned", merknad="Fronten lukker luka for vanntanken."),
        Part("elektronikkplate", elektronikkplate(), 1, "PETG", "veggen ned"),
        Part("fot", fot(), 4, "PETG + gummipute", "som modellert"),
    ]
    orient = {
        "krage": FLIP, "melskrue": Rot(0, -90, 0), "saltskrue": Rot(0, -90, 0),
        "tannhjul_skrue": Rot(0, 90, 0), "tannhjul_rorer": Rot(0, 90, 0),
        "traktlokk": FLIP, "saltboks": FLIP, "saltlokk": FLIP, "takmodul": FLIP,
        "fallror_mel": FLIP, "fallror_salt": FLIP, "varmekanal": DOWN_MAX_Y,
        "dorhengsel_ramme": NONE, "dorhengsel_dor": NONE, "dorhandtak": DOWN_MAX_Y,
        "bryternese": DOWN_MIN_Y, "bryterholder": Rot(0, 90, 0), "kontrollpanel": DOWN_MIN_Y,
        "bakpanelinnsats": DOWN_MAX_Y, "tankskuff": DOWN_MIN_Y, "elektronikkplate": Rot(0, 90, 0),
        "melmotorfeste": NONE,
    }
    for p in parts:
        p.print_rot = orient.get(p.navn, NONE)
    return parts


def kopier(navn: str):
    """Extra assembly placements (transforms applied to the base shape)."""
    if navn in ("dorhengsel_ramme", "dorhengsel_dor"):
        return [Pos(0, 0, S.dor.hengsel_z[1] - S.dor.hengsel_z[0])]
    if navn == "melskrue":
        x0 = S.trakt.x[0] + 1
        x1 = S.melskrue.utlop_x + 16
        step = (x1 - x0) / S.melskrue.segmenter
        return [Pos(step * i, 0, 0) for i in range(1, S.melskrue.segmenter)]
    if navn == "fot":
        dx = (G.X1 - 35) - (G.X0 + 35)
        dy = (G.Y1 - 35) - (G.Y0 + 35)
        return [Pos(dx, 0, 0), Pos(0, dy, 0), Pos(dx, dy, 0)]
    return []
