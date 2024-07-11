from locust import HttpUser, task, between

# smartics uncomment for userscripts
# from extension.confluence.extension_locust import app_specific_action_userscript_rest
# from extension.confluence.extension_locust import app_specific_action

# smartics comment in / out what you want to test. Must be synchron to the file(s) above
# from extension.confluence.extension_locust import app_specific_action_docm

# from extension.confluence.extension_locust import app_specific_action_docm_section
# from extension.confluence.extension_locust import app_specific_action_docm_hide
# from extension.confluence.extension_locust import app_specific_action_docm_hidefromreader
# from extension.confluence.extension_locust import app_specific_action_docm_hidefromanonymous
# from extension.confluence.extension_locust import app_specific_action_docm_definitionlist

# smartics uncomment for projectdoc toolbox
from extension.confluence.extension_locust import app_specific_action_transclude_documents
from extension.confluence.extension_locust import app_specific_action_display_table

# smartics uncomment for projectdoc toolbox extensions
from extension.confluence.extension_locust import app_specific_action_web_api
from extension.confluence.extension_locust import app_specific_action_information_system

from locustio.common_utils import LocustConfig, MyBaseTaskSet
from locustio.confluence.http_actions import login_and_view_dashboard, \
    view_dashboard, view_blog, \
    search_cql_and_view_results, open_editor_and_create_blog, \
    create_and_edit_page, comment_page, view_attachments, \
    upload_attachments, like_page, view_page
from util.conf import CONFLUENCE_SETTINGS

# smartics
config = LocustConfig(config_yml=CONFLUENCE_SETTINGS)


class ConfluenceBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        login_and_view_dashboard(self)

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
        search_cql_and_view_results(self)

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

    # smartics the name in quotes can be configured in confluence.yml line 40ff

    #    @task(config.percentage('standalone_extension'))
    #    def custom_action_docm(self):
    #        app_specific_action_docm(self)


'''
# smartics uncomment for userscripts
    @task(config.percentage('standalone_extension_us_rest_content'))
    def custom_action_userscript_rest(self):
        app_specific_action_userscript_rest(self)

    @task(config.percentage('standalone_extension'))
    def custom_action_is(self):
        app_specific_action(self)
'''

'''
    # smartics uncomment for documentationmacros
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

'''

    @task(config.percentage('standalone_extension_transclude_documents'))
    def custom_action_transclude_documents(self):
        app_specific_action_transclude_documents(self)


    @task(config.percentage('standalone_extension_display_table'))
    def custom_action_display_table(self):
        app_specific_action_display_table(self)

    @task(config.percentage('standalone_extension_information_system'))
    def custom_action_information_system(self):
        app_specific_action_information_system(self)

    # smartics uncomment for projectdoc toolbox extensions
    @task(config.percentage('standalone_extension_web_api'))
    def custom_action_web_api(self):
        app_specific_action_web_api(self)

class ConfluenceUser(HttpUser):
    host = CONFLUENCE_SETTINGS.server_url
    tasks = [ConfluenceBehavior]
    wait_time = between(0, 0)
