# Publishing on GitHub Pages

1. Create the GitHub repository priestap/operationbarnabasinternational.
   - Pages on a **private** repository needs a paid GitHub plan.
   - On a free account, make the repository **public**. Nothing private is committed: the export and .env files are ignored, and the Formspree endpoint is public by design.
2. Commit and push, including docs/.
3. Set the Pages source: Settings → Pages → Build and deployment → "Deploy from a branch" → main, /docs.
4. Check the temporary URL https://priestap.github.io/operationbarnabasinternational/.
   - Pages and images
   - Mobile menu
   - Dark mode
   - Redirect stubs, for example /about/contact/
5. Switch the domain:
   - Under Settings → Pages → Custom domain, enter operationbarnabasinternational.com. GitHub commits docs/CNAME, so pull before your next build.
   - At the DNS provider, point the apex domain at GitHub Pages with four A records: 185.199.108.153, .109.153, .110.153 and .111.153. Add a CNAME for www pointing to priestap.github.io.
   - Keep the existing MX and TXT records.
   - Turn on "Enforce HTTPS" once the certificate is issued.
6. Once the new site is live, cancel the Flywheel plan.

To update the site: edit, rebuild, commit, and push. Pages redeploys within a minute or two.
