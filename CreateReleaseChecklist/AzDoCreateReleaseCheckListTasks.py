from jira import JIRA
import argparse
import sys,ast
    
class JiraOperations:
    projectId="13378"
    parentId="10100"
    summary=['AzDo - Merge Plugin Changes from Trunk to branch','AzDo - Create Label For Plugin','Raise DOC Task','AzDo - Signing', 'AzDo - Binscope','AzDo - MetaData Tester', 'AzDo - Private Driver Loading','AzDo - Proxy Server Test',
    'AzDo - Functional Test','AzDo - Scalabitlity Tests','AzDo - Private Driver Loading','AzDo - PowerBI', 'AzDo - Tableau', 'AzDo - Branding Verification and SQL Browse Connect',
    'AzDo - ETW Logger', 'AzDo - Secure CRT Function check', 'AzDo - Integration Test Suite', 'AzDo - Ini Tests','AzDo - Package Testing']
    #summary=['AzDo - Merge Plugin Changes from Trunk to branch']
    
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.jiraOptions={'server': "https://insightsoftware.atlassian.net",'verify':False}
        
    def createReleaseCheckList(self,drivername,versionNumber,customer):
        jira=JIRA(options=self.jiraOptions,basic_auth=(self.username,self.password))
        issue_values={'project':{'id': self.projectId}, 'summary': drivername  +' ' +versionNumber +' '+ 'ODBC' +' ' + customer + ' Release','issuetype': {'id' : self.parentId }}
        parentIssue=jira.create_issue(fields=issue_values)
        print(parentIssue)
        for eachSummary in self.summary:
            issue_values={"project":{"id":self.projectId},"issuetype":{"id":"10010"},"summary":eachSummary,"parent":{"id":parentIssue.id}}
            issue=jira.create_issue(fields=issue_values)
            print(issue)
        
jira=JiraOperations(sys.argv[1],sys.argv[2])
jira.createReleaseCheckList(sys.argv[3],sys.argv[4],sys.argv[5])
        
        
