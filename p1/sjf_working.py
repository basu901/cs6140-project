# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

import sys
import process_gen
from util import *

inf = float('inf') # Define constant for infinity

# Behavior for Submitty = False
# If you want to see all output (i.e. events after 1000ms) set to True
verbose = False 

# TODO

# Either of us
# Resolve IO bug
# Test preemptions (output3, srt)
# (Eventually) Confirm output for all 4 tests for SJF and SRT

# Farhad
# Store stats in Process object
# Increment wait time, other stats in algorithm
# Compute average stats at end

# Mike
# Adjust formatting to match Submitty output

# End TODO

# Implementation of Shortest Job First & Shortest Time Remaining

# processes:  (list)    Contains process info (arrival time, cpu bursts, io bursts)
# t_cs:       (integer) Time (ms) for context switch
# alpha:      (float)   Weight parameter for updating burst time estimate
# preemptive: (boolean) False -> SJF, True -> SRT
def SJF_SRT(processes, t_cs, alpha, preemptive):
  n_processes = len(processes)
  ave_CPU_burst = 0
  ave_wait_time = 0
  ave_turnaround = 0
  no_context_switch = 0
  no_preemptions = 0

  running_proc = None  # Process currently using CPU
  ready_queue = []
  doing_io    = []     # List of processes currently blocked by io

  preempted = False  # Was in_process pre-empted by out_process?
  switch_time_1 = 0  # The time the first  half of the context switch will complete
  switch_time_2 = 0  # The time the second half of the context switch will complete
  in_process = None  # The process going in to the CPU
  out_process = None # The process going out of the CPU (to the queue)

  if preemptive: alg = "SRT"
  else:          alg = "SJF"

  t = 0 # simulation clock
  print("time %.0fms: Simulator started for %s %s" % (t, alg, printQueue(ready_queue)))

  # Each iteration of the loop is 1ms
  while(not done(processes)):

    # Determine when next process will arrive
    next_proc, arr_time = getNextArrival(processes, t)
    
    # If a process is currently using the CPU, 
    #   determine when it will finish its current burst
    if running_proc != None: cpu_time = getCPUBurst(running_proc)
    else:                    cpu_time = inf
    
    # If there are processes currently blocked on IO,
    #   determine when the next one will finish
    if not doing_io: io_time = inf
    else:            io_time = getIOBurst(doing_io[0]) 

    if t == switch_time_2 and switch_time_2 != 0: # Second half of context switch over
      running_proc = in_process # Put process on the CPU 
      switch_time_2 = 0
      in_process = None
      if t <= 999 or verbose:
        print("time %.0fms: Process %s started using the CPU for %.0fms burst %s" % (t, running_proc.name, running_proc.orig_bursts[running_proc.curr_cpu], printQueue(ready_queue)))

    if cpu_time == 0:
      if processCompleted(running_proc):
        print("time %.0fms: Process %s terminated %s" % (t, running_proc.name, printQueue(ready_queue)))
        running_proc.terminated = True
      else:
        updateBurstGuess(running_proc, alpha, running_proc.orig_bursts[running_proc.curr_cpu])
    
        if t <= 999 or verbose:
          bursts = running_proc.no_cpu_bursts - running_proc.curr_cpu - 1
          if bursts == 1:
            print("time %.0fms: Process %s completed a CPU burst; %d burst to go %s" % (t, running_proc.name, bursts, printQueue(ready_queue)))
          else:
            print("time %.0fms: Process %s completed a CPU burst; %d bursts to go %s" % (t, running_proc.name, bursts, printQueue(ready_queue)))
      
          print("time %.0fms: Recalculated tau = %.0fms for process %s %s" % (t, running_proc.tau, running_proc.name, printQueue(ready_queue)))
          print("time %.0fms: Process %s switching out of CPU; will block on I/O until time %.0fms %s" % (t, running_proc.name, t + running_proc.io_bursts[running_proc.curr_io] + (t_cs / 2), printQueue(ready_queue)))     
    
        running_proc.curr_cpu += 1 # Increment CPU burst counter
    
      switch_time_1 = t + (t_cs / 2.)
      out_process = running_proc
      running_proc = None

    while io_time == 0:
      doing_io[0].curr_io += 1 # Increment IO burst counter
      popped = doing_io.pop(0) # Remove from IO queue
      addToQueue(ready_queue, popped, True) # Add to ready queue

      if t <= 999 or verbose:
        print("time %.0fms: Process %s (tau %.0fms) completed I/O; added to ready queue %s" % (t, popped.name, popped.tau, printQueue(ready_queue)))

      # Need to check if another process finished doing I/O at the same time 
      if not doing_io: io_time = inf
      else:            io_time = getIOBurst(doing_io[0]) 

    if t == arr_time:
      addToQueue(ready_queue, next_proc, True)

      if t <= 999 or verbose:
        print("time %.0fms: Process %s (tau %.0fms) arrived; added to ready queue %s" % (t, next_proc.name, next_proc.tau, printQueue(ready_queue)))

    # If no process is doing any of the following: 
      # (a) using the CPU
      # (b) switching *out* of the CPU
      # (c) switching *in*  to the CPU
    # and there are processes waiting in the ready queue,
    # begin a context switch for the first process in the queue
    if running_proc == None and switch_time_1 == 0 and out_process == None and switch_time_2 == 0 and in_process == None and ready_queue:
      switch_time_2 = t + (t_cs / 2)  # No process to wait for -- only wait half switch
      in_process = ready_queue.pop(0) # Remove immediately

    if t == switch_time_1 and switch_time_1 != 0: # First half of context switch over
      if not processCompleted(out_process):      # If process isn't done
        addToQueue(doing_io, out_process, False) # start it on I/O
      switch_time_1 = 0
      out_process = None

      # Grab a process from the queue (if there is one in the queue) to go in the CPU
      # (if there isn't one on its way already)
      if bool(ready_queue) and switch_time_2 == 0 and in_process == None:
        switch_time_2 = t + (t_cs / 2)
        in_process = ready_queue.pop(0)

    # Run everything for 1ms
    if running_proc != None: useCPU(running_proc, 1)
    for i in range(len(doing_io)):
      doIO(doing_io[i], 1)

    t += 1 # Increment clock

  # End of Main Loop
  t -= 1          # Remove increment from last iteration of loop
  t += (t_cs / 2) # Add 1/2 context switch for last process removal

  print("time %.0fms: Simulator ended for %s [Q <empty>]" % (t, alg))
  return ave_CPU_burst, ave_wait_time, ave_turnaround, no_context_switch, no_preemptions

