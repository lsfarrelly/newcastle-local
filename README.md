# NewcastleLocal — Directory Site

## Quick workflow — adding or updating a listing

1. Edit `data/psychologists.json`
2. Run `python generate.py`
3. `git add . && git commit -m "update listings" && git push`
4. Netlify deploys in ~60 seconds ✓

## File structure

```
index.html                        Homepage
psychologists.html                Directory page (AUTO-GENERATED — do not edit directly)
profiles/psychologists/*.html     Individual profile pages (AUTO-GENERATED)
update/index.html                 Owner self-update page
netlify/functions/update-listing.js  Handles update form submissions
data/psychologists.json           MASTER DATA — edit this, then run generate.py
css/style.css                     Shared styles
generate.py                       Generates all pages from JSON
newcastle_psych_scraper.py        Scraper to find new listings
netlify.toml                      Netlify configuration
```

## Owner update links

Each listing has a unique secret key in the JSON. The update URL for any listing is:
  https://yoursite.netlify.app/update?slug=SLUG&key=SECRET_KEY

Example:
  https://yoursite.netlify.app/update?slug=newpsych-psychologists&key=np-x7k9m2p4

Send this link to the business owner. They can update:
- Accepting / not accepting (the big one)
- Phone, email, website, hours
- Description
- Any other notes

Their submission emails you → you update the JSON → run generate.py → push.

## Secret keys (keep private)

| Practice                    | Slug                           | Key           |
|-----------------------------|--------------------------------|---------------|
| NewPsych Psychologists      | newpsych-psychologists         | np-x7k9m2p4  |
| Elevated Wellbeing          | elevated-wellbeing-psychology  | ew-r3t8n6q1  |
| New Lambton Psychology      | new-lambton-psychology         | nl-b5w2j9k7  |
| Lacuna Clinical Psychology  | lacuna-clinical-psychology     | lc-v9d4f2s8  |
| Oracle Psychology           | oracle-psychology              | op-m1z6c3h5  |
| Psychology Centre Newcastle | psychology-centre-newcastle    | pc-a8y5t1w3  |
| Wildflower Psychology       | wildflower-psychology          | wp-k4r7e9u2  |
| ELD Psychology              | eld-psychology                 | el-q2n8g5j6  |
| Esteem Psychology           | esteem-psychology              | es-f6h3b1c9  |
| Dyer & Dyer Psychologists   | dyer-and-dyer-psychologists    | dd-u5m7w4p3  |
| Cerenova                    | cerenova                       | ce-t9p2l8r4  |
