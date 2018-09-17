import sys, numpy as np
import json
from time import sleep
from contextlib import contextmanager
import os
import socket

def main():
	# JavaScript Local Data Socket
	socket_path = '/tmp/node-python-sock'
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)

	# Python Ethernet Slave Socket
	TCP_IP = '127.0.0.1'
	TCP_PORT = 5005
	BUFFER_SIZE = 1024
	tcp = socket.socket(Socket.AF_INET, socket.SOCK_STREAM)
	tcp.connect((TCP_IP, TCP_PORT))

	while True:
		try:
			sleep(0.25)

			# Gets data from TCP socket
			tcp_data = tcp.recv(BUFFER_SIZE)

			# Parses TCP data
			tcp_parsed = json.parse(tcp_data)

			# Sets the flight values from TCP data
			data['power_x'] = tcp_parsed['power_x']
			data['power_y'] = tcp_parsed['power_y']
			data['time'] = tcp_parsed['time']

			# Converts to json format
			jsonData = json.dumps(data)

			# Sends data to JavaScript (marvel_drone_socket.js)
			client.send(jsonData)

		# Ends infinite loop and closes threads
		except KeyboardInterrupt:
			client.close()
			tcp.close()
			sys.exit()

if __name__=='__main__':
	main()