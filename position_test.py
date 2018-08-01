from marvelmind import MarvelmindHedge
from time import sleep
import sys
import math
import copy

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def main():
    hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False) # create MarvelmindHedge thread
    hedge.start() # start thread
    origin = (0, 0)
    rotation = 2.37365
    first_run = True
    initial_position = []
    position = []
    while True:
        try:
            sleep(1)
            if(first_run):
                initial_position = copy.deepcopy(hedge.position())
                initial_point = (initial_position[1], initial_position[2])
                initial_position[1], initial_position[2] = rotate(origin, initial_point, rotation)
                print("INITIAL POSITION: " + str(initial_position))
                first_run = False
            # print (hedge.position()) # get last position and print
            position = hedge.position()
            point = (position[1], position[2])
            position[1], position[2] = rotate(origin, point, rotation)
            position[1], position[2] = position[1]-initial_position[1], position[2]-initial_position[2]
            print(position)
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port
            sys.exit()
main()