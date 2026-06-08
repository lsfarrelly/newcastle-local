# NewcastleLocal — Directory Site

A static directory website for Newcastle NSW, starting with a psychologists listing.

## Files

```
index.html                  Homepage with category grid
psychologists.html          Psychologists directory (live, filterable)
list.html                   "List Your Business" submission page
css/style.css               Shared stylesheet
data/psychologists.json     Listing data (real, scraped)
newcastle_psych_scraper.py  Python scraper to refresh data
```

## Deploy to Netlify

1. Drag the entire folder into app.netlify.com → drop zone
2. Done — live in ~30 seconds

Or via Netlify CLI:
```
npm install -g netlify-cli
netlify deploy --prod --dir .
```

## Refresh listing data

```bash
pip install requests beautifulsoup4 lxml
python newcastle_psych_scraper.py
```

Then re-deploy the updated `data/psychologists.json`.

The scraper:
- Hits Yellow Pages, Local Business Guide, and Psychology Today AU
- Deduplicates by name
- Infers specialties and referral types from description text
- Merges with existing data (preserves manual `featured` and `rating` values)
- Outputs to `data/psychologists.json`

## Adding new categories

1. Copy `psychologists.html` → e.g. `electricians.html`
2. Update the `LISTINGS` array and hero text
3. Run a new scraper pass for the new category
4. Add the category card to `index.html`

## Monetisation

- **Free listings** — no action needed, just list
- **Featured listings** — set `"featured": true` in the JSON + gold border appears automatically
- Charge ~$99/month for featured placement
- Future: automated Stripe payment → webhook → update JSON → redeploy
