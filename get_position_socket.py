import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket

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
	if(diff < (previous*0.1)):
		return (previous*0.9)
	return current

def main():
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()
	socket_path = '/tmp/node-python-sock'
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)
	desired_x, desired_y, flight_x, flight_y = 0, 0, 0, 0
	data, y, all_data = {}, {0, 0, 0, 0, 0}, {}
	while True:
		try:
			sleep(1)
			x = hedge.position()
			x[1] = smooth_data(y[1], x[1])
			x[2] = smooth_data(y[2], x[2])
			add_data += x
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