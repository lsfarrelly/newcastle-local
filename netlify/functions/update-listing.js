// netlify/functions/update-listing.js
// ─────────────────────────────────────
// BACKUP endpoint: validates the secret key and returns a success page.
// Email delivery is handled by Netlify Forms (configured in the dashboard).
// This function is called by the old direct-fetch path — the new path posts
// to Netlify Forms via '/' and does NOT call this function.
//
// To use this function as the primary email path instead, set:
//   RESEND_API_KEY  — from resend.com (free account, 3000 emails/month)
//   EMAIL_TO        — defaults to info@cerenova.com.au

// Secret keys embedded here — never need to read the filesystem
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

  // Parse URL-encoded form body
  const params = new URLSearchParams(event.body);
  const fields = Object.fromEntries(params.entries());
  const { slug, key, name, phone, email, website, hours, accepting, telehealth, description, notes } = fields;

  // Basic validation
  if (!slug || !key || !name) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Missing required fields" }),
    };
  }

  // Validate secret key
  if (SECRET_KEYS[slug] !== key) {
    return {
      statusCode: 403,
      body: JSON.stringify({ error: "Invalid listing or key" }),
    };
  }

  // ── OPTIONAL: send email via Resend API ──────────────────────────────────
  // Sign up at resend.com, add RESEND_API_KEY to Netlify environment variables.
  // From address: once you verify your domain, change to no-reply@newcastlelocal.com.au
  const resendKey = process.env.RESEND_API_KEY;
  const emailTo   = process.env.EMAIL_TO || "info@cerenova.com.au";

  if (resendKey) {
    const acceptingLabel  = accepting  === "yes" ? "✓ Accepting new clients" : "⏱ Waitlist only";
    const telehealthLabel = telehealth === "yes" ? "Yes" : "No";

    const html = `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
        <h2 style="font-size:20px;border-bottom:2px solid #2d5f4e;padding-bottom:10px;color:#1a1a1a;">
          NewcastleLocal — Listing Update
        </h2>
        <p style="color:#555;margin-bottom:20px;">
          A business owner has submitted changes. Review and update
          <code>data/psychologists.json</code>, re-run <code>generate.py</code>, and push.
        </p>
        <table style="width:100%;border-collapse:collapse;font-size:15px;">
          <tr style="background:#f7f4ef;">
            <td style="padding:10px 14px;font-weight:600;width:160px;">Practice</td>
            <td style="padding:10px 14px;">${name}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;">Slug</td>
            <td style="padding:10px 14px;font-family:monospace;">${slug}</td>
          </tr>
          <tr style="background:#f7f4ef;">
            <td style="padding:10px 14px;font-weight:600;">Accepting</td>
            <td style="padding:10px 14px;">${acceptingLabel}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;">Telehealth</td>
            <td style="padding:10px 14px;">${telehealthLabel}</td>
          </tr>
          <tr style="background:#f7f4ef;">
            <td style="padding:10px 14px;font-weight:600;">Phone</td>
            <td style="padding:10px 14px;">${phone || "(unchanged)"}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;">Email</td>
            <td style="padding:10px 14px;">${email || "(unchanged)"}</td>
          </tr>
          <tr style="background:#f7f4ef;">
            <td style="padding:10px 14px;font-weight:600;">Website</td>
            <td style="padding:10px 14px;">${website || "(unchanged)"}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;font-weight:600;">Hours</td>
            <td style="padding:10px 14px;">${hours || "(unchanged)"}</td>
          </tr>
          ${description ? `
          <tr style="background:#f7f4ef;">
            <td style="padding:10px 14px;font-weight:600;vertical-align:top;">Description</td>
            <td style="padding:10px 14px;">${description}</td>
          </tr>` : ""}
          ${notes ? `
          <tr>
            <td style="padding:10px 14px;font-weight:600;vertical-align:top;">Notes</td>
            <td style="padding:10px 14px;">${notes}</td>
          </tr>` : ""}
        </table>
        <p style="margin-top:20px;font-size:12px;color:#888;">
          Secret key verified ✓ &nbsp;·&nbsp;
          Edit <code>data/psychologists.json</code> → run <code>python generate.py</code> → git push
        </p>
      </div>
    `;

    try {
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${resendKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from:    "NewcastleLocal <onboarding@resend.dev>",
          to:      [emailTo],
          subject: `[NewcastleLocal] Update: ${name}`,
          html,
        }),
      });
    } catch (err) {
      // Don't fail the user-facing response if email errors
      console.error("Resend error:", err.message);
    }
  } else {
    // Log if no Resend key — visible in Netlify function logs
    console.log(`[listing-update] Key not set. Submission from: ${name} (${slug})`);
  }

  // ── SUCCESS RESPONSE ────────────────────────────────────────────────────
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
  body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:520px;text-align:center}
  .icon{font-size:48px;margin-bottom:20px}
  h1{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:12px;color:#1a1a1a}
  p{color:#7a756d;font-size:15px;line-height:1.7;margin-bottom:12px}
  a{color:#2d5f4e;font-weight:500;text-decoration:none}
</style>
</head>
<body>
<div class="card">
  <div class="icon">✅</div>
  <h1>Update received</h1>
  <p>Thank you — changes for <strong>${name}</strong> have been submitted and will be reviewed within 48 hours.</p>
  <p>Once approved, your updated listing will be live on the site.</p>
  <p style="margin-top:24px"><a href="/psychologists.html">← Back to directory</a></p>
</div>
</body>
</html>`,
  };
};
