#!/usr/bin/env python3
"""
Smartics DCAPT Setup Script
===========================
Erstellt Spaces und Testseiten in Confluence für DCAPT-Tests.

Spaces:
- DCAPT: Standard-Testseiten für Atlassian Performance Tests (100 Seiten)
- DCAPT-UC: Use-Case-Seiten für Smartics App-Tests (DM, Toolbox, IS, BP, US)

Usage:
    python setup_confluence_spaces.py [--url URL] [--user USER] [--password PASS]

    Oder Umgebungsvariablen setzen:
    - CONFLUENCE_URL
    - CONFLUENCE_USER
    - CONFLUENCE_PASSWORD
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# .env laden falls dotenv verfügbar
try:
    from dotenv import load_dotenv
    # Lade .env aus dem smartics Ordner
    script_dir = Path(__file__).parent
    env_file = script_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()  # Fallback: Standard-Suche
except ImportError:
    pass  # dotenv nicht installiert - kein Problem


class ConfluenceSetup:

    def __init__(self, base_url, username, password=None, token=None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()

        # Token-Auth hat Vorrang vor Basic Auth
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
        else:
            self.auth = (username, password)
            self.session.auth = self.auth

        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Atlassian-Token': 'no-check'
        })

    def _api_url(self, endpoint):
        """Erstellt die vollständige API-URL"""
        return f"{self.base_url}/rest/api/{endpoint}"

    def test_connection(self):
        """Testet die Verbindung zu Confluence"""
        print(f"Teste Verbindung zu {self.base_url}...")
        try:
            response = self.session.get(self._api_url('user/current'))
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Verbunden als: {user_data.get('displayName', self.username)}")
                return True
            else:
                print(f"  FEHLER: Status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"  FEHLER: {e}")
            return False

    def space_exists(self, space_key):
        """Prüft ob ein Space existiert"""
        response = self.session.get(self._api_url(f'space/{space_key}'))
        return response.status_code == 200

    def create_space(self, space_key, name, description=""):
        """Erstellt einen neuen Space"""
        if self.space_exists(space_key):
            print(f"  Space '{space_key}' existiert bereits.")
            return self.get_space_homepage_id(space_key)

        payload = {
            "key": space_key,
            "name": name,
            "description": {
                "plain": {
                    "value": description,
                    "representation": "plain"
                }
            }
        }

        response = self.session.post(self._api_url('space'), json=payload)

        if response.status_code in [200, 201]:
            data = response.json()
            print(f"  Space '{space_key}' erstellt.")
            return data.get('homepage', {}).get('id')
        else:
            print(f"  FEHLER beim Erstellen von Space '{space_key}': {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def get_space_homepage_id(self, space_key):
        """Holt die Homepage-ID eines Spaces"""
        response = self.session.get(self._api_url(f'space/{space_key}?expand=homepage'))
        if response.status_code == 200:
            data = response.json()
            return data.get('homepage', {}).get('id')
        return None

    def page_exists(self, space_key, title):
        """Prüft ob eine Seite existiert"""
        response = self.session.get(
            self._api_url('content'),
            params={
                'spaceKey': space_key,
                'title': title,
                'type': 'page'
            }
        )
        if response.status_code == 200:
            data = response.json()
            return len(data.get('results', [])) > 0
        return False

    def create_page(self, space_key, title, content="", parent_id=None):
        """Erstellt eine neue Seite"""
        if self.page_exists(space_key, title):
            print(f"    Seite '{title}' existiert bereits.")
            return None

        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        response = self.session.post(self._api_url('content'), json=payload)

        if response.status_code in [200, 201]:
            data = response.json()
            print(f"    Seite '{title}' erstellt (ID: {data.get('id')})")
            return data.get('id')
        else:
            print(f"    FEHLER bei Seite '{title}': {response.status_code}")
            if response.status_code != 400:  # 400 = oft Duplikat
                print(f"    Response: {response.text[:200]}")
            return None

    def create_test_pages(self, space_key, count=100, parent_id=None):
        """Erstellt Testseiten für Performance-Tests"""
        print(f"\nErstelle {count} Testseiten in Space '{space_key}'...")

        created = 0
        for i in range(1, count + 1):
            title = f"DCAPT Test Page {i:04d}"
            content = f"""
            <h1>Test Page {i}</h1>
            <p>Diese Seite wurde automatisch für DCAPT Performance-Tests erstellt.</p>
            <p>Seiten-Nummer: {i}</p>
            <ac:structured-macro ac:name="toc" />
            <h2>Abschnitt 1</h2>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
            <h2>Abschnitt 2</h2>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
            nisi ut aliquip ex ea commodo consequat.</p>
            <h2>Abschnitt 3</h2>
            <p>Duis aute irure dolor in reprehenderit in voluptate velit esse
            cillum dolore eu fugiat nulla pariatur.</p>
            """

            if self.create_page(space_key, title, content, parent_id):
                created += 1

        print(f"  {created} von {count} Seiten erstellt.")
        return created

    def create_usecase_structure(self, space_key, parent_id=None):
        """Erstellt die Struktur für Smartics App Use-Cases"""
        print(f"\nErstelle Use-Case-Struktur in Space '{space_key}'...")

        # Hauptordner für jede App
        apps = {
            'DM': 'Documentation Macros Use Cases',
            'Toolbox': 'projectdoc Toolbox Use Cases',
            'IS': 'Information System Use Cases',
            'BP': 'Blueprints Use Cases',
            'US': 'Userscripts Use Cases'
        }

        for app_key, app_name in apps.items():
            folder_content = f"""
            <p>Use-Case-Seiten für <strong>{app_name}</strong></p>
            <p>Hier werden die Testseiten für die DCAPT Performance-Tests der App angelegt.</p>
            <ac:structured-macro ac:name="children" />
            """
            folder_id = self.create_page(space_key, app_name, folder_content, parent_id)

            if folder_id and app_key == 'DM':
                # DM-Testseite erstellen (MoreProjectdocUC equivalent)
                self.create_dm_test_page(space_key, folder_id)

    def create_dm_test_page(self, space_key, parent_id):
        """Erstellt die DM-Testseite mit allen benötigten Macros"""
        title = "MoreProjectdocUC"
        content = """<h1>Documentation Macros Test Page</h1>
