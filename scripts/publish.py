#!/usr/bin/env python3
"""Build and verify public publication pages. Python standard library only."""
from pathlib import Path
from urllib.parse import urlsplit
import argparse, concurrent.futures, hashlib, html, json, re, shutil, sys, urllib.request, urllib.error

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT / path).read_text())

def digest(data):
    return hashlib.sha256(data).hexdigest()

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def origin(m):
    u = urlsplit(m["canonical_url"])
    return f"{u.scheme}://{u.netloc}"

def full_title(m):
    return m["title"] + (": " + m["subtitle"] if m.get("subtitle") else "")

def validate_manifest(m):
    for key in ["schema_version", "id", "kind", "title", "author", "canonical_url", "repository", "deployment", "checkout", "release", "description"]:
        require(key in m, "Missing manifest field: " + key)
    require(m["schema_version"] == "1.0.0", "Unsupported manifest schema")
    require(m["kind"] in ["book", "research_framework"], "Unknown publication kind")
    require(m["canonical_url"].startswith("https://"), "Canonical URL must use HTTPS")
    require(re.fullmatch(r"[a-z0-9-]+", m["id"]) is not None, "Invalid publication ID")
    c = m["checkout"]
    require(c.get("provider") == "paypal", "Unsupported checkout provider")
    require(c.get("mode") == "hosted_button", "Checkout must use hosted button mode")
    require(c.get("hosted_url", "").startswith("https://www.paypal.com/ncp/payment/"), "Missing hosted PayPal URL")
    require(c.get("endpoint", "").startswith("/api/"), "Checkout route must be same-origin")
    require(re.fullmatch(r"\d+\.\d{2}", c.get("amount", "")) is not None, "Invalid amount")
    require(c.get("currency") == "USD", "Currency change needs explicit review")
    require(m["release"]["product_id"] == c["product_id"], "Release and checkout product IDs differ")
    require(m["release"]["price"] == c["amount"] and m["release"]["currency"] == c["currency"], "Release and checkout price differ")
    return m

def product_schema(m):
    p = {
        "@type": ["Book", "Product"] if m["kind"] == "book" else ["CreativeWork", "Product"],
        "@id": m["canonical_url"] + "#publication",
        "name": full_title(m),
        "url": m["canonical_url"],
        "description": m["description"],
        "author": {"@type": "Person", "name": m["author"], "url": "https://joe-nasr-signals.vercel.app/"},
        "inLanguage": "en",
        "offers": {
            "@type": "Offer",
            "price": m["checkout"]["amount"],
            "priceCurrency": m["checkout"]["currency"],
            "url": origin(m) + m["checkout"]["endpoint"],
        },
    }
    if m["kind"] == "book":
        p["numberOfPages"] = m["release"]["book_pages"]
        p["bookFormat"] = "https://schema.org/EBook"
    if m.get("catalogue", {}).get("cover"):
        p["image"] = m["catalogue"]["cover"]
    return p

def replace_schema(text, transform):
    def repl(match):
        obj = transform(json.loads(match.group(1)))
        return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"
    return re.sub(r'<script\s+type="application/ld\+json">(.*?)</script>', repl, text, flags=re.S)

def build_book(m, out):
    for route in m["routes"]:
        src = ROOT / route["file"]
        require(src.is_file(), "Missing public source " + route["file"])
        text = src.read_text()
        canonical = origin(m) + route["path"]
        text = re.sub(r'(<link\s+rel="canonical"\s+href=")[^"]*(")', lambda x: x.group(1) + canonical + x.group(2), text)
        text = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")', lambda x: x.group(1) + canonical + x.group(2), text)
        def transform(obj):
            graph = obj.get("@graph", [obj])
            rebuilt = []
            for node in graph:
                types = node.get("@type", [])
                if "Book" in types or "Product" in types:
                    new = product_schema(m)
                    new["@id"] = node.get("@id", new["@id"])
                    rebuilt.append(new)
                else:
                    rebuilt.append(node)
            return {**obj, "@graph": rebuilt} if "@graph" in obj else rebuilt[0]
        text = replace_schema(text, transform)
        prices = re.findall(r"\$(\d+\.\d{2})", text)
        require(all(p == m["checkout"]["amount"] for p in prices), "Visible price conflicts with manifest: " + route["file"])
        (out / route["file"]).write_text(text)
    for p in ROOT.glob("*.css"):
        shutil.copy2(p, out / p.name)
    for p in ROOT.glob("google*.html"):
        shutil.copy2(p, out / p.name)
    if (ROOT / "assets").exists():
        shutil.copytree(ROOT / "assets", out / "assets")
    for item in m.get("assets", []):
        p = ROOT / item["path"]
        require(digest(p.read_bytes()) == item["sha256"], "Asset checksum conflict: " + item["path"])
    for name in ["robots.txt", "llms.txt"]:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, out / name)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        "<url><loc>" + html.escape(origin(m) + r["path"]) + "</loc></url>\n" for r in m["routes"] if r["indexable"]
    ) + "</urlset>\n"
    (out / "sitemap.xml").write_text(sitemap)
    shutil.copy2(ROOT / "publication.json", out / "publication.json")
    return [m]

