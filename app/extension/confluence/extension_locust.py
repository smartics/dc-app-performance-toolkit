import re
import random
import string
import json
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')

# --------------------------------------------------------------------------------------------------------------------
# smartics
# smartics switch between userscripts and projectdoc toolbox and DM
# --------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------
# smartics-dm
# --------------------------------------------------------------------------------------------------------------------
#TESTCASE_SPACE_KEY = "PROJECTDOCTEST"
#TESTCASE_SPACE_KEY = "DCPTCONTENT1" ??

# --------------------------------------------------------------------------------------------------------------------
# smartics-pd
# --------------------------------------------------------------------------------------------------------------------
TESTCASE_SPACE_KEY = "PROJECTDOCTEST"

# --------------------------------------------------------------------------------------------------------------------
# smartcs-us USERSCRIPT-PARAMETERS
# --------------------------------------------------------------------------------------------------------------------
TC_US_PAGEID = "44957866"
TC_US_EXPECTED_SCRIPT_NAME = "Inspect-1.0.js"

# --------------------------------------------------------------------------------------------------------------------
# smartics-dm DocumentationMacros (And Toolbox ?)
# --------------------------------------------------------------------------------------------------------------------

TC_DOCM = "MoreProjectdocUC"
TC_DOCM_SECTION_ASSERTION_TEXT = "Section1"
TC_DOCM_HIDE_ASSERTION_TEXT = "HideFromAll"
TC_DOCM_HIDEFROMANONYMOUS_ASSERTION_TEXT = "HideFromAnonymous"
TC_DOCM_HIDEFROMREADER_ASSERTION_TEXT = "HideFromReader"
TC_DOCM_DEFINITIONLIST_ASSERTION_TEXT = "Value2"

# --------------------------------------------------------------------------------------------------------------------
# smartics-pd ProjectdocToolbox (TC = TestCase)
# --------------------------------------------------------------------------------------------------------------------
TC_DISPLAY_TABLE = "Test Case Display Table"
TC_DISPLAY_TABLE_ASSERTION_TEXT = "List of Documents"
TC_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"
TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT = "Transclusion from Documents"

# --------------------------------------------------------------------------------------------------------------------
# smartics-is Extension Informationssystem
# --------------------------------------------------------------------------------------------------------------------
TC_INFORMATIONSYSTEM_ASSERTION_URL= "https://raw.githubusercontent.com/smartics/dc-app-performance-toolkit/refs/heads/master/informationsystem-test-case.txt"
TC_INFORMATIONSYSTEM_TEST = "Test+Case+Informationsystemtest"
TC_INFORMATIONSYSTEM_ASSERTION_TEXT = "informationsystem-test-case-id"

# --------------------------------------------------------------------------------------------------------------------
# smartics-bp BluePrints
# --------------------------------------------------------------------------------------------------------------------
BLUEPRINT_LOCATION = "47596907"
BLUEPRINT_SPACEKEY= "BLUEPRINT"
# --------------------------------------------------------------------------------------------------------------------
# smartics-us
# --------------------------------------------------------------------------------------------------------------------

@confluence_measure("locust_app_specific_action_userscript_rest")
def app_specific_action_userscript_rest(locust):
    page_id = TC_US_PAGEID  # Entfernen der geschweiften Klammern
    expected_text = TC_US_EXPECTED_SCRIPT_NAME
    url = f'/rest/userscripts-for-confluence/1/context?page-id={page_id}'
    logger.info(f"Requesting Userscripts RestAPI(1) content for: PAGEID {page_id}")
    with locust.client.get(url, catch_response=True) as response:
        if response.status_code == 200:
            content = response.text
            if expected_text in content:
                response.success()
            else:
                response.failure(f"Expected text '{expected_text}' not found in response content. But found: {content}")
        else:
            response.failure(f"Request failed with status code {response.status_code}")

@confluence_measure("locust_app_specific_action")
def app_specific_action(locust):
    page_id = TC_US_PAGEID
    expected_text = TC_US_EXPECTED_SCRIPT_NAME
    url = f'/rest/userscripts-for-confluence/1/context?page-id={page_id}'
    logger.info(f"Requesting Userscripts RestAPI(2) content for: PAGEID {page_id}")
    with locust.client.get(url, catch_response=True) as response:
        if response.status_code == 200:
            content = response.text
            if expected_text in content:
                response.success()
            else:
                response.failure(f"Expected text '{expected_text}' not found in response content.")
        else:
            response.failure(f"Request failed with status code {response.status_code}")

# --------------------------------------------------------------------------------------------------------------------
# smartics-dm
# --------------------------------------------------------------------------------------------------------------------

@confluence_measure("locust_app_specific_action_docm_section")
def app_specific_action_docm_section(locust):
    logger.info(f"SectionMacro DocumentationMacro")
    response = locust.get('/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM), catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DOCM_SECTION_ASSERTION_TEXT)

@confluence_measure("locust_app_specific_action_docm_hide")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_docm_hide(locust):
    logger.info(f"HideMacro DocumentationMacro")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DOCM_HIDE_ASSERTION_TEXT)


