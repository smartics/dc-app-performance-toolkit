#!/usr/bin/env bash
#
# install_plugins.sh
# ------------------
# Installiert die .obr-Plugins aus smartics/plugins/ per UPM-REST-API auf der
# laufenden Confluence-Instanz (Bearer-PAT-Auth). Reihenfolge = Abhaengigkeiten:
# Toolbox zuerst, dann Extensions (WA/IS), dann Blueprints (Core zuerst), dann Userscripts.
#
# Auth:  Personal Access Token aus Datei .token (Repo-Root; git-ignored, NICHT ausgeben).
# Ziel:  aus app/confluence.yml (application_*), per BASE_URL ueberschreibbar.
#
# Verwendung:
#   bash smartics/install_plugins.sh            # installiert die Liste unten
#   BASE_URL=http://host/confluence bash smartics/install_plugins.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGDIR="$REPO_ROOT/smartics/plugins"
TOKEN_FILE="${TOKEN_FILE:-$REPO_ROOT/.token}"
YML="$REPO_ROOT/app/confluence.yml"

# --- Token laden (nie ausgeben) ---
[ -f "$TOKEN_FILE" ] || { echo "FEHLER: $TOKEN_FILE fehlt" >&2; exit 1; }
TOKEN="$(tr -d '\r\n' < "$TOKEN_FILE")"
[ -n "$TOKEN" ] || { echo "FEHLER: Token leer" >&2; exit 1; }

# --- Base-URL aus confluence.yml ableiten (oder BASE_URL nutzen) ---
if [ -z "${BASE_URL:-}" ]; then
  host=$(grep -E '^\s*application_hostname:' "$YML" | head -1 | awk '{print $2}')
  proto=$(grep -E '^\s*application_protocol:' "$YML" | head -1 | awk '{print $2}')
  port=$(grep -E '^\s*application_port:' "$YML" | head -1 | awk '{print $2}')
  postfix=$(grep -E '^\s*application_postfix:' "$YML" | head -1 | awk '{print $2}')
  BASE_URL="${proto}://${host}:${port}${postfix}"
fi
echo "Ziel: $BASE_URL"

# Gemeinsamer Cookie-Jar: haelt JSESSIONID + INGRESSCOOKIE (Node-Stickiness im Cluster),
# damit der session-gebundene upm-token zwischen GET und POST gueltig bleibt.
COOKIEJAR="$(mktemp)"
trap 'rm -f "$COOKIEJAR"' EXIT
AUTH=(-H "Authorization: Bearer $TOKEN" -b "$COOKIEJAR" -c "$COOKIEJAR")

# --- Installations-Reihenfolge: EXAKT wie vorgegeben (Dateinamen, nicht aendern!) ---
# Zwischen den Plugins wird ZWINGEND WAIT Sekunden gewartet (Default 120), auch bei "OK".
WAIT="${WAIT:-120}"
ORDER=(
  "userscripts-for-confluence-4.0.0.obr"
  "smartics-projectdoc-confluence-8.0.2.obr"
  "smartics-projectdoc-infosys-extension-9.0.1.obr"
  "smartics-projectdoc-webapi-extension-14.0.0.obr"
  "smartics-projectdoc-confluence-space-core-21.0.0.obr"
  "smartics-projectdoc-confluence-space-swdev-17.0.0.obr"
  "smartics-projectdoc-confluence-arc42-15.0.0.obr"
  "smartics-projectdoc-confluence-space-agileplanning-18.0.0.obr"
  "smartics-projectdoc-confluence-space-devdiary-18.0.0.obr"
  "smartics-projectdoc-confluence-space-prjmgmt-10.0.0.obr"
  "smartics-projectdoc-confluence-space-teamwork-6.0.0.obr"
  "smartics-doctype-addon-services-7.0.0.obr"
  "smartics-doctype-addon-strategy-7.0.0.obr"
  "smartics-doctype-addon-vmodellxt-8.0.0.obr"
)

# --- Auth-Vorabpruefung (read-only) ---
echo "== Auth-Check =="
code=$(curl -sS -m 30 "${AUTH[@]}" -H "Accept: application/vnd.atl.plugins.installed+json" \
  -o /dev/null -w "%{http_code}" "$BASE_URL/rest/plugins/1.0/")
echo "GET /rest/plugins/1.0/ -> HTTP $code"
[ "$code" = "200" ] || { echo "FEHLER: Auth/Erreichbarkeit fehlgeschlagen (HTTP $code)"; exit 1; }

install_one() {
  local file="$1" name; name="$(basename "$file")"
  echo "---- $name ----"
  # 1) UPM-Token (CSRF) aus Response-Header holen
  local upm
  upm=$(curl -sS -m 30 "${AUTH[@]}" -H "Accept: application/vnd.atl.plugins.installed+json" \
        -D - -o /dev/null "$BASE_URL/rest/plugins/1.0/" | tr -d '\r' | awk -F': ' 'tolower($1)=="upm-token"{print $2}')
  [ -n "$upm" ] || { echo "  ! kein upm-token erhalten"; return 1; }
  # 2) Datei hochladen
  local resp
  resp=$(curl -sS -m 300 "${AUTH[@]}" -X POST \
        -F "plugin=@${file};type=application/octet-stream" \
        "$BASE_URL/rest/plugins/1.0/?token=${upm}")
  # 3) Pending-Task pollen
  local self; self=$(printf '%s' "$resp" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('links',{}).get('self',''))" 2>/dev/null || true)
  if [ -z "$self" ]; then echo "  Antwort: $(printf '%s' "$resp" | head -c 200)"; return 1; fi
  for i in $(seq 1 60); do
    local p; p=$(curl -sS -m 30 "${AUTH[@]}" "$BASE_URL$self" 2>/dev/null || true)
    echo "$p" | grep -q '"done":true\|"enabled":true\|"status":{"done":true' && { echo "  OK installiert"; return 0; }
    echo "$p" | grep -qi 'err\|"code":' && { echo "  Status: $(printf '%s' "$p" | head -c 200)"; }
    sleep 3
  done
  echo "  (Timeout beim Pollen – bitte im UPM pruefen)"; return 1
}

echo "== Installation (${#ORDER[@]} Plugins, ${WAIT}s Pause dazwischen) =="
# Vorab pruefen, dass alle Dateien existieren
for name in "${ORDER[@]}"; do
  [ -e "$PLUGDIR/$name" ] || { echo "FEHLER: Datei fehlt: $name"; exit 1; }
done
total=${#ORDER[@]}; idx=0
for name in "${ORDER[@]}"; do
  idx=$((idx+1))
  echo "############ [$idx/$total] $(date '+%F %T') : $name ############"
  install_one "$PLUGDIR/$name" || echo "  -> PROBLEM bei $name"
  if [ "$idx" -lt "$total" ]; then
    echo "  ... Pflichtpause ${WAIT}s vor dem naechsten Plugin (auch bei OK) ..."
    sleep "$WAIT"
  fi
done
echo "== Fertig: $(date '+%F %T') =="
