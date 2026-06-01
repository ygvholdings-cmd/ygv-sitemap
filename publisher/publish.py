#!/usr/bin/env python3
"""YGV Cash Buyers - Automated Blog Publisher (GitHub Actions)"""
import os, re, sys, json, base64
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    import subprocess; subprocess.run(["pip","install","requests","-q"],check=True); import requests

try:
    import anthropic
except ImportError:
    import subprocess; subprocess.run(["pip","install","anthropic","-q"],check=True); import anthropic

TOPICS = [
    "how to sell your house fast in Cincinnati Ohio",
    "what cash home buyers look for in Cincinnati",
    "how the cash home buying process works step by step",
    "how to avoid foreclosure in Cincinnati Ohio",
    "selling an inherited home in Cincinnati Ohio",
    "selling a house during divorce in Cincinnati",
    "selling a damaged or distressed home for cash",
    "what does selling a house as-is really mean",
    "comparing cash offers vs listing with a real estate agent",
    "how to sell a rental property fast in Cincinnati",
    "what happens after you accept a cash offer on your home",
    "common mistakes homeowners make when trying to sell fast",
    "how to get a fair cash offer for your Cincinnati home",
    "selling a hoarder house or cluttered home in Cincinnati",
    "how to handle liens and title issues when selling your home",
    "estate sales and probate property in Cincinnati Ohio",
    "downsizing in Cincinnati tips for selling your home fast",
    "why Cincinnati homeowners choose cash buyers over realtors",
    "how to sell a house with code violations in Cincinnati",
    "selling your home fast during a job relocation from Cincinnati",
]

IMG = {
    0:  "https://images.pexels.com/photos/8469940/pexels-photo-8469940.jpeg?auto=compress&cs=tinysrgb&w=1200",
    1:  "https://images.pexels.com/photos/32497163/pexels-photo-32497163.jpeg?auto=compress&cs=tinysrgb&w=1200",
    2:  "https://images.pexels.com/photos/48148/document-agreement-documents-sign-48148.jpeg?auto=compress&cs=tinysrgb&w=1200",
    3:  "https://images.pexels.com/photos/7937733/pexels-photo-7937733.jpeg?auto=compress&cs=tinysrgb&w=1200",
    4:  "https://images.pexels.com/photos/36794346/pexels-photo-36794346.jpeg?auto=compress&cs=tinysrgb&w=1200",
    5:  "https://images.pexels.com/photos/7876037/pexels-photo-7876037.jpeg?auto=compress&cs=tinysrgb&w=1200",
    6:  "https://images.pexels.com/photos/7937764/pexels-photo-7937764.jpeg?auto=compress&cs=tinysrgb&w=1200",
    7:  "https://images.pexels.com/photos/7641828/pexels-photo-7641828.jpeg?auto=compress&cs=tinysrgb&w=1200",
    8:  "https://images.pexels.com/photos/8293781/pexels-photo-8293781.jpeg?auto=compress&cs=tinysrgb&w=1200",
    9:  "https://images.pexels.com/photos/8482510/pexels-photo-8482510.jpeg?auto=compress&cs=tinysrgb&w=1200",
    10: "https://images.pexels.com/photos/34134899/pexels-photo-34134899.jpeg?auto=compress&cs=tinysrgb&w=1200",
    11: "https://images.pexels.com/photos/8469934/pexels-photo-8469934.jpeg?auto=compress&cs=tinysrgb&w=1200",
    12: "https://images.pexels.com/photos/8482523/pexels-photo-8482523.jpeg?auto=compress&cs=tinysrgb&w=1200",
    13: "https://images.pexels.com/photos/7203849/pexels-photo-7203849.jpeg?auto=compress&cs=tinysrgb&w=1200",
    14: "https://images.pexels.com/photos/7054510/pexels-photo-7054510.jpeg?auto=compress&cs=tinysrgb&w=1200",
    15: "https://images.pexels.com/photos/6862089/pexels-photo-6862089.jpeg?auto=compress&cs=tinysrgb&w=1200",
    16: "https://images.pexels.com/photos/7937207/pexels-photo-7937207.jpeg?auto=compress&cs=tinysrgb&w=1200",
    17: "https://images.pexels.com/photos/27522902/pexels-photo-27522902.jpeg?auto=compress&cs=tinysrgb&w=1200",
    18: "https://images.pexels.com/photos/8293678/pexels-photo-8293678.jpeg?auto=compress&cs=tinysrgb&w=1200",
    19: "https://images.pexels.com/photos/4554377/pexels-photo-4554377.jpeg?auto=compress&cs=tinysrgb&w=1200",
}


