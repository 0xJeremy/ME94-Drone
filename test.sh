#!/bin/bash

while(true)
do
	python get_position.py
	node marvel_drone.js
done