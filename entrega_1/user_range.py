import sys
import os
import simulator
import pytz
import datetime as dt

if __name__ == "__main__":
    tz = pytz.timezone('America/Bogota')
    t = dt.datetime.now(tz).date()
    if len(sys.argv) == 1:
        simulator.pair_number_verify(800,t)
    else:
         n = int(sys.argv[1])
         simulator.pair_number_verify(n,t)

