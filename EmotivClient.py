"""
Simple client for Emotiv devices

Usage:
  EmotivClient.py (read_from_emotiv | generate_random) [--seconds=<nr>]

Options:
  --seconds=<nr>

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
from itertools import chain, izip_longest
from docopt import docopt
import pprint

SAMPLING_RATE = 128 # Emotiv's sampling rate
nr_emotiv_channels = 17
nr_gyros_emotiv = 2

#conn = builder()('emotivrecordings' + str(datetime.datetime.now().isoformat()) + '.db', debug=False)
conn = builder()('recording.db', debug=False)


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
    """Write an numpy array (or a list of lists) to a comma-separated values file.
    Source code: emokitten"""
    if electrodes is not None:
        df = pd.DataFrame(recording, columns=electrodes)
    else:
        df = pd.DataFrame(recording)
    # TODO append to csv instead of always writing a new one
    df.to_csv(filename)


def prepare_recording_for_csv(packets_list):
    recording = nmpy.zeros((len(packets_list), 1 + nr_emotiv_channels * 2))
    for packet in packets_list:
        values = map(lambda d: d['value'], packet.sensors.values())
        readings_quality = map(lambda d: d['quality'], packet.sensors.values())
        if len(values) == len(readings_quality):
            values_and_qualities = [i for i in chain(*izip_longest(values, readings_quality)) if i is not None]
            recording[packets_list.index(packet), :] = [i for i in chain([packet.time], values_and_qualities)]
        else:
            print "Something went wrong - mismatch between readings' values and quality of readings."
    return recording


class TimedEmotivPacket():
    """
    Emotiv packet wrapped together with the time when it was read from the headset.
    """
    def __init__(self, emotiv_packet, time_of_reading):
        self.counter = emotiv_packet.counter
        self.rawData = emotiv_packet.rawData
        self.battery = emotiv_packet.battery
        self.sensors = emotiv_packet.sensors
        self.sync = emotiv_packet.sync
        self.gyroX = emotiv_packet.gyroX
        self.gyroY = emotiv_packet.gyroY
        self.time = time_of_reading


class EmotivPacketMock(emotiv.EmotivPacket):
    def __init__(self):
        self.counter = random.randint(0, 128)
        self.battery = random.randint(0, 100)
        self.gyroX = random.randint(0, 100)
        self.gyroY = random.randint(0, 100)
        self.sensors = {
            'F3': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'FC6': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'P7': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'T8': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'F7': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'F8': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'T7': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'P8': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'AF4': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'F4': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'AF3': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'O2': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'O1': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'FC5': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'X': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'Y': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)},
            'Unknown': {'value': random.randint(-8900, 8900), 'quality': random.randint(0, 100)}
        }


def create_randomized_packets(seconds):
    packets = []
    for i in range(seconds * SAMPLING_RATE):
        packets.append(create_randomized_packet())
    return packets


def create_randomized_packet():
    return EmotivPacketMock()


class EegData(SQLObject):
    _connection = conn
    time_stamp = DateTimeCol()
    gyroX = StringCol(length=5)
    gyroY = StringCol(length=5)
    sensorY_value = StringCol()
    sensorY_quality = StringCol()
    sensorF3_value = StringCol()
    sensorF3_quality = StringCol()
    sensorF4_value = StringCol()
    sensorF4_quality = StringCol()
    sensorP7_value = StringCol()
    sensorP7_quality = StringCol()
    sensorFC6_value = StringCol()
    sensorFC6_quality = StringCol()
    sensorF7_value = StringCol()
    sensorF7_quality = StringCol()
    sensorF8_value = StringCol()
    sensorF8_quality = StringCol()
    sensorT7_value = StringCol()
    sensorT7_quality = StringCol()
    sensorP8_value = StringCol()
    sensorP8_quality = StringCol()
    sensorFC5_value = StringCol()
    sensorFC5_quality = StringCol()
    sensorAF4_value = StringCol()
    sensorAF4_quality = StringCol()
    sensorUnknown_value = StringCol()
    sensorUnknown_quality = StringCol()
    sensorT8_value = StringCol()
    sensorT8_quality = StringCol()
    sensorX_value = StringCol()
    sensorX_quality = StringCol()
    sensorO2_value = StringCol()
    sensorO2_quality = StringCol()
    sensorO1_value = StringCol()
    sensorO1_quality = StringCol()
    sensorAF3_value = StringCol()
    sensorAF3_quality = StringCol()


def save_packet_to_sqldb(packet):
    EegData(time_stamp=datetime.datetime.fromtimestamp(packet.time),
            gyroX = str(packet.gyroX), gyroY = str(packet.gyroY),
            sensorY_value = str(packet.sensors['Y']['value']),
            sensorY_quality = str(packet.sensors['Y']['quality']),
            sensorF3_value = str(packet.sensors['F3']['value']),
            sensorF3_quality = str(packet.sensors['F3']['quality']),
            sensorF4_value = str(packet.sensors['F4']['value']),
            sensorF4_quality = str(packet.sensors['F4']['quality']),
            sensorP7_value = str(packet.sensors['P7']['value']),
            sensorP7_quality = str(packet.sensors['P7']['quality']),
            sensorFC6_value = str(packet.sensors['FC6']['value']),
            sensorFC6_quality = str(packet.sensors['FC6']['quality']),
            sensorF7_value = str(packet.sensors['F7']['value']),
            sensorF7_quality = str(packet.sensors['F7']['quality']),
            sensorF8_value = str(packet.sensors['F8']['value']),
            sensorF8_quality = str(packet.sensors['F8']['quality']),
            sensorT7_value = str(packet.sensors['T7']['value']),
            sensorT7_quality = str(packet.sensors['T7']['quality']),
            sensorP8_value = str(packet.sensors['P8']['value']),
            sensorP8_quality = str(packet.sensors['P8']['quality']),
            sensorFC5_value = str(packet.sensors['FC5']['value']),
            sensorFC5_quality = str(packet.sensors['FC5']['quality']),
            sensorAF4_value = str(packet.sensors['AF4']['value']),
            sensorAF4_quality = str(packet.sensors['AF4']['quality']),
            sensorT8_value = str(packet.sensors['T8']['value']),
            sensorT8_quality = str(packet.sensors['T8']['quality']),
            sensorX_value = str(packet.sensors['X']['value']),
            sensorX_quality = str(packet.sensors['X']['quality']),
            sensorO2_value = str(packet.sensors['O2']['value']),
            sensorO2_quality = str(packet.sensors['O2']['quality']),
            sensorO1_value = str(packet.sensors['O1']['value']),
            sensorO1_quality = str(packet.sensors['O1']['quality']),
            sensorAF3_value = str(packet.sensors['AF3']['value']),
            sensorAF3_quality = str(packet.sensors['AF3']['quality']),
            sensorUnknown_value = str(packet.sensors['Unknown']['value']),
            sensorUnknown_quality = str(packet.sensors['Unknown']['quality']))


def save_packets_to_sqldb(packets):
    for packet in packets:
        save_packet_to_sqldb(packet)


def convert_emotiv_packets_to_json(packets):
    jsonpackets = []
    for packet in packets:
        jsonpack = {
                    #'counter': packet.counter,
                    #'battery': packet.battery,
                    'gyroX': packet.gyroX,
                    'gyroY': packet.gyroY,
                    'sensors': packet.sensors}
        jsonpackets.append(jsonpack)
    return jsonpackets


def save_packets_to_jsonfile(packets, filename="recording" + str(datetime.datetime.now().isoformat()) + ".txt"):
    jsonpackets = convert_emotiv_packets_to_json(packets)
    with open(filename, 'w') as file_out:
        json.dump(jsonpackets, file_out)


def read_packets_from_emotiv(nr_seconds_to_record):
    headset = emotiv.Emotiv()
    gevent.spawn(headset.setup)
    gevent.sleep(1.5)

    packets = []

    try:
        nr_seconds_left_to_record = nr_seconds_to_record

        nr_packets_read = 0
        while nr_seconds_left_to_record > 0:
            for sample in range(SAMPLING_RATE):
                packet = headset.dequeue()
                timed_packet = TimedEmotivPacket(packet, time.time())
                packets.append(timed_packet)
                nr_packets_read = nr_packets_read + 1
                print "packets read " + str(nr_packets_read)
                print "current time " + str(datetime.datetime.now().isoformat())
                print "packet counter " + str(timed_packet.counter)
                print "packet battery " + str(timed_packet.battery)
                print "sensors" + str(timed_packet.sensors)
                gevent.sleep(0)
            nr_seconds_left_to_record -= 1
    finally:
        headset.close()
    return packets


def main(arguments):
    packets = []
    seconds_to_record = 1
    if arguments['--seconds']:
        seconds_to_record = int(arguments['--seconds'])
    if arguments['read_from_emotiv']:
        packets = read_packets_from_emotiv(seconds_to_record)
    elif arguments['generate_random']:
        packets = create_randomized_packets(seconds_to_record)

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

if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(arguments)
