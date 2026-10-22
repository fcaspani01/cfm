#!/usr/bin/env python3
"""Genera il set di illustrazioni isometriche in src/illustrations/scene-*.svg.

Uso:  python3 tools/illustrazioni.py
"""
from pathlib import Path
from iso import Scene, PAL, shade

OUT = Path(__file__).resolve().parent.parent / "src" / "illustrations"
p = PAL
FONT = 'font-family="system-ui,sans-serif" font-weight="800"'


def window(s, wy0, wy1, wz0, wz1):
    """Finestra sulla parete sinistra con il tramonto su Verona."""
    U = s.U
    w, h = (wy1 - wy0) * U, (wz1 - wz0) * U
    gid = f"sky{len(s.defs)}"
    s.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26415c"/>'
                  f'<stop offset=".55" stop-color="#e98a5a"/><stop offset="1" stop-color="#f6c48b"/></linearGradient>')
    arches = "".join(f'<path d="M{w*.12 + k*w*.055:.1f} {h*.86:.1f} v-{h*.05:.1f} a{w*.018:.1f} {w*.018:.1f} 0 0 1 {w*.036:.1f} 0 v{h*.05:.1f}z" fill="#f2b07c" opacity=".55"/>' for k in range(8))
    sky = (f'<rect x="-8" y="-8" width="{w+16:.0f}" height="{h+16:.0f}" fill="#ffffff"/>'
           f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="url(#{gid})"/>'
           f'<circle cx="{w*.72:.0f}" cy="{h*.62:.0f}" r="{w*.07:.0f}" fill="#ffe3b0" opacity=".9"/>'
           f'<path d="M0 {h*.92:.0f} V{h*.78:.0f} Q{w*.32:.0f} {h*.68:.0f} {w*.6:.0f} {h*.78:.0f} V{h*.6:.0f} h{w*.07:.0f} '
           f'V{h*.42:.0f} h{w*.04:.0f} V{h*.6:.0f} h{w*.05:.0f} V{h*.74:.0f} L{w:.0f} {h*.72:.0f} V{h:.0f} H0z" fill="#2b2733" opacity=".9"/>'
           + arches +
           f'<rect x="{w/2-3:.0f}" y="0" width="6" height="{h:.0f}" fill="#ffffff"/>')
    s.face("x", (.02, wy1, wz1), w, h, sky)
    s.box(0, wy0 - .2, wz0 - .3, .45, wy1 - wy0 + .4, .12, "#ffffff", "#e9e2d8", "#f4efe8")


def radiator(s, ry0, ry1, rz0, rz1):
    s.box(0, ry0, rz0, .35, ry1 - ry0, rz1 - rz0, "#ffffff", "#e7ecec", "#f7f9f9")
    U = s.U
    w, h = (ry1 - ry0) * U, (rz1 - rz0) * U
    fins = "".join(f'<line x1="{w*k/12:.1f}" y1="5" x2="{w*k/12:.1f}" y2="{h-5:.1f}" stroke="#cdd6d5" stroke-width="2"/>' for k in range(1, 12))
    s.face("x", (.351, ry1, rz1), w, h, fins)


def thermostat(s, x, z):
    s.box(x, 0, z, .7, .12, .8, "#ffffff", "#ffffff", "#e3e9e8")
    s.face("y", (x, .121, z + .8), .7 * s.U, .8 * s.U,
           f'<circle cx="{.35*s.U:.0f}" cy="{.42*s.U:.0f}" r="7" fill="none" stroke="#c9d3d4" stroke-width="2"/>'
           f'<circle cx="{.35*s.U:.0f}" cy="{.42*s.U:.0f}" r="3.5" fill="{p["orange"]}"/>')


