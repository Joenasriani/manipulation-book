from pathlib import Path
import subprocess, hashlib, json, tempfile, shutil, sys
root=Path(__file__).resolve().parents[1]
def run(path,*args):return subprocess.run([sys.executable,str(path/'scripts/publish.py'),*args],capture_output=True,text=True)
def need(ok,msg):
 if not ok:raise AssertionError(msg)
before=(root/'dist/release.json').read_bytes();r=run(root,'build');need(r.returncode==0,r.stderr);need(before==(root/'dist/release.json').read_bytes(),'Build is not deterministic')
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
assert.equal(u.searchParams.get('amount'),m.checkout.amount);assert.equal(u.searchParams.get('item_number'),m.checkout.product_id);
assert.equal(u.searchParams.get('business'),m.checkout.merchant);assert.equal(u.searchParams.get('currency_code'),m.checkout.currency);
assert.equal(u.searchParams.get('return'),new URL(m.canonical_url).origin+m.checkout.return_path);
assert.equal(u.searchParams.get('cancel_return'),new URL(m.canonical_url).origin+m.checkout.cancel_path);
out={};handler({method:'POST'},res);assert.equal(out.status,405);assert.equal(out.Allow,'GET, HEAD');
"""
 endpoint=json.loads((root/'publication.json').read_text())['checkout']['endpoint'].lstrip('/')+'.js'
 script=script.replace('CHECKOUT_FILE',endpoint)
 r=subprocess.run(['node','--input-type=module','-e',script],cwd=root,capture_output=True,text=True);need(r.returncode==0,r.stderr)
print('PASS: reproducible build, rejected identity/price or snapshot tampering, rejected unverified cutover, fixed checkout mapping')
