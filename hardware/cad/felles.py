"""Shared helpers for the Surdeigsbaker v0 CAD (build123d, algebra mode)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml
from build123d import Box, Cone, Cylinder, Pos, Rot

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "hardware" / "spec" / "v0.yaml"
OUT = ROOT / "hardware" / "v0"


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


def m5_slot_hole(x, y, z0, z1):
    return cyl_z(S.skrue.m5_klaring / 2, z0, z1, x, y)


# ---------------------------------------------------------------- geometry


def bowl_radius(z_rel: float) -> float:
    """Inner wall radius of the bowl at height z_rel above its bottom (cone model)."""
    b = S.bolle
    r0, r1 = b.bunn_d / 2, b.kant_d / 2
    return r0 + (r1 - r0) * max(0.0, min(z_rel, b.hoyde)) / b.hoyde


def hook_points():
    """Hook centre-line (x, z) in the hook's own plane; x = radius, rotate about z."""
    k, z_b = S.krok, S.varmeplate.topp_z
    z_top = z_b + k.c_topp
    z_bot = z_b + k.c_bunn
    r_top = bowl_radius(k.c_topp) - k.klaring_vegg - k.stang_d / 2
    r_low = bowl_radius(k.c_bunn + 15) - k.klaring_vegg - k.stang_d / 2
    return [
        (0.0, k.topp_z),
        (0.0, z_top),
        (r_top, z_top),
        (r_low, z_bot),
        (k.indre_r, z_bot),
    ]


def rotate_about_hinge(y, z, theta_deg):
    """Rotate a point (y, z) of the lid about the hinge axis by the opening angle."""
    t = math.radians(theta_deg)
    yh, zh = S.lokk.hengsel_akse_y, S.lokk.hengsel_akse_z
    dy, dz = y - yh, z - zh
    return yh + dy * math.cos(t) + dz * math.sin(t), zh - dy * math.sin(t) + dz * math.cos(t)


@dataclass
class Part:
    """A printed part with metadata used for exports and the print list."""

    navn: str
    shape: object
    antall: int = 1
    materiale: str = "PETG"
    orientering: str = "som modellert"
    trinn: int = 1
    merknad: str = ""