def scene_casa():
    s = Scene(label="Illustrazione: soggiorno riscaldato da una caldaia murale, con termosifone e finestra su Verona")
    W, D, H = 10, 8, 6.2
    s.shadow(W / 2, D / 2 + 1, 330, 70, .10)
    s.room(W, D, H)
    window(s, 1.2, 3.6, 2.4, 5.0)
    # tubi lungo il battiscopa: mandata e ritorno verso il termosifone
    bx0, bz0, bw = 6.3, 2.6, 1.8
    ry0, ry1, rz0, rz1 = 4.3, 7.2, .7, 2.3
    cu = p["copper"]
    s.path3([(bx0 + bw * .2, .45, bz0), (bx0 + bw * .2, .45, .25), (.45, .45, .25), (.45, ry0 + .35, .25), (.2, ry0 + .35, rz0 + .05)], cu, 5)
    s.path3([(bx0 + bw * .4, .45, bz0), (bx0 + bw * .4, .45, .45), (.7, .45, .45), (.7, ry1 - .35, .45), (.2, ry1 - .35, rz0 + .05)], cu, 5)
    s.path3([(bx0 + bw * .4, .45, .45), (.7, .45, .45), (.7, ry1 - .35, .45)], p["copper_l"], 2, 'class="iso-flow" stroke-dasharray="3 12"')
    radiator(s, ry0, ry1, rz0, rz1)
    s.waves(.6, ry1 - .6, rz1 + .3, 3, .9)
    thermostat(s, 3.2, 2.9)
    s.boiler(bx0, bz0, bw)
    for k, x in enumerate((bx0 + bw * .6, bx0 + bw * .8)):
        s.line((x, .45, bz0), (x, .45, bz0 - .8), cu, 5)
    s.poly([(2.2, 3.2, .01), (7.4, 3.2, .01), (7.4, 6.8, .01), (2.2, 6.8, .01)], p["teal"])
    s.poly([(2.5, 3.5, .02), (7.1, 3.5, .02), (7.1, 6.5, .02), (2.5, 6.5, .02)], "none",
           f'stroke="{p["teal_light"]}" stroke-width="2" stroke-dasharray="6 6"')
    s.box(1.3, 5.0, 0, 1.0, 2.6, .9, "#e9e1d4", "#cfc3b1", "#ddd2c1")
    s.box(2.3, 5.0, 0, 3.4, 2.6, .55, "#e9e1d4", "#cfc3b1", "#ddd2c1")
    s.box(2.3, 6.9, .55, 3.4, .7, .9, "#f1ebe1", "#d6cab8", "#e4dacb")
    s.box(2.6, 5.3, .55, 1.2, 1.4, .28, p["orange"], p["orange_d"], p["orange_m"])
    s.toolbox(8.4, 1.6)
    s.plant(8.6, 6.3)
    return s


