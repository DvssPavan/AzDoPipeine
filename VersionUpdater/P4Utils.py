"""
P4 Utility
This module is a helper for all Perforce operations, gets called by various modules that require anything perforce.
"""

from P4 import P4, P4Exception


class Perforce:
    """
    Initializes an instance of P4 and saves all P4 related info for use in methods.
    Throws P4Exception if connection not successful.
    """
    def __init__(self):
        mP4V = P4()
        try:
            with mP4V.connect():
                info = mP4V.run('info')
                self.mP4Root = info[0]['serverRoot']
                self.mP4Host = info[0]['clientHost']
                self.mP4User = info[0]['userName']
                self.mP4Client = info[0]['clientName']
                self.mP4ClientRoot = info[0]['clientRoot']
                mP4V.exception_level = 1
                self.mP4 = mP4V
                print("Connected to perforce")
        except P4Exception as p4e:
            # TODO: log exception
            raise PerforceException("Perforce connection error " + str(p4e))

    def createNewCL(self, inCLDescription: str):
        """Creates a new empty changelist and returns the changelist number."""
        try:
            with self.mP4.connect():
                newCL = self.mP4.save_change({
                    'Change': 'new',
                    'Description': inCLDescription
                })[0]
                return int(newCL.split()[1])  # returns the changelist number.
        except P4Exception as p4e:
            # TODO: log exception
            raise PerforceException("Perforce connection error " + str(p4e))

    def markForAdd(self, inCLNumber: str, *inFiles: str):
        """
        Opens file(s) for add within the cl_number specified.
        Equivalent of `p4 add -c cl_number file`.
        """
        try:
            with self.mP4.connect():
                for f in inFiles:
                    self.mP4.run_add('-c', inCLNumber, f)
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def markForDelete(self, inCLNumber: str, *inFiles: str):
        """
        Mark file(s) for delete within the cl_number specified.
        Equivalent of `p4 delete -c cl_number file`.
        """
        try:
            with self.mP4.connect():
                for f in inFiles:
                    self.mP4.run_delete('-c', inCLNumber, f)
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def checkout(self, inCLNumber: str, *inFiles: str):
        """
        Opens file(s) for edit within the cl_number specified.
        Equivalent of `p4 edit -c cl_number file`.
        """
        try:
            with self.mP4.connect():
                for f in inFiles:
                    self.mP4.run_edit('-c', inCLNumber, f)
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def createLabel(self, inLabelName: str, inLabelDescription: str, inViews: list, inOptions='unlocked'):
        """
        Creates a new label.
        """
        try:
            with self.mP4.connect():
                newLabel = self.mP4.run_label('-o', inLabelName)[0]
                newLabel['Description'] = inLabelDescription
                newLabel['Options'] = inOptions
                newLabel['Owner'] = self.mP4User
                newLabel['View'] = inViews.copy()
                self.mP4.input = newLabel
                self.mP4.run_label('-i')
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def tagToLabel(self, inLabelName: str, inViews: list, inRevision: str = 'head'):
        inRevision = f'#{inRevision}' if inRevision == 'head' else f'@{inRevision}'
        try:
            with self.mP4.connect():
                self.mP4.run_tag('-l', inLabelName, inViews, inRevision)
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def submit(self, inCLNumber: int):
        """Submit a changelist given it's number."""
        try:
            with self.mP4.connect():
                self.mP4.run_submit('-c', str(inCLNumber))
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def fetchLabel(self, inLabelName):
        try:
            with self.mP4.connect():
                return self.mP4.fetch_label(inLabelName)
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def lockLabel(self, inLabelName: str):
        """Creates a new label."""
        try:
            with self.mP4.connect():
                newLabel = self.mP4.run_label('-o', inLabelName)[0]
                newLabel['Options'] = 'locked'
                self.mP4.input = newLabel
                self.mP4.run_label('-i')
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))

    def getRevision(self, inPath: str, inRevision: str = 'head'):
        """
        To get particular revision of file from P4V
        :param inPath: Path of file or directory to get
        :param inRevision: Revision of file.
        """
        try:
            with self.mP4.connect():
                self.mP4.run('sync', f'{inPath}...' if inRevision == 'head' else f'{inPath}...@{inRevision}')
        except P4Exception as p4e:
            raise PerforceException("Perforce connection error " + str(p4e))


class PerforceException(Exception):
    pass
