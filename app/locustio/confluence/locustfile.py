from locust import HttpUser, task, between
import json
import os

# --------------------------------------------------------------------------------------------
#Hier muss alles mit from importiert werden, was unten genutzt werden soll
# smartics-US uncomment for Userscripts
# --------------------------------------------------------------------------------------------

from extension.confluence.extension_locust import app_specific_action_userscript_rest
from extension.confluence.extension_locust import app_specific_action

# --------------------------------------------------------------------------------------------
# smartics-dm uncomment for Userscripts
# --------------------------------------------------------------------------------------------

#from extension.confluence.extension_locust import app_specific_action_docm
from extension.confluence.extension_locust import app_specific_action_docm_section
from extension.confluence.extension_locust import app_specific_action_docm_hide
from extension.confluence.extension_locust import app_specific_action_docm_hidefromreader
from extension.confluence.extension_locust import app_specific_action_docm_hidefromanonymous
from extension.confluence.extension_locust import app_specific_action_docm_definitionlist

# --------------------------------------------------------------------------------------------
# smartics-Projectdoc uncomment for projectdoc Toolbox
# smartics-pd
# --------------------------------------------------------------------------------------------

from extension.confluence.extension_locust import app_specific_action_transclude_documents
from extension.confluence.extension_locust import app_specific_action_display_table

# --------------------------------------------------------------------------------------------
# smartics-Projectdoc uncomment for projectdoc Toolbox
# smartixs-pd
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# smartics uncomment for projectdoc toolbox extensions
# smartics-wa
# --------------------------------------------------------------------------------------------
from extension.confluence.extension_locust import app_specific_action_web_api

# --------------------------------------------------------------------------------------------
# smartics uncomment for projectdoc toolbox extensions
# smartics-is
# --------------------------------------------------------------------------------------------
from extension.confluence.extension_locust import app_specific_action_information_system


# --------------------------------------------------------------------------------------------
# smartics uncomment for projectdoc toolbox extensions
# smartics-bp
# --------------------------------------------------------------------------------------------
from extension.confluence.extension_locust import app_specific_action_check_blueprint_page

from locustio.common_utils import LocustConfig, MyBaseTaskSet
from locustio.confluence.http_actions import login_and_view_dashboard, view_dashboard, view_blog, \
    open_editor_and_create_blog, create_and_edit_page, comment_page, view_attachments, \
    upload_attachments, like_page, view_page, search_cql_two_words_and_view_results, search_cql_three_words
from util.conf import CONFLUENCE_SETTINGS

config = LocustConfig(config_yml=CONFLUENCE_SETTINGS)

# --------------------------------------------------------------------------------------------
# smartics-bp - Blueprint-Seiten aus JSON-Datei laden
# --------------------------------------------------------------------------------------------
def load_blueprint_pages():
    """Lädt Blueprint-Seiten aus der JSON-Datei"""
    blueprint_file = 'datasets/confluence/blueprint_pages.json'
    if os.path.exists(blueprint_file):
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                pages = json.load(f)
                print(f"Blueprint-Seiten aus Datei geladen: {len(pages)} Seiten")
                return pages
        except Exception as e:
            print(f"ERROR: Fehler beim Laden der Blueprint-Seiten: {e}")
            return []
    else:
        print(f"INFO: {blueprint_file} nicht gefunden. Führen Sie zuerst 'python util/data_preparation/confluence_prepare_data.py' aus.")
        return []

blueprint_pages = load_blueprint_pages()

class ConfluenceBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        login_and_view_dashboard(self)
        print(f"User gestartet - {len(blueprint_pages)} Blueprint-Seiten verfügbar")

    @task(config.percentage('view_page'))
    def view_page_action(self):
        view_page(self)

    @task(config.percentage('view_dashboard'))
    def view_dashboard_action(self):
        view_dashboard(self)

    @task(config.percentage('view_blog'))
    def view_blog_action(self):
        view_blog(self)

    @task(config.percentage('search_cql'))
    def search_cql_action(self):
        search_cql_two_words_and_view_results(self)

    @task(config.percentage('search_cql'))
    def search_cql_action_three_words(self):
        search_cql_three_words(self)

    @task(config.percentage('create_blog'))
    def create_blog_action(self):
        open_editor_and_create_blog(self)

    @task(config.percentage('create_and_edit_page'))
    def create_and_edit_page_action(self):
        create_and_edit_page(self)

    @task(config.percentage('comment_page'))
    def comment_page_action(self):
        comment_page(self)

    @task(config.percentage('view_attachment'))
    def view_attachments_action(self):
        view_attachments(self)

    @task(config.percentage('upload_attachment'))
    def upload_attachments_action(self):
        upload_attachments(self)

    @task(config.percentage('like_page'))
    def like_page_action(self):
        like_page(self)

# smartics Allgemeiner Hinweis the name in quotes can be configured in confluence.yml line 40ff
    #    @task(config.percentage('standalone_extension'))
    #    def custom_action_docm(self):
    #        app_specific_action_docm(self)


# smartics comment uncomment bei Bedarf

# --------------------------------------------------------------------------------------------------------------------
# smartics-pd
# --------------------------------------------------------------------------------------------------------------------

    @task(config.percentage('standalone_extension_transclude_documents'))
    def custom_action_transclude_documents(self):
        app_specific_action_transclude_documents(self)

    @task(config.percentage('standalone_extension_display_table'))
    def custom_action_display_table(self):
        app_specific_action_display_table(self)

# --------------------------------------------------------------------------------------------------------------------
# smartics-is
# --------------------------------------------------------------------------------------------------------------------

    @task(config.percentage('standalone_extension_information_system'))
    def custom_action_information_system(self):
        app_specific_action_information_system(self)

# --------------------------------------------------------------------------------------------------------------------
# smartics-wa
# --------------------------------------------------------------------------------------------------------------------

    @task(config.percentage('standalone_extension_web_api'))
    def custom_action_web_api(self):
        app_specific_action_web_api(self)

    @task(config.percentage('standalone_extension_blueprints'))
    def custom_action_blueprints(self):
        global blueprint_pages
        if blueprint_pages:
            app_specific_action_check_blueprint_page(self, blueprint_pages)
        else:
            print("WARNING: Keine Blueprint-Seiten verfügbar. Führen Sie zuerst 'python util/data_preparation/confluence_prepare_data.py' aus.")

# --------------------------------------------------------------------------------------------------------------------
# smartics-us
# --------------------------------------------------------------------------------------------------------------------

    @task(config.percentage('standalone_extension_us_rest_content'))
    def custom_action_userscript_rest(self):
        app_specific_action_userscript_rest(self)

#    @task(config.percentage('standalone_extension'))
#    def custom_action(self):
#        app_specific_action(self)

# --------------------------------------------------------------------------------------------------------------------
# smartics-dm
# --------------------------------------------------------------------------------------------------------------------

    @task(config.percentage('standalone_extension_section'))
    def custom_action_section(self):
        app_specific_action_docm_section(self)

    @task(config.percentage('standalone_extension_hide'))
    def custom_action_hide(self):
        app_specific_action_docm_hide(self)

    @task(config.percentage('standalone_extension_hidefromreader'))
    def custom_action_hidefromreader(self):
        app_specific_action_docm_hidefromreader(self)

    @task(config.percentage('standalone_extension_hidefromanonymous'))
    def custom_action_hidefromanonymous(self):
        app_specific_action_docm_hidefromanonymous(self)

    @task(config.percentage('standalone_extension_definitionlist'))
    def custom_action_definitionlist(self):
        app_specific_action_docm_definitionlist(self)

class ConfluenceUser(HttpUser):
    host = CONFLUENCE_SETTINGS.server_url
    tasks = [ConfluenceBehavior]
    wait_time = between(0, 0)