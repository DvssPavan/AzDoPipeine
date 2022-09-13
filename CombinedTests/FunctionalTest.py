"""This module is responsible for triggering bamboo build plans for Compile, OEM and FT plans.
  Typical usage example:
  $ python FTPlans.py <CommandLineArgs>
"""
import os
from json import load

import requests
import base64
import xml.etree.cElementTree as et
import webbrowser
import time
import urllib
import zipfile

import csv
from io import TextIOWrapper
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
from os.path import basename
from atlassian import Bamboo

class FTPlans:

    def __init__(self, username, password, outlook_username, outlook_password, email, shared_folder_path,
                 input_args: dict):
        self.input_args = input_args
        self.projects = input_args['inBambooConfigs']['inProjectKey']
        self.driver_label = input_args['inBambooConfigs']['inDriverLabel']
        self.core_label = input_args['inBambooConfigs']['inCoreLabel']
        self.sen_label = input_args['inBambooConfigs']['inSENLabel']
        self.driver_brand = input_args['inBambooConfigs']['inDriverBrand']
        self.booster_label = input_args['inBambooConfigs']['inBooster_Label']
        self.disable_parent_match = input_args['inBambooConfigs']['inDisableParentMatch']
        self.memory_test = input_args['inBambooConfigs']['inMemoryTest']
        self.retail = input_args['inBambooConfigs']['inRetail']
        self.app_verifier = input_args['inBambooConfigs']['inAppVerifier']
        self.testsuite_list = input_args['inBambooConfigs']['inTestSuiteList']
        self.build_configs = input_args['inBambooConfigs']['inBuildConfigs']
        self.branch_name = input_args['inBambooConfigs']['inBranchName']
        self.compiler = input_args['inBambooConfigs']['inCompiler']
        self.insight_desktop_label = input_args['inBambooConfigs']['inInsightDesktopLabel']
        self.insight_branch = input_args['inBambooConfigs']['inInsightBranch']
        self.atlassian_user = username
        self.atlassian_password = password
        self.outlook_username = outlook_username
        self.outlook_password = outlook_password
        self.receiver_email = email
        self.shared_folder_path = shared_folder_path

    def build(self):

        user_pass = self.atlassian_user + ':' + self.atlassian_password
        base_64_val = base64.b64encode(user_pass.encode()).decode()
        bamboo_url = os.environ.get("http://bergamot3.lakes.ad:8085", "http://bergamot3.lakes.ad:8085")

        # Creates the bamboo object with user credentials for sending http requests
        bamboo = Bamboo(url=bamboo_url, username=self.atlassian_user, password=self.atlassian_password)

        for x in range(len(self.build_configs)):
            project = self.projects[x]
            url = self.get_project_url(base_64_val, project)
            print(url)
            if not url == None:
                if len(self.build_configs[x]) > 2:
                    branch_info = bamboo.get_branch_info(
                        self.get_plan_key(url, base_64_val, self.build_configs[x]),
                        self.branch_name)
                    branch_key = branch_info['key']
                    bamboo.execute_build(branch_key, **self.get_params())
                    print('Bamboo build is started for ' + str(self.build_configs[x]) +
                          ' agent of ' + self.branch_name.split(' ')[0])
                    final_url, current_job_id = self.active_plan(branch_info['latestResult']['link']['href'], base_64_val)

                status = self.status_of_agent(final_url)
                if status == True or project[:3] == "TST":
                    # As Binscope test is a part of Compile plan for only `Windows` platform
                    # Logs Verification for Binscope should be done if and only if given Project Key is for Compile Plan and
                    # Platform is `Windows`
                    if status and project == 'BULDOMEM' and branch_info['shortKey'].startswith('WIN'):
                        self.verify_binscope_log(branch_key, current_job_id, bamboo_url)

                    # Generate logs if plan is FT
                    if project == "TSTFOMEM":
                        data = urllib.request.urlopen(
                            final_url.replace('rest/api/latest/result', 'browse')
                            + "/artifact/JOB/Logs/build.txt")

                        path = data.readlines()[1].strip().decode('utf-8')
                        path = path.replace('oak', 'oak.simba.ad')
                        self.get_logs(path)
                else:
                    print(self.build_configs[x] + ' agent is failed.')
                    return False

                if self.build_configs[x] == self.build_configs[-1]:
                    return True

            else:
                print(project + ' project not found. Please verify the project key.')
                return False

    def get_plan_key(self, url, base_64_user_pass, build_configs):
        url += '?expand=plans'
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass,
            'Accept': "application/json"
        }
        print("GetPlanKeyURL "+url)
        response = requests.request("GET", url, data=payload, headers=headers)
        tree = response.json()  # response format make as a json

        found_proj = False
        start_index, max_results, size = 0, int(tree['plans']['max-result']), int(tree['plans']['size'])

        # traverse all the plan for the project using pagination
        while start_index <= size:
            if 'plans' in tree and tree['plans'] is not None and tree['plans']['size'] > 0:
                for plan in tree['plans']['plan']:
                    if plan['shortName'] == build_configs:
                        found_proj = True
                        break
                if found_proj:
                    return plan['key']  # return key value of the plan
                else:
                    start_index = int(tree['plans']['start-index'])
                    start_index = start_index + max_results  # set start_index for the next page

            # update the url for new start-index
            response = requests.request("GET", f"{url}&start-index={start_index}", data=payload, headers=headers)
            tree = response.json()

    def get_project_url(self, base_64_user_pass, project):
        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/"
        url += project
        print("GetProjectURL "+url)
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }

        response = requests.request("GET", url, data=payload, headers=headers)

        if response.status_code != 200:
            return None
        return url

    def get_params(self):

        params = {
            "BOOSTER_LABEL": "__head__",
            "DRV_LABEL": self.driver_label,
            "CORE_LABEL": self.core_label,
            "SEN_LABEL": self.sen_label,
            "DRV_BRAND": self.driver_brand,
            "DISABLE_PARENT_MATCH": self.disable_parent_match if self.disable_parent_match != "" else 0,
            "DYNAMIC_LINKING": 0,
            "RETAIL": self.retail if self.retail != "" else 0,
            "PRODUCT_LABEL": "BAMBOO_DRV_LABEL",
            "TARGET": "release",
            "COMPILER": self.compiler,
            "TESTSUITE_LIST": self.testsuite_list if self.testsuite_list != "" else "",
            "AFL": 0,
            "VERACODE": 0,
            "CODE_ANALYSIS": 0,
            "INSIGHT_DESKTOP_LABEL": self.insight_desktop_label if self.insight_desktop_label != "" else "",
            "INSIGHT_BRANCH": self.insight_branch if self.insight_branch != "" else ""
        }

        params1 = {}

        # consider only non empty parameters.
        for i in params.keys():
            if params[i] != "":
                params1[i] = params[i]
        return params1

    def active_plan(self, url: str, base_64_user_pass):
        """
        return plan url and active plan id
        """

        is_exist = True
        final_url = url
        current_job_id = 1
        while is_exist:
            id_list = url.split('-')
            job_id = int(id_list[-1]) + 1
            url = url[0: len(url) - len(id_list[-1])] + str(job_id)
            payload = ""
            headers = {
                'Authorization': "Basic " + base_64_user_pass
            }

            response = requests.request("GET", url, data=payload, headers=headers)

            if response.status_code == 200:
                final_url = url
                current_job_id = job_id
            else:
                is_exist = False
        return final_url, current_job_id

    def status_of_agent(self, url: str):
        """
        return status of agent
        """
        print("Inside status of Agent")
        print(url)
        response = requests.request("GET", url)
        tree = et.fromstring(response.content)

        status = True
        is_fail = False
        while status:
            if tree.attrib.get('lifeCycleState') == "InProgress":
                time.sleep(60)
                response = requests.request("GET", url)
                tree = et.fromstring(response.content)
            elif tree.attrib.get('lifeCycleState') == "Queued":
                time.sleep(60)
                response = requests.request("GET", url)
                tree = et.fromstring(response.content)
            elif tree.attrib.get('successful') == "false":
                print("Plan is Failed")
                status = False
                is_fail = True
            elif tree.attrib.get('successful') == "true":
                print("plane is successful")
                status = False
                is_fail = False
        return not is_fail

    def get_logs(self, file_path):
        """
        scrap logs from log.zip folder and generate final logs.
        """

        print("generating Logs.....")
        
        # path of logs folder
        remotezip = self.shared_folder_path + file_path[file_path.find("\\archive\\"):] + "\\log.zip"
        #remotezip = 'Z:\\archive\\TSTFOMEM-WIN2012R26464M104\\47\\log.zip'
        print(remotezip)
        zip = zipfile.ZipFile(remotezip)
        final_summary = []
        files = []
        filename = "Final_Summary.txt"

        # For summary
        for fn in zip.namelist():
            if fn.endswith("set_summary.csv"):

                all_summary = open(filename, "w+")

                with zip.open(fn, 'r') as infile:
                    csv_list = []
                    reader = csv.reader(TextIOWrapper(infile, 'utf-8'))
                    for row in reader:
                        # process the CSV here
                        print(row)
                        csv_list.append(row)
                    print(csv_list)
                    if(len(csv_list)):
                        field = csv_list[0][1:]
                        summary = csv_list[-1][1:]

                        if len(final_summary) == 0:
                            final_summary = summary
                        else:
                            for i in range(len(summary)):
                                final_summary[i] = int(final_summary[i]) + int(summary[i])
        for i in range(len(field)):
            all_summary.write(field[i] + ":-" + str(final_summary[i]) + "\n")

        # store results of all testcases
        all_Log_Files = []
        for fn in zip.namelist():
            if fn.endswith("_verbose.log"):
                print(fn)
                file = zip.read(fn).decode("utf-8")
                file = file.split('----------------------------------------------------------------------')
                all_Log_Files.append(file[1:])

        # display only failed testcases results.
        count1 = 0
        for fn in zip.namelist():
            if fn.endswith("__summary.csv"):
                print(fn)
                count2 = 0
                file = zip.open(fn, 'r')
                reader = csv.reader(TextIOWrapper(file, 'utf-8'))

                all_summary.write("\n=========================================================================\n")
                all_summary.write(fn.split('/')[-1])
                all_summary.write("\n=========================================================================")

                for row in reader:
                    if row[0] == 'Result':
                        continue
                    if row[0] == "FAILED_STARTUP" or row[0] == "FAILED":
                        print("------------------All logs ============")
                        print(count1)
                        print(count2)
                        print("------------------All logs end --------------")
                        if(len(all_Log_Files[count1])):
                            all_summary.write(all_Log_Files[count1][count2])
                            all_summary.write('----------------------------------------------------------------------')
                    count2 += 1
                count1 += 1
        if (os.stat(all_summary.name).st_size > 0):
            files.append(filename)
        all_summary.close()

        #self.send_mail(files)

    def send_mail(self, attachments):
        """
        send final logs in mail
        """
        print("Sending mail")
        SERVER = "smtp-mail.outlook.com"
        FROM = "pavan.cheemakurthi@insightsoftware.com"
        TO = [self.receiver_email]  # must be a list

        # Prepare actual message
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = ", ".join(TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "FT Report"

        msg.attach(MIMEText("Hey!\r\n Here is your report from Functional Test.\r\n Thanks."))
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
        server.login("pavan.cheemakurthi@insightsoftware.com", self.outlook_password)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()

    def verify_binscope_log(self, branch_key, build_number, bamboo_url):
        """
        return binscope logs in console
        """
        print("Verifying binscope logs")
        build_log_url = bamboo_url + '/download/' + branch_key + '-JOB/build_logs/' + branch_key + '-JOB-' + str(
            build_number) + '.log'
        build_log = requests.get(build_log_url)
        binscope_content = list()
        start_parsing, binscope_test_passed = False, False
        if build_log.status_code == 200 and len(build_log.text) > 0:
            for curr_line in build_log.text.splitlines():
                if 'Enter BinScope' in curr_line:
                    start_parsing = True
                elif start_parsing:
                    if curr_line.endswith('====') and len(binscope_content) > 0 and binscope_content[0].endswith(
                            '===='):
                        binscope_content.append(curr_line)
                        break
                    if 'BinScope test succeeded' in curr_line:
                        binscope_test_passed = True
                    binscope_content.append(curr_line)
            if binscope_test_passed:
                with open(f"{self.driver_label}_BinscopeLog_{build_number}.txt", 'w') as f:
                    f.write(build_log.text)
                print('Binscope Test Succeeded')
            else:
                print('Binscope Test Failed')
            print('Binscope Log Content:')
            print('\n'.join(binscope_content))
        else:
            print('Build Logs Download Failed!')
 


def run_bamboo_adapter_build(input_args: dict):
    print("Building driver/adapter on bamboo...BEGIN")
    bamboo_build = FTPlans(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], input_args)
    # run_build_driver_as_server(input_args)
    if bamboo_build.build():
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
