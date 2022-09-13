# DrMemory

This script will run Drmemory in Bamboo, parse the logs and mail the parsed logs to the end user.

Pre-requisites:
1. Please install python 3.7 or above.
2. Run the following command on your terminal to install the required dependencies:
   - python -m pip install wheel
   - python -m pip install atlassian-python-api
   - python -m pip install requests

The following files are available:
1. DrMemory: Python file that will read input from user_input.json file and triggers bamboo builds for Drmemory, parse the logs and mails the final result to user.
2. user_input: Json file that user can use to input Driver label, Core label, SEN label, Driver branch and whether to exclude compilation.

### Usage
Assuming user_input.json has been modified accordingly (see Parameters section), please run:
$ python DrMemory.py <cwd> <simbaUsername> <simbaPassword> <receiverEmail> <outlookPassword> <shared_folder_path>

### Command line arguments
- cwd: Current working directory.
- simbaUsername: Simba Username (without simba\).
- simbaPassword: Simba Password.
- receiverEmail: Email to which the drmemory results will be sent.
- outlookPassword: Outlook password of email receiver.
- shared_folder_path: Path to the shared folder in Network drive (i.e. \\vmware-host\Shared Folders\archive) from where the logs will be retrieved.

### Parameters
For an example of what these parameters should look like, please refer to user_input.json
- inDriverLabel: P4 driver label.
- inCoreLabel: P4 Memphis Core label.
- inSENLabel: P4 SEN label.
- inBranchName: Branch name defined on bamboo for each driver.
- ExcludeCompilation: indicates whether compilation step should be excluded and directly trigger Functional Test for DrMemory.

### Output
The user will get an email from self at the end which will contain Attachments of parsed results which he/she has to review once and fixes (if any) in his/her respective driver.
Note: Parsed results will show only those Errors which occured due to either Memphis Core / DataSource code.

