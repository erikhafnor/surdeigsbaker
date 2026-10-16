"""Printed parts for Surdeigsbaker v0.

Every part is modelled in machine (assembly) coordinates so that the
assembly, the collision checks and the drawings share one geometry.
`print_rot` turns a part into a good print orientation before export.
"""

from __future__ import annotations

import math

from build123d import (
    Axis,
    Plane,
    Pos,
    Rot,
    Polyline,
    make_face,
    revolve,
    fillet,
)

from felles import S, Part, box, cone_z, cyl_x, cyl_y, cyl_z, bowl_radius

P = S.ramme.profil
HALF = S.ramme.bredde / 2           # 170
INNER = HALF - P                    # 150
Z_TOP = S.ramme.hoyde               # 320
Z_MID = S.ramme.midtramme_z         # 90
Z_FLOOR = Z_MID + P + S.ramme.gulvplate_t   # 113
M3, M5, M6 = S.skrue.m3_klaring / 2, S.skrue.m5_klaring / 2, S.skrue.m6_klaring / 2
M5_HEAD = S.skrue.m5_hode / 2
INSERT = S.skrue.m3_innsats / 2
YH, ZH = S.lokk.hengsel_akse_y, S.lokk.hengsel_akse_z
PANEL = 3.0

DOWN_MIN_Y = Rot(90, 0, 0)     # face with the smallest y ends up on the bed
DOWN_MAX_Y = Rot(-90, 0, 0)    # face with the largest y ends up on the bed
FLIP = Rot(180, 0, 0)          # top face ends up on the bed
NONE = Rot(0, 0, 0)


def round_vertical(part, r):
    """Cosmetic fillet on vertical edges; silently skipped if OCC refuses."""
    try:
        return fillet(part.edges().filter_by(Axis.Z), r)
    except Exception:  # noqa: BLE001 - cosmetic only
        return part


# ------------------------------------------------------------------ hinge


def hengsel_ramme(xh: float = 0.0):
    """Hinge leaf on the frame (centre knuckle + opening stop at ~100°)."""
    plate = box(xh - 20, xh + 20, INNER + P + PANEL, INNER + P + PANEL + 8, Z_TOP - P, Z_TOP)
    web = box(xh - 7.75, xh + 7.75, INNER + P + PANEL, YH, ZH - 14, ZH)
    knuckle = cyl_x(9, xh - 7.75, xh + 7.75, YH, ZH)
    stop = box(xh - 7.75, xh + 7.75, YH + 6, YH + 26, Z_TOP - P, ZH + 7)
    leaf = plate + web + knuckle + stop
    leaf -= cyl_x(M6, xh - 8, xh + 8, YH, ZH)
    y0 = INNER + P + PANEL
    for dx in (-12, 12):
        leaf -= cyl_y(M5, y0 - 1, y0 + 9, xh + dx, Z_TOP - P / 2)
        leaf -= cyl_y(M5_HEAD, y0 + 4, y0 + 9, xh + dx, Z_TOP - P / 2)
    return leaf


def hengsel_lokk(xh: float = 0.0):
    """Hinge leaf on the lid (two outer knuckles)."""
    y0 = INNER + P  # lid has no back panel
    plate = box(xh - 20, xh + 20, y0, y0 + 8, Z_TOP, Z_TOP + P)
    leaf = plate
    for x0, x1 in ((xh - 20, xh - 8.25), (xh + 8.25, xh + 20)):
        leaf += box(x0, x1, y0, YH, ZH, ZH + 14)
        leaf += cyl_x(9, x0, x1, YH, ZH)
    leaf -= cyl_x(M6, xh - 21, xh + 21, YH, ZH)
    for dx in (-14, 14):
        leaf -= cyl_y(M5, y0 - 1, y0 + 9, xh + dx, Z_TOP + P / 2)
        leaf -= cyl_y(M5_HEAD, y0 + 4, y0 + 9, xh + dx, Z_TOP + P / 2)
    return leaf


# ------------------------------------------------------------------ drive


