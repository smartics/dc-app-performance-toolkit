import csv
import json
import sys
import logging
import yaml
import os
import glob
import subprocess
from atlassian import Confluence
from typing import Dict

import requests
from requests.auth import HTTPBasicAuth
import smarticssecrets

# set username and password and url in smarticssecrets
#e.g.:
#username="anton.kronseder"
#password="XXXXX"
#url="https://www.smartics.eu/confluence"


class SmarticsException(Exception):
    pass

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')

def login_to_confluence(url, username, password):
    """
    Login to a Confluence instance.

    This function logs into a Confluence instance given a base URL, username, and password.
    It creates a new session and logs in using a POST request to the login endpoint.
    The function then returns the requests session object for further interactions with the Confluence instance.

    Parameters:
    url (str): The base URL of the Confluence instance (e.g., "https://my-domain.atlassian.net").
    username (str): The username to log in with.
    password (str): The password to log in with.

    Returns:
    session (requests.Session): A session object for interacting with the Confluence instance.
    """
    # Define the login URL and credentials
    login_url = url + "/login.action"
    data = {
        "os_username": username,
        "os_password": password,
        "login": "Log In",
    }

    # Send the POST request with the login data
    session = requests.Session()
    session.post(login_url, data=data)

    # Return the session object
    return session

def dictionary_to_projectdoc_json(csvDictionary):
    data = {"property": []}
    for key, value in csvDictionary.items():
        name = key
        value = value
        data["property"].append({
            "name": name,
            "value": value,
            "controls": "",
            "position": "after",
            "ref": "Sort Key"
        })
    return data

def sort_keys_in_properties_order(key):
    sorting_order = {
        'server-information-': 0,
        'bzt-settings': 1,
        'projectdoc-version-information-': 2,
        'app_specific_action': 3
    }

    for k, v in sorting_order.items():
        if k in key:
            return (v, key)
    return (4, key)

def flatten_csv(input_data):
    reader = csv.reader(input_data)
    header = next(reader)
    output_rows: dict[str, str] = {}
    for row in reader:
    # Skip if row is empty or contains only whitespaces and newline characters
        if not row or not any(x.strip() for x in row):
            continue
        label = row[0]
        for i in range(1, len(row)):
            new_key = (label + '-' + header[i]).replace(' ', '_')
            new_value = row[i]
            output_rows[new_key] = new_value
    return output_rows

