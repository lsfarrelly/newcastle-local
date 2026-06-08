#!/usr/bin/env python3
"""
generate.py — NewcastleLocal site generator
────────────────────────────────────────────
Reads data/psychologists.json and generates:
  - profiles/psychologists/{slug}.html  (one per listing)
  - psychologists.html                  (updated directory page)

Run after any change to the JSON:
  python generate.py

Then push to GitHub → Netlify auto-deploys.
"""

import json, os, re
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "psychologists.json")
PROFILES_DIR = os.path.join(BASE, "profiles", "psychologists")
DIRECTORY_FILE = os.path.join(BASE, "psychologists.html")

# ── LOAD DATA ────────────────────────────────────────────────────────────────

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]
os.makedirs(PROFILES_DIR, exist_ok=True)

# ── SHARED HTML FRAGMENTS ────────────────────────────────────────────────────

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">'

def header(active=""):
    return f"""
<header class="site-header">
  <div class="site-header-inner">
    <a href="/index.html" class="site-logo">Newcastle<span>Local</span></a>
    <nav><ul class="site-nav">
      <li><a href="/psychologists.html" {"style='color:#fff'" if active=='health' else ''}>Health</a></li>
      <li><a href="#">Trades</a></li>
      <li><a href="#">Legal</a></li>
      <li><a href="#">Finance</a></li>
      <li><a href="#">NDIS</a></li>
      <li><a href="/list.html" style="color:var(--gold)">List Your Business</a></li>
    </ul></nav>
  </div>
</header>"""

def footer():
    return """
<footer>
  <div class="footer-inner">
    <a href="/index.html" style="font-family:'Playfair Display',serif;color:#fff;font-size:16px;text-decoration:none;">Newcastle<span style="color:var(--gold)">Local</span></a>
    <div class="footer-links">
      <a href="#">About</a>
      <a href="/list.html">List Your Practice</a>
      <a href="#">Privacy</a>
      <a href="#">Contact</a>
    </div>
    <div>© 2025 NewcastleLocal · Not a medical referral service · Data sourced from public records</div>
  </div>
</footer>"""

