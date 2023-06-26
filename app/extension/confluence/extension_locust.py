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
    """
    Calls the use case where multiple documents are listed in a Display Table
    Macro and Transclude Documents Macro.
    """
    logger.info(f"XXXXXYYYY  LOCUST DISPLAYTABLE")
    response = locust.get(
        '/display/{}/{}'.format(TESTCASE_SPACE_KEY,
                                           TC_DISPLAY_TABLE),
        catch_response=True)
    content = response.content.decode('utf-8')

    assertion_string = TC_DISPLAY_TABLE_ASSERTION_TEXT
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
    assert assertion_string in content

