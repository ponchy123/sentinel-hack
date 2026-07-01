"""Generate Sentinel logo using PIL."""
from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background circle
cx, cy, r = SIZE//2, SIZE//2, 230
for i in range(r, 0, -1):
    ratio = i / r
    red = int(20 + (99 - 20) * (1 - ratio))
    green = int(20 + (102 - 20) * (1 - ratio))
    blue = int(32 + (241 - 32) * (1 - ratio))
    draw.ellipse([(cx-i, cy-i), (cx+i, cy+i)], fill=(red, green, blue, 255))

# Shield shape
shield_pts = [
    (cx, cy - 140),
    (cx + 120, cy - 80),
    (cx + 110, cy + 40),
    (cx, cy + 140),
    (cx - 110, cy + 40),
    (cx - 120, cy - 80),
]
draw.polygon(shield_pts, fill=(15, 15, 25, 220), outline=(129, 140, 248, 255))

# Inner neural network lines
nodes = [
    (cx, cy - 80),
    (cx - 60, cy - 20),
    (cx + 60, cy - 20),
    (cx - 40, cy + 50),
    (cx + 40, cy + 50),
    (cx, cy + 90),
]
for i, (x1, y1) in enumerate(nodes):
    for j, (x2, y2) in enumerate(nodes):
        if i < j and abs(i - j) <= 2:
            draw.line([(x1, y1), (x2, y2)], fill=(99, 102, 241, 150), width=2)

# Draw nodes
for x, y in nodes:
    draw.ellipse([(x-8, y-8), (x+8, y+8)], fill=(129, 140, 248, 255), outline=(255, 255, 255, 200))

# Center eye/watch icon
eye_cx, eye_cy = cx, cy + 10
draw.ellipse([(eye_cx-25, eye_cy-15), (eye_cx+25, eye_cy+15)], outline=(34, 197, 94, 255), width=3)
draw.ellipse([(eye_cx-10, eye_cy-10), (eye_cx+10, eye_cy+10)], fill=(34, 197, 94, 255))

# Text
try:
    font_large = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Save main logo
logo_path = r"D:\lifespace\lifebook\temp3\sentinel-hack\demo\logo.png"
img.save(logo_path, "PNG")
print(f"Logo saved: {logo_path}")

# Create icon version (smaller, no text)
icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
icon_draw = ImageDraw.Draw(icon)
icx, icy, ir = 64, 64, 58
for i in range(ir, 0, -1):
    ratio = i / ir
    red = int(20 + (99 - 20) * (1 - ratio))
    green = int(20 + (102 - 20) * (1 - ratio))
    blue = int(32 + (241 - 32) * (1 - ratio))
    icon_draw.ellipse([(icx-i, icy-i), (icx+i, icy+i)], fill=(red, green, blue, 255))

shield_pts_icon = [
    (icx, icy - 35),
    (icx + 30, icy - 18),
    (icx + 28, icy + 12),
    (icx, icy + 38),
    (icx - 28, icy + 12),
    (icx - 30, icy - 18),
]
icon_draw.polygon(shield_pts_icon, fill=(15, 15, 25, 220), outline=(129, 140, 248, 255))
icon_draw.ellipse([(icx-6, icy-6), (icx+6, icy+6)], fill=(34, 197, 94, 255))

icon_path = r"D:\lifespace\lifebook\temp3\sentinel-hack\demo\logo_icon.png"
icon.save(icon_path, "PNG")
print(f"Icon saved: {icon_path}")
