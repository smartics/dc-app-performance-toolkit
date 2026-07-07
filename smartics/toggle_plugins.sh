#!/usr/bin/env bash
#
# toggle_plugins.sh <disable|enable> [single-key]
# ------------------------------------------------
# Aktiviert/deaktiviert die 14 Smartics-Apps per UPM-REST (Bearer-PAT aus .token).
# disable-Reihenfolge: Abhaengige zuerst, Toolbox zuletzt. enable-Reihenfolge: umgekehrt.
# Mit optionalem [single-key] wird nur diese eine App getoggelt (zum Testen).
#
set -euo pipefail
MODE="${1:?Usage: toggle_plugins.sh <disable|enable> [single-key]}"
SINGLE="${2:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKEN="$(tr -d '\r\n' < "$REPO_ROOT/.token")"
host="$(grep -E '^\s*application_hostname:' "$REPO_ROOT/app/confluence.yml" | head -1 | awk '{print $2}')"
BASE="http://${host}/confluence"
JAR="$(mktemp)"; trap 'rm -f "$JAR"' EXIT
AUTH=(-H "Authorization: Bearer $TOKEN" -b "$JAR" -c "$JAR")

# enable-Reihenfolge (Toolbox zuerst); disable = umgekehrt
ENABLE_ORDER=(
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence"
  "de.smartics.atlassian.smartics-projectdoc-webapi-extension"
  "de.smartics.atlassian.smartics-projectdoc-infosys-extension"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-core"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-swdev"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-arc42"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-agileplanning"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-devdiary"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-prjmgmt"
  "de.smartics.atlassian.confluence.smartics-projectdoc-confluence-space-teamwork"
  "de.smartics.atlassian.confluence.smartics-doctype-addon-services"
  "de.smartics.atlassian.confluence.smartics-doctype-addon-strategy"
  "de.smartics.atlassian.confluence.smartics-doctype-addon-vmodellxt"
  "de.smartics.userscripts-for-confluence"
)
if [ "$MODE" = "disable" ]; then STATE=false; KEYS=(); for ((i=${#ENABLE_ORDER[@]}-1;i>=0;i--)); do KEYS+=("${ENABLE_ORDER[$i]}"); done
elif [ "$MODE" = "enable" ]; then STATE=true; KEYS=("${ENABLE_ORDER[@]}")
else echo "MODE muss disable|enable sein"; exit 1; fi
[ -n "$SINGLE" ] && KEYS=("$SINGLE")

upm_token(){ curl -sS -m 30 "${AUTH[@]}" -H "Accept: application/vnd.atl.plugins.installed+json" -D - -o /dev/null "$BASE/rest/plugins/1.0/" | tr -d '\r' | awk -F': ' 'tolower($1)=="upm-token"{print $2}'; }

echo "== MODE=$MODE (enabled=$STATE), ${#KEYS[@]} App(s) =="
for key in "${KEYS[@]}"; do
  upm="$(upm_token)"
  code=$(curl -sS -m 60 "${AUTH[@]}" -X PUT \
    -H "Content-Type: application/vnd.atl.plugins.plugin+json" \
    "$BASE/rest/plugins/1.0/${key}-key?token=${upm}" \
    -d "{\"key\":\"${key}\",\"enabled\":${STATE}}" -o /tmp/toggle_resp.json -w "%{http_code}")
  now=$(python3 -c "import json;print(json.load(open('/tmp/toggle_resp.json')).get('enabled','?'))" 2>/dev/null || echo '?')
  printf "  %-70s HTTP %s enabled=%s\n" "$key" "$code" "$now"
  sleep 2
done
