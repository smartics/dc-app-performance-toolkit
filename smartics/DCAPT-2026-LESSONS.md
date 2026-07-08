# DCAPT 2026 — Lessons Learned + Automatisierungs-Vorschläge

> Erfahrungsbericht der Testkampagne 2026-07 (Branch `smartics-dcapt-2026-all`), damit der
> nächste Lauf (in ~1 Jahr) schneller, robuster und mit weniger Handarbeit läuft.
> Ergänzt `smartics/DCAPT-RUNBOOK.md` (Ablauf) und `smartics/TESTDATA-SETUP.md` (Testdaten).

## 0. Umgebung dieser Kampagne
- DCAPT **8.10.4**, Confluence **10.2.2**, Terraform-Image **atlassianlabs/terraform:2.9.23**
- Enterprise-Dataset (~900k Seiten), Region us-east-2, `dcapt-confluence-e1`, m5.2xlarge
- Getestet: **alle Apps außer DM** (US, PD-Toolbox, WA, IS, BP = 14 Marketplace-Apps)

## 1. Wie wir jeden Schritt gemacht haben (konkret)

### 1a. Credentials aus 1Password (Service-Account)
- `smartics/.env`: `OP_SERVICE_ACCOUNT_TOKEN=ops_…` (git-ignored).
- **AWS:** `bash smartics/fetch_aws_credentials.sh` → `op read op://service/AWS-DCPT-TOKEN/username|credential`
  → schreibt `app/util/k8s/aws_envs`, verifiziert via `aws sts get-caller-identity`.
- **Lizenz:** `bash smartics/fetch_confluence_license.sh` → `op read op://service/Confluence DC Lizenz/reg_code`,
  entfernt Zeilenumbrüche, trägt `confluence_license` in `dcapt.tfvars` ein.
- Merke: `op item get --fields id=…` wird NICHT unterstützt → `op read` mit Feld-ID nutzen.

### 1b. Cluster provisionieren
- `dcapt.tfvars`: `confluence_version_tag=10.2.2`, **`confluence_replica_count=1`** (Start immer 1!),
  `confluence_installation_timeout` **auf 60 setzen** (Default 30 reicht bei 900k Seiten nicht, s. Pain Points).
- `install.sh` via Docker (Runbook §3). Danach ELB-Hostname aus der Ausgabe in `app/confluence.yml`
  (`application_hostname`) eintragen. Login admin/admin.

### 1c. Plugins herunterladen + installieren
- **Download:** `bash smartics/download_plugins.sh` → holt via Marketplace-REST-API die **neueste
  DC-Version** jeder App (.obr) nach `smartics/plugins/`. 14 Apps (PD/WA/IS/US + 10 Blueprints).
- **Installation:** `bash smartics/install_plugins.sh` → UPM-REST (Bearer-PAT aus `.token`).
  - **Cookie-Jar** hält Session/Node-Stickiness (sonst upm-token beim POST ungültig).
  - UPM-Upload-Antwort ist in `<textarea>` verpackt → vor JSON-Parse strippen.
  - **FESTE Reihenfolge + 120 s Pause zwischen den Plugins** (User-Vorgabe; Reihenfolge in der Datei).

### 1d. Lizenzen eintragen
- **Nur Userscripts + projectdoc Toolbox brauchen eine Lizenz** (Extensions/Blueprints laufen unter der
  Toolbox-Lizenz). Testkey: `smartics/plugins/lizenz.txt` (Timebomb → jährlich erneuern).
- Eintragen: UPM → *Manage apps* → jeweilige App → Lizenzschlüssel. (App-Lizenz ≠ die Confluence-Lizenz aus 1b.)

### 1e. Testdaten: Spaces importieren
- Space-Exporte liegen in `DATA/*.zip` (PROJECTDOCTEST=PD/WA/IS/DM, USTEST=US, BLUEPRINT=BP).
- Per `kubectl cp` in den Confluence-Pod ins **Shared-Home-Restore-Verzeichnis**:
  `…:/var/atlassian/application-data/shared-home/restore/space/` (NICHT lokales Home!).
- Dann Confluence-Admin → `…/confluence/admin/restore.action` → aus Dropdown importieren.