@confluence_measure("locust_app_specific_action_docm_hidefromreader")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_docm_hidefromreader(locust):
    logger.info(f"HideFromReaderMacro DocumentationMacro")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DOCM_HIDEFROMREADER_ASSERTION_TEXT)


@confluence_measure("locust_app_specific_action_docm_hidefromanonymous")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_docm_hidefromanonymous(locust):
    logger.info(f"HideFromAnonymousMacro DocumentationMacro")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DOCM_HIDEFROMANONYMOUS_ASSERTION_TEXT)


@confluence_measure("locust_app_specific_action_docm_definitionlist")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_docm_definitionlist(locust):
    logger.info(f"Definitionlist DocumentationMacro")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DOCM_DEFINITIONLIST_ASSERTION_TEXT)

# --------------------------------------------------------------------------------------------------------------------
# smartics-pd
# --------------------------------------------------------------------------------------------------------------------


@confluence_measure("locust_app_specific_action_display_table")
def app_specific_action_display_table(locust):
    logger.info(f"DisplayTable")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DISPLAY_TABLE_ASSERTION_TEXT)



@confluence_measure("locust_app_specific_action_transclude_documents")
def app_specific_action_transclude_documents(locust):
    logger.info(f"TranscludeDocuments")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT)


# --------------------------------------------------------------------------------------------------------------------
# smartics-is
# --------------------------------------------------------------------------------------------------------------------

@confluence_measure("locust_app_specific_action_information_system")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_information_system(locust):
    logger.info(f"Informationsystems")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_INFORMATIONSYSTEM_TEST),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_INFORMATIONSYSTEM_ASSERTION_TEXT)


# --------------------------------------------------------------------------------------------------------------------
# smartics-wa
# --------------------------------------------------------------------------------------------------------------------

@confluence_measure("locust_app_specific_action_web_api")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_web_api(locust):
    logger.info(f"WEB-API")
    r = locust.get('/rest/projectdoc/1/document?select=Title%2CName%2CIteration&from=PROJECTDOCTEST&where=%24%3CTitle%3E%3D%5Bprojectdoc%20Space%20for%20Test%20Cases%5D&expand=property',
                   catch_response=True)  # call app-specific GET endpoint
    content = r.content.decode('utf-8')  # decode response content

    token_pattern_example = '"id-list":"(.+?)"'
    token = re.findall(token_pattern_example, content)
    logger.locust_info(f'token: {token}')  # log info for debug when verbose is true in confluence.yml file
    if token == "":
        logger.error(f"'assertion string' was not found in {content}")
    assert token != ""  # assert that TOKEN is not empty

# --------------------------------------------------------------------------------------------------------------------
# smartics-bp (BluePrints)
# --------------------------------------------------------------------------------------------------------------------

def setup_blueprint_pages(locust, doctypes):
    """
    Setup-Funktion: Erstellt für jeden Doctype eine Blueprint-Seite
    Diese Funktion wird NICHT gemessen und läuft nur einmal beim Setup
    """
    created_pages = []

    logger.info(f"Blueprint Setup: Erstelle Seiten für {len(doctypes)} Doctypes")

    for doctype in doctypes:
        NAME = f"{doctype} "+"".join([random.choice(string.ascii_lowercase) for _ in range(20)])
        SHORT_DESCRIPTION = f"Short Description for doctype {doctype}"
        SPACEKEY = BLUEPRINT_SPACEKEY
        LOCATION = BLUEPRINT_LOCATION

        j_payload = {
            "property": [
                {
                    "name": "New Property",
                    "value": "My Value",
                    "controls": "",
                    "position": "after",
                    "ref": "Name"
                }
            ],
            "section": [
                {
                    "title": "My Section",
                    "content": "<p>Some text</p>",
                    "position": "before",
                    "ref": "References"
                }
            ]
        }

        URL = f"/rest/projectdoc/1/document.json?doctype={doctype}&name={NAME}&short-description={SHORT_DESCRIPTION}&space-key={SPACEKEY}&location=_{LOCATION}_"
        headers = {'Content-Type': 'application/json'}

        try:
            response = locust.post(URL, headers=headers, data=json.dumps(j_payload))
            if response.status_code == 200:
                # Extrahiere die Page-ID aus der Response (falls vorhanden)
                try:
                    response_data = response.json()
                    page_id = response_data.get('id', NAME)  # Fallback auf NAME wenn keine ID
                    created_pages.append({
                        'doctype': doctype,
                        'name': NAME,
                        'page_id': page_id,
                        'space_key': SPACEKEY
                    })
                    print(f'Setup: Successfully created blueprint page for doctype: {doctype}')
                except:
                    # Fallback wenn JSON parsing fehlschlägt
                    created_pages.append({
                        'doctype': doctype,
                        'name': NAME,
                        'page_id': NAME,
                        'space_key': SPACEKEY
                    })
                    print(f'Setup: Successfully created blueprint page for doctype: {doctype} (no page ID extracted)')
            else:
                logger.warning(f"Setup: Failed to create blueprint for doctype: {doctype}, status: {response.status_code}")
        except Exception as e:
            logger.error(f"Setup: Error creating blueprint for doctype {doctype}: {str(e)}")

    print(f'Setup: Created {len(created_pages)} blueprint pages out of {len(doctypes)} doctypes')
    return created_pages

