# CS 6140 - Computer Operating Systems
# Project 1
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

from math import log, floor, ceil

'''
The Rand48 class implementation was copied directly from an answer here
https://stackoverflow.com/questions/7287014/is-there-any-drand48-equivalent-in-python-or-a-wrapper-to-it
This class is used to replicate the functionality of srand48 and drand8 in C
The only extra function is the exp_rand which converts the uniform random number
    to an exponential distribution and also checks whether it is beyond the max
    limit of the exponential distribution given in the arguments
'''
class Rand48(object):
    def __init__(self, seed):
        self.n = seed
    def seed(self, seed):
        self.n = seed
    def srand(self, seed):
        self.n = (seed << 16) + 0x330e
    def next(self):
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n
    def drand(self):
        return self.next() / 2**48
    def exp_rand(self, lamb, EXP_MAX):
        while (1):
            x = self.next() / 2**48
            ex = -log(x) / lamb
            if(ex < EXP_MAX):
                break
        return ex
    def lrand(self):
        return self.next() >> 17
    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

'''
The class object has a name (which is a letter between A to Z), arrival time,
    a list for cpu_bursts and a list for io_bursts.
    The get functions return the i-th cpu_burst or i-th io_burst
    all time or time differences are in miliseconds
'''
class Process(object):
    def __init__(self, name, lamb):
        self.name = name
        self.tau = 1. / lamb
        self.tau_rem = 1. / lamb
        self.curr_cpu = 0 # Index of current CPU burst
        self.curr_io = 0
        self.terminated = False
        self.wait_time = 0. # to store wait time
        self.turn_time = 0. # to store turnaround time
        self.burst_start_or_resume = 0 # this will help calculation of turnaround time for SRT
        self.termination_time = -1
    def set_params(self, arrival_time, no_bursts, cpu_burst_list, io_burst_list):
        self.arrival = arrival_time
        self.no_cpu_bursts = no_bursts
        self.cpu_bursts = cpu_burst_list
        self.orig_bursts = cpu_burst_list.copy()
        self.io_bursts = io_burst_list
        self.orig_io = io_burst_list.copy()
    def get_cpu_burst_i(self, i):
        return self.cpu_bursts[i]
    def get_io_burst_i(self, i):
        return self.io_bursts[i]




#Process object for RR annd FCFS:

class Process_RF(object):
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




'''
This function gets called in the main project files to create the processes
    in a pseudorandom manner according to the arguments.
    Creates an array of process arguments
    Also stores and returns the other parameters (context_switch time, time slice etc.)
'''
def create_processes(args,isRF):

    seed_num = int(args[1]) # seed for randomization function
    lamb = float(args[2]) # lambda, parameter for exponential distribution
    EXP_MAX = float(args[3]) # max limit for random number in exponential distribution
    n_processes = int(args[4]) # number of processes
    t_cs = int(args[5]) # time (ms) for context switching
    alpha = float(args[6]) # weight parameter for updating burst time estimate in SJF/SRT
    t_slice = int(args[7]) # time_slice (ms) for RR algo
    rr_add = None
    if(len(args) > 8): 
        rr_add = args[8] # optional argument for RR
    if(rr_add=="BEGINNING"):
    	rr_add = False
    else:
        rr_add = True
    
    #print ('Number of arguments:', len(args), 'arguments.')
    #print ('Argument List:', str(args))
    
    # seeding the rand function
    r = Rand48(0)
    r.srand(seed_num)
    
    '''
    This portion is copied from post 276 in Piazza, it was rather concisely-written
    1) Initial process arrival time is drand() with the exponential distribution function applied
    2) Quantity of CPU bursts is drand() * 100 and truncated 
    3) For each CPU burst, and then IO burst, drand() with exponential distribution applied
    '''
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    processes = []
    
    for n in range(n_processes):
        if(isRF):
                new_p = Process_RF(alphabet[n])
        else:
                new_p = Process(alphabet[n], lamb)	#new_p = Process(alphabet[n]) for RR and FCFS
        arrival = floor(r.exp_rand(lamb, EXP_MAX))
        no_b = int(r.drand() * 100) + 1
        cpu_list = []
        io_list = []
        for burst in range(no_b):
            cpu_list.append( ceil(r.exp_rand(lamb, EXP_MAX)) )
            if( burst < no_b - 1 ):
                io_list.append( ceil(r.exp_rand(lamb, EXP_MAX)) )
        new_p.set_params(arrival, no_b, cpu_list, io_list)
        processes.append(new_p)
    
    for P in processes:
        print_process_details(P)
    return processes, t_cs, alpha, t_slice, rr_add

def print_process_details(P):
    if(P.no_cpu_bursts == 1):
        print("Process %s [NEW] (arrival time %.0f ms) %d CPU burst" % (P.name, P.arrival, P.no_cpu_bursts))
    else:
        print("Process %s [NEW] (arrival time %.0f ms) %d CPU bursts" % (P.name, P.arrival, P.no_cpu_bursts))
    #for i in range(P.no_cpu_bursts - 1):
    #    print("--> CPU burst %.0lf ms --> I/O burst %.0lf ms"%(P.get_cpu_burst_i(i), P.get_io_burst_i(i) ))
    #print("--> CPU burst %.0lf ms"%P.get_cpu_burst_i(P.no_cpu_bursts - 1))
    
def print_full_details(P):
    print("Process %s [NEW] (arrival time %.0f ms) %d CPU bursts" % (P.name, P.arrival, P.no_cpu_bursts))
    for i in range(P.no_cpu_bursts - 1):
        print("--> CPU burst %.0lf ms --> I/O burst %.0lf ms"%(P.get_cpu_burst_i(i), P.get_io_burst_i(i) ))
    print("--> CPU burst %.0lf ms"%P.get_cpu_burst_i(P.no_cpu_bursts - 1))
    
