# dns-performance-test

This script will query DNS servers with a provided query list and measure the response time.

By default, it'll read the inputs from filenames:
- nameservers.txt - list of DNS nameservers to query
- queries.txt - list of queries to perform on the DNS nameservers.
- output.json - the results of querying all the nameservers and their response times in JSON format.

```json
{  
   "dnsNameServerIP": [
    {
      "query": "hostname.example",
      "response": [
        "<IP1>",
        "<IP2>",
      ],
      "responseTime": "<Time in Milliseconds for response>"
    },
    {
      "query": "hostname2.example",
      "response": [
        "<IP1>",
        "<IP2>",
        "<IP3>",
        "<IP4>"
      ],
      "responseTime": "<Time in Milliseconds for response>"
    }
  ]
}

```

Sample result:

```json
{
  "8.8.8.8": [
    {
      "query": "test.com",
      "response": [
        "69.172.200.235"
      ],
      "responseTime": "7.3"
    },
    {
      "query": "google.com",
      "response": [
        "216.58.217.46"
      ],
      "responseTime": "6.6"
    },
    {
      "query": "abc.com",
      "response": [
        "99.84.79.64",
        "99.84.79.93",
        "99.84.79.91",
        "99.84.79.12"
      ],
      "responseTime": "39.9"
    }
  ]
}

```


Future improvements:
* default list of nameservers and queries to be included in bundle
* ability to download nameservers and queries from a URL
* ability to publish the output to a webserver somewhere (HTTP POST)
* ability to create excel spreadsheet with all tests.
    * extending this to perform conditional highlighting of cells with large latency (>100ms)
    * highlight responseTime results that are beyond a certain threshold compared to other results.
* ability to publish results to google sheets, ms excel online, etc.
