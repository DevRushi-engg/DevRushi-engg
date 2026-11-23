#!/usr/bin/env python3
"""
Render the profile README's cards as animated SVGs into cards/.

Design: Royal Maroon and White Aesthetic
Palette: Warm Ivory Paper (#fdfbf7), Royal Maroon (#800020), Imperial Gold (#c59b27),
Deep Crimson (#a82038), Deep Maroon Ink (#4a0b16), Rosewood Slate (#753b47).
Typography: Instrument Serif, Geist, Geist Mono.

Live numbers are derived from data/contributions.json (fetch_contributions.py).
Run daily by .github/workflows/update-profile-art.yml.
"""
import base64
import datetime
import json
import os
import re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
PORTRAIT = os.path.join(ROOT, "rushi-ascii.svg")

# ---- Brand Color Tokens (Royal Maroon & White) -------------------------------
PAPER = "#fdfbf7"         # Warm royal ivory paper
PAPER_DEEP = "#f3ebe6"    # Cream paper accent
INK = "#4a0b16"           # Rich deep royal maroon ink
INK_SOFT = "#6b202d"      # Subtle dark wine
MUTED = "#8e5562"         # Muted rosewood slate
RULE = "#e2d3cc"          # Subtle cream-maroon border/divider
MAROON = "#800020"        # Royal Maroon
GOLD = "#c59b27"          # Imperial Gold
CRIMSON = "#a82038"       # Deep Ruby / Crimson
W = 880                   # Full card width for GitHub README

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
@keyframes rowtype{0%{opacity:0;transform:translateX(-14px)}60%{opacity:.9}100%{opacity:1;transform:none}}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
.rt{opacity:0;animation:rowtype .4s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro,.rg,.rt{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}}
"""


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        path = os.path.join(FONTS, fn)
        if os.path.exists(path):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            out.append(
                f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                f"src:url(data:font/woff;base64,{b64}) format('woff')}}"
            )
    return "".join(out)


GAP = 12
BOTTOM = 12
COL = W / 3


def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=BOTTOM):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    if os.environ.get("STATIC"):
        css += ".r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f"<style>{css}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines)
    )


# ---- 1 · Hero Card -----------------------------------------------------------
def hero():
    h = 420
    portrait = []
    if os.path.exists(PORTRAIT):
        src = open(PORTRAIT).read()
        rows = re.findall(r'<text xml:space="preserve"[^>]*\by="([\d.]+)"[^>]*>(.*?)</text>', src, re.S)
        for i, (y, txt) in enumerate(rows):
            portrait.append(
                f'<text class="rt" style="animation-delay:{0.25 + i * 0.026:.3f}s" '
                f'xml:space="preserve" x="20" y="{y}" fill="url(#portrait-grad)" font-size="8.8" font-weight="700" '
                f'textLength="800" lengthAdjust="spacing">{txt}</text>'
            )

    s = 0.41
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{INK}"/>
    <stop offset=".42" stop-color="{INK}"/>
    <stop offset=".5" stop-color="{GOLD}"/>
    <stop offset=".58" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0"
      keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="portrait-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#140205"/>
    <stop offset="30%" stop-color="#2d030b"/>
    <stop offset="70%" stop-color="#4d0613"/>
    <stop offset="100%" stop-color="#1c0206"/>
  </linearGradient>
  <clipPath id="portrait-clip">
    <rect x="0" y="0" width="840" height="840" rx="12"/>
  </clipPath>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}" stroke="{RULE}" stroke-width="1"/>
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{MAROON}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">FINAL-YEAR AI &amp; DATA SCIENCE ENGINEER</text>
</g>
<text class="r" {d(0.15)} x="44" y="190" font-family="{SERIF}" font-size="108" letter-spacing="-2.5" fill="{INK}">Rushikesh</text>
<text class="r" {d(0.3)} x="44" y="290" font-family="{SERIF}" font-style="italic" font-size="108" letter-spacing="-2.5" fill="url(#shine)">Gurav</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 338, ["Engineer working with AI agents, Cloud, and DevOps."], 27, f'font-family="{SANS}" font-size="18" fill="{INK_SOFT}"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" fill="{INK}">linkedin.com/in/rushikesh-gurav</text>
  <text class="nu" x="305" y="396" font-family="{MONO}" font-size="13" fill="{MAROON}">&#8599;</text>
</g>
<g transform="translate(520 42) scale({s}) translate(-20 -35)" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <g clip-path="url(#portrait-clip)">
    {''.join(portrait)}
  </g>
</g>
"""
    svg_content = svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                      "Rushikesh Gurav. Engineer working with AI agents, Cloud, and DevOps.")
    write("hero.svg", svg_content)
    write("hero-card.svg", svg_content)
    write("hero-header.svg", svg_content)