### 1f. Post-Import-PFLICHTSCHRITTE (sonst rendern Makros nicht!)
1. **Alle Seiten im Space PROJECTDOCTEST neu speichern** (inkl. Space-Home „projectdoc Space for Test
   Cases") → erst dann greift der projectdoc-Index (Display-Table/Transclude rendern, WA-Query findet Docs).
2. **Allowlist:** `https://raw.githubusercontent.com` eintragen (Confluence-Admin → Allowlist) für IS.
3. **Userscripts Client-Logging aktivieren** (Userscripts-Admin → Konfiguration → Client-Logging → Modulnamen).

### 1g. Code-Konstanten nach Import anpassen (`extension_locust.py`)
- `TESTCASE_SPACE_KEY = "PROJECTDOCTEST"`
- `TC_US_PAGEID` = neue ID der USTEST-Home (Page-IDs ändern sich beim Import!)
- `TC_US_EXPECTED_SCRIPT_NAME = "de.smartics.test/hello"` (Version inkrementiert → nur namespace/name)
- `BLUEPRINT_LOCATION` = neue ID der BLUEPRINT-Home
- WA: Query auf ein auffindbares Dokument (`DCAPT Document 1`), Assertion `assert token` (nicht `!= ""`).

### 1h. Runs 1–5
- Config-Profile in `confluence.yml`: Baseline (alle `standalone_extension*=0`) für Run 1/2/1b;
  `US/PD/WA/IS/BP=6, DM=0` für Run 3–5. US-Selenium bleibt auskommentiert (US via REST-Test abgedeckt).
- Start: `bzt_on_pod.sh confluence.yml` via Terraform-Docker → Test läuft in **tmux-Session `bzt_session`
  auf dem Exec-Pod** (`dcapt-*`), unabhängig vom lokalen Rechner.
- Ergebnisse per `kubectl cp POD:dc-app-performance-toolkit/app/results/confluence/<ts>` holen.

### 1i. Skalierung (Run 4/5)
- `confluence_replica_count` 1→2→4, `install.sh`. Neue Nodes wärmen den Index auf (dauert!).

### 1j. Reports
- `app/reports_generation/*.yml` (runName/relativePath/title) + `csv_chart_generator.py` via `atlassian/dcapt`
  → Ordner mit `.csv/.png/_summary.log` **+ Run-ZIP-Archive** (automatisch — das sind die Einreichungs-ZIPs).
- Regression = Run1/1b vs Run2; Scale = Run3/4/5. Per-App = gleiche Läufe, nur andere Titel/Namen.
- **Immer `docker chown app/results` auf den User nach Docker-Läufen** (Docker legt als root an).

## 2. Pain Points (was uns Zeit gekostet hat)
1. **`bzt_on_pod.sh`-Wrapper hängt sich von der tmux-Session ab** und meldet fälschlich „completed" +
   kopiert Results vorzeitig/leer. → Eigener kubectl-Monitor nötig; Results manuell per `kubectl cp`.
2. **Node-Warmup > Timeout:** Neuer Node (900k Seiten) wird nicht in 30 min ready → Terraform-Timeout.
   Node wird aber später von selbst `1/1`. → `confluence_installation_timeout=60` + Readiness abwarten.
3. **`app/results` root-owned** nach Docker → lokale Kopien/Reports scheitern. → auto-chown.
4. **UPM-Eigenheiten:** Cookie-Jar (Node-Stickiness), `<textarea>`-Wrapper, `--fields id=` nicht unterstützt.
5. **`uninstall.sh` fragt interaktiv** → im Hintergrund `-f` (Auto-Approve) nutzen.
6. **kubectl cp bricht sporadisch ab** („unexpected EOF") → Retry-Schleife.
7. **Viele manuelle Confluence-UI-Schritte:** Space-Import, Seiten-Neuspeichern (Index), Allowlist,
   US-Client-Logging, Lizenz-Eintrag — alles Handarbeit im Browser.
8. **Lokaler Rechner = Single Point of Failure:** Verbindungsabbruch/Shutdown killt Orchestrierung
   (Test läuft auf dem Pod weiter, aber Chaining/Monitor/Copy sterben).

## 3. Automatisierungs-Vorschlag: der „Treiber"
Ein Orchestrierungs-Skript **`smartics/dcapt_driver.sh`** (Skelett bereits angelegt), das die
**automatisierbaren** Teile end-to-end verkettet und die manuellen Gates klar ausweist:

Vollautomatisch machbar (im Treiber):
- `fetch_aws_credentials.sh` + `fetch_confluence_license.sh`
- `install.sh` (provision/scale) inkl. **Warten auf alle Nodes `1/1`** (statt Terraform-Timeout blind)
- Config-Profil in `confluence.yml` setzen (Baseline vs Run3-5) per sed/python
- `download_plugins.sh` + `install_plugins.sh`
- Einen Run fahren = bzt_on_pod **starten + selbst per kubectl überwachen** (Auto-Abort) + Results per cp holen
- Reports generieren (alle Profile) + `chown` + ZIP-Bündel
- `uninstall.sh -f`

Bleibt (vorerst) manuell — mit Automatisierungs-Ideen:
- **Space-Import** (UI restore.action). *Idee:* Confluence hat keine saubere Space-Import-REST; aber die
  Datei liegt schon im restore/space-Dir → evtl. per `long-running-task`-REST triggerbar (zu prüfen).
- **Seiten-Neuspeichern für Index.** *Idee:* per REST alle PROJECTDOCTEST-Seiten `PUT` mit version+1
  (Body unverändert) → erzwingt Reindex ohne UI. **Guter Automatisierungs-Kandidat.**
- **Allowlist-Eintrag.** *Idee:* Confluence hat eine Allowlist-REST (`/rest/whitelist/…` bzw.
  `/rest/api/settings`) → automatisierbar.
- **US-Client-Logging + Lizenz-Eintrag.** App-Konfiguration; ggf. REST der jeweiligen App (zu recherchieren).

## 4. Konkrete Verbesserungsvorschläge (priorisiert)
1. **Treiber in `tmux`/`nohup` auf dem Rechner laufen lassen** → überlebt Verbindungsabbruch/Logout
   (die ganze Kampagne läuft durch, auch wenn das Terminal weg ist). *Größter Robustheitsgewinn.*
2. **Monitor-Pattern fest in den Treiber** (kubectl `tmux has-session`/`capture-pane`, Auto-Abort 25 %),
   den kaputten Wrapper-Attach ignorieren. Zusätzlich `passfail`-Kriterium in `confluence.yml` (haben wir).
3. **`confluence_installation_timeout=60`** dauerhaft in `dcapt.tfvars` (Node-Warmup).
4. **Reindex per REST** statt manuellem Seiten-Neuspeichern (s. 3) — spart den lästigsten Handarbeits-Schritt.
5. **Idempotente Helfer** (haben wir: fetch_*, download_/install_/toggle_plugins) beibehalten + im Treiber nutzen.
6. **Ein `dcapt-snapshots.json` mit vorbereiteten Testdaten-Spaces** (falls Atlassian das erlaubt) würde den
   ganzen Import + Post-Import-Schritt sparen — prüfen, ob ein Custom-Snapshot mit PROJECTDOCTEST/USTEST/
   BLUEPRINT möglich ist. *Höchster Zeitgewinn, aber Aufwand/Abklärung nötig.*
7. **`confluence.yml`-Hostname automatisch** aus dem `install.sh`-Output ziehen (statt manuell eintragen).
8. **Kosten-Guard:** Treiber terminiert am Ende automatisch (`uninstall.sh -f`) — nichts vergessen.

## 5. Wiederverwendbare Assets (dieses Jahr gebaut)
| Datei | Zweck |
|-------|-------|
| `smartics/fetch_aws_credentials.sh` | AWS-Creds aus 1Password → aws_envs |
| `smartics/fetch_confluence_license.sh` | Confluence-Lizenz aus 1Password → dcapt.tfvars |
| `smartics/download_plugins.sh` | neueste DC-Versionen aller Apps (.obr) laden |
| `smartics/install_plugins.sh` | Apps per UPM-REST installieren (Reihenfolge + 120 s) |
| `smartics/toggle_plugins.sh` | Apps enable/disable (für Kontroll-Läufe) |
| `smartics/wa_test.sh` | WA-REST-Query diagnostizieren |
| `smartics/dcapt_driver.sh` | **NEU:** Orchestrierungs-Treiber (Skelett) |
| `smartics/DCAPT-RUNBOOK.md` | Schritt-für-Schritt Runs 1–5 |
| `smartics/TESTDATA-SETUP.md` | Testdaten je App + Post-Import |