def load_catalogue():
    entries = read("catalogue/sources.lock.json")["entries"]
    results, seen = [], set()
    for entry in entries:
        m = validate_manifest(read(entry["snapshot"]))
        require(entry["id"] == m["id"], "Catalogue identity mismatch")
        require(m["id"] not in seen, "Duplicate catalogue ID")
        seen.add(m["id"])
        results.append((entry, m))
    return results

def build_store(out):
    pairs = load_catalogue()
    manifests = [m for _, m in pairs]
    articles = []
    for entry, m in pairs:
        article = (ROOT / entry["template"]).read_text()
        vals = {
            "canonical_url": m["canonical_url"],
            "buy_url": origin(m) + m["checkout"]["endpoint"],
            "full_title": full_title(m),
            "price_label": "$" + m["checkout"]["amount"],
            "scene": m.get("catalogue", {}).get("scene", ""),
            "title": m["title"],
            "subtitle": m.get("subtitle", ""),
            "id": m["id"],
            "hook": m["catalogue"]["coreIdea"],
            "store_line": m["catalogue"]["storeLine"],
        }
        for key, value in vals.items():
            article = article.replace("{{" + key + "}}", html.escape(value, quote=True))
        require("{{" not in article, "Unresolved catalogue template variable: " + entry["id"])
        articles.append(article)
    text = (ROOT / "templates/index.html").read_text().replace("{{catalogue}}", "\n".join(articles))
    def update_schema(obj):
        for node in obj.get("@graph", []):
            if node.get("@type") == "ItemList":
                node["numberOfItems"] = len(manifests)
                node["itemListElement"] = [
                    {"@type": "ListItem", "position": i + 1, "item": product_schema(m)}
                    for i, m in enumerate(manifests)
                ]
        return obj
    (out / "index.html").write_text(replace_schema(text, update_schema))
    for pattern in ["*.css", "*.js", "google*.html", "404.html", "robots.txt"]:
        for p in ROOT.glob(pattern):
            shutil.copy2(p, out / p.name)
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'
        + read("store.json")["canonical_url"] + "</loc></url></urlset>\n"
    )
    (out / "llms.txt").write_text(
        "# The Reasoning Library\n\n" + "".join("- [" + full_title(m) + "](" + m["canonical_url"] + ")\n" for m in manifests)
    )
    save(out / "data/books.json", [
        {
            "id": m["id"],
            "title": m["title"],
            "subtitle": m.get("subtitle", ""),
            "author": m["author"],
            "landingPage": m["canonical_url"],
            "buyUrl": origin(m) + m["checkout"]["endpoint"],
            "price": {"amount": m["checkout"]["amount"], "currency": m["checkout"]["currency"]},
            **m.get("catalogue", {}),
        }
        for m in manifests
    ])
    return manifests

def build():
    out = ROOT / "dist"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    manifests = build_book(validate_manifest(read("publication.json")), out) if (ROOT / "publication.json").exists() else build_store(out)
    files = [
        {"path": p.relative_to(out).as_posix(), "sha256": digest(p.read_bytes()), "bytes": p.stat().st_size}
        for p in sorted(out.rglob("*")) if p.is_file()
    ]
    save(out / "release.json", {"schema_version": "1.0.0", "publication_ids": [m["id"] for m in manifests], "files": files})
    print("PASS: public build")

def local_validate():
    if (ROOT / "publication.json").exists():
        validate_manifest(read("publication.json"))
    else:
        load_catalogue()
    require((ROOT / "dist/release.json").exists(), "Build before validation")
    for f in read("dist/release.json")["files"]:
        require(digest((ROOT / "dist" / f["path"]).read_bytes()) == f["sha256"], "Built file changed: " + f["path"])
    print("PASS: public release checks")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request(url):
    try:
        r = urllib.request.build_opener(NoRedirect).open(url, timeout=20)
        return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()

def verify(base):
    require(base and base.startswith("https://"), "Specify HTTPS --base")
    release = read("dist/release.json")
    expected = release["files"] + [{"path": "release.json", "sha256": digest((ROOT / "dist/release.json").read_bytes())}]
    def check_file(f):
        path = "/" + f["path"]
        if path == "/index.html":
            path = "/"
        elif path.endswith(".html") and not path.startswith("/google") and path != "/404.html":
            path = path[:-5]
        try:
            status, _, body = request(base.rstrip("/") + path)
            return path, status == 200 and digest(body) == f["sha256"]
        except Exception:
            return path, False
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        checks = list(pool.map(check_file, expected))
    require(all(ok for _, ok in checks), "Deployed bytes do not match build")
    if (ROOT / "publication.json").exists():
        m = read("publication.json")
        status, headers, _ = request(base.rstrip("/") + m["checkout"]["endpoint"])
        target = headers.get("Location", headers.get("location", ""))
        require(status == 302 and target.rstrip("/") == m["checkout"]["hosted_url"].rstrip("/"), "Checkout redirect mismatch")
    print("PASS: deployed public files and checkout redirect")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "validate", "verify"])
    parser.add_argument("--base")
    args = parser.parse_args()
    try:
        if args.command == "build":
            build()
        elif args.command == "validate":
            local_validate()
        else:
            verify(args.base)
    except Exception as exc:
        print("BLOCKED:", str(exc), file=sys.stderr)
        sys.exit(1)