def scene_manutenzione():
    s = Scene(label="Illustrazione: manutenzione della caldaia con analizzatore fumi, attrezzi e libretto di impianto")
    W, D, H = 7.5, 6.5, 6.2
    s.shadow(W / 2, D / 2 + 1, 260, 60, .10)
    s.room(W, D, H, floor="tile")
    # calendario delle manutenzioni sulla parete sinistra
    U = s.U
    cw, ch = 2.3 * U, 2.2 * U
    cells = "".join(
        f'<rect x="{8 + (k % 5) * (cw - 16) / 5:.1f}" y="{30 + (k // 5) * 12:.1f}" width="{(cw - 16) / 5 - 3:.1f}" height="9" '
        f'fill="{p["orange"] if k == 17 else "#e9e2d8"}"/>' for k in range(25))
    s.face("x", (.03, 4.6, 5.0), cw, ch,
           f'<rect width="{cw:.0f}" height="{ch:.0f}" rx="4" fill="#ffffff"/><rect width="{cw:.0f}" height="20" rx="4" fill="{p["teal"]}"/>'
           f'<text x="8" y="14" {FONT} font-size="8" fill="#ffffff">MANUTENZIONE</text>' + cells)
    # caldaia aperta con canna fumaria
    bx0, bz0, bw, bh = 2.6, 2.4, 1.9, 2.7
    s.box(bx0 + .7, .15, bz0 + bh, .5, .5, H - bz0 - bh - .2, "#c9d3d4", "#b5c1c3", "#9fb0b3")
    s.boiler(bx0, bz0, bw, bh, open_front=True)
    s.pipes_down(bx0, bw, bz0)
    # coperchio frontale appoggiato alla parete
    s.box(5.2, .1, 0, 1.6, .15, 2.4, "#ffffff", "#f4f7f6", "#dfe7e5")
    # analizzatore fumi con sonda nella canna fumaria
    s.path3([(2.2, 3.1, .55), (2.4, 2.4, 1.6), (2.9, 1.2, 3.8), (bx0 + .95, .55, bz0 + bh + .45)], p["orange"], 3)
    s.box(1.6, 2.7, 0, .9, .6, .5, p["dark_l"], p["dark"], p["dark_r"])
    s.face("y", (1.68, 3.3, .45), .74 * U, .35 * U,
           f'<rect width="{.74*U:.0f}" height="{.3*U:.0f}" rx="2" fill="#123033"/>'
           f'<text x="3" y="9" {FONT} font-size="8" fill="{p["screen"]}">CO 12</text>')
    # cassetta attrezzi aperta
    s.toolbox(4.6, 2.4, open_=True, label=False)
    # cartellina con checklist e libretto sul pavimento
    s.face("z", (1.2, 4.3, .02), 1.6 * U, 2.0 * U,
           f'<rect width="{1.6*U:.0f}" height="{2.0*U:.0f}" rx="4" fill="#8a5a3a"/>'
           f'<rect x="5" y="8" width="{1.6*U-10:.0f}" height="{2.0*U-13:.0f}" fill="#ffffff"/>'
           + "".join(f'<path d="M10 {20+k*12} l3 3 6 -6" fill="none" stroke="#2f8f5b" stroke-width="2"/>'
                     f'<line x1="24" y1="{19+k*12}" x2="{1.6*U-14:.0f}" y2="{19+k*12}" stroke="#c9d3d4" stroke-width="2"/>' for k in range(4)))
    s.box(3.3, 4.7, 0, 1.3, 1.0, .12, "#2b5f9e", "#214a7c", "#1b3f6a")
    s.face("z", (3.3, 4.7, .121), 1.3 * U, 1.0 * U,
           f'<text x="5" y="18" {FONT} font-size="7.5" fill="#ffffff">LIBRETTO</text>'
           f'<text x="5" y="28" font-family="system-ui,sans-serif" font-size="6" fill="#cfe0f5">di impianto</text>')
    s.plant(6.3, 5.2, .9)
    return s


def scene_riparazione():
    s = Scene(label="Illustrazione: riparazione di una caldaia in blocco con codice errore, attrezzi e ricambio originale")
    W, D, H = 7.5, 6.5, 6.2
    s.shadow(W / 2, D / 2 + 1, 260, 60, .10)
    s.room(W, D, H, floor="tile")
    bx0, bz0, bw, bh = 3.0, 2.5, 1.9, 2.7
    s.boiler(bx0, bz0, bw, bh, display="F.28", display_color="#ff9a5c", glow=False)
    s.pipes_down(bx0, bw, bz0)
    # fumetto di allarme che lampeggia
    ax, ay = s.P(bx0 + bw + .2, .8, bz0 + bh + .5)
    s.add(f'<g class="iso-blink"><path d="M{ax:.0f} {ay-38:.0f} l24 42 h-48z" fill="{p["orange"]}" stroke="#ffffff" stroke-width="4" '
          f'stroke-linejoin="round"/><rect x="{ax-2.5:.0f}" y="{ay-22:.0f}" width="5" height="14" rx="2" fill="#ffffff"/>'
          f'<circle cx="{ax:.0f}" cy="{ay-3:.0f}" r="3" fill="#ffffff"/></g>')
    thermostat(s, 1.2, 2.9)
    # scatola ricambio con scheda elettronica
    s.cbox(1.4, 2.6, 0, 1.6, 1.3, .9, "#c9a46c")
    s.box(1.55, 2.7, .9, 1.3, 1.0, .06, "#2f8f5b", "#257349", "#1f633f")
    s.face("z", (1.55, 2.7, .961), 1.3 * s.U, 1.0 * s.U,
           "".join(f'<rect x="{6+k*10}" y="{6+(k%2)*12}" width="7" height="7" fill="#1c3b2c"/>' for k in range(4))
           + '<line x1="6" y1="30" x2="40" y2="30" stroke="#d9b25a" stroke-width="2"/>')
    s.face("y", (1.5, 3.9, .75), 1.4 * s.U, .5 * s.U,
           f'<text x="4" y="11" {FONT} font-size="9" fill="#6f5531">RICAMBIO</text>')
    # chiave e cacciavite sul pavimento
    s.face("z", (3.6, 4.0, .02), 2.4 * s.U, 1.4 * s.U,
           f'<g transform="rotate(-18 40 25)"><rect x="8" y="20" width="60" height="9" rx="4" fill="#9fb0b3"/>'
           f'<path d="M66 12 a13 13 0 1 1 0 26 v-8 h8 v-10 h-8z" fill="#9fb0b3"/></g>'
           f'<g transform="rotate(14 50 40)"><rect x="20" y="38" width="34" height="11" rx="4" fill="{p["orange"]}"/>'
           f'<rect x="54" y="41" width="30" height="5" fill="#c9d3d4"/></g>')
    s.toolbox(5.5, 2.0, open_=True, label=False)
    s.plant(.9, 5.3, .9)
    return s


