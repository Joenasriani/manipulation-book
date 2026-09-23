#!/usr/bin/env python3
"""Publication build, source validation and independent HTTP verification. Python standard library only."""
from pathlib import Path
from urllib.parse import urlsplit, urljoin, parse_qs
import datetime, argparse, concurrent.futures, hashlib, html, json, re, shutil, sys, urllib.request, urllib.error, zipfile
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
def digest(data):return hashlib.sha256(data).hexdigest()
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def origin(m):return urlsplit(m['canonical_url']).scheme+'://'+urlsplit(m['canonical_url']).netloc
def full_title(m):return m['title']+(': '+m['subtitle'] if m.get('subtitle') else '')
def validate_manifest(m):
 for key in ['schema_version','id','kind','title','author','canonical_url','repository','deployment','checkout','release','description']:
  require(key in m,'Missing manifest field: '+key)
 require(m['schema_version']=='1.0.0','Unsupported manifest schema')
 require(m['kind'] in ['book','research_framework'],'Unknown publication kind')
 require(m['canonical_url'].startswith('https://'),'Canonical URL must use HTTPS')
 require(re.fullmatch(r'[a-z0-9-]+',m['id']) is not None,'Invalid publication ID')
 c=m['checkout'];require(re.fullmatch(r'\d+\.\d{2}',c['amount']) is not None,'Invalid amount')
 require(c['currency']=='USD','Currency change needs an explicit checkout review')
 require(c['provider']=='paypal' and c['merchant'],'Missing checkout provider or recipient')
 require(c['endpoint'].startswith('/api/'),'Checkout route must be same-origin')
 require(m['release']['product_id']==c['product_id'],'Release and checkout product IDs differ')
 require(m['release']['price']==c['amount'] and m['release']['currency']==c['currency'],'Release and checkout price differ')
 if m['kind']=='book':
  require(m['release']['archive_sha256'] and re.fullmatch('[a-f0-9]{64}',m['release']['archive_sha256']),'Invalid recorded archive SHA256')
  require(m['release']['product_id']==c['product_id'],'Release and checkout product IDs differ')
  require(m['release']['price']==c['amount'] and m['release']['currency']==c['currency'],'Release and checkout price differ')
  paths=[r['path'] for r in m['routes']];require(len(paths)==len(set(paths)),'Duplicate public route')
  require(c['return_path'] in paths,'Missing delivery route')
 return m
def product_schema(m):
 p={'@type':['Book','Product'] if m['kind']=='book' else ['CreativeWork','Product'],'@id':m['canonical_url']+'#publication','name':full_title(m),'url':m['canonical_url'],'description':m['description'],'author':{'@type':'Person','name':m['author'],'url':'https://joe-nasr-signals.vercel.app/'},'inLanguage':'en','offers':{'@type':'Offer','price':m['checkout']['amount'],'priceCurrency':m['checkout']['currency'],'url':origin(m)+m['checkout']['endpoint']}}
 if m['kind']=='book':p.update({'numberOfPages':m['release']['book_pages'],'bookFormat':'https://schema.org/EBook'})
 if m.get('catalogue',{}).get('cover'):p['image']=m['catalogue']['cover']
 return p
def replace_schema(text, transform):
 def f(match):
  obj=json.loads(match[1]);obj=transform(obj)
  return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace('</','<\\/')+'</script>'
 return re.sub(r'<script\s+type="application/ld\+json">(.*?)</script>',f,text,flags=re.S)
