# Memphis Bamboo Build Plans 1.0
# Author: ShubhamS
"""This module is responsible for triggering bamboo build plans for driver/adapter.
This triggers the bamboo build plan.
  Typical usage example:
  $ python BambooBuildPlans.py
  And follow the on-screen instructions.
"""
import os
from json import load

import codecs
import urllib
import requests
import getpass
import base64
import xml.etree.cElementTree as et
import webbrowser
from socket import *

import zipfile
import shutil
import os, stat
import urllib
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
from os.path import basename
import sys

from atlassian import Bamboo


class AppVerifierTask:

    def __init__(self, username, password, email, office_password, shared_folder_path, input_args: dict):
        self.input_args = input_args
        self.driver_label = input_args['inBambooConfigs']['inDriverLabel']
        self.core_label = input_args['inBambooConfigs']['inCoreLabel']
        self.sen_label = input_args['inBambooConfigs']['inSENLabel']
        self.testsuite_list=input_args['inBambooConfigs']['inTestSuiteList']
        #self.windows_build_configs = input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inPlatform'] + " " + \
        #                             input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inCompiler'] + " " + \
        #                             input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inConfiguration']
        self.branch_name = input_args['inBambooConfigs']['inBranchName']
        self.excludeCompile = input_args['ExcludeCompilation']
        self.atlassian_user = username
        self.atlassian_password = password
        self.office_password = office_password
        self.receiver_email = email
        self.shared_folder_path = shared_folder_path

    def build(self, projectKey):
        user_pass = self.atlassian_user + ':' + self.atlassian_password
        base_64_val = base64.b64encode(user_pass.encode()).decode()
        bamboo_url = os.environ.get("http://bergamot3.lakes.ad:8085", "http://bergamot3.lakes.ad:8085")

        # Creates the bamboo object with user credentials for sending http requests
        bamboo = Bamboo(url=bamboo_url, username=self.atlassian_user, password=self.atlassian_password)
        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/" + projectKey
        if url is not None:
            #if len(self.windows_build_configs) > 2:
                # self.get_plan_key(url, base_64_val, self.windows_build_configs)
                branch_info = bamboo.get_branch_info(
                    "BULDOMEM-WIN2012R2VS000201332" if projectKey == "BULDOMEM" else "TSTFOMEM-WIN0020166432M",
                    self.branch_name)
                print(branch_info)
                branch_key = branch_info['key']
                bamboo.execute_build(branch_key, **self.get_params())
                print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' ODBC in windows platform')
                self.open_browser(branch_info['latestResult']['link']['href'])
                self.check_plan_status(branch_info['latestResult']['link']['href'].split("/")[-1], base_64_val)
                if projectKey == "TSTFOMEM":
                    data = urllib.request.urlopen(branch_info['latestResult']['link']['href'].replace('rest/api/latest/result', 'browse') + "/artifact/JOB/Logs/build.txt")
                    path = data.readlines()[1].strip().decode('utf-8')
                    path = path.replace('oak', 'oak.simba.ad')
                    self.get_logs(path)

                    return True
        else:
            print(self.project + ' project not found. Please verify the project key.')
            return False


# def get_plan_key(self, url, base_64_user_pass, build_configs):
#     payload = ""
#     headers = {
#         'Authorization': "Basic " + base_64_user_pass
#     }
#     params = {
#         "expand": "plans",
#         "max-result": 25,
#         "start-index": 0
#     }
#     while True:
#         response = requests.request("GET", url,params=params,data=payload, headers=headers)
#         tree = et.fromstring(response.content)
#         for child in tree.iter('*'):
#             try:
#                 if child.attrib.get('shortName').__contains__(build_configs):
#                     return child.attrib.get('key')
#             except:
#                 continue
#         params["start-index"]+=25

