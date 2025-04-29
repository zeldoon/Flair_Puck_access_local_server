# NOTE
# Use python code_adjuster.py [input file name] where the
# input file name is the txt file you want to adjust the
# IR codes and this will create an output file named
# [filename]-adjusted.txt in the same directory

import sys
import json
from collections import Counter
from pprint import pprint
from struct import *

def adjust_codes(file_to_adjust):
    original_file = open(file_to_adjust, "r")
    print "File to adjust: ", original_file.name
    json_data = open(file_to_adjust).read()

    data = json.loads(json_data)
    
    codes = data['Codes']
    for idx, code in enumerate(codes):
        if idx > 0:
            old_beef = str(code['Data'])
            mid_beef = old_beef[:69] + '0' + old_beef[70:]
            old_beef = mid_beef

            print "-----------------------------------"
            print mid_beef

            code_data = old_beef[57:81]
            print code_data
            checksum = int(code_data[0:4], 2) + int(code_data[4:8], 2) + int(code_data[8:12], 2) + int(code_data[12:16], 2) + int(code_data[16:20], 2) + int(code_data[20:24], 2)
            calculated_checksum = format(checksum, 'b')
            length = len(calculated_checksum)
            result_checksum = calculated_checksum[length - 4: length]

            new_beef = old_beef[:81] + result_checksum + old_beef[85:]
            
            print old_beef
            print new_beef
            
            code['Data'] = new_beef

    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)


# MAIN PROGRAM

print "==================================="
print "THE ADJUSTER"
print "==================================="
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



