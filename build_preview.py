#!/usr/bin/env python3
"""Build the Busy Bees Preview v1 static site into preview/.

Multi-screen, mobile-first, fully static HTML. Design data (towns, categories,
jobs, size questions, tiers) is transcribed from the locked sandbox build at
~/workspace/your_files/busy-bees-sandbox-board/busy-bees-sandbox-board.html.
Customers never see fees anywhere in this preview — fees appear only on the
contractor screens, exactly as in the locked design.

Re-run:  python3 build_preview.py     (writes into ./preview/)
"""
import html, json, os, urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")

# Preview version + reviewer-safe changelog: single source of truth lives in
# review/version.json (also shown on the review packet page). Bump it there.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "review", "version.json"), encoding="utf-8") as _vf:
    _VER = json.load(_vf)
_STAGE = _VER.get("stage", "")
VERSION_LABEL = (f"Test site version {_VER['version']}"
                 + (f" — {_STAGE}" if _STAGE else "")
                 + f" · Updated {_VER['date_label']}")

def q(s):
    return urllib.parse.quote(s, safe="")

# ---------------------------------------------------------------- data ----
TOWNS = ["Yarmouth", "Hyannis / Barnstable", "Dennis", "Sandwich",
         "Chatham", "Harwich", "Mashpee", "Brewster"]

LAWN_TIERS = [("Tiny", "up to 2,000 sq ft"), ("Small", "2,001–5,000 sq ft"),
              ("Standard", "5,001–10,000 sq ft"), ("Large", "10,001–20,000 sq ft"),
              ("Huge", "over 20,000 sq ft")]
MULCH_TIERS = [("Tiny", "up to 1 cubic yard"), ("Small", "up to 2 cubic yards"),
               ("Standard", "up to 5 cubic yards"), ("Full", "up to 10 cubic yards"),
               ("Huge", "over 10 cubic yards")]
CLEAN_TIERS = ["Tiny", "Small", "Standard", "Acre+", "Huge"]

# Job kinds: opts | lawn | mulch | cleanup | freq | variant+<size kind>
# fields: id, name, kind, q (question), opts, variant, freq, note, target
CATS = [
 dict(id="tree", name="Tree Work", desc="Removal, limbs, stumps, trimming", jobs=[
   dict(id="treeremoval", name="Tree removal", kind="opts", q="How many trees?",
        opts=["1 tree", "2–3 trees", "4–6 trees", "7 or more"]),
   dict(id="limb", name="Limb removal", kind="opts", q="Tell us about the limbs",
        opts=["A few limbs — open yard", "Heavy limbs — open yard",
              "A few limbs — near roof, drive, or lines",
              "Heavy limbs — near roof, drive, or lines"]),
   dict(id="stump", name="Stump grinding", kind="opts", q="How many stumps?",
        opts=["1 stump", "2–3 stumps", "4 or more"]),
   dict(id="trim", name="Tree trimming & pruning", kind="opts", q="What kind of trimming?",
        opts=["Dead limb", "Clearance", "Crown work", "Canopy shaping", "Young tree"]),
   dict(id="brush", name="Brush clearing", kind="opts", q="How big is the area?",
        opts=["Small overgrown lot", "Large overgrown lot"],
        note="Overgrown lots only. If it's a wetland or a tricky job, pick “Something else” at the bottom of the jobs list instead."),
 ]),
 dict(id="lawn", name="Lawn Care", desc="Mowing, aeration & seeding", jobs=[
   dict(id="mowing", name="Lawn mowing", kind="lawnfreq",
        freq=["One-time", "Monthly", "Every 2 weeks", "Weekly", "Seasonal"]),
   dict(id="aeration", name="Aeration & seeding", kind="variant+lawn",
        variant=["Aeration only", "Overseed only", "Both"]),
   dict(id="leafpickup", name="Curbside leaf pickup", kind="opts",
        q="How much is piled at the curb?",
        desc="You pile the leaves at the curb — we load them up and haul them away",
        opts=["A few bags or one small pile", "One big pile — about a pickup-truck load",
              "A long row of piles along the curb", "Multiple truck loads"]),
 ]),
 dict(id="land", name="Landscaping", desc="Hedges, mulch, cleanups, hardscape", jobs=[
   dict(id="bush", name="Hedges & shrubs (bush trimming)", kind="optsfreq",
        q="How much trimming?", opts=["Tiny", "Small", "Medium", "Large", "Huge"],
        freq=["One-time", "Seasonal (spring + fall)"]),
   dict(id="beds", name="Mulch, weed & edge (garden beds)", kind="variant+mulch",
        variant=["Mulch", "Weed & edge", "Both"]),
   dict(id="cleanup", name="Yard cleanups", kind="variant+cleanup",
        variant=["Fall cleanup", "Spring cleanup", "General cleanup"],
        freq=["One-time", "Both seasons"]),
   dict(id="hardscape", name="Hardscape install & repair", kind="opts",
        q="What size job?", opts=["Small repair", "Standard project", "Full install"]),
   dict(id="brush2", name="Brush clearing", kind="link", target="brush",
        desc="Same questions as under Tree Work"),
   dict(id="stump2", name="Stump grinding", kind="link", target="stump",
        desc="Same questions as under Tree Work"),
 ]),
 dict(id="storm", name="Storm Cleanup", desc="Branches down, fallen trees, roof tarping", jobs=[
   dict(id="debris", name="Branches & debris", kind="opts", q="How much is down?",
        opts=["One small pile", "A yard's worth", "Lot-wide"]),
   dict(id="fallentree", name="Fallen tree", kind="link", target="treeremoval",
        desc="Goes through the tree removal questions — same job"),
   dict(id="tarp", name="Cover a storm-damaged roof (roof tarping)", kind="opts",
        q="How big is the damaged area?",
        opts=["Small damaged area", "Medium damaged area", "Large damaged area"],
        note="On the real site, we look at the roof on a satellite map to get oriented — the size comes from the damaged area you describe, and the contractor confirms it."),
 ]),
 dict(id="snow", name="Snow Removal", desc="Shoveling, snowblower, plowing, salting", jobs=[
   dict(id="shovel", name="Shoveling", kind="opts", q="What needs clearing?",
        desc="Walks, steps, small areas",
        opts=["Walkway — one storm", "Full clearing — one storm",
              "Walkway + steps — one storm", "Season — walkway",
              "Season — full (steps included)"]),
   dict(id="blower", name="Snowblower", kind="opts", q="Drive size?",
        desc="Standard drives",
        opts=["Standard drive — one storm", "Large drive — one storm",
              "Season — standard", "Season — large"]),
   dict(id="plow", name="Plowing", kind="plow", desc="Large drives & lots"),
   dict(id="salt", name="Salting", kind="opts", q="Salting on its own",
        desc="Just salting", opts=["Yes — salting only"],
        note="Salting is free when it's bundled with another snow job done by the same contractor."),
   dict(id="rake", name="Roof raking (from the ground)", kind="opts", q="House size?",
        desc="Done from the ground with a long rake", opts=["Ranch", "2-story"],
        note="Done from the ground with a long rake. Going up on the roof itself is not a board service — pick “Something else” at the bottom of the jobs list if that's what you need."),
   dict(id="snow unsure", name="Not sure which fits", kind="unsure",
        desc="Tell us in the notes on a later screen"),
 ]),
 dict(id="haul", name="Heavy Hauling", desc="Single items to whole-property cleanouts", jobs=[
   dict(id="single", name="Single item", kind="opts", q="One item to go",
        opts=["Yes — one item"]),
   dict(id="full", name="Full load", kind="opts", q="A full load",
        opts=["Yes — full load"]),
   dict(id="multi", name="Multi-load", kind="opts", q="How many loads?",
        opts=["Multi-load", "Multi-load + construction debris"]),
   dict(id="estate", name="Whole property (estate cleanout)", kind="opts",
        q="How much of the property?", opts=["Partial", "Average", "Full"]),
   dict(id="leafpickup2", name="Curbside leaf pickup", kind="link", target="leafpickup",
        desc="Same questions as under Lawn Care"),
 ]),
 dict(id="wash", name="Pressure Washing", desc="House, driveways, decks, roofs, gutters, car wash", jobs=[
   dict(id="housewash", name="House wash — siding", kind="opts", q="House size?",
        opts=["Small / ranch", "Standard 2-story", "Large / estate"]),
   dict(id="surfaces", name="Driveways, patios & decks", kind="variant+opts",
        variant=["Walkway", "Porch & steps", "Patio", "Driveway", "Pool deck", "Deck"],
        q="Size?", opts=["Small", "Standard", "Large"]),
   dict(id="roofwash", name="Roof wash — soft wash for roofs", kind="opts",
        q="Roof size?", opts=["Small", "Standard", "Large"]),
   dict(id="gutter", name="Gutter cleaning (one-time only)", kind="opts", q="Stories?",
        opts=["Ranch", "2-story", "3-story"]),
   dict(id="carwash", name="Car wash — exterior only (we come to you)", kind="freq",
        q="How often?", freq=["One wash", "Monthly", "Every 2 weeks", "Weekly"]),
 ]),
]
JOB_BY_ID = {}
for c in CATS:
    for j in c["jobs"]:
        JOB_BY_ID[j["id"]] = (c, j)

