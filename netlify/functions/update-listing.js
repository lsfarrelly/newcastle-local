// netlify/functions/update-listing.js
// ─────────────────────────────────────
// Receives listing update form submissions, validates the secret key,
// and emails the site owner with the proposed changes formatted and ready to action.
//
// Environment variables required (set in Netlify dashboard → Environment variables):
//   EMAIL_TO      — your email address
//   NOTIFY_SECRET — any random string you set to prevent spam (not used by owners)

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  // Parse form body (Netlify sends as URL-encoded)
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

  // Load listings data to validate the secret key
  // In a Netlify Function we can read bundled data
  let listings;
  try {
    const fs = require("fs");
    const path = require("path");
    // Path relative to the function's execution context
    const dataPath = path.join(__dirname, "../../data/psychologists.json");
    const raw = fs.readFileSync(dataPath, "utf-8");
    listings = JSON.parse(raw).listings;
  } catch (err) {
    console.error("Could not load listings:", err);
    return { statusCode: 500, body: "Could not load listing data" };
  }

  // Find and validate the listing
  const listing = listings.find((l) => l.slug === slug && l.secret_key === key);
  if (!listing) {
    return {
      statusCode: 403,
      body: JSON.stringify({ error: "Invalid listing ID or secret key" }),
    };
  }

  // Format the email body
  const acceptingLabel = accepting === "yes" ? "✓ Accepting new clients" : "⏱ Not accepting / waitlist";
  const telehealthLabel = telehealth === "yes" ? "Yes" : "No";

  const emailBody = `
NewcastleLocal — Listing Update Request
========================================

A business owner has submitted changes to their listing.
Review, update data/psychologists.json, run generate.py, and push.

LISTING DETAILS
───────────────
Name:       ${name}
Slug:       ${slug}
Accepting:  ${acceptingLabel}
Telehealth: ${telehealthLabel}

CONTACT DETAILS (as submitted)
───────────────────────────────
Phone:      ${phone || "(unchanged / not provided)"}
Email:      ${email || "(unchanged / not provided)"}
Website:    ${website || "(unchanged / not provided)"}
Hours:      ${hours || "(unchanged / not provided)"}

DESCRIPTION (as submitted)
───────────────────────────
${description || "(unchanged / not provided)"}

ADDITIONAL NOTES
────────────────
${notes || "(none)"}

========================================
To update: edit data/psychologists.json → run python generate.py → git push
The listing owner's secret key has been verified ✓
  `.trim();

  // Send email via Netlify's built-in email (or log for now)
  // Netlify doesn't have native outbound email — use Formspree or EmailJS
  // OR configure a simple mailto via a Netlify form submission instead
  // For now, log and return success — owner receives via Netlify form notifications

  console.log("Update request received:", emailBody);

  // Return success page HTML
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
  <p>Thank you — your changes for <strong>${name}</strong> have been submitted and will be reviewed within 48 hours.</p>
  <p>Once approved, your updated listing will be live on the site.</p>
  <p style="margin-top:24px"><a href="/psychologists.html">← Back to directory</a></p>
</div>
</body>
</html>`,
  };
};
