"""
Usage:
  EmotivClient-timeit.py demo
  EmotivClient-timeit.py save_to_sqldb
  EmotivClient-timeit.py save_to_csv
  EmotivClient-timeit.py save_to_jsonfile
  EmotivClient-timeit.py save [--nrexperiments=<nr>] (tocsv | tosqldb | tojsonfile) [compress (gzip | 7zip)]

Options:
  --nrexperiments=<nr>

"""

import EmotivClient
import timeit
import os
from docopt import docopt
import matplotlib.pyplot as plt

read_packets_statement = """
from EmotivClient import *
#packets = read_packets_from_emotiv(1)
packets = create_randomized_packets(1)
"""

def save_to_sqldb_timeit(nrexp):
    setup_statement = read_packets_statement
    primary_statement = """
EegData.dropTable(ifExists=True)
EegData.createTable(ifNotExists=True)
save_packets_to_sqldb(packets)
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))
    return min(results)


def save_to_csv_timeit(nrexp):
    setup_statement = read_packets_statement + """
recording = prepare_recording_for_csv(packets)
    """
    primary_statement = """
write_recording_to_csv(recording, "recording.csv")
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))
    return min(results)


def compress_with_bzip_timeit(nrexp, file_in, file_out):
    setup_statement = "from EmotivClient import *"
    primary_statement = \
"bZipFile(\"" + file_in + "\",\"" + file_out + "\")"
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    return min(results)


def compress_with_gzip_timeit(nrexp, file_in, file_out):
    setup_statement = "from EmotivClient import *"
    primary_statement = \
"gZipFile(\"" + file_in + "\",\"" + file_out + "\")"
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    return min(results)


def compress_with_7zip_timeit(nrexp, file_in, file_out):
    setup_statement = "from EmotivClient import *"
    primary_statement = \
"sevenZipFile(\"" + file_in + "\",\"" + file_out + "\")"
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    return min(results)


def save_to_jsonfile_timeit(nrexp):
    setup_statement = read_packets_statement
    primary_statement = """
save_packets_to_jsonfile(packets)
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))
    return min(results)


def main(arguments):
    nrexp = 100
    if arguments['--nrexperiments']:
        nrexp = int(arguments['--nrexperiments'])
    print "Experiments number " + str(nrexp)

    '''CSV and compressed CSV'''

    t_save_csv = save_to_csv_timeit(nrexp)
    print "time to save to csv file " + str(t_save_csv)
    size_csv_file = os.path.getsize("recording.csv")
    print "size csv file " + str(size_csv_file)

    t_compress_csv_bzip = compress_with_bzip_timeit(nrexp, "recording.csv", "recording.csv.bz2")
    print "time to compress csv file with bzip " + str(t_compress_csv_bzip)
    size_csv_bzip_file = os.path.getsize("recording.csv.bz2")
    print "size csv file compressed with bzip " + str(size_csv_bzip_file)

    t_compress_csv_gzip = compress_with_gzip_timeit(nrexp, "recording.csv", "recording.csv.gz")
    print "time to compress csv file with gzip " + str(t_compress_csv_gzip)
    size_csv_gzip_file = os.path.getsize("recording.csv.gz")
    print "size csv file compressed with gzip " + str(size_csv_gzip_file)

    t_compress_csv_7zip = compress_with_7zip_timeit(nrexp, "recording.csv", "recording.csv.7z")
    print "time to compress csv file with 7zip " + str(t_compress_csv_7zip)
    size_csv_7zip_file = os.path.getsize("recording.csv.7z")
    print "size csv file compressed with 7zip " + str(size_csv_7zip_file)

    '''JSON and compressed JSON'''

    t_save_json = save_to_jsonfile_timeit(nrexp)
    print "time to save to json file " + str(t_save_json)
    size_json_file = os.path.getsize("recording.txt")
    print "size json file " + str(size_json_file)

    t_compress_json_bzip = compress_with_bzip_timeit(nrexp, "recording.txt", "recording.txt.bz2")
    print "time to compress json file with bzip " + str(t_compress_json_bzip)
    size_json_bzip_file = os.path.getsize("recording.txt.bz2")
    print "size json file compressed with bzip " + str(size_json_bzip_file)

    t_compress_json_gzip = compress_with_gzip_timeit(nrexp, "recording.txt", "recording.txt.gz")
    print "time to compress json file with gzip " + str(t_compress_json_gzip)
    size_json_gzip_file = os.path.getsize("recording.txt.gz")
    print "size json file compressed with gzip " + str(size_json_gzip_file)

    t_compress_json_7zip = compress_with_7zip_timeit(nrexp, "recording.txt", "recording.txt.7z")
    print "time to compress json file with 7zip " + str(t_compress_json_7zip)
    size_json_7zip_file = os.path.getsize("recording.txt.7z")
    print "size json file compressed with 7zip " + str(size_json_7zip_file)


    '''SQLite and compressed SQLite'''

    t_save_sqlite = save_to_sqldb_timeit(nrexp)
    print "time to save to sqlite file " + str(t_save_sqlite)
    size_sqlite_file = os.path.getsize("recording.db")
    print "size sqlite file " + str(size_sqlite_file)

    t_compress_sqlite_bzip = compress_with_bzip_timeit(nrexp, "recording.db", "recording.db.bz2")
    print "time to compress sqlite file with bzip " + str(t_compress_sqlite_bzip)
    size_sqlite_bzip_file = os.path.getsize("recording.db.bz2")
    print "size sqlite compressed with bzip " + str(size_sqlite_bzip_file)

    t_compress_sqlite_gzip = compress_with_gzip_timeit(nrexp, "recording.db", "recording.db.gz")
    print "time to compress sqlite file with gzip " + str(t_compress_sqlite_gzip)
    size_sqlite_gzip_file = os.path.getsize("recording.db.gz")
    print "size sqlite compressed with gzip " + str(size_sqlite_gzip_file)

    t_compress_sqlite_7zip = compress_with_7zip_timeit(nrexp, "recording.db", "recording.db.7z")
    print "time to compress sqlite file with 7zip " + str(t_compress_sqlite_7zip)
    size_sqlite_7zip_file = os.path.getsize("recording.db.7z")
    print "size sqlite compressed with 7zip " + str(size_sqlite_7zip_file)

    ''' Plot 1: Memory-time plot for raw files '''

    x = [t_save_csv, t_save_json, t_save_sqlite]
    y = [size_csv_file, size_json_file, size_sqlite_file]
    plt.scatter(x, y)
    plt.show()

    ''' Plot 2: Memory-time plot for archived files '''

    t1 = t_save_csv + t_compress_csv_bzip
    t2 = t_save_csv + t_compress_csv_7zip
    t3 = t_save_csv + t_compress_csv_gzip
    t4 = t_save_json + t_compress_json_bzip
    t5 = t_save_json + t_compress_json_7zip
    t6 = t_save_json + t_compress_json_gzip
    t7 = t_save_sqlite + t_compress_sqlite_bzip
    t8 = t_save_sqlite + t_compress_sqlite_7zip
    t9 = t_save_sqlite + t_compress_sqlite_gzip
    s1 = size_csv_bzip_file
    s2 = size_csv_7zip_file
    s3 = size_csv_gzip_file
    s4 = size_json_bzip_file
    s5 = size_json_7zip_file
    s6 = size_json_gzip_file
    s7 = size_sqlite_bzip_file
    s8 = size_sqlite_7zip_file
    s9 = size_sqlite_gzip_file
    x = [t1, t2, t3, t4, t5, t6, t7, t8, t9]
    y = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
    plt.scatter(x, y, c=y, s=200)
    plt.gray()
    plt.show()

    if arguments['save_to_csv']:
        save_to_csv_timeit(nrexp)
    elif arguments['save_to_sqldb']:
        save_to_sqldb_timeit(nrexp)
    elif arguments['save_to_jsonfile']:
        save_to_jsonfile_timeit(nrexp)
    elif arguments['save']:
        print "Save"
        if arguments['tocsv']:
            print "tocsv"
        elif arguments['tosqldb']:
            print "tosqldb"

        if (arguments['compress']):
            print "compress"
            if (arguments['7zip']):
                print "7zip"
    else:
        print "Invalid argument."


if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(arguments)