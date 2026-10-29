#!/usr/bin/env python3
"""Publish a read-only catalog of PDFs from the public Dokumente Drive folder."""
import json, os, urllib.parse, urllib.request
from datetime import datetime, timezone
FOLDER='1N_G-1mRKps4Yv1x7IsrQqKBEYc2pDWpy'
key=os.environ['DRIVE_API_KEY']
items=[]; token=None
while True:
    args={'q':f"'{FOLDER}' in parents and trashed = false",'fields':'nextPageToken,files(id,name,mimeType)','pageSize':1000,'key':key}
    if token:args['pageToken']=token
    req=urllib.request.Request('https://www.googleapis.com/drive/v3/files?'+urllib.parse.urlencode(args))
    with urllib.request.urlopen(req,timeout=40) as response:data=json.load(response)
    for f in data.get('files',[]):
        if f.get('mimeType')=='application/pdf' or f.get('name','').lower().endswith('.pdf'):
            items.append({'id':f['id'],'name':f['name'],'url':'https://drive.google.com/file/d/'+f['id']+'/view'})
    token=data.get('nextPageToken')
    if not token:break
items.sort(key=lambda f:f['name'].casefold())
with open('dokumente-katalog.json','w',encoding='utf-8') as out:
    json.dump({'updatedAt':datetime.now(timezone.utc).isoformat(),'folderId':FOLDER,'files':items},out,ensure_ascii=False,indent=2)
print(f'{len(items)} documents indexed')
