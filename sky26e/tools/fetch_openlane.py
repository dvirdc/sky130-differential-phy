#!/usr/bin/env python3
"""Fetch official immutable OCI layers onto host disk, avoiding Docker VM capacity.
Only stages verified archives. Extraction and bind mounts are separate steps.
"""
from pathlib import Path
import urllib.request, json, hashlib, shutil
root=Path(__file__).resolve().parents[3]/'toolchain/openlane';root.mkdir(parents=True,exist_ok=True)
repo='efabless/openlane2';digest='sha256:77c4c5a02b802ec7c5a584622d3ee34c686b003419910ef60ef97499f3f9ee2f'
token=json.load(urllib.request.urlopen('https://ghcr.io/token?service=ghcr.io&scope=repository:'+repo+':pull'))['token']
def get(path):
 return urllib.request.urlopen(urllib.request.Request('https://ghcr.io/v2/'+repo+'/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.docker.distribution.manifest.v2+json'}),timeout=120)
raw=get('manifests/'+digest).read();assert hashlib.sha256(raw).hexdigest()==digest.split(':')[1]
manifest=json.loads(raw);(root/'manifest.json').write_bytes(raw)
raw=get('blobs/'+manifest['config']['digest']).read();assert hashlib.sha256(raw).hexdigest()==manifest['config']['digest'].split(':')[1]
(root/'config.json').write_bytes(raw)
for layer in manifest['layers']:
 h=layer['digest'].split(':')[1];f=root/(h+'.tar.gz')
 if not f.exists():
  partial=f.with_suffix('.partial')
  with get('blobs/'+layer['digest']) as src,partial.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
  assert hashlib.file_digest(partial.open('rb'),'sha256').hexdigest()==h
  partial.rename(f)
 assert hashlib.file_digest(f.open('rb'),'sha256').hexdigest()==h
 print('Verified '+f.name,flush=True)
