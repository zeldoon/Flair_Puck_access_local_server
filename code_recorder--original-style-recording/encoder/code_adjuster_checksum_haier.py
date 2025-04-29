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
    print("File to adjust: ", original_file.name)
    json_data = open(file_to_adjust).read()

    data = json.loads(json_data)
    
    codes = data['Codes']
    for idx, code in enumerate(codes):
        if idx > 1:
            old_beef = str(code['Data'])
            code_data = old_beef[66:170]
            old_checksum = old_beef[170:178]
            check_checksum = int(code_data[0:8], 2) + int(code_data[8:16], 2) + int(code_data[16:24], 2) + int(code_data[24:32], 2) + \
                                int(code_data[32:40], 2) + int(code_data[40:48], 2) + int(code_data[48:56], 2) + int(code_data[56:64], 2) + \
                                int(code_data[64:72], 2) + int(code_data[72:80], 2) + int(code_data[80:88], 2) + int(code_data[88:96], 2) + \
                                int(code_data[96:104], 2)

            print("-----------------------------------")
            if check_checksum % 256 == int(old_checksum, 2):
                print('Old checksum match!')
            else:
                print('BIG ERROR BUDDY!  ALERT!')

            mid_beef = old_beef[0:167] + '101'
            new_code_data = mid_beef[66:170]
            new_checksum = int(new_code_data[0:8], 2) + int(new_code_data[8:16], 2) + int(new_code_data[16:24], 2) + int(new_code_data[24:32], 2) + \
                            int(new_code_data[32:40], 2) + int(new_code_data[40:48], 2) + int(new_code_data[48:56], 2) + int(new_code_data[56:64], 2) + \
                            int(new_code_data[64:72], 2) + int(new_code_data[72:80], 2) + int(new_code_data[80:88], 2) + int(new_code_data[88:96], 2) + \
                            int(new_code_data[96:104], 2)
            new_beef = mid_beef + format(new_checksum % 256, 'b').zfill(8) + '4'
            print(new_beef)            
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



