import csv
import json
import sys
import logging
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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')

def login_to_confluence(url, username, password):
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

def csv_to_json(csv_file_path):
    data = {"property": []}

    with open(csv_file_path+"/performance_profile.csv", encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        for rows in csvReader:
            name = rows['Action']
            value = rows['with app']
            data["property"].append({
                "name": name,
                "value": value,
                "controls": "",
                "position": "after",
                "ref": "Sort Key" 
            })
    return json.dumps(data, indent=4)

def post_to_url(report_path, url, doctype, name, short_description, location, payload):
    # Define the query string parameters
    querystring = {
        "doctype": doctype,
        "name": name,
        "space-key": "pdacswad",
        "short-description": short_description,
        #"location": "Performance Measurements DC"
        "location": "{"+str(235340405)+"}"
    }

    login_url=smarticssecrets.url+"/login"
    session = login_to_confluence(login_url,smarticssecrets.username,smarticssecrets.password)

    response = session.get(smarticssecrets.url + "/rest/api/user/current")
    # print(response.text)
    print(smarticssecrets.url+url)
    print(querystring)
    # print(payload)
    response = session.post(smarticssecrets.url+url, params=querystring, json=payload)

    # Check the response status code
    if response.status_code == 200:
        print("POST request sent successfully!")
    else:
        print("Error sending POST request:", response.status_code)
        raise SmarticsException("Error sending POST request:", response.status_code)

    json_data = json.loads(response.text)
    page_id=json_data['id'];

    attach_file_to_page(session, page_id, report_path+"/performance_profile.png")


def attach_file_to_page(session, page_id, file_path):
    url = "/rest/api/content/{}/child/attachment".format(page_id)
    headers = {
        "X-Atlassian-Token": "no-check"
    }
    files = {
        'file': open(file_path, 'rb')
    }
    response = session.post(smarticssecrets.url+url, headers=headers, files=files)
    if response.status_code == 200:
        print("File attached successfully!")
    else:
        print("Error attaching file. Status code: {}".format(response.status_code))

location=sys.argv[1]
path_to_report=sys.argv[2]
name=sys.argv[3]

payload=csv_to_json(path_to_report)
payload_json=json.loads(payload)
section_content='''<ac:structured-macro ac:name="projectdoc-section" ac:schema-version="1"><ac:parameter ac:name="show-title">false</ac:parameter><ac:parameter ac:name="title">Description</ac:parameter><ac:rich-text-body><p><ac:image><ri:attachment ri:filename="performance_profile.png"/></ac:image></p></ac:rich-text-body></ac:structured-macro>'''
escaped_section_content = json.dumps(section_content)
image_section = '''{
    "section": [
        {
            "title": "Image",
            "content": %s,
            "position": "before",
            "ref": "References"
        }
    ]
}''' % escaped_section_content.replace('\n', '')
image_section_data = json.loads(image_section)
payload_json["section"] = image_section_data["section"]
post_to_url(path_to_report,"/rest/projectdoc/1/document.json","report",name,"my short desc",location, payload_json)
