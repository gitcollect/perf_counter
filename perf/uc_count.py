#!/usr/bin/python
# File Name: perf_count.py

"""
	This file is used to count and calculate the uncore performance events
	Uncore events can only be supported system-wide.
"""

import os
import string
import sys 
import getopt
import locale
import argparse

CONCURRENCY = 0
INTERVAL = ""
TOTAL_TIME = ""
SOCKET_NR = 2

event_list = []
event_value = []

def median(lst):
	lst.sort()
        return lst[len(lst)/2]

def mean(lst):
	return sum(lst)/float(len(lst))

def init_event_list():
	event_list.append('uncore_imc_0/event=0x4,umask=0x3/')
	event_list.append('uncore_imc_1/event=0x4,umask=0x3/')
	event_list.append('uncore_imc_2/event=0x4,umask=0x3/')
	event_list.append('uncore_imc_3/event=0x4,umask=0x3/')

	for i in range(len(event_list)*SOCKET_NR):
		event_value.append([])

def execute_cmd(event_name, output):
	cmd = "perf stat -e " + event_name + " -I" + INTERVAL + " -a --per-socket" + " sleep "+ TOTAL_TIME +  " 2>>" + output
	os.popen(cmd)

def process(output):

	data = open(output, 'r')
	activities = data.readlines()
	data.close()

	locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

	for activity in activities:
		activity_list = activity.split()
		if (len(activity_list) == 5):
			for i in range(len(event_list)):
				if ((activity_list[4] == event_list[i])):
					socket = (int)(activity_list[1].split("S")[1])
					try:
						event_value[socket*len(event_list)+i].append(locale.atoi(activity_list[3]))
					except (TypeError, ValueError, AttributeError):
						event_value[socket*len(event_list)+i].append(0)

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

	for event_name in event_name_list:
		execute_cmd(event_name, "output")

	process("output")

	result = open('data', 'a')
	result.writelines("%d "% (mean(item)) for item in event_value)
#	result.writelines("%d "% (median(item)) for item in event_value)
	result.close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--concurrency", type=int, default=50,
			    help="specify how many counters concurrently")
	parser.add_argument("-t", "--time", default="10",
			    help="specify the total time (s)")
	parser.add_argument("-i", "--interval", default="1000",
			    help="specify the interval (ms)")
	args = parser.parse_args()

	CONCURRENCY = args.concurrency
	TOTAL_TIME = args.time
	INTERVAL = args.interval
	main(sys.argv[1:])
