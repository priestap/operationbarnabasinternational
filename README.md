# Operation Barnabas International — static site

A small static rebuild of operationbarnabasinternational.com, made from its WordPress export. It is compiled on your computer and the output, docs/, is committed. GitHub Pages serves docs/ for free, with no build step or hosting service.

Rebuild after any change:

    python3 scripts/build.py ~/Downloads/operationbarnabasinternational.WordPress.2026-10-31.xml

Preview:

    python3 -m http.server 8090 -d docs

Open http://localhost:8090/ .

Keep the WordPress export outside this repository: it contains drafts and author records (.gitignore also blocks *.xml).

## What to edit

- style.css: styling. The build copies it to docs/style.css.
- conferences.html: the conference schedule. Edit it and rebuild.
- assets/: images and scripts, copied to docs/assets/.
- source-photos/: put full-size photo downloads here. Git ignores this folder. Resize and rename a photo into assets/photos/ before using it on the site.
- scripts/build.py: page text for Home, Contact, and Donate, plus navigation.
- posts/: new updates, one .txt file per post. The file name becomes the URL, for example posts/in-the-andamans.txt is published at /in-the-andamans/. Start the file with title:, date: (YYYY-MM-DD) and category: (News or Devotionals) lines, then a --- line, then the text. A blank line starts a new paragraph, and <h2>…</h2> makes a heading.
- About and the original four posts come from the export.

The build deletes docs/ and rewrites it, except docs/CNAME, which GitHub Pages creates when you set the custom domain.

## Contact form

The form stays hidden until FORM_ENDPOINT is set at the top of scripts/build.py. Until then the Contact page shows only the address and phone numbers. To turn it on:

1. Create a free Formspree form.
2. Route it to jerryachristian@hotmail.com. That was the old WordPress form's recipient.
3. Paste the endpoint into FORM_ENDPOINT and rebuild.

assets/contact-form.js matches the Vision For Christ form.

## Legacy WordPress URLs

GitHub Pages does not support server-side redirects. The build handles old URLs in two ways:

- **Moved paths:** /about/contact/, /about/donate/, /home/, /photos/, /category/devotionals/, /category/news/, /devotionals-test/ and /sample-page/ each get a small meta-refresh page.
- **Numeric links:** a script in the homepage forwards ?p= and ?page_id= links.

Posts keep their original root-level permalinks, for example /is-hope-a-rare-commodity/.

All links are relative, so the site works on the temporary username.github.io/repo/ URL and on the custom domain. The exception is 404.html, which assumes the custom domain.