# queue is a list of Process
# Function assumes queue is already in order
def printQueue(queue):
  if not queue:
    return "[Q <empty>]"

  s = "[Q"
  for p in queue:
    s += " " + p.name

  s += "]"
  return s

# isCPU - True  if queue is running_queue
#       - False if queue is doing_io
def addToQueue(queue, proc, isCPU):
  # Queue is empty
  if not queue:
    queue.append(proc)

  # Ready Queue
  elif isCPU:
    proc_burst = proc.tau_rem

    for i in range(len(queue)):
      queue_burst = queue[i].tau_rem

      # If two processes have the same burst time, tie is broken
      #   by name (i.e. alphabetic order)
      if proc_burst == queue_burst:
        if proc.name < queue[i].name:
          queue.insert(i, proc)
          return

      elif proc_burst < queue_burst:
        queue.insert(i, proc)
        return

    # Got to end -- add to end of queue
    queue.append(proc)

  # IO Queue
  else:
    proc_burst = getIOBurst(proc)

    for i in range(len(queue)):
      queue_burst = getIOBurst(queue[i])

      # If two processes have the same burst time, tie is broken
      #   by name (i.e. alphabetic order)
      if proc_burst == queue_burst:
        if proc.name < queue[i].name:
          queue.insert(i, proc)
          return

      elif proc_burst < queue_burst:
        queue.insert(i, proc)
        return

    # Got to end -- add to end of queue
    queue.append(proc)

