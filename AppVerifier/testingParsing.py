import zipfile
import urllib
import requests
import os, stat

shared_folder_path=r"\\vmware-host\Shared Folders\Z"
#remotezip = urllib.request.urlopen(r"file:C:\Users\pcheemakurthi\Documents\Rough\log.zip")
filePath = r"\\oak.simba.ad\build_archives\archive\TSTFOMEM-WIN0020166432M88\25"
remotezip = shared_folder_path + filePath[filePath.find("\\archive\\"):] + "\\log.zip"
zip = zipfile.ZipFile(remotezip)
files = []
for fn in zip.namelist():
        if fn.find("test_output/appverifier") != -1:
            print(fn)
            file = zip.read(fn).decode("utf-8")
            fileName = fn[fn.find("test_output/appverifier/")+24:]
            if fileName!="":
                f = open(fileName, "w+")
                rdfodbcTracefound = 0
                prevLine=""
                start=False
                end=False
                errors=""
                for line in file.split("\n"):
                    if ('Severity="Error"' in line):
                        start=True
                    if '</avrf:logEntry>' in line:
                        end=True
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
                        rdfodbcTracefound=0
                        errors=""
                if (os.stat(f.name).st_size > 0):
                    files.append(fileName)
                print(files)
                f.close()
