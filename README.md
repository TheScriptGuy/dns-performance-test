# dns-performance-test

This script will query DNS servers with a provided query list and measure the response time.

By default, it'll read the inputs from filenames:
- nameservers.txt - list of DNS nameservers to query
- queries.txt - list of queries to perform on the DNS nameservers.
- output.json - the results of querying all the nameservers and their response times in JSON format.


Future improvements:
* default list of nameservers and queries to be included in bundle
* ability to download nameservers and queries from a URL
* ability to publish the output to a webserver somewhere.