def build_book(m,d):
 for r in m['routes']:
  src=ROOT/r['file'];require(src.is_file(),'Missing public source '+r['file'])
  txt=src.read_text(); canonical=origin(m)+r['path']
  txt=re.sub(r'(<link\s+rel="canonical"\s+href=")[^"]*(")',lambda x:x[1]+canonical+x[2],txt)
  txt=re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")',lambda x:x[1]+canonical+x[2],txt)
  def transform(obj):
   graph=obj.get('@graph',[obj]);out=[]
   for node in graph:
    types=node.get('@type',[])
    if 'Book' in types or 'Product' in types:
     new=product_schema(m);new['@id']=node.get('@id',new['@id']);out.append(new)
    else:out.append(node)
   return {**obj,'@graph':out} if '@graph' in obj else out[0]
  txt=replace_schema(txt,transform)
  # Prices in the HTML sources are checked against the manifest, not silently repriced.
  prices=re.findall(r'\$(\d+\.\d{2})',txt)
  require(all(p==m['checkout']['amount'] for p in prices),'Visible price conflicts with manifest: '+r['file'])
  require(not re.search(r'https://raw\.githubusercontent\.com/Joenasriani/test-things/main/assets',txt),'Mutable legacy asset reference in '+r['file'])
  (d/r['file']).write_text(txt)
 for p in ROOT.glob('*.css'):shutil.copy2(p,d/p.name)
 for p in ROOT.glob('google*.html'):shutil.copy2(p,d/p.name)
 if (ROOT/'assets').exists():shutil.copytree(ROOT/'assets',d/'assets')
 for item in m.get('assets',[]):
  p=ROOT/item['path'];require(digest(p.read_bytes())==item['sha256'],'Asset checksum conflict: '+item['path'])
 # Compatibility assets are served by the local serverless redirect, never GitHub main.
 for name in ['robots.txt','llms.txt']:
  if (ROOT/name).exists():shutil.copy2(ROOT/name,d/name)
 sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+html.escape(origin(m)+r['path'])+'</loc></url>\n' for r in m['routes'] if r['indexable'])+'</urlset>\n'
 (d/'sitemap.xml').write_text(sitemap);shutil.copy2(ROOT/'publication.json',d/'publication.json')
 return [m]
def load_catalogue():
 entries=read('catalogue/sources.lock.json')['entries'];ms=[];seen=set();projects=set()
 for e in entries:
  p=ROOT/e['snapshot'];data=p.read_bytes();require(digest(data)==e['sha256'],'Pinned manifest hash mismatch: '+e['id'])
  m=validate_manifest(json.loads(data));require(e['id']==m['id'],'Catalogue identity mismatch')
  require(m['id'] not in seen,'Duplicate catalogue ID');seen.add(m['id'])
  project=m['deployment']['project_id']
  if project:require(project not in projects,'Multiple publications assigned to one project');projects.add(project)
  ms.append((e,m))
 return ms
def build_store(d):
 pairs=load_catalogue();ms=[m for e,m in pairs];articles=[]
 for e,m in pairs:
  a=(ROOT/e['template']).read_text();vals={'canonical_url':m['canonical_url'],'buy_url':origin(m)+m['checkout']['endpoint'],'full_title':full_title(m),'price_label':'$'+m['checkout']['amount'],'scene':m.get('catalogue',{}).get('scene',''),'title':m['title'],'subtitle':m.get('subtitle',''),'id':m['id'],'hook':m['catalogue']['coreIdea'],'store_line':m['catalogue']['storeLine']}
  for k,v in vals.items():a=a.replace('{{'+k+'}}',html.escape(v,quote=True))
  require('{{' not in a,'Unresolved catalogue template variable: '+e['id']);articles.append(a)
 text=(ROOT/'templates/index.html').read_text().replace('{{catalogue}}','\n'.join(articles))
 def update(obj):
  for node in obj.get('@graph',[]):
   if node.get('@type')=='ItemList':
    node['numberOfItems']=len(ms);node['itemListElement']=[{'@type':'ListItem','position':i+1,'item':product_schema(m)} for i,m in enumerate(ms)]
  return obj
 text=replace_schema(text,update);(d/'index.html').write_text(text)
 for pattern in ['*.css','*.js','google*.html','404.html','robots.txt']:
  for p in ROOT.glob(pattern):shutil.copy2(p,d/p.name)
 # Product paths do not become store pages. ICF-AI's old routes remain a cutover blocker until redirects are verified.
 (d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+read('store.json')['canonical_url']+'</loc></url></urlset>\n')
 (d/'llms.txt').write_text('# The Reasoning Library\n\n'+''.join('- ['+full_title(m)+']('+m['canonical_url']+')\n' for m in ms))
 save(d/'data/books.json',[{'id':m['id'],'title':m['title'],'subtitle':m.get('subtitle',''),'author':m['author'],'landingPage':m['canonical_url'],'buyUrl':origin(m)+m['checkout']['endpoint'],'price':{'amount':m['checkout']['amount'],'currency':m['checkout']['currency']},**m.get('catalogue',{})} for m in ms])
 return ms
