"""
Simple client for Emotiv devices
"""
from emokit import emotiv
import datetime
import gevent
import json
import pprint
import pandas as pd
import numpy as nmpy
import time
import timeit
from os import urandom
import random
from sqlobject import *
from sqlobject.sqlite import builder
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

conn = builder()('emotivrecordings-random.db', debug=False)

SAMPLING_RATE = 128 # Emotiv's sampling rate
epoc_channels = 17

def write_recording_to_csv(recording, filename="recording" + str(datetime.datetime.now().isoformat()) + ".csv",
                           electrodes=None):
    """Write an numpy array (or a list of lists) to a comma-separated values file."""
    if electrodes is not None:
        df = pd.DataFrame(recording, columns=electrodes)
    else:
        df = pd.DataFrame(recording)
    # TODO append to csv instead of always writing a new one
    df.to_csv(filename)


def prepare_recording_for_csv(packets_list):
    recording = nmpy.zeros((len(packets_list), epoc_channels))
    for packet in packets:
        values = map(lambda d: d['value'], packet.sensors.values())
        recording[packets.index(packet), :] = values
    return recording


class EmotivPacketMock(object):
    def __init__(self):
        self.counter = random.randint(0, 100)
        self.battery = random.randint(0, 100)
        self.gyro_x = random.randint(0, 100)
        self.gyro_y = random.randint(0, 100)
        self.sensors = {
            'F3': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'FC6': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'P7': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'T8': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'F7': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'F8': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'T7': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'P8': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'AF4': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'F4': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'AF3': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'O2': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'O1': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'FC5': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'X': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'Y': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)},
            'Unknown': {'value': random.randint(-10000, 10000), 'quality': random.randint(0, 100)}
        }


"""
def create_randomized_packet():
    headset = emotiv.Emotiv()
    randombytes = bytearray()
    randombytes.extend(chr(48))
    randombytes.extend(urandom(33))
    randombytes[29] = chr(48)
    randombytes[30] = chr(48)
    print " " + str(randombytes[0])
    return emotiv.EmotivPacket(randombytes, headset.sensors, headset.old_model)
"""

def create_randomized_packet():
    return EmotivPacketMock()


class EegData(SQLObject):
    _connection = conn
    gyroX = StringCol(length=5)
    gyroY = StringCol(length=5)
    """Another option is to have a Sensors table (FK, SensorName, Value, Quality)"""
    sensorY = StringCol()
    sensorF3 = StringCol()
    sensorF4 = StringCol()
    sensorP7 = StringCol()
    sensorFC6 = StringCol()
    sensorF7 = StringCol()
    sensorF8 = StringCol()
    sensorT7 = StringCol()
    sensorP8 = StringCol()
    sensorFC5 = StringCol()
    sensorAF4 = StringCol()
    sensorUnknown = StringCol()
    sensorT8 = StringCol()
    sensorX = StringCol()
    sensorO2 = StringCol()
    sensorO1 = StringCol()
    sensorAF3 = StringCol()


def save_packet_to_sqldb(packet):
    EegData(gyroX = str(packet.gyro_x), gyroY = str(packet.gyro_y), sensorY = str(packet.sensors['Y']['value']),
            sensorF3 = str(packet.sensors['F3']['value']),
            sensorF4 = str(packet.sensors['F4']['value']),
            sensorP7 = str(packet.sensors['P7']['value']),
            sensorFC6 = str(packet.sensors['FC6']['value']),
            sensorF7 = str(packet.sensors['F7']['value']),
            sensorF8 = str(packet.sensors['F8']['value']),
            sensorT7 = str(packet.sensors['T7']['value']),
            sensorP8 = str(packet.sensors['P8']['value']),
            sensorFC5 = str(packet.sensors['FC5']['value']),
            sensorAF4 = str(packet.sensors['AF4']['value']),
            sensorUnknown = str(packet.sensors['Unknown']['value']),
            sensorT8 = str(packet.sensors['T8']['value']),
            sensorX = str(packet.sensors['X']['value']),
            sensorO2 = str(packet.sensors['O2']['value']),
            sensorO1 = str(packet.sensors['O1']['value']),
            sensorAF3 = str(packet.sensors['AF3']['value']))


