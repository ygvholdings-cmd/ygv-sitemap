#!/usr/bin/env python3
"""YGV Cash Buyers - Automated Blog Publisher (GitHub Actions)"""
import os, re, sys, json, base64, time, random
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
    # Core topics (0-19)
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
    # Neighborhood-specific topics (20-39)
    "sell my house fast in Hyde Park Cincinnati Ohio",
    "cash home buyers in Blue Ash Ohio",
    "sell your home fast in Mason Ohio",
    "how to sell a house fast in Norwood Ohio",
    "cash buyers for homes in Anderson Township Ohio",
    "sell my house fast in West Chester Ohio",
    "cash home buyers in Loveland Ohio",
    "how to sell a house fast in Fairfield Ohio",
    "sell your home fast in Montgomery Ohio",
    "cash buyers in Oakley Cincinnati Ohio",
    "sell my house fast in Kenwood Cincinnati Ohio",
    "how to sell a home in Madeira Ohio for cash",
    "cash home buyers in Sharonville Ohio",
    "selling a house fast in Milford Ohio",
    "sell my house fast in Symmes Township Ohio",
    "how to sell a house fast in Colerain Township Ohio",
    "cash home buyers in Reading Ohio",
    "sell your house fast in Cheviot Ohio",
    "how to sell a home in Price Hill Cincinnati",
    "cash home buyers in College Hill Cincinnati Ohio",
    # Series 2 (40+): fresh angles added 2026-10-06 once the first 40 had been used ~twice over.
    # Situations - each targets a distinct seller problem not covered above.
    "how to sell a vacant house in Cincinnati Ohio",
    "selling a house with foundation problems in Cincinnati",
    "selling a fire-damaged house in Cincinnati for cash",
    "selling a house with mold or water damage in Cincinnati",
    "selling a house with tenants still living in it in Ohio",
    "selling a house with unpaid property taxes in Hamilton County Ohio",
    "selling a house with a reverse mortgage in Ohio",
    "what to do when you owe more than your house is worth in Cincinnati",
    "selling a house with an old or leaking roof in Cincinnati",
    "selling a rental house after a bad tenant or eviction in Ohio",
    "selling an inherited house when siblings disagree in Ohio",
    "how to sell a house without a realtor in Ohio",
    "how much do cash home buyers pay in Cincinnati",
    "how to tell if a cash home buyer is legitimate in Ohio",
    "how long does it take to sell a house in Cincinnati",
    "who pays closing costs when you sell a house in Ohio",
    "Ohio seller disclosure requirements explained",
    "do you need repairs or a home inspection before selling in Ohio",
    "selling a house during bankruptcy in Ohio",
    "what happens at a sheriff sale in Hamilton County Ohio",
    "selling the family home after the death of a spouse in Cincinnati",
    "selling your house to pay for assisted living or nursing care in Ohio",
    "selling an outdated house without renovating in Cincinnati",
    "what to do when a buyer backs out of your Cincinnati home sale",
    "best time of year to sell a house in Cincinnati",
    "selling a house in winter in Cincinnati",
    "cash offer vs conventional financing which closes faster in Ohio",
    "selling a house with an open building permit in Ohio",
    "selling a house with no will when the owner died intestate in Ohio",
    "selling an inherited Cincinnati house when you live out of state",
    "selling an older Cincinnati home with lead paint or asbestos",
    # Neighborhoods and suburbs
    "sell my house fast in Springdale Ohio",
    "cash home buyers in Forest Park Ohio",
    "sell your house fast in Glendale Ohio",
    "cash buyers for homes in Wyoming Ohio",
    "how to sell a house fast in Silverton Ohio",
    "sell my house fast in Deer Park Ohio",
    "cash home buyers in Evendale Ohio",
    "selling a home in Indian Hill Ohio for cash",
    "sell your house fast in Mariemont Ohio",
    "cash home buyers in Delhi Township Ohio",
    "sell my house fast in Green Township Ohio",
    "cash buyers for homes in Westwood Cincinnati",
    "how to sell a house fast in Cleves Ohio",
    "sell my house fast in Harrison Ohio",
    "cash home buyers in Miami Township Ohio",
    "sell your house fast in Batavia Ohio",
    "cash buyers for homes in Amelia Ohio",
    "how to sell a house fast in Union Township Ohio",
    "sell my house fast in Springfield Township Ohio",
    "cash home buyers in Mt. Healthy Ohio",
    "sell your house fast in Finneytown Ohio",
    "cash buyers for homes in Pleasant Ridge Cincinnati",
    "how to sell a house fast in Madisonville Cincinnati",
    "sell my house fast in Mt. Lookout Cincinnati",
    "cash home buyers in Northside Cincinnati",
    "sell your house fast in Clifton Cincinnati",
    "cash buyers for homes in Walnut Hills Cincinnati",
    "how to sell a house fast in Avondale Cincinnati",
    "sell my house fast in Sayler Park Cincinnati",
    "cash home buyers in St. Bernard Ohio",
    "sell your house fast in Greenhills Ohio",
    "cash buyers for homes in North College Hill Ohio",
    "how to sell a house fast in Lebanon Ohio",
    "sell my house fast in Hamilton Ohio",
    "cash home buyers in Middletown Ohio",
]

