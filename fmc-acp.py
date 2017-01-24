#!/usr/bin/python
# =====================================================================================================================
#
# Overview: This script delete objects out of Cisco FMC utilizing the built-in API
#
# Usage:    Run python <script_name> 
#
# Use script at you own risk, and no warranties are inferred or granted. 
# =====================================================================================================================
import requests
import json
import requests
import logging
import time
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(filename='response.log',level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

results=[]
ipaddr = "192.168.16.150"
user1="api"
pass1= raw_input("Enter your FMC password: ")
querystring = {"limit":"1000"}
headers = {
    'cache-control': "no-cache",
    'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
    }

url = "https://%s/api/fmc_platform/v1/auth/generatetoken" % ipaddr

response = requests.request("POST", url, headers=headers, auth=(user1,pass1), verify=False)

# Authenicates token used in addiotnal HTTPS CRUD request
auth = response.headers['X-auth-access-token']

url = "https://%s/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies" % ipaddr

headers = {
    'x-auth-access-token': auth,
    'cache-control': "no-cache",
    'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
    }

#Need to work on this logic list item need to be verifed. Need to verify which ACP is applied.
# get all objects type based in user reponse from FMC 
response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

r = response.json()
number=1
for i in r['items']:
 print "%d. %s" % (number,i['name'])
 number+=1

acp = input("Enter your FMC ACP policy number: ")

acp -= 1
url = r['items'][acp]['links']['self']

#querystring = {"expanded":"true"}
response = requests.request("GET", url, headers=headers, verify=False)

url = response.json()['rules']['links']['self']

response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

raw = response.json()

for i in raw['items']:  
	results.append(i['links']['self'])
number=1

def getSubdictData(subdict, fieldname, prop2):
    if 'objects' in subdict[fieldname]:
        return subdict[fieldname]['objects'][0]['name']
    elif 'literals' in subdict[fieldname]:
        if prop2 in subdict[fieldname]['literals'][0]:
            return subdict[fieldname]['literals'][0][prop2]
        else:
            return "0"
    else :
        return subdict[fieldname]

target = open('rules.csv', 'w')

print >> target, "ID, Name, Action, Source Zone, Source Network, Source Port, Destination Zone, Destination Network, Destination Port"

for i in results:
	response = requests.request("GET", i, headers=headers, verify=False)
	raw=response.json()
	raw.setdefault('name', "noname_rule")
	raw.setdefault('action', "no_action")
	raw.setdefault('sourceNetworks', "any-src")
	raw.setdefault('destinationNetworks', "any-dest")
	raw.setdefault('sourcePorts', "any-src-port")
	raw.setdefault('destinationPorts', "any-dest-port")
	raw.setdefault('sourceZones', "any-src-zn")
	raw.setdefault('destinationZones', "any-dst-zn")
	interesting_keys = ('name', 'action','sourceZones', 'sourceNetworks', 'sourcePorts', 'destinationZones', 'destinationNetworks', 'destinationPorts' )
	subdict = {x: raw.get(x, "any") for x in interesting_keys if x in raw}
	
	srczn = getSubdictData(subdict, 'sourceZones', 'port')
	srcnet = getSubdictData(subdict, 'sourceNetworks', 'value')
	srcprt = getSubdictData(subdict, 'sourcePorts', 'port')
	dstzn = getSubdictData(subdict, 'destinationZones', 'port')
	dstnet = getSubdictData(subdict, 'destinationNetworks', 'value')
	dstprt = getSubdictData(subdict, 'destinationPorts', 'port')

	print >> target, "%d,%s,%s,%s,%s,%s,%s,%s,%s" %(number, subdict['name'],subdict['action'],srczn,srcnet,srcprt,dstzn,dstnet,dstprt)
	#print "%d,%s,%s,%s,%s,%s,%s,%s,%s" %(number, subdict['name'],subdict['action'],srczn,srcnet,srcprt,dstzn,dstnet,dstprt)
	number+=1
	time.sleep(.5)

target.close()








