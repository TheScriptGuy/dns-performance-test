# DNS Performance Testing
# Version:            0.02
# Last updated:       2021-04-16
# Changelog:          0.02 - added argument parsing
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
        #print(line.rstrip('\n'))
        dnsNameServers.append(line.rstrip('\n'))

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
        #print(line.rstrip('\n'))
        queries.append(line.rstrip('\n'))

    #print(queries)
    queryFile.close()

    return queries



def displayResults(results):
    headers = ['DNS Server','DNS Query', 'DNS Response', 'Response Time (ms)']
    print(*headers,sep='\t\t')

    print('{: <24}{: <24}{}\t\t{:.1f}'.format(server,query,response,queryTime))





def performQueries(nameservers, queries):
    resolver = dns.resolver.Resolver()
    results = {}

    counter = 1

    for server in nameservers:
        resolver.nameservers = [server]
        for query in queries:
            print('Query count = ' + str(counter))
            queryStartTime = datetime.now()
            answer = resolver.resolve(query)

            queryEndTime = datetime.now()

            queryTime = (queryEndTime - queryStartTime).total_seconds() * 1000

            l_response = []

            for response in answer:
                s_queryTime = str("{:.1f}".format(queryTime))
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

