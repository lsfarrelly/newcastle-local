#!/usr/bin/env python3
"""
newcastle_psych_scraper.py
──────────────────────────
Scrapes Newcastle psychologist listings from public sources and outputs
a JSON data file compatible with the NewcastleLocal directory site.

Sources targeted:
  1. Yellow Pages (yellowpages.com.au)
  2. Local Business Guide (localbusinessguide.com.au)
  3. Psychology Today AU (psychologytoday.com/au) — limited, polite scraping

Usage:
  pip install requests beautifulsoup4 lxml
  python newcastle_psych_scraper.py

Output:
  data/psychologists.json  (replaces existing file)

Run this periodically (e.g. monthly cron job) to refresh listings.
"""

import json
import time
import re
import os
import sys
from datetime import date
from urllib.parse import urljoin, urlencode

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# ── CONFIG ──────────────────────────────────────────────────────────────────

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "psychologists.json")
DELAY = 2.5          # seconds between requests — be polite
TIMEOUT = 15         # request timeout
MAX_PAGES = 5        # max pages to scrape per source

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; NewcastleLocalBot/1.0; "
        "+https://newcastlelocal.com.au/bot)"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ── HELPERS ─────────────────────────────────────────────────────────────────

def get(url):
    """Fetch a URL with polite delay and error handling."""
    try:
        time.sleep(DELAY)
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    except requests.RequestException as e:
        print(f"  ✗ Error fetching {url}: {e}")
        return None


def clean(text):
    """Normalise whitespace."""
    if not text:
        return None
    return re.sub(r'\s+', ' ', text.strip())


def extract_phone(text):
    """Pull first Australian phone number from a string."""
    if not text:
        return None
    match = re.search(
        r'(\(?\d{2}\)?\s?\d{4}\s?\d{4}|04\d{2}\s?\d{3}\s?\d{3})',
        text
    )
    return match.group(0).strip() if match else None


def extract_suburb(address):
    """Extract suburb from a NSW address string."""
    if not address:
        return "Newcastle"
    # Match "SuburbName NSW XXXX"
    m = re.search(r'([A-Za-z\s]+),?\s+NSW', address)
    if m:
        return m.group(1).strip().title()
    # Fallback: second-last comma-separated segment
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 2:
        return parts[-2].title()
    return "Newcastle"


def merge_listings(existing, new_entries):
    """
    Merge new scrape results into existing listings.
    Matches on name (case-insensitive). New data wins for most fields
    but preserves manually-set 'featured' and 'rating' if present.
    """
    existing_by_name = {e["name"].lower(): e for e in existing}
    for entry in new_entries:
        key = entry["name"].lower()
        if key in existing_by_name:
            old = existing_by_name[key]
            # Preserve manual overrides
            entry["featured"] = old.get("featured", False)
            entry["rating"] = old.get("rating", entry.get("rating"))
            entry["review_count"] = old.get("review_count", entry.get("review_count", 0))
            existing_by_name[key] = entry
        else:
            existing_by_name[key] = entry
    return list(existing_by_name.values())

# ── SCRAPERS ─────────────────────────────────────────────────────────────────

def scrape_yellowpages():
    """
    Scrape Yellow Pages for Newcastle psychologists.
    Returns list of raw listing dicts.
    """
    print("\n[1/3] Scraping Yellow Pages…")
    results = []
    base = "https://www.yellowpages.com.au"
    url = f"{base}/find/psychologist/newcastle-nsw-2300"

    for page in range(1, MAX_PAGES + 1):
        page_url = url if page == 1 else f"{url}?pageNumber={page}"
        print(f"  Page {page}: {page_url}")
        soup = get(page_url)
        if not soup:
            break

        listings = soup.select("div.listing-content, div[class*='ListingItem']")
        if not listings:
            print("  No more listings found.")
            break

        for item in listings:
            name_el = item.select_one("h2 a, .listing-name a, h3 a")
            if not name_el:
                continue
            name = clean(name_el.get_text())

            address_el = item.select_one(".listing-address, address, [class*='address']")
            address = clean(address_el.get_text()) if address_el else None

            phone_el = item.select_one(".listing-phone, [class*='phone'], [href^='tel:']")
            phone = None
            if phone_el:
                phone = phone_el.get("href", "").replace("tel:", "") or clean(phone_el.get_text())

            desc_el = item.select_one(".listing-description, [class*='description'], p")
            description = clean(desc_el.get_text()) if desc_el else None

            website_el = item.select_one("a[href*='http']:not([href*='yellowpages'])")
            website = website_el.get("href") if website_el else None

            if name:
                results.append({
                    "name": name,
                    "address": address,
                    "suburb": extract_suburb(address),
                    "phone": extract_phone(phone or address or ""),
                    "website": website,
                    "description": description,
                    "source": "yellowpages.com.au",
                })
                print(f"    + {name}")

    print(f"  → {len(results)} listings found on Yellow Pages")
    return results


