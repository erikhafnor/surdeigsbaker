"""Build everything for Surdeigsbaker v1.

    python hardware/cad/v1/bygg.py            # all outputs
    python hardware/cad/v1/bygg.py --rask     # skip the slow 3D renders

Outputs (hardware/v1/):
    stl/<del>.stl           printable parts, in print orientation
    step/<del>.step         same parts as STEP (for editing in FreeCAD etc.)
    step/montasje.step      full assembly
    dxf/<plate>.dxf         cutting files for panels and aluminium plates
    tegninger/              plate overview
    bilder/                 renders and sections
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
from felles import OUT, G, S, box  # noqa: E402

PRINTED = (0.96, 0.55, 0.16)
FOOD = (0.93, 0.9, 0.78)
COLORS = {
    "profil": (0.78, 0.79, 0.82), "panel": (0.22, 0.24, 0.28), "alu": (0.84, 0.85, 0.87),
    "xps": (0.62, 0.78, 0.95), "form": (0.35, 0.36, 0.38), "stål": (0.6, 0.62, 0.66),
    "motor": (0.12, 0.12, 0.13), "reim": (0.15, 0.15, 0.15), "celle": (0.75, 0.75, 0.7),
    "pcb": (0.12, 0.45, 0.25), "rod": (0.8, 0.1, 0.1), "svart": (0.1, 0.1, 0.1),
    "varme": (0.85, 0.35, 0.2), "vann": (0.55, 0.75, 0.95),
}
ALU_PANELS = {"panel_bunn", "mellomgulv", "toppplate", "plattform"}


def _color(name):
    if name in ("brodform",):
        return COLORS["form"]
    if name in ("eltemotor", "melmotor", "saltmotor", "servo_mel", "servo_salt", "vifte", "vannpumpe", "dreieknapp"):
        return COLORS["motor"]
    if name in ("reim",):
        return COLORS["reim"]
    if name.startswith("lastcelle") or name == "overlaststopp":
        return COLORS["celle"]
    if name in ("aksel", "melaksel", "roreaksel", "rorepinner", "dyserør", "koblingsdel", "kobling_mel") or name.startswith("reimskive"):
        return COLORS["stål"]
    if name in ("varmematte",):
        return COLORS["varme"]
    if name in ("kjoleribbe",):
        return COLORS["alu"]
    if name in ("bærekort", "pi_zero", "oled"):
        return COLORS["pcb"]
    if name in ("e_stopp",):
        return COLORS["rod"]
    if name in ("vanntank",):
        return COLORS["vann"]
    return COLORS["svart"]


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
    items = [(p.navn, p.face()) for p in panels]
    for name, face in items:
        exp = ExportDXF(unit=Unit.MM)
        exp.add_layer("kontur")
        exp.add_shape(face, layer="kontur")
        exp.write(str(out / f"{name}.dxf"))
    return items


# ------------------------------------------------------------------ assembly


def assembly(parts, door_theta=0.0, hide=(), pan=True):
    """List of (shape, rgb, alpha, label) for rendering and STEP."""
    items = []
    door_tf = I.door_transform(door_theta)

    def add(shape, rgb, label, alpha=1.0, on_door=False):
        if label in hide:
            return
        items.append(((door_tf * shape) if on_door else shape, rgb, alpha, label))

    for name, _l, shp in I.profiler():
        add(shp, COLORS["profil"], name)
    for pnl in I.paneler():
        rgb = COLORS["alu"] if pnl.navn in ALU_PANELS else (0.93, 0.93, 0.93) if pnl.navn == "takforing" else COLORS["panel"]
        add(pnl.solid(), rgb, pnl.navn, on_door=pnl.dor)
    for name, shp in I.isolasjon():
        add(shp, COLORS["xps"], name, alpha=1.0)
    add(I.dorplugg(), COLORS["xps"], "dorplugg", on_door=True)
    if pan:
        add(I.brodform(), COLORS["form"], "brodform")
    add(I.koblingsdel(), COLORS["stål"], "koblingsdel")
    groups = (I.drivverk() + I.lastcelle_fast() + I.melmotor() + I.saltmotor() + I.aksler_dosering() + I.servoer()
              + I.vannsystem() + I.varmeenhet() + I.vifte() + I.elektronikk() + I.dorbeslag())
    for name, shp in groups:
        add(shp, _color(name), name)
    for p in parts:
        rgb = FOOD if "matkontakt" in p.materiale else PRINTED
        on_door = p.gruppe == "dor"
        add(p.shape, rgb, p.navn, on_door=on_door)
        for tf in deler.kopier(p.navn):
            add(tf * p.shape, rgb, p.navn, on_door=on_door)
    return items


def export_assembly(items):
    children = []
    for shape, _rgb, _a, label in items:
        shape.label = label
        children.append(shape)
    export_step(Compound(children=children), str(OUT / "step" / "montasje.step"))


def cut(items, keep):
    """Intersect every item with the half-space box `keep` (for sections)."""
    out = []
    for shape, rgb, alpha, label in items:
        bb = shape.bounding_box()
        kb = keep.bounding_box()
        if bb.max.X < kb.min.X or bb.min.X > kb.max.X or bb.max.Y < kb.min.Y or bb.min.Y > kb.max.Y:
            continue
        inside = bb.min.X >= kb.min.X and bb.max.X <= kb.max.X and bb.min.Y >= kb.min.Y and bb.max.Y <= kb.max.Y
        try:
            s = shape if inside else shape & keep
            if s is None or not s.solids():
                continue
        except Exception:  # noqa: BLE001 - keep the render going
            continue
        out.append((s, rgb, alpha, label))
    return out


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


def render(items, path, elev, azim, title, tol=0.8, figsize=(10, 9), ortho=False, max_edge=22):
    light = np.array([0.35, -0.55, 0.75])
    light /= np.linalg.norm(light)
    polys, colors = [], []
    for shape, rgb, alpha, label in items:
        try:
            t = _tris(shape, tol, max_edge=max_edge)
        except AttributeError:
            print(f"  (hopper over {label}: kunne ikke trianguleres)")
            continue
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
    if ortho:
        ax.set_proj_type("ortho")
    ax.add_collection3d(Poly3DCollection(polys, facecolors=colors, edgecolors="none"))
    mn, mx = polys.reshape(-1, 3).min(0), polys.reshape(-1, 3).max(0)
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
    cols = 6
    rows = math.ceil(len(parts) / cols)
    fig = plt.figure(figsize=(cols * 3.0, rows * 3.0), dpi=110)
    light = np.array([0.35, -0.55, 0.75])
    light /= np.linalg.norm(light)
    for i, p in enumerate(parts):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        t = _tris(to_bed(p), 0.3)
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.4 + 0.6 * np.abs(n @ light)
        rgb = FOOD if "matkontakt" in p.materiale else PRINTED
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


def render_panels(items, path):
    cols = 4
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4.5), dpi=110)
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


def render_weighing_diagram(path):
    """2D section (x–z at y = 0) of the weighing stack with the gaps annotated."""
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=140)

    def rect(x0, x1, z0, z1, color, label=None, alpha=1.0, **kw):
        ax.add_patch(plt.Rectangle((x0, z0), x1 - x0, z1 - z0, color=color, alpha=alpha, label=label, **kw))

    pf = S.plattform
    rect(G.X0, G.X1, -S.bunnplate_t, 0, "0.65", "bunnplate (fast)")
    rect(G.X0, G.X1, G.Z_MG, G.Z_MG1, "0.65")
    rect(G.CX0, G.CX1, G.Z_MG1, G.Z_FLOOR, COLORS["xps"], "isolasjon (fast)", alpha=0.7)
    rect(pf.x[0], pf.x[1], G.Z_PL0, G.Z_PL1, "tab:orange", "veies")
    lc = S.lastcelle
    rect(lc.x_fast, lc.x_fast + 30, 0, lc.avstand_t, "0.4")
    rect(lc.x_fast, lc.x_fast + lc.l, lc.avstand_t, lc.avstand_t + lc.h, "0.8", "lastcelle")
    rect(lc.x_fast + lc.l - 30, lc.x_fast + lc.l, G.Z_PL0 - lc.avstand_t, G.Z_PL0, "tab:orange")
    rect(-S.lagersoyle.flens_r, S.lagersoyle.flens_r, G.Z_PL1, G.Z_PL1 + S.lagersoyle.flens_t, "tab:orange")
    rect(-G.R_COL, G.R_COL, G.Z_PL1, G.Z_COL_TOP, "tab:orange")
    for s in (-1, 1):
        rect(s * G.R_KRAGE_IN, s * G.R_KRAGE_OUT, G.Z_MG1, G.Z_KRAGE_TOP, "0.45", "krage (fast)" if s > 0 else None)
        rect(s * G.R_KRAGE_OUT, s * (G.R_KRAGE_OUT + 10), G.Z_FLOOR, G.Z_FLOOR + G.KRAGE_FLENS_T, "0.45")
        rect(s * G.R_GROOVE_OUT, s * G.R_CUP_OUT, G.Z_SKIRT, G.Z_CUP_FLOOR, "tab:orange")
        rect(s * G.R_CUP_IN, s * G.R_CUP_OUT, G.Z_CUP_FLOOR, G.Z_CUP_TOP, "tab:orange")
    rect(-G.R_HUB, G.R_HUB, G.Z_SKIRT, G.Z_CUP_FLOOR, "tab:orange")
    rect(-G.R_CUP_OUT, G.R_CUP_OUT, G.Z_GROOVE_TOP, G.Z_CUP_FLOOR, "tab:orange")
    f = S.form
    rect(-f.bunn[0] / 2, f.bunn[0] / 2, G.Z_PAN, G.Z_PAN + 6, COLORS["form"], "brødform (veies)")
    rect(-f.fot_d / 2, f.fot_d / 2, G.Z_CUP_FLOOR, G.Z_PAN, COLORS["form"], alpha=0.6)
    m = S.eltemotor
    mx = -math.hypot(*m.pos)
    rect(mx - m.d / 2, mx + m.d / 2, G.Z_PL1, G.Z_PL1 + 100, COLORS["motor"], "eltemotor (veies, vist i reimplanet)", alpha=0.8)
    rect(mx - G.R_P_MOTOR - 3, mx + G.R_P_MOTOR + 3, G.Z_PULLEY0, G.Z_PULLEY1, "0.3")
    rect(-G.R_P_SHAFT - 3, G.R_P_SHAFT + 3, G.Z_PULLEY0, G.Z_PULLEY1, "0.3", "reimskiver")
    for x, z, txt in ((G.R_KRAGE_OUT + 2, G.Z_KRAGE_TOP + 1, f"{G.GAP:.0f} mm"),
                      (G.R_KRAGE_OUT + 12, G.Z_FLOOR + 2.5, f"{G.Z_SKIRT - G.Z_FLOOR - G.KRAGE_FLENS_T:.0f} mm"),
                      (60, G.Z_PL1 + 1, f"{G.Z_MG - G.Z_PL1:.0f} mm"),
                      (G.R_HUB + 0.5, G.Z_KRAGE_TOP - 15, f"{G.R_KRAGE_IN - G.R_HUB:.0f} mm")):
        ax.annotate(txt, (x, z), xytext=(x + 40, z + 25), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.set_aspect("equal")
    ax.set_xlim(-320, 140)
    ax.set_ylim(-10, 300)
    ax.set_xlabel("x (mm)  ← tårnet · kammeret →")
    ax.set_ylabel("z (mm)")
    ax.set_title("Veiespalten: oransje veies (står på lastcella), grått og blått er fast")
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ print list


def write_print_list(parts, path):
    rows = ["# Printliste – Surdeigsbaker v1", "",
            "Generert av `hardware/cad/v1/bygg.py`. STL-filene ligger i [`stl/`](stl/) og er allerede snudd til anbefalt printretning.", "",
            "**Standard:** PETG, 0,2 mm lag, 4 perimetre, 30–40 % gyroid, 5 topp- og bunnlag. Delene som bærer formen og drivverket (formholder, lagersøyle, hengsler og motorfeste) får **6 perimetre** og 50 % fyll.", "",
            "**Deler som berører mel eller salt** (merket «matkontakt»): naturfarget PETG med samsvarserklæring etter EU 10/2011, printet med dyse av rustfritt stål. Ingen printede deler berører deigen. Brødformen og eltebladet er kjøpt.", "",
            "| Del | Antall | Materiale | Printretning | Volum (cm³) | Merknad |", "|---|---|---|---|---|---|"]
    for p in parts:
        rows.append(f"| [{p.navn}](stl/{p.navn}.stl) | {p.antall} | {p.materiale} | {p.orientering} | {p.shape.volume / 1000:.1f} | {p.merknad} |")
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
    write_print_list(parts, OUT / "printliste.md")
    res = sjekk.write_report(parts, OUT / "sjekkrapport.md")
    print(f"[{time.time() - t0:5.1f}s] sjekkrapport: {res}")
    render_weighing_diagram(OUT / "bilder" / "v1_veiespalte.png")

    asm = assembly(parts, 0.0)
    export_assembly(asm)
    print(f"[{time.time() - t0:5.1f}s] montasje.step")
    if not args.rask:
        closed = [it for it in asm if not it[3].startswith("xps") and it[3] != "dorplugg"]
        render(closed, OUT / "bilder" / "v1_lukket.png", 20, -58, "Surdeigsbaker v1 – lukket")
        print(f"[{time.time() - t0:5.1f}s] bilde lukket")
        hide = {"panel_front_taarn", "panel_front_topp", "panel_front_sokkel", "panel_venstre", "panel_topp", "traktlokk",
                "saltlokk", "xps_hoyre"}
        render(assembly(parts, S.dor.apning_grader, hide=hide), OUT / "bilder" / "v1_aapen.png", 18, -62,
               "Surdeigsbaker v1 – døra åpen, front, venstre side og topp fjernet")
        print(f"[{time.time() - t0:5.1f}s] bilde åpen")
        keep = box(-2000, 2000, 0, 2000, -2000, 2000)
        sec = cut(assembly(parts, 0.0, hide={"panel_dor", "dorplugg", "dorhandtak", "bryternese", "dorhengsel_dor"}), keep)
        render(sec, OUT / "bilder" / "v1_snitt_front.png", 0, -90, "Snitt gjennom eltebladets aksel, sett forfra",
               ortho=True, figsize=(11, 11))
        print(f"[{time.time() - t0:5.1f}s] snitt forfra")
        keep = box(-2000, 0, -2000, 2000, -2000, 2000)
        sec = cut(assembly(parts, 0.0), keep)
        render(sec, OUT / "bilder" / "v1_snitt_side.png", 0, 0, "Snitt gjennom eltebladets aksel, sett fra høyre",
               ortho=True, figsize=(9, 11))
        print(f"[{time.time() - t0:5.1f}s] snitt fra siden")
        render_parts_overview(parts, OUT / "bilder" / "deler_oversikt.png")
        print(f"[{time.time() - t0:5.1f}s] deloversikt")


if __name__ == "__main__":
    main()