def get_published_slugs():
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/ygvholdings-cmd/ygv-sitemap/main/sitemap.xml",
            timeout=10)
        return re.findall(r"ygvcashbuyers\.com/post/([^<\s]+)", r.text)
    except Exception as e:
        print(f"WARN sitemap fetch: {e}"); return []


def generate_blog_post(topic, slugs):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    slug_hint = (
        "\nFor internal linking, link to one of these published posts if relevant: "
        + ", ".join(slugs[:6])
    ) if slugs else ""

    prompt = (
        f"Write a high-quality SEO blog post for YGV Cash Buyers (ygvcashbuyers.com), "
        f"a cash home buying company in Cincinnati, Ohio.\n\n"
        f"Topic: {topic}\n\n"
        f"Requirements:\n"
        f"- 650-850 words, warm and helpful tone, NOT salesy\n"
        f"- First 2-3 sentences directly answer the topic (no preamble like 'In this post...')\n"
        f"- Use ## for H2 subheadings throughout\n"
        f"- Do NOT include the post title in the body\n"
        f"- Reference Cincinnati, Hamilton County, or Greater Cincinnati naturally\n"
        f"- End with a soft CTA mentioning YGV Cash Buyers"
        f"{slug_hint}\n\n"
        f"Return ONLY in this exact format, no extra text before or after:\n"
        f"TITLE: compelling SEO title (50-60 chars)\n"
        f"SLUG: url-slug-here\n"
        f"---BODY---\n"
        f"[full post body with ## headings]\n"
        f"---FAQ---\n"
        f"Q: [question a Cincinnati homeowner would Google]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]"
    )

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


def to_html(txt):
    lines = txt.split("\n"); parts = []; para = []

    def fl():
        if para:
            p = " ".join(para)
            p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", p)
            p = re.sub(r"\*(.*?)\*", r"<em>\1</em>", p)
            p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
            parts.append("<p>" + p + "</p>"); para.clear()

    for line in lines:
        s = line.strip()
        if s.startswith("## "):   fl(); parts.append("<h2>" + s[3:] + "</h2>")
        elif s.startswith("# "): fl()
        elif s == "":             fl()
        else:                     para.append(s)
    fl()
    return "\n".join(parts)


ST = chr(60) + 'script type="application/ld+json">'
ET = chr(60) + "/script>"


def sc(d):
    return "\n" + ST + "\n" + json.dumps(d, indent=2) + "\n" + ET


