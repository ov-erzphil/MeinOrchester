#!/usr/bin/env python3
"""Read alerts only from the existing public, Google-authenticated calendar."""
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SOURCE='https://calendar.google.com/calendar/ical/ov.erzphil%40gmail.com/public/basic.ics'
TARGET=Path('Mein-Orchester-App-v1.0/eilmeldung.json')
PREFIX='[EILMELDUNG]'

def unescape(value):
    return re.sub(r'\\([nN,;\\])',lambda m:'\n' if m[1].lower()=='n' else m[1],value)

def timestamp(value,params):
    if len(value)==8:
        return datetime.strptime(value,'%Y%m%d').replace(tzinfo=ZoneInfo('Europe/Berlin'))
    parsed=datetime.strptime(value.rstrip('Z'),'%Y%m%dT%H%M%S')
    tz=timezone.utc if value.endswith('Z') else ZoneInfo(params.get('TZID','Europe/Berlin'))
    return parsed.replace(tzinfo=tz)

def alerts_from_ics(data,now):
    text=data.decode('utf-8-sig')
    if not text.lstrip().startswith('BEGIN:VCALENDAR') or 'END:VCALENDAR' not in text:
        raise ValueError('Incomplete calendar; keep previous alert')
    text=re.sub(r'\r?\n[ \t]','',text)
    alerts=[]
    for block in re.findall(r'BEGIN:VEVENT\r?\n(.*?)\r?\nEND:VEVENT',text,re.S):
        props={}
        for line in block.splitlines():
            if ':' not in line: continue
            key,value=line.split(':',1);parts=key.split(';')
            props[parts[0]]=(value,dict(x.split('=',1) for x in parts[1:] if '=' in x))
        title=unescape(props.get('SUMMARY',('',{}))[0])
        if not title.startswith(PREFIX) or props.get('STATUS',('',{}))[0]=='CANCELLED':continue
        # Recurring calendar events are never used as broadcasts.
        if 'RRULE' in props:continue
        try:
            start=timestamp(*props['DTSTART'])
            end=timestamp(*props['DTEND']) if 'DTEND' in props else start+timedelta(hours=24)
            changed=timestamp(*props.get('LAST-MODIFIED',props.get('DTSTAMP',props['DTSTART'])))
        except (KeyError,ValueError):continue
        if not start<=now<end:continue
        title=title[len(PREFIX):].strip()
        if not title:continue
        message=unescape(props.get('DESCRIPTION',('',{}))[0])
        if len(title)>180 or len(message)>5000:continue
        uid=props.get('UID',('',{}))[0]
        identity=hashlib.sha256((uid+'|'+title+'|'+message+'|'+changed.isoformat()).encode()).hexdigest()[:24]
        alerts.append({'active':True,'id':identity,'title':title,'message':message,'publishedAt':changed.isoformat(),'expiresAt':end.isoformat()})
    return sorted(alerts,key=lambda a:a['publishedAt'],reverse=True)

def main():
    request=urllib.request.Request(SOURCE,headers={'User-Agent':'MeinOrchester-Eilmeldungen/1.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=45) as response:data=response.read()
    alerts=alerts_from_ics(data,datetime.now(timezone.utc))
    result=alerts[0] if alerts else {'active':False,'id':'','title':'','message':''}
    previous=json.loads(TARGET.read_text()) if TARGET.exists() else None
    if previous!=result: TARGET.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(alerts)} active calendar alerts; publication state synchronized')

if __name__=='__main__':main()
