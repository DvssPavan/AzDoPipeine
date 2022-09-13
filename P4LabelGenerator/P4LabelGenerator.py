import json
import subprocess
import sys

from P4Utils import Perforce


class P4Label:
    """
    Represents class P4Label
    """

    def __init__(self, inLabelName: str, inLabelDescription: str, inViewContext: dict, inProductName: str):
        """
        The constructor
        :param inLabelName: Name of the label
        :param inLabelDescription: Description for label
        :param inViewContext: Views to be added in the created label with revisions
        :param inProductName: Name of the product
        """
        self.mLabelName = inLabelName
        self.mLabelDescription = inLabelDescription
        self.mViewContext = inViewContext.copy()
        self.mViews = sorted(inViewContext.keys())
        self.mProductName = inProductName
        self.mP4 = Perforce()

    def create(self):
        """Creates the P4 Label"""
        try:
            if not self.exists():
                print(self.mLabelName)
                self.mP4.createLabel(self.mLabelName, self.mLabelDescription, self.mViews)
            else:
                print(f'{self.mLabelName} exists. Further operation might be risky. Quitting here')
                quit(1)
        except Exception as error:
            print(error)

    def exists(self):
        print("I am in Exists")
        """Checks if the label already exists"""
        try:
            #result = subprocess.check_output(f'p4.exe labels -E {self.mLabelName}').decode()
            result = subprocess.run(['p4.exe', 'labels', '-E', self.mLabelName], stdout=subprocess.PIPE , shell=True).stdout.decode()
            return self.mLabelName in result
        except Exception as error:
            print(error)
            return True

    def map(self):
        """Maps files to label"""
        for path, revisions in self.mViewContext.items():
            for revision in revisions:
                try:
                    self.mP4.tagToLabel(self.mLabelName, path, revision)
                    print(f'{path} with {revision} mapped')
                except Exception as error:
                    print(error)

    def prepare(self):
        """Wrapper function to create, map and lock the label"""
        self.create()
        self.map()
        self.mP4.lockLabel(self.mLabelName)


def main(inCWD: str ,inPluginName: str, inLabelName: str, inSENLabel: str, inCoreLabel: str = ''):
    context = {
        'DRV': inPluginName,
        'CORELBL': inCoreLabel,
        'SENLBL': inSENLabel
    }
    with open(inCWD + '\input.json', 'r') as file:
        content = file.read()
    print("Input file read")
    for var, val in context.items():
        content = content.replace('{' + var + '}', val)
    data = json.loads(content)
    labelViews = data['dependencies']['common']
    if len(inCoreLabel) == 0:
        for path, revisions in data['dependencies']['core'].items():
            labelViews[path] = revisions
    else:
        for path, revisions in data['dependencies']['plugin'].items():
            labelViews[path] = revisions
    labelDesc = f'This Label was created by AzDo script\nAssociated Labels:\n - SEN: {inSENLabel}'
    labelDesc += f'\n - Core: {inCoreLabel}' if len(inCoreLabel) > 0 else ''
    P4Label(inLabelName, labelDesc, labelViews, inPluginName).prepare()


if __name__ == '__main__':
    if len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] , sys.argv[5])
    else:
        print('Invalid Input')
