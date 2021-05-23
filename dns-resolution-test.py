# DNS Performance Testing
# Version:            0.11
# Last updated:       2021-05-22

import sys
import argparse
import json
import dns.resolver
from datetime import datetime, timedelta
import os.path
from os import path

from systemInfo import systemInfo,systemData

def writeResults(results, outputFile):
    outputfile = open(outputFile,"w",encoding="utf-8")
    
    outputfile.write(json.dumps(results)) 
    
    outputfile.close()

def printJsonStdout(results):
    print(json.dumps(results))


def loadNameServersFile(nameserversFile):
    if args.verbose:
        print('Loading the nameservers that are to be queried.')
    
    dnsNameServers = []
    
    if not path.exists(nameserversFile):
        print('I cannot find file ' + nameserversFile)
        sys.exit(1)

    nameServerFile = open(nameserversFile, "r", encoding="utf-8")

    for line in nameServerFile:
        if args.verbose:
            print(line.rstrip('\n'), end=' ')
        dnsNameServers.append(line.rstrip('\n'))
    if args.verbose:
        print()

    return dnsNameServers


def loadQueriesFile(queriesFile):

    queries = []

    if not path.exists(queriesFile):
        print('I cannot find file ' + queriesFile)
        sys.exit(1)

    if args.verbose:
        print('Loading queries from ' + queriesFile)

    

    queryFile = open(queriesFile, "r", encoding="utf-8")

    for line in queryFile:
        if args.verbose:
            print(line.rstrip('\n'),end=' ')
        queries.append(line.rstrip('\n'))
    
    if args.verbose:
        print()

    queryFile.close()

    return queries



def displayResults(results):
    headers = ['DNS Server','DNS Query', 'DNS Response', 'Response Time (ms)']
    print(*headers,sep='\t\t')

    for nameserverItem in results:

        for dataItem in results[nameserverItem]:
            print('{: <15}'.format(nameserverItem),end=' ')
            for dataItem2 in dataItem:
                if dataItem2 == 'query':
                    print('\t{: <23}'.format(dataItem[dataItem2]), end=' ')
                if dataItem2 == 'response':
                    for i,responseItem in enumerate(dataItem[dataItem2]):
                        if i:
                            print(',',end='')
                        print('{}'.format(responseItem), end='')
                if dataItem2 == 'responseTime':
                    print('\t\t{}'.format(dataItem[dataItem2]))


    #print('{: <24}{: <24}{}\t\t{:.1f}'.format(server,query,response,queryTime))





def performQueries(nameservers, queries):
    resolver = dns.resolver.Resolver()
    results = {}

    counter = 1

    for server in nameservers:
        resolver.nameservers = [server]
        for query in queries:
            if args.verbose:
                print('Query count = ' + str(counter))

            queryStartTime = datetime.now()

            try:
                answer = resolver.resolve(query)
            except dns.exception.Timeout:
                print('DNS Timeout - ' + query + ' @' + server)
                answer = []

            except dns.resolver.NoNameservers:
                print('No response. ' + query + ' @' + server)
                answer = []

            queryEndTime = datetime.now()
            queryTime = (queryEndTime - queryStartTime).total_seconds() * 1000

            s_queryTime = str("{:.1f}".format(queryTime))
            
            l_response = []
           
            if answer:
                for response in answer:
                    l_response.append(response.address)
            else:
                l_response.append('Err')

            if server not in results:
                results[server] = []

            try:

                thisQuery = {"query": query, "response": l_response, "responseTime": s_queryTime}
                results[server].append(thisQuery)
                
                counter += 1

            except KeyError:
                print('I made an oops.')

    return results

def gatherData(queryResults,scriptStartTime,scriptEndTime):
    myInfo = systemInfo.systemInfo()
    
    if myInfo.uuid == "":
        n = systemData.systemData()
        n.createUuidIfNotExist()
        myInfo.uuid = myInfo.getUuid()

    myData = {
        "deviceUuid": myInfo.uuid,
        "deviceTag": myInfo.deviceTag,
        "hostName": myInfo.hostname,
        "scriptUTCStartTime": scriptStartTime,
        "scriptUTCEndTime": scriptEndTime,
        "queryResults": queryResults
    }

    return myData

def parseArguments():

    # Instantiate the parser
    parser = argparse.ArgumentParser(description='DNS Performance testing')

    # Optional arguments
    parser.add_argument('--ifname', default="nameservers.txt",
                        help='List of nameserver IP addresses, each on a new line')

    parser.add_argument('--ifquery', default='queries.txt',
                        help='List of queries to be performed.')

    parser.add_argument('--ofresults', action='store_true',
                        help='JSON results output file')

    parser.add_argument('--jsonstdout', action='store_true',
                        help='print results to stdout')

    parser.add_argument('--verbose', action='store_true',
                        help='Displays the response times of all the tests.')

    parser.add_argument('--setTag', default='',
                        help='Set the tag for the query results. Creates tag.cfg file with tag.')

    parser.add_argument('--deleteTag', action='store_true',
                        help='Delete the tag file - tag.cfg')

    parser.add_argument('--getTag', action='store_true',
                        help='Get the tag from tag.cfg file')

    parser.add_argument('--renewUuid', action='store_true',
                        help='Renew the UUID value.')

    parser.add_argument('--getUuid', action='store_true',
                        help='Get the UUID value from uuid.cfg file.')

    parser.add_argument('--deleteUuid', action='store_true',
                        help='Remove the UUID value. Caution: when script runs again a new UUID will be generated.')


    global args
    args = parser.parse_args()



def main():
    
    parseArguments()
    
    o = systemData.systemData()
    myInfo = systemInfo.systemInfo()

    if args.setTag:
        o.setTag(args.setTag)
        print('New tag set.')
        sys.exit(0)

    if args.getTag:
        print(myInfo.getTag())
        sys.exit(0)
    
    if args.deleteTag:
        o.deleteTag()
        sys.exit(0)

    if args.getUuid:
        print(myInfo.getUuid())
        sys.exit(0)

    if args.deleteUuid:
        o.deleteUuid()
        sys.exit(0)

    if args.renewUuid:
        o.deleteUuid()
        o.createUuidIfNotExist()
        sys.exit(0)


    scriptStartTime = datetime.utcnow()
    if args.verbose:
        print('Script start time: ', str(scriptStartTime), '\n')
        
    
    queryFile = args.ifquery
    nameserversFile = args.ifname
    outputFileResults = 'output.json'
    
    queries = loadQueriesFile(queryFile)
    nameservers = loadNameServersFile(nameserversFile)
    
    results = performQueries(nameservers,queries)

    if args.verbose:
        displayResults(results)

    scriptEndTime = datetime.utcnow()
    if args.verbose:
        print('\nScript stop time: ', str(scriptEndTime))
    
    myData = gatherData(results,str(scriptStartTime),str(scriptEndTime))
    
    if args.jsonstdout:
        printJsonStdout(myData)
    
    if args.ofresults:
        writeResults(myData,outputFileResults)




if __name__ == '__main__':
    try:
        
        main()


    except KeyboardInterrupt:
        print('Interrupted')
        print
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
