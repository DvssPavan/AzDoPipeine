import subprocess as sp
import pyodbc 
import os
import platform
import winreg
import sys
from shutil import copy
#declaring one global varibale
OdbcLibDriverPath = ""

def isNoneOrEmpty(*args) -> bool:
    """Checks if any of the given argument is None or Empty."""
    return any(map(lambda inArgs: inArgs is None or len(inArgs) == 0, args))

def FindDllVersion(OdbcLibDriverPath):
    '''
    Fetch the "NAME" and "VERSION" of DLL file for specified driver.
    
    Lib_path = Path to the driver's "Lib" folder 
    Dll_file = Name of the DLL file with Extension
    Dll_Version = Version of the driver's DLL file
    '''
    Lib_path = OdbcLibDriverPath[0:OdbcLibDriverPath.rfind("\\",0) + 1]        
    Dll_file = OdbcLibDriverPath[OdbcLibDriverPath.rfind("\\",0)+1:]
    os.chdir(Lib_path)
    Dll_Version = sp.getoutput("powershell \"(Get-Item -path .\{}).VersionInfo.ProductVersion".format(Dll_file)) #Fetching version of Dll file
    print('Dll File name       =',Dll_file)
    print("Dll version         =",Dll_Version)
        
def GetSetRegistry(inTargetKey, inDriverBit, inDriverRegistryConfig):
    '''
    Deals with registry. It modifies the "UseEncryptedEndpoints" key to generate error messages, 
    and also find the path of "Lib" for the specified driver.
    
    valueName = value_name is a string indicating the value to query.
    '''
    #Setting UseEncryptedEndpoints
    valueName = "Driver" 
    systemBit = int(platform.architecture()[0][:2])
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey, 'Software', 0, winreg.KEY_READ) as parentKey:
                if systemBit != inDriverBit:
                    parentKey = winreg.OpenKey(parentKey, 'Wow6432Node', 0, winreg.KEY_READ)
                with winreg.OpenKey(parentKey, 'ODBC', 0, winreg.KEY_READ) as odbcKey:
                    with winreg.OpenKey(odbcKey, 'ODBC.INI', 0, winreg.KEY_WRITE) as odbcIniKey:
                        with winreg.CreateKeyEx(odbcIniKey, inTargetKey, 0, winreg.KEY_ALL_ACCESS) as driverKey:                        
                            for key, value in inDriverRegistryConfig.items():
                                winreg.SetValueEx(driverKey, key, 0, winreg.REG_SZ, value)
                            DriverPath = winreg.QueryValueEx(driverKey, valueName)[0]                            
                            
                    with winreg.OpenKey(odbcKey, 'ODBCINST.INI', 0, winreg.KEY_WRITE) as odbcIniKey:    
                        with winreg.CreateKeyEx(odbcIniKey, DriverPath, 0, winreg.KEY_ALL_ACCESS) as inOdbcInstKey:                                            
                            global OdbcLibDriverPath
                            OdbcLibDriverPath = winreg.QueryValueEx(inOdbcInstKey, valueName)[0]                                                            
    except Exception as e:
        print(f"Error: {e}")

def ReadErrMsgs(ErrMsgPath):
    '''
    Read Error Message and fetch the Component name.
    
    ReadValue is list which contains the component name.
    '''
    
    file = open(ErrMsgPath, "r")
    f = file.read()
    ReadValue = list()
    cnt = 0
    temp_str = ""
    flg = 0
    for i in range(0,len(f)):
        if f[i] == "[":
            flg = 1
        elif(f[i] == "]"):
            flg = 0
            ReadValue.append(temp_str)
            temp_str = ""
        elif flg == 1:
            temp_str = temp_str + f[i]

    print("Please verify component name from below.")
    print(ReadValue)
    
    
def main(DSN_Name: str, MetaData_path: str, inDriverBit: int):
    '''
    DSN_Name            = Datasource Name (i.e. "IBM Facebook")
    MetaData_Path       = Path to Metadata tester's "Bin" folder
    System Bit          = 32 / 64 (As per system configuration)
    Lib_path            = Absolute path of the driver's LIB folder
    Dll_file            = Name of DLL file of the driver
    OdbcLibDriverPath   = Path of the dll file getting from registery
    '''
    if isNoneOrEmpty(DSN_Name, MetaData_path, inDriverBit):
        print('Error: Invalid Parameter')
    elif not os.path.exists(MetaData_path):
        print(f"Error: Invalid Path {MetaData_path}")
    else:            
        
        #Set UseEncryptedEndpoints to 1( Default Value)
        inDriverBit = int(inDriverBit)
        inDriverRegistryConfig = {"UseEncryptedEndpoints":"1"}
        GetSetRegistry(DSN_Name,inDriverBit,inDriverRegistryConfig)
        
        
        pyodbc.pooling = False
        pyodbc.autocommit = True      
        inDriverBit = int(inDriverBit)
        inDSN = "DSN="+DSN_Name
        connection = pyodbc.connect(inDSN,autocommit=True)
        print('Data Source Name    =',connection.getinfo(2))
        print('Driver version      =',connection.getinfo(7))        



        #Start finding DLL path
        GetSetRegistry(DSN_Name,inDriverBit,inDriverRegistryConfig)        
        #END finding DLL path
        
        #Find DLL Version
        FindDllVersion(OdbcLibDriverPath)
        
        
        #ErrorMessageFetching
        
        #Set UseEncryptedEndpoints to 0 to generate Error Message    
        inDriverRegistryConfig = {"UseEncryptedEndpoints":"0"}
        GetSetRegistry(DSN_Name,inDriverBit,inDriverRegistryConfig)
              
        #Generating the Error Message      
        if(inDriverBit == 64):
            print(MetaData_path)
            baseDirectoryPath=MetaData_path
            MetaData_path = os.path.join(MetaData_path,"x64","Debug")
            print(MetaData_path)
            if not os.path.exists(MetaData_path):
               os.makedirs(MetaData_path)
            os.chdir(MetaData_path)
            copy(baseDirectoryPath+'\MetaTester64.exe',MetaData_path)
            ErrMsgStr = sp.getoutput("MetaTester64.exe -d \"{}\" -o ErrorMessage.txt".format(DSN_Name))
        elif(inDriverBit == 32):                 
            MetaData_path = os.path.join(MetaData_path,"Win32","Debug")
            if not os.path.exists(MetaData_path):
               os.makedirs(MetaData_path)
            os.chdir(MetaData_path)
            copy(baseDirectoryPath+'\MetaTester32.exe',MetaData_path)
            ErrMsgStr = sp.getoutput("MetaTester32.exe -d \"{}\" -o ErrorMessage.txt".format(DSN_Name))
        else:
            print("Error: Invalid Driver Bit.")
            
        #Set UseEncryptedEndpoints to 1( Default Value)
        inDriverRegistryConfig = {"UseEncryptedEndpoints":"1"}
        GetSetRegistry(DSN_Name,inDriverBit,inDriverRegistryConfig)
        
        
        #Start Reading ErrorMessage to find Component name and Vendor name    
        ErrMsgPath = os.path.join(MetaData_path,"ErrorMessage.txt")
        #print(ErrMsgPath)
        ReadErrMsgs(ErrMsgPath)
    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