def lagerhus():
    """Printed housing for 2 × 6000-2RS bearings, hangs under the lid liner."""
    lh = S.lagerhus
    z1 = lh.topp_z
    z0 = z1 - lh.hoyde
    rb = lh.lager_ytre_d / 2 + 0.05
    body = box(-40, 40, -22, 22, z0, z1)
    body = round_vertical(body, 4)
    body -= cyl_z(6.0, z0 - 1, z1 + 1)
    body -= cyl_z(rb, z1 - lh.lager_b, z1 + 1)
    body -= cyl_z(rb, z0 - 1, z0 + lh.lager_b)
    for x in (-lh.bolt_x, lh.bolt_x):
        body -= cyl_z(M5, z0 - 1, z1 + 1, x, 0)
        body -= cyl_z(M5_HEAD, z0 - 1, z0 + 6, x, 0)
    for y in (-15, 15):  # M3 inserts for the home-sensor arm
        body -= cyl_z(INSERT, z0 - 1, z0 + 6, 15, y)
    return body


def motorplate():
    m = S.motor
    z0 = S.lokk.hoyde + Z_TOP + S.lokk.panel_t
    z1 = z0 + m.motorplate_t
    tx = S.lokk.tverrbjelke_x
    plate = round_vertical(box(-55, 55, -80, 80, z0, z1), 8)
    plate -= cyl_z(S.kobling.d / 2 + 2, z0 - 1, z1 + 1)
    for x in (-tx, tx):
        for y in (-60, 60):
            plate -= cyl_z(M5, z0 - 1, z1 + 1, x, y)
            plate -= cyl_z(M5_HEAD, z1 - 6, z1 + 1, x, y)
        for y in (-40, 40):
            plate -= cyl_z(M5, z0 - 1, z1 + 1, x, y)
    pcd = m.get("flens_hullsirkel", 0) or 0
    if pcd > 0:  # optional holes for the motor's own flange screws, heads recessed underneath
        n, d = int(m.flens_hull_antall), m.flens_hull_d
        for i in range(n):
            a = math.radians(45 + i * 360 / n)
            x, y = pcd / 2 * math.cos(a), pcd / 2 * math.sin(a)
            plate -= cyl_z(d / 2, z0 - 1, z1 + 1, x, y)
            plate -= cyl_z(d, z0 - 1, z0 + 5, x, y)
    return plate


def motorklemme():
    m = S.motor
    z0 = m.flate_z
    r_in = m.kropp_d / 2 + 0.3
    r_out = r_in + 10
    tx = S.lokk.tverrbjelke_x
    flange = round_vertical(box(-45, 45, -55, 55, z0, z0 + 5), 6)
    ring = cyl_z(r_out, z0, z0 + 40)
    ears = box(r_in + 6, r_out + 14, -11, 11, z0 + 7, z0 + 37)
    clamp = flange + ring + ears
    clamp -= cyl_z(r_in, z0 - 1, z0 + 41)
    clamp -= box(r_in - 2, r_out + 15, -1, 1, z0 - 1, z0 + 41)  # split
    for z in (z0 + 15, z0 + 29):
        clamp -= cyl_y(M5, -12, 12, r_out + 6, z)
        clamp -= cyl_y(S.skrue.m3_mutter * 1.35 / 2 + 0.5, 8, 12, r_out + 6, z)  # M5 nut trap
    for x in (-tx, tx):
        for y in (-40, 40):
            clamp -= cyl_z(M5, z0 - 1, z0 + 6, x, y)
    return clamp


def motordeksel():
    m = S.motor
    z0 = m.flate_z + 5
    r_in = m.kropp_d / 2 + 10.6
    cover = cyl_z(r_in + 2.5, z0, z0 + m.lengde) - cyl_z(r_in, z0 - 1, z0 + m.lengde - 3)
    cover -= box(r_in - 4, r_in + 20, -13, 13, z0 - 1, z0 + 34)  # clamp ears + cable exit
    for i in range(8):
        a = i * 45 + 22.5
        cover -= Rot(0, 0, a) * box(r_in - 1, r_in + 4, -2, 2, z0 + m.lengde - 50, z0 + m.lengde - 12)
    return cover


