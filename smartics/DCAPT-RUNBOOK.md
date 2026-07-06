# DCAPT Confluence Enterprise Runbook (Smartics)

> **Zweck:** Vollständige, wiederverwendbare Anleitung, um die DCAPT-Runs **1–5** für Confluence
> Data Center auf AWS durchzuführen. Ausgelegt zum Wiedereinlesen in neuen Sessions und zur
> **jährlichen Wiederholung** (Marketplace-Review).
>
> **Quellen (offiziell):**
> - Repo: https://github.com/atlassian/dc-app-performance-toolkit
> - User Guide Confluence: https://github.com/atlassian/dc-app-performance-toolkit/blob/master/docs/dc-apps-performance-toolkit-user-guide-confluence.md
>
> **Stand dieses Runbooks:** DCAPT `8.10.4`, Confluence `10.2.2`, Terraform-Image
> `atlassianlabs/terraform:2.9.23`, Branch `smartics-dcapt-2026-all`, Region `us-east-2`.
> Nur Confluence Data Center — nicht Jira/Bamboo/Bitbucket.

---

## 0. Grundprinzip

- Alle Runs laufen **auf dem Execution-Pod im AWS-Cluster** (nicht lokal), gestartet über das
  Terraform-Docker-Image mit `bzt_on_pod.sh`. Lokal wird nur konfiguriert, deployt und ausgewertet.
- **Alle 5 Runs müssen mit demselben Toolkit-Code/-Version laufen.** Nicht mitten in der Serie mergen.
- **Region immer `us-east-2`** (Snapshots liegen dort). Nicht ändern.
- Zwischen den Runs ändert sich nur: App installiert? / `standalone_extension*` > 0? / `confluence_replica_count`.

## 1. Run-Matrix

| Run | Nodes (`confluence_replica_count`) | App installiert | App-Actions (`standalone_extension*`) | Zweck |
|-----|-----|-----|-----|-------|
| **Run 1** | 1 | **Nein** | 0 | Performance-Baseline ohne App |
| **Run 2** | 1 | **Ja** | 0 | Performance mit App (ohne Custom-Actions) → Vergleich zu Run 1 |
| **Run 3** | 1 | Ja | **>0** | Scalability-Baseline 1 Node mit App-Actions |
| **Run 4** | 2 | Ja | >0 | Scalability 2 Nodes |
| **Run 5** | 4 | Ja | >0 | Scalability 4 Nodes |

- **Regression-Report** vergleicht Run 1 vs Run 2 (`performance_profile.yml`).
- **Scale-Report** vergleicht Run 3/4/5 (`scale_profile.yml`).

## 2. Voraussetzungen (einmalig)

- **AWS vCPU-Limit:** min. 40, empfohlen 50 vCPU (On-Demand Standard, us-east-2). Ggf. Quota-Increase.
- **Kosten:** 1 Node ~$1–2/h, 2 Nodes ~$1,5–2/h, 4 Nodes ~$2–3/h. **Nach Tests sofort terminieren!**
- **Lokales Tooling** (für Auswertung/Config): Python 3.9–3.13 venv + `pip install -r requirements.txt`,
  Docker. (JDK/Chrome nur für lokale Läufe nötig, nicht für den Pod-Lauf.)
- **AWS-Credentials:** per 1Password holen → schreibt `app/util/k8s/aws_envs`:
  ```bash
  bash smartics/fetch_aws_credentials.sh   # holt Vault "service"/Item "AWS-DCPT-TOKEN", testet mit sts
  ```
- **Confluence-Lizenz:** per 1Password holen → schreibt `dcapt.tfvars` (einzeilig normalisiert):
  ```bash
  bash smartics/fetch_confluence_license.sh   # Vault "service"/Item "Confluence DC Lizenz"/Feld reg_code
  ```
  Timebomb-Lizenzen laufen ab! Neue erzeugen unter
  https://developer.atlassian.com/platform/marketplace/timebomb-licenses-for-testing-data-center-apps/
  und in 1Password aktualisieren. `dcapt.tfvars` ist git-getrackt → Lizenz-Änderung **nicht committen**.
- **`app/util/k8s/dcapt.tfvars`** prüfen: `environment_name` (aktuell `dcapt-confluence-e1`),
  `products = ["confluence"]`, `region = "us-east-2"`, `confluence_version_tag = "10.2.2"`,
  **`confluence_replica_count = 1`** (für Run 1!).

