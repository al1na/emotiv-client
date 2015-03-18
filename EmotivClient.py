"""
Simple client for Emotiv devices
"""
from emokit import emotiv
import pandas as pd
import numpy as nmpy
import random
from sqlobject import *
from sqlobject.sqlite import builder
from subprocess import check_call
import gzip
import pylzma
import bz2
import gevent
import datetime
import time
import json
import pprint

SAMPLING_RATE = 128 # Emotiv's sampling rate
epoc_channels = 17

conn = builder()('emotivrecordings.db', debug=False)


def sevenZipFile(source_file, compressed_file):
    # Source: http://www.linuxplanet.org/blogs/?cat=3845
    f_in = open(source_file, 'rb')
    f_out = open(compressed_file, 'wb')
    f_in.seek(0)
    s = pylzma.compressfile(f_in)
    while True:
        tmp = s.read(1)
        if not tmp: break
        f_out.write(tmp)
    f_out.close()
    f_in.close()


def gZipFile(source_file, compressed_file):
    f_in = open(source_file, 'rb')
    f_out = gzip.open(compressed_file, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def gZipFile2(source_file):
    '''
    :param source_file: full path to the file to be compressed
    :returns: 0 if all is OK, otherwise error
    '''
    check_call(['gzip', '-k', source_file])


def bZipFile(source_file, compressed_file):
    f_in = open(source_file, 'rb')
    f_out = bz2.BZ2File(compressed_file, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def bZipFile2(source_file):
    '''
    :param source_file: full path to the file to be compressed
    :returns 0 if all is OK, otherwise error
    '''
    check_call(['bzip2', '-k', source_file])


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
    for packet in packets_list:
        values = map(lambda d: d['value'], packet.sensors.values())
        recording[packets_list.index(packet), :] = values
        recording[packets_list.index(packet), :] = values
    return recording


class EmotivPacketMock(emotiv.EmotivPacket):
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


def create_randomized_packet():
    return EmotivPacketMock()


class EegData(SQLObject):
    _connection = conn
    gyroX = StringCol(length=5)
    gyroY = StringCol(length=5)
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
    EegData(gyroX = str(packet.gyro_x), gyroY = str(packet.gyro_y),
            sensorY = str(packet.sensors['Y']['value']),
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
            sensorT8 = str(packet.sensors['T8']['value']),
            sensorX = str(packet.sensors['X']['value']),
            sensorO2 = str(packet.sensors['O2']['value']),
            sensorO1 = str(packet.sensors['O1']['value']),
            sensorAF3 = str(packet.sensors['AF3']['value']),
            sensorUnknown = str(packet.sensors['Unknown']['value']))


def save_packets_to_sqldb(packets):
    for packet in packets:
        save_packet_to_sqldb(packet)


def convert_emotiv_packets_to_json(packets):
    jsonpackets = []
    for packet in packets:
        jsonpack = {
                    #'counter': packet.counter,
                    #'battery': packet.battery,
                    #'gyroX': packet.gyro_x,
                    #'gyroY': packet.gyro_y,
                    'sensors': packet.sensors}
        jsonpackets.append(jsonpack)
    return jsonpackets


def save_packets_to_jsonfile(packets):
    jsonpackets = convert_emotiv_packets_to_json(packets)
    with open('jsonfile.txt', 'w') as file_out:
        json.dump(jsonpackets, file_out)


def read_packets_from_emotiv(nr_seconds_to_record):
    #headset = emotiv.Emotiv()
    #gevent.spawn(headset.setup)
    #gevent.sleep(1.5)

    packets = []

    try:
        nr_seconds_left_to_record = nr_seconds_to_record

        nr_packets_read = 0
        while nr_seconds_left_to_record > 0:
            for sample in range(SAMPLING_RATE):
                # packet = headset.dequeue()
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

            recording = prepare_recording_for_csv(packets)
            start_writing = time.time()
            csvfile = "emotivrecordings.csv"
            write_recording_to_csv(recording, csvfile)
            print "It took " + str(time.time() - start_writing) + " seconds to save the file"
            gZipFile(csvfile, 'emotivrecordings.csv.gz')
            sevenZipFile(csvfile, 'emotivrecordings.csv.7z')
            bZipFile(csvfile, 'emotivrecordings.csv.bz2')

            EegData.createTable(ifNotExists=True)
            start_writing_to_sqldb = time.time()
            save_packets_to_sqldb(packets)
            print "It took " + str(time.time() - start_writing_to_sqldb) + " seconds to save to the sqlite database"
            gZipFile('emotivrecordings.db', 'emotivrecordings.db.gz')
            sevenZipFile('emotivrecordings.db', 'emotivrecordings.db.7z')
            bZipFile('emotivrecordings.db', 'emotivrecordings.db.bz2')

            start_writing_to_jsonfile = time.time()
            save_packets_to_jsonfile(packets)
            print "It took " + str(time.time() - start_writing_to_jsonfile) + " seconds to save to the json file"
            gZipFile('jsonfile.txt', 'jsonfile.txt.gz')
            sevenZipFile('jsonfile.txt', 'jsonfile.txt.7z')
            bZipFile('jsonfile.txt', 'jsonfile.txt.bz2')

        finally:
            #headset.close()
            pass
    except KeyboardInterrupt:
        pass
else:
    print "Not run as main"