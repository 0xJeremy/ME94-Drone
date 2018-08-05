import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket
import math
import copy

# Used to rotate data. 'rotation' is in radians
rotation = 1.5708
origin = (0, 0) 

# Gets user input for position
def get_desired_position(plane):
	desired_pos = input('Enter desired ' + plane + ' coordinate: ')
	return desired_pos

# Calculates the amount of thrust power
def calculate_flight_power(position, desired_position):
	diff = desired_position - position
	if(abs(diff) <= 0.3):
		return 0
	margin = abs(diff*0.2)
	if(abs(diff) <= margin):
		return 0
	else:
		power = 0.020 * diff
		if(power > 0.20):
			return 0.20
		elif(power < -0.20):
			return -0.20
		else:
			return power

# Smoothes incoming data from MarvelMind
def smooth_data(previous, current):
	return ((previous*0.75) + (current*0.25))

# Rotates MarvelMind data around the origin
def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

# Sets initial position, calculates rotation, and returns position
def calculate_initial_position(initial_position, hedge_number):
	initial_position = copy.deepcopy(initial_position)
	initial_point = (initial_position[1], initial_position[2])
	initial_position[1], initial_position[2] = rotate(origin, initial_point, rotation)
	print("Initial Position " + str(hedge_number) + ": " + str(initial_position))
	return initial_position

def calculate_position(position, prev_position, initial_position):
	point = (position[1], position[2])
	position[1], position[2] = rotate(origin, point, rotation)
	position[1], position[2] = position[1]-initial_position[1], position[2]-initial_position[2]
	position[1] = smooth_data(prev_position[1], position[1])
	position[2] = smooth_data(prev_position[2], position[2])
	return position

def send_zero_power(client):
	data['power_x'] = 0
	data['power_y'] = 0
	data['time'] = position[4]
	jsonData = json.dumps(data)
	client.send(jsonData)



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
	prev_position_1, prev_position_5 = [], []
	data_log = []
	data_log_raw = []
	initial_position = []
	position = []
	first_run_1, first_run_5 = True
	location_counter = 0

	f = open("flight_data.txt", "w")

	# Loop to get location and fly drone
	while True:
		try:
			# Sleep delay. Change to change update speed
			# For multiple beacons, 0.125 works best
			sleep(0.125)

			# First run zeroing
			if(first_run_1 or first_run_5):
				# Gets initial position
				initial_position = copy.deepcopy(hedge.position())

				# Zeroing for Hedgehog 1
				if(initial_position[0] == 1 and first_run_1 == True):
					initial_position_1 = calculate_initial_position(initial_position)
					first_run_1 = False

				# Zeroing for Hedgehog 5
				elif(initial_position[0] == 5 and first_run_5 == True):
					initial_position_5 = calculate_initial_position(initial_position)
					first_run_5 = False

			# Gets drone position
			position = hedge.position()

			if(position[0] == 1 and first_run_1 == False):
				position_1 = calculate_position(position, prev_position_1, initial_position_1)
				prev_position_1 = copy.deepcopy(position_1)

			# Positioning for Hedgehog 5
			elif(position[0] == 5 and first_run_5 == False):
				position_5 = calculate_position(position, prev_position_5, initial_position_5)
				prev_position_5 = copy.deepcopy(position_5)
				print("5: " + str(position_5))

			# Prompts user for desired flight location

			if(flight_x == 0 and flight_y == 0):
				# Sends 0 power commands to quad
				send_zero_power(client)

				# Gets location from user
				desired_x = get_desired_position('x')
				desired_y = get_desired_position('y')
				location_counter += 1

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