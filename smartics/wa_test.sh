#!/usr/bin/env bash
#
# wa_test.sh - setzt den EXAKTEN Web-API-Call ab, den der DCAPT-WA-Test verwendet
#              (app_specific_action_web_api in extension_locust.py, Z.261-274).
# Token wird aus .token gelesen (nicht auf der Kommandozeile sichtbar).
#
# Aufruf:  bash smartics/wa_test.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKEN="$(tr -d '\r\n' < "$REPO_ROOT/.token")"
host="$(grep -E '^\s*application_hostname:' "$REPO_ROOT/app/confluence.yml" | head -1 | awk '{print $2}')"
BASE="http://${host}/confluence"

echo "Ziel: $BASE/rest/projectdoc/1/document"
echo "Query: select=Title,Name,Iteration | from=PROJECTDOCTEST | where=\$<Title>=[projectdoc Space for Test Cases]"
echo "======================================================================"
echo "### 1) DER WA-TEST-CALL (soll nicht-leere id-list liefern) ###"
curl -sS -G "$BASE/rest/projectdoc/1/document" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "select=Title,Name,Iteration" \
  --data-urlencode "from=PROJECTDOCTEST" \
  --data-urlencode 'where=$<Title>=[projectdoc Space for Test Cases]' \
  --data-urlencode "expand=property" \
  -w "\n[HTTP %{http_code}]\n"

echo
echo "### 2) GEGENPROBE: gleiche Query, aber [DCAPT Document 1] (funktioniert erfahrungsgemaess) ###"
curl -sS -G "$BASE/rest/projectdoc/1/document" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "select=Title,Name,Iteration" \
  --data-urlencode "from=PROJECTDOCTEST" \
  --data-urlencode 'where=$<Title>=[DCAPT Document 1]' \
  --data-urlencode "expand=property" \
  -w "\n[HTTP %{http_code}]\n"
