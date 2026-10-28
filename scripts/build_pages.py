"""Builds the guide/kit pages of money-stories.ch.

    python3 scripts/build_pages.py

- public/start/index.html          free guide "Start Like Leo" (text: content/start_like_leo.md)
- public/first-year-investing/     paid kit page (buy button = STRIPE_LINK below)
- public/products/index.html       products overview
- templates/thanks-first-year-investing.html   download page, served only after a paid Stripe session
Figures are computed here (fv) so the pages and the guide can't drift apart.
"""
import re, html, pathlib, markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

# Fill in once Kiko creates the Stripe Payment Link (live mode, CHF 29 incl. VAT).
STRIPE_LINK = "https://buy.stripe.com/eVq00kdnEfbBcKd4KT38404"
PRICE = "CHF 29"
# Buyer download links (Drive). Filled in once the files are in the shared folder.
SHEET_ID = ""          # Google Sheet id of the calculator
PDF_FILE_ID = ""       # Drive file id of the guide PDF
CONTACT = "kikotajada@gmail.com"


def fv(monthly, rate, years):
    i = (1 + rate) ** (1 / 12) - 1
    n = years * 12
    return monthly * ((1 + i) ** n - 1) / i * (1 + i)


def chf(x):
    return "CHF&nbsp;" + f"{round(x):,}"


SAV30, INV30, INV25 = fv(500, .005, 30), fv(500, .05, 30), fv(500, .05, 25)
FEE_LOW, FEE_HIGH = fv(500, 1.05 * (1 - .002) - 1, 30), fv(500, 1.05 * (1 - .015) - 1, 30)


def head(title, desc, path, og="img/kit/og-start.jpg", robots=None, ogtype="website"):
    rob = f'<meta name="robots" content="{robots}">\n' if robots else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{rob}<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://money-stories.ch{path}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Money Stories">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://money-stories.ch{path}">
<meta property="og:image" content="https://money-stories.ch/{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F6F3EC">
<link rel="icon" href="/assets/img/favicon.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/anton.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
"""


def header(current=""):
    def a(href, label):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<div class="wrap">
  <header class="site-header">
    <a class="logo" href="/"><img src="/assets/img/avatar.jpg" alt="" width="44" height="44">Money <span>Stories</span></a>
    <nav class="site-nav" aria-label="Main">{a('/start/', 'Free guide')}{a('/first-year-investing/', 'Investing kit')}{a('/products/', 'Products')}</nav>
  </header>
</div>
"""


FOOTER = f"""<div class="wrap">
  <footer class="site-footer">
    <p>Educational and entertainment content. Not financial, tax or legal advice. Rules vary by canton and change over time. Investing involves risk of loss.</p>
    <p><a href="/start/">Free guide</a> · <a href="/first-year-investing/">Investing kit</a> · <a href="https://www.instagram.com/money_stories.ch/" rel="noopener">Instagram</a> · <a href="https://www.tiktok.com/@money_stories.ch" rel="noopener">TikTok</a> · <a href="mailto:{CONTACT}">Contact</a></p>
    <p>Money Stories is part of Tajada Studios · Zurich · © 2026</p>
  </footer>
</div>
</body>
</html>
"""


def md(s):
    return markdown.markdown(s, extensions=["tables"])


def duo(text):
    """'**Leo** … **Sofia** …' paragraph → two boxes."""
    leo, sof = text.split("**Sofia**", 1)
    leo = leo.replace("**Leo**", "Leo", 1).strip()
    return (f'<div class="duo"><div class="who who--leo"><b>✗ Leo</b>{md(leo)[3:-4]}</div>'
            f'<div class="who who--sofia"><b>✓ Sofia</b>{md("Sofia" + sof)[3:-4]}</div></div>')


def kit_box():
    return f"""<a class="card kit-box" href="/first-year-investing/">
  <img src="/img/kit/kit-square.webp" alt="The guide PDF and the calculator of the Your First Year Investing kit" width="400" height="400" loading="lazy">
  <div>
    <span class="badge badge--paid">Kit · {PRICE}</span>
    <h2>Want the <span class="mark">full plan?</span></h2>
    <p><strong>Your First Year Investing in Switzerland</strong>: an illustrated 20-page guide plus a calculator. Pillar 3a, fees, choosing a broker by criteria, a simple portfolio, Swiss tax on investing and what to do each month of your first year.</p>
    <span class="btn">See the kit</span>
  </div>
</a>"""


