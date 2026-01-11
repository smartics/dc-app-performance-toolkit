# DCAPT Execution Guide - Confluence Enterprise Tests

> Dokumentation für DCAPT Instructor Skill
> Letzte Aktualisierung: 2026-01-09

## Übersicht

Dieser Guide führt durch die komplette Ausführung von DCAPT Enterprise Performance Tests für Confluence Data Center Apps (speziell: Documentation Macros von smartics).

## Test-Szenario: Performance Regression Testing

**Ziel:** Messen der Performance-Auswirkung einer installierten App

### Test-Runs Übersicht

| Run | Beschreibung | App Status | Extension Actions | Zweck |
|-----|-------------|------------|-------------------|-------|
| RUN 1 | Baseline | Nicht installiert | Alle auf 0 | Referenz-Performance ohne App |
| RUN 2 | Mit App | Installiert | Alle auf 0 | Passive Performance-Auswirkung der App |
| RUN 3-5 | Scalability | Installiert | Aktiviert (6%) | App-Features unter Last (optional) |

**Erfolgskriterium RUN 1 vs RUN 2:** Performance-Verschlechterung < 20%

---

## Voraussetzungen

### System
- Python 3.9-3.13 mit pip
- JDK 17 oder 21
- Google Chrome
- Docker (für AWS Deployment)
- Git

### AWS Infrastruktur
- Confluence Data Center Instance (AWS)
- Enterprise Dataset (~900k Seiten)
- Load Balancer URL
- `aws_envs` Datei mit Credentials

### Repository
```bash
cd /home/anton/DCPT/dc-app-performance-toolkit
```

---

## Phase 1: Vorbereitung

### 1.1 Repository-Status prüfen
```bash
git status
git branch
```

Aktueller Branch: `smartics-dcapt-2025-all`

### 1.2 Confluence.yml Konfiguration

**Wichtige Parameter für Enterprise Tests:**

```yaml
settings:
  env:
    application_hostname: a98e3638710f1468ab64b50cd0b93d33-1489266278.us-east-2.elb.amazonaws.com
    application_protocol: http
    application_port: 80
    application_postfix: /confluence
    admin_login: admin
    admin_password: admin
    load_executor: locust
    concurrency: 200              # Enterprise
    test_duration: 45m            # Enterprise
    ramp-up: 5m
    total_actions_per_hour: 20000
```

### 1.3 ChromeDriver Version anpassen

**Problem:** Docker Container hat Chrome 142, lokale Tests nutzen Chrome 143

**Lösung in confluence.yml:**
```yaml
selenium:
  chromedriver:
    version: "142.0.7444.134"  # AWS/Docker - Chrome 142
    # version: "143.0.7499.192"  # WINDOWS - Chrome 143
```

**Regel:**
- Für AWS/Docker-Tests: Chrome 142 Version aktiv
- Für lokale Windows-Tests: Chrome 143 Version aktiv (auskommentiert belassen)

### 1.4 Custom Dataset Query deaktivieren (RUN 1 & 2)

**Problem:** Enterprise System hat keine Custom Pages für Smartics-Tests

**Lösung für RUN 1 & 2:**
```yaml
# Custom dataset section.
# RUN 1 & 2: Custom dataset deaktiviert (keine Extension Actions)
# RUN 3-5: Aktivieren mit: custom_dataset_query: title ~ 'MoreProjectdocUC'
custom_dataset_query:  # Leer lassen für RUN 1 & 2
```

**Für RUN 3-5:** Query aktivieren, nachdem Custom Pages erstellt wurden

### 1.5 Extension Actions Konfiguration

**Für RUN 1 & 2 (Performance Regression):**
```yaml
standalone_extension: 0
standalone_extension_us_rest_content: 0
standalone_extension_section: 0              # DM
standalone_extension_hide: 0                 # DM
standalone_extension_hidefromreader: 0       # DM
standalone_extension_hidefromanonymous: 0    # DM
standalone_extension_definitionlist: 0       # DM
standalone_extension_transclude_documents: 0 # Toolbox
standalone_extension_display_table: 0        # Toolbox
standalone_extension_web_api: 0              # Toolbox
standalone_extension_information_system: 0   # IS
standalone_extension_blueprints: 0           # BP
```

**Für RUN 3-5:** DM-Actions auf 6 setzen (section, hide, hidefromreader, hidefromanonymous, definitionlist)

---

## Phase 2: RUN 1 - Baseline (ohne App)

### 2.1 Vorbedingungen prüfen
- [ ] Confluence läuft auf AWS
- [ ] **Keine** Apps installiert (außer System-Apps)
- [ ] confluence.yml konfiguriert (ChromeDriver, custom_dataset_query leer)
- [ ] aws_envs Datei vorhanden

### 2.2 Test starten

