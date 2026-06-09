# Category Schema Notes

Most categories share a standard JSON schema (`services`, `service_areas`, `status`, `featured`, `last_verified`).

## Psychologists — DIFFERENT SCHEMA

`data/psychologists.json` uses a **unique schema** and will break the listing page if the standard schema is used.

Required fields for psychologist entries:
```json
{
  "id": <integer — next sequential ID>,
  "slug": "...",
  "secret_key": "...",
  "name": "...",
  "credentials": "...",
  "address": "...",
  "suburb": "...",
  "phone": "...",
  "email": "...",
  "website": "...",
  "google_search": "...",
  "specialties": ["Anxiety", "Depression", ...],
  "referral_types": ["MHCP", "Private", "NDIS", ...],
  "telehealth": true,
  "accepting": true,
  "hours": "...",
  "description": "...",
  "long_description": "...",
  "featured": false,
  "status": "active"
}
```

**Do NOT use**: `services`, `service_areas`, `last_verified`

The `psychologists.html` listing page calls `l.specialties.slice(0,5)` and `l.referral_types.join()` on every listing — missing these fields will throw a JavaScript error and break the entire page.
