#!/usr/bin/env python3

import json,urllib.request,urllib.parse,hashlib

from datetime import datetime,timezone

from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data'; OUT.mkdir(exist_ok=True)

API='https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA&text=open&pageSize=100&pageNumber={}'

def fetch(page):
  
 boundary='----GrantMatchBoundary'; parts=[]
  
 for name,obj in [('query',{'bool':{'must':[],'filter':[]}}),('sort',{'order':'DESC','field':'startDate'}),('languages',['en'])]:
   
  parts += [f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\nContent-Type: application/json\r\n\r\n{json.dumps(obj)}\r\n']
   
 body=(''.join(parts)+f'--{boundary}--\r\n').encode(); req=urllib.request.Request(API.format(page),body,{'Content-Type':f'multipart/form-data; boundary={boundary}','User-Agent':'GrantMatchEurope/1.0'})
  
 return json.load(urllib.request.urlopen(req,timeout=90))
  
now=datetime.now(timezone.utc); calls={}

for page in range(1,9):
  
 for r in fetch(page).get('results',[]):
   
  m=r.get('metadata',{}); one=lambda k,d='': (m.get(k) or [d])[0]
   
  ds=m.get('deadlineDate') or []
   
  if one('type')!='1' or one('status')!='31094502' or not ds: continue
    
  if max(ds)[:10] < now.date().isoformat(): continue
    
  ident=one('identifier');
   
  if not ident: continue
    
  calls[ident]={'id':ident,'name':one('title'),'geo':'EU / associated countries','who':'Call-specific applicants','theme':one('programmeDivision') or one('callTitle') or 'EU funding','amount':'See official topic','timing':'Deadline '+ ' / '.join(x[:10] for x in ds),'deadlines':[x[:10] for x in ds],'eligibility':'Official topic conditions apply','url':one('url'),'source':'EU Funding & Tenders Portal (SEDIA)','sourceUpdated':one('esDA_IngestDate') or one('esDA_FirstIngestDate'),'status':'Open'}
   
rows=sorted(calls.values(),key=lambda x:x['deadlines'][0]); old=[]

try: old=json.loads((OUT/'calls.json').read_text())
  
except: pass
  
oldmap={x['id']:x for x in old}; changes=[]

for x in rows:
  
 if x['id'] not in oldmap: changes.append({'type':'added','id':x['id'],'at':now.isoformat()})
   
 elif x!=oldmap[x['id']]: changes.append({'type':'changed','id':x['id'],'at':now.isoformat()})
   
for k in oldmap.keys()-calls.keys(): changes.append({'type':'removed_or_closed','id':k,'at':now.isoformat()})
  
(OUT/'calls.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))

(OUT/'status.json').write_text(json.dumps({'source':'European Commission SEDIA Search API','source_url':'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search','fetched_at':now.isoformat(),'open_calls':len(rows),'ok':len(rows)>=10,'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()},indent=2))

if changes:
  
 with (OUT/'changes.ndjson').open('a') as f:
   
  for c in changes:f.write(json.dumps(c)+'\n')
    
if len(rows)<10: raise SystemExit('coverage failure: fewer than 10 open official calls')
  
# Switch the static page to the current official snapshot while keeping a fetch for later refreshes.

p=ROOT/'index.html'; s=p.read_text(); import re as _re

m=_re.search(r'const P=(\[.*?\]);',s,_re.S)

if m:
  
 s=s[:m.start()]+"let P="+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+";"+s[m.end():]
  
s=s.replace('let P=', 'let P=',1)

if "fetch('data/calls.json')" not in s:
  
 s=s.replace('render();</script>',"render();fetch('data/calls.json').then(r=>r.json()).then(x=>{if(x.length>=10){P=x;render()}}).catch(()=>{});</script>",1)
  
s=s.replace('No scraped deadlines are displayed because stale deadlines are dangerous.','Open status and deadlines come from the official European Commission SEDIA index, refreshed every 6 hours; deadlines are never inferred.')

p.write_text(s)




























