#!/bin/bash

gnome-terminal -e "node fly_drone.js"
sleep 1
python fly_drone.py
