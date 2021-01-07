# coding=utf-8

# Test case to run requests and and calculate the userscript context dependent
# on the activation record.
#
# When a homepage of a space is accessed via GET the activation record will
# activate a number of userscripts. These scripts simply write to the client
# console.
#
# The test case is based on
# https://github.com/atlassian/dc-app-performance-toolkit/blob/master/docs/dc-apps-performance-toolkit-user-guide-confluence.md

from locustio.common_utils import init_logger, confluence_measure

logger = init_logger(app_type='confluence')

USER_SPACE_KEY = "USR1"
USER_SPACE_HOMEPAGE = "Userspace 1"


@confluence_measure
def app_specific_action(locust):
    """
    Simply calls the homepage of a user space to activate a number of
    userscripts.
    """
    response = locust.get(
        '/confluence/display/{}/{}'.format(USER_SPACE_KEY, USER_SPACE_HOMEPAGE),
        catch_response=True)
    content = response.content.decode('utf-8')

    assertion_string = 'Userspace 1'
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
    assert assertion_string in content
