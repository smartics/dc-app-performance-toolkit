# DC App Performance Toolkit (DCAPT) - Confluence Zusammenfassung

> **WICHTIG: Alle Fragen und Arbeiten beziehen sich ausschließlich auf Confluence Data Center!**
> **NICHT auf Jira, Bamboo, Bitbucket oder andere Atlassian-Produkte!**

> **COMMIT-REGEL: Keine Claude Code Branding/Werbung in Commit-Messages!**
> Kein "🤖 Generated with Claude Code", kein "Co-Authored-By: Claude"

---

## Smartics Marketplace Apps & Teststrategie

### Apps im Atlassian Marketplace

| App | Kürzel | Status |
|-----|--------|--------|
| Documentation Macros | DM, smartics-dm | **AKTUELL** - Tests werden jetzt durchgeführt |
| projectdoc Toolbox | Toolbox, smartics-pd | Geplant in 2-3 Monaten |
| Information System | IS, smartics-is | - |
| Blueprints | BP, smartics-bp | - |
| Userscripts | US, smartics-us | - |

### Wichtige Abhängigkeit

```
projectdoc Toolbox ⊃ Documentation Macros

- DM-Tests → können für BEIDE Apps verwendet werden (DM und Toolbox)
- Toolbox-Tests → können NUR für Toolbox verwendet werden (NICHT für DM)
```

Die projectdoc Toolbox enthält alle Funktionen der Documentation Macros plus zusätzliche Features.

### Teststrategie

- **EIN Branch** für alle App-Tests (kein mehrfaches Auschecken)
- Tests werden **nacheinander** für einzelne Apps durchgeführt
- Konfiguration wird je nach zu testender App angepasst
- Aktueller Branch: `smartics-dcapt-2025-all`

### Confluence Spaces

| Space Key | Zweck |
|-----------|-------|
| `DCAPT` | Standard-Testseiten für Atlassian Performance Tests (100 Seiten) |
| `DCAPTUC` | Use-Case-Seiten für Smartics App-Tests (DM, Toolbox, IS, BP, US) |

**Test-Instanz:** `https://c10dcapt.smartics.eu`

**Setup-Script:** `smartics/setup_confluence_spaces.py`

### Credentials

Credentials werden in `smartics/.env` gespeichert (nicht committed):

```bash
# Template kopieren
cp smartics/.env.template smartics/.env
# Dann .env editieren
```

Inhalt von `smartics/.env`:
```
CONFLUENCE_URL=https://c10dcapt.smartics.eu
CONFLUENCE_USER=admin
CONFLUENCE_TOKEN=<personal_access_token>
```

### Setup ausführen

```bash
# Mit python-dotenv (liest .env automatisch)
pip install python-dotenv
python smartics/setup_confluence_spaces.py

# Oder mit expliziten Parametern
python smartics/setup_confluence_spaces.py --token <TOKEN>

# Optionen
--skip-dcapt      # Nur Use-Case Space erstellen
--skip-usecase    # Nur DCAPT Space erstellen
--pages 50        # Anzahl Testseiten (default: 100)
--pages-folder ./pages  # Seiten aus Storage-Format-Dateien laden
```

### Blueprint-Steuerung (gelöst)

Ein Schalter in `confluence.yml` steuert **beides** - Setup und Locust-Task:

```yaml
standalone_extension_blueprints: 0   # Deaktiviert: kein Setup, kein Task
standalone_extension_blueprints: 6   # Aktiviert: Setup + Task mit 6%
```

| Wert | Data Preparation | Locust-Task |
|------|------------------|-------------|
| `0` | Übersprungen | Übersprungen |
| `>0` | Ausgeführt | Ausgeführt |

---

## Zweck

Das DCAPT ist Atlassians offizielles Tool zum Performance- und Skalierungstesten von Confluence Data Center Apps. Es wird verwendet um:
- Performance-Regression zu messen (Baseline vs. App installiert)
- Skalierungstests durchzuführen (1, 2, 4 Nodes)
- Marketplace-Zertifizierung zu erlangen

## Unterstützte Confluence-Versionen

- LTS: `8.5.27`, `9.2.9`
- Platform Release: `10.0.3`

---

## Projektstruktur (Confluence-relevant)

