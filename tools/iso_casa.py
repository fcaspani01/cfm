"""Illustrazione isometrica "casa calda": soggiorno in sezione con caldaia, termosifone e finestra su Verona."""
import math, sys

U = 34                      # pixel per unità
C, S = math.cos(math.radians(30)), math.sin(math.radians(30))
OX, OY = 430, 250           # origine sullo schermo

def P(x, y, z):
    return (OX + (x - y) * C * U, OY + (x + y) * S * U - z * U)

def poly(pts, fill, extra=""):
    d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in pts))
    return f'<polygon points="{d}" fill="{fill}" {extra}/>'

def box(x, y, z, dx, dy, dz, top, left, right, extra=""):
    """Parallelepipedo: facce visibili superiore, frontale-sinistra (y max), frontale-destra (x max)."""
    return "".join([
        poly([(x, y, z+dz), (x+dx, y, z+dz), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)], top, extra),
        poly([(x, y+dy, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)], left, extra),
        poly([(x+dx, y, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x+dx, y, z+dz)], right, extra),
    ])

def line(a, b, stroke, w=2, extra=""):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" {extra}/>'

W, D, H, T = 10, 8, 6.2, 0.45    # larghezza (x), profondità (y), altezza, spessore muri
ry0, ry1, rz0, rz1 = 4.3, 7.2, 0.7, 2.3   # termosifone
o = []
o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="110 10 700 580" role="img" aria-label="Illustrazione: soggiorno in sezione riscaldato da una caldaia murale">')
o.append('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26415c"/><stop offset=".55" stop-color="#e98a5a"/><stop offset="1" stop-color="#f6c48b"/></linearGradient>
<radialGradient id="warm" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb070" stop-opacity=".55"/><stop offset="1" stop-color="#ffb070" stop-opacity="0"/></radialGradient>
<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe2a8" stop-opacity=".9"/><stop offset="1" stop-color="#ffe2a8" stop-opacity="0"/></linearGradient>
</defs>''')
# ombra a terra
fx, fy = P(W/2, D/2, -0.6)
o.append(f'<ellipse cx="{fx:.0f}" cy="{fy+40:.0f}" rx="330" ry="70" fill="#8a5432" opacity=".10"/>')
# solaio (pavimento con spessore)
o.append(box(-T, -T, -0.5, W+T, D+T, 0.5, "#c98d5e", "#8a5432", "#a5663e"))
# parquet
for k in range(1, 10):
    o.append(line((k, 0, 0.001), (k, D, 0.001), "#b67b4f", 1.4))
# muro sinistro (piano x=0, lungo y) e muro destro (piano y=0, lungo x), con spessore
o.append(box(-T, 0, 0, T, D, H, "#d9cbb8", "#cdbba4", "#f1e7d9"))   # muro x=0: la faccia interna è la "right"
o.append(box(-T, -T, 0, W+T, T, H, "#d9cbb8", "#ebe0cf", "#cdbba4"))  # muro y=0: faccia interna è la "left"
# battiscopa
o.append(poly([(0, 0.02, 0), (W, 0.02, 0), (W, 0.02, 0.25), (0, 0.02, 0.25)], "#d8c7b0"))
o.append(poly([(0.02, 0, 0), (0.02, D, 0), (0.02, D, 0.25), (0.02, 0, 0.25)], "#e6d8c4"))

# finestra sul muro sinistro (x=0): tramonto su Verona
wy0, wy1, wz0, wz1 = 1.2, 3.6, 2.4, 5.0
o.append(poly([(0.01, wy0-.15, wz0-.15), (0.01, wy1+.15, wz0-.15), (0.01, wy1+.15, wz1+.15), (0.01, wy0-.15, wz1+.15)], "#ffffff"))
o.append(poly([(0.02, wy0, wz0), (0.02, wy1, wz0), (0.02, wy1, wz1), (0.02, wy0, wz1)], "url(#sky)"))
# skyline nella finestra: arcate dell'Arena e torre
def wp(y, z): return P(0.03, y, z)
sk = [(wy0, wz0), (wy0, wz0+.6), (wy0+.5, wz0+.75), (wy0+1.1, wz0+.75), (wy0+1.1, wz0+.6), (wy0+1.4, wz0+.6),
      (wy0+1.4, wz0+1.5), (wy0+1.6, wz0+1.5), (wy0+1.6, wz0+.5), (wy1, wz0+.45), (wy1, wz0)]
o.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in (wp(*q) for q in sk)) + '" fill="#2b2733" opacity=".85"/>')
o.append(poly([(0.03, (wy0+wy1)/2, wz0), (0.03, (wy0+wy1)/2, wz1)] * 1 + [(0.03, (wy0+wy1)/2 + .06, wz1), (0.03, (wy0+wy1)/2 + .06, wz0)], "#ffffff"))
o.append(box(0, wy0-.2, wz0-.3, 0.45, wy1-wy0+.4, 0.12, "#ffffff", "#e9e2d8", "#f4efe8"))  # davanzale

# caldaia sul muro destro (y=0)
bx0, bx1, bz0, bz1 = 6.3, 8.1, 2.6, 5.2
gx, gy = P((bx0+bx1)/2, 0.5, (bz0+bz1)/2)
o.append(f'<circle cx="{gx:.0f}" cy="{gy:.0f}" r="95" fill="url(#warm)"/>')
o.append(box(bx0, 0, bz0, bx1-bx0, 0.8, bz1-bz0, "#f4f7f6", "#ffffff", "#dfe7e5"))
# display e oblò sulla faccia frontale (y=0.8)
o.append(poly([(bx0+.35, .81, bz0+.45), (bx1-.35, .81, bz0+.45), (bx1-.35, .81, bz0+.95), (bx0+.35, .81, bz0+.95)], "#123033"))
tx, ty = P(bx0+.55, .81, bz0+.62)
o.append(f'<text x="{tx:.0f}" y="{ty:.0f}" font-family="system-ui,sans-serif" font-weight="800" font-size="13" fill="#7fe0cf" transform="skewY(30) translate(0 {-tx*math.tan(math.radians(30)):.1f})">55°</text>')
cx_, cy_ = P((bx0+bx1)/2, .81, bz0+1.75)
o.append(f'<ellipse cx="{cx_:.0f}" cy="{cy_:.0f}" rx="17" ry="20" fill="#123033" transform="rotate(-30 {cx_:.0f} {cy_:.0f}) skewX(0)"/>')
o.append(f'<path class="iso-flame" d="M{cx_:.0f} {cy_-14:.0f} c5 7 -5 9 -5 16 a5 5 0 0 0 10 0 c0 -4 -3 -6 -3 -9 c-1 3 -3 4 -3 4 c0 -4 4 -6 1 -11z" fill="#ff8a3d"/>')
# tubi in rame dalla caldaia al pavimento e verso il termosifone
cu = "#c27a4a"
for k, x in enumerate((bx0+.4, bx0+.75, bx1-.75, bx1-.4)):
    o.append(line((x, .45, bz0), (x, .45, 0.25 if k < 2 else bz0-.8), cu, 5))
# mandata e ritorno lungo il battiscopa fino al termosifone
o.append(line((bx0+.4, .45, .25), (0.45, .45, .25), cu, 5))
o.append(line((bx0+.75, .45, .45), (0.7, .45, .45), cu, 5))
o.append(line((0.45, .45, .25), (0.45, ry0+.35, .25), cu, 5))
o.append(line((0.7, .45, .45), (0.7, ry1-.35, .45), cu, 5))
o.append(line((0.45, ry0+.35, .25), (0.2, ry0+.35, rz0+.05), cu, 5))
o.append(line((0.7, ry1-.35, .45), (0.2, ry1-.35, rz0+.05), cu, 5))
# acqua calda che scorre
o.append(line((bx0+.75, .45, .45), (0.7, .45, .45), "#ffd9b8", 2, 'class="iso-flow" stroke-dasharray="3 12"'))
o.append(line((0.7, .45, .45), (0.7, ry1-.35, .45), "#ffd9b8", 2, 'class="iso-flow" stroke-dasharray="3 12"'))

# termosifone sul muro sinistro
o.append(box(0, ry0, rz0, 0.35, ry1-ry0, rz1-rz0, "#ffffff", "#e7ecec", "#f7f9f9"))
n = 12
for k in range(1, n):
    y = ry0 + k * (ry1-ry0) / n
    o.append(line((0.36, y, rz0+.08), (0.36, y, rz1-.08), "#cdd6d5", 1.6))
# calore dal termosifone
for k, y in enumerate((ry0+.6, ry0+1.45, ry0+2.3)):
    a, b = P(0.6, y, rz1+.3), P(0.6, y, rz1+1.4)
    o.append(f'<path class="iso-wave" style="animation-delay:{k*.7}s" d="M{a[0]:.1f} {a[1]:.1f} c-6 -8 6 -14 0 -22 s6 -14 0 -22" fill="none" stroke="#f08a4b" stroke-width="3" stroke-linecap="round" opacity=".8"/>')

# cronotermostato sul muro destro
o.append(box(3.2, 0, 2.9, 0.7, 0.12, 0.8, "#ffffff", "#ffffff", "#e3e9e8"))
ttx, tty = P(3.55, .13, 3.3)
o.append(f'<circle cx="{ttx:.0f}" cy="{tty:.0f}" r="5" fill="#e8611a"/>')

# tappeto, divano, lampada, pianta
o.append(poly([(2.2, 3.2, .01), (7.4, 3.2, .01), (7.4, 6.8, .01), (2.2, 6.8, .01)], "#0f6b62"))
o.append(poly([(2.5, 3.5, .02), (7.1, 3.5, .02), (7.1, 6.5, .02), (2.5, 6.5, .02)], "none", 'stroke="#7cc7b9" stroke-width="2" stroke-dasharray="6 6"'))
o.append(box(1.3, 5.0, 0, 1.0, 2.6, 0.9, "#e9e1d4", "#cfc3b1", "#ddd2c1"))   # bracciolo/schienale
o.append(box(2.3, 5.0, 0, 3.4, 2.6, 0.55, "#e9e1d4", "#cfc3b1", "#ddd2c1"))  # seduta
o.append(box(2.3, 6.9, 0.55, 3.4, 0.7, 0.9, "#f1ebe1", "#d6cab8", "#e4dacb"))  # schienale
o.append(box(2.6, 5.3, 0.55, 1.2, 1.4, 0.28, "#e8611a", "#b9480f", "#cf5615"))  # cuscino
o.append(box(8.6, 6.3, 0, 0.8, 0.8, 0.9, "#c56a3f", "#9a4e2b", "#ad5a33"))   # vaso
lx, ly = P(9.0, 6.7, 0.9)
for dx, dy, r in ((0, -26, 18), (-14, -40, 15), (14, -42, 16), (0, -56, 13)):
    o.append(f'<circle cx="{lx+dx:.0f}" cy="{ly+dy:.0f}" r="{r}" fill="#2f7d55"/>')
o.append(box(8.4, 1.6, 0, 1.2, 1.2, 0.7, "#2b3a40", "#1d2a2f", "#24333a"))   # cassetta attrezzi CFM
o.append(box(8.4, 1.6, 0.7, 1.2, 1.2, 0.18, "#e8611a", "#b9480f", "#cf5615"))
kx, ky = P(9.0, 2.8, 0.35)
o.append(f'<text x="{kx:.0f}" y="{ky:.0f}" font-family="system-ui,sans-serif" font-weight="800" font-size="11" fill="#ffffff" text-anchor="middle">CFM</text>')
o.append("</svg>")
sys.stdout.write("\n".join(o))
