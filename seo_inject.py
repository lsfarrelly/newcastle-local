#!/usr/bin/env python3
import json, os, re
from pathlib import Path
from datetime import date

BASE = Path(__file__).parent
BASE_URL = "https://newcastlelocal.com.au"
TODAY = date.today().isoformat()
OG_IMAGE = f"{BASE_URL}/css/og-image.png"

CATEGORIES = {
    "psychologists":    {"label": "Psychologists",       "schema_type": "MedicalBusiness",   },
    "gps":              {"label": "GPs",                 "schema_type": "MedicalClinic",     },
    "dentists":         {"label": "Dentists",            "schema_type": "Dentist",           },
    "physiotherapists": {"label": "Physiotherapists",    "schema_type": "MedicalBusiness",   },
    "plumbers":         {"label": "Plumbers",            "schema_type": "Plumber",           },
    "electricians":     {"label": "Electricians",        "schema_type": "Electrician",       },
    "builders":         {"label": "Builders",            "schema_type": "GeneralContractor", },
    "lawyers":          {"label": "Lawyers",             "schema_type": "LegalService",      },
    "accountants":      {"label": "Accountants",         "schema_type": "AccountingService", },
    "ndis":             {"label": "NDIS Providers",      "schema_type": "MedicalBusiness",   },
    "mechanics":        {"label": "Mechanics",           "schema_type": "AutoRepair",        },
    "removalists":      {"label": "Removalists",         "schema_type": "MovingCompany",     },
}

def inject_seo(html, canonical, title, description, og_type="website", json_ld=None):
    html = re.sub(r'<!-- SEO-INJECT-START -->.*?<!-- SEO-INJECT-END -->\n?', '', html, flags=re.DOTALL)
    ld_script = ""
    if json_ld:
        ld_str = json.dumps(json_ld, indent=2, ensure_ascii=False)
        ld_script = f'\n<script type="application/ld+json">\n{ld_str}\n</script>'
    block = f"""<!-- SEO-INJECT-START -->
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Newcastle Local">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{OG_IMAGE}">{ld_script}
<!-- SEO-INJECT-END -->"""
    return html.replace('</head>', block + '\n</head>', 1)

def load_json(cat_slug):
    p = BASE / "data" / f"{cat_slug}.json"
    if not p.exists(): return {}
    with open(p) as f: return json.load(f)

def patch_home():
    path = BASE / "index.html"
    html = path.read_text(encoding="utf-8")
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{BASE_URL}/#website",
             "name": "Newcastle Local", "url": BASE_URL,
             "description": "Hunter Region local business directory — free to search, free to list.",
             "inLanguage": "en-AU",
             "potentialAction": {"@type": "SearchAction",
               "target": {"@type": "EntryPoint",
                 "urlTemplate": f"{BASE_URL}/psychologists?search={{search_term_string}}"},
               "query-input": "required name=search_term_string"}},
            {"@type": "Organization", "@id": f"{BASE_URL}/#organization",
             "name": "Newcastle Local", "url": BASE_URL,
             "description": "Newcastle and Hunter Region local business directory.",
             "areaServed": {"@type": "City", "name": "Newcastle",
               "addressRegion": "NSW", "addressCountry": "AU"}}
        ]
    }
    html = inject_seo(html,
        canonical=BASE_URL,
        title="Newcastle Local — Find Local Services in Newcastle NSW",
        description="Newcastle's local business directory for the Hunter Region. Find GPs, psychologists, dentists, plumbers, electricians, lawyers, accountants and more. Free to search. Free to list.",
        og_type="website", json_ld=json_ld)
    path.write_text(html, encoding="utf-8")
    print(f"  OK index.html")

def patch_category(cat_slug):
    page_path = BASE / f"{cat_slug}.html"
    if not page_path.exists(): return
    info = CATEGORIES[cat_slug]
    label = info["label"]
    data = load_json(cat_slug)
    listings = data.get("listings", [])
    item_list = [{"@type": "ListItem", "position": i+1,
                  "url": f"{BASE_URL}/profiles/{cat_slug}/{b['slug']}.html",
                  "name": b.get("name","")}
                 for i, b in enumerate(listings) if b.get("slug")]
    json_ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": f"{label} in Newcastle NSW",
         "description": f"Find and compare {label.lower()} in Newcastle NSW. Hunter Region directory.",
         "url": f"{BASE_URL}/{cat_slug}", "numberOfItems": len(item_list),
         "itemListElement": item_list},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": label, "item": f"{BASE_URL}/{cat_slug}"}
        ]}
    ]}
    html = page_path.read_text(encoding="utf-8")
    tm = re.search(r'<title>(.*?)</title>', html)
    dm = re.search(r'<meta name="description" content="([^"]*)"', html)
    title = tm.group(1).replace("&amp;","&") if tm else f"{label} in Newcastle NSW | NewcastleLocal"
    desc = dm.group(1) if dm else f"Find trusted {label.lower()} in Newcastle NSW. Free Hunter Region directory."
    html = inject_seo(html, canonical=f"{BASE_URL}/{cat_slug}",
        title=title, description=desc, og_type="website", json_ld=json_ld)
    page_path.write_text(html, encoding="utf-8")
    print(f"  OK {cat_slug}.html ({len(listings)} listings)")

