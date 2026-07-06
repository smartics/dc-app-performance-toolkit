#!/usr/bin/env bash
#
# download_plugins.sh
# -------------------
# Laedt die JEWEILS NEUESTE Data-Center-Version der benoetigten Smartics-Marketplace-Apps
# nach smartics/plugins/ herunter (via oeffentliche Atlassian-Marketplace-REST-API v2).
#
# App-Keys stammen aus dem Vendor smartics (id 1211428). Nicht benoetigte Apps unten auskommentieren.
# Verwendung:  bash smartics/download_plugins.sh
#
set -euo pipefail

API="https://marketplace.atlassian.com/rest/2"
BASE="https://marketplace.atlassian.com"
OUTDIR="${OUTDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugins}"
mkdir -p "$OUTDIR"

# --- Benoetigte Apps (Key = Reverse-DNS). Fuer "alle Apps ausser DM": PD, WA, IS, US, BP. ---
APPS=(
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence"             # PD  projectdoc Toolbox
  "de.smartics.atlassian.smartics-projectdoc-webapi-extension"                  # WA  Web API Extension
  "de.smartics.atlassian.smartics-projectdoc-infosys-extension"                 # IS  Information Systems Extension
  "de.smartics.userscripts-for-confluence"                                      # US  Userscripts for Confluence
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-core"  # BP  projectdoc Core Blueprints
  # --- weitere Blueprints (bei Bedarf einkommentieren) ---
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-prjmgmt"       # Project Management
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-agileplanning" # Agile Planning
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-teamwork"      # Teamwork
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-swdev"         # Software Development
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-arc42"               # arc42
  # "de.smartics.atlassian.confluence.smartics-doctype-addon-services"                    # Service Management
  # "de.smartics.atlassian.confluence.smartics-doctype-addon-strategy"                    # Business Strategy
  # "de.smartics.atlassian.confluence.smartics-doctype-addon-vmodellxt"                   # V-Modell XT
  # "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-devdiary"      # Developer Diaries
  # --- DM wird fuer "alle ausser DM" NICHT gebraucht ---
  # "de.smartics.atlassian.confluence.smartics-atlassian-confluence-macros"               # DM  Documentation Macros
)

echo "Ziel-Verzeichnis: $OUTDIR"
echo "======================================================================"
for key in "${APPS[@]}"; do
  ver_json="$(curl -sS -m 60 "$API/addons/$key/versions/latest?hosting=datacenter" || true)"
  info="$(printf '%s' "$ver_json" | python3 -c "
import sys,json
try: d=json.load(sys.stdin)
except Exception: print('ERR\t\t\t'); sys.exit()
name=d.get('name','?')
art=d.get('_embedded',{}).get('artifact',{})
self=art.get('_links',{}).get('self',{}).get('href','')
comp=d.get('compatibilities',[])
cc=''
for c in comp:
    if c.get('application')=='confluence':
        dc=c.get('hosting',{}).get('dataCenter',{})
        cc='Confluence %s-%s'%(dc.get('min',{}).get('version','?'), dc.get('max',{}).get('version','?'))
print('%s\t%s\t%s' % (name, self, cc))
")"
  IFS=$'\t' read -r version asset_path compat <<<"$info"
  if [ "$version" = "ERR" ] || [ -z "$asset_path" ]; then
    echo "!! $key : keine DC-Version/kein Artifact gefunden"; continue
  fi
  asset_json="$(curl -sS -m 60 "$BASE$asset_path" || true)"
  finfo="$(printf '%s' "$asset_json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('%s\t%s' % (d.get('fileInfo',{}).get('logicalFileName','app.obr'),
                  d.get('_links',{}).get('binary',{}).get('href','')))
")"
  IFS=$'\t' read -r fname binary <<<"$finfo"
  printf "%-70s v%-8s [%s]\n" "$key" "$version" "$compat"
  code=$(curl -sSL -m 300 "$binary" -o "$OUTDIR/$fname" -w "%{http_code}")
  sz=$(stat -c%s "$OUTDIR/$fname" 2>/dev/null || echo 0)
  echo "    -> $fname  (HTTP $code, $sz bytes)"
done
echo "======================================================================"
echo "Fertig. Inhalt:"
ls -la "$OUTDIR"
