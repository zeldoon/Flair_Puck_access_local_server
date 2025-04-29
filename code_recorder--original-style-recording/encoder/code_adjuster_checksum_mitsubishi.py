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
            old_beef = str(code['Data'])
            print("-----------------------------------")
            print(old_beef)
            code_data = old_beef[65:209]
            print(code_data)
            code_data_adjusted = code_data[0:54] + '0' + code_data[55:115] + '0' + code_data[116:131] + '000' + code_data[134:136]
            print(code_data_adjusted)

            old_checksum = code_data[136:144][::-1]
            old_checksum_calc = 0
            for i in range(0, 17):
                old_checksum_calc += int(code_data[i*8:i*8+8][::-1],2)
            old_checksum_calc = old_checksum_calc % 256
            old_checksum_calc = format(old_checksum_calc, '08b')
            if old_checksum_calc == old_checksum:
                print('MATCH!')
            else:
                print('ERROR!')
            new_checksum_calc = 0
            for i in range(0, 17):
                new_checksum_calc += int(code_data_adjusted[i*8:i*8+8][::-1],2)
            new_checksum_calc = new_checksum_calc % 256
            new_checksum_calc = format(new_checksum_calc, '08b')
            new_beef = old_beef[0:65] + code_data_adjusted[0:136] + new_checksum_calc[::-1] + '3'
            print(new_beef)
            code['Data'] = new_beef

    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)

"""
            checksum = int(code_data[0:8][::-1], 2) + int(code_data[8:16][::-1], 2) + int(code_data[16:24][::-1], 2) + int(code_data[24:32][::-1], 2) + int(code_data[32:40][::-1], 2) + int(code_data[40:48][::-1], 2) + \
                       int(code_data[48:56][::-1], 2) + int(code_data[56:64][::-1], 2) + int(code_data[64:72][::-1], 2) + int(code_data[72:80][::-1], 2) + int(code_data[80:88][::-1], 2) + int(code_data[88:96][::-1], 2) + \
                       int(code_data[96:104][::-1], 2) + int(code_data[104:112][::-1], 2) + int(code_data[112:120][::-1], 2) + int(code_data[120:128][::-1], 2) + int(code_data[128:136][::-1], 2) + int(code_data[136:144][::-1], 2)
            calculated_checksum = format(checksum, 'b')
            length = len(calculated_checksum)
            result_checksum = calculated_checksum[length-8:length][::-1]

            new_beef = old_beef[:363] + result_checksum + old_beef[371:]
            
            print('Old: ' + old_beef)
            print('New: ' + str(new_beef))
            
            code['Data'] = new_beef
"""
    



# MAIN PROGRAM

print("===================================")
print("THE ADJUSTER")
print("===================================")
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



