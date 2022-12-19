# DNS Performance Testing
# Version:            0.21
# Last updated:       2022-12-04
import sys
import argparse
import json
import dns.resolver
from datetime import datetime, timedelta
import os.path
from os import path

from systemInfo import systemInfo, systemData

import requests

# Global Variables
dnsResponseTextMaxLength = 0
scriptVersion = "0.21"

def writeResults(results, outputFile):
    """Send the json data to the outputFile variable."""
    with open(outputFile, "w", encoding="utf-8") as outputFile:
        outputFile.write(json.dumps(results))


def printJsonStdout(results):
    """This will output the json data to stdout."""
    print(json.dumps(results))
    print()


def uploadJsonHTTP(url, jsonData):
    """
    This will upload the json data to a URL via a POST method.
    If the verbose argument is set, it'll display what URL it's being
    submitted to as well as the json data (jsonData).
    When the response is returned, it'll return the X-Headers that are sent back
    from the server.
    """
    x = requests.post(url, json=jsonData)
    if args.verbose:
        print('Submission URL: ', url)
        print('jsonData: ', json.dumps(jsonData))
        print('X-Headers: ', x.headers)
    return x.headers


def getFileFromURL(fileURL):
    """This function will download the contents of fileURL and return a list with the contents."""
    tmpData = []
    try:
        urlData = requests.get(fileURL)
        if urlData.status_code == 200:
            tmpData = urlData.text.split('\n')
            try:
                # Attempt to remove any blank entries in the dict
                tmpData.remove('')
            except ValueError:
                # Do nothing
                print()
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

    # Check to see if nameserversFile is a URL and if it is, attempt to download it.
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

    # Check to see if queriesFile is a URL and if it is, attempt to download it.
    if queriesFile.startswith('http://') or queriesFile.startswith('https://'):
        queries = getFileFromURL(queriesFile)
        return queries

    # Check to see if if the file exists. If not, exit with error code 1.
    if not path.exists(queriesFile):
        print('I cannot find file ' + queriesFile)
        sys.exit(1)

    if args.verbose:
        print('Loading queries from ' + queriesFile)

    queryFile = open(queriesFile, "r", encoding="utf-8")

    for line in queryFile:
        if ","  in line:
            tmpLine = line.rstrip('\n').split(',')
            queries.append({tmpLine[1]: tmpLine[0]})
        else:
            queries.append({'a': line.rstrip('\n')})

        if args.verbose:
            print(line.rstrip('\n'), end=' ')

    if args.verbose:
        print()
        print(queries)

    queryFile.close()

    return queries


def displayResults(results):
    """
    This will display the results to stdout. Not always formatted correctly
    because the responses could have a variable number.
    """
    # Get the global variable dnsResponseTextMaxLength
    global dnsResponseTextMaxLength
    filler = ' '

    if args.verbose:
        print("dnsResponseTextMaxLength = ", dnsResponseTextMaxLength)

    headers = ['DNS Server', 'DNS Type', 'DNS Query', 'DNS Response', 'Response Time (ms)', 'DNS TTL']

    # DNS Column lengths
    dnsServerLength = 18
    dnsQueryTypeLength = 15
    dnsQueryLength = 30
    dnsResponseTextMaxLength += 10
    dnsResponseTimeLength = 20
    dnsResponseTTLLength = 8

    # Print the headers with appropriate spacing.
    for count, item in enumerate(headers):
        if count == 0:
            # DNS Server
            print(f'{item:{filler}<{dnsServerLength}}', end='')

        if count == 1:
            # DNS Type
            print(f'{item:{filler}<{dnsQueryTypeLength}}', end='')

        if count == 2:
            # DNS Query
            print(f'{item:{filler}<{dnsQueryLength}}', end='')

        if count == 3:
            # DNS Response
            print(f'{item:{filler}<{dnsResponseTextMaxLength}}', end='')

        if count == 4:
            # Response Time (ms)
            print(f'{item:{filler}<{dnsResponseTimeLength}}', end='')

        if count == 5:
            # DNS TTL
            print(f'{item:{filler}<{dnsResponseTTLLength}}', end='')

    print()

    # Iterate through the response data and format the columns with appropriate spaces.
    for nameserverItem in results:
        for dataItem in results[nameserverItem]:
            print(f'{nameserverItem:{filler}<{dnsServerLength}}', end='')

            for dataItem2 in dataItem:
                if dataItem2 == 'query':
                    queryType = list(dataItem[dataItem2].items())[0][0]
                    queryName = list(dataItem[dataItem2].items())[0][1]
                    print(f'{queryType:{filler}<{dnsQueryTypeLength}}', end='')
                    print(f'{queryName:{filler}<{dnsQueryLength}}', end='')

                if dataItem2 == 'response':
                    dnsElements = list(dataItem[dataItem2])

                    dnsResponseFormatted = ','.join(dnsElements)
                    print(f'{dnsResponseFormatted:{filler}<{dnsResponseTextMaxLength}}', end='')

                if dataItem2 == 'responseTime':
                    responseTime = dataItem[dataItem2]
                    print(f'{responseTime:{filler}<{dnsResponseTimeLength}}', end='')

                if dataItem2 == 'responseTTL':
                    responseTTL = dataItem[dataItem2]
                    print(f'{responseTTL:{filler}<{dnsResponseTTLLength}}')


