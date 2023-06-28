import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')

TESTCASE_SPACE_KEY = "PROJECTDOCTEST"
TC_DISPLAY_TABLE = "Test Case Display Table"
TC_DISPLAY_TABLE_ASSERTION_TEXT = "List of Documents"
TC_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"
TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT="Transclusion from Documents"

logger.info(f"XXXXXYYYY  LOCUST AAAAAAAAAAAAAAA")

@confluence_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):
    logger.info(f"XXXXXAAA LOCUST:: '{locust}'")
    """
    Calls the use case where multiple documents are listed in a Display Table
    Macro and Transclude Documents Macro.
    """
    logger.info(f"XXXXXYYYY  LOCUST DISPLAYTABLE")
    responseDT = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE), catch_response=True)
    contentDT = responseDT.content.decode('utf-8')

    responseTD = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS), catch_response=True)
    contentTD = responseTD.content.decode('utf-8')

    assertion_stringDT = TC_DISPLAY_TABLE_ASSERTION_TEXT
    assertion_stringTD = TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT 

    if assertion_stringDT not in contentDT and  assertion_stringTD not in contentTD:
        logger.error(f"'{assertion_stringDT}' or '{assertion_stringTD}' was not found in content: {contentDT} / {contentTD}")
        if assertion_stringDT not in contentDT:
           logger.error(f"'{assertion_stringDT}' was not found in {contentDT}")
           assert assertion_stringDT in contentDT
        elif assertion_stringTD not in contentTD:
           logger.error(f"'{assertion_stringTD}' was not found in {contentTD}")
           assert assertion_stringTD in contentTD
    else:
        logger.info(f"'{assertion_stringDT}' or '{assertion_stringTD}' was found in content")


@confluence_measure("locust_app_specific_action2")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action2(locust):
    logger.info(f"2XXXXXAAA LOCUST:: '{locust}'")
    """
    Calls the use case where multiple documents are listed in a Display Table
    Macro and Transclude Documents Macro.
    """
    logger.info(f"2XXXXXYYYY  LOCUST DISPLAYTABLE")
    responseDT = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE), catch_response=True)
    contentDT = responseDT.content.decode('utf-8')

    responseTD = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS), catch_response=True)
    contentTD = responseTD.content.decode('utf-8')

    assertion_stringDT = TC_DISPLAY_TABLE_ASSERTION_TEXT
    assertion_stringTD = TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT 

    if assertion_stringDT not in contentDT and  assertion_stringTD not in contentTD:
        logger.error(f"'{assertion_stringDT}' or '{assertion_stringTD}' was not found in content: {contentDT} / {contentTD}")
        if assertion_stringDT not in contentDT:
           logger.error(f"'{assertion_stringDT}' was not found in {contentDT}")
           assert assertion_stringDT in contentDT
        elif assertion_stringTD not in contentTD:
           logger.error(f"'{assertion_stringTD}' was not found in {contentTD}")
           assert assertion_stringTD in contentTD
    else:
        logger.info(f"'{assertion_stringDT}' or '{assertion_stringTD}' was found in content")


@confluence_measure("locust_app_specific_action_is")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_is(locust):
    logger.info(f"2XXXXXAAA LOCUST:: '{locust}'")
    """
    Calls the use case where multiple documents are listed in a Display Table
    Macro and Transclude Documents Macro.
    """
    logger.info(f"2XXXXXYYYY  LOCUST DISPLAYTABLE")
    responseDT = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_DISPLAY_TABLE), catch_response=True)
    contentDT = responseDT.content.decode('utf-8')

    responseTD = locust.get( '/display/{}/{}'.format(TESTCASE_SPACE_KEY, TC_TRANSCLUDE_DOCUMENTS), catch_response=True)
    contentTD = responseTD.content.decode('utf-8')

    assertion_stringDT = TC_DISPLAY_TABLE_ASSERTION_TEXT
    assertion_stringTD = TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT 

    if assertion_stringDT not in contentDT and  assertion_stringTD not in contentTD:
        logger.error(f"'{assertion_stringDT}' or '{assertion_stringTD}' was not found in content: {contentDT} / {contentTD}")
        if assertion_stringDT not in contentDT:
           logger.error(f"'{assertion_stringDT}' was not found in {contentDT}")
           assert assertion_stringDT in contentDT
        elif assertion_stringTD not in contentTD:
           logger.error(f"'{assertion_stringTD}' was not found in {contentTD}")
           assert assertion_stringTD in contentTD
    else:
        logger.info(f"'{assertion_stringDT}' or '{assertion_stringTD}' was found in content")



@confluence_measure("locust_app_specific_action_wa")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action_wa(locust):
    r = locust.get('/app/get_endpoint', catch_response=True)  # call app-specific GET endpoint
    content = r.content.decode('utf-8')   # decode response content

    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)  # get TOKEN from response using regexp
    id = re.findall(id_pattern_example, content)    # get ID from response using regexp
    logger.locust_info(f'token: {token}, id: {id}')  # log info for debug when verbose is true in confluence.yml file
    if 'assertion string' not in content:
       logger.error(f"'assertion string' was not found in {content}")
    assert 'assertion string' in content  # assert specific string in response content

    body = {"id": id, "token": token}  # include parsed variables to POST request body
    headers = {'content-type': 'application/json'}
    r = locust.post('/app/post_endpoint', body, headers, catch_response=True)  # call app-specific POST endpoint
    content = r.content.decode('utf-8')
    if 'assertion string after successful POST request' not in content:
       logger.error(f"'assertion string after successful POST request' was not found in {content}")
    assert 'assertion string after successful POST request' in content  # assertion after POST request