def build():
 d=ROOT/'dist'
 if d.exists():shutil.rmtree(d)
 d.mkdir()
 if (ROOT/'publication.json').exists():ms=build_book(validate_manifest(read('publication.json')),d)
 else:ms=build_store(d)
 files=[{'path':p.relative_to(d).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(d.rglob('*')) if p.is_file()]
 code=[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p.read_bytes())} for p in sorted((ROOT/'api').rglob('*.js'))] if (ROOT/'api').exists() else []
 save(d/'release.json',{'schema_version':'1.0.0','status':'built_not_deployed','publication_ids':[m['id'] for m in ms],'manifests':{m['id']:digest((ROOT/'publication.json').read_bytes()) if (ROOT/'publication.json').exists() else next(e['sha256'] for e,x in load_catalogue() if x['id']==m['id']) for m in ms},'files':files,'serverless_sources':code,'verification':{'payment':'not_verified','buyer_receipt':'not_verified'}})
 print('PASS: deterministic build, manifest identities, assets and catalogue records')
def local_validate():
 if (ROOT/'publication.json').exists():
  m=validate_manifest(read('publication.json'));require(m['deployment']['project_id'],'Missing dedicated Vercel project')
  require(m['deployment']['root_directory']=='.','Expected repository root deployment')
 else:load_catalogue()
 require((ROOT/'dist/release.json').exists(),'Build before validation')
 for f in read('dist/release.json')['files']:
  require(digest((ROOT/'dist'/f['path']).read_bytes())==f['sha256'],'Built file changed: '+f['path'])
 print('PASS: local release checks')
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def request(url):
 try:
  r=urllib.request.build_opener(NoRedirect).open(url,timeout=20);return r.status,dict(r.headers),r.read()
 except urllib.error.HTTPError as e:return e.code,dict(e.headers),e.read()
