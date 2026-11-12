#!/usr/bin/env python3
"""Read-only catalog of a public Google Drive folder tree. Requires DRIVE_API_KEY."""
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.environ.get('NOTEN_ROOT_ID','17hEhLogO2Br1enG6R2vum7xMNezkkI8T')
KEY = os.environ.get('DRIVE_API_KEY')
if not KEY:
    sys.exit('DRIVE_API_KEY missing (Google Cloud Drive API key required).')

from instrument_names import classify, horn_voices

def api(params):
    params = dict(params, key=KEY)
    url = 'https://www.googleapis.com/drive/v3/files?' + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url,timeout=35) as resp:
                return json.load(resp)
        except Exception as e:
            if attempt == 4: raise RuntimeError(f'Drive API failure: {e}')
            time.sleep(2**attempt)

def children(folder):
    token=None
    while True:
        q={'q':f"'{folder}' in parents and trashed = false",'fields':'nextPageToken,files(id,name,mimeType,webViewLink,size)','pageSize':1000}
        if token:q['pageToken']=token
        data=api(q)
        yield from data.get('files',[])
        token=data.get('nextPageToken')
        if not token:break

instrument = classify
voices = horn_voices

def main():
    todo=[(ROOT,[])]; entries=[]; folders=0; visited=set()
    while todo:
        folder,path=todo.pop(0)
        if folder in visited:continue
        visited.add(folder);folders+=1
        for f in children(folder):
            if f['mimeType']=='application/vnd.google-apps.folder':
                todo.append((f['id'],path+[f['name']]))
            elif f['mimeType']=='application/pdf' or f['name'].lower().endswith('.pdf'):
                entries.append({'id':f['id'],'name':f['name'],'path':path,'production':path[0] if path else 'Allgemein','work':' / '.join(path[1:]) if len(path)>1 else (path[0] if path else 'Allgemein'),'instruments':instrument(f['name']),'hornVoices':voices(f['name']) if 'Horn' in instrument(f['name']) else [],'url':'https://drive.google.com/file/d/'+f['id']+'/view'})
    entries.sort(key=lambda x:(x['production'].casefold(),x['work'].casefold(),x['name'].casefold()))
    output={'version':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'rootFolderId':ROOT,'foldersScanned':folders,'totalPdfs':len(entries),'files':entries}
    with open('noten-katalog.json','w',encoding='utf-8') as fp:json.dump(output,fp,ensure_ascii=False,indent=2)
    print(f'Catalog written: {len(entries)} PDFs across {folders} folders')

if __name__=='__main__':main()
