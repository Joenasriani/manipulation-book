from pathlib import Path
import json, re, shutil, subprocess, sys, tempfile

root = Path(__file__).resolve().parents[1]

def run(path, *args):
    return subprocess.run([sys.executable, str(path / "scripts/publish.py"), *args], capture_output=True, text=True)

def need(ok, msg):
    if not ok:
        raise AssertionError(msg)

def public_boundary_scan():
    blocked_names = {
        "VERCEL_HANDOFF.md",
        "BOOKSTORE_PRE_MIGRATION_ROLLBACK.md",
        "MIGRATION_STATUS.json",
        "PUBLISHING_WORKFLOW.md",
        "PUBLISHING_RELEASE_MANIFEST.md",
        "MANIPULATION_RELEASE_MANIFEST.md",
        "TO_THE_AI_BUILDER.txt",
        "THE_LAST_PAGE_IS_NOT_IN_THE_BOOK.txt",
    }
    forbidden = [
        (re.compile(r"@gmail\\.com", re.I), "personal Gmail address"),
        (re.compile(r"paypal\\.com/cgi-bin/webscr", re.I), "legacy PayPal merchant URL"),
        (re.compile(r"(?:^|[?&])business=", re.I), "PayPal merchant parameter"),
        (re.compile(r"\\bprj_[A-Za-z0-9]+"), "Vercel project ID"),
        (re.compile(r"\\bteam_[A-Za-z0-9]+"), "Vercel team ID"),
        (re.compile(r"\\bVERCEL_TOKEN\\b"), "Vercel token reference"),
        (re.compile("Joenasriani/" + "test" + "-things", re.I), "legacy combined repository"),
        (re.compile("You are " + "Chat" + "GPT", re.I), "system-prompt text"),
        (re.compile(r"<<User knowledge memory:", re.I), "memory transcript marker"),
        (re.compile(r"Model set context updated\\.", re.I), "memory update marker"),
        (re.compile(r"(?mi)^\\s*(?:#{1,3}\\s*)?(?:User|Assistant)\\s*:\\s+"), "chat transcript marker"),
    ]
    skip_dirs = {".git", "dist", "node_modules", "__pycache__"}
    text_suffixes = {".md", ".txt", ".json", ".html", ".css", ".js", ".mjs", ".py", ".yml", ".yaml", ".xml"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in skip_dirs for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.name in blocked_names:
            raise AssertionError(f"Internal operations file is public: {path.relative_to(root)}")
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(errors="ignore")
        for pattern, label in forbidden:
            if pattern.search(text):
                raise AssertionError(f"Public-boundary violation ({label}) in {path.relative_to(root)}")

public_boundary_scan()

r = run(root, "build")
need(r.returncode == 0, r.stderr)
first = (root / "dist/release.json").read_bytes()
r = run(root, "build")
need(r.returncode == 0, r.stderr)
need(first == (root / "dist/release.json").read_bytes(), "Build is not deterministic")

with tempfile.TemporaryDirectory() as tmp:
    candidate = Path(tmp) / "candidate"
    shutil.copytree(root, candidate, ignore=shutil.ignore_patterns(".git", "node_modules", "dist", "__pycache__"))
    if (candidate / "publication.json").exists():
        p = candidate / "publication.json"
        original = p.read_text()
        m = json.loads(original)
        m["checkout"]["product_id"] = "WRONG"
        p.write_text(json.dumps(m))
        need(run(candidate, "build").returncode != 0, "Cross-product checkout was accepted")
        p.write_text(original)
        m = json.loads(original)
        m["checkout"]["amount"] = "0.01"
        p.write_text(json.dumps(m))
        need(run(candidate, "build").returncode != 0, "Conflicting checkout price was accepted")
        p.write_text(original)
        m = json.loads(original)
        if m.get("assets"):
            asset = candidate / m["assets"][0]["path"]
            asset.write_bytes(b"CORRUPTED")
            need(run(candidate, "build").returncode != 0, "Corrupt public asset was accepted")
    else:
        lock = json.loads((candidate / "catalogue/sources.lock.json").read_text())
        p = candidate / lock["entries"][0]["snapshot"]
        m = json.loads(p.read_text())
        m["id"] = "wrong-publication"
        p.write_text(json.dumps(m))
        need(run(candidate, "build").returncode != 0, "Catalogue identity tampering was accepted")

if (root / "publication.json").exists():
    m = json.loads((root / "publication.json").read_text())
    endpoint = m["checkout"]["endpoint"].lstrip("/") + ".js"
    script = """import assert from 'node:assert/strict';
import handler from './CHECKOUT_FILE';
let out={};
const res={setHeader(k,v){out[k]=v},status(n){out.status=n;return this},end(){},redirect(n,u){out.status=n;out.url=u}};
handler({method:'GET'},res);
assert.equal(out.status,302);
assert.equal(out.url.replace(/\\/$/,''),'HOSTED_URL'.replace(/\\/$/,''));
out={};
handler({method:'POST'},res);
assert.equal(out.status,405);
assert.equal(out.Allow,'GET, HEAD');
"""
    script = script.replace("CHECKOUT_FILE", endpoint).replace("HOSTED_URL", m["checkout"]["hosted_url"])
    r = subprocess.run(["node", "--input-type=module", "-e", script], cwd=root, capture_output=True, text=True)
    need(r.returncode == 0, r.stderr)

print("PASS: public boundary, deterministic build, identity/price integrity, hosted checkout")