# def get_project_url(self, base_64_user_pass):
#     url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/" + self.project
#     if self.project != "":
#         return url
#     payload = ""
#     headers = {
#         'Authorization': "Basic " + base_64_user_pass
#     }
#
#     response = requests.request("GET", url, data=payload, headers=headers)
#     tree = et.fromstring(response.content)
#
#     found_proj = False
#     for child in tree.iter('*'):
#         if found_proj:
#             return child.attrib.get('href')
#         try:
#             if child.attrib.get('key').__contains__(self.project):
#                 found_proj = True
#                 key = child.attrib.get('key')
#         except:
#             continue

    def get_params(self):
        params = {
            "BOOSTER_LABEL": "__head__",
            "DRV_LABEL": self.driver_label,
            "CORE_LABEL": self.core_label,
            "SEN_LABEL": self.sen_label,
            "DYNAMIC_LINKING": 0,
            "RETAIL": 0,
            "PRODUCT_LABEL": "BAMBOO_DRV_LABEL",
            "DISBALE_PARENT_MATCH": 0,
            "TARGET": "release",
            "MEMORY_TEST": 0,
            "APPVERIFIER": 1,
            "TESTSUITE_LIST": self.testsuite_list,
            "AFL": 0,
            "VERACODE": 0,
            "CODE_ANALYSIS": 0,
            "COMPILER": 'vs2013',
            "BUILD_SOURCE": 'w2012r2'
        }
        return params


    def open_browser(self, url: str):
        job_id = int(url[len(url) - 1]) + 1
        url = url[0: len(url) - 1] + str(job_id)
        url = url.replace('rest/api/latest/result', 'browse')
        webbrowser.open(url, new=2)


    def check_plan_status(self, build_key, base_64_user_pass):
        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/result/" + build_key
        job_id = int(url[len(url) - 1]) + 1
        url = url[0: len(url) - 1] + str(job_id)
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }
        if build_key.find("BULD") != -1:
            print("Compile plan (with MEM) is running and in progress")
        else:
            print("Functional test plan (with AppVerifier) is running and in progress")
        status = ""
        while True:
            response = requests.request("GET", url, data=payload, headers=headers)
            root = et.fromstring(response.content)
            for buildState in root.iter('buildState'):
                status = buildState.text
            if status != "Unknown":
                print("Bamboo Plan Execution Stopped")
                break
            time.sleep(60)
        print("Bamboo Plan Execution Finished with result: " + status)


    def get_logs(self, filePath):
        #print(filePath)
        #filePath=r"\\oak.simba.ad\build_archives\archive\TSTFOMEM-WIN0020166432M88\25"
        remotezip = self.shared_folder_path + filePath[filePath.find("\\archive\\"):] + "\\log.zip"
        #remotezip = urllib.request.urlopen(r"file:" + filePath + r"\\log.zip")
        #remotezip = r"\\oak.simba.ad\build_archives\archive\TSTFOMEM-WIN0020166432M88\12\log.zip"
        zip = zipfile.ZipFile(remotezip)
        files = []
        for fn in zip.namelist():
            if fn.find("test_output/appverifier") != -1:
                file = zip.read(fn).decode("utf-8")
                fileName = fn[fn.find("test_output/appverifier/") + 24:]
                if fileName != "":
                    f = open(fileName, "w+")
                    rdfodbcTracefound = 0
                    prevLine = ""
                    start = False
                    end = False
                    errors = ""
                    for line in file.split("\n"):
                        if ('Severity="Error"' in line):
                            start = True
                        if '</avrf:logEntry>' in line:
                            end = True
                        if start and not end:
                            errors += line + "\n"
                            if '<avrf:trace>RDFODBC_sb64' in line:
                                rdfodbcTracefound = 1
                        if start and end:
                            start = False
                            end = False
                            if rdfodbcTracefound:
                                print(errors)
                                f.write(errors)
                            rdfodbcTracefound = 0
                            errors = ""
                    if (os.stat(f.name).st_size > 0):
                        files.append(fileName)
                    f.close()
        print(files)            
        #self.send_mail(files)


    def send_mail(self, attachments):
        SERVER = "smtp-mail.outlook.com"
        FROM = "pcheemakurthi@magnitude.com"
        TO = [self.receiver_email]  # must be a list

        # Prepare actual message
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = ", ".join(TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "AppVerifier Report"

        msg.attach(MIMEText("Hey!\r\n Here is your AppVerifier report.\r\n Thanks.\r\n\n Note:There are no errors if the logs are not attached. \r\n\n"))
        # message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\
        for file in attachments or []:
            with open(file, "rb") as report:
                part = MIMEApplication(
                    report.read(),
                    Name=basename(file)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
            msg.attach(part)

        server = smtplib.SMTP(SERVER, 587)
        server.connect(SERVER, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("pcheemakurthi@magsw.com", self.office_password)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()

        """ % (FROM, ", ".join(TO), SUBJECT, TEXT) """

        # Send the mail


def run_bamboo_adapter_build(input_args: dict):
    print("Building driver/adapter on bamboo...BEGIN")
    bamboo_build = AppVerifierTask(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], input_args)
    projectKeys = ["TSTFOMEM"]
    if not bamboo_build.excludeCompile:
        projectKeys.insert(0, "BULDOMEM")
    for projectKey in projectKeys:
        if bamboo_build.build(projectKey):
            print("Please go through the logs generated on bamboo for further reference.")
        else:
            print("Please check the input parameters and try again.")


def main():
    input_json_file = sys.argv[1] + '\\user_input.json'
    if not os.path.exists(input_json_file):
        print("IMPORTANT: Please ensure to modify user_input.json as per your "
              "needs prior to running this.")
        input_json_file = input("Please enter the full path to the input json "
                                "file (e.g., C:\\user_input.json): ")
    f = open(input_json_file)
    run_bamboo_adapter_build(load(f))


if __name__ == '__main__':
    main()