# Posts published on/after this instant belong to series 2; the next topic index is
# SERIES2_START_IDX + (number of such posts), derived from GHL itself so it cannot drift.
SERIES2_START_IDX = 40
SERIES2_CUTOVER   = "2026-10-07T00:00:00+00:00"

GHL_CATEGORY_ID = "6abbc7c8e1ac9e6cde4af85e"  # "Home Selling Tips" — created once via REIReply UI
GHL_AUTHOR_ID   = "6abbc8647e0007f3be23ed73"  # "YGV Cash Buyers" — created once via REIReply UI

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


def fetch_all_ghl_posts():
    """Return every post from GHL's list endpoint, paginating with limit/offset.

    The endpoint caps a page at 100. A single un-paginated call silently truncates once the
    blog passes 100 posts, which would make the topic-rotation index (len(slugs) % len(TOPICS))
    stop advancing correctly. Returns None on API failure so callers can tell "no posts"
    apart from "couldn't fetch".
    """
    ghl_key = os.environ["GHL_API_KEY"]
    headers = {"Authorization": f"Bearer {ghl_key}", "Version": "2021-07-28"}
    posts, offset, page = [], 0, 100
    try:
        while True:
            r = requests.get(
                "https://services.leadconnectorhq.com/blogs/posts/list",
                headers=headers,
                params={"locationId": "fgK4QNPrkW9TsnxdOLjN", "blogId": "fp2IcYMIduN23MjmXgRE",
                        "limit": page, "offset": offset},
                timeout=15,
            )
            if r.status_code != 200:
                print(f"WARN GHL post list: {r.status_code} {r.text[:150]}"); return None
            batch = r.json().get("blogPosts", [])
            posts.extend(batch)
            if len(batch) < page:
                return posts
            offset += page
    except Exception as e:
        print(f"WARN GHL post list fetch: {e}"); return None


def get_published_slugs():
    """Fetch actual published post slugs directly from GHL — the authoritative source.

    Previously this read from the GitHub-hosted sitemap mirror instead. That mirror's
    own write (update_sitemap, below) fails silently on error, which let its post count
    drift behind GHL's real count (seen: 56 vs 68 actual). Since the topic rotation index
    is `len(slugs) % len(TOPICS)`, that drift caused already-used topics to be re-selected
    long before all 40 had been covered, producing near-duplicate posts on the same topic.
    Querying GHL directly can't drift out of sync with itself.
    """
    posts = fetch_all_ghl_posts() or []
    return [p["urlSlug"] for p in posts if p.get("urlSlug")]


def published_within_days(days):
    """True if GHL already has a post published in the last `days` days.

    Used to make the Tue/Wed fallback cron runs idempotent: they only publish if Monday's
    run never happened. Fails open (returns False) if GHL can't be queried, since a missed
    week is worse than the small risk of an extra pair of posts.
    """
    posts = fetch_all_ghl_posts()
    if not posts:
        return False
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    for p in posts:
        try:
            ts = datetime.fromisoformat(p["publishedAt"].replace("Z", "+00:00")).timestamp()
        except (KeyError, ValueError, AttributeError):
            continue
        if ts >= cutoff:
            return True
    return False


