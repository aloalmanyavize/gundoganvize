#!/usr/bin/env python3
"""Build branded PNG for link-sharing preview, 1200x630."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path("assets/social-share.png")
im = Image.new("RGB", (1200, 630), "#0b1e3c")
d = ImageDraw.Draw(im)
d.rounded_rectangle((52, 48, 1148, 582), radius=32, fill="#102a4f", outline="#346b9e", width=3)
d.rounded_rectangle((90, 94, 270, 103), radius=4, fill="#48d3b0")
d.ellipse((920, 105, 1090, 275), outline="#348ac3", width=7)
d.ellipse((959, 144, 1051, 236), outline="#48d3b0", width=5)
d.line([(1008, 145), (1008, 235)], fill="#48d3b0", width=4)
d.rounded_rectangle((930, 392, 1093, 506), radius=20, outline="#348ac3", width=5)
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
normal = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def label(x, y, value, size, color, face=font):
    d.text((x, y), value, font=ImageFont.truetype(face, size), fill=color)
label(95, 143, "GÜNDOĞAN", 82, "#ffffff")
label(95, 248, "VİZE", 101, "#48d3b0")
d.line([(96, 399), (865, 399)], fill="#3977a9", width=3)
label(98, 422, "Schengen vize danışmanlığı", 38, "#ffffff")
label(99, 491, "Randevu  •  Evrak  •  Başvuru desteği", 27, "#afcce4", normal)
out.parent.mkdir(parents=True, exist_ok=True)
im.save(out, "PNG", optimize=True)
assert Image.open(out).size == (1200, 630)
print("Created", out, out.stat().st_size, "bytes")
