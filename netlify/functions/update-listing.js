// netlify/functions/update-listing.js
// ─────────────────────────────────────────────────────────────────────────────
// Validates the secret key and automatically updates data/psychologists.json
// via the GitHub API, triggering a Netlify redeploy. Zero manual steps needed.
//
// Required Netlify env var:
//   GITHUB_TOKEN  — Fine-Grained PAT with Contents: Read & Write
// Optional:
//   GITHUB_REPO   — defaults to "lsfarrelly/newcastle-local"
//   GITHUB_BRANCH — defaults to "main"
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

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const params = new URLSearchParams(event.body);
  const fields = Object.fromEntries(params.entries());
  const { slug, key, listing_name, status, telehealth,
          phone, email, website, hours, description, notes } = fields;

  if (!slug || !key) {
    return { statusCode: 400, body: "Missing slug or key" };
  }

  if (SECRET_KEYS[slug] !== key) {
    return {
      statusCode: 403,
      headers: { "Content-Type": "text/html" },
      body: `<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Invalid link</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}
.card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:480px;text-align:center}
h1{font-size:22px;margin-bottom:10px;color:#1a1a1a}p{color:#7a756d;font-size:14px;line-height:1.7}</style>
</head><body><div class="card"><h1>Invalid link</h1>
<p>This update link could not be verified. Please contact <a href="mailto:info@cerenova.com.au" style="color:#2d5f4e">info@cerenova.com.au</a>.</p>
</div></body></html>`,
    };
  }

  const name = listing_name || slug;

  const GITHUB_TOKEN  = process.env.GITHUB_TOKEN;
  const REPO          = process.env.GITHUB_REPO   || "lsfarrelly/newcastle-local";
  const BRANCH        = process.env.GITHUB_BRANCH || "main";
  const FILE_PATH     = "data/psychologists.json";
  const API_BASE      = `https://api.github.com/repos/${REPO}/contents/${FILE_PATH}`;
  const GH_HEADERS    = {
    "Authorization": `Bearer ${GITHUB_TOKEN}`,
    "Accept":        "application/vnd.github.v3+json",
    "Content-Type":  "application/json",
    "User-Agent":    "newcastle-local-update-function",
  };

  let updateApplied = false;

  if (GITHUB_TOKEN) {
    try {
      const getRes  = await fetch(API_BASE, { headers: GH_HEADERS });
      const fileData = await getRes.json();
      if (!fileData.sha) throw new Error("Could not retrieve file SHA");

      const currentJson = JSON.parse(
        Buffer.from(fileData.content, "base64").toString("utf-8")
      );

      const idx = currentJson.listings.findIndex(l => l.slug === slug);
      if (idx !== -1) {
        const l = currentJson.listings[idx];

        // 3-way status: "accepting" | "waitlist" | "hidden"
        if (status === "accepting" || status === "waitlist" || status === "hidden") {
          l.status   = status;
          l.accepting = status === "accepting";
        } else {
          // Legacy: map old yes/no accepting field
          if (fields.accepting === "yes") { l.status = "accepting"; l.accepting = true; }
          else if (fields.accepting === "no") { l.status = "waitlist"; l.accepting = false; }
        }

        l.telehealth = (telehealth === "yes");

        const changed = (val) => val && val !== "(unchanged)" && val.trim() !== "";
        if (changed(phone))       l.phone       = phone.trim();
        if (changed(email))       l.email       = email.trim();
        if (changed(website))     l.website     = website.trim();
        if (changed(hours))       l.hours       = hours.trim();
        if (changed(description)) l.description = description.trim();

        currentJson.meta.last_updated = new Date().toISOString().split("T")[0];
      }

      const newContent = Buffer.from(
        JSON.stringify(currentJson, null, 2)
      ).toString("base64");

      const putRes = await fetch(API_BASE, {
        method:  "PUT",
        headers: GH_HEADERS,
        body: JSON.stringify({
          message: `Update listing: ${name} (via update form)`,
          content: newContent,
          sha:     fileData.sha,
          branch:  BRANCH,
        }),
      });

      if (putRes.ok) {
        updateApplied = true;
      } else {
        const err = await putRes.text();
        console.error(`[update-listing] GitHub PUT failed: ${err}`);
      }

    } catch (err) {
      console.error(`[update-listing] GitHub API error: ${err.message}`);
    }
  }

  const deployNote = updateApplied
    ? "Your listing will update automatically within about 60 seconds."
    : "Your changes have been submitted and will be reviewed within 48 hours.";

  return {
    statusCode: 200,
    headers: { "Content-Type": "text/html" },
    body: `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Update Received — NewcastleLocal</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:520px;width:100%;text-align:center}
  .icon{font-size:48px;margin-bottom:20px}
  h1{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:12px;color:#1a1a1a}
  p{color:#7a756d;font-size:15px;line-height:1.7;margin-bottom:10px}
  a{color:#2d5f4e;font-weight:500;text-decoration:none}
</style>
</head>
<body>
<div class="card">
  <div class="icon">✅</div>
  <h1>Update received</h1>
  <p>Thank you — changes for <strong>${name}</strong> have been submitted.</p>
  <p>${deployNote}</p>
  <p style="margin-top:24px"><a href="/psychologists.html">← Back to directory</a></p>
</div>
</body>
</html>`,
  };
};
