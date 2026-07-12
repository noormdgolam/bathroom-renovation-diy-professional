import os
import re
import json
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader

# Configuration
CONTENT_DIR = "content"
ARTICLES_DIR = os.path.join(CONTENT_DIR, "articles")
PAGES_DIR = os.path.join(CONTENT_DIR, "pages")
TEMPLATES_DIR = "templates"
ASSETS_DIR = "assets"
PUBLIC_DIR = "."
SITE_URL = "https://bathroom-renovation-diy-professional.bongshai.com"
SITE_NAME = "Bathroom Renovation DIY Guide"

# Hub Data for SEO Topic Clusters
HUBS = {
    "costs": {"title": "Bathroom Renovation Costs", "description": "Comprehensive guides comparing the costs of DIY bathroom remodeling versus hiring professional contractors."},
    "plumbing": {"title": "Bathroom Plumbing Guides", "description": "Expert advice on bathroom plumbing, from basic DIY fixes to knowing when you must hire a licensed plumber."},
    "tiling": {"title": "Flooring & Tiling", "description": "Guides and tutorials on bathroom flooring, tile selection, and installation best practices."},
    "fixtures-fittings": {"title": "Fixtures & Fittings", "description": "Reviews and installation guides for bathroom fixtures, vanities, and hardware."},
    "design-planning": {"title": "Design & Planning", "description": "Inspiration, layouts, and planning tips for a successful bathroom renovation project."}
}

# Setup Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def parse_markdown(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    metadata = {}
    content = text
    
    if match:
        frontmatter_str = match.group(1)
        content = match.group(2)
        for line in frontmatter_str.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip().strip('"').strip("'")
                
    html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
    # Inject Newsletter after second H2
    newsletter_html = """
    <div class="newsletter-inline">
        <h3>Want more DIY tips?</h3>
        <p>Subscribe to our newsletter for weekly guides.</p>
        <form onsubmit="event.preventDefault(); alert('Subscribed!');">
            <input type="email" placeholder="Email Address" required>
            <button type="submit" class="btn">Join</button>
        </form>
    </div>
    """
    
    parts = html_content.split('<h2>', 2)
    if len(parts) > 2:
        # Re-attach the <h2> tags since split removes them
        html_content = parts[0] + '<h2>' + parts[1] + '<h2>' + newsletter_html + parts[2]
        
    return metadata, html_content

