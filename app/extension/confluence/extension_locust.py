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
#TESTCASE_SPACE_KEY = "DOCM"
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
TC_DOCM = "DOCM1"
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
BLUEPRINT_LOCATION = "44320083"

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
    r = locust.get('/rest/projectdoc/1/document?select=Title%2CName%2CIteration&from=PROJECTDOCTEST&where=%24%3CTitle%3E%3D%5Bprojectdoc%20Space%20for%20Test%20Cases%5D&expand=property',
                   catch_response=True)  # call app-specific GET endpoint
    content = r.content.decode('utf-8')  # decode response content

    token_pattern_example = '"id-list":"(.+?)"'
    token = re.findall(token_pattern_example,
                       content)  # get TOKEN from response using regexp
    logger.locust_info(f'token: {token}')  # log info for debug when verbose is true in confluence.yml file
    if token == "":
        logger.error(f"'assertion string' was not found in {content}")
    assert token != ""  # assert that TOKEN is not empty

# --------------------------------------------------------------------------------------------------------------------
# smartics-bp (BluePrints)
# --------------------------------------------------------------------------------------------------------------------

@confluence_measure("locust_app_specific_action_blueprints")
def app_specific_action_create_from_blueprint(locust, doctypes, doctypesAll):
    logger.locust_info(f'XXXXX blueprint: {doctypesAll}')
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

    URL = f"/rest/projectdoc/1/document.json?doctype={DOCTYPE}&name={NAME}&short-description={SHORT_DESCRIPTION}&space-key={SPACEKEY}&location=%7B{LOCATION}%7D"
    headers = {'Content-Type': 'application/json'}
    response = locust.post(URL, headers=headers, data=json.dumps(j_payload), name="locust_app_specific_action_blueprints:"+DOCTYPE)
    content = response.content.decode('utf-8')  # decode response content
    if response.status_code != 200:
        logger.error(f'Failed to create from blueprint with doctype: {DOCTYPE}')
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