# ------------------------------------------------------------------ lid internals


def kantpress_hus():
    """Spring housing for a rim pad (front instance; others are rotated copies)."""
    kp = S.kantpress
    z1 = Z_TOP - S.lokk.foring_t     # 317
    y = -kp.radius
    body = box(-10, 10, y - 10, y + 10, z1 - 40, z1)
    flange = box(-28, 28, y - 10, y + 10, z1 - 6, z1)
    part = round_vertical(body + flange, 3)
    part -= cyl_z(kp.fjaer_d / 2, z1 - 36, z1 + 1, 0, y)       # spring bore
    part -= cyl_z(4.0, z1 - 41, z1 - 35, 0, y)                  # lip for the plunger stem
    for x in (-20, 20):
        part -= cyl_z(M5, z1 - 7, z1 + 1, x, y)
    return part


def kantpress_stempel():
    kp = S.kantpress
    z1 = Z_TOP - S.lokk.foring_t
    y = -kp.radius
    collar = cyl_z(kp.fjaer_d / 2 - 0.3, z1 - 36, z1 - 30, 0, y)
    stem = cyl_z(3.8, z1 - 62, z1 - 36, 0, y)
    return collar + stem


def kantpress_tupp():
    kp = S.kantpress
    z1 = Z_TOP - S.lokk.foring_t
    y = -kp.radius
    tip = cyl_z(7.0, z1 - 65, z1 - 57, 0, y) - cyl_z(3.7, z1 - 62, z1 - 56, 0, y)
    return tip


def sensorhus():
    sx, sy = S.sensorhus.pos
    z1 = Z_TOP - S.lokk.foring_t
    z0 = z1 - 20
    tw, th = S.sensorhus.tof_kort
    body = round_vertical(box(sx - 22, sx + 22, sy - 22, sy + 22, z0, z1), 4)
    tof_x = sx - 8
    body -= box(tof_x - tw / 2 - 0.2, tof_x + tw / 2 + 0.2, sy - th / 2 - 0.2, sy + th / 2 + 0.2, z1 - 5, z1 + 1)
    body -= cyl_z(4.5, z0 - 1, z1, tof_x, sy)                    # ToF window
    ir_x = sx + 14
    body -= cyl_z(S.sensorhus.ir_d / 2, z0 - 1, z1 + 1, ir_x, sy)   # IR sensor
    for y in (-16, 16):
        body -= cyl_z(M5, z0 - 1, z1 + 1, sx, sy + y)
        body -= cyl_z(M5_HEAD, z0 - 1, z0 + 5, sx, sy + y)
    return body


def hjemmeflagg():
    z0 = 264.0
    ring = cyl_z(11, z0, z0 + 10) - cyl_z(S.krok.stang_d / 2 + 0.1, z0 - 1, z0 + 11)
    flag = box(10, 24, -1.2, 1.2, z0, z0 + 10)
    ear = box(-19, -9, -6, 6, z0, z0 + 10)
    part = ring + flag + ear
    part -= box(-20, -4, -0.75, 0.75, z0 - 1, z0 + 11)
    part -= cyl_y(1.7, -7, 7, -14.5, z0 + 5)
    return part


def sensorarm():
    z1 = S.lagerhus.topp_z - S.lagerhus.hoyde   # under the bearing housing
    plate = box(6, 30, -22, 22, z1 - 4, z1)
    web = box(26, 30, -10, 10, z1 - 32, z1)
    part = plate + web
    for y in (-15, 15):
        part -= cyl_z(M3, z1 - 5, z1 + 1, 15, y)
    part -= cyl_x(1.7, 25, 31, 0, z1 - 18)      # M3 for the slot sensor
    part -= box(25, 31, -6, 6, z1 - 31, z1 - 26)   # zip-tie slot
    return part