# ------------------------------------------------------------- chrome -----
def page(title, depth, body, back=None, step=None, gate=True):
    """depth: 0 = preview root, 1 = customer/ or contractor/."""
    up = "" if depth == 0 else "../"
    step_html = f'<p class="step">{html.escape(step)}</p>' if step else ""
    back_html = ""
    if back is not None:
        back_html = (f'<nav class="botnav"><a class="js-back" href="{back}">← Back</a>'
                     f'<a href="{up}index.html">⌂ Home</a></nav>')
    gate_script = ""
    if gate:
        gate_script = ("<script>try{if(localStorage.getItem('bb_agreed')!=='1')"
                       f"{{location.replace('{up}../review/');}}}}catch(e){{}}</script>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#14161F">
<title>{html.escape(title)} — Busy Bees (pretend test)</title>
<link rel="icon" href="{up}../assets/busy-bees-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}preview.css">
</head>
<body>
{gate_script}
<div class="pretend">PRETEND TEST VERSION — nothing here is real, and nothing you tap sends anything.</div>
<header class="hdr"><div class="hdr-in">
<img src="{up}../assets/busy-bees-logo.png" alt="Busy Bees gold shield logo">
<span class="brand">Busy Bees<small>Local service dispatch</small></span>
<a class="home" href="{up}index.html">⌂ Home</a>
</div></header>
<main class="wrap">
{step_html}{body}
</main>
{back_html}
<footer><b>Busy Bees</b> — pretend test version · busybeesdispatch.com<br>
{VERSION_LABEL}<br>
Questions? Call or text <b>(508) 258-9899</b> · dispatch@busybeesdispatch.com<br>
<a href="{up}privacy.html">Privacy — what's counted</a> · <a href="{up}whats-new.html">What's New</a></footer>
<script src="{up}preview.js"></script>
<script src="{up}bbtrack.js" defer></script>
</body>
</html>
"""

def opt(href, label, desc=None, carry=True):
    d = f'<span class="d">{html.escape(desc)}</span>' if desc else ""
    c = " data-carry" if carry else ""
    return (f'<a class="opt" href="{href}"{c}>{html.escape(label)}'
            f'<span class="arr">→</span>{d}</a>')

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", rel)

# ---------------------------------------------------------------- home ----
def build_home():
    body = """
<div class="banner"><b>Pretend test version — nothing here is real.</b>
<p>Fake jobs, pretend payments. You can't break anything. This is the practice copy of the new Busy Bees site, here so fresh eyes can check it before the real one goes live.</p></div>
<div class="hero">
<img src="../assets/busy-bees-logo.png" alt="Busy Bees gold shield logo">
<h1>Give us a buzz.</h1>
<p>One board for local yard, home, and hauling help. Pick your town, pick what you need, and send one simple request. No account needed to ask.</p>
</div>
<a class="btn btn-gold" href="customer/town.html" data-track="start-request">Request a local pro<span class="d">Free to send — a local pro confirms first. It's a request, not an instant booking.</span></a>
<a class="btn btn-dark" href="contractor/join.html" data-track="contractor-entry">I'm a contractor<span class="d">See how job offers work — you pay only when you accept a job.</span></a>
<div class="card"><h2>How it works</h2>
<ol class="tight">
<li>Pick a town and a service.</li>
<li>Answer one question at a time.</li>
<li>Send the request with one tap. A local contractor confirms, then they handle the rest.</li>
</ol></div>
<div class="card"><h2>Customers — explore the whole site</h2>
<a class="opt" href="customer/town.html">Request a local pro<span class="arr">→</span><span class="d">The full request flow: town, service, size, how often (when it applies), details, send.</span></a>
<a class="opt" href="customer/account.html">Your account — free &amp; premium<span class="arr">→</span><span class="d">Saved details, past requests, one-tap re-requests, premium extras.</span></a>
<a class="opt" href="contractor/ownpage.html">A member's own page<span class="arr">→</span><span class="d">What it looks like when you request a contractor directly on their own page.</span></a>
<a class="opt" href="areas.html">Areas we serve<span class="arr">→</span><span class="d">Cape Cod is live. See which areas open next.</span></a>
<a class="opt" href="almanac.html" style="margin-bottom:0">The Cape Cod Yard Almanac<span class="arr">→</span><span class="d">Free seasonal yard &amp; garden reading — no sign-in, ever.</span></a>
</div>
<div class="card"><h2>For contractors</h2>
<p>Registered contractors get matched job offers by text: the job, the town, the size, how often it repeats, and the flat fee — all in plain words. You confirm before anything is final, and declining is always free.</p>
<a class="opt" href="contractor/join.html">Join &amp; how job offers work<span class="arr">→</span></a>
<a class="opt" href="contractor/offer.html">See a pretend job offer<span class="arr">→</span></a>
<a class="opt" href="contractor/membership.html">Membership — your own page<span class="arr">→</span><span class="d">Your own Busy Bees page, where your customers request you directly. Optional — never required for board jobs.</span></a>
<a class="opt" href="contractor/levels.html">Levels &amp; verified<span class="arr">→</span><span class="d">How levels work, and what showing your business paperwork does.</span></a>
<a class="opt" href="contractor/founding.html">Founding codes<span class="arr">→</span><span class="d">The founding offer and how referral codes earn free time.</span></a>
<a class="opt" href="contractor/backoffice.html">The Hive — member tools<span class="arr">→</span><span class="d">A peek at the tools members get: their customers, estimates, jobs, invoices, and what each job made them — fed by the board itself.</span></a>
<a class="opt" href="contractor/future-trades.html" style="margin-bottom:0">Don't see your trade?<span class="arr">→</span><span class="d">Apply to the future-trades list — the trade is not live yet.</span></a>
</div>
"""
    write("index.html", page("Busy Bees — pretend test version", 0, body))

# ------------------------------------------------------- customer pages ---
def build_town():
    opts = "".join(opt(f"category.html?t={q(t)}", t, carry=False) for t in TOWNS)
    body = f"""
<h1>Where is the job?</h1>
<p class="sub">Pick the town. One tap takes you to the next question.</p>
{opts}
<p class="note">Busy Bees serves Cape Cod now. More areas are coming — each new area opens when 3 local contractors there are on the roster.</p>
"""
    write("customer/town.html", page("Pick your town", 1, body,
          back="../index.html", step="Customer request · Step 1 of 6 — Town"))

def build_category():
    opts = "".join(
        opt(f"job-{c['id']}.html?c={q(c['name'])}", c["name"], c["desc"])
        for c in CATS)
    body = f"""
<h1>What do you need done?</h1>
<p class="sub">Pick the kind of work. Not sure? There's a “Something else” button at the bottom.</p>
{opts}
<a class="opt" href="other.html" data-carry>Something else<span class="arr">→</span><span class="d">Not on the list? Describe it in your own words.</span></a>
"""
    write("customer/category.html", page("Pick what you need", 1, body,
          back="town.html", step="Customer request · Step 2 of 6 — Category"))

def first_screen(job):
    """First screen file for a job (relative to customer/)."""
    k = job["kind"]
    if k == "link":
        return "size-%s.html" % job["target"]
    if k == "unsure":
        return "details.html"
    if k == "plow":
        return "plow.html"
    if k.startswith("variant"):
        return "variant-%s.html" % job["id"]
    return "size-%s.html" % job["id"]

def build_job_pages():
    for c in CATS:
        items = ""
        for j in c["jobs"]:
            href = "%s?j=%s" % (first_screen(j), q(j["name"]))
            items += opt(href, j["name"], j.get("desc"))
        body = f"""
<h1>{html.escape(c['name'])}</h1>
<p class="sub">Pick the job. Each button takes you to one short question about size.</p>
{items}
<a class="opt" href="other.html" data-carry>Something else<span class="arr">→</span><span class="d">Not on the list? Describe it in your own words.</span></a>
"""
        write(f"customer/job-{c['id']}.html",
              page(c["name"] + " — pick the job", 1, body,
                   back="category.html", step="Customer request · Step 3 of 6 — Job"))

def size_help(next_href):
    return """
<div class="card"><h3 style="margin-top:0">Not sure of the size? Measure the area that needs work</h3>
<p>On the real site, this is where a satellite map opens: you tap the corners of the area and it works out the square feet for you. It's the <b>area to work</b> that counts — not the whole lot. Here in the pretend version, use one of these two helpers instead:</p>
<p style="font-weight:700;margin-bottom:4px">Helper 1 — tap the boxes</p>
<p class="small" style="margin-top:0">Each box stands for about 400 sq ft — roughly a two-car driveway. Tap the boxes that cover the area that needs work.</p>
<div class="mapgrid" id="mapGrid">""" + "".join(
    '<button type="button" aria-label="area box"></button>' for _ in range(50)) + """</div>
<p class="calc-out" id="mapOut">Tap the squares that cover the area that needs work.</p>
<a class="btn btn-gold" id="mapUse" href="NEXT" data-carry style="display:none">Use this size and continue →</a>
<p style="font-weight:700;margin-bottom:4px">Helper 2 — the square-foot calculator</p>
<p class="small" style="margin-top:0">Measure the area in feet, then multiply: length × width = square feet. Odd shape? Split it into rectangles, work out each one, and add them up.</p>
<label>Length (feet)<input type="number" id="calcL" min="0" inputmode="decimal" placeholder="e.g. 50"></label>
<label>Width (feet)<input type="number" id="calcW" min="0" inputmode="decimal" placeholder="e.g. 100"></label>
<button class="btn btn-ghost" type="button" id="calcBtn">Work out my size</button>
<p class="calc-out" id="calcOut"></p>
<a class="btn btn-gold" id="calcUse" href="NEXT" data-carry style="display:none">Use this size and continue →</a>
<p class="small">Rough guides: a parking space ≈ 160 sq ft · a two-car driveway ≈ 400 sq ft · a living room ≈ 200–300 sq ft · a tennis court ≈ 2,800 sq ft.</p>
</div>
""".replace("NEXT", next_href)

def size_filename(job):
    return "size-%s.html" % job["id"]

def emit(fname, title, body, back, step):
    write("customer/" + fname, page(title, 1, body, back=back, step=step))

def build_job_screens():
    for c in CATS:
        back = f"job-{c['id']}.html"
        for j in c["jobs"]:
            k = j["kind"]
            if k in ("link", "unsure"):
                continue
            has_freq = bool(j.get("freq"))
            after_size = (f"freq-{j['id']}.html?j={q(j['name'])}" if has_freq
                          else "details.html")
            size_back = (f"variant-{j['id']}.html" if k.startswith("variant")
                         else back)
            if k.startswith("variant"):
                # screen 1: which one?
                vopts = "".join(
                    opt(f"size-{j['id']}.html?v={q(v)}", v) for v in j["variant"])
                emit(f"variant-{j['id']}.html", j["name"] + " — which one",
                     f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">First: which one do you need? The next screen asks about size.</p>
{vopts}
""", back, "Customer request · Step 4 of 6 — Size")
            if k == "plow":
                emit("plow.html", "Plowing — one storm or the season",
                     f"""
<h1>Plowing</h1>
<p class="sub">One storm at a time, or covered for the whole season?</p>
{opt('plow-once.html', 'One storm', 'Pay per visit, one storm at a time')}
{opt('plow-season.html', 'The whole season', 'Covered all winter')}
""", back, "Customer request · Step 4 of 6 — Size")
                once = "".join(
                    opt(f"details.html?p={q(p)}", p) for p in
                    ["Small — one storm", "Standard — one storm", "Large — one storm",
                     "Small — one storm + sand & salt", "Standard — one storm + sand & salt",
                     "Large — one storm + sand & salt"])
                emit("plow-once.html", "Plowing — one storm",
                     f"""
<h1>Plowing — one storm</h1>
<p class="sub">How big is the drive or lot?</p>
{once}
""", "plow.html", "Customer request · Step 4 of 6 — Size")
                season = "".join(
                    opt(f"details.html?p={q(p)}", p) for p in
                    ["Season — small", "Season — standard", "Season — large"])
                emit("plow-season.html", "Plowing — the whole season",
                     f"""
<h1>Plowing — the whole season</h1>
<p class="sub">How big is the drive or lot?</p>
{season}
""", "plow.html", "Customer request · Step 4 of 6 — Size")
            elif k in ("opts", "optsfreq"):
                o = "".join(opt(f"{after_size}&p={q(o_)}" if "?" in after_size
                                else f"{after_size}?p={q(o_)}", o_) for o_ in j["opts"])
                b = f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">{html.escape(j.get('q',''))}</p>
{o}
"""
                if j.get("note"):
                    b += f'<p class="note">{html.escape(j["note"])}</p>'
                emit(size_filename(j), j["name"] + " — size", b, size_back,
                     "Customer request · Step 4 of 6 — Size")
            elif k in ("lawnfreq", "variant+lawn"):
                tiers = "".join(
                    opt(f"{after_size}&p={q(n + ' lawn')}" if "?" in after_size
                        else f"{after_size}?p={q(n + ' lawn')}", n, r)
                    for n, r in LAWN_TIERS)
                b = f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">How big is the lawn — the part that gets worked on?</p>
{tiers}
{size_help(after_size)}
"""
                emit(size_filename(j), j["name"] + " — lawn size", b, size_back,
                     "Customer request · Step 4 of 6 — Size")
            elif k == "variant+mulch":
                tiers = "".join(
                    opt(f"details.html?p={q(n + ' (' + r + ')')}", n, r)
                    for n, r in MULCH_TIERS)
                b = f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">How much mulch — measured in cubic yards?</p>
{tiers}
<div class="card"><h3 style="margin-top:0">Know the number of cubic yards? Type it</h3>
<label>Cubic yards<input type="number" id="ydIn" min="0" step="0.5" inputmode="decimal" placeholder="e.g. 2.5"></label>
<button class="btn btn-ghost" type="button" id="ydBtn">Work out my size</button>
<p class="calc-out" id="ydOut"></p>
<a class="btn btn-gold" id="ydUse" href="details.html" data-carry style="display:none">Use this size and continue →</a>
<p class="small" style="margin-bottom:0">One cubic yard covers about 100 sq ft, 3 inches deep. Weed &amp; edge in the same visit uses the same mulch size — there's never a second size to pick.</p>
</div>
"""
                emit(size_filename(j), j["name"] + " — mulch size", b, size_back,
                     "Customer request · Step 4 of 6 — Size")
            elif k == "variant+cleanup":
                tiers = "".join(
                    opt(f"freq-{j['id']}.html?p={q(n + ' yard')}", n)
                    for n in CLEAN_TIERS)
                b = f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">How big is the yard?</p>
{tiers}
<p class="note">Guessing is fine — the contractor confirms the size before anything is final.</p>
"""
                emit(size_filename(j), j["name"] + " — yard size", b, size_back,
                     "Customer request · Step 4 of 6 — Size")
            elif k == "variant+opts":
                o = "".join(opt(f"details.html?p={q(o_)}", o_) for o_ in j["opts"])
                b = f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">{html.escape(j.get('q',''))}</p>
{o}
"""
                emit(size_filename(j), j["name"] + " — size", b, size_back,
                     "Customer request · Step 4 of 6 — Size")
            if has_freq and j["id"] != "carwash":
                fopts = "".join(opt(f"details.html?f={q(f_)}", f_) for f_ in j["freq"])
                emit(f"freq-{j['id']}.html", j["name"] + " — how often",
                     f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">How often?</p>
{fopts}
""", size_filename(j), "Customer request · Step 4 of 6 — How often")
            if k == "freq":  # car wash: the how-often question IS the screen
                fopts = "".join(opt(f"details.html?f={q(f_)}", f_) for f_ in j["freq"])
                emit(size_filename(j), j["name"] + " — how often",
                     f"""
<h1>{html.escape(j['name'])}</h1>
<p class="sub">{html.escape(j.get('q',''))}</p>
{fopts}
""", back, "Customer request · Step 4 of 6 — Size")

def build_other():
    body = """
<h1>Something else</h1>
<p class="sub">Describe it in your own words. There's no size or price to pick here — Busy Bees reads it, assigns it to the right service, and a contractor confirms before anything is final.</p>
<form method="get" action="details.html" data-draft="request-other">
<label>What do you need?<span class="hint">A sentence or two is plenty.</span>
<textarea name="desc" rows="4" placeholder="e.g. Big tree leaning after the storm…"></textarea></label>
<button class="btn btn-gold" type="submit" data-track="other-continue">Continue — add my details →</button>
</form>
<p class="note">Pretend version: continuing only carries your words to the next screen. Nothing is sent anywhere. What you type is kept on this device as you go, so closing the page won't lose it.</p>
"""
    emit("other.html", "Something else", body, "category.html",
         "Customer request · Step 4 of 6 — Describe it")

def build_details():
    body = """
<h1>Your details</h1>
<p class="sub">For: <b><span data-echo="j">your job</span></b> · <span data-echo="t">Cape Cod</span></p>
<form method="get" action="review.html" id="detailsForm" data-draft="request-details">
<label>Your name
<input type="text" name="name" autocomplete="name" placeholder="e.g. Jane Smith"></label>
<label>Address where the work is
<input type="text" name="address" autocomplete="street-address" placeholder="Street address and town"></label>
<label>Best way to reach you — phone or email
<span class="hint">Only used to update you about this request. You and the contractor talk through the board's private relay, so your real number is never shown to them.</span>
<input type="text" name="contact" placeholder="e.g. 508-555-0100 or you@email.com"></label>
<label>Notes for the contractor (optional)
<span class="hint">Gate codes, dogs, timing — anything that helps.</span>
<textarea name="notes" id="fNotes" rows="3"></textarea></label>
<button class="btn btn-gold" type="submit" data-track="details-continue">Continue to review →</button>
</form>
<p class="note">Sizes are your best estimate — the contractor confirms the size with you before anything is final. Requesting is always free, and you never owe Busy Bees anything.</p>
<p class="note">Pretend version: this form only carries your words to the review screen on this device. Nothing is sent anywhere. What you type is kept on this device as you go, so you can close the page and pick up right where you left off.</p>
"""
    emit("details.html", "Your details", body, "category.html",
         "Customer request · Step 5 of 6 — Your details")

