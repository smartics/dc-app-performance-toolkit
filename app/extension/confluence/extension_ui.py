import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS

def dm_uc(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    @print_timing("selenium_dm_uc")
    def measure():

        @print_timing("selenium_dm_uc:view_page")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/pages/viewpage.action?pageId={app_specific_page_id}")
            title_locator = (By.ID, "title-text")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(title_locator))
            # Titel auslesen
            title_element = webdriver.find_element(*title_locator)
            page_title = title_element.text  # Hol Text des Titel-Elements
            print(f"XXXX Page Title: {page_title}")

            # Basierend auf dem Titel wird der Seiteninhalt überprüft
            if "UseCase Sections" in page_title:
                # Warten auf ein spezifisches Element, das nur auf der "UseCase Sections"-Seite existiert
                sections_locator = (By.ID, "div-UseCaseSections-Section1")
                WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(sections_locator))
                print("XXXX UseCase Sections Content loaded successfully")

            elif "UseCase Hide" in page_title:
                # Warten auf ein spezifisches Hide-Element
                hide_locator = (By.ID, "div-UseCaseHide-Hide_me_1")
                WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(hide_locator))
                print("XXXX UseCase Hide Content loaded successfully")

            elif "UseCase Definitionlist" in page_title:
                # Warten auf ein spezifisches Definitionlist-Element
                definitionlist_locator = (By.ID, "div-UseCaseDefinitionlist-DefinitionlistSection")
                WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(definitionlist_locator))
                print("XXXX UseCase Definitionlist Content loaded successfully")

            else:
                # Standardprüfung für andere Seiten
                print("XXXX Fehler. Unbekannte Seite")

        sub_measure()
    measure()
