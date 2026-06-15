#!/usr/bin/env python3
"""프로모션 타일 생성: 작은(440x280), 마키(1400x560). 24-bit RGB PNG, no alpha."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))
C1 = (88, 80, 236)     # indigo
C2 = (192, 38, 211)    # fuchsia
WHITE = (255, 255, 255)

AR = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(b, s): return ImageFont.truetype(ARB if b else AR, s)


def diag_gradient(w, h, c1, c2):
    yy, xx = np.mgrid[0:h, 0:w]
    t = (xx + yy) / (w + h - 2)
    arr = np.empty((h, w, 3), np.uint8)
    for i in range(3):
        arr[..., i] = (c1[i] + (c2[i] - c1[i]) * t).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def text_w(d, s, f): return d.textlength(s, font=f)


def glyph(base, cx, cy, sz):
    """흰 테두리를 두른 그라데이션 로고 타일 (요약 라인 포함)."""
    # 소프트 섀도
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [cx - sz/2, cy - sz/2 + sz*0.06, cx + sz/2, cy + sz/2 + sz*0.06],
        radius=int(sz*0.24), fill=(0, 0, 0, 110))
    base.paste(sh.filter(ImageFilter.GaussianBlur(sz*0.06)), (0, 0),
               sh.filter(ImageFilter.GaussianBlur(sz*0.06)))
    # 타일(반대 방향 그라데이션으로 배경과 분리)
    g = diag_gradient(int(sz), int(sz), C2, C1)
    m = Image.new("L", (int(sz), int(sz)), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, int(sz)-1, int(sz)-1], radius=int(sz*0.24), fill=255)
    base.paste(g, (int(cx - sz/2), int(cy - sz/2)), m)
    d = ImageDraw.Draw(base)
    # 흰 테두리
    d.rounded_rectangle([cx - sz/2, cy - sz/2, cx + sz/2, cy + sz/2],
                        radius=int(sz*0.24), outline=(255, 255, 255, 235), width=max(2, int(sz*0.035)))
    # 요약 라인
    x0, y0 = cx - sz/2, cy - sz/2
    pad = sz*0.27
    lh = max(2, int(sz*0.085))
    gap = (sz - 2*pad - 3*lh) / 2
    yy = y0 + pad
    for wf in (0.62, 0.44, 0.28):
        d.rounded_rectangle([x0+pad, yy, x0+pad+(sz-2*pad)*wf, yy+lh], radius=lh/2, fill=WHITE)
        yy += lh + gap


def shadow_text(d, x, y, s, f, fill=WHITE, sx=2, sy=2):
    d.text((x+sx, y+sy), s, font=f, fill=(0, 0, 0, 90))
    d.text((x, y), s, font=f, fill=fill)


# ---- 작은 타일 440x280 : 로고 + 워드마크 + 태그라인 (중앙) ----
def small_tile():
    W, H = 440, 280
    base = diag_gradient(W, H, C1, C2)
    d = ImageDraw.Draw(base)
    glyph(base, W/2, 92, 96)
    d = ImageDraw.Draw(base)
    fw = font(True, 52)
    word = "Gist"
    shadow_text(d, (W - text_w(d, word, fw))/2, 156, word, fw)
    ft = font(False, 20)
    tag = "AI Summarizer"
    d.text(((W - text_w(d, tag, ft))/2, 220), tag, font=ft, fill=(240, 235, 252))
    base.convert("RGB").save(os.path.join(OUT, "promo-small.png"), "PNG")
    print("saved promo-small.png", (W, H))


# ---- 마키 타일 1400x560 : 좌측 로고 락업 + 헤드라인/태그라인 ----
def marquee_tile():
    W, H = 1400, 560
    base = diag_gradient(W, H, C1, C2)
    # 로고 + 워드마크 가로 락업, 좌측 정렬
    gx = 150
    glyph(base, gx + 95, 230, 190)
    d = ImageDraw.Draw(base)
    fw = font(True, 150)
    shadow_text(d, gx + 220, 150, "Gist", fw, sx=3, sy=3)
    # 태그라인
    ft = font(False, 44)
    shadow_text(d, gx + 6, 350, "Summarize any web page with AI", ft, fill=(244, 240, 253), sx=2, sy=2)
    ft2 = font(False, 30)
    d.text((gx + 6, 412), "Then translate the summary — using your own API key.",
           font=ft2, fill=(226, 220, 245))
    base.convert("RGB").save(os.path.join(OUT, "promo-marquee.png"), "PNG")
    print("saved promo-marquee.png", (W, H))


small_tile()
marquee_tile()
print("done")
