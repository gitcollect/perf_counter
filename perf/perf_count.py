#!/usr/bin/python
# File Name: perf_count.py

"""
	This file is used to count and calculate the performance events
"""

import os
import string
import sys 
import getopt
import locale

PID = "25677"

MAX_CONCURRENCY = 50
ROUND_NR = 5

event_list = []
event_value = []

def init_event_list():
#	event_list.append('cache-references')
#	event_list.append('cache-misses')
	event_list.append('L1-dcache-loads')
	event_list.append('L1-dcache-load-misses')
	event_list.append('L1-dcache-stores')
	event_list.append('L1-dcache-store-misses')
	event_list.append('L1-dcache-prefetch-misses')
	event_list.append('L1-icache-load-misses')
	event_list.append('LLC-loads')
	event_list.append('LLC-load-misses')
	event_list.append('LLC-stores')
	event_list.append('LLC-store-misses')
	event_list.append('LLC-prefetches')
	event_list.append('LLC-prefetch-misses')
	event_list.append('dTLB-loads')
	event_list.append('dTLB-load-misses')
	event_list.append('dTLB-stores')
	event_list.append('dTLB-store-misses')
	event_list.append('iTLB-loads')
	event_list.append('iTLB-load-misses')
	event_list.append('branch-loads')
	event_list.append('branch-load-misses')
	event_list.append('node-loads')
	event_list.append('node-load-misses')
	event_list.append('node-stores')
	event_list.append('node-store-misses')
	event_list.append('node-prefetches')
	event_list.append('node-prefetch-misses')

	for i in range(len(event_list)):
		event_value.append(0)

def execute_cmd(event_name, pid, output):
	cmd = "perf stat -e " + event_name + " -p " + pid + " sleep 0.1 " +  "2>>" + output
	os.popen(cmd)

def process(output):

	data = open(output, 'r')
	activities = data.readlines()
	data.close()

	locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

	for i in range(len(event_list)):
		for activity in activities:
			activity_list = activity.split(' ')
			for j in range(len(activity_list)):
				if (activity_list[j] == event_list[i]):
					try:
						event_value[i] = event_value[i] + locale.atoi(activity_list[j-1])
					except (TypeError, ValueError, AttributeError):
						event_value[i] = event_value[i]

def main(argv):
	init_event_list()

	event_name_list = []
	index = 0
	event_temp = ""
	for event in event_list:
		index = index + 1
		event_temp = event_temp + event + ","
		if (index == MAX_CONCURRENCY):
			index = 0
			event_name_list.append(event_temp[:-1])
			event_temp = ""
	if (index != 0):
		event_name_list.append(event_temp[:-1])

	cmd = "rm -rf output"
	os.popen(cmd)

	for i in range(ROUND_NR):
		for event_name in event_name_list:
			execute_cmd(event_name, PID, "output")

	process("output")
	result = open('data', 'w')
	result.writelines("%d "% (item/ROUND_NR) for item in event_value)
	result.close()

if __name__ == "__main__":
	main(sys.argv[1:])
