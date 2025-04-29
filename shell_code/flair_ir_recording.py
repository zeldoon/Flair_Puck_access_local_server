# NOTE
# Use python encode_csv.py [input file name] where the
# input file name is the csv file you want to get encoded
# and this will create an output file named encoded.txt
# in the same directory

import encode
import sys
import serial
import argparse
import time


def encode_raw(input_string):
    raw_code = input_string.split(bytes('w:', 'utf-8'))[1]
    encoded_code = encode.encode_to_data_without_timing_info_from_recording(raw_code)
    return encoded_code


def init():
    print('===================================')
    print('FLAIR IR RECORDER')
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
        timeout=3)

    print('Connected to: %s.' % (read_serial_port))
    return ser


def homemade_buffer_flush(ser):
    ser.timeout = 0
    for i in range(10):
        buf = ser.readline()
    while True:
        buf = ser.readline()
        if not buf:
            break
    ser.timeout = 3


def test_for_power_on_requirement(ser):
    print('===================================')
    print('Please set your remote to Heat, 71, Fan Auto, Swing Off.')
    input('Press enter when ready\n')
    homemade_buffer_flush(ser)
    print('Please increment your remote from 71 to 72.\n')
    
    encoded_increment = None
    while True:
        line = ser.readline()
        if bytes('Raw', 'utf-8') in line:
            encoded_increment = encode_raw(line)[0]
            print('\nRECEIVED!\n\n')
            break

    header_len = 24
    num_symbols = int(encoded_increment[8:10])
    header_len += (8 * num_symbols)
    encoded_increment = encoded_increment[header_len::]

    print('===================================')
    print('Please press power to turn off the remote.')
    input('Press enter when complete\n')
    homemade_buffer_flush(ser)
    print('Please power on your remote. Your remote should power')
    print('on into Heat, 72, Fan Auto, Swing Off.\n')

    encoded_power_into = None
    while True:
        line = ser.readline()
        if bytes('Raw', 'utf-8') in line:
            encoded_power_into = encode_raw(line)[0]
            print('\nRECEIVED!\n\n')
            break

    header_len = 24
    num_symbols = int(encoded_power_into[8:10])
    header_len += (8 * num_symbols)
    encoded_power_into = encoded_power_into[header_len::]

    if encoded_increment == encoded_power_into:
        print('NORMAL!\n\n')
    else:
        print('POWER ON REQUIRED!\n\n')


# MAIN PROGRAM
if __name__ == '__main__':
    ser = init()
    test_for_power_on_requirement(ser)
    
    while True:
        line = ser.readline()
        print(line)