def generate_blog_post(topic, slugs):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    slug_hint = ""
    if len(slugs) >= 3:
        slug_hint = (
            "\nFor internal linking, naturally embed 2-3 links within the body to these "
            "published posts where topically relevant "
            "(use full URL format: https://ygvcashbuyers.com/post/SLUG): "
            + ", ".join(slugs[:15])
        )

    prompt = (
        f"Write a high-quality SEO blog post for YGV Cash Buyers (ygvcashbuyers.com), "
        f"a cash home buying company in Cincinnati, Ohio.\n\n"
        f"Topic: {topic}\n\n"
        f"Requirements:\n"
        f"- 1400-1800 words, warm and helpful tone, NOT salesy\n"
        f"- First 2-3 sentences directly answer the topic (no preamble like 'In this post...')\n"
        f"- Use ## for H2 subheadings throughout (5-8 subheadings)\n"
        f"- Each H2 section should be 150-250 words with concrete, specific advice\n"
        f"- Do NOT include the post title in the body\n"
        f"- Reference Cincinnati, Hamilton County, or Greater Cincinnati naturally\n"
        f"- Include at least one specific local detail (neighborhood, county process, local market fact)\n"
        f"- End with a soft CTA mentioning YGV Cash Buyers"
        f"{slug_hint}\n\n"
        f"Return ONLY in this exact format, no extra text before or after:\n"
        f"TITLE: compelling SEO title (50-60 chars)\n"
        f"SLUG: url-slug-here\n"
        f"META: search-result snippet that earns clicks, 140-160 chars, mentions Cincinnati "
        f"and the core benefit (fast cash offer, no repairs/fees), ends with a soft CTA\n"
        f"IMAGE_ALT: one-sentence accessibility description of a photo that would illustrate this topic\n"
        f"---BODY---\n"
        f"[full post body with ## headings]\n"
        f"---FAQ---\n"
        f"Q: [question a Cincinnati homeowner would Google]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]\n"
        f"Q: [question]\n"
        f"A: [answer in 1-2 sentences]"
    )

    msg = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    text_block = next((b for b in msg.content if hasattr(b, 'text')), None)
    return text_block.text if text_block else ""


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


def get_gbp_access_token():
    cid = os.environ.get("GOOGLE_CLIENT_ID", "")
    cs  = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    rt  = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
    if not all([cid, cs, rt]):
        return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid, "client_secret": cs,
        "refresh_token": rt, "grant_type": "refresh_token"
    }, timeout=10)
    if r.status_code == 200:
        return r.json().get("access_token")
    print(f"WARN GBP token: {r.status_code} {r.text[:150]}")
    return None


def post_to_facebook(title, bhtml, post_url):
    page_id    = os.environ.get("FB_PAGE_ID", "")
    page_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    if not page_id or not page_token:
        print("Facebook skipped - FB_PAGE_ID/FB_PAGE_ACCESS_TOKEN not set"); return
    text   = re.sub(r"<[^>]+>", " ", bhtml)
    text   = re.sub(r"\s+", " ", text).strip()
    teaser = text[:400].rsplit(" ", 1)[0] + "..."
    msg    = f"{title}\n\n{teaser}\n\nRead more: {post_url}"
    r = requests.post(
        f"https://graph.facebook.com/v19.0/{page_id}/feed",
        json={"message": msg, "link": post_url},
        params={"access_token": page_token},
        timeout=15
    )
    status = "OK" if r.status_code in (200, 201) else f"FAIL {r.status_code}: {r.text[:150]}"
    print(f"Facebook post - {status}")


def update_post_seo_metadata(post_id, description, image_alt):
    """Set meta description, image alt text, category, and author on a just-created post.

    The create endpoint (POST /blogs/posts) doesn't take these fields, but the update
    endpoint (PUT /blogs/posts/{id}) does — under different names than the ones that get
    rejected (metaTitle/metaDescription/metaTags all 422 with "property X should not exist").
    Confirmed working 2026-09-29 by inspecting a GET /blogs/posts/list response:
      - description   (str)             -> meta description
      - imageAltText  (str)             -> cover image alt text
      - categories    (list[str])       -> category ID(s) — NOT the full {_id,label,urlSlug}
                                            objects the GET response shows; sending objects
                                            here returns 200 but corrupts the post (live page
                                            then 404s: "Unsupported conversion from object to
                                            objectId in $convert with no onError value")
      - author        (str)             -> author ID — NOT the full object either
    Category/author records themselves are created once via the REIReply blog editor UI
    (GHL_CATEGORY_ID / GHL_AUTHOR_ID above), not through this API.
    """
    ghl_key = os.environ["GHL_API_KEY"]
    r = requests.put(
        f"https://services.leadconnectorhq.com/blogs/posts/{post_id}",
        headers={"Authorization": f"Bearer {ghl_key}", "Content-Type": "application/json",
                 "Version": "2021-07-28"},
        json={
            "locationId": "fgK4QNPrkW9TsnxdOLjN", "blogId": "fp2IcYMIduN23MjmXgRE",
            "status": "PUBLISHED",
            "description": description[:250],
            "imageAltText": image_alt,
            "categories": [GHL_CATEGORY_ID],
            "author": GHL_AUTHOR_ID,
        },
        timeout=15,
    )
    status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}: {r.text[:150]}"
    print(f"SEO metadata - {status}")