GOOGLE_ICON = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>"""

# ── PROFILE PAGE GENERATOR ───────────────────────────────────────────────────

def generate_profile(l):
    status = l.get("status", "accepting" if l.get("accepting") else "waitlist")
    accepting_class = "open" if status == "accepting" else "waitlist"
    accepting_text  = "✓ Accepting new clients" if status == "accepting" else ("⏱ Currently on waitlist" if status == "waitlist" else "")
    accepting_color = "#e8f5e9" if status == "accepting" else ("#fff3e0" if status == "waitlist" else "transparent")
    accepting_tc    = "#2e7d32" if status == "accepting" else ("#e65100" if status == "waitlist" else "transparent")

    tags_html = "".join(f'<span class="tag">{s}</span>' for s in l["specialties"])
    if l["telehealth"]:
        tags_html += '<span class="tag telehealth">Telehealth</span>'

    ref_html = " · ".join(l["referral_types"])

    website_btn = f'<a href="/profiles/psychologists/{l["slug"]}.html" class="btn-primary" style="display:inline-block;width:auto;padding:12px 28px;">View Profile</a>'
    visit_website_btn = ""
    if l.get("website"):
        visit_website_btn = f'<a href="{l["website"]}" target="_blank" rel="noopener" class="btn-secondary" style="display:inline-block;width:auto;padding:11px 28px;">Visit Website</a>'

    email_btn = ""
    if l.get("email"):
        email_btn = f'<a href="mailto:{l["email"]}" class="btn-secondary" style="display:inline-block;width:auto;padding:11px 28px;">Send Email</a>'

    phone_html = f'<div class="detail-row"><span class="detail-icon">📞</span><span>{l["phone"]}</span></div>' if l.get("phone") else ""
    email_html = f'<div class="detail-row"><span class="detail-icon">✉️</span><a href="mailto:{l["email"]}" style="color:var(--accent)">{l["email"]}</a></div>' if l.get("email") else ""
    web_html   = f'<div class="detail-row"><span class="detail-icon">🌐</span><a href="{l["website"]}" target="_blank" rel="noopener" style="color:var(--accent)">{l["website"].replace("https://","")}</a></div>' if l.get("website") else ""
    fee_html   = f'<div class="detail-row"><span class="detail-icon">💲</span><span>{l["fee_note"]}</span></div>' if l.get("fee_note") else ""

    long_desc = l.get("long_description", l["description"])
    paras = "".join(f"<p>{p.strip()}</p>" for p in long_desc.split("\n\n") if p.strip())

    google_url = f"https://www.google.com/search?q={l['google_search'].replace(' ', '+')}"
    update_url = f"/update/index.html?slug={l['slug']}&key={l['secret_key']}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{l["name"]} — Newcastle Psychologist | NewcastleLocal</title>
<meta name="description" content="{l['description']} Located in {l['suburb']}, Newcastle NSW.">
<link rel="stylesheet" href="/css/style.css">
{FONTS}
<style>
  .profile-hero {{
    background: var(--ink); padding: 56px 24px 64px; position: relative; overflow: hidden;
  }}
  .profile-hero::before {{
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 360px; height: 360px; border-radius: 50%;
    background: radial-gradient(circle, rgba(45,95,78,0.15) 0%, transparent 70%);
  }}
  .profile-hero-inner {{ max-width: 1100px; margin: 0 auto; }}
  .profile-back {{ color: #888; font-size: 13px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 24px; transition: color 0.15s; }}
  .profile-back:hover {{ color: #fff; }}
  .profile-name {{ font-family: 'Playfair Display', serif; font-size: clamp(28px,4vw,46px); color: #fff; line-height: 1.1; margin-bottom: 8px; }}
  .profile-credentials {{ color: #aaa; font-size: 14px; margin-bottom: 20px; }}
  .profile-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 20px; }}
  .profile-status {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 18px; border-radius: 3px; font-size: 13px; font-weight: 600;
    background: {accepting_color}; color: {accepting_tc};
  }}

  .profile-body {{ max-width: 1100px; margin: 0 auto; padding: 48px 24px; display: grid; grid-template-columns: 1fr 300px; gap: 48px; align-items: start; }}

  .profile-section {{ margin-bottom: 36px; }}
  .profile-section h2 {{ font-family: 'Playfair Display', serif; font-size: 22px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--rule); }}
  .profile-section p {{ font-size: 15px; color: #444; line-height: 1.8; margin-bottom: 12px; }}

  .detail-card {{ background: var(--warm-white); border: 1px solid var(--rule); border-radius: 4px; padding: 24px; position: sticky; top: 80px; }}
  .detail-card h3 {{ font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 18px; }}
  .detail-row {{ display: flex; align-items: flex-start; gap: 10px; font-size: 14px; color: var(--ink); margin-bottom: 14px; line-height: 1.5; }}
  .detail-icon {{ font-size: 16px; flex-shrink: 0; margin-top: 1px; }}
  .detail-divider {{ border: none; border-top: 1px solid var(--rule); margin: 18px 0; }}
  .referral-list {{ display: flex; flex-wrap: wrap; gap: 5px; }}
  .ref-chip {{ padding: 3px 10px; background: var(--cream); border-radius: 2px; font-size: 12px; color: var(--muted); }}

  .btn-group {{ display: flex; flex-direction: column; gap: 8px; margin-top: 18px; }}

  .update-link {{ display: block; text-align: center; font-size: 11px; color: var(--muted); text-decoration: none; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--rule); }}
  .update-link:hover {{ color: var(--accent); }}
  .delete-link {{ display: block; text-align: center; font-size: 11px; color: #c62828; text-decoration: none; margin-top: 8px; }}
  .delete-link:hover {{ text-decoration: underline; }}

  @media (max-width: 768px) {{
    .profile-body {{ grid-template-columns: 1fr; }}
    .detail-card {{ position: static; }}
  }}
</style>
</head>
<body>
{header("health")}

<div class="breadcrumb-bar">
  <div class="breadcrumb-inner">
    <a href="/index.html">Home</a><span>/</span>
    <a href="/psychologists.html">Psychologists</a><span>/</span>
    {l["name"]}
  </div>
</div>

<section class="profile-hero">
  <div class="profile-hero-inner">
    <a href="/psychologists.html" class="profile-back">← Back to all psychologists</a>
    <div class="profile-name">{l["name"]}</div>
    <div class="profile-credentials">{l["credentials"]}</div>
    <div class="profile-tags">{tags_html}</div>
    {"<div class='profile-status'>" + accepting_text + "</div>" if accepting_text else ""}
  </div>
</section>

<div class="profile-body">
  <div>
    <div class="profile-section">
      <h2>About {l["name"]}</h2>
      {paras}
    </div>

    <div class="profile-section">
      <h2>Specialties</h2>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        {"".join(f'<span class="tag" style="font-size:13px;padding:5px 12px;">{s}</span>' for s in l["specialties"])}
      </div>
    </div>

    <div class="profile-section">
      <h2>Referral &amp; Funding Types</h2>
      <div class="referral-list">
        {"".join(f'<span class="ref-chip">{r}</span>' for r in l["referral_types"])}
      </div>
      <p style="margin-top:14px;font-size:13px;color:var(--muted);">
        Most clients attend under a Mental Health Care Plan (MHCP) from their GP, which provides Medicare rebates for up to 10 sessions per calendar year. Private clients are also welcome without a referral.
      </p>
    </div>
  </div>

  <aside>
    <div class="detail-card">
      <h3>Contact &amp; Location</h3>
      <div class="detail-row"><span class="detail-icon">📍</span><span>{l["address"]}</span></div>
      {phone_html}
      {email_html}
      {web_html}
      {fee_html}
      <hr class="detail-divider">
      <div class="detail-row"><span class="detail-icon">🕐</span><span>{l.get("hours","Mon–Fri")}</span></div>
      <div class="detail-row"><span class="detail-icon">💻</span><span>{"Telehealth available" if l["telehealth"] else "In-person only"}</span></div>
      <hr class="detail-divider">
      <div class="btn-group">
        {website_btn}
        {email_btn}
        <a href="{google_url}" target="_blank" rel="noopener" class="btn-secondary" style="display:inline-flex;align-items:center;justify-content:center;gap:6px;width:100%;">
          {GOOGLE_ICON} See Google Reviews
        </a>
      </div>
      <a href="{update_url}" class="update-link">Are you the owner? Update your listing →</a>
      <a href="/.netlify/functions/delete-listing?slug={l['slug']}&key={l['secret_key']}" style="display:block;text-align:center;font-size:11px;color:#c62828;text-decoration:none;margin-top:8px;">Remove this listing</a>
    </div>
  </aside>
</div>

{footer()}
</body>
</html>"""

