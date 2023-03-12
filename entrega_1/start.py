import sys
import os
import simulator
import datetime as dt

if __name__ == "__main__":
    simulator.update_offers_day(n=800, t="2024-04-04")

    # if len(sys.argv) == 1:
    #     t = 0 
    #     simulator.simulation_date_run(t)
    # else:
    #      t = dt.datetime(sys.argv[1])
         
         
         
        #  if int(t[0:4]) >= 2021 and int(t[0:4]) <= 2030 and int(t[5:7]) >= 1 and int(t[5:7]) <= 12 and int(t[8:10]) >= 1 and int(t[8:10]) <= 31:
        #      simulator.simulation_date_run(t)
        #  else: 
        #      print("Please, add date with this format: YYYY-MM-DD")