def main():
    # Step 1: Determine topic
    slugs = get_published_slugs()
    idx = len(slugs) % len(TOPICS)
    topic = TOPICS[idx]
    print(f"Published posts: {len(slugs)} -> topic index {idx}: {topic}")

    # Step 2: Generate content via Claude API
    print("Calling Claude API...")
    raw = generate_blog_post(topic, slugs)

    title_m = re.search(r"^TITLE:\s*(.+)$", raw, re.M)
    slug_m  = re.search(r"^SLUG:\s*(.+)$",  raw, re.M)
    if not title_m or not slug_m:
        print("ERROR: bad format from Claude"); print(raw[:500]); sys.exit(1)

    title = title_m.group(1).strip()
    slug  = re.sub(r"[^a-z0-9-]", "", slug_m.group(1).strip().lower().replace(" ", "-"))
    bm    = re.search(r"---BODY---\n([\s\S]+?)(?=---FAQ---|\Z)", raw)
    body  = bm.group(1).strip() if bm else ""

    faqs = []
    fm = re.search(r"---FAQ---\n([\s\S]+)", raw)
    if fm:
        cq = None
        for ln in fm.group(1).strip().split("\n"):
            ln = ln.strip()
            if ln.startswith("Q: "):          cq = ln[3:]
            elif ln.startswith("A: ") and cq: faqs.append({"q": cq, "a": ln[3:]}); cq = None

    # Step 3: Build HTML + all schemas
    img   = IMG.get(idx, IMG[0])
    bhtml = to_html(body)
    wc    = len(re.sub(r"<[^>]+>", " ", bhtml).split())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base_url = "https://ygvcashbuyers.com"
    post_url = f"{base_url}/post/{slug}"

    eeat = (
        '<div class="about-publisher"><p><strong>About YGV Cash Buyers:</strong> '
        "A local cash home buying company serving Cincinnati and Hamilton County. "
        "We buy homes in any condition — no repairs, no commissions, close in as little as 7 days. "
        '<a href="https://ygvcashbuyers.com">ygvcashbuyers.com</a>.</p></div>'
    )

    fqhtml = (
        "<h2>Frequently Asked Questions</h2><dl>\n" +
        "".join(f'<dt><strong>{f["q"]}</strong></dt><dd>{f["a"]}</dd>\n' for f in faqs) +
        "</dl>"
    ) if faqs else ""

    bpsc = sc({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": title, "datePublished": today, "dateModified": today,
        "author":    {"@type": "Organization", "name": "YGV Cash Buyers", "url": base_url},
        "publisher": {"@type": "Organization", "name": "YGV Cash Buyers", "url": base_url},
        "url": post_url, "mainEntityOfPage": post_url,
        "keywords": topic, "wordCount": wc,
        "about":    [{"@type": "Thing", "name": topic}],
        "mentions": [
            {"@type": "Place", "name": "Cincinnati",
             "sameAs": "https://www.wikidata.org/wiki/Q43196"},
            {"@type": "Place", "name": "Hamilton County, Ohio",
             "sameAs": "https://www.wikidata.org/wiki/Q486291"},
        ]
    })

    fqsc = sc({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs
        ]
    }) if faqs else ""

    steps = [
        {"@type": "HowToStep", "name": m.group(1)}
        for m in re.finditer(r"<h2>(.*?)</h2>", bhtml)
        if not re.search(r"faq|frequently", m.group(1), re.I)
    ]
    hwsc = sc({"@context": "https://schema.org", "@type": "HowTo",
               "name": topic, "step": steps}) \
        if steps and re.match(r"^how (to|the) ", topic, re.I) else ""

    bcsc = sc({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",  "item": f"{base_url}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog",  "item": f"{base_url}/blog"},
            {"@type": "ListItem", "position": 3, "name": title,   "item": post_url},
        ]
    })

    html = f"<h1>{title}</h1>{bhtml}{eeat}{fqhtml}{bpsc}{fqsc}{hwsc}{bcsc}"
    print(f"Title: {title}\nSlug:  {slug}\nFAQs:  {len(faqs)}\nWords: {wc}\nHTML:  {len(html)} chars")

    # Step 4: Publish to GoHighLevel
    ghl_key = os.environ["GHL_API_KEY"]
    r = requests.post(
        "https://services.leadconnectorhq.com/blogs/posts",
        headers={"Authorization": f"Bearer {ghl_key}", "Content-Type": "application/json",
                 "Version": "2021-07-28"},
        json={
            "locationId": "fgK4QNPrkW9TsnxdOLjN", "blogId": "fp2IcYMIduN23MjmXgRE",
            "title": title, "rawHTML": html, "status": "PUBLISHED",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "urlSlug": slug, "imageUrl": img,
            "tags": ["cash buyers", "Cincinnati", "sell house fast"],
        }
    )
    if r.status_code in (200, 201):
        post_id = r.json().get("blogPost", {}).get("_id", "")
        print(f"GHL OK - {post_id}\n{post_url}")
    else:
        print(f"GHL FAIL - {r.status_code}: {r.text[:300]}"); sys.exit(1)

    # Step 5: Update sitemap on GitHub
    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    gh_url   = "https://api.github.com/repos/ygvholdings-cmd/ygv-sitemap/contents/sitemap.xml"
    gh_h     = {"Authorization": f"token {gh_token}", "User-Agent": "ygv-blog-publisher"}
    try:
        g = requests.get(gh_url, headers=gh_h, timeout=15)
        if g.status_code == 200:
            d   = g.json()
            old = base64.b64decode(d["content"]).decode()
            urls = list(dict.fromkeys(
                [f"{base_url}/", f"{base_url}/blog", f"{base_url}/contact"] +
                re.findall(r"<loc>(.*?)</loc>", old) +
                [post_url]
            ))
            xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join(
                    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
                    for u in urls
                ) + "</urlset>"
            )
            p = requests.put(
                gh_url,
                headers={**gh_h, "Content-Type": "application/json"},
                json={"message": f"Add /post/{slug}",
                      "content": base64.b64encode(xml.encode()).decode(),
                      "sha": d["sha"]}
            )
            print(f"GitHub sitemap - {p.status_code}")
        else:
            print(f"WARN GitHub: {g.status_code}")
    except Exception as e:
        print(f"WARN GitHub: {e}")

    # Step 6: Ping Google
    try:
        pg = requests.get(
            "https://www.google.com/ping?sitemap=https%3A%2F%2Fygvcashbuyers.com%2Fsitemap.xml",
            timeout=10)
        print(f"Google ping - {pg.status_code}")
    except Exception:
        pass

    print(f"\nDONE - {title}\n{post_url}")


if __name__ == "__main__":
    main()