# ------------------------------------------------------------------ floor / bowl


def varmeplateholder():
    z0, z1 = Z_FLOOR, Z_FLOOR + 10
    rp = S.varmeplate.d / 2
    lip_top = S.varmeplate.topp_z - 1
    part = cyl_z(20, z0, z1)
    for a in (90, 210, 330):
        part += Rot(0, 0, a) * box(0, rp + 8, -7, 7, z0, z1)
        part += Rot(0, 0, a) * box(rp + 0.6, rp + 8, -7, 7, z1, lip_top)
        part -= Rot(0, 0, a) * cyl_z(M3, z0 - 1, z1 + 1, 60, 0)
        part -= Rot(0, 0, a) * box(20, rp - 4, -2, 2, z1 - 2, z1 + 1)   # wire groove
    return part


def _bowl_face_r(z):
    return bowl_radius(z - S.varmeplate.topp_z) + 0.5


def bollestotte(with_sensor: bool = False, angle: float = 30.0):
    """Bowl support segment (40° arc) that centres the bowl on the heater plate."""
    z0 = Z_FLOOR
    za, zb = 150.0, 188.0
    r_out = 118.0
    pts = [
        (102.0, 0, z0),
        (r_out, 0, z0),
        (r_out, 0, zb),
        (_bowl_face_r(zb), 0, zb),
        (_bowl_face_r(za), 0, za),
        (102.0, 0, za - (102.0 - _bowl_face_r(za))),
    ]
    face = make_face(Polyline(*pts, close=True))
    seg = revolve(face, Axis.Z, 40)
    seg = Rot(0, 0, -20) * seg
    zg = 172.0
    groove_face = Plane.XZ * Pos(_bowl_face_r(zg), zg) * _circle(1.7)
    groove = Rot(0, 0, -21) * revolve(groove_face, Axis.Z, 42)
    seg -= groove
    for a in (-12, 12):
        seg -= Rot(0, 0, a) * cyl_z(M3, z0 - 1, zb + 1, 110, 0)
        seg -= Rot(0, 0, a) * cyl_z(3.2, za, zb + 1, 110, 0)
    if with_sensor:
        zs = 168.0
        r_probe = bowl_radius(zs - S.varmeplate.topp_z) + 3.2
        seg -= cyl_y(3.2, -40, 40, r_probe, zs)
    return Rot(0, 0, angle) * seg


def _circle(r):
    from build123d import Circle

    return Circle(r)


# ------------------------------------------------------------------ base / electronics


def elektronikkplate():
    ep = S.elektronikkplate
    z0 = ep.z
    y0, y1 = -30.0, -30.0 + ep.d
    plate = round_vertical(box(-ep.b / 2, ep.b / 2, y0, y1, z0, z0 + ep.t), 5)
    y = y0 + 12
    while y < y1 - 8:
        for x in range(-100, 80, 38):
            plate -= box(x, x + 30, y - 1.7, y + 1.7, z0 - 1, z0 + ep.t + 1)
        y += 15
    for x in (-113, 113):
        for yy in (-18, 60, 138):
            plate -= cyl_z(M3, z0 - 1, z0 + ep.t + 1, x, yy)
    return plate


def plateholder(side: int = 1):
    ep = S.elektronikkplate
    s = side
    zt = ep.z
    x_in = INNER - 45
    wall = box(INNER - 4, INNER, -25, 145, 2, zt) if s > 0 else box(-INNER, -INNER + 4, -25, 145, 2, zt)
    ledge = box(x_in, INNER, -25, 145, zt - 4, zt) if s > 0 else box(-INNER, -x_in, -25, 145, zt - 4, zt)
    part = wall + ledge
    for y in (0, 60, 120):
        part -= cyl_x(M5, s * INNER - 5, s * INNER + 5, y, P / 2)
    for y in (-18, 60, 138):
        part -= cyl_z(INSERT, zt - 6, zt + 1, s * 113, y)
    return part