# ---------------------------------------------------------------- /start/
def build_start():
    text = (ROOT / "content" / "start_like_leo.md").read_text()
    secs = {}
    for part in re.split(r"^## ", text, flags=re.M)[1:]:
        title, body = part.split("\n", 1)
        secs[title.strip()] = body.strip()
    images = {1: ("free-1", "Leo at the kitchen table squinting at his payslip"),
              9: ("free-2", "Sofia gives Leo a thumbs-up next to a board of ticked boxes")}
    moves = []
    for title, body in secs.items():
        m = re.match(r"Move (\d+) — (.*)", title)
        if not m:
            continue
        n = int(m.group(1))
        paras = re.split(r"\n\s*\n", body)
        out = []
        for i, p in enumerate(paras):
            if p.startswith("**Leo**"):
                out.append(duo(p))
            elif p.startswith("**Want the full plan?**"):
                continue  # replaced by the kit box at the end
            elif i == 0:
                out.append(f'<p><strong>{md(p)[3:-4]}</strong></p>')
            else:
                out.append(md(p))
        img = ""
        if n in images:
            f, alt = images[n]
            img = f'<img class="st-img" src="/img/kit/{f}.webp" alt="{alt}" width="1200" height="805" loading="lazy">'
        moves.append((n, f'<li class="card st-move" id="move-{n}"><span class="st-n">{n}</span><h3>{html.escape(m.group(2))}</h3>{img}{"".join(out)}</li>'))

    checklist = [re.sub(r"^\d+\\?\.\s*", "", l[6:].strip()) for l in secs["Your checklist"].splitlines() if l.startswith("- [ ]")]
    sources = md(secs["Sources (checked 22 October 2026)"]).replace("<ul>", '<ul class="sources">')
    desc = "Ten money moves for your first year in Switzerland: payslip, withholding tax, health insurance, emergency fund, rent deposit, fees, pension fund, AHV, pillar 3a and investing. Free."
    page = head("Start Like Leo: free guide to your first year in Switzerland · Money Stories", desc, "/start/") + header("/start/") + f"""<main id="content">
<section class="st-hero">
  <div class="wrap st-hero-grid">
    <div>
      <span class="badge badge--free">Free guide · 10 moves</span>
      <h1>Start like <span class="mark">Leo</span></h1>
      <p class="lead">Ten money moves for your first year in Switzerland. Each one takes an evening, and together they save most expats thousands of francs. No jargon, nothing to sell you.</p>
      <a class="btn" href="#move-1">Start with move 1</a>
    </div>
    <img class="st-hero-img" src="/img/kit/cover-free.webp" alt="Leo, in his red bomber jacket, holds a map by the lake in Zurich with his suitcase" width="966" height="1200">
  </div>
</section>
<div class="wrap narrow">
  <div class="card st-facts">
    <p><span class="num">CHF&nbsp;7,258</span>you can deduct from your taxable income through pillar 3a in 2026 (with a pension fund).</p>
    <p><span class="num loss">≈&nbsp;CHF&nbsp;1,500</span>a year Leo overpaid on health insurance with the wrong franchise.</p>
    <p><span class="num">≈&nbsp;{chf(INV30)}</span>is what CHF 500 a month could become in 30 years at an assumed 5% a year, vs ≈&nbsp;{chf(SAV30)} in a savings account.</p>
  </div>
  <p class="muted small">✗ Leo arrived in Zurich last year and made every one of these mistakes. ✓ Sofia, his colleague, got them right. Do what she does.</p>

  <h2 class="st-group">Moves 1–6: <span class="mark">protect yourself</span></h2>
  <ol class="st-moves">{''.join(h for n, h in moves if n <= 6)}</ol>
  <h2 class="st-group">Moves 7–10: <span class="mark">build your future</span></h2>
  <ol class="st-moves" start="7">{''.join(h for n, h in moves if n > 6)}</ol>

  {kit_box()}

  <h2 class="st-group">Your <span class="mark">checklist</span></h2>
  <ul class="card checklist">{''.join(f'<li><input type="checkbox" id="c{i}" aria-label="Done"><label for="c{i}">{i}. {html.escape(c)}</label></li>' for i, c in enumerate(checklist, 1))}</ul>

  <div class="disclaimer">
    <p><strong>Sources (checked 22 October 2026)</strong></p>
    {sources}
    <p style="margin-top:10px">Investing figures: CHF 500 paid at the start of each month for 30 years, compounded monthly, at an assumed 5% a year (world equities, before costs) vs 0.5% (savings account); no taxes or inflation. Assumptions, not forecasts. Educational and entertainment content: not financial, tax or legal advice, and no provider is recommended or paid to be mentioned.</p>
  </div>
</div>
</main>
""" + FOOTER
    (PUB / "start" / "index.html").write_text(page)


