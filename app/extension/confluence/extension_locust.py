# coding=utf-8

# Test case to run requests to serve pages that run the central use cases.
#
# These use cases are
#   Use the Display Table Macro
#   Use the Transclude Documents Macro
#   Optional: Have an ITSM page
#
# When a test case page is accessed via GET then the macros will put load on the servers.
#
# The test case is based on
# https://github.com/atlassian/dc-app-performance-toolkit/blob/master/docs/dc-apps-performance-toolkit-user-guide-confluence.md

from locustio.common_utils import init_logger, confluence_measure

logger = init_logger(app_type='confluence')

TESTCASE_SPACE_KEY = "TC"
TC_DISPLAY_TABLE = "Test+Case+Display+Table"
TC_DISPLAY_TABLE_ASSERTION_TEXT = "List of Documents"
TC_TRANSCLUDE_DOCUMENTS = "Test+Case+Transclude+from+Documents"
TC_TRANSCLUDE_DOCUMENTS_ASSERTION_TEXT="Transclusion from Documents"

@confluence_measure
def app_specific_action(locust):
    """
    Calls the use case where multiple documents are listed in a Display Table
    Macro and Transclude Documents Macro.
    """
    response = locust.get(
        '/confluence/display/{}/{}'.format(TESTCASE_SPACE_KEY,
                                           TC_DISPLAY_TABLE),
        catch_response=True)
    content = response.content.decode('utf-8')

    assertion_string = TC_DISPLAY_TABLE_ASSERTION_TEXT
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
    assert assertion_string in content
