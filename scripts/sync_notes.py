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

instruments={
    "Horn":r"(?<![a-z])(?:horn|hrn\.?|corno)(?![a-z])",
    "Trompete":r"(?<![a-z])(?:trompete|trp\.?|tpt\.?|trumpet)(?![a-z])",
    "Posaune":r"(?<![a-z])(?:posaune|pos\.?|trombone)(?![a-z])",
    "Tuba":r"(?<![a-z])tuba(?![a-z])",
    "Flöte":r"(?<![a-z])(?:flöte|floete|flute|fl\.?)(?![a-z])",
    "Oboe":r"(?<![a-z])(?:oboe|ob\.?)(?![a-z])",
    "Klarinette":r"(?<![a-z])(?:klarinette|clarinet|kl\.?)(?![a-z])",
    "Fagott":r"(?<![a-z])(?:fagott|bassoon|fg\.?)(?![a-z])",
    "Violine":r"(?<![a-z])(?:violine|violin|viol\.?|vl\.?)(?![a-z])",
    "Viola":r"(?<![a-z])(?:viola|va\.?)(?![a-z])",
    "Violoncello":r"(?<![a-z])(?:violoncello|cello|vc\.?)(?![a-z])",
    "Kontrabass":r"(?<![a-z])(?:kontrabass|contrabass|kb\.?)(?![a-z])",
    "Schlagwerk":r"(?<![a-z])(?:schlagwerk|pauke|percussion|perc\.?)(?![a-z])",
    "Cembalo":r"(?<![a-z])(?:cembalo|harpsichord)(?![a-z])",
}
def infer(name):
    value=name.lower().replace("_"," ").replace("-"," ")
    return [label for label,pattern in instruments.items() if re.search(pattern,value,re.I)]
def normalize_trombones(name, tags):
    """Bass trombone is the third trombone part, even if no number is printed."""
    value=name.lower().replace("_"," ").replace("-"," ")
    value=re.sub(r"\.pdf$","",value)
    trombone=r"(?:posaune|trombone|trombon|pos\.?)"
    if not re.search(trombone,value):
        return tags
    tags=[tag for tag in tags if tag not in ("Posaune 1","Posaune 2","Posaune 3")]
    voices=set()
    if re.search(r"(?:bass\s*posaune|bass\s*trombon(?:e)?|bassposaune)",value):
        voices.add(3)
    for m in re.finditer(r"(?:(?<!\d)([123])\s*[.]?\s*"+trombone+r"\b|"+trombone+r"\s*[.]?\s*([123])\b)",value):
        voices.add(int(m.group(1) or m.group(2)))
    # Combined parts, e.g. Posaune1+2.
    if re.search(trombone+r"\s*1\s*[+&/]\s*2",value):
        voices.update((1,2))
    if "Posaune" not in tags:
        tags.append("Posaune")
    tags.extend(f"Posaune {n}" for n in sorted(voices))
    return tags

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
        "instruments":normalize_trombones(name, previous.get("instruments",[]) if unchanged else infer(name)),
        "hornVoices":previous.get("hornVoices",[]) if unchanged else [],
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