# ---------------------------------------------------------------- kit page
def buy_button(big=False):
    cls = "btn btn--big" if big else "btn"
    if STRIPE_LINK:
        return f'<a class="{cls}" href="{STRIPE_LINK}" data-checkout>Buy the kit · {PRICE}</a>'
    return f'<span class="{cls}" aria-disabled="true" style="opacity:.55;cursor:default">Coming soon · {PRICE}</span>'


def build_kit():
    chapters = ["Are you ready to invest? Emergency fund, debt and timing", "Why invest at all? Savings account vs markets",
                "Pillar 3a first? Interest account vs securities 3a", "ETF, index fund or the bank's own fund?",
                "Choosing a broker, by criteria", "A simple portfolio: world, Switzerland and your currency",
                "Swiss tax on investing: wealth tax, dividends, withholding tax", "Your first 12 months, month by month"]
    tabs = [("Ready", "emergency fund, expensive debt and how much you can really invest today."),
            ("Growth", "savings account vs investing over 10, 20 or 30 years, also in today's francs."),
            ("3a", "your tax saving and interest account vs securities 3a."),
            ("Fees", "what an expensive fund costs you against a low-cost one."),
            ("Broker compare", "trading, custody, currency and stamp duty for up to three brokers, on your plan."),
            ("My portfolio", "your target mix and where to put next month's money."),
            ("Tax", "income tax on dividends, wealth tax and the withholding tax you get back."),
            ("Year plan", "month-by-month checklist and log.")]
    gallery = [("ch3", "3 · Pillar 3a first?", "Leo holds a red and a grey folder, unsure which is the 3a"),
               ("ch4", "4 · What fees really cost", "Leo's bucket of coins leaks through a hole"),
               ("ch6", "6 · A simple portfolio", "Sofia's tidy shelf with two jars next to Leo's crowded one"),
               ("ch7", "7 · Swiss tax on investing", "Sofia hands Leo one neat folder over a pile of papers")]
    desc = "Illustrated guide + calculator to start investing with a Swiss salary: emergency fund, pillar 3a, fees, choosing a broker, a simple portfolio, Swiss tax and a month-by-month plan."
    page = head("Your First Year Investing in Switzerland · Money Stories", desc, "/first-year-investing/", "img/kit/og-kit.jpg", ogtype="product") + header("/first-year-investing/") + f"""<main id="content">
<section class="kit-hero">
  <div class="wrap kit-hero-grid">
    <div>
      <span class="pill">New · Guide + calculator</span>
      <h1>Your first year <span class="mark">investing</span> in Switzerland</h1>
      <p class="lead">What to sort out before you invest, whether 3a comes first, which funds and broker to pick, and how Swiss tax works on investments. Month by month, for people with a normal Swiss salary.</p>
      <div class="kit-buy">{buy_button(True)}
        <span class="kit-note">One-off payment · Instant download · VAT included · Secure payment with Stripe</span></div>
    </div>
    <img src="/img/kit/kit-wide.webp" alt="The PDF guide and the calculator of the Your First Year Investing kit" width="1400" height="875">
  </div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow">The problem</p>
    <h2>Investing isn't hard. <span class="mark">Starting wrong is.</span></h2>
    <div class="kit-facts">
      <div class="card card-pad"><span class="num">≈&nbsp;{chf(INV30)}</span><p>is what CHF 500 a month could become in 30 years at an assumed 5% a year. In a savings account at 0.5%: ≈&nbsp;{chf(SAV30)}.</p></div>
      <div class="card card-pad"><span class="num loss">−{chf(FEE_LOW - FEE_HIGH)}</span><p>is what a typical 1.5% bank fund costs you over those 30 years, against a 0.2% index fund.</p></div>
      <div class="card card-pad"><span class="num loss">−{chf(INV30 - INV25)}</span><p>is what waiting 5 years to "learn more first" costs in the same example.</p></div>
    </div>
    <p class="kit-note" style="margin-top:16px">Educational examples with assumed returns, before taxes. Not a promise of future results.</p>
  </div>
</section>

<section class="section alt">
  <div class="wrap">
    <p class="eyebrow">What's inside</p>
    <h2>Two pieces that <span class="mark">work together</span></h2>
    <div class="kit-two">
      <div class="card card-pad">
        <h3>📘 The guide (PDF, 20 pages)</h3>
        <p class="muted">Illustrated with Leo and Sofia. Every chapter ends with what Leo did (don't), what Sofia did (do) and which calculator tab to open.</p>
        <ol class="kit-list">{''.join(f'<li>{c}</li>' for c in chapters)}</ol>
      </div>
      <div class="card card-pad">
        <h3>📊 The calculator (Google Sheets or Excel)</h3>
        <p class="muted">Make a copy in your Google Drive, or download it as Excel, and put in your own numbers.</p>
        <ul class="kit-list">{''.join(f'<li><strong>{t}:</strong> {d}</li>' for t, d in tabs)}</ul>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow">Inside the guide</p>
    <h2>What it <span class="mark">looks like</span></h2>
    <div class="kit-gallery">{''.join(f'<figure class="card"><img src="/img/kit/{f}.webp" alt="{alt}" width="1200" height="805" loading="lazy"><figcaption>{cap}</figcaption></figure>' for f, cap, alt in gallery)}</div>
  </div>
</section>

<section class="section alt">
  <div class="wrap kit-two">
    <div>
      <p class="eyebrow">It's for you if…</p>
      <ul class="kit-list kit-yes">
        <li>You earn a Swiss salary and your savings sit in a bank account.</li>
        <li>You're not sure whether to start with 3a, an ETF or the bank's fund.</li>
        <li>Swiss tax on investments (wealth tax, withholding tax, US vs Irish funds) confuses you.</li>
        <li>You want to invest a fixed amount every month and stop checking the news.</li>
        <li>You'd like boring and working over exciting and costly.</li>
      </ul>
    </div>
    <div>
      <p class="eyebrow">It's not for you if…</p>
      <ul class="kit-list kit-no">
        <li>You want us to tell you which fund or broker to buy. This is education, not advice.</li>
        <li>You want trading, crypto or single stocks to get rich fast.</li>
        <li>You've been investing in index funds for years.</li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">Questions</p>
    <h2>Before you <span class="mark">buy</span></h2>
    <details><summary>How do I get it?</summary><p>Right after paying you land on your download page: the PDF guide and the calculator (copy it to Google Sheets or download it as Excel). The link is also in your Stripe receipt.</p></details>
    <details><summary>How much money do I need to start?</summary><p>None to read it. The examples use CHF 500 a month, but every number in the calculator is yours to change.</p></details>
    <details><summary>Do you recommend a broker or a fund?</summary><p>No. You get the criteria and a calculator to compare on your own plan. We keep a separate, up-to-date broker comparison on money-stories.ch.</p></details>
    <details><summary>Does it work outside Zurich?</summary><p>Yes. The rules are Swiss; where a canton matters (tax rates, wealth-tax allowances, filing thresholds) the guide says so and the calculator lets you enter your canton's numbers.</p></details>
    <details><summary>What if I'm leaving Switzerland?</summary><p>The guide covers what happens to your 3a and pension fund when you leave, and why the currency you'll retire in matters.</p></details>
    <details><summary>Can I get a refund?</summary><p>It's a digital download, available immediately. If something doesn't work, write to <a class="link" href="mailto:{CONTACT}">{CONTACT}</a> and we'll sort it out.</p></details>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="card price-card">
      <p class="eyebrow">Your First Year Investing in Switzerland</p>
      <span class="num">{PRICE}</span>
      <p class="muted" style="margin:8px 0 20px">Guide (PDF, 20 pages) + calculator · one-off payment</p>
      {buy_button(True)}
      <p class="kit-note" style="margin-top:14px">Not ready? Start with the <a class="link" href="/start/">free guide</a>.</p>
    </div>
    <p class="disclaimer">Educational and entertainment content. Not financial, tax or legal advice. Figures checked on 22 October 2026; rules vary by canton and change over time. Investing involves risk of loss. No provider in the kit paid to be mentioned.</p>
  </div>
</section>
</main>
""" + FOOTER
    (PUB / "first-year-investing" / "index.html").write_text(page)


