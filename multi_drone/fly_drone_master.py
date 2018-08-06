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
def get_desired_position():
	x = input('Enter desired x coordinate: ')
	y = input('Enter desired y coordinate: ')
	return x, y

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

# Calculates the relative positon of the drone
def calculate_position(position, prev_position, initial_position):
	point = (position[1], position[2])
	position[1], position[2] = rotate(origin, point, rotation)
	position[1], position[2] = position[1]-initial_position[1], position[2]-initial_position[2]
	position[1] = smooth_data(prev_position[1], position[1])
	position[2] = smooth_data(prev_position[2], position[2])
	return position

# Sends a specified power to the drone
def send_power(client, x, y, time):
	data['power_x'] = x
	data['power_y'] = y
	data['time'] = time
	jsonData = json.dumps(data)
	client.send(jsonData)

# Returns a json object with the position and the flight powers
def get_json_data(position, x, y):
	data['power_x'] = calculate_flight_power(position[1], x)
	data['power_y'] = calculate_flight_power(position[2], y)
	data['time'] = position[4]
	jsonData = json.dumps(data)
	return jsonData

def main():
	# Setup for MarvelMind and data socket
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()

	# Local JavaScript Socket
	socket_path = '/tmp/node-python-sock'
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)

	# TCP Data Socket Master
	TCP_IP = '127.0.0.1'
	TCP_PORT = 5005
	BUFFER_SIZE = 1024
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	tcp, addr = s.accept()

	# Variable declarations and initalization
	desired_x_1, desired_y_1, flight_x_1, flight_y_1 = 0, 0, 0, 0
	desired_x_5, desired_y_5, flight_x_5, flight_y_5 = 0, 0, 0, 0
	data_1, data_5 = {}, {}
	prev_position_1, prev_position_5 = [], []
	data_log_1, data_log_5 = [], []
	data_log_raw_1, data_log_raw_5 = [], []
	initial_position_1, initial_position_5 = [], []
	position = []
	first_run_1, first_run_5 = True
	location_counter_1, location_counter_5 = 0, 0

	f1 = open("flight_data_1.txt", "w")
	f5 = open("flight_data_5.txt", "w")

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
				print("1: " + str(position_1))

			# Positioning for Hedgehog 5
			elif(position[0] == 5 and first_run_5 == False):
				position_5 = calculate_position(position, prev_position_5, initial_position_5)
				prev_position_5 = copy.deepcopy(position_5)
				print("5: " + str(position_5))

			# Prompts user for desired flight location
			if(flight_x_1 == 0 and flight_y_1 == 0):
				# Sends 0 power commands to quad
				send_power(client, 0, 0, 0)

				# Gets location from user
				desired_x_1, desired_y_1 = get_desired_position()
				location_counter_1 += 1

			if(flight_x_5 == 0 and flight_y_5 == 0):
				# Sends 0 power commands to quad
				send_power(tcp, 0, 0, 0)

				# Gets location from user
				desired_x_5, desired_y_5 = get_desired_position()
				location_counter_5 += 1

			# Gets jsonData
			jsonData_1 = get_json_data(position_1, desired_x_1, desired_y_1)
			jsonData_5 = get_json_data(position_5, desired_x_5, desired_y_5)

			# Sends data to JavaScript (marvel_drone_socket.js)
			client.send(jsonData_1)

			# Sends data to TCP Client (Raspberry Pi)
			tcp.send(jsonData_5)

		# Ends infinite loop and closes threads
		except KeyboardInterrupt:
			client.close()
			tcp.close()
			hedge.stop()
			sys.exit()

if __name__=='__main__':
	main()