```
app/
├── confluence.yml                    # Hauptkonfiguration
├── extension/confluence/
│   ├── extension_locust.py          # App-spezifische Locust-Actions
│   └── extension_ui.py              # App-spezifische Selenium-Actions
├── selenium_ui/
│   ├── confluence_ui.py             # Selenium Test-Suite
│   └── confluence/
│       ├── modules.py               # Selenium-Module (Login, View, etc.)
│       └── pages/
│           ├── pages.py             # Page Objects
│           └── selectors.py         # CSS/XPath Selektoren
├── locustio/confluence/
│   ├── locustfile.py                # Locust User-Verhalten
│   ├── http_actions.py              # HTTP-Aktionen
│   └── requests_params.py           # Request-Parameter
├── jmeter/
│   └── confluence.jmx               # JMeter Test-Plan
├── util/
│   └── data_preparation/
│       └── confluence_prepare_data.py  # Datenvorbereitung
├── datasets/confluence/             # Generierte Testdaten
│   ├── users.csv
│   ├── pages.csv
│   ├── blogs.csv
│   ├── custom_pages.csv
│   └── blueprint_pages.json         # Smartics Blueprint-Seiten
└── results/confluence/              # Testergebnisse
```

---

## Konfiguration (confluence.yml)

### Wichtige Parameter

| Parameter | Dev-Wert | Enterprise-Wert | Beschreibung |
|-----------|----------|-----------------|--------------|
| `application_hostname` | - | - | Server ohne Protokoll |
| `application_protocol` | http/https | http/https | Protokoll |
| `application_port` | 80/443/8080 | 80/443 | Port |
| `application_postfix` | /confluence | /confluence | URL-Suffix |
| `admin_login` | admin | admin | Admin-Benutzer |
| `admin_password` | admin | admin | Admin-Passwort |
| `load_executor` | locust | locust/jmeter | Test-Framework |
| `concurrency` | 2 | 200 | Parallele User |
| `test_duration` | 5m | 45m | Testdauer |
| `ramp-up` | 5m | 5m | Hochfahrzeit |

### Action-Verteilung (Prozent)

```yaml
view_page: 33
view_dashboard: 10
view_blog: 13
search_cql: 4
create_blog: 5
create_and_edit_page: 9
comment_page: 8
view_attachment: 6
upload_attachment: 7
like_page: 3
upload_emoticon: 4
standalone_extension: 5  # App-spezifische Actions
```

---

## Testausführung

### Voraussetzungen

1. Python 3.9-3.13 mit pip
2. JDK 17 oder 21
3. Google Chrome (passend zur chromedriver Version)
4. Virtual Environment eingerichtet

### Befehle

```bash
# Virtual Environment aktivieren (Windows)
.\venv\Scripts\activate

# Virtual Environment aktivieren (Linux/Mac)
source venv/bin/activate

# Test ausführen
cd app
bzt confluence.yml

# Nur Datenvorbereitung
python util/data_preparation/confluence_prepare_data.py

# JMeter UI starten (für manuelle Tests)
python util/jmeter/start_jmeter_ui.py --app confluence
```

---

## Testszenarien

### Szenario 1: Performance Regression
1. **Run 1 (Baseline)**: Confluence ohne App
2. **Run 2**: Confluence mit installierter App
3. Vergleich: <20% Timing-Differenz akzeptabel

### Szenario 2: Skalierung
1. **Run 3**: 1-Node mit App
2. **Run 4**: 2-Node Cluster
3. **Run 5**: 4-Node Cluster

---

## App-spezifische Actions entwickeln

### Locust (API-Tests) - extension_locust.py

```python
from locustio.common_utils import confluence_measure, run_as_specific_user

@confluence_measure("locust_my_action")
def my_action(locust):
    response = locust.get('/rest/my-app/1/endpoint', catch_response=True)
    content = response.content.decode('utf-8')
    assert 'expected_string' in content
```

### Selenium (UI-Tests) - extension_ui.py

```python
from selenium_ui.conftest import print_timing
from selenium_ui.base_page import BasePage

@print_timing("selenium_my_action")
def my_action(webdriver, datasets):
    page = BasePage(webdriver)
    page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/my/page")
    page.wait_until_visible((By.ID, "my-element"))
```

### Action in confluence_ui.py aktivieren

```python
from extension.confluence import extension_ui

def test_1_selenium_my_action(confluence_webdriver, confluence_datasets, confluence_screen_shots):
    extension_ui.my_action(confluence_webdriver, confluence_datasets)
```