def patch_profile(cat_slug, biz):
    slug = biz.get("slug","")
    if not slug: return
    path = BASE / "profiles" / cat_slug / f"{slug}.html"
    if not path.exists(): return
    info = CATEGORIES[cat_slug]
    name = biz.get("name","")
    json_ld = {"@context": "https://schema.org", "@graph": [
        {"@type": info["schema_type"], "name": name,
         "url": f"{BASE_URL}/profiles/{cat_slug}/{slug}.html",
         "description": biz.get("description",""),
         "telephone": biz.get("phone","") or None,
         "sameAs": biz.get("website","") or None,
         "address": {"@type": "PostalAddress",
           "streetAddress": biz.get("address",""),
           "addressLocality": biz.get("suburb","Newcastle"),
           "addressRegion": "NSW", "addressCountry": "AU"},
         "areaServed": {"@type": "City", "name": "Newcastle", "addressRegion": "NSW"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": info["label"], "item": f"{BASE_URL}/{cat_slug}"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{BASE_URL}/profiles/{cat_slug}/{slug}.html"}
        ]}
    ]}
    # Remove None values
    json_ld["@graph"][0] = {k:v for k,v in json_ld["@graph"][0].items() if v is not None and v != ""}
    html = path.read_text(encoding="utf-8")
    tm = re.search(r'<title>(.*?)</title>', html)
    dm = re.search(r'<meta name="description" content="([^"]*)"', html)
    title = tm.group(1).replace("&amp;","&") if tm else f"{name} | NewcastleLocal"
    desc = dm.group(1) if dm else (biz.get("description","") or f"{name} — {info['label']} in Newcastle NSW")
    html = inject_seo(html, canonical=f"{BASE_URL}/profiles/{cat_slug}/{slug}.html",
        title=title, description=desc, og_type="article", json_ld=json_ld)
    path.write_text(html, encoding="utf-8")

def patch_static(filename, url_path, title, description):
    path = BASE / filename
    if not path.exists(): return
    html = path.read_text(encoding="utf-8")
    html = re.sub(r'<link rel="canonical"[^>]*/?>','', html)
    html = inject_seo(html, canonical=f"{BASE_URL}/{url_path}",
        title=title, description=description, og_type="website")
    path.write_text(html, encoding="utf-8")
    print(f"  OK {filename}")

def generate_sitemap(all_urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, priority, changefreq in all_urls:
        lines.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    lines.append('</urlset>')
    (BASE / "sitemap.xml").write_text('\n'.join(lines), encoding="utf-8")
    print(f"  OK sitemap.xml ({len(all_urls)} URLs)")

def generate_robots():
    (BASE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /update/\nDisallow: /netlify/\n\nSitemap: {BASE_URL}/sitemap.xml\n",
        encoding="utf-8")
    print("  OK robots.txt")

print("=== SEO Inject ===")
print("Home..."); patch_home()
print("Categories...")
for slug in CATEGORIES: patch_category(slug)
print("Profiles...")
all_profile_urls = []
for cat_slug in CATEGORIES:
    data = load_json(cat_slug)
    listings = data.get("listings", [])
    n = 0
    for biz in listings:
        patch_profile(cat_slug, biz)
        if biz.get("slug"):
            all_profile_urls.append(f"{BASE_URL}/profiles/{cat_slug}/{biz['slug']}.html")
            n += 1
    print(f"  OK {cat_slug}: {n} profiles")
print("Static pages..."); 
patch_static("about.html","about","About Newcastle Local — Hunter Region Business Directory","Learn about Newcastle Local, a free business directory for Newcastle and the Hunter Region.")
patch_static("privacy.html","privacy","Privacy Policy — Newcastle Local","Newcastle Local privacy policy.")
print("Sitemap...")
sitemap_urls = [(BASE_URL,"1.0","weekly")]
for slug in CATEGORIES: sitemap_urls.append((f"{BASE_URL}/{slug}","0.9","weekly"))
for url in all_profile_urls: sitemap_urls.append((url,"0.7","monthly"))
sitemap_urls += [(f"{BASE_URL}/about","0.4","yearly"),(f"{BASE_URL}/privacy","0.2","yearly")]
generate_sitemap(sitemap_urls)
print("Robots..."); generate_robots()
print(f"\nDone. {len(sitemap_urls)} URLs in sitemap.")
