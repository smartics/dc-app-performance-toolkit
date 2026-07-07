# Testdaten-Setup für die Smartics-App-Tests (Confluence DCPT)

> Quelle: Diary-Seite `dev.smartics.mobi` id **1101841** „Datacenter Performance Tests projectdoc
> Toolbox – 2023-06-29 anton.kronseder" (+ Kind-Seiten 1103324 IS, 1103365 US) und Repo
> https://github.com/smartics/projectdoc-toolbox-dcpt . Abgerufen 2026-07-06.
>
> Zweck: Wie die instanzseitigen Testdaten je App entstehen. Für die jährliche Wiederholung.

## Überblick (Stand 2023) — welche App wie getestet wurde

| App | Test-Framework | Testdaten-Quelle |
|-----|----------------|------------------|
| projectdoc Toolbox (PD) | locust | Repo `projectdoc-toolbox-dcpt` (automatisch) |
| Web API (WA) | locust | Repo `projectdoc-toolbox-dcpt` (Testcase-Space) |
| Userscripts (US) | Selenium | manuell: `userscript-dc-test.js` hochladen+konfigurieren |
| Information System (IS) | locust | manuell: Allowlist + Property `url-github` |

## 1. PD + WA — via Repo `projectdoc-toolbox-dcpt`
```
pip install atlassian-python-api
python testcases/test_setup.py -sc 1 -cl 3,2 -tl 2,2 -cm -px <PREFIX>
```
Erzeugt:
- Content-Spaces `<PREFIX>CONTENT<n>` (projectdoc-Dokument-Bäume + Tags)
- Testcase-Space `<PREFIX>TEST` mit Namen **„projectdoc Space for Test Cases"**  → WA-Assertion
- Seite **„Test Case Display Table"** (`projectdoc-display-table`, Section „List of Documents") → PD
- Seite **„Test Case Transclude from Documents"** (`projectdoc-transclude-documents-macro`,
  Section „Transclusion from Documents") → PD
- Voraussetzung: projectdoc Toolbox **+ Web API Extension** installiert (sonst 404).
- Aufräumen: `python testcases/test_teardown.py -s <space1>,<space2>`