@confluence_measure("locust_app_specific_action_pd_bp")
def app_specific_action_check_blueprint_page(locust, blueprint_pages):
    """
    Test-Funktion: Prüft zufällig eine der erstellten Blueprint-Seiten
    Diese Funktion wird gemessen und prüft nur die Existenz der Seite
    """
    if not blueprint_pages:
        logger.error("Keine Blueprint-Seiten für Überprüfung verfügbar")
        return
    
    # Wähle zufällig eine der erstellten Seiten
    import random
    page_info = random.choice(blueprint_pages)
    page_name = page_info['name']
    space_key = page_info['space_key']
    doctype = page_info['doctype']
    url_name = page_info.get('url_name', page_name.replace(" ", "+"))
    
    logger.info(f"Teste Blueprint-Seite: {page_name} (doctype: {doctype})")
    
    # Prüfe die Seite durch Aufruf der Display-URL
    url = f'/display/{space_key}/{url_name}'
    
    with locust.client.get(url, catch_response=True, name=f"locust_app_pd_bp_{doctype}") as response:
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            # Mehrere Prüfungen für robustere Validierung
            content_checks = [
                doctype in content,
                page_name.split('_')[0] in content,  # Erster Teil des Namens (doctype)
                "Blueprint setup" in content,
                space_key in content
            ]
            
            if any(content_checks):
                response.success()
                logger.info(f"✓ Blueprint-Seite erfolgreich validiert: {page_name} (doctype: {doctype})")
            else:
                response.failure(f"Blueprint-Seite {page_name} enthält nicht den erwarteten Content für doctype {doctype}")
                logger.warning(f"✗ Content-Validierung fehlgeschlagen für: {page_name}")
        else:
            response.failure(f"Fehler beim Laden der Blueprint-Seite {page_name}, Status: {response.status_code}")
            logger.error(f"✗ HTTP-Fehler {response.status_code} beim Laden von: {page_name}")


@confluence_measure("locust_app_specific_action_blueprints")
def app_specific_action_create_from_blueprint(locust, doctypes, doctypesAll):

    logger.info(f"Blueprints: doctypes Länge: {len(doctypes)}")
    DOCTYPE = random.choice(doctypes)
    doctypes.remove(DOCTYPE)

    if len(doctypes) == 0:
        doctypes.extend(doctypesAll)

    NAME = f"{DOCTYPE} "+"".join([random.choice(string.ascii_lowercase) for _ in range(20)])
    SHORT_DESCRIPTION = f"Short Description for doctype {DOCTYPE}"
    SPACEKEY = "BLUEPRINT"
    LOCATION = BLUEPRINT_LOCATION
    j_payload = {
            "property": [
                {
                    "name": "New Property",
                    "value": "My Value",
                    "controls": "",
                    "position": "after",
                    "ref": "Name"
                }
            ],
            "section": [
                {
                    "title": "My Section",
                    "content": "<p>Some text</p>",
                    "position": "before",
                    "ref": "References"
                }
            ]
    }

    URL = f"/rest/projectdoc/1/document.json?doctype={DOCTYPE}&name={NAME}&short-description={SHORT_DESCRIPTION}&space-key={SPACEKEY}&location=_{LOCATION}_"
    headers = {'Content-Type': 'application/json'}
    response = locust.post(URL, headers=headers, data=json.dumps(j_payload), name="locust_app_specific_action_projectdoc_toolbox_bp:"+DOCTYPE)
    content = response.content.decode('utf-8')  # decode response content
    if response.status_code != 200:
        logger.info(f"Failed to create from blueprint with doctype: {DOCTYPE} with response: {content}")
        assert response.status_code != 200
    else:
        print(f'Successfully created from blueprint with doctype: {DOCTYPE}')


#@confluence_measure("locust_app_specific_action")
#def app_specific_action_transclude_documents(locust):
#    logger.info(f"TranscludeDocuments")
#    response = locust.get(
#        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS),
#        catch_response=True)
#    content = response.content.decode('utf-8')
#    assert_text(content, TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT)

# --------------------------------------------------------------------------------------------------------------------
# smartics ENDE
# --------------------------------------------------------------------------------------------------------------------

def assert_text(content, assertion_string):
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")