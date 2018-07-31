import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket
import math

def get_desired_position(plane):
	desired_pos = input('Enter desired ' + plane + ' coordinate: ')
	return desired_pos

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

def smooth_data(previous, current):
	diff = current - previous
	if(diff > (previous*0.1)):
		return (previous*1.1)
	if(diff < -(previous*0.1)):
		return (previous*0.9)
	return current

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

# Rotate 136 degrees
def main():
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()
	socket_path = '/tmp/node-python-sock'
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)
	desired_x, desired_y, flight_x, flight_y = 0, 0, 0, 0
	data, y = {}, []
	all_data_x, all_data_y, all_data_time = [], [], []
	first_run = True
	rotation = 136
	origin = (0, 0)
	while True:
		try:
			sleep(1)
			if(first_run):
				initial_position = hedge.position()
				y = initial_position
				point = (y[1], y[2])
				y[1], y[2] = rotate(origin, point, rotation)
				first_run = False
			x = hedge.position()
			x[1] = smooth_data(y[1], x[1]-initial_position[1])
			x[2] = smooth_data(y[2], x[2]-initial_position[2])
			point = (x[1], x[2])
			x[1], x[2] = rotate(origin, point, rotation)
			all_data_x.append(x[1])
			all_data_y.append(x[2])
			all_data_time.append(x[4])
			y = x
			print(x)
			if(flight_x == 0 and flight_y == 0):
				desired_x = get_desired_position('x')
				desired_y = get_desired_position('y')
			flight_x = calculate_flight_power(x[1], desired_x)
			# flight_y = calculate_flight_power(x[2], desired_y)
			data['power_x'] = flight_x
			# data['power_y'] = flight_y
			data['time'] = x[4]
			jsonData = json.dumps(data)
			client.send(jsonData)
		except KeyboardInterrupt:
			client.close()
			hedge.stop()
			sys.exit()

if __name__=='__main__':
	main()