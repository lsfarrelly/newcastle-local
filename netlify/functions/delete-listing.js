// netlify/functions/delete-listing.js
// ─────────────────────────────────────────────────────────────────────────────
// Owner-verified listing deletion.
// POST with slug + key → validates, removes from JSON + deletes profile HTML
// via GitHub API, triggering a Netlify redeploy.
//
// Required env var: GITHUB_TOKEN (same as update-listing)
// ─────────────────────────────────────────────────────────────────────────────

const SECRET_KEYS = {
  "newpsych-psychologists":        "np-x7k9m2p4",
  "elevated-wellbeing-psychology": "ew-r3t8n6q1",
  "new-lambton-psychology":        "nl-b5w2j9k7",
  "lacuna-clinical-psychology":    "lc-v9d4f2s8",
  "oracle-psychology":             "op-m1z6c3h5",
  "psychology-centre-newcastle":   "pc-a8y5t1w3",
  "wildflower-psychology":         "wp-k4r7e9u2",
  "eld-psychology":                "el-q2n8g5j6",
  "esteem-psychology":             "es-f6h3b1c9",
  "dyer-and-dyer-psychologists":   "dd-u5m7w4p3",
  "cerenova":                      "ce-t9p2l8r4",
};

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
    const slug = params.get("slug");
    const key  = params.get("key");

    if (!slug || !key || SECRET_KEYS[slug] !== key) {
      return {
        statusCode: 403,
        headers: { "Content-Type": "text/html" },
        body: `${HTML_HEAD}<div class="card"><div class="icon">🔒</div>
          <h1>Invalid link</h1>
          <p>This delete link could not be verified. Please contact <a href="mailto:info@cerenova.com.au">info@cerenova.com.au</a>.</p>
        </div></body></html>`,
      };
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
          <input type="hidden" name="confirmed" value="yes">
          <br>
          <button type="submit" class="btn-danger">Yes, remove my listing</button>
        </form>
        <br>
        <a href="/profiles/psychologists/${slug}.html" class="btn-cancel">Cancel — keep my listing</a>
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

  if (!slug || !key || SECRET_KEYS[slug] !== key || confirmed !== "yes") {
    return {
      statusCode: 403,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card"><div class="icon">🔒</div>
        <h1>Not authorised</h1>
        <p>Deletion could not be verified.</p>
        <p><a href="/psychologists.html">Back to directory</a></p>
      </div></body></html>`,
    };
  }

  let deleted = false;
  let listingName = slug;

  if (GITHUB_TOKEN) {
    try {
      const JSON_PATH = "data/psychologists.json";
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
      if (found) listingName = found.name;

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
          const PROFILE_PATH = `profiles/psychologists/${slug}.html`;
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
        <p style="margin-top:24px"><a href="/psychologists.html">← Back to directory</a></p>
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
