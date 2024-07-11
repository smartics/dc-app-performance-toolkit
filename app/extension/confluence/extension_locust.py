import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')


@confluence_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):
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
