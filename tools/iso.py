"""Mini motore per illustrazioni isometriche in SVG.

Convenzioni: x va verso destra-basso, y verso sinistra-basso, z verso l'alto.
Le pareti di fondo di una stanza sono il piano x=0 (a sinistra) e il piano y=0 (a destra).
Le scene si disegnano dal fondo verso chi guarda (algoritmo del pittore).
"""
import math

C, S = math.cos(math.radians(30)), math.sin(math.radians(30))

# Palette condivisa da tutte le scene
PAL = {
    "wall_l": "#f1e7d9", "wall_r": "#e9dccb", "wall_top": "#d9cbb8", "wall_edge": "#cdbba4",
    "floor": "#c98d5e", "floor_line": "#b67b4f", "slab_l": "#8a5432", "slab_r": "#a5663e",
    "white": "#ffffff", "white_l": "#f4f7f6", "white_r": "#dfe7e5",
    "ink": "#123033", "teal": "#0f6b62", "teal_light": "#7cc7b9", "screen": "#7fe0cf",
    "orange": "#e8611a", "orange_d": "#b9480f", "orange_m": "#cf5615", "flame": "#ff8a3d",
    "copper": "#c27a4a", "copper_l": "#ffd9b8", "green": "#2f7d55", "terracotta": "#c56a3f",
    "steel": "#9fb0b3", "steel_d": "#7d8f93", "dark": "#24333a", "dark_l": "#2b3a40", "dark_r": "#1d2a2f",
}