# ── DIRECTORY PAGE GENERATOR ─────────────────────────────────────────────────

def listing_js_array(listings):
    """Build the JS listings array for the directory page."""
    items = []
    for l in listings:
        spec  = json.dumps(l["specialties"])
        refs  = json.dumps(l["referral_types"])
        web   = json.dumps(l.get("website") or "")
        phone = json.dumps(l.get("phone") or "")
        fee   = json.dumps(l.get("fee_note") or "")
        gs    = json.dumps(l.get("google_search",""))
        items.append(f"""  {{
    id:{l["id"]},slug:{json.dumps(l["slug"])},name:{json.dumps(l["name"])},
    credentials:{json.dumps(l["credentials"])},suburb:{json.dumps(l["suburb"])},
    address:{json.dumps(l["address"])},phone:{phone},website:{web},
    google_search:{gs},specialties:{spec},referral_types:{refs},
    telehealth:{"true" if l["telehealth"] else "false"},
    accepting:{"true" if l["accepting"] else "false"},
    hours:{json.dumps(l.get("hours","Mon–Fri"))},
    description:{json.dumps(l["description"])},
    fee_note:{fee},
    featured:{"true" if l.get("featured") else "false"}
  }}""")
    return "[\n" + ",\n".join(items) + "\n]"

