import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket
import math
import copy

rotation = 1.5708
origin = (0,0)

socket_path = '/tmp/node-python-sock'
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socket_path)

class drone:
	def __init__(self, num):
		self.drone_num = num
		self.desired_x = 0
		self.desired_y = 0
		self.flight_x = 0
		self.flight_y = 0
		self.data = {}
		self.prev_position = []
		self.data_log = []
		self.data_low_raw = []
		self.position = []
		self.location_counter = 0
		self.initial_position = []
		self.eland = False
		self.first_time = True

	def fly(hedge):
		if(first_time):
			first_run(hedge)
		calculate_position()
		check_input_need()
		set_flight_power()
		send_json_data()

	def first_run(self, hedge):
		self.first_time = False
		self.initial_position = calculate_initial_position(hedge)

	def calculate_initial_position(self, hedge):
		initial_point = (initial_position[1], initial_position[2])
		self.initial_position[1], self.initial_position[2] = rotate(origin, initial_point, rotation)

	def rotate(origin, point, angle):
		ox, oy = origin
		px, py = point
		qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
		qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
		return qx, qy

	def calculate_position(self):
		point = (self.position[1], self.position[2])
		self.position[1], self.position[2] = rotate(origin, point, rotation)
		self.position[1] = self.position[1]-self.initial_position[1]
		self.position[2] = self.position[2]-self.initial_position[2]
		self.position[1] = smooth_data(self.prev_position[1], self.position[1])
		self.position[2] = smooth_data(self.prev_position[2], self.position[2])

	def smooth_data(previous, current):
		return ((previous*0.75) + (current*0.25))

	def check_input_need(self):
		if(self.flight_x == 0 and self.flight_y == 0):
			request_position()

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

	def send_json_data(self):
		data['drone_num'] = self.drone_num
		data['power_x'] = self.flight_x
		data['power_y'] = self.flight_y
		data['eland'] = self.eland
		jsonData = json.dumps(data)
		client.send(jsonData)


def main():
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()

	swarm = []
	quad1 = drone(1)
	quad5 = drone(5)
	swarm.append(quad1)
	swarm.append(quad5)

	while True:
		try:
			sleep(0.125)

			hedge_pos = hedge.position()

			for quad in swarm:
				if(hedge_pos[0] == quad.drone_num):
					quad.fly(hedge_pos)

		except KeyboardInterrupt:
			quad1.send_land()
			quad5.send_land()
			client.close()
			hedge.stop()
			sys.exit()

if __name__=='__main__':
	main()