## 3. Cluster provisionieren (vor Run 1)

```bash
cd app/util/k8s
# 1) confluence_replica_count = 1 in dcapt.tfvars setzen
# 2) frische Creds
bash ../../../smartics/fetch_aws_credentials.sh
# 3) Install (~40 min)
docker run --pull=always --env-file aws_envs \
  -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
  -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
  -v "/$PWD/logs:/data-center-terraform/logs" \
  -it atlassianlabs/terraform:2.9.23 ./install.sh -c conf.tfvars
```
Aus der Konsolenausgabe die **Product-URL** kopieren (Format
`http://a1234-54321.us-east-2.elb.amazonaws.com/confluence`) und in `app/confluence.yml` eintragen:
`application_hostname` (ohne Protokoll/Port), `application_protocol: http`, `application_port: 80`,
`application_postfix: /confluence`. Login: `admin` / `admin`.

## 4. Einen Run ausführen (identisch für Run 1–5)

```bash
# aus dem Repo-Root
export ENVIRONMENT_NAME=dcapt-confluence-e1
docker run --pull=always --env-file ./app/util/k8s/aws_envs \
  -e REGION=us-east-2 \
  -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
  -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
  -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
  -it atlassianlabs/terraform:2.9.23 bash bzt_on_pod.sh confluence.yml
```
Dauer ~50 min. Ergebnisse landen unter `app/results/confluence/<YYYY-MM-DD_hh-mm-ss>/`.
**Nach jedem Run:** Ergebnisordner umbenennen/kopieren (z. B. `RUN1`, `RUN2`, …), damit er nicht
verwechselt wird.

### Was sich pro Run ändert
- **Vor Run 2:** App(s) in Confluence installieren + lizenzieren. `standalone_extension*` bleibt 0.
- **Vor Run 3:** `standalone_extension*` in `confluence.yml` > 0 setzen (siehe §6), App-Actions
  einkommentiert. `confluence_replica_count` bleibt 1.
- **Vor Run 4:** hochskalieren auf 2 (siehe §5).
- **Vor Run 5:** hochskalieren auf 4.

## 5. Hochskalieren (vor Run 4 und Run 5)

```bash
cd app/util/k8s
# dcapt.tfvars: confluence_replica_count = 2   (bzw. = 4 vor Run 5)
docker run --pull=always --env-file aws_envs \
  -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
  -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
  -v "/$PWD/logs:/data-center-terraform/logs" \
  -it atlassianlabs/terraform:2.9.23 ./install.sh -c conf.tfvars
# ~20 min pro Skalierung warten (Cluster-Stabilisierung)
```

## 6. Smartics-Spezifika (welche Apps, Actions, Testdaten)

Getestete Apps (Kürzel → Marketplace):
`smartics-us` (Userscripts), `smartics-dm` (Documentation Macros), `smartics-pd` (projectdoc Toolbox),
`smartics-is` (Information System), `smartics-wa` (Web API), `smartics-bp` (Blueprints).

**Abhängigkeit:** projectdoc Toolbox ⊃ Documentation Macros. Tests werden **nacheinander pro App**
(oder App-Gruppe) gefahren; je Lauf `standalone_extension*` in `app/confluence.yml` anpassen.

**App-Action-Verdrahtung (bereits im Branch vorhanden):**
- Locust-Actions: `app/extension/confluence/extension_locust.py`
- Selenium-Actions: `app/extension/confluence/extension_ui.py`
- Aktivierung Locust: `app/locustio/confluence/locustfile.py` (Task einkommentieren)
- Aktivierung Selenium: `app/selenium_ui/confluence_ui.py` (Test einkommentieren)
- Prozentsteuerung: Keys `standalone_extension_*` in `app/confluence.yml`

**Aktuelle Konfiguration (Branch `smartics-dcapt-2026-all`): „alle Apps außer DM" aktiv**
US/PD/IS/WA/BP = 6, DM = 0. Für andere App-Kombis diese Keys umstellen.

**KRITISCHE Testdaten-Voraussetzungen auf der Instanz** (der Setup-Skript legt nur `DCAPTUC` +
`MoreProjectdocUC` an — der Rest muss manuell erstellt / IDs angepasst werden):
- **Plugins installieren:** `smartics-us`, `smartics-pd`, `smartics-is` (je nach Lauf).
- **US:** Seite mit konfiguriertem Userscript; `TC_US_PAGEID` + `TC_US_EXPECTED_SCRIPT_NAME`
  (in `extension_locust.py`) auf reale Werte setzen. Für US-Selenium `custom_dataset_query`
  (`confluence.yml`) auf die US-Seite zeigen lassen.
