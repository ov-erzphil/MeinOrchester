#!/usr/bin/env python3
"""Publish only a verified theater PDF URL; never copy the internal plan."""
import concurrent.futures
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from pypdf import PdfReader

BASE='https://www.erzgebirgische.theater/user/'
MONTHS={'januar':1,'februar':2,'marz':3,'märz':3,'april':4,'mai':5,'juni':6,'juli':7,'august':8,'september':9,'oktober':10,'november':11,'dezember':12}

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'MeinOrchester-Tagesplan/1.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=25) as response:
        if not response.url.startswith(BASE): raise ValueError('Unexpected redirect')
        return response.read(15_000_001)

def discover():
    urls={BASE+f'aktuell{n}.pdf' for n in range(1,10)}
    # Discover renamed PDFs when the theater exposes links on its staff page.
    for page in (BASE,BASE+'index.html'):
        try:
            html=fetch(page).decode('utf-8',errors='replace')
            for href in re.findall(r'href=[\"\']([^\"\']+\.pdf(?:\?[^\"\']*)?)[\"\']',html,re.I):
                url=urllib.parse.urljoin(page,href)
                if url.startswith(BASE): urls.add(url)
        except (OSError,ValueError): pass
    return sorted(urls)

def inspect(url):
    try:
        data=fetch(url)
        if len(data)>15_000_000 or not data.startswith(b'%PDF-'): return None
        pdf=PdfReader(io.BytesIO(data))
        dates=set()
        for page in pdf.pages[:20]:
            text=page.extract_text() or ''
            for line in text.splitlines():
                if not re.search(r'Tagesplan\s+f[uü]r',line,re.I): continue
                for d,m,y in re.findall(r'(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]+)\s+(20\d{2})',line):
                    if m.lower() in MONTHS: dates.add(date(int(y),MONTHS[m.lower()],int(d)).isoformat())
                for d,m,y in re.findall(r'(\d{1,2})\.(\d{1,2})\.(20\d{2})',line):
                    dates.add(date(int(y),int(m),int(d)).isoformat())
        if not dates: return None
        return {'url':url,'dates':sorted(dates)}
    except Exception as error:
        print(f'Unavailable candidate {url}: {type(error).__name__}')
        return None

def select(candidates,today):
    # Prefer a document containing today; otherwise the nearest upcoming plan,
    # otherwise the most recent available plan. Never use the slot number as date.
    def rank(item):
        days=[date.fromisoformat(d) for d in item['dates']]
        if today in days: return (0,-max(d.toordinal() for d in days),item['url'])
        future=[d for d in days if d>today]
        if future: return (1,min(d.toordinal() for d in future),item['url'])
        return (2,-max(d.toordinal() for d in days),item['url'])
    return min(candidates,key=rank) if candidates else None

def main():
    today=datetime.now(ZoneInfo('Europe/Berlin')).date()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        found=[x for x in pool.map(inspect,discover()) if x]
    chosen=select(found,today)
    output={'available':bool(chosen),'checkedAt':datetime.now(timezone.utc).isoformat()}
    if chosen: output.update(chosen)
    Path('tagesplan-aktuell.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(f'Verified {len(found)} day-plan PDFs; selected {chosen}')

if __name__=='__main__':main()