def kontrollpanel():
    kp = S.kontrollpanel
    w, h = kp.utsparing
    zc = (P + Z_MID) / 2            # 55
    y_out = -HALF - PANEL           # -173
    plate = box(-w / 2 - 8, w / 2 + 8, y_out - 4, y_out, zc - h / 2 - 8, zc + h / 2 + 8)
    rim = box(-w / 2 + 0.4, w / 2 - 0.4, y_out, y_out + 4, zc - h / 2 + 0.4, zc + h / 2 - 0.4)
    rim -= box(-w / 2 + 2.4, w / 2 - 2.4, y_out - 1, y_out + 5, zc - h / 2 + 2.4, zc + h / 2 - 2.4)
    part = plate + rim
    yy = (y_out - 5, y_out + 1)
    part -= cyl_y(kp.e_stopp_d / 2, *yy, -48, zc)
    ow, oh = kp.oled_vindu
    part -= box(2 - ow / 2, 2 + ow / 2, *yy, zc + 3 - oh / 2, zc + 3 + oh / 2)
    hx, hz = kp.oled_hull
    for dx in (-hx / 2, hx / 2):
        for dz in (-hz / 2, hz / 2):
            part -= cyl_y(kp.oled_hull_d / 2, *yy, 2 + dx, zc + 3 + dz)
    part -= cyl_y(kp.led_d / 2, *yy, 2, zc + 22)
    for x in (40, 62):
        part -= cyl_y(kp.knapp_d / 2, *yy, x, zc)
    for x in (-w / 2 - 3, w / 2 + 3):
        for z in (zc - h / 2 - 3, zc + h / 2 + 3):
            part -= cyl_y(M3, *yy, x, z)
    return part


def bakpanelinnsats():
    bp = S.bakpanel
    w, h = bp.utsparing
    xc, zc = 70.0, (P + Z_MID) / 2
    y_out = HALF + PANEL            # 173
    plate = box(xc - w / 2 - 6, xc + w / 2 + 6, y_out, y_out + 4, zc - h / 2 - 8, zc + h / 2 + 8)
    rim = box(xc - w / 2 + 0.4, xc + w / 2 - 0.4, y_out - 4, y_out, zc - h / 2 + 0.4, zc + h / 2 - 0.4)
    rim -= box(xc - w / 2 + 2.4, xc + w / 2 - 2.4, y_out - 5, y_out + 1, zc - h / 2 + 2.4, zc + h / 2 - 2.4)
    part = plate + rim
    yy = (y_out - 1, y_out + 5)
    part -= cyl_y(bp.dc_hull_d / 2, *yy, xc - 30, zc)
    uw, uh = bp.usb_slisse
    part -= box(xc + 15 - uw / 2, xc + 15 + uw / 2, *yy, zc - uh / 2, zc + uh / 2)
    part -= cyl_y(6.5, *yy, xc + 45, zc)          # grommet for the lid cable
    for x in (xc - w / 2 - 3, xc + w / 2 + 3):
        for z in (zc - h / 2 - 4, zc + h / 2 + 4):
            part -= cyl_y(M3, *yy, x, z)
    return part


def romfolerhus():
    x0, z0 = -115.0, 45.0
    y_out = HALF + PANEL
    shell = box(x0, x0 + 30, y_out, y_out + 16, z0, z0 + 32) - box(x0 + 2, x0 + 28, y_out - 1, y_out + 14, z0 + 2, z0 + 30)
    for i in range(5):
        shell -= box(x0 + 5 + i * 4.5, x0 + 7 + i * 4.5, y_out + 13, y_out + 17, z0 + 6, z0 + 26)
    for z in (z0 + 8, z0 + 24):
        shell -= cyl_y(M3, y_out - 1, y_out + 3, x0 + 15, z)
    return shell


def fot():
    x, y = HALF - 10, HALF - 40
    z1 = -PANEL
    foot = cyl_z(15, z1 - 10, z1, x, y)
    foot -= cyl_z(M5, z1 - 11, z1 + 1, x, y)
    foot -= cone_z(5.0, M5, z1 - 10.01, z1 - 7.5, x, y)
    foot -= cyl_z(12, z1 - 10.01, z1 - 8.5, x, y)    # recess for a rubber pad
    return foot