<p>Diese Seite enthält alle DM-Macros für Performance-Tests.</p>
<h2>Section Macro Test</h2>
<ac:structured-macro ac:name="projectdoc-section" ac:schema-version="1"><ac:parameter ac:name="title">Section1</ac:parameter><ac:rich-text-body>
<p class="auto-cursor-target">Inhalt der Section1 für Tests.</p></ac:rich-text-body></ac:structured-macro>
<h2>Hide Macro Test</h2>
<ac:structured-macro ac:name="projectdoc-hide" ac:schema-version="1"><ac:parameter ac:name="replacement">HideFromAll</ac:parameter><ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter><ac:plain-text-body><![CDATA[HideFromAll - Dieser Text ist versteckt.]]></ac:plain-text-body></ac:structured-macro>
<h2>Hide from Reader Test</h2>
<ac:structured-macro ac:name="projectdoc-hide-from-reader-macro" ac:schema-version="2"><ac:parameter ac:name="replacement">HideFromReader</ac:parameter><ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter><ac:rich-text-body>
<p class="auto-cursor-target">HideFromReader - Nur für Editoren sichtbar.</p></ac:rich-text-body></ac:structured-macro>
<h2>Hide from Anonymous Test</h2>
<ac:structured-macro ac:name="projectdoc-hide-from-anonymous-user-macro" ac:schema-version="1"><ac:parameter ac:name="replacement">HideFromAnonymous</ac:parameter><ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter><ac:rich-text-body>
<p class="auto-cursor-target">HideFromAnonymous - Nur für angemeldete User sichtbar.</p></ac:rich-text-body></ac:structured-macro>
<h2>Definition List Test</h2>
<ac:structured-macro ac:name="projectdoc-definition-list-macro" ac:schema-version="1"><ac:rich-text-body>
<table><colgroup><col /><col /></colgroup>
<tbody>
<tr>
<th scope="row">Key1</th>
<td>Value1</td></tr>
<tr>
<th scope="row">Key2</th>
<td>Value2</td></tr></tbody></table></ac:rich-text-body></ac:structured-macro>
<p><br /></p>"""

        self.create_page(space_key, title, content, parent_id)

    def load_pages_from_folder(self, space_key, folder_path, parent_id=None):
        """Lädt Seiten aus Storage-Format-Dateien"""
        folder = Path(folder_path)
        if not folder.exists():
            print(f"  FEHLER: Ordner '{folder_path}' existiert nicht.")
            return 0

        print(f"\nLade Seiten aus '{folder_path}'...")

        created = 0
        for file_path in folder.glob('*.xml'):
            title = file_path.stem  # Dateiname ohne Extension
            content = file_path.read_text(encoding='utf-8')

            if self.create_page(space_key, title, content, parent_id):
                created += 1

        for file_path in folder.glob('*.html'):
            title = file_path.stem
            content = file_path.read_text(encoding='utf-8')

            if self.create_page(space_key, title, content, parent_id):
                created += 1

        print(f"  {created} Seiten aus Dateien erstellt.")
        return created


def main():
    parser = argparse.ArgumentParser(description='Smartics DCAPT Confluence Setup')
    parser.add_argument('--url', default=os.getenv('CONFLUENCE_URL', 'https://c10dcapt.smartics.eu'),
                        help='Confluence Base URL')
    parser.add_argument('--user', default=os.getenv('CONFLUENCE_USER', 'admin'),
                        help='Confluence Username')
    parser.add_argument('--password', default=os.getenv('CONFLUENCE_PASSWORD', ''),
                        help='Confluence Password (für Basic Auth)')
    parser.add_argument('--token', default=os.getenv('CONFLUENCE_TOKEN', ''),
                        help='Personal Access Token (für Token Auth, hat Vorrang vor Password)')
    parser.add_argument('--pages', type=int, default=100,
                        help='Anzahl der Testseiten für DCAPT Space (default: 100)')
    parser.add_argument('--pages-folder',
                        help='Ordner mit Storage-Format-Dateien für zusätzliche Seiten')
    parser.add_argument('--skip-dcapt', action='store_true',
                        help='DCAPT Space überspringen')
    parser.add_argument('--skip-usecase', action='store_true',
                        help='DCAPT-UC Space überspringen')

    args = parser.parse_args()

    if not args.password and not args.token:
        print("FEHLER: Weder Passwort noch Token gesetzt!")
        print("  Setze --password oder --token Parameter")
        print("  Oder Umgebungsvariablen: CONFLUENCE_PASSWORD / CONFLUENCE_TOKEN")
        sys.exit(1)

    print("=" * 60)
    print("Smartics DCAPT Confluence Setup")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"User: {args.user}")
    print(f"Auth: {'Token' if args.token else 'Basic Auth'}")
    print()

    setup = ConfluenceSetup(args.url, args.user, args.password, args.token)

    # Verbindung testen
    if not setup.test_connection():
        sys.exit(1)

    # Space DCAPT für Standard-Tests
    if not args.skip_dcapt:
        print("\n" + "-" * 40)
        print("Space: DCAPT (Standard Performance Tests)")
        print("-" * 40)

        homepage_id = setup.create_space(
            'DCAPT',
            'DCAPT Performance Tests',
            'Space für Atlassian DC App Performance Toolkit Tests'
        )

        setup.create_test_pages('DCAPT', args.pages, homepage_id)

    # Space DCAPT-UC für Smartics App Use-Cases
    if not args.skip_usecase:
        print("\n" + "-" * 40)
        print("Space: DCAPT-UC (Smartics App Use Cases)")
        print("-" * 40)

        homepage_id = setup.create_space(
            'DCAPTUC',  # Keine Bindestriche in Space Keys
            'DCAPT Use Cases',
            'Use-Case-Seiten für Smartics App Performance Tests (DM, Toolbox, IS, BP, US)'
        )

        setup.create_usecase_structure('DCAPTUC', homepage_id)

    # Zusätzliche Seiten aus Ordner laden
    if args.pages_folder:
        setup.load_pages_from_folder('DCAPTUC', args.pages_folder)

    print("\n" + "=" * 60)
    print("Setup abgeschlossen!")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("1. Prüfe die erstellten Spaces in Confluence")
    print("2. Installiere die zu testenden Apps (DM, Toolbox, etc.)")
    print("3. Passe app/confluence.yml an (hostname, credentials)")
    print("4. Aktualisiere TESTCASE_SPACE_KEY in extension_locust.py auf 'DCAPTUC'")
    print("5. Führe Tests aus: cd app && bzt confluence.yml")


if __name__ == '__main__':
    main()
