from jira import JIRA
import argparse
import sys,ast
class JiraOperations:
    conmapProjectId="15904"
    subtaskProjectId="14301"
    allPlatforms={
    "windows": "10503",
    "osx":"10505",
    "linux":"10504",
    "jdbc":"13006"
    }
    allCustomers={
    "qlik": "12030",
    "rstudio":"12033",
    "acl":"12011",
    "ibm":"12704",
    "retail":"13007"
    }
    parentIds={
    "S3": "111478",
    "Marketo": "111471",
    "Eloqua": "111467",
    "Hubspot": "111468",
    "Jira": "111469",
    "Responsys": "111477",
    "PayPal": "111475",
    "Xero": "111483",
    "Zoho": "111484",
    "MWS": "111473",
    "GoogleAnalytics": "110818",
    "WooCommerce": "110911",
    "Facebook": "110815",
    "FreshBooks": "110816",
    "OSvC": "111474",
    "Shopify": "111481",
    "Concur": "111466",
    "Magento": "110825",
    "ServiceNow": "111479",
    "Square": "111482",
    "SFMarketingCloud": "111480",
    "QuickBooks": "111476",
    "LinkedIn": "110824",
    "GoogleAds": "237016"
    }
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.jiraOptions={'server': "https://jira.magsw.com",'verify':False}
        
    def createSubTask(self,projectId,summary,parentId):
        issue_values={'project':{'id': projectId}, 'summary':summary,'issuetype': {'id' : '5' },'parent': {'id': parentId }}
        jira=self.connect(issue_values)
        return jira.create_issue(fields=issue_values)
        
    def createConmapTask(self,driverName,summary,releaseVersion,platforms,customers):
        issue_values={'project':{'id': self.conmapProjectId}, 'summary':summary,'issuetype': {'id' : '10902' },'parent': {'id': self.parentIds[driverName]}, 'customfield_11008': releaseVersion}
        
        #print(platforms[1])
        #print(customers)
        customerArray=list()
        for customer in customers:
            print(customer)
            customerDict = dict()
            customerDict["id"]=self.allCustomers[customer]
            customerArray.append(customerDict)
        issue_values["customfield_13915"]=customerArray
        
        customerPlatforms=list()
        for platform in platforms:
            tempDict = dict()
            tempDict["id"]=self.allPlatforms[platform]
            customerPlatforms.append(tempDict) 
        issue_values["customfield_11003"]=customerPlatforms
            
        jira=self.connect(issue_values)
        return jira.create_issue(fields=issue_values)
        
    
    def connect(self,issue_values):
        return JIRA(options=self.jiraOptions,basic_auth=(self.username,self.password))
        
platformArgs = sys.argv[6].split(',')

customerArgs = sys.argv[7].split(',')

jira=JiraOperations(sys.argv[1],sys.argv[2])
issue=jira.createConmapTask(sys.argv[3],sys.argv[4],sys.argv[5],platformArgs,customerArgs)
print(issue)




 