def performQueries(nameservers, queries):
    """This will perform all the all the queries against each nameserver."""
    # Set the resolver
    resolver = dns.resolver.Resolver()

    # Set the results to empty dict
    results = {}

    counter = 1

    totalQueries = len(nameservers) * len(queries)

    # Get the global variable dnsResponseTextMaxLength
    global dnsResponseTextMaxLength

    for server in nameservers:
        # Set the name servers to a single list entry.
        # We don't need multiple failover nameservers because we want
        # a result from each name server and want to point out any failures.
        resolver.nameservers = [server]
        for query in queries:
            # Display the query count to keep track of progress.
            queryType = list(query.items())[0][0].lower()
            queryName = list(query.items())[0][1].lower()

            if args.verbose:
                print('Query = ' + str(query))
                print('Query count = ' + str(counter) + ' of ' + str(totalQueries))

            # Start Query Time
            queryStartTime = datetime.now()

            try:
                if queryType == "ptr":
                    answer = resolver.resolve_address(queryName)
                else:
                    answer = resolver.resolve(queryName, queryType)

            # If there's a timeout, display the timeout, which query and which nameserver
            # typical timeout is 5.5s

            except dns.rdatatype.UnknownRdatatype:
                print('Unkown DNS response - ' + str(query) + ' @' + server)
                answer = []

            except dns.resolver.NoAnswer:
                # No answer from DNS server
                print('No DNS answer - ' + str(query) + ' @' + server)
                answer = []

            except dns.exception.Timeout:
                # DNS Server timed out
                print('DNS Timeout - ' + str(query) + ' @' + server)
                answer = []

            except dns.resolver.NXDOMAIN:
                # NXDOMAIN response from DNS server
                print('NXDOMAIN response - ' + str(query) + ' @' + server)
                answer = []

            except dns.resolver.NoNameservers:
                # If there are no responses from name servers, display No Response.
                print('No response. ' + str(query) + ' @' + server)
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
                if queryType in ("a", "aaaa"):
                    for counter, response in enumerate(answer):
                        aResponse = response.address
                        l_response.append(aResponse)
                        currentLength = len(str(aResponse)) * (counter + 1)
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                if queryType == "mx":
                    for response in answer:
                        mxResponse = response.to_text()
                        l_response.append(mxResponse)
                        currentLength = len(str(mxResponse))
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                if queryType == "ptr":
                    for response in answer:
                        ptrResponse = response.to_text()
                        l_response.append(ptrResponse)
                        currentLength = len(str(ptrResponse))
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                if queryType == "soa":
                    for response in answer:
                        soaResponse = response.to_text().split(' ')[0]
                        l_response.append(soaResponse)
                        currentLength = len(str(soaResponse))
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                if queryType == "cname":
                    for response in answer:
                        cnameResponse = response.to_text()
                        l_response.append(cnameResponse)
                        currentLength = len(str(cnameResponse))
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                if queryType == "ns":
                    for response in answer:
                        nsResponse = response.to_text()
                        l_response.append(nsResponse)
                        currentLength = len(str(nsResponse))
                        dnsResponseTextMaxLength = max(dnsResponseTextMaxLength, currentLength)

                a_responseTTL = answer.rrset.ttl
            else:
                a_responseTTL = -1
                l_response.append('Err')
                if dnsResponseTextMaxLength < 3:
                    dnsResponseTextMaxLength = 4

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


def gatherData(queryResults, scriptStartTime, scriptEndTime):
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
        "dataFormatVersion": 3,
        "queryResults": queryResults
    }

    return myData


def parseArguments():
    """Create argument options and parse through them to determine what to do with script."""
    # Instantiate the parser
    global scriptVersion
    parser = argparse.ArgumentParser(description='DNS Performance Testing ' + scriptVersion)

    # Optional arguments
    parser.add_argument('--ifname', default="nameservers.txt",
                        help='List of nameserver IP addresses, each on a new line')

    parser.add_argument('--ifquery', default='queries.txt',
                        help='List of queries to be performed.')

    parser.add_argument('--ofresults', action='store_true',
                        help='JSON results output file')

    parser.add_argument('--jsonstdout', action='store_true',
                        help='print results to stdout')

    parser.add_argument('--displayResponses', action='store_true',
                        help='Display formatted results')

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


def defineInfoArguments(o_systemData, o_systemInfo):
    """defineInfoArguments definition"""
    global args
    # If setTag argument is set, create the new Tag.
    if args.setTag:
        o_systemData.setTag(args.setTag)
        print('New tag set.')
        sys.exit(0)

    # If getTag is set, it will grab the value in tag.cfg file.
    if args.getTag:
        print(o_systemInfo.getTag())
        sys.exit(0)

    # If deleteTag is set, it will delete the tag.cfg file.
    if args.deleteTag:
        o_systemData.deleteTag()
        sys.exit(0)

    # If getUuid is set, it grab the value in uuid.cfg
    if args.getUuid:
        print(o_systemInfo.getUuid())
        sys.exit(0)

    # If deleteUuid is set, the uuid.cfg file will be deleted.
    if args.deleteUuid:
        o_systemData.deleteUuid()
        sys.exit(0)

    # If renewUuid is set, first delete uuid.cfg file, then generate a new uuid.
    if args.renewUuid:
        o_systemData.deleteUuid()
        o_systemData.createUuidIfNotExist()
        sys.exit(0)


def main():
    """main definition"""
    # Parse all the arguments
    parseArguments()

    # Gather the information from the device where the script is executed.
    o_mySystemData = systemData.systemData()
    o_myInfo = systemInfo.systemInfo()

    defineInfoArguments(o_mySystemData, o_myInfo)

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

    results = performQueries(nameservers, queries)

    # If verbose argument is parsed, display the results to stdout.
    if args.verbose:
        print(results)

    if args.displayResponses:
        displayResults(results)

    # Script end time (UTC format)
    scriptEndTime = datetime.utcnow()

    # If verbose argument is set, display script end time.
    if args.verbose:
        print('\nScript stop time: ', str(scriptEndTime))

    # Collate all the data into myData
    myData = gatherData(results, str(scriptStartTime), str(scriptEndTime))

    # If the httpPOST argument is set, send the json data to the URL via POST method
    if args.httpPOST:
        print(uploadJsonHTTP(args.httpPOST, myData))

    # If the jsonstdout argument is set, then print myData to stdout.
    if args.jsonstdout:
        printJsonStdout(myData)

    # If the ofresults is set, output the data to outputFileResults.
    # Results will always be overwritten.
    if args.ofresults:
        writeResults(myData, outputFileResults)


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
