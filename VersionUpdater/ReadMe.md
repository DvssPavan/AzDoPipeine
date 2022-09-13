# Version Updater
 - Use to update the version in the Branding XML files
 - `Note`: This script directly submits the updated XML and DID files to the perforce

## Requirements:
  1. Install [Python](https://www.python.org/downloads/)
  2. Perforce API
     ```
     pip3 install p4python
     ```
  3. Perforce Client needs to be installed
  
## Input:
  1. `NewVersion`        - New Version of the product
  2. `ProductName`       - Name of the product (`Note`: Use 'Core' for MemphisCore)

## Usage
- To Update Plugin Version
     ```bash
     python .\VersionUpdate.py 1.7.8.9001 Hubspot
     ```
- To Update Core Version
     ```bash
     python .\VersionUpdate.py 1.7.8.9001 Core
     ```
  