# Memphis Bamboo Build Plans for Dr Memory 1.0
# Author: ShyamJ
"""This module is responsible for triggering bamboo build plans for running DrMemory for driver.

This triggers the bamboo build plan for DrMemory.

  Typical usage example:
  $ python DrMemory.py <CommandLineArgs>
"""
import os
import codecs
import urllib
import requests
import getpass
import base64
import xml.etree.cElementTree as et
import webbrowser
import zipfile
import stat
import time
import smtplib
import sys
from json import load
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename
from atlassian import Bamboo


class DrMemoryTask:

    """Read inputs from JSON file and command line arguments and set in variables"""
    def __init__(self, username, password, email, outlook_password, shared_folder_path, input_args: dict):
        self.input_args = input_args
        self.driver_label = input_args['inBambooConfigs']['inDriverLabel']
        self.core_label = input_args['inBambooConfigs']['inCoreLabel']
        self.sen_label = input_args['inBambooConfigs']['inSENLabel']
        self.branch_name = input_args['inBambooConfigs']['inBranchName']
        self.excludeCompile = input_args['ExcludeCompilation']
        self.atlassian_user = username
        self.atlassian_password = password
        self.receiver_email = email
        self.outlook_password = outlook_password
        self.shared_folder_path = shared_folder_path

    """Triggers bamboo plan"""
    def build(self, projectKey):
        # base64 encode user and pass
        user_pass = self.atlassian_user + ':' + self.atlassian_password
        base_64_val = base64.b64encode(user_pass.encode()).decode()
        bamboo_url = os.environ.get("http://bergamot3.lakes.ad:8085", "http://bergamot3.lakes.ad:8085")

        # Creates the bamboo object with user credentials for sending http requests
        bamboo = Bamboo(url=bamboo_url, username=self.atlassian_user, password=self.atlassian_password)

        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/" + projectKey
        if url is not None:
            # get branch info for Compile/FT plan for win32 platform
            branch_info = bamboo.get_branch_info(
                          "BULDOMEM-WIN2012R2VS000201532" if projectKey == "BULDOMEM" else "TSTFOMEM-WIN2012R26432M",
                          self.branch_name)
            branch_key = branch_info['key']

            # Trigger Bamboo build
            bamboo.execute_build(branch_key, **self.get_params())
            print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' ODBC in windows platform')

            # Get url with Job ID of currently running plan
            url = update_job_id(branch_info['latestResult']['link']['href'])
            self.open_browser(url)

            # Check and wait until the plan is finished
            self.check_plan_status(url, base_64_val)

            # Get and parse the logs for Functional Test
            if projectKey == "TSTFOMEM":
                data = urllib.request.urlopen(
                       url.replace('rest/api/latest/result', 'browse') + "/artifact/JOB/Logs/build.txt")
                path = data.readlines()[1].strip().decode('utf-8')
                path = path.replace('oak', 'oak.simba.ad')
                self.get_logs(path)
            return True
        else:
            print(self.project + ' project not found. Please verify the project key.')
            return False

    """Bamboo Variables to be set before triggering the plan"""
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
            "MEMORY_TEST": 1,
            "AFL": 0,
            "VERACODE": 0,
            "CODE_ANALYSIS": 0,
            "COMPILER": 'vs2015',
            "BUILD_SOURCE": 'w2012r2'
        }
        return params

    """Open a browser with plan url"""
    def open_browser(self, url: str):
        url = url.replace('rest/api/latest/result', 'browse')
        webbrowser.open(url, new=2)

    """Check and wait until the current plan is finished with Fail/Success"""
    def check_plan_status(self, url, base_64_user_pass):
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }
        if url.find("BULD") != -1:
            print("Compile plan (with MEM) is running and in progress")
        else:
            print("Functional test plan (with DrMemory) is running and in progress")
        status = ""
        lifeCycleState = ""

        # Loop until the current plan's Status is Failed/Successful
        while True:
            response = requests.request("GET", url, data=payload, headers=headers)
            root = et.fromstring(response.content)
            lifeCycleState = root.attrib['lifeCycleState']
            for buildState in root.iter('buildState'):
                status = buildState.text
            if status != "Unknown" or lifeCycleState == "NotBuilt":
                break
            time.sleep(60)

        # If compile plan failed then notify about same and exit
        if status == "Failed" and url.find("BULD") != -1:
            raise Exception('The Compile plan is Failed. Please Check it and re-solve the errors if any.')
        # If plan is failed then notify about same and exit
        elif status == "Unknown" and lifeCycleState == "NotBuilt":
            raise Exception('The plan has stopped in the middle of the process. Re-run it.')

        print("Bamboo Plan Execution Finished with result: " + status)

    """Get and parse the logs"""
    def get_logs(self, filePath):
        # read path from Shared folder
        remotezip = self.shared_folder_path + filePath[filePath.find("\\archive\\"):] + "\\log.zip"

        # open remote log.zip file
        os.chmod(remotezip, 0o777)
        zip = zipfile.ZipFile(remotezip)
        files = []
        for fn in zip.namelist():
            # parse all results.txt files inside log.zip
            if fn.endswith("results.txt"):
                file = zip.read(fn).decode("utf-8")
                # File(including parsed results) naming format is Env_TestSet_TestSuite (i.e. TestEnv_SQL_TestSuite)
                fileName = sys.argv[1] + "\\" + fn[fn.find("memoryReport/") + 13:fn.find("/DrMemory-Touchstone.exe")]
                f = open(fileName, "w+")
                found = 0
                # Loop through each line in results.txt and parse
                for line in file.split("\n"):
                    # If the error is from Memphis datasource/core then include it in Parsed results
                    if "# 0 " in line and "\\drivers\\memphis" in line:
                        errors = "\n" + prevLine
                        found = 1
                    # Continue looping until we scan all the stack traces of current error and finally write it to file
                    if found == 1:
                        if line != "\r":
                            errors += line
                            continue
                        else:
                            found = 0
                            f.write(errors)
                    prevLine = line

                # only prepare parsed results file if there is at least 1 error in the parsed results
                if os.stat(f.name).st_size > 0:
                    files.append(fileName)
                f.close()

        # Send all parsed results files as attachments in mail
        #self.send_mail(files)

    """Send an email"""
    def send_mail(self, attachments):
        SERVER = "smtp-mail.outlook.com"
        USER = self.receiver_email[:self.receiver_email.find("@")]
        FROM = USER + "@insightsoftware.com"
        TO = [self.receiver_email]  # must be a list
        print(USER)
        print(FROM)
        print(TO)
        # Prepare actual message
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = COMMASPACE.join(TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "DrMemory Report"

        msg.attach(MIMEText("Hey!\r\n Here is your memory report from DrMemory.\r\n Thanks."))
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
        server.login(USER + "@insightsoftware.com", self.outlook_password)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()

"""Update JOB ID in url to the currently executing plan's Job Id"""
def update_job_id(url):
    job_id = url.split("-")[-1]
    url = url[0: len(url) - len(job_id)] + str(int(job_id) + 1)
    return url

"""Read input JSON file, Loop through each Project (i.e. Compile / FT) and build it on bamboo"""
def run_bamboo_adapter_build(input_args: dict):
    print("Building driver/adapter on bamboo...BEGIN")
    bamboo_build = DrMemoryTask(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], input_args)
    projectKeys = ["TSTFOMEM"]
    # check whether Compile plan needs to be triggered before FT
    if not bamboo_build.excludeCompile:
        projectKeys.insert(0, "BULDOMEM")
    for projectKey in projectKeys:
        if bamboo_build.build(projectKey):
            print("Please go through the logs generated on bamboo for further reference.")
        else:
            print("Please check the input parameters and try again.")

def main():
    # sys.argv[1] is current working directory
    input_json_file = sys.argv[1] + '\\' + sys.argv[7]
    if not os.path.exists(input_json_file):
        print("IMPORTANT: Please ensure to modify user_input.json as per your "
              "needs prior to running this.")
        input_json_file = input("Please enter the full path to the input json "
                                "file (e.g., C:\\user_input.json): ")
    f = open(input_json_file)
    run_bamboo_adapter_build(load(f))

if __name__ == '__main__':
    main()
