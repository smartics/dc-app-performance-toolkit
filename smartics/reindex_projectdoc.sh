#!/usr/bin/env bash
#
# reindex_projectdoc.sh [SPACE_KEY ...]   (default: PROJECTDOCTEST)
# ================================================================
# Erzwingt den projectdoc-/Confluence-Reindex NACH einem Space-Import, OHNE manuelles
# Neu-Speichern in der UI: liest jede Seite des Space per REST und schreibt sie mit
# version+1 und UNVERAENDERTEM Body zurueck (PUT) -> triggert Re-Indizierung.
# Ersetzt den laestigen Post-Import-Handschritt "alle Seiten neu speichern".
#
# Auth: Bearer-PAT aus .token (Repo-Root). Ziel-URL aus app/confluence.yml.
# Verwendung:  bash smartics/reindex_projectdoc.sh              # PROJECTDOCTEST
#              bash smartics/reindex_projectdoc.sh PROJECTDOCTEST USTEST BLUEPRINT
#
# ⚠️ Erstmals 2026-07 geschrieben, noch nicht gegen eine Live-Instanz getestet.
#
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKEN="$(tr -d '\r\n' < "$REPO/.token")"
HOST="$(grep -E '^\s*application_hostname:' "$REPO/app/confluence.yml" | head -1 | awk '{print $2}')"
BASE="http://${HOST}/confluence"
SPACES=("${@:-PROJECTDOCTEST}")

TOKEN="$TOKEN" BASE="$BASE" python3 - "${SPACES[@]}" <<'PY'
import os, sys, json, urllib.request, urllib.error, time
BASE=os.environ['BASE']; TOKEN=os.environ['TOKEN']
H={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'}

def req(method,url,data=None):
    r=urllib.request.Request(url,data=(json.dumps(data).encode() if data is not None else None),headers=H,method=method)
    with urllib.request.urlopen(r,timeout=60) as resp: return json.loads(resp.read().decode())

def pages(space):
    start=0
    while True:
        u=f"{BASE}/rest/api/content?spaceKey={space}&type=page&limit=50&start={start}&expand=version,body.storage,space"
        d=req('GET',u); res=d.get('results',[])
        for p in res: yield p
        if len(res)<50: break
        start+=50

for space in sys.argv[1:]:
    print(f"== Space {space}: reindex per re-save ==")
    ok=err=0
    for p in pages(space):
        pid=p['id']; title=p['title']; ver=p['version']['number']
        body=p.get('body',{}).get('storage',{}).get('value','')
        payload={"id":pid,"type":"page","title":title,"space":{"key":space},
                 "version":{"number":ver+1,"message":"reindex re-save (no content change)"},
                 "body":{"storage":{"value":body,"representation":"storage"}}}
        try:
            req('PUT',f"{BASE}/rest/api/content/{pid}",payload); ok+=1
            print(f"  ok   {pid}  v{ver}->{ver+1}  {title}")
        except urllib.error.HTTPError as e:
            err+=1; print(f"  FAIL {pid}  {title}  HTTP {e.code} {e.read()[:120]}")
        time.sleep(0.2)
    print(f"  -> {space}: {ok} neu gespeichert, {err} Fehler")
print("Fertig. Hinweis: projectdoc-Index braucht ggf. 1-2 min zum Durchlaufen.")
PY
