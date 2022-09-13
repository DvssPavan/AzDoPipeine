from jira import JIRA
import argparse
import sys,ast

"""projectId="13201"
parentId="225420"
summary=['AzDo - Merge Plugin Changes from Trunk to branch','AzDo - Create Label For Plugin','Raise DOC Task','AzDo - Signing', 'AzDo - Binscope','AzDo - MetaData Tester', 'AzDo - Private Driver Loading','AzDo - Proxy Server Test',
'AzDo - Functional Test','AzDo - Scalabitlity Tests','AzDo - Private Driver Loading','AzDo - PowerBI', 'AzDo - Tableau', 'AzDo - Branding Verification and SQL Browse Connect',
'AzDo - ETW Logger', 'AzDo - Secure CRT Function check', 'AzDo - Integration Test Suite', 'AzDo - Ini Tests','AzDo - Package Testing'
]
#summary=['AzDo - Merge Plugin Changes from Trunk to branch']
jiraOptions={'server': "https://jira.magsw.com",'verify':False}
jira=JIRA(options=jiraOptions,basic_auth=("pcheemakurthi","Gnca9a059nabah$23"))
issue_values={'project':{'id': projectId}, 'summary':'Marketo Task Creation from AzDo Script','issuetype': {'id' : '7' }}
issue=jira.create_issue(fields=issue_values)
#mainIssue = jira.issue('MPHCO-513')
#issueArray=mainIssue.fields.subtasks
#for eachIssue in issueArray:
#   eachIssue.update(fields={'labels':["MemphisDrivers"]})
for eachSummary in summary:
    issue_values={'project':{'id': projectId}, 'summary':eachSummary,'issuetype': {'id' : '5' },'parent': {'id': issue.id }}
    issue=jira.create_issue(fields=issue_values)
    print(issue)"""
    
class JiraOperations:
    projectId="13201"
    parentId="225420"
    summary=['AzDo - MetaData Changes','AzDo - Auth Changes','AzDo - Merge Plugin Changes from Trunk to branch','AzDo - Create Label For Plugin','Raise DOC Task','AzDo - Signing', 'AzDo - Binscope','AzDo - MetaData Tester', 'AzDo - Private Driver Loading','AzDo - Proxy Server Test',
    'AzDo - Functional Test','AzDo - Scalabitlity Tests','AzDo - Private Driver Loading','AzDo - PowerBI', 'AzDo - Tableau', 'AzDo - Branding Verification and SQL Browse Connect',
    'AzDo - ETW Logger', 'AzDo - Secure CRT Function check', 'AzDo - Integration Test Suite', 'AzDo - Ini Tests','AzDo - Package Testing']
    #summary=['AzDo - Merge Plugin Changes from Trunk to branch']
    
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.jiraOptions={'server': "https://jira.magsw.com",'verify':False}
        
    def createReleaseCheckList(self,drivername,versionNumber,customer):
        jira=JIRA(options=self.jiraOptions,basic_auth=(self.username,self.password))
        issue_values={'project':{'id': self.projectId}, 'summary': drivername + versionNumber + 'ODBC' + customer + 'Release','issuetype': {'id' : '7' }}
        parentIssue=jira.create_issue(fields=issue_values)
        print(parentIssue)
        for eachSummary in self.summary:
            issue_values={'project':{'id': self.projectId}, 'summary':eachSummary,'issuetype': {'id' : '5' },'parent': {'id': parentIssue.id }}
            issue=jira.create_issue(fields=issue_values)
            print(issue)
        
jira=JiraOperations(sys.argv[1],sys.argv[2])
jira.createReleaseCheckList(sys.argv[3],sys.argv[4],sys.argv[5])
