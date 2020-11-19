#!/usr/bin/env python3


# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

import sys
import random as rand
import collections as col

#FUNCTION TO PRINT THE QUEUE
def printQueue(q):
	print("[Q", end = " ")
	for i in range(len(q)-1):
		print(q[i].name,end = " ")
	if(q):
		print(q[len(q)-1].name,"]",sep="")
	else:
		print("<empty>]")



#DEFINING THE PROCESS OBJECT
class Process(object):
    def __init__(self, name):
        self.name = name
    def set_params(self, arrival_time, no_bursts, cpu_burst_list, io_burst_list):
        self.arrival = arrival_time
        self.no_cpu_bursts = no_bursts
        self.cpu_bursts = cpu_burst_list
        self.io_bursts = io_burst_list
        self.is_prempt = False
        self.in_cpu_time=0.0	#Used to store the time spent in the CPU
        self.wait_time=0.0	#Used to store the amount of time spent waiting for the CPU
        self.turn_time=0.0	#Used to store the turn time
        self.cpu_burst_no=0	#CPU burst number being executed
        self.io_no=0		#IO number being executed
        self.io_time=0.0	#Time at which IO burst has been completed
        self.cpu_time=0.0	#Time at which CPU burst is to be completed
        self.ready_queue_enter=0.0	#Time at which the process enter the ready_queue
        self.init_cs=0.0		#Store the intial context switch time
        self.final_cs=0.0		#Store the final context swtich time

	


