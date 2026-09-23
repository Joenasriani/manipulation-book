from pathlib import Path
import subprocess, hashlib, json, tempfile, shutil, sys
root=Path(__file__).resolve().parents[1]
def run(path,*args):return subprocess.run([sys.executable,str(path/'scripts/publish.py'),*args],capture_output=True,text=True)
def need(ok,msg):
 if not ok:raise AssertionError(msg)
manifest=json.loads((root/'publication.json').read_text()) if (root/'publication.json').exists() else {}
release_path=root/'dist'/manifest.get('public_metadata',{}).get('release','/release.json').lstrip('/')
before=release_path.read_bytes();r=run(root,'build');need(r.returncode==0,r.stderr);need(before==release_path.read_bytes(),'Build is not deterministic')
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)/'candidate';shutil.copytree(root,d,ignore=shutil.ignore_patterns('.git','node_modules'))
 if (d/'publication.json').exists():
  p=d/'publication.json';m=json.loads(p.read_text());m['checkout']['product_id']='WRONG';p.write_text(json.dumps(m));need(run(d,'build').returncode!=0,'Cross-product checkout was accepted')
  shutil.copy2(root/'publication.json',p)
  m=json.loads(p.read_text());m['checkout']['amount']='0.01';p.write_text(json.dumps(m));need(run(d,'build').returncode!=0,'Conflicting checkout price was accepted')
  shutil.copy2(root/'publication.json',p)
  m=json.loads(p.read_text())
  if m['assets']:
   (d/m['assets'][0]['path']).write_bytes(b'CORRUPTED');need(run(d,'build').returncode!=0,'Corrupt public asset was accepted')
 else:
  lock=json.loads((d/'catalogue/sources.lock.json').read_text());p=d/lock['entries'][0]['snapshot'];p.write_text(p.read_text()+' ')
  need(run(d,'build').returncode!=0,'Changed imported manifest was accepted')
need(run(root,'release-gate').returncode!=0,'Unverified candidate passed cutover gate')
if (root/'publication.json').exists():
 script="""import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import handler from './CHECKOUT_FILE';
const m=JSON.parse(readFileSync('publication.json','utf8'));let out={};
const res={setHeader(k,v){out[k]=v},status(n){out.status=n;return this},end(){},redirect(n,u){out.status=n;out.url=u}};
handler({method:'GET',query:{amount:'0.01',item_number:'WRONG'}},res);
const u=new URL(out.url);assert.equal(out.status,302);assert.equal(u.origin,'https://www.paypal.com');
if (m.checkout.hosted_url) {assert.equal(out.url,m.checkout.hosted_url)} else {
assert.equal(u.searchParams.get('amount'),m.checkout.amount);assert.equal(u.searchParams.get('item_number'),m.checkout.product_id);
assert.equal(u.searchParams.get('business'),m.checkout.merchant);assert.equal(u.searchParams.get('currency_code'),m.checkout.currency);
assert.equal(u.searchParams.get('return'),new URL(m.canonical_url).origin+m.checkout.return_path);
assert.equal(u.searchParams.get('cancel_return'),new URL(m.canonical_url).origin+m.checkout.cancel_path);
}
out={};handler({method:'POST'},res);assert.equal(out.status,405);assert.equal(out.Allow,'GET, HEAD');
"""
 endpoint=json.loads((root/'publication.json').read_text())['checkout']['endpoint'].lstrip('/')+'.js'
 script=script.replace('CHECKOUT_FILE',endpoint)
 r=subprocess.run(['node','--input-type=module','-e',script],cwd=root,capture_output=True,text=True);need(r.returncode==0,r.stderr)
print('PASS: reproducible build, rejected identity/price or snapshot tampering, rejected unverified cutover, fixed checkout mapping')

# Discovery checks run against the actual build, not the source templates.
import re, xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from html.parser import HTMLParser
class Head(HTMLParser):
 def __init__(self):super().__init__();self.canonicals=[];self.robots=[];self.descriptions=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='link' and a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
  if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content',''))
  if tag=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content',''))
m=manifest
if m:
 origin='https://'+urlsplit(m['canonical_url']).netloc
 routes=m['routes']
else:
 origin=json.loads((root/'store.json').read_text())['canonical_url'].rstrip('/')
 routes=[{'path':'/','file':'index.html','indexable':True}]
for route in routes:
 text=(root/'dist'/route['file']).read_text();head=Head();head.feed(text)
 need(head.canonicals==[origin+route['path']],'Missing or conflicting canonical: '+route['path'])
 if route['indexable']:
  need(not any('noindex' in x for x in head.robots),'Public page blocked: '+route['path'])
  need(len(head.descriptions)==1 and head.descriptions[0].strip(),'Missing description: '+route['path'])
 else:need(any('noindex' in x for x in head.robots),'Delivery page is indexable')
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
  data=json.loads(raw)
  def check(node):
   if isinstance(node,list):
    for child in node:check(child)
   elif isinstance(node,dict):
    types=node.get('@type',[])
    if 'Product' in types:
     need(node['offers']['url']==node['url'],'Offer points away from canonical product page')
     need(node['author']['@id']=='https://joe-nasr-signals.vercel.app/#joe-nasr','Disconnected author identity')
     if 'Book' in types:need(bool(node.get('bookEdition')),'Edition lost during build')
    for child in node.values():check(child)
  check(data)
sitemap=root/'dist'/m.get('public_metadata',{}).get('sitemap','/sitemap.xml').lstrip('/')
urls={n.text for n in ET.parse(sitemap).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
need(urls=={origin+r['path'] for r in routes if r['indexable']},'Sitemap differs from indexable routes')
config=json.loads((root/'vercel.json').read_text())
for rule in config['headers']:
 if rule['source']=='/(.*)' and not rule.get('has'):
  need(not any(h['key'].lower()=='x-robots-tag' and 'noindex' in h['value'] for h in rule['headers']),'Global noindex blocks production')
print('PASS: canonical URLs, public indexing, edition/author metadata and sitemap boundaries')

script="""import assert from 'node:assert/strict';import {checkoutUrl} from './lib/paypal.js';
for (const hosted_url of [undefined, '', 'https://example.com/ncp/payment/WRONGPRODUCT', 'https://www.paypal.com/ncp/payment/TESTBUTTON123?amount=0.01']) {
 assert.throws(()=>checkoutUrl({checkout:{hosted_url}}));
}
"""
r=subprocess.run(['node','--input-type=module','-e',script],cwd=root,capture_output=True,text=True);need(r.returncode==0,r.stderr)
print('PASS: missing, foreign and modified hosted checkout links fail closed')