- **PD:** Seiten `Test Case Display Table` (Assertion „List of Documents") und
  `Test Case Transclude from Documents` (Assertion „Transclusion from Documents") im Space `DCAPTUC`.
- **IS:** Seite `Test Case Informationsystemtest` (Assertion `informationsystem-test-case-id`).
- **WA:** projectdoc-Dokument `[projectdoc Space for Test Cases]` im Space `DCAPTUC`.
- **BP:** Space `BLUEPRINT` + Parent-Seite; `BLUEPRINT_LOCATION` (in `extension_locust.py`) anpassen.
  Data-Prep erzeugt dann `datasets/confluence/blueprint_pages.json`.
- **Setup-Skript:** `python smartics/setup_confluence_spaces.py` (nutzt `smartics/.env`).
- **Smoke-Test:** vor dem 45-min-Lauf jeden aktivierten Endpoint einmal manuell prüfen (curl/Browser).

## 7. Reports generieren

**Regression (Run 1 vs 2):** `app/reports_generation/performance_profile.yml` mit den Pfaden zu
Run 1 (`without app`) und Run 2 (`with app`) füllen, dann:
```bash
docker run --pull=always -v "/$PWD:/dc-app-performance-toolkit" \
  --workdir="//dc-app-performance-toolkit/app/reports_generation" \
  --entrypoint="python" -it atlassian/dcapt csv_chart_generator.py performance_profile.yml
```
**Scale (Run 3/4/5):** `app/reports_generation/scale_profile.yml` mit 1/2/4-Node-Pfaden füllen, dann
denselben Docker-Aufruf mit `scale_profile.yml`.
Output: `app/results/reports/<ts>/` (`*.csv`, `*.png`, `*_summary.log`).

**Smartics-Report (optional):** `python convert-to-projectdoc-json.py <location_id> [result_name]`
(braucht `SMARTICS_DOC_SYSTEM_*` / `SMARTICS_TEST_SYSTEM_*` in `.env`).

## 8. Erfolgskriterien

- Erfolgsrate **≥ 95 %** je Action (`results_summary.log`); keine Action mit 0 %.
- Fehlerrate **< 25 %** (sonst Abbruch).
- Performance-Impact / Scale-Delta **< 20 %** je Action.

## 9. Terminieren (IMMER nach den Tests — Kosten!)

```bash
cd app/util/k8s
bash ../../../smartics/fetch_aws_credentials.sh
docker run --pull=always --env-file aws_envs \
  -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
  -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
  -v "/$PWD/logs:/data-center-terraform/logs" \
  -it atlassianlabs/terraform:2.9.23 ./uninstall.sh -c conf.tfvars
```
Falls uninstall hängt: Force-Terminate via `terminate_cluster.py` (siehe CLAUDE.md „AWS Cluster
Management"). Danach mit AWS-CLI prüfen: `aws eks list-clusters --region us-east-2` → `[]`,
keine RDS/ELB/EC2 mehr.

## 10. Jährliche Wiederholung — Checkliste

1. Upstream mergen: `git fetch upstream && git merge upstream/master` (Konflikte i. d. R. nur
   `confluence.yml`, `dcapt.tfvars`, `requirements.txt` — Tooling von upstream, Smartics-Config behalten).
2. Versionen prüfen (README „Supported versions"): `TOOLKIT_VERSION`, `confluence_version_tag`,
   `chromedriver`, `selenium`, **Terraform-Image-Tag** (`grep -r atlassianlabs/terraform: app/util/k8s`).
3. `bash smartics/fetch_aws_credentials.sh` → aws_envs; License in `dcapt.tfvars` aktuell?
4. Testdaten/Plugins auf frischer Instanz neu anlegen (§6) — IDs sind instanzspezifisch!
5. Runs 1–5 (§3–5) mit **einer** Toolkit-Version. Ergebnisse pro Run sichern.
6. Reports (§7), Kriterien prüfen (§8), an ECOHELP/Marketplace hängen.
7. **Cluster terminieren** (§9).

> Alte, nicht in git liegende Testläufe vor dem Löschen sichern (`app/results/` ist git-ignored) —
> z. B. nach `../results-backup-<datum>/`.
