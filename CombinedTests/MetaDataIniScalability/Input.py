import json
import os
import sys
from Packages import Core, Plugin


class InputReader:

    # Class Variables
    RemoteMachineAddress = 'RemoteMachineAddress'
    Core = 'Core'
    Plugin = 'Plugin'
    Compile = 'Compile'
    SourcePath = 'SourcePath'
    DestPath = 'DestPath'
    ForceUpdate = 'ForceUpdate'
    Branch = 'Branch'
    Brand = 'Brand'
    CoreLabel = 'CoreLabel'
    DriverLabel = 'DriverLabel'
    SENLabel = 'SENLabel'
    DataSourceConfiguration = 'DataSourceConfiguration'
    WaitForUserToSetupDSN = 'WaitForUserToSetupDSN'
    DriverName = 'DriverName'

    def __init__(self, inInputFileName: str):
        if os.path.exists(inInputFileName):
            with open(inInputFileName) as file:
                inInputFile = json.load(file)
        else:
            print(f"Error: Given {inInputFileName} file not found")
            sys.exit(1)
            
        if InputReader.DriverName in inInputFile and \
                inInputFile[InputReader.DriverName] is not None \
                and len(inInputFile[InputReader.DriverName]) > 0:
            self.__mDriverName = inInputFile[InputReader.DriverName]
        else:
            print(f"Error: Invalid Attribute DriverName: `{InputReader.DriverName}`")
            sys.exit(1)
            
        if InputReader.RemoteMachineAddress in inInputFile and \
                inInputFile[InputReader.RemoteMachineAddress] is not None \
                and len(inInputFile[InputReader.RemoteMachineAddress]) > 0:
            self.__mRemoteMachineAddress = inInputFile[InputReader.RemoteMachineAddress]
        else:
            print(f"Error: Invalid Attribute: `{InputReader.RemoteMachineAddress}`")
            sys.exit(1)
        
        if InputReader.DriverLabel in inInputFile and \
                inInputFile[InputReader.DriverLabel] is not None \
                and len(inInputFile[InputReader.DriverLabel]) > 0:
            self.__mDriverLabel = inInputFile[InputReader.DriverLabel]
        else:
            print(f"Error: Invalid Attribute DriverLabel: `{InputReader.DriverLabel}`")
            sys.exit(1)
        
        if InputReader.CoreLabel in inInputFile and \
                inInputFile[InputReader.CoreLabel] is not None \
                and len(inInputFile[InputReader.CoreLabel]) > 0:
            self.__mCoreLabel = inInputFile[InputReader.CoreLabel]
        else:
            print(f"Error: Invalid Attribute CoreLabel: `{InputReader.CoreLabel}`")
            sys.exit(1)
            
        if InputReader.SENLabel in inInputFile and \
                inInputFile[InputReader.SENLabel] is not None \
                and len(inInputFile[InputReader.SENLabel]) > 0:
            self.__mSENLabel = inInputFile[InputReader.SENLabel]
        else:
            print(f"Error: Invalid Attribute SENLabel: `{InputReader.SENLabel}`")
            sys.exit(1)
            
        try:
            self.__mSourcePath = inInputFile[InputReader.Core][InputReader.SourcePath]
            self.__mDesPath  = inInputFile[InputReader.Core][InputReader.DestPath]
            if '{{Driver_Label}}' in self.__mSourcePath:
                self.__mSourcePath=self.__mSourcePath.replace('{{Driver_Label}}',self.__mDriverLabel)
            if '{{Core_Label}}' in self.__mSourcePath:
                self.__mSourcePath=self.__mSourcePath.replace('{{Core_Label}}',self.__mCoreLabel)
            if '{{SEN_Label}}' in self.__mSourcePath:
                self.__mSourcePath=self.__mSourcePath.replace('{{SEN_Label}}',self.__mSENLabel)
            if '{{Driver_Name}}' in self.__mSourcePath:
                self.__mSourcePath=self.__mSourcePath.replace('{{Driver_Name}}',self.__mDriverName)
            if '{{Driver_Label}}' in self.__mDesPath:
                self.__mDesPath=self.__mDesPath.replace('{{Driver_Label}}',self.__mDriverLabel)
            if '{{Core_Label}}' in self.__mDesPath:
                self.__mDesPath=self.__mDesPath.replace('{{Core_Label}}',self.__mCoreLabel)
            if '{{SEN_Label}}' in self.__mDesPath:
                self.__mDesPath=self.__mDesPath.replace('{{SEN_Label}}',self.__mSENLabel)
            if '{{Driver_Name}}' in self.__mDesPath:
                self.__mDesPath=self.__mDesPath.replace('{{Driver_Name}}',self.__mDriverName)
            
            self.__mCoreInfo = Core(self.__mSourcePath,
                                    self.__mDesPath,
                                    inInputFile[InputReader.Core][InputReader.Branch],
                                    inInputFile[InputReader.Core][InputReader.ForceUpdate])
        except Exception as e:
            print(f"Invalid Attribute: `{InputReader.Core}`\nError: {e}")
            sys.exit(1)
        if InputReader.Plugin in inInputFile and InputReader.Compile in inInputFile[InputReader.Plugin] \
                and len(inInputFile[InputReader.Plugin][InputReader.Compile]) > 0:
            self.__mPluginInfo = list()
            print(self.__mPluginInfo)
            for pluginInfo in inInputFile[InputReader.Plugin][InputReader.Compile]:
                try:
                    self.__mSourcePath = pluginInfo[InputReader.SourcePath]
                    self.__mDesPath  = pluginInfo[InputReader.DestPath]
                    if '{{Driver_Label}}' in self.__mSourcePath:
                        self.__mSourcePath=self.__mSourcePath.replace('{{Driver_Label}}',self.__mDriverLabel)
                    if '{{Core_Label}}' in self.__mSourcePath:
                        self.__mSourcePath=self.__mSourcePath.replace('{{Core_Label}}',self.__mCoreLabel)
                    if '{{SEN_Label}}' in self.__mSourcePath:
                        self.__mSourcePath=self.__mSourcePath.replace('{{SEN_Label}}',self.__mSENLabel)
                    if '{{Driver_Name}}' in self.__mSourcePath:
                        self.__mSourcePath=self.__mSourcePath.replace('{{Driver_Name}}',self.__mDriverName)
                    if '{{Driver_Label}}' in self.__mDesPath:
                        self.__mDesPath=self.__mDesPath.replace('{{Driver_Label}}',self.__mDriverLabel)
                    if '{{Core_Label}}' in self.__mDesPath:
                        self.__mDesPath=self.__mDesPath.replace('{{Core_Label}}',self.__mCoreLabel)
                    if '{{SEN_Label}}' in self.__mDesPath:
                        self.__mDesPath=self.__mDesPath.replace('{{SEN_Label}}',self.__mSENLabel)
                    if '{{Driver_Name}}' in self.__mDesPath:
                        self.__mDesPath=self.__mDesPath.replace('{{Driver_Name}}',self.__mDriverName)
                    self.__mPluginInfo.append(
                        Plugin(self.__mSourcePath,
                               self.__mDesPath,
                               pluginInfo[InputReader.Brand], pluginInfo[InputReader.DataSourceConfiguration],
                               pluginInfo[InputReader.WaitForUserToSetupDSN], pluginInfo[InputReader.ForceUpdate])
                    )
                except KeyError as e:
                    print(f"Error: {e}")
                    sys.exit(KeyError)
        else:
            print(f'Error: Invalid Attribute: `{InputReader.Plugin}` or `{InputReader.Compile}`')
            sys.exit(1)

    def getRemoteMachineAddress(self):
        return self.__mRemoteMachineAddress

    def getCoreInfo(self):
        return self.__mCoreInfo

    def getPluginInfo(self):
        return self.__mPluginInfo
