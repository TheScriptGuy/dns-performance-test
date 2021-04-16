import sys
import json
import dns.resolver
from datetime import datetime, timedelta


def writeResults(results, outputFile):
    outputfile = open(outputFile,"w",encoding="utf-8")
    
    outputfile.write(json.dumps(results)) 
    
    outputfile.close()



def loadNameServersFile(nameserversFile):
    print('Loading the nameservers that are to be queried.')
    
    dnsNameServers = []

    nameServerFile = open(nameserversFile, "r", encoding="utf-8")

    for line in nameServerFile:
        #print(line.rstrip('\n'))
        dnsNameServers.append(line.rstrip('\n'))

    #print(dnsNameServers)
    return dnsNameServers


def loadQueriesFile(queriesFile):
    queries = []

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


def main():
    queries = loadQueriesFile('queries.txt')
    nameservers = loadNameServersFile('nameservers.txt')

    results = performQueries(nameservers,queries)

    writeResults(results,'output.json')


if __name__ == '__main__':
    try:
        timenow = datetime.utcnow()
        print('Script start time: ', str(timenow), '\n')
        

        main()

        timenow = datetime.utcnow()
        print('\nScript stop time: ', str(timenow))


    except KeyboardInterrupt:
        print('Interrupted')
        print
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

