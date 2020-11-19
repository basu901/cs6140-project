# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu         (basus6)
# Michael Giancola (giancm)
# Farhad    Mohsin     (mohsif)

import sys
import process_gen
from util import *

inf = float('inf') # Define constant for infinity

# Behavior for Submitty = False
# If you want to see all output (i.e. events after 1000ms) set to True
verbose = False

# TODO: What if two processes end IO at same time?

# processes:    (list)        Contains process info (arrival time, cpu bursts, io bursts)
# t_cs:             (integer) Time (ms) for context switch
# alpha:            (float)     Weight parameter for updating burst time estimate
# preemptive: (boolean) False -> SJF, True -> SRT
def SRT(processes, t_cs, alpha):
    n_processes = len(processes)
    ave_CPU_burst = 0
    ave_wait_time = 0
    ave_turnaround = 0        
    no_context_switch = 0
    no_preemptions = 0
    
    running_proc = None    # Process currently using CPU
    ready_queue = []
    doing_io        = []         # List of processes currently blocked by io

    preempted = False    # Was in_process pre-empted by out_process?
    switch_time_1 = -1 # The time the first    half of the context switch will complete
    switch_time_2 = -1 # The time the second half of the context switch will complete
    in_process = None    # The process going in to the CPU
    out_process = None # The process going out of the CPU (to the queue)
    preemption_from_Q = True
    
    min_idx = -1
    
    alg = "SRT"

    t = 0. # simulation clock
    cnt = 0.
    print("time %.0fms: Simulator started for %s %s" % (t, alg, printQueue(ready_queue)))
            
    while(notDone(processes)):
#        # Random printing shit in every iteration
#        # not really a good idea
#        if( t< 100 ):
#            print("Time = %d ms: Process Queue = %s" %(t, printQueue(ready_queue)) )
#            print("Time = %d ms: IO Queue: %s" % (t, printQueue(doing_io)) )
            
        # Case: first half of context switch finishing
        if(t == switch_time_1):
            # Add outgoing process to ready_queue in case it isn't finished
            if(out_process):
                if(preempted):
                    #print("time %d: proc %s going back to the ready queue" %(t, out_process.name))
                    addToQueue(ready_queue, out_process, True)
                    out_process = None
                    preempted = False
                else:
                    out_process.curr_cpu += 1
                    #print("time %d: proc %s should do IO of time %d" %(t, out_process.name, getIOBurst(out_process)))
                    addToQueue(doing_io, out_process, False)
                    #print("time %d: IO %s" %(t, printQueue(doing_io)))
                    out_process = None
            if(in_process):
                switch_time_2 = t + t_cs / 2
        
        # Case: second half of context switch finishing
        if(t == switch_time_2):
            if(min_idx == -1):
                print("No incoming process defined: This is an error")
            running_proc = in_process
            #HEYYYYYYYY#
#            ready_queue.remove(in_process)
            #print("time %d: proc %s should start a burst of %d ms %s" %(t, running_proc.name, running_proc.cpu_bursts[running_proc.curr_cpu], printQueue(ready_queue)))
            if t <= 999 or verbose:
                if(running_proc.orig_bursts[running_proc.curr_cpu] > getCPUBurst(running_proc)):
                    print("time %dms: Process %s started using the CPU with %.0fms remaining %s" % (t, running_proc.name, getCPUBurst(running_proc), printQueue(ready_queue)))
                else: 
                    print("time %dms: Process %s started using the CPU for %.0fms burst %s" % (t, running_proc.name, running_proc.orig_bursts[running_proc.curr_cpu], printQueue(ready_queue)))
            in_process = None
            no_context_switch += 1
        
        # Check for any new arrival
        # properly enqueue newly arrived process
        for proc in processes:
            if(proc.arrival == t):
                if not running_proc and switch_time_1 < t and switch_time_2 < t:
#                    running_proc = proc
                    #current_burst = proc.cpu_bursts[curr_cpu]
                    switch_time_2 = t + t_cs / 2
                    addToQueue(ready_queue, proc, True)
                    in_process = proc
                    min_idx = 0
                    
                else:
                    addToQueue(ready_queue, proc, True)
                if t <= 999 or verbose:
                    print("time %.0fms: Process %s (tau %.0fms) arrived; added to ready queue %s" % (t, proc.name, proc.tau, printQueue(ready_queue)))
        
        
        ####THIS IS WHERE THE IO BLOCK PREVIOUSLY WAS####
        # Check if something has finished doing IO in the previous case
        if(doing_io):
            io_time = getIOBurst(doing_io[0])
            while( io_time == 0 ):
                
                if(in_process and (t > switch_time_1 - t_cs/2 and t <= switch_time_1)):
                    addToQueue(ready_queue, in_process, True)
#                    in_process = None
                
                #print("time %d: IO Q : %s" %(t, printQueue(doing_io)))
                doing_io[0].curr_io += 1 # Increment IO burst counter
                popped = doing_io.pop(0) # Remove from IO queue
                #print("time %d: proc %s has finished IO once" %(t, popped.name))
                addToQueue(ready_queue, popped, True)
                
                if(in_process and (t > switch_time_1 - t_cs/2 and t <= switch_time_1)):
                    if(popped.tau_rem < in_process.tau_rem):
                        in_process = popped
                        min_idx = 0
                    elif(popped.tau_rem == in_process.tau_rem):
                        if(popped.name < in_process.name):
                            in_process = popped
                            min_idx = 0
                    
                #print("time %d: [ready Q = %s]" %(t, printQueue(ready_queue)))
                if(running_proc):
                    if(popped.tau_rem < running_proc.tau_rem):
                        
                        preemption_from_Q = False
                        if t <= 999 or verbose:
                            print("time %dms: Process %s (tau %.0fms) completed I/O and will preempt %s %s" %(t, popped.name, popped.tau_rem, running_proc.name, printQueue(ready_queue)))
                    else:
                        if t <= 999 or verbose:
                            print("time %dms: Process %s (tau %.0fms) completed I/O; added to ready queue %s" %(t, popped.name, popped.tau_rem, printQueue(ready_queue)))
                else:
                    if t <= 999 or verbose:
                        print("time %dms: Process %s (tau %.0fms) completed I/O; added to ready queue %s" %(t, popped.name, popped.tau_rem, printQueue(ready_queue)))
                if(doing_io):
                    io_time = getIOBurst(doing_io[0])
                else:
                    io_time = inf
        
        # Use CPU for current running process
        # This can happen even if context switching has just finished, or just arrived
        if(running_proc and t >= switch_time_2):
#            if(t < 100):
#                print("    time %d: proc %s, remaining_tau = %d" %(t, running_proc.name, running_proc.tau_rem) )        
            # Check if running process completed a burst, if yes
            # set switch_time_1
            if(getCPUBurst(running_proc) == 0):
                #print("time %d: proc %s has finished a burst, yay!" %(t, running_proc.name))
                bursts = running_proc.no_cpu_bursts - running_proc.curr_cpu - 1
                if t <= 999 or verbose:
                    if bursts == 1:
                        print("time %dms: Process %s completed a CPU burst; %d burst to go %s" % (t, running_proc.name, bursts, printQueue(ready_queue)))
                    elif bursts == 0:
                        pass
                    else:
                        print("time %dms: Process %s completed a CPU burst; %d bursts to go %s" % (t, running_proc.name, bursts, printQueue(ready_queue)))
                
                switch_time_1 = t + t_cs / 2
                
                updateBurstGuess(running_proc, alpha, running_proc.orig_bursts[running_proc.curr_cpu])
                    
                # Check if running process has completed all its bursts
                # Based on that, modify ready_queue
                if(not(processCompleted(running_proc))):
                    out_process = running_proc
                    if t <= 999 or verbose:
                        print("time %dms: Recalculated tau = %.0fms for process %s %s" % (t, running_proc.tau, running_proc.name, printQueue(ready_queue)))
                        print("time %dms: Process %s switching out of CPU; will block on I/O until time %.0fms %s" % (t, running_proc.name, t + getIOBurst(running_proc) + (t_cs / 2), printQueue(ready_queue)))
                else:
                    out_process = None
                    print("time %dms: Process %s terminated %s" %(t, running_proc.name, printQueue(ready_queue) ))
                    running_proc.terminated = True
                    running_proc.termination_time = t
                    
                running_proc = None
                # We do not pop yet
                if(ready_queue):
                    in_process = ready_queue[0]
                    min_idx = 0
            # If not the end of a burst
            # we check for a preemption anyway
            else:
                # Check for possibility of preemption after every ms
                # Keep track of which process it is, because we need to remove it from ready_queue
                # after context switch is complete
                if(ready_queue):
                    if(ready_queue[0].tau_rem < running_proc.tau_rem):
                        #print("  HEY! PREEMPTION TIME. Switch times are %d and %d" %(switch_time_1, switch_time_2))
                        #print("    time %d - ready: %s %d, running: %s %d" %(t, ready_queue[0].name, ready_queue[0].tau_rem, running_proc.name, running_proc.tau_rem))
                        if(preemption_from_Q):
                            if t <= 999 or verbose:
                                print("time %dms: Process %s (tau %.0fms) will preempt %s %s" %(t, ready_queue[0].name, ready_queue[0].tau_rem, running_proc.name, printQueue(ready_queue)))