### Action in locustfile.py aktivieren

```python
from extension.confluence.extension_locust import my_action

class ConfluenceBehavior(MyBaseTaskSet):
    @task(config.percentage('standalone_extension'))
    def custom_action(self):
        my_action(self)
```

---

## Smartics-spezifische Erweiterungen

Dieses Repository enthält Smartics-spezifische Tests für:

### Produkte
- **smartics-us**: Userscripts for Confluence
- **smartics-dm**: Documentation Macros
- **smartics-pd**: ProjectDoc Toolbox
- **smartics-is**: Information System Extension
- **smartics-wa**: Web API
- **smartics-bp**: Blueprints

### Konfigurierte Actions (confluence.yml)

```yaml
standalone_extension_us_rest_content: 5
standalone_extension_section: 6
standalone_extension_hide: 6
standalone_extension_hidefromreader: 6
standalone_extension_hidefromanonymous: 6
standalone_extension_definitionlist: 6
standalone_extension_transclude_documents: 6
standalone_extension_display_table: 6
standalone_extension_web_api: 6
standalone_extension_information_system: 6
standalone_extension_blueprints: 6
```

### Test-Konstanten (extension_locust.py)

```python
TESTCASE_SPACE_KEY = "PROJECTDOCTEST"
TC_DISPLAY_TABLE = "Test Case Display Table"
TC_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"
TC_INFORMATIONSYSTEM_TEST = "Test+Case+Informationsystemtest"
BLUEPRINT_SPACEKEY = "BLUEPRINT"
BLUEPRINT_LOCATION = "47596907"
```

---

## Custom Dataset

Für app-spezifische Tests:

1. Seiten mit spezifischem Präfix erstellen (z.B. "Test Case")
2. CQL-Query in confluence.yml setzen:
   ```yaml
   custom_dataset_query: title ~ 'Test Case'
   ```
3. Daten werden in `datasets/confluence/custom_pages.csv` gespeichert

---

## Ergebnisse

### Wichtige Dateien nach Testlauf

```
results/confluence/<timestamp>/
├── results.csv           # Konsolidierte Metriken
├── effective.yml         # Effektive Konfiguration
├── bzt.log              # Detailliertes Log
├── results_summary.log   # Zusammenfassung
├── kpi.jtl              # JMeter/Locust Rohdaten
└── selenium.jtl         # Selenium Rohdaten
```

### Erfolgskriterien

- **Erfolgsrate**: >= 95%
- **Performance-Impact**: < 20% Verschlechterung
- **Fehlerrate**: < 25% (sonst Test-Abbruch)

---

## Smartics Report-Generierung

Das `convert-to-projectdoc-json.py` Script:
1. Liest Testergebnisse aus `results/confluence/`
2. Sammelt Metadaten (Server-Info, Plugin-Versionen)
3. Generiert Performance-Chart
4. Erstellt projectdoc-Dokument im Dokumentationssystem

```bash
python convert-to-projectdoc-json.py <location> [result_name]
```

Benötigte Umgebungsvariablen (.env):
```
SMARTICS_DOC_SYSTEM_URL=https://docs.example.com
SMARTICS_DOC_SYSTEM_USERNAME=user
SMARTICS_DOC_SYSTEM_PASSWORD=pass
SMARTICS_TEST_SYSTEM_URL=https://confluence.example.com
SMARTICS_TEST_SYSTEM_USERNAME=admin
SMARTICS_TEST_SYSTEM_PASSWORD=admin
```

---

## Wichtige Hinweise

1. **Sprache**: Confluence muss auf **English (US/GB)** eingestellt sein
2. **Remote API**: Muss aktiviert sein
3. **Collaborative Editing**: Muss aktiviert sein
4. **Admin-Rechte**: Test-User braucht `confluence-administrators` Gruppe
5. **Lizenz**: Muss gültig sein und freie Seats haben

---

## AWS Deployment (Enterprise)

### Kosten (geschätzt)
- 1 Node: $1-2/Stunde
- 2 Nodes: $1.50-2/Stunde
- 4 Nodes: $2-3/Stunde

### vCPU Anforderung
- Minimum: 40 vCPU
- Empfohlen: 50 vCPU

### Dataset-Größe (Enterprise)
- ~900.000 Seiten
- ~100.000 Blogposts
- ~2.300.000 Anhänge
- ~6.000.000 Kommentare
- ~5.000 Spaces und Benutzer

