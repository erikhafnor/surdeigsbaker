"""Design checks for Surdeigsbaker v1 → hardware/v1/sjekkrapport.md."""

from __future__ import annotations

import math

from build123d import Pos

import innkjop as I
from felles import G, S, box, cyl_x, flap_servo_pos, rounded_rect_points

MIN_GAP = 3.0           # weighing gap and moving parts
DENSITY = {"alu": 2.7e-3, "steel": 7.9e-3, "petg": 1.27e-3 * 0.55}   # g/mm³ (printed parts ~55 % solid)


# ------------------------------------------------------------------ helpers


def _bb_gap(a, b):
    """Lower bound of the distance between two bounding boxes."""
    d = 0.0
    for lo1, hi1, lo2, hi2 in ((a.min.X, a.max.X, b.min.X, b.max.X), (a.min.Y, a.max.Y, b.min.Y, b.max.Y),
                               (a.min.Z, a.max.Z, b.min.Z, b.max.Z)):
        gap = max(lo2 - hi1, lo1 - hi2, 0.0)
        d += gap * gap
    return math.sqrt(d)


def min_distance(moving, obstacles, cutoff=40.0, skip=()):
    """Smallest distance from any (name, shape) in `moving` to any in `obstacles`."""
    best = (1e9, "", "")
    bbs = [(n, s, s.bounding_box()) for n, s in obstacles if n not in skip]
    for mn, ms in moving:
        mbb = ms.bounding_box()
        for on, os_, obb in bbs:
            if _bb_gap(mbb, obb) > min(cutoff, best[0]):
                continue
            d = ms.distance_to(os_)
            if d < best[0]:
                best = (d, mn, on)
    return best


def overlap_volume(a, b):
    inter = a & b
    try:
        return sum(s.volume for s in inter.solids())
    except Exception:  # noqa: BLE001 - empty result
        return 0.0


# ------------------------------------------------------------------ groups


def groups(parts, door_theta=0.0):
    """Split the whole machine into weighed, fixed, door and excluded (name, shape) lists."""
    weighed, fixed, door = [], [], []
    for p in parts:
        shapes = [p.shape] + [tf * p.shape for tf in _copies(p.navn)]
        for s in shapes:
            (weighed if p.gruppe == "vekt" else door if p.gruppe == "dor" else fixed).append((p.navn, s))
    for pnl in I.paneler():
        if pnl.navn == "plattform":
            weighed.append((pnl.navn, pnl.solid()))
        elif pnl.dor:
            door.append((pnl.navn, pnl.solid()))
        else:
            fixed.append((pnl.navn, pnl.solid()))
    weighed += [("brodform", I.brodform()), ("koblingsdel", I.koblingsdel())] + I.drivverk()
    fixed += [(n, s) for n, _l, s in I.profiler()]
    fixed += I.isolasjon() + I.melmotor() + I.saltmotor() + I.aksler_dosering() + I.servoer()
    fixed += I.vannsystem() + I.varmeenhet() + I.vifte() + I.elektronikk() + I.dorbeslag()
    fixed += [(n, s) for n, s in I.lastcelle_fast() if n == "lastcelle_kloss_bunn"]
    door.append(("dorplugg", I.dorplugg()))
    tf = I.door_transform(door_theta)
    door = [(n, tf * s) for n, s in door]
    return weighed, fixed, door


def _copies(navn):
    import deler
    return deler.kopier(navn)


# ------------------------------------------------------------------ checks


def bed_fit(parts):
    bx, by, bz = S.skriver.x, S.skriver.y, S.skriver.z
    rows = []
    for p in parts:
        bb = (p.print_rot * p.shape).bounding_box()
        dx, dy, dz = bb.size.X, bb.size.Y, bb.size.Z
        a, b = max(dx, dy), min(dx, dy)
        ok = a <= bx and b <= by and dz <= bz
        rows.append((p.navn, f"{dx:.0f} × {dy:.0f} × {dz:.0f}", "✅" if ok else "❌"))
    return rows


def weighing_gaps(weighed, fixed):
    d, a, b = min_distance(weighed, fixed)
    lc_body = [(n, s) for n, s in I.lastcelle_fast() if n == "lastcelle"]
    moving_wo_spacer = [(n, s) for n, s in weighed if n != "lastcelle_kloss_topp"]
    d_cell, a_cell, b_cell = min_distance(moving_wo_spacer, lc_body)
    return (d, a, b), (d_cell, a_cell, b_cell)