def discover_gbp_ids(token):
    r = requests.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    if r.status_code != 200:
        print(f"WARN GBP accounts: {r.status_code} {r.text[:150]}"); return None, None
    accounts = r.json().get("accounts", [])
    if not accounts:
        print("WARN GBP: no accounts found"); return None, None
    account_name = accounts[0]["name"]  # e.g. "accounts/123456789"
    account_num  = account_name.split("/")[-1]
    print(f"GBP account: {account_name}")
    r2 = requests.get(
        f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations",
        params={"readMask": "name"},
        headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    if r2.status_code != 200:
        print(f"WARN GBP locations: {r2.status_code} {r2.text[:150]}"); return account_num, None
    locations = r2.json().get("locations", [])
    if not locations:
        print("WARN GBP: no locations found"); return account_num, None
    location_name = locations[0]["name"]  # e.g. "accounts/123/locations/456"
    location_num  = location_name.split("/")[-1]
    print(f"GBP location: {location_name}")
    return account_num, location_num


def post_to_gbp(title, bhtml, post_url, img_url):
    token = get_gbp_access_token()
    if not token:
        print("GBP skipped - credentials not configured"); return

    account_id  = os.environ.get("GBP_ACCOUNT_ID", "").strip().split("/")[-1]
    location_id = os.environ.get("GBP_LOCATION_ID", "").strip().split("/")[-1]

    if not account_id or not location_id:
        account_id, location_id = discover_gbp_ids(token)
    if not account_id or not location_id:
        print("GBP skipped - could not determine account/location"); return

    summary = re.sub(r"<[^>]+>", " ", bhtml)
    summary = re.sub(r"\s+", " ", summary).strip()[:1490]

    payload = {
        "topicType": "STANDARD",
        "summary": summary,
        "callToAction": {"actionType": "LEARN_MORE", "url": post_url},
        "media": [{"mediaFormat": "PHOTO", "sourceUrl": img_url}],
    }
    url = (f"https://mybusiness.googleapis.com/v4/accounts/{account_id}"
           f"/locations/{location_id}/localPosts")
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=15)
    status = "OK" if r.status_code in (200, 201) else f"FAIL {r.status_code}: {r.text[:150]}"
    print(f"GBP post - {status}")