total    = len(listings)
accepting = sum(1 for l in listings if l["accepting"])
suburbs   = len(set(l["suburb"] for l in listings))

def generate_directory(listings):
    js_array = listing_js_array(listings)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Psychologists in Newcastle NSW — Find &amp; Compare | NewcastleLocal</title>
<meta name="description" content="Find AHPRA-registered psychologists in Newcastle NSW. Compare by suburb, specialty, and availability. Includes telehealth and NDIS options.">
<link rel="stylesheet" href="css/style.css">
{FONTS}
<style>
  .hero {{ background:var(--ink); padding:64px 24px 80px; position:relative; overflow:hidden; }}
  .hero::before {{ content:''; position:absolute; top:-60px; right:-60px; width:400px; height:400px; border-radius:50%; background:radial-gradient(circle,rgba(45,95,78,0.18) 0%,transparent 70%); pointer-events:none; }}
  .hero-inner {{ max-width:1100px; margin:0 auto; }}
  .hero-eyebrow {{ display:inline-flex; align-items:center; gap:8px; font-size:11px; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:var(--gold); margin-bottom:20px; }}
  .hero-eyebrow::before {{ content:''; display:block; width:24px; height:1px; background:var(--gold); }}
  .hero h1 {{ font-family:'Playfair Display',serif; font-size:clamp(32px,5vw,54px); color:#fff; line-height:1.1; max-width:640px; margin-bottom:18px; }}
  .hero h1 em {{ font-style:italic; color:var(--gold); }}
  .hero-sub {{ color:#aaa; font-size:16px; max-width:500px; margin-bottom:32px; font-weight:300; line-height:1.7; }}
  .search-bar {{ display:flex; max-width:620px; border:1.5px solid #444; border-radius:4px; overflow:hidden; background:#252525; }}
  .search-bar input {{ flex:1; padding:13px 18px; background:transparent; border:none; color:#fff; font-family:'DM Sans',sans-serif; font-size:15px; outline:none; }}
  .search-bar input::placeholder {{ color:#555; }}
  .search-bar select {{ padding:13px 14px; background:#333; border:none; border-left:1px solid #444; color:#ccc; font-family:'DM Sans',sans-serif; font-size:13px; outline:none; cursor:pointer; }}
  .search-bar button {{ padding:13px 22px; background:var(--accent); border:none; color:#fff; font-family:'DM Sans',sans-serif; font-size:14px; font-weight:500; cursor:pointer; transition:background 0.2s; }}
  .search-bar button:hover {{ background:#3a7a63; }}
  .hero-stats {{ display:flex; gap:32px; margin-top:32px; }}
  .stat-item {{ color:#888; font-size:13px; }}
  .stat-item strong {{ display:block; font-size:20px; color:#fff; font-weight:500; margin-bottom:2px; }}

  .main-wrap {{ max-width:1100px; margin:0 auto; padding:48px 24px; display:grid; grid-template-columns:250px 1fr; gap:36px; align-items:start; }}
  .sidebar {{ position:sticky; top:72px; }}
  .filter-panel {{ background:var(--warm-white); border:1px solid var(--rule); border-radius:4px; overflow:hidden; }}
  .filter-panel-header {{ padding:14px 18px; border-bottom:1px solid var(--rule); display:flex; justify-content:space-between; align-items:center; }}
  .filter-panel-header h3 {{ font-size:11px; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); }}
  .clear-btn {{ font-size:12px; color:var(--accent); font-weight:500; cursor:pointer; background:none; border:none; padding:0; font-family:'DM Sans',sans-serif; }}
  .filter-section {{ padding:18px; border-bottom:1px solid var(--rule); }}
  .filter-section:last-child {{ border-bottom:none; }}
  .filter-label {{ font-size:11px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin-bottom:10px; }}
  .filter-chip-group {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .chip {{ padding:4px 11px; border:1px solid var(--rule); border-radius:20px; font-size:12px; cursor:pointer; background:#fff; transition:all 0.15s; color:var(--ink); white-space:nowrap; font-family:'DM Sans',sans-serif; user-select:none; }}
  .chip:hover {{ border-color:var(--accent); color:var(--accent); }}
  .chip.active {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
  .filter-checkbox {{ display:flex; align-items:center; gap:10px; margin-bottom:9px; cursor:pointer; font-size:13px; color:var(--ink); }}
  .filter-checkbox input {{ accent-color:var(--accent); }}

  .results-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid var(--rule); }}
  .results-count {{ font-family:'Playfair Display',serif; font-size:20px; }}
  .results-count span {{ color:var(--muted); font-size:14px; font-family:'DM Sans',sans-serif; font-weight:300; }}
  .sort-select {{ padding:7px 12px; border:1px solid var(--rule); border-radius:4px; background:#fff; font-family:'DM Sans',sans-serif; font-size:13px; color:var(--ink); outline:none; cursor:pointer; }}

  .listing-card {{ background:var(--warm-white); border:1px solid var(--rule); border-radius:4px; padding:26px; margin-bottom:14px; display:grid; grid-template-columns:1fr 160px; gap:20px; transition:border-color 0.2s,box-shadow 0.2s; animation:fadeUp 0.4s ease both; }}
  .listing-card:hover {{ border-color:#b5c9c2; box-shadow:0 4px 20px rgba(45,95,78,0.07); }}
  .listing-name {{ font-family:'Playfair Display',serif; font-size:19px; margin-bottom:3px; line-height:1.2; }}
  .listing-name a {{ color:var(--ink); text-decoration:none; transition:color 0.15s; }}
  .listing-name a:hover {{ color:var(--accent); }}
  .listing-credentials {{ font-size:12px; color:var(--muted); margin-bottom:10px; }}
  .listing-tags {{ display:flex; flex-wrap:wrap; gap:5px; margin-bottom:10px; }}
  .listing-meta {{ display:flex; flex-wrap:wrap; gap:14px; font-size:12px; color:var(--muted); margin-bottom:10px; }}
  .listing-excerpt {{ font-size:13px; color:#555; line-height:1.65; border-top:1px solid var(--rule); padding-top:10px; }}
  .listing-right {{ display:flex; flex-direction:column; align-items:flex-end; gap:10px; }}
  .google-reviews-link {{ display:inline-flex; align-items:center; gap:5px; font-size:12px; color:var(--muted); text-decoration:none; transition:color 0.15s; }}
  .google-reviews-link:hover {{ color:#4285F4; }}
  .no-results {{ text-align:center; padding:60px 20px; color:var(--muted); }}
  .no-results h3 {{ font-family:'Playfair Display',serif; font-size:22px; margin-bottom:10px; color:var(--ink); }}

  .seo-block {{ background:var(--cream); border-top:1px solid var(--rule); padding:56px 24px; }}
  .seo-inner {{ max-width:1100px; margin:0 auto; display:grid; grid-template-columns:1fr 1fr; gap:56px; }}
  .seo-block h2 {{ font-family:'Playfair Display',serif; font-size:26px; margin-bottom:14px; }}
  .seo-block p {{ font-size:14px; color:#555; line-height:1.8; margin-bottom:10px; }}
  .faq-item {{ border-bottom:1px solid var(--rule); padding:14px 0; }}
  .faq-q {{ font-weight:500; font-size:14px; margin-bottom:6px; display:flex; justify-content:space-between; gap:10px; cursor:pointer; }}
  .faq-q::after {{ content:'+'; color:var(--accent); font-size:18px; flex-shrink:0; }}
  .faq-a {{ font-size:13px; color:#555; line-height:1.7; }}

  @media (max-width:768px) {{
    .main-wrap {{ grid-template-columns:1fr; }}
    .sidebar {{ position:static; }}
    .listing-card {{ grid-template-columns:1fr; }}
    .listing-right {{ align-items:flex-start; flex-direction:row; flex-wrap:wrap; }}
    .seo-inner {{ grid-template-columns:1fr; }}
    .hero-stats {{ flex-wrap:wrap; gap:18px; }}
  }}
</style>
</head>
<body>
{header("health")}
<div class="breadcrumb-bar">
  <div class="breadcrumb-inner">
    <a href="index.html">Home</a><span>/</span>
    <a href="#">Health &amp; Wellbeing</a><span>/</span>
    Psychologists in Newcastle NSW
  </div>
</div>
<section class="hero">
  <div class="hero-inner">
    <div class="hero-eyebrow">Newcastle NSW Directory</div>
    <h1>Find a <em>Psychologist</em><br>in Newcastle</h1>
    <p class="hero-sub">Compare local psychologists by specialty, suburb, and availability. All practitioners are registered with AHPRA.</p>
    <div class="search-bar">
      <input type="text" id="searchInput" placeholder="Search by name, suburb, or specialty…">
      <select id="suburbFilter">
        <option value="">All Suburbs</option>
        {"".join(f'<option value="{s}">{s}</option>' for s in sorted(set(l["suburb"] for l in listings)))}
      </select>
      <button onclick="applyFilters()">Search</button>
    </div>
    <div class="hero-stats">
      <div class="stat-item"><strong id="statTotal">{total}</strong> Listed practices</div>
      <div class="stat-item"><strong>{suburbs}</strong> Suburbs covered</div>
      <div class="stat-item"><strong id="statAccepting">{accepting}</strong> Accepting new clients</div>
    </div>
  </div>
</section>

<div class="main-wrap">
  <aside class="sidebar">
    <div class="filter-panel">
      <div class="filter-panel-header">
        <h3>Filters</h3>
        <button class="clear-btn" onclick="clearFilters()">Clear all</button>
      </div>
      <div class="filter-section">
        <div class="filter-label">Availability</div>
        <div class="filter-chip-group">
          <div class="chip" data-filter="accepting" onclick="toggleChip(this)">Accepting clients</div>
          <div class="chip" data-filter="telehealth" onclick="toggleChip(this)">Telehealth</div>
        </div>
      </div>
      <div class="filter-section">
        <div class="filter-label">Specialty</div>
        <div class="filter-chip-group">
          <div class="chip" data-filter="Anxiety" onclick="toggleChip(this)">Anxiety</div>
          <div class="chip" data-filter="Depression" onclick="toggleChip(this)">Depression</div>
          <div class="chip" data-filter="Trauma" onclick="toggleChip(this)">Trauma &amp; PTSD</div>
          <div class="chip" data-filter="ADHD" onclick="toggleChip(this)">ADHD</div>
          <div class="chip" data-filter="Child" onclick="toggleChip(this)">Child &amp; Adolescent</div>
          <div class="chip" data-filter="Relationships" onclick="toggleChip(this)">Relationships</div>
          <div class="chip" data-filter="Grief" onclick="toggleChip(this)">Grief &amp; Loss</div>
          <div class="chip" data-filter="Eating" onclick="toggleChip(this)">Eating Disorders</div>
          <div class="chip" data-filter="OCD" onclick="toggleChip(this)">OCD</div>
          <div class="chip" data-filter="EMDR" onclick="toggleChip(this)">EMDR</div>
        </div>
      </div>
      <div class="filter-section">
        <div class="filter-label">Referral type</div>
        <div class="filter-chip-group">
          <div class="chip" data-filter="MHCP" onclick="toggleChip(this)">MHCP</div>
          <div class="chip" data-filter="NDIS" onclick="toggleChip(this)">NDIS</div>
          <div class="chip" data-filter="EAP" onclick="toggleChip(this)">EAP</div>
          <div class="chip" data-filter="WorkCover" onclick="toggleChip(this)">WorkCover</div>
          <div class="chip" data-filter="DVA" onclick="toggleChip(this)">DVA</div>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-checkbox"><input type="checkbox" id="chkTelehealth" onchange="applyFilters()"> Telehealth available</label>
        <label class="filter-checkbox"><input type="checkbox" id="chkAccepting" onchange="applyFilters()"> Accepting new clients</label>
      </div>
    </div>
  </aside>
  <main>
    <div class="results-header">
      <div class="results-count"><span id="resultsCount">{total}</span> Psychologists <span>in Newcastle NSW</span></div>
      <select class="sort-select" id="sortSelect" onchange="applyFilters()">
        <option value="name">Sort: A–Z</option>
        <option value="accepting">Sort: Accepting first</option>
        <option value="telehealth">Sort: Telehealth first</option>
      </select>
    </div>
    <div id="listingsContainer"></div>
  </main>
</div>

<section class="seo-block">
  <div class="seo-inner">
    <div>
      <h2>Finding a Psychologist in Newcastle</h2>
      <p>Newcastle and the broader Hunter Region has a growing network of registered psychologists offering a wide range of services — from anxiety and depression through to specialist eating disorder treatment, ADHD assessment, and trauma therapy.</p>
      <p>Most psychologists in Newcastle accept referrals under a Mental Health Care Plan (MHCP) from your GP, which entitles you to Medicare rebates on up to 10 individual sessions per calendar year.</p>
      <p>Telehealth options have expanded significantly, meaning you can access Newcastle-based psychologists from anywhere across NSW.</p>
      <p style="margin-top:20px;"><a href="list.html" style="color:var(--accent);font-weight:500;">Are you a psychologist in Newcastle? Get listed free →</a></p>
    </div>
    <div>
      <h2>Frequently Asked Questions</h2>
      <div class="faq-item"><div class="faq-q">Do I need a GP referral to see a psychologist?</div><div class="faq-a">No — you can self-refer as a private client. However, a GP referral with a Mental Health Care Plan unlocks Medicare rebates.</div></div>
      <div class="faq-item"><div class="faq-q">What's the difference between a psychologist and a psychiatrist?</div><div class="faq-a">Psychologists are trained in assessment and therapy. Psychiatrists are medical doctors who can prescribe medication.</div></div>
      <div class="faq-item"><div class="faq-q">How much does a session cost in Newcastle?</div><div class="faq-a">Private sessions typically range from $180–$280 per hour. With an MHCP, you receive back approximately $141.85 (clinical) or $96.65 (registered) per session.</div></div>
      <div class="faq-item"><div class="faq-q">How do I verify a psychologist is AHPRA registered?</div><div class="faq-a">Search any practitioner's registration at ahpra.gov.au using their name.</div></div>
    </div>
  </div>
</section>
{footer()}

<script>
const GOOGLE_ICON = `{GOOGLE_ICON}`;
const LISTINGS = {js_array};
let activeFilters = new Set();

function renderCard(l) {{
  const tags = l.specialties.slice(0,5).map(s=>`<span class="tag">${{s}}</span>`).join('');
  const telTag = l.telehealth ? `<span class="tag telehealth">Telehealth</span>` : '';
  const status = l.status || (l.accepting ? "accepting" : "waitlist");
  const badge = status === "accepting"
    ? `<span class="accepting-badge open">✓ Accepting</span>`
    : status === "waitlist"
    ? `<span class="accepting-badge waitlist">⏱ Waitlist</span>`
    : "";
  const websiteBtn = `<a href="/profiles/psychologists/${{l.slug}}.html" class="btn-primary">View Profile</a>`;
  const googleUrl = `https://www.google.com/search?q=${{encodeURIComponent(l.google_search)}}`;
  const phoneEl = l.phone ? `<span>📞 ${{l.phone}}</span>` : '';
  const feeEl = l.fee_note ? `<span>💲 ${{l.fee_note}}</span>` : '';
  return `
    <div class="listing-card fade-up">
      <div>
        <div class="listing-name"><a href="/profiles/psychologists/${{l.slug}}.html">${{l.name}}</a></div>
        <div class="listing-credentials">${{l.credentials}}</div>
        <div class="listing-tags">${{tags}}${{telTag}}</div>
        <div class="listing-meta">
          <span>📍 ${{l.suburb}}</span>
          ${{l.hours ? `<span>🕐 ${{l.hours}}</span>` : ''}}
          <span>📋 ${{l.referral_types.join(' · ')}}</span>
          ${{phoneEl}}${{feeEl}}
        </div>
        <div class="listing-excerpt">${{l.description}}</div>
      </div>
      <div class="listing-right">
        ${{badge}}
        ${{websiteBtn}}
        <a href="${{googleUrl}}" target="_blank" rel="noopener" class="google-reviews-link">${{GOOGLE_ICON}} See Google Reviews</a>
      </div>
    </div>`;
}}

function applyFilters() {{
  const term = document.getElementById('searchInput').value.toLowerCase();
  const suburb = document.getElementById('suburbFilter').value;
  const sort = document.getElementById('sortSelect').value;
  const chkTel = document.getElementById('chkTelehealth').checked;
  const chkAcc = document.getElementById('chkAccepting').checked;
  let list = LISTINGS.filter(l => {{
    if (term) {{ const hay=[l.name,l.suburb,l.address,...l.specialties,l.description].join(' ').toLowerCase(); if(!hay.includes(term)) return false; }}
    if (suburb && l.suburb!==suburb) return false;
    if (chkTel && !l.telehealth) return false;
    if (chkAcc && !l.accepting) return false;
    for (const f of activeFilters) {{
      if (f==='telehealth' && !l.telehealth) return false;
      if (f==='accepting' && !l.accepting) return false;
      if (!l.specialties.some(s=>s.toLowerCase().includes(f.toLowerCase())) && !l.referral_types.some(r=>r.toLowerCase().includes(f.toLowerCase()))) return false;
    }}
    return true;
  }});
  if (sort==='accepting') list.sort((a,b)=>(b.accepting?1:0)-(a.accepting?1:0));
  else if (sort==='telehealth') list.sort((a,b)=>(b.telehealth?1:0)-(a.telehealth?1:0));
  else list.sort((a,b)=>a.name.localeCompare(b.name));
  document.getElementById('listingsContainer').innerHTML = list.length ? list.map(renderCard).join('') : '<div class="no-results"><h3>No results found</h3><p>Try adjusting your filters.</p></div>';
  document.getElementById('resultsCount').textContent = list.length;
  document.getElementById('statTotal').textContent = list.length;
  document.getElementById('statAccepting').textContent = list.filter(l=>l.accepting).length;
}}
function toggleChip(el) {{ const f=el.dataset.filter; el.classList.toggle('active'); activeFilters[el.classList.contains('active')?'add':'delete'](f); applyFilters(); }}
function clearFilters() {{ activeFilters.clear(); document.querySelectorAll('.chip.active').forEach(c=>c.classList.remove('active')); document.getElementById('searchInput').value=''; document.getElementById('suburbFilter').value=''; document.getElementById('chkTelehealth').checked=false; document.getElementById('chkAccepting').checked=false; applyFilters(); }}
document.getElementById('searchInput').addEventListener('keyup',e=>{{ if(e.key==='Enter') applyFilters(); }});
applyFilters();
</script>
</body>
</html>"""

# ── RUN ──────────────────────────────────────────────────────────────────────

print(f"Generating {len(listings)} profile pages...")
for l in listings:
    path = os.path.join(PROFILES_DIR, f"{l['slug']}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(generate_profile(l))
    print(f"  ✓ profiles/psychologists/{l['slug']}.html")

print("\nGenerating directory page...")
with open(DIRECTORY_FILE, "w", encoding="utf-8") as f:
    f.write(generate_directory(listings))
print("  ✓ psychologists.html")

print(f"\nDone. {len(listings)} profiles + 1 directory page generated.")
print("Run: git add . && git commit -m 'regenerate' && git push")
