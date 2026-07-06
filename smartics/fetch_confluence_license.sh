#!/usr/bin/env bash
#
# fetch_confluence_license.sh
# ---------------------------
# Holt den Confluence-DC-Lizenzschluessel via 1Password Service-Account,
# normalisiert ihn auf EINE Zeile (ohne Zeilenumbrueche/Leerzeichen) und traegt
# ihn in app/util/k8s/dcapt.tfvars (Zeile `confluence_license = "..."`) ein.
#
# Hintergrund: Terraform verlangt die Lizenz einzeilig ohne Whitespace. Der in
# 1Password gespeicherte Wert darf ruhig Zeilenumbrueche enthalten - dieses
# Skript entfernt sie.
#
# Voraussetzungen:
#   - 1Password CLI (op) installiert
#   - OP_SERVICE_ACCOUNT_TOKEN in smartics/.env (git-ignored, NICHT committen!)
#
# Verwendung (vor dem Cluster-Start):
#   bash smartics/fetch_confluence_license.sh
#
set -euo pipefail

# --- Vault/Item-Konfiguration (bei Bedarf ueber Umgebungsvariablen ueberschreiben) ---
# Item "Confluence DC Lizenz" im Vault "service", Feld-ID "reg_code".
OP_VAULT="${OP_VAULT:-service}"
OP_ITEM="${OP_ITEM:-Confluence DC Lizenz}"
OP_FIELD_LICENSE="${OP_FIELD_LICENSE:-reg_code}"   # Feld-ID (Label ist "Lizenzschluessel")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
TFVARS="$REPO_ROOT/app/util/k8s/dcapt.tfvars"

# --- .env laden (liefert OP_SERVICE_ACCOUNT_TOKEN) ---
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${OP_SERVICE_ACCOUNT_TOKEN:?FEHLER: OP_SERVICE_ACCOUNT_TOKEN nicht gesetzt (erwartet in $ENV_FILE)}"
command -v op >/dev/null 2>&1 || { echo "FEHLER: 'op' (1Password CLI) nicht gefunden." >&2; exit 1; }
[ -f "$TFVARS" ] || { echo "FEHLER: $TFVARS nicht gefunden." >&2; exit 1; }

echo "Hole Confluence-Lizenz aus 1Password (Vault='$OP_VAULT', Item='$OP_ITEM') ..."
# Whitespace/Zeilenumbrueche entfernen -> einzeilig
lic="$(op read "op://${OP_VAULT}/${OP_ITEM}/${OP_FIELD_LICENSE}" | tr -d '\r\n\t ')"

if [ -z "$lic" ]; then
  echo "FEHLER: Leere Lizenz aus 1Password erhalten. Vault/Item/Feld pruefen." >&2
  exit 1
fi
case "$lic" in
  *'"'*) echo "FEHLER: Lizenz enthaelt ein Anfuehrungszeichen - abgebrochen." >&2; exit 1 ;;
esac

# --- confluence_license-Zeile in dcapt.tfvars ersetzen (python, sicher ggü. Sonderzeichen) ---
CONF_LIC="$lic" TFVARS_PATH="$TFVARS" python3 - <<'PY'
import os, re
lic = os.environ['CONF_LIC']
p   = os.environ['TFVARS_PATH']
s   = open(p).read()
new, n = re.subn(r'(?m)^confluence_license\s*=.*$', 'confluence_license = "%s"' % lic, s, count=1)
if n == 0:
    raise SystemExit("FEHLER: Zeile 'confluence_license = ...' nicht gefunden in dcapt.tfvars")
if new != s:
    open(p, 'w').write(new)
    print("confluence_license aktualisiert - einzeilig, Laenge=%d Zeichen" % len(lic))
else:
    print("confluence_license bereits aktuell (identisch) - Laenge=%d Zeichen" % len(lic))
PY

echo "-> $TFVARS aktualisiert."
echo "Hinweis: dcapt.tfvars ist git-getrackt - Aenderung NICHT committen (Lizenz nicht in git)."
