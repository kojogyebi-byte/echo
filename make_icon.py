#!/usr/bin/env python3
"""Generate the DeHowl app icon: dark rounded square, frequency-response
curve with a deep narrow notch, red accent at the notch."""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 2048  # supersample, downscale to 1024 at the end

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# --- background: vertical gradient inside a rounded square ---
grad = Image.new("RGBA", (S, S))
top, bottom = (26, 32, 48), (12, 15, 24)
px = grad.load()
for y in range(S):
    t = y / (S - 1)
    r = int(top[0] + (bottom[0] - top[0]) * t)
    g = int(top[1] + (bottom[1] - top[1]) * t)
    b = int(top[2] + (bottom[2] - top[2]) * t)
    for x in range(S):
        px[x, y] = (r, g, b, 255)

mask = Image.new("L", (S, S), 0)
md = ImageDraw.Draw(mask)
margin = int(S * 0.04)
radius = int(S * 0.22)
md.rounded_rectangle([margin, margin, S - margin, S - margin], radius=radius, fill=255)
img.paste(grad, (0, 0), mask)

d = ImageDraw.Draw(img)

# --- subtle grid lines ---
grid = (255, 255, 255, 14)
for i in range(1, 5):
    y = margin + (S - 2 * margin) * i / 5
    d.line([(margin + 60, y), (S - margin - 60, y)], fill=grid, width=6)

# --- frequency-response curve with a deep notch ---
cx = S * 0.5            # notch centre x
base_y = S * 0.40       # flat response line
depth = S * 0.34        # notch depth
sigma = S * 0.045       # notch width

pts = []
x0, x1 = margin + int(S * 0.06), S - margin - int(S * 0.06)
for x in range(x0, x1, 4):
    wiggle = math.sin(x / S * 9.0) * S * 0.006
    dip = depth * math.exp(-((x - cx) ** 2) / (2 * sigma ** 2))
    pts.append((x, base_y + wiggle + dip))

# red glow under the notch
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.line(pts, fill=(229, 72, 77, 200), width=64, joint="curve")
glow = glow.filter(ImageFilter.GaussianBlur(48))
img.alpha_composite(glow)

# red vertical marker at the notch frequency
d.line([(cx, base_y + depth + S * 0.02), (cx, S - margin - int(S * 0.10))],
       fill=(229, 72, 77, 255), width=20)
dot_r = 36
d.ellipse([cx - dot_r, base_y + depth - dot_r, cx + dot_r, base_y + depth + dot_r],
          fill=(229, 72, 77, 255))

# main white curve on top (overlapping discs = perfectly smooth stroke)
r = 22
for (x, y) in pts:
    d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 244, 252, 255))

img = img.resize((1024, 1024), Image.LANCZOS)
img.save("Assets/icon.png")
img.resize((512, 512), Image.LANCZOS).save("Assets/icon_small.png")
print("icons written")