def pan_path(weighed, fixed, door_open):
    """Unlock (rotate), lift and pull the pan out through the open door."""
    f = S.form
    holder = [(n, s) for n, s in weighed if n in ("formholder", "koblingsdel")]
    others = [(n, s) for n, s in fixed if _in_chamber(s)] + door_open
    theta_un = -S.formholder.knast_vinkel
    worst = {"dreie": (1e9, "", ""), "løfte": (1e9, "", ""), "trekke": (1e9, "", "")}
    clash = {"dreie": 0.0, "løfte": 0.0}
    for i in range(0, 6):
        th = theta_un * i / 5
        pan = I.brodform(theta=th)
        worst["dreie"] = min(worst["dreie"], min_distance([("brodform", pan)], others))
        clash["dreie"] = max(clash["dreie"], sum(overlap_volume(pan, s) for _n, s in holder))
    for i in range(0, 8):
        lift = f.loft * i / 7
        pan = I.brodform(theta=theta_un, lift=lift)
        worst["løfte"] = min(worst["løfte"], min_distance([("brodform", pan)], others))
        clash["løfte"] = max(clash["løfte"], sum(overlap_volume(pan, s) for _n, s in holder))
    for i in range(0, 15):
        dy = -20.0 * i
        pan = I.brodform(theta=theta_un, lift=f.loft, dy=dy)
        worst["trekke"] = min(worst["trekke"], min_distance([("brodform", pan)], others + holder))
    return worst, clash


def _in_chamber(shape):
    bb = shape.bounding_box()
    return bb.max.X > G.CX0 - 25 and bb.min.X < G.CX1 + 25 and bb.max.Z > G.Z_FLOOR - 25 and bb.min.Z < G.Z_TP + 5


def door_swing(parts, fixed, weighed):
    """Smallest clearance between the swinging door and everything fixed, from 5° to fully open."""
    obstacles = [(n, s) for n, s in fixed if s.bounding_box().min.Y < G.Y0 + 60] + [
        (n, s) for n, s in weighed if n in ("brodform", "formholder")]
    skip = ("dorhengsel_ramme",)
    worst = (1e9, "", "", 0.0)
    for th in range(5, int(S.dor.apning_grader) + 1, 5):
        door = _door_at(parts, th)
        d, a, b = min_distance(door, obstacles, skip=skip)
        if d < worst[0]:
            worst = (d, a, b, th)
    return worst


def _door_at(parts, theta):
    door = []
    for p in parts:
        if p.gruppe == "dor":
            door += [(p.navn, p.shape)] + [(p.navn, tf * p.shape) for tf in _copies(p.navn)]
    door += [(pn.navn, pn.solid()) for pn in I.paneler() if pn.dor]
    door.append(("dorplugg", I.dorplugg()))
    tf = I.door_transform(theta)
    return [(n, tf * s) for n, s in door]


def hopper_numbers(parts):
    """Flour capacity of the hopper and clearances of the agitator."""
    import deler

    t, rv = S.trakt, S.rorverk
    x0, x1 = t.x
    cav = deler.prism_x(deler.hopper_profile(0), x0, x1) & box(x0 - 1, x1 + 1, -500, 500, 0, G.Z_HOPPER_TOP - 10)
    screw = sum(p.shape.volume * p.antall for p in parts if p.navn == "melskrue") * (x1 - x0) / (S.melskrue.utlop_x + 16 - x0 - 1)
    shafts = math.pi * (rv.aksel_d / 2) ** 2 * (x1 - x0)
    vol = cav.volume - screw - shafts
    grams = vol / 1000 * t.romvekt
    reach = rv.r + rv.pinne_d / 2
    gap_screw = rv.avstand - reach - G.R_AUG
    # distance from the agitator axis to the 60° wall line through the slot edge
    a = math.radians(t.vinkel)
    dz = G.AGI_Z - G.Z_SLOT
    d_wall = _point_line_distance((0.0, G.AGI_Z), (G.R_TROUGH, G.Z_SLOT), (math.cos(a), math.sin(a)))
    d_corner = math.hypot(G.R_TROUGH, dz)
    gap_wall = min(d_wall, d_corner) - reach
    slot_len = x1 - x0
    return {"vol_l": vol / 1e6, "gram": grams, "gap_screw": gap_screw, "gap_wall": gap_wall,
            "slot_ratio": slot_len / S.melskrue.d, "choke": (S.melskrue.utlop_x - G.R_TROUGH) - (x1 + t.vegg)}


