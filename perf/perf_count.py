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
import argparse

PID = ""
CONCURRENCY = 0
ROUND_NR = 0
INTERVAL = ""

event_list = []
event_value = []

def median(lst):
	lst.sort()
        return lst[len(lst)/2]

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
		event_value.append([])

def execute_cmd(event_name, pid, output):
	cmd = "perf stat -e " + event_name + " -p " + pid + " sleep "+ INTERVAL +  " 2>>" + output
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
						event_value[i].append(locale.atoi(activity_list[j-1]))
					except (TypeError, ValueError, AttributeError):
						event_value[i].append(0)

def main(argv):
	init_event_list()

	event_name_list = []
	index = 0
	event_temp = ""
	for event in event_list:
		index = index + 1
		event_temp = event_temp + event + ","
		if (index == CONCURRENCY):
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

	result = open('data', 'a')
	result.writelines("%d "% (median(item)) for item in event_value)
	result.writelines("\n")
	result.close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("pid", help="specify the process id")
	parser.add_argument("-c", "--concurrency", type=int, default=50,
			    help="specify how many counters concurrently")
	parser.add_argument("-n", "--round_nr", type=int, default=5,
			    help="specify how many rounds you want to counter")
	parser.add_argument("-i", "--interval", default="0.1",
			    help="specify how long for each round")
	args = parser.parse_args()

	PID = args.pid
	CONCURRENCY = args.concurrency
	ROUND_NR = args.round_nr
	INTERVAL = args.interval

	main(sys.argv[1:])