def post_to_url(session, url, querystring={}, payload={}, headers={}):

    if querystring == {}:
        if payload == {}:
            if headers == {}:
                response = session.post(url)
            else:
                response = session.post(url, headers=headers)
        else:
            if headers == {}:
                response = session.post(url, json=payload)
            else:
                response = session.post(url, json=payload, headers=headers)
    else:
        if payload == {}:
            if headers == {}:
                response = session.post(url, params=querystring)
            else:
                response = session.post(url, params=querystring, headers=headers)
        else:
            if headers == {}:
                response = session.post(url, params=querystring, json=payload)
            else:
                response = session.post(url, params=querystring, json=payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        logging.debug("POST request sent successfully!")
    else:
        logging.debug("Error sending POST request:", response.status_code)
        raise SmarticsException("Error sending POST request:", response.status_code, response.text)

    json_data = json.loads(response.text)
    return json_data


def create_and_attach_to_page(session, report_path, url, attachment_rest_url, file_to_attach, doctype, name, short_description, location, payload):
    # Define the query string parameters
    querystring = {
        "doctype": doctype,
        "name": name,
        "space-key": "pdacswad",
        "short-description": short_description,
        #"location": "Performance Measurements DC"
        "location": "{"+str(location)+"}"
    }

    response = session.post(url, params=querystring, json=payload)

    # Check the response status code
    if response.status_code == 200:
        logging.debug("POST request sent successfully!")
    else:
        logging.debug("Error sending POST request:", response.status_code)
        raise SmarticsException("Error sending POST request:", response.status_code)

    json_data = json.loads(response.text)
    page_id=json_data['id'];
    attach_file_to_page(session, attachment_rest_url, page_id, file_to_attach)


def attach_file_to_page(session, attachment_rest_url, page_id, file_path):
    logging.debug("Attaching file to page..."+file_path)
    attachment_rest_url = attachment_rest_url.format(page_id)
    logging.debug(attachment_rest_url)
    headers = {
        "X-Atlassian-Token": "no-check"
    }
    files = {
        'file': open(file_path, 'rb')
    }
    response = session.post(attachment_rest_url, headers=headers, files=files)
    if response.status_code == 200:
        logging.debug("File attached successfully!")
    else:
        logging.debug("Error attaching file. Status code: {}".format(response.status_code))


def fetch_projectdoc_versions_data(session, url, keyword):
    response = session.get(url)
    data = json.loads(response.text)
    # Dictionary to store the versions that contain 'projectdoc'.
    versions = {}
    for plugin in data['plugins']:
        if keyword in plugin['key']:
            version, date = (plugin['version'].split("-", 1) + ["RELEASE"])[:2]
            versions["projectdoc-version-information-"+plugin['key']+"#"] = plugin['version']
            versions["projectdoc-version-information-"+plugin['key']+"$"] = version
            versions["projectdoc-version-information-"+plugin['key']+"%"] = date
    return versions


def fetch_confluence_server_info(session, url, headers):
    server_infos = post_to_url(session, url , headers=headers)
    server_info = {}
    for info in server_infos.items():
        server_info["server-information-" + info[0]] = info[1]
    server_info["server-information-fullVersion"] = str(server_info[
                                                       "server-information-majorVersion"]) + "." + \
                                                   str(server_info[
                                                       "server-information-minorVersion"]) + "." + \
                                                   str(server_info[
                                                       "server-information-patchLevel"])
    return server_info

def fetch_bzt_settings(url):
    with open(url, 'r') as file:
        effective_yml = yaml.safe_load(file)
    settings = {}
    settings["bzt-settings-version"] = effective_yml["version"]
    settings["bzt-settings-TAURUS_ARTIFACTS_DIR"] = \
        effective_yml["settings"]["env"]["TAURUS_ARTIFACTS_DIR"]
    settings["bzt-settings-application_hostname"] = \
        effective_yml["settings"]["env"]["application_hostname"]
    settings["bzt-settings-custom_dataset_query"] = \
        effective_yml["settings"]["env"]["custom_dataset_query"]
    settings["bzt-settings-ramp-up"] = effective_yml["settings"]["env"][
        "ramp-up"]
    settings["bzt-settings-test_duration"] = effective_yml["settings"]["env"][
        "test_duration"]
    settings["bzt-settings-total_actions_per_hour"] = \
        effective_yml["settings"]["env"]["total_actions_per_hour"]
    return settings

def check_login(session, url, system_name):
    response = session.get(url)
    if response.status_code == 200 and "username" in response.text:
        logging.debug(f"Login to {system_name} successful!")  # 200 = OK
        logging.debug(f"Login to {system_name} successful!")
        logging.debug(response.text)
    else:
        logging.debug(f"Login to {system_name} failed. Status code: {response.status_code}")
        raise SmarticsException(f"Login to documentation system failed. Status code: {response.status_code}")



def replace_vars_in_yaml(source_file, target_file, baseline, newversion, confluence_version, projectdoc_version):
    # Read YAML file
    with open(source_file, 'r') as yaml_file:
        yaml_content = yaml_file.read()

    # Replace the placeholders
    yaml_content = yaml_content.replace("${baseline}", baseline)
    yaml_content = yaml_content.replace("${newversion}", newversion)
    yaml_content = yaml_content.replace("${confluence_version}", confluence_version)
    yaml_content = yaml_content.replace("${projectdoc_version}", projectdoc_version)

    # Write the changes back to the file
    with open(target_file, 'w') as yaml_file:
        yaml_file.write(yaml_content)


def generate_report(template, target, base_line, path_to_last_run, confluence_version, projectdoc_version):
    replace_vars_in_yaml(template, target, base_line.replace("\\", "/"),
                         path_to_last_run.replace("\\", "/"),
                         confluence_version, projectdoc_version)
    # Get the current directory
    cwd = os.getcwd()
    script_dir = os.path.join(cwd, "reports_generation")
    venv_dir = os.path.join(os.path.dirname(cwd), "venv2")
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    script_path = os.path.join(script_dir, "csv_chart_generator.py")
    logging.debug("Running script: " + script_path)
    logging.debug("Using python executable: " + python_exe)
    logging.debug("Using config file: " + target)
    subprocess.call([python_exe, script_path, target.replace("\\", "/")],
                    cwd=script_dir)

#read commandline
location=sys.argv[1]
confluence_performance_document_name=sys.argv[2]

results_dir = "results/confluence/"
reports_dir = "results/reports/"
base_line = os.path.join(os.getcwd(), results_dir, 'baseline')
latest_dirs = sorted(glob.glob(os.path.join(os.getcwd(), results_dir, '*/')), key=os.path.getmtime, reverse=True)
latest_dir = latest_dirs[0] if latest_dirs else None
path_to_last_run = os.path.normpath(latest_dir)

template = os.path.join(os.getcwd(), "reports_generation/performance_profile-orig.yml")
target = os.path.join(os.getcwd(), "reports_generation/performance_profile.yml")

latest_report_dirs = sorted(glob.glob(os.path.join(os.getcwd(), reports_dir, '*/')), key=os.path.getmtime, reverse=True)
latest_report_dir = latest_report_dirs[0] if latest_report_dirs else None
path_to_last_report = os.path.normpath(latest_report_dir)

# #prepare data
effective_config_yml=path_to_last_run + "/effective.yml"
results_csv = path_to_last_run+"/results.csv"

#prepare data
documentation_system_url= smarticssecrets.documentation_system_url
documentation_system_create_projectdoc_document_url=documentation_system_url+"/rest/projectdoc/1/document.json"
documentation_system_check_login_url=documentation_system_url + "/rest/api/user/current"
documentation_system_username= smarticssecrets.documentation_system_username
documentation_system_password= smarticssecrets.documentation_system_password

system_under_test_url= smarticssecrets.system_under_test_url
system_under_test_username= smarticssecrets.system_under_test_username
system_under_test_password= smarticssecrets.system_under_test_password
system_under_test_check_login_url=system_under_test_url + "/rest/api/user/current"

#login to documentation_system
documentation_system_login_url=documentation_system_url + "/login"
documentation_system_session = login_to_confluence(documentation_system_login_url,documentation_system_username,documentation_system_password)
check_login(documentation_system_session, documentation_system_check_login_url, "documentation system")

#login to system_under_test
system_under_test_login_url=system_under_test_url + "/login"
system_under_test_session = login_to_confluence(system_under_test_login_url,system_under_test_username,system_under_test_password)
check_login(system_under_test_session, system_under_test_check_login_url, "system under test")

system_under_test_upm_plugins_url=system_under_test_url + "/rest/plugins/1.0/"
system_under_test_server_info_url=system_under_test_url + "/rpc/json-rpc/confluenceservice-v2/getServerInfo"

#confluence = Confluence(
#    url=system_under_test_url,
#    username='anton.kronseder',
#    password='weltkome')
#existing = confluence.page_exists("PROJECTDOCTEST", "Informationsystemtest")



#fetch metadata

bzt_settings=fetch_bzt_settings(effective_config_yml)
server_info = fetch_confluence_server_info(system_under_test_session, system_under_test_server_info_url, headers={"Content-Type":"application/json"})
projectdoc_versions = fetch_projectdoc_versions_data(system_under_test_session, system_under_test_upm_plugins_url, "projectdoc")

properties_dictionary = flatten_csv(open(results_csv, encoding='utf-8'))
properties_dictionary.update(bzt_settings)
properties_dictionary.update(server_info)
properties_dictionary.update(projectdoc_versions)
property_keys = properties_dictionary.keys()

# sort the dictionary keys using the custom function
sorted_keys = sorted(property_keys, key=sort_keys_in_properties_order)
# reverse the list to get descending order
sorted_keys.reverse()
# create a new dictionary using sorted keys
sorted_properties_dictionary = {key: properties_dictionary[key] for key in sorted_keys}
payload=dictionary_to_projectdoc_json(sorted_properties_dictionary)
payload_json=json.loads(json.dumps(payload))

section_content='''<ac:structured-macro ac:name="projectdoc-section" ac:schema-version="1"><ac:parameter ac:name="show-title">false</ac:parameter><ac:parameter ac:name="title">Description</ac:parameter><ac:rich-text-body><p><ac:image><ri:attachment ri:filename="performance_profile.png"/></ac:image></p></ac:rich-text-body></ac:structured-macro>'''
escaped_section_content = json.dumps(section_content)
image_section = {
    "section": [
        {
            "title": "Image",
            "content": escaped_section_content.replace('\n', ''),
            "position": "before",
            "ref": "References"
        }
    ]
}

payload_json.update(image_section)

generate_report(template, target, base_line, path_to_last_run,server_info["server-information-fullVersion"], projectdoc_versions["projectdoc-version-information-de.smartics.atlassian.confluence.smartics-projectdoc-confluence#"])

attachment_rest_url = documentation_system_url + "/rest/api/content/{}/child/attachment"
file_to_attach = path_to_last_report + "/performance_profile.png"

create_and_attach_to_page(documentation_system_session, path_to_last_report,documentation_system_create_projectdoc_document_url, attachment_rest_url, file_to_attach,"report",confluence_performance_document_name,"my short desc",location, payload_json)
