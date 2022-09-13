import json
import re
import os
import subprocess
import sys

from Input import InputReader
from RemoteConnection import RemoteConnection
from GenUtility import TimeOutLevel, isNoneOrEmpty, writeInFile
from ScalabilityTestRunner import ScalabilityTestRunner

"""
    The Launcing part of the Scalability Test with required user credentials
    which are required for the package setup.
"""
def main(inUserName: str, inPassword: str, inBasePath: str, inputFileName: str):
    if isNoneOrEmpty(inUserName, inPassword, inBasePath, inputFileName):
        print('Error: Invalid Parameter')
    elif not os.path.exists(inBasePath):
        print(f"Error: Invalid Path {inBasePath}")
    else:
        inputReader = InputReader(os.path.join(inBasePath, inputFileName))
        summary = dict()
        remoteConnection = RemoteConnection(inputReader.getRemoteMachineAddress(), inUserName, inPassword)
        if remoteConnection.connect():
            coreInfo = inputReader.getCoreInfo()
            if coreInfo.download():
                summary['CoreSetup'] = 'Succeed'
            else:
                summary['CoreSetup'] = 'Failed'
                return summary

            summary['Plugins'] = dict()
            for pluginInfo in inputReader.getPluginInfo():
                sourceFilePath = os.path.abspath(pluginInfo.getSourcePath())

                if pluginInfo.setup(coreInfo):
                    summary['Plugins'][sourceFilePath] = dict()
                    summary['Plugins'][sourceFilePath]['Setup'] = 'Succeed'
                    
                    ScalabilityTestRunner(os.path.join(inBasePath, 'ScalabilityTester.exe'),
                                          pluginInfo.getDestinationPath(),
                                          os.path.join(pluginInfo.getLogsPath(), pluginInfo.getPackageName()) + '\\',
                                          'dsn=' + pluginInfo.getDataSourceName()).start(inBasePath)
                else:
                    summary['Plugins'][sourceFilePath] = 'Failed'
            remoteConnection.disconnect()

            # with open(os.path.join(inBasePath, 'MetaTestSummary.json'), 'w') as file:
            #     json.dump(summary, file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
