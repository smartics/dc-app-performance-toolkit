#!/usr/bin/env bash
#
# dcapt_driver.sh — Orchestrierungs-Treiber fuer die DCAPT-Confluence-Kampagne (Smartics).
# ==========================================================================================
# Kapselt die AUTOMATISIERBAREN Schritte. Manuelle Confluence-UI-Gates (Space-Import,
# Seiten-Neuspeichern/Reindex, Allowlist, US-Client-Logging, App-Lizenzen) sind als
# "MANUAL GATE" markiert und werden NICHT automatisch erledigt (siehe DCAPT-2026-LESSONS.md).
#
# ⚠️ STAND: erstmals 2026-07 geschrieben, in dieser Form noch NICHT end-to-end getestet.
#    Beim naechsten Lauf verifizieren/anpassen. Am besten in tmux/nohup laufen lassen,
#    damit ein Verbindungsabbruch die Kampagne nicht killt:
#      tmux new -s dcapt 'bash smartics/dcapt_driver.sh <phase>'
#
# Verwendung:  bash smartics/dcapt_driver.sh <phase>
#   phases: creds | provision <N> | plugins | config <baseline|apps> |
#           run <LABEL> | scale <N> | reports | teardown | status
#
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S="$REPO/app/util/k8s"; NS=atlassian; REGION=us-east-2; ENVN=dcapt-confluence-e1
TF_IMG=atlassianlabs/terraform:2.9.23
KUBECTL="${KUBECTL:-$HOME/bin/kubectl}"
ABORT_THRESHOLD=25   # % failures -> Auto-Abort (nach 420s)

log(){ echo "[$(date '+%F %T')] $*"; }
aws_env(){ export AWS_ACCESS_KEY_ID=$(grep '^AWS_ACCESS_KEY_ID=' "$K8S/aws_envs"|cut -d= -f2) \
                  AWS_SECRET_ACCESS_KEY=$(grep '^AWS_SECRET_ACCESS_KEY=' "$K8S/aws_envs"|cut -d= -f2); }
exec_pod(){ "$KUBECTL" -n $NS get pods -o name 2>/dev/null | grep dcapt | head -1 | cut -d/ -f2; }

creds(){ bash "$REPO/smartics/fetch_aws_credentials.sh"; bash "$REPO/smartics/fetch_confluence_license.sh"; }

wait_nodes_ready(){ # N
  local want=$1; aws_env
  log "Warte, bis $want confluence-Nodes 1/1 ready sind ..."
  for i in $(seq 1 120); do
    local n; n=$("$KUBECTL" -n $NS get pods 2>/dev/null | grep -cE 'confluence-[0-9]+ +1/1')
    log "  ready: $n/$want"; [ "$n" -ge "$want" ] && { log "alle $want ready ✓"; return 0; }
    sleep 60
  done; log "TIMEOUT beim Warten auf Node-Readiness"; return 1
}

provision(){ # N replicas
  local n=$1
  sed -i "s/^confluence_replica_count = .*/confluence_replica_count = $n/" "$K8S/dcapt.tfvars"
  grep -q '^confluence_installation_timeout = 60' "$K8S/dcapt.tfvars" || \
    sed -i 's/^confluence_installation_timeout = .*/confluence_installation_timeout = 60/' "$K8S/dcapt.tfvars"
  creds
  log "install.sh (replica_count=$n) ..."
  ( cd "$K8S" && docker run --pull=always --env-file aws_envs \
      -v "$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
      -v "$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
      -v "$PWD/logs:/data-center-terraform/logs" \
      $TF_IMG ./install.sh -c conf.tfvars ) 2>&1 | tee "$REPO/install_driver.log" || log "install.sh non-zero (evtl. Node-Warmup-Timeout)"
  # #6 ELB-Hostname automatisch in confluence.yml eintragen (aus install-Output)
  local elb; elb=$(grep -oE 'load_balancer_hostname" = "[^"]+' "$REPO/install_driver.log" | head -1 | sed 's/.*"= *"//;s/.*"//')
  [ -z "$elb" ] && elb=$(grep -oE '[a-z0-9]+-[0-9]+\.'"$REGION"'\.elb\.amazonaws\.com' "$REPO/install_driver.log" | head -1)
  if [ -n "$elb" ]; then
    sed -i "s|^\( *application_hostname:\) .*|\1 $elb|" "$REPO/app/confluence.yml"
    log "confluence.yml application_hostname -> $elb ✓"
  else
    log "MANUAL: ELB-Hostname nicht aus Output extrahierbar -> selbst in app/confluence.yml eintragen."
  fi
  wait_nodes_ready "$n"   # Terraform-Timeout ignorieren, auf echte Readiness warten
}

set_config(){ # baseline | apps
  local val6=6; [ "$1" = baseline ] && val6=0
  for k in us_rest_content transclude_documents display_table web_api information_system blueprints; do
    sed -i "s/^\( *standalone_extension_$k:\) .*/\1 $val6 /" "$REPO/app/confluence.yml"
  done
  log "confluence.yml Profil = $1 (App-Actions=$val6; DM bleibt 0)"
}

