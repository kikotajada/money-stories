# money-stories.ch

Website for **Money Stories** (Swiss money for expats, explained with stories). Plain static HTML and CSS, served by **Netlify** from `public/`, plus one small function for the paid-kit download page. Same setup as historiasdepasta.es.

## Structure

| Path | What it is |
|---|---|
| `public/index.html` | Home (keeps its own inline styles) |
| `public/start/` | Free guide "Start Like Leo" (generated) |
| `public/first-year-investing/` | Paid kit page "Your First Year Investing in Switzerland" (generated) |
| `public/products/` | Products overview (generated) |
| `public/css/site.css` | Shared styles of the inner pages |
| `public/img/kit/` | Web-sized kit images, mock-ups and OG images |
| `content/start_like_leo.md` | Text of the free guide (exported from the Claude Doc) |
| `scripts/build_pages.py` | Builds `start/`, `first-year-investing/`, `products/` and the download template. Run `python3 scripts/build_pages.py` after any change |
| `templates/thanks-first-year-investing.html` | Download page (never in `public/`) |
| `netlify/functions/thanks-first-year-investing.mjs` + `src/thanks.js` | Serve the download page only for a paid Stripe Checkout session |

Header and footer of the inner pages live in `scripts/build_pages.py`.

## Paid kit and download page

- The Stripe Payment Link must redirect after payment to `https://money-stories.ch/first-year-investing/thanks?session_id={CHECKOUT_SESSION_ID}` (exactly like that; Stripe fills in the ID).
- Netlify environment variables: `STRIPE_KEY` (secret; restricted key, read access to Checkout Sessions only) and optionally `PLINK_FIRST_YEAR_INVESTING` (the `plink_…` ID) so only this kit's payments unlock the page.
- `STRIPE_LINK`, `SHEET_ID` and `PDF_FILE_ID` at the top of `scripts/build_pages.py` hold the buy link and the Drive download IDs. Until `STRIPE_LINK` is set, the buy buttons show "Coming soon".

## Hosting (Netlify)

`netlify.toml` sets everything: publish folder `public`, build command `node scripts/build-templates.mjs`, functions in `netlify/functions`, `www` → bare domain. Every push to `main` deploys.

Moving from GitHub Pages: create the Netlify site from this repo, add the env variables, add the custom domain `money-stories.ch` (+ `www`), point the DNS at hosttech to Netlify (the values Netlify shows when you add the domain), then turn off GitHub Pages.

Local test: `npx netlify-cli dev` (needs `STRIPE_KEY` in `.env` to unlock the download page).
