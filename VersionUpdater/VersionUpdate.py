import os
import re
import sys
import stat
import subprocess
from P4Utils import Perforce


class VersionUpdator:
    """
    Represents class VersionUpdator
    """

    # Constants
    #DIDENCRYPTERPATH = os.path.abspath(os.path.join(os.curdir, 'DriverIDEncrypter.exe'))

    def __init__(self, inCWD: str, inBrandingDirPath: str, inNewVersion: str, inProductName: str = 'Core'):
        """
        The constructor
        :param inBrandingDirPath: Directory path to `Branding`
        :param inNewVersion: New version string
        :param inProductName: Name of the Product (Core/Plugin)
        """
        self.mNewVersion = inNewVersion
        self.mProductName = inProductName
        self.mP4V = Perforce()
        self.mBrandingDirPath = os.path.abspath(self.mP4V.mP4ClientRoot + inBrandingDirPath)
        self.mCWD = inCWD
        self.DIDENCRYPTERPATH = os.path.abspath(os.path.join(inCWD, 'DriverIDEncrypter.exe'))

    def getBrandingFileConfig(self) -> dict:
        """Returns Dictionary of <Path-to-Branding.xml>:<DIDName> from each branding"""
        brandingConfig = dict()
        for brandingDir in os.listdir(self.mBrandingDirPath):
            for filename in os.listdir(os.path.join(self.mBrandingDirPath, brandingDir)):
                result = re.search(r'([A-Za-z]+)_([A-Za-z0-9]*[_]?)branding([.]?[A-Za-z0-9]*).xml$', filename)
                if result is None:
                    continue
                brand, product, didPostFix = result.groups()
                # May contain special chars at end
                product = product[:len(product) - 1] if len(product) > 0 else 'RDF'
                brandingConfig[os.path.join(self.mBrandingDirPath, brandingDir, filename)] = \
                    os.path.join(self.mBrandingDirPath, brandingDir, f'{product}ODBC{didPostFix}.did')
        return brandingConfig

    def updateVersion(self, inFilePath: str):
        """Updates the Version in the branding file"""
        with open(inFilePath, 'r') as file:
            content = file.read().strip()
        newContent = ''
        flag = False
        for line in content.split('\n'):
            flag = False if '/branding' in line else flag
            newContent += f'  <version-number>{self.mNewVersion}</version-number>\n' \
                if 'version-number' in line else ('  ' if flag else '') + line.strip() + '\n'
            flag = not flag if 'branding' in line else flag
        with open(inFilePath, 'w') as file:
            file.write(newContent)

    def run(self):
        self.mP4V.getRevision(self.mBrandingDirPath)
        brandingConfig = self.getBrandingFileConfig()
        newCL = self.mP4V.createNewCL(f'[Memphis][{self.mProductName}][ODBC] - {self.mNewVersion}\n'
                                      f' - Version updated to {self.mNewVersion}')
        for brandingFile, didPath in brandingConfig.items():
            os.chmod(brandingFile, stat.FILE_ATTRIBUTE_NORMAL)
            os.chmod(didPath, stat.FILE_ATTRIBUTE_NORMAL)
            self.updateVersion(brandingFile)
            subprocess.call(f'{self.DIDENCRYPTERPATH} {brandingFile} {didPath}' , shell = True)
            self.mP4V.checkout(newCL, brandingFile, didPath)
        # self.mP4V.submit(newCL)


def main( inCWD: str,inNewVersion: str, inProductName: str):
    if inProductName == 'Core':
        brandingDir = f'//Drivers/Memphis/Core/Maintenance/1.6/ODBC/Branding/'
    else:
        brandingDir = f'//Drivers/Memphis/DataSources/{inProductName}/ODBC/Maintenance/1.6/Branding/'
    VersionUpdator(inCWD, brandingDir, inNewVersion, inProductName).run()


if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2], sys.argv[3])