def verify(base,report,source_repository,source_commit):
 require(source_repository and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",source_repository),"Specify --source-repository")
 require(source_commit and re.fullmatch("[a-f0-9]{40}",source_commit),"Specify immutable --source-commit")
 require(base and base.startswith('https://'),'Specify HTTPS --base for the actual deployment to verify')
 release=read('dist/release.json');checks=[]
 expected_files=release['files']+[{'path':'release.json','sha256':digest((ROOT/'dist/release.json').read_bytes())}]
 def check_file(f):
  path='/'+f['path'];path='/' if path=='/index.html' else path[:-5] if path.endswith('.html') and not path.startswith('/google') and path!='/404.html' else path
  try:
   status,headers,body=request(base.rstrip('/')+path)
   return {'path':path,'status':status,'expected_sha256':f['sha256'],'actual_sha256':digest(body),'pass':status in ([200,404] if path=='/404.html' else [200]) and digest(body)==f['sha256']}
  except Exception as e:return {'path':path,'pass':False,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:checks=list(pool.map(check_file,expected_files))
 if (ROOT/'publication.json').exists():
  m=read('publication.json');c=m['checkout']
  try:
   status,headers,body=request(base.rstrip('/')+c['endpoint']+'?amount=0.01&item_number=WRONG')
   target=urlsplit(headers.get('Location',headers.get('location','')));q=parse_qs(target.query)
   expected={'cmd':'_xclick','business':c['merchant'],'item_number':c['product_id'],'amount':c['amount'],'currency_code':c['currency'],'return':origin(m)+c['return_path'],'cancel_return':origin(m)+c['cancel_path']}
   checks.append({'path':c['endpoint'],'status':status,'pass':status==302 and target.scheme=='https' and target.netloc=='www.paypal.com' and all(q.get(k)==[v] for k,v in expected.items())})
  except Exception as e:checks.append({'path':c['endpoint'],'pass':False,'error':str(e)})
 data={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_repository':source_repository,'source_commit':source_commit,'publication_manifest_sha256':digest((ROOT/'publication.json').read_bytes()) if (ROOT/'publication.json').exists() else None,'deployment_base':base,'expected_release_sha256':digest((ROOT/'dist/release.json').read_bytes()),'pass':all(x['pass'] for x in checks),'checks':checks,'payment_acceptance':'not_tested','buyer_receipt':'not_tested'}
 save(Path(report),data);require(data['pass'],'Independent deployment checks failed; see '+report)
 print('PASS: deployed bytes and checkout mapping. Payment and receipt remain unverified.')
def private_archive(path):
 m=read('publication.json');p=Path(path);require(digest(p.read_bytes())==m['release']['archive_sha256'],'Buyer ZIP differs from recorded release hash')
 with zipfile.ZipFile(p) as z:
  require(z.testzip() is None,'Buyer ZIP CRC failure');names=[n for n in z.namelist() if not n.endswith('/')]
  require(len(names)==m['release']['file_count'],'Buyer ZIP file count differs')
  require(len(names)==len(set(names)),'Duplicate ZIP member names')
  inventory=m['release'].get('files')
  if inventory:
   require(set(names)=={f['path'] for f in inventory},'Buyer ZIP inventory differs')
   for f in inventory:
    data=z.read(f['path']);require(len(data)==f['bytes'] and digest(data)==f['sha256'],'Buyer file differs: '+f['path'])
  else:
   manifests=[n for n in names if Path(n).name=='RELEASE_MANIFEST.json'];sums=[n for n in names if Path(n).name=='SHA256SUMS.txt']
   require(len(manifests)==1 and len(sums)==1,'Missing or ambiguous buyer manifest/checksum file')
   json.loads(z.read(manifests[0]));prefix=str(Path(sums[0]).parent)
   for line in z.read(sums[0]).decode().splitlines():
    if not line.strip():continue
    expected,name=line.split(maxsplit=1);name=name.lstrip('* ')
    member=name if name in names else str(Path(prefix)/name)
    require(member in names and digest(z.read(member))==expected,'Internal checksum mismatch: '+name)
 print('PASS: private archive identity, CRCs, file count and recorded file checksums')
def gate():
 local_validate();p=ROOT/'verification/preview.json';require(p.exists(),'Missing independent preview evidence')
 evidence=json.loads(p.read_text());require(evidence.get('pass') is True,'Preview verification failed')
 require(evidence.get('expected_release_sha256')==digest((ROOT/'dist/release.json').read_bytes()),'Preview evidence is stale')
 require(re.fullmatch('[a-f0-9]{40}',evidence.get('source_commit','')),'Evidence lacks immutable source commit')
 require(evidence.get('deployment_base','').startswith('https://'),'Evidence lacks HTTPS deployment URL')
 checked=datetime.datetime.fromisoformat(evidence.get('verified_at',''))
 age=(datetime.datetime.now(datetime.timezone.utc)-checked).total_seconds()
 require(0<=age<=86400,'Preview evidence must be less than 24 hours old')
 checks=evidence.get('checks',[]);require(checks and all(c.get('pass') is True for c in checks),'Missing or failed deployment checks')
 paths=[c['path'] for c in checks];require(len(paths)==len(set(paths)),'Duplicate deployment checks')
 expected=read('dist/release.json')['files']+[{'path':'release.json','sha256':digest((ROOT/'dist/release.json').read_bytes())}]
 for f in expected:
  path='/'+f['path'];path='/' if path=='/index.html' else path[:-5] if path.endswith('.html') and not path.startswith('/google') and path!='/404.html' else path
  matches=[c for c in checks if c['path']==path]
  require(len(matches)==1 and matches[0].get('expected_sha256')==f['sha256'] and matches[0].get('actual_sha256')==f['sha256'],'Missing or mismatched deployed bytes: '+path)
 if (ROOT/'publication.json').exists():
  m=read('publication.json')
  require(evidence.get('publication_manifest_sha256')==digest((ROOT/'publication.json').read_bytes()),'Evidence publication differs')
  require(m['checkout']['endpoint'] in paths,'Missing checkout verification')
 if (ROOT/'store.json').exists():
  require(not read('store.json')['blockers'],'Unresolved store cutover blockers')
  for e,m in load_catalogue():require(e.get('source_commit') and re.fullmatch('[a-f0-9]{40}',e['source_commit']),'Manifest needs immutable source commit')
 else:require(read('publication.json')['deployment']['project_id'],'Missing Vercel mapping')
 print('PASS: technical cutover gate. Commercial payment/receipt evidence is separate.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['build','validate','verify','archive','release-gate']);parser.add_argument('--base');parser.add_argument('--report',default='verification/preview.json');parser.add_argument('--file');parser.add_argument('--source-repository');parser.add_argument('--source-commit');args=parser.parse_args()
 try:
  if args.command=='build':build()
  elif args.command=='validate':local_validate()
  elif args.command=='verify':verify(args.base,args.report,args.source_repository,args.source_commit)
  elif args.command=='archive':private_archive(args.file)
  else:gate()
 except Exception as e:print('BLOCKED:',str(e),file=sys.stderr);sys.exit(1)
