# json2excel convertor

This python script will help convert the json data into a more readable format in excel.

As of now, the spreadsheet will highlight (in red) any response times above the average.

By default it will look for the file **output.json** and output the data into **output.xlsx**.

## Arguments
```bash
  --jsonfile JSONFILE     json formatted results from dns-resolution-test script
  --excelfile EXCELFILE   the excel file where you want to format the results
```

## Future improvements
* Highlight results above a configurable response time