2023 verwendete Space-Keys: **`PROJECTDOCTEST`, `PROJECTDOCCONTENT1/2`** (Prefix „PROJECTDOC").

## 2. US — Userscripts (2023: Selenium-Banner)
- `userscript-dc-test.js` (liegt in `smartics/testdata-2023/`) im US-App hochladen & konfigurieren.
- Das Script injiziert ein `<div id="userscripts-dc-test-banner">` (oranger Streifen) auf den
  Seiten „Test Case Display Table" / „Test Case Transclude from Documents".
- Selenium prüfte auf Element `userscripts-dc-test-banner`.

## 3. IS — Information System
- In Confluence **Allowlist** die URL `https://raw.githubusercontent.com` eintragen.
- IS-Testseite unter die **Space-Homepage von `PROJECTDOCTEST`** („projectdoc Space for Test Cases") legen.
- Auf der Space-Homepage das Property **`url-github` = `https://raw.githubusercontent.com`** (Label „github")
  anlegen (Muster: Kind-Seite „Informationsystemtest", id 1103324).
- Seite nur für Test-User sichtbar (admin bei DC-AWS; anton.kronseder/robert.reiner lokal).

## 4. custom_dataset_query (2023)
- Selenium: `space='PROJECTDOCTEST' AND (title = 'Test Case Display Table' OR title = 'Test Case Transclude from Documents')`
- Datenaufbereitung (`util/data_preparation/confluence_prepare_data.py`):
  - lokal: nur `space.key in (…CONTENT1..5, …TEST)`
  - DC/AWS: `space.key not in (PROJECTDOCTEST, PROJECTDOCCONTENT1, PROJECTDOCCONTENT2)`

## ⚠️ Abweichungen 2023 → aktueller Branch (smartics-dcapt-2026-all)
1. **Space-Key:** 2023 `PROJECTDOCTEST`; aktueller `extension_locust.py` erwartet **`DCAPTUC`**
   (`TESTCASE_SPACE_KEY`). → entweder Repo mit passendem Prefix laufen lassen und Konstante anpassen,
   ODER Testdaten im Space `DCAPTUC` erzeugen.
2. **US-Testmethode geändert:** 2023 Selenium-Banner `userscripts-dc-test-banner`.
   Aktueller Branch nutzt REST `/rest/userscripts-for-confluence/1/context?page-id=<TC_US_PAGEID>` und
   erwartet `Inspect-1.0.js` (+ Selenium `inspect-root`/`userscripts-admin-tool`). → US-Testdaten-Konzept
   für den neuen Lauf neu klären (welches Userscript, welche Seite/ID).
3. **BP (Blueprints):** 2023 nicht dokumentiert — im aktuellen Branch neu (`BLUEPRINT`-Space/Location).
4. **DM (Documentation Macros):** via `smartics/setup_confluence_spaces.py` (`MoreProjectdocUC`) —
   für „alle außer DM" deaktiviert.

## ⭐ ABKÜRZUNG: Fertige Space-Exporte (in `DATA/`)

In `DATA/` liegen **komplette Confluence-Space-Exporte** (`.xml.zip`, Juli/Aug 2025) — damit lassen
sich die Testdaten **importieren** statt neu anzulegen:

| ZIP | Space-Key | Deckt ab | Wichtige Seiten |
|-----|-----------|----------|-----------------|
| `DCAPT--1-spaces-2025-08-04…` | **PROJECTDOCTEST** | PD, WA, IS, DM | Test Case Display Table, Test Case Transclude from Documents, Test Case Informationsystemtest, projectdoc Space for Test Cases, MoreProjectdocUC |
| `DCAPT-TESTSUIT--1-spaces-2025-07-21…` | PROJECTDOCTEST (älter) | dito | dito |
| `DCAPT--BLUEPRINT-2025-08-06…` (klein) | **BLUEPRINT** | BP | alle Doctype-Index-Seiten, BLUEPRINT Home |
| `DCAPT--BLUEPRINT-2025-08-04…` (8,9 MB) | BLUEPRINT (groß) | BP | dito, mehr Daten |
| `DCAPT--USTEST-2025-08-04…` | **USTEST** | US | Inspect Menu for projectdoc, projectdoc-inspect-menu.js, DCPT-US-Test-Script, Scripts/Types |

Import: Confluence → *Space verwalten → Space importieren* (oder REST). Exporte stammen von Build 9109
→ Ziel Confluence 10.2.x (höherer Build) akzeptiert sie.

### ⚠️ Nach dem Import unbedingt beachten
0. **INDIZIERUNG erzwingen (WICHTIG, sonst rendern PD-Makros nicht / WA findet nichts):** Nach dem
   Space-Import werden die importierten Seiten NICHT automatisch vom projectdoc-Index erfasst. Man muss
   **alle Seiten im Space `PROJECTDOCTEST` einmal neu speichern** (inkl. der **Space-Home-Seite**
   „projectdoc Space for Test Cases"), damit Display-Table/Transclude rendern und die WA-REST-Query
   Treffer liefert. (Erfahrung 2026-07-07.)
0b. **IS-Allowlist:** In Confluence-Admin → **Allowlist** die Domain `https://raw.githubusercontent.com`
   eintragen — sonst rendert das Information-System-Makro den externen Test-Text nicht. (Pflicht!)
1. **Page-IDs werden beim Import NEU vergeben!** Bei diesem Lauf (2026-07-07) ermittelt:
   - `TC_US_PAGEID` → **`46944746`** (USTEST Space-Home; Userscript space-weit aktiv)
   - `BLUEPRINT_LOCATION` → **`46944143`** (BLUEPRINT Home)
2. **`TESTCASE_SPACE_KEY`** → **`PROJECTDOCTEST`** (nicht DCAPTUC). Erledigt.
3. **`TC_US_EXPECTED_SCRIPT_NAME`**: Live liefert die App `de.smartics.test/hello-1.0.x.js` (Version
   inkrementiert!) → Konstante auf **`de.smartics.test/hello`** (versionsunabhängig) gesetzt.

### Manuelle Schritte, die ein Space-Import NICHT abdeckt (aus den Screenshots von Seite 1101841)
- **IS – globale Allowlist:** `https://raw.githubusercontent.com` als *Domain name* eintragen,
  *Allow Incoming* + *Allow anonymous* aktivieren (Confluence-Admin → Allowlist). Die IS-Seite hat das
  Property `url-github = https://raw.githubusercontent.com` (im Export enthalten) und rendert
  `<div id="informationsystem-test-case-id">…</div>`.
- **US – Client-Logging aktivieren (PFLICHT vor dem US-Test!):** In der **Userscripts-Admin-Oberfläche**
  → *Konfiguration → Client-Logging* die zu loggenden **Modulnamen** eintragen (komma-separiert).
  Ohne diese Aktivierung liefert `/rest/userscripts-for-confluence/1/context` keine/keine korrekten
  Scripts. (Erfahrung 2026-07-07.)
- **US – Userscript-Registrierung** (nicht reiner Space-Content!): Der aktive Test-Userscript wird von
  der App aus dem USTEST-Space bedient; nach dem Space-Import + Seiten-Neuspeichern liefert die App
  `de.smartics.test/hello-1.0.x.js` (space-weit auf USTEST). Frühere 2023-Variante: Userscript im Admin
  anlegen (Namespace `de.smartics.userscripts`, Script-URL = Attachment `userscript-dc-test.js`,
  Space Keys, Page Label `blank`).
- **Plugins** installiert (US/PD/IS + Blueprints), **Permissions** der Testseiten (Permission Manager).

## Zugriff auf die Quelle
Confluence DC `dev.smartics.mobi` per REST (Bearer-PAT aus 1Password Vault `service`,
Item `dev.smartics.mobi`, Feld `Token`):
`curl -H "Authorization: Bearer <token>" https://dev.smartics.mobi/rest/api/content/1101841?expand=body.storage`