def scrape_localbusinessguide():
    """
    Scrape Local Business Guide for Newcastle psychologists.
    """
    print("\n[2/3] Scraping Local Business Guide…")
    results = []
    url = "https://www.localbusinessguide.com.au/new-south-wales/newcastle/health-and-medical/psychologists/"

    for page in range(1, MAX_PAGES + 1):
        page_url = url if page == 1 else f"{url}page/{page}/"
        print(f"  Page {page}: {page_url}")
        soup = get(page_url)
        if not soup:
            break

        items = soup.select(".business-listing, article[class*='listing'], .biz-result")
        if not items:
            print("  No more listings found.")
            break

        for item in items:
            name_el = item.select_one("h2, h3, .business-name, a.name")
            if not name_el:
                continue
            name = clean(name_el.get_text())

            address_el = item.select_one(".address, address, [class*='addr']")
            address = clean(address_el.get_text()) if address_el else None

            phone_text = item.get_text()
            phone = extract_phone(phone_text)

            desc_el = item.select_one("p, .description, .excerpt")
            description = clean(desc_el.get_text()) if desc_el else None

            if name and "newcastle" in (address or "").lower():
                results.append({
                    "name": name,
                    "address": address,
                    "suburb": extract_suburb(address),
                    "phone": phone,
                    "website": None,
                    "description": description,
                    "source": "localbusinessguide.com.au",
                })
                print(f"    + {name}")

    print(f"  → {len(results)} listings from Local Business Guide")
    return results


def scrape_psychology_today():
    """
    Scrape Psychology Today AU for Newcastle practitioners.
    Note: PT has a JS-rendered listing page; this gets what's available
    in the initial HTML (practice names and summary data).
    """
    print("\n[3/3] Scraping Psychology Today AU…")
    results = []
    url = "https://www.psychologytoday.com/au/counselling/nsw/newcastle"
    soup = get(url)
    if not soup:
        return results

    # PT renders some data in meta tags and structured data
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("itemListElement", [data])
            else:
                continue
            for item in items:
                if item.get("@type") in ("Person", "MedicalBusiness", "LocalBusiness", "Psychologist"):
                    name = item.get("name")
                    address_data = item.get("address", {})
                    address = (
                        f"{address_data.get('streetAddress', '')}, "
                        f"{address_data.get('addressLocality', '')} NSW "
                        f"{address_data.get('postalCode', '')}"
                    ).strip(", ")
                    if name:
                        results.append({
                            "name": clean(name),
                            "address": clean(address) if address.strip(",") else None,
                            "suburb": address_data.get("addressLocality", "Newcastle"),
                            "phone": item.get("telephone"),
                            "website": item.get("url"),
                            "description": clean(item.get("description")),
                            "source": "psychologytoday.com/au",
                        })
                        print(f"    + {name}")
        except (json.JSONDecodeError, AttributeError):
            continue

    print(f"  → {len(results)} listings from Psychology Today")
    return results


# ── NORMALISE ────────────────────────────────────────────────────────────────

SPECIALTY_KEYWORDS = {
    "Anxiety": ["anxiety", "anxious", "worry", "worr", "panic", "phobia", "ocd", "social anxiety"],
    "Depression": ["depression", "depressive", "low mood", "mood disorder"],
    "Trauma & PTSD": ["trauma", "ptsd", "post-traumatic", "emdr"],
    "ADHD": ["adhd", "attention deficit", "hyperactivity"],
    "Child & Adolescent": ["child", "adolescent", "teenager", "youth", "young people", "paediatric"],
    "Couples Therapy": ["couples", "relationship", "marriage", "partner"],
    "Grief & Loss": ["grief", "loss", "bereavement"],
    "Eating Disorders": ["eating disorder", "anorexia", "bulimia", "binge"],
    "OCD": ["ocd", "obsessive", "compulsive"],
    "Autism": ["autism", "asd", "autistic", "asperger"],
    "Workplace / EAP": ["eap", "employee assistance", "workplace", "burnout", "work stress"],
    "NDIS": ["ndis", "disability"],
    "Stress": ["stress", "burnout"],
    "Self-Esteem": ["self-esteem", "confidence", "self-worth"],
}

