# NOTE
# Use python encode_csv.py [input file name] where the
# input file name is the csv file you want to get encoded
# and this will create an output file named encoded.txt
# in the same directory

import encode
import sys

def encode_file(file_to_encode):
    encode_file = open(file_to_encode, "r")
    print "File to encode: ", encode_file.name
    
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    new_file_name = "encoded-"+my_list[1].rstrip()+".txt"
    print new_file_name
    output_file = open(new_file_name, "w")

    print "Formatting device metadata..."
    output_file.write("{\n")
    output_file.write("    \"Meta\": {\n")
    output_file.write("        \"Manufacturer\":\""+my_list[1].rstrip()+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Model number\":\""+my_list[1].rstrip()+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Unit Type\":\""+my_list[1].rstrip()+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Remote model\":\""+my_list[1].rstrip()+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Description\":\""+my_list[1].rstrip()+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Notes\":\""+my_list[1].rstrip()+"\"\n")
    output_file.write("    },\n")
    my_line = encode_file.readline()
    my_line = encode_file.readline()

    print "Encoding raw data..."
    output_file.write("    \"Codes\": {\n")
    i = 0
    for line in encode_file.readlines():
        if (i == 0):
            i += 1
        else:
            output_file.write(",\n")
        my_list = line.split(",")
        raw_code = line.split("w:")[1]
        encoded_code,length,warning_1,warning_2 = encode.encode_to_data_without_timing_info_from_recording(raw_code)
        output_file.write("        \""+my_list[0]+"\":\""+encoded_code+"\"")
        print my_list[0]
    output_file.write("\n    }\n")

    output_file.write("}\n")
    encode_file.close()
    output_file.close()




# MAIN PROGRAM

print "==================================="
print "THE ENCODER"
print "==================================="
my_encode_file = sys.argv[1]
encode_file(my_encode_file)



