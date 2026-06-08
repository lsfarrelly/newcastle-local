// netlify/functions/delete-listing.js
// ─────────────────────────────────────────────────────────────────────────────
// Owner-verified listing deletion.
// POST with slug + key → validates, removes from JSON + deletes profile HTML
// via GitHub API, triggering a Netlify redeploy.
//
// Required env var: GITHUB_TOKEN (same as update-listing)
// ─────────────────────────────────────────────────────────────────────────────

// Key validation now done against JSON (supports dynamically-added listings)

const STYLES = `
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:520px;width:100%;text-align:center}
  .icon{font-size:48px;margin-bottom:20px}
  h1{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:12px;color:#1a1a1a}
  p{color:#7a756d;font-size:15px;line-height:1.7;margin-bottom:10px}
  a{color:#2d5f4e;font-weight:500;text-decoration:none}
  .btn-danger{display:inline-block;margin-top:18px;padding:12px 28px;background:#c62828;color:#fff;border:none;border-radius:3px;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer;text-decoration:none}
  .btn-cancel{display:inline-block;margin-top:10px;padding:10px 24px;background:#f0ede8;color:#555;border:none;border-radius:3px;font-family:'DM Sans',sans-serif;font-size:14px;cursor:pointer;text-decoration:none}
`;

const HTML_HEAD = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Delete Listing — NewcastleLocal</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>${STYLES}</style>
</head>
<body>`;

exports.handler = async (event) => {
  const GITHUB_TOKEN  = process.env.GITHUB_TOKEN;
  const REPO          = process.env.GITHUB_REPO   || "lsfarrelly/newcastle-local";
  const BRANCH        = process.env.GITHUB_BRANCH || "main";
  const GH_HEADERS    = {
    "Authorization": `Bearer ${GITHUB_TOKEN}`,
    "Accept":        "application/vnd.github.v3+json",
    "Content-Type":  "application/json",
    "User-Agent":    "newcastle-local-delete-function",
  };

  // ── GET: show confirmation page ───────────────────────────────────────────
  if (event.httpMethod === "GET") {
    const params = new URLSearchParams(event.queryStringParameters || {});
    const slug   = params.get("slug");
    const key    = params.get("key");
    const ALLOWED_CATS = ['psychologists','plumbers','gps','dentists','physiotherapists','electricians','builders','lawyers','accountants','ndis','mechanics','removalists'];
    const rawCat = params.get("cat") || "psychologists";
    const cat    = ALLOWED_CATS.includes(rawCat) ? rawCat : "psychologists";

    if (!slug || !key) {
      return {
        statusCode: 403,
        headers: { "Content-Type": "text/html" },
        body: `${HTML_HEAD}<div class="card"><div class="icon">🔒</div>
          <h1>Invalid link</h1>
          <p>This delete link could not be verified.</p>
        </div></body></html>`,
      };
    }
    // Validate key against JSON
    try {
      const API_JSON = `https://api.github.com/repos/${REPO}/contents/data/${cat}.json`;
      const res = await fetch(API_JSON, { headers: GH_HEADERS });
      const fd = await res.json();
      const json = JSON.parse(Buffer.from(fd.content, "base64").toString("utf-8"));
      const listing = json.listings.find(l => l.slug === slug);
      if (!listing || listing.secret_key !== key) {
        return {
          statusCode: 403,
          headers: { "Content-Type": "text/html" },
          body: `${HTML_HEAD}<div class="card"><div class="icon">🔒</div>
            <h1>Invalid link</h1>
            <p>This delete link could not be verified.</p>
          </div></body></html>`,
        };
      }
    } catch(e) {
      return { statusCode: 500, body: "Server error during validation" };
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card">
        <div class="icon">⚠️</div>
        <h1>Remove your listing?</h1>
        <p>This will permanently remove <strong>${slug.replace(/-/g, ' ')}</strong> from the NewcastleLocal directory.</p>
        <p style="font-size:13px;color:#aaa;margin-top:8px;">This cannot be undone. To re-list in future, submit a new listing.</p>
        <form method="POST" action="/.netlify/functions/delete-listing">
          <input type="hidden" name="slug" value="${slug}">
          <input type="hidden" name="key" value="${key}">
          <input type="hidden" name="cat" value="${cat}">
          <input type="hidden" name="confirmed" value="yes">
          <br>
          <button type="submit" class="btn-danger">Yes, remove my listing</button>
        </form>
        <br>
        <a href="/profiles/${cat}/${slug}.html" class="btn-cancel">Cancel — keep my listing</a>
      </div></body></html>`,
    };
  }

  // ── POST: confirmed deletion ──────────────────────────────────────────────
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const params = new URLSearchParams(event.body);
  const slug      = params.get("slug");
  const key       = params.get("key");
  const confirmed = params.get("confirmed");
  const ALLOWED_CATS_POST = ['psychologists','plumbers','gps','dentists','physiotherapists','electricians','builders','lawyers','accountants','ndis','mechanics','removalists'];
  const rawCatPost = params.get("cat") || "psychologists";
  const cat = ALLOWED_CATS_POST.includes(rawCatPost) ? rawCatPost : "psychologists";

  if (!slug || !key || confirmed !== "yes") {
    return {
      statusCode: 403,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card"><div class="icon">🔒</div>
        <h1>Not authorised</h1>
        <p>Deletion could not be verified.</p>
        <p><a href="/${cat}.html">Back to directory</a></p>
      </div></body></html>`,
    };
  }

  let deleted = false;
  let listingName = slug;

  if (GITHUB_TOKEN) {
    try {
      const JSON_PATH = `data/${cat}.json`;
      const API_JSON  = `https://api.github.com/repos/${REPO}/contents/${JSON_PATH}`;

      // 1. Fetch + update JSON (remove the listing)
      const getRes   = await fetch(API_JSON, { headers: GH_HEADERS });
      const fileData = await getRes.json();
      if (!fileData.sha) throw new Error("Could not retrieve JSON SHA");

      const currentJson = JSON.parse(
        Buffer.from(fileData.content, "base64").toString("utf-8")
      );

      const before = currentJson.listings.length;
      const found  = currentJson.listings.find(l => l.slug === slug);
      if (!found || found.secret_key !== key) throw new Error("Invalid key");
      listingName = found.name;

      currentJson.listings = currentJson.listings.filter(l => l.slug !== slug);
      currentJson.meta.total        = currentJson.listings.length;
      currentJson.meta.last_updated = new Date().toISOString().split("T")[0];

      if (currentJson.listings.length < before) {
        const newContent = Buffer.from(
          JSON.stringify(currentJson, null, 2)
        ).toString("base64");

        const putRes = await fetch(API_JSON, {
          method: "PUT",
          headers: GH_HEADERS,
          body: JSON.stringify({
            message: `Remove listing: ${listingName} (owner requested)`,
            content: newContent,
            sha:     fileData.sha,
            branch:  BRANCH,
          }),
        });

        if (putRes.ok) {
          deleted = true;

          // 2. Delete the profile HTML page
          const PROFILE_PATH = `profiles/${cat}/${slug}.html`;
          const API_PROFILE  = `https://api.github.com/repos/${REPO}/contents/${PROFILE_PATH}`;

          try {
            const profGet = await fetch(API_PROFILE, { headers: GH_HEADERS });
            const profData = await profGet.json();
            if (profData.sha) {
              await fetch(API_PROFILE, {
                method: "DELETE",
                headers: GH_HEADERS,
                body: JSON.stringify({
                  message: `Remove profile page: ${slug} (owner requested)`,
                  sha:     profData.sha,
                  branch:  BRANCH,
                }),
              });
            }
          } catch (profileErr) {
            console.warn(`[delete-listing] Could not delete profile page: ${profileErr.message}`);
          }
        }
      }
    } catch (err) {
      console.error(`[delete-listing] Error: ${err.message}`);
    }
  }

  if (deleted) {
    return {
      statusCode: 200,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card">
        <div class="icon">✅</div>
        <h1>Listing removed</h1>
        <p><strong>${listingName}</strong> has been removed from NewcastleLocal.</p>
        <p>The directory will update within about 60 seconds.</p>
        <p style="margin-top:24px"><a href="/${cat}.html">← Back to directory</a></p>
      </div></body></html>`,
    };
  } else {
    return {
      statusCode: 500,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card">
        <div class="icon">❌</div>
        <h1>Something went wrong</h1>
        <p>We couldn't process the deletion automatically. Please email <a href="mailto:info@cerenova.com.au">info@cerenova.com.au</a> and we'll remove it manually.</p>
        <p><a href="/psychologists.html">← Back to directory</a></p>
      </div></body></html>`,
    };
  }
};