# ---------------------------------------------------------------- products
def build_products():
    page = head("Products · Money Stories", "Free guide and investing kit from Money Stories: Swiss money for expats, explained with stories.", "/products/") + header("/products/") + f"""<main id="content">
<section class="section">
  <div class="wrap">
    <h1>Guides <span class="mark">&amp; kits</span></h1>
    <p class="lead">Plain-English help with money in Switzerland, with Leo and Sofia.</p>
    <div class="prod-grid">
      <a class="card prod" href="/start/"><img src="/img/kit/og-start.jpg" alt="" width="1200" height="630" loading="lazy"><div><span class="badge badge--free">Free</span><h3>Start Like Leo</h3><p>Ten money moves for your first year in Switzerland, from your payslip to your first investment.</p><span class="btn btn--light">Read the guide</span></div></a>
      <a class="card prod" href="/first-year-investing/"><img src="/img/kit/og-kit.jpg" alt="" width="1200" height="630" loading="lazy"><div><span class="badge badge--paid">{PRICE if STRIPE_LINK else 'Coming soon'}</span><h3>Your First Year Investing in Switzerland</h3><p>Guide + calculator: 3a, fees, brokers by criteria, a simple portfolio, Swiss tax and a month-by-month plan.</p><span class="btn">See the kit</span></div></a>
    </div>
  </div>
</section>
</main>
""" + FOOTER
    (PUB / "products" / "index.html").write_text(page)


