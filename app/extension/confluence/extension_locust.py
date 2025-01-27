import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')

@confluence_measure("locust_app_specific_action")
def app_specific_action(locust):
    logger.info(f"SectionMacro DocumentationMacro")
    response = locust.get('/display/{}/{}'.format("DOC", "UseCase+Sections"), catch_response=True)
    content = response.content.decode('utf-8')
    assert_text(content, "div-UseCaseSections-Section1")

def assert_text(content, assertion_string):
    if assertion_string not in content:
        logger.error(f"'{assertion_string}' was not found in {content}")
        assert assertion_string in content
    else:
        logger.info(
            f"'{assertion_string}' was found in content")