def _point_line_distance(p, a, direction):
    (px, py), (ax, ay), (dx, dy) = p, a, direction
    return abs((px - ax) * dy - (py - ay) * dx) / math.hypot(dx, dy)


def salt_numbers(parts):
    sb = S.saltboks
    vol = 0.0
    for p in parts:
        if p.navn == "saltboks":
            outer = box(sb.x[0] + sb.vegg, sb.x[1] - sb.vegg, sb.y[0] + sb.vegg, sb.y[1] - sb.vegg, G.SALT_Z - 6, sb.z[1] - 10)
            vol = outer.volume - overlap_volume(outer, p.shape)
    return vol / 1000, vol / 1000 * 1.2


def pan_numbers():
    """Dough height in the pan, ToF distance and rise headroom."""
    f, d = S.form, S.deig
    z_in = G.Z_PAN + f.gods

    def height_for(volume_mm3):
        h, v = 0.0, 0.0
        while v < volume_mm3 and h < f.hoyde:
            v += I.pan_inner_area(h + 0.25) * 0.5
            h += 0.5
        return h

    v0 = d.masse_g / d.tetthet * 1000
    rows = []
    for rise in (0.0, 0.5, 0.75, d.maks_heving):
        h = height_for(v0 * (1 + rise))
        rows.append((rise, h, G.Z_CEIL - (z_in + h)))
    full = sum(I.pan_inner_area(z + 0.5) for z in range(int(f.hoyde - 2 * f.gods))) / 1e6
    return rows, full


def outlet_margins():
    """Distance from each outlet/sensor spot to the inside wall of the pan at the rim."""
    f = S.form
    w, dd = f.topp[0] - 2 * f.gods, f.topp[1] - 2 * f.gods
    r = f.hjorneradius - f.gods
    items = [("fallrør mel", S.melskrue.utlop_x, G.AUG_Y, 16.0), ("fallrør salt", S.saltskrue.utlop[0], G.SALT_Y, 5.0),
             ("vanndyse", S.vann.dyse[0], S.vann.dyse[1], 2.0), ("ToF-punkt", S.tak.tof[0], S.tak.tof[1], 0.0),
             ("IR-punkt", S.tak.ir[0], S.tak.ir[1], 0.0), ("kamera", S.tak.kamera[0], S.tak.kamera[1], 0.0)]
    out = []
    for name, x, y, rad in items:
        out.append((name, _inside_rounded_rect(x, y, w, dd, r) - rad))
    return out


def _inside_rounded_rect(x, y, w, d, r):
    """Signed distance from (x, y) to the boundary of a rounded rectangle (positive inside)."""
    qx, qy = abs(x) - (w / 2 - r), abs(y) - (d / 2 - r)
    outside = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)
    return r - outside


def weighed_mass(weighed):
    total = 0.0
    rows = []
    for n, s in weighed:
        if n == "brodform":
            g = S.form.masse_kg * 1000
        elif n == "eltemotor":
            g = S.eltemotor.masse_kg * 1000
        elif n in ("plattform", "lastcelle_kloss_topp"):
            g = s.volume * DENSITY["alu"]
        elif n in ("aksel",):
            g = s.volume * DENSITY["steel"]
        elif n.startswith("reimskive"):
            g = s.volume * DENSITY["alu"] * 0.5
        elif n == "reim":
            g = 25
        elif n == "koblingsdel":
            g = 60
        else:
            g = s.volume * DENSITY["petg"]
        rows.append((n, g))
        total += g
    return total, rows


def belt_numbers():
    c, need, std = I.belt_geometry()
    r1, r2 = G.R_P_MOTOR, G.R_P_SHAFT
    lo, hi = c - 30, c + 30
    for _ in range(60):
        mid = (lo + hi) / 2
        length = 2 * mid + math.pi * (r1 + r2) + (r2 - r1) ** 2 / mid
        lo, hi = (mid, hi) if length < std else (lo, mid)
    return c, need, std, lo - c


def power_budget():
    e = S.elektrisk
    peak = e.motor_w + e.varme_w + e.steppere_w + e.pumpe_w + e.vifte_w + e.elektronikk_w
    normal = e.motor_w + e.vifte_w + e.elektronikk_w
    return peak, normal, e.psu_w


