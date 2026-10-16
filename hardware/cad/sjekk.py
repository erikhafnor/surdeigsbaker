"""Design checks for Surdeigsbaker v0 → hardware/v0/sjekkrapport.md."""

from __future__ import annotations

import math

import numpy as np
from build123d import FilletPolyline, Vector

from felles import S, bowl_radius, hook_points, rotate_about_hinge


def _hook_samples(park_angle_deg=90.0, n=400):
    k = S.krok
    a = math.radians(park_angle_deg)
    pts = [Vector(r * math.cos(a), r * math.sin(a), z) for r, z in hook_points()]
    path = FilletPolyline(*pts, radius=k.boyeradius)
    return np.array([tuple(path.position_at(t / (n - 1))) for t in range(n)]), path


def bed_fit(parts):
    bx, by, bz = S.skriver.x, S.skriver.y, S.skriver.z
    rows = []
    for p in parts:
        if p.antall == 0:
            continue
        bb = (p.print_rot * p.shape).bounding_box()
        dx, dy, dz = bb.size.X, bb.size.Y, bb.size.Z
        a, b = max(dx, dy), min(dx, dy)
        ok = a <= bx and b <= by and dz <= bz
        rows.append((p.navn, f"{dx:.0f} × {dy:.0f} × {dz:.0f}", "✅" if ok else "❌"))
    return rows


def hook_bowl_clearance():
    """Min distance from the rotating hook surface to bowl wall and bottom."""
    pts, path = _hook_samples(0.0)
    rod = S.krok.stang_d / 2
    zb = S.varmeplate.topp_z + S.bolle.gods
    min_wall, min_bottom = 1e9, 1e9
    for x, _y, z in pts:
        r = abs(x)
        if z <= S.varmeplate.topp_z + S.bolle.hoyde:
            min_wall = min(min_wall, bowl_radius(z - S.varmeplate.topp_z) - r - rod)
        min_bottom = min(min_bottom, z - rod - zb)
    return min_wall, min_bottom, path.length


def _bowl_clearance(r, z, rad):
    """Clearance from a sphere (radius rad) at (r, z) to the bowl wall or rim lip."""
    zb = S.varmeplate.topp_z
    z_rim = zb + S.bolle.hoyde
    rim_r = S.bolle.kant_d / 2
    if z > z_rim:
        if rim_r - 1 <= r <= rim_r + 4:
            dr = 0.0
        else:
            dr = min(abs(r - (rim_r - 1)), abs(r - (rim_r + 4)))
        return math.hypot(dr, z - z_rim) - rad
    rw = bowl_radius(z - zb)
    inner = rw - r - rad
    outer = r - (rw + (4 if z > z_rim - 3 else 1)) - rad
    return max(inner, outer)


def lid_swing(step=1.0, max_angle=100.0):
    """Hook (parked towards the hinge) and rim pads vs. bowl while opening the lid."""
    hook, _ = _hook_samples(90.0)
    rod = S.krok.stang_d / 2
    kp = S.kantpress
    z_tip = S.ramme.hoyde - S.lokk.foring_t - 65 + 7   # centre of the ⌀14 tip when fully extended
    pads = [(kp.radius * math.cos(math.radians(a)), kp.radius * math.sin(math.radians(a)), z_tip)
            for a in kp.vinkler]
    worst = (1e9, 0.0, "")
    theta = 0.0
    while theta <= max_angle + 1e-9:
        for label, pts, rad, skip_below in (("krok", hook, rod, 0.0), ("kantpute", pads, 7.0, 3.0)):
            if theta < skip_below:
                continue
            for x, y, z in pts:
                yy, zz = rotate_about_hinge(y, z, theta)
                c = _bowl_clearance(math.hypot(x, yy), zz, rad)
                if c < worst[0]:
                    worst = (c, theta, label)
        theta += step
    return worst


def hinge_stop_angle(hinge_frame, hinge_lid):
    from build123d import Pos, Rot

    yh, zh = S.lokk.hengsel_akse_y, S.lokk.hengsel_akse_z
    for theta in range(80, 131):
        moved = Pos(0, yh, zh) * Rot(-theta, 0, 0) * Pos(0, -yh, -zh) * hinge_lid
        inter = hinge_frame & moved
        vol = sum(s.volume for s in inter.solids()) if inter is not None else 0.0
        if vol > 1.0:
            return theta
    return None


