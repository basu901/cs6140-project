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
verbose = True

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
  switch_time_1 = 0. # The time the first  half of the context switch will complete
  switch_time_2 = 0. # The time the second half of the context switch will complete
  in_process = None  # The process going in to the CPU
  out_process = None # The process going out of the CPU (to the queue)

  if preemptive: alg = "SRT"
  else:          alg = "SJF"

  t = 0. # simulation clock
  print("time %.0fms: Simulator started for %s %s" % (t, alg, printQueue(ready_queue)))

  # Each iteration of the loop, one interesting event happens (e.g. process arrives,
  #   process completes burst, etc.)
  # Therefore the amount of time passed on each iteration is *not* equal
  while(notDone(processes)):

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

    # Next interesting event is first half of context switch finishing
    if switch_time_1 > 0 and switch_time_1 <= arr_time and switch_time_1 <= (cpu_time + t) and switch_time_1 <= (io_time + t):
      time_step = switch_time_1 - t
      t = switch_time_1
    
      # IO can still happen during context switch!
      for i in range(len(doing_io)):
        doIO(doing_io[i], time_step)

      if processCompleted(out_process):
        pass
        #print("<Process %s left>" % out_process.name)
      elif preempted: # Add process to ready queue
        addToQueue(ready_queue, out_process, True)
        print("<Entered ready queue: %s>" % out_process.name)
        preempted = False
      else: # Process should start IO
        #print("TIME %.0f: Process %s entered IO Queue" % (t, out_process.name))
        addToQueue(doing_io, out_process, False)
      
      switch_time_1 = 0
      out_process = None

    # Next interesting event is second half of context switch finishing
    elif switch_time_2 > 0 and switch_time_2 <= arr_time and switch_time_2 <= (cpu_time + t) and switch_time_2 <= (io_time + t):
      time_step = switch_time_2 - t
      t = switch_time_2

      # IO can still happen during context switch!
      for i in range(len(doing_io)):
        doIO(doing_io[i], time_step)

      #ready_queue.remove(in_process) # Remove from ready queue 
      running_proc = in_process      # and put in the CPU
      if t <= 999 or verbose:
        print("time %.0fms: Process %s started using the CPU for %.0fms burst %s" % (t, in_process.name, in_process.orig_bursts[in_process.curr_cpu], printQueue(ready_queue)))

      switch_time_2 = 0
      in_process = None

    # Next interesting event is process finishes CPU burst
    elif (cpu_time + t) <= arr_time and (cpu_time + t) <= (io_time + t):
      time_step = cpu_time
      t += time_step

      useCPU(running_proc, time_step) # Run CPU Burst
      for i in range(len(doing_io)):  # Decrement IO usage time
        doIO(doing_io[i], time_step)

      if processCompleted(running_proc):
        print("time %.0fms: Process %s terminated %s" % (t, running_proc.name, printQueue(ready_queue)))

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

      # If there's a process in the ready queue, AND a process didn't just finish I/O,
      #   start its context switch in to the CPU
      if ready_queue and cpu_time != io_time:
        switch_time_2 = t + t_cs
        in_process = ready_queue[0]

    # Next interesting event is process finishes IO burst
    elif (io_time + t) <= arr_time and (io_time + t) <= (cpu_time + t):
      time_step = io_time
      t += time_step

      if t > 13400 and time_step == 0:
        print("time step zero")

      # Run CPU burst (if there is a process currently using the CPU)
      if running_proc != None: useCPU(running_proc, time_step)

      for i in range(len(doing_io)):  # Decrement IO usage time
        doIO(doing_io[i], time_step)

      doing_io[0].curr_io += 1 # Increment IO burst counter
      popped = doing_io.pop(0) # Remove from IO queue
      addToQueue(ready_queue, popped, True) # Add to ready queue

      if t <= 999 or verbose:
        print("time %.0fms: Process %s (tau %.0fms) completed I/O; added to ready queue %s" % (t, popped.name, popped.tau, printQueue(ready_queue)))

      # If the CPU is idle and there is no other process in the middle of a
      #   context switch, start the context switch of this process into the CPU
      if running_proc == None and switch_time_2 == 0:
        if switch_time_1 != 0:      # Context switch out
          switch_time_2 = t + t_cs
        else:                       # No context switch out
          switch_time_2 = t + (t_cs / 2)
          #ready_queue.remove(popped) # Don't need to wait for other process to leave # TODO Try

        in_process = popped

    # Next interesting event is process arrival
    else:
      time_step = arr_time - t
      t += time_step

      # Run CPU burst (if there is a process currently using the CPU)
      if running_proc != None: useCPU(running_proc, time_step)

      for i in range(len(doing_io)):  # Decrement IO usage time
        doIO(doing_io[i], time_step)

      addToQueue(ready_queue, next_proc, True)

      if t <= 99 or verbose:
        print("time %.0fms: Process %s (tau %.0fms) arrived; added to ready queue %s" % (t, next_proc.name, next_proc.tau, printQueue(ready_queue)))


      # If the CPU is idle and there is no other process in the middle of a
      #   context switch, start the context switch of this process into the CPU
      if running_proc == None and switch_time_2 == 0:
        if switch_time_1 != 0: # Wait for context switch out
          switch_time_2 = t + t_cs
        else:
          switch_time_2 = t + (t_cs / 2)
          #ready_queue.remove(next_proc) # TODO Try

        in_process = next_proc

      # If preemptive, check if new process has less remaining time than
      #   the currently running process
      
      # TODO Yes, Farhad's comment is correct, this needs to be fixed
      # Farhad: Should this check be done for all other processes and not just next_proc?
      # In that case, this probably should not be the place to do it
      elif preemptive and running_proc != None and getCPUBurst(next_proc) < getCPUBurst(running_proc):
        preempted = True
        print("<Preempted! %s out, %s in>" % (running_proc.name, next_proc.name))

        switch_time_1 = t + (t_cs / 2.)
        out_process = running_proc
        running_proc = None

        switch_time_2 = t + t_cs
        in_process = next_proc

    # in_process is starting its (half) context switch into the CPU
    if t == switch_time_2 - (t_cs/2) and in_process != None and in_process in ready_queue:
      ready_queue.remove(in_process)
      if in_process.name == "G" and t > 13400:
        print(t)
        print(switch_time_2)

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

