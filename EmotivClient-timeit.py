import EmotivClient
import timeit

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
