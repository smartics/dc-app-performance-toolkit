import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')
# smartics
# USERSCRIPT-PARAMETERS
TC_US_PAGEID = "3539099"
TC_US_EXPECTED_SCRIPT_NAME = "projectdoc-inspect-menu.js"

# DOCUMENTATION Macros, projectdoc, ...
TESTCASE_SPACE_KEY = "DCPTCONTENT1"
#TESTCASE_SPACE_KEY = "DOCM"
#TESTCASE_SPACE_KEY = "PROJECTDOCTEST"

#DocumentationMacros (And Toolbox ?)
TC_DOCM = "DOCM1"
TC_DOCM_SECTION_ASSERTION_TEXT = "Section1"
TC_DOCM_HIDE_ASSERTION_TEXT = "HideFromAll"
TC_DOCM_HIDEFROMANONYMOUS_ASSERTION_TEXT = "HideFromAnonymous"
TC_DOCM_HIDEFROMREADER_ASSERTION_TEXT = "HideFromReader"
TC_DOCM_DEFINITIONLIST_ASSERTION_TEXT = "Value2"

#ProjectdocToolbox
TC_DISPLAY_TABLE = "Test Case Display Table"
TC_DISPLAY_TABLE_ASSERTION_TEXT = "List of Documents"
TC_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"
TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT = "Transclusion from Documents"

#Extension Informationssystem
TC_INFORMATIONSYSTEM_TEST = "Informationsystemtest"
TC_INFORMATIONSYSTEM_ASSERTION_TEXT = "informationsystem-test-case-id"
#smartics comment in only the wanted tests

@confluence_measure("locust_app_specific_action_userscript_rest")
def app_specific_action_userscript_rest(locust):
    page_id = TC_US_PAGEID
    expected_text = {TC_US_EXPECTED_SCRIPT_NAME}
    url = f'/rest/userscripts-for-confluence/1/context?page-id={page_id}'
    logger.info(f"Requesting Userscripts RestAPI(1) content for: PAGEID {page_id}")
    with locust.client.get(url, catch_response=True) as response:
        if response.status_code == 200:
            content = response.text
            if expected_text in content:
                response.success()
            else:
                response.failure(f"Expected text '{expected_text}' not found in response content.")
        else:
            response.failure(f"Request failed with status code {response.status_code}")

@confluence_measure("locust_app_specific_action")
def app_specific_action(locust):
    page_id = TC_US_PAGEID
    expected_text = {TC_US_EXPECTED_SCRIPT_NAME}
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

#@confluence_measure("locust_app_specific_action")
#def app_specific_action(locust):
#    logger.info(f"Userscripts RestAPI content 1")
# http://a9ad5e96ce29c45b1a45a1d85829e3a3-1034839394.us-east-2.elb.amazonaws.com/confluence/rest/userscripts-for-confluence/1/context?page-id=44236807
#    response = locust.get('/rest/userscripts-for-confluence/1/repo/de.smartics.test/test-1.0.0.js', catch_response=True)
#    content = response.content.decode('utf-8')
#    assert_text(content, "Copyright 2019-2020 Kronseder & Reiner GmbH, smartics")

#@confluence_measure("locust_app_specific_action")
#def app_specific_action(locust):
#    logger.info(f"Atlassian RestAPI check")
#    response = locust.get('/rest/api/user/current', catch_response=True)
#    content = response.content.decode('utf-8')
#    assert_text(content, "type")


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



@confluence_measure("locust_app_specific_action_dt")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_dt(locust):
    logger.info(f"DisplayTable")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_DISPLAY_TABLE_ASSERTION_TEXT)



@confluence_measure("locust_app_specific_action_td")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_td(locust):
    logger.info(f"TranscludeDocuments")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT)


@confluence_measure("locust_app_specific_action_is")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_is(locust):
    logger.info(f"Informationsystems")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_INFORMATIONSYSTEM_TEST),
        catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, TC_INFORMATIONSYSTEM_ASSERTION_TEXT)


#REST API (Web API = wa)
@confluence_measure("locust_app_specific_action_wa")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_wa(locust):
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


@confluence_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
#def app_specific_action(locust):
#    r = locust.get('/app/get_endpoint', catch_response=True)  # call app-specific GET endpoint
#    content = r.content.decode('utf-8')   # decode response content

#    token_pattern_example = '"token":"(.+?)"'
#    id_pattern_examplem= '"id":"(.+?)"'
#    token = re.findall(token_pattern_example, content)  # get TOKEN from response using regexp
#    id = remfindall(id_pattern_example, content)    # get id from response using regexp

#    logger.locust_info(f'token: {token}, id: {id}')  # log info for debug when verbose is true in confluence.yml file
#    if 'assertion string' not in content:
#        logger.error(f"'assertion string' was not found in {content}")
#    assert 'assertion string' in content  # assert specific string in response content

#    body = {"id": id, "token": token}  # include parsed variables to POST request body
#    headers = {'content-type': 'application/json'}
#    r = locust.post('/app/post_endpoint', body, headers, catch_response=True)  # call app-specific POST endpoint
#    content = r.content.decode('utf-8')
#    if 'assertion string after successful POST request' not in content:
#        logger.error(f"'assertion string after successful POST request' was not found in {content}")
#    assert 'assertion string after successful POST request' in content  # assertion after POST request


def assert_text(content, assertion_string):
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")

# {
#     "size": 1,
#     "start-index": 0,
#     "max-result": 1,
#     "id-list": "43647154",
#     "document": [
#         {
#             "id": 43647154,
#             "property": [
#                 {
#                     "name": "Title",
#                     "value": "projectdoc Space for Test Cases",
#                     "controls": "artificial, is-single-value"
#                 },
#                 {
#                     "name": "Name",
#                     "value": "\n                    projectdoc Space for Test Cases\n                    \n                  ",
#                     "controls": "hide"
#                 }
#             ],
#             "section": []
#         }
#     ]
# }



#@confluence_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
#def app_specific_action(locust):
#    r = locust.get('/app/get_endpoint', catch_response=True)  # call app-specific GET endpoint
#    content = r.content.decode('utf-8')   # decode response content

#    token_pattern_example = '"token":"(.+?)"'
#    id_pattern_example = '"id":"(.+?)"'
#    token = re.findall(token_pattern_example, content)  # get TOKEN from response using regexp
#    id = re.findall(id_pattern_example, content)    # get ID from response using regexp

#    logger.locust_info(f'token: {token}, id: {id}')  # log info for debug when verbose is true in confluence.yml file
#    if 'assertion string' not in content:
#        logger.error(f"'assertion string' was not found in {content}")
#    assert 'assertion string' in content  # assert specific string in response content

#    body = {"id": id, "token": token}  # include parsed variables to POST request body
#    headers = {'content-type': 'application/json'}
#    r = locust.post('/app/post_endpoint', body, headers, catch_response=True)  # call app-specific POST endpoint
#    content = r.content.decode('utf-8')
#    if 'assertion string after successful POST request' not in content:
#        logger.error(f"'assertion string after successful POST request' was not found in {content}")
#    assert 'assertion string after successful POST request' in content  # assertion after POST request
