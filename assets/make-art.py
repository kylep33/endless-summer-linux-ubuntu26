#!/usr/bin/env python3
"""Render every image in the theme into ../root/.

Needs: cairosvg, pillow (pip, in a venv). Run: python make-art.py
Inputs in this folder: photos/*.png (reference photos), joe-frame.png (avatar source),
fonts/BebasNeue-Regular.ttf.
"""
import io, math, os, random
import cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "root")
BEBAS = os.path.join(HERE, "fonts", "BebasNeue-Regular.ttf")

# palette: Kodachrome sea and sky, sand, and the Travoltas-cover red
NAVY, OCEAN, SURF, SKY = "#0E2F44", "#1B7FA6", "#2BB3C9", "#9FD8E8"
SAND, CREAM, CORAL, ORANGE, SUN = "#EDD7A8", "#FBF4E4", "#E0472F", "#F28C28", "#F9C74F"
DUSK_TOP, DUSK_MID = "#0B1D2E", "#3D2A5C"


def out(*p):
    path = os.path.join(ROOT, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def svg2img(svg, w, h):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert("RGBA")


def wave_path(y, amp, length, phase, w, h, bottom=None):
    pts = [f"M0,{bottom}"] if bottom is not None else []
    for x in range(0, w + 41, 40):
        yy = y + amp * math.sin(2 * math.pi * x / length + phase) + amp * 0.35 * math.sin(2 * math.pi * x / (length * 0.43) + phase * 2)
        pts.append(f"L{x},{yy:.1f}")
    if bottom is None:
        return "M" + " ".join(pts)[1:]
    pts.append(f"L{w},{bottom} Z")
    return " ".join(pts)


def board(cx, base, length, width, angle, rail, deck, stringer):
    """A longboard standing nose-up in the sand, outline in local coords then rotated."""
    l, w = length, width / 2
    d = (f"M0,{-l} C{w*0.9},{-l*0.82} {w},{-l*0.45} {w},{-l*0.2} "
         f"C{w},{-l*0.02} {w*0.7},0 0,0 C{-w*0.7},0 {-w},{-l*0.02} {-w},{-l*0.2} "
         f"C{-w},{-l*0.45} {-w*0.9},{-l*0.82} 0,{-l} Z")
    inner = w * 0.78
    di = (f"M0,{-l*0.95} C{inner*0.9},{-l*0.8} {inner},{-l*0.45} {inner},{-l*0.2} "
          f"C{inner},{-l*0.05} {inner*0.7},{-l*0.03} 0,{-l*0.03} C{-inner*0.7},{-l*0.03} {-inner},{-l*0.05} {-inner},{-l*0.2} "
          f"C{-inner},{-l*0.45} {-inner*0.9},{-l*0.8} 0,{-l*0.95} Z")
    return (f'<g transform="translate({cx},{base}) rotate({angle})">'
            f'<path d="{d}" fill="{rail}"/><path d="{di}" fill="{deck}"/>'
            f'<rect x="-6" y="{-l*0.95}" width="12" height="{l*0.92}" fill="{stringer}"/></g>')


def scene(night, w=3840, h=2160):
    hz = int(h * 0.60)  # horizon
    sun_r, sun_cy = 560, (hz + 40 if night else hz - 260)
    sky = [(0, DUSK_TOP), (0.55, DUSK_MID), (1, CORAL)] if night else [(0, "#7CC6DE"), (0.6, "#CFEAEF"), (1, "#FCE6B6")]
    sun = [(0, SUN), (0.55, ORANGE), (1, CORAL)] if night else [(0, "#FFE08A"), (0.6, SUN), (1, ORANGE)]
    stops = lambda s: "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in s)
    # retro sun: horizontal cuts that thicken toward the horizon
    cuts, y, gap = [], min(sun_cy + 40, hz - 260), 10
    while y < sun_cy + sun_r:
        cuts.append(f'<rect x="0" y="{y}" width="{w}" height="{gap}" fill="url(#sky)"/>')
        y += 70
        gap += 9
    stars = ""
    if night:
        rnd = random.Random(7)
        stars = "".join(f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, hz*0.6):.0f}" r="{rnd.choice([2, 2, 3, 4])}" fill="{CREAM}" opacity="{rnd.uniform(.4, .9):.2f}"/>' for _ in range(160))
    seas = ([("#152C45", 0), ("#11253B", 140), ("#0C1C2E", 330)] if night else [(OCEAN, 0), ("#166D93", 140), (NAVY, 330)])
    sea = f'<rect x="0" y="{hz}" width="{w}" height="{h-hz}" fill="{seas[0][0]}"/>'
    for i, (c, dy) in enumerate(seas[1:], 1):
        sea += f'<path d="{wave_path(hz + dy, 14 + 8*i, 900 - 150*i, i, w, h, h)}" fill="{c}"/>'
    foam = "".join(f'<path d="{wave_path(hz + dy, 10 + 6*i, 700 - 90*i, i*1.7, w, h)}" fill="none" stroke="{CREAM}" stroke-width="{5+3*i}" stroke-opacity="{.35 if night else .55}" stroke-linecap="round"/>'
                   for i, dy in enumerate([60, 210, 400]))
    # sun glitter on the water
    glit = "".join(f'<rect x="{w/2 - (380 - 26*k)}" y="{hz + 30 + 34*k}" width="{2*(380 - 26*k)}" height="{8 + k}" rx="6" fill="{ORANGE if night else "#FFF3C4"}" opacity="{.75 - .05*k:.2f}"/>' for k in range(12))
    sand_top = int(h * 0.80)
    sand = (f'<path d="M0,{sand_top+60} C{w*0.25},{sand_top-30} {w*0.55},{sand_top+50} {w},{sand_top-40} L{w},{h} L0,{h} Z" fill="{"#7A5A44" if night else SAND}"/>'
            f'<path d="M0,{sand_top+60} C{w*0.25},{sand_top-30} {w*0.55},{sand_top+50} {w},{sand_top-40}" fill="none" stroke="{CREAM}" stroke-width="22" stroke-opacity="{.25 if night else .9}"/>')
    boards = (board(3020, sand_top + 170, 980, 230, 7, "#5E2A22" if night else CORAL, "#2E2230" if night else CREAM, "#5E2A22" if night else CORAL)
              + board(3260, sand_top + 150, 900, 210, -5, "#1E2A3A" if night else NAVY, "#3A2F3F" if night else SAND, "#1E2A3A" if night else NAVY))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{hz}">{stops(sky)}</linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">{stops(sun)}</linearGradient>
