# Code Signing DLLS/EXEs/Installers
This script will run a Code Signing plan in Bamboo.
Pre-requisites:
1. Please install python 3.7 or above.
2. Run the following command on your terminal to install the required dependencies:
   - python -m pip install atlassian-python-api
   - python -m pip install requests
The following files are available:
1. CodeSigningBuild: Python file that will read input from user_input.json file and triggers bamboo Code Signing plans.
2. user_input: Json file that user can use to input Driver label, Core label, SEN label, Driver branch, Driver brand and Build Configurations for Windows/Linux/OSX.
### Usage
Assuming user_input.json has been modified accordingly (see Parameters section), please run:
$ python CodeSigningBuild.py <simbaUsername> <simbaPassword> <cwd>
### Command line arguments
- simbaUsername: Simba Username (without simba\).
- simbaPassword: Simba Password.
- cwd: Current working directory.
<!--- Note: The User/Owner to whom the simba Username & Password belongs to should have the permissions to start a Signed Installer Code Signing Plans. --->
### Parameters
For an example of what these parameters should look like, please refer to user_input.json
- inProjectKey: The project key which is assigned to the particular plan. For example, the key "SGINOMEM" is assigned for Signed Installer Plans.
- inDriverLabel: P4 driver label.
- inCoreLabel: P4 Memphis Core label.
- inSENLabel: P4 SEN label.
- inDriverBrand: P4 Driver Brand name which is used for the release (Microsoft, Simba, RStudio ...)
- inBranchName: Branch name defined on bamboo for each driver.
- inCompiler: Compiler type mentioned on the Bamboo plan. For instance, "vs2013" or "vs2015" is used for windows.
- inPlatform: Type of the platform mentioned on the Bamboo plan. For example, "w2012r2" is one of the plaform types/codes used for windows.
- inConfiguration: Configuration Type mentioned on the Bamboo plan such as "64 msi" which is used for 64-bit Signed Installer. 
### Output
You will get an exception if the plan is "Failed" or "Stopped" in the Middle of the process.
Else, the code will be executed successfully.