```bash
cd C:\p\dc-app-performance-toolkit

export ENVIRONMENT_NAME=dcapt-confluence-e1

docker run --pull=always --env-file ./app/util/k8s/aws_envs \
  -e REGION=us-east-2 \
  -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
  -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
  -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
  -it atlassianlabs/terraform:2.9.12 bash bzt_on_pod.sh confluence.yml
```

**Erwartete Dauer:** ~50 Minuten

### 2.3 Link erstellen

Nach Abschluss (neuestes Verzeichnis ermitteln):
```bash
ls -lt app/results/confluence/ | head -5
ln -s 2026-01-09_XX-XX-XX app/results/confluence/RUN1_DM
```

### 2.4 Erfolg prüfen

```bash
# Log-Ende prüfen
tail -20 app/results/confluence/RUN1_DM/bzt.log

# Zusammenfassung anzeigen
cat app/results/confluence/RUN1_DM/results_summary.log
```

**Erfolgskriterien:**
- Exit Code: 0
- Summary run status: OK
- Success Rate: >= 95% (besser 100%)
- Finished: True, OK
- Compliant: True, OK

**RUN 1 Ergebnis (2026-01-09):**
- ✓ Exit Code 0
- ✓ Success Rate: 100%
- ✓ Test Duration: 3013 sec (50 Min)
- ✓ Dataset: 906,367 pages
- ✓ Concurrency: 200 users
- ✓ All actions: 0.0% Error Rate

---

## Phase 3: RUN 2 - Mit App installiert

### 3.1 Documentation Macros App installieren

**Auf AWS Confluence:**
1. Als Admin einloggen: http://a98e3638710f1468ab64b50cd0b93d33-1489266278.us-east-2.elb.amazonaws.com:80/confluence
2. **⚙️ Settings** → **Manage apps**
3. **Find new apps**
4. Suche: **"Documentation Macros by smartics"**
5. **Install** (Trial-Lizenz)
6. Warten bis Status: "Installed and ready to go"

**Wichtig:** App-Lizenz prüfen (Trial: 30 Tage)

### 3.2 Konfiguration prüfen

**Die confluence.yml bleibt UNVERÄNDERT:**
- Extension Actions: Alle auf 0
- custom_dataset_query: Leer
- ChromeDriver: 142.0.7444.134

**Warum bleiben Actions auf 0?**
RUN 2 misst die **passive Performance-Auswirkung** der installierten App ohne aktive Nutzung der App-Features.

### 3.3 Test starten

**Gleicher Befehl wie RUN 1:**
```bash
cd C:\p\dc-app-performance-toolkit

export ENVIRONMENT_NAME=dcapt-confluence-e1

docker run --pull=always --env-file ./app/util/k8s/aws_envs \
  -e REGION=us-east-2 \
  -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
  -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
  -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
  -it atlassianlabs/terraform:2.9.12 bash bzt_on_pod.sh confluence.yml
```

### 3.4 Link erstellen
```bash
ln -s 2026-01-09_XX-XX-XX app/results/confluence/RUN2_DM
```

### 3.5 Ergebnisse vergleichen

**Performance-Vergleich RUN1 vs RUN2:**
```bash
# Response Times vergleichen
grep "selenium_view_page " app/results/confluence/RUN1_DM/results.csv
grep "selenium_view_page " app/results/confluence/RUN2_DM/results.csv

# Zusammenfassungen nebeneinander
cat app/results/confluence/RUN1_DM/results_summary.log
cat app/results/confluence/RUN2_DM/results_summary.log
```

**Erfolgskriterium:**
Performance-Verschlechterung < 20% bei allen Actions

**Berechnung:**
```
Verschlechterung (%) = ((RUN2_Zeit - RUN1_Zeit) / RUN1_Zeit) × 100
```

Beispiel:
- RUN1 View Page: 1.02s (90th Percentile)
- RUN2 View Page: 1.15s
- Verschlechterung: ((1.15 - 1.02) / 1.02) × 100 = 12.7% ✓ OK

---

## Phase 4: RUN 3-5 - Scalability Tests (optional)

### 4.1 Custom Pages erstellen

**Voraussetzung:** Space DCAPTUC mit MoreProjectdocUC-Seiten erstellen

```bash
# Setup-Script ausführen (falls vorhanden)
python smartics/setup_confluence_spaces.py --skip-dcapt
```

### 4.2 Konfiguration anpassen

**Extension Actions aktivieren:**
```yaml
standalone_extension_section: 6              # DM
standalone_extension_hide: 6                 # DM
standalone_extension_hidefromreader: 6       # DM
standalone_extension_hidefromanonymous: 6    # DM
standalone_extension_definitionlist: 6       # DM
```

**Custom Dataset aktivieren:**
```yaml
custom_dataset_query: title ~ 'MoreProjectdocUC'
```

### 4.3 Tests durchführen
- RUN 3: 1-Node Cluster
- RUN 4: 2-Node Cluster (AWS Scaling)
- RUN 5: 4-Node Cluster (AWS Scaling)

---

## Häufige Probleme & Lösungen

### Problem 1: ChromeDriver Version Mismatch
**Symptom:**
```
ERROR: Your Chromedriver version 143.0.7499.192 is not corresponding to your Chrome browser version 142.0.7444.134
```

**Lösung:**
confluence.yml anpassen - erste Zahl muss übereinstimmen (142 = 142)

### Problem 2: Custom Pages nicht gefunden
**Symptom:**
```
Exception: Content with cql 'title ~ 'MoreProjectdocUC'' not found.
```

**Lösung:**
Für RUN 1 & 2: `custom_dataset_query:` leer lassen (ohne Wert)

### Problem 3: Test bricht sofort ab
**Diagnose:**
```bash
tail -50 app/results/confluence/<timestamp>/bzt.log
```

Häufige Ursachen:
- ChromeDriver Version
- Custom Dataset Query
- Confluence nicht erreichbar
- Falsche Credentials

### Problem 4: Niedrige Success Rate
**Symptom:** Success Rate < 95%

**Ursachen:**
- Confluence überlastet
- Netzwerk-Timeouts
- Datenbankprobleme

**Lösung:** Test wiederholen, ggf. concurrency reduzieren

---

## Checkliste: Vor jedem Test-Run

- [ ] Confluence erreichbar und läuft stabil
- [ ] Richtige App-Version installiert (für RUN 2+)
- [ ] confluence.yml korrekt konfiguriert
  - [ ] ChromeDriver Version passt zur Umgebung
  - [ ] custom_dataset_query korrekt (leer für RUN 1&2)
  - [ ] Extension Actions korrekt (0 für RUN 1&2, 6 für RUN 3-5)
- [ ] aws_envs Datei vorhanden
- [ ] Genügend Zeit eingeplant (~50-60 Min pro Run)
- [ ] Vorheriger Run erfolgreich abgeschlossen

---

## Wichtige Dateien & Verzeichnisse

```
dc-app-performance-toolkit/
├── app/
│   ├── confluence.yml                  # Hauptkonfiguration
│   ├── results/confluence/             # Test-Ergebnisse
│   │   ├── RUN1_DM -> 2026-01-09_XX    # Symlink zu RUN 1
│   │   ├── RUN2_DM -> 2026-01-09_YY    # Symlink zu RUN 2
│   │   └── 2026-01-09_XX-XX-XX/        # Timestamp-Verzeichnisse
│   │       ├── bzt.log                 # Haupt-Logfile
│   │       ├── results_summary.log     # Zusammenfassung
│   │       ├── results.csv             # Detaillierte Metriken
│   │       ├── kpi.jtl                 # Locust Rohdaten
│   │       └── selenium.jtl            # Selenium Rohdaten
│   ├── util/k8s/
│   │   ├── aws_envs                    # AWS Credentials & Config
│   │   └── bzt_on_pod.sh              # Execution Script
│   └── extension/confluence/
│       ├── extension_locust.py         # App-spezifische Locust-Actions
│       └── extension_ui.py             # App-spezifische Selenium-Actions
├── CLAUDE.md                           # Confluence DCAPT Dokumentation
└── Execute-DCAPT.md                    # Dieser Guide
```

---

## Nächste Schritte für Skill-Entwicklung

**Der "DCAPT Instructor" Skill sollte:**

1. **Interaktive Führung:** Schritt-für-Schritt durch jeden Test-Run
2. **Status-Checks:** Automatisches Prüfen von Vorbedingungen
3. **Konfigurationshilfe:** confluence.yml validieren und anpassen
4. **Fehlerdiagnose:** Logs analysieren und Lösungen vorschlagen
5. **Ergebnis-Vergleich:** RUN1 vs RUN2 Performance automatisch vergleichen
6. **Checklisten:** Interaktive Checklisten mit Haken-System

**Skill-Funktionen:**
- `/dcapt-start` - Guide starten
- `/dcapt-check` - Konfiguration prüfen
- `/dcapt-status` - Test-Status überwachen
- `/dcapt-compare` - Runs vergleichen
- `/dcapt-troubleshoot` - Fehlerdiagnose

---

## Referenzen

- [DCAPT User Guide Confluence](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-confluence/)
- [Atlassian Marketplace Requirements](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/)
- [Slack Support](https://community.atlassian.com) - #data-center-app-performance-toolkit

---

**Dokumentiert von:** Claude (2026-01-09)
**Für:** Smartics Documentation Macros Performance Testing
**Test-Instanz:** https://c10dcapt.smartics.eu (AWS)
