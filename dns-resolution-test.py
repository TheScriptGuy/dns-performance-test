# DNS Performance Testing
# Version:            0.17
# Last updated:       2021-08-15

import sys
import argparse
import json
import dns.resolver
from datetime import datetime, timedelta
import os.path
from os import path

from systemInfo import systemInfo,systemData

import requests

def writeResults(results, outputFile):
    """
    Send the json data to the outputFile variable.
    """
    outputfile = open(outputFile,"w",encoding="utf-8")
    
    outputfile.write(json.dumps(results)) 
    
    outputfile.close()

def printJsonStdout(results):
    """
    This will output the json data to stdout.
    """
    print(json.dumps(results))
    print()

def uploadJsonHTTP(url,jsonData):
    """
    This will upload the json data to a URL via a POST method.
    If the verbose argument is set, it'll display what URL it's being 
    submitted to as well as the json data (jsonData).
    When the response is returned, it'll return the X-Headers that are sent back
    from the server.
    """   
    x = requests.post(url, json = jsonData)
    if args.verbose:
        print('Submission URL: ', url)
        print('jsonData: ', json.dumps(jsonData))
        print('X-Headers: ',x.headers)
    return x.headers

def getFileFromURL(fileURL):
    """
    This function will download the contents of fileURL and return a list with the contents.
    """
    tmpData = []
    try:
        urlData = requests.get(fileURL)
        if urlData.status_code == 200:
            tmpData = urlData.text.split('\n')
            try:
                """
                Attempt to remove any blank entries in the dict
                """
                tmpData.remove('')
            except ValueError:
                """
                Do nothing
                """
        else:
            tmpData = ['Error while retrieving URL']
    except socket.gaierror:
        print('Invalid hostname')
        tmpData = ['URL error']
    except requests.exceptions.Timeout:
        print('Timeout while retrieving URL.')
        tmpData = ['URL Timeout']
    except requests.exceptions.TooManyRedirects:
        print('Too many redirects while accessing the URL')
        tmpData = ['URL Redirects too many']
    except requests.exceptions.ConnectionError:
        print('Could not connect to URL - ' + fileURL + '\n')
        tmpData = ['URL connection error']
    return tmpData


def loadNameServersFile(nameserversFile):
    """
    This will load the name servers from the file nameserversFile.
    Each name server should be on it's own line.
    """
    
    dnsNameServers = []
    
    """
    Check to see if nameserversFile is a URL and if it is, attempt to download it
    """

    if nameserversFile.startswith('http://') or nameserversFile.startswith('https://'):
        dnsnameServers = getFileFromURL(nameserversFile)
        return dnsnameServers
   

    if not path.exists(nameserversFile):
        print('I cannot find file ' + nameserversFile)
        sys.exit(1)

    if args.verbose:
        print('Loading the nameservers that are to be queried.')
    
    nameServerFile = open(nameserversFile, "r", encoding="utf-8")

    for line in nameServerFile:
        if args.verbose:
            print(line.rstrip('\n'), end=' ')
        dnsNameServers.append(line.rstrip('\n'))
    if args.verbose:
        print()

    return dnsNameServers


def loadQueriesFile(queriesFile):
    """
    This will load the queries that need to be performed against each name server.
    One query per line. Right now it's only meant to be for 'A' record resolutions.
    """
    queries = []


    """
    Check to see if queriesFile is a URL and if it is, attempt to download it
    """
    if queriesFile.startswith('http://') or queriesFile.startswith('https://'):
        queries = getFileFromURL(queriesFile)
        return queries


    """
    Check to see if if the file exists. If not, exit with error code 1.
    """
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
    """
    This will display the results to stdout. Not always formatted correctly 
    because the responses could have a variable number.
    """
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
    """
    This will perform all the all the queries against each nameserver.
    """

    # Set the resolver
    resolver = dns.resolver.Resolver()
    # Set the results to empty dict
    results = {}

    counter = 1

    totalQueries = len(nameservers) * len(queries)

    for server in nameservers:
        # Set the name servers to a single list entry.
        # We don't need multiple failover nameservers because we want 
        # a result from each name server and want to point out any failures.
        resolver.nameservers = [server]
        for query in queries:
            # Display the query count to keep track of progress.
            if args.verbose:
                print('Query count = ' + str(counter) + ' of ' + str(totalQueries))

            # Start Query Time
            queryStartTime = datetime.now()

            try:
                answer = resolver.resolve(query)

            # If there's a timeout, display the timeout, which query and which nameserver
            # typical timeout is 5.5s
            except dns.exception.Timeout:
                print('DNS Timeout - ' + query + ' @' + server)
                answer = []

            # If there are no responses from name servers, display No Response.
            # Also print the query and name servers.
            except dns.resolver.NoNameservers:
                print('No response. ' + query + ' @' + server)
                answer = []

            # End query time. 
            queryEndTime = datetime.now()

            # Calculate the difference between End Query Time and Start Query Time
            # Multiply the result by a 1000 to get millisecond response.
            queryTime = (queryEndTime - queryStartTime).total_seconds() * 1000

            # Format the queryTime response.
            s_queryTime = str("{:.1f}".format(queryTime))
            
            l_response = []
           
            # If there were any answers from the query, append the response 
            # to l_response.
            # If there were any errors, add 'Err'
            if answer:
                for response in answer:
                    l_response.append(response.address)
                a_responseTTL = answer.rrset.ttl

            else:
                a_responseTTL = -1
                l_response.append('Err')

            # If the server is not in the results, set the response to a blank list.
            if server not in results:
                results[server] = []

            try:
                # Create the json dict with all of the responses.
                thisQuery = {"query": query, "response": l_response, "responseTime": s_queryTime, "responseTTL": a_responseTTL}
                results[server].append(thisQuery)
                
                counter += 1

            except KeyError:
                # If there's some accidental programming error, then display error.
                print('I made an oops.')

    return results

