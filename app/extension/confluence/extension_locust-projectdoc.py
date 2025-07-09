import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')

#TESTCASE_SPACE_KEY = "PROJECTDOCTEST"
TC_DOCM = "DOCM1"
TC_DOCM_ASSERTION_TEXT = "Section1"
TC_DISPLAY_TABLE = "Test Case Display Table"
TC_DISPLAY_TABLE_ASSERTION_TEXT = "List of Documents"
TC_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"
TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT = "Transclusion from Documents"
TC_INFORMATIONSYSTEM_TEST = "Informationsystemtest"
TC_INFORMATIONSYSTEM_ASSERTION_TEXT = "informationsystem-test-case-id"

@confluence_measure("locust_app_specific_action_docm")
# @run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action_docm(locust):
    logger.info(f"DocumentationMacro")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DOCM),
        catch_response=True)
    content = response.content.decode('utf-8')
    assertion_string = TC_DOCM_ASSERTION_TEXT

    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")


@confluence_measure("locust_app_specific_action_dt")
# @run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action_dt(locust):
    logger.info(f"DisplayTable")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE),
        catch_response=True)
    content = response.content.decode('utf-8')
    assertion_string = TC_DISPLAY_TABLE_ASSERTION_TEXT

    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")


@confluence_measure("locust_app_specific_action_td")
# @run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action_td(locust):
    logger.info(f"TranscludeDocuments")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS),
        catch_response=True)
    content = response.content.decode('utf-8')
    assertion_string = TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT

    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")

@confluence_measure("locust_app_specific_action_is")
# @run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action_is(locust):
    logger.info(f"Informationsystems")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_INFORMATIONSYSTEM_TEST),
        catch_response=True)
    content = response.content.decode('utf-8')
    assertion_string = TC_INFORMATIONSYSTEM_ASSERTION_TEXT

    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")


@confluence_measure("locust_app_specific_action_wa")
# @run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
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
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
#@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
#def app_specific_action(locust):
#    r = locust.get('/app/get_endpoint', catch_response=True)  # call app-specific GET endpoint
#    content = r.content.decode('utf-8')   # decode response content
#
#    token_pattern_example = '"token":"(.+?)"'
#    id_pattern_example = '"id":"(.+?)"'
#    token = re.findall(token_pattern_example, content)  # get TOKEN from response using regexp
#    id = re.findall(id_pattern_example, content)    # get ID from response using regexp
#
#    logger.locust_info(f'token: {token}, id: {id}')  # log info for debug when verbose is true in confluence.yml file
#    if 'assertion string' not in content:
#        logger.error(f"'assertion string' was not found in {content}")
#    assert 'assertion string' in content  # assert specific string in response content
#
#    body = {"id": id, "token": token}  # include parsed variables to POST request body
#    headers = {'content-type': 'application/json'}
#    r = locust.post('/app/post_endpoint', body, headers, catch_response=True)  # call app-specific POST endpoint
#    content = r.content.decode('utf-8')
#    if 'assertion string after successful POST request' not in content:
#        logger.error(f"'assertion string after successful POST request' was not found in {content}")
#    assert 'assertion string after successful POST request' in content  # assertion after POST request
