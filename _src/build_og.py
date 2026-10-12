#!/usr/bin/env python3
"""Картинка превью ссылки (Open Graph) 1200x630 для мессенджеров: assets/og-easyestate-2.jpg.

Запуск: python3 _src/build_og.py (нужны Pillow и шрифт Liberation Sans Bold — аналог Arial по брендбуку).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
W, H = 1200, 630
BG, FG, MUTED, BEZEL = (44, 72, 38), (255, 255, 255), (207, 229, 197), (27, 36, 25)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

logo = Image.open(ROOT / "_src/og/logo_mark_light.png").convert("RGBA").resize((72, 72), Image.LANCZOS)
img.paste(logo, (64, 64), logo)
d.text((152, 84), "EASY ESTATE", font=ImageFont.truetype(FONT_B, 34), fill=FG)

f_h = ImageFont.truetype(FONT_B, 64)
y = 220
for line in ["Личный помощник", "риелтора"]:
    d.text((64, y), line, font=f_h, fill=FG)
    y += 70
d.text((64, y + 24), "A personal assistant for real estate agents", font=ImageFont.truetype(FONT_R, 26), fill=MUTED)
d.text((64, H - 70), "easyestate.solutions", font=ImageFont.truetype(FONT_B, 26), fill=MUTED)

# Телефон справа: настоящий экран карточки объекта, верх экрана.
shot = Image.open(ROOT / "assets/screens/07_property_card.webp").convert("RGB")
pw = 300
ph = round(shot.height * pw / shot.width)
shot = shot.resize((pw, ph), Image.LANCZOS)
x0, y0, bez = 800, 70, 10
mask = Image.new("L", (pw + 2 * bez, ph + 2 * bez), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw + 2 * bez - 1, ph + 2 * bez - 1], radius=40, fill=255)
frame = Image.new("RGB", mask.size, BEZEL)
inner = Image.new("L", (pw, ph), 0)
ImageDraw.Draw(inner).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=30, fill=255)
frame.paste(shot, (bez, bez), inner)
img.paste(frame, (x0, y0), mask)

out = ROOT / "assets/og-easyestate-2.jpg"
img.save(out, "JPEG", quality=86, optimize=True, progressive=True)
print(out, out.stat().st_size)