def lid_open_height(theta=100.0):
    """Highest and rear-most point of the lid assembly when open."""
    h = S.ramme.hoyde
    m = S.motor
    corners = [(-170, h + S.lokk.hoyde + 3), (170, h + S.lokk.hoyde + 3), (0, m.flate_z + m.lengde + 5)]
    zs, ys = [], []
    for y, z in corners:
        yy, zz = rotate_about_hinge(y, z, theta)
        zs.append(zz)
        ys.append(yy)
    hmax = 0.0
    for t in range(0, int(theta) + 1):
        for y, z in corners:
            hmax = max(hmax, rotate_about_hinge(y, z, t)[1])
    return hmax, max(ys)


def power_budget():
    e = S.elektrisk
    peak = e.motor_w + e.varme_w + e.elektronikk_w
    return peak, e.psu_w


def write_report(parts, path):
    lines = ["# Sjekkrapport – Surdeigsbaker v0", "",
             "Generert automatisk av `hardware/cad/bygg.py` fra `hardware/spec/v0.yaml`. Ikke rediger for hånd.", ""]

    lines += ["## 1. Passer delene på printeren?", "",
              f"Byggevolum: {S.skriver.x} × {S.skriver.y} × {S.skriver.z} mm (delene kan dreies 90° på platen).", "",
              "| Del | Mål i printretning (mm) | OK |", "|---|---|---|"]
    rows = bed_fit(parts)
    lines += [f"| {n} | {d} | {ok} |" for n, d, ok in rows]
    n_bad = sum(1 for r in rows if r[2] != "✅")
    lines += ["", f"**{len(rows) - n_bad} av {len(rows)} deler passer.**", ""]

    wall, bottom, length = hook_bowl_clearance()
    lines += ["## 2. Kroken i bollen", "",
              f"- Minste klaring mellom krok og bollevegg mens kroken roterer: **{wall:.1f} mm**",
              f"- Minste klaring mellom krok og bollebunn: **{bottom:.1f} mm**",
              f"- Utbrettet lengde på krokstanga (senterlinje): **{length:.0f} mm**. Kapp stanga til {math.ceil(length / 10) * 10 + 30} mm.",
              "- Modellen regner bollen som en rett kjegle. En ekte bolle har avrundet overgang mellom bunn og vegg, så **mål og sjekk klaringen med bollen din før du bøyer kroken**.", ""]

    c, th, lbl = lid_swing()
    lines += ["## 3. Lokket åpnes (0–100°)", "",
              "Kroken parkeres med C-en mot hengselen (hjemmesensoren) før lokket åpnes.", "",
              f"- Minste klaring mot bollen under åpning: **{c:.1f} mm** ({lbl}, ved {th:.0f}°)",
              "- Kantputene er unntatt de første 3°, fordi de skal ligge mot bollekanten når lokket er lukket.", ""]
    hmax, ymax = lid_open_height()
    foot = S.lokk.panel_t + 10.0                       # bottom panel + printed feet
    closed = S.motor.flate_z + 5 + S.motor.lengde      # top of the motor cover
    lines += [f"- Høyde med lukket lokk: **{closed + foot:.0f} mm** over benken.",
              f"- Høyeste punkt under åpning: **{hmax + foot:.0f} mm** over benken. Bakerste punkt: **{ymax - S.ramme.dybde / 2:.0f} mm** bak maskinen.",
              "- Høyere enn plassen under vanlige overskap: **trekk maskinen fram før du åpner lokket**, som med en kjøkkenmaskin.", ""]

    stop = hinge_stop_angle(parts_by_name(parts, "hengsel_ramme"), parts_by_name(parts, "hengsel_lokk"))
    lines += [f"- Hengselen stopper lokket ved ca. **{stop}°**." if stop else "- ⚠️ Fant ingen stopp i hengselen mellom 80 og 130°.", ""]

    peak, psu = power_budget()
    lines += ["## 4. Effekt", "",
              f"- Verste tilfelle (motor + varme + elektronikk samtidig): **{peak:.0f} W** mot strømforsyningens **{psu:.0f} W**.",
              "- Fastvaren slår av varmen mens motoren går, så det normale toppforbruket blir ca. motor + elektronikk.", ""]

    total = sum(p.shape.volume * max(p.antall, 0) for p in parts) / 1000
    lines += ["## 5. Filament", "",
              f"- Massivt volum av alle printede deler: **{total:.0f} cm³**. Med vanlige innstillinger (4 perimetre, 30–40 % fyll) blir det ca. **{total * 1.27 * 0.55:.0f} g PETG** pluss litt TPU.", ""]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"bed_bad": n_bad, "wall": wall, "bottom": bottom, "swing": c, "stop": stop}


def parts_by_name(parts, name):
    for p in parts:
        if p.navn == name:
            return p.shape
    raise KeyError(name)
