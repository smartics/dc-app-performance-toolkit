#!/usr/bin/env bash
#
# fetch_aws_credentials.sh
# -------------------------
# Holt die AWS-Credentials via 1Password Service-Account aus dem Vault
# und schreibt sie nach app/util/k8s/aws_envs (das der Terraform-Docker-Run mountet).
#
# Voraussetzungen:
#   - 1Password CLI (op) installiert           -> op --version
#   - AWS CLI (aws) installiert                 -> aws --version
#   - OP_SERVICE_ACCOUNT_TOKEN in smartics/.env (git-ignored, NICHT committen!)
#
# Verwendung (vor jedem Cluster-Start):
#   bash smartics/fetch_aws_credentials.sh
#
set -euo pipefail

# --- Vault/Item-Konfiguration (bei Bedarf an reale 1Password-Struktur anpassen) ---
# Kann alternativ per Umgebungsvariable ueberschrieben werden.
# API_CREDENTIAL-Item "AWS-DCPT-TOKEN" im Vault "service":
#   Feld-ID username   (Label "Benutzername")  = AWS_ACCESS_KEY_ID
#   Feld-ID credential (Label "Anmeldedaten")  = AWS_SECRET_ACCESS_KEY
OP_VAULT="${OP_VAULT:-service}"                       # Vault-Name (fest; Service-Account sieht nur diesen)
OP_ITEM="${OP_ITEM:-AWS-DCPT-TOKEN}"                  # Item-Titel
OP_FIELD_ACCESS_KEY="${OP_FIELD_ACCESS_KEY:-username}"   # Feld-ID
OP_FIELD_SECRET_KEY="${OP_FIELD_SECRET_KEY:-credential}" # Feld-ID
AWS_REGION="${AWS_REGION:-us-east-2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
AWS_ENVS="$REPO_ROOT/app/util/k8s/aws_envs"

# --- .env laden (liefert OP_SERVICE_ACCOUNT_TOKEN) ---
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${OP_SERVICE_ACCOUNT_TOKEN:?FEHLER: OP_SERVICE_ACCOUNT_TOKEN nicht gesetzt (erwartet in $ENV_FILE)}"

command -v op  >/dev/null 2>&1 || { echo "FEHLER: 'op' (1Password CLI) nicht gefunden." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "FEHLER: 'aws' CLI nicht gefunden." >&2; exit 1; }

# Secret-References op://<vault>/<item>/<feld-id> (op read loest Feld per ID auf)
: "${OP_VAULT:?FEHLER: OP_VAULT nicht gesetzt}"
ref_ak="op://${OP_VAULT}/${OP_ITEM}/${OP_FIELD_ACCESS_KEY}"
ref_sk="op://${OP_VAULT}/${OP_ITEM}/${OP_FIELD_SECRET_KEY}"

echo "Hole AWS-Credentials aus 1Password (Vault='$OP_VAULT', Item='$OP_ITEM') ..."
ak="$(op read "$ref_ak")"
sk="$(op read "$ref_sk")"

if [ -z "$ak" ] || [ -z "$sk" ]; then
  echo "FEHLER: Leere Credentials aus 1Password erhalten. Vault/Item/Feld-Labels pruefen." >&2
  exit 1
fi

# --- aws_envs schreiben (restriktive Rechte) ---
umask 077
printf 'AWS_ACCESS_KEY_ID=%s\nAWS_SECRET_ACCESS_KEY=%s\n' "$ak" "$sk" > "$AWS_ENVS"
echo "-> $AWS_ENVS aktualisiert (chmod 600)."

# --- Verifikation ---
echo "Verifiziere via 'aws sts get-caller-identity' ($AWS_REGION) ..."
AWS_ACCESS_KEY_ID="$ak" AWS_SECRET_ACCESS_KEY="$sk" aws sts get-caller-identity --region "$AWS_REGION"
echo "OK: AWS-Credentials gueltig und in aws_envs geschrieben."
