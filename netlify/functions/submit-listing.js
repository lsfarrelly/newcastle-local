// netlify/functions/submit-listing.js
// ─────────────────────────────────────────────────────────────────────────────
// Handles new listing form submissions.
// Auto-creates the listing in data/psychologists.json AND generates the
// profile HTML page via the GitHub API, triggering a Netlify redeploy.
//
// Required env var: GITHUB_TOKEN (same as update-listing)
// ─────────────────────────────────────────────────────────────────────────────

const STYLES = `
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:#f7f4ef;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:24px}
  .card{background:#fff;border:1px solid #d4cfc6;border-radius:4px;padding:48px;max-width:520px;width:100%;text-align:center}
  .icon{font-size:48px;margin-bottom:20px}
  h1{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:12px;color:#1a1a1a}
  p{color:#7a756d;font-size:15px;line-height:1.7;margin-bottom:10px}
  a{color:#2d5f4e;font-weight:500;text-decoration:none}
  .key-box{background:#f0ede8;border:1px solid #d4cfc6;border-radius:3px;padding:14px 18px;font-family:monospace;font-size:15px;color:#1a1a1a;margin:14px 0;letter-spacing:0.05em}
`;

const HTML_HEAD = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Listing Submitted — NewcastleLocal</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>${STYLES}</style>
</head>
<body>`;

const GOOGLE_ICON = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>`;

