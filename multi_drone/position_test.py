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
	rotation = 1.5708 #2.37365
	first_run_1 = True
	first_run_5 = True
	initial_position = []
	position = []
	while True:
		try:
			sleep(0.125)

			# First run zeroing
			if(first_run_1 or first_run_5):
				# Gets initial position
				initial_position = copy.deepcopy(hedge.position())

				# Zeroing for Hedgehog 1
				if(initial_position[0] == 1 and first_run_1 == True):
					initial_position_1 = copy.deepcopy(initial_position)
					initial_point_1 = (initial_position_1[1], initial_position_1[2])
					initial_position_1[1], initial_position_1[2] = rotate(origin, initial_point_1, rotation)
					print("INITIAL POSITION 1: " + str(initial_position_1))
					first_run_1 = False

				# Zeroing for Hedgehog 5
				elif(initial_position[0] == 5 and first_run_5 == True):
					initial_position_5 = copy.deepcopy(initial_position)
					initial_point_5 = (initial_position_5[1], initial_position_5[2])
					initial_position_5[1], initial_position_5[2] = rotate(origin, initial_point_5, rotation)
					print("INITIAL POSITION 5: " + str(initial_position))
					first_run_5 = False
  
  			# Gets Hedgehog position
			position = hedge.position()

			# Positioning for Hedgehog 1
			if(position[0] == 1 and first_run_1 == False):
				point = (position[1], position[2])
				position[1], position[2] = rotate(origin, point, rotation)
				position[1], position[2] = position[1]-initial_position_1[1], position[2]-initial_position_1[2]
				print(position)

			# Positioning for Hedgehog 5
			elif(position[0] == 5 and first_run_5 == False):
				point = (position[1], position[2])
				position[1], position[2] = rotate(origin, point, rotation)
				position[1], position[2] = position[1]-initial_position_5[1], position[2]-initial_position_5[2]
				print(position)
		except KeyboardInterrupt:
			hedge.stop()  # stop and close serial port
			sys.exit()
main()