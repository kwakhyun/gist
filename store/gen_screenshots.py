#!/usr/bin/env python3
"""Chrome Web Store 스크린샷 생성 (1280x800, 24-bit RGB PNG, no alpha)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 800
OUT = os.path.dirname(os.path.abspath(__file__))

C1 = (88, 80, 236)     # indigo
C2 = (192, 38, 211)    # fuchsia
DARK_BG = (31, 35, 40)
FG = (240, 243, 246)
MUTED = (184, 192, 204)
BORDER = (74, 82, 92)
ACCENT = (88, 155, 255)
PANEL = (45, 51, 59)
WHITE = (255, 255, 255)

AR = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
KO = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
def font(b, s): return ImageFont.truetype(ARB if b else AR, s)
def kfont(s): return ImageFont.truetype(KO, s)


def diag_gradient(w, h, c1, c2):
    yy, xx = np.mgrid[0:h, 0:w]
    t = (xx + yy) / (w + h - 2)
    arr = np.empty((h, w, 3), np.uint8)
    for i in range(3):
        arr[..., i] = (c1[i] + (c2[i] - c1[i]) * t).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def shadow_paste(box, r, blur=24, alpha=90):
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle(box, radius=r, fill=(0, 0, 0, alpha))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    base.paste(s, (0, 0), s)


def text_center(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def tri_down(d, cx, cy, s, fill):
    d.polygon([(cx - s, cy - s * 0.6), (cx + s, cy - s * 0.6), (cx, cy + s * 0.7)], fill=fill)


def kebab(d, cx, cy, fill):
    for dx in (-7, 0, 7):
        d.ellipse([cx + dx - 2, cy - 2, cx + dx + 2, cy + 2], fill=fill)


def draw_lock(d, cx, cy, s, color):
    bw, bh = s, s * 0.78
    bx0, by0 = cx - bw / 2, cy - bh * 0.18
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=s * 0.16, fill=color)
    sw = s * 0.62
    d.arc([cx - sw / 2, by0 - sw * 0.82, cx + sw / 2, by0 + sw * 0.4],
          start=180, end=360, fill=color, width=max(3, int(s * 0.11)))
    d.ellipse([cx - s * 0.09, cy + s * 0.04, cx + s * 0.09, cy + s * 0.22], fill=DARK_BG)


def brand_glyph(d, x, y, sz):
    g = diag_gradient(sz, sz, C1, C2).convert("RGBA")
    m = Image.new("L", (sz, sz), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, sz - 1, sz - 1], radius=int(sz * 0.26), fill=255)
    base.paste(g, (x, y), m)
    pad = sz * 0.28
    lh = max(2, int(sz * 0.085))
    gap = (sz - 2 * pad - 3 * lh) / 2
    yy = y + pad
    for wf in (0.66, 0.46, 0.30):
        d.rectangle([x + pad, yy, x + pad + (sz - 2 * pad) * wf, yy + lh], fill=WHITE)
        yy += lh + gap


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def headline(d, title, sub):
    f_h, f_s = font(True, 60), font(False, 28)
    x, y = 90, 250
    for ln in wrap(d, title, f_h, 520):
        d.text((x, y), ln, font=f_h, fill=WHITE); y += 74
    y += 14
    for ln in wrap(d, sub, f_s, 520):
        d.text((x, y), ln, font=f_s, fill=(235, 235, 250)); y += 40


def ghost_btn(d, x, y, label, f, accent=False):
    w = d.textlength(label, font=f) + 24
    rrect(d, [x, y, x + w, y + 32], 7,
          fill=ACCENT if accent else PANEL, outline=None if accent else BORDER, width=1)
    d.text((x + 12, y + 7), label, font=f, fill=WHITE if accent else FG)
    return w


def lang_pill(d, x, y, label, f):
    w = d.textlength(label, font=f) + 34
    rrect(d, [x, y, x + w, y + 32], 7, fill=DARK_BG, outline=BORDER, width=1)
    d.text((x + 11, y + 7), label, font=f, fill=FG)
    tri_down(d, x + w - 14, y + 16, 4, MUTED)
    return w


# ---- 단일 요약 카드 (탭 없음) ----
def card_main(result_lines, result_font=None, translated=False):
    result_font = result_font or font(False, 17)
    cw, ch = 480, 540
    cx, cy = 720, 130
    shadow_paste([cx + 6, cy + 14, cx + cw, cy + ch], 26)
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 18, fill=DARK_BG)
    # 헤더
    brand_glyph(d, cx + 22, cy + 20, 30)
    d = ImageDraw.Draw(base)
    d.text((cx + 62, cy + 24), "Gist", font=font(True, 22), fill=FG)
    kebab(d, cx + cw - 36, cy + 36, MUTED)
    d.line([cx, cy + 70, cx + cw, cy + 70], fill=BORDER, width=1)
    # 옵션 행
    oy = cy + 96
    d.text((cx + 26, oy - 4), "Length", font=font(False, 14), fill=MUTED)
    rrect(d, [cx + 26, oy + 18, cx + 220, oy + 52], 8, fill=DARK_BG, outline=BORDER, width=1)
    d.text((cx + 38, oy + 26), "Medium (5 bullets)", font=font(False, 15), fill=FG)
    tri_down(d, cx + 206, oy + 34, 5, MUTED)
    bx = cx + 250
    rrect(d, [bx, oy + 22, bx + 22, oy + 44], 5, fill=DARK_BG, outline=BORDER, width=1)
    d.text((bx + 32, oy + 25), "Selection only", font=font(False, 15), fill=FG)
    # 요약 버튼
    by = oy + 74
    rrect(d, [cx + 26, by, cx + cw - 26, by + 48], 10, fill=ACCENT)
    text_center(d, cx + cw / 2, by + 13, "Summarize this page", font(True, 18), WHITE)
    # 결과
    d.line([cx + 26, by + 78, cx + cw - 26, by + 78], fill=BORDER, width=1)
    ry = by + 98
    for ln in result_lines:
        for wl in wrap(d, ln, result_font, cw - 56):
            d.text((cx + 26, ry), wl, font=result_font, fill=FG); ry += 27
        ry += 3
    # 결과 액션 바 (하단)
    ay = cy + ch - 56
    ghost_btn(d, cx + 26, ay, "Copy", font(False, 13))
    x = cx + 122
    x += lang_pill(d, x, ay, "한국어", kfont(14)) + 8
    x += ghost_btn(d, x, ay, "Translate", font(False, 13), accent=translated) + 8
    if translated:
        ghost_btn(d, x, ay, "Original", font(False, 13))


def screenshot_1():
    headline(dh, "Summarize any page in one click.",
             "Short, bulleted, or detailed — AI summaries while you read.")
    card_main([
        "• Iran says the Strait of Hormuz will reopen",
        "  after the peace deal is signed in Switzerland.",
        "• All military operations end immediately.",
        "• The U.S. naval blockade will be lifted.",
        "• Tehran will verify compliance before signing.",
    ])


def screenshot_2():
    headline(dh, "Translate the summary.",
             "Turn any summary into your language — then back to the original.")
    card_main([
        "• 이란은 스위스에서 평화 협정이 서명된 후",
        "  호르무즈 해협을 재개방한다고 밝혔습니다.",
        "• 모든 군사 작전은 즉시 종료됩니다.",
        "• 미국의 해상 봉쇄가 해제됩니다.",
        "• 서명 전 이행 여부를 검증합니다.",
    ], result_font=kfont(16), translated=True)


def screenshot_3():
    headline(dh, "Bring your own API key.",
             "OpenAI or Anthropic. No subscription, no markup.")
    cw, ch = 480, 540
    cx, cy = 720, 130
    shadow_paste([cx + 6, cy + 14, cx + cw, cy + ch], 26)
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 18, fill=DARK_BG)
    d.text((cx + 26, cy + 24), "Gist — Settings", font=font(True, 22), fill=FG)
    def field(label, value, y):
        d.text((cx + 26, y), label, font=font(True, 15), fill=MUTED)
        rrect(d, [cx + 26, y + 24, cx + cw - 26, y + 62], 8, fill=PANEL, outline=BORDER, width=1)
        d.text((cx + 38, y + 33), value, font=font(False, 16), fill=FG)
    field("AI provider", "OpenAI (GPT)", cy + 78)
    field("API key", "sk-•••••••••••••••••••••••••••", cy + 168)
    field("OpenAI model", "gpt-5.4-mini (fast & cheap, recommended)", cy + 258)
    rrect(d, [cx + 26, cy + 360, cx + 150, cy + 408], 9, fill=ACCENT)
    text_center(d, cx + 88, cy + 372, "Save", font(True, 17), WHITE)
    draw_lock(d, cx + 36, cy + 452, 22, MUTED)
    d.text((cx + 56, cy + 440), "Your key is stored only in this browser", font=font(False, 14), fill=MUTED)
    d.text((cx + 56, cy + 462), "and never sent to us.", font=font(False, 14), fill=MUTED)


def screenshot_4():
    headline(dh, "Right-click to summarize.",
             "Summarize the whole page, or just the text you select.")
    cx, cy, cw, ch = 700, 150, 500, 500
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 14, fill=(250, 250, 252))
    ly = cy + 40
    for i in range(11):
        wf = 0.9 if i % 3 else 0.6
        hl = (i in (3, 4, 5))
        if hl:
            d.rectangle([cx + 36, ly - 4, cx + 36 + (cw - 72) * wf, ly + 20], fill=(180, 205, 255))
        d.rounded_rectangle([cx + 36, ly, cx + 36 + (cw - 72) * wf, ly + 14], radius=7,
                            fill=(60, 66, 74) if hl else (205, 210, 218))
        ly += 34
    # 컨텍스트 메뉴 (요약 단일 항목)
    mx, my, mw = cx + 150, cy + 150, 230
    shadow_paste([mx, my, mx + mw, my + 50], 10)
    d = ImageDraw.Draw(base)
    rrect(d, [mx, my, mx + mw, my + 50], 10, fill=(255, 255, 255), outline=(210, 214, 220), width=1)
    brand_glyph(d, mx + 14, my + 14, 22)
    d = ImageDraw.Draw(base)
    d.text((mx + 46, my + 16), "Summarize with Gist", font=font(False, 16), fill=(30, 34, 40))


def screenshot_5():
    headline(dh, "Private by design.",
             "No server. Your key stays in your browser.")
    cx, cy, cw, ch = 760, 200, 400, 400
    shadow_paste([cx, cy, cx + cw, cy + ch], 26)
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 18, fill=DARK_BG)
    draw_lock(d, cx + cw / 2, cy + 90, 96, FG)
    pts = ["Key stored only in your browser",
           "Requests go straight to the AI",
           "No tracking, no data collection",
           "Runs only when you click"]
    yy = cy + 170
    for p in pts:
        d.ellipse([cx + 40, yy + 8, cx + 50, yy + 18], fill=ACCENT)
        d.text((cx + 64, yy), p, font=font(False, 17), fill=FG)
        yy += 46


SCREENS = [screenshot_1, screenshot_2, screenshot_3, screenshot_4, screenshot_5]
for i, fn in enumerate(SCREENS, 1):
    base = diag_gradient(W, H, C1, C2).convert("RGBA")
    dh = ImageDraw.Draw(base)
    globals()["base"] = base
    fn()
    base.convert("RGB").save(os.path.join(OUT, f"screenshot-{i}.png"), "PNG")
    print(f"saved screenshot-{i}.png")
print("done")
