# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

import sys
import process_gen
#from srt_test import *
#from rr import *
import sjf_srt
import srt_test
import rr


def write_to_file(algo):
  fp.write("Algorithm %s\n" %algo)
  fp.write('-- average CPU burst time: %1.3f ms\n'%ave_CPU_burst)
  fp.write('-- average wait time: %1.3f ms\n'%ave_wait_time)
  fp.write('-- average turnaround time: %1.3f ms\n'%ave_turnaround)
  fp.write('-- total number of context switches: %d\n'%no_context_switch)
  fp.write('-- total number of preemptions: %d\n'%no_preemptions)

def print_stats(algo):
  print("Algorithm %s" %algo)
  print('-- average CPU burst time: %1.3f ms'%ave_CPU_burst)
  print('-- average wait time: %1.3f ms'%ave_wait_time)
  print('-- average turnaround time: %1.3f ms'%ave_turnaround)
  print('-- total number of context switches: %d'%no_context_switch)
  print('-- total number of preemptions: %d'%no_preemptions)

if __name__=='__main__':
    
  # Argument Checks

  if(len(sys.argv) < 7):
    print("Usage: python3 project1.py <seed_num> <lamb> <EXP_MAX> <n_processes> <t_cs> <alpha> <t_slice> [<rr_add>]", file=sys.stderr)
    exit()

  if(int(sys.argv[4]) > 26):
    print("Error: Too many processes (must be <= 26)", file=sys.stderr)
    exit()

  try:
    if(int(sys.argv[5]) < 0 or int(sys.argv[5]) % 2 != 0):
      print("Error: Context Switch Time should be a positive even integer.", file=sys.stderr)
      exit()
  except ValueError: # If a floating point number is passed
    print("Error: Context Switch Time should be a positive even integer.", file=sys.stderr)
    exit()

  if(len(sys.argv) > 8): 
    rr_add = sys.argv[8] # optional argument for RR
    if(not(rr_add=="BEGINNING" or rr_add=="END")):
      print("ERROR: Invalid argument for rr_add.",file=sys.stderr)
      exit()

# Generate the processes from system arguments and print their details
  
#  for i in range(len(processes)):
#    process_gen.print_process_details(processes[i])

  fp = open("simout.txt", 'w')
 
  processes, t_cs, alpha, t_slice, rr_add = process_gen.create_processes(sys.argv, False)
  ave_CPU_burst, ave_wait_time, ave_turnaround, no_context_switch, no_preemptions = sjf_srt.SJF_SRT(processes, t_cs, alpha, False)

  num_bursts = 0.
  burst_time = 0.
  for p in processes:
    num_bursts += ( p.no_cpu_bursts - 1 )
    for b in p.orig_io:
      burst_time += b

  ave_IO_burst = burst_time / num_bursts
  fp.write('-- average IO burst time: %1.3f ms\n'%ave_IO_burst)

  write_to_file("SJF")
  print("")
  
  processes, t_cs, alpha, t_slice, rr_add = process_gen.create_processes(sys.argv, False)
  ave_CPU_burst, ave_wait_time, ave_turnaround, no_context_switch, no_preemptions = srt_test.SRT(processes, t_cs, alpha)
#  print_stats("SRT")
  write_to_file("SRT")
  print("")
  
  processes, t_cs, alpha, t_slice, rr_add = process_gen.create_processes(sys.argv, True)  
  ave_CPU_burst, ave_wait_time, ave_turnaround, no_context_switch, no_preemptions = rr.RR_FCFS(False, t_slice, len(processes), processes, t_cs, True)
  write_to_file("FCFS")
  print("")
  
  processes, t_cs, alpha, t_slice, rr_add = process_gen.create_processes(sys.argv, True)
  ave_CPU_burst, ave_wait_time, ave_turnaround, no_context_switch, no_preemptions = rr.RR_FCFS(True, t_slice, len(processes), processes, t_cs, False)
  write_to_file("RR")

  fp.close()
