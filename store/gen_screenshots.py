#!/usr/bin/env python3
"""Chrome Web Store 스크린샷 생성 (1280x800, 24-bit RGB PNG, no alpha)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 800
OUT = os.path.dirname(os.path.abspath(__file__))

# ---- 색상 ----
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


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diag_gradient(w, h, c1, c2):
    yy, xx = np.mgrid[0:h, 0:w]
    t = (xx + yy) / (w + h - 2)
    arr = np.empty((h, w, 3), np.uint8)
    for i in range(3):
        arr[..., i] = (c1[i] + (c2[i] - c1[i]) * t).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def shadow(size, box, r, blur=24, alpha=90):
    s = Image.new("RGBA", size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(s)
    ds.rounded_rectangle(box, radius=r, fill=(0, 0, 0, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur))


def text_center(d, cx, y, s, f, fill):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


def tri_down(d, cx, cy, s, fill):
    d.polygon([(cx - s, cy - s * 0.6), (cx + s, cy - s * 0.6), (cx, cy + s * 0.7)], fill=fill)


def kebab(d, cx, cy, fill):
    for dx in (-7, 0, 7):
        d.ellipse([cx + dx - 2, cy - 2, cx + dx + 2, cy + 2], fill=fill)


def draw_lock(d, cx, cy, s, color):
    """자물쇠 아이콘 (cx,cy = 중심)."""
    bw, bh = s, s * 0.78
    bx0, by0 = cx - bw / 2, cy - bh * 0.18
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=s * 0.16, fill=color)
    # 고리(shackle)
    sw = s * 0.62
    d.arc([cx - sw / 2, by0 - sw * 0.82, cx + sw / 2, by0 + sw * 0.4],
          start=180, end=360, fill=color, width=max(3, int(s * 0.11)))
    # 열쇠구멍
    kc = (DARK_BG)
    d.ellipse([cx - s * 0.09, cy + s * 0.04, cx + s * 0.09, cy + s * 0.22], fill=kc)


def brand_glyph(d, x, y, sz):
    """미니 브랜드 아이콘 (그라데이션 사각 + 흰 요약선)."""
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
        d.text((x, y), ln, font=f_h, fill=WHITE)
        y += 74
    y += 14
    for ln in wrap(d, sub, f_s, 520):
        d.text((x, y), ln, font=f_s, fill=(235, 235, 250))
        y += 40


# ---- 팝업 카드 (요약/번역 탭) ----
def card_popup(active, body_lines, length_label, btn_label, sel_checked,
               value_font=None, body_font=None):
    value_font = value_font or font(False, 15)
    body_font = body_font or font(False, 17)
    cw, ch = 480, 540
    cx, cy = 720, 130
    base.paste(shadow((W, H), [cx + 6, cy + 14, cx + cw, cy + ch], 26), (0, 0),
               shadow((W, H), [cx + 6, cy + 14, cx + cw, cy + ch], 26))
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 18, fill=DARK_BG)
    # 헤더
    brand_glyph(d, cx + 22, cy + 20, 30)
    d = ImageDraw.Draw(base)
    d.text((cx + 62, cy + 24), "Gist", font=font(True, 22), fill=FG)
    kebab(d, cx + cw - 36, cy + 36, MUTED)
    d.line([cx, cy + 70, cx + cw, cy + 70], fill=BORDER, width=1)
    # 탭
    tabs = ["Summarize", "Translate"]
    tw = cw / 2
    for i, t in enumerate(tabs):
        on = (t == active)
        col = ACCENT if on else MUTED
        text_center(d, cx + tw * i + tw / 2, cy + 86, t, font(on, 19), col)
        if on:
            cwid = d.textlength(t, font=font(True, 19))
            mid = cx + tw * i + tw / 2
            d.line([mid - cwid / 2, cy + 118, mid + cwid / 2, cy + 118], fill=ACCENT, width=3)
    d.line([cx, cy + 120, cx + cw, cy + 120], fill=BORDER, width=1)
    # 옵션 행 (드롭다운 + 체크박스)
    oy = cy + 150
    d.text((cx + 26, oy - 4), "Length" if active == "Summarize" else "Translate to",
           font=font(False, 14), fill=MUTED)
    rrect(d, [cx + 26, oy + 18, cx + 220, oy + 52], 8, fill=DARK_BG, outline=BORDER, width=1)
    d.text((cx + 38, oy + 26), length_label, font=value_font, fill=FG)
    tri_down(d, cx + 206, oy + 34, 5, MUTED)
    # 체크박스
    bx = cx + 250
    rrect(d, [bx, oy + 22, bx + 22, oy + 44], 5,
          fill=ACCENT if sel_checked else DARK_BG, outline=BORDER, width=1)
    if sel_checked:
        d.line([bx + 5, oy + 33, bx + 10, oy + 39], fill=WHITE, width=2)
        d.line([bx + 10, oy + 39, bx + 18, oy + 27], fill=WHITE, width=2)
    d.text((bx + 32, oy + 25), "Selection only", font=font(False, 15), fill=FG)
    # 기본 버튼
    by = oy + 74
    rrect(d, [cx + 26, by, cx + cw - 26, by + 48], 10, fill=ACCENT)
    text_center(d, cx + cw / 2, by + 13, btn_label, font(True, 18), WHITE)
    # 결과
    d.line([cx + 26, by + 80, cx + cw - 26, by + 80], fill=BORDER, width=1)
    ry = by + 100
    f_r = body_font
    for ln in body_lines:
        for wl in wrap(d, ln, f_r, cw - 56):
            d.text((cx + 26, ry), wl, font=f_r, fill=FG)
            ry += 28
        ry += 4


def screenshot_1():
    headline(dh, "Summarize any page in one click.",
             "Short, bulleted, or detailed — AI summaries while you read.")
    card_popup("Summarize", [
        "• Iran says the Strait of Hormuz will reopen after",
        "  the peace deal is signed in Switzerland.",
        "• All military operations end immediately.",
        "• The U.S. naval blockade will be lifted.",
        "• Tehran will verify compliance before signing.",
        "• Markets expect oil prices to ease.",
    ], "Medium (5 bullets)", "Summarize this page", False)


def screenshot_2():
    headline(dh, "Translate into 7 languages.",
             "Read the web in your language — selection or whole page.")
    card_popup("Translate", [
        "선택한 텍스트가 한국어로 즉시",
        "번역됩니다. 원문의 의미와 서식을",
        "그대로 유지하며, 결과는 실시간으로",
        "한 글자씩 표시됩니다.",
    ], "한국어", "Translate", True,
        value_font=kfont(15), body_font=kfont(17))


def screenshot_3():
    headline(dh, "Bring your own API key.",
             "OpenAI or Anthropic. No subscription, no markup.")
    # 설정 카드
    cw, ch = 480, 540
    cx, cy = 720, 130
    base.paste(shadow((W, H), [cx + 6, cy + 14, cx + cw, cy + ch], 26), (0, 0),
               shadow((W, H), [cx + 6, cy + 14, cx + cw, cy + ch], 26))
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 18, fill=DARK_BG)
    d.text((cx + 26, cy + 24), "Gist — Settings", font=font(True, 22), fill=FG)
    def field(label, value, y, accent=False):
        d.text((cx + 26, y), label, font=font(True, 15), fill=MUTED)
        rrect(d, [cx + 26, y + 24, cx + cw - 26, y + 62], 8,
              fill=PANEL if not accent else DARK_BG, outline=BORDER, width=1)
        d.text((cx + 38, y + 33), value, font=font(False, 16), fill=FG)
    field("AI provider", "OpenAI (GPT)", cy + 78)
    field("API key", "sk-•••••••••••••••••••••••••••", cy + 168)
    field("OpenAI model", "gpt-5.4-mini (fast & cheap, recommended)", cy + 258)
    rrect(d, [cx + 26, cy + 360, cx + 150, cy + 408], 9, fill=ACCENT)
    text_center(d, cx + 88, cy + 372, "Save", font(True, 17), WHITE)
    draw_lock(d, cx + 36, cy + 452, 22, MUTED)
    d.text((cx + 56, cy + 440), "Your key is stored only in this browser",
           font=font(False, 14), fill=MUTED)
    d.text((cx + 56, cy + 462), "and never sent to us.",
           font=font(False, 14), fill=MUTED)


def screenshot_4():
    headline(dh, "Right-click to summarize.",
             "Select any text, then summarize or translate it instantly.")
    # 가짜 페이지 + 컨텍스트 메뉴
    cx, cy, cw, ch = 700, 150, 500, 500
    d = ImageDraw.Draw(base)
    rrect(d, [cx, cy, cx + cw, cy + ch], 14, fill=(250, 250, 252))
    # 가짜 본문 라인
    ly = cy + 40
    for i in range(11):
        wf = 0.9 if i % 3 else 0.6
        hl = (i in (3, 4, 5))  # 선택 하이라이트
        if hl:
            d.rectangle([cx + 36, ly - 4, cx + 36 + (cw - 72) * wf, ly + 20], fill=(180, 205, 255))
        d.rounded_rectangle([cx + 36, ly, cx + 36 + (cw - 72) * wf, ly + 14], radius=7,
                            fill=(60, 66, 74) if hl else (205, 210, 218))
        ly += 34
    # 컨텍스트 메뉴
    mx, my, mw = cx + 150, cy + 150, 250
    base.paste(shadow((W, H), [mx, my, mx + mw, my + 104], 10), (0, 0),
               shadow((W, H), [mx, my, mx + mw, my + 104], 10))
    d = ImageDraw.Draw(base)
    rrect(d, [mx, my, mx + mw, my + 104], 10, fill=(255, 255, 255), outline=(210, 214, 220), width=1)
    d.text((mx + 18, my + 16), "Summarize selection", font=font(False, 16), fill=(30, 34, 40))
    d.line([mx + 10, my + 52, mx + mw - 10, my + 52], fill=(232, 234, 238), width=1)
    d.text((mx + 18, my + 66), "Translate selection", font=font(False, 16), fill=(30, 34, 40))


def screenshot_5():
    headline(dh, "Private by design.",
             "No server. Your key stays in your browser.")
    cx, cy, cw, ch = 760, 200, 400, 400
    base.paste(shadow((W, H), [cx, cy, cx + cw, cy + ch], 26), (0, 0),
               shadow((W, H), [cx, cy, cx + cw, cy + ch], 26))
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
