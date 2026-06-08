// netlify/functions/delete-listing.js
// ─────────────────────────────────────────────────────────────────────────────
// Three-step owner-verified listing deletion.
//   GET  ?slug=xxx&cat=yyy          → key entry form
//   POST slug + cat + key           → validate key → confirmation page
//   POST slug + cat + key + confirm → delete listing
// ─────────────────────────────────────────────────────────────────────────────

const ALLOWED_CATS = [
  'psychologists','plumbers','gps','dentists','physiotherapists',
  'electricians','builders','lawyers','accountants','ndis','mechanics','removalists'
];

const STYLES = `
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:520px;width:100%;text-align:center}
  .icon{font-size:48px;margin-bottom:20px}
  h1{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:12px;color:#1a1a1a}
  p{color:#7a756d;font-size:15px;line-height:1.7;margin-bottom:10px}
  a{color:#2d5f4e;font-weight:500;text-decoration:none}
  label{display:block;font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:#7a756d;margin-bottom:6px;text-align:left}
  input[type=text]{width:100%;padding:12px 14px;border:1px solid #d4cfc6;border-radius:3px;font-family:monospace;font-size:15px;color:#1a1a1a;outline:none;margin-bottom:4px}
  input[type=text]:focus{border-color:#2d5f4e}
  .hint{font-size:12px;color:#aaa;text-align:left;margin-bottom:20px;line-height:1.5}
  .btn-danger{display:block;width:100%;margin-top:8px;padding:13px 28px;background:#c62828;color:#fff;border:none;border-radius:3px;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer}
  .btn-danger:hover{background:#b71c1c}
  .btn-cancel{display:block;width:100%;margin-top:10px;padding:11px 24px;background:#f0ede8;color:#555;border:none;border-radius:3px;font-family:'DM Sans',sans-serif;font-size:14px;cursor:pointer;text-decoration:none;text-align:center}
  .btn-cancel:hover{background:#e8e4de}
  .form-group{text-align:left;margin-bottom:16px}
  .error-msg{background:#fff3e0;border:1px solid #ffcc80;border-radius:3px;padding:12px 16px;font-size:14px;color:#e65100;margin-bottom:20px;text-align:left}
`;