# ---------------------------------------------------------------- thank-you (template)
def build_thanks():
    sheet_copy = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/copy"
    sheet_xlsx = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
    pdf = f"https://drive.google.com/file/d/{PDF_FILE_ID}/view"
    page = head("Thank you · Your First Year Investing in Switzerland", "Download page of the Your First Year Investing kit.", "/first-year-investing/thanks", "img/kit/og-kit.jpg", robots="noindex, nofollow") + header() + f"""<main id="content" class="thanks">
<div class="wrap narrow">
  <span class="pill">Purchase complete ✓</span>
  <h1>Thank you! The kit <span class="mark">is yours</span></h1>
  <p class="lead">Three steps and you're set. <strong>Bookmark this page</strong>: it's your download link.</p>
  <div class="steps">
    <div class="card card-pad step"><span class="n">1</span><div>
      <h2>Get the calculator</h2>
      <p><strong>Google Sheets:</strong> click "Copy" and then "Make a copy". It's saved in your Drive and only you can see it (you need a Google account). <strong>Excel:</strong> click "Download for Excel" to get the .xlsx file.</p>
      <div class="dl"><a class="btn" href="{sheet_copy}" target="_blank" rel="noopener">📊 Copy to Google Sheets</a> <a class="btn btn--light" href="{sheet_xlsx}" rel="noopener">⬇️ Download for Excel (.xlsx)</a></div>
    </div></div>
    <div class="card card-pad step"><span class="n">2</span><div>
      <h2>Download the guide</h2>
      <p>20 illustrated pages. Every chapter tells you which calculator tab to open.</p>
      <div class="dl"><a class="btn" href="{pdf}" target="_blank" rel="noopener">📘 Download the guide (PDF)</a></div>
    </div></div>
    <div class="card card-pad step"><span class="n">3</span><div>
      <h2>Start with the first filter</h2>
      <p>Open the <strong>Ready</strong> tab, fill in the yellow cells (spending, savings, debt, franchise) and read chapter 1. Before you invest a franc, you'll know how much you can really invest.</p>
    </div></div>
  </div>
  <p class="tip muted">Any problem with the download? Write to <a class="link" href="mailto:{CONTACT}">{CONTACT}</a> and we'll fix it. The kit is for personal use: please don't share it, so we can keep making free videos.</p>
</div>
</main>
""" + FOOTER
    (ROOT / "templates" / "thanks-first-year-investing.html").write_text(page)


if __name__ == "__main__":
    build_start(); build_kit(); build_products(); build_thanks()
    print("built: start, first-year-investing, products, templates/thanks-first-year-investing.html")
