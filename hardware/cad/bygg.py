"""Build everything for Surdeigsbaker v0.

    python hardware/cad/bygg.py            # all outputs
    python hardware/cad/bygg.py --rask     # skip the slow 3D renders

Outputs (hardware/v0/):
    stl/<del>.stl           printable parts, in print orientation
    step/<del>.step         same parts as STEP (for editing in FreeCAD etc.)
    step/montasje.step      full assembly
    dxf/<panel>.dxf         cutting files for sheet panels and the heater plate
    tegninger/              hook bending template (1:1 SVG), panel overview
    bilder/                 renders of the assembly and the printed parts
    printliste.md           generated print list
    sjekkrapport.md         generated design checks
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from build123d import Compound, ExportDXF, Pos, Unit, export_step, export_stl  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

import deler  # noqa: E402
import innkjop as I  # noqa: E402
import sjekk  # noqa: E402
from felles import OUT, S, hook_points, rotate_about_hinge  # noqa: E402

PRINTED = (0.96, 0.55, 0.16)
COLORS = {
    "profil": (0.78, 0.79, 0.82), "panel": (0.22, 0.24, 0.28), "gulv": (0.85, 0.86, 0.88),
    "foring": (0.9, 0.9, 0.9), "xps": (0.62, 0.78, 0.95), "bolle": (0.86, 0.88, 0.9),
    "varmeplate": (0.72, 0.74, 0.78), "varmeelement": (0.85, 0.35, 0.2), "kork": (0.65, 0.5, 0.35),
    "krok": (0.55, 0.58, 0.62), "motor": (0.12, 0.12, 0.13), "kobling": (0.75, 0.2, 0.2),
    "pcb": (0.12, 0.45, 0.25), "rod": (0.8, 0.1, 0.1), "svart": (0.1, 0.1, 0.1),
}

LID_PARTS = {"hengsel_lokk", "lagerhus", "motorplate", "motorklemme", "motordeksel", "kantpress_hus",
             "kantpress_stempel", "kantpress_tupp", "sensorhus", "hjemmeflagg", "sensorarm", "bryternese"}


# ------------------------------------------------------------------ exports


def to_bed(part):
    shape = part.print_rot * part.shape
    bb = shape.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * shape


def export_parts(parts):
    (OUT / "stl").mkdir(parents=True, exist_ok=True)
    (OUT / "step").mkdir(parents=True, exist_ok=True)
    for p in parts:
        shape = to_bed(p)
        export_stl(shape, str(OUT / "stl" / f"{p.navn}.stl"), tolerance=0.02, angular_tolerance=0.1)
        export_step(shape, str(OUT / "step" / f"{p.navn}.step"))


def export_dxf(panels):
    out = OUT / "dxf"
    out.mkdir(parents=True, exist_ok=True)
    items = [(p.navn, p.face()) for p in panels] + [("varmeplate_aluminium", I.varmeplate_face())]
    for name, face in items:
        exp = ExportDXF(unit=Unit.MM)
        exp.add_layer("kontur")
        exp.add_shape(face, layer="kontur")
        exp.write(str(out / f"{name}.dxf"))
    return items


# ------------------------------------------------------------------ assembly


def assembly(parts, theta=0.0, cutaway=False):
    """List of (shape, rgb, alpha, label) for rendering and STEP."""
    lid = I.lid_transform(theta)
    items = []

    def add(shape, rgb, label, alpha=1.0, on_lid=False):
        items.append(((lid * shape) if on_lid else shape, rgb, alpha, label))

    for name, _l, shp in I.profiler():
        if cutaway and name == "stolpe":
            bb = shp.bounding_box()
            if bb.min.Y < 0 and bb.min.X > 0:
                continue
        add(shp, COLORS["profil"], name)
    for name, _l, shp in I.lokkprofiler():
        add(shp, COLORS["profil"], name, on_lid=True)
    for pnl in I.paneler():
        if cutaway and pnl.navn in ("panel_front", "panel_side_hoyre"):
            continue
        rgb = COLORS["foring"] if pnl.navn == "panel_lokk_foring" else COLORS["gulv"] if pnl.navn == "panel_gulv" else COLORS["panel"]
        add(pnl.solid(), rgb, pnl.navn, on_lid=pnl.lokk)
    for i, (name, shp) in enumerate(I.isolasjon()):
        if cutaway and i in (0, 3):
            continue
        add(shp, COLORS["xps"], name)
    add(I.bolle(), COLORS["bolle"], "bolle")
    for name, shp in I.varmeplate_stack():
        add(shp, COLORS[name], name)
    add(I.krok(90.0), COLORS["krok"], "krok", on_lid=True)
    for name, shp in I.drivverk():
        add(shp, COLORS["kobling" if name == "kobling" else "motor"], name, on_lid=True)
    for name, shp in I.elektronikk():
        rgb = COLORS["rod"] if name == "e_stopp_knapp" else COLORS["svart"] if name in ("knapp", "dc_kontakt", "e_stopp_hus") else COLORS["pcb"]
        add(shp, rgb, name)
    for name, shp in I.lokk_utstyr():
        add(shp, COLORS["profil"], name, on_lid=True)
    for name, shp in I.ramme_utstyr():
        add(shp, COLORS["svart"], name)
    for p in parts:
        if p.antall == 0 or p.navn in ("kabelklemme",):
            continue
        on_lid = p.navn in LID_PARTS
        add(p.shape, PRINTED, p.navn, on_lid=on_lid)
        for tf in deler.kopier(p.navn):
            add(tf * p.shape, PRINTED, p.navn, on_lid=on_lid)
    return items


def export_assembly(items):
    children = []
    for shape, _rgb, _a, label in items:
        shape.label = label
        children.append(shape)
    export_step(Compound(children=children), str(OUT / "step" / "montasje.step"))


# ------------------------------------------------------------------ rendering


def _tris(shape, tol, max_edge=None):
    verts, tris = shape.tessellate(tol, 0.35)
    if not tris:
        return np.zeros((0, 3, 3))
    v = np.array([(p.X, p.Y, p.Z) for p in verts])
    t = v[np.array(tris)]
    return _subdivide(t, max_edge) if max_edge else t


def _subdivide(t, max_edge):
    """Split large triangles so matplotlib's painter's algorithm sorts better."""
    done = []
    for _ in range(8):
        e = np.max(np.linalg.norm(t - np.roll(t, 1, axis=1), axis=2), axis=1)
        big = e > max_edge
        done.append(t[~big])
        if not big.any():
            break
        b = t[big]
        a, bb, c = b[:, 0], b[:, 1], b[:, 2]
        ab, bc, ca = (a + bb) / 2, (bb + c) / 2, (c + a) / 2
        t = np.concatenate([np.stack(x, axis=1) for x in ((a, ab, ca), (ab, bb, bc), (ca, bc, c), (ab, bc, ca))])
    else:
        done.append(t)
    return np.concatenate(done)


def render(items, path, elev, azim, title, tol=0.8, limits=None, figsize=(10, 9)):
    light = np.array([0.35, -0.55, 0.75])
    light /= np.linalg.norm(light)
    polys, colors = [], []
    for shape, rgb, alpha, _label in items:
        t = _tris(shape, tol, max_edge=22)
        if len(t) == 0:
            continue
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.42 + 0.58 * np.abs(n @ light)
        c = np.clip(np.outer(shade, rgb), 0, 1)
        polys.append(t)
        colors.append(np.hstack([c, np.full((len(c), 1), alpha)]))
    polys = np.vstack(polys)
    colors = np.vstack(colors)
    fig = plt.figure(figsize=figsize, dpi=140)
    ax = fig.add_subplot(projection="3d")
    ax.add_collection3d(Poly3DCollection(polys, facecolors=colors, edgecolors="none"))
    if limits is None:
        mn, mx = polys.reshape(-1, 3).min(0), polys.reshape(-1, 3).max(0)
    else:
        mn, mx = np.array(limits[0]), np.array(limits[1])
    ax.set_xlim(mn[0], mx[0])
    ax.set_ylim(mn[1], mx[1])
    ax.set_zlim(mn[2], mx[2])
    ax.set_box_aspect(mx - mn)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def render_parts_overview(parts, path):
    shown = [p for p in parts if p.antall > 0]
    cols = 6
    rows = math.ceil(len(shown) / cols)
    fig = plt.figure(figsize=(cols * 3.0, rows * 3.0), dpi=110)
    light = np.array([0.35, -0.55, 0.75])
    light /= np.linalg.norm(light)
    for i, p in enumerate(shown):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        t = _tris(to_bed(p), 0.3)
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.4 + 0.6 * np.abs(n @ light)
        rgb = (0.55, 0.35, 0.75) if "TPU" in p.materiale else PRINTED
        ax.add_collection3d(Poly3DCollection(t, facecolors=np.clip(np.outer(shade, rgb), 0, 1), edgecolors="none"))
        mn, mx = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
        c, r = (mn + mx) / 2, (mx - mn).max() / 2
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(28, -55)
        ax.set_axis_off()
        ax.set_title(f"{p.navn} ×{p.antall}", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def render_section(path):
    """2D section (y–z plane through the centre) with the lid swing of the hook."""
    fig, ax = plt.subplots(figsize=(9, 9), dpi=140)
    half, inner, h = S.ramme.bredde / 2, S.ramme.bredde / 2 - 20, S.ramme.hoyde
    zb = S.varmeplate.topp_z
    b = S.bolle
    # frame outline and floor
    ax.add_patch(plt.Rectangle((-half, 0), 2 * half, h, fill=False, lw=1.5, ec="0.3"))
    for z0 in (0, S.ramme.midtramme_z, h - 20):
        for y0 in (-half, inner):
            ax.add_patch(plt.Rectangle((y0, z0), 20, 20, color="0.75"))
    ax.add_patch(plt.Rectangle((-half, S.ramme.midtramme_z + 20), 2 * half, 3, color="0.8"))
    t = S.isolasjon_t
    ax.add_patch(plt.Rectangle((-inner, 113), t, h - 20 - 113, color=COLORS["xps"], alpha=0.6))
    ax.add_patch(plt.Rectangle((inner - t, 113), t, h - 20 - 113, color=COLORS["xps"], alpha=0.6))
    # heater stack and bowl
    ax.add_patch(plt.Rectangle((-S.varmeplate.d / 2, zb - 3), S.varmeplate.d, 3, color=COLORS["varmeplate"]))
    ax.add_patch(plt.Rectangle((-S.varmeplate.element_d / 2, zb - 4), S.varmeplate.element_d, 1, color=COLORS["varmeelement"]))
    r0, r1 = b.bunn_d / 2, b.kant_d / 2
    ax.plot([-r1, -r0, r0, r1], [zb + b.hoyde, zb, zb, zb + b.hoyde], color="0.35", lw=2.5)
    # lid
    def lid_poly(theta, **kw):
        corners = [(-half, h), (half, h), (half, h + 23), (-half, h + 23)]
        pts = [rotate_about_hinge(y, z, theta) for y, z in corners]
        ax.add_patch(plt.Polygon(pts, closed=True, **kw))
    lid_poly(0, color="0.55", alpha=0.9)
    lid_poly(100, fill=False, ec="0.55", ls="--")
    m = S.motor
    ax.add_patch(plt.Rectangle((-m.kropp_d / 2, m.flate_z), m.kropp_d, m.lengde, color=COLORS["motor"], alpha=0.85))
    ax.add_patch(plt.Rectangle((-S.kobling.d / 2, S.kobling.bunn_z), S.kobling.d, S.kobling.lengde, color=COLORS["kobling"]))
    lh = S.lagerhus
    ax.add_patch(plt.Rectangle((-22, lh.topp_z - lh.hoyde), 44, lh.hoyde, color=PRINTED))
    # hook at three angles of the lid
    pts, _ = sjekk._hook_samples(90.0)
    for theta, style in ((0, "-"), (30, ":"), (60, ":"), (100, "--")):
        yz = np.array([rotate_about_hinge(p[1], p[2], theta) for p in pts])
        ax.plot(yz[:, 0], yz[:, 1], style, color="tab:blue", lw=3 if theta == 0 else 1.5,
                label="krok, lokk lukket" if theta == 0 else (f"krok ved {theta}°" if theta in (30, 100) else None))
    ax.plot([S.lokk.hengsel_akse_y], [S.lokk.hengsel_akse_z], "o", color="tab:red", label="hengselakse")
    ax.set_aspect("equal")
    ax.set_xlabel("y (mm)  ← front · bak →")
    ax.set_ylabel("z (mm)")
    ax.set_title("Snitt gjennom senter: bolle, krok og lokkets svingbane")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(-230, 470)
    ax.set_ylim(-20, 720)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def render_panels(items, path):
    cols = 3
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5), dpi=110)
    for ax, (name, face) in zip(axes.flat, items):
        for f in face.faces():
            for wire in [f.outer_wire()] + list(f.inner_wires()):
                pts = np.array([(v.X, v.Y) for v in wire.positions([i / 200 for i in range(201)])])
                ax.plot(pts[:, 0], pts[:, 1], color="black", lw=0.8)
        ax.set_aspect("equal")
        ax.set_title(name, fontsize=10)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.2)
    for ax in list(axes.flat)[len(items):]:
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ hook template


def hook_template(path):
    """1:1 SVG of the hook centre line for bending (print at 100 %)."""
    _pts, line = sjekk._hook_samples(0.0)
    k = S.krok
    xs = [p.X for p in line.positions([i / 400 for i in range(401)])]
    zs = [p.Z for p in line.positions([i / 400 for i in range(401)])]
    hp = hook_points()
    zmax, zmin = max(zs), min(zs)
    margin = 25
    w = max(max(xs) - min(xs) + 2 * margin + 60, 200)
    hgt = zmax - zmin + 2 * margin + 40
    def X(x):
        return x - min(xs) + margin + 10
    def Y(z):
        return zmax - z + margin + 20
    d_center = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.2f},{Y(z):.2f}" for i, (x, z) in enumerate(zip(xs, zs)))
    corners = " ".join(f"{X(r):.1f},{Y(z):.1f}" for r, z in hp)
    seg = []
    for (r0, z0), (r1, z1) in zip(hp, hp[1:]):
        seg.append(math.hypot(r1 - r0, z1 - z0))
    txt = [
        f'<text x="{margin}" y="10" font-size="6" font-family="sans-serif">Surdeigsbaker v0 – bøyemal for kroken (1:1)</text>',
        f'<text x="{margin}" y="17" font-size="4.5" font-family="sans-serif">Rundstang Ø{k.stang_d} mm AISI 304/316, bøyeradius {k.boyeradius} mm (innvendig ca. {k.boyeradius - k.stang_d / 2:.0f} mm).</text>',
        f'<text x="{margin}" y="{hgt - 11:.0f}" font-size="4.5" font-family="sans-serif">Utbrettet lengde ≈ {line.length:.0f} mm. Kapp {math.ceil(line.length / 10) * 10 + 30} mm og juster.</text>',
        f'<text x="{margin}" y="{hgt - 5:.0f}" font-size="4.5" font-family="sans-serif">Skriv ut i 100 % og sjekk 50 mm-streken.</text>',
        f'<line x1="{w - 70}" y1="{hgt - 20}" x2="{w - 20}" y2="{hgt - 20}" stroke="black" stroke-width="0.6"/>',
        f'<text x="{w - 70}" y="{hgt - 23}" font-size="4" font-family="sans-serif">50 mm</text>',
    ]
    for i, ((r0, z0), (r1, z1), L) in enumerate(zip(hp, hp[1:], seg)):
        mx, mz = (X(r0) + X(r1)) / 2, (Y(z0) + Y(z1)) / 2
        dz = 12 if abs(z1 - z0) < 1 else 0
        txt.append(f'<text x="{mx + 9:.1f}" y="{mz + dz:.1f}" font-size="4.5" fill="#1f5fa8" font-family="sans-serif">{chr(65 + i)}: {L:.0f} mm</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}mm" height="{hgt:.0f}mm" viewBox="0 0 {w:.0f} {hgt:.0f}">
<rect width="100%" height="100%" fill="white"/>
<path d="{d_center}" fill="none" stroke="#d9dde3" stroke-width="{k.stang_d}" stroke-linecap="round"/>
<path d="{d_center}" fill="none" stroke="black" stroke-width="0.5"/>
<polyline points="{corners}" fill="none" stroke="#1f5fa8" stroke-width="0.3" stroke-dasharray="2,1.5"/>
<line x1="{X(0):.1f}" y1="{Y(zmax) - 8:.1f}" x2="{X(0):.1f}" y2="{Y(zmin) + 8:.1f}" stroke="red" stroke-width="0.3" stroke-dasharray="4,2"/>
<text x="{X(0) + 2:.1f}" y="{Y(zmax) - 10:.1f}" font-size="4" fill="red" font-family="sans-serif">rotasjonsakse</text>
<text x="{X(0) + 2:.1f}" y="{Y(zmax) - 4:.1f}" font-size="3.5" fill="#1f5fa8" font-family="sans-serif">blå stiplet = mål hjørne til hjørne (før bøyeradius)</text>
{chr(10).join(txt)}
</svg>
'''
    path.write_text(svg, encoding="utf-8")
    return line.length


# ------------------------------------------------------------------ print list


def write_print_list(parts, path):
    rows = ["# Printliste – Surdeigsbaker v0", "",
            "Generert av `hardware/cad/bygg.py`. STL-filene ligger i [`stl/`](stl/) og er allerede snudd til anbefalt printretning.", "",
            "**Standardinnstillinger:** PETG, 0,2 mm lag, 4 perimetre, 30–40 % gyroid, 5 topp- og bunnlag. Bærende deler (lagerhus, motorplate, motorklemme og hengsler) skal ha **5 perimetre** og 40 % fyll. TPU-deler: 95A, 100 % fyll.", "",
            "Ingen printede deler er i kontakt med deigen. Bollen og kroken er av rustfritt stål.", "",
            "| Del | Antall | Materiale | Printretning | Volum (cm³) | Merknad |", "|---|---|---|---|---|---|"]
    for p in parts:
        rows.append(f"| [{p.navn}](stl/{p.navn}.stl) | {p.antall} | {p.materiale} | {p.orientering} | {p.shape.volume / 1000:.1f} | {p.merknad} |")
    rows += ["", "Delene med antall 0 er valgfrie."]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rask", action="store_true", help="hopp over 3D-bildene")
    args = ap.parse_args()
    t0 = time.time()
    for d in ("bilder", "tegninger"):
        (OUT / d).mkdir(parents=True, exist_ok=True)

    parts = deler.alle_deler()
    print(f"[{time.time() - t0:5.1f}s] {len(parts)} deler bygget")
    export_parts(parts)
    print(f"[{time.time() - t0:5.1f}s] STL/STEP eksportert")
    panels = I.paneler()
    items2d = export_dxf(panels)
    render_panels(items2d, OUT / "tegninger" / "plater_oversikt.png")
    print(f"[{time.time() - t0:5.1f}s] DXF eksportert")
    length = hook_template(OUT / "tegninger" / "krok_boyemal.svg")
    print(f"[{time.time() - t0:5.1f}s] bøyemal (krok {length:.0f} mm)")
    write_print_list(parts, OUT / "printliste.md")
    res = sjekk.write_report(parts, OUT / "sjekkrapport.md")
    print(f"[{time.time() - t0:5.1f}s] sjekkrapport: {res}")
    render_section(OUT / "bilder" / "v0_snitt.png")

    asm = assembly(parts, 0.0)
    export_assembly(asm)
    print(f"[{time.time() - t0:5.1f}s] montasje.step")
    if not args.rask:
        closed = [it for it in asm if not it[3].startswith("xps")]
        render(closed, OUT / "bilder" / "v0_lukket.png", 22, -58, "Surdeigsbaker v0 – lukket")
        print(f"[{time.time() - t0:5.1f}s] bilde lukket")
        render(assembly(parts, 75.0, cutaway=True), OUT / "bilder" / "v0_aapen_snitt.png", 24, -48,
               "Surdeigsbaker v0 – lokket åpent, front og høyre side fjernet")
        print(f"[{time.time() - t0:5.1f}s] bilde åpent")
        render_parts_overview(parts, OUT / "bilder" / "deler_oversikt.png")
        print(f"[{time.time() - t0:5.1f}s] deloversikt")


if __name__ == "__main__":
    main()