const HEAD = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Remove Listing — NewcastleLocal</title>
<meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>${STYLES}</style>
</head>
<body>`;

exports.handler = async (event) => {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const REPO         = process.env.GITHUB_REPO   || "lsfarrelly/newcastle-local";
  const BRANCH       = process.env.GITHUB_BRANCH || "main";
  const GH_HEADERS   = {
    "Authorization": `Bearer ${GITHUB_TOKEN}`,
    "Accept":        "application/vnd.github.v3+json",
    "Content-Type":  "application/json",
    "User-Agent":    "newcastle-local-delete-function",
  };

  // ── Helpers ───────────────────────────────────────────────────────────────
  function html(body) {
    return { statusCode: 200, headers: { "Content-Type": "text/html" }, body: HEAD + body + "</body></html>" };
  }
  function err403(msg) {
    return {
      statusCode: 403, headers: { "Content-Type": "text/html" },
      body: `${HEAD}<div class="card"><div class="icon">🔒</div><h1>Invalid link</h1><p>${msg}</p></div></body></html>`
    };
  }

  async function fetchListing(cat, slug) {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/contents/data/${cat}.json`,
      { headers: GH_HEADERS }
    );
    const fd = await res.json();
    if (!fd.content) return null;
    const data = JSON.parse(Buffer.from(fd.content, "base64").toString("utf-8"));
    return data.listings.find(l => l.slug === slug) || null;
  }

  // ── GET: show key entry form ──────────────────────────────────────────────
  if (event.httpMethod === "GET") {
    const qp   = event.queryStringParameters || {};
    const slug = (qp.slug || "").trim();
    const rawCat = (qp.cat  || "psychologists").trim();
    const cat  = ALLOWED_CATS.includes(rawCat) ? rawCat : "psychologists";

    if (!slug) return err403("No listing specified.");

    // Fetch listing name for display (ignore any key in URL — not used)
    let listingName = slug.replace(/-/g, " ");
    try {
      const l = await fetchListing(cat, slug);
      if (l) listingName = l.name;
    } catch(e) {}

    return html(`
      <div class="card">
        <div class="icon">🗑️</div>
        <h1>Remove your listing</h1>
        <p>Enter your secret key to remove <strong>${listingName}</strong> from the directory.</p>
        <form method="POST" action="/.netlify/functions/delete-listing" style="margin-top:28px">
          <input type="hidden" name="slug" value="${slug}">
          <input type="hidden" name="cat"  value="${cat}">
          <div class="form-group">
            <label>Your secret key</label>
            <input type="text" name="key" placeholder="e.g. gr-hxtfya7o" autocomplete="off" required>
            <p class="hint">Your secret key was provided when your listing was created. Check your original confirmation email or the directory spreadsheet.</p>
          </div>
          <button type="submit" class="btn-danger">Verify &amp; continue →</button>
          <a href="/${cat}.html" class="btn-cancel">Cancel</a>
        </form>
      </div>`);
  }

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  // ── POST ──────────────────────────────────────────────────────────────────
  const params    = new URLSearchParams(event.body);
  const slug      = (params.get("slug") || "").trim();
  const rawCat    = (params.get("cat")  || "psychologists").trim();
  const cat       = ALLOWED_CATS.includes(rawCat) ? rawCat : "psychologists";
  const key       = (params.get("key") || "").trim();
  const confirmed = params.get("confirmed");

  if (!slug || !key) return err403("Missing required fields.");

  // ── Step 1: validate key → show confirmation ──────────────────────────────
  if (!confirmed) {
    let listing;
    try {
      listing = await fetchListing(cat, slug);
    } catch(e) {
      return { statusCode: 500, body: "Server error during validation." };
    }

    if (!listing || listing.secret_key !== key) {
      // Wrong key — show form again with error
      let listingName = slug.replace(/-/g, " ");
      if (listing) listingName = listing.name;
      return html(`
        <div class="card">
          <div class="icon">🗑️</div>
          <h1>Remove your listing</h1>
          <p>Enter your secret key to remove <strong>${listingName}</strong> from the directory.</p>
          <div class="error-msg">⚠️ That key doesn't match our records. Please check and try again.</div>
          <form method="POST" action="/.netlify/functions/delete-listing" style="margin-top:4px">
            <input type="hidden" name="slug" value="${slug}">
            <input type="hidden" name="cat"  value="${cat}">
            <div class="form-group">
              <label>Your secret key</label>
              <input type="text" name="key" placeholder="e.g. gr-hxtfya7o" autocomplete="off" required>
              <p class="hint">Check your original confirmation email or the directory spreadsheet.</p>
            </div>
            <button type="submit" class="btn-danger">Verify &amp; continue →</button>
            <a href="/${cat}.html" class="btn-cancel">Cancel</a>
          </form>
        </div>`);
    }

    // Key valid — show confirmation
    return html(`
      <div class="card">
        <div class="icon">⚠️</div>
        <h1>Are you sure?</h1>
        <p>This will permanently remove <strong>${listing.name}</strong> from the NewcastleLocal directory.</p>
        <p style="font-size:13px;color:#aaa;margin-top:4px">This cannot be undone. To re-list in future, you'll need to submit a new listing.</p>
        <form method="POST" action="/.netlify/functions/delete-listing" style="margin-top:28px">
          <input type="hidden" name="slug"      value="${slug}">
          <input type="hidden" name="cat"       value="${cat}">
          <input type="hidden" name="key"       value="${key}">
          <input type="hidden" name="confirmed" value="yes">
          <button type="submit" class="btn-danger">Yes, permanently remove my listing</button>
        </form>
        <a href="/profiles/${cat}/${slug}.html" class="btn-cancel">Cancel — keep my listing</a>
      </div>`);
  }

  // ── Step 2: confirmed → delete ────────────────────────────────────────────
  if (confirmed !== "yes") return err403("Deletion not confirmed.");

  let deleted     = false;
  let listingName = slug;

  if (GITHUB_TOKEN) {
    try {
      const JSON_PATH = `data/${cat}.json`;
      const API_JSON  = `https://api.github.com/repos/${REPO}/contents/${JSON_PATH}`;

      const getRes   = await fetch(API_JSON, { headers: GH_HEADERS });
      const fileData = await getRes.json();
      if (!fileData.sha) throw new Error("Could not retrieve JSON SHA");

      const currentJson = JSON.parse(
        Buffer.from(fileData.content, "base64").toString("utf-8")
      );

      const found = currentJson.listings.find(l => l.slug === slug);
      if (!found || found.secret_key !== key) throw new Error("Invalid key on confirmed delete");
      listingName = found.name;

      const before = currentJson.listings.length;
      currentJson.listings         = currentJson.listings.filter(l => l.slug !== slug);
      currentJson.meta.total        = currentJson.listings.length;
      currentJson.meta.last_updated = new Date().toISOString().split("T")[0];

      if (currentJson.listings.length < before) {
        const newContent = Buffer.from(JSON.stringify(currentJson, null, 2)).toString("base64");
        const putRes = await fetch(API_JSON, {
          method: "PUT", headers: GH_HEADERS,
          body: JSON.stringify({
            message: `Remove listing: ${listingName} (owner requested)`,
            content: newContent, sha: fileData.sha, branch: BRANCH,
          }),
        });

        if (putRes.ok) {
          deleted = true;
          // Delete profile HTML page
          try {
            const PROFILE_PATH = `profiles/${cat}/${slug}.html`;
            const API_PROFILE  = `https://api.github.com/repos/${REPO}/contents/${PROFILE_PATH}`;
            const profGet = await fetch(API_PROFILE, { headers: GH_HEADERS });
            const profData = await profGet.json();
            if (profData.sha) {
              await fetch(API_PROFILE, {
                method: "DELETE", headers: GH_HEADERS,
                body: JSON.stringify({
                  message: `Remove profile page: ${slug} (owner requested)`,
                  sha: profData.sha, branch: BRANCH,
                }),
              });
            }
          } catch(e) { console.warn(`[delete-listing] Profile delete failed: ${e.message}`); }
        }
      }
    } catch(err) {
      console.error(`[delete-listing] Error: ${err.message}`);
    }
  }

  if (deleted) {
    return html(`
      <div class="card">
        <div class="icon">✅</div>
        <h1>Listing removed</h1>
        <p><strong>${listingName}</strong> has been removed from NewcastleLocal.</p>
        <p>The directory will update within about 60 seconds.</p>
        <p style="margin-top:24px"><a href="/${cat}.html">← Back to directory</a></p>
      </div>`);
  } else {
    return html(`
      <div class="card">
        <div class="icon">❌</div>
        <h1>Something went wrong</h1>
        <p>We couldn't process the deletion automatically. Please email <a href="mailto:info@cerenova.com.au">info@cerenova.com.au</a> and we'll remove it manually.</p>
        <p><a href="/${cat}.html">← Back to directory</a></p>
      </div>`);
  }
};
