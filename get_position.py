import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def main():
    hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False) # create MarvelmindHedge thread
    hedge.start() # start thread
    x = hedge.position()
    data = {}
    data['x'] = x[0]
    data['y'] = x[1]
    data['z'] = x[2]
    data['time'] = x[3]
    jsonData = json.dumps(data)
    print (jsonData) # get last position and print
    with suppress_stdout():
        hedge.stop()
    file = open("drone_position.txt", "w")
    file.write(jsonData)
    file.close()
    # while True:
    #     try:
    #         sleep(1)
    #         x = hedge.position()
    #         data = {}
    #         data['x'] = x[0]
    #         data['y'] = x[1]
    #         data['z'] = x[2]
    #         data['time'] = x[3]
    #         jsonData = json.dumps(data)
    #         print (jsonData) # get last position and print
    #         # hedge.print_position()
    #     except KeyboardInterrupt:
    #         hedge.stop()  # stop and close serial port
    #         sys.exit()

if __name__=='__main__':
    main()