"""Shared helpers and derived geometry for the Surdeigsbaker v1 CAD (build123d, algebra mode)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from build123d import (
    Align,
    Box,
    Cone,
    Cylinder,
    Location,
    Plane,
    Polyline,
    Pos,
    Rot,
    extrude,
    make_face,
)

ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = ROOT / "hardware" / "spec" / "v1.yaml"
OUT = ROOT / "hardware" / "v1"


class Spec(dict):
    """dict with attribute access, recursively."""

    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc
        return Spec(value) if isinstance(value, dict) else value


def load_spec(path: Path = SPEC_PATH) -> Spec:
    with open(path, encoding="utf-8") as fh:
        return Spec(yaml.safe_load(fh))


S = load_spec()

# ---------------------------------------------------------------- primitives


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max coordinates."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def cyl_x(r, x0, x1, y, z):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


def cyl_y(r, y0, y1, x, z):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


def cone_z(r0, r1, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, (z0 + z1) / 2) * Cone(r0, r1, z1 - z0)


def ring_z(r_in, r_out, z0, z1, x=0.0, y=0.0):
    return cyl_z(r_out, z0, z1, x, y) - cyl_z(r_in, z0 - 1, z1 + 1, x, y)


def prism_x(points_yz, x0, x1):
    """Extrude a closed (y, z) polygon along +x from x0 to x1."""
    pts = [(y, z) for y, z in points_yz]
    face = make_face(Polyline(*pts, close=True))
    return extrude(Plane.YZ.offset(x0) * face, x1 - x0)


def rounded_rect_points(w, d, r, n=8):
    """Outline of a rounded rectangle centred on the origin (counter-clockwise)."""
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90),
                       (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def gear_points(module, teeth, pressure_deg=20.0, n_inv=6):
    """2D outline of a spur gear (involute flanks, simple root arc)."""
    m, z = module, teeth
    rp = m * z / 2
    rb = rp * math.cos(math.radians(pressure_deg))
    ra = rp + m
    rf = max(rp - 1.25 * m, 0.5)

    def inv(a):
        return math.tan(a) - a

    a_p = math.acos(rb / rp)
    half_tooth = math.pi / (2 * z) + inv(a_p)    # half tooth angle at the base circle
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z
        flank = []
        for i in range(n_inv + 1):
            r = max(rb, rf) + (ra - max(rb, rf)) * i / n_inv
            a = math.acos(min(1.0, rb / r))
            flank.append((r, half_tooth - inv(a)))
        left = [(r, c - t) for r, t in flank]
        right = [(r, c + t) for r, t in reversed(flank)]
        pts.append((rf, c - half_tooth - 0.25 * math.pi / z))
        pts.extend(left)
        pts.extend(right)
        pts.append((rf, c + half_tooth + 0.25 * math.pi / z))
    return [(r * math.cos(t), r * math.sin(t)) for r, t in pts]


def gear_x(module, teeth, x0, x1, y, z, bore=0.0, flat=0.0):
    """Spur gear with its axis along x."""
    face = make_face(Polyline(*gear_points(module, teeth), close=True))
    g = Pos(x0, y, z) * Rot(0, 90, 0) * Rot(0, 0, 0) * extrude(face, x1 - x0)
    if bore:
        g -= cyl_x(bore / 2, x0 - 1, x1 + 1, y, z)
        if flat:  # D-flat for a D-shaft
            g += box(x0, x1, y - bore / 2, y + bore / 2, z + bore / 2 - flat, z + bore / 2) & cyl_x(bore / 2 + 0.1, x0, x1, y, z)
    return g


# ---------------------------------------------------------------- derived geometry


class G:
    """Derived levels and positions (mm). Everything comes from the spec."""

    P = S.ramme.profil
    X0, X1 = S.ramme.x0, S.ramme.x1
    Y0, Y1 = S.ramme.y0, S.ramme.y1
    SKX = S.ramme.skille_x                    # right face of the partition posts
    H = S.ramme.hoyde
    RINGS = [(z, z + S.ramme.profil) for z in S.ramme.ringer_z]
    T = S.plate_t
    XPS = S.isolasjon_t

    Z_MG = S.mellomgulv.z                     # mellomgulv underside
    Z_MG1 = S.mellomgulv.z + S.mellomgulv.t
    Z_TP = S.toppplate.z
    Z_TP1 = S.toppplate.z + S.toppplate.t

    CX0, CX1 = S.kammer.x
    CY0, CY1 = S.kammer.y
    Z_FLOOR = S.kammer.gulv_z
    Z_CEIL = S.kammer.tak_z

    # holder chain (see hardware/v1/README.md, section on the weighing gap)
    GAP = S.formholder.spor_klaring
    KRAGE_FLENS_T = 1.5
    R_COL = S.lagersoyle.r
    R_KRAGE_IN = R_COL + 6
    R_KRAGE_OUT = R_KRAGE_IN + S.krage.vegg
    Z_KRAGE_TOP = Z_FLOOR + S.krage.hoyde
    Z_SKIRT = Z_FLOOR + KRAGE_FLENS_T + GAP
    R_HUB = R_KRAGE_IN - GAP
    R_GROOVE_OUT = R_KRAGE_OUT + GAP
    Z_GROOVE_TOP = Z_KRAGE_TOP + GAP
    Z_CUP_FLOOR = Z_GROOVE_TOP + 4
    Z_CUP_TOP = Z_CUP_FLOOR + S.formholder.kopp_dybde
    R_CUP_IN = S.form.fot_d / 2 + S.formholder.klaring_fot
    R_CUP_OUT = R_CUP_IN + S.formholder.vegg
    Z_COL_TOP = Z_SKIRT
    Z_PAN = Z_CUP_FLOOR + S.form.fot_h        # underside of the pan body
    Z_RIM = Z_PAN + S.form.hoyde

    Z_PL0 = S.plattform.z
    Z_PL1 = S.plattform.z + S.plattform.t

    # belt and pulleys under the platform
    Z_BELT0 = S.reim.z
    Z_BELT1 = S.reim.z + S.reim.bredde
    Z_PULLEY0 = Z_BELT0 - 5
    Z_PULLEY1 = Z_BELT1 + 5
    R_P_SHAFT = S.reim.tenner_aksel * S.reim.deling / (2 * math.pi)
    R_P_MOTOR = S.reim.tenner_motor * S.reim.deling / (2 * math.pi)

    # flour auger
    AUG_Z = 360.0
    AUG_Y = S.trakt.y_senter
    R_AUG = S.melskrue.d / 2
    R_TROUGH = R_AUG + S.melskrue.klaring
    Z_SLOT = AUG_Z + R_TROUGH                 # top of the vertical trough walls
    Z_HOPPER_TOP = S.ramme.hoyde - 3          # rim just under the top panel
    AGI_Z = AUG_Z + S.rorverk.avstand

    SALT_Z = 360.0
    SALT_Y = (S.saltboks.y[0] + S.saltboks.y[1]) / 2

    @classmethod
    def taper_top(cls):
        """z where the 60° hopper walls reach the full top width."""
        t = S.trakt
        return cls.Z_SLOT + (t.topp_b / 2 - cls.R_TROUGH) * math.tan(math.radians(t.vinkel))


def flap_servo_pos(which):
    """(x, y) of the output shaft of the flap servo for 'mel' or 'salt'."""
    if which == "mel":
        return (S.melskrue.utlop_x, G.AUG_Y - 34)
    return (S.saltskrue.utlop[0], G.SALT_Y + 22)


@dataclass
class Part:
    """A printed part with metadata used for exports and the print list."""

    navn: str
    shape: object
    antall: int = 1
    materiale: str = "PETG"
    orientering: str = "som modellert"
    merknad: str = ""
    gruppe: str = "fast"          # "vekt" = carried by the load cell, "dor" = on the door
    print_rot: object = field(default_factory=lambda: Location())