def publish_one(idx, known_slugs):
    """Generate and publish one blog post. Returns new slug on success, None on failure."""
    topic    = TOPICS[idx]
    img      = IMG[idx % len(IMG)]
    base_url = "https://ygvcashbuyers.com"
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"\nTopic [{idx}]: {topic}")
    print("Calling Claude API...")
    raw = generate_blog_post(topic, known_slugs)

    title_m = re.search(r"^TITLE:\s*(.+)$", raw, re.M)
    slug_m  = re.search(r"^SLUG:\s*(.+)$",  raw, re.M)
    if not title_m or not slug_m:
        print("ERROR: bad format from Claude"); print(raw[:500]); return None

    title    = title_m.group(1).strip()
    slug     = re.sub(r"[^a-z0-9-]", "", slug_m.group(1).strip().lower().replace(" ", "-"))
    if slug in known_slugs:
        # Second+ pass through TOPICS regenerates the same slug. GHL silently renames the new
        # post (e.g. -4787) while the JSON-LD canonical, GBP link, Indexing API and sitemap
        # all kept pointing at the OLD post. Suffix it ourselves, before post_url is built.
        slug = f"{slug}-{random.randint(1000, 9999)}"
    meta_m   = re.search(r"^META:\s*(.+)$", raw, re.M)
    alt_m    = re.search(r"^IMAGE_ALT:\s*(.+)$", raw, re.M)
    meta_description = meta_m.group(1).strip() if meta_m else f"{title} — YGV Cash Buyers, Cincinnati."
    image_alt = alt_m.group(1).strip() if alt_m else title
    bm       = re.search(r"---BODY---\n([\s\S]+?)(?=---FAQ---|\Z)", raw)
    body     = bm.group(1).strip() if bm else ""
    post_url = f"{base_url}/post/{slug}"

    faqs = []
    fm = re.search(r"---FAQ---\n([\s\S]+)", raw)
    if fm:
        cq = None
        for ln in fm.group(1).strip().split("\n"):
            ln = ln.strip()
            if ln.startswith("Q: "):          cq = ln[3:]
            elif ln.startswith("A: ") and cq: faqs.append({"q": cq, "a": ln[3:]}); cq = None

    bhtml = to_html(body)
    wc    = len(re.sub(r"<[^>]+>", " ", bhtml).split())

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
        ],
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", "p:first-of-type", ".faq-section dt"]
        }
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

    # Publish to GHL
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
    if r.status_code not in (200, 201):
        print(f"GHL FAIL - {r.status_code}: {r.text[:300]}"); return None

    post_id = r.json().get("blogPost", {}).get("_id", "")
    actual_slug = r.json().get("blogPost", {}).get("urlSlug", "")
    if actual_slug and actual_slug != slug:
        print(f"WARN GHL renamed slug {slug} -> {actual_slug}; using GHL's")
        slug, post_url = actual_slug, f"{base_url}/post/{actual_slug}"
    print(f"GHL OK - {post_id}\n{post_url}")

    # Set meta description / alt text / category / author (rejected on create, accepted on update)
    if post_id:
        update_post_seo_metadata(post_id, meta_description, image_alt)

    # Post to GBP (optional — skipped if secrets not configured)
    post_to_gbp(title, bhtml, post_url, img)

    # Post to Facebook (optional — skipped if secrets not configured)
    post_to_facebook(title, bhtml, post_url)

    return slug


def submit_to_indexing_api(sa_key_json_str, slugs):
    """Submit URLs to Google Indexing API using service account JWT auth."""
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
    except ImportError:
        import subprocess; subprocess.run(["pip","install","cryptography","-q"],check=True)
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

    if not sa_key_json_str:
        print("Indexing API skipped - INDEXING_SA_KEY_JSON not set"); return

    try:
        sa = json.loads(sa_key_json_str)
    except Exception as e:
        print(f"WARN Indexing: bad SA key JSON: {e}"); return

    now = int(time.time())
    header  = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": sa["client_email"],
        "scope": "https://www.googleapis.com/auth/indexing",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600, "iat": now,
    }

    def b64url(d):
        return base64.urlsafe_b64encode(
            json.dumps(d, separators=(',', ':')).encode()
        ).rstrip(b'=').decode()

    hdr_b64  = b64url(header)
    pay_b64  = b64url(payload)
    sign_in  = f"{hdr_b64}.{pay_b64}".encode()
    priv_key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig      = priv_key.sign(sign_in, asym_padding.PKCS1v15(), hashes.SHA256())
    sig_b64  = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()
    jwt_tok  = f"{hdr_b64}.{pay_b64}.{sig_b64}"

    tr = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt_tok,
    }, timeout=10)
    if tr.status_code != 200:
        print(f"WARN Indexing token: {tr.status_code} {tr.text[:150]}"); return
    access_token = tr.json()["access_token"]

    ok = fail = 0
    for slug in slugs:
        url = f"https://ygvcashbuyers.com/post/{slug}"
        r = requests.post(
            "https://indexing.googleapis.com/v3/urlNotifications:publish",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={"url": url, "type": "URL_UPDATED"},
            timeout=10,
        )
        if r.status_code == 200:
            ok += 1
        else:
            fail += 1
            print(f"  WARN Indexing FAIL {slug} - {r.status_code}: {r.text[:100]}")
        time.sleep(0.2)
    print(f"Indexing API - {ok} submitted, {fail} failed")


