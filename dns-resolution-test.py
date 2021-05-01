# DNS Performance Testing
# Version:            0.04
# Last updated:       2021-04-30
# Changelog:          0.04 - Improved error handling and display output. Display entries being loaded from files.
#                     0.03 - Adding detailed results output
#                     0.02 - added argument parsing
#                     0.01 - initial build


import sys
import argparse
import json
import dns.resolver
from datetime import datetime, timedelta
import os.path
from os import path

def writeResults(results, outputFile):
    outputfile = open(outputFile,"w",encoding="utf-8")
    
    outputfile.write(json.dumps(results)) 
    
    outputfile.close()



def loadNameServersFile(nameserversFile):
    print('Loading the nameservers that are to be queried.')
    
    dnsNameServers = []
    
    if not path.exists(nameserversFile):
        print('I cannot find file ' + nameserversFile)
        sys.exit(1)

    nameServerFile = open(nameserversFile, "r", encoding="utf-8")

    for line in nameServerFile:
        print(line.rstrip('\n'), end=' ')
        dnsNameServers.append(line.rstrip('\n'))
    
    print()
    #print(dnsNameServers)
    return dnsNameServers


def loadQueriesFile(queriesFile):

    queries = []

    if not path.exists(queriesFile):
        print('I cannot find file ' + queriesFile)
        sys.exit(1)

    print('Loading queries from ' + queriesFile)

    

    queryFile = open(queriesFile, "r", encoding="utf-8")

    for line in queryFile:
        print(line.rstrip('\n'),end=' ')
        queries.append(line.rstrip('\n'))
    
    print()

    queryFile.close()

    return queries



def displayResults(results):
    headers = ['DNS Server','DNS Query', 'DNS Response', 'Response Time (ms)']
    print(*headers,sep='\t\t')

# dataItem =  {'query': 'test.com', 'response': ['69.172.200.235'], 'responseTime': '14.8'}
#dataItem2 =  query
#dataItem2 =  response
#dataItem2 =  responseTime
#dataItem =  {'query': 'google.com', 'response': ['142.250.69.206'], 'responseTime': '7.3'}
#dataItem2 =  query
#dataItem2 =  response
#dataItem2 =  responseTime
#dataItem =  {'query': 'abc.com', 'response': ['99.86.38.114', '99.86.38.15', '99.86.38.42', '99.86.38.122'], 'responseTime': '32.8'}
#dataItem2 =  query
#dataItem2 =  response
#dataItem2 =  responseTime

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
            if not args.verbose:
                print('Query count = ' + str(counter))

            queryStartTime = datetime.now()

            try:
                answer = resolver.resolve(query)
            except dns.exception.Timeout:
                print('DNS Timeout - ' + query + ' @' + server)
                answer = []

            queryEndTime = datetime.now()
            queryTime = (queryEndTime - queryStartTime).total_seconds() * 1000

            s_queryTime = str("{:.1f}".format(queryTime))
            
            l_response = []
            
            for response in answer:
                l_response.append(response.address)

            if server not in results:
                results[server] = []

            try:

                thisQuery = {"query": query, "response": l_response, "responseTime": s_queryTime}
                results[server].append(thisQuery)
                
                counter += 1

            except KeyError:
                print('I made an oops.')

    return results


def parseArguments():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='DNS Performance testing')

    # Optional arguments
    parser.add_argument('--ifname', default="nameservers.txt",
                        help='List of nameserver IP addresses, each on a new line')

    parser.add_argument('--ifquery', default='queries.txt',
                        help='List of queries to be performed.')

    parser.add_argument('--ofresults', default='output.txt',
                        help='JSON results output file')


    parser.add_argument('--verbose', action='store_true',
                        help='Displays the response times of all the tests.')

    global args
    args = parser.parse_args()



def main():
    
    
    parseArguments()
    
    timenow = datetime.utcnow()
    print('Script start time: ', str(timenow), '\n')
        
    
    queryFile = args.ifquery
    nameserversFile = args.ifname
    outputResults = args.ofresults

    queries = loadQueriesFile(queryFile)
    nameservers = loadNameServersFile(nameserversFile)
    
    results = performQueries(nameservers,queries)

    displayResults(results)

    writeResults(results,outputResults)


    timenow = datetime.utcnow()
    print('\nScript stop time: ', str(timenow))



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

