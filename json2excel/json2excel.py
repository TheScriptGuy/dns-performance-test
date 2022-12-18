# JSON to Excel spreadsheet
# Version:            0.02
# Last updated:       2022-12-04

import xlsxwriter
import json
import os.path
from os import path
import sys
import argparse

def copyJsonFile2Excel(jsonFile, excelFile):
    """copyJsonFile2Excel definition."""
    print('Starting conversion...')
    if path.exists(jsonFile):
        jf = open(jsonFile, 'r', encoding='utf-8')
    else:
        print('json file does not exist!')
        sys.exit(1)

    workbook = xlsxwriter.Workbook(excelFile)

    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    # Create the format options for the workbook.
    headersFormat = workbook.add_format({'bold': 1})
    responseTimeFormat = workbook.add_format({'bold': 1, 'font_color': 'red'})
    numberFormat = workbook.add_format({'num_format': '0.0'})

    # Display initial information
    worksheet.write(row, col, 'Input file:')
    worksheet.write(row, col+1, jsonFile)
    worksheet.write(row+1, col, 'Output file:')
    worksheet.write(row+1, col+1, excelFile)
    worksheet.write(row+2, col, 'Number of Nameserver Entries:')
    worksheet.write(row+3, col, 'Average response time:')
    entries =  0

    row = 6

    # Create headers for all data.
    worksheet.write(row, col, 'deviceUuid', headersFormat)
    worksheet.write(row, col+1, 'hostname', headersFormat)
    worksheet.write(row, col+2, 'deviceTag', headersFormat)
    worksheet.write(row, col+3, 'scriptStartTime', headersFormat)
    worksheet.write(row, col+4, 'scriptEndTime', headersFormat)
    worksheet.write(row, col+5, 'Nameserver', headersFormat)
    worksheet.write(row, col+6, 'Query', headersFormat)
    worksheet.write(row, col+7, 'Record', headersFormat)
    worksheet.write(row, col+8, 'Response', headersFormat)
    worksheet.write(row, col+9, 'Response Time', headersFormat)

    # Grab the first line from the file
    jf_line = jf.readline()

    # Loop through each line that is read
    while jf_line:
        json_dict  = json.loads(jf_line)

        for nsEntry in json_dict['queryResults']:
            for query in json_dict['queryResults'][nsEntry]:
                queryElements = list(query['query'].items())
                row += 1
                worksheet.write(row, col, json_dict['deviceUuid'])
                worksheet.write(row, col+1, json_dict['hostName'])
                worksheet.write(row, col+2, json_dict['deviceTag'])
                worksheet.write(row, col+3, json_dict['scriptUTCStartTime'])
                worksheet.write(row, col+4, json_dict['scriptUTCEndTime'])
                worksheet.write(row, col+5, nsEntry)
                worksheet.write(row, col+6, queryElements[0][0])
                worksheet.write(row, col+7, queryElements[0][1])
                worksheet.write(row, col+8, ','.join(query['response']))
                worksheet.write_number(row, col+9, float(query['responseTime']), numberFormat)

        # Keep track with the number of entries.
        entries += 1

        # Read the next line in the file.
        jf_line = jf.readline()

        row += 1

    # Close the jsonFile
    jf.close()

    worksheet.write(2, 1, entries)
    responseTimeArea = 'J8:J' + str(row)

    # Create a conditional format to highlight any entries above the average response time.
    worksheet.conditional_format(responseTimeArea, { 'type': 'average', 'criteria': 'above', 'format': responseTimeFormat } )

    # Display the average time at the information section of spreadsheet for comparison purposes.
    worksheet.write(3, 1, '=AVERAGE(' + responseTimeArea + ')', numberFormat)

    # Close the excel spreadsheet.
    workbook.close()

    print('Done.')

def parseArguments():
    """parseArguments definition."""
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='json to excel converter')

    # Optional arguments
    parser.add_argument('--jsonfile', default='output.json',
                        help='json formatted results from dns-resolution-test script')

    parser.add_argument('--excelfile', default='output.xlsx',
                        help='the excel file where you want to format the results')

    global args
    args = parser.parse_args()

def main():
    """Main definition."""
    parseArguments()

    jsonFile = args.jsonfile
    excelFile = args.excelfile
    print('Input file argument : ', jsonFile)
    print('Output file argument: ', excelFile)

    copyJsonFile2Excel(jsonFile, excelFile)

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