# ------------------------------------------------------------------ lid closure


def bryterholder():
    ms = S.mikrobryter
    y_back = -HALF - PANEL          # -173
    plate = box(100, 150, y_back - 3, y_back, 288, 318)
    boss = box(122, 148, y_back - 6, y_back - 3, 296, 314)
    part = plate + boss
    part -= cyl_y(M5, y_back - 4, y_back + 1, 110, Z_TOP - P / 2)
    for x in (135 - ms.hull_avstand / 2, 135 + ms.hull_avstand / 2):
        part -= cyl_y(ms.hull_d / 2, y_back - 7, y_back + 1, x, 305)
    return part


def bryternese():
    y_face = -HALF                  # lid front face
    block = box(125, 150, y_face - 18, y_face, Z_TOP + 4, Z_TOP + P)
    nose = box(130, 146, y_face - 18, y_face - 8, Z_TOP - 2, Z_TOP + 4)
    part = block + nose
    part -= cyl_y(M5, y_face - 19, y_face + 1, 137.5, Z_TOP + P / 2)
    part -= cyl_y(M5_HEAD, y_face - 19, y_face - 10, 137.5, Z_TOP + P / 2)
    return part


def styrekile():
    x, y = HALF - P / 2, -110.0
    return box(x - 2.9, x + 2.9, y - 10, y + 10, Z_TOP - 4, Z_TOP + 4)


# ------------------------------------------------------------------ small hardware


def kabelklemme():
    base = box(-10, 10, -6, 6, 0, 3)
    tab = box(-8, 8, -2.9, 2.9, -3, 0)
    loop = box(-3, 3, -6, 6, 3, 9) - box(-4, 4, -2, 2, 4, 7)
    return (base + tab + loop) - cyl_z(M5, -4, 4)


def vinkel_2020():
    leg_a = box(0, 30, 0, 20, 0, 4)
    leg_b = box(0, 4, 0, 20, 0, 30)
    gusset = make_face(Polyline((4, 9, 4), (24, 9, 4), (4, 9, 24), close=True))
    from build123d import extrude

    gus = extrude(gusset, amount=2)
    part = leg_a + leg_b + gus
    part -= cyl_z(M5, -1, 5, 19, 10)
    part -= cyl_x(M5, -1, 5, 10, 19)
    return part


# ------------------------------------------------------------------ registry


