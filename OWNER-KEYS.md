# NewcastleLocal — Practice Update Links

Private reference for the site owner. Send each practice their unique update link.

Replace `https://your-site.netlify.app` with your live domain.

---

| Practice | Update Link |
|---|---|
| NewPsych Psychologists | `https://your-site.netlify.app/update/?slug=newpsych-psychologists&key=np-x7k9m2p4` |
| Elevated Wellbeing Psychology | `https://your-site.netlify.app/update/?slug=elevated-wellbeing-psychology&key=ew-r3t8n6q1` |
| New Lambton Psychology | `https://your-site.netlify.app/update/?slug=new-lambton-psychology&key=nl-b5w2j9k7` |
| Lacuna Clinical Psychology | `https://your-site.netlify.app/update/?slug=lacuna-clinical-psychology&key=lc-v9d4f2s8` |
| Oracle Psychology | `https://your-site.netlify.app/update/?slug=oracle-psychology&key=op-m1z6c3h5` |
| Psychology Centre Newcastle | `https://your-site.netlify.app/update/?slug=psychology-centre-newcastle&key=pc-a8y5t1w3` |
| Wildflower Psychology | `https://your-site.netlify.app/update/?slug=wildflower-psychology&key=wp-k4r7e9u2` |
| ELD Psychology | `https://your-site.netlify.app/update/?slug=eld-psychology&key=el-q2n8g5j6` |
| Esteem Psychology | `https://your-site.netlify.app/update/?slug=esteem-psychology&key=es-f6h3b1c9` |
| Dyer & Dyer Psychologists | `https://your-site.netlify.app/update/?slug=dyer-and-dyer-psychologists&key=dd-u5m7w4p3` |
| Cerenova | `https://your-site.netlify.app/update/?slug=cerenova&key=ce-t9p2l8r4` |

---

## Setting up email notifications (one-time, 5 minutes)

This is what makes you receive an email every time a practice submits changes.

1. Log in to [app.netlify.com](https://app.netlify.com)
2. Open your site → **Site configuration** → **Forms**
3. After the first form submission comes through, you'll see **listing-update** appear in the forms list
4. Click **listing-update** → **Form notifications** → **Add notification** → **Email notification**
5. Enter `info@cerenova.com.au` and save

From that point on, every practice submission triggers an instant email to you.

> **Before the first real submission:** Netlify only shows forms that have had at least one submission. To test it, open one of your own update links, fill in the form, and click Submit. Once that comes through, set up the email notification as above.

---

## When you receive an update email

The email shows exactly what changed. To publish the changes:

1. Open `data/psychologists.json`
2. Find the listing by slug
3. Update the relevant fields
4. Run `python generate.py` (if using the generator)
5. Commit and push → Netlify redeploys automatically

Total time: about 5 minutes.