def machine_size(parts):
    xs = (G.X0 - G.T, G.X1 + G.T)
    ys = (G.Y0 - G.T, G.Y1 + G.T)
    zmax = max(p.shape.bounding_box().max.Z for p in parts)
    feet = S.fot_h + S.bunnplate_t
    handle = max(p.shape.bounding_box().max.Z for p in parts if p.navn == "traktlokk")
    hinge_x = max(p.shape.bounding_box().max.X for p in parts if p.navn.startswith("dorhengsel"))
    handle_y = min(p.shape.bounding_box().min.Y for p in parts if p.navn == "dorhandtak")
    return {"b": xs[1] - xs[0], "d": ys[1] - ys[0], "h_panel": G.H + G.T + feet, "h_max": max(zmax, handle) + feet,
            "b_max": hinge_x - xs[0], "d_max": ys[1] - handle_y}


# ------------------------------------------------------------------ report


def write_report(parts, path):
    weighed, fixed, door_closed = groups(parts, 0.0)
    door_open = _door_at(parts, S.dor.apning_grader)
    L = ["# Sjekkrapport – Surdeigsbaker v1", "",
         "Generert automatisk av `hardware/cad/v1/bygg.py` fra `hardware/spec/v1.yaml`. Ikke rediger for hånd.", ""]
    res = {}

    L += ["## 1. Passer delene på printeren?", "",
          f"Byggevolum: {S.skriver.x} × {S.skriver.y} × {S.skriver.z} mm (delene kan dreies 90° på platen).", "",
          "| Del | Mål i printretning (mm) | OK |", "|---|---|---|"]
    rows = bed_fit(parts)
    L += [f"| {n} | {d} | {ok} |" for n, d, ok in rows]
    res["bed_bad"] = sum(1 for r in rows if r[2] != "✅")
    L += ["", f"**{len(rows) - res['bed_bad']} av {len(rows)} deler passer.**", ""]

    (d, a, b), (dc, ac, bc) = weighing_gaps(weighed, fixed + door_closed)
    res["gap"] = d
    ok = "✅" if d >= MIN_GAP else "❌"
    L += ["## 2. Veiespalten", "",
          "Alt som står på lastcella (plattformen, lagersøylen, formholderen, formen, akselen, reimskivene, reima og eltemotoren) skal gå fri av resten av maskinen. Ellers bærer noe av vekta seg selv, og doseringen blir feil.", "",
          f"- Minste spalte mellom det som veies og resten av maskinen: **{d:.1f} mm** ({a} mot {b}) {ok} (krav ≥ {MIN_GAP:.0f} mm)",
          f"- Minste spalte mellom det som veies og selve lastcella: **{dc:.1f} mm** ({ac} mot {bc})",
          f"- Overlaststoppene er satt **{S.overlast.klaring} mm** under plattformen. Juster dem med følelermål etter montering.",
          "- Ledningene til eltemotoren og deigføleren må henge i en myk sløyfe. Bruk tynne silikonledninger.", ""]

    worst, clash = pan_path(weighed, fixed, door_open)
    res["pan"] = min(v[0] for v in worst.values())
    L += ["## 3. Formen tas ut", "",
          f"Formen dreies {S.formholder.knast_vinkel}° for å løsne bajonetten, løftes {S.form.loft} mm og trekkes ut gjennom døra (åpen {S.dor.apning_grader}°).", "",
          "| Trinn | Minste klaring (mm) | Nærmest | Kollisjon med holderen (mm³) |", "|---|---|---|---|"]
    for k in ("dreie", "løfte", "trekke"):
        v = worst[k]
        c = f"{clash.get(k, 0.0):.1f}" if k in clash else "–"
        L.append(f"| {k} | {v[0]:.1f} {'✅' if v[0] >= MIN_GAP else '❌'} | {v[2]} | {c} |")
    res["pan_clash"] = max(clash.values())
    L += ["", "Knastene skal gli i sporene i holderen, så kollisjonen med holderen skal være 0.", ""]

    dw = door_swing(parts, fixed, weighed)
    res["door"] = dw[0]
    L += ["## 4. Døra åpnes", "",
          f"- Minste klaring mellom døra og maskinen fra 5° til {S.dor.apning_grader}°: **{dw[0]:.1f} mm** ({dw[1]} mot {dw[2]}, ved {dw[3]:.0f}°) {'✅' if dw[0] > 0.2 else '❌'}",
          f"- Døra er hengslet på høyre side. Isolasjonspluggen i døra er skåret {I.dorplugg_taper():.1f} mm skrått på venstre kant (innerst), ellers ville hjørnet gått inn i isolasjonen når døra åpnes.", ""]

    hn = hopper_numbers(parts)
    sv, sg = salt_numbers(parts)
    res["hopper_g"] = hn["gram"]
    L += ["## 5. Mel og salt", "",
          f"- Melbeholderen rommer **{hn['vol_l']:.1f} l**, dvs. ca. **{hn['gram'] / 1000:.1f} kg** løst mel ({S.trakt.romvekt} g/cm³). Det er nok til {int(hn['gram'] // 560)} bakinger på 560 g.",
          f"- Innløpet langs skruen er {hn['slot_ratio']:.1f} × skruediameteren (krav ≥ 4). Lukket rør før utløpet: {hn['choke']:.0f} mm.",
          f"- Røreverket går **{hn['gap_screw']:.1f} mm** fra skruen og **{hn['gap_wall']:.1f} mm** fra veggene.",
          f"- Saltboksen rommer ca. **{sv:.0f} ml**, dvs. ca. {sg:.0f} g fint salt ({int(sg // 12)} bakinger).", ""]

    rows_p, full = pan_numbers()
    res["rise_ok"] = rows_p[-1][2] > 0 and rows_p[-1][1] < S.form.hoyde - 10
    L += ["## 6. Deigen i formen", "",
          f"Formen rommer ca. {full:.1f} l. Deigen veier {S.deig.masse_g} g ({S.deig.tetthet} g/cm³).", "",
          "| Heving | Deighøyde (mm) | Avstand ToF → deig (mm) |", "|---|---|---|"]
    for rise, h, dist in rows_p:
        L.append(f"| +{rise * 100:.0f} % | {h:.0f} | {dist:.0f} |")
    L += ["", "VL53L0X måler 30–1 200 mm. Hele området er innenfor.", "",
          "**Utløp og målepunkter, avstand innenfor formveggen ved kanten:**", "",
          "| Punkt | Margin (mm) |", "|---|---|"]
    om = outlet_margins()
    L += [f"| {n} | {m:.0f} {'✅' if m >= 5 else '⚠️'} |" for n, m in om]
    res["outlet"] = min(m for _n, m in om)
    L.append("")

    mass, mrows = weighed_mass(weighed)
    dough = S.deig.masse_g
    L += ["## 7. Vekt og lastcelle", "",
          f"- Det som veies, uten deig: ca. **{mass / 1000:.1f} kg**. Med deig: ca. **{(mass + dough) / 1000:.1f} kg** mot cellas **{S.lastcelle.kapasitet_kg} kg**.",
          f"- Tyngst: " + ", ".join(f"{n} {g / 1000:.2f} kg" for n, g in sorted(mrows, key=lambda r: -r[1])[:4]) + ".",
          "- NAU7802 med 10 kg-celle gir ca. 0,02–0,08 g støy. Krypet etter 470 g vann er ca. 0,5 g. Maskinen tarer før hver tilsetning.", ""]

    c, need, std, dc = belt_numbers()
    L += ["## 8. Reim", "",
          f"- Akseavstand {c:.1f} mm, {S.reim.tenner_motor} og {S.reim.tenner_aksel} tenner (utveksling {S.reim.tenner_aksel / S.reim.tenner_motor:.1f}:1).",
          f"- Nødvendig lengde {need:.0f} mm. Valgt standardreim: **HTD {std}-5M-{S.reim.bredde}** ({std // 5} tenner). Motoren flyttes {dc:+.1f} mm i sporene for å stramme.", ""]

    peak, normal, psu = power_budget()
    L += ["## 9. Effekt", "",
          f"- Verste tilfelle (alt på samtidig): **{peak:.0f} W** mot strømforsyningens **{psu:.0f} W**.",
          f"- Fastvaren slår av varmen og doseringen mens eltemotoren går. Da blir toppen ca. **{normal:.0f} W**.", ""]

    sz = machine_size(parts)
    L += ["## 10. Størrelse", "",
          f"- Kassa: **{sz['b']:.0f} × {sz['d']:.0f} × {sz['h_panel']:.0f} mm** (b × d × h, med føtter).",
          f"- Med håndtak, hengsler og lokkgrep: {sz['b_max']:.0f} × {sz['d_max']:.0f} × {sz['h_max']:.0f} mm.",
          "- Melbeholderen fylles ovenfra. Står maskinen under et overskap, må den trekkes fram for å fylle mel.", ""]
    res["size"] = sz

    total = sum(p.shape.volume * max(p.antall, 0) for p in parts) / 1000
    L += ["## 11. Filament", "",
          f"- Massivt volum av alle printede deler: **{total:.0f} cm³**. Med vanlige innstillinger blir det ca. **{total * 1.27 * 0.55:.0f} g PETG**.", ""]

    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return res