<clipPath id="sunclip"><circle cx="{w/2}" cy="{sun_cy}" r="{sun_r + 2}"/></clipPath></defs>
<rect width="{w}" height="{hz}" fill="url(#sky)"/>{stars}
<circle cx="{w/2}" cy="{sun_cy}" r="{sun_r}" fill="url(#sun)"/><g clip-path="url(#sunclip)">{"".join(cuts)}</g>
{sea}{glit}{foam}{sand}{boards}</svg>'''


def title(img, text, size, xy, fill, shadow, anchor="ls", spacing=0.08):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(BEBAS, size)
    x, y = xy
    # Bebas looks right with wide tracking, which PIL lacks: lay letters out by hand
    widths = [d.textlength(c, font=f) + size * spacing for c in text]
    total = sum(widths) - size * spacing
    if anchor[0] == "m":
        x -= total / 2
    for c, cw in zip(text, widths):
        if shadow:
            d.text((x + size * 0.04, y + size * 0.04), c, font=f, fill=shadow, anchor="l" + anchor[1])
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += cw


def logo_svg():
    s = 512
    cuts = "".join(f'<rect x="0" y="{y}" width="{s}" height="{g}" fill="url(#sky)"/>' for y, g in [(236, 8), (268, 13), (300, 18)])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">
<defs><clipPath id="c"><circle cx="256" cy="256" r="232"/></clipPath>
<linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{s}"><stop offset="0" stop-color="{SKY}"/><stop offset="1" stop-color="#FCE6B6"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE08A"/><stop offset=".6" stop-color="{ORANGE}"/><stop offset="1" stop-color="{CORAL}"/></linearGradient>
<clipPath id="sc"><circle cx="256" cy="250" r="129"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{s}" height="{s}" fill="url(#sky)"/>
<circle cx="256" cy="250" r="128" fill="url(#sun)"/><g clip-path="url(#sc)">{cuts}</g>
<path d="M0,330 C80,300 150,350 256,322 C360,294 430,346 512,318 L512,512 L0,512 Z" fill="{OCEAN}"/>
<path d="M0,380 C90,356 170,400 270,374 C370,348 440,396 512,372 L512,512 L0,512 Z" fill="{NAVY}"/>
<path d="M0,330 C80,300 150,350 256,322 C360,294 430,346 512,318" fill="none" stroke="{CREAM}" stroke-width="10" stroke-linecap="round"/>
<path d="M40,420 C120,404 190,432 280,414" fill="none" stroke="{SURF}" stroke-width="8" stroke-linecap="round"/></g>
<circle cx="256" cy="256" r="232" fill="none" stroke="{NAVY}" stroke-width="22"/>
<circle cx="256" cy="256" r="214" fill="none" stroke="{CREAM}" stroke-width="6"/></svg>'''


def save(img, *p, **kw):
    path = out(*p)
    (img.convert("RGB") if path.endswith(".jpg") else img).save(path, **kw)


def grade(img):
    """Faded Kodachrome: lift blacks, warm the mids, add grain."""
    img = img.convert("RGB")
    img = Image.blend(img, Image.new("RGB", img.size, "#F5E3C0"), 0.10)
    noise = Image.effect_noise(img.size, 18).convert("RGB")
    return Image.blend(img, noise, 0.04)


def fit(img, w, h, ytop=0.5):
    """Crop to w:h (keeping the vertical slice at ytop) and resize."""
    sw, sh = img.size
    if sw / sh > w / h:
        nw = int(sh * w / h)
        img = img.crop(((sw - nw) // 2, 0, (sw + nw) // 2, sh))
    else:
        nh = int(sw * h / w)
        top = int((sh - nh) * ytop)
        img = img.crop((0, top, sw, top + nh))
    return img.resize((w, h), Image.LANCZOS)


def panel_mock(bg, dark):
    """Theme thumbnail: wallpaper plus a floating panel, since there's no Plasma here to screenshot."""
    img = bg.copy().convert("RGBA")
    w, h = img.size
    ov = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(ov)
    ph, m = int(h * 0.055), int(h * 0.012)
    d.rounded_rectangle((m * 6, h - ph - m, w - m * 6, h - m), radius=ph // 3, fill=(19, 40, 58, 230) if dark else (251, 244, 228, 235))
    cy, r = h - m - ph // 2, int(ph * 0.3)
    logo = svg2img(logo_svg(), 2 * r + 8, 2 * r + 8)
    ov.alpha_composite(logo, (m * 6 + ph // 2 - r - 4, cy - r - 4))
    for i, c in enumerate([OCEAN, ORANGE, SURF, CORAL]):
        x = m * 6 + ph * 2 + i * ph
        d.rounded_rectangle((x - r, cy - r, x + r, cy + r), radius=r // 3, fill=c)
    # one open window
    d.rounded_rectangle((w * 0.05, h * 0.10, w * 0.38, h * 0.62), radius=12, fill=(19, 40, 58, 245) if dark else (251, 244, 228, 245))
    d.rounded_rectangle((w * 0.05, h * 0.10, w * 0.38, h * 0.145), radius=12, fill=(11, 29, 46, 255) if dark else (237, 215, 168, 255))
    return Image.alpha_composite(img, ov)


if __name__ == "__main__":
    # wallpapers: one package, day in images/, night in images_dark/ (Plasma picks by color scheme)
    day, night = svg2img(scene(False), 3840, 2160), svg2img(scene(True), 3840, 2160)
    for img, sub in [(day, "images"), (night, "images_dark")]:
        title(img, "ENDLESS SUMMER", 150, (180, 2000), NAVY if sub == "images" else CREAM, None)
        for w, h in [(3840, 2160), (1920, 1080)]:
            save(img.resize((w, h), Image.LANCZOS).convert("RGB"), "usr/share/wallpapers/EndlessSummer/contents", sub, f"{w}x{h}.png", optimize=True)
    save(day.resize((400, 225), Image.LANCZOS).convert("RGB"), "usr/share/wallpapers/EndlessSummer/contents/screenshot.png")

    # the reference photos as extra wallpapers
    photos = {"SurfCheck": ("Pasted image.png", 0.12), "TheWave": ("Pasted image (3).png", 0.5)}
    for name, (f, ytop) in photos.items():
        img = grade(fit(Image.open(os.path.join(HERE, "photos", f)), 1920, 1080, ytop))
        save(img, f"usr/share/wallpapers/EndlessSummer{name}/contents/images/1920x1080.jpg", quality=92)
        save(img.resize((400, 225), Image.LANCZOS), f"usr/share/wallpapers/EndlessSummer{name}/contents/screenshot.png")

    # logo
    svg = logo_svg()
    for theme in ["EndlessSummer", "EndlessSummerNight"]:
        for n in ["start-here-kde", "start-here", "distributor-logo"]:
            open(out("usr/share/icons", theme, "scalable/places", n + ".svg"), "w").write(svg)
    logo256 = svg2img(svg, 256, 256)
    save(logo256, "usr/share/endless-summer/logo.png")

    # plymouth: night art without text, plus logo+title on its own so the script can center it
    save(night.resize((1920, 1080), Image.LANCZOS).convert("RGB"), "usr/share/plymouth/themes/endless-summer/background.png")
    plogo = Image.new("RGBA", (720, 420))
    plogo.alpha_composite(svg2img(svg, 240, 240), (240, 0))
    title(plogo, "ENDLESS SUMMER", 110, (360, 380), CREAM, (11, 29, 46, 200), anchor="ms")
    save(plogo, "usr/share/plymouth/themes/endless-summer/logo.png")
    save(Image.new("RGBA", (4, 4), CREAM), "usr/share/plymouth/themes/endless-summer/bar.png")

    # ksplash: same art per variant, the logo is drawn by QML
    for pkg, bg in [("org.endlesssummer.desktop", day), ("org.endlesssummernight.desktop", night)]:
        base = f"usr/share/plasma/look-and-feel/{pkg}/contents"
        save(bg.resize((1920, 1080), Image.LANCZOS).convert("RGB"), base, "splash/images/background.jpg", quality=90)
        save(svg2img(svg, 512, 512), base, "splash/images/logo.png")
        mock = panel_mock(bg.resize((1920, 1080), Image.LANCZOS), "night" in pkg)
        save(mock, base, "previews/fullscreenpreview.jpg", quality=88)
        save(mock.resize((960, 540), Image.LANCZOS), base, "previews/preview.png")

    # sddm: The Wave photo, darkened at the bottom-centre where the login box sits
    sd = fit(Image.open(os.path.join(HERE, "photos", "Pasted image (3).png")), 1920, 1080)
    sd = grade(sd).convert("RGBA")
    shade = Image.new("L", (1920, 1080), 0)
    ImageDraw.Draw(shade).ellipse((560, 260, 1360, 1000), fill=110)
    sd = Image.composite(Image.new("RGBA", sd.size, (11, 29, 46, 255)), sd, shade.filter(ImageFilter.GaussianBlur(160)))
    save(sd, "usr/share/sddm/themes/endless-summer-sddm/background.jpg", quality=92)
    save(sd.resize((640, 360), Image.LANCZOS), "usr/share/sddm/themes/endless-summer-sddm/preview.png")

    # avatar: Chicken Joe
    joe = Image.open(os.path.join(HERE, "joe-frame.png")).convert("RGB")
    joe = joe.crop((470, 20, 1030, 580)).resize((256, 256), Image.LANCZOS)
    for p in ["etc/skel/.face", "etc/skel/.face.icon", "usr/share/sddm/themes/endless-summer-sddm/faces/.face.icon"]:
        save(joe, p, format="PNG")
    print("art written to", os.path.normpath(ROOT))