#                            print("    time %d - ready: %s %d, running: %s %d" %(t, ready_queue[0].name, ready_queue[0].tau_rem, running_proc.name, running_proc.tau_rem))
                        in_process = ready_queue[0]
                        min_idx = 0
                        switch_time_1 = t + t_cs / 2
                        out_process = running_proc
                        running_proc = None
                        preempted = True
                        no_preemptions += 1
                
                # If only one process and there is no running_proc 
                # this must go into running_proc now
#                if(len(ready_queue) == 1 and running_proc == None): 
#                    switch_time_2 = t + t_cs / 2
#                    in_process = popped
#                    min_idx = 0
        
        # What if there is nothing in running_proc and by now we have something in ready_queue
        # and we are not inside of a context switch
        
        if(running_proc == None and switch_time_1 < t and switch_time_2 < t):
            if(ready_queue):
                switch_time_2 = t + t_cs / 2
                in_process = ready_queue[0]
                min_idx = 0
        
        if(running_proc):
            useCPU(running_proc, 1)
        
        for io_proc in doing_io:
            doIO(io_proc, 1)
        
        #HEYYYYYYYYYY#
        if(in_process):
            if(in_process in ready_queue):
                ready_queue.remove(in_process)
                
        for i in range(len(ready_queue)):
            ready_queue[i].wait_time += 1
        
        t += 1
        preemption_from_Q = True
    
    # Compute stats
    num_bursts = 0.
    burst_time = 0.
    wait_time  = 0.
    turnaround_time = 0.
    for p in processes:
        num_bursts += p.no_cpu_bursts
        wait_time  += p.wait_time
        for b in p.orig_bursts:
            burst_time += b
        
        #Finish termination for whichever ended last
        if(p.terminated == False):
            p.terminated = True
            p.termination_time = t
            print("time %dms: Process %s terminated %s" %(t, p.name, printQueue(ready_queue) ))
        
        # Calculated turn time for each process
        p.turn_time = p.termination_time - p.arrival
        for i in p.orig_io:
            p.turn_time -= (i + t_cs/2)
        turnaround_time += p.turn_time

    ave_CPU_burst = burst_time / num_bursts
#    ave_wait_time = wait_time  / num_bursts
    ave_turnaround = turnaround_time / num_bursts + t_cs/2
    
    wait_time_2 = turnaround_time - burst_time  - num_bursts * t_cs/2 - no_preemptions * t_cs
    ave_wait_time = wait_time_2 / num_bursts
    
    print("time %dms: Simulator ended for %s [Q <empty>]" % (t + t_cs/2, alg))
    
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

# isCPU - True    if queue is running_queue
#             - False if queue is doing_io
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
            #     by name (i.e. alphabetic order)
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
            #     by name (i.e. alphabetic order)
            if proc_burst == queue_burst:
                if proc.name < queue[i].name:
                    queue.insert(i, proc)
                    return

            elif proc_burst < queue_burst:
                queue.insert(i, proc)
                return

        # Got to end -- add to end of queue
        queue.append(proc)

