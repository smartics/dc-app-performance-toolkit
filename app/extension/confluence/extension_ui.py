import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS

def verify_page_content(page_title, webdriver):
    """
    Überprüft den Seiteninhalt basierend auf dem Seitentitel und wartet auf spezifische Elemente.

    :param page_title: Der Titel der Seite, die überprüft werden soll
    :param webdriver: Der WebDriver, der für die Interaktionen verwendet wird
    """
    try:
        if "UseCase Sections" in page_title:
            # Warten auf ein spezifisches Element auf der "UseCase Sections"-Seite
            locator = (By.ID, "div-UseCaseSections-Section1")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(locator))
        elif "UseCase Hide" in page_title:
            # Warten auf ein spezifisches Hide-Element
            locator = (By.ID, "div-UseCaseHide-Hide_me_1")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(locator))
        elif "UseCase Definitionlist" in page_title:
            # Warten auf ein spezifisches Definitionlist-Element
            locator = (By.ID, "div-UseCaseDefinitionlist-DefinitionlistSection")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(locator))
        else:
            # Standardprüfung für unbekannte Seiten
            raise AssertionError("Unbekannte Seite (Elsezweig): "+page_title+" Test schlägt fehl.")
    except Exception as e:
        raise AssertionError("Unbekannte Seite: "+page_title+" Test schlägt fehl: "+e)


def dm_uc1(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    @print_timing("selenium_dm_uc1")
    def measure():

        @print_timing("selenium_dm_uc1:view_page")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/DOC/UseCase+Definitionlist")
            title_locator = (By.ID, "title-text")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(title_locator))
            # Titel auslesen
            title_element = webdriver.find_element(*title_locator)
            page_title = title_element.text  # Hol Text des Titel-Elements
            # Beispielaufruf:
            verify_page_content(page_title="UseCase Definitionlist", webdriver=webdriver)
        sub_measure()
    measure()

def dm_uc2(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    @print_timing("selenium_dm_uc2")
    def measure():

        @print_timing("selenium_dm_uc2:view_page")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/DOC/UseCase+Hide")
            title_locator = (By.ID, "title-text")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(title_locator))
            # Titel auslesen
            title_element = webdriver.find_element(*title_locator)
            page_title = title_element.text  # Hol Text des Titel-Elements
            # Beispielaufruf:
            verify_page_content(page_title="UseCase+Hide", webdriver=webdriver)
        sub_measure()
    measure()

def dm_uc3(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    @print_timing("selenium_dm_uc3")
    def measure():

        @print_timing("selenium_dm_uc3:view_page")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/DOC/UseCase+Sections")
            title_locator = (By.ID, "title-text")
            WebDriverWait(webdriver, 10).until(EC.presence_of_element_located(title_locator))
            # Titel auslesen
            title_element = webdriver.find_element(*title_locator)
            page_title = title_element.text  # Hol Text des Titel-Elements
            # Beispielaufruf:
            verify_page_content(page_title="UseCase+Sections", webdriver=webdriver)
        sub_measure()
    measure()
