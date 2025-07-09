from locust import HttpUser, task, between
# smartics-US
from extension.confluence.extension_locust import app_specific_action_userscript_rest
from extension.confluence.extension_locust import app_specific_action

#smartics comment in / out what you want to test. Must be synchron to the file(s) above
#from extension.confluence.extension_locust import app_specific_action_docm

#from extension.confluence.extension_locust import app_specific_action_docm_section
#from extension.confluence.extension_locust import app_specific_action_docm_hide
#from extension.confluence.extension_locust import app_specific_action_docm_hidefromreader
#from extension.confluence.extension_locust import app_specific_action_docm_hidefromanonymous
#from extension.confluence.extension_locust import app_specific_action_docm_definitionlist

#from extension.confluence.extension_locust import app_specific_action_td
#from extension.confluence.extension_locust import app_specific_action_dt
#from extension.confluence.extension_locust import app_specific_action_wa
#from extension.confluence.extension_locust import app_specific_action_is



from locustio.common_utils import LocustConfig, MyBaseTaskSet
from locustio.confluence.http_actions import login_and_view_dashboard, view_dashboard, view_blog, \
    open_editor_and_create_blog, create_and_edit_page, comment_page, view_attachments, \
    upload_attachments, like_page, view_page, search_cql_two_words_and_view_results, search_cql_three_words
from util.conf import CONFLUENCE_SETTINGS

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
        search_cql_two_words_and_view_results(self)

    @task(config.percentage('search_cql'))
    def search_cql_action(self):
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

    #smartics the name in quotes can be configured in confluence.yml line 40ff

    #    @task(config.percentage('standalone_extension'))
    #    def custom_action_docm(self):
    #        app_specific_action_docm(self)

    @task(config.percentage('standalone_extension_us_rest_content'))
    def custom_action_userscript_rest(self):
        app_specific_action_userscript_rest(self)

    @task(config.percentage('standalone_extension'))
    def custom_action_is(self):
        app_specific_action(self)


'''
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

    @task(config.percentage('standalone_extension'))
    def custom_action_dt(self):
        app_specific_action_dt(self)

#    @task(config.percentage('standalone_extension'))
#    def custom_action_td(self):
#        app_specific_action_td(self)

#    @task(config.percentage('standalone_extension'))
#    def custom_action_wa(self):
#        app_specific_action_wa(self)

#    @task(config.percentage('standalone_extension'))
#    def custom_action_is(self):
#        app_specific_action_is(self)
'''

class ConfluenceUser(HttpUser):
    host = CONFLUENCE_SETTINGS.server_url
    tasks = [ConfluenceBehavior]
    wait_time = between(0, 0)