from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

TC_TITLE_DISPLAY_TABLE = "Test Case Display Table"
TC_TITLE_TRANSCLUDE_DOCUMENTS = "Test Case Transclude from Documents"


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_page")
        def sub_measure():
            page.go_to_url(
                f"{CONFLUENCE_SETTINGS.server_url}/pages/viewpage.action?pageId={app_specific_page_id}")
            page.wait_until_visible(
                (By.ID, "title-text"))  # Wait for title field visible

            title = page.get_element((By.ID, "title-text")).text
            if (TC_TITLE_DISPLAY_TABLE == title):
                # page.wait_until_visible((By.ID, "projectdoc-success"))
                i = 1
            elif (TC_TITLE_TRANSCLUDE_DOCUMENTS == title):
                # page.wait_until_visible((By.ID, "projectdoc-success"))
                i = 2

        sub_measure()

    measure()
