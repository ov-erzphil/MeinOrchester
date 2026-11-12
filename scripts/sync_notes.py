#!/usr/bin/env python3
"""Refresh the GitHub Pages note catalog from the public Apps Script Drive inventory."""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = os.environ["NOTES_SOURCE_URL"]
TARGET = Path("noten-katalog.json")
ROOT = "Notenarchiv fuer App"
with urllib.request.urlopen(urllib.request.Request(ENDPOINT,headers={"User-Agent":"MeinOrchester-Sync/1.0"}),timeout=180) as response:
    source = json.load(response)
incoming = source.get("files")
if not isinstance(incoming,list) or len(incoming)<1000:
    raise ValueError("Drive inventory missing or unexpectedly small; refusing to replace catalog")
existing=json.loads(TARGET.read_text(encoding="utf-8"))
old={f["id"]:f for f in existing["files"]}
if len(incoming)<len(old)*0.75:
    raise ValueError("More than 25% of PDFs missing; refusing to replace catalog")

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from instrument_names import classify, horn_voices

files=[]
for item in incoming:
    fid=item.get("id");name=item.get("name","");folder=item.get("folder","")
    if not fid or not name.lower().endswith(".pdf") or not folder.startswith(ROOT):
        continue
    path=[p for p in folder.split("/")[1:] if p]
    previous=old.get(fid,{})
    unchanged=previous.get("name")==name and previous.get("path")==path
    files.append({
        "id":fid,"name":name,"path":path,
        "production":path[0] if path else "Sonstiges",
        "work":path[-1] if path else name.rsplit(".",1)[0],
        "instruments":classify(name),
        "hornVoices":horn_voices(name),
        "url":f"https://drive.google.com/file/d/{fid}/view"
    })
files.sort(key=lambda f:(f["production"].casefold(),f["work"].casefold(),f["name"].casefold()))
if len(files)<1000: raise ValueError("Too few valid PDF records")
result={
    "version":1,"generatedAt":datetime.now(timezone.utc).isoformat(),
    "rootFolderId":existing.get("rootFolderId"),
    "foldersScanned":len({tuple(f["path"][:i]) for f in files for i in range(1,len(f["path"])+1)}),
    "totalPdfs":len(files),"files":files
}
# Do not commit an unchanged list just to update its timestamp.
if [{k:v for k,v in f.items()} for f in files]==existing.get("files",[]):
    print(f"No changes ({len(files)} PDFs)")
else:
    TARGET.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Updated catalog: {len(files)} PDFs, {sum('zelenka' in f['name'].lower() for f in files)} Zelenka PDFs")