def save_packet_to_mongodb(packet):
    jsonpacket = {
                'datetime': str(datetime.datetime.now().isoformat()),
                'emotivpacket': {
                        'counter': packet.counter,
                        'battery': packet.battery,
                        'gyroX': packet.gyro_x,
                        'gyroY': packet.gyro_y,
                        'sensors': packet.sensors}}
    db = client.emotiv_recordings
    db.emotiv_packets.insert(jsonpacket)


def save_packets_to_sqldb(packets):
    for packet in packets:
        save_packet_to_sqldb(packet)


def save_packets_to_mongodb(packets):
    #TODO bulk save
    for packet in packets:
        save_packet_to_mongodb(packet)

        
def read_packets_from_emotiv(nr_of_seconds_to_record):
    #headset = emotiv.Emotiv()
    #gevent.spawn(headset.setup)
    #gevent.sleep(1.5)

    packets = []

    try:
        nr_seconds_to_record = 1
        nr_seconds_left_to_record = nr_seconds_to_record
        samples = nr_seconds_left_to_record * SAMPLING_RATE

        recording = nmpy.zeros((samples, epoc_channels))
        nr_packets_read = 0
        while nr_seconds_left_to_record > 0:
            for sample in range(SAMPLING_RATE):
                #packet = headset.dequeue()
                packet = create_randomized_packet()
                packets.append(packet)
                nr_packets_read = nr_packets_read + 1
                print "packets read " + str(nr_packets_read)
                print "sample " + str(sample) + " " + " seconds left " + \
                      str(nr_seconds_left_to_record) + \
                      " " + str((nr_seconds_to_record - nr_seconds_left_to_record) * SAMPLING_RATE
                                + sample)
                print "date " + str(datetime.datetime.now().isoformat())
                print "packet counter " + str(packet.counter)
                print "packet battery " + str(packet.battery)
                print "sensors" + str(packet.sensors)
                gevent.sleep(0)
            nr_seconds_left_to_record = nr_seconds_left_to_record - 1
    finally:
        #headset.close()
        pass
    return packets

if __name__ == "__main__":
    try:
        #headset = emotiv.Emotiv()
        #gevent.spawn(headset.setup)
        #gevent.sleep(1.5)

        try:
            nr_seconds_to_record = 1
            nr_seconds_left_to_record = nr_seconds_to_record
            samples = nr_seconds_left_to_record * SAMPLING_RATE

            recording = nmpy.zeros((samples, epoc_channels))
            nr_packets_read = 0
            packets = []
            while nr_seconds_left_to_record > 0:
                for sample in range(SAMPLING_RATE):
                    #packet = headset.dequeue()
                    packet = create_randomized_packet()
                    packets.append(packet)
                    nr_packets_read = nr_packets_read + 1
                    print "packets read " + str(nr_packets_read)
                    print "sample " + str(sample) + " " + " seconds left " + \
                          str(nr_seconds_left_to_record) + \
                          " " + str((nr_seconds_to_record - nr_seconds_left_to_record) * SAMPLING_RATE
                                    + sample)
                    print "date " + str(datetime.datetime.now().isoformat())
                    print "packet counter " + str(packet.counter)
                    print "packet battery " + str(packet.battery)
                    print "sensors" + str(packet.sensors)

                    gevent.sleep(0)
                nr_seconds_left_to_record = nr_seconds_left_to_record - 1

            #recording = prepare_recording_for_csv(packets)
            #start_writing = time.time()
            #write_recording_to_csv(recording)
            #print "It took " + str(time.time() - start_writing) + " seconds to save the file"

            #EegData.createTable(ifNotExists=True)
            #start_writing_to_sqldb = time.time()
            #save_packets_to_sqldb(packets)
            #print "It took " + str(time.time() - start_writing_to_sqldb) + " seconds to save to the SQL database"

            start_writing_to_mongodb = time.time()
            save_packets_to_mongodb(packets)
            print "It took " + str(time.time() - start_writing_to_mongodb) + " seconds to save to MongoDB"

        finally:
            #headset.close()
            pass
    except KeyboardInterrupt:
        pass
else:
    print "Not run as main"