# ---- 2 · World Metric Tiles ---------------------------------------------------
TILE_W, TILE_H = 880 / 3 - 8, 210


def count_up(num, word, x, y, attrs, begin, dur=1.1, frames=18):
    m = re.match(r"^([\d.]+)(.*)", num)
    if not m:
        tail = f' <tspan font-style="italic" font-size="0.65em">{escape(word)}</tspan>' if word else ""
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)}{tail}</text>'

    val, suf = float(m.group(1)), m.group(2)
    dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    tail = f' <tspan font-style="italic" font-size="0.65em">{escape(word)}</tspan>' if word else ""
    if os.environ.get("STATIC"):
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)}{tail}</text>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = num if i == frames else f"{val * e:.{dec}f}{suf}"
        on = begin + dur * i / frames
        off = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out.append(f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}'
                   f'<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>')
    return "".join(out)


def tile(name, label, color, on, num, word, blurb, delay, pos, font_size=42):
    lines = wrap(blurb, 34)
    blurb_svg = "".join(
        f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="24" y="{150 + i * 20}" font-family="{SANS}" '
        f'font-size="14" fill="{on}" opacity=".92">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    body = f"""
<defs>
  <clipPath id="card-{name}"><rect width="{TILE_W}" height="{TILE_H}" rx="14"/></clipPath>
  <clipPath id="slot-{name}"><rect x="0" y="60" width="{TILE_W}" height="64"/></clipPath>
  <linearGradient id="gl-{name}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".35"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#card-{name})">
    <rect width="{TILE_W}" height="{TILE_H}" fill="{color}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 40}" cy="{TILE_H - 40}" r="60" fill="none" stroke="{on}" stroke-opacity=".5" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="90" height="{TILE_H + 40}" fill="url(#gl-{name})" transform="translate(-260 0)"/>
  </g>
  <text class="sl" {d(delay + 0.35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{on}">{escape(label)}</text>
  <g class="ai" {d(delay + 0.5)}><text class="n" style="animation-delay:{delay + 1.3:.2f}s" x="250" y="38" font-family="{MONO}" font-size="14" fill="{on}">&#8594;</text></g>
  <g clip-path="url(#slot-{name})"><g class="ro" {d(delay + 0.45)}>
    {count_up(num, word, 22, 110, f'font-family="{SERIF}" font-size="{font_size}" fill="{on}"', delay + 0.45)}
  </g></g>
  {blurb_svg}
</g>
"""
    write(f"{name}.svg", svg(TILE_W, TILE_H, body, ["serif", "serif-i", "sans", "mono"],
                             f"{label}: {num} {word}. {blurb}", left=4 * pos, right=8 - 4 * pos))


# ---- 3 · Activity Card (12-Month Bar Chart) -----------------------------------
def activity(data):
    h = 340
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = max(best["total"], 1)
    x0, x1, base, maxh, gap = 40, 600, 292, 140, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, m in enumerate(monthly):
        partial = i == len(monthly) - 1
        is_best = m is best
        bh = max(4, round(m["total"] / top * maxh))
        x = x0 + i * (bw + gap)
        fill = MAROON if is_best else (RULE if partial else INK)
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        bars.append(
            f'<rect class="g" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}"><title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MAROON}">{m["total"]:,}</text>'
            )
    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    streak_note = "current streak, and the longest" if cs >= ls else f"current streak, longest {ls}"
    total_days = len(data["days"])
    stats = [
        (f'{cs} <tspan font-style="italic">days</tspan>', streak_note),
        (f'{data["active_days"]}<tspan fill="#a0707a"> / {total_days}</tspan>', "days with a commit"),
        (f'{data["best_day"]["count"]}', "on the busiest day"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 104 + i * 92
        side.append(
            f'<g class="r" {d(2.6 + i * 0.15)}>'
            f'<text x="650" y="{y}" font-family="{SERIF}" font-size="40" fill="{INK}">{big}</text>'
            f'<text x="650" y="{y + 24}" font-family="{SANS}" font-size="13" fill="{MUTED}">{small}</text></g>'
        )
        if i < 2:
            side.append(f'<rect class="f" {d(2.6)} x="650" y="{y + 44}" width="190" height="1" fill="{RULE}"/>')

    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}" stroke="{RULE}" stroke-width="1"/>
<text class="f" {d(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{INK}">{data["total_contributions"]:,} <tspan font-style="italic">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write("activity.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                              f'{data["total_contributions"]:,} contributions in the last year, {cs}-day streak'))


# ---- 4 · Royal Maroon Heatmap Card -------------------------------------------
MAROON_RAMP = [PAPER_DEEP, "#e8b8c2", "#cf7486", "#a6334a", MAROON, "#4d0012"]


def level_for(c):
    return 0 if c == 0 else 1 if c <= 5 else 2 if c <= 15 else 3 if c <= 30 else 4 if c <= 50 else 5


def heatmap(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = 1.0 + col * 0.03 + row * 0.02
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{MAROON_RAMP[level_for(c)]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months if col < ncols - 12
    )
    legend_x = right - len(MAROON_RAMP) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(MAROON_RAMP)
    )
    h = gy + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}" stroke="{RULE}" stroke-width="1"/>
<text class="r" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">Every day, <tspan font-style="italic" fill="{MAROON}">in royal maroon</tspan></text>
<text class="f" {d(0.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.4)}>{labels}
<text x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>
{legend}
<text x="{legend_x + len(MAROON_RAMP) * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                             f'Contribution graph: {data["total_contributions"]:,} contributions in the last year'))


# ---- 5 · Featured Repositories ------------------------------------------------
REPO_W, REPO_H = 880 / 3 - 8, 176
REPOS = [
    ("AuditPilot", "Autonomous Multi-Agent Financial Forensic Audit Copilot with Google ADK & Gemini Flash.", "Python", MAROON),
    ("IaC-Sentinal", "AI-assisted Terraform infrastructure drift detection & human-approved automated remediation.", "Python", GOLD),
    ("CoverCraft", "Full-stack serverless web application using Amazon Bedrock Nova Lite to craft tailored cover letters.", "TypeScript", CRIMSON),
]


def repo_card(i, name, desc, lang, color, stars, full_repo_name=None):
    delay = 4.6 + i * 0.12
    meta = f"{lang}  ·  ★ {stars}" if stars else f"{lang}  ·  live"
    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="14" fill="{PAPER}" stroke="{RULE}" stroke-width="1"/>
<g class="r" {d(delay)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{color}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="18" fill="{INK}">{escape(name)}</text>
  {text_lines(24, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{INK_SOFT}"')}
  <text x="24" y="{REPO_H - 24}" font-family="{MONO}" font-size="12" fill="{MUTED}">{escape(meta)}</text>
</g>
"""
    write(f"repo-{name.lower()}.svg", svg(REPO_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{name}: {desc}",
                                         left=4 * i, right=8 - 4 * i))


def section_title(text, italic, theme):
    fg = "#f7ebef" if theme == "dark" else INK
    body = (
        f'<text class="r" {d(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">{escape(text)} '
        f'<tspan font-style="italic">{escape(italic)}</tspan></text>'
    )
    write(f"title-coding-{theme}.svg", svg(W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0))


def repo_stars():
    stars = {}
    repo_map = {
        "AuditPilot": "AuditPilot",
        "IaC-Sentinal": "IaC-Sentinal",
        "CoverCraft": "CoverCraft---AI-Powered-Cover-Letter-Generator",
    }
    try:
        import requests
        for disp_name, actual_name in repo_map.items():
            r = requests.get(f"https://api.github.com/repos/DevRushi-engg/{actual_name}", timeout=10)
            if r.ok:
                stars[disp_name] = r.json().get("stargazers_count", 0)
    except Exception as e:
        print(f"stars unavailable: {e}")
    return stars


def link_buttons():
    h = 26
    # LinkedIn Compact Badge
    w_in = 110
    in_icon = 'M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z'
    body_in = f"""
<rect width="{w_in}" height="{h}" rx="6" fill="{MAROON}" stroke="#a82038" stroke-width="1"/>
<path transform="translate(10 6) scale(0.58)" fill="#fdfbf7" d="{in_icon}"/>
<text x="30" y="17" font-family="{SANS}" font-weight="600" font-size="12" fill="#fdfbf7">LinkedIn</text>
<text x="94" y="17" font-family="{MONO}" font-size="11" fill="{GOLD}">&#8599;</text>
"""
    badge_in = svg(w_in, h, body_in, ["sans-b", "mono"], "LinkedIn Profile", bottom=0)
    write("link-linkedin.svg", badge_in)
    write("badge-linkedin.svg", badge_in)

    # AWS Community Compact Badge
    w_aws = 142
    aws_icon = 'M6.924 12.395c0 .42-.047.78-.142 1.077a1.91 1.91 0 0 1-.453.79 2.053 2.053 0 0 1-.789.475 3.322 3.322 0 0 1-1.15.166 3.01 3.01 0 0 1-1.192-.224 2.222 2.222 0 0 1-.84-.633 2.518 2.518 0 0 1-.476-.988 4.78 4.78 0 0 1-.157-1.282c0-.498.056-.939.167-1.324a3.02 3.02 0 0 1 .494-1.023 2.378 2.378 0 0 1 .825-.668 2.656 2.656 0 0 1 1.16-.239 2.91 2.91 0 0 1 1.167.224 2.344 2.344 0 0 1 .84.623 2.54 2.54 0 0 1 .484.975c.105.39.157.838.157 1.344zm3.003-4.148c-.283-.41-.65-.729-1.102-.958a3.542 3.542 0 0 0-1.615-.344 3.753 3.753 0 0 0-1.579.324 3.315 3.315 0 0 0-1.18.898 3.655 3.655 0 0 0-.705 1.378 5.76 5.76 0 0 0-.236 1.767c0 .66.082 1.258.246 1.794a3.864 3.864 0 0 0 .73 1.419 3.58 3.58 0 0 0 1.22.932 3.744 3.744 0 0 0 1.698.354 3.553 3.553 0 0 0 1.503-.314 3.4 3.4 0 0 0 1.134-.87v.984h2.514V7.153H9.927v1.094zm7.625 4.148c0 .42-.047.78-.142 1.077a1.91 1.91 0 0 1-.453.79 2.053 2.053 0 0 1-.789.475 3.322 3.322 0 0 1-1.15.166 3.01 3.01 0 0 1-1.192-.224 2.222 2.222 0 0 1-.84-.633 2.518 2.518 0 0 1-.476-.988 4.78 4.78 0 0 1-.157-1.282c0-.498.056-.939.167-1.324a3.02 3.02 0 0 1 .494-1.023 2.378 2.378 0 0 1 .825-.668 2.656 2.656 0 0 1 1.16-.239 2.91 2.91 0 0 1 1.167.224 2.344 2.344 0 0 1 .84.623 2.54 2.54 0 0 1 .484.975c.105.39.157.838.157 1.344zm3.003-4.148c-.283-.41-.65-.729-1.102-.958a3.542 3.542 0 0 0-1.615-.344 3.753 3.753 0 0 0-1.579.324 3.315 3.315 0 0 0-1.18.898 3.655 3.655 0 0 0-.705 1.378 5.76 5.76 0 0 0-.236 1.767c0 .66.082 1.258.246 1.794a3.864 3.864 0 0 0 .73 1.419 3.58 3.58 0 0 0 1.22.932 3.744 3.744 0 0 0 1.698.354 3.553 3.553 0 0 0 1.503-.314 3.4 3.4 0 0 0 1.134-.87v.984h2.514V7.153h-2.396v1.094zM12 21.054a14.73 14.73 0 0 1-8.528-2.617.47.47 0 0 1-.061-.647l.95-.97a.465.465 0 0 1 .634-.035 12.87 12.87 0 0 0 7.005 2.072c5.093 0 9.772-2.36 10.978-2.628a.468.468 0 0 1 .536.326l.42 1.312a.471.471 0 0 1-.322.584c-1.393.364-5.918 2.603-11.612 2.603zm10.742-3.136c-.461-.634-.897-1.157-1.615-1.576a.377.377 0 0 0-.498.083l-.707.925a.37.37 0 0 0 .044.512c.563.42 1.052.88 1.488 1.455.105.14.303.17.447.07l.794-.57a.37.37 0 0 0 .047-.899z'
    body_aws = f"""
<rect width="{w_aws}" height="{h}" rx="6" fill="#232f3e" stroke="#3b4754" stroke-width="1"/>
<path transform="translate(10 6) scale(0.58)" fill="#ff9900" d="{aws_icon}"/>
<text x="28" y="17" font-family="{SANS}" font-weight="600" font-size="12" fill="#fdfbf7">AWS Community</text>
<text x="126" y="17" font-family="{MONO}" font-size="11" fill="{GOLD}">&#8599;</text>
"""
    badge_aws = svg(w_aws, h, body_aws, ["sans-b", "mono"], "AWS Community Profile", bottom=0)
    write("badge-aws.svg", badge_aws)

    # GitHub Compact Badge
    w_gh = 100
    gh_icon = 'M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z'
    body_gh = f"""
<rect width="{w_gh}" height="{h}" rx="6" fill="#240308" stroke="#4a0b16" stroke-width="1"/>
<path transform="translate(10 6) scale(0.58)" fill="#fdfbf7" d="{gh_icon}"/>
<text x="30" y="17" font-family="{SANS}" font-weight="600" font-size="12" fill="#fdfbf7">GitHub</text>
<text x="84" y="17" font-family="{MONO}" font-size="11" fill="{GOLD}">&#8599;</text>
"""
    badge_gh = svg(w_gh, h, body_gh, ["sans-b", "mono"], "GitHub Profile", bottom=0)
    write("link-github.svg", badge_gh)
    write("badge-github.svg", badge_gh)


if __name__ == "__main__":
    data = json.load(open(DATA))
    hero()
    
    # 3 World Metric Tiles (Option A)
    tile("build", "AI & AGENTS", MAROON, "#ffffff", "Multi-Agent", "Copilot",
         "Financial forensics & generative workflows with Google ADK, Gemini & AWS Bedrock.", 3.1, 0, font_size=33)
    tile("brand", "CLOUD & DEVOPS", GOLD, INK, "Zero-Drift", "IaC",
         "Terraform drift detection, automated governance, and serverless AWS architecture.", 3.35, 1, font_size=33)
    tile("learn", "SYSTEMS & DSA", CRIMSON, "#ffffff", f'{data["total_contributions"]}+', "commits",
         "Daily algorithmic problem solving in C++, continuous shipping & 22+ active repos.", 3.6, 2, font_size=38)
    
    activity(data)
    
    stars = repo_stars()
    for i, (name, desc, lang, color) in enumerate(REPOS):
        repo_card(i, name, desc, lang, color, stars.get(name, 0))
        
    section_title("Featured", "Projects", "dark")
    section_title("Featured", "Projects", "light")
    heatmap(data)
    link_buttons()