def gatherData(queryResults,scriptStartTime,scriptEndTime):
    """
    This will collect all the data into a uniform data structure that can 
    help with measuring results across multiple executions. 

    Data that is included is:
    * deviceUuid         - a unique device identifier.
    * deviceTag          - a tag for the device to help with aggregating data across.
                           multiple endpoints (for example all production, development, qa devices).
    * hostName           - the hostname of the device where script is executing.
    * scriptUTCStartTime - script start time (UTC format).
    * scriptUTCEndTime   - script end time (UTC format).
    * queryResults       - The results of all queries that were performed against the nameservers.  
    """
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

    parser.add_argument('--httpPOST', default='',
                        help='Upload the JSON results to the URL')

    global args
    args = parser.parse_args()



def main():
    # Parse all the arguments
    parseArguments()
    
    # Gather the information from the device where the script is executed.
    o = systemData.systemData()
    myInfo = systemInfo.systemInfo()

    # If setTag argument is set, create the new Tag.
    if args.setTag:
        o.setTag(args.setTag)
        print('New tag set.')
        sys.exit(0)

    # If getTag is set, it will grab the value in tag.cfg file.
    if args.getTag:
        print(myInfo.getTag())
        sys.exit(0)
    
    # If deleteTag is set, it will delete the tag.cfg file.
    if args.deleteTag:
        o.deleteTag()
        sys.exit(0)

    # If getUuid is set, it grab the value in uuid.cfg
    if args.getUuid:
        print(myInfo.getUuid())
        sys.exit(0)

    # If deleteUuid is set, the uuid.cfg file will be deleted.
    if args.deleteUuid:
        o.deleteUuid()
        sys.exit(0)

    # If renewUuid is set, first delete uuid.cfg file, then generate a new uuid.
    if args.renewUuid:
        o.deleteUuid()
        o.createUuidIfNotExist()
        sys.exit(0)


    # Script start time (UTC format)
    scriptStartTime = datetime.utcnow()

    # If verbose argument is set, display the script start time to stdout.
    if args.verbose:
        print('Script start time: ', str(scriptStartTime), '\n')
        
    
    # Query file from ifquery argument
    queryFile = args.ifquery

    # Nameserver file from ifname argument
    nameserversFile = args.ifname

    # Results to be written to output.json
    outputFileResults = 'output.json'
    
    queries = loadQueriesFile(queryFile)
    nameservers = loadNameServersFile(nameserversFile)
    
    results = performQueries(nameservers,queries)

    # If verbose argument is parsed, display the results to stdout.
    if args.verbose:
        displayResults(results)

    # Script end time (UTC format)
    scriptEndTime = datetime.utcnow()
    
    # If verbose argument is set, display script end time.
    if args.verbose:
        print('\nScript stop time: ', str(scriptEndTime))
    
    # Collate all the data into myData
    myData = gatherData(results,str(scriptStartTime),str(scriptEndTime))
    
    # If the httpPOST argument is set, send the json data to the URL via POST method
    if args.httpPOST:
        print(uploadJsonHTTP(args.httpPOST,myData))

    # If the jsonstdout argument is set, then print myData to stdout.
    if args.jsonstdout:
        printJsonStdout(myData)
    
    # If the ofresults is set, output the data to outputFileResults.
    # Results will always be overwritten.
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