def RR_FCFS(is_rr,t_slice_in,n,process_list,t_cs,end):
	
	if(is_rr):
		t_slice = t_slice_in
	else:
		t_slice = float('inf')

	n_processes = n			#Total number of processes
	processes = process_list	#The list of processes		
	total_cpu_time = 0		#Total CPU BURST over all processes
	no_of_cs = 0			#Total number of context_switches
	no_of_premp = 0			#Total number of pre-emptions
	cpu_each_process = 0		#Sum over all CPU Bursts of each process
	total_jobs = 0			#Total no of bursts over all processes

	for i in processes:
		for j in range(0,i.no_cpu_bursts):
			cpu_each_process += i.cpu_bursts[j]
		total_cpu_time +=cpu_each_process
		total_jobs += i.no_cpu_bursts
		cpu_each_process=0

	#sorting by name
	processes.sort(key=lambda x:x.name)
	#sorting based on the arrival time
	processes.sort(key=lambda x:x.arrival)
	

	ready_queue = col.deque()

	time=0	

	process_arrived=list()		#Store the arrived processes
	io_list=list()			#Store the processes doing IO
	io_complete_list=list()		#list of processes which have finished IO
	done_list = list()		#used to store completed processes
	finished_burst = None		#to check if process has been switched out of CPU
	cpu_occupied= False		#to check if the CPU is occupied
	prev_occ_cpu = None		#to store the latest process Object occupying the CPU
	occ_cpu = None			#Process presently occupying the CPU
	in_io = False			#Is the process performing IO
	no_switch_process=None		#Process not being pre-empted because of empty ready queue

	if(is_rr):
		print("time ",time,"ms: Simulator started for RR",sep="",end=" ")
	else:
		print("time ",time,"ms: Simulator started for FCFS",sep="",end=" ")
	printQueue(ready_queue)

	while(len(done_list)<n_processes):
			
		if(processes):
			while(processes):
				if(processes[0].arrival==time):
					processes[0].ready_queue_enter = time
					process_arrived.append(processes.pop(0))
				else:	
					break
		if(not occ_cpu):#THIS CHECK IS DONE AS WE WOULD LIKE TO PRINT 'ARRIVALS TIME' LATER, EXCEPT FOR THE FIRST CASE 
			if(process_arrived):
				if(time<1000):
					print("time ",time,"ms: Process ",(process_arrived[0].name)," arrived; added to ready queue",sep="",end = " ")
					ready_queue.append(process_arrived.pop(0))
					printQueue(ready_queue)
				else:
					ready_queue.append(process_arrived.pop(0))
			
		if(io_list):
			#sort the io list based on completion time
			io_list.sort(key=lambda x:x.io_time)
			#for each cpu in io_list, if io burst time is = time, insert them later into the ready queue
			while(io_list):
				if(io_list[0].io_time==time):
					io_list[0].ready_queue_enter = time
					io_list[0].is_prempt = False
					io_complete_list.append(io_list.pop(0))
					prev_occ_cpu=None # Same process going into CPU after IO should be context switched in  
				else:
					break
			#sort io list based on the process alphabets
			io_complete_list.sort(key=lambda x:x.name)

		if(cpu_occupied==False):
			if(no_switch_process):
				occ_cpu=no_switch_process #The same process is used without a context switch
				if(prev_occ_cpu == no_switch_process): #Do not include the context-switch-out time
					no_switch_process.turn_time -= t_cs*0.5
				#!!!!!!!!!!prev_occ_cpu=no_switch_process #To 
				no_switch_process=None
				no_of_cs -=1		#Reduce the number of context switches
			else:
				if(ready_queue):
					occ_cpu=ready_queue.popleft()
	
	
			if(occ_cpu):
				if(occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]>t_slice):
					if(prev_occ_cpu==occ_cpu):
						occ_cpu.cpu_time = time + t_slice + t_cs*0.5-1 	#When should the process be pre-empted
						occ_cpu.turn_time = occ_cpu.turn_time + (t_slice + t_cs*0.5)
						occ_cpu.final_cs = time + t_slice-1
					
					else:
						occ_cpu.cpu_time = time + t_slice + t_cs 	#When should the process be pre-empted
						occ_cpu.turn_time = occ_cpu.turn_time + (t_slice + t_cs)
						occ_cpu.init_cs = time + (t_cs*0.5)
						occ_cpu.final_cs = time + t_cs*0.5 + t_slice
					
					occ_cpu.wait_time = occ_cpu.wait_time + (time - occ_cpu.ready_queue_enter)
					occ_cpu.turn_time += (time-occ_cpu.ready_queue_enter)
					occ_cpu.single_burst_enter = 0
					cpu_burst_amount = occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]
					occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]=occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]-t_slice
					burst_incomplete = True	
					no_of_cs +=1			
					prev_occ_cpu = occ_cpu	#prev_occ_cpu is used to store the last process in cpu to avoid context 								#switch for the last process.
					cpu_occupied = True
				else:
					if(prev_occ_cpu==occ_cpu):
						occ_cpu.cpu_time = time + occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] + t_cs*0.5-1
						occ_cpu.final_cs = time + occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]-1
						occ_cpu.turn_time = occ_cpu.turn_time + (occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] + t_cs*0.5)

					else:
						occ_cpu.cpu_time = time + occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] + t_cs
						occ_cpu.init_cs = time + (t_cs*0.5)
						occ_cpu.final_cs = time + occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] + (t_cs*0.5)
						occ_cpu.turn_time = occ_cpu.turn_time + (occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] + t_cs)
	
					
					occ_cpu.wait_time = occ_cpu.wait_time + (time-occ_cpu.ready_queue_enter)
					occ_cpu.turn_time += (time-occ_cpu.ready_queue_enter)
					occ_cpu.single_burst_enter = 0
					cpu_burst_amount = occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]
					occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no] = 0
					burst_incomplete = False
					occ_cpu.cpu_burst_no = occ_cpu.cpu_burst_no + 1
					prev_occ_cpu = occ_cpu
					no_of_cs +=1
					cpu_occupied = True
						
		
		if(occ_cpu):

			if(occ_cpu.init_cs==time):
				if(time<1000):
					if(occ_cpu.is_prempt):
						print("time ",time,"ms: Process ",occ_cpu.name," started using the CPU with ",(cpu_burst_amount),"ms remaining",sep="",end = " ")
					else:
						print("time ",time,"ms: Process ",occ_cpu.name," started using the CPU for ",(cpu_burst_amount),"ms burst",sep="",end = " ")
					printQueue(ready_queue)
					if(burst_incomplete):
						occ_cpu.is_prempt = True
					else:
						occ_cpu.is_prempt = False
			
			if(occ_cpu.final_cs==time):
				if(not burst_incomplete):
					if(occ_cpu.cpu_burst_no<occ_cpu.no_cpu_bursts):
						if(occ_cpu.no_cpu_bursts-occ_cpu.cpu_burst_no==1):
							if(time<1000):
								print("time ",(time),"ms: Process ",(occ_cpu.name)," completed a CPU burst; ",(occ_cpu.no_cpu_bursts-occ_cpu.cpu_burst_no)," burst to go",sep="",end = " ")
								printQueue(ready_queue)
						else:
							if(time<1000):	
								print("time ",(time),"ms: Process ",(occ_cpu.name)," completed a CPU burst; ",(occ_cpu.no_cpu_bursts-occ_cpu.cpu_burst_no)," bursts to go",sep="",end = " ")
								printQueue(ready_queue)
					else:
						print("time ",(time),"ms: Process ",(occ_cpu.name)," terminated",sep="",end = " ")
						printQueue(ready_queue)

					
					if(occ_cpu.io_no<=occ_cpu.no_cpu_bursts-2):		
						io = occ_cpu.io_bursts[occ_cpu.io_no]
						occ_cpu.io_time = time + io + (t_cs*0.5)
						occ_cpu.io_no = occ_cpu.io_no + 1
						in_io=True
						io_list.append(occ_cpu)
						if(time<1000):
							print("time ",time,"ms: Process ",(occ_cpu.name)," switching out of CPU; will block on I/O until time ",round(occ_cpu.io_time),"ms",sep="",end = " ")
							printQueue(ready_queue)
						
							
				else:
				
					if(not ready_queue):
						no_switch_process=occ_cpu
						no_switch_process.ready_queue_enter=time+1
						no_switch_process.cpu_time=0 #To prevent being appended at the end of time slice
						if(time<1000):
							print("time ",time,"ms: Time slice expired; no preemption because ready queue is empty",sep="",end = " ")
							printQueue(ready_queue)
						cpu_occupied=False
						occ_cpu.cpu_time=0
					
					else:
						if(time<1000):
							print("time ",time,"ms: Time slice expired; process ",(occ_cpu.name)," preempted with ",(occ_cpu.cpu_bursts[occ_cpu.cpu_burst_no]),"ms to go",sep="",end = " ")
							printQueue(ready_queue)
						no_of_premp +=1
				
					
					
			if(occ_cpu.cpu_time==time):
				if(burst_incomplete):
					finished_burst=occ_cpu
					finished_burst.ready_queue_enter = time
					finished_burst.is_prempt =True #if Process has been pre-empted, different message to be returned on printing
					cpu_occupied=False
					occ_cpu=None
				else:
					if(occ_cpu.cpu_burst_no==occ_cpu.no_cpu_bursts):
						done_list.append(occ_cpu)
						cpu_occupied=False
						occ_cpu=None
					else:
						if(in_io):
							finished_burst=None
							occ_cpu=None
							cpu_occupied=False
							in_io=False
						else:
							finished_burst=occ_cpu
							finished_burst.ready_queue_enter=time
							cpu_occupied=False
							occ_cpu=None
				
					
				
	
		#if process has completed its time slice,append completed process first and then io and then process_arrived to the deque
		if(finished_burst):
			if(not end):
				ready_queue.extendleft([finished_burst])
			else:
				ready_queue.extend([finished_burst])
			finished_burst=None
	
		if(not end):
			if(io_complete_list):
				for i in range(len(io_complete_list)):
					ready_queue.appendleft(io_complete_list[i])
					if(time<1000):
						print("time ",(time),"ms: Process ",(io_complete_list[i].name)," completed IO; added to ready queue",sep="",end = " ")
						printQueue(ready_queue)
		else:
			if(io_complete_list):
				for i in range(len(io_complete_list)):
					ready_queue.append(io_complete_list[i])
					if(time<1000):
						print("time ",(time),"ms: Process ",(io_complete_list[i].name)," completed I/O; added to ready queue",sep="",end = " ")
						printQueue(ready_queue)
				
		io_complete_list.clear()

		if(not end):	
			if(process_arrived):
				for i in range(len(process_arrived)):
					ready_queue.appendleft(process_arrived[i])
					if(time<1000):
						print("time ",(time),"ms: Process ",(process_arrived[i].name)," arrived; added to ready queue",sep="",end = " ")
						printQueue(ready_queue)
		else:
			if(process_arrived):
				for i in range(len(process_arrived)):
					ready_queue.append(process_arrived[i])
					if(time<1000):
						print("time ",(time),"ms: Process ",(process_arrived[i].name)," arrived; added to ready queue",sep="",end = " ")
						printQueue(ready_queue)
		process_arrived.clear()		


	

		#Exit when all processes have completed
		if(len(done_list)==n_processes):
			break
		
		if(not occ_cpu and ready_queue):	#(Don't remember why this is there, but it's IMP)
			continue
		
		time = time + 1

	if(is_rr):
		print("time ",(time),"ms: Simulator ended for RR",sep="",end = " ")
	else:
		print("time ",(time),"ms: Simulator ended for FCFS",sep="",end = " ")
	printQueue(ready_queue)
	
	total_wait = 0
	total_turn = 0
	for i in done_list:
		total_wait += i.wait_time
		total_turn += i.turn_time
	
	return (total_cpu_time/total_jobs),(total_wait/total_jobs),(total_turn/total_jobs),no_of_cs,no_of_premp




