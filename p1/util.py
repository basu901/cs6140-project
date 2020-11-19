# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

import sys
from math import ceil

inf = float('inf') # Define constant for infinity
nan = float('nan') # Define constant for Not a Number

# Checks if process p has completed all of its bursts
def processCompleted(p):
  for t in p.cpu_bursts:
    if t != 0.: return False
  for t in p.io_bursts:
    if t != 0.: return False
  return True

def done(processes):
  for p in processes:
    if not p.terminated:
      return False
  return True

# Returns True if there are still processes which haven't terminated yet
#         False otherwise
def notDone(processes):
  for p in processes:
    if(not processCompleted(p)):
      return True
  return False

# Returns the process which will arrive next after *or at* curr_time
# MIKE NOTE: Changed this to give process which could arrive at curr_time (i.e. equal to or greater than, not just greater than)
def getNextArrival(processes, curr_time):
  t = inf
  next_proc = None

  for p in processes:
    if p.arrival >= curr_time and p.arrival < t:
      t = p.arrival
      next_proc = p

  return next_proc, t

# Get the amount of time left in the current CPU burst of process p
def getCPUBurst(p):
  return p.cpu_bursts[p.curr_cpu]

# Get the amount of time left in the current IO burst of process p
def getIOBurst(p):
  return p.io_bursts[p.curr_io]

# Running process running_proc for time_step ms
def useCPU(running_proc, time_step):
  curr_burst = -1
  for i in range(len(running_proc.cpu_bursts)):
    if running_proc.cpu_bursts[i] != 0:
      curr_burst = i
      break
  if curr_burst == -1:
    print("Error: Process has no CPU time remaining (this is a bug)")
  else:
    running_proc.cpu_bursts[curr_burst] -= time_step
    running_proc.tau_rem -= time_step

# Do time_step ms of IO on process proc
def doIO(proc, time_step):
  curr_burst = -1
  for i in range(len(proc.io_bursts)):
    if proc.io_bursts[i] != 0:
      curr_burst = i
      break
  if curr_burst == -1:
    print("Error: Process has no IO time remaining (this is a bug)")
  else:
    proc.io_bursts[curr_burst] -= time_step

# Do time_step ms of context switch
def doContextSwitch(proc, time_step):
  proc.switch_time -= time_step

def updateBurstGuess(P, alpha, latest_burst):
     del_guess = alpha * (latest_burst - P.tau)
     P.tau += ceil(del_guess)
     P.tau_rem = P.tau

