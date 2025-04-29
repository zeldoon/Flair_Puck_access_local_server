# NOTE
# Use python encode_csv.py [input file name] where the
# input file name is the csv file you want to get encoded
# and this will create an output file named encoded.txt
# in the same directory

import encode
import sys
import serial
import argparse

def encode_raw(input_string):
    raw_code = input_string.split(bytes('w:', 'utf-8'))[1]
    encoded_code = encode.encode_to_data_without_timing_info_from_recording(raw_code)
    return encoded_code

# MAIN PROGRAM
if __name__ == '__main__':
    print('===================================')
    print('REAL TIME ENCODER')
    print('                 ')
    print('      _---_      ')
    print('       _-_       ')
    print('                 ')
    print('       ___       ')
    print('      |oo||      ')
    print('      |oo||      ')
    print('      |  ||      ')
    print('      |__||      ')
    print('                 ')
    print('===================================')
    
    parser = argparse.ArgumentParser(description='Encode raw IR data into Flair BEEF codes')
    parser.add_argument('serial_port', type=str, help='Arduino serial port = <serial_port>')
    args = parser.parse_args()
    read_serial_port = args.serial_port
    print('Connecting to port: %s...' % (read_serial_port))

    ser = serial.Serial(
        port=read_serial_port,\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=20)

    print('Connected to: %s.' % (read_serial_port))
    print('Scanning...')

    while True:
        line = ser.readline()
        if bytes('Raw', 'utf-8') in line:
            print(str(line[0:30])+' ...')
            try:
                encoded = encode_raw(line)
                print(encoded[0])
                print(' ')
            except:
                print('Empty or error')