def build_site():
    articles = []
    hub_articles = {key: [] for key in HUBS.keys()}
    
    # Process Articles (Parse Metadata)
    for filename in os.listdir(ARTICLES_DIR):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(ARTICLES_DIR, filename)
        metadata, html_content = parse_markdown(filepath)
        
        slug = metadata.get("slug", filename[:-3])
        category = metadata.get("category", "")
        metadata['url'] = f"/articles/{slug}.html"
        metadata['html_content'] = html_content
        metadata['slug'] = slug
        
        articles.append(metadata)
        if category in hub_articles:
            hub_articles[category].append(metadata)
            
    # Sort everything by date
    articles.sort(key=lambda x: x.get("date", ""), reverse=True)
    for cat in hub_articles:
        hub_articles[cat].sort(key=lambda x: x.get("date", ""), reverse=True)
        
    # Process Articles (Render)
    article_template = env.get_template("article.html")
    for metadata in articles:
        category = metadata.get("category", "")
        slug = metadata.get("slug")
        hub_title = HUBS.get(category, {}).get("title", category)
        
        # Get 5 related articles
        related_articles = [a for a in hub_articles.get(category, []) if a.get("slug") != slug][:5]
        
        output_html = article_template.render(
            site_name=SITE_NAME,
            site_url=SITE_URL,
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            author=metadata.get("author", "Editorial Team"),
            date=metadata.get("date", ""),
            category=category,
            hub_title=hub_title,
            related_articles=related_articles,
            content=metadata['html_content'],
            url=metadata['url']
        )
        
        out_dir = os.path.join(PUBLIC_DIR, "articles")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        with open(os.path.join(out_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(output_html)
    
    # Process Category Hubs (Pillar Pages)
    category_template = env.get_template("category.html")
    for cat_slug, cat_data in HUBS.items():
        cat_data['articles'] = hub_articles.get(cat_slug, [])
        cat_data['articles'].sort(key=lambda x: x.get("date", ""), reverse=True)
        
        output_html = category_template.render(
            site_name=SITE_NAME,
            site_url=SITE_URL,
            title=cat_data["title"],
            description=cat_data["description"],
            articles=cat_data['articles'],
            url=f"/category/{cat_slug}.html"
        )
        
        cat_dir = os.path.join(PUBLIC_DIR, "category")
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir)
            
        with open(os.path.join(cat_dir, f"{cat_slug}.html"), "w", encoding="utf-8") as f:
            f.write(output_html)
            
    # Process Pages
    page_template = env.get_template("page.html")
    for filename in os.listdir(PAGES_DIR):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(PAGES_DIR, filename)
        metadata, html_content = parse_markdown(filepath)
        
        slug = metadata.get("slug", filename[:-3])
        
        output_html = page_template.render(
            site_name=SITE_NAME,
            site_url=SITE_URL,
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            content=html_content,
            url=f"/{slug}.html"
        )
        
        with open(os.path.join(PUBLIC_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(output_html)
            
    # Generate Index (Home)
    index_template = env.get_template("index.html")
    output_html = index_template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        title=f"Home | {SITE_NAME}",
        description="Your ultimate guide to DIY vs Professional bathroom renovation.",
        articles=articles[:12], # Show latest 12 on home
        hubs=HUBS,
        url="/"
    )
    with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(output_html)
        
    # Generate 404
    try:
        template_404 = env.get_template("404.html")
        output_html = template_404.render(
            site_name=SITE_NAME,
            site_url=SITE_URL,
            title=f"Page Not Found | {SITE_NAME}",
            description="The page you are looking for does not exist.",
            url="/404.html"
        )
        with open(os.path.join(PUBLIC_DIR, "404.html"), "w", encoding="utf-8") as f:
            f.write(output_html)
    except:
        pass
        
    with open(os.path.join(PUBLIC_DIR, "searchIndex.json"), "w", encoding="utf-8") as f:
        json.dump(articles, f)
        
    generate_rss(articles)
    generate_sitemap(articles, HUBS)
    generate_pwa()

def generate_rss(articles):
    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>{SITE_NAME}</title>
  <link>{SITE_URL}</link>
  <description>Your ultimate guide to DIY vs Professional bathroom renovation.</description>
"""
    for a in articles:
        rss += f"""  <item>
    <title>{a.get('title')}</title>
    <link>{SITE_URL}{a.get('url')}</link>
    <description>{a.get('description')}</description>
    <pubDate>{a.get('date')}</pubDate>
  </item>
"""
    rss += "</channel>\n</rss>"
    with open(os.path.join(PUBLIC_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(rss)

def generate_sitemap(articles, hubs):
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE_URL}/about.html</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{SITE_URL}/contact.html</loc>
    <priority>0.8</priority>
  </url>
"""
    for slug in hubs.keys():
        sitemap += f"""  <url>
    <loc>{SITE_URL}/category/{slug}.html</loc>
    <priority>0.9</priority>
  </url>
"""
    for a in articles:
        sitemap += f"""  <url>
    <loc>{SITE_URL}{a.get('url')}</loc>
    <priority>0.6</priority>
  </url>
"""
    sitemap += "</urlset>"
    with open(os.path.join(PUBLIC_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

def generate_pwa():
    manifest = {
        "name": SITE_NAME,
        "short_name": "Bath Reno DIY",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#005f73",
        "icons": [
            {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    with open(os.path.join(PUBLIC_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f)
        
    sw = """
const CACHE_NAME = 'bath-reno-v2';
const urlsToCache = [
  '/',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/js/search.js',
  '/searchIndex.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) return response;
        return fetch(event.request).then(function(response) {
            if(!response || response.status !== 200 || response.type !== 'basic') return response;
            var responseToCache = response.clone();
            caches.open(CACHE_NAME).then(function(cache) { cache.put(event.request, responseToCache); });
            return response;
          }
        );
      })
  );
});
"""
    with open(os.path.join(PUBLIC_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)
        
    robots = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(PUBLIC_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

if __name__ == "__main__":
    print("Building static site (Phase 2)...")
    build_site()
    print("Build complete.")
