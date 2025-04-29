import serial
import redis
import json
from datetime import datetime
from encoder import encode
import uuid
import time

for port_number in range(0, 20000):
    try:
	    serialport = serial.Serial("/dev/cu.usbmodem" + str(port_number), 115200)
    except:
        pass

rc = redis.StrictRedis(host='localhost', port=6379, db=0)

ir_redis_codes = "ir:codes"

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

while True:
    command = serialport.readline()
    if 'Raw' in command and len(command) > 100:
        try:

            #add in trailing space
            raw_command = command.strip()
            print raw_command
            if raw_command[-1] == ',' or int(raw_command.split(',')[-1]) > 0:
                raw_command += "-50000"
            else:
                raw_command = raw_command[0:-1]

            encoded_commands = encode.encode_to_uird_from_raw_string(raw_command)
            encoded_commands["raw_command"] = raw_command
            command_data = encode.encode_to_data_without_timing_info_from_raw_string(raw_command)
            print encoded_commands
            command_uuid = str(uuid.uuid4())
            rc.hset(ir_redis_codes, command_uuid, json.dumps({
                'uuid': command_uuid,
                'raw_command': encoded_commands["raw_command"],
                'recorded_at': int(time.time()),
                'transcoded_command': encoded_commands["transcoded_command"],
                'command_data': command_data,
                'meta_data': { 'uuid': command_uuid }
            },
             cls=DateTimeEncoder))
        except Exception as e:
            e.printStackTrace()
