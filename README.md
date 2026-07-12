# Bathroom Renovation DIY vs Professional - Static Site

This is a custom-built, ultra-fast static site generator designed for SEO and Google AdSense readiness.

## Directory Structure
- `content/`: Contains all Markdown files.
  - `articles/`: Add new blog posts here as `.md` files.
  - `pages/`: Static pages like About, Contact, Privacy Policy.
- `templates/`: Jinja2 HTML templates used to compile the site.
- `assets/`: CSS, JS, and image files.
- `public/`: The final built output. **Deploy this directory.**
- `build.py`: The python script that generates the static site.

## How to Add New Articles

1. Create a new `.md` file in `content/articles/` (e.g., `my-new-guide.md`).
2. Add the YAML frontmatter at the top:
   ```yaml
   ---
   title: "My New Guide"
   description: "A short meta description here."
   author: "Your Name"
   date: "YYYY-MM-DD"
   category: "diy-guides"
   ---
   ```
3. Write your content in Markdown below the frontmatter. Use `#` for the H1 title and `##` for H2 subheadings.
4. Run the build script: `python build.py`. The new article will automatically be added to the homepage, `sitemap.xml`, `rss.xml`, and the search index.

## Inserting Google AdSense

To add your AdSense code, open `templates/base.html`.
- Add the main `<script data-ad-client="ca-pub-..." async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>` to the `<head>` block.
- For manual ad placements, you can edit `templates/article.html` and add the AdSense `<ins>` blocks where you want them (e.g., mid-article or end-of-article).

## Connecting the Newsletter Form

The current newsletter form is a placeholder UI located in two places:
- Footer: `templates/base.html`
- Mid-Article: `templates/article.html`

To connect to a real email provider (like Mailchimp or ConvertKit), update the `<form action="#">` tag in those templates to point to your provider's form action URL and ensure the input `name` attribute matches their requirements.

## Deployment

Simply upload the contents of the `public/` directory to any static hosting service (Cloudflare Pages, Vercel, Netlify, or standard CDN/FTP).
Your Service Worker (`sw.js`) will handle caching automatically for repeat visitors.
Google Search Console verification can be done by either placing the verification HTML file in the `assets/` folder (then running `build.py`) or using DNS verification.

## Testing Locally
Run this command from the root of the project to test the compiled site:
```bash
cd public
python -m http.server 8000
```
Then visit `http://localhost:8000` in your browser.
