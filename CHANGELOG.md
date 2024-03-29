# Change Log
All notable changes to this project will be documented in this file.

## 0.21 - 2022-12-04
### Changed
* Improved python syntax formatting.
* Improved interpretation of DNS responses.

## 0.20 - 2022-01-23
### Changed
* Fixed display output to be better formatted.

## 0.19 - 2021-08-24
### Changed
* Fixed bug around UUID and Tag handling.
* Improved object names and comments in script.

## 0.18 - 2021-08-22
### Added
* Added the ability to resolve different DNS requests - SOA, NS, CNAME, A, AAAA, PTR, MX. By default an entry in queries file that doesn't have a DNS type will be assumed to be an 'A' record. Refer to readme for format of queries file.
* Added --displayResponses option with column formatting. 
* With newer improvements for DNS queries, included a data structure format version tag in json output.

### Changed
Updated the display results formatting when run from command line.


## 0.17 - 2021-08-15
### Added
Added the ability to download nameservers and queries entries from a webserver (both HTTP and HTTPS). I have not added support for error handling when the hostname in the URL is invalid.

## 0.16 - 2021-08-14
### Added
Allows the ability to upload the json data through the HTTP POST method.

## 0.15 - 2021-08-14
### Fixed
Fixed a minor bug with a_responseTTL variable and a DNS nameserver response timing out.

## 0.14 - 2021-08-14
### Added
Included response time-to-live (TTL) from name server.

## 0.13 - 2021-05-29
### Added
Improved code comments for better programming interpretation.

## 0.12 - 2021-05-22
### Added
Added the ability to manage tags from device.

## 0.11 - 2021-05-22
### Changed
Minor change logic around how arguments are parsed.

## 0.10 - 2021-05-22
### Added
Added options for managing UUID and tag files.


## 0.10 - 2021-05-22
### Changed
Fixed logic for print results to files, stdout, etc.

## 0.09 - 2021-05-22
### Added
* Ability to tag results for aggregating data. To use, create a 'tag.cfg' file in the same working directory as dns-resolution-test.py and insert a label. For example:
```bash
echo "production" > tag.cfg
```
If the tag.cfg file does not exist then the deviceTag field is "".


## 0.08 - 2021-05-22
### Added
* Added script start and end time (UTC format) to json results.
* Added hostname gathering feature to json results
* Added UUID creation feature to track results across multiple devices.

## 0.07 - 2021-05-20

### Added
Added argument option to print results in json format to stdout

### Changed
Amended results field from DNS query to "Err" if there's a:
* DNS Timeout
* No response


## 0.06 - 2021-05-20
### Changed
Minor adjustment to output data to output.json, not output.txt

## 0.05 - 2021-05-01
### Added
Added error handling for dns.resolver.NoNameservers

## 0.04 - 2021-04-30 
### Changed
Improved error handling and display output. Display entries being loaded from files. 

## 0.03 - 2021-04-17
### Added
Added ability to display verbose results.

### Changed
None

### Fixed
None

## 0.02 - 2021-04-16

### Added
Added ability to grab custom input files for nameservers and queries.

### Changed
None

### Fixed
None

## 0.01 - 2021-04-14

Initial build.

### Added
Added ability to perform DNS queries to multiple name servers and measure the response time.


### Changed
None

### Fixed
None
 
 
 