def scene_sostituzione():
    s = Scene(label="Illustrazione: sostituzione di una vecchia caldaia con una nuova caldaia a condensazione")
    W, D, H = 9.5, 6.5, 6.2
    s.shadow(W / 2, D / 2 + 1, 320, 64, .10)
    s.room(W, D, H)
    # nuova caldaia sulla parete
    bx0, bz0, bw, bh = 5.4, 2.5, 1.8, 2.6
    s.boiler(bx0, bz0, bw, bh)
    s.pipes_down(bx0, bw, bz0)
    s.waves(bx0 + .2, .9, bz0 + bh + .5, 3, .6, plane="y")
    # sagoma della vecchia caldaia sulla parete (segno più chiaro)
    s.poly([(1.6, .01, 2.3), (3.8, .01, 2.3), (3.8, .01, 5.4), (1.6, .01, 5.4)], "#f3ebdf")
    s.poly([(1.6, .01, 2.3), (3.8, .01, 2.3), (3.8, .01, 5.4), (1.6, .01, 5.4)], "none",
           'stroke="#d8c7b0" stroke-width="2" stroke-dasharray="6 6"')
    # carrello con la vecchia caldaia
    ox, oy = 1.5, 3.4
    s.box(ox - .1, oy - .1, 0, 2.5, 1.4, .12, "#7d8f93", "#6b7c80", "#5d6d71")
    for x in (ox + .1, ox + 2.1):
        s.line((x, oy - .05, .1), (x, oy - .05, 3.9), "#5d6d71", 5)
    s.line((ox + .1, oy - .05, 3.9), (ox + 2.1, oy - .05, 3.9), "#5d6d71", 5)
    s.boiler(ox, .12, 2.2, 3.0, d=1.1, display="---", old=True, glow=False, y0=oy)
    for x in (ox + .3, ox + 1.9):
        cx, cy = s.P(x, oy + 1.25, .2)
        s.add(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="9" ry="12" fill="#24333a"/>')
    # freccia a terra: dalla vecchia alla nuova
    s.path3([(4.2, 4.6, .02), (5.4, 4.6, .02), (6.3, 3.6, .02), (6.3, 2.2, .02)], p["orange"], 4,
            'stroke-dasharray="10 8" class="iso-flow"')
    tx, ty = s.P(6.3, 2.0, .02)
    s.add(f'<path d="M{tx:.0f} {ty:.0f} l-12 2 l9 9z" fill="{p["orange"]}"/>')
    # imballo della nuova caldaia
    s.cbox(7.4, 3.8, 0, 1.6, 1.5, 1.2, "#c9a46c")
    s.poly([(7.4, 5.3, 1.2), (9.0, 5.3, 1.2), (9.0, 5.9, 1.7), (7.4, 5.9, 1.7)], "#b38f5a")
    s.poly([(9.0, 3.8, 1.2), (9.0, 5.3, 1.2), (9.5, 5.3, 1.6), (9.5, 3.8, 1.6)], "#a5824f")
    s.plant(.8, 5.5, .85)
    return s


def house(s, x, y, w, d, h, wall="#f1dcc4", roof="#c2553a", windows=True):
    s.cbox(x, y, 0, w, d, h, wall)
    # tetto a capanna lungo x
    r = .9
    s.poly([(x - .1, y + d + .1, h), (x + w + .1, y + d + .1, h), (x + w + .1, y + d / 2, h + r), (x - .1, y + d / 2, h + r)], roof)
    s.poly([(x + w + .1, y - .1, h), (x + w + .1, y + d + .1, h), (x + w + .1, y + d / 2, h + r)], shade(roof, .8))
    if windows:
        U = s.U
        win = "".join(f'<rect x="{8 + k * 22}" y="10" width="12" height="14" fill="#ffd27a" opacity=".85"/>'
                      for k in range(int((w * U - 10) // 22)))
        s.face("y", (x, y + d, h - .2), w * U, h * U * .5, win)


def cypress(s, x, y, h=2.2):
    bx, by = s.P(x, y, 0)
    s.add(f'<path d="M{bx:.0f} {by:.0f} c-11 -{h*14:.0f} -6 -{h*26:.0f} 0 -{h*34:.0f} c6 {h*8:.0f} 11 {h*20:.0f} 0 {h*34:.0f}z" fill="#2f6b4f"/>')


def scene_zone():
    s = Scene(label="Illustrazione: il furgone CFM in viaggio tra le strade di Verona e provincia")
    W, D = 13, 10
    s.shadow(W / 2, D / 2 + 1, 400, 80, .10)
    s.box(0, 0, -.5, W, D, .5, "#e4dccb", "#b9a88c", "#cbbb9f")
    # prato e strada
    s.poly([(0, 0, .001), (W, 0, .001), (W, 4.2, .001), (0, 4.2, .001)], "#cfe0bf")
    s.poly([(0, 6.4, .001), (W, 6.4, .001), (W, D, .001), (0, D, .001)], "#cfe0bf")
    s.poly([(0, 4.4, .002), (W, 4.4, .002), (W, 6.2, .002), (0, 6.2, .002)], "#5b6670")
    s.line((0, 5.3, .003), (W, 5.3, .003), "#ffffff", 2.5, 'stroke-dasharray="14 14"')
    # Arena: blocco in rosso Verona con due ordini di arcate
    ax, ay, aw, ad, ah = 1.0, .6, 4.2, 2.8, 2.2
    s.cbox(ax, ay, 0, aw, ad, ah, "#e8b9a3")
    U = s.U
    arcs = lambda w, h: "".join(
        f'<path d="M{6 + k*24} {h - 4} v-{h*.28:.0f} a8 8 0 0 1 16 0 v{h*.28:.0f}z M{6 + k*24} {h*.45:.0f} v-{h*.2:.0f} '
        f'a8 8 0 0 1 16 0 v{h*.2:.0f}z" fill="#b97d66"/>' for k in range(int(w // 24)))
    s.face("y", (ax, ay + ad, ah), aw * U, ah * U, arcs(aw * U, ah * U))
    s.face("x", (ax + aw, ay + ad, ah), ad * U, ah * U, arcs(ad * U, ah * U))
    s.box(ax + .3, ay + .3, ah, aw - .6, ad - .6, .02, "#d79f88", "#d79f88", "#d79f88")
    # Torre dei Lamberti
    tx, ty = 7.2, .8
    s.cbox(tx, ty, 0, .9, .9, 5.2, "#d9b08c")
    s.cbox(tx - .1, ty - .1, 5.2, 1.1, 1.1, .7, "#f0e2cc")
    s.cbox(tx + .1, ty + .1, 5.9, .7, .7, .5, "#e3d2b8")
    tpx, tpy = s.P(tx + .45, ty + .45, 6.4)
    s.add(f'<path d="M{tpx-12:.0f} {tpy:.0f} q12 -26 24 0z" fill="#8fa6a0"/>')
    house(s, 9.0, .8, 2.2, 2.2, 1.8)
    cypress(s, 6.4, 3.6, 2.4); cypress(s, 12.2, 3.4, 2.0); cypress(s, .6, 3.8, 1.8)
    # furgone CFM
    vx, vy = 4.0, 4.7
    for x in (vx + .5, vx + 2.6):
        for y in (vy, vy + 1.1):
            cx, cy = s.P(x, y + .02, .3)
            s.add(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="10" ry="13" fill="#1d2a2f"/>')
    s.box(vx, vy, .3, 2.6, 1.1, 1.6, "#ffffff", "#f4f7f6", "#dfe7e5")
    s.box(vx + 2.6, vy, .3, .8, 1.1, 1.0, "#ffffff", "#f4f7f6", "#dfe7e5")
    s.poly([(vx + 2.6, vy, 1.9), (vx + 2.6, vy + 1.1, 1.9), (vx + 3.4, vy + 1.1, 1.3), (vx + 3.4, vy, 1.3)], "#9cc7d6")
    s.face("y", (vx, vy + 1.1, 1.9), 2.6 * U, 1.6 * U,
           f'<rect x="0" y="{.9*U:.0f}" width="{2.6*U:.0f}" height="9" fill="{p["orange"]}"/>'
           f'<rect x="0" y="{.9*U+11:.0f}" width="{2.6*U:.0f}" height="4" fill="{p["teal"]}"/>'
           f'<text x="10" y="{.75*U:.0f}" {FONT} font-size="16" fill="{p["teal"]}">CFM</text>'
           f'<text x="10" y="{.75*U+38:.0f}" font-family="system-ui,sans-serif" font-weight="600" font-size="7" fill="#51626b">Assistenza caldaie</text>')
    for x in (vx + .5, vx + 2.6):
        cx, cy = s.P(x, vy + 1.12, .3)
        s.add(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="10" ry="13" fill="#24333a"/><ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="4" ry="5" fill="#9fb0b3"/>')
    # case sul lato vicino e segnaposto
    house(s, 10.2, 7.4, 2.0, 1.8, 1.5, "#f6e7d3", "#b9482f")
    cypress(s, 2.0, 8.4, 2.0); cypress(s, 3.0, 8.9, 1.6)
    px, py = s.P(vx + 1.3, vy + .5, 3.2)
    s.add(f'<g class="iso-float"><path d="M{px:.0f} {py+18:.0f} c-12 -14 -20 -22 -20 -32 a20 20 0 0 1 40 0 c0 10 -8 18 -20 32z" '
          f'fill="{p["orange"]}"/><circle cx="{px:.0f}" cy="{py-14:.0f}" r="7" fill="#ffffff"/></g>')
    return s


def scene_laboratorio():
    s = Scene(label="Illustrazione: laboratorio CFM con scaffale di ricambi originali, banco di lavoro e attrezzi")
    W, D, H = 9.5, 7, 6.2
    s.shadow(W / 2, D / 2 + 1, 320, 66, .10)
    s.room(W, D, H, floor="tile")
    U = s.U
    # pannello porta-attrezzi sulla parete sinistra
    pw, ph = 3.4 * U, 2.0 * U
    holes = "".join(f'<circle cx="{8 + (k % 14) * (pw - 16) / 13:.1f}" cy="{8 + (k // 14) * 12:.1f}" r="1.6" fill="#b9a88c"/>' for k in range(14 * 6))
    tools = (f'<rect x="20" y="16" width="8" height="42" rx="3" fill="#9fb0b3"/><circle cx="24" cy="16" r="9" fill="#9fb0b3"/>'
             f'<rect x="48" y="20" width="10" height="26" rx="3" fill="{p["orange"]}"/><rect x="51" y="46" width="4" height="18" fill="#c9d3d4"/>'
             f'<path d="M78 18 l10 0 l-2 30 l-6 0z" fill="#24333a"/><rect x="77" y="48" width="12" height="14" rx="3" fill="{p["orange"]}"/>'
             f'<rect x="100" y="22" width="16" height="30" rx="4" fill="#e3c04a"/><rect x="103" y="26" width="10" height="7" fill="#123033"/>')
    s.face("x", (.03, 5.6, 5.0), pw, ph, f'<rect width="{pw:.0f}" height="{ph:.0f}" rx="3" fill="#e2d3bb"/>' + holes + tools)
    # scaffale ricambi sulla parete destra
    sx, sw = 4.6, 3.8
    for z in (.2, 1.5, 2.8, 4.1):
        s.box(sx, 0, z, sw, 1.0, .12, "#d9e1e2", "#c9d3d4", "#b5c1c3")
    colors = [p["orange"], "#c9a46c", p["teal"], "#c9a46c", "#9fb0b3", p["orange"], "#c9a46c", p["teal"], "#c9a46c", "#c9a46c", p["orange"], "#9fb0b3"]
    k = 0
    for z in (.32, 1.62, 2.92):
        x = sx + .15
        while x < sx + sw - .8:
            c = colors[k % len(colors)]; k += 1
            bw = .7 if c != "#9fb0b3" else .55
            s.cbox(x, .15, z, bw, .7, .75 if c == "#c9a46c" else .55, c)
            x += bw + .15
    for x in (sx, sx + sw - .1):
        s.box(x, .9, 0, .1, .1, 4.3, "#b5c1c3", "#9fb0b3", "#7d8f93")
    # banco di lavoro con scheda elettronica e caldaia in prova
    bx, by = 2.0, 2.8
    for x, y in ((bx + .1, by + .1), (bx + 3.3, by + .1), (bx + .1, by + 1.5), (bx + 3.3, by + 1.5)):
        s.box(x, y, 0, .2, .2, 1.5, "#7d8f93", "#6b7c80", "#5d6d71")
    s.box(bx, by, 1.5, 3.6, 1.8, .18, "#d9a46f", "#b98252", "#a9744a")
    s.box(bx + .4, by + .4, 1.68, 1.3, .9, .06, "#2f8f5b", "#257349", "#1f633f")
    s.face("z", (bx + .4, by + .4, 1.741), 1.3 * U, .9 * U,
           "".join(f'<rect x="{5+i*10}" y="{5+(i%2)*10}" width="7" height="7" fill="#1c3b2c"/>' for i in range(4))
           + '<line x1="5" y1="25" x2="38" y2="25" stroke="#d9b25a" stroke-width="2"/>')
    s.box(bx + 2.1, by + .5, 1.68, .6, .4, .5, "#e3c04a", "#c9a73a", "#b39230")
    s.face("y", (bx + 2.15, by + .9, 2.12), .5 * U, .3 * U, '<rect x="2" y="2" width="13" height="7" fill="#123033"/>')
    s.line((bx + 2.4, by + .9, 1.9), (bx + 1.6, by + 1.2, 1.75), "#e04a3a", 2)
    s.toolbox(6.6, 4.6)
    s.cbox(1.0, 5.4, 0, 1.2, 1.0, .8, "#c9a46c")
    s.cbox(1.1, 5.5, .8, 1.0, .8, .6, "#d4b07a")
    return s


SCENES = {
    "scene-casa": scene_casa, "scene-manutenzione": scene_manutenzione, "scene-riparazione": scene_riparazione,
    "scene-sostituzione": scene_sostituzione, "scene-zone": scene_zone, "scene-laboratorio": scene_laboratorio,
}

if __name__ == "__main__":
    for name, fn in SCENES.items():
        svg = fn().svg()
        # ID univoci per scena: più illustrazioni possono stare nella stessa pagina
        svg = svg.replace('id="', f'id="{name}-').replace("url(#", f"url(#{name}-")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("ok", name)
