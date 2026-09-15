#!/usr/bin/env python3
import json,urllib.request
from pathlib import Path
root=Path(__file__).parents[1]; status=json.loads((root/'data/status.json').read_text()); calls=json.loads((root/'data/calls.json').read_text()); alerts=[]
if not status.get('ok') or len(calls)<10:alerts.append({'severity':'critical','code':'coverage','detail':status})
for x in calls:
 if not x.get('deadlines') or not x.get('url','').startswith('https://ec.europa.eu/'):alerts.append({'severity':'critical','code':'invalid_official_record','id':x.get('id')})
(root/'data/alerts.json').write_text(json.dumps({'active':alerts,'checked_at':status.get('fetched_at'),'count':len(alerts)},indent=2))
if alerts:raise SystemExit('active data alert')