def alle_deler() -> list[Part]:
    """All printed parts with metadata. Coordinates = assembly position."""
    kp_angles = S.kantpress.vinkler
    parts = [
        Part("hengsel_ramme", hengsel_ramme(S.lokk.hengsel_x), 2, "PETG", "monteringsflaten ned", 1,
             "M6 × 45 hengselbolt med låsemutter. Venstre og høyre er like."),
        Part("hengsel_lokk", hengsel_lokk(S.lokk.hengsel_x), 2, "PETG", "monteringsflaten ned", 1),
        Part("lagerhus", lagerhus(), 1, "PETG", "som modellert", 1,
             "2 × 6000-2RS presses inn, ett fra hver side. Bruk 5 perimetre."),
        Part("motorplate", motorplate(), 1, "PETG", "som modellert", 1, "5 perimetre, 40 % gyroid"),
        Part("motorklemme", motorklemme(), 1, "PETG", "flensen ned", 1,
             "Indre ⌀ = motor.kropp_d + 0,6. Legg 1 mm gummi rundt motoren."),
        Part("motordeksel", motordeksel(), 1, "PETG", "toppen ned", 1),
        Part("kantpress_hus", kantpress_hus(), len(kp_angles), "PETG", "flensen ned", 1),
        Part("kantpress_stempel", kantpress_stempel(), len(kp_angles), "PETG", "stående", 1),
        Part("kantpress_tupp", kantpress_tupp(), len(kp_angles), "TPU 95A", "som modellert", 1,
             "Myk tupp som klemmer bollekanten. Kan erstattes med kjøpt silikonfot."),
        Part("sensorhus", sensorhus(), 1, "PETG", "toppen ned", 1),
        Part("hjemmeflagg", hjemmeflagg(), 1, "PETG", "som modellert", 1),
        Part("sensorarm", sensorarm(), 1, "PETG", "toppen ned", 1),
        Part("varmeplateholder", varmeplateholder(), 1, "PETG", "som modellert", 1,
             "Holder aluminiumsplaten. Temperaturen holdes ≤ 45 °C, termostaten bryter ved 60 °C."),
        Part("bollestotte", bollestotte(False, 30), 2, "PETG", "toppen ned", 1,
             "Silikonsnor ⌀3 mm i sporet gir friksjon mot bollen."),
        Part("bollestotte_foler", bollestotte(True, 270), 1, "PETG", "toppen ned", 1,
             "Med kanal for DS18B20-føleren som ligger mot bolleveggen."),
        Part("elektronikkplate", elektronikkplate(), 1, "PETG", "som modellert", 1),
        Part("plateholder_hoyre", plateholder(1), 1, "PETG", "veggen ned", 1),
        Part("plateholder_venstre", plateholder(-1), 1, "PETG", "veggen ned", 1),
        Part("kontrollpanel", kontrollpanel(), 1, "PETG", "frontflaten ned", 1),
        Part("bakpanelinnsats", bakpanelinnsats(), 1, "PETG", "utsiden ned", 1),
        Part("romfolerhus", romfolerhus(), 1, "PETG", "som modellert", 1),
        Part("fot", fot(), 4, "PETG + gummipute", "som modellert", 1),
        Part("bryterholder", bryterholder(), 1, "PETG", "baksiden ned", 1),
        Part("bryternese", bryternese(), 1, "PETG", "baksiden ned", 1),
        Part("styrekile", styrekile(), 2, "PETG", "liggende", 1),
        Part("kabelklemme", kabelklemme(), 6, "PETG", "som modellert", 1),
        Part("vinkel_2020", vinkel_2020(), 0, "PETG", "som modellert", 1,
             "Valgfri. Kjøpte hjørnebeslag i aluminium anbefales (32 stk)."),
    ]
    orient = {
        "hengsel_ramme": DOWN_MIN_Y, "hengsel_lokk": DOWN_MIN_Y,
        "motordeksel": FLIP, "kantpress_hus": FLIP, "sensorhus": FLIP, "sensorarm": FLIP,
        "bollestotte": FLIP, "bollestotte_foler": FLIP,
        "plateholder_hoyre": Rot(0, 90, 0), "plateholder_venstre": Rot(0, -90, 0),
        "kontrollpanel": DOWN_MIN_Y, "bakpanelinnsats": DOWN_MAX_Y, "romfolerhus": DOWN_MIN_Y,
        "bryterholder": DOWN_MAX_Y, "bryternese": DOWN_MAX_Y, "styrekile": Rot(0, 90, 0),
    }
    for p in parts:
        p.print_rot = orient.get(p.navn, NONE)
    return parts


def kopier(navn: str):
    """Extra assembly placements (transforms applied to the base shape)."""
    if navn in ("hengsel_ramme", "hengsel_lokk"):
        return [Pos(-2 * S.lokk.hengsel_x, 0, 0)]
    if navn.startswith("kantpress"):
        return [Rot(0, 0, a - 270) for a in S.kantpress.vinkler if a != 270]
    if navn == "bollestotte":
        return [Rot(0, 0, 120)]
    if navn == "fot":
        x, y = HALF - 10, HALF - 40
        return [Pos(-2 * x, 0, 0), Pos(0, -2 * y, 0), Pos(-2 * x, -2 * y, 0)]
    if navn == "styrekile":
        return [Pos(-2 * (HALF - P / 2), 0, 0)]
    return []