REFERRAL_KEYWORDS = {
    "MHCP": ["mental health care plan", "mhcp", "medicare", "gp referral", "better access"],
    "NDIS": ["ndis"],
    "EAP": ["eap", "employee assistance"],
    "WorkCover": ["workcover", "work cover", "workers comp"],
    "DVA": ["dva", "veteran", "defence"],
    "Private": ["private client", "self-refer", "no referral required"],
}


def infer_specialties(text):
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for label, keywords in SPECIALTY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(label)
    return found or ["Psychology"]


def infer_referrals(text):
    if not text:
        return ["MHCP", "Private"]
    text_lower = text.lower()
    found = []
    for label, keywords in REFERRAL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(label)
    if "MHCP" not in found:
        found.insert(0, "MHCP")  # almost all practices accept MHCP
    return found or ["MHCP", "Private"]


def normalise(raw_listings):
    """Convert raw scrape dicts to normalised listing schema."""
    normalised = []
    for i, raw in enumerate(raw_listings, start=1):
        desc = raw.get("description") or ""
        normalised.append({
            "id": i,
            "name": raw.get("name", "Unknown"),
            "type": "practice",
            "credentials": "Registered Psychologist",
            "address": raw.get("address"),
            "suburb": raw.get("suburb", "Newcastle"),
            "phone": raw.get("phone"),
            "email": raw.get("email"),
            "website": raw.get("website"),
            "specialties": infer_specialties(desc),
            "referral_types": infer_referrals(desc),
            "telehealth": any(w in desc.lower() for w in ["telehealth", "online", "video", "zoom"]),
            "bulk_billing": "bulk bill" in desc.lower(),
            "accepting": True,  # default; update manually or from site
            "hours": None,
            "description": desc or f"{raw.get('name')} is a psychology practice serving the Newcastle NSW area.",
            "featured": False,
            "rating": None,
            "review_count": 0,
            "source": raw.get("source", "scraped"),
            "last_verified": str(date.today()),
        })
    return normalised


# ── MAIN ─────────────────────────────────────────────────────────────────────

def load_existing():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("listings", [])
    return []


def save(listings):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output = {
        "meta": {
            "category": "Psychologists",
            "location": "Newcastle NSW",
            "last_updated": str(date.today()),
            "total": len(listings),
            "sources": ["yellowpages.com.au", "localbusinessguide.com.au", "psychologytoday.com/au"],
        },
        "listings": listings,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(listings)} listings to {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("  NewcastleLocal — Psychology Directory Scraper")
    print(f"  Run date: {date.today()}")
    print("=" * 60)

    # Load existing data (preserves manual edits like featured/rating)
    existing = load_existing()
    print(f"\nLoaded {len(existing)} existing listings from disk.")

    # Scrape sources
    raw = []
    raw.extend(scrape_yellowpages())
    raw.extend(scrape_localbusinessguide())
    raw.extend(scrape_psychology_today())

    print(f"\nTotal raw records scraped: {len(raw)}")

    if not raw:
        print("\n⚠ No new records scraped. Check site structures haven't changed.")
        print("  Existing data preserved unchanged.")
        return

    # Deduplicate raw by name
    seen = {}
    for r in raw:
        key = r["name"].lower()
        if key not in seen:
            seen[key] = r
        else:
            # Merge: fill in missing fields
            for field in ["phone", "website", "description", "address"]:
                if not seen[key].get(field) and r.get(field):
                    seen[key][field] = r[field]
    deduped = list(seen.values())
    print(f"After deduplication: {len(deduped)} unique practices")

    # Normalise
    normalised = normalise(deduped)

    # Merge with existing (preserves featured/rating)
    merged = merge_listings(existing, normalised)

    # Re-number IDs
    for i, listing in enumerate(merged, start=1):
        listing["id"] = i

    # Save
    save(merged)

    print("\nDone. Review data/psychologists.json before deploying.")
    print("Tip: Manually set 'featured': true and 'rating' for known practices.")


if __name__ == "__main__":
    main()
