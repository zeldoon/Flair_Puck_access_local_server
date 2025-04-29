from flask import render_template, request
import encoder
import serial
from time import sleep
from app import app
import json
import redis
import config
import time

ir_redis_codes = "ir:codes"
rc = redis.StrictRedis(host='localhost', port=6379, db=0)
if config.DELETE_ON_START:
    rc.delete(ir_redis_codes)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ir_codes')
def ir_codes():
    return json.dumps(sorted([json.loads(value) for key, value in rc.hgetall(ir_redis_codes).iteritems()], key=lambda x: x['recorded_at'], reverse=True))

@app.route('/ir_codes/hash')
def ir_codes_hash():
    return str(hash(str(sorted([json.loads(value) for key, value in rc.hgetall(ir_redis_codes).iteritems()], key=lambda x: x['recorded_at'], reverse=True))))

@app.route('/ir_codes/<uuid>', methods=['GET', 'PATCH','DELETE'])
def ir_code(uuid):
    if request.method == 'GET':
        return json.dumps(rc.hget(ir_redis_codes, uuid))
    if request.method == 'DELETE':
        rc.hdel(ir_redis_codes, uuid)
        return 'Deleted'
    if request.method == 'PATCH':
        #this is not atomic and should be but whatever
        command = json.loads(rc.hget(ir_redis_codes, uuid))
        print command['meta_data']
        command['meta_data'] = json.loads(request.get_data())
        command['meta_data']['uuid'] = uuid
        print command['meta_data']
        rc.hset(ir_redis_codes, uuid, json.dumps(command))
        return 'OK'