function slugify(name) {
  return name.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function generateKey(slug) {
  const prefix = slug.split('-').slice(0, 2).map(s => s[0] || 'x').join('');
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let suffix = '';
  for (let i = 0; i < 8; i++) {
    suffix += chars[Math.floor(Math.random() * chars.length)];
  }
  return `${prefix}-${suffix}`;
}

function generateProfileHTML(l) {
  const statusBg   = l.status === 'accepting' ? '#e8f5e9' : (l.status === 'waitlist' ? '#fff3e0' : 'transparent');
  const statusColor = l.status === 'accepting' ? '#2e7d32' : (l.status === 'waitlist' ? '#e65100' : 'transparent');
  const statusText  = l.status === 'accepting' ? '✓ Accepting new clients' : (l.status === 'waitlist' ? '⏱ Currently on waitlist' : '');
  const statusHtml  = statusText
    ? `<div class="profile-status" style="background:${statusBg};color:${statusColor};">${statusText}</div>`
    : '';

  const tags_html = l.specialties.map(s => `<span class="tag">${s}</span>`).join('')
    + (l.telehealth ? '<span class="tag telehealth">Telehealth</span>' : '');

  const phoneEl = l.phone ? `<div class="detail-row"><span class="detail-icon">📞</span><span>${l.phone}</span></div>` : '';
  const emailEl = l.email ? `<div class="detail-row"><span class="detail-icon">✉️</span><a href="mailto:${l.email}" style="color:var(--accent)">${l.email}</a></div>` : '';
  const webEl   = l.website ? `<div class="detail-row"><span class="detail-icon">🌐</span><a href="${l.website}" target="_blank" rel="noopener" style="color:var(--accent)">${l.website.replace('https://','')}</a></div>` : '';
  const telEl   = l.telehealth ? '<div class="detail-row"><span class="detail-icon">💻</span><span>Telehealth available</span></div>' : '';
  const refHtml = l.referral_types.map(r => `<span class="ref-chip">${r}</span>`).join('');
  const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(l.name + ' ' + l.suburb + ' Newcastle reviews')}`;
  const websiteBtn = l.website
    ? `<a href="${l.website}" target="_blank" rel="noopener" class="btn-primary" style="display:inline-block;width:auto;padding:12px 28px;">View Website</a>`
    : '';
  const suburb = l.suburb || (l.address ? l.address.split(',').pop().trim() : 'Newcastle NSW');
  const updateUrl = `/update/index.html?slug=${l.slug}&key=${l.secret_key}`;
  const deleteUrl = `/.netlify/functions/delete-listing?slug=${l.slug}&key=${l.secret_key}`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${l.name} — Newcastle Psychologist | NewcastleLocal</title>
<meta name="description" content="${l.description.replace(/"/g,"'")} Located in ${suburb}, Newcastle NSW.">
<link rel="stylesheet" href="/css/style.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<style>
  .profile-hero{background:var(--ink);padding:56px 24px 64px;position:relative;overflow:hidden;}
  .profile-hero::before{content:'';position:absolute;top:-60px;right:-60px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(45,95,78,0.15) 0%,transparent 70%);}
  .profile-hero-inner{max-width:1100px;margin:0 auto;}
  .profile-back{color:#888;font-size:13px;text-decoration:none;display:inline-flex;align-items:center;gap:6px;margin-bottom:24px;transition:color 0.15s;}
  .profile-back:hover{color:#fff;}
  .profile-name{font-family:'Playfair Display',serif;font-size:clamp(28px,4vw,46px);color:#fff;line-height:1.1;margin-bottom:8px;}
  .profile-credentials{color:#aaa;font-size:14px;margin-bottom:20px;}
  .profile-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;}
  .profile-status{display:inline-flex;align-items:center;gap:8px;padding:8px 18px;border-radius:3px;font-size:13px;font-weight:600;}
  .profile-body{max-width:1100px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px;align-items:start;}
  .profile-section{margin-bottom:36px;}
  .profile-section h2{font-family:'Playfair Display',serif;font-size:22px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--rule);}
  .profile-section p{font-size:15px;color:#444;line-height:1.8;margin-bottom:12px;}
  .detail-card{background:var(--warm-white);border:1px solid var(--rule);border-radius:4px;padding:24px;position:sticky;top:80px;}
  .detail-card h3{font-size:11px;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:18px;}
  .detail-row{display:flex;align-items:flex-start;gap:10px;font-size:14px;color:var(--ink);margin-bottom:14px;line-height:1.5;}
  .detail-icon{font-size:16px;flex-shrink:0;margin-top:1px;}
  .detail-divider{border:none;border-top:1px solid var(--rule);margin:18px 0;}
  .referral-list{display:flex;flex-wrap:wrap;gap:5px;}
  .ref-chip{padding:3px 10px;background:var(--cream);border-radius:2px;font-size:12px;color:var(--muted);}
  .btn-group{display:flex;flex-direction:column;gap:8px;margin-top:18px;}
  .update-link{display:block;text-align:center;font-size:11px;color:var(--muted);text-decoration:none;margin-top:14px;padding-top:14px;border-top:1px solid var(--rule);}
  .update-link:hover{color:var(--accent);}
  .delete-link{display:block;text-align:center;font-size:11px;color:#c62828;text-decoration:none;margin-top:8px;}
  .delete-link:hover{text-decoration:underline;}
  @media(max-width:768px){.profile-body{grid-template-columns:1fr;}.detail-card{position:static;}}
</style>
</head>
<body>
<header class="site-header">
  <div class="site-header-inner">
    <a href="/index.html" class="site-logo">Newcastle<span>Local</span></a>
    <nav><ul class="site-nav">
      <li><a href="/psychologists.html" style='color:#fff'>Health</a></li>
      <li><a href="#">Trades</a></li><li><a href="#">Legal</a></li>
      <li><a href="#">Finance</a></li><li><a href="#">NDIS</a></li>
      <li><a href="/list.html" style="color:var(--gold)">List Your Business</a></li>
    </ul></nav>
  </div>
</header>
<div class="breadcrumb-bar">
  <div class="breadcrumb-inner">
    <a href="/index.html">Home</a><span>/</span>
    <a href="/psychologists.html">Psychologists</a><span>/</span>
    ${l.name}
  </div>
</div>
<section class="profile-hero">
  <div class="profile-hero-inner">
    <a href="/psychologists.html" class="profile-back">← Back to all psychologists</a>
    <div class="profile-name">${l.name}</div>
    <div class="profile-credentials">${l.credentials}</div>
    <div class="profile-tags">${tags_html}</div>
    ${statusHtml}
  </div>
</section>
<div class="profile-body">
  <div>
    <div class="profile-section">
      <h2>About ${l.name}</h2>
      <p>${l.description}</p>
    </div>
    <div class="profile-section">
      <h2>Specialties</h2>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        ${l.specialties.map(s => `<span class="tag" style="font-size:13px;padding:5px 12px;">${s}</span>`).join('')}
      </div>
    </div>
    ${l.referral_types.length ? `<div class="profile-section">
      <h2>Referral &amp; Payment Types</h2>
      <div class="referral-list" style="gap:8px;">
        ${l.referral_types.map(r => `<span class="ref-chip" style="font-size:13px;padding:5px 12px;">${r}</span>`).join('')}
      </div>
    </div>` : ''}
  </div>
  <aside>
    <div class="detail-card">
      <h3>Contact &amp; Location</h3>
      <div class="detail-row"><span class="detail-icon">📍</span><span>${l.address}</span></div>
      ${phoneEl}${emailEl}${webEl}
      <hr class="detail-divider">
      ${l.hours ? `<div class="detail-row"><span class="detail-icon">🕐</span><span>${l.hours}</span></div>` : ''}
      ${telEl}
      <hr class="detail-divider">
      <div class="btn-group">
        ${websiteBtn}
        <a href="${googleUrl}" target="_blank" rel="noopener" class="btn-secondary" style="display:inline-flex;align-items:center;justify-content:center;gap:6px;width:100%;">
          ${GOOGLE_ICON} See Google Reviews
        </a>
      </div>
      <div id="ownerControls" data-key="${l.secret_key}" style="display:none;border-top:1px solid var(--rule);margin-top:14px;padding-top:14px;">
        <a href="${updateUrl}" class="update-link" style="border:none;margin:0;padding:0;">Update your listing →</a>
        <a href="${deleteUrl}" class="delete-link">Remove this listing</a>
      </div>
    </div>
  </aside>
</div>
<footer>
  <div class="footer-inner">
    <a href="/index.html" style="font-family:'Playfair Display',serif;color:#fff;font-size:16px;text-decoration:none;">Newcastle<span style="color:var(--gold)">Local</span></a>
    <div class="footer-links"><a href="#">About</a><a href="/list.html">List Your Practice</a><a href="#">Privacy</a><a href="#">Contact</a></div>
    <div>© 2025 NewcastleLocal · Not a medical referral service · Data sourced from public records</div>
  </div>
</footer>
<script>
(function() {
  var p = new URLSearchParams(window.location.search);
  var k = p.get('key');
  var ctrl = document.getElementById('ownerControls');
  if(ctrl && k && k === ctrl.dataset.key) ctrl.style.display = 'block';
  fetch("/data/psychologists.json?v=" + Date.now())
    .then(function(r){return r.json();})
    .then(function(data){
      var l = data.listings.find(function(x){return x.slug==="${l.slug}";});
      if(!l) return;
      var badge = document.querySelector(".profile-status");
      if(badge){
        if(l.status==="accepting"){badge.style.background="#e8f5e9";badge.style.color="#2e7d32";badge.textContent="\\u2713 Accepting new clients";badge.style.display="";}
        else if(l.status==="waitlist"){badge.style.background="#fff3e0";badge.style.color="#e65100";badge.textContent="\\u23f1 Currently on waitlist";badge.style.display="";}
        else{badge.style.display="none";}
      }
    }).catch(function(){});
})();
</script>
</body>
</html>`;
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const params = new URLSearchParams(event.body);
  const fields = Object.fromEntries(params.entries());

  const {
    business_name, category, contact_email, address, phone,
    website, specialties, referral_types, description,
    accepting, telehealth, hours, notes
  } = fields;

  if (!business_name || !contact_email || !address || !description) {
    return { statusCode: 400, body: "Missing required fields" };
  }

  // Build the listing object
  const slug      = slugify(business_name);
  const secretKey = generateKey(slug);
  const suburb    = address.split(',').find(p => /NSW|QLD|VIC|WA|SA|TAS|NT|ACT/i.test(p))?.trim()
                 || address.split(',').slice(-2, -1)[0]?.trim()
                 || 'Newcastle';
  const specialtyList  = specialties ? specialties.split(',').map(s => s.trim()).filter(Boolean) : [];
  const referralList   = referral_types ? referral_types.split(',').map(s => s.trim()).filter(Boolean) : [];

  // Normalise website URL — always use https://
  let websiteUrl = (website || '').trim();
  if (websiteUrl) {
    websiteUrl = 'https://' + websiteUrl.replace(/^https?:\/\/|^\/\//i, '');
  }

  let statusVal = 'accepting';
  if (accepting === 'waitlist') statusVal = 'waitlist';
  else if (accepting === 'no' || accepting === 'hidden') statusVal = 'hidden';

  const newListing = {
    id: Date.now(),
    slug,
    secret_key: secretKey,
    name: business_name,
    credentials: category || 'Psychologists',
    address,
    suburb,
    phone:         phone || '',
    email:         contact_email,
    website:       websiteUrl,
    google_search: `${business_name} ${suburb} Newcastle reviews`,
    specialties:   specialtyList,
    referral_types: referralList,
    telehealth:    telehealth === 'yes' || telehealth === 'only',
    accepting:     statusVal === 'accepting',
    status:        statusVal,
    hours:         hours || '',
    description:   description,
    long_description: description,
    featured: false,
  };

  const GITHUB_TOKEN  = process.env.GITHUB_TOKEN;
  const REPO          = process.env.GITHUB_REPO   || "lsfarrelly/newcastle-local";
  const BRANCH        = process.env.GITHUB_BRANCH || "main";
  const GH_HEADERS    = {
    "Authorization": `Bearer ${GITHUB_TOKEN}`,
    "Accept":        "application/vnd.github.v3+json",
    "Content-Type":  "application/json",
    "User-Agent":    "newcastle-local-submit-function",
  };

  let created = false;

  if (GITHUB_TOKEN) {
    try {
      // 1. Update JSON
      const JSON_PATH = "data/psychologists.json";
      const API_JSON  = `https://api.github.com/repos/${REPO}/contents/${JSON_PATH}`;

      const getRes   = await fetch(API_JSON, { headers: GH_HEADERS });
      const fileData = await getRes.json();
      if (!fileData.sha) throw new Error("Could not retrieve JSON SHA");

      const currentJson = JSON.parse(
        Buffer.from(fileData.content, "base64").toString("utf-8")
      );

      // Avoid duplicate slugs
      let finalSlug = slug;
      let counter = 2;
      while (currentJson.listings.some(l => l.slug === finalSlug)) {
        finalSlug = `${slug}-${counter++}`;
      }
      newListing.slug = finalSlug;

      currentJson.listings.push(newListing);
      currentJson.meta.total        = currentJson.listings.length;
      currentJson.meta.last_updated = new Date().toISOString().split("T")[0];

      const jsonContent = Buffer.from(
        JSON.stringify(currentJson, null, 2)
      ).toString("base64");

      const putJson = await fetch(API_JSON, {
        method: "PUT",
        headers: GH_HEADERS,
        body: JSON.stringify({
          message: `New listing: ${business_name} (via submission form)`,
          content: jsonContent,
          sha:     fileData.sha,
          branch:  BRANCH,
        }),
      });

      if (!putJson.ok) throw new Error("JSON PUT failed: " + await putJson.text());

      // 2. Create profile HTML
      const profileHtml    = generateProfileHTML(newListing);
      const PROFILE_PATH   = `profiles/psychologists/${newListing.slug}.html`;
      const API_PROFILE    = `https://api.github.com/repos/${REPO}/contents/${PROFILE_PATH}`;
      const profileContent = Buffer.from(profileHtml).toString("base64");

      const putProfile = await fetch(API_PROFILE, {
        method: "PUT",
        headers: GH_HEADERS,
        body: JSON.stringify({
          message: `Add profile page: ${business_name}`,
          content: profileContent,
          branch:  BRANCH,
        }),
      });

      if (putProfile.ok) {
        created = true;
        console.log(`[submit-listing] ✓ Created listing + profile for ${newListing.slug}`);
      } else {
        console.error("[submit-listing] Profile PUT failed:", await putProfile.text());
      }

    } catch (err) {
      console.error(`[submit-listing] Error: ${err.message}`);
    }
  }

  if (created) {
    return {
      statusCode: 200,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card">
        <div class="icon">🎉</div>
        <h1>You're live!</h1>
        <p>Your listing for <strong>${business_name}</strong> has been created and will appear in the directory within about 60 seconds.</p>
        <p style="margin-top:18px;font-size:13px;color:#888;">Save your owner key — you'll need it to update or remove your listing:</p>
        <div class="key-box">${secretKey}</div>
        <p style="font-size:12px;color:#aaa;">Your update link: <a href="/update/index.html?slug=${newListing.slug}&key=${secretKey}" style="color:var(--accent,#2d5f4e)">/update/?slug=${newListing.slug}</a></p>
        <p style="margin-top:24px"><a href="/psychologists.html">← Browse the directory</a></p>
      </div></body></html>`,
    };
  } else {
    // Fallback: submission still stored (Netlify Forms also captures it)
    return {
      statusCode: 200,
      headers: { "Content-Type": "text/html" },
      body: `${HTML_HEAD}<div class="card">
        <div class="icon">✅</div>
        <h1>Submission received</h1>
        <p>Thanks for submitting <strong>${business_name}</strong>. We'll review and publish your listing within 48 hours — we'll email you at ${contact_email} to confirm.</p>
        <p style="margin-top:24px"><a href="/psychologists.html">← Browse the directory</a></p>
      </div></body></html>`,
    };
  }
};
