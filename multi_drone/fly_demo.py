import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket
import math
import copy

ROTATION = 1.5708
ORIGIN = (0,0)

DEMOX = [0, 0.75, -0.75, 0]
DEMOY = [0, 0.75, -0.75, 0]

socket_path = '/tmp/node-python-sock'
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socket_path)

def rotate(point, angle):
	ox, oy = ORIGIN
	px, py = point
	qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
	qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
	return qx, qy

def smooth_data(previous, current):
	return ((previous*0.75) + (current*0.25))

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

class drone:
	def __init__(self, num):
		self.drone_num = num
		self.desired_x = 0
		self.desired_y = 0
		self.flight_x = 0
		self.flight_y = 0
		self.data = {}
		self.prev_position = [0, 0, 0]
		self.data_log = []
		self.data_low_raw = []
		self.position = []
		self.location_counter = 0
		self.initial_position = [0, 0, 0]
		self.position = [0, 0, 0]
		self.eland = 0
		self.first_run = True
		self.demo_counter = 0

	def fly(self, hedge):
		self.calculate_position(hedge)
		self.check_input_need()
		self.set_flight_power()
		self.send_json_data()

	def calculate_initial_position(self, hedge):
		initial_point = (hedge[1], hedge[2])
		self.initial_position[1], self.initial_position[2] = rotate(initial_point, ROTATION)
		self.first_run = False

	def calculate_position(self, hedge):
		point = (hedge[1], hedge[2])
		self.position[1], self.position[2] = rotate(point, ROTATION)
		self.position[1] = self.position[1]-self.initial_position[1]
		self.position[2] = self.position[2]-self.initial_position[2]
		self.position[1] = smooth_data(self.prev_position[1], self.position[1])
		self.position[2] = smooth_data(self.prev_position[2], self.position[2])

	def check_input_need(self):
		if(self.flight_x == 0 and self.flight_y == 0):
			self.desired_x = DEMOX[self.demo_counter]
			self.desired_y = DEMOY[self.demo_counter]
			self.demo_counter += 1

	def request_position(self):
		print("Currently controlling drone number " + str(self.drone_num))
		self.desired_x = input('Enter desired x coordinate: ')
		self.desired_y = input('Enter desired y coordinate: ')

	def set_desired(self, x, y):
		self.desired_x = x
		self.desired_y = y

	def set_flight_power(self):
		self.flight_x = calculate_flight_power(self.position[1], self.desired_x)
		self.flight_y = calculate_flight_power(self.position[2], self.desired_y)

	def send_json_data(self):
		self.data['drone_num'] = self.drone_num
		self.data['power_x'] = self.flight_x
		self.data['power_y'] = self.flight_y
		self.data['eland'] = self.eland
		jsonData = json.dumps(self.data)
		client.send(jsonData)

	def send_land(self):
		self.eland = 1
		self.send_json_data()


def main():
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()

	swarm = []
	quad1 = drone(1)
	# quad5 = drone(5)
	swarm.append(quad1)
	# swarm.append(quad5)

	while True:
		try:
			sleep(0.125)

			hedge_pos = hedge.position()

			for quad in swarm:
				if(hedge_pos[0] == quad.drone_num and quad.first_run):
					quad.calculate_initial_position(hedge_pos)

			for quad in swarm:
				if(hedge_pos[0] == quad.drone_num):
					quad.fly(hedge_pos)

		except KeyboardInterrupt:
			quad1.send_land()
			# quad5.send_land()
			client.close()
			hedge.stop()
			sys.exit()

if __name__=='__main__':
	main()