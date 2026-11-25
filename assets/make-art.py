#!/usr/bin/env python3
"""Render every image in the theme into ../root/.

Needs: cairosvg, pillow (pip, in a venv). Run: python make-art.py
Inputs in this folder: photos/*.png (reference photos), joe-frame.png (avatar source),
fonts/BebasNeue-Regular.ttf, photos/surf/* (wallpaper pool).
"""
import io, os
import cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "root")
BEBAS = os.path.join(HERE, "fonts", "BebasNeue-Regular.ttf")

# palette: Kodachrome sea and sky, sand, and the Travoltas-cover red
NAVY, OCEAN, SURF, SKY = "#0E2F44", "#1B7FA6", "#2BB3C9", "#9FD8E8"
SAND, CREAM, CORAL, ORANGE, SUN = "#EDD7A8", "#FBF4E4", "#E0472F", "#F28C28", "#F9C74F"

# Surf photos for the wallpaper pool, in photos/surf/: (file, crop ytop, pre-crop box or None)
PHOTOS = [
    ("surfback1.jpg", 0.5, None), ("surfaback2.png", 0.5, None), ("surfback3.jpg", 0.5, None),  # surfback3 is AVIF despite the name
    ("surfback4.jpg", 0.5, None), ("surfback5.jpeg", 0.5, None), ("surfback6.jpg", 0.5, None),
]


def out(*p):
    path = os.path.join(ROOT, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def svg2img(svg, w, h):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert("RGBA")


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


def fit16x9(img, ytop=0.5):
    """Crop to 16:9 at the photo's own resolution, capped at 4K."""
    sw, sh = img.size
    w = min(3840, sw, int(sh * 16 / 9)) // 16 * 16
    return fit(img, w, w * 9 // 16, ytop)


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
    # wallpaper pool: a random one is set at every login (see usr/libexec/endless-summer-first-login)
    pool = {}
    for i, (name, ytop, box) in enumerate(PHOTOS, 1):
        img = Image.open(os.path.join(HERE, "photos", "surf", name))
        pool[name] = grade(fit16x9(img.crop(box) if box else img, ytop))
        save(pool[name], f"usr/share/endless-summer/wallpapers/{i:02}.jpg", quality=92)

    # the default wallpaper package (before the first login picks one): day in images/, night in images_dark/
    day, night = pool["surfback1.jpg"], pool["surfback5.jpeg"]
    for img, sub in [(day, "images"), (night, "images_dark")]:
        save(fit(img, 1920, 1080), "usr/share/wallpapers/EndlessSummer/contents", sub, "1920x1080.jpg", quality=90)
    save(fit(day, 400, 225), "usr/share/wallpapers/EndlessSummer/contents/screenshot.png")

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

    # plymouth: a dark photo, dimmed further under the logo, plus logo+title on its own so the script can center it
    boot = fit(pool["surfback5.jpeg"], 1920, 1080)
    save(Image.blend(boot, Image.new("RGB", boot.size, NAVY), 0.35), "usr/share/plymouth/themes/endless-summer/background.png")
    plogo = Image.new("RGBA", (720, 420))
    plogo.alpha_composite(svg2img(svg, 240, 240), (240, 0))
    title(plogo, "ENDLESS SUMMER", 110, (360, 380), CREAM, (11, 29, 46, 200), anchor="ms")
    save(plogo, "usr/share/plymouth/themes/endless-summer/logo.png")
    save(Image.new("RGBA", (4, 4), CREAM), "usr/share/plymouth/themes/endless-summer/bar.png")

    # ksplash: same art per variant, the logo is drawn by QML
    for pkg, bg in [("org.endlesssummer.desktop", day), ("org.endlesssummernight.desktop", night)]:
        base = f"usr/share/plasma/look-and-feel/{pkg}/contents"
        bg = fit(bg, 1920, 1080)
        save(bg, base, "splash/images/background.jpg", quality=90)
        save(svg2img(svg, 512, 512), base, "splash/images/logo.png")
        mock = panel_mock(bg, "night" in pkg)
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
