# NOTE
# Use python code_adjuster.py [input file name] where the
# input file name is the txt file you want to adjust the
# IR codes and this will create an output file named
# [filename]-adjusted.txt in the same directory

#decoded using https://stackoverflow.com/questions/48531654/fujitsu-ir-remote-checksum-calculation

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
        if idx > 2:
            old_beef = str(code['Data'])
            
            print "-----------------------------------"
            print old_beef
            checksum = old_beef[177:185]
            calc_checksum = int(old_beef[169:177][::-1],2) + \
            int(old_beef[161:169][::-1],2) + \
            int(old_beef[153:161][::-1],2) + \
            int(old_beef[145:153][::-1],2) + \
            int(old_beef[137:145][::-1],2) + \
            int(old_beef[129:137][::-1],2) + \
            int(old_beef[121:129][::-1],2)
            calc_checksum = (208 - calc_checksum) % 256
            res = format(calc_checksum, '08b')
            res_rev = res[::-1]
            if res_rev == checksum:
            	print 'MATCH'
            else:
            	print 'ERROR!!!!!!!!!!'

            mid_beef = old_beef[:121] + '1' + old_beef[122:]
            print mid_beef
            new_checksum = int(mid_beef[169:177][::-1],2) + \
            int(mid_beef[161:169][::-1],2) + \
            int(mid_beef[153:161][::-1],2) + \
            int(mid_beef[145:153][::-1],2) + \
            int(mid_beef[137:145][::-1],2) + \
            int(mid_beef[129:137][::-1],2) + \
            int(mid_beef[121:129][::-1],2)
            new_checksum = (208 - new_checksum) % 256
            res = format(new_checksum, '08b')
            res_rev = res[::-1]

            new_beef = mid_beef[:177] + res_rev + '3'
            print new_beef
            
            code['Data'] = new_beef
        else:
            old_beef = str(code['Data'])

            print "-----------------------------------"
            print old_beef

    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)


# MAIN PROGRAM

print "==================================="
print "THE ADJUSTER"
print "==================================="
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



