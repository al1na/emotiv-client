"""
Usage:
  EmotivClient-timeit.py save_to_sqldb
  EmotivClient-timeit.py save_to_csv
  EmotivClient-timeit.py save_to_jsonfile
  EmotivClient-timeit.py save [--nrexperiments=<nr>] (tocsv | tosqldb | tojsonfile) [compress (gzip | 7zip)]

Options:
  --nrexperiments=<nr>

"""

import EmotivClient
import timeit
from docopt import docopt

read_packets_statement = """
from EmotivClient import *
packets = read_packets_from_emotiv(1)
"""

def save_to_sqldb_timeit(nrexp):
    setup_statement = read_packets_statement
    primary_statement = """
EegData.createTable(ifNotExists=True)
save_packets_to_sqldb(packets)
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))

def save_to_csv_timeit(nrexp):
    setup_statement = read_packets_statement + """
recording = prepare_recording_for_csv(packets)
    """
    primary_statement = """
write_recording_to_csv(recording, "w.csv")
bZipFile("w.csv", "arw.csv.bz2")
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))


def save_to_jsonfile_timeit(nrexp):
    setup_statement = read_packets_statement
    primary_statement = """
save_packets_to_jsonfile(packets)
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(nrexp, 1)
    print results
    print "min time " + str(min(results))


def main(arguments):
    nrexp = 100
    if arguments['--nrexperiments']:
        nrexp = int(arguments['--nrexperiments'])
    print "Experiments number " + str(nrexp)

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

"""
TODO if it is important for the compression measurements to
use data actually read from Emotiv instead of random data,
then it is also important to wear the cap while doing
the Emotiv recording.
"""

if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(arguments)