### Aktuelle Konfiguration (Januar 2026)
- **Environment Name**: `dcapt-confluence-e1`
- **Region**: `us-east-2`
- **Produkt**: Confluence 10.0.3
- **Nodes**: 4 Replica (m5.2xlarge, 200GB Disk)
- **RDS**: db.m5.xlarge, PostgreSQL 14, 200GB
- **Terraform Version**: `atlassianlabs/terraform:2.9.10`
- **Config File**: `app/util/k8s/dcapt.tfvars`

---

## AWS Cluster Management

### Environment starten (Enterprise-Scale)

```bash
cd app/util/k8s

# Enterprise-Scale Cluster erstellen
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.9.10 ./install.sh -c conf.tfvars
```

**Wichtig:**
- AWS Credentials in `app/util/k8s/aws_envs` konfigurieren
- Lizenz in `dcapt.tfvars` eintragen (Zeile 29)
- Ersten Start mit `replica_count = 1`, dann hochskalieren
- Installation dauert ca. 30-45 Minuten

### Environment terminieren (EMPFOHLEN)

**Methode 1: Offizieller Terraform Uninstall**

```bash
cd app/util/k8s

# Saubere Terraform-Terminierung
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.9.10 ./uninstall.sh -c conf.tfvars
```

**Löscht automatisch:**
- ✅ EKS Kubernetes Cluster + Node Groups
- ✅ RDS Datenbank (ohne Final Snapshot)
- ✅ VPC, Subnets, Route Tables, Security Groups
- ✅ Load Balancers (ALB/NLB)
- ✅ NAT Gateways + Internet Gateways
- ✅ EBS Volumes (Local & Shared Home)
- ✅ Elastic IPs

**Methode 2: Force Terminate (falls Terraform fehlschlägt)**

```bash
cd app/util/k8s

# Python-Script für vollständige Bereinigung
docker run --pull=always --env-file aws_envs \
--workdir="//data-center-terraform" \
--entrypoint="python" \
-v "/$PWD/terminate_cluster.py:/data-center-terraform/terminate_cluster.py" \
atlassian/dcapt terminate_cluster.py \
--cluster_name atlas-dcapt-confluence-e1-cluster \
--aws_region us-east-2
```

**Löscht zusätzlich:**
- ✅ S3 Buckets (Terraform State: `atl-dc-dcapt-confluence-e1-*`)
- ✅ DynamoDB Tables (Terraform Lock: `atl_dc_dcapt_confluence_e1`)
- ✅ IAM Rollen (clusterspezifisch: `atlas-dcapt-confluence-e1-*`)
- ✅ IAM Policies (clusterspezifisch)
- ✅ OpenID Connect Provider
- ✅ Orphaned EBS Volumes

### Nach-Terminierung Prüfung

**AWS CLI Credentials Setup:**

```bash
# Credentials aus aws_envs exportieren
cd app/util/k8s
export AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID aws_envs | cut -d= -f2)
export AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY aws_envs | cut -d= -f2)

# Oder manuell:
export AWS_ACCESS_KEY_ID=AKIAXJULYBHH3I4QRTUI
export AWS_SECRET_ACCESS_KEY=<secret_from_aws_envs>
```

**Ressourcen prüfen:**

```bash
# EKS Cluster
aws eks list-clusters --region us-east-2

# RDS Datenbanken
aws rds describe-db-instances --region us-east-2 \
  --query "DBInstances[?contains(DBInstanceIdentifier, 'confluence')].DBInstanceIdentifier"

# EBS Volumes (nicht gemountet)
aws ec2 describe-volumes --region us-east-2 \
  --filters "Name=status,Values=available" \
  --query "Volumes[].{ID:VolumeId,Size:Size,Tags:Tags[?Key=='Name'].Value|[0]}"

# NAT Gateways (aktiv)
aws ec2 describe-nat-gateways --region us-east-2 \
  --filter "Name=state,Values=available"

# S3 Buckets
aws s3 ls | grep -E "(dcapt|confluence)"

# Unattached Elastic IPs
aws ec2 describe-addresses --region us-east-2 \
  --query "Addresses[?AssociationId==null].{IP:PublicIp,ID:AllocationId}"

# VPCs (non-default)
aws ec2 describe-vpcs --region us-east-2 \
  --filters "Name=isDefault,Values=false" \
  --query "Vpcs[].{ID:VpcId,Tags:Tags[?Key=='Name'].Value|[0]}"
```