def build_review():
    body = """
<h1>Request ready — one tap sends it</h1>
<p class="sub">Check it over. Anything wrong, use Back and fix it — nothing is final until you tap the gold button.</p>
<div class="card"><h2 style="margin-top:0">Your request</h2>
<div class="kv"><b>Town</b><span data-echo="t">—</span></div>
<div class="kv"><b>Job</b><span data-echo="j">—</span></div>
<div class="kv"><b>Which</b><span data-echo="v">—</span></div>
<div class="kv"><b>Size</b><span data-echo="p">—</span></div>
<div class="kv"><b>How often</b><span data-echo="f">—</span></div>
<div class="kv"><b>Name</b><span data-echo="name">—</span></div>
<div class="kv"><b>Address</b><span data-echo="address">—</span></div>
<div class="kv"><b>Reach you at</b><span data-echo="contact">—</span></div>
<div class="kv"><b>Notes</b><span data-echo="notes">—</span></div>
</div>
<p class="note">Free to send — customers never pay. The contractor pays a small flat fee only if they accept your job. A local pro confirms first: this is a request, not an instant booking.</p>
<a class="btn btn-gold" href="sent.html" data-carry data-track="send-request" style="font-size:21px">Request Ready — One Tap Sends It</a>
<p class="note center">Pretend version: tapping that button sends nothing anywhere. On the real board, this one tap texts your request to Busy Bees.</p>
<p class="note" id="cartNote" style="display:none"></p>
<button class="btn btn-ghost" type="button" id="addJob" data-track="add-job">Add another job<span class="d">Saves this job, then lets you pick one more — send them all together.</span></button>
<a class="btn btn-dark" id="cartBtn" href="cart.html" data-carry data-track="view-cart" style="display:none">Your jobs</a>
"""
    emit("review.html", "Review your request", body, "details.html",
         "Customer request · Step 6 of 6 — Review & send")

def build_sent():
    body = """
<span id="clearCart" hidden></span>
<p class="bigcheck">🎉</p>
<h1 class="center">Request sent — well, pretend sent</h1>
<p class="sub center">In the real board, that one tap texts your request to Busy Bees at (508) 258-9899. Here, nothing left your phone.</p>
<div class="card"><h2 style="margin-top:0">What happens next</h2>
<ol class="tight">
<li>Busy Bees matches your request to a local pro who does this work in your town.</li>
<li>The pro looks at the job and confirms. Only then is anything final.</li>
<li>You hear back, and you talk through the board's private relay — your real phone number stays hidden.</li>
<li>If every matched contractor passes, Busy Bees keeps working on it and lets you know. You're never just left hanging.</li>
</ol></div>
<a class="btn btn-gold" href="town.html">Make another pretend request</a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    emit("sent.html", "Request sent (pretend)", body, "review.html",
         "Customer request · Done")

# ------------------------------------------------- cart + account pages ---
def build_cart():
    body = """
<h1>Your jobs</h1>
<p class="sub">Jobs you've saved to send together. Nothing here has been sent yet — check the list, take off anything you don't want, then send them all with one tap.</p>
<div class="card"><div id="cartList"><p class="note">Loading your saved jobs…</p></div></div>
<a class="btn btn-gold" href="sent.html" data-carry>Send all requests together</a>
<a class="btn btn-ghost" href="town.html">Start a new request instead</a>
<p class="note">Free to send — customers never pay. Each job is matched and confirmed separately, and a contractor confirms before anything is final.</p>
"""
    emit("cart.html", "Your jobs", body, "review.html", "Customer request · Your jobs")

def build_account():
    body = """
<h1>Your Busy Bees account</h1>
<p class="sub">You never need an account to send a request. An account just makes the next one faster — and keeps your requests in one place.</p>
<div class="card"><h2 style="margin-top:0">Free account</h2>
<ul class="tight">
<li><b>Saved details</b> — your name, address, and contact filled in for you.</li>
<li><b>Request history</b> — every past request in one place.</li>
<li><b>One-tap re-request</b> — ask for the same job again in seconds.</li>
<li><b>Track your request</b> — see where it stands.</li>
<li><b>Pick your contractor</b> — choose who gets your request first.</li>
</ul>
<a class="btn btn-gold" href="account-home.html">Pretend sign-in — free account<span class="d">Pretend: no password, nothing is saved or sent.</span></a></div>
<div class="card deal"><h2 style="margin-top:0">Premium <span class="badge">$20/month</span></h2>
<p>Everything the free account has, <b>plus</b>:</p>
<ul class="tight">
<li><b>Your main contractor</b> — stay connected to the pro you trust, per kind of work.</li>
<li><b>Preference extras</b> — your saved preferences ride along with every request.</li>
</ul>
<p style="margin-bottom:0"><b>Try it free for 30 days</b>, then $20/month. It renews automatically after the trial until you cancel. Cancel anytime. <a href="premium.html"><b>See premium →</b></a></p></div>
<p class="note">Requesting work is always free, with or without an account. Premium is only ever about the extras above — it never changes what a request costs, because requests cost nothing.</p>
"""
    emit("account.html", "Your account", body, "../index.html", "Customer account · Free & premium")

def build_account_home():
    body = """
<h1>Welcome back, Jane <span class="badge">Free account</span></h1>
<p class="sub">Pretend signed-in home. Everything below is made-up example info.</p>
<div class="card"><h2 style="margin-top:0">Your saved details</h2>
<div class="kv"><b>Name</b><span>Jane Smith</span></div>
<div class="kv"><b>Home address</b><span>12 Main Street, Yarmouth</span></div>
<div class="kv"><b>Reach you at</b><span>508-555-0100</span></div>
<p class="small" style="margin-bottom:0">These fill in automatically on every request. Contractors still only see your address after they accept — and talk to you through the private relay.</p></div>
<div class="card"><h2 style="margin-top:0">Your main contractor</h2>
<p><b>Example Tree Co</b> — tree work</p>
<p class="small">Your saved first choice for tree work. Premium members keep a main contractor for every kind of work, and their preferences travel with each request.</p>
<a class="btn btn-gold" href="category.html">Request Example Tree Co again</a></div>
<div class="card"><h2 style="margin-top:0">Past requests</h2>
<div class="kv"><b>Jun 2026</b><span>Lawn mowing — Standard lawn · Weekly <br><a href="category.html"><b>Request again →</b></a></span></div>
<div class="kv"><b>Apr 2026</b><span>Yard cleanups — Spring cleanup · Standard yard <br><a href="category.html"><b>Request again →</b></a></span></div>
<div class="kv"><b>Nov 2025</b><span>Curbside leaf pickup — one big pile <br><a href="category.html"><b>Request again →</b></a></span></div>
<p class="small" style="margin-bottom:0">One tap puts the same job back in your hands — just check it and send.</p></div>
<div class="card deal"><h2 style="margin-top:0">Go premium — 30 days free</h2>
<p>Keep a main contractor for every kind of work, and your preferences ride along with every request. Free for 30 days, then $20/month, renewing automatically until you cancel. Cancel anytime.</p>
<a class="btn btn-gold" href="premium.html">See premium &amp; start free</a></div>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    emit("account-home.html", "Your account home", body, "account.html", "Customer account · Signed in")

def build_premium():
    body = """
<h1>Busy Bees Premium</h1>
<p class="sub">For customers who use the board a lot and want their pros and preferences remembered.</p>
<div class="card"><h2 style="margin-top:0">What premium adds</h2>
<ul class="tight">
<li><b>Main-contractor connection</b> — stay connected to the contractor you trust, for each kind of work, instead of starting fresh every time.</li>
<li><b>Preference extras</b> — gate codes, dogs, timing, how you like the yard left — saved once, sent with every request automatically.</li>
<li>Everything in the <b>free account</b>: saved details, history, one-tap re-requests, tracking, contractor choice.</li>
</ul></div>
<div class="card deal"><h2 style="margin-top:0">The price, plainly</h2>
<ul class="tight">
<li><b>30 days free</b> to try it.</li>
<li>Then <b>$20/month</b>. Premium <b>renews automatically</b> until you cancel — <b>cancel anytime</b> in two taps. Premium stays on until the end of the paid period, and there are <b>no refunds for unused time</b>.</li>
<li>Sending requests stays <b>free</b> either way. Premium never changes that.</li>
</ul></div>
<a class="btn btn-gold" href="premium-on.html">Start my 30 days free<span class="d">Pretend here: nothing is charged, ever, in this test version.</span></a>
<a class="btn btn-ghost" href="account.html">Keep the free account instead</a>
"""
    emit("premium.html", "Premium", body, "account.html", "Customer account · Premium")

def build_premium_on():
    body = """
<p class="bigcheck">🎉</p>
<h1 class="center">Premium is on <span class="badge">Premium</span></h1>
<p class="sub center">Pretend version: nothing was charged and no trial really started. On the real board, here's exactly how it works:</p>
<div class="card"><ul class="tight">
<li>Your <b>30 free days</b> start today. The first charge — <b>$20</b> — happens after those 30 days unless you cancel before then. Premium then renews automatically each month until you cancel.</li>
<li>Your main contractors and preferences now ride along with every request.</li>
<li><b>Cancel anytime</b> from your account page — two taps, no phone call, no hard feelings. Premium stays on until the end of the paid period, unused time is not refunded, and cancelling keeps your free account and your history.</li>
</ul></div>
<a class="btn btn-gold" href="account-home.html">Go to my account home</a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    emit("premium-on.html", "Premium is on", body, "premium.html", "Customer account · Premium")

# ----------------------------------------------------- contractor pages ---
def build_contractor():
    join = """