def update_sitemap(gh_token, new_slugs, today):
    """Best-effort backup mirror of the sitemap on GitHub Pages.

    Not authoritative for anything anymore (see get_published_slugs) — the real sitemap
    lives on ygvcashbuyers.com/sitemap.xml via GHL's own XML Sitemap feature. Retries once
    on a sha conflict so a transient race doesn't silently drop this run's posts from the
    mirror the way it used to.
    """
    base_url = "https://ygvcashbuyers.com"
    gh_url   = "https://api.github.com/repos/ygvholdings-cmd/ygv-sitemap/contents/sitemap.xml"
    gh_h     = {"Authorization": f"token {gh_token}", "User-Agent": "ygv-blog-publisher"}

    for attempt in range(2):
        try:
            g = requests.get(gh_url, headers=gh_h, timeout=15)
            if g.status_code != 200:
                print(f"WARN GitHub sitemap fetch: {g.status_code}"); return
            d    = g.json()
            old  = base64.b64decode(d["content"]).decode()
            urls = list(dict.fromkeys(
                [f"{base_url}/", f"{base_url}/blog", f"{base_url}/contact"] +
                re.findall(r"<loc>(.*?)</loc>", old) +
                [f"{base_url}/post/{s}" for s in new_slugs]
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
                json={"message": "Add posts: " + ", ".join(f"/post/{s}" for s in new_slugs),
                      "content": base64.b64encode(xml.encode()).decode(),
                      "sha": d["sha"]}
            )
            print(f"GitHub sitemap - {p.status_code}")
            if p.status_code in (200, 201) or attempt == 1:
                return
            print(f"WARN GitHub sitemap PUT: {p.status_code} {p.text[:150]} - retrying with fresh sha")
        except Exception as e:
            print(f"WARN GitHub sitemap: {e}")
            if attempt == 1:
                return


def main():
    # Scheduled runs fire Mon + Tue + Wed (see blog-publisher.yml); Tue/Wed exist only to
    # recover a Monday run GitHub failed to start (seen 2026-10-05: "job was not acquired by
    # Runner"). Skip if this week already has posts. Manual dispatch always publishes.
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and published_within_days(5):
        print("Already published within the last 5 days - nothing to do this run.")
        return

    posts = fetch_all_ghl_posts()
    if posts is None:
        # Without the list we can't know which topics are used; guessing would repeat topics.
        print("ERROR: could not read existing posts from GHL - aborting rather than guess"); sys.exit(1)
    slugs = [p["urlSlug"] for p in posts if p.get("urlSlug")]
    cutover = datetime.fromisoformat(SERIES2_CUTOVER).timestamp()
    def _after_cutover(p):
        try:
            return datetime.fromisoformat(p["publishedAt"].replace("Z", "+00:00")).timestamp() >= cutover
        except (KeyError, ValueError, AttributeError):
            return False
    base_idx = SERIES2_START_IDX + sum(1 for p in posts if _after_cutover(p))
    print(f"Existing posts: {len(slugs)} | next topic index {base_idx} of {len(TOPICS)}")

    new_slugs = []
    for run_num in range(2):
        idx = base_idx + len(new_slugs)
        if idx >= len(TOPICS):
            # Never fall back to re-using topics - that produced ~36 near-duplicate posts that
            # compete with each other in search. Fail loudly so GitHub emails the owner; fix by
            # appending new topics to TOPICS.
            print(f"TOPICS EXHAUSTED at index {idx} - add more topics to TOPICS in publish.py")
            break
        if run_num > 0:
            time.sleep(3)
        new_slug = publish_one(idx, slugs + new_slugs)
        if new_slug:
            new_slugs.append(new_slug)

    if not new_slugs:
        print("ERROR: No posts published"); sys.exit(1)

    # Single sitemap update covering both new posts
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    update_sitemap(gh_token, new_slugs, today)

    # Submit new posts to Google Indexing API
    sa_key_json = os.environ.get("INDEXING_SA_KEY_JSON", "")
    if sa_key_json:
        submit_to_indexing_api(sa_key_json, new_slugs)
    else:
        print("Indexing API skipped - INDEXING_SA_KEY_JSON not set")

    # Ping Google once
    try:
        pg = requests.get(
            "https://www.google.com/ping?sitemap=https%3A%2F%2Fygvcashbuyers.com%2Fsitemap.xml",
            timeout=10)
        print(f"Google ping - {pg.status_code}")
    except Exception:
        pass

    print(f"\nDONE - {len(new_slugs)} post(s) published")
    for s in new_slugs:
        print(f"  https://ygvcashbuyers.com/post/{s}")


if __name__ == "__main__":
    main()