class Scene:
    def __init__(self, unit=34, label=""):
        self.U = unit
        self.label = label
        self.out = []
        self.defs = []
        self.xs, self.ys = [], []

    # proiezione
    def P(self, x, y, z):
        px, py = (x - y) * C * self.U, (x + y) * S * self.U - z * self.U
        self.xs.append(px); self.ys.append(py)
        return px, py

    def add(self, s):
        self.out.append(s)

    # primitive
    def poly(self, pts, fill, extra=""):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.P(*p) for p in pts))
        self.add(f'<polygon points="{d}" fill="{fill}" {extra}/>')

    def box(self, x, y, z, dx, dy, dz, top, left, right, extra=""):
        """Facce visibili: superiore, frontale-sinistra (y+dy), frontale-destra (x+dx)."""
        self.poly([(x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)], top, extra)
        self.poly([(x, y + dy, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)], left, extra)
        self.poly([(x + dx, y, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x + dx, y, z + dz)], right, extra)

    def cbox(self, x, y, z, dx, dy, dz, color, extra=""):
        """Box con ombreggiatura automatica a partire da un solo colore."""
        self.box(x, y, z, dx, dy, dz, shade(color, 1.12), color, shade(color, .82), extra)

    def line(self, a, b, stroke, w=2, extra=""):
        (x1, y1), (x2, y2) = self.P(*a), self.P(*b)
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                 f'stroke-width="{w}" stroke-linecap="round" {extra}/>')

    def path3(self, pts, stroke, w=2, extra=""):
        d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in (self.P(*p) for p in pts))
        self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" '
                 f'stroke-linejoin="round" {extra}/>')

    def face(self, plane, origin, w, h, content, extra=""):
        """Disegna contenuto 2D (unità = pixel di U) su una faccia.

        plane 'y': parete destra/fronte di oggetti sulla parete destra; origine = angolo in alto a sinistra.
        plane 'x': parete sinistra/fronte di oggetti sulla parete sinistra; origine = angolo in alto a sinistra (y massima).
        plane 'z': pavimento o piano superiore; u lungo x, v lungo y.
        """
        x, y, z = origin
        ox, oy = self.P(x, y, z)
        if plane == "y":
            m = (C, S, 0, 1); self.P(x + w / self.U, y, z - h / self.U)
        elif plane == "x":
            m = (C, -S, 0, 1); self.P(x, y - w / self.U, z - h / self.U)
        else:
            m = (C, S, -C, S); self.P(x + w / self.U, y + h / self.U, z)
        self.add(f'<g transform="matrix({m[0]:.4f} {m[1]:.4f} {m[2]:.4f} {m[3]:.4f} {ox:.1f} {oy:.1f})" {extra}>'
                 f'{content}</g>')

    def shadow(self, x, y, rx, ry, opacity=.12):
        cx, cy = self.P(x, y, 0)
        self.add(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx}" ry="{ry}" fill="#3a2414" opacity="{opacity}"/>')

    def svg(self, pad=16):
        x0, x1, y0, y1 = min(self.xs) - pad, max(self.xs) + pad, min(self.ys) - pad, max(self.ys) + pad
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg class="iso-illu" xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} '
                f'{x1 - x0:.0f} {y1 - y0:.0f}" role="img" aria-label="{self.label}">{defs}'
                + "".join(self.out) + "</svg>\n")

    # elementi ricorrenti
    def room(self, W, D, H, T=.45, floor="wood"):
        p = PAL
        self.box(-T, -T, -.5, W + T, D + T, .5, p["floor"] if floor == "wood" else "#d8d2c8",
                 p["slab_l"], p["slab_r"])
        if floor == "wood":
            for k in range(1, int(W)):
                self.line((k, 0, .001), (k, D, .001), p["floor_line"], 1.4)
        else:
            for k in range(1, int(W)):
                self.line((k, 0, .001), (k, D, .001), "#c4bdb1", 1.2)
            for k in range(1, int(D)):
                self.line((0, k, .001), (W, k, .001), "#c4bdb1", 1.2)
        self.box(-T, 0, 0, T, D, H, p["wall_top"], p["wall_edge"], p["wall_l"])
        self.box(-T, -T, 0, W + T, T, H, p["wall_top"], p["wall_r"], p["wall_edge"])
        self.poly([(0, .02, 0), (W, .02, 0), (W, .02, .25), (0, .02, .25)], "#d8c7b0")
        self.poly([(.02, 0, 0), (.02, D, 0), (.02, D, .25), (.02, 0, .25)], "#e6d8c4")

    def boiler(self, x0, z0, w=1.8, h=2.6, d=.8, display="55°", old=False, open_front=False, glow=True,
               display_color=None, y0=0):
        """Caldaia murale sulla parete destra (y=0), o appoggiata altrove con y0."""
        p = PAL
        if glow:
            gid = f"g{len(self.defs)}"
            self.defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="#ffb070" stop-opacity=".55"/>'
                             f'<stop offset="1" stop-color="#ffb070" stop-opacity="0"/></radialGradient>')
            gx, gy = self.P(x0 + w / 2, y0 + .3, z0 + h / 2)
            self.add(f'<circle class="iso-glow" cx="{gx:.0f}" cy="{gy:.0f}" r="{self.U * 2.9:.0f}" fill="url(#{gid})"/>')
        body = ("#efe6cf", "#e6dbbf", "#cbbf9f") if old else (p["white_l"], p["white"], p["white_r"])
        self.box(x0, y0, z0, w, d, h, *body)
        U = self.U
        fw, fh = w * U, h * U
        if open_front:
            inner = (f'<rect x="{fw*.08:.0f}" y="{fh*.06:.0f}" width="{fw*.84:.0f}" height="{fh*.88:.0f}" rx="6" fill="#2a3b40"/>'
                     f'<rect x="{fw*.2:.0f}" y="{fh*.12:.0f}" width="{fw*.6:.0f}" height="{fh*.3:.0f}" rx="5" fill="#8d9a9c"/>'
                     + "".join(f'<line x1="{fw*.24:.0f}" y1="{fh*(.16+k*.05):.0f}" x2="{fw*.76:.0f}" y2="{fh*(.16+k*.05):.0f}" stroke="#c27a4a" stroke-width="3"/>' for k in range(5))
                     + f'<rect x="{fw*.3:.0f}" y="{fh*.48:.0f}" width="{fw*.4:.0f}" height="{fh*.12:.0f}" rx="4" fill="#3d5157"/>'
                     f'<path class="iso-flame" d="M{fw*.5:.0f} {fh*.49:.0f} c4 6 -4 7 -4 12 a4 4 0 0 0 8 0 c0 -3 -2 -5 -2 -7z" fill="{p["flame"]}"/>'
                     f'<rect x="{fw*.18:.0f}" y="{fh*.68:.0f}" width="{fw*.64:.0f}" height="{fh*.16:.0f}" rx="4" fill="#2f8f5b"/>'
                     + "".join(f'<rect x="{fw*(.24+k*.12):.0f}" y="{fh*.72:.0f}" width="{fw*.07:.0f}" height="{fh*.07:.0f}" fill="#1c3b2c"/>' for k in range(4)))
        else:
            dc = display_color or p["screen"]
            col = "#d9cfb3" if old else "#e6eceb"
            inner = (f'<rect x="0" y="0" width="{fw:.0f}" height="{fh*.13:.0f}" fill="{col}" opacity=".6"/>'
                     f'<circle cx="{fw/2:.0f}" cy="{fh*.4:.0f}" r="{fw*.22:.0f}" fill="{p["ink"] if not old else "#6d6551"}"/>'
                     f'<circle cx="{fw/2:.0f}" cy="{fh*.4:.0f}" r="{fw*.22:.0f}" fill="none" stroke="{col}" stroke-width="4"/>'
                     + ("" if old else
                        f'<path class="iso-flame" d="M{fw/2:.0f} {fh*.4-14:.0f} c6 8 -6 10 -6 18 a6 6 0 0 0 12 0 c0 -5 -3 -7 -3 -10 '
                        f'c-1 3 -3 4 -3 4 c0 -4 4 -7 0 -12z" fill="{p["flame"]}"/>')
                     + f'<rect x="{fw*.14:.0f}" y="{fh*.68:.0f}" width="{fw*.72:.0f}" height="{fh*.16:.0f}" rx="5" '
                       f'fill="{p["ink"] if not old else "#6d6551"}"/>'
                     f'<text x="{fw*.22:.0f}" y="{fh*.8:.0f}" font-family="system-ui,sans-serif" font-weight="800" '
                     f'font-size="{fh*.1:.0f}" fill="{dc}">{display}</text>'
                     + ("" if old else f'<circle cx="{fw*.75:.0f}" cy="{fh*.76:.0f}" r="{fh*.03:.0f}" fill="{p["orange"]}"/>'))
        self.face("y", (x0, y0 + d, z0 + h), fw, fh, inner)
        return x0, z0, w, h, d

    def pipes_down(self, x0, w, z0, to_z=.25, n=4, d=.45):
        for k in range(n):
            x = x0 + w * (k + 1) / (n + 1)
            self.line((x, d, z0), (x, d, to_z if k < 2 else z0 - .8), PAL["copper"], 5)

    def waves(self, x, y, z, n=3, gap=.8, plane="x"):
        for k in range(n):
            px, py = self.P(x, y - k * gap, z) if plane == "x" else self.P(x + k * gap, y, z)
            self.add(f'<path class="iso-wave" style="animation-delay:{k * .7:.1f}s" d="M{px:.1f} {py:.1f} '
                     f'c-6 -8 6 -14 0 -22 s6 -14 0 -22" fill="none" stroke="#f08a4b" stroke-width="3" '
                     f'stroke-linecap="round" opacity=".8"/>')

    def plant(self, x, y, s=1.0):
        self.box(x, y, 0, .8 * s, .8 * s, .9 * s, "#d07a4f", PAL["terracotta"], "#a5532f")
        lx, ly = self.P(x + .4 * s, y + .4 * s, .9 * s)
        for dx, dy, r in ((0, -26, 18), (-14, -40, 15), (14, -42, 16), (0, -56, 13)):
            self.add(f'<circle cx="{lx + dx * s:.0f}" cy="{ly + dy * s:.0f}" r="{r * s:.0f}" fill="{PAL["green"]}"/>')
        self.add(f'<circle cx="{lx - 6 * s:.0f}" cy="{ly - 44 * s:.0f}" r="{5 * s:.0f}" fill="#4a9a6d"/>')

    def toolbox(self, x, y, s=1.0, label=True, open_=False):
        p = PAL
        self.box(x, y, 0, 1.2 * s, 1.0 * s, .7 * s, p["dark_l"], p["dark"], p["dark_r"])
        if open_:
            self.box(x, y + .05, .7 * s, 1.2 * s, .9 * s, .05, "#3c4c52", "#3c4c52", "#3c4c52")
            for k, c in enumerate(("#c9d3d4", p["orange"], "#c9d3d4")):
                self.box(x + .2 + k * .3, y + .3, .72 * s, .12, .5, .25, c, shade(c, .85), shade(c, .7))
            self.poly([(x, y, .7 * s), (x + 1.2 * s, y, .7 * s), (x + 1.2 * s, y - .1, 1.5 * s), (x, y - .1, 1.5 * s)], p["orange_m"])
        else:
            self.box(x, y, .7 * s, 1.2 * s, 1.0 * s, .18 * s, p["orange"], p["orange_d"], p["orange_m"])
            self.box(x + .4 * s, y + .45 * s, .88 * s, .4 * s, .1, .14, p["dark"], p["dark"], p["dark_r"])
        if label:
            self.face("y", (x + .25 * s, y + 1.0 * s, .5 * s), 40 * s, 14 * s,
                      f'<text x="0" y="11" font-family="system-ui,sans-serif" font-weight="800" font-size="{11*s:.0f}" fill="#ffffff">CFM</text>')


def shade(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, round(c * f))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"