<h1>Keep your phone buzzing.</h1>
<p class="sub">Busy Bees is one board where local customers ask for yard, home, and hauling help — and the requests come to contractors like you, by text.</p>
<div class="card deal"><h2 style="margin-top:0">The deal, in plain words</h2>
<ul class="tight">
<li><b>You only pay when you accept a job</b> — one flat fee, shown in the offer before you decide.</li>
<li><b>No subscription to join.</b> <b>No commission.</b> You keep <b>100% of the job price</b> — you quote the customer yourself.</li>
<li>For example: curbside leaf pickup runs <b>$10 to $60</b> by pile size, and a standard weekly mowing arrangement is <b>$25</b>.</li>
<li><b>Declining is always free</b>, and passing on a job never counts against you.</li>
<li><b>The fee you see is the fee you pay</b> — it never changes after you accept. Fees run <b>$5 to $100</b>, set by the size of the job.</li>
<li><b>Repeat work:</b> for weekly or seasonal jobs, the flat fee is paid once, when you accept the arrangement — never per visit. One arrangement = one customer, one address, one kind of work. A new season, or a different kind of work, is a new offer with a new fee. An arrangement lasts at most <b>12 months</b>. When it ends, the customer is asked whether to continue with the same contractor under a new arrangement and fee, or send the request to the board.</li>
<li><b>If the job dies through no fault of yours, the fee comes back as credit.</b> What qualifies: a bad number, a fake or duplicate lead, a customer who answers nobody within 4 days of you accepting (after you've texted them at least twice through the board), a cancel within 24 hours of you accepting, or a no-show at the door.</li>
<li><b>How credit works:</b> text Busy Bees within 7 days of the problem to claim it or to report a no-show — for a customer who answers nobody, the 7 days run from day 4. The credit equals what you actually paid, after any discount, and sits on your account — it comes off your next charge automatically, whichever comes first, whether that's a lead or your membership bill. Credit never expires and is never paid out as cash. Credits are not discounts — they only replace a fee you already paid. The same rule covers own-page and standing-accept jobs — for an own-page job, the 10% for that job is simply removed from your next bill. If a one-time discount (welcome pick or referral) was on a lead that dies, the discount comes back whole too, good for 30 days from the day the credit lands — a dead lead never uses up part of a multi-lead discount.</li>
<li><b>What doesn't count:</b> a size that's off — you quote the real job on site (two trees that turn out to be ten is a bigger quote, not a credit).</li>
<li>Getting the customer, quoting, and losing the job — that's the introduction doing its work.</li>
<li>A repeat plan cancelled more than 24 hours after you accepted — before or after the first visit. A job that's a different kind of work than the request said <b>does</b> count as a bad lead.</li>
<li>Customers never pay anything. The fee is yours, only on jobs you accept.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">How it works</h2>
<ol class="tight">
<li><b>Get the text.</b> A matched job arrives by text: the job, the town, the size, how often it repeats, and the flat fee — all in plain words.</li>
<li><b>Confirm and pay.</b> Say yes, pay the flat fee through a secure checkout, and only then are the customer's details released to you. Declining is always free.</li>
<li><b>Do the job.</b> You talk to the customer through the board's private relay — neither phone number is ever shown. You quote the job price yourself, on site.</li>
</ol></div>
<div class="card"><h2 style="margin-top:0">Good to know</h2>
<ul class="tight">
<li><b>Verified discount:</b> show insurance = 5% off the fee · insurance + a second paper of a different kind (license or business certificate — two papers of the same kind count as one) = 10% off · a license or certificate alone earns the status but 0% off until insurance is shown. Any business paper counts toward verified — we keep a copy on file; we don't check it with the issuer. No paperwork is needed to join the board or get jobs. When a paper expires, the discount ends and verified pauses until you show a current copy. Busy Bees texts a reminder 30 days before a paper expires.</li>
<li><b>Standing-accept</b> is optional and off unless you turn it on (see Levels).</li>
<li><b>One discount per lead</b> — discounts never combine.</li>
<li><b>Welcome pick (choose one when you join):</b> 50% off your first lead, or 25% off your first 3 leads. Lead fees are never free — discounts are percentages only.</li>
<li><b>Referrals:</b> bring a new contractor and you both get 25% off a lead once they're approved. Bring a new customer and you get 20% off your next lead when their first request is accepted.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">Optional extra — your own booking page</h2>
<p>Membership is <b>never required</b> for board jobs, and the deal above never changes. Members also get their own Busy Bees page to hand to customers they already have; bookings that come through that page cost <b>membership plus 10% of the normal fee</b> instead of the full fee. The 10% is figured on the normal fee, before any discounts, and figured to the cent — 10% of $25 is $2.50. Fees and discounts are always figured to the cent.</p>
<p style="margin-bottom:0">Membership: <b>$19/week · $49/month · $490/year</b>. Membership never buys ranking, ratings, level, or verified status — ever.</p></div>
<a class="btn btn-gold" href="offer.html">See a pretend job offer →<span class="d">This is what the text looks like — and what Accept and Decline do.</span></a>
<a class="btn btn-ghost" href="future-trades.html">Don't see your trade?<span class="d">See how to apply for a future trade — no new trade is live yet.</span></a>
"""
    write("contractor/join.html", page("Contractors — how Busy Bees works", 1, join,
          back="../index.html", step="Contractor side · Start here"))

    offer = """
<h1>A job offer arrives like this</h1>
<p class="sub">On the real board this lands as a text message — the waggle, in bee terms: a bee dances directions to the good flowers; this points you straight at work that fits. The customer's address and notes stay hidden until you accept and pay the fee.</p>
<div class="msg"><div class="msg-hd">💬 Busy Bees — pretend text message</div>
<div class="msg-bd">
<p><b>New job offer</b></p>
<p>Job: <b>Tree removal</b></p>
<p>Size: <b>2–3 trees</b></p>
<p>Town: <b>Dennis</b></p>
<p class="fee">Flat fee if you accept: <b>$30</b></p>
<p class="note">The fee you see is the fee you pay — it never changes after you accept. For repeat work, the fee is paid once per arrangement, never per visit. One arrangement = one customer, one address, one kind of work; a new season or a different kind of work is a new offer with a new fee. A plan cancelled more than 24 hours after you accept earns no credit, before or after the first visit. An arrangement lasts at most <b>12 months</b>; when it ends, the customer chooses whether to continue with the same contractor under a new arrangement and fee, or send the request to the board.</p>
<p class="note">If the job dies through no fault of yours — bad number, fake or duplicate lead, a customer who answers nobody within 4 days of you accepting, a cancel within 24 hours of you accepting, or a no-show at the door — the fee comes back as credit on your account.</p>
<p class="small" style="margin-bottom:0">One flat fee, only if you accept. No commission — you keep 100% of the job price you quote.</p>
</div></div>
<div class="msg"><div class="msg-hd">💬 Busy Bees — pretend text message (repeat work)</div>
<div class="msg-bd">
<p><b>New job offer</b></p>
<p>Job: <b>Lawn mowing</b></p>
<p>Size: <b>Standard lawn</b></p>
<p>How often: <b>Weekly</b></p>
<p>Town: <b>Yarmouth</b></p>
<p class="fee">Flat fee if you accept: <b>$25</b> — paid once for the whole arrangement, never per visit</p>
</div></div>
<a class="btn btn-gold" href="accepted.html">Accept — I'll take this job<span class="d">Pretend here: the next screen shows what happens. On the real board you'd pay the fee shown in the offer first.</span></a>
<a class="btn btn-ghost" href="declined.html">Decline — pass on this job<span class="d">Always free. Never counts against you.</span></a>
"""
    write("contractor/offer.html", page("A pretend job offer", 1, offer,
          back="join.html", step="Contractor side · Job offer"))

    accepted = """
<p class="bigcheck">🎉</p>
<h1 class="center">You got the job</h1>
<p class="sub center">Pretend version: no fee was charged and no details were really released. On the real board, here's exactly what happens when you accept:</p>
<div class="card"><ol class="tight">
<li><b>You pay the flat fee</b> — $30 for this job — through a secure checkout. That fee is the only thing Busy Bees ever charges you for this job. If the job falls through for a covered reason (what counts is listed on Join), the fee comes back as credit. Need the fee back? Text Busy Bees within 7 days.</li>
<li><b>The details are released:</b> the customer's address and their notes open up for you.</li>
<li><b>You talk through the private relay:</b> messages pass through the board, so neither of you ever sees the other's real phone number.</li>
<li><b>You quote the job price yourself, on site</b> — and you keep 100% of it. Busy Bees takes no commission, ever.</li>
</ol></div>
<a class="btn btn-gold" href="offer.html">See the offer again</a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    write("contractor/accepted.html", page("You got the job", 1, accepted,
          back="offer.html", step="Contractor side · Accepted"))

    declined = """
<h1>No problem — declining is always free</h1>
<p class="sub">Nothing was charged, and nothing about this counts against you.</p>
<div class="card"><ul class="tight">
<li>Declining costs <b>nothing</b> — the fee only exists if you accept.</li>
<li>A decline, or letting an offer time out, is a <b>pass, never a strike</b>. It never counts as a strike against you.</li>
<li>The job is offered to the other matching contractors at that level, then the next level down.</li>
<li>The next offer that fits your work and your towns will text you the same way.</li>
</ul></div>
<a class="btn btn-gold" href="offer.html">See the offer again</a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    write("contractor/declined.html", page("Declined — always free", 1, declined,
          back="offer.html", step="Contractor side · Declined"))

def build_future_trades():
    body = """
<h1>Don’t see your trade?</h1>
<p class="sub">Busy Bees is starting with the services already on the board. This page is only an <b>application process for future trades</b> — it does not make a new trade live.</p>
<div class="card deal"><h2 style="margin-top:0">What this is — and what it isn’t</h2>
<ul class="tight">
<li><b>It is:</b> a waitlist for trades such as auto repair, HVAC, plumbing, electrical, or appliance repair.</li>
<li><b>It isn’t:</b> a customer service, a promise of jobs, or a way to start receiving offers now.</li>
<li>There is <b>no fee to apply</b>, and applying does not join you to the live roster for a trade that has not opened.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">How the process works</h2>
<ol class="tight">
<li><b>You apply by text</b> with the short template on the next screen.</li>
<li><b>Busy Bees reviews every application personally.</b> Busy Bees’ back-office AI can sort applications by trade and town, spot missing information or duplicates, count the list, and draft possible jobs and sizes for the owner to review.</li>
<li><b>The AI never approves an application</b>, never adds a trade, never promises work, and never contacts you on its own. The owner decides.</li>
<li>A new trade is normally considered when <b>three approved contractors</b> offer the same trade in the same area. Before it can open, the owner still has to approve its jobs, size questions, flat fees, and any legal or licensing requirements.</li>
<li>Until the owner opens the trade, <b>Busy Bees takes no customer requests for it</b>.</li>
</ol></div>
<a class="btn btn-gold" href="future-trades-apply.html">See the application text<span class="d">The exact words to copy, fill in, and text to Busy Bees in the real build.</span></a>
<a class="btn btn-ghost" href="join.html">Back to how the board works</a>
"""
    write("contractor/future-trades.html", page("Don’t see your trade?", 1, body,
          back="join.html", step="Contractor side · Future trades — not live"))

    apply_body = """
<h1>Future-trade application</h1>
<p class="sub">In the real build, this opens as a text to Busy Bees. Fill in every line you can — the AI uses these words to sort the application, and the owner reads the original.</p>
<div class="msg"><div class="msg-hd">💬 Application text — copy and fill in</div>
<div class="msg-bd">
<p><b>NEW TRADE APPLICATION</b></p>
<p>Business: ____</p>
<p>Your name: ____</p>
<p>Trade you want added: ____</p>
<p>Towns you serve: ____</p>
<p>Jobs you want from Busy Bees: ____</p>
<p>Shop, mobile, or both (if it applies): ____</p>
<p>Best text number: ____</p>
<p style="margin-bottom:0">Anything Busy Bees should know: ____</p>
</div></div>
<div class="card"><h2 style="margin-top:0">Before you send it</h2>
<p style="margin-bottom:0">Applying puts you on the <b>future-trades waitlist</b> only. It does not create a live category, does not put customer requests in front of you, and does not guarantee the trade will open.</p></div>
<a class="btn btn-gold" href="future-trades-sent.html">Pretend send — see what happens next<span class="d">Nothing is sent in this test version.</span></a>
<a class="btn btn-ghost" href="future-trades.html">Back to how it works</a>
"""
    write("contractor/future-trades-apply.html", page("Future-trade application", 1, apply_body,
          back="future-trades.html", step="Contractor side · Future trades — application"))

    sent_body = """
<p class="bigcheck">📝</p>
<h1 class="center">You’re on the future-trades list</h1>
<p class="sub center">Pretend version: nothing was sent. On the real board, here is exactly what happens after an application arrives:</p>
<div class="card"><ol class="tight">
<li>The application goes into the Busy Bees <b>future-trades waitlist</b>, under its trade and towns.</li>
<li>The back-office AI sorts it, checks for missing lines or a duplicate, and keeps the count for that trade and area.</li>
<li><b>Busy Bees reviews it personally</b> and decides whether it is approved for the waitlist.</li>
<li>When a trade reaches three approved contractors in an area, the owner can decide whether to design and open it. The jobs, sizes, and fees are built first — the trade is never switched on automatically.</li>
</ol></div>
<p class="note">No customer requests are taken for a trade until the owner opens it. If that happens, the contractors on its waitlist are contacted first.</p>
<a class="btn btn-gold" href="future-trades.html">Back to future trades</a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    write("contractor/future-trades-sent.html", page("On the future-trades list", 1, sent_body,
          back="future-trades-apply.html", step="Contractor side · Future trades — received"))


def build_membership():
    body = """
<h1>Membership — your own Busy Bees page</h1>
<p class="sub">Membership is an optional extra for contractors. Board jobs work exactly the same without it — you never need membership to get offers.</p>
<div class="card deal"><h2 style="margin-top:0">What membership gives you</h2>
<ul class="tight">
<li><b>Your own page</b> — busybeesdispatch.com/<b>your-company</b>, ready to print on cards, trucks, and flyers.</li>
<li><b>Your own customers request you directly there</b> — you're already chosen, no competing with the board.</li>
<li><b>Own-page bookings: membership plus 10% of the normal fee</b> — a $30 board fee becomes $3 on top of membership — tallied up and billed with your membership, never per job at checkout. The 10% is figured on the normal fee, before any discounts, and figured to the cent — 10% of $25 is $2.50. If you decline an own-page request, it closes, the customer is asked before it can go to the board, and you owe <b>no 10%</b> for that declined request.</li>
<li><b>Board jobs stay the full fee</b>, the same as for everyone. Membership changes nothing there.</li>
<li><b>The Hive, included.</b> Your own customers, estimates customers can approve with one tap, your job schedule, invoices your customers pay through <b>your own</b> payment account, and what each job actually made you — all in one place. Jobs you win on the board land there on their own; you never start from an empty screen.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">The price, plainly</h2>
<ul class="tight">
<li><b>$19/week · $49/month · $490/year</b> — pick what fits. Membership <b>renews automatically</b> until you cancel. Cancel anytime in two taps; your page stays up until the end of the paid period, and there are <b>no refunds for unused time</b>.</li>
<li><b>Membership never buys</b> ranking, ratings, level, or verified status — ever. Those are earned, not sold.</li>
<li><b>Never required</b> to join the board or accept any job.</li>
</ul></div>
<a class="btn btn-gold" href="member-welcome.html">Become a member — pretend sign-up<span class="d">Pretend here: no card, no charge. The next screen shows your page switched on.</span></a>
<a class="btn btn-ghost" href="backoffice.html">Peek at The Hive<span class="d">Customers, estimates, jobs, invoices, and what each job made you — the tools that come with membership.</span></a>
<a class="btn btn-ghost" href="ownpage.html">See what a member's page looks like →</a>
"""
    write("contractor/membership.html", page("Membership — your own page", 1, body,
          back="join.html", step="Contractor side · Membership"))

def build_member_welcome():
    body = """
<p class="bigcheck">🎉</p>
<h1 class="center">You're a member</h1>
<p class="sub center">Pretend version: no payment was taken and no real page was created. On the real board, your membership starts the moment you check out.</p>
<div class="card"><h2 style="margin-top:0">Your page is live</h2>
<p class="fee" style="font-size:19px">busybeesdispatch.com/<b>example-co</b></p>
<p>That's the address to hand out — on flyers, cards, your truck, everywhere. Customers who request through it are requesting <b>you</b>, and those jobs cost you <b>membership plus 10% of the normal fee</b>, tallied with your membership. (Founders pay no own-page 10% during the free test run.)</p></div>
<a class="btn btn-gold" href="backoffice.html">Open The Hive<span class="d">Your customers, estimates, jobs, invoices, and what each job made you.</span></a>
<a class="btn btn-ghost" href="ownpage.html">View my page<span class="d">See it the way your customers see it.</span></a>
<a class="btn btn-ghost" href="ownpage.html">Share my page<span class="d">Pretend: on the real site this copies your link and opens your usual share options.</span></a>
<a class="btn btn-ghost" href="membership.html">Membership settings<span class="d">Pretend: plan, billing, and cancel live here on the real site — cancel anytime.</span></a>
<a class="btn btn-ghost" href="../index.html">⌂ Back to the start</a>
"""
    write("contractor/member-welcome.html", page("You're a member", 1, body,
          back="membership.html", step="Contractor side · Membership"))

def build_ownpage():
    cats = "".join(
        opt(f"../customer/job-{c['id']}.html?c={q(c['name'])}", c["name"], c["desc"], carry=False)
        for c in CATS)
    body = f"""
<div class="hero">
<img src="../../assets/busy-bees-logo.png" alt="Busy Bees gold shield logo">
<h1>Example Tree Co</h1>
<p>A Busy Bees member page — this contractor's own page.</p>
</div>
<div class="card deal"><h2 style="margin-top:0">You're requesting Example Tree Co directly</h2>
<p style="margin-bottom:0">You came to <b>Example Tree Co's</b> own page, so your request goes to <b>them first</b> — no one else. It's still a request: they confirm before anything is final, and you talk through the board's private relay, so your real phone number stays hidden. If Example Tree Co declines, your request closes there — Busy Bees will ask you before sending it to the board.</p></div>
<h2>What do you need done?</h2>
<p class="sub">Pick the kind of work — Example Tree Co is already chosen. Each pick takes you to one short question at a time.</p>
{cats}
<a class="opt" href="../customer/other.html" data-carry>Something else<span class="arr">→</span><span class="d">Not on the list? Describe it in your own words.</span></a>
<p class="note">Free to send — customers never pay. Member pages are part of Busy Bees: busybeesdispatch.com/example-co</p>
"""
    write("contractor/ownpage.html", page("Example Tree Co — member page", 1, body,
          back="../index.html", step="Member page · Request this contractor"))

def build_levels():
    body = """
<h1>Levels &amp; verified</h1>
<p class="sub">Two separate things: your <b>level</b> comes from jobs you've done. <b>Verified</b> comes from documents you choose to show. Neither can be bought — membership never buys ranking, ratings, level, or verified status.</p>
<div class="card"><h2 style="margin-top:0">Levels — how the line works</h2>
<ul class="tight">
<li><b>Level 1</b> — 0–4 jobs done</li>
<li><b>Level 2</b> — 5–19 jobs done</li>
<li><b>Level 3</b> — 20–49 jobs done</li>
<li><b>Level 4</b> — 50+ jobs done</li>
</ul>
<p>New jobs start at the top of the ladder: <b>every contractor at the highest level with a match for the job gets it</b>. Verified contractors at that level get the <b>first look</b>. Verified speeds you up inside your level — it does not move you ahead of a higher level. The clock never runs on a level with no matching contractor. The job opens in steps: <b>Level 4 sees it first</b>, Level 3 joins at <b>15 minutes</b>, Level 2 at <b>30 minutes</b>, and Level 1 at <b>45 minutes</b> — from then it's open to the whole roster, and the <b>first contractor to accept wins</b>. The clock is capped, so <b>no job ever waits more than 1 hour total</b> before it lands in the Busy Bees dispatch queue.</p>
<p style="margin-bottom:0">Your level grows with jobs done. Separately, the private ratings customers leave feed your <b>trust score</b> — figured from jobs you complete through the board (70%) and your ratings (30%) — it grows only from completed jobs and ratings, and paying for anything adds nothing to it. Your trust score is kept private, and membership can't change it. <b>Declining a job is never a strike against you</b> — a pass is a pass. Not answering counts the same as declining: free, and never a strike.</p></div>
<div class="card deal"><h2 style="margin-top:0">Verified — show your business paperwork</h2>
<p>Showing your business paperwork is <b>optional</b> — any business paper counts: a trade license, a town business certificate, or insurance. We keep a copy on file — we don't check it with the issuer. No paperwork is needed to join the board or get jobs; this is only the bonus. If you show them:</p>
<ul class="tight">
<li><b>Insurance shown</b> = <b>5% off</b> your fees.</li>
<li><b>Insurance + a second paper</b> (a license or business certificate — it has to be a different kind; two papers of the same kind count as one) = <b>10% off</b> your fees.</li>
<li><b>A license or certificate alone</b> earns the status, but <b>0%</b> off until insurance is also shown.</li>
<li>When a paper expires, the discount ends and verified pauses until you show a current copy. First look and standing-accept pause too. You enter each paper's expiry date when you show it, and Busy Bees texts you a reminder 30 days before it expires.</li>
<li>If one paper expires but another is still current, your status stays at whatever the current paper earns. Papers with no expiry date count as current until you replace them. A job you accepted before the expiry keeps the discount it was accepted with.</li>
<li>By showing a paper, you confirm it's yours and current. A paper that turns out to be fake ends your paperwork status.</li>
<li>Verified unlocks the <b>first look</b> at new jobs, and <b>standing-accept</b>: if you opt in, jobs with a fee under $35 that match your work are accepted for you automatically. It fires when the first look ends, if the job is still there — before the job opens to the rest of the level. Verified pros get their head start to claim jobs by hand first. Verified contractors only, and only if you turn it on. You still pay the fee yourself — nothing is ever charged automatically.</li>
</ul>
<p style="margin-bottom:0"><b>What "verified" means:</b> you showed us your business paperwork — a license, a town business certificate, or insurance — and we keep a copy on file. On customer pages, this shows as <b>"Paperwork shown."</b></p></div>
<a class="btn btn-gold" href="join.html">Back to how the board works</a>
"""
    write("contractor/levels.html", page("Levels & verified", 1, body,
          back="join.html", step="Contractor side · Levels & verified"))

def build_founding():
    body = """
<h1>Founding codes</h1>
<p class="sub">The founding offer for the first contractors who help launch the board.</p>
<div class="card deal"><h2 style="margin-top:0">The founding offer</h2>
<ul class="tight">
<li>The first core contractors get <b>membership free during the test run</b> — your own page, the whole membership deal, no charge while we test. Founders also pay <b>no own-page 10%</b> during the test run — that starts when paid membership starts.</li>
<li>When paid membership starts later, your banked free time (below) is waiting for you.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">Your founding code (example)</h2>
<p class="fee">BUZZ-01</p>
<p>That code is an <b>example</b> — your own founding code is assigned to you personally, and that one goes on your flyer stack, and it's how referrals are credited to you. One person, one code. Credit follows the code no matter whose hands a flyer passes through.</p>
<ul class="tight">
<li><b>First approved referral</b> brought in with your code: <b>90 days</b> of free membership.</li>
<li><b>Each approved referral after that: +30 days.</b> No cap — the time banks up. Free time stops piling up once the founding roster reaches 10 contractors — everything already banked stays yours.</li>
<li>Banked time starts counting when paid membership begins.</li>
</ul>
<p style="margin-bottom:0">A recruit joins by scanning the QR on your flyer, texting “JOIN” plus your own code to (508) 258-9899, or just telling us the code.</p></div>
<a class="btn btn-gold" href="membership.html">See what membership includes</a>
<a class="btn btn-ghost" href="join.html">Back to how the board works</a>
"""
    write("contractor/founding.html", page("Founding codes", 1, body,
          back="join.html", step="Contractor side · Founding"))

# ------------------------------------------- dispatch / areas / almanac ---
def build_dispatch():
    body = """
<script>try{var _bbc=(localStorage.getItem("bb_code")||"").toUpperCase().replace(/[^A-Z0-9-]/g,"");if(_bbc!=="BEE-13"){location.replace("index.html");}}catch(e){location.replace("index.html");}</script>
<h1>Dispatcher view</h1>
<p class="sub"><b>Dispatcher view — only the dispatcher sees this screen.</b> Pretend data.</p>
<div class="card"><h2 style="margin-top:0">Incoming requests</h2>
<div class="kv"><b>Tree removal</b><span>2–3 trees · Dennis — <b>awaiting contractor</b> (offered 10:04 AM, Level 4 first look)</span></div>
<div class="kv"><b>Lawn mowing</b><span>Standard lawn · Weekly · Yarmouth — <b>accepted</b> by Example Tree Co</span></div>
<div class="kv"><b>Curbside leaf pickup</b><span>One big pile · Harwich — <b>awaiting contractor</b></span></div>
<div class="kv"><b>House wash</b><span>Standard 2-story · Chatham — <b>needs the dispatcher</b> (every match passed — it's on the dispatcher's desk, and the customer has been told we're still working on it)</span></div>
<p class="small" style="margin-bottom:0">If every matched contractor passes, the request lands here with the dispatcher — it never just disappears, and the customer gets an honest update.</p></div>
<div class="card"><h2 style="margin-top:0">Contractor roster</h2>
<div class="kv"><b>Example Tree Co</b><span>Level 4 · Verified ✓ · Tree work, storm cleanup</span></div>
<div class="kv"><b>Bob of All Trades</b><span>Level 3 · Hauling, cleanouts, handyman yard work</span></div>
<div class="kv"><b>Cape Clean Cuts</b><span>Level 2 · Verified ✓ · Lawn care, landscaping</span></div>
<div class="kv"><b>Harbor Snow Co</b><span>Level 1 · Snow removal</span></div></div>
<div class="card"><h2 style="margin-top:0">Today</h2>
<div class="kv"><b>Fees collected</b><span>$135 (pretend)</span></div>
<div class="kv"><b>Requests in</b><span>7</span></div>
<div class="kv"><b>Accepted</b><span>5</span></div>
<div class="kv"><b>On the dispatcher's desk</b><span>1</span></div>
<div class="kv"><b>Suggestions inbox</b><span>3 new — Busy Bees reads and decides every one; nothing changes on its own</span></div></div>
<p class="note">On the real board this desk runs the matching: verified first look, then the level cascade, then the dispatcher — with texts and checkout handled by the board's tools, and the owner making the calls.</p>
<a class="btn btn-ghost" href="index.html">⌂ Back to the start</a>
"""
    write("dispatch.html", page("Dispatcher view", 0, body,
          back="index.html", step="Dispatcher"))

def build_areas():
    body = """
<h1>Areas we serve</h1>
<p class="sub">Busy Bees grows one area at a time — an area only opens when real local contractors are on board.</p>
<div class="card deal"><h2 style="margin-top:0">Cape Cod — LIVE</h2>
<p>Yarmouth, Hyannis / Barnstable, Dennis, Sandwich, Chatham, Harwich, Mashpee, and Brewster. Requests are open now.</p>
<a class="btn btn-gold" href="customer/town.html">Request a local pro on Cape Cod</a></div>
<div class="card"><h2 style="margin-top:0">South Shore — opening soon</h2>
<p style="margin-bottom:0">Opens when <b>3 local contractors</b> are on the roster. So far: <b>2 of 3</b> (pretend count). Contractors there can already join the list.</p></div>
<div class="card"><h2 style="margin-top:0">Western Mass — opening soon</h2>
<p style="margin-bottom:0">Opens when <b>3 local contractors</b> are on the roster. So far: <b>1 of 3</b> (pretend count).</p></div>
<div class="card"><h2 style="margin-top:0">Rhode Island — opening soon</h2>
<p style="margin-bottom:0">Opens when <b>3 local contractors</b> are on the roster. So far: <b>2 of 3</b> (pretend count).</p></div>
<p class="note">Counters only ever count contractors on the roster — no padded numbers.</p>
"""
    write("areas.html", page("Areas we serve", 0, body,
          back="index.html", step="Busy Bees · Areas"))

def build_almanac():
    body = """
<div class="hero">
<img src="../assets/busy-bees-logo.png" alt="Busy Bees gold shield logo">
<h1>The Cape Cod Yard Almanac</h1>
<p>Seasonal yard &amp; garden know-how for Cape Cod — free for everybody, no sign-in, ever. Brought to you by Busy Bees.</p>
</div>
<a class="opt" href="almanac-article.html">When to do your fall cleanup<span class="arr">→</span><span class="d">Too early wastes it, too late buries it. The Cape Cod timing, plain and simple.</span></a>
<div class="card"><p class="tag">Coming soon</p><h2 style="margin-top:0">Fall planting: what still works late in the season</h2><p style="margin-bottom:0">Bulbs, garlic, and the perennials that love a fall start on the Cape.</p></div>
<div class="card"><p class="tag">Coming soon</p><h2 style="margin-top:0">Mulch basics: how much, how deep, when</h2><p style="margin-bottom:0">The 3-inch rule, the cubic-yard math, and the volcano mistake.</p></div>
<div class="card"><p class="tag">Coming soon</p><h2 style="margin-top:0">Getting the yard ready for snow season</h2><p style="margin-bottom:0">What to clear, mark, and fix before the first plow-worthy storm.</p></div>
<div class="card sponsor"><p class="tag">Sponsored — Local Partner</p>
<p style="margin-bottom:0"><b>Cape Cod Garden Center</b> — seeds, soil, mulch, and local advice. (Pretend sponsor slot — on the real Almanac, local shops only, never contractors.)</p></div>
<div class="card sponsor"><p class="tag">Sponsored — Local Partner</p>
<p style="margin-bottom:0"><b>Yarmouth Hardware</b> — tools, rakes, and everything for fall cleanup. (Pretend sponsor slot.)</p></div>
<p class="note">Reading the Almanac never costs anything and never asks for an account. Need the work done instead? <a href="customer/town.html"><b>Request a local pro →</b></a></p>
"""
    write("almanac.html", page("The Cape Cod Yard Almanac", 0, body,
          back="index.html", step="Busy Bees · The Almanac"))

def build_almanac_article():
    body = """
<p class="step">The Cape Cod Yard Almanac · Fall</p>
<h1>When to do your fall cleanup</h1>
<p class="sub">Too early wastes the work. Too late buries it under wet leaves and early snow. Here's the timing that works on Cape Cod.</p>
<div class="card"><h2 style="margin-top:0">Wait for most of the leaves — not all of them</h2>
<p>The sweet spot is after roughly three-quarters of the leaves are down but before they mat into a wet layer. On the Cape that's usually late October into November, later near the water where oaks hold on. A matted layer left all winter smothers grass and invites mold — that's the thing you're preventing.</p>
<h2>What a good fall cleanup covers</h2>
<ul class="tight">
<li>Leaves off the lawn, beds, and driveway — piled at the curb if you're having them hauled.</li>
<li>Perennials cut back (leave some standing for the birds if you like — it's your call, not a rule).</li>
<li>Gutters cleared before the freeze, so ice doesn't back up under the shingles.</li>
<li>Last mow a touch shorter than summer height.</li>
</ul>
<h2>The curb trick</h2>
<p style="margin-bottom:0">If raking is the part you don't mind, pile the leaves at the curb and let someone else do the hauling. It's an easy split of the job: you rake, they load and go. On Busy Bees it's called <b>Curbside leaf pickup</b>, under Lawn Care.</p></div>
<div class="card sponsor"><p class="tag">Sponsored — Local Partner</p>
<p style="margin-bottom:0"><b>Cape Cod Garden Center</b> — leaf bags, rakes, and mulch for the beds you're clearing. (Pretend sponsor slot — local shops only.)</p></div>
<a class="btn btn-gold" href="customer/town.html">Rather have it done? Request a local pro</a>
<a class="btn btn-ghost" href="almanac.html">← More Almanac reading</a>
"""
    write("almanac-article.html", page("When to do your fall cleanup — Almanac", 0, body,
          back="almanac.html", step="Busy Bees · The Almanac"))

# ------------------------------------------------------------- analytics --
# First-party visitor counting (Bobby, Oct 31 2026): page views, tagged
# taps, the request funnel, exit pages — totals and rates only, counted in
# Busy Bees' own Workspace. No third-party trackers, no IPs, no form
# contents, no per-visitor views. Backend: the standalone Apps Script
# "Busy Bees — Site Activity" (source in goals/side-gig-income/files/
# site-activity/Code.gs; deploy steps in hidden_files/
# site-activity-deploy-runbook.md). ANALYTICS_ENDPOINT stays "" until that
# script is deployed — with no endpoint the logger is a complete no-op,
# so the site is safe to ship before, during, or after the deploy.
ANALYTICS_ENDPOINT = "https://script.google.com/macros/s/AKfycbzoOal_JmYyjT5Z9hviIJXdG0DtC5kY8_oycSp85DBb9R5d7y7-oUuKcJqdjSxvG60a/exec"

BBTRACK_JS = r"""/* Busy Bees — first-party visitor counting (bbtrack.js).
   Counts page views, taps on buttons and links, how far a request
   gets, and the page a visit ends on. Run by Busy Bees itself, in
   Busy Bees' own Workspace — no outside analytics company, no ad
   trackers, nothing shared or sold.

   Never sent: names, phone numbers, addresses, anything typed into
   a box, IP addresses. The visit id is random, made fresh for each
   visit, kept only in this tab, and exists only to join one visit's
   own steps together (started -> ... -> sent). It is never used to
   follow anyone between visits, and no screen anywhere shows a
   single person's visit — the office side shows totals and rates.

   Your choice: the Privacy page's toggle sets bb_no_track in this
   browser and this logger checks it before every send; the
   browser's Do Not Track setting is honored the same way. Sending
   is fire-and-forget — if the counter is unreachable the page
   simply carries on. */
(function () {
  "use strict";
  var ENDPOINT = "__BB_ENDPOINT__";
  if (!ENDPOINT) { return; }

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function optedOut() {
    if (lsGet("bb_no_track") === "1") { return true; }
    try {
      var d = navigator.doNotTrack || window.doNotTrack;
      return d === "1" || d === "yes";
    } catch (e) { return false; }
  }
  if (optedOut()) { return; }

  /* Random per-visit id — a funnel join key, nothing more. */
  var sid = "";
  try { sid = sessionStorage.getItem("bb_sid") || ""; } catch (e) { }
  if (!sid) {
    sid = "v";
    var chars = "0123456789abcdef";
    for (var i = 0; i < 16; i++) { sid += chars.charAt(Math.floor(Math.random() * 16)); }
    try { sessionStorage.setItem("bb_sid", sid); } catch (e) { }
  }

  function device() {
    var ua = navigator.userAgent || "";
    if (/iPad|Tablet/i.test(ua)) { return "tablet"; }
    if (/Android/i.test(ua)) { return /Mobile/i.test(ua) ? "phone" : "tablet"; }
    if (/Mobi|iPhone|iPod/i.test(ua)) { return "phone"; }
    return "desktop";
  }

  function refHost() {
    try {
      if (!document.referrer) { return ""; }
      var h = new URL(document.referrer).hostname;
      return (h && h !== location.hostname) ? h : "";
    } catch (e) { return ""; }
  }

  function stepFor(p) {
    if (/\/customer\/town\.html$/.test(p)) { return "town"; }
    if (/\/customer\/category\.html$/.test(p)) { return "category"; }
    if (/\/customer\/other\.html$/.test(p)) { return "describe"; }
    if (/\/customer\/details\.html$/.test(p)) { return "details"; }
    if (/\/customer\/review\.html$/.test(p)) { return "review"; }
    if (/\/customer\/sent\.html$/.test(p)) { return "submitted"; }
    if (/\/customer\//.test(p)) { return "job"; }
    return "";
  }

  function reviewCode() {
    /* Only on the gated review pages — the gate already discloses that
       activity there is recorded. The test site itself stays anonymous. */
    try {
      if (location.pathname.indexOf("/review/") === -1) { return ""; }
      return (lsGet("bb_code") || "").toUpperCase().replace(/[^A-Z0-9-]/g, "").slice(0, 12);
    } catch (e) { return ""; }
  }

  function send(type, element, beacon) {
    if (optedOut()) { return; }
    var payload = {
      page: location.pathname,
      event: type,
      element: (element || "").slice(0, 80),
      step: stepFor(location.pathname),
      ref: refHost(),
      device: device(),
      session: sid,
      code: reviewCode()
    };
    var body = JSON.stringify(payload);
    try {
      if (beacon && navigator.sendBeacon) {
        if (navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "text/plain;charset=utf-8" }))) { return; }
      }
      fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: body, keepalive: true, mode: "no-cors"
      }).catch(function () { });
    } catch (e) { /* counting never breaks the site */ }
  }

  send("pageview", "");
  var here = stepFor(location.pathname);
  if (here === "details" || here === "review" || here === "submitted") {
    send("form_step", "");
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    while (t && t !== document) {
      if (t.getAttribute) {
        var tag = t.getAttribute("data-track");
        if (tag) { send("click", tag); return; }
      }
      if (t.tagName === "A") {
        var href = t.getAttribute("href") || "";
        var base = href.split("?")[0].split("#")[0].split("/").pop();
        if (base) { send("click", "link:" + base); }
        return;
      }
      t = t.parentNode;
    }
  }, false);

  var exited = false;
  window.addEventListener("pagehide", function () {
    if (exited) { return; }
    exited = true;
    send("pageexit", "", true);
  });
})();
"""

def build_analytics():
    write("bbtrack.js", BBTRACK_JS.replace("__BB_ENDPOINT__", ANALYTICS_ENDPOINT))

def build_privacy():
    body = """
<div class="banner"><b>DRAFT — being reviewed.</b>
<p>Plain words about what this site counts and why. This page is a draft until Busy Bees' legal review is finished — the same review the Terms are going through.</p></div>
<h1>Privacy — what's counted</h1>
<p class="sub">Busy Bees counts visits on this site so we can see what's confusing and fix it before the real site launches. The counting is ours: it runs in Busy Bees' own Workspace, not through an outside analytics company, and there are no ad trackers here.</p>
<div class="card"><h2 style="margin-top:0">What we count</h2>
<ul class="tight">
<li>Which pages get opened, and roughly how many separate visits there are.</li>
<li>Which buttons and links get tapped.</li>
<li>How far a request gets — started, each step, sent, or left part-way — so we can see where people stop.</li>
<li>The page a visit ends on.</li>
<li>Whether a visit was on a phone, a tablet, or a computer — just the kind, nothing finer.</li>
<li>The name of the site that sent you here, if one did — just the name.</li>
</ul>
<p>Each visit gets a random number that lasts only for that visit. It joins that visit's own steps together (started → … → sent), it's gone when the tab closes, and it's never used to follow anyone from one day to the next. What Busy Bees sees is totals and percentages — there is no screen that shows a single person's visit.</p>
</div>
<div class="card"><h2 style="margin-top:0">What we never collect</h2>
<ul class="tight">
<li>Your name, phone number, email, or address.</li>
<li>Anything you type into any box on this site.</li>
<li>Your IP address, or anything that pinpoints where you are.</li>
<li>No advertising cookies, no trackers from other companies, nothing that follows you to other sites.</li>
<li>Nothing is sold, and nothing is shared with anyone outside Busy Bees.</li>
</ul>
</div>
<div class="card"><h2 style="margin-top:0">If you're reviewing this site</h2>
<p>If you came in through the review gate, your visits on the review pages are counted under your review code — the gate told you your activity is recorded, and the code is how your feedback gets matched to your notes. On the test site itself, visits are counted anonymously.</p>
</div>
<div class="card"><h2 style="margin-top:0">How long it's kept</h2>
<p>The detailed list is kept for 90 days. After that, only the totals stay (how many visits, which pages, where requests stopped) — the day-by-day detail is folded into monthly totals and the rest is deleted.</p>
</div>
<div class="card"><h2 style="margin-top:0">Your choice</h2>
<p id="bbTrackState">Checking this browser's setting…</p>
<button class="btn btn-dark" type="button" id="bbTrackToggle">Turn counting off for this browser</button>
<p class="note">The choice lives in this browser on this device — it doesn't need an account and it isn't sent anywhere. If your browser sends a "Do Not Track" signal, we honor that too: those visits are never counted at all.</p>
</div>
<p class="note">Questions about any of this: call or text <b>(508) 258-9899</b> · dispatch@busybeesdispatch.com</p>
<script>
(function(){
  var btn = document.getElementById("bbTrackToggle"), st = document.getElementById("bbTrackState");
  if(!btn || !st){ return; }
  function isOff(){ try { return localStorage.getItem("bb_no_track") === "1"; } catch(e){ return false; } }
  function paint(){
    if(isOff()){
      st.textContent = "Counting is OFF for this browser. This visit isn't being counted, and none will be unless you turn it back on.";
      btn.textContent = "Turn counting back on";
    } else {
      st.textContent = "Counting is ON for this browser.";
      btn.textContent = "Turn counting off for this browser";
    }
  }
  btn.addEventListener("click", function(){
    try {
      if(isOff()){ localStorage.removeItem("bb_no_track"); }
      else { localStorage.setItem("bb_no_track", "1"); }
    } catch(e){}
    paint();
  });
  paint();
})();
</script>
"""
    write("privacy.html", page("Privacy — what's counted", 0, body, gate=False))

def build_whatsnew():
    body = """
<h1>What's New</h1>
<p class="sub">Every change to Busy Bees, posted here in plain words — what changed, and what it means for you. Newest first.</p>
<p class="note">This is the practice copy of the page. On the real site this page is public, and every change lands here as it ships — nothing quiet, nothing buried.</p>
<div class="card"><p class="tag">October 31, 2026</p><h2 style="margin-top:0">The Hive — a back office for members</h2>
<p>Contractors now have their own back office, called <b>The Hive</b>: their customers, estimates, jobs, and invoices in one place — fed by the jobs they win on the board, so a job they accept shows up in their own records on its own. It even keeps track of what each job made them.</p>
<p style="margin-bottom:0">Invoices run through the contractor's own payment account: money goes straight from the customer to the contractor, and Busy Bees never holds job money and never takes a cut of it. Coming for members after that: <b>Lead Hunter</b>, an optional extra that finds local work looking for a pro. It's not on sale yet.</p></div>
<div class="card"><p class="tag">October 31, 2026</p><h2 style="margin-top:0">Your work saves as you go</h2>
<p style="margin-bottom:0">Forms and notes on this site now save on your own device while you type. Close a page halfway through a request and you can pick up right where you left off — nothing gets lost because a page closed.</p></div>
<div class="card"><p class="tag">October 31, 2026</p><h2 style="margin-top:0">A privacy page in plain words</h2>
<p style="margin-bottom:0">Busy Bees added a <a href="privacy.html"><b>privacy page</b></a> that says exactly what this site counts and why — visits are counted in Busy Bees' own system, with no outside trackers and no ad cookies — and it carries a switch to turn the counting off in your browser.</p></div>
<div class="card"><p class="tag">October 30, 2026</p><h2 style="margin-top:0">Plainer words, on purpose</h2>
<p style="margin-bottom:0">We cleaned up the board's wording: out went words that promised more than we do — no "vetted" claims, no fast-response promises. Here, "verified" means one thing only: a contractor's business paperwork is on file. Nothing more is implied, ever.</p></div>
<div class="card"><p class="tag">October 30, 2026</p><h2 style="margin-top:0">Where this starts — how Busy Bees works</h2>
<p>Busy Bees is a local dispatch board for Cape Cod. A customer picks a town, answers a few plain questions, and sends one simple request — free, always. Local contractors get matched job offers by text and pay one flat fee only when they accept a job; saying no is always free, and no contractor ever pays a percentage of the job price.</p>
<p style="margin-bottom:0">This page starts here. Every change from now on gets posted above, in the open.</p></div>
<p class="note">Questions about any change: call or text <b>(508) 258-9899</b> · dispatch@busybeesdispatch.com</p>
"""
    write("whats-new.html", page("What's New", 0, body,
          back="index.html", step="Busy Bees · What's New"))

# ------------------------------------------------------------ the hive ----
# The member tools — The Hive. The whole point of ours: it is fed by the
# board — a job a member accepts on the board lands in My Jobs and My
# Customers on its own, instead of starting from an empty screen.
# House line: "The board finds the work. The Hive is where you run it."
def build_hive():
    hub = """
<h1>The Hive</h1>
<p class="sub">Welcome back, <b>Example Tree Co</b> <span class="badge">Member</span><br>
This is the pretend member view — fake customers, fake jobs, fake money.</p>
<p><b>The board finds the work. The Hive is where you run it.</b></p>
<div class="card deal"><h2 style="margin-top:0">Fed by the board</h2>
<p style="margin-bottom:0">Every job you accept on the board lands here on its own — in <b>My Jobs</b> with the day it's booked for, and in <b>My Customers</b> with the customer's name on it. Nothing to type in twice. Work you line up yourself can be added the same way.</p></div>
<div class="card"><h2 style="margin-top:0">This week, at a glance</h2>
<div class="kv"><b>Jobs booked</b><span>3 — tree removal today, mowing route Monday, cleanup Wednesday</span></div>
<div class="kv"><b>Estimates out</b><span>2 waiting on customers · 1 approved this week</span></div>
<div class="kv"><b>Invoices open</b><span>2 — $1,820 out, $275 paid this week</span></div>
<div class="kv"><b>Follow-ups</b><span>2 due — Dana W. (stump quote) and Pat M. (spring cleanup)</span></div>
<div class="kv"><b>Your level</b><span>Level 2 · 11 board jobs done · referral reward waiting: 25% off a lead</span></div>
</div>
<a class="opt" href="backoffice-customers.html">My Customers<span class="arr">→</span><span class="d">Your own customer list — everyone the board has sent you, plus anyone you add. Yours, not the board's.</span></a>
<a class="opt" href="backoffice-estimates.html">Estimates<span class="arr">→</span><span class="d">Write it up once, send it, and the customer can approve it with one tap.</span></a>
<a class="opt" href="backoffice-jobs.html">My Jobs &amp; schedule<span class="arr">→</span><span class="d">What's booked, what day, and the notes and checklist for each job.</span></a>
<a class="opt" href="backoffice-invoices.html">Invoices &amp; getting paid<span class="arr">→</span><span class="d">Bill from a job or an estimate. Customers pay <b>you</b> — through your own payment account.</span></a>
<a class="opt" href="backoffice-costing.html">What each job made you<span class="arr">→</span><span class="d">The price minus what it cost you — the honey each job actually brought in, and a plain look at which work is worth taking.</span></a>
<a class="opt" href="backoffice-leadhunter.html" style="margin-bottom:0">Lead Hunter — coming for members<span class="arr">→</span><span class="d">A paid extra we're building: Busy Bees forages local demand and brings back work so you don't have to. Not on sale yet.</span></a>
<div class="card" style="margin-top:16px"><h2 style="margin-top:0">Tools, nothing more</h2>
<p style="margin-bottom:0">The Hive is a set of tools that comes with membership. It never changes who gets offered a board job: membership does <b>not</b> buy ranking, level, or verified status — those are earned, the same as always.</p></div>
"""
    write("contractor/backoffice.html", page("The Hive — member tools", 1, hub,
          back="join.html", step="Contractor side · The Hive"))

    customers = """
<h1>My Customers</h1>
<p class="sub">Your list, for your business. A customer lands here the moment you accept their job on the board — and you can add your own customers too. Busy Bees doesn't sell or share this list; it's yours.</p>
<a class="opt" href="backoffice-customer.html">Dana W. — Dennis<span class="arr">→</span><span class="d">Tree removal (board job, done) · <b>Follow-up due:</b> ask about the stump-grinding quote</span></a>
<a class="opt" href="backoffice-customer.html">Chidi O. — Yarmouth<span class="arr">→</span><span class="d">Weekly mowing arrangement (board job, running) · Next visit Monday</span></a>
<a class="opt" href="backoffice-customer.html">Pat M. — Harwich<span class="arr">→</span><span class="d">Fall cleanup (own customer) · <b>Follow-up due:</b> spring cleanup reminder</span></a>
<a class="opt" href="backoffice-customer.html" style="margin-bottom:0">Sam R. — Brewster<span class="arr">→</span><span class="d">Limb removal (board job, done) · Paid in full</span></a>
<p class="note">On the real site, tapping a name opens that customer's page: every job you've done for them, your private notes, and a spot to set the next follow-up. Every name here opens the same pretend example.</p>
"""
    write("contractor/backoffice-customers.html", page("My Customers", 1, customers,
          back="backoffice.html", step="The Hive · My Customers"))

    customer = """
<h1>Dana W. — Dennis</h1>
<p class="sub">Came to you through the board — tree removal, accepted and done in October.</p>
<div class="card"><h2 style="margin-top:0">Jobs with Dana</h2>
<div class="kv"><b>Oct — done</b><span>Tree removal, 2–3 trees — $1,400 · paid</span></div>
<div class="kv"><b>Waiting</b><span>Stump grinding — estimate sent, Dana is thinking it over</span></div>
<div class="kv"><b>Follow-up</b><span>Ask about the stump quote — due this week</span></div>
</div>
<div class="card"><h2 style="margin-top:0">Your notes on Dana</h2>
<p class="small">Private to you — the customer never sees these. They save on this device as you type, the same as everywhere on this test site.</p>
<form data-draft="backoffice-cust-dana">
<label>Notes<textarea name="notes" rows="3" placeholder="Gate sticks on the left. Dog is friendly. Prefers texts after 5."></textarea></label>
<label>Next follow-up<span class="hint">What to ask, and roughly when — it shows on your Hive home until you clear it.</span><input type="text" name="followup" placeholder="Text about the stump quote on Friday"></label>
</form></div>
<a class="btn btn-gold" href="backoffice-estimate-new.html">Write Dana an estimate<span class="d">For the stump grinding — or anything else she asks about.</span></a>
<a class="btn btn-ghost" href="backoffice-customers.html">Back to My Customers</a>
"""
    write("contractor/backoffice-customer.html", page("Dana W. — customer", 1, customer,
          back="backoffice-customers.html", step="The Hive · My Customers"))

    est_list = """
<h1>Estimates</h1>
<p class="sub">Quotes are always free for the customer. Write one up, send it, and they can approve it with one tap — you get told the moment they do.</p>
<a class="opt" href="backoffice-estimate-view.html">For Pat M. — fall cleanup, three ways <span class="badge">Approved</span><span class="arr">→</span><span class="d">Sent Oct 27 · Pat approved the middle option — $420</span></a>
<a class="opt" href="backoffice-estimate-view.html">For Dana W. — stump grinding <span class="badge">Sent</span><span class="arr">→</span><span class="d">Sent Oct 29 · $180 · waiting on Dana</span></a>
<a class="opt" href="backoffice-estimate-view.html">For Sam R. — brush clearing <span class="badge">Draft</span><span class="arr">→</span><span class="d">Not sent yet · $650</span></a>
<a class="opt" href="backoffice-estimate-view.html" style="margin-bottom:0">For Chidi O. — aeration &amp; overseeding <span class="badge">Declined</span><span class="arr">→</span><span class="d">Sent Oct 20 · $300 · Chidi passed — no hard feelings, it happens</span></a>
<p class="note">In this test version every estimate opens the same pretend example — Pat's approved one, the way the customer saw it.</p>
<a class="btn btn-gold" href="backoffice-estimate-new.html">Write a new estimate<span class="d">Line by line, with a running total — and room for good / better / best if the job suits it.</span></a>
"""
    write("contractor/backoffice-estimates.html", page("Estimates", 1, est_list,
          back="backoffice.html", step="The Hive · Estimates"))

    est_new = """
<h1>Write an estimate</h1>
<p class="sub">Pretend version: nothing is sent. What you type saves on this device as you go. The total adds itself up while you type.</p>
<form data-draft="backoffice-estimate" id="estForm">
<div class="card"><h2 style="margin-top:0">Who it's for</h2>
<label>Customer name<input type="text" name="cust" placeholder="Dana W."></label>
<label>Job, in plain words<input type="text" name="job" placeholder="Stump grinding — two stumps by the drive"></label>
</div>
<div class="card"><h2 style="margin-top:0">The work, line by line</h2>
<label>Line 1 — what<span class="hint">Price for this line, in dollars</span><input type="text" name="d1" placeholder="Grind both stumps below grade"></label>
<label>Line 1 — price $<input type="number" name="p1" class="est-price" min="0" step="1" placeholder="140"></label>
<label>Line 2 — what<input type="text" name="d2" placeholder="Haul away the grindings"></label>
<label>Line 2 — price $<input type="number" name="p2" class="est-price" min="0" step="1" placeholder="40"></label>
<label>Line 3 — what<input type="text" name="d3" placeholder=""></label>
<label style="margin-bottom:0">Line 3 — price $<input type="number" name="p3" class="est-price" min="0" step="1" placeholder="0"></label>
<p class="calc-out">Total: <span class="tier" id="estTotal">$0</span></p>
</div>
<div class="card"><h2 style="margin-top:0">Good / better / best — if the job suits it</h2>
<p class="small">Some jobs are easier to say yes to with a choice. Leave these empty and the estimate goes out with just the total above.</p>
<label>Good — the plain version, price $<input type="number" name="good" min="0" step="1" placeholder="150"></label>
<label>Better — the one you'd recommend, price $<input type="number" name="better" min="0" step="1" placeholder="180"></label>
<label style="margin-bottom:0">Best — everything included, price $<input type="number" name="best" min="0" step="1" placeholder="240"></label>
</div>
</form>
<a class="btn btn-gold" href="backoffice-estimate-view.html">See it the way the customer sees it<span class="d">This is the screen your customer gets — with the Approve button on it.</span></a>
<a class="btn btn-ghost" href="backoffice-estimates.html">Back to Estimates</a>
<script>
(function(){
  function money(n){ return "$" + (Math.round(n * 100) / 100).toLocaleString("en-US"); }
  function tick(){
    var t = 0;
    document.querySelectorAll(".est-price").forEach(function(el){
      var v = parseFloat(el.value); if(!isNaN(v)) t += v;
    });
    var out = document.getElementById("estTotal");
    if(out) out.textContent = money(t);
  }
  document.querySelectorAll(".est-price").forEach(function(el){
    el.addEventListener("input", tick);
  });
  tick();
})();
</script>
"""
    write("contractor/backoffice-estimate-new.html", page("Write an estimate", 1, est_new,
          back="backoffice-estimates.html", step="The Hive · Estimates · New"))

    est_view = """
<div class="banner"><b>How the customer sees it.</b>
<p>This is Pat M.'s screen, not yours — an estimate that already came back approved. Quotes are always free; approving is the customer's call, in their own time.</p></div>
<h1>Your estimate from Example Tree Co</h1>
<p class="sub">Fall cleanup — three ways to do it. Pick the one that suits you; there's no wrong answer and no rush.</p>
<div class="card"><h2 style="margin-top:0">Good — $350</h2>
<p style="margin-bottom:0">Leaves, sticks, and beds cleared; everything hauled away. The plain tidy-up.</p></div>
<div class="card deal"><h2 style="margin-top:0">Better — $420 <span class="badge">The one we'd pick</span></h2>
<p style="margin-bottom:0">Everything in Good, plus hedges trimmed and shaped while we're there.</p></div>
<div class="card"><h2 style="margin-top:0">Best — $560</h2>
<p style="margin-bottom:0">Everything in Better, plus fresh mulch in the front beds to finish it.</p></div>
<p class="note" id="estState">Pat picked <b>Better — $420</b> and approved it on Oct 27. The job landed in Example Tree Co's schedule on its own, and the invoice was ready to send from this same estimate.</p>
<button class="btn btn-gold" type="button" id="estApprove">Approve — pretend tap<span class="d">See what approving does. Nothing is sent in this test version.</span></button>
<button class="btn btn-ghost" type="button" id="estDecline">Decline — pretend tap</button>
<script>
(function(){
  var st = document.getElementById("estState");
  document.getElementById("estApprove").addEventListener("click", function(){
    st.innerHTML = "<b>Approved (pretend).</b> On the real site, Example Tree Co is told right away, the job goes on their schedule, and an invoice can be sent from this estimate with one tap.";
  });
  document.getElementById("estDecline").addEventListener("click", function(){
    st.innerHTML = "<b>Declined (pretend).</b> On the real site, Example Tree Co is told politely, and that's the end of it — declining a quote costs the customer nothing, ever.";
  });
})();
</script>
"""
    write("contractor/backoffice-estimate-view.html", page("Your estimate — customer view", 1, est_view,
          back="backoffice-estimates.html", step="The Hive · Estimates · Customer view"))

    jobs = """
<h1>My Jobs &amp; schedule</h1>
<p class="sub">Booked work, in one place. Board jobs land here the moment you accept them — your own jobs can be added too.</p>
<div class="card"><h2 style="margin-top:0">Today — Saturday</h2>
<a class="opt" href="backoffice-job.html">9:00 — Tree removal · Dana W., Dennis<span class="arr">→</span><span class="d">Board job · 2–3 trees · your notes and checklist are on the job page</span></a>
<a class="opt" href="backoffice-job.html" style="margin-bottom:0">1:00 — Hedge trim visit · Pat M., Harwich<span class="arr">→</span><span class="d">Follow-on from Pat's approved estimate</span></a>
</div>
<div class="card"><h2 style="margin-top:0">This week</h2>
<div class="kv"><b>Monday</b><span>Mowing route — Chidi O. (weekly arrangement) + two own customers</span></div>
<div class="kv"><b>Wednesday</b><span>Fall cleanup · Pat M., Harwich — from the approved estimate</span></div>
<div class="kv"><b>Friday</b><span>Stump grinding · Dana W., Dennis — if the estimate's approved by then</span></div>
</div>
<p class="note">In this test version every job opens the same pretend example — today's tree removal, with its notes, photo spots, and checklist.</p>
"""
    write("contractor/backoffice-jobs.html", page("My Jobs & schedule", 1, jobs,
          back="backoffice.html", step="The Hive · My Jobs"))

    job = """
<h1>Tree removal — Dana W.</h1>
<p class="sub">Today, 9:00 · Dennis · Board job — accepted Oct 28, details released when you accepted, like always.</p>
<div class="card"><h2 style="margin-top:0">The job</h2>
<div class="kv"><b>Work</b><span>Tree removal — 2–3 trees, back corner of the lot</span></div>
<div class="kv"><b>Your quote</b><span>$1,400 — quoted on site, it's yours to set</span></div>
<div class="kv"><b>Talking</b><span>Through the board's private relay — numbers stay hidden, same as the board</span></div>
</div>
<div class="card"><h2 style="margin-top:0">On-the-day checklist</h2>
<p class="small">Ticks save on this device, for this job.</p>
<div id="jobChecks">
<label><input type="checkbox" data-chk="gear"> Saws, ropes, and the chipper loaded</label>
<label><input type="checkbox" data-chk="look"> Walk the lot first — wires, fences, the neighbor's shed</label>
<label><input type="checkbox" data-chk="photos"> Before photos taken</label>
<label><input type="checkbox" data-chk="done"> Yard left tidy — grindings raked, gate closed</label>
<label style="margin-bottom:0"><input type="checkbox" data-chk="invoiced"> Invoice sent (or marked ready to send)</label>
</div></div>
<div class="card"><h2 style="margin-top:0">Photos</h2>
<p style="margin-bottom:0" class="note">📷 Before — <i>spot reserved</i> &nbsp;·&nbsp; 📷 After — <i>spot reserved</i><br>
On the real site, photos you take on the job land here, on the job — handy when a customer asks what was done.</p></div>
<div class="card"><h2 style="margin-top:0">Job notes</h2>
<form data-draft="backoffice-job-dana">
<label>Notes<textarea name="notes" rows="3" placeholder="Leaner over the back fence — drop it in pieces. Chipper fits through the side gate."></textarea></label>
</form></div>
<a class="btn btn-gold" href="backoffice-invoice.html">Invoice for this job<span class="d">Bill Dana from this job — most of it's already filled in.</span></a>
<a class="btn btn-ghost" href="backoffice-jobs.html">Back to My Jobs</a>
<script>
(function(){
  var KEY = "bb_backoffice_chk_v1:dana-tree";
  var saved = {};
  try{ saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; }catch(e){}
  document.querySelectorAll("#jobChecks input[data-chk]").forEach(function(box){
    var k = box.getAttribute("data-chk");
    box.checked = !!saved[k];
    box.addEventListener("change", function(){
      saved[k] = box.checked;
      try{ localStorage.setItem(KEY, JSON.stringify(saved)); }catch(e){}
    });
  });
})();
</script>
"""
    write("contractor/backoffice-job.html", page("Tree removal — Dana W.", 1, job,
          back="backoffice-jobs.html", step="The Hive · My Jobs · Job"))

    inv_list = """
<h1>Invoices &amp; getting paid</h1>
<p class="sub">Bill from a job or straight from an estimate. When a customer pays, the money goes to <b>your own payment account</b> — Busy Bees is never the one holding your job money, and never takes a cut of it.</p>
<a class="opt" href="backoffice-invoice.html">Invoice 202 — Dana W. · Tree removal <span class="badge">Sent</span><span class="arr">→</span><span class="d">$1,400 · sent Oct 28 · a polite nudge went out Oct 30</span></a>
<a class="opt" href="backoffice-invoice.html">Invoice 201 — Pat M. · Fall cleanup <span class="badge">Sent</span><span class="arr">→</span><span class="d">$420 · sent Oct 27 · due Nov 7</span></a>
<a class="opt" href="backoffice-invoice.html">Invoice 198 — Sam R. · Limb removal <span class="badge">Paid</span><span class="arr">→</span><span class="d">$275 · paid Oct 22 — straight into the contractor's own account</span></a>
<a class="opt" href="backoffice-invoice.html" style="margin-bottom:0">Invoice 203 — Sam R. · Brush clearing <span class="badge">Draft</span><span class="arr">→</span><span class="d">$650 · made from the draft estimate · not sent</span></a>
<p class="note">An invoice that runs past its due date shows as <b>Overdue</b> here, and The Hive offers a firmer follow-up wording — the words stay polite; the timing does the work. In this test version every invoice opens the same pretend example — Dana's.</p>
"""
    write("contractor/backoffice-invoices.html", page("Invoices & getting paid", 1, inv_list,
          back="backoffice.html", step="The Hive · Invoices"))

    invoice = """
<h1>Invoice 202 — Dana W.</h1>
<p class="sub">Tree removal, Dennis · Made from the finished job, most of it filled in on its own.</p>
<div class="card"><h2 style="margin-top:0">What's on it</h2>
<div class="kv"><b>Work</b><span>Tree removal — 2–3 trees, hauled away</span></div>
<div class="kv"><b>Amount</b><span class="fee" style="font-size:19px">$1,400</span></div>
<div class="kv"><b>Sent</b><span>Oct 28 · Due Nov 4</span></div>
<div class="kv"><b>Standing</b><span>Sent — one polite follow-up already out (Oct 30)</span></div>
</div>
<div class="card deal"><h2 style="margin-top:0">How Dana pays</h2>
<p>Dana gets a payment link with the invoice. It runs through <b>your own connected payment account</b> — the money lands with you, and Busy Bees never touches it and never takes a percentage of your job. (This test version shows the link's place only — it's in test mode and moves no money.)</p>
<p class="fee" style="font-size:16px">Payment link: pay.example…/inv-202 <span class="badge">Test mode</span></p>
<p style="margin-bottom:0" class="small">The small card-processing fee your payment provider charges is theirs, not ours — it's shown to you plainly before you connect an account.</p></div>
<div class="card"><h2 style="margin-top:0">Follow-ups, handled gently</h2>
<ul class="tight">
<li><b>Sent</b> — Oct 28, with the payment link.</li>
<li><b>Polite nudge</b> — sent Oct 30 (the wording stays friendly: "just floating this back to the top of your inbox").</li>
<li><b>If it's not paid by Nov 4</b> — it shows as overdue, and a firmer note is ready for you to approve and send. Nothing ever goes out without your say.</li>
</ul></div>
<button class="btn btn-gold" type="button" id="invPaid">Mark it paid — pretend tap<span class="d">For cash or a check at the door. On the real site this closes the invoice and updates what the job made you.</span></button>
<p class="note" id="invState"></p>
<script>
(function(){
  document.getElementById("invPaid").addEventListener("click", function(){
    document.getElementById("invState").innerHTML = "<b>Marked paid (pretend).</b> On the real site the invoice closes, Dana drops off your follow-ups, and the job's page shows the money in.";
  });
})();
</script>
"""
    write("contractor/backoffice-invoice.html", page("Invoice 202 — Dana W.", 1, invoice,
          back="backoffice-invoices.html", step="The Hive · Invoices · Invoice"))

    costing = """
<h1>What each job made you</h1>
<p class="sub">The price you charged, minus what the job cost you — your hours, materials, fuel, and the board's flat fee where there was one. Plain arithmetic, no jargon — this is the honey each job brought in, counted honestly, so the good work stands out from the busy work.</p>
<div class="card"><h2 style="margin-top:0">Tree removal — Dana W. · October</h2>
<div class="kv"><b>You charged</b><span>$1,400</span></div>
<div class="kv"><b>It cost you</b><span>$585 — your hours $390 · dump fees $120 · fuel $45 · board fee $30</span></div>
<div class="kv"><b>It made you</b><span><b>$815</b> — about 58¢ of every dollar stayed with you</span></div>
</div>
<div class="card"><h2 style="margin-top:0">Fall cleanup — Pat M. · October</h2>
<div class="kv"><b>You charged</b><span>$420</span></div>
<div class="kv"><b>It cost you</b><span>$225 — your hours $180 · mulch &amp; bags $25 · board fee $20</span></div>
<div class="kv"><b>It made you</b><span><b>$195</b> — about 46¢ of every dollar</span></div>
</div>
<div class="card"><h2 style="margin-top:0">Weekly mowing — Chidi O. · per month</h2>
<div class="kv"><b>You charge</b><span>$260 a month</span></div>
<div class="kv"><b>It costs you</b><span>$175 — your hours $140 · fuel $10 · board fee $25 (once, for the whole arrangement)</span></div>
<div class="kv"><b>It makes you</b><span><b>$85</b> a month — about 33¢ of every dollar</span></div>
<p style="margin-bottom:0" class="small">Repeat work always looks thinner per visit — the board fee lands once, and the route gets faster as you learn the lawns.</p></div>
<p class="note">Your hours are figured at the rate you set for yourself in your settings — change the rate and every job re-figures. Only you see these numbers; they're never shared, ranked, or shown to customers.</p>
"""
    write("contractor/backoffice-costing.html", page("What each job made you", 1, costing,
          back="backoffice.html", step="The Hive · What each job made you"))

    leadhunter = """
<h1>Lead Hunter</h1>
<p class="sub">A paid extra for members, still being built. This page is a first look — <b>it is not on sale, and there's no price on it yet</b>. When it opens, members will hear first.</p>
<div class="card deal"><h2 style="margin-top:0">What it will do</h2>
<p>The board already sees more local demand than it can fill — requests in towns with no contractor yet, jobs that got turned away, people asking around in local groups and search. <b>Lead Hunter will forage those signals for you</b> — the way bees range out and bring back what the hive needs, it works that demand and brings back the jobs that check out:</p>
<ul class="tight">
<li>It watches for local people saying they need work done — on the board, in public local posts, in local search.</li>
<li>It reaches out, confirms it's a real homeowner with a real job, and books the conversation — or the visit — for you.</li>
<li>A lead it brings you is <b>yours alone</b>. It's never handed to a second contractor, never resold, and never mixed into the board's regular offers.</li>
<li>You only ever hear about the ones that check out — real person, real job, local.</li>
</ul></div>
<div class="card"><h2 style="margin-top:0">Why it's a member extra</h2>
<p style="margin-bottom:0">Finding and chasing work takes hours a week. Lead Hunter is Busy Bees doing that legwork as an optional paid bonus for members — separate from board jobs, which keep working exactly the way they do now, fee-only-on-accept and all. It will never change who gets board offers: hunting is a service on top, not a louder voice in the line.</p></div>
<div class="card"><h2 style="margin-top:0">Want first word?</h2>
<p id="lhState">Tell us and we'll let you know the moment Lead Hunter opens for members — what it costs, what counts as a lead, all of it in plain words before anyone's asked for a cent.</p>
<button class="btn btn-gold" type="button" id="lhBtn">Notify me — pretend tap<span class="d">On the real site this saves your interest. Nothing is bought, nothing is owed.</span></button>
</div>
<script>
(function(){
  var KEY = "bb_leadhunter_interest_v1";
  var btn = document.getElementById("lhBtn"), st = document.getElementById("lhState");
  function paint(on){
    if(on){
      st.innerHTML = "<b>You're on the list (pretend).</b> When Lead Hunter opens, members on this list hear first — with the full plain-words rundown before anything goes on sale.";
      btn.firstChild.textContent = "You're on the list — tap to undo ";
    }
  }
  var on = false;
  try{ on = localStorage.getItem(KEY) === "1"; }catch(e){}
  if(on) paint(true);
  btn.addEventListener("click", function(){
    on = !on;
    try{ localStorage.setItem(KEY, on ? "1" : "0"); }catch(e){}
    if(on){ paint(true); }
    else {
      st.textContent = "Taken off the list. You can put yourself back on any time — the button remembers nothing but your word.";
      btn.firstChild.textContent = "Notify me — pretend tap ";
    }
  });
})();
</script>
"""
    write("contractor/backoffice-leadhunter.html", page("Lead Hunter — coming for members", 1, leadhunter,
          back="backoffice.html", step="The Hive · Lead Hunter — not on sale yet"))

# ------------------------------------------------------------------ main --
def main():
    build_home()
    build_town()
    build_category()
    build_job_pages()
    build_job_screens()
    build_other()
    build_details()
    build_review()
    build_sent()
    build_cart()
    build_account()
    build_account_home()
    build_premium()
    build_premium_on()
    build_contractor()
    build_future_trades()
    build_membership()
    build_member_welcome()
    build_hive()
    build_ownpage()
    build_levels()
    build_founding()
    build_dispatch()
    build_areas()
    build_almanac()
    build_almanac_article()
    build_analytics()
    build_privacy()
    build_whatsnew()
    print("done")

if __name__ == "__main__":
    main()
