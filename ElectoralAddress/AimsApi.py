import requests
import json
import Config
from qgis.core import * #TEMP

_url = Config.ConfigSectionMap('uri')['review']
#_user=getpass.getuser()
_user=Config.ConfigSectionMap('user')['name']
_password=Config.ConfigSectionMap('user')['pass']
_headers = {'content-type':'application/json', 'accept':'application/json'}

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def getResolutionPageHrefs ( page ): # now count has been added the loading of resolution items needs to be reviewed
    """ get the reference to each resolution item associated with each resolution pages"""    
    pageUrl = _url+'?page='+page+'&count=25' #hacked count on the end (TEMP)
    r = requests.get(pageUrl,auth=(_user, _password)).json()
    for i in r['entities']:
        yield i['links'][0]['href']

def loadResolutionItem ( href ):
    """ load each resolution item as per its href url"""    
    r = requests.get(href,auth=(_user, _password)).json()
    return r

def acceptResolution ( changeId, verisonId ):
    payload = {"version":{str(verisonId)},"changeId":{str(changeId)}}
    url =_url+'/{0}/accept'.format( changeId )
    r = requests.post(url, data=json.dumps(payload, default=set_default), headers=_headers, auth=(_user, _password)).json() 
    QgsMessageLog.logMessage(json.dumps(r), level=QgsMessageLog.CRITICAL) #TEMP

    try: 
        status = r.get('properties').get('workflow').get('queueStatusName')   
        return ['status',status ]
    except: 
        message = r.get('properties').get('reason')+': ' +r.get('properties').get('message')
        return ['message',message ]

def rejectResolution ( changeId, verisonId ):
    payload = {"version":{str(verisonId)},"changeId":{str(changeId)}}
    url =_url+'/{0}/decline'.format( changeId )
    r = requests.post(url, data=json.dumps(payload, default=set_default), headers=_headers, auth=(_user, _password)).json()   
    QgsMessageLog.logMessage(url, level=QgsMessageLog.CRITICAL) #TEMP
    
    try: 
        status = r.get('properties').get('workflow').get('queueStatusName')   
        return ['status',status ]            
    except: 
        message = r.get('properties').get('reason')+': ' +r.get('properties').get('message')
        return ['message',message ]
