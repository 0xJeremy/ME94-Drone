import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket
import math
import copy

# Gets user input for position
def get_desired_position(plane):
	desired_pos = input('Enter desired ' + plane + ' coordinate: ')
	return desired_pos

# Calculates the amount of thrust power
def calculate_flight_power(position, desired_position):
	diff = desired_position - position
	margin = abs(diff*0.05)
	if(abs(diff) <= margin):
		return 0
	else:
		power = 0.05 * diff
		if(power > 0.5):
			return 0.5
		elif(power < -0.5):
			return -0.5
		else:
			return power

# Smoothes incoming data from MarvelMind
def smooth_data(previous, current):
	diff = current - previous
	if(diff > (previous*0.1)):
		return (previous*1.1)
	if(diff < -(previous*0.1)):
		return (previous*0.9)
	return current

# Rotates MarvelMind data around the origin
def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def main():
	# Setup for MarvelMind and data socket
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()
	socket_path = '/tmp/node-python-sock'
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)

	# Variable declarations and initalization
	desired_x, desired_y, flight_x, flight_y = 0, 0, 0, 0
	data = {}
	prev_position = []
	data_log = []
	data_log_raw = []
	first_run = True

	# Used to rotate data. 'rotation' is in radians
	rotation = 2.37365
	origin = (0, 0)

	# Loop to get location and fly drone
	while True:
		try:
			# Sleep delay. Change to change update speed
			sleep(1)

			# Code to run the first time
			if(first_run):
				# Gets initial position and rotates it
				initial_position = copy.deepcopy(hedge.position())
				initial_point = (initial_position[1], initial_position[2])
				initial_position[1], initial_position[2] = rotate(origin, point, rotation)

				# Sets the previous position
				prev_position = initial_position

				print("Initial Position: " + str(initial_position))

				first_run = False

			# Gets drone position
			position = hedge.position()

			# Rotates the drone position
			point = (position[1], position[2])
			position[1], position[2] = rotate(origin, point, rotation)

			# Adds positiion data to raw data log
			data_log_raw.append((position[1], position[2], position[4]))

			# Smooths position data
			position[1] = smooth_data(prev_position[1], position[1]-initial_position[1])
			position[2] = smooth_data(prev_position[2], position[2]-initial_position[2])

			# Adds position data to data log
			data_log.append((position[1], position[2], position[4]))

			# Sets current value as previous value
			prev_position = position

			# Displays location
			print(position)

			# Prompts user for desired flight location
			if(flight_x == 0 and flight_y == 0):
				desired_x = get_desired_position('x')
				desired_y = get_desired_position('y')

			# Calculates the drone power
			flight_x = calculate_flight_power(position[1], desired_x)
			flight_y = calculate_flight_power(position[2], desired_y)

			# Sets the flight values into a json format
			data['power_x'] = flight_x
			data['power_y'] = flight_y
			data['time'] = position[4]
			jsonData = json.dumps(data)

			# Sends data to JavaScript (marvel_drone_socket.js)
			client.send(jsonData)

		# Ends infinite loop and closes threads
		except KeyboardInterrupt:
			client.close()
			hedge.stop()
			sys.exit()

if __name__=='__main__':
	main()