import EmotivClient
import timeit

"""
TODO if it is important for the compression measurements to
use data actually read from Emotiv instead of random data,
then it is also important to wear the cap while doing
the Emotiv recording.
"""

def save_to_sqldb_timeit():
    pass

def save_to_csv_timeit():
    pass


if __name__ == "__main__":
    setup_statement = """
from EmotivClient import *
EegData.createTable(ifNotExists=True)
packets = read_packets_from_emotiv(1)
    """
    primary_statement = """
save_packets_to_sqldb(packets)
    """
    results = timeit.Timer(primary_statement, setup_statement).repeat(100, 1)
    print results
    print "min time " + str(min(results))