run_test(){ # LABEL  (z.B. RUN3)
  local label="$1"; creds; aws_env
  log "Starte $label (bzt_on_pod) ..."
  ( cd "$REPO" && ENVIRONMENT_NAME=$ENVN docker run --pull=always --env-file ./app/util/k8s/aws_envs \
      -e REGION=$REGION -e ENVIRONMENT_NAME=$ENVN \
      -v "$PWD:/data-center-terraform/dc-app-performance-toolkit" \
      -v "$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
      $TF_IMG bash bzt_on_pod.sh confluence.yml ) >/dev/null 2>&1 || true   # Wrapper detacht -> egal
  local POD; POD=$(exec_pod); log "Exec-Pod: $POD — ueberwache tmux bzt_session ..."
  local start; start=$(date +%s)
  while "$KUBECTL" -n $NS exec "$POD" -- tmux has-session -t bzt_session 2>/dev/null; do
    local el; el=$(( $(date +%s) - start ))
    local fail; fail=$("$KUBECTL" -n $NS exec "$POD" -- tmux capture-pane -t bzt_session -p 2>/dev/null \
      | tr '\n' ' ' | grep -oE '[0-9.]+% failures' | tail -1 | grep -oE '^[0-9.]+'); fail=${fail:-0}
    log "  $label elapsed=${el}s cum_fail=${fail}%"
    if [ "$el" -ge 420 ] && awk "BEGIN{exit !($fail >= $ABORT_THRESHOLD)}"; then
      log "!!! ABORT $label ($fail% >= $ABORT_THRESHOLD%)"; "$KUBECTL" -n $NS exec "$POD" -- tmux kill-session -t bzt_session 2>/dev/null; break
    fi; sleep 60
  done
  local res; res=$("$KUBECTL" -n $NS exec "$POD" -- sh -c 'ls -1t /dc-app-performance-toolkit/app/results/confluence/ | head -1' 2>/dev/null | tr -d '\r')
  local dest="/home/anton/DCPT/${label}-${res}"
  for t in 1 2 3; do rm -rf "$dest"; "$KUBECTL" -n $NS cp "$NS/$POD:dc-app-performance-toolkit/app/results/confluence/$res" "$dest" 2>/dev/null && break; sleep 5; done
  cp -a "$dest" "$REPO/app/results/confluence/$label" 2>/dev/null || true
  log "$label fertig -> $dest (+ app/results/confluence/$label). Success: $(grep -E '^Success' "$dest/results_summary.log" 2>/dev/null)"
}

reports(){ # generiert alle in reports_generation/ vorhandenen reg_*/scale_* Profile
  docker run --rm -v "$REPO/app/results:/r" alpine sh -c "chown -R $(id -u):$(id -g) /r" >/dev/null 2>&1
  for prof in "$REPO"/app/reports_generation/reg_*.yml "$REPO"/app/reports_generation/scale_*.yml; do
    [ -e "$prof" ] || continue; local p; p=$(basename "$prof" .yml)
    log "Report $p ..."
    ( cd "$REPO" && docker run --pull=always -v "$PWD:/dc-app-performance-toolkit" \
       --workdir="//dc-app-performance-toolkit/app/reports_generation" \
       --entrypoint=python $TF_IMG >/dev/null 2>&1 || \
       docker run --pull=always -v "$PWD:/dc-app-performance-toolkit" \
       --workdir="//dc-app-performance-toolkit/app/reports_generation" \
       --entrypoint=python atlassian/dcapt csv_chart_generator.py "$p.yml" )
  done
  docker run --rm -v "$REPO/app/results:/r" alpine sh -c "chown -R $(id -u):$(id -g) /r" >/dev/null 2>&1
  log "Reports in app/results/reports/ (umbenennen + buendeln s. Kampagnen-Notizen)"
}

teardown(){ creds; aws_env
  log "TERMINIERE Cluster (uninstall.sh -f) ..."
  ( cd "$K8S" && printf 'yes\nyes\n' | docker run -i --pull=always --env-file aws_envs \
      -v "$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
      -v "$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
      -v "$PWD/logs:/data-center-terraform/logs" \
      $TF_IMG ./uninstall.sh -c conf.tfvars -f )
  aws eks list-clusters --region $REGION --query clusters --output text
}

status(){ aws_env; "$KUBECTL" -n $NS get pods 2>/dev/null | grep -E "confluence-[0-9]|dcapt"; }

# ---- Dispatcher ----
cmd="${1:-help}"; shift || true
case "$cmd" in
  creds) creds ;;
  provision) provision "${1:?N}" ;;
  plugins) bash "$REPO/smartics/download_plugins.sh"; bash "$REPO/smartics/install_plugins.sh" ;;
  config) set_config "${1:?baseline|apps}" ;;
  reindex) bash "$REPO/smartics/reindex_projectdoc.sh" "$@" ;;
  run) run_test "${1:?LABEL}" ;;
  scale) provision "${1:?N}" ;;
  reports) reports ;;
  teardown) teardown ;;
  status) status ;;
  *) cat <<TXT
dcapt_driver.sh <phase>
  creds                 AWS + Lizenz aus 1Password
  provision <N>         install.sh mit N Nodes + auf Readiness warten (erstes Mal: N=1)
  plugins               download_plugins + install_plugins
  reindex [SPACES...]   Reindex per REST erzwingen (default PROJECTDOCTEST) - Post-Import
  config <baseline|apps> confluence.yml Profil setzen
  run <LABEL>           einen Test fahren + selbst ueberwachen (Auto-Abort) + Results holen
  scale <N>             = provision <N> (fuer Run 4=2, Run 5=4)
  teardown              Cluster terminieren (uninstall -f)
  status                Pods anzeigen
Typischer Ablauf:
  creds; provision 1;  # dann MANUAL: plugins, config apps? NEIN erst Baseline:
  run RUN1; plugins;   # (Lizenzen+Spaces+Post-Import MANUAL, s. DCAPT-2026-LESSONS.md)
  run RUN2;            # Baseline-config, App installiert
  config apps; run RUN3; scale 2; run RUN4; scale 4; run RUN5; reports; teardown
TXT
  ;;
esac
