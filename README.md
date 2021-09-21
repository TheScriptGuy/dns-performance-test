# dns-performance-test

This script will query DNS servers with a provided query list and measure the response time.

## Device Identification

In order to track multiple results from different hosts, the hostname and a unique ID is gathered from each host where the script runs.

For the UUID, when the script runs for it's initial attempt, it'll try and see if there's a uuid.cfg file. 
* If there is a uuid.cfg file, it'll read the contents and use that for identification.
* if there is not a uuid.cfg file, it'll create a new uuid and write that to uuid.cfg.

## UUID
To read the current UUID for the device:
```bash
python3 dns-resolution-test.py --getUuid
```

To delete the UUID, ether remove the uuid.cfg file, or run the command:
```bash
python3 dns-resolution-test.py --deleteUuid
```

To renew/reset the UUID:
```bash
python3 dns-resolution-test.py --renewUuid
```

## Tags

If you want to tag your results for aggregating data across multiple devices, do the following:
```bash
python3 dns-resolution-test.py --setTag <TAGNAME>
```

If there's no tag.cfg file, then deviceTag in the output.json file is "".

If you want to remove the tag, either remove the tag.cfg file or:
```bash
python3 dns-resolution-test.py --deleteTag
```

To display the current tag:
```bash
python3 dns-resolution-test.py --getTag
```

## Reference files

By default, it'll read the inputs from filenames:
- nameservers.txt - list of DNS nameservers to query
- queries.txt - list of queries to perform on the DNS nameservers.

**It will also by default not create any output (file, stdout, other).**

The queries file will accept entries in the following formats:
```
test.com
123.123.123.123,ptr
abc.com,a
cnn.com,mx
google.com,aaaa
```

If an entry has an incorrect DNS query type, for example - referencing 'aaa' (invalid) instead of 'aaaa' (valid IPv6 query type), the program will not stop, but will report an error and continue to the next entry.

## Arguments

If you want output there are some options available (in any combination):
```
  --ifname IFNAME      List of nameserver IP addresses file, each entry on a new line. This can be a URL as well.
  --ifquery IFQUERY    List of queries file to be performed, each entry on a new line. This can be a URL as well.
  --ofresults          JSON results output file (uuid,tag,script start time, script end time, results)
  --jsonstdout         print results to stdout
  --displayResponses   Display formatted results
  --verbose            Displays the response times of all the tests.
  --setTag SETTAG      Set the tag for the query results. Creates tag.cfg file with tag.
  --deleteTag          Delete the tag file - tag.cfg
  --getTag             Get the tag from tag.cfg file
  --renewUuid          Renew the UUID value.
  --getUuid            Get the UUID value from uuid.cfg file.
  --deleteUuid         Remove the UUID value. Caution: when script runs again a new UUID will be generated.
  --httpPOST HTTPPOST  Upload the JSON results to the URL
```


## JSON Sample format

```json
{
  "deviceUuid": "<UUID>",
  "hostName": "<HOSTNAME>",
  "deviceTag": "<DEVICETAG>",
  "scriptUTCStartTime": "<Script start time in UTC Format>",
  "scriptUTCEndTime": "<Script end time in UTC Format>",
  "dataFormatVersion": 3,
  "queryResults": {
    "dnsNameServerIP": [
      {
        "query": {
          "queryType": "hostname.example"
        },
        "response": [
          "<IP1>"
        ],
        "responseTime": "<Time in Milliseconds for response>",
        "responseTTL": <time_in_seconds_from_nameserver>
      },
      {
        "query": {
          "queryType": "hostname2.example2"
        },
        "response": [
          "<IP1>",
          "<IP2>"
        ],
        "responseTime": "<Time in Millseconds for response>",
        "responseTTL": <time_in_seconds_from_nameserver>
      },
      {
        "query": {
          "queryType": "hostname3.example3"
        },
        "response": [
          "<IP1>",
          "<IP2>",
          "<IP3>",
          "<IP4>"
        ],
        "responseTime": "<Time in Millseconds for response>",
        "responseTTL": <time_in_seconds_from_nameserver>
      }
    ]
  }
}
```

## Actual Sample Result:

```json
{
  "deviceUuid": "c166d274-2fca-42c2-9a26-d1887ca97bb2",
  "hostName": "myTestHost",
  "deviceTag": "production",
  "scriptStartTime": "2021-05-22 20:25:49.706083",
  "scriptEndTime": "2021-05-22 20:25:49.748855",
  "dataFormatVersion": 3,
  "queryResults": {
    "8.8.8.8": [
      {
        "query": {
          "a": "test.com"
        },
        "response": [
          "69.172.200.235"
        ],
        "responseTime": "7.1",
        "responseTTL": 311
      },
      {
        "query": {
          "a": "google.com"
        },
        "response": [
          "142.250.217.110"
        ],
        "responseTime": "13.3",
        "responseTTL": 3429
      },
      {
        "query": {
          "a": "abc.com"
        },
        "response": [
          "99.84.73.44",
          "99.84.73.60",
          "99.84.73.41",
          "99.84.73.70"
        ],
        "responseTime": "21.8",
        "responseTTL": 151
      },
      {
        "query": {
          "mx": "testdomain.com"
        },
        "response": [
          "20 mail.testdomain.com.",
          "20 mail2.testdomain.com.",
          "30 mail3.testdomain.com."
        ]   
      }
    ]
  }
}
```


Future improvements:
* default list of nameservers and queries to be included in bundle
* ability to publish results to google sheets, ms excel online, etc.
* show if the DNS lookup is a PASS/FAIL based on evaluating criteria.
** evaluation criteria:
*** ALL responses must be the same
*** ANY of the responses must be what we expect
** ability to set an evaluation file based on immediate results for comparison later.