### Kosten-Übersicht

**Laufende Kosten (während Tests):**

| Ressource | Stündlich | Täglich (24h) | Monatlich |
|-----------|-----------|---------------|-----------|
| EKS Control Plane | $0.10 | $2.40 | ~$73 |
| EC2 m5.2xlarge × 4 | $1.54 | $36.96 | ~$1,109 |
| RDS db.m5.xlarge | $0.348 | $8.35 | ~$251 |
| NAT Gateway | $0.045 | $1.08 | ~$32 |
| Load Balancer | $0.025 | $0.60 | ~$18 |
| EBS 200GB × 5 | - | - | ~$50 |
| **GESAMT** | **~$2.06/h** | **~$49/Tag** | **~$1,533** |

**Kosten nach Terminierung:**

| Ressource | Status | Kosten |
|-----------|--------|--------|
| EKS + EC2 + RDS | ✅ Gelöscht | $0.00 |
| NAT Gateway | ✅ Gelöscht | $0.00 |
| Load Balancer | ✅ Gelöscht | $0.00 |
| EBS Volumes | ✅ Gelöscht | $0.00 |
| IAM Rollen | ⚠️ Verbleiben (optional) | $0.00 |
| S3 State Buckets | ⚠️ Falls vorhanden | ~$0.01-0.10/Monat |

**Wichtig:**
- IAM Rollen verursachen KEINE Kosten und können für nächsten Lauf bleiben
- S3 Terraform State Buckets nur mit Force Terminate gelöscht
- EBS Snapshots (falls manuell erstellt) kosten ~$0.05/GB/Monat

### Troubleshooting

**Problem: Terraform Uninstall hängt/fehlschlägt**

```bash
# Lösung: Force Terminate verwenden
cd app/util/k8s
docker run --pull=always --env-file aws_envs \
--workdir="//data-center-terraform" \
--entrypoint="python" \
-v "/$PWD/terminate_cluster.py:/data-center-terraform/terminate_cluster.py" \
atlassian/dcapt terminate_cluster.py \
--cluster_name atlas-dcapt-confluence-e1-cluster \
--aws_region us-east-2
```

**Problem: "Unable to locate credentials"**

```bash
# Lösung: Credentials aus aws_envs exportieren
cd app/util/k8s
source <(grep -v '^#' aws_envs | sed 's/^/export /')
```

**Problem: VPC kann nicht gelöscht werden**

```bash
# Ursache: Dependencies (Load Balancer, NAT Gateway, ENIs)
# Lösung: Force Terminate Script räumt automatisch auf
# Oder manuell: AWS Console → VPC → Delete Dependencies
```

**Detaillierte K8s Logs sammeln:**

```bash
export ENVIRONMENT_NAME=dcapt-confluence-e1
export REGION=us-east-2

docker run --pull=always --env-file aws_envs \
-v "/$PWD/k8s_logs:/data-center-terraform/k8s_logs" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.9.10 \
./scripts/collect_k8s_logs.sh atlas-$ENVIRONMENT_NAME-cluster $REGION k8s_logs
```

### Best Practices

1. **Immer denselben Terraform Tag verwenden** (`2.9.10` für install/uninstall)
2. **Nach Tests sofort terminieren** - Kosten laufen weiter!
3. **IAM Rollen können bleiben** - keine Kosten, Wiederverwendung möglich
4. **Monitoring aktivieren** falls Performance-Debugging nötig:
   ```yaml
   # In dcapt.tfvars:
   monitoring_enabled = true
   monitoring_grafana_expose_lb = true
   ```
5. **Credentials sicher verwenden**:
   - `aws_envs` NICHT in Git committen
   - Template: `aws_envs_SECRETS` als Vorlage verwenden
6. **Regelmäßig aufräumen** (alle 6 Monate):
   - Alte IAM Rollen prüfen
   - Ungenutzte EBS Snapshots löschen
   - S3 Buckets prüfen

---

## Referenzen

- [DCAPT User Guide Confluence](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-confluence/)
- [Performance and Scale Testing](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/)
- [GitHub Repository](https://github.com/atlassian/dc-app-performance-toolkit)
- [Slack Support](https://community.atlassian.com) - Channel: `#data-center-app-performance-toolkit`
