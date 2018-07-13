import sys, json, numpy as np
import json
from marvelmind import MarvelmindHedge
from time import sleep
from contextlib import contextmanager
import sys, os
import socket

def main():
	hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=10, debug=False)
	hedge.start()
	socket_path = '/tmp/node-python-sock'
	# connect to the unix local socket with a stream type
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(socket_path)
	while True:
		try:
			sleep(1)
			x = hedge.position()
			data = {}
			data['x'] = x[0]
			data['y'] = x[1]
			data['z'] = x[2]
			data['time'] = x[3]
			jsonData = json.dumps(data)
			# Might need to send as bytes...
			client.send(jsonData)
		except KeyboardInterrupt:
			client.close()
			hedge.stop()  # stop and close serial port
			sys.exit()

if __name__=='__main__':
	main()

# # send an initial message (as bytes)
# client.send(b'python connected')
# # start a loop
# while True:
#	 # wait for a response and decode it from bytes
#	 msg = client.recv(2048).decode('utf-8')
#	 print(msg)
#	 if msg == 'hi':
#		 client.send(b'hello')
#	 elif msg == 'end':
#		 # exit the loop
#		 break

# # close the connection
# client.close()