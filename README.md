# dns-performance-test

This script will query DNS servers with a provided query list and measure the response time.

In order to track multiple results from different hosts, the hostname and a unique ID is gathered from each host where the script runs.

For the UUID, when the script runs for it's initial attempt, it'll try and see if there's a uuid.cfg file. 
* If there is a uuid.cfg file, it'll read the contents and use that for identification.
* if there is not a uuid.cfg file, it'll create a new uuid and write that to uuid.cfg.

If you want to tag your results for aggregating data across multiple devices, create a 'tag.cfg' file in the same working directory as dns-resolution-test.py and insert a label. For example:
```bash
echo "production" > tag.cfg
```

If there's no tag.cfg file, then deviceTag in the output.json file is "".

By default, it'll read the inputs from filenames:
- nameservers.txt - list of DNS nameservers to query
- queries.txt - list of queries to perform on the DNS nameservers.

If the argument '--ofresults' is added:
- output.json - the results of querying all the nameservers and their response times in JSON format.


```json
{
  "deviceUuid": "<UUID>",
  "hostName": "<HOSTNAME>",
  "deviceTag": "<DEVICETAG>",
  "scriptUTCStartTime": "<Script start time in UTC Format>",
  "scriptUTCEndTime": "<Script end time in UTC Format>",
  "queryResults": {
    "dnsNameServerIP": [
      {
        "query": "hostname.example",
        "response": [
          "<IP1>"
        ],
        "responseTime": "<Time in Milliseconds for response>"
      },
      {
        "query": "hostname2.example2",
        "response": [
          "<IP1>",
          "<IP2>"
        ],
        "responseTime": "<Time in Millseconds for response>"
      },
      {
        "query": "hostname3.example3",
        "response": [
          "<IP1>",
          "<IP2>",
          "<IP3>",
          "<IP4>"
        ],
        "responseTime": "<Time in Millseconds for response>"
      }
    ]
  }
}
```

Sample result:

```json
{
  "deviceUuid": "c166d274-2fca-42c2-9a26-d1887ca97bb2",
  "hostName": "myTestHost",
  "deviceTag": "production",
  "scriptStartTime": "2021-05-22 20:25:49.706083",
  "scriptEndTime": "2021-05-22 20:25:49.748855",
  "queryResults": {
    "8.8.8.8": [
      {
        "query": "test.com",
        "response": [
          "69.172.200.235"
        ],
        "responseTime": "7.1"
      },
      {
        "query": "google.com",
        "response": [
          "142.250.217.110"
        ],
        "responseTime": "13.3"
      },
      {
        "query": "abc.com",
        "response": [
          "99.84.73.44",
          "99.84.73.60",
          "99.84.73.41",
          "99.84.73.70"
        ],
        "responseTime": "21.8"
      }
    ]
  }
}
```


Future improvements:
* default list of nameservers and queries to be included in bundle
* ability to download nameservers and queries from a URL
* ability to publish the output to a webserver somewhere (HTTP POST)
* ability to perform different types of nameservers queries (A, PTR, CNAME, MX, COA, NS)
* ability to create excel spreadsheet with all tests.
    * extending this to perform conditional highlighting of cells with large latency (>100ms)
    * highlight responseTime results that are beyond a certain threshold compared to other results.
* ability to publish results to google sheets, ms excel online